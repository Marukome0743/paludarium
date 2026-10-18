## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19
**Scope:** entry-f.py (SHA-256 18567771…a46f), binding-e05f.json (5c9d99de…7fc0), test_entry_f.py, compared with entry-e.py and binding-e05.json. test_entry_f.py was not re-run.

(Process note: Grep is not available here, so I used read-only shell commands: `diff entry-e.py entry-f.py`, `diff binding-e05.json binding-e05f.json`, `shasum`, `ls` and `grep`. Nothing else was executed or written except this file.)

### Conclusion

All four points the coordinator asked about hold. There are no Critical or Major findings. There are 2 Minor findings, both about the regression set, and 2 notes.

### Answers to the four questions

**(1) Minor 1 (replace refs): fixed, no finding.**
- entry-f.py:130-131. `GIT_ARGS` now starts with `--no-replace-objects`, and `git_env()` (:167-171) sets `GIT_NO_REPLACE_OBJECTS=1`.
- The `diff` shows the file has exactly two places that start git: `git()` (:174) and `git_has_commit()` (:184-185). Both build the command from `GIT_ARGS` and the environment from `git_env()`. No third call site exists, so every git call carries both guards.
- `verify_repository_state()` (:188-197) refuses a shallow repository (`rev-parse --is-shallow-repository` must print `false`) and a graft file (`rev-parse --git-path info/grafts` must not exist, not even as a symlink). It is called in `verify()` at :541, as stage "(1a)", before `verify_lineage` (:542), `verify_changed` (:543) and `verify_working_copy` (:546). Stages (0) and (4) before it read only stored files and call no git, so nothing that asks git about commits runs ahead of it.
- Both new git calls use `rev-parse`, which is in `GIT_READ_ONLY`.

**(2) Minor 3 (no dependence on a pre-push commit id): fixed, no finding.**
- test_entry_f.py:66-88 builds a temporary repository under the entry folder (root commit A, commit B with 351 changed files, 350 inside aidlc/ and `docs/x.md`, and commit C used only as a replacement). `tearDownClass` removes it (:122-123).
- Tests 28 and 31 now use this fixture through `mock.patch.object(E,'ROOT',...)` (:124, :261-270, :282-290). The 300-file case is still covered (351 files).
- The only fixed commit ids left are `E.BASE` (e3c29d1d) and `PARENT` a54315f9 (:39). Both are already pushed. The text a7aecb72 appears only in the module docstring (:7), as history.
- test_10 (:184-199) builds a real replace ref in the fixture and checks it against plain git as a control (:190-191). It confirms that `git_tree` and `git_parents` return the real tree and parents, and that a record carrying the replaced tree is refused (:197).
- test_11 (graft), test_12 (shallow clone) and test_13 (the stage runs before the lineage in `verify`) cover the new state check.

**(3) Did any check disappear from entry-e? No.**
The `diff` shows these changes only:
- SCHEMA `f1`, USAGE, the module docstring and the DECISION_F/REVIEW_F texts;
- `--no-replace-objects` and `GIT_NO_REPLACE_OBJECTS`;
- the new `verify_repository_state` and its stage line;
- four more HISTORY pins;
- a new claimed line;
- result key renames (`_e` to `_f`) and the new `repository_state` key.

`verify_lineage`, `verify_changed`, working copy, CI, performance, upstream and base records are byte-for-byte unchanged. binding-e05f differs from binding-e05 only in schema, purpose, approval and the same four history entries.

**(4) History pins: complete, no finding.**
HISTORY (entry-f.py:70-99) now holds entry-e.py, binding-e05.json, test_entry_e.py and commits-e3c29d1d.json. That makes 28 entries (12 from v1-v4, plus 5 entries, 5 bindings, 5 tests and the commit record, 16). The values equal the shasum results (entry-e c362be77…, binding-e05 6fa27506…, test_entry_e 6a160459…, commits 0f5d4624…). binding-e05f has the same four additions, and `check_binding_shape` requires equality with HISTORY.

### New findings

| Severity | Location | Finding | Required action |
|---|---|---|---|
| Minor | test_entry_f.py:226-352 (compared with test_entry_e.py) | test_entry_f.py is a trimmed copy of test_entry_e.py, not a superset. Cases for checks that entry-f.py still contains are gone: chain-ends and order check "from the base to the head" (e test_23 second case), a stored record with a missing `tree` field or non-list `parents`, the mocked other-parent case, the `commit_records` key-set and `repository` checks (e test_26), the "sorted unique" product-list case, `list_digest` (e test_33), the `paths_bytes_may_differ` loosening case (e test_44), the `tools/aidlc-recoveryX` and extra-crate-file unexpected-path cases (e test_42), the rerun "failed job differs" case, the performance "passed is not true" and "stored API digest" cases, and the earlier-binding cases e01 and e02. The README says every check of version e stays, which is true of the code, but those checks now have no regression against entry-f.py. test_entry_e.py still passes only against entry-e.py. Because the functions are byte-identical (see question 3), the risk is low. | Restore the dropped cases in a later test file, or add a short statement to the README listing which e regressions are not carried over and why the code identity covers them. |
| Minor | test_entry_f.py:184-199 | test_10 would still pass if only one of the two guards were removed, because `--no-replace-objects` and `GIT_NO_REPLACE_OBJECTS=1` each prevent following the replace ref on their own. The test asserts both are present (:185) but does not show that each is effective on its own. `git_has_commit` (used for the upstream head) is never run against a replace ref. | Add a case per guard: patch out one at a time and show the fixture still returns the real tree. Optional, because a missing guard would be caught by the first assertion at :185. |
| Note | entry-f.py:188-197 and test_entry_f.py:200-206 | test_11 proves that the check refuses a file at `info/grafts`, but not that the installed git honours that file. Modern git may ignore grafts. The refusal is therefore a safe over-approximation, not an observed attack. | None. |
| Note | entry-f.py:564-585 | Same as in review 03: the entry bytes and the bindings are pinned from the working copy, not from the pushed head tree, and aidlc/ file content is not compared. This is in the not_claimed list. | None. |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| shasum entry-f.py, binding-e05f.json, entry-e.py, test_entry_e.py, binding-e05.json | match the values in HISTORY and the README | Pins consistent. |
| diff entry-e.py entry-f.py | only the changes listed under question 3 | No check removed. |
| diff binding-e05.json binding-e05f.json | schema, purpose, approval, +4 history pins | The binding says what the entry requires. |
| test_entry_f.py (34 test methods counted) | not re-run, as instructed | The passing result is the author's report. |

### Summary

Version f fixes both Minor findings of review 03 correctly and drops no check of version e. Every git call is guarded, the shallow and graft refusal runs before the lineage, the temporary-repository tests do not depend on pushed or unpushed local ids, and the history pins contain the full version e set. Open items are Minor and concern only the regression set.
