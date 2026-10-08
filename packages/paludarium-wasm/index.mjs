import { isNode, spawnWorker, listen, stopWorker } from "./worker-support.mjs";
export class PaludariumError extends Error {
  constructor(kind, message) { super(message); this.name = "PaludariumError"; this.kind = kind; }
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
  if (options.tty != null) throw new PaludariumError("unimplemented", "Worker terminal support is unavailable");
  if (options.jit === true) throw new PaludariumError("unimplemented", "Worker JIT is unavailable");
  if (options.args && (!Array.isArray(options.args) || options.args.some(arg => typeof arg !== "string" || arg.includes("\0")))) throw new PaludariumError("invalid-program", "invalid guest arguments");
  if (Object.entries(options.env ?? {}).some(([key, value]) => !key || key.includes("=") || key.includes("\0") || typeof value !== "string" || value.includes("\0"))) throw new PaludariumError("invalid-program", "invalid guest environment");
  if (Object.entries(options.files ?? {}).some(([path, bytes]) => !path.startsWith("/") || path.includes("\0") || !(bytes instanceof Uint8Array))) throw new PaludariumError("invalid-program", "invalid guest files");
}
/** C12: all Rust execution and locking takes place in dedicated Workers. */
export async function createPaludarium({ wasmUrl }) {
  const module = await WebAssembly.compile(await moduleBytes(wasmUrl));
  const memory = new WebAssembly.Memory({ initial: 128, maximum: 16384, shared: true });
  const coordinator = await spawnWorker(new URL("coordinator.mjs", import.meta.url));
  const pending = new Map(); let next = 1, closed = false, readyResolve, readyReject, disposeResolve;
  const ready = new Promise((resolve, reject) => { readyResolve = resolve; readyReject = reject; });
  const initTimer = setTimeout(() => void failAll(new PaludariumError("host", "30 second launcher initialization watchdog")), 30000);
  async function failAll(error) {
    if (closed) return;
    closed = true; clearTimeout(initTimer); readyReject(error);
    for (const job of pending.values()) { clearTimeout(job.timer); job.reject(error); job.stdout?.error(error); job.stderr?.error(error); }
    pending.clear(); await stopWorker(coordinator); disposeResolve?.();
  }
  listen(coordinator, report => {
    if (report.type === "fatal") { void failAll(new PaludariumError(report.error.kind, report.error.message)); return; }
    if (report.type === "ready") { clearTimeout(initTimer); readyResolve(report); return; }
    if (report.type === "disposed") { void stopWorker(coordinator); disposeResolve?.(); return; }
    const job = pending.get(report.id);
    if (!job) { if (report.type === "failed" && report.id === undefined) void failAll(new PaludariumError(report.error.kind, report.error.message)); return; }
    if (report.type === "output") job[report.stream]?.enqueue(report.bytes);
    else if (report.type === "finished" || report.type === "failed") {
      clearTimeout(job.timer); pending.delete(report.id);
      if (report.type === "failed") { const error = new PaludariumError(report.error.kind, report.error.message); job.stdout?.error(error); job.stderr?.error(error); job.reject(error); }
      else { job.stdout?.close(); job.stderr?.close(); job.resolve(report.status); }
    } else if (report.type === "diagnostics") { pending.delete(report.id); clearTimeout(job.timer); job.resolve(report.diagnostics); }
  }, cause => void failAll(new PaludariumError("internal", String(cause))));
  coordinator.postMessage({ type: "init", module, memory });
  await ready;
  return {
    run(options) {
      validate(options);
      if (closed) throw new PaludariumError("host", "Launcher is closed");
      const id = next++, job = {};
      const stdout = new ReadableStream({ start(controller) { job.stdout = controller; }, cancel() { job.stdout = null; } });
      const stderr = new ReadableStream({ start(controller) { job.stderr = controller; }, cancel() { job.stderr = null; } });
      const exited = new Promise((resolve, reject) => { job.resolve = resolve; job.reject = reject; });
      // The outer thread can terminate a stuck Rust coordinator without acquiring any Rust lock.
      job.timer = setTimeout(() => void failAll(new PaludariumError("host", "30 second production Worker watchdog")), 30000);
      pending.set(id, job);
      coordinator.postMessage({ type: "run", id, options });
      const stdin = new WritableStream({
        write(bytes) { if (!(bytes instanceof Uint8Array)) throw new TypeError("stdin requires Uint8Array"); if (!closed) coordinator.postMessage({ type: "stdin", id, bytes }); },
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
      if (closed) return;
      closed = true;
      await new Promise(resolve => { disposeResolve = resolve; coordinator.postMessage({ type: "dispose" }); setTimeout(() => { void stopWorker(coordinator); resolve(); }, 1000).unref?.(); });
    },
  };
}
