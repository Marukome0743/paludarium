# Issue title

[Bug]: Code Generation summary-confirmation receipt blocked by Plan Approval guard before the plan exists (Codex, 2.11.0)

### Description

Code Generation gets stuck **before its plan is written** when summary confirmation and Plan Approval are both enabled. The human has answered “Looks correct”, but recording that prerequisite confirmation is refused by the `plan-approval-guard` PreToolUse hook because the plan does not exist yet.

The prescribed ordering becomes circular:

1. Record summary confirmation before generating the planning artifacts.
2. The execution guard demands an approved plan before allowing that confirmation-recording command.

This was reproduced in a live Codex desktop session. The **same command succeeded from the user's external terminal**, and emitted `SUMMARY_CONFIRMATION_RECORDED` for the intended unit. This separates the observed pre-execution rejection from a failure inside the answer handler.

### Steps to Reproduce

1. Use AI-DLC 2.11.0 with the Codex harness.
2. Reach a per-unit `code-generation` run-stage with summary confirmation **on**, Plan Approval **on**, and no `code-generation-plan.md` yet. Observed configuration: custom scope, Standard depth, unit-major, serial, gated Construction, Guard Policy relaxed.
3. Create an in-record questions file with `## Consolidated Summary Confirmation`, ask the person to confirm the unit's scope before writing the plan and test instructions, and receive “Looks correct”.
4. Write `[Answer]: Looks correct` in that questions file.
5. Execute the following through the agent's shell tool, substituting the active record and unit:

```sh
aidlc engine log answer --stage code-generation --checkpoint summary-confirmation --questions-file aidlc/spaces/default/intents/<intent>/construction/<unit>/code-generation/planning-confirmation-questions.md --details 'Looks correct' --unit <unit>
```

6. Observe the PreToolUse rejection below. The command does not execute.
7. As a diagnostic/workaround, have the person run the identical command from an external terminal in the project directory. In the observed session it succeeded and wrote the confirmation event.

### Expected Behavior

The summary-confirmation record operation is a prerequisite to planning and should be admitted before Plan Approval, with the log handler continuing to validate the human reply, questions file, active stage, and unit.

Developer dispatch and application-source mutations must remain blocked until a current Plan Approval is present. Recording summary confirmation must not grant Plan Approval.

### Actual Behavior

The agent's shell tool returned:

```text
Command blocked by PreToolUse hook: Code generation cannot run mutation-capable shell commands for unit u8-process-spawn because the plan, unit-test instructions, and current Testing Contract do not have a current matching approval. Reason: code-generation-plan.md is missing or empty. Writes inside the selected code-generation record directory remain available for planning. When the plan is ready, run `aidlc engine orchestrate next` exactly as written, as a command of its own (no `cd` before it, no pipe or second command after it): the engine asks the person to approve it before any code is written. The plan-approval setting is unchanged.
```

The external-terminal run subsequently produced this audit evidence (unrelated identifiers omitted):

```text
**Timestamp**: 2026-10-09T19:39:35Z
**Event**: SUMMARY_CONFIRMATION_RECORDED
**Stage**: code-generation
**Details**: Looks correct
**Checkpoint**: Consolidated Summary Confirmation
**Questions File**: aidlc/spaces/default/intents/<intent>/construction/u8-process-spawn/code-generation/planning-confirmation-questions.md
**Hash Scope**: confirmed-content-v2
**Unit**: u8-process-spawn
```

### AI-DLC Version

v2

### Release / Commit

`aidlc version` output: `aidlc 2.11.0 (runtime 2.11.0)`.

The relevant allowlist condition was also inspected on public `main` during this investigation; it still admitted only the `plan-approval` checkpoint. No execution reproduction against a newly built main binary has been performed.

### AI-DLC Phase

Construction

### Harness

Codex CLI (Codex desktop app using the Codex harness)

### AI Model

GPT-6 family; exact selected model identifier was not captured for this report.

### Environment

- OS: macOS
- Shell: zsh
- Native AI-DLC installation, version/runtime 2.11.0
- Per-unit Code Generation; active unit `u8-process-spawn`
- Summary confirmation on; Plan Approval on; Guard Policy relaxed
- Codex app/CLI version and macOS version were not captured.

### Additional Context

#### Cause identified from source inspection

The project's `.codex/hooks.json` registers this command under **PreToolUse**, not PostToolUse:

```text
aidlc engine adapter codex plan-approval-guard
```

The native engine is therefore the executed hook; editing the project's mirrored TypeScript alone does not alter that execution path.

In the plan-approval prerequisite allowlist, the `log decision` / `log answer` branch currently requires:

```ts
const routeArgs = args.slice(3);
return (
  lastFlagValue(routeArgs, "--stage") === GUARDED_STAGE &&
  lastFlagValue(routeArgs, "--checkpoint") === "plan-approval"
);
```

Thus the required `summary-confirmation` answer falls outside this admitted branch and is treated as a mutation needing the approval it precedes.

Source: [core/hooks/aidlc-plan-approval-guard.ts](https://github.com/awslabs/aidlc-workflows/blob/main/core/hooks/aidlc-plan-approval-guard.ts).
The pre-generation summary stop is required by the installed AI-DLC skill: artifacts must not be generated until the Looks correct answer is written **and the recording receipt succeeds**.

The live rejection and external success are directly observed. The omitted prerequisite allowlist entry is the source-supported cause; the compiled binary's internal implementation was not independently instrumented.

#### Proposed fix

Admit both `plan-approval` and `summary-confirmation` for this narrow `code-generation` `log decision|answer` prerequisite branch, retaining the existing command parsing and stage checks. For example:

```ts
lastFlagValue(routeArgs, "--stage") === GUARDED_STAGE &&
["plan-approval", "summary-confirmation"].includes(
  lastFlagValue(routeArgs, "--checkpoint") ?? "",
)
```

This is a proposed change, **not a tested fix**. The actual handler must retain all existing confirmation validation. Ship the fix in the native executable through the normal release/configuration path.

Suggested regression coverage:

- With the plan missing and no Plan Approval, the exact native `log answer --stage code-generation --checkpoint summary-confirmation` command passes PreToolUse admission.
- The corresponding `log decision` command passes as well.
- Invalid or missing confirmation evidence remains rejected by the log handler.
- Other checkpoints and stages do not gain a broad mutation exemption.
- Unapproved source edits and developer dispatch remain refused after summary confirmation is recorded.
- Exercise the packaged executable/adapter path, not only source-level tests.

#### Current workaround

The person records the already-given summary response using the same official command in an external terminal; Plan Approval stays enabled. This worked for the observed confirmation-recording step. Subsequent full-stage completion is **not yet verified**.

#### Related issues

- #1598: same family of prerequisite/lifecycle allowlist omissions, but for park/unpark rather than summary confirmation.
- #1549: approval/recovery deadlock on Kiro IDE/Windows; different observed failure path.

No exact duplicate for this summary-confirmation command rejection was found in the searches performed.

