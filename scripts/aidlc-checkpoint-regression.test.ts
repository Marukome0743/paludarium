import { expect, test } from "bun:test";
import { loadConstructionEvidence, resolveConstructionCheckpoint } from "../.codex/tools/aidlc-construction-checkpoints.ts";
import { findStageBySlug, freshReviewReceipts, readStateFile, reviewAttemptWindow, setField } from "../.codex/tools/aidlc-lib.ts";

const project = process.cwd();
const unit = "u1-skeleton";

test("relaxed checkpoint respects the authenticated review scanner after source drift", () => {
  const evidence = loadConstructionEvidence(project);
  const stage = findStageBySlug("code-generation")!;
  const receipts = freshReviewReceipts(project, evidence.evidenceState, stage, {
    boltDag: evidence.dag,
    reviewClass: "adversarial",
    attemptWindow: reviewAttemptWindow(project, evidence.evidenceState, stage, evidence.allRows),
    sourceState: evidence.source,
  });
  console.log(JSON.stringify({ verdict: receipts.unitVerdicts.get(unit), stale: receipts.unitStale.has(unit), changes: receipts.acceptedChanges.filter(change => change.unit === unit) }));
  expect(receipts.unitVerdicts.get(unit)).toBe("READY");
  expect(receipts.unitStale.has(unit)).toBe(false);
  const checkpoint = resolveConstructionCheckpoint(project, unit, "skeleton", evidence.state, evidence);
  expect(checkpoint.errors).toEqual([]);
  expect(checkpoint.ready).toBe(true);
  // The changed source still needs a new command run and human approval.
  expect(checkpoint.verified).toBe(false);
  expect(checkpoint.approved).toBe(false);
});

test("strict checkpoint continues to refuse changed reviewed source", () => {
  const state = setField(readStateFile(project), "Guard Policy", "strict");
  const checkpoint = resolveConstructionCheckpoint(project, unit, "skeleton", state);
  expect(checkpoint.ready).toBe(false);
  expect(checkpoint.errors.some(error => error.includes("terminal review evidence"))).toBe(true);
});
