# U7 現在の要件対応

ドキュメント根拠：unit-of-work/story-mapのU7担当17 IDs、FR/NFR、C2/C6/C8/C10/C11。担当外43 IDsの完成を主張しない。OKは実装と対応する現在テストへのmappingであり、要件の全挙動測定を意味しない。

|ID|状態|target|
|---|---|---|
|FR2.10|OK|crates/paludarium-kernel/src/files.rs|
|FR3|OK|crates/paludarium-vfs/src/lib.rs|
|FR3.1|OK|crates/paludarium-runtime/src/lib.rs|
|FR3.2|OK|crates/paludarium-host/src/native_fs.rs|
|FR3.3|OK|crates/paludarium-harness/tests/diff_u7.rs|
|FR3.4|OK|crates/paludarium-runtime/src/lib.rs|
|FR9.1|OK|crates/paludarium-harness/tests/diff_u7.rs|
|FR9.3|GAP|fuzz/fuzz_targets/vfs_paths.rs|
|NFR1|OK|docs/u7/native-comparison.md|
|NFR2|GAP|fuzz/fuzz_targets/syscall_args.rs|
|NFR3|GAP|docs/u7/verification.md|
|NFR4|OK|crates/paludarium-host/src/native_fs.rs|
|NFR5|OK|crates/paludarium-vfs/src/operations.rs|
|NFR6|N/A|FR7.4とFR8.3の速度評価はU10/U14担当。U7に速度目標なし。|
|NFR7|OK|crates/paludarium-harness/tests/diff_u7.rs|
|NFR8|OK|deny.toml|
|NFR9|OK|rust-toolchain.toml|

FR9.3/NFR2/NFR3のGAP：旧測定依存が現在と相違し、現在の各600秒ASanとU7限定80%は未検証。NFR6はU7専用性能目標がなくN/A。現在の観測・テスト名・raw行・限定範囲はevidence-current.md。
