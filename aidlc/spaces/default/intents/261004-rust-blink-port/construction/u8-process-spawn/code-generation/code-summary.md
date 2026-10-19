# U8 現行process起動の再確認

## 現在の状態（2026-10-19 JST、Step17）

本節はStep17の記録である。U15のStep22〜28で製品のファイルが変わってfork `codex/build-and-test` へ送られた（head 27d05de1、e3c29d1d→8b415a7c→8360be2e→27d05de1、4つともVerified）ので、U8を確かめ直した（`reviews/review-06.md`、NOT-READY、Critical 1・Major 3・Minor 4）。checkpointで人がRequest Changesを選んだので、R-04〜R-08とR-10をU8の記録で直し、R-09とR-11は記録して人の判断を待つことにした（Step18で、再レビュー review-07 のR-12・R-13に合わせてこの一文とNFR8の理由を直した）。U8の製品のコード・CI・workflow・ほかのUnitの記録は変えていない。

- **今の正式な確認コマンド（R-06）**：`aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の U15 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用、command SHA-256 `00f5c8832e04f7d27b30c6b445fdc30e0e5d233dfa5452e02c2c99368a08a159`）。今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`。下の節の `u2_candidate.py`、候補 `verify-current-u1-u7-u9-u3-u5-u6-u8.py`（不採用・履歴、R-10）、公式2026-10-10配布のnightly、head 692264fa、「未実行」「未検証」は、それぞれの時点の記述である。下の各節の「先頭の『現行Step16〜18』節を参照」の案内は、今はこの節を指す（R-10）。U8のcheckpointはentry-fで確かめる。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べるので、U8の記録の変更はその結果に影響しない想定である（結果はcheckpointの記録が持つ）。
- **U8に関わる製品の変更**：U8の製品のファイルは変わっていない。U8のsource-manifestにある `ci.yml` は `push` が `main` だけになり、`u8-current-verification.yml`・`u8-native-diagnostic.yml` は消えた（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）。source-manifest.jsonのwritesから2本を外した（27件→25件、R-05。manifestはpathだけを持ち、hashは持たない）。27d05de1のCI 8 runはすべて成功した（U12は人が認めた1 jobの再実行。記録はU15の `verification/ci-27d05de1/`）。
- **traceability.json（R-04・R-07）**：行ごとにJSONとして直し、27d05de1の版と比べて変わったのはcoverageのNFR3・NFR8・NFR9の3行と、reverseから外した2行だけであることを確かめた。NFR8のtargetを `.github/workflows/ci.yml` に替え、notesの先頭に理由を書いた。NFR8は要件書で供給網（依存はcrates.ioだけ、ライセンスがApache-2.0と両立、actionのSHA固定）と決められていて、`ci.yml` の `dependencies` のjobの `cargo deny`（取得元・ライセンス・既知の脆弱性）と、actionのSHA固定・読み取りだけの既定の権限がその検査を担う（Step18でこの理由に直した。Step17では誤って差分テストのjobを理由にしていた）。Step19で、NFR8のnotesの後半（692264fa時点の差分テスト・3OSの結果）は供給網の検査の結果ではなく、当時の `u8-native-diagnostic.yml` が動かしたものだと明記した（review-08のR-14）。reverseから、消えた `u8-native-diagnostic.yml`・`u8-current-verification.yml` の行を外した（27行→25行）。NFR3・NFR9のnotesの先頭に、692264fa時点の旧pin・旧runであることと今のtoolchain・CIの記録の場所を書いた。statusとidは変えていない。
- **U8の受け入れが今どこで動くか（R-11）**：`diff_u8` は `ci.yml` の差分テストのjob（143行目）、3OSのテストは `ci.yml` の `test` のjobがU1_PACKAGES全体を `cargo test` で動かし `u8_` を含む、workspaceの行80%のcoverage、fmt・clippy・deny、ASanは `u11-fuzz.yml`・`u14-fuzz.yml`。**今は測られていないもの**：U8専用のnative診断のrun（fresh Linux 29件とrunner 1件の個別のログ）、`u8_` の56件を名前で個別に記録する検査、324入力の前後のハッシュの照合と実compiler・設定の記録。**もともと未検証のもの**：U8のfork/exec/waitのNode/Safari。これらをCIに戻すかは、残りのUnitを見てからまとめて決める（人の判断、2026-10-19）。
- **R-09**：`.github/scripts/u8-current-diagnostic.py` は呼び元が無く、消えた `u8-current-verification.yml` を読むので実行すると失敗する（履歴・実行不可）。ファイルは残っているので、traceability.jsonのreverseとmanifestのその行は残した。消すかどうかは、製品の変更なので次のpushで決める。
- 「現行」で始まっていた見出しは「履歴：…（作成時の見出しは「…」）」にした。本文は変えていない。手順書の古い記述には、計画のときに注記を付けた（R-08）。
- 未検証：この作業ではentry-fを実行していない（checkpointで実行する）。独立再レビューはこの記録の後に行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：Step16〜18（Build and TestのLoop-back 1）（作成時の見出しは「現行Step16〜18（Build and TestのLoop-back 1）」）

