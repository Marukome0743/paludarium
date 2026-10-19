
## 2026-10-08 Docker VMM復旧後：最新全体実行の失敗

検証済み：親が `bash scripts/linux-dev.sh cargo test --locked --workspace` を実行し、session95414はexit101。正式な保存先は `verification/docker-vmm-workspace-tests.log`。

- ログ:654–675：diff_u1は16 passed/0 failed、suite54.61秒。hello3件と命令13件。30秒case watchdogは保持。
- ログ:1074–1082：diff_u2は32 passed/6 failed。cmps/scasのfault時flags比較4件、enter allocation fault比較1件、u2_aluのouter30秒watchdog期限切れ1件（:1071）。期待値との差5件と期限切れ1件の観測に限り、原因は断定しない。
- 今回はApple SiliconのDocker VMM/QEMU上のlinux/amd64環境。native x86-64 Linux実機での機能同等性は未検証。workspace全体と新checkpointは不合格。旧197件/94.00%・保存済み89.79%から今回の合格を推定しない。
- Docker build成功とコンパイル完了を確認したため、前節のimage未作成/新Rust実行なしは履歴となる。変更は親の `scripts/linux-dev.sh` build/runへの `--ulimit stack=-1` 追加だけ。現在のsource snapshotは同scriptのSHA256を更新し、他の製品source不変を確認した。
- 未解消のreview-06 R-01：テスト指示本文の旧U2履歴表現。承認に束縛された計画/テスト指示は変更せず、旧sourceの197件/94.00%を現在のrunner成功に用いない。現在の保存済みカバレッジ証拠はU7のcoverage-final.txtであり、今回新測定ではない。

以下の静的コマンドを最新snapshot更新後にも実行した。診断用の照合であり、失敗した全体検証を合格にするreceiptではない。全体失敗を受け、レビュー・承認・完了を新しく作らず停止する。

## 2026-10-08 現在値の確認（VMM復旧前の履歴）

今回の新実行は静的照合のみ。製品変更はなく、同sourceのRust/Linuxテストを反復していない。以下の先行attemptに書かれた「今回」「現在」は各記載時点の履歴。旧U2の197件/94.00%と初期U1の102件/87.11%は現在sourceの合格値ではない。

再現コマンド（workspace rootで実行）：

```bash
python3 aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/check-current-source.py
```

検証済み、exit0：95claims/99files、missing0/untracked0、U7 snapshot34ファイル不一致0、更新後U1 snapshot99ファイル不一致0、traceability upstream47/coverage47・OK target欠落0、census66エントリの根拠片欠落0。censusの検査は静的対応でありテストの実行ではない。更新前のU1 snapshot98ファイルとの差分は他者の復旧作業による `.gitignore` だけだった。U7で移動された既存U1 VFS5テストをmanifestへ1件追加し、独立U7/U2実装は追加していない。

最新保存済み測定：`docs/u7/inventory/coverage-final.txt:888` は全体4681行/未実行478/89.79%。:46–47 はcensus helper2件、:728–729 はwrite回帰2件の成功。この測定はU1専用coverageでなく、diff_u1の実行結果も含まない。80%下限は保持。

保存済みLinux全体テスト：`docs/u7/inventory/repair-workspace-verification-retry.json` は2026-10-06の `scripts/linux-dev.sh cargo test --locked --workspace`、exit0、stderrにdiff_u1対象の実行を記録する。今回の新実行・承認・正式receiptには用いない。tailから16passedを推定しない。旧文書が参照する機械ローカルの `.aidlc-construction-checkpoints/u1-skeleton/skeleton.json` はこのMacに無く、現receiptとして未確認。

依存検査の保存済み根拠：`docs/u7/inventory/deny-final-locked.txt` 末尾はadvisories/bans/licenses/sources全ok。現Cargo.lock hashは上の照合コマンドが出力する `553b2b8d7670426ed73c51f1d756b93a6a8b26bc427de87afa01a15f60264b27` で保存U7snapshotと一致。旧U2lockの検査を現在へ転用しない。

