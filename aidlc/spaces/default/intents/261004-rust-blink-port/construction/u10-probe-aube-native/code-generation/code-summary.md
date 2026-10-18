# U10 現行ソース再確認サマリ（独立レビュー待ち）

## 現行Step31〜32（Build and TestのLoop-back 1）

2026-10-18。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と正式確認コマンドの更新の途中で、Code Generationの段階全体の作り直しのため、U10を確かめ直した。製品・workflow・source-manifest.json・traceability.jsonは変えていない。
- (a) U10の担当source（source-manifestの42 paths）は、12d6a2f6・1ceae86cで変わったファイル（U14のJIT・wasm・テストと `mise.toml`）を含まない。作業コピーはe4f84768（U9 Step80の `u10-native-diagnostic.yml` の修正を含む）と同じである（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <42 paths>` がexit 0）。
- (b) 下の「履歴：Step30」節（作成時の見出しは「現行Step30」）の「CI未実行」は、その時点の記述である。その後、e4f84768のCI（PR CI 39015770796、u12-quality 39015780495、u13-quality 39015782530）と1ceae86cのCI（u12-quality 39028303336、u13-quality 39028305765）で、U10の差分job（`U10 fixed guests and fresh native differential`）を含めて成功した。
- (c) 下の「履歴：Step26」節（作成時の見出しは「現行Step26」）が挙げるU1の `final_candidate.py` は、その時点の正式確認コマンドである。今の正式確認コマンドは、人が採用した `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` である。
- (d) 2026-10-18のU10 checkpointの、今の正式確認コマンドでの検証はexit 0（`source_compatibility: PASS`、`u2_candidate: PASS`、`U15_acceptance: GAP`）だった。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：Step30：U9が直した共有workflowの再確認

Build and Testからの差し戻し（人の指示）に対応する節です。U10のsource-manifestが持つ2つのworkflowを、U9が承認済みのSteps77〜79で直しました。U10はその変更を再確認するだけで、U10自身の製品、fixture、workflowは変えていません。

- 変更1：`.github/workflows/u10-native-diagnostic.yml` の `native-first` job。checkoutの直後（30〜32行目）に、SHA固定の `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`（`python-version: '3.15.0'`）を加えました。ゲストのビルド（44行目）を `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` に変えました。
- 変更2：`.github/workflows/ci.yml` の最上位の `env`（22行目）に `PALUDARIUM_TEST_NODE: node` を加えました。
- 根拠：U15の記録 `aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/u12-quality-38994430947/README.md`（run 38994430947、head `be45b36ce9d7a65719ba1f86cf6a0b018070741b`）。(1) policyの指定がないため、aubeの依存監査 `cargo deny` がexit 1になり、U10の `native-first` job（117283723628）も失敗しました。(2) `PALUDARIUM_TEST_NODE` がないため、`crates/paludarium-jit/src/bridge.rs` の実Wasm試験9件がpanicしました（3 OS）。run 38994430947が実行したのは `u12-quality.yml` で、`ci.yml` そのものではありません。`ci.yml` の変更は、同じ単体試験が同じ理由で失敗するのを防ぐためのものです。
- 確認結果（2026-10-17、手元で実行）：`actionlint` 1.7.12（shellcheck 0.11.0を明示）で2ファイルを検査し、終了コードは1でした。`u10-native-diagnostic.yml` の指摘は0件です。`ci.yml` の指摘は、今回触れていない87・203・226行目の既存4件（SC2086×2、SC1090×2）だけで、変更した22行目に新しい指摘はありません。既存4件は直していません。
- 未実行・未確認：この変更後のworkflowはCIでまだ実行していません（push・CIの起動は、Build and Testで人の承認を得てから行います）。そのため、U10のfresh native・probe・aubeの新しい実行結果は確認できていません。下の節にある過去の成功を、この変更後の成功として扱いません。
- 範囲：変更したのはこのcode-summary.mdだけです。traceability.jsonとsource-manifest.jsonは封印の対象なので変えていません。

## 履歴：Step26：ルート.gitignoreの位置づけと正式検証コマンド

- R-04：ルート `.gitignore` は、U10のビルド、テスト、probe、aubeの入力ではありません。source-manifest.json（42パス）に含めない、ビルド対象外の共有パスです。2026-10-16のClaude Code harness追加で、そのAI-DLCブロックに `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行が入り、これが今回の再確認（iteration 3）のきっかけになりました。U10のmanifestにある `tests/guests/u10/.gitignore`（中身は `__pycache__/` の1行）と `tests/guests/u10/probe/.gitignore`（中身は `/target/` の1行）は、この追加で変わっていません（Step26でファイルを読んで確認）。
- R-05：checkpointで実行する正式コマンドは、採用済みのConstruction Verification Command `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py`（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）です。2026-10-17の再確認ではexit 0、source_compatibility PASS、U15_acceptance GAPでした。終了コード0はcheckpointの検証記録 `aidlc/spaces/default/intents/261004-rust-blink-port/.aidlc-construction-checkpoints/u10-probe-aube-native/unit.json`（最新の実行を記録し、今後の再検証で更新される）にあり、この再確認の判定は `aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792186532618870000-51059/result.json`（`source_compatibility` が `PASS`、`head` が `be45b36ce9d7a65719ba1f86cf6a0b018070741b`）にあります。`51059`（formal-candidate-1792186532618870000-51059）は2026-10-17の再確認（iteration 3の後）の初回の実行で、正式コマンドは実行のたびに `r05-r11-repair-01/` の下へ新しい `formal-candidate-<id>/` 出力ディレクトリを作るため、checkpointの最新の実行の出力先と判定は `unit.json` の `verification.stdout_tail` に記録され、どの実行も同じ採用済みコマンド（SHA-256 `d799bbb9…`）で、同じ判定項目（source_compatibility、U15_acceptance）を出します。下の「最終候補」段落の `verify-current-u1-u7-u9-u3-u5-u6-u8-u10.py` は採用前の候補として履歴に残すもので（構文確認のみ・未実行）、現行の成功とは扱いません。
- 範囲：今回は記録の文言修正だけです。新しいguest実行、CI、Node／Safari、ASan、U15の受理は主張しません。製品、fixture、source-manifest.json、traceability.jsonは変更していません。