2026-10-17。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と正式確認コマンドの更新の途中で、Code Generationの段階全体の作り直しのため、U8を確かめ直した。製品・テストは変えていない。
- 計画の「## Testing Contract」を、memoryの更新で古くなっていたため、今の内容（contract `sha256:7ff27a24…`）に置き換えた。テストの方針（custom、Ordering、Standard、80%下限）は変わらない。
- U8の担当source（source-manifestの27 paths）は、12d6a2f6・1ceae86cで変わったファイル（`crates/paludarium-jit/src/` の5ファイル、`crates/paludarium-wasm/src/abi.rs`、`crates/paludarium-harness/tests/diff_u14.rs`、`tests/guests/u14/` の3ファイル、`packages/paludarium-wasm/` の3ファイル、`mise.toml`）を含まない。
- 下の「履歴：署名head 692264faの検証結果」の数値（workspace全体coverage 10634/11427行＝93.06%、3OSのClippy・deny、CI run 38089705214）は、692264faの時点のものである。その後のU14の変更で `paludarium-jit` と `abi.rs` が変わったので、今のsourceについてのworkspace全体の数値ではない。今回、新しく測り直してはいない。
- 今の正式確認コマンドは `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py`（人が採用）である。2026-10-17のU8 checkpointの検証はexit 0（`source_compatibility: PASS`、`u2_candidate: PASS`、`U15_acceptance: GAP`）だった。下の「正式検査・最終確認の境界」にある候補 `verify-current-u1-u7-u9-u3-u5-u6-u8.py` は、その時点の履歴であり、正式採用されていない。

## 履歴：署名head 692264faの検証結果

（以下の「検証済み」は、署名head 692264faの時点の結果である。U14の変更の後のsourceについての結果ではない。）

