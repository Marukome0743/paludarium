import { test, expect } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { workspaceSourceState } from "../.codex/tools/aidlc-lib.ts";

test("jj metadata updates do not change source identity; real source still does", () => {
  const root = mkdtempSync(join(tmpdir(), "aidlc-jj-source-"));
  try {
    mkdirSync(join(root, ".jj", "working_copy"), { recursive: true });
    mkdirSync(join(root, "nested", ".jj"), { recursive: true });
    writeFileSync(join(root, "main.rs"), "fn main() {}\n");
    writeFileSync(join(root, ".jj.ts"), "export const source = 1;\n");
    writeFileSync(join(root, ".jj", "working_copy", "tree_state"), "before");
    const before = workspaceSourceState(root);
    expect(before).not.toBeNull();
    expect([...before!.listing.keys()].some((key) => key.includes(".jj/"))).toBe(false);
    expect([...before!.listing.keys()].some((key) => key.endsWith(".jj.ts"))).toBe(true);

    writeFileSync(join(root, ".jj", "working_copy", "tree_state"), "after");
    writeFileSync(join(root, "nested", ".jj", "operation"), "new metadata");
    expect(workspaceSourceState(root)?.fingerprint).toBe(before!.fingerprint);

    writeFileSync(join(root, "main.rs"), "fn main() { println!(\"changed\"); }\n");
    expect(workspaceSourceState(root)?.fingerprint).not.toBe(before!.fingerprint);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
