// Synchronous compiler/executor owned by one existing guest Worker. Pointers
// address trusted Rust scratch buffers, never guest virtual memory.
export function jitImports(memory) {
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
          if (entry.bytes.length !== view.length || entry.bytes.some((value, i) => value !== view[i])) return -1;
          compiled.delete(key); compiled.set(key, entry);
          return 0;
        }
        const bytes = view.slice();
        const module = new WebAssembly.Module(bytes);
        const instance = new WebAssembly.Instance(module, { env: { memory } });
        if (typeof instance.exports.run !== "function") return -1;
        if (compiled.size >= 1024) compiled.delete(compiled.keys().next().value);
        compiled.set(key, { bytes, run: instance.exports.run });
        return 0;
      } catch { return -1; }
    },
    execute(key, codePointer, codeLength, statePointer, stateLength) {
      if (running || !Number.isInteger(key) || key <= 0 || codeLength > 65536
          || stateLength !== 144 || !range(codePointer, codeLength) || !range(statePointer, stateLength)) return -1;
      // A module ID is allocated in shared Rust and never reused. Each Worker
      // separately compiles it; JS objects/handles never cross Worker boundaries.
      const bytes = new Uint8Array(memory.buffer, codePointer, codeLength).slice();
      const before = new Uint8Array(memory.buffer, statePointer, stateLength).slice();
      running = true;
      try {
        let entry = compiled.get(key);
        if (entry && (entry.bytes.length !== bytes.length || entry.bytes.some((value, i) => value !== bytes[i]))) return -1;
        if (!entry) return -1;
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
