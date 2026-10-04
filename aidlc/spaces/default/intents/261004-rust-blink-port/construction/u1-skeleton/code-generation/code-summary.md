# コード生成の結果（u1-skeleton）

## 実装と変更したファイル

U1 の既存実装を復旧し、Step 17 の成果物を作成した。アプリケーション側の変更範囲は `source-manifest.json` の 94 件のファイル・ディレクトリ claim に記録する。今回の復旧では `crates/paludarium-jit/src/lib.rs` のテスト 2 件と、Kernel の short/zero write の修正・回帰テスト 2 件を追加した。

| 場所 | 内容 |
|---|---|
| `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `clippy.toml`, `deny.toml`, `.gitignore` | 12 クレートの workspace、固定 nightly、lint、供給網の設定 |
| `crates/paludarium-{types,decoder,mmu,cpu,loader,vfs,kernel,host,jit,runtime}/` | 共通型、デコーダ、MMU、CPU、ELF、VFS、syscall、Host、JIT の口、Session |
| `crates/paludarium/` | 公開 API と CLI |
| `crates/paludarium-harness/`, `tests/guests/` | ネイティブとの差分テスト、C/Rust hello world、13 の命令系ゲスト |
| `tools/insn-trace/`, `docs/u1/census/` | 命令の実行履歴を取る道具と hello world の命令一覧 |
| `fuzz/` | decode、load_elf、mmu_ops、syscall_args の入口 |
| `ci/linux-dev/Dockerfile`, `scripts/linux-dev.sh` | Linux の差分テスト・カバレッジ・ファジング用環境 |
| `.github/workflows/ci.yml`, `.github/workflows/nightly.yml` | PR/夜間の検査 |
| `spikes/wasm-threads/`, `docs/reports/wasm-threads.md` | wasm の共有メモリの確認と結果報告 |
| `README.md` | ビルド、実行、単体/差分/カバレッジ/ファジング、U1 の範囲 |

## 判断と取り決めへの追加

- ドキュメント根拠：製品のデコーダは iced-x86 1.21 を使用する（`crates/paludarium-decoder/Cargo.toml`）。yaxpeax-x86 との比較試作の結果ログは復旧時に見つからず、選定の比較結果は未検証。
- ドキュメント根拠：C1 へ `ExitReason::BudgetExhausted` を追加し、C2 へ `Host::random_bytes` を追加した（`crates/paludarium-types/src/lib.rs`、`crates/paludarium-host/src/lib.rs`）。機能設計 R-09 の contract-summary への反映は上流文書の残項目として扱う。
- ドキュメント根拠：CLI は `--no-jit` を受け付ける（`crates/paludarium/src/cli.rs`）。U1 は `NoopCodeCache` でインタプリタへ戻る。
- ドキュメント根拠：syscall の実装範囲は README に記載した hello world 用の一覧。機能設計 BR3.3 の一覧に対して `mprotect` が追加されている。検証済み：conductor の `readelf` は C が EXEC、Rust が DYN を確認。Rust hello world の `strace -qq -c` は exit 0 で mprotect・write・poll・arch_prctl・set_tid_address・rt_sigprocmask・sigaltstack・mmap・munmap・brk・rt_sigaction を記録した（execve は起動側）。
- 検証済み：JIT のテスト数を 3 件から 5 件へ補い、承認済み Standard の下限を維持した。追加テストは RX ページのコードと CPU 状態の保持、および共有 cache の並行 fallback/invalidation を確認する。

## 検証の証拠

2026-10-04 の conductor の実行結果。チェック済み task marker から合格を推定していない。

| コマンド | 観測結果 |
|---|---|
| `cargo test --locked -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-loader -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-jit -p paludarium-runtime -p paludarium`（Windows、追加テスト前） | 検証済み：exit 0、98 件と doctest 1 件が合格 |
| `cargo fmt -p paludarium-jit` | 検証済み：exit 0 |
| `cargo test --locked -p paludarium-jit`（追加後） | 検証済み：exit 0、5 passed、0 failed。`invalidation_and_fallback_preserve_guest_code`、`shared_cache_supports_concurrent_fallback_and_invalidation` を含む |
| `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u1` | 検証済み：exit 0、16 passed、0 failed、10.79 秒。`hello_c`、`hello_rs`、`hello_rs_with_arguments` と 13 の命令系テスト |
| unit-test-instructions の Linux `cargo llvm-cov ... --fail-under-lines 80` | 検証済み：TOTAL lines 3259、missed 420、line coverage 87.11%（>=80%）。102 tests が合格。exit 0（conductor が確認） |

差分テストは C/Rust hello world の標準出力・標準エラー・終了状態を、当該実行のネイティブ結果と比較する。命令系 13 件の合格だけから、census の全命令・全形式の網羅を主張しない。`traceability.json` の OK は実装・テストへの対応を表し、要件の測定合格の代わりにはならない。

`cargo fmt --all -- --check`：検証済み、exit 0（conductor）。`cargo clippy --locked`（U1 の 12 packages、`--all-targets -- -D warnings`）：検証済み、exit 0（conductor）。

## 未検証と残項目

- 検証済み：`cargo test --locked -p paludarium-harness --lib coverage::tests -- --nocapture` は exit 0、2 passed、`U1 instruction coverage by differential tests: 66/66`。`crates/paludarium-harness/src/coverage.rs` が命令・ゲスト・ソースの根拠片を対応させている。以前の「対応表がない」という記載を訂正する。この測定はソースの根拠片の存在を数えるもので、全命令形式・全フラグの意味論の網羅を保証しない。
- NFR3.3：Linux の観測値は 87.11%（3259 行、未実行 420 行）で 80% を満たした。exit 0 を conductor が確認した。
- wasm：`docs/reports/wasm-threads.md` は過去の Node.js/Chromium/Firefox の観測を記録した文書根拠。今回の再実行は未検証。Safari、入れ子の Worker、std の共有ヒープ初期化は未検証。
- ファジング各対象の短時間実行、nightly の 10 分実行、cargo-deny、macOS の単体テスト、decoder 候補比較のログは今回未検証。実行可能な conductor/CI で承認済み計画と README のコマンドを実行する。
- Step 1〜16 の歴史的な試行順序（native の期待結果を実装前に用意したこと）はチェックマークだけでは復旧できない。今回も Testing Contract の custom ordering を維持し、内部 JIT 部品の追加テストは実装後に実行した。

## 対応表

`traceability.json` は割り当てられた BR 26 件・詳細 NFR 21 件を列挙する。上流では User Stories が scope によりスキップされており、AC を新しく作らない。対象は既存の workspace 相対ファイルに束縛し、測定不足は GAP として残す。




## write の短い結果への対応

反証可能な確認事項：`write(fd=1/2, 有効な buf, count>0)` は、Host が短い結果（0 を含む）を返したら、その値を返して Host を再呼び出ししない。

- 検証済み（修正前）：`cargo test --locked -p paludarium-kernel write_returns_` は exit 1、0 passed / 2 failed。`write_returns_zero_without_retrying_host` は left 18446744073709551611（-EIO）/ right 0、`write_returns_partial_count_without_filling_remainder` は left 5 / right 1。mock の 2 回目を有限の応答にし、停止しないテストを避けた。
- `sys_write` の `Ok(w)` で、累計を増やして `w < n` なら即座に累計を返す。0 もここで返す。全量 chunk の継続と、エラー時の既存の累計/errno の選択は保つ。
- 検証済み（修正後）：`cargo test --locked -p paludarium-kernel` は exit 0、10 passed / 0 failed。上の 2 テストは各 fd=1/2 で返却値 0/1 と Host 呼び出し数 1 を確認する。`cargo fmt -p paludarium-kernel` は exit 0。
- 検証済み（修正後）：`scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u1` は exit 0、16 passed / 0 failed、10.79 秒。unit-test-instructions の 11 packages の Linux `cargo llvm-cov --locked ... --fail-under-lines 80` は exit 0、102 tests が合格、TOTAL lines 3259 / missed 420 / line coverage 87.11%。
- 検証済み（修正後）：`cargo clippy --locked -p paludarium-kernel --all-targets -- -D warnings` と `cargo fmt --all -- --check` は exit 0。


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

## 2026-10-07 redo：現在のsourceと保存済み証拠の照合

今回の新実行はファイルの実在・SHA256・jj追跡・traceability照合のみ。アプリケーションsource、共有README、他unitの成果物は変更していない。上の102件/87.11%、197件/94.00%および「今回実行」と記された66/66は各先行attemptの履歴であり、本redoの新テスト実行ではない。

- 検証済み（保存済み正式実行）：`.aidlc-construction-checkpoints/u1-skeleton/skeleton.json` のid `4747d3c8-ee4d-4d76-9d3e-b4046449d3c0`、command_label `"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked --workspace`、2026-10-06T22:02:21.817Z〜22:02:50.262Z、exit0、verified:true、evidence_unchanged:true。stderr_tailはdiff_u1とKernelを含む全workspace対象を記録。stdout digest `2b834e096fec7d78d18e5f14c3cd9149a14e632c2f5ec946a1af1edbf3560322`。このテスト証拠は新attemptの人間承認の代わりにはしない。proofの末尾だけから全件数を推定しない。
- 検証済み（最新保存測定）：`docs/u7/inventory/coverage-final.txt:888` TOTAL lines4681、missed478、89.79%（4203/4681）、80%下限を満たす。U7を含む現在の全体分母でありU1専用カバレッジではない。同ファイル:46〜47はcensus対応helper2件ok、:728〜729はwriteのゼロ/部分結果回帰2件ok。先行U1 diff16件は正式全workspaceのdiff_u1対象で再確認されている。
- 検証済み（本redoの照合）：`docs/u7/inventory/source-bytes-final.json` の34ファイルをGet-FileHashで現在値と比較し、不一致0。現在U1 manifest94claimsを展開した98ファイルを `source-bytes-current.json` へ保存。欠落0、jj file listのWindows区切り正規化後の未追跡0。traceability47件のOK target欠落0。source-manifest SHA256 `9ad3020d09ec0ee6a512ceb4c8546d6e59914ae2fb1c0d8363d9dd853a747a1a`、source snapshot SHA256 `842ba15c913b6d6d04157249a137228e2b70f3815087f1aa9288f3e91d2b2701`。
- 検証済み（保存済み依存検査）：`docs/u7/inventory/deny-final-locked.txt` 末尾にadvisories/bans/licenses/sources全ok。現在Cargo.lock SHA256 `553b2b8d7670426ed73c51f1d756b93a6a8b26bc427de87afa01a15f60264b27`。これは最新lockの検査記録であり、旧U2 lockに対する検査を現在へ転用していない。
- ドキュメント根拠：C1〜C11のU1 providerと後続共有変更は保持。U2のArithmeticFault/atomic/REPに加え、U4のsignal/time/MMUとU7のVFS/Hostの現在の共有拡張をU1新実装と数えない。独立後続sourceをU1 claimsへ追加しない。
- 未検証：wasm spike再実行、Safari/macOS、U1 decode/load_elf各fuzzの本redo実行、候補decoder比較の歴史的ログ。後続unitのfuzz合格を代用しない。既存nightly各600秒、80%下限、差分30秒watchdog、nightly pin、custom orderingは保持。承認済みStep19のとおり不足を開示し、同じproductionの全体テストは反復しなかった。