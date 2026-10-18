# U11 単体・差分テスト実行手順

## 今回Steps 29〜30：Safariの待ち時間の修正と新しい正式確認の入口

Step 29：この Mac で WebDriver の道具の試験を実行する（本物の Safari は使わない。endpoint は試験の中の仮の HTTP サーバー）。本物の Safari での確認は、人の承認を受けた push の後の CI（PR CI と u12-quality）で行う。u14-quality は正式な性能測定を含むので起動しない。

```sh
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs
```

期待する結果：`node --test` は失敗0件（既存8件と新しい回帰1件）。CIの `u11-programs / differential (macos-latest, safari)` が時間切れなく成功する。

Step 30：project rootで、新しい入口と拒否の回帰、sensorを実行する（入口のファイル名は作るときに決め、README.mdに書く）。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/test_u11_candidate.py
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md
```

期待する結果：新しい入口はexit 0。拒否の回帰（2ファイルの別のbytes、ほかのcompiled sourceの変更、別のhead、CIの欠落・失敗、U11記録の許可外の変更）はすべて拒否。sensor 2件はpass。新しい入口は、人が採用してからcheckpointで実行する。

## 前回Step 28：Step 27 の取り消し

Step 27 で変えた2ファイルを元のバイトに戻し、既存の試験が通ることを確かめる。

```sh
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md
```

期待する結果：2ファイルの SHA-256 が head e4f84768 の版と一致する。`node --test` は既存8件が成功し失敗0件。sensorは2件とも pass。

## 前回Step 27：Safariのsession作成の待ち時間（取り消し済み）

この Mac で WebDriver の道具の試験を実行する（本物の Safari は使わない。endpoint は試験の中の仮の HTTP サーバー）。本物の Safari での確認は Build and Test の CI 再実行で行う。

```sh
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md
```

期待する結果：`node --test` は失敗0件（既存の試験と新しい回帰1件）。sensorは2件とも pass。

## 今回Step26：共有workflowの再確認

新しいテストはない。U9が直したworkflowの書き方を actionlint で確かめる（shellcheck はインストール済みの 0.11.0 を明示する）。CIでの実行は、Build and Testで人の承認を得てから行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u11-acceptance.yml .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md
```

期待する結果：u11-acceptance.yml と u10-native-diagnostic.yml の指摘0件。ci.yml は今回触れない87・203・226行目の既存4件（SC2086×2、SC1090×2）だけで、新しい指摘はない（このため終了コードは1）。sensorは2件とも pass。

## 今回Steps23〜25：配布パッケージと再実行手順

修正前と修正後の両方で実際のnpm tarballを生成し、プロジェクト内の隔離ディレクトリへ展開する。公開しない。npm cacheはプロジェクト内の専用領域を使用し、別作業のcacheや設定を変更しない。実体Node/npm/Pythonはmiseの実pathから解決する。既存Rustの固定版はrust-toolchain.tomlを正本として読み、過去のnightly-2026-10-10を現在の固定版と扱わない。公式最新情報と実versionとの差は必要な更新・限定再利用・未実行のいずれかで明記する。

新しい配布回帰入口を packages/paludarium-wasm/tests/packed-distribution.test.mjs に用意する。実行入口は `$U11_NODE --test packages/paludarium-wasm/tests/packed-distribution.test.mjs`。実npmのパス・同梱module・固定hello guestの入力は検査前に解決しhashを記録する。回帰は正常配布、必須JS欠落、無効/破損入力を確認する。補助ハーネスの具体的argvは実装時にこの手順へ確定する。

必須条件：tarballの全相対import/export先が存在すること、配布packageからimportできること、配布物に含まれるproduction wasmでlauncher生成とhello実行が成功すること、stdout/exitと終了後のdispose/Worker cleanupを観測できること。起動JSは展開したpackageだけから読み、リポジトリのJSへの代替参照を禁止する。guest入力は固定済みバイナリを独立fixtureとして渡し、package内容と混同しない。各guest30秒・suiteの有限監督を維持する。既存u11-api-check.mjsのC12/dispose回帰も実行する。

今回の記録では、配布物検査・ローカルC12回帰・保存CI照合・新規ブラウザー受入・新規Linux coverage/ASanを別々に分類する。ブラウザー準備と不足するツールを確認し、実行しなかった項目は未検証と理由を記録する。保存14guest/coverage/sanitizer成功を今回の新規実行と数えない。既存80%下限と検証条件は維持する。

