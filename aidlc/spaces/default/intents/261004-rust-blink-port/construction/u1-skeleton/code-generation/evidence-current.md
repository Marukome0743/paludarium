
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