import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { COST_FIELDS, costSnapshot, jitImports } from "../jit-support.mjs";
import { validateBuildReceipt, validateProfileReport } from "./u14-cost-profile-check.mjs";

const hash = bytes => createHash("sha256").update(bytes).digest("hex");
const locks = ["Cargo.lock", "fuzz/Cargo.lock", "tests/guests/u10/source-lock.json", "tests/guests/u10/probe/Cargo.lock", "rust-toolchain.toml", "deny.toml"];
function build() {
  const source_files = Object.fromEntries(locks.sort().map(name => [name, "1".repeat(64)]));
  const source_digest = hash(JSON.stringify(source_files));
  return { schema: 1, purpose: "u14-cost-profile", features: ["u14-cost-profile"],
    source_files, source_digest, module_sha256: "2".repeat(64), locks: { ...source_files },
    local_snapshot: true, head: "local:" + source_digest };
}
const receipt = build();
const identity = { head: receipt.head, module_sha256: receipt.module_sha256,
  source_digest: receipt.source_digest, oracle_sha256: "3".repeat(64), probe_sha256: "4".repeat(64) };
function report() {
  const rows = [false, true].map(jit => {
    const counters = Object.fromEntries(COST_FIELDS.map(name => [name, "0"]));
    counters.checkpoints = "1";
    if (jit) Object.assign(counters, { executedBlocks: "1", executedInstructions: "2", compileAttempts: "1", jsTransitions: "2", blockLength2: "1" });
    return { jit, pass: true, exit: 0, timed_out: false, errors: [], seconds: 1, cleaned: true,
      costProfile: { schema: 1, purpose: "u14-cost-profile", overflow: false, counters } };
  });
  return { schema: 1, purpose: "u14-cost-profile", performanceAcceptance: false, ...identity, complete: true, rows };
}
const rejectReport = change => { const r = report(); change(r); assert.throws(() => validateProfileReport(r, identity)); };
test("cost runner accepts exact two diagnostic observations without claiming performance", () => {
  validateBuildReceipt(build(), receipt.module_sha256);
  assert.equal(validateProfileReport(report(), identity), true);
});
test("cost runner rejects ordinary acceptance receipt or missing feature", () => {
  for (const change of [r => r.purpose = "u14-acceptance-control", r => r.features = []]) {
    const r = build(); change(r); assert.throws(() => validateBuildReceipt(r, receipt.module_sha256));
  }
});
test("cost runner rejects wrong module or external CI head", () => {
  assert.throws(() => validateBuildReceipt(build(), "5".repeat(64)));
  const r = build(); r.local_snapshot = false; r.head = "a".repeat(40);
  assert.throws(() => validateBuildReceipt(r, receipt.module_sha256, "b".repeat(40)));
});
test("cost runner rejects missing/changed source closure and lock", () => {
  for (const change of [r => delete r.source_files, r => r.source_files["Cargo.lock"] = "8".repeat(64), r => r.locks["Cargo.lock"] = "9".repeat(64)]) {
    const r = build(); change(r); assert.throws(() => validateBuildReceipt(r, receipt.module_sha256));
  }
});
test("cost runner rejects unsafe source paths even when self-digest matches", () => {
  const r = build(); r.source_files["../outside"] = "1".repeat(64);
  r.source_digest = hash(JSON.stringify(Object.fromEntries(Object.entries(r.source_files).sort())));
  assert.throws(() => validateBuildReceipt(r, receipt.module_sha256));
});
test("cost runner rejects incomplete/duplicate/extra mode observations", () => {
  for (const change of [r => r.complete = false, r => r.rows.pop(), r => r.rows.push(r.rows[0]), r => r.rows.reverse()]) rejectReport(change);
});
test("cost runner rejects cross-module/head/oracle/report substitutions", () => {
  for (const key of Object.keys(identity)) rejectReport(r => r[key] = "different");
});
test("cost runner rejects missing counter, overflow and invalid integer", () => {
  for (const change of [r => delete r.rows[1].costProfile.counters.cacheHits,
    r => r.rows[1].costProfile.overflow = true, r => r.rows[1].costProfile.counters.cacheHits = "-1",
    r => r.rows[1].costProfile.counters.cacheHits = "18446744073709551616"]) rejectReport(change);
});
test("cost runner rejects guest failure/timeout/cleanup/nonfinite durations", () => {
  for (const change of [r => r.rows[0].timed_out = true, r => r.rows[1].exit = 1,
    r => r.rows[0].cleaned = false, r => r.rows[1].seconds = 30.01,
    r => r.rows[1].seconds = NaN, r => r.rows[0].errors.push("failure")]) rejectReport(change);
});
test("cost runner rejects fallback-only and inconsistent block histogram", () => {
  rejectReport(r => r.rows[1].costProfile.counters.executedBlocks = "0");
  rejectReport(r => r.rows[1].costProfile.counters.blockLength2 = "0");
});
test("cost runner rejects diagnostic/performance receipt conflation", () => {
  rejectReport(r => r.performanceAcceptance = true);
  rejectReport(r => r.purpose = "performance");
});

const bytes = Buffer.from("0061736d0100000001060160017f017f030201000707010372756e00000a0601040041000b", "hex");
function bridge(cost, now) {
  const memory = new WebAssembly.Memory({ initial: 1, maximum: 1, shared: true });
  new Uint8Array(memory.buffer, 512, bytes.length).set(bytes);
  return { memory, jit: jitImports(memory, cost, now) };
}
test("cost collector disabled path never reads clock or calls diagnostic exports", () => {
  const s = bridge(null, () => { throw Error("disabled clock"); });
  assert.equal(s.jit.prepare(1, 512, bytes.length), 0);
  assert.equal(s.jit.execute(1, 512, bytes.length, 64, 144), 0);
});
test("cost collector times only cold actual compilation and counts bytes separately", () => {
  const counters = Array(88).fill(0), times = [10, 11];
  const s = bridge((field, value) => { counters[field] += value; }, () => times.shift());
  assert.equal(s.jit.prepare(1, 512, bytes.length), 0);
  assert.equal(s.jit.execute(1, 512, bytes.length, 64, 144), 0);
  assert.equal(s.jit.prepare(1, 512, bytes.length), 0);
  assert.equal(s.jit.execute(1, 512, bytes.length, 64, 144), 0);
  assert.equal(counters[14], 1); assert.equal(counters[15], 1000000);
  assert.equal(counters[18], bytes.length); assert.equal(counters[19], 288);
  assert.equal(times.length, 0);
});
test("cost collector records failed cold compilation while preserving state", () => {
  const counters = Array(88).fill(0);
  const s = bridge((field, value) => counters[field] += value, () => 1);
  new Uint8Array(s.memory.buffer)[512] = 1;
  assert.equal(s.jit.prepare(1, 512, bytes.length), -1);
  assert.equal(counters[14], 1);
  assert.equal(new BigUint64Array(s.memory.buffer, 64, 18)[0], 0n);
});
test("cost snapshot refuses wrong ABI and has no ordinary-module fallback claim", () => {
  assert.equal(costSnapshot({}), null);
  assert.throws(() => costSnapshot({ u14_cost_version: () => 2 }));
  assert.throws(() => costSnapshot({ u14_cost_version: () => 1, u14_cost_fields: () => 0 }));
});
test("cost snapshot retains overflow for fail-closed report validation", () => {
  const s = costSnapshot({ u14_cost_version: () => 1, u14_cost_fields: () => 88,
    u14_cost_overflow: () => 1, u14_cost_stat: () => 0n });
  assert.equal(s.overflow, true);
  assert.equal(Object.keys(s.counters).length, 88);
});