C1〜C11の現在のprovider/consumerとU2/U4/U7の共有拡張を `code-summary.md` 冒頭へ記載。U1の初期仕様であったsignal登録のみ/mount拒否と、後続U4/U7の拡張を区別した。Step18〜20はチェックを証拠とせず今回照合を終えて保持。Step1〜17の履歴、記録済み回答、Testing Contractは変更していない。

未検証：新Linux diff_u1/Rust単体/U1専用coverage、wasm再実行、Safari/macOS製品テスト、U1各fuzzの新実行、decoder候補比較の歴史的ログ。Docker daemonは稼働（linux/aarch64）だが `docker image inspect paludarium-dev` はimageなし。同production再実行不要の計画に従ってimage buildは行わなかった。必要ならimageを準備したうえで承認済みexact commandsを実行する：

```bash
scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u1
scripts/linux-dev.sh cargo test --locked -p paludarium-harness --lib coverage::tests -- --nocapture
scripts/linux-dev.sh cargo test --locked -p paludarium-kernel --lib tests::write_returns_zero_without_retrying_host -- --exact
scripts/linux-dev.sh cargo test --locked -p paludarium-kernel --lib tests::write_returns_partial_count_without_filling_remainder -- --exact
```

期待件数は順に16/2/1/1。0件を合格と扱わない。sync実行はfuzzと同時に行わない。80%下限・30秒watchdog・nightly各600秒・nightly pin・custom orderingを維持した。

## 先行attemptの共有source確認履歴

今回の変更はU1記録文書だけで、application source・README・U2成果物は変更していない。上記102件/87.11%と初回write修正のRed/Greenは先行sourceの履歴である。現在のsourceについて次の具体物を照合した。

| 具体物 | 現在の観測 |
|---|---|
| docs/u2/repairs/r01-workspace-coverage.txt:118〜136 | 検証済み：hello_c/hello_rs/hello_rs_with_argumentsと既存13命令系、U1差分16 passed/0 failed。serial実行34.83秒はsuite合計で、各case30秒watchdogを維持 |
| 同ファイル:564〜565 | 検証済み：tests::write_returns_partial_count_without_filling_remainder と tests::write_returns_zero_without_retrying_host はok。Kernel11 passed。有限mockはfd1/2、0/1返却とHost呼出し1回を検査 |
| 同ファイル:670 | 検証済み：全workspace197 parent tests、lines4233/missed254/94.00%、regions90.20%、保存済み実行exit0。全体分母でありU1専用件数/coverageとは呼ばない |
| cargo test --locked -p paludarium-harness --lib coverage::tests -- --nocapture | 今回実行exit0、2 passed/0 failed、U1 instruction coverage by differential tests:66/66。coverage_counts_missing_sources_as_uncovered/every_u1_instruction_has_a_differential_testが通過。形式・flags全入力の意味論網羅率ではない |
| docs/u2/repairs/u2-cargo-deny.txt | 検証済み：advisories/bans/licenses/sources全ok、公式asset digest照合後のWindows --locked check exit0。先行Linux missing-command失敗から後続取得で確認済み |

ドキュメント根拠：C1〜C11の現在の実装は既存provider crateに保持される。U2で共有sourceにArithmeticFault（Types/Cpu/Kernel同時更新、Kernel SIGFPE）、typed atomic/common Mmu同期、FS/GS linear address、REP continuationが加わった。これをU1の新規実装成果とは数えない。CpuはKernel/Hostを直接利用せず、MmuはCpu型に依存しない。C2乱数・C9no-op fallback・C10Session・C11CLIの既存口も維持する。上流contract-summaryは完全な現API宣言ではなく、古い型形状との差分をこの記録で開示する。

最新CPU/MMU ASan600秒の通過はU2対象の観測であり、U1 decode/load_elf/mmu_ops/syscall_args各targetの合格へ転用していない。U1各targetの今回実行、macOS/Safari、wasm spikeの再実行、候補decoder比較の歴史的ログは未検証。nightly各600秒・80%・30秒・nightly pin・custom orderingは維持する。既存full実行と同じproductionであるため、全体検証を反復しなかった。必要な証拠が新たに不足した場合は承認済みexact U1 commandsで回収する。

