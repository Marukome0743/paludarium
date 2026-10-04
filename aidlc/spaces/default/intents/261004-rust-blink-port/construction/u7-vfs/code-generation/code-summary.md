# U7 ファイルシステム：実装結果

## 変更したファイル

変更全体は `source-manifest.json` に列挙する。MemFsとマウント合成、Hostの型付きファイル能力、KernelのFD表とfile syscall、Runtimeのpreload・mount接続、CLIの`--mount`、ゲスト差分、ファジングとnightly設定を含む。共有MMUの変更はguest bufferの読取可否検査に限定する。

## 実装上の判断

ドキュメント根拠：C2/C6/C8/C10/C11、FR2.10、FR3.1–FR3.4。ゲストnamespaceのパスをsymlink展開と各成分の順序で解決し、ホスト操作は保持したrootディレクトリ能力から相対的に実行する。既定はMemFsで、明示mountのみホストへ接続する。FDは共有open-file descriptionを参照し、dupのoffset・status flags・flock所有者を共有する。unlink後のopen inode寿命を維持する。

検証済み：末尾slashのsymlink削除・renameと`O_CREAT | O_DIRECTORY`の不具合をnative結果に合わせて修正した。`diff_u7`の共有絶対パスfixtureは親caseを直列化し、各childの30秒watchdogを維持した。根拠：`docs/u7/inventory/repair-before.txt`、`repair-after.txt`、`coverage-final.txt`。

## 検証結果

検証済み：Linuxの最終測定は `cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1` がexit0。4203 covered / 4681 total、89.79%。U7変更クレートの既存libとguest差分・CLI integrationを測定し、未変更CPU等とharness基盤のreport行を除外した。diff63親case、CLI command6件が成功。child結果を親件数に重複加算しない。

検証済み：修正後のworkspace clippy `cargo clippy --locked --workspace --all-targets -- -D warnings` はexit0、fmtもexit0。workspace正式検証の成功証拠は `docs/u7/inventory/repair-workspace-verification-retry.json`。この再開で製品ソースは変更していない。根拠一覧と制限は `docs/u7/verification.md`。

検証済み：`target/aidlc-tools/cargo-deny.exe --locked check` はexit0、advisories/bans/licenses/sourcesがすべてok（`docs/u7/inventory/deny-final-locked.txt`）。既存multiple-versions=warnの重複版11グループの警告は残り、設定を下げていない。ASan fuzzはvfs_paths 859022 runs / 601秒、syscall_args 469436 runs / 601秒、両exit0でpanic/ASan異常なし。raw logは `fuzz-vfs-final-retry.txt` と `fuzz-syscall-final.txt`。独立reviewと現在U7 checkpointは親担当で実行する。

## 計画との差分

ドキュメント根拠：Testing Contractのcustom順序を維持した。初期ゲスト差分のnative期待取得とemulator失敗は `docs/u7/inventory/diff-red.txt`、内部層の実装後単体検証は同inventoryに記録した。以前の実装はUnit開始receiptの無い保持状態だったため、現在のルートで正規`UNIT_STARTED`を記録し、既存実装を最終検証した。過去の開始を遡及記録していない。

検証済み：ファジング手順のcontainer login shellはcargo PATHを失いexit127となったため、`bash -c`へ修正して同じASan・600秒・単一入力30秒条件を維持した。初期失敗logは保持している。relaxed fenceによる手順変更であり、新たに人が承認した内容とは扱わない。

## 未検証の範囲

Linux以外のHost mount、browser/wasm/JIT、probe/aube全体の合格は未検証で後続Unitの担当。statのuid/gid/timestamp全フィールド互換、外部rename後の既存dirfd参照維持は本corpusで未検証。native比較の対象・除外は `docs/u7/native-comparison.md` に記録する。

検証済み：正規traceabilityセンサー31ec39e1はpassed。共有要件60IDのうちU7対象17IDを対応させ、担当外43FRは所有UnitへDeferredとして明示した。範囲外Unitの完成を本Unitの合格へ含めない。
