import test from "node:test";
import assert from "node:assert/strict";
import { jitImports } from "../jit-support.mjs";

const section = (id, bytes) => [id, bytes.length, ...bytes];
const word = value => [...new TextEncoder().encode(value)];
function moduleBytes(body = [0x20, 0, 0x42, 42, 0x37, 3, 0, 0x41, 0]) {
  return Uint8Array.from([
    0, 97, 115, 109, 1, 0, 0, 0,
    ...section(1, [1, 0x60, 1, 0x7f, 1, 0x7f]),
    ...section(2, [1, 3, ...word("env"), 6, ...word("memory"), 2, 3, 1, 4]),
    ...section(3, [1, 0]),
    ...section(7, [1, 3, ...word("run"), 0, 0]),
    ...section(10, [1, body.length + 2, 0, ...body, 0x0b]),
  ]);
}
function setup(bytes = moduleBytes()) {
  const memory = new WebAssembly.Memory({ initial: 1, maximum: 4, shared: true });
  new Uint8Array(memory.buffer, 512, bytes.length).set(bytes);
  return { memory, bridge: jitImports(memory), bytes,
    run(key = 1) { return this.bridge.prepare(key, 512, this.bytes.length) === 0
      ? this.bridge.execute(key, 512, this.bytes.length, 64, 144) : -1; } };
}
test("u14 bridge executes actual synchronous shared-memory wasm", () => {
  const s = setup();
  assert.equal(s.run(), 0);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 42n);
});
test("u14 bridge reuses immutable Worker-local compiled module", () => {
  const s = setup();
  assert.equal(s.run(), 0);
  assert.equal(s.run(), 0);
});
test("u14 bridge rejects changed bytes for an existing module ID", () => {
  const s = setup();
  assert.equal(s.run(), 0);
  new Uint8Array(s.memory.buffer)[512] = 1;
  assert.equal(s.run(), -1);
});
test("u14 bridge malformed wasm preserves state", () => {
  const s = setup(Uint8Array.of(1, 2, 3));
  assert.equal(s.run(), -1);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 0n);
});
test("u14 bridge trap rolls back scratch state and permits retry", () => {
  const s = setup(moduleBytes([0x20, 0, 0x42, 42, 0x37, 3, 0, 0]));
  assert.equal(s.run(), -1);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 0n);
  s.bytes = moduleBytes();
  new Uint8Array(s.memory.buffer, 512, s.bytes.length).set(s.bytes);
  assert.equal(s.run(), 0);
});
test("u14 bridge validates buffer range and exact state ABI", () => {
  const s = setup();
  assert.equal(s.bridge.execute(1, 65535, 2, 64, 144), -1);
  assert.equal(s.bridge.execute(1, 512, s.bytes.length, 64, 143), -1);
  assert.equal(s.bridge.execute(0, 512, s.bytes.length, 64, 144), -1);
});
test("u14 bridge remains usable after shared memory growth", () => {
  const s = setup();
  assert.equal(s.run(), 0);
  s.memory.grow(1);
  assert.equal(s.run(), 0);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 42n);
});
test("u14 execution cannot compile an unprepared module", () => {
  const s = setup();
  assert.equal(s.bridge.execute(1, 512, s.bytes.length, 64, 144), -2);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 0n);
  assert.equal(s.bridge.prepare(1, 512, s.bytes.length), 0);
  assert.equal(s.bridge.execute(1, 512, s.bytes.length, 64, 144), 0);
});

import { requireJitProof } from './u14-suite.mjs';
test('u14 provisional observation survives and completed proof has no stale error', () => {
 const row={pass:false,exit:0}; requireJitProof(row);
 assert.equal(row.jit_error,undefined);
 row.jit={executedBlocks:'1',executedInstructions:'2'};row.pass=true;
 requireJitProof(row);assert.equal(row.pass,true);assert.equal(row.jit_error,undefined);
});
test('u14 final fallback-only and original failure remain failures', () => {
 const missing={pass:true,exit:0};requireJitProof(missing);assert.equal(missing.pass,false);
 const failed={pass:false,timed_out:true,error:'original timeout'};
 requireJitProof(failed);assert.equal(failed.error,'original timeout');assert.equal(failed.pass,false);
});
