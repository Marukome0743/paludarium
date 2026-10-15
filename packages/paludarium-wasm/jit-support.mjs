// Synchronous compiler/executor owned by one existing guest Worker. Pointers
// address trusted Rust scratch buffers, never guest virtual memory.
export const COST_FIELDS = [
  "hookAttempts", "checkpoints", "cacheHits", "negativeHits", "cacheMisses", "epochInvalidations",
  "lruUpdates", "snapshotBytes", "translatedBlocks", "executedBlocks", "executedInstructions", "fallbacks",
  "prepareCalls", "executeCalls", "compileAttempts", "compileNanoseconds", "jsTransitions",
  "comparisonBytesUpperBound", "codeBytesCopied", "stateBytesCopied", "prepareRejections", "executeRejections",
  "interpreterSteps", "budgetCharged", ...Array.from({ length: 64 }, (_, i) => `blockLength${i + 1}`),
  "observationLookups", "observationBytes", "nextPositive", "nextPrepared", "nextMissing",
  "nextNegative", "nextEpoch", "nextUnprepared", "nextUnavailable", "chainLength1", "chainLength2",
  "chainLength3", "chainLength4to7", "chainLength8plus", "stopUnsupported", "stopNegative",
  "stopFallback", "stopEpoch", "stopBudget", "stopExit", "stopKill",
];
export function costSnapshot(exports) {
  if (typeof exports.u14_cost_version !== "function") return null;
  if (exports.u14_cost_version() !== 2 || exports.u14_cost_fields() !== COST_FIELDS.length) throw Error("Diagnostic ABI mismatch");
  return { schema: 2, purpose: "u14-cost-profile", overflow: exports.u14_cost_overflow() !== 0,
    counters: Object.fromEntries(COST_FIELDS.map((name, index) => [name, String(exports.u14_cost_stat(index))])) };
}
export function jitImports(memory, cost = null, now = () => performance.now()) {
  const compiled = new Map();
  let running = false;
  const range = (pointer, length) => Number.isInteger(pointer) && pointer > 0
    && Number.isInteger(length) && length > 0 && pointer + length <= memory.buffer.byteLength;
  return {
    prepare(key, codePointer, codeLength) {
      if (running || !Number.isInteger(key) || key <= 0 || codeLength > 65536
          || !range(codePointer, codeLength)) return -1;
      const view = new Uint8Array(memory.buffer, codePointer, codeLength);
      try {
        const entry = compiled.get(key);
        if (entry) {
          if (cost) cost(17, view.length);
          if (entry.bytes.length !== view.length || entry.bytes.some((value, i) => value !== view[i])) return -1;
          compiled.delete(key); compiled.set(key, entry);
          return 0;
        }
        const bytes = view.slice();
        if (cost) cost(18, bytes.length);
        const started = cost ? now() : 0;
        let instance;
        try {
          const module = new WebAssembly.Module(bytes);
          instance = new WebAssembly.Instance(module, { env: { memory } });
        } finally {
          if (cost) { cost(14, 1); cost(15, Math.round(Math.max(0, now() - started) * 1e6)); }
        }
        if (typeof instance.exports.run !== "function") return -1;
        if (compiled.size >= 1024) compiled.delete(compiled.keys().next().value);
        compiled.set(key, { bytes, run: instance.exports.run });
        return 0;
      } catch { return -1; }
    },
    execute(key, codePointer, codeLength, statePointer, stateLength) {
      // Diagnostic-only query: never prepare, run, evict, touch recency, or
      // access scratch. Ordinary imports reject this sentinel below.
      if (cost && statePointer === 0 && stateLength === 0) {
        if (running || !Number.isInteger(key) || key <= 0 || codeLength > 65536
            || !range(codePointer, codeLength)) return -1;
        cost(88, 1);
        const entry = compiled.get(key);
        if (!entry) return -2;
        const bytes = new Uint8Array(memory.buffer, codePointer, codeLength);
        cost(89, bytes.length);
        return entry.bytes.length === bytes.length && entry.bytes.every((value, i) => value === bytes[i]) ? 0 : -1;
      }
      if (running || !Number.isInteger(key) || key <= 0 || codeLength > 65536
          || stateLength !== 144 || !range(codePointer, codeLength) || !range(statePointer, stateLength)) return -1;
      // A module ID is allocated in shared Rust and never reused. Each Worker
      // separately compiles it; JS objects/handles never cross Worker boundaries.
      const entry = compiled.get(key);
      if (!entry) return -2;
      const bytes = new Uint8Array(memory.buffer, codePointer, codeLength);
      if (cost) cost(17, bytes.length);
      if (entry.bytes.length !== bytes.length || entry.bytes.some((value, i) => value !== bytes[i])) return -1;
      const before = new Uint8Array(memory.buffer, statePointer, stateLength).slice();
      if (cost) cost(19, stateLength);
      compiled.delete(key); compiled.set(key, entry);
      running = true;
      try {
        if (entry.run(statePointer) !== 0) throw new Error("JIT result rejected");
        return 0;
      } catch {
        new Uint8Array(memory.buffer, statePointer, stateLength).set(before);
        compiled.delete(key);
        return -1;
      } finally { running = false; }
    },
  };
}
