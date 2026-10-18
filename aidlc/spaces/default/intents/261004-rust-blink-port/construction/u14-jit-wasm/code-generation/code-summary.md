# U14 JIT Wasm — 208fd965

## 現在の状態（2026-10-19 JST）

27d05de1の後のU14の確かめ直し（review-13、NOT-READY）の指摘を、Step48でU14の記録だけで直した。製品・CI・workflow・入口・binding・ほかのUnitの記録は変えていない。下の「履歴：」の節は、それぞれ書いた時点の記録である。

- **head**：fork `Marukome0743/paludarium` の `codex/build-and-test` の署名head `27d05de1`（鎖 e3c29d1d → 8b415a7c → 8360be2e → 27d05de1、すべてVerified）。27d05de1のCIは8 runとも成功した（U12 current full quality（run 39149189719）はattempt 1で `u12-fuzz / fuzz (vfs_paths)` だけがapt.llvm.orgへの接続で失敗し、人の承認でそのjobだけをやり直したattempt 2で成功した）。U14 current full quality（run 39149187727）とU14 fresh thirteen target ASan and LSan（run 39149194521）も成功した（U15の `construction/u15-release/code-generation/verification/ci-27d05de1/ci-27d05de1.json`・`ci-jobs-27d05de1.json`。品質の原本は同じ場所の `u14-quality-39149187727/`）。
- **今の正式な確認コマンド**：U15の `entry-e3c29d1d/entry-f.py --entry-sha256 185677712836e73d6a716657a24521c42581504550f9f398c5bb1ca7eaa4a46f --binding-sha256 9a7e8e396706f83bba6de41c1e032dade923b2cf953decb786a2b9450ce8acf9`（binding-e06f、command SHA-256 `00f5c8832e04f7d27b30c6b445fdc30e0e5d233dfa5452e02c2c99368a08a159`。このコマンド行のSHA-256で、checkpointが検証のたびに計算し、`aidlc/spaces/default/intents/261004-rust-blink-port/.aidlc-construction-checkpoints/u14-jit-wasm/unit.json` の `command_sha256` に記録する）。2026-10-19に人が採用した（intent直下の `aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の1行目）。entry-fは `aidlc/` の外の作業コピーのbytesだけを比べるので、U14の記録の変更はこの確認に影響しない。2026-10-18の時点（Step47）は、U15の `entry-e3c29d1d/entry-c.py` が正式な確認コマンドだった。U14の入口（`u14_candidate.py`・`u14_candidate_v2.py`）とそのbinding・回帰は、どれも今の正式な確認コマンドではなく、履歴として中身を変えずに残す。
- **1ceae86cから27d05de1までに変わったU14のmanifestのファイル**（`git diff --name-only 1ceae86c 27d05de1 -- <manifestの全ファイル>` と `git log` を読み取りで確かめた）：
  - `.github/workflows/u1-u14-source-bound.yml`・`u14-fuzz.yml`・`u14-native-first.yml`・`u14-quality.yml`・`u14-wasm-acceptance.yml`：8360be2e（2026-10-19、U15 Step22〜28）で、主に `push:` の起動条件を消した。今の `u14-quality.yml` は呼び出し（`nightly.yml` から）と手動、`u14-fuzz.yml` も呼び出し（`nightly.yml` から）と手動、`u1-u14-source-bound.yml` は手動でだけ起動する。`u14-native-diagnostic.yml` は変わっていない。
  - `.github/workflows/u14-cost-diagnostic.yml`：8360be2eで消えた。Step48でsource-manifest.jsonのwritesから外した（91→90件）。
  - `Cargo.lock`・`fuzz/Cargo.lock`・`packages/paludarium-wasm/package.json`：bb197e04（2026-10-18、U15の版0.1.0）で、paludariumの版が0.0.0から0.1.0になっただけ。
  - 変わっていないもの：U14のコード（`crates/` のJIT・CPU・MMU・Runtime・wasm、`packages/paludarium-wasm` のJS、`tests/guests/u14/`、`scripts/`、fuzzの対象）。
- **FR8.3（JITありが有意に速い）**：根拠は今も、1ceae86cのU14 quality run `39030957672` のattempt 1での1回の測定（片側p=1/1024）である（下の「履歴：現行Steps30〜44」節の「正式性能（FR8.3）」の項）。そのあとU14のコードは変わっていない。測り直しはしていない。
- **traceability.json**：最上位に `history_note` を足し、11行の `justification` の先頭に、27d05de1の時点の注記（U14のコードは変わっていない、27d05de1のU14 qualityとASan/LSanの成功、後ろの「現行（2026-10-18…）」はその時点の記述）を足した。status・id・targetは変えていない。
- **`verification/loopback1-next/README.md`**：先頭に、「Step46（現行）」の「現行」「まだ採用されていません」「署名headは57a8c96f」は2026-10-18の時点の記述で、今の正式な確認コマンドはentry-fである、という節を足した。下の本文と、入口・binding・回帰のファイルは変えていない。
- **2026-10-18の時点（Step47）の記録**：Step47では、再レビュー（`reviews/review-11.md`）で残していたMinor R-14・R-15・R-16を記録で直した（traceability.jsonのFR8.2・FR6.3・FR7.2の行にU13 quality `39028305765` とU14 quality `39030957672` がattempt 2で成功したことを足し、NFR2・NFR3・NFR8の行の参照先をFR8.1の行（7 run）に直した）。Steps45〜46の記録は `verification/loopback1-next/README.md` の「Step46」節にある。
- **確かめていないこと**：この節を書いた時点で、新しいCI・性能測定・fuzzの実行はしていない。上のCIの結果はU15の記録の保存済みの証拠である。

## 履歴：現行Steps30〜44（Build and TestのLoop-back 1）（作成時の見出しは「現行Steps30〜44（Build and TestのLoop-back 1）」）

2026-10-18 JST。Build and Testで、FR8.3（JITありが有意に速い）が不合格になった（head `bd247f1e`、run `39009460781`、AMD EPYC 7763、Node v26.12.0、JITなし平均5.4972097502秒・JITあり平均5.4987317293秒、p=529/1024=0.5166015625。原本は `construction/build-and-test/verification/ci-bd247f1e/u14-quality-39009460781/u11-node/performance/observations.json`）。人はRetry with fixを選び、U14のCode Generationに戻した。この節は、そのあとのSteps30〜44の記録である。

- Step30（診断。製品は変えていない）：記録は `verification/loopback1-diagnosis/`。probeを手元のnative interpreter（macOS arm64）で1回実行し、17,704,550境界を全数で数えた。今のJITが受け付ける形式は実行の25.30%だが、3命令以上のblockに入るのは0.248%（43,929命令、平均3.001命令）だけで、対応形式が未対応命令で細かく分断されていた。整数SSE群だけを足すと30.58%（平均25.6命令）と見積もった。命令の数だけの見積りで、時間は測っていない。
- Step31（費用。製品は変えていない）：記録は `verification/loopback1-cost/`。Apple M1・Node 26.12.0の実Worker microbenchで、interpreter 110.4 ns/命令、今のJIT 5.8 ns/命令、blockの固定費用587 ns、損益分岐5.6命令。probe全体の変化の見積りは、整数SSE群だけで約−13%〜−7%、GPRのregister形式で約+2%〜+8%、byte比較群は測り方で向きが逆（−13%〜+24%）。人は「SSEだけ先に」を選んだ。
- Steps35〜36（GPRのregister形式、byte比較群）は、人の選択により行っていない。C9の契約は変えていない。
- Step32：整数SSE群のnative差分ケースを先に用意し、署名commit `12d6a2f63c205b672d30e8bcb104dc0ee75932ac` で送った（4ファイル。下の表）。
- Steps33〜34：JITの状態にXMM0〜15を足し（trap時のrollbackを144 byteから400 byteへ）、整数SSE群（register形式だけ）をwasmのv128へ翻訳する変更を、署名commit `1ceae86ce303a1019e97ac7d162ce0efa9fadd50` で送った（10ファイル。下の表）。memory operand・VEX・prefixの組合せはfallbackにした。
- Step37（手元の確認）：記録は `verification/loopback1-next/step37-local.md`。workspace全体の `cargo test` のexit 101は、既知の `diff_u8` の `u8_runner_ready`（x86-64 Linux以外では合格にしない作り）1件だけだった。ほかの手元の検査（jit・cpu・wasmの単体テスト、fmt、clippy、wasm32のビルド、U14のJS試験153件、Python試験131件。どちらも `PALUDARIUM_TEST_NODE` を設定）はexit 0。製品の受付判定でprobeを数え直すと、18,511,472命令のうち5,435,697命令（29.36%、平均24.96命令）がblockに入った。手元の時間は診断で、FR8.3の根拠にしない。
- Step38（CIと正式性能）：2つのcommitはGitHubでVerified（`construction/u1-skeleton/code-generation/verification/loopback1-next/ci-1ceae86c.json`）。1ceae86cのCIは、CI `39028285747`（23 job）、Release package checks `39028285755`、U12 quality `39028303336`（29 job）、U13 quality `39028305765`（attempt 2。attempt 1は差分テストのjobが未観測のIntel `000606a6` で設計どおり止まり、そのjobだけ再実行して成功）、U14 fuzz `39028307842`（13対象）、U1 U14 source-bound `39028309948`（7 job）、U14 quality `39030957672`（attempt 2、34 job。attempt 1は `windows-host` のcoverage計測付きprobe-allが30秒の上限で止まり、そのjobだけ再実行して成功。遅かった原因は分かっていない）がすべて成功した。job一覧は同じ場所の `ci-jobs-1ceae86c.json`。
- 正式性能（FR8.3）：U14 qualityのrun `39030957672` のattempt 1で1回だけ測った。原本は `verification/loopback1-next/perf-39030957672-observations.json`（SHA-256 `b827a5e1c1ece977be6acab4988d5c1d9dc8a1d54cd5877451eb6d241e402b7c`）。head 1ceae86c、AMD EPYC 9V74、Node v26.12.0、seed 5321（bd247f1eの不合格と同じ順序）、warmup各1（2件ともPASS・exit 0）、各mode10回の20標本。JITなし平均4.5277275564秒、JITあり平均3.6349344776秒（約19.72%速い）、1024通りの符号反転で片側p=1/1024=0.0009765625。20標本はすべてprobe 8項目PASS・exit 0・時間切れなし（最長約4.64秒）で、JITありの10標本はすべてJITのblockを実行した（executedBlocksの最小207,275）。この判定は原本から計算し直して一致を確かめた。測り直しはしていない。測ったmoduleは `d892ea2879dd160aa3e81f0afafef56b73d826bcfa88995b310a60e49d51faad`、probeは `f09911e4b21f52af843a13a426ad321c5a04b94cbde388bd33d738c695516e30`、oracleは `cb3372b24dd756cc0e899b84ea363640e5d28d2d158da2ca34ebb6a6bf47cc73`。moduleと同じrunのbuildとの結び付きは、U1のbinding-02（module receipt）で検査している。bd247f1eの不合格とはCPUの機種が違う（EPYC 7763と9V74）ので、両者の差をそのまま比べられる量とは言わない。ほかのCPUやブラウザでの速さの改善は主張しない。
- 12d6a2f6のU14 quality（run `39025059974`）でも、Node jobの性能のstepが1回動いた（attempt 1、job `117375914433`、2026-10-17 10:42〜10:43 UTC。attempt 2は同じjobを引き継いでいて、動き直していない）。整数SSEのJITを入れる前のheadの測定で、その標本は読んでいない。FR8.3の根拠にしない。
- Step39（Safariのsession作成の待ち時間）：U11を開き直して直した（U11 Steps29〜31。署名commit `2b8723ab`・`57a8c96f`。人の承認済み）。57a8c96fのPR CI（`39073492190`）とU12 quality（`39073501121`、attempt 2）で本物のSafariのjobが成功した。57a8c96fではU14 qualityを起動していない。1ceae86cから57a8c96fまでの変更はU11のWebDriverの試験の道具の2ファイルだけで、U14のファイルは変わっていない。（2026-10-19 注記：1ceae86c〜57a8c96fの範囲の記述。そのあと27d05de1までに、U14のworkflowと版0.1.0の両lock・package.jsonが変わった。U14のコードは変わっていない。先頭の「現在の状態」節のとおり）
- Step40：`mise.toml` に `"npm:npm" = "12.2.0"` を足した。U1の入口（binding-02）がこの1行だけを許している。
- 今の正式確認コマンド（人が採用済み）は、`/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py --entry-sha256 56870072810100fa97456ced54a0732e8696489dcb297fa38aa17c0a39978ca7 --binding-sha256 a3d81077e557df7acee86878656360088880b13a75c4c100a68aa748c0450905` である。このコマンドは、この節を足したcode-summary.mdとtraceability.jsonの変更で止まる（U1がU14の記録3ファイルを固定時のbytesで照合しているため）。（2026-10-19 注記：2026-10-18の時点の正式確認コマンド。今の正式な確認コマンドはentry-fで、先頭の「現在の状態」節のとおり）
- Step43で、この記録の変更を許す新しい確認の入口 `verification/loopback1-next/u14_candidate.py`（binding-06）を作った。入口とbindingのSHA-256の値と結果は同じ場所のREADME.mdにある。この入口の採用はまだで、独立再レビューと人の承認が残っている。（2026-10-19 注記：その時点の記述。この入口は2026-10-18に仮に採用された後、正式な確認コマンドはU15の入口に替わった）入口や検査のexit 0を、unitの完了や全要件の達成とは呼ばない。
- 入口の結果にある `U15_acceptance: GAP` は、全体の受入を担うU15が未完了という既知の表示で、U14の不合格を意味しない。

送った2つのcommitで変えたU14のファイル（`git diff-tree` の結果。すべて `source-manifest.json` の `writes` に既にある）：

| 署名commit | 変えたファイル |
|---|---|
| `12d6a2f63c205b672d30e8bcb104dc0ee75932ac` | `crates/paludarium-harness/tests/diff_u14.rs`、`tests/guests/u14/native.c`、`tests/guests/u14/test_validation.py`、`tests/guests/u14/validation.py` |
| `1ceae86ce303a1019e97ac7d162ce0efa9fadd50` | `crates/paludarium-harness/tests/diff_u14.rs`、`crates/paludarium-jit/src/block.rs`、`crates/paludarium-jit/src/bridge.rs`、`crates/paludarium-jit/src/emit.rs`、`crates/paludarium-jit/src/lib.rs`、`crates/paludarium-jit/src/microbench.rs`、`crates/paludarium-wasm/src/abi.rs`、`packages/paludarium-wasm/jit-support.mjs`、`packages/paludarium-wasm/tests/u14-cost-profile.test.mjs`、`packages/paludarium-wasm/tests/u14-jit.test.mjs` |

`source-manifest.json` は変えていない。engineが読むこのファイルは `stage`・`unit`・`version`・`writes`（各要素は `path` と `repo`）以外の項目を受け付けないので、署名headはここ（この表）に記録した。今の署名headは `57a8c96f610d6e02234354e5e4fb5cac068d5036` で、U14のファイルのbytesは1ceae86cと同じである。（2026-10-19 注記：2026-10-18の時点の記述。今の署名headは27d05de1で、U14のworkflowと版0.1.0の両lock・package.jsonは1ceae86cと違う。U14のコードは同じ。先頭の「現在の状態」節のとおり）

主張しないこと：unitの完了、U15の受入、配布の公開、手元の診断の時間を性能の根拠にすること、有限時間のfuzzを任意入力の安全性の証明とすること。

下の節は、それぞれの時点の履歴として読む。下の節の本文にある「現行」「今回」「未実施」「未検証」「未採用」は、その節を書いた時点（署名head 208fd965、2026-10-16 JST）のものを指す。

## 履歴：208fd965の記録（作成時は見出しのない冒頭の段落）

検証済み：署名head `208fd9652528fbb9002a7bd25c0cb1f2105a5738`（GitHub Verified、branch `codex/u14-jit-wasm`）について、JIT性能とU9専用coverageの不足を修復した。今回の最終製品差分はCPUの既知negative hintをbudget比較より先に判定する1条件の並べ替えである。以前のCPU policy const特殊化、JS bridgeの不要なallocation/callback削減、既存ISA限定JIT・negative hint・実命令数課金を保持する。新ISAやbatch実装は加えていない。

診断は別featureで120 fields・有限site表・microbenchmark・通常module samplingを持つ。通常moduleには診断exportsを入れず、公開C9/C10/C12、Noop/既定CodeCache、MMU generation/lock、Worker局所性、kill/syscall/fault境界、144byte rollbackを保持した。U14限定aube overlayは元source/lockを保存し、ビルドコピーのrustlsのみ0.23.46とする。監査例外は増やしていない。

## 履歴：正式性能と4環境（208fd965）

検証済み：品質成功後のmanual run `38840433942`、元Node job `116781223162` の固定20標本＋warmup各1を1回だけ取得した。interpreter平均5.856590694899998秒、JIT平均5.696370400100001秒、改善2.7357263491%、全1024符号反転の片側p=7/1024=0.0068359375。全probe成功、時間制限、実JIT実行、固定seed/順序と実commandの成功を原本から再検査した。同moduleの性能再試行は禁止した。

module `fb2fdb513866fd86979b6b5f9127f256a5bcfcb50ba1ccba49a220fb819258e2`、fresh native oracle `b18979f8bbf9508cfb8b668f40aba1b1b9b3a153eef550e0f85524ac6891e1f0`、probe `f09911e4b21f52af843a13a426ad321c5a04b94cbde388bd33d738c695516e30` を結合した。原標本・Node/V8版・machine・開始前ps/loadavg・終了後loadavgを保存した。psに並列cargo/fuzzer/browser測定はなく、runner常駐processと当該Nodeを区別する。完全な無負荷状態や他環境の速度改善は主張しない。

初回Safari job `116781223111` はsession作成の約10秒timeoutで0比較・exit1となった。attempt1全metadata/公式ZIP/性能原本を封印後、Safariだけ1回再実行し、job `116783397511` で28比較に成功した。attempt2は34/34成功。Node継承job `116783399354` の開始・終了・全step時刻/結果は元jobと完全一致し、20標本を再実行していない。初回失敗を成功へ置換しない。

同じformal入力組に対し、Node/Chromium/Firefoxは元実行、Safariは単発retryの原本を用い、112 CPU/native/interpreter/JIT比較と32 filesystem比較を再計算した。主なコマンドは実体Node26.12.0による `verification/jit-u9-next/recheck-formal-environments-208fd965.mjs`（exit0、112/32）、実体Python3.15.0による `bind-formal-208fd965-isolated-node.py`（exit0、classification=PASS）。この別checkerは初回whole-run failureを明示保持する。旧binderは変更していない。完全な引数は `formal-analysis-208fd965-01/outer-execution.json`、Node再計算の引数は同dirの `recheck-exit.json` に保持した。

## 履歴：正しさ・品質・U9（208fd965）

検証済み：主品質 `38836468601` 35/35、source-bound `38836468596` 7/7、standalone fuzz `38836468590` 13/13が成功した。39品質ZIPと11 source-bound ZIPの計50ZIP/2492raw filesを公式digest・展開全bytesと照合した。signed875は署名tree、compiled223は通常/診断build closureとして区別する。source-manifestは所有91パスを申告する。90パスは現在root bytesと署名pinが一致し、残りの `packages/paludarium-wasm/tests/u14-single.mjs` は未送信のローカル診断helperとして別SHAで固定する。このhelperはCI未検証で、compiled223・正式測定・配布importの入力には含めない。rootの全875一致とは主張しない。

- Rust JIT 1668/1817=91.7997%、feature集合4548/5260=86.4639%、JS515/584=88.1849%、Python435/527=82.5427%、U9 checker Python282/294=95.9184%。
- U1 11689/12509=93.4447%、workspace12161/13010=93.4743%。
- U9専用既存13集合2766/3292=84.0219%、追加10集合2174/2415=90.0207%。25 instrumented ELF・3 exports・profdata・JSON/LCOVの固定分母と全file集合を原本再解析した。14差分成功/ignore0。
- fresh native13命令ケース、直接実Wasm JE taken/not-taken、prepare中write、epoch/自己書換え/budget/kill/rollback境界を確認した。ローカル最終CPU148成功/native専用2ignored、JIT90、Runtime55、packed import＋実Wasm hello/bridge19成功・skip0。これらlocalはCI compiled223と別closureの記録を持つ。
- 13 fuzz各600秒以上、376 source、両lock・compiler/flags・binary・ASan/LSan原本を照合した。3OS unit/lint、依存advisories/bans/licenses/sourcesの4監査を維持する。

追加full-quality `38836468606` の初回U3差分は未観測Intel profile `000606a6` をfault比較前に拒否した。fixture/binaryと通常23576状態の一致を確認し、原本保持後の単発job retryでは観測済みAMD `00a10f11` で通常23576・fault1162状態が一致した。profile許可・maskは変更していない。このIntel環境のfault意味論は未検証のまま保持する。

主な純粋再検査は `check-quality-208fd965.py`、`recheck-quality-208fd965.mjs`、`check-fuzz13-official.py`、`u9-official-208fd965-proof.json`、`finalize-step25-208fd965.py` に記録する。argv/stdout/stderr/exit・公式run/job/catalog・ZIP・展開原本は `verification/jit-u9-next/` 配下に保存した。checker exit0だけをunit完了と呼ばない。

## 履歴：保存した失敗と残る確認（208fd965）

旧3成果物の完全bytesは `verification/jit-u9-next/step5-before-208fd965/` に保存した。旧canonical/binding・旧023/109 fields・全正式性能失敗・5aの早期実行逸脱・初回CI/解析helper失敗を保持した。元c9の失敗はstderr欠落により原因未特定・未再現のままであり、今回のSafari/CPU環境失敗をその原因と断定しない。

今回の正式性能と必要coverageが条件を満たしたため、親FR8/FR8.3/NFR6とU9を含むNFR3の現在証拠をtraceabilityへ接続する。これは過去のGAPや失敗原本を書き換えるものではない。R-05は他Unitの未解決Minorとして保持する。有限600秒fuzzは任意入力の安全性証明ではなく、JITは既存subsetだけを扱う。

新しい正式検証コマンドはまだ未採用である（2026-10-19 注記：208fd965の時点の記述。今の正式な確認コマンドはentry-f）。最終source/produces固定後の旧全chain、sensor、独立レビュー、人による正式command選択と完了確認が残る。新候補は未統合や欠落を成功扱いせず拒否する。unit完了・配布公開はまだ主張しない。
