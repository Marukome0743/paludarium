# Unit をまたぐ要件の対応（最終確認）

2026-10-18、`aidlc engine sensor-traceability --stage build-and-test` の出力から作った（Loop-back 2 の後にもう一度実行し、未対応は FR10.1 の 1 件だけで変わらないことを確かめた）。2026-10-19、U15 の Step22〜30 と U1〜U15 の確かめ直しの後（head 27d05de1）にもう一度実行し、未対応は FR10.1 の 1 件だけで変わらないことを確かめ、FR9.1 の行を今の出力に合わせた（U10 の `u10-current-verification.yml` は U15 の Step23 で消え、今の出力では `u10-native-diagnostic.yml`）。対象は 15 Unit の Code Generation の成果（各 Unit の `code-generation-plan.md`・`unit-test-instructions.md`・`code-summary.md` と `traceability.json`）。

## 判定

**不合格**（未対応 1 件：FR10.1）。

- FR1〜FR9 のすべての小項目と NFR1〜NFR9 は、どれかの Unit で作られているか、詳細の NFR を通して対応している。
- FR10.1（成功条件を満たしたら、タグを打って CI から crates.io と npm に公開し、公開の前に人が承認する）は、どの Unit の成果にも「作った」として対応していない。公開はまだしていない（`test-results.md` の Target Verification Matrix では Unverified）。U15 は公開の仕組み（`release.yml`・`scripts/release/`）と公開物の確認を作り、Loop-back 2 で版を 0.1.0 にそろえ、受け入れの証拠を作る部品（`u15-acceptance.yml`）、初回の限定トークン、途中で止まった初回の公開の再開を足し、Step24 で再開の判定の owners・yanked の確認を足したが、実際の公開は人が行う手順（`docs/release.md` の Owner hand-off）の後になる。

## 要件ごとの対応