製品package.jsonの変更後は旧設定差分専用canonicalが現ソースをそのまま受け入れると仮定しない。変更した入力を厳密に結合した新入口の必要性を確認し、正式コマンドの変更は具体化・手動検証・人の変更承認後に行う。

## 保存手順Steps20〜22：同時dispose修正

公開APIの処理中Promiseを共有し、同時disposeの両呼び出し成功、成功後の冪等性、実行中拒否後の終了・再試行、大規模FS破棄を実moduleで検証する。Rust・固定guest・snapshot上限は保持する。既存u11-api-check.mjsへ境界回帰を追加し、既存のNode／Chromium／Firefox／本物Safari各14guestとC12を同一入力で再確認する。全製品JSの既存測定範囲で80%下限を維持する。実体ツール、全入力・両lock・module／guest hash、生ログ・実exit・30秒境界・cleanupを保存する。旧ASanはRust依存・binary・compiler・設定一致範囲だけ再利用し、失敗や未検証を隠さない。新確認コマンドは別承認後に正式実行する。以下の旧手順は各時点の履歴として保持する。

## Steps17–19 dispose限定修正（新しい承認後）

保存再現は verification/dispose-current-proposal.md。新しい承認前は製品を修正しない。準備済みrunnerを使い、修正後は以下を実行する。RUSTC/CARGO/U11_NODEは下記Current Setupの実体を使用する。

```sh
env RUSTC="$U11_RUSTC" "$U11_CARGO" test -p paludarium-wasm --lib u11_filesystem
env RUSTC="$U11_RUSTC" "$U11_CARGO" test -p paludarium-wasm --lib filesystem
env PATH=/Users/mutoakio/.cargo/bin:/usr/bin:/bin RUSTC="$U11_RUSTC" bash scripts/build-wasm.sh
"$U11_NODE" packages/paludarium-wasm/tests/u11-api-check.mjs packages/paludarium-wasm/paludarium.wasm
"$U11_NODE" aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/dispose-current-repro.mjs packages/paludarium-wasm/paludarium.wasm
```

実Wasmコマンドは既存Python3.15 supervisorで外部60秒以下、診断内部30秒を維持し、exit/timeout/process_group_cleanedを記録する。修正後の限定再現はcreate成功、snapshotは既存64MiB上限による拒否を維持、dispose成功が期待結果。Rust内部はidle/large idle/active拒否と解放/closed acquire/snapshot/remove/二重closeなど7件以上、JSは既存C12 active/stale/他launcher/idempotenceと大規模disposeを保持する。その後Steps15–16のfresh4環境14件、3OS、定義coverage80%、厳密ASan依存比較、freshpackを実施する。

## Historical Steps14–16 Setup（当時のツール指定）

以下は新計画承認・内容確認後の実行手順。旧手順と旧成功は末尾へ履歴として保持し、現行のpassへ読み替えない。製品ソースは保持し、disposeの最小修正は限定再現の結果を親へ報告した後に別途扱う。

