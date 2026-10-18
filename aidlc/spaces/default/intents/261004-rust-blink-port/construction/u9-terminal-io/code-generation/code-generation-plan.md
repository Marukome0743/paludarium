# U9 入出力と端末のコード生成計画

## Summary

- Builds: Step81。U9が担当するファイルは、Step80の承認（head e4f84768）の後に変わっていないことを確かめ、今の正式確認コマンドで確かめ直す。製品・workflow・試験・記録は変えない。
- Touches: この計画と手順書のStep81の節だけ。
- Tests: 新しいテスト・CIの実行はない。U9のsource-manifestの全ファイルが e4f84768 の版と同じことを読み取りで確かめ、独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpointを行う。

## 今回の計画：Step81（Build and TestのLoop-back 1：変更がないことの再確認）

2026-10-17。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と、U1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。12d6a2f6・1ceae86cで変わったのは、U14のJIT・wasm・テスト（`crates/paludarium-jit/src/` の5ファイル、`crates/paludarium-wasm/src/abi.rs`、`crates/paludarium-harness/tests/diff_u14.rs`、`tests/guests/u14/` の3ファイル、`packages/paludarium-wasm/` の3ファイル）と `mise.toml` で、U9のsource-manifestのファイルは含まれない。正式確認コマンドは、人の承認でU2の `verification/loopback1-next/u2_candidate.py` になっている。

