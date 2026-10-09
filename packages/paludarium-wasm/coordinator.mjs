import { channel, imports, spawnWorker, listen, stopWorker, putBuffer, takeBuffer } from "./worker-support.mjs";
const port = await channel();
const encoder = new TextEncoder(), decoder = new TextDecoder();
let module, memory, e;
const jobs = new Map();
const latestDiagnostics = [];
const childWorkers = new Set();
let abandoned = false;
const failure = (kind, message) => ({ kind, message });
function check(value, name) { if (value < 0) throw new Error(`${name} rejected`); return value; }
function withBytes(bytes, callback) { const id = putBuffer(e, bytes); try { return callback(id); } finally { e.buffer_drop(id); } }
function errorFor(handle) {
  const kind = e.session_error_kind(handle);
  const names = ["internal", "unimplemented", "internal", "invalid-program", "host"];
  const message = decoder.decode(takeBuffer(e, e.session_error_message(handle)));
  return failure(names[kind] ?? "internal", message || "Guest session failed");
}
function flush(job) {
  for (const [stream, name] of [[1, "stdout"], [2, "stderr"]]) {
    const bytes = takeBuffer(e, e.session_output(job.handle, stream));
    const offset = job.offsets[name];
    if (bytes.length > offset) port.send({ type: "output", id: job.id, stream: name, bytes: bytes.slice(offset) });
    job.offsets[name] = bytes.length;
  }
}
function fatal(message) {
  if (abandoned) return;
  abandoned = true;
  for (const job of jobs.values()) { clearTimeout(job.timer); clearInterval(job.poll); }
  // Termination may abandon Rust locks; no further Rust ABI calls are permitted.
  void Promise.all([...childWorkers].map(stopWorker)).finally(() => port.send({ type: "fatal", error: failure("host", message) }));
}
async function sharedProbe() {
  const space = e.shared_space_new();
  if (!space) throw new Error("shared AddressSpace creation failed");
  const children = [];
  const timer = setTimeout(() => fatal("shared probe watchdog; discard shared heap"), 30000);
  try {
    for (let index = 0; index < 2; index++) {
      const tlsSize = Number(e.__tls_size.value), align = Math.max(16, Number(e.__tls_align.value));
      const region = e.region_new(2 * 1024 * 1024 + tlsSize + align + 16);
      const pointer = e.region_pointer(region), tlsPointer = Math.ceil(pointer / align) * align;
      const stackTop = Math.ceil((tlsPointer + tlsSize) / 16) * 16 + 2 * 1024 * 1024;
      const token = putBuffer(e, new Uint8Array([73]));
      const worker = await spawnWorker(new URL("execution.mjs", import.meta.url));
      childWorkers.add(worker);
      const child = { worker, region, token, pending: new Map() };
      child.next = type => new Promise((resolve, reject) => child.pending.set(type, { resolve, reject }));
      listen(worker, report => {
        if (report.type === "failed") { fatal(report.error); for (const promise of child.pending.values()) promise.reject(new Error(report.error)); }
        else { child.pending.get(report.type)?.resolve(report); child.pending.delete(report.type); }
      }, cause => { fatal(String(cause)); for (const promise of child.pending.values()) promise.reject(cause); });
      const started = child.next("started"); children.push(child);
      worker.postMessage({ type: "execute", operation: "probe", module, memory, stackTop, tlsPointer, tokenHandle: token });
      child.diagnostics = (await started).diagnostics;
    }
    const completions = children.map(child => { const done = child.next("probe-done"); child.worker.postMessage({ type: "probe-go", space }); return done; });
    const allocations = await Promise.all(completions);
    if (abandoned) throw new Error("shared runtime abandoned");
    const value = String(e.shared_space_value(space));
    check(e.shared_wait_word(space, 0), "wait word");
    const waiter = children[0], starting = waiter.next("wait-starting"), done = waiter.next("wait-done");
    waiter.worker.postMessage({ type: "wait-go", space }); await starting;
    await new Promise(resolve => setTimeout(resolve, 50));
    check(e.shared_wait_word(space, 1), "notify word");
    const notified = e.shared_notify(space, 1), waited = (await done).result;
    if (abandoned) throw new Error("shared runtime abandoned");
    for (const child of children) { await stopWorker(child.worker); childWorkers.delete(child.worker); e.region_drop(child.region); e.buffer_drop(child.token); }
    e.shared_space_drop(space);
    return { value, allocations, notified, waited, workers: children.map(child => child.diagnostics) };
  } catch (cause) {
    // A trapped child may own a Rust lock: discard the complete runtime, never free/reuse it.
    fatal(String(cause)); throw cause;
  } finally { clearTimeout(timer); }
}
async function finish(job, result, error) {
  if (job.finished) return;
  if (abandoned) return;
  job.finished = true;
  clearTimeout(job.timer); clearInterval(job.poll);
  try { flush(job); } catch (cause) { error ??= failure("internal", String(cause)); }
  if (job.worker) await stopWorker(job.worker);
  if (abandoned) return;
  childWorkers.delete(job.worker);
  // Parent owns these allocations until the child is gone; never free an active stack.
  // This path is reached only after Rust returned, including a typed guest error.
  // Traps and forced failures discard the complete runtime through fatal().
  e.region_drop(job.region); e.buffer_drop(job.token);
  if (error) port.send({ type: "failed", id: job.id, error });
  else port.send({ type: "finished", id: job.id, status: result >= 256 ? { kind: "signaled", signal: result - 256 } : { kind: "exited", code: result }, diagnostics: job.diagnostics });
  e.session_drop(job.handle); jobs.delete(job.id);
}
async function launch(message) {
  const config = withBytes(encoder.encode(message.options.program), id => e.config_new(id));
  if (!config) throw new Error("invalid program configuration");
  try {
    for (const arg of message.options.args ?? [message.options.program]) withBytes(encoder.encode(arg), id => check(e.config_arg(config, id), "argument"));
    for (const [key, value] of Object.entries(message.options.env ?? {})) withBytes(encoder.encode(key), keyId => withBytes(encoder.encode(value), valueId => check(e.config_env(config, keyId, valueId), "environment")));
    for (const [path, bytes] of Object.entries(message.options.files ?? {})) withBytes(encoder.encode(path), pathId => withBytes(bytes, dataId => check(e.config_file(config, pathId, dataId), "file")));
    const handle = withBytes(new Uint8Array(), id => e.session_from_config(config, id));
    if (!handle) throw new Error("session creation failed");
    const tlsSize = Number(e.__tls_size.value), tlsAlign = Math.max(16, Number(e.__tls_align.value));
    const region = e.region_new(2 * 1024 * 1024 + tlsSize + tlsAlign + 16);
    if (!region) { e.session_drop(handle); throw new Error("Worker region allocation failed"); }
    const pointer = e.region_pointer(region);
    const tlsPointer = Math.ceil(pointer / tlsAlign) * tlsAlign;
    const stackTop = Math.ceil((tlsPointer + tlsSize) / 16) * 16 + 2 * 1024 * 1024;
    const token = putBuffer(e, new Uint8Array([73]));
    const job = { id: message.id, handle, region, token, offsets: { stdout: 0, stderr: 0 }, finished: false, diagnostics: null };
    jobs.set(message.id, job);
    port.send({ type: "accepted", id: message.id });
    job.timer = setTimeout(() => fatal("30 second Worker watchdog; discard shared heap"), 30000);
    job.worker = await spawnWorker(new URL("execution.mjs", import.meta.url));
    childWorkers.add(job.worker);
    listen(job.worker, report => {
      if (report.type === "started") { job.diagnostics = { ...report.diagnostics, regionPointer: pointer, coordinatorTls: e.__tls_base.value, coordinatorThreadToken: String(e.thread_token()), sharedMemory: memory.buffer instanceof SharedArrayBuffer, nestedWorker: true }; latestDiagnostics.push(job.diagnostics); }
      else if (report.type === "finished") void finish(job, report.result, report.result < 0 ? errorFor(handle) : null);
      else if (report.type === "failed") fatal(report.error);
    }, cause => fatal(String(cause)));
    job.poll = setInterval(() => { try { flush(job); } catch (cause) { fatal(String(cause)); } }, 10);
    job.worker.postMessage({ type: "execute", module, memory, sessionHandle: handle, stackTop, tlsPointer, tokenHandle: token });
  } finally { if (typeof e.config_drop === "function") e.config_drop(config); }
}
port.listen(async message => {
  if (abandoned) return;
  try {
    if (message.type === "init") {
      module = message.module; memory = message.memory;
      e = (await WebAssembly.instantiate(module, imports(memory))).exports;
      port.send({ type: "ready", exports: WebAssembly.Module.exports(module), imports: WebAssembly.Module.imports(module) });
    } else if (message.type === "run") await launch(message);
    else if (message.type === "diagnostics") port.send({ type: "diagnostics", id: message.id, diagnostics: { workers: latestDiagnostics, sharedProbe: await sharedProbe() } });
    else if (message.type === "stdin") {
      const job = jobs.get(message.id);
      if (job) withBytes(message.bytes, id => check(e.session_stdin_write(job.handle, id), "stdin"));
    } else if (message.type === "stdin-close") { const job = jobs.get(message.id); if (job) check(e.session_stdin_close(job.handle), "stdin close"); }
    else if (message.type === "kill") { const job = jobs.get(message.id); if (job) e.session_kill(job.handle); }
    else if (message.type === "dispose") {
      for (const job of jobs.values()) e.session_kill(job.handle);
      while (jobs.size) await new Promise(resolve => setTimeout(resolve, 10));
      port.send({ type: "disposed" });
    }
  } catch (cause) { port.send({ type: "failed", id: message.id, error: failure("internal", String(cause)) }); }
});
