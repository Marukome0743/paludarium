import { isNode, spawnWorker, listen, stopWorker } from "./worker-support.mjs";
export class PaludariumError extends Error {
  constructor(kind, message, details = {}) { super(message); this.name = "PaludariumError"; this.kind = kind; for (const field of ["rip", "bytes", "syscall"]) if (details[field] !== undefined) this[field] = details[field]; }
}
async function moduleBytes(url) {
  const source = new URL(url, typeof location === "undefined" ? import.meta.url : location.href);
  if (isNode && source.protocol === "file:") return (await import("node:fs/promises")).readFile(source);
  const response = await fetch(source, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new PaludariumError("host", `Wasm fetch returned ${response.status}`);
  return response.arrayBuffer();
}
function validate(options) {
  if (!options || typeof options.program !== "string" || !options.program.startsWith("/") || options.program.includes("\0")) throw new PaludariumError("invalid-program", "program must be an absolute guest path");
  if (options.tty != null && [options.tty.columns, options.tty.rows].some(value => !Number.isInteger(value) || value < 0 || value > 65535)) throw new PaludariumError("invalid-program", "invalid guest terminal size");
  if (options.jit === true) throw new PaludariumError("unimplemented", "Worker JIT is unavailable");
  if (options.cwd !== undefined && (typeof options.cwd !== "string" || !options.cwd.startsWith("/") || options.cwd.includes("\0"))) throw new PaludariumError("invalid-program", "invalid guest current directory");
  if (options.args && (!Array.isArray(options.args) || options.args.some(arg => typeof arg !== "string" || arg.includes("\0")))) throw new PaludariumError("invalid-program", "invalid guest arguments");
  if (Object.entries(options.env ?? {}).some(([key, value]) => !key || key.includes("=") || key.includes("\0") || typeof value !== "string" || value.includes("\0"))) throw new PaludariumError("invalid-program", "invalid guest environment");
  if (Object.entries(options.files ?? {}).some(([path, bytes]) => !path.startsWith("/") || path.includes("\0") || !(bytes instanceof Uint8Array))) throw new PaludariumError("invalid-program", "invalid guest files");
  if (Object.entries(options.fileModes ?? {}).some(([path, mode]) => !Object.hasOwn(options.files ?? {}, path) || !Number.isInteger(mode) || mode < 0 || mode > 0o7777)) throw new PaludariumError("invalid-program", "invalid guest file modes");
}
function decodeSnapshot(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength), decoder = new TextDecoder(); let offset = 0;
  const u32 = () => { const value = view.getUint32(offset, true); offset += 4; return value; };
  const u64 = () => { const value = view.getBigUint64(offset, true); offset += 8; return value; };
  const chunk = () => { const length = u32(); if (offset + length > bytes.length) throw new Error("invalid filesystem snapshot"); const value = bytes.slice(offset, offset + length); offset += length; return value; };
  const entries = [], count = u32();
  for (let index = 0; index < count; index++) { const path = decoder.decode(chunk()), mode = u32(), inode = u64(), links = u64(), mtimeNs = u64(), content = chunk(); entries.push({ path, mode, inode, links, mtimeNs, content }); }
  if (offset !== bytes.length) throw new Error("invalid filesystem snapshot length");
  return entries;
}
/** C12: all Rust execution and locking takes place in dedicated Workers. */
export async function createPaludarium({ wasmUrl }) {
  const module = await WebAssembly.compile(await moduleBytes(wasmUrl));
  const memory = new WebAssembly.Memory({ initial: 128, maximum: 16384, shared: true });
  const coordinator = await spawnWorker(new URL("coordinator.mjs", import.meta.url));
  const pending = new Map(); let next = 1, closed = false, failed = false, readyResolve, readyReject, disposeResolve, disposal, disposeTimer;
  const filesystems = new WeakMap();
  function control(type, values = {}) {
    if (closed) return Promise.reject(new PaludariumError("host", "Launcher is closed"));
    const id = next++;
    return new Promise((resolve, reject) => { pending.set(id, { resolve, reject }); coordinator.postMessage({ type, id, ...values }); });
  }
  const ready = new Promise((resolve, reject) => { readyResolve = resolve; readyReject = reject; });
  const initTimer = setTimeout(() => void failAll(new PaludariumError("host", "30 second launcher initialization watchdog")), 30000);
  function rejectPending(error) {
    for (const job of pending.values()) { clearTimeout(job.timer); job.reject(error); job.stdout?.error(error); job.stderr?.error(error); job.stdin?.error(error); }
    pending.clear();
  }
  async function failAll(error) {
    if (failed) return;
    failed = true; closed = true; clearTimeout(initTimer); clearTimeout(disposeTimer); readyReject(error);
    rejectPending(error);
    await stopWorker(coordinator); disposeResolve?.();
  }
  listen(coordinator, report => {
    if (report.type === "fatal") { void failAll(new PaludariumError(report.error.kind, report.error.message)); return; }
    if (report.type === "ready") { clearTimeout(initTimer); readyResolve(report); return; }
    if (report.type === "disposed") { clearTimeout(disposeTimer); void stopWorker(coordinator).then(() => disposeResolve?.()); return; }
    const job = pending.get(report.id);
    if (!job) { if (report.type === "failed" && report.id === undefined) void failAll(new PaludariumError(report.error.kind, report.error.message)); return; }
    if (report.type === "output") job[report.stream]?.enqueue(report.bytes);
    else if (report.type === "finished" || report.type === "failed") {
      clearTimeout(job.timer); pending.delete(report.id);
      if (report.type === "failed") { const error = new PaludariumError(report.error.kind, report.error.message, report.error); job.stdout?.error(error); job.stderr?.error(error); job.reject(error); }
      else { job.stdout?.close(); job.stderr?.close(); job.resolve(report.status); }
    } else if (report.type === "diagnostics") { pending.delete(report.id); clearTimeout(job.timer); job.resolve(report.diagnostics); }
    else if (report.type === "control") { pending.delete(report.id); job.resolve(report.value); }
  }, cause => void failAll(new PaludariumError("internal", String(cause))));
  coordinator.postMessage({ type: "init", module, memory });
  await ready;
  return {
    async createFileSystem(options = {}) {
      validate({ ...options, program: "/" });
      const handle = await control("filesystem-new", { options });
      let disposed = false;
      const available = () => { if (disposed) throw new PaludariumError("host", "Filesystem is disposed"); };
      const filesystem = Object.freeze({
        async snapshot() { available(); return decodeSnapshot(await control("filesystem-snapshot", { handle })); },
        async remove(path, { recursive = false } = {}) {
          available();
          if (typeof path !== "string" || !path.startsWith("/") || path.includes("\0") || typeof recursive !== "boolean") throw new PaludariumError("invalid-program", "invalid filesystem removal");
          await control("filesystem-remove", { handle, path, recursive });
        },
        async dispose() { if (disposed) return; await control("filesystem-drop", { handle }); disposed = true; filesystems.delete(filesystem); },
      });
      filesystems.set(filesystem, handle); return filesystem;
    },
    run(options) {
      validate(options);
      if (closed) throw new PaludariumError("host", "Launcher is closed");
      const id = next++, job = {};
      const stdout = new ReadableStream({ start(controller) { job.stdout = controller; }, cancel() { job.stdout = null; } });
      const stderr = new ReadableStream({ start(controller) { job.stderr = controller; }, cancel() { job.stderr = null; } });
      const exited = new Promise((resolve, reject) => { job.resolve = resolve; job.reject = reject; });
      // Guest deadlines belong to the caller/test supervisor. kill() requests
      // a cooperative stop; dispose() retains its bounded resource cleanup.
      pending.set(id, job);
      const { filesystem, ...messageOptions } = options;
      if (filesystem !== undefined) {
        const handle = filesystems.get(filesystem);
        if (!handle) { pending.delete(id); throw new PaludariumError("invalid-program", "filesystem belongs to another launcher"); }
        messageOptions.filesystemHandle = handle;
      }
      coordinator.postMessage({ type: "run", id, options: messageOptions });
      const stdin = new WritableStream({
        start(controller) { job.stdin = controller; },
        write(bytes) { if (!(bytes instanceof Uint8Array)) throw new TypeError("stdin requires Uint8Array"); if (closed || !pending.has(id)) throw new PaludariumError("host", "Guest input is closed"); coordinator.postMessage({ type: "stdin", id, bytes }); },
        close() { if (!closed) coordinator.postMessage({ type: "stdin-close", id }); },
        abort() { if (!closed) coordinator.postMessage({ type: "kill", id }); },
      });
      return { stdin, stdout, stderr, exited, kill() { if (!closed) coordinator.postMessage({ type: "kill", id }); } };
    },
    diagnostics() {
      if (closed) return Promise.reject(new PaludariumError("host", "Launcher is closed"));
      const id = next++;
      return new Promise((resolve, reject) => { const timer = setTimeout(() => void failAll(new PaludariumError("host", "diagnostics watchdog")), 30000); pending.set(id, { resolve, reject, timer }); coordinator.postMessage({ type: "diagnostics", id }); });
    },
    async dispose() {
      if (disposal) return disposal;
      if (closed) return;
      closed = true;
      rejectPending(new PaludariumError("host", "Launcher disposed"));
      disposal = new Promise(resolve => {
        disposeResolve = resolve;
        coordinator.postMessage({ type: "dispose" });
        // Graceful kill gets one second; forced termination discards this entire heap.
        disposeTimer = setTimeout(() => void failAll(new PaludariumError("host", "Launcher disposal watchdog")), 1000);
      });
      return disposal;
    },
  };
}