- [ ] Step 81 — U9のsource-manifestの全ファイルについて、作業コピーが e4f84768（Step80で承認した版）と同じであることを読み取りで確かめる（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <paths>`）。違いがあれば止めて報告する。記録は変えない。独立再レビューのあと、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。

## 前回のSummary（Step 80）

- Builds: Build and TestのCIで、Steps77〜79の修正が足りなかったと分かった。advisory policy付きのゲストビルドは `ci_head`（`GITHUB_SHA`）を記録し、U10の差分jobがそれを照合するが、`u10-native-diagnostic.yml` の差分の手順は `sudo unshare --net env ...` で `GITHUB_SHA` を渡していないため照合が失敗する。U14の同じ手順（`u14-native-diagnostic.yml` 83行目）と同じく `GITHUB_SHA="$GITHUB_SHA"` を渡す。
- Touches: `.github/workflows/u10-native-diagnostic.yml` の differential job の1行だけ。製品source、試験、スクリプト、他Unitの記録、source-manifest.json（記載済み）は変えない。直した後の署名付きpushとCIの再実行は、人がPRのAuto-fixで許可済み。
- Tests: 新規テストなし。actionlint（shellcheck 0.11.0を明示）で検査し、CIの再実行で確かめる。正式sensor、独立再レビュー、正式コマンドでのcheckpoint再検証を行う。

## 今回の差し戻し対応：Step 80（差分jobへのheadの受け渡し）

Build and Testで、承認を得てfork `codex/build-and-test` にpushしたCIで、`U10 fixed guests and fresh native differential / differential` が失敗した（PRゲート run 39009487698 の job 117332287585、u12-quality run 39009464565 の job 117331520277）。原因は `tests/guests/u10/evidence.py` 169〜171行目の `overlay artifact CI head binding mismatch`：`tests/guests/u10/build.py` 82行目は advisory policy 付きのとき `receipt['ci_head'] = os.environ.get('GITHUB_SHA')` を記録し、差分側は `os.environ.get('GITHUB_SHA')` と照合するが、差分の手順は `sudo unshare --net env PATH=... RUSTC=... CARGO_HOME=... cargo test ...` で、sudo が `GITHUB_SHA` を引き継がない。Steps77〜79で policy を付けたことで初めてこの照合が働くようになったため、U9の修正の続きとして直す。

- [ ] Step 80 — workflowの修正と確認（FR6.3、FR7.2、FR7.3、FR9.1）。`.github/workflows/u10-native-diagnostic.yml` の differential job の「Fresh native oracle then bounded C10 differential without network」の行 `sudo unshare --net env PATH="$u10_bin:$PATH" ...` を、`u14-native-diagnostic.yml` 83行目と同じ `sudo unshare --net env GITHUB_SHA="$GITHUB_SHA" PATH="$u10_bin:$PATH" ...` にする。他の行は変えない。actionlintで検査し、code-summary.mdの「現行Steps77〜78」節に、失敗したrun・job、原因、変えた行、CIでの再実行はまだで未確認であることを足す。traceability.jsonは分類・targetを変えず、FR9.1のnotesに参照を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 前回のSummary（Steps77〜79）

- Builds: Build and Testからの差し戻し（人の指示）。U9が持つ共有workflowのゲストビルドを `--advisory-policy u15-fixed-aube-zip9-name` 付きに揃え（u11-acceptance.yml・u10-native-diagnostic.yml）、ci.ymlに `PALUDARIUM_TEST_NODE: node` を足してJITの実Wasm試験とdiff_u14が通常CIで動くようにする。
- Step 79（追加）：2つのworkflowのゲストビルドの前に、u14-native-first.ymlと同じSHA固定の `actions/setup-python`（Python 3.15.0）を足す。

## 今回の追加対応：Step 79（Pythonの準備とactionlintの扱い）

Steps77〜78の実行で2つの問題が分かった。(1) 新しいゲストビルドの行は `python` を使うが、u11-acceptance.yml と u10-native-diagnostic.yml には `actions/setup-python` がない。参照元の u14-native-first.yml（25〜27行目）と ce0b746 の u12-native-first.yml は、先に Python 3.15.0 を入れている。(2) 承認済みのactionlintコマンドは、この Mac の mise の `shellcheck` shim に版がないため exit 3 で止まった。shellcheck 0.11.0 を明示すると、変更した2ファイルの指摘は0件、ci.yml は今回触れない87・203・226行目の4件（SC2086、SC1090）で exit 1 になる。人は「setup-python を足す」を選んだ。

- [ ] Step 79 — (1) `.github/workflows/u11-acceptance.yml` の `build-oracle` job と `.github/workflows/u10-native-diagnostic.yml` の `native-first` job で、`actions/checkout` の直後に、`u14-native-first.yml` 25〜27行目と同じ `uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` と `with: python-version: '3.15.0'` を足す。他の行は変えない。(2) instructionsのactionlintコマンドに `-shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck` を足し、期待結果を「変更した2ファイルの指摘0件。ci.ymlは今回触れない87・203・226行目の既存4件（SC2086×2、SC1090×2）だけで、新しい指摘はない」とする。既存4件は直さず、code-summaryに既存の指摘として記録する。(3) actionlintとJIT単体試験を再実行し、code-summaryの「現行Steps77〜78」節に、Step 79の変更と結果、Steps77〜78で出たexit 3／exit 1の記録（消さずに残す）を足す。CIでの実行は、引き続きBuild and Testで人の承認を得てから行う（FR9.1、FR9.2、NFR3）。

## 今回の差し戻し対応：Steps77〜78（workflowの修正）

Build and Testの準備中に、人が次を指示した：「fork の branch codex/u15-macos-native（commit ce0b746）で、u12-native-first.yml のゲストビルドを --advisory-policy u15-fixed-aube-zip9-name に揃えました。同じ問題は u11-acceptance.yml・u10-native-diagnostic.yml（policy の指定なし）と u12-quality.yml（PALUDARIUM_TEST_NODE なし）にもあります。…手元への反映は、影響する Unit（U9〜U12）の再レビューを含めて正規の手順で進め、push と CI の前には承認を求めてください。」根拠はU15の `verification/u12-quality-38994430947/README.md`（run 38994430947：ゲストビルドで aube の `cargo deny` が exit 1、`PALUDARIUM_TEST_NODE` 不在でJITの実Wasm試験9件とdiff_u14がpanic）と `verification/u12-workflow-fix-proposal.md`。U9のsource-manifestはu11-acceptance.yml・u10-native-diagnostic.yml・ci.ymlを含むため、この3ファイルをU9で直す。u12-native-first.yml・u12-quality.ymlはU12で直す。U10・U11は同じ共有ファイルの再レビューを行う。

- [ ] Step 77 — workflowの修正（FR9.1、FR9.2、NFR1、NFR3）。(1) `.github/workflows/u11-acceptance.yml` 24行目と `.github/workflows/u10-native-diagnostic.yml` 41行目の `bash scripts/u10-build-guests.sh target/guests/u10` を、be45b36cで成功している `u14-native-first.yml` 53行目と同じ `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` に置き換える（ce0b746の `u12-native-first.yml` と同じ形）。(2) `.github/workflows/ci.yml` のworkflowの `env` に、`u14-quality.yml` 21行目と同じ `PALUDARIUM_TEST_NODE: node` を1行足す。これは人の指示の4ファイルに含まれないが、同じ原因で通常CIの3OS単体試験とcoverageが失敗するため、計画で明示して承認を求める。閾値・mask・対象・他の行は変えない。actionのSHA固定と権限は変えない。
- [ ] Step 78 — 確認と記録。`actionlint` で3ファイルを検査し、この Mac で `PALUDARIUM_TEST_NODE` を設定してJIT単体試験（57件）を実行する。code-summary.mdの冒頭に「現行Steps77〜78」節を加え、変更した3行と根拠、確認の結果、CIでの実行はBuild and Testで人の承認後に行うこと（まだ未確認であること）を書く。traceability.jsonは分類・targetを変えず、FR9.1のnotesに今回の修正の参照を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 今回の指摘対応：Step76（R-06・R-07・R-08）

ユーザーはU9 checkpointでRequest Changesを選び、R-06・R-07・R-08への対応を指定した。根拠はすでに保存済みである。jobログ `job-116962253357.log` の364行目に `Restored from cache key "v0-rust-coverage-Linux-x64-e120b189-6c223cb7" full match: true.` があり、334〜335行目の「Rust Versions」は2行（1.101.0-nightly、1.99.0）である。Step74 JSONは、headの `rust-toolchain.toml` のchannelを `nightly-2026-10-11` と記録している。

- [ ] Step 76 — 記録の文言修正（R-06・R-07・R-08）。(1) traceability.jsonのNFR9：id・status・targetを保持する。notesの `nightly-2026-10-10` に触れる文を「Step20時点の観測（履歴）」と分かる表現にし、「現行head be45b36cのchannelは `nightly-2026-10-11`（`verification/step74-u9-coverage-binding.json`）」という1文を足す。(2) traceability.jsonのNFR3：id・status・targetを保持し、Step74の文に「rust-cacheが認識した版（1.101.0-nightlyと1.99.0の2行）で、どちらでビルドしたかは未確定」という注意書きを足す。(3) code-summary.mdの「現行Steps74〜75」節(a)：jobログ364行目のとおり `target/` がrust-cacheから復元された（full match）ことと、headのbytesとの結合はcheckoutした入力に対するもので、全オブジェクトが再ビルドされた証明ではないことを、1〜2文で足す。この節の他の文と他の節は変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR3、NFR9）。

## 今回の指摘対応：Steps74〜75（R-02・R-04・R-05）

ユーザーはU9 checkpointでRequest Changesを選び、R-04・R-05・R-02への対応を指定した。保存済みjobログ `job-116962253357.log`（U15 verification `full-quality-1792153236541522000/`）の rust-cache 設定の「Rust Versions」には `1.101.0-nightly x86_64-unknown-linux-gnu 6f5da406b56c2db6607202b63daee73aa8c61297` が記録されている。また、「Lockfiles considered」には `Cargo.lock` と `rust-toolchain.toml` が記録されている（SHAの記録はない）。署名済みhead be45b36cはローカルのjj履歴にあるので、新しいCI実行や外部送信をせずに、headのファイルbytesからlockとtoolchainのSHAを得られる。fork CIの新しい実行が必要になった場合は、送信前に別途承認を求める。

- [ ] Step 74 — 結合結果の作成（R-02・R-05）。U9 verification配下に新規 `step74_u9_coverage_binding.py` を作る（Python 3.15標準ライブラリだけを使い、引数は取らない）。このスクリプトは次を行う。(1) `step72-u9-coverage-recount.json` を読み取り専用で読み、head・run・jobと3集合の値を引き継ぐ。値は再計算せず参照するだけにする。(2) `full-quality-1792153236541522000/` の run.json に記録されたhead SHAがbe45b36cと一致することを確かめる。(3) job-116962253357.logから「Rust Versions」の各行と「Lockfiles considered」の各行を取り出す。(4) `jj --ignore-working-copy file show -r be45b36ce9d7a65719ba1f86cf6a0b018070741b <path>` で、headの `Cargo.lock`・`fuzz/Cargo.lock`・`rust-toolchain.toml` のbytesを得てSHA-256を計算し、現在の作業コピーの同じファイルのSHA-256と比べる。`rust-toolchain.toml` からchannelを取り出す。(5) 結果を新規 `step74-u9-coverage-binding.json` に排他作成で保存する。保存する内容は次のとおり。lock・toolchainはパスごとのSHAで、欄名は `lock_sha256_by_path` とする。compilerにはjobログの記録行とその出典を書く。Step72 JSONの `lock_sha256` 欄が誤り（未照合の文であり、「wasm lock」は `fuzz/Cargo.lock` の誤称）であるという訂正注記を入れる。DA行数とTOTAL行数の差（74行）については `cause: unconfirmed` と書く。照合できない項目は未照合と明記し、成功とは扱わない。いずれかの照合が不一致なら終了コード1にする。Step72のスクリプト・結果JSON、製品、既存試験、旧原本、CI設定は変更しない（NFR3、FR9.1）。
- [ ] Step 75 — 記録の更新（R-02・R-04・R-05）とレビューの準備。code-summary.mdの「現行Steps72〜73」節の直前に「現行Steps74〜75」節を加え、次を記録する。(a) compiler（jobログの記録行。jobログで分かるのは、rust-cacheが認識したtoolchainの版だけであることも書く）、headの両lockとtoolchainのSHA、作業コピーとの一致・不一致、各値の出典。(b) R-04：DA行数5633とTOTAL行数5707の差（74行）は原因が未確認であること。あわせて、Steps72〜73節の「llvm-covの表の行数とlcovのDA行数は数え方が異なるため一致しない」という文を「差（74行）の原因は未確認」と言い換える。(c) R-05：Step72 JSONの `lock_sha256` 欄の誤りと、その訂正先（Step74 JSON）。Steps72〜73節は、この文と、compiler・lockを未照合とした文に「Steps74〜75で結合」という参照を足す以外は書き換えない。traceability.jsonのNFR3は分類とtargetを変えず、notesにStep74の結合結果の参照を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む。全経路差分、Node／Safari、ASanの新しい実行、U15の受理は主張しない（NFR3、全割当FR/NFR）。

## 今回の指摘対応：Steps72〜73（R-02・R-03）

ユーザーはU9 checkpointの再確認でRequest Changesを選び、R-02とR-03への対応を指定した（fork CIの実行・外部送信は送信前に別途承認を求める）。署名済み現行head be45b36ce9d7a65719ba1f86cf6a0b018070741bの公式品質CI run 38897611874（job 116962253357）は、unit-test-instructionsの既存U9 coverageコマンドを同じpackages・除外regex・`--fail-under-lines 80`で実行して成功し（TOTAL lines 5707/767 missed）、`u9-coverage-lcov` artifactを公開している。この公式原本（U15 verification `full-quality-1792153236541522000/` に保存済み）を使うため、新しいCI実行・push・外部送信は不要である。

- [ ] Step 72 — 公式原本の再集計（R-02）。U9 verification配下に新規 `step72_u9_coverage_recount.py` を作り、`full-quality-1792153236541522000/` の artifacts.json／inventory.json から `u9-coverage-lcov` のartifact ID・digestを取得し、保存ZIPのSHA-256がdigestと一致し、ZIPから取り出したlcovのSHAを記録する。lcovのSF/DA行から、`verification/step20-fixed-proof.json` の `coverage.original13.paths`（13件）と `coverage.additional10.paths`（10件）の各集合と全23件の行数・カバー行数・割合を計算し、各集合の欠落ファイル・重複を拒否する。80%下限未満は失敗として記録し隠さない。head・run・job・compiler（同jobログの実rustc）・両lockのSHA（job ログまたはinputs原本に記録があれば照合、なければ未照合と明記）を結果 `verification/step72-u9-coverage-recount.json` に保存する。旧541b値（2693/3202、2156/2397）は履歴として並記し置き換えない。製品・既存試験・旧原本・CI設定は変更しない（NFR3、FR9.1）。
- [ ] Step 73 — 記録更新（R-02・R-03）とレビュー準備。code-summary.mdの冒頭に「現行Steps72〜73」節を追加し、(a) Step 72の再集計結果（be45b36c／run 38897611874／job 116962253357、旧13・追加10・全23の分子分母と割合、80%判定、原本SHA）を記録し、旧541b値は保存観測の履歴として保持する。(b) `.gitignore` はU9 source-manifest外の非ビルド共有パスであり、2026-10-16のClaude Code harness追加でAI-DLCブロックへ `aidlc/active-memory/`・`aidlc/.aidlc-request-text/` の2行が入ったことで再確認が起きたこと、製品・テスト・端末契約に影響しないことを明記する（R-03）。traceability.jsonのNFR3は既存の分類・targetを保持し、notesへ現行再集計の結果参照を追記する。正式sensor実行後に全書込を止め、独立再レビュー・採用済み正式コマンドでのcheckpoint再検証・人の完了承認へ進む。全経路差分・Node／Safari・ASanの新実行やU15受理は主張しない（NFR3、全割当FR/NFR）。

## 今回の記録更新：Steps22〜24

- [ ] Step 22 — 公式renderのTesting Contractを全体置換し、U9の現行manifest・担当ソース・依存・両lock・compiler・設定を保存証拠へ照合する。旧原本と現行参照を区別し、不一致を分類する。製品・既存試験は変更しない（FR4.1/4.2、NFR1/2/3/9）。
- [ ] Step 23 — 有限な一致範囲と未検証を記録し、正式traceability／required-sectionsを実行する。旧Linux差分・coverage・Node／本物Safari・ASan証拠は条件一致範囲のみ再利用し、新規実行と区別する。不足は具体的に提示し、閾値・mask・分母を変更しない（全割当FR/NFR）。
- [ ] Step 24 — 全書込みを止めて独立再レビューを受け、承認済み `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py` の正式最終確認と人の完了承認へ進む。U11への遷移を正式手順で進め、ID競合の完全解消やU11同時disposeの修正完了は主張しない（NFR2/3/8/9）。

## 履歴：Steps13〜15

## 承認された追加検証：Steps16〜18

## 今回の限定修正：Steps19〜21

- [ ] Step 19 — 最新Clippyで失敗したdiff_u7.rsの8byte分割をas_chunks::<8>().0.iter()とfrom_le_bytes(*bytes)へ限定変更する。実装意味論・比較case・maskを保持する。公式最新版を確認し、rust-toolchain.tomlと実行対象script/CIのRust明示指定を同じ最新確認版に揃える。全設定を棚卸しし、履歴文書の旧版は書き換えない。新規依存・無関係な製品改善を加えない（NFR3/9）。
- [ ] Step 20 — 最終ソース・両lock・設定を固定し、署名済みfork CIでfmt/Clippy、依存4検査、関連diff_u7/diff_u9、U9 coverage80%（旧13ファイル集合と追加集合を別記）、production wasmのNode/本物Safari全現行caseを再確認する。Safariを含むsource before/after/current監査とmodule/native SHA、全raw/実exitを保存する。30秒・比較mask・測定対象・閾値を維持する。ASan証拠はtargetごとの依存sourceと実使用compiler/flagsが一致する場合だけ再利用し、時点・設定変更を明記する。不一致対象は必要な再検証を提示し、例外で隠さない（NFR1/2/3/7/8/9）。
- [ ] Step 21 — 変更pathをmanifestへ列挙し、旧失敗と最新検証を区別して4成果物・対応表を更新する。正式検査・独立レビューへ渡す前に全書込を止める。最終ソース用canonicalを具体化し、変更コマンドは人の新承認前に実行しない。strict guardと品質下限を維持する（全割当FR/NFR）。

## 前回の追加検証：Steps16〜18

- [ ] Step 16 — 製品を変更せず、全現行入力・両lock・設定を固定した署名済みfork診断CIでfresh native Linux diff_u9と既存U9 scope coverage80%以上を実行する。公式最新版ツールを診断環境へ固定し、測定分母・除外・比較mask・30秒watchdogを維持する。raw exit・source before/after/current・署名Verifiedを保存する。PR/mergeは行わない（FR9.1、NFR1/3/8/9）。
- [ ] Step 17 — 同一ソースのproduction wasmをビルドし、同CI生成native期待値と現行全ケースをNodeおよび本物Safariで確認する。同じmodule SHA、COOP/COEP、既存operation/whole-process期限、cleanupと全rawを保存する。load_elfだけを600秒以上ASan/LSanで実行し、seed1・timeout30・rss2048・既定max_len・detect_leaks1・既存suppression・最小C診断を維持する。U7の3対象は実入力一致で限定再利用し、他Unitへ検証範囲を広げない（FR9.3、NFR2/3/7/9）。
- [ ] Step 18 — 取得した実測を現行ソースと照合して不足6項目を更新し、失敗・不足を合格へ読み替えない。成果物・manifest・正式検査を確定して独立レビューを受ける。U9の実測を含む最終確認コマンドを具体化し、人の新しいコマンド承認前には実行しない。strict guard、80%下限、30秒制限を維持する（全割当FR/NFR）。

## 前回の照合手順：Steps13〜15

- [ ] Step 13 — U9の担当ソース、共有契約、保存CI・coverage・wasm/Safari・ASan証拠を読み、現行ソース・両lock・設定と対象ごとの依存範囲を照合する。旧成功を現行実行として扱わない。保存証拠は一致範囲だけ再利用し、不足は具体的な対象・コマンドとして示す。既存端末実装を再実装しない（FR4.1/4.2、NFR1/3/9）。
- [ ] Step 14 — unit-test-instructionsのU9限定内部・公開API・compile_fail・CLIを現行ソースで確認し、実コマンド・件数・exitを保存する。Linux差分、U9 coverage80%、wasm/Safari、ASan証拠の不足は未検証として明示し、具体的な最小追加検証案を人へ提示する。最新ツールを確認し、30秒watchdog・比較mask・測定分母を維持する。製品変更が必要なら原因と限定差分を先に提示する（FR9.1/9.3、NFR1/2/3/7/9）。
- [ ] Step 15 — 現行と履歴を区別して4成果物・manifest・証拠を確定し、正式検査と独立レビューを行う。承認済み最終確認を実行し、人の完了承認後に続ける。確認コマンド変更が必要なら具体化後に新しい承認を取得する。ID競合の完全解消は実測範囲を超えて主張しない（全割当FR/NFR）。

## 根拠と範囲

根拠：inception/units-generation/unit-of-work.md のU9、unit-of-work-story-map.md のFR4・FR4.1・FR4.2、requirements-analysis/requirements.md、contract-design/contract-summary.md のC2・C8・C10・C11。
U9固有の設計成果物は存在しない。既存Host・Kernel・Runtimeの境界を維持して必要な設計を各手順に記録する。ストーリー工程は省略されているため直接FRに対応する。
検証済み（ソース読取）：RuntimeのConfig.ttyは定義されているがSession.runからKernelへの受け渡しがない。Hostの標準入出力とLoaderへのargv/envpは既存。
Steps1〜7は保存済み実装の履歴であり、今回再実行しない。今回の対象はR-01の公開型と共有契約の不一致修正、変更後ソースの検証更新。U1・U2・U4・U7の成果物を維持し、共有ソース変更後の必要な完了確認を更新する。probe全項目・aube・JIT・任意ゲストの保証へ範囲を広げない。

## 実装手順

- [ ] Step 1 — 既存Host・Kernelのfd表・Runtime・Loader・CLIの接続を読み、端末情報の型と既定値、Config.ttyの優先順位、非端末の扱いを文書化する。C2/C8/C10を壊さない追加とする。（FR4.1・FR4.2）
- [ ] Step 2 — 既存Cargoテスト環境を確認し、U9専用フィルタと差分テスト入口を整える。tests/guests/u9/build.sh と crates/paludarium-harness/tests/diff_u9.rs を用意し、実装前にコマンドがケースを検出することを確認する。（FR9.1・NFR9）
- [ ] Step 3 — tests/guests/u9/ に引数・空文字・環境変数・stdin EOF/短い読み取り・stdout/stderr分離・TCGETS・TIOCGWINSZ・非端末・不正fd・不正ポインタ・未知requestのケースを先に作る。Linux x86-64で毎CI実行時に期待結果を生成する。ttyケースは管理されたPTYの設定とnative/guestの条件を一致させ、端末入力待ちを30秒watchdogで制限する。取得できない条件は未検証として残し、保存期待値で代えない。（FR4.1・FR4.2・FR9.1・NFR1・NFR7）
- [ ] Step 4 — Hostにstream単位の端末情報取得を追加し、TestingHostの制御可能な設定と非端末既定値を実装する。Linux端末照会をHost内に閉じ込める。macOS/Windowsはコンパイルとfake Hostを確認し実機端末動作を推定しない。Host内部の単体テストを実装後に5〜8件追加する。（FR4.2・NFR3・NFR4）
- [ ] Step 5 — KernelでLinux x86-64のTCGETSとTIOCGWINSZのゲストABIを明示的にシリアライズする。fd/端末種別/ゲストメモリを検査しEBADF・ENOTTY・EFAULTを差分ケースに従って返す。未知requestを番号のままホストへ渡さない。複製された標準fdと通常ファイルを区別する。内部テスト5〜8件を実装後に追加する。（FR4.2・NFR1〜NFR4）
- [ ] Step 6 — Config.ttyをKernelまで渡し、argv/envp・stdin・stdout/stderrの既存経路を統合テストで確認する。RuntimeのU9内部テスト5〜8件とCLI境界のU9統合テストを追加する。差分ケースを実行してnative一致を確認し、既存CIの3OS・lint・依存チェックにU9を接続する。（FR4.1・FR4.2・NFR8・NFR9）
- [ ] Step 7 — U9対象のLinux行カバレッジ80%以上、差分結果、各OS内部テスト、署名済みCIと現行ソースの一致を記録する。取得不能なcoverage/fuzz/端末実機はGAPとする。code-summary・traceability・厳密source-manifestとH2 sensorを検証し独立レビューへ渡す。承認済みUnitの検証結果をU9の結果として流用しない。（FR4・FR9.1・NFR1〜NFR9）

## 変更対象と品質

## 今回の修正手順

- [ ] Step 8 — 型・Default・全literal利用側を確認し、既存Cargo設定とU9専用runnerを--listで確認する。新しい外部crate回帰入口を用意し、0件を成功にしない。（R-01、C2/C8/C10、FR4.2、NFR9）
- [ ] Step 9 — HostのTerminalAttributesとTerminalInfoに#[non_exhaustive]と全既存フィールドを指定できるconstructorを追加する。外部crateのliteralを更新し、Defaultと端末/ioctlの意味論を維持する。Runtimeの同名公開型も確認し、今回変更する型は契約を満たす。（R-01、FR4.2、NFR1・NFR4）
- [ ] Step 10 — 実装後、crates/paludarium-host/tests/u9_public_api.rsに外部crateのconstructor・Default・フィールド保持・非端末・境界値の5〜8件を追加する。compile_fail doctestで外部literal構築禁止を確認する。既存Host/Kernel/Runtime/CLIのU9テスト、Linux diff_u9（実行時native期待値）を実行する。（FR4.1・FR4.2・FR9.1、NFR1〜NFR4）
- [ ] Step 11 — 変更ソースを署名付きでfork CIへ反映し、3OSテスト・fmt・clippy・依存検査・Linux差分・U9対象coverage80%以上を確認する。変更後production wasmをビルドしNodeと実Safariの既存14ケースを実行する。保存済みASan/fuzz/Windows race証拠は依存byte一致を照合し、不一致対象は必要な検証を再実行する。閾値・時間制限を下げない。（FR5.3・FR9.1・FR9.3、NFR1〜NFR4・NFR7〜NFR9）
- [ ] Step 12 — 全変更をmanifestへ列挙し、旧履歴と今回のraw証拠を区別してsummary・traceabilityを更新する。変更後checkerを具体化し、canonical commandの変更は人の承認を取得する。成果物とソースを固定してsensor・独立レビュー・完了確認へ渡す。（R-01、FR4、NFR1〜NFR9）

追加対象は外部crate回帰テスト、compile_fail APIドキュメント、literal利用側、必要な検証スクリプトとCI証拠。既存Steps1〜7の作り直しは行わない。

想定対象：crates/paludarium-host/src/{lib.rs,testing.rs,u9_tests.rs}、crates/paludarium-kernel/src/{lib.rs,files.rs,syscalls.rs,u9_tests.rs}、crates/paludarium-runtime/src/{lib.rs,u9_tests.rs}、crates/paludarium/tests/command.rs、crates/paludarium-harness/tests/{diff_u9.rs,support/u9.rs}、tests/guests/u9/、必要な既存CI設定。
新規依存は既存の道具で不足した場合だけライセンス・crates.io取得元を確認して導入する。unsafeはHost以外禁止。clippy警告0、既存テスト維持、行カバレッジ80%、watchdog30秒、nightly固定を弱めない。
NFR2/3のfuzz安全性は実行証拠を取得するまでGAP。未検証を合格に置き換えない。

## Testing Contract

```json
{
  "version": 1,
  "methodology": "custom",
  "source": "team",
  "ordering": "命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
  "scope": "rust-blink-port",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "私たちはテストを各 Bolt の成果物の一部として扱います。エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まるので、差分テストを中心に置きます。\n\n- **Methodology**: custom\n- **Ordering**: 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。\n\n補足：\n\n- **カバレッジ**（Q5）：行カバレッジ 80% を下限にします。測るのはネイティブの Linux です。あわせて「範囲内の命令のうち、差分テストが 1 件以上ある命令の割合」を記録します。決めた下限は Build and Test で下げません。\n- **差分テストの期待結果**（Q6）：期待結果は、**CI を実行するたびに x86-64 Linux のランナーで作り**、エミュレータの結果と比べます。期待結果をリポジトリに保存する方式は取りません。\n  - 比べるもの：命令の単位ではレジスタ・フラグ・メモリ、プログラムの単位では標準出力・標準エラー・終了コード。\n  - x86 で結果が未定義のフラグや値は比べません。命令ごとに「比べないもの」を表で持ちます。\n  - pid・時刻・乱数・アドレスなど、実行ごとに変わる値は、比べる前にそろえるか、比べる対象から外します。\n  - 段階 5 では、JIT ありと JIT なし（インタプリタ）の結果も同じ差分テストで比べます。JIT だけの意味論は持ちません。\n- **単体テスト**：層ごとに `cargo test` で書きます。テストやビルドの道具は外部のものを使ってよいです（Q1）。\n- **CI のゲート**（Q7）：\n  - 変更のたび（PR）：Linux・macOS・Windows の単体テスト、lint（`cargo fmt --check`、clippy の警告はエラー）、依存の検査（ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること、既知の脆弱性）、x86-64 Linux での差分テスト。通らなければマージしません。\n  - 段階ごと：その段階に入ったら、その段階の probe と aube の合格を必須にします。\n  - 夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）。失敗したら Issue にして直します。\n- **Safari**（Q12）：Safari での合格は、macOS の CI で本物の Safari を動かして確かめます。WebKit を使う別のテスト用ブラウザでは代えません。\n- **wasm**：paludarium が用意する起動用 JS とテストハーネスで、Node.js の Worker とブラウザ（Chromium 系・Firefox・Safari）で同じテストを動かします。テスト用のページには COOP/COEP の見出しを付けます。\n- **揺れるテスト**：スレッドを使うテストには時間切れの上限を付けます。揺れたテストは記録して直します。\n- 段階 5 の「JIT なしより速い」は、回数・統計量・差の大きさを要件分析で数値にしてから測ります。速さの測定は PR のゲートにしません。\n- Test Strategy は Standard です。量と種類はこの設定に従い、上の補足はそれに足すだけです。"
    },
    {
      "layer": "project",
      "text": "- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) \n\n- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) \n\n- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) \n\n- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) \n\n- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) \n\n- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) \n\n- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) \n\n- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) \n\n- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) \n\n- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) \n\n- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) \n\n- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) \n\n- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) \n\n- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) \n\n- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) \n\n- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) \n\n- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) \n\n- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) \n\n- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) \n\n- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) \n\n- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) \n\n- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) \n\n- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) \n\n- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) \n\n- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) \n\n- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) \n\n- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) \n\n- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) \n\n- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) \n\n- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) \n\n- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) \n\n- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) \n\n- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) \n\n- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) \n\n- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) \n\n- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) \n\n- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) \n\n- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) \n\n- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11)"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "custom",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Custom ordering - 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
      "Implementation and tests - preserve that exact ordering; do not convert it to layer-local TDD.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cc8e6bbb985d32c580aff1d457ccafb5f05a4b442140eb6cb6303d51ca2ba418",
  "contract_sha256": "sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5"
}
```