検証済み：署名head `692264fab8997c70cc611b6f03ce101c2db9bef2` はGitHub Verified=true/valid。専用CI [38089705214](https://github.com/Marukome0743/paludarium/actions/runs/38089705214) はnative-coverageとLinux/macOS/Windowsの4ジョブ全SUCCESS。製品Rust・guest fixtureを変更せず、専用helper/workflowだけを追加した。

検証済み：fresh x86-64 Linux U8差分29件＋runner1件を実行。fork/clone-vm/vfork、exec/ENOENT/EFAULT/不正ELF/CLOEXEC、wait/割込み/restart/rusage、Rust Command spawn/status/output/missingを既存ケース・比較規則のまま確認した。`wait-fault` はEFAULTでもreapする承認済みLinux動作を保持する。stdout/stderr/exit/statusは既存harnessのcompareで比較し、errnoやPID/rusage性質はguest stdoutの真偽条件へ正規化する。原本は `verification/step14-final-raw/native/target/u8-current-evidence/diff.log`。各入力30秒のwatchdog、kill/reapは既存supportのまま。

検証済み：3OS各56件は本体42（MMU7/Kernel28/Runtime7）と既存Kernel回帰14（pipe7/exec-thread7）を個別の実test名で確認した。関連U5 Kernel27/Runtime6=33件とU6 Kernel49件もignored0・exit0。fmt/Clippy `-D warnings`、deny advisories/bans/licenses/sourcesの4検査も3OSでexit0。正確な全test名とexitは `verification/step15-current-proof.json`。

検証済み：workspace全体coverageはempty profilesからfresh U3 native 23576/1162/CPUID12、instrumented CLI、U8/U5/U6差分を含む既存全workspace入口で測定し、10634/11427行=93.06029579067122%、80%下限を通過した。45測定ファイルの行分母合計11427とJSON totalsが一致する。U8だけのcoverageとは扱わない。旧10899行は歴史的な異なるソースの分母であり、除外を追加して合わせていない。LCOV/JSON/consoleと実exitを保存した。

## 実コマンド・入力と責務

（履歴：署名head 692264faの時点の記述。この節の「現行」「今回」はその時点を指す。今の状態は先頭の「現行Step16〜18」節を参照。）

`.github/workflows/u8-current-verification.yml` に実コマンドを保存した。3OSの入口は `cargo test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu --lib u8_`、関連入口は `--lib u5_tests::`（Kernel/Runtime）と `--lib u6_tests::`（Kernel）。Linux差分は `cargo test --locked -p paludarium-harness --test diff_u8 -- --nocapture`。全体coverageは `cargo llvm-cov clean --workspace`、`show-env --sh`下のinstrumented CLI build、`cargo llvm-cov --no-clean --locked --workspace --fail-under-lines 80`を実行した。測定対象規則を変更せずignore regexを追加していない。

検証済み：実使用Rustは各jobのRUSTC/RUSTDOC実体を明示し、commit32dba69d69c5b10ea89a4042de8d0619f7756203/LLVM23.1.3。準備の公式確認（2026-10-11 JST）はnightly配布2026-10-10、llvm-cov0.9.1、deny0.20.2と一致した。構成を作業途中の日付だけで更新していない。4job全324入力の厳密path/hashと両lockはbefore/after/current一致。原本994ファイルのhashを保存した。初期rootと隔離checkoutの新2診断ファイルの末尾空行差異は署名CIの実bytesへ整合し、例外やfake hashを使わず全324一致を再検査した。

文書根拠：共有requirements FR2.8、unit-of-workのU8、C4 MMU/C6 VFS/C7 Loader/C8 Kernel/C10 Runtimeを保持する。process起動はU8、thread/futexはU5、wasm guest Workerとbrowser processの確認はU11境界で区別する。NFR5は初期guest quotaを追加しない方針を保持し、PIDのLinux ABI範囲やexec引数の検査は既存の境界として残す。ホスト資源の無制限保証ではない。

## ASanの限定再利用と未検証

（履歴：署名head 692264faの時点の記述。この節の「現行」「今回」はその時点を指す。今の状態は先頭の「現行Step16〜18」節を参照。）

検証済み：U9/U5/U6の保存証拠の保守的な132製品・依存入力（crates/fuzz、root/fuzz lock、toolchainを含む）が現行と一致する。実compiler32dba/LLVM23.1.3、cargo-fuzz0.13.2、sanitizer=address、detect_leaks=1、LSan suppression、seed1、600秒、timeout30、rss2048、既存default max_len4096を固定した成功jobのみ限定再利用する。load_elf/syscall_args/mmu_ops/vfs_pathsはU9保存の同instrumented binary結合、threads/futex/events/socketsは各U5/U6の601秒原本へ結合する。U9 87/U5 426/U6 1144原本hashも今回照合した。対象別receipt・binary/原本hash・設定は `verification/step15-sanitizer-reuse.json`。新U8 headでfresh fuzzを実行したという主張はしない。

未検証：U8 fork/exec/waitのNode/本物Safari実行。共有launcher20件やU6の102件成功で代替しない。全process lifecycleをfuzzで網羅した保証、並行セッションID競合の完全解消も未検証。既存clone3/process-group waits/stop-continue通知等の範囲を拡張していない。

## 失敗と歴史的証拠

（履歴：署名head 692264faの時点の記述。この節の「現行」「今回」はその時点を指す。今の状態は先頭の「現行Step16〜18」節を参照。）

初回run38089177224は3OS validatorがFAILした。製品testの実exitは0だが、診断filter `u8_tests::` が既存pipe/exec-thread14件を漏らし、本体42件しか実行していなかった。旧入口 `u8_` へ1箇所戻す承認済み訂正後、新runで本体42と回帰14をすべて実行した。テストを水増し・削除していない。初回の「u8_tests::で56件」報告は誤りで、原本 `current-u8-local.log` と `step14-first-ubuntu-job.log`、取得artifactを保持する。初回native-coverage jobのみSUCCESS（10633/11427=93.0515%）で、初回run全体はFAIL。最終10634とは分ける。

歴史的完成時source06d58952の担当25path中6変更、現行322の旧commit投影207一致/34変更/81未存在、旧nightly10-01と現在の相違は `verification/current-source-audit.json`。これは現行pathの投影であり旧commit全入力数を表さない。古い全体92.75%や25path checkerは現行U8の合格として再利用しない。元summary/trace/manifestは `verification/step13-historical-*` へ保持した。

## 正式検査・最終確認の境界

（履歴：署名head 692264faの時点の記述。この節の「現行」「今回」はその時点を指す。今の状態は先頭の「現行Step16〜18」節を参照。）

独立したrequirements本文60 IDsと割当定義により、U8必須10をOK、他Unit40をDeferred、集約10をN/Aへ分類した。sensor/framework/要件割当は変更しない。今回の正式sensor原本は `verification/step15-formal-sensors.json` へ保存する。

（履歴：2026-10-17のStep17の時点で、この候補は正式採用されておらず、今の正式確認コマンドはU2の `u2_candidate.py` である。上の「現行Step16〜18」節を参照。）当時の新最終確認候補：`python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3-u5-u6-u8.py`。AST構文のみ検証済み、未実行。旧U6 owning checker `verification/verify-current-u1-u7-u9-u3-u5-u6.py` を固定SHAで変更せず呼び、先行証拠を維持し、新U8の全324実bytes/署名head/4job/原本exit/56実test名/全体coverageを追加検査する。これは共有検証契約の単一sibling integrationファイルであり、他Unit成果物の変更はない。人のexact command承認と独立レビューはrootが担当する。
