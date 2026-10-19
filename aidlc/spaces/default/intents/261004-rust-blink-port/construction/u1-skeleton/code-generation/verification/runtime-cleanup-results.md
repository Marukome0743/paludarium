# Approved Runtime test cleanup, Step 24b

Verified pre-repair native Windows CI evidence: `windows-host-d238c8d1.log` reports `tests::u7_runtime_mount` failing at `tests.rs:164` with OS error 32 during `remove_dir_all`. `Session::file_system` clones the mount capability Arc, so the Session and its MountedFs both retain the root handle.

The only source change adds `drop(fs); drop(s);` immediately before the existing strict removal in `crates/paludarium-runtime/src/tests.rs::u7_runtime_mount`. Production behavior and cleanup failure assertions are unchanged. This reuses the existing regression rather than adding a duplicate test.

Verified locally with Docker VMM, the pinned nightly, and serialized commands:

| Command | Result | Exact log |
| --- | --- | --- |
| `bash scripts/linux-dev.sh cargo test --locked -p paludarium-runtime --lib tests::u7_runtime_mount -- --exact --nocapture` | 1 passed, 0 failed | `runtime-cleanup-exact.log` |
| `bash scripts/linux-dev.sh cargo test --locked -p paludarium-runtime --lib` | 25 passed, 0 failed | `runtime-cleanup-lib.log` |
| `bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-runtime --all-targets -- -D warnings` | exit 0 | `runtime-cleanup-clippy.log` |
| `bash scripts/linux-dev.sh cargo fmt --all -- --check` | exit 0 | `runtime-cleanup-fmt.log` |

Native Windows validation remains unverified at report creation and is assigned to root-owned CI. Three-platform existing suites, native Linux differential tests, and whole-workspace/U1 coverage gates remain required. No watchdog, toolchain pin, comparison mask, coverage floor, or hook was changed.
