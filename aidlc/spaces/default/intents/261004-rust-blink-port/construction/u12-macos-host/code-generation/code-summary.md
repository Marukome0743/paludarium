# U12 macOS Host code summary

## 現行Step13〜15（Build and TestのLoop-back 1）

2026-10-18。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）、U11のSafariの待ち時間の修正（2b8723ab・57a8c96f）と正式確認コマンドの更新の途中で、Code Generationの段階全体の作り直しのため、U12を確かめ直した。製品・workflow・source-manifest.json・traceability.jsonは変えていない。

- (a) U12の担当source（source-manifestの全ファイル）は、上の変更で変わったファイル（U14のJIT・wasm・テスト、U11の `packages/paludarium-wasm/tests/u11-browser-driver.mjs`・`.test.mjs`、`mise.toml`）を含まない。作業コピーはe4f84768（Steps11〜12のworkflowの修正を含む）と同じである（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <source-manifestの全ファイル>` がexit 0）。
- (b) 下の「履歴：Steps11〜12」節（作成時の見出しは「現行Steps11〜12」）の「未確認」は、その時点の記述である。その後、U12の品質CI（u12-quality、`macos-host` jobを含む）は、1ceae86c（run 39028303336）・2b8723ab（39044793102）・57a8c96f（39073501121）で成功した。57a8c96fのrunは、1回目に差分テスト（x86-64 Linux）のjobが失敗し、失敗したjobだけを再実行した2回目で成功した。
- (c) 末尾の「梱包と範囲」節が挙げる `verification/verify-current-u12-macos-host.py` は採用前の候補である。今の正式確認コマンドは、人が採用した `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py --entry-sha256 56870072810100fa97456ced54a0732e8696489dcb297fa38aa17c0a39978ca7 --binding-sha256 a3d81077e557df7acee86878656360088880b13a75c4c100a68aa748c0450905` である。
- (d) 2026-10-18のU12 checkpointの、今の正式確認コマンドでの検証はexit 0（`source_compatibility: PASS`、`u11_candidate_v2: PASS`、`old_chain_source_compatibility: PASS`、`U15_acceptance: GAP`）だった。
- (e) Step15（2回目のRequest Changes）で、再レビューの新しいMinor 2件を直した：「現行検証と再実行」の見出しを「履歴：検証と再実行」に変え、末尾の括弧書きがその段落全体（Step10時点の記述）にかかることを明記した。
- 下の節は、それぞれの時点の履歴として読む。下の節の本文にある「現行」は、その節を書いた時点の現行を指す。

## 履歴：Steps11〜12（作成時の見出しは「現行Steps11〜12」）

Build and Testの準備中の人の指示による差し戻し。U15のrun 38994430947（`verification/u12-quality-38994430947/README.md`）で、u12-native-first.yml のゲストビルドが aube の `cargo deny` で exit 1 になり、u12-quality.yml に `PALUDARIUM_TEST_NODE` がないためJITの実Wasm試験9件と diff_u14 がpanicし、`macos-host` job がskippedになった。これに対応して、U12の2つのworkflowだけを直した。

変更した2行：

- `.github/workflows/u12-native-first.yml` 49行目：`bash scripts/u10-build-guests.sh target/guests/u10 2>&1 | tee target/u12-native-first/build.log` を、fork の commit ce0b746 と同じ `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name 2>&1 | tee target/u12-native-first/build.log` に置き換えた。このjobには setup-python 3.15.0 がすでにあり、`tests/guests/u10/build.py` が `--advisory-policy u15-fixed-aube-zip9-name` を受け付けることをソースで確かめた。
- `.github/workflows/u12-quality.yml` のworkflowの `env`（22行目、`CARGO_TERM_COLOR: always` の次）：`u14-quality.yml` 21行目と同じ `PALUDARIUM_TEST_NODE: node` を足した。

他の行、閾値、Actions の SHA 固定、権限は変えていない。製品source、試験、スクリプト、`source-manifest.json`、他Unitの記録も変えていない。U9で直した共有workflow（ci.yml・u10-native-diagnostic.yml・u11-acceptance.yml）は今回変更していないが、再レビューの対象に含める。

確認の結果（actionlint 1.7.12、shellcheck 0.11.0 を明示）：

- 実行したコマンド：`/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u12-native-first.yml .github/workflows/u12-quality.yml` は exit 1。
- `u12-native-first.yml`：指摘0件。
- `u12-quality.yml`：指摘5件。どれも変更前からある「既存の指摘」で、変更前のファイルにも同じ5件があった（変更前は63/159/275/298/298行、1行足したので変更後は64/160/276/299/299行）。今回は直していない。
  - 64行目 SC1090（warning）：`source <(cargo llvm-cov show-env --sh)` の読み込み先を追えない。
  - 160行目 SC2086（info）：`$U1_PACKAGES` を引用符で囲んでいない。
  - 276行目 SC1090（warning）：64行目と同じ。
  - 299行目 SC1090（warning）：64行目と同じ。
  - 299行目 SC2086（info）：160行目と同じ。
- 変更した2行（u12-native-first.yml 49行目、u12-quality.yml 22行目）には新しい指摘がない。

未確認：CIでの実行はまだ行っていない。push とCIの起動は、Build and Testで人の承認を得てから行う。このため、ゲストビルドの `cargo deny` が通ること、JITの実Wasm試験9件と diff_u14、`macos-host` job が今回の変更で成功することは確認していない。以下の節の記録（Step10までの証拠）は、変更前のworkflowに対するものである。

## 実装

macOSのNativeHostへDarwin端末観測を接続した。libcのhost-owned termios/winsize bufferを使用し、LinuxゲストABIへflag・baud・control characterを明示変換する。未知flag・未対応速度はEINVAL、tcgetattrの非端末ENODEVだけは端末なしへ限定変換する。VMIN/VTIMEの255は数値として保持し、他のdisabled control characterはLinuxの0へ変換する。ゲストポインターやsyscall番号をDarwinへ渡さない。

既存clock、threads、capability filesystemを維持し、Host共通7件・FS7件、Darwin変換7件・本物PTY7件の計28件を検査した。Rust/libc依存・両lock・明示compilerを最新確認nightly-2026-10-11へ整合した。固定probe/aube source、fixture、CDLA限定条件、比較mask、ゲスト30秒制限は保持した。

端末ABIはC2の観測用subsetであり、Darwinの全拡張flag/baudをサポートする主張はしない。未対応flag、片側flow-control、未対応baudは曖昧に丸めずEINVALを返す。対応表とnegative境界は`verification/darwin-linux-terminal-mapping.md`に列挙した。端末設定変更APIは今回追加していない。

## 差分検証

署名済みheadは`a275bd3d6f08bf48c1a58dead339240b5364af4c`、累積24 application files。公開履歴とexact parent/file数は`verification/publication-history.json`、対象は`source-manifest.json`。旧U11 baselineの399原本をhash固定し、旧全検査を保持するbridgeと現行342入力の検査を分離した。

Linux x86-64のfresh native期待値をDarwin製品実装より先に取得した。同じ固定guestをmacOSのprimary14＋default VFS2、original argv14＋default VFS2と比較する。primaryは既存stdout/stderr/exit完全比較、original install/frozenだけは既存U10補足条件を用い、raw stderrを保持する。他12件のstderr比較は維持した。

## 履歴：検証と再実行（作成時の見出しは「現行検証と再実行」）

CI run38125760476 attempt1は27成功・2失敗。macOS original default installは30.013886秒でkill、SafariはWebDriver session creationに失敗しguest未実行だった。全原本は`verification/step10-failed-ci-attempt1/`に保存した。同じinstrumented binaryとfresh fixtureの手元3回は3.585／3.594／3.808秒で成功したが、初回CI timeoutの原因は未特定である。CI負荷原本は無く、負荷原因やinstrumentation原因を断定しない。

同headのfailed-only attempt2ではmacOSとSafariが成功した。旧成功27は新job IDに見えるが実行時刻・stepsは初回と同一であり、旧原本と厳密に結合する。新2jobは新実行時刻・新artifactを別に検査する。成功した再実行を初回停止原因の完全解消とは扱わない。

11 ASan/LSanは初回の同head・同compilerで各601秒、全exit0。CPU4096／MMU4608、入力timeout30秒と既存LSan suppressionを維持し、両lock・binary・source before/afterを保存した。最新moduleを用いたJS固定5file coverageは426/455、93.6263736264%。Node API・32 unit tests・14guestの新原本は`verification/step10-js-results/`に保存した。旧coverageを現行合格へ読み替えない。

## 検証済みと残件

検証済み：3OS品質、依存4検査、Linux差分、workspace coverage、production wasm、11ASan、4環境のCI job成功、runner22回帰、candidate32回帰。Host固定6fileは890/987行（90.172239%）、Python固定3moduleは107/109行（98.165138%）。macOS primary14＋default2の最大5.435823秒、original14＋default2の最大19.449718秒。現candidateの全診断はexit0（116.091809秒）。342署名入力・旧全検査・retry provenance・全artifact・全終端gateを省略せず通過し、`verification/step10-full-diagnostic.{json,log}`に実command/出力/hashを保存した。これはレビュー前診断であり正式確認コマンドの実行、独立レビュー、完了承認は未実施。

32回帰の実commandは`python3 -m unittest discover -s construction/u12-macos-host/code-generation/verification -p 'test_step10_*.py' -v`（実際の絶対Pythonとworkspace相対探索pathは`verification/step10-regressions.json`）。exit0、全test名・出力を`verification/step10-regressions.log`へ保存した。`test_node_exact_full_slice_schema`、`test_wasm_exact_fourteen_object_inventory`、`test_duplicate_manifest_or_json_keys_rejected`、`test_failed_job_needs_new_execution_time`などが誤結合を拒否する。

未検証：初回macOS timeoutの完全な原因解消、並行セッションID競合の完全解消、U13 Windows Host guest動作、U14 JIT性能。今回のmacOS guest結果とWindowsの一般unit test成功を混同しない。

## 梱包と範囲

（履歴：この段落はStep10時点の記述で、次に挙げる `verify-current-u12-macos-host.py` は採用前の候補である。現行の正式コマンドは先頭の「現行Step13〜15」節を参照）最終candidateは`verification/verify-current-u12-macos-host.py`（intent直下verification）。正式実行は独立レビューと確認コマンド承認後。必要なartifact、署名chain、source inventory、fail-closed回帰、受入項目の索引はU12の`verification/step10-acceptance-audit.md`に整理した。strict guard、coverage80%下限、ゲスト30秒、固定guestと比較条件を維持する。

Application342入力は製品・テスト・設定の署名source検査であり、確認スクリプト自身を含まない。確認スクリプト・補助predicate・U12計画/手順/成果物は、レビュー前の独立verification-proofで別にSHA256固定する。旧SCM/source bridgeの安全性を確認スクリプトの自己主張だけへ依存させない。

正式produce検査はplan・unit-test-instructions・code-summaryの3 Markdownとtraceability JSONがPASS。traceabilityは全IntentのIDを宣言するが、U12担当外46 FRは上流owner/required_forに基づくDeferredとし、既完了Unitの承認を取消さず、U12の新合格を主張しない。

別途engine所有code-generation-questions.mdのrequired-sections検査はFAIL（fire44b215ae、H2=Plan Approvalの1件）。正式produce3 Markdownへ混入せず、承認fingerprint/回答を含む生成ファイルは編集しなかった。これはframework生成Q&Aとgeneric sensorの不適合として失敗原本を保持し、独立レビューへ提示する。