| ID | 対応 | 担当の Unit と作ったファイル |
|---|---|---|
| FR1.1 | OK | u1-skeleton：`crates/paludarium-harness/tests/diff_u1.rs` |
| FR1.2 | OK | u3-sse：`crates/paludarium-decoder/src/lib.rs` |
| FR1.3 | OK | u2-integer-isa：`crates/paludarium-cpu/src/lib.rs` |
| FR1.4 | OK | u3-sse：`crates/paludarium-harness/tests/diff_u3.rs` |
| FR1.5 | OK | u4-memory-signals：`crates/paludarium-mmu/src/lib.rs` |
| FR1.6 | OK | u1-skeleton・u2-integer-isa：`crates/paludarium-cpu/src/lib.rs`、u3-sse：`crates/paludarium-decoder/src/u3_tests.rs` |
| FR2.1 | OK | u1-skeleton：`crates/paludarium-kernel/src/lib.rs`、u4-memory-signals：`crates/paludarium-kernel/src/syscalls.rs` |
| FR2.2 | OK | u4-memory-signals：`tests/guests/u4/memory.c` |
| FR2.3 | OK | u5-threads-futex：`crates/paludarium-kernel/src/threads.rs` |
| FR2.4 | OK | u6-events-sockets：`crates/paludarium-kernel/src/events.rs` |
| FR2.5 | OK | u6-events-sockets：`crates/paludarium-kernel/src/epoll.rs` |
| FR2.6 | OK | u6-events-sockets：`crates/paludarium-kernel/src/sockets.rs` |
| FR2.7 | OK | u6-events-sockets：`crates/paludarium-kernel/src/sockets.rs` |
| FR2.8 | OK | u8-process-spawn：`crates/paludarium-harness/tests/diff_u8.rs` |
| FR2.9 | OK | u4-memory-signals：`crates/paludarium-harness/tests/diff_u4.rs` |
| FR2.10 | OK | u7-vfs：`crates/paludarium-kernel/src/files.rs` |
| FR3.1 | OK | u1-skeleton：`crates/paludarium-vfs/src/lib.rs`、u7-vfs：`crates/paludarium-runtime/src/lib.rs` |
| FR3.2 | OK | u7-vfs：`crates/paludarium-host/src/native_fs.rs` |
| FR3.3 | OK | u7-vfs：`crates/paludarium-harness/tests/diff_u7.rs` |
| FR3.4 | OK | u1-skeleton：`crates/paludarium-vfs/src/lib.rs`、u7-vfs：`crates/paludarium-runtime/src/lib.rs` |
| FR4.1 | OK | u9-terminal-io：`crates/paludarium-runtime/src/u9_tests.rs` |
| FR4.2 | OK | u9-terminal-io：`crates/paludarium-kernel/src/syscalls.rs` |
| FR5.1 | OK | u12-macos-host：`crates/paludarium-host/src/lib.rs`、u13-windows-host：`crates/paludarium-host/src/windows.rs` |
| FR5.2 | OK | u11-wasm-launcher：`packages/paludarium-wasm/index.mjs` |
| FR5.3 | OK | u11-wasm-launcher：`packages/paludarium-wasm/tests/u11-browser-check.mjs` |
| FR5.4 | OK | u11-wasm-launcher：`packages/paludarium-wasm/worker-support.mjs`、u5-threads-futex：`crates/paludarium-runtime/src/workers.rs` |
| FR6.1 | OK | u10-probe-aube-native：`tests/guests/u10/probe/src/main.rs` |
| FR6.2 | OK | u10-probe-aube-native：`tests/guests/u10/probe/src/main.rs` |
| FR6.3 | OK | u10-probe-aube-native：`crates/paludarium-harness/tests/diff_u10.rs`、u11-wasm-launcher：`packages/paludarium-wasm/tests/u11-suite.mjs`、u12-macos-host：`crates/paludarium-host/src/lib.rs`、u13-windows-host：`crates/paludarium-host/src/windows.rs`、u14-jit-wasm：`packages/paludarium-wasm/tests/u11-programs.mjs` |
| FR6.4 | OK | u10-probe-aube-native：`docs/u10/source-review.md` |
| FR7.1 | OK | u10-probe-aube-native：`tests/guests/u10/source-lock.json` |
| FR7.2 | OK | u10-probe-aube-native：`tests/guests/u10/differential.py`、u11-wasm-launcher：`packages/paludarium-wasm/tests/u11-filesystem.mjs`、u12-macos-host：`crates/paludarium-host/src/lib.rs`、u13-windows-host：`crates/paludarium-host/src/windows.rs`、u14-jit-wasm：`packages/paludarium-wasm/tests/u11-programs.mjs` |
| FR7.3 | OK | u10-probe-aube-native：`tests/guests/u10/comparison.py`、u11-wasm-launcher：`packages/paludarium-wasm/tests/u11-filesystem.mjs`、u12-macos-host：`crates/paludarium-host/src/lib.rs`、u13-windows-host：`crates/paludarium-host/src/windows.rs` |
| FR7.4 | OK | u10-probe-aube-native：`docs/u10/timings.md`、u11-wasm-launcher：`construction/u11-wasm-launcher/code-generation/verification/current-sequential-timings.md` |
| FR8.1 | OK | u14-jit-wasm：`crates/paludarium-jit/src/lib.rs` |
| FR8.2 | OK | u14-jit-wasm：`crates/paludarium-harness/tests/diff_u14.rs` |
| FR8.3 | OK | u14-jit-wasm：`packages/paludarium-wasm/tests/u14-performance.mjs` |
| FR9.1 | OK | u1〜u9・u10〜u13 の差分テスト（`diff_u1.rs`〜`diff_u8.rs`、`.github/workflows/ci.yml`・`u10-native-diagnostic.yml`、`tests/guests/u9/oracle.py`、`u11-suite.mjs`、Host の `lib.rs`・`windows.rs`） |
| FR9.2 | OK | u11-wasm-launcher：`packages/paludarium-wasm/tests/u11-browser-check.mjs` |
| FR9.3 | OK | u4-memory-signals：`fuzz/fuzz_targets/syscall_args.rs`、u7-vfs：`fuzz/fuzz_targets/vfs_paths.rs` |
| FR10.1 | **未対応** | なし（公開は未実施。U15 の公開の仕組みはあるが、公開の実行は人の設定の後） |
| NFR1 | OK | u1-skeleton：NFR1.1・NFR1.2、u2-integer-isa：NFR1.1〜NFR1.3 |
| NFR2 | OK | u1-skeleton：NFR2.1〜NFR2.4、u2-integer-isa：NFR2.1・NFR2.2 |
| NFR3 | OK | u1-skeleton：NFR3.1〜NFR3.3、u2-integer-isa：NFR3.1〜NFR3.4 |
| NFR4 | OK | u1-skeleton：NFR4.1〜NFR4.4、u2-integer-isa：NFR4.1 |
| NFR5 | OK | u1-skeleton：NFR5.1（N/A：要件上の資源上限はなし。ELF 読み込みの安全対策は別途 Loader に実装）、u2-integer-isa：NFR5.1 |
| NFR6 | OK | u1-skeleton：NFR6.1、u2-integer-isa：NFR6.1 |
| NFR7 | OK | u1-skeleton：NFR7.1、u2-integer-isa：NFR7.1・NFR7.2 |
| NFR8 | OK | u1-skeleton：NFR8.1〜NFR8.4、u2-integer-isa：NFR8.1 |
| NFR9 | OK | u1-skeleton：NFR9.1、u2-integer-isa：NFR9.1 |

## 未対応の項目（承認の場で示すもの）

- **FR10.1**：担当の段階は build-and-test（Q4 の B、この段階で公開まで行う）。版は 0.1.0 に決まった（Q7）。公開に要る人の手順（upstream への取り込み、`release` environment の保護、名前の所有と初回の公開、Trusted Publisher、公開する head での品質 run と `u15-acceptance` の受け入れの証拠、`v0.1.0` の tag と承認）がそろってから公開する。