公式checkpoint：[Playwright registry](https://registry.npmjs.org/playwright/latest)は1.64.0、[公式browser manifest](https://github.com/microsoft/playwright/blob/v1.64.0/packages/playwright-core/browsers.json)はChromium156.0.8078.4/rev1248・Firefox157.0/rev1555。[Node Current](https://nodejs.org/en/download/current)は26.11.1、[Python Downloads](https://www.python.org/downloads/)は3.15.0（2026-10-09）、[Rust nightly manifest](https://static.rust-lang.org/dist/channel-rust-nightly.toml)は2026-10-10/32dba69d6。実SafariはOS付属の版とWebDriver capabilityを記録する。cargo-deny/fuzz/llvm-cov/Node付属npmなど実際に使う道具も公式最新情報と実versionを照合し、差があれば限定更新の影響を親へ報告する。固定guestのsource/tag/lockと専用CDLA全文・製品denyは変更しない。

手元のNode/Python/npmはインストール後のmise実体をglobで解決し、version一致を確認して `U11_NODE` / `U11_PYTHON` / `U11_NPM` に保存する。Macの根は `/Users/mutoakio/.local/share/mise/installs/`。shim/mise execや付属python3.9を使わない。CIはsetup-node26.11.1/setup-python3.15.0の実pathを保存する。Rustは `/Users/mutoakio/.rustup/toolchains/nightly-2026-10-10-aarch64-apple-darwin/bin/cargo` と同dirのrustcを明示する（CIは同固定nightlyの実体）。この文書の変数は検証済み絶対pathを表す。

同期対象はspikes/wasm-threads/package.json・package-lock.json、必要U11 workflow/configのみ。Playwright1.64.0 lock確定後に `$U11_NPM ci --prefix spikes/wasm-threads`、`$U11_NODE spikes/wasm-threads/node_modules/playwright/cli.js install chromium firefox` を行い、install/runで同じPLAYWRIGHT_BROWSERS_PATHを使う。Linux CIは `install --with-deps chromium firefox`。Safariは本物のsafaridriver（CIのみ既存enable手順）、prefs/profilerは使わない。

## Historical U11-scoped commands（当時のツール・検証範囲）

準備/内部試験（最新同期後に実行し、old Python3.9/installedPlaywright1.62での観測は履歴に残す）：

```sh
$U11_PYTHON scripts/u11-run.py --self-test
$U11_PYTHON -m unittest discover -s tests/guests/u11/runner-tests -p 'test_*.py'
$U11_NODE --test packages/paludarium-wasm/tests/u11-contract.test.mjs packages/paludarium-wasm/tests/u11-browser-driver.test.mjs packages/paludarium-wasm/tests/u11-filesystem.test.mjs packages/paludarium-wasm/tests/u11-worker-support.test.mjs packages/paludarium-wasm/tests/u7-mtime-snapshot.test.mjs
$U11_CARGO test --locked -p paludarium-kernel --test u11_fuzz_wait
$U11_CARGO test --locked -p paludarium-host --lib wasm_tasks
$U11_CARGO test --locked -p paludarium-wasm --lib
$U11_CARGO test --locked -p paludarium-vfs --lib u11_tests
$U11_CARGO test --locked -p paludarium-kernel --lib u11_tests
$U11_NODE packages/paludarium-wasm/tests/u11-browser-ready.mjs chromium firefox
$U11_NODE packages/paludarium-wasm/tests/u11-browser-ready.mjs safari
```

14ケース×4環境のコマンドは下記旧手順と同じfile/argvを最新実体へ置換して用いる。Linux nativeはnetwork namespace隔離、moduleはscripts/build-wasm.shの同じproduction設定。生成guest/oracle/module/source/compilerのhashを照合してから実行する。各guest30秒、共通suite600秒とprocess-group kill/reapを守り、tests/guests/u11/supervisor.pyの `supervise(...,seconds=600)` をCIの共通入口にする。独立した準備/driver/init時間とguest時間は混同しない。

idle largeFS限定診断は専用record-only helperで二つの34MiBファイルをcreate、snapshotとdisposeを別々に観測し、外部600秒以下監督・cleanupを付ける。期待はidle dispose成功で、snapshotサイズ制限をdisposeの失敗理由へ転用しない。再現がない段階で製品修正を実施しない。再現したら対象ABI/PrivateFs/coordinatorと所有/active/stale/idempotent回帰を具体化して親へ返す。

## Current quality populations and evidence

U11 Rust行coverageの定義はhost/vfs/kernel/runtime/wasm全lib（実行されたnative cfg）のLCOV、80%以上。CI専用コマンドは `cargo llvm-cov --locked -p paludarium-host -p paludarium-vfs -p paludarium-kernel -p paludarium-runtime -p paludarium-wasm --lib --ignore-filename-regex 'paludarium-(cpu|decoder|mmu|loader|types|jit)/' --fail-under-lines 80 --lcov --output-path target/u11-coverage.lcov`。workspace/U1/U3/U9等の既存下限と3OS/整形/clippy/依存4監査/Linux差分は全体CIで1回実施し、このUnit手順のrunへ裸のworkspace commandを追加しない。共有変更の影響はU5/U6/U8 unitとdiffの実test名・rawlogで確認する。

JS製品母集団はpackages/paludarium-wasmのindex.mjs、coordinator.mjs、execution.mjs、worker-support.mjs、filesystem-snapshot.mjsの全実行可能行（test/生成wasm/READMEは対象外）。既存unit/APIと実Node guestでこの全母集団を測り、独立Workerもinstrument対象へ入れる。JS coverage用専用設定/集約器を用意し、欠測ファイルを分母から除かず、合計80%以上と各ファイルの分母/分子を保存する。正確な集約コマンドはStep14で用意した専用fileを用い、未成立をpassとしない。Pythonは最新3.15.0でU11 runner-tests全件（現24件）を実行し、source/hashと数を保存する。

ASan/LSanの元7対象はvfs_paths/load_elf/syscall_args/kernel_threads_u5/kernel_futex_u5/kernel_events_u6/kernel_sockets_u6。現在の依存・Cargo/fuzz両lock・rustc commit/LLVM・cargo-fuzz・flags・seed1・timeout30・rss2048・max_total_time600・defaultmaxlen・suppressionを保存rawへ照合し、instrumented binaryのSHA同一性を必要ならbuild-onlyで検証する。一致対象は有限保存実行の再結合として記録（freshとしない）。不一致対象だけ同じ設定で新600秒実行し、LSan終了とexit0を要求する。新規除外/suppression/品質下限の変更はしない。

現326baseline＋実変更をbefore/after/signed headへ照合し、全FR/NFR対応、raw4環境/coverage/sanitizer/pack/timingsへ結び付ける。packはfresh CI moduleだけをprepare-pack.pyで反映してdry-runし、公開しない。速度測定は既知バックグラウンド負荷停止後に逐次実行し、完全な無負荷が未確認なら明記する。現正式commandは親の人による変更承認まで変更・実行しない。

## Historical Setup（Steps1–13）

Rustはrust-toolchain.tomlの固定nightly、wasmは共有std/atomics/TLSを含むscripts/build-wasm.shのproduction moduleを使う。Nodeとブラウザのrunnerは既存の手段を拡張する。Linux native生成はU10固定static-musl guestとfixtureを再利用する。macOSのSafariは本物のWebDriverを使う。新規依存は既存設定/ライセンスを調べてから限定追加する。

## U11-scoped Commands

Step2で最小runnerを用意し、以下の準備検査が成功するまで最初の実guest差分段階へ入らない。

```sh
python3 scripts/u11-run.py --self-test
node --test packages/paludarium-wasm/tests/u11-*.test.mjs
python3 -m unittest discover -s tests/guests/u11/runner-tests -p 'test_*.py'
cargo test --locked -p paludarium-kernel --test u11_fuzz_wait
cargo test --locked -p paludarium-mmu --lib
```

native-only、self-test、Nodeと実ブラウザの受入runnerを実装済み。固定guest/native/moduleビルドを先に終え、guest実行の30秒期限とbuild期限を分ける。以下のNode/browserコマンドはCIでは外部600秒process-group監督から実行する。

```sh
python3 scripts/u11-run.py --native-only --guest-dir target/guests/u10 --output target/u11/native
node packages/paludarium-wasm/tests/u11-node-check.mjs packages/paludarium-wasm/paludarium.wasm target/u11/native/observations.json target/guests/u10 target/u11/node
node packages/paludarium-wasm/tests/u11-browser-check.mjs chromium packages/paludarium-wasm/paludarium.wasm target/u11/native/observations.json target/guests/u10 target/u11/chromium
node packages/paludarium-wasm/tests/u11-browser-check.mjs firefox packages/paludarium-wasm/paludarium.wasm target/u11/native/observations.json target/guests/u10 target/u11/firefox
node packages/paludarium-wasm/tests/u11-browser-check.mjs safari packages/paludarium-wasm/paludarium.wasm target/u11/native/observations.json target/guests/u10 target/u11/safari
node packages/paludarium-wasm/tests/u11-api-check.mjs packages/paludarium-wasm/paludarium.wasm
```

native-onlyはrunner自身がLinux network namespace隔離を検査し、不成立なら失敗する。Chromium/Firefox/SafariはCOOP/COEPページで同じguestケースを実行する。SafariコマンドはmacOS専用。実guestはモックに置換しない。必要Rust内部単体の正確なtest-filterを実装時に追加し、全workspaceコマンドをUnit手順に混在させない。

準備検査（実guestの受入結果を代替しない）：

```sh
node packages/paludarium-wasm/tests/u11-browser-ready.mjs chromium firefox
node packages/paludarium-wasm/tests/u11-browser-ready.mjs safari
```

承認済み修正によりspikes/wasm-threads/package-lock.jsonのPlaywright 1.63.0を使用する。`npm ci --prefix spikes/wasm-threads`の後、固定版に対応するbrowserを用意する。`PLAYWRIGHT_BROWSERS_PATH`を指定した場合、installとrunで同じ値を使う。Safariは実safaridriverで接続する。driver startup/session creation/navigation/script/cleanupの失敗は段階付きで保持する。製品prefsやprofilerを有効にせず既定設定で合格を検証する。

製品変更前の現wasm診断はfresh native取得後だけ実行する（oracleパスはそのrunのダウンロード先に置換）：

```sh
python3 scripts/u11-run.py --baseline --node /path/to/real/node --wasm packages/paludarium-wasm/paludarium.wasm --native target/u11/native/observations.json --guest-dir target/guests/u10 --output target/u11/baseline
```

この診断の既知GAPは合格へ読み替えない。全suiteの外部600秒監督がprocess groupを終了・回収し、suite-supervisor.jsonと途中observations.jsonを保持する。各guestは別に30秒期限を持つ。oracleのguest hashが一致しなければ実行しない。検証済み：自己診断、Python24件、JS29件（contract7、WebDriver8、filesystem7、Worker7）、実wasmのC12境界試験。生記録はverification/c12-boundary-proof.jsonを参照する。

U11のみinstall/frozenに公式`--reporter=append-only`を双方へ指定する。fixture初期mtimeをepoch0へ揃え、nativeのcwd/HOME/TMPDIRをguestへ渡す。生成lockfile時刻は各側の実statとの整合を検査してから明示的に正規化する。詳しい比較規則と固定aubeの根拠はfilesystem-comparison.mdに記録する。U10の既定ケースは変更しない。

syscall_argsの空pipe待機inputはfuzz専用Hostのwait_on quotaを回帰7件で確認する。修正前の失敗と修正後の成功はverification/syscall-wait-regression.mdに保持する。製品のblocking readと30秒/600秒の上限を変えない。Firefoxのtask診断helperは観測専用で、受入合格には使用しない。

MMU候補は実Firefoxの3回ずつの検証で改善せず、承認済み修正により署名済み47a38745の実装へ戻した。候補の試験・失敗記録はverification/mmu-read-path.mdへ保持する。専用MMU追加coverageと追加3fuzzは候補撤回に合わせ除き、既存workspace/U1下限は維持する。独立したfuzz専用Hostのquota修正と7件の回帰を維持し、元の7対象各600秒ASan/LSan・入力30秒を新headで実行する。Firefox検証器の上流修正と隔離比較はverification/firefox-driver-repair-proposal.mdを参照する。

## Tests and Coverage

- 新規/変更内部部品は各7件、C12境界は8件。正常と最低2種の異常/境界を含める。Worker開始失敗、trap、timeout、kill、dispose、stdin EOF、streamエラー、複数ゲストの状態分離を確認する。
- probe8項目＋all/environmentとaube4操作を同じバイナリでNode/Chromium/Firefox/本物Safariへ渡す。各操作でstdout/stderr/exit、filesystem、fixture0644、node不在、#1645をfresh Linux nativeに照合する。
- install→node_modules除去→frozen→listのVFS状態保持を含める。既存API/default0755を壊さない。異なるguestに状態を漏らさない。
- 30秒のguest期限は外部テスト監督で実装し、子Workerを回収する。C12の契約では利用者のkillによる停止を保持する。buildとbrowser全suiteには別の有限期限を設定する。
- 変更Rust部品はLinux行coverage80%以上、既存workspace/U1/U3/U9など設定済み下限を維持する。対象source依存が変われば既存fuzz証拠を自動再利用せず必要な600秒ASan/LSanを再実行する。
- 既存3OS単体/lint/依存/Linux差分/production wasmはCI全体の必須チェックとして維持する。U11手順はU11の専用実行だけを定義する。

## Evidence and Traceability

最終実装証拠は署名head7eb1819f52acede33e83775374dd4ee93edf643b、CI38021278452（attempt3全jobs成功）。Node/Chromium/Firefox/native/coverage/fuzzはverification/final-7eb-ci、最新実Safari成功はverification/final-7eb-safari-attempt3を参照する。旧final-7eb-ci/u11-safariは準備失敗であり受入成功の証拠へ使わない。65パスmanifest/hash、traceability、acceptance-evidence、pack-proof、timingsを同headへ結び付けた。正式検証コマンドは親担当が人の変更承認後に実行し、これらの実装試験でその承認・独立レビューを代替しない。

FR5.2/FR5.3/FR5.4/FR6.3/FR7.2/FR7.3/FR7.4/FR9.1/FR9.2、NFR1〜NFR4/NFR6〜NFR9が対象。source/module/guest/oracle hash、runner環境、各case結果・時間・cleanup、signed headとCIを保存する。古いoracleを新runへ読み替えず失敗も保存する。未検証をPASSへ変えない。

