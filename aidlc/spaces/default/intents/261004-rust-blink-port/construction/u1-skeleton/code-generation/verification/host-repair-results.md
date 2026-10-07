# Approved Host repair, Step 24a

## Observed failures before repair

Verified native CI evidence is retained in `native-final-mac-e0818962.log` and `native-final-windows-e0818962.log`. macOS lock contention returned host errno 35 rather than guest EAGAIN 11. Windows lock contention returned host error 33, and hardlink metadata reported 1 rather than 2 links. Windows fixture teardown attempted to remove its directory while the retained capability root was alive and failed with error 32. These observations justify the scoped translation, metadata, and fixture fixes; the teardown failure does not establish an I/O operation failure.

## Implementation

`native_fs.rs` preserves exact Linux raw errno values and translates other hosts through error kinds into Linux guest errno values. Lock contention uses fs2's native contention error, including Windows ERROR_LOCK_VIOLATION. Unix fcntl errors use the same conversion without changing flag behavior.

Windows file and capability metadata read the actual number of links. Missing link metadata returns EIO instead of inventing a count. Directory enumeration retains its existing inode/type behavior and does not request unavailable link counts or reopen paths through ambient authority. `lib.rs` enables the pinned nightly's `windows_by_handle` feature on Windows only.

Test fixtures explicitly drop their retained root before directory removal; cleanup failures still fail the test. Existing capability escape and bounded rename-race tests remain enabled. Added internal tests were written after implementation, as required by the authoritative custom Testing Contract. The hardlink test now checks both path and open-file metadata before and after unlink.

## Documentation grounds

[Rust Windows MetadataExt](https://doc.rust-lang.org/std/os/windows/fs/trait.MetadataExt.html) documents `number_of_links` and the nightly `windows_by_handle` feature; metadata obtained from directory entries can omit this field. The locked cap-primitives 4.0.3 source was inspected: its Windows MetadataExt exposes the link count and its build script probes the corresponding nightly feature. No dependency or toolchain pin changed.

[fs2 lock_contended_error](https://docs.rs/fs2/0.4.3/fs2/fn.lock_contended_error.html) provides the platform's lock contention error. This is used directly rather than assuming Windows categorizes contention as WouldBlock.

## Local verification

Verified on Docker VMM Linux using the existing serialized development script and pinned toolchain:

| Command after `bash scripts/linux-dev.sh` | Result | Evidence |
| --- | --- | --- |
| `cargo test --locked -p paludarium-host --lib native_fs::u7_tests -- --nocapture` | 11 passed, 0 failed | `host-local-u7.log` |
| `cargo test --locked -p paludarium-host --lib` | 25 passed, 0 failed | `host-local-all.log` |
| `cargo clippy --locked -p paludarium-host --all-targets -- -D warnings` | exit 0 | `host-local-clippy.log` |
| `cargo fmt --all -- --check` | exit 0 | `host-local-fmt-check.log` |

The race child separately reports one passing test; it is included in the parent totals above, not an additional parent test. Native macOS and Windows results are unverified at this report's creation and require the root-owned three-platform CI run. No platform assertion, cleanup error, coverage threshold, watchdog, flag mask, or capability boundary was relaxed.