## 概要（Steps19〜25の履歴）

今回追加したSteps22〜25では、旧U10対応表と現行記録の参照を分離しました。旧hash原本の完全一致、現行記録の完全hash・60要件・42パス、局所loaderの成功／例外復元など19回帰が成功しました。新候補の全診断はexit0、旧全検査と34必須品質job・367入力の厳密照合を保持しています。正式検査・独立レビュー・別承認後の最終確認へ進みます。詳細は verification/step24-reference-repair.md。旧 `Trace original digest differs` のexit1を保持し、診断を正式完了へ読み替えません。

今回の対象はSteps19〜21の記録更新です。以下のSteps16〜18の実行結果はコミットcb979713／CI38095031011に結び付いた履歴であり、現在のソースで再実行した結果ではありません。今回新規に実行したのはPython内部44件、runner準備検査と正式文書検査です。適用範囲・入力差分・原本照合は verification/step20-applicability.md に記載しました。製品・既存試験・旧checker・AI-DLC本体・guardを変更していません。

検証済み：42担当パスに欠落なし。旧326入力のhash対象37パス中30一致・7変更、対象外の文書5パスは旧署名コミットとのjj差分なし。両lockとcompiler指定に変更があるため、旧coverage／ASan／Linux guest成功を現行での新規成功へ読み替えません。保存された17分割manifestと1674原本はhash一致しました。新しい独立レビュー・承認済み最終確認・完了承認は未完了です。

## 変更と判断

既存probe標準8項目・固定aube v2.6.1/bd94e42f・C10/C11・fixture・製品処理を保持しました。今回の変更は `.github/scripts/u10-current-diagnostic.py`、`.github/workflows/u10-current-verification.yml` と `native_fs.rs` のcfg(test)内mtime2件だけです。Windowsの100ns精度に合わせ、正負1/99ns→0、100/101ns→100を確認し、Unix1ns・秒・u64最大境界を維持しました。製品mtime変換は変更していません。正確な旧新hashと逆差分は verification/step16-test-delta.json に保存しました。