source-manifestは94 claims。U1独立fuzzは4ファイルへ限定し、U2専用cpu_u2/mmu_u2 targetsを所有権へ加えていない。shell/scaffolding/generator由来を含む既存U1 sourcesを保持する。記録済み回答は保持し、新しい機能回答や合格を作っていない。
最終整合観測：traceability upstream47/coverage47、OK target実ファイル欠落0。source-manifest94 claimsはjj未追跡0。Cpu dependenciesはTypes/Decoder/Mmuのみ、MmuはTypesのみ（各Cargo.toml読取）。exec.rs SHA256=e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0を保持。Step18〜20のチェックは今回の確認完了を表し、Step1〜17の過去試行順序の証明にはしない。

## 2026-10-07 redo：現在のsourceと保存済み証拠の照合

今回の新実行はファイルの実在・SHA256・jj追跡・traceability照合のみ。アプリケーションsource、共有README、他unitの成果物は変更していない。上の102件/87.11%、197件/94.00%および「今回実行」と記された66/66は各先行attemptの履歴であり、本redoの新テスト実行ではない。

- 検証済み（保存済み正式実行）：`.aidlc-construction-checkpoints/u1-skeleton/skeleton.json` のid `4747d3c8-ee4d-4d76-9d3e-b4046449d3c0`、command_label `"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked --workspace`、2026-10-06T22:02:21.817Z〜22:02:50.262Z、exit0、verified:true、evidence_unchanged:true。stderr_tailはdiff_u1とKernelを含む全workspace対象を記録。stdout digest `2b834e096fec7d78d18e5f14c3cd9149a14e632c2f5ec946a1af1edbf3560322`。このテスト証拠は新attemptの人間承認の代わりにはしない。proofの末尾だけから全件数を推定しない。
- 検証済み（最新保存測定）：`docs/u7/inventory/coverage-final.txt:888` TOTAL lines4681、missed478、89.79%（4203/4681）、80%下限を満たす。U7を含む現在の全体分母でありU1専用カバレッジではない。同ファイル:46〜47はcensus対応helper2件ok、:728〜729はwriteのゼロ/部分結果回帰2件ok。先行U1 diff16件は正式全workspaceのdiff_u1対象で再確認されている。
- 検証済み（本redoの照合）：`docs/u7/inventory/source-bytes-final.json` の34ファイルをGet-FileHashで現在値と比較し、不一致0。現在U1 manifest94claimsを展開した98ファイルを `source-bytes-current.json` へ保存。欠落0、jj file listのWindows区切り正規化後の未追跡0。traceability47件のOK target欠落0。source-manifest SHA256 `9ad3020d09ec0ee6a512ceb4c8546d6e59914ae2fb1c0d8363d9dd853a747a1a`、source snapshot SHA256 `842ba15c913b6d6d04157249a137228e2b70f3815087f1aa9288f3e91d2b2701`。
- 検証済み（保存済み依存検査）：`docs/u7/inventory/deny-final-locked.txt` 末尾にadvisories/bans/licenses/sources全ok。現在Cargo.lock SHA256 `553b2b8d7670426ed73c51f1d756b93a6a8b26bc427de87afa01a15f60264b27`。これは最新lockの検査記録であり、旧U2 lockに対する検査を現在へ転用していない。
- ドキュメント根拠：C1〜C11のU1 providerと後続共有変更は保持。U2のArithmeticFault/atomic/REPに加え、U4のsignal/time/MMUとU7のVFS/Hostの現在の共有拡張をU1新実装と数えない。独立後続sourceをU1 claimsへ追加しない。
- 未検証：wasm spike再実行、Safari/macOS、U1 decode/load_elf各fuzzの本redo実行、候補decoder比較の歴史的ログ。後続unitのfuzz合格を代用しない。既存nightly各600秒、80%下限、差分30秒watchdog、nightly pin、custom orderingは保持。承認済みStep19のとおり不足を開示し、同じproductionの全体テストは反復しなかった。
