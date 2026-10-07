# VFS fixture cleanup, Step 24c

The current tool-produced brief authorizes this scoped continuation with the plan-approval fence off; this is not a new human approval. Its Testing Contract remains unchanged.

Verified prior native Windows evidence: `runtime-windows-2a8fe818.log` shows Runtime's 25 tests passing, followed by VFS mount's 16 tests failing in the shared Fixture Drop at `mount.rs:366` with OS error 32. The fixture retained its MountedFs and native mount root until after directory removal.

The only source change is in the test-only `Fixture::drop` in `crates/paludarium-vfs/src/mount.rs`: replace its MountedFs with an empty instance and drop the previous instance before the unchanged strict `remove_dir_all(...).unwrap()`. Production mount behavior, all 16 test assertions, and cleanup failure reporting are retained. A read-only search of VFS source found no other directory cleanup sites to repair.

Verified locally using serialized Docker VMM commands and the existing pinned nightly:

| Command | Result | Exact log |
| --- | --- | --- |
| `bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib mount::u7_mount_tests -- --nocapture` | 16 passed, 0 failed | `vfs-cleanup-mount.log` |
| `bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib` | 45 passed, 0 failed | `vfs-cleanup-lib.log` |
| `bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-vfs --all-targets -- -D warnings` | exit 0 | `vfs-cleanup-clippy.log` |
| `bash scripts/linux-dev.sh cargo fmt --all -- --check` | exit 0 | `vfs-cleanup-fmt.log` |

Native Windows confirmation remains unverified at report creation and belongs to root-owned three-platform CI. Existing native Linux differential and both 80% coverage gates remain required. No toolchain, watchdog, comparison mask, capability behavior, or hook changed.