診断ツールは公式確認済みRust nightly2026-10-10（32dba/LLVM23.1.3）、Python3.15.0、coverage7.16.2、llvm-cov0.9.1、deny0.20.2、cargo-fuzz0.13.2を使用しました。ASan containerのPython3.11.2は固定再現環境の入力監査専用です。全OS道具が最新版とは断定しません。llvm-covの公開show-env出力全体を隔離subprocessへ引き継ぎ、旧診断の未定義RUSTFLAGS/CARGO_ENCODED_RUSTFLAGS失敗を修正しました。

## 検証結果

検証済み：署名Verified head `cb9797138313046b3cf9bbbfcab0515910b81215`、CI [38095031011](https://github.com/Marukome0743/paludarium/actions/runs/38095031011) の5ジョブすべてsuccess。全326入力・両lock・before/after/current、原本1674ファイルの集合/hashを verification/step18-current-proof.json と17分割raw manifestへ固定しました。旧324との差は新診断2入力と承認済みmtimeテスト差分だけです。

検証済み：Python内部44件（core21＋追加23）、fresh Linux native14/emulator16、元argv追加native14/emulator16、probe8/all/environment、aube4・node不在・#1645・0644 fixture・default VFS2操作が成功しました。nativeを先に生成し、同じ新ビルドguestのstdout/stderr/exit・状態を既存maskで比較しました。公開llvm-cov環境preflight、guest-build/native/diff/instrumented U10/coverage/report/Python/wasm/source-auditの実exitはすべて0です。

検証済み：Linux/macOS/Windowsの既存製品回帰、mtime2件、U5 Kernel27＋Runtime6、U6 Kernel49（これらはignored0）、fmt/Clippy-Dwarnings/依存4検査は実exit0。全体lib内のU3 native収集専用ignored入口を全件ignored0とは称しません。Linux coverageはfresh U3 nativeを生成し、空profiles・既存workspace全分母・instrumented CLI/U10を含め10635/11429=93.0528%。Python core evidence/comparison/runnerは除外なし全行137/154=88.9610%。追加5は別集合267/313=85.3035%（build77/92、native49/57、differential89/93、metadata33/52、comparison_args19/19）であり、各追加モジュール80%とは主張しません。

検証済み：固定aube upstream1365入力before/after一致・新static ELF・binary hash・両guest依存4監査・root deny全bytes継承・webpki-root-certs1.0.9限定CDLA全文hashを新receiptへ保存。production wasmビルドexit0。aube4操作の逐次wall time秒（native/emulator）はversion0.015350704/1.322762866、install0.035129085/5.064128053、frozen0.010482534/3.516087382、list0.003274707/1.002548795。各guest30秒期限と停止/回収を維持し、速度閾値を新設していません。

検証済み：ASan132依存・compiler/flags/settings・抑制hashと、新8対象のinstrumented binaryを再評価しました。新build実exit0・旧成功binary SHA完全一致に限り、既存601秒ASan/LSan原本を限定再利用します。原本とtarget単位のbindingは verification/step18-sanitizer-reuse.json。新fuzz実行ではありません。

## 残る確認と再現手順

初回・中間失敗（環境、Windows旧±1ns期待値、llvm-cov引継ぎ）とPython3.12時の成功は別の履歴として保存し、今回の成功へ読み替えていません。bookmark失敗後に不要中間headが一度pushされ、最終3パスheadへ修正しました。中間runのcancelはHTTP403で拒否され、成功証拠には使用しません。verification/step18-python-push-history.json に経緯があります。

未検証：U10 probe/aubeのNode・本物Safari guest実行、後続U11/U12/U13環境の完全合格、全入力保証、背景負荷完全ゼロ、並行セッションID競合の完全解消。今回のproduction wasmはビルドの検証です。formicarium同期は既存source-review文書根拠と現行probe8検証を区別します。

（履歴：採用前の候補。現行の正式コマンドは先頭の「現行Step31〜32」節を参照）最終候補は `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3-u5-u6-u8-u10.py`。旧checker実bytesを保持し、mtime2テストの完全逆差分に限る局所adapter、新326/raw集合/署名CI/実exitを検査します。構文確認のみで未実行です。独立レビューと人によるこの具体的コマンドの別承認・最終確認・完了承認が残ります。承認済みplan/instructions本文は変更せず、完了したSteps16〜18のcheckboxだけを更新します。source-manifestは42担当パス、全60要件を17担当leaf/10集約N/A/33担当外Deferredへ独立分類します。PR作成はしていません。
