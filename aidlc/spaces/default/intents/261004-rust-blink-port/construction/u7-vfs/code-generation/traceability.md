# U7 実装・検証対応（作業中）

ドキュメント根拠：inception requirements FR3.1–3.4/FR2.10/FR9.1/FR9.3/NFR1–9、unit-of-work U7、C2/C6/C8/C10/C11。Testing Contractは承認計画のJSONをそのまま適用する。これは途中成果物であり、未修正不具合・未完了ゲートを成功と表示しない。

|要件|実装面|観測・残件|
|---|---|---|
|FR3.1 既定private|vfs MemFs/inode/OpenFile、Runtime file_system|diff-host-greenのMemFs32、runtime_default_private、mount namespace16。最終source再検証待ち。|
|FR3.2 明示Host root隔離|Host NativeFs/cap_std root、HostFs型、MountedFs、Session.mounts、CLI mount|Host8＋race1、Host guest29成功。CLI6内部＋2commandは追加済み未実行。末尾slash guest破壊操作にcase32 Redがあり未修正。|
|FR3.3 file操作|VFS operations/paths/open_file/mount、Kernel files/FD/ABI|61 native差分成功の中間証拠。追加case32は2失敗、破壊操作・flags不具合を修正する必要あり。|
|FR3.4 preload|Config.with_file、Runtime file_system、MountedFs private namespace|runtime_preload、mount_root_private_preload、mount_private_nested_preload成功。CLI root接続は未実行。|
|FR2.10 NULL stat→EFAULT|Kernel guest_cstr/stat checked MMU output|null_stat/null_lstat/null_statat native比較成功。|
|FR9.1 native期待毎回生成|guest raw syscall corpus＋diff_u7 child watchdog|初回20Red→20green、FD3Red→31green、Host5Red→61green、生ログ保存。固定期待値ファイルなし。|
|FR9.3 VFS/syscall fuzz|vfs_paths finite operation列、syscall_args file入力、nightly matrix|target追加済み。各600秒は未実行、fuzz lock未更新。|
|NFR1 正しさ|差分ケースと比較除外表|native-comparison.mdにbytes/errno/type/size/nlinkと除外理由を記載。case32は未修正。|
|NFR2 堅さ|checked guest buffers、MMU check_read、try_reserve、bounded fuzz harness|huge_invalid_bufferなど成功。ASan fuzz未実行。|
|NFR3 unsafe禁止/coverage/lint|既存forbid unsafe、Linux owned scope測定|coverage-fourth 4099/4569＝89.71%、CLI前の中間source。最終fmt/clippy/coverage未実行。|
|NFR4 隔離|root relative safe capability API、typed Host boundary|Host parent/symlink escape、1000-operation rename/symlink競合成功。canonicalize後absolute openなし。最終回帰待ち。|
|NFR5 資源|product file数/サイズquotaなし|Linux ABI maxRWとfuzz one-input予算はproduct quotaと区別。fuzzによる最終堅さ確認待ち。|
|NFR6 速さ|U7では新性能目標/JIT意味論を追加しない|テスト実行時間をbenchmark合格とは扱わない。U7専用速度目標なし。|
|NFR7 安定|diff/Host raceのwhole-child30秒kill/reap、interruptible flock|61diffとHost race成功。case32も30秒child境界下で結果取得。fuzz single-input30秒は設定済み未実行。|
|NFR8 供給網|cap_std/cap_fs_ext/fs2/rustix crates.io依存、Cargo.lock、nightly SHA|crate license metadata観測済み。cargo-deny/advisory/source最終検査とfuzz lock更新未完了。|
|NFR9 toolchain|rust-toolchain nightly＋既存Linux runner|実行ログにnightly-2026-10-01 Linux。CI/toolchain既存設定を維持。|

## 必要なMMU API変更

`crates/paludarium-mmu/src/lib.rs` に `Memory::check_read` を追加した。guest read/write ABIがbufferアクセス可能性をallocation前に確認するために使う。既存Access::Readのdata.checkを呼び、バイトを書き換えない。coverage-fourthでMMU lib831行中763行covered（91.82%）を測定した。既存MMU29テストが同測定で成功している。CPU/decoder/fault意味論を新設する変更はない。

## 対象外・未検証

guest clone/process/network/SSE/wasm/JIT、probe/aube全体、Win/mac固有mount合格をU7成果として主張しない。Host外部rename後の既存dirfd identity、stat uid/gid/timestamp全フィールド、platform別errno同等性は未検証。最終source manifest、code-summary、fuzz/品質ゲート、独立reviewはまだ未完了。
