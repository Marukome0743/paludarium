# U10 source and behavior review

## Standard probe inventory

Read-only comparison with formicarium/guest/probe/src/main.rs. The eight standard names and acceptance conditions are preserved; additional diagnostic-only checks in that project are outside its standard CHECKS list. No source implementation is copied.

| Name | Condition |
|---|---|
| tokio-timer | Four-worker multi-thread runtime; 50ms sleep in [50ms, 2s]; five 10ms interval ticks within 10s |
| unix-stream-pair | One MiB transfer with matching bytes and EOF |
| rayon | Four-worker parallel sum of 0..1,000,000 = 499999500000 |
| mutex-condvar | Four threads increment 10,000 each; 1,000 ping-pong round trips within 10s |
| fs-basic | Create/write/read/rename/read_dir and cleanup |
| fs-hardlink | nlink=2 and shared content |
| fs-symlink | readlink and content via symlink |
| fs-flock | Independent fd conflicts EWOULDBLOCK, then acquires after unlock |

## Fixed aube and background

Official source https://github.com/aubepkg/aube at v2.6.1, bd94e42f54d3b5e3dd102716b7197f316cb5f4ed. Historical lock hash 8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668. The build receipt under docs/u2/inventory/rebuild/ records an empty AUBE_PRIMER_PATH file and an unmodified-source release --locked x86_64-unknown-linux-musl build. U10 generates new evidence rather than claiming historical builder provenance.

#1645 fixture behavior: app depends on file:./filedep (1.0.0) and link:../outside/linked (2.0.0). Run install, remove node_modules, frozen install, then list; frozen/list must reproduce 0.0.0 natively before differential implementation. The upstream Issue web fetch was unavailable; this contract is supported by the local session fixture and historical native logs, and must be newly observed.

CheerpX background from knowledge/documents/research/cheerpx-oss.md: version 1.3.9, i586/glibc 2.28 with statx preload shim, hidden page, four page loads. version 0.3–0.7s; install 1.8–5.7s; frozen 1.3–3.6s; list 0.17–0.65s. These historical, different-host values are context, not speed acceptance thresholds.

## Contracts and supply chain

C11 CLI accepts env and bounded explicit mounts but no cwd option. U10 uses C10 Session with default VFS and bounded fixture mounts. After native Linux metadata observation and human approval, C10 optional file_modes/with_file_mode sets initial fixture permissions; existing with_file remains 0755. No chmod/fchmod implementation or production dependency was added. Guest probe uses crates.io tokio (MIT), rayon (MIT/Apache-2.0), libc (MIT/Apache-2.0). 検証済み：run 38009664758 builds both static-musl binaries and passes all four cargo-deny checks before compilation. Root deny.toml is unchanged; only the human-approved guest webpki-root-certs@1.0.9/CDLA-Permissive-2.0 exception is appended to the generated guest configuration. The full license and hashes accompany the build receipt.

検証済み: cargo metadata --locked --manifest-path tests/guests/u10/probe/Cargo.toml --format-version 1 confirms all nine external resolved crates come from registry+https://github.com/rust-lang/crates.io-index. Versions: tokio1.53.1 (MIT), libc0.2.186/rayon1.11.0/rayon-core1.13.0/crossbeam-deque0.8.8/crossbeam-epoch0.9.21/crossbeam-utils0.8.23/either1.19.0 (MIT OR Apache-2.0), pin-project-lite0.2.17 (Apache-2.0 OR MIT). Run 38009664758 records build exit0, audits probe/aube0, fixed aube source before/after equality for 1365 files, and fresh native14/emulator16 successful rows. These are finite Linux observations. Historical failed receipts remain preserved and are not relabeled as successes.
