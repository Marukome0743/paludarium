import test from "node:test";
import assert from "node:assert/strict";
import { imports } from "../worker-support.mjs";

test("random import uses ordinary crypto views and copies all chunks into shared memory", () => {
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, "crypto");
  const sizes = [];
  Object.defineProperty(globalThis, "crypto", { configurable: true, value: {
    getRandomValues(view) {
      assert.ok(view.buffer instanceof ArrayBuffer);
      assert.ok(view.length <= 65536);
      sizes.push(view.length); view.fill(19); return view;
    },
  } });
  try {
    const memory = new WebAssembly.Memory({ initial: 2, maximum: 2, shared: true });
    const random = imports(memory).paludarium.random_fill;
    assert.equal(random(8, 70000), 0);
    assert.deepEqual(sizes, [65536, 4464]);
    assert.ok(new Uint8Array(memory.buffer, 8, 70000).every(byte => byte === 19));
    assert.equal(random(131072, 1), -1);
  } finally { Object.defineProperty(globalThis, "crypto", descriptor); }
});

test("random import reports secure entropy failure", () => {
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, "crypto");
  Object.defineProperty(globalThis, "crypto", { configurable: true, value: {
    getRandomValues() { throw new Error("entropy unavailable"); },
  } });
  try {
    const memory = new WebAssembly.Memory({ initial: 1, maximum: 1, shared: true });
    assert.equal(imports(memory).paludarium.random_fill(0, 16), -1);
  } finally { Object.defineProperty(globalThis, "crypto", descriptor); }
});
