# U9 単体・差分テスト手順

## 今回Step82：確かめ直しの指摘を記録で直す

記録だけを直すので、新しい試験はない。project rootで正式sensor 2件を実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/traceability.json
```

期待する結果：required-sectionsはpass、traceabilityは前と同じ（traceability.jsonを変えていない）。checkpointでは今の正式な確認コマンド（`verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`）を実行する。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べる（`entry-f.py` の `verify_working_copy`）ので、exit 0になる想定で、結果はcheckpointの記録が持つ。

## 履歴：Step 81（作成時の見出しは「今回Step 81：変更がないことの再確認」）

（この節の正式確認コマンド（U2の `u2_candidate.py`）は2026-10-17時点のもの。2026-10-19からは上の Step82 の節のとおり entry-f・binding-e06f。）

新しいテスト・CIの実行はない。project rootで、U9のsource-manifestの全ファイルが e4f84768 と同じであることを確かめる（読み取りだけ）。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/source-manifest.json'))['writes']))")
```

期待する結果：exit 0（差なし）。checkpointでは今の正式確認コマンド `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` がexit 0になる。

## 前回Step 80：差分jobへのheadの受け渡し

新しいテストはない。変えたworkflowを actionlint で確かめる。CIでの再実行は Build and Test で行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u10-native-diagnostic.yml
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md
```

期待する結果：u10-native-diagnostic.yml の指摘0件。sensorは2件とも pass。

## 今回Step 79：Pythonの準備とactionlintの扱い

shellcheck はインストール済みの 0.11.0 を明示する（mise の shim には版が設定されていないため）。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u11-acceptance.yml .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml
env PATH="$HOME/.cargo/bin:$PATH" PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node cargo test --locked -p paludarium-jit --lib
```

期待する結果：actionlint は u11-acceptance.yml と u10-native-diagnostic.yml の指摘0件。ci.yml は今回触れない87・203・226行目の既存4件（SC2086×2、SC1090×2）だけで、新しい指摘はない（このため終了コードは1）。JITのlib試験は失敗0件。

## 今回Steps77〜78：workflowの修正

新しいテストはない。変更する3つのworkflowの書き方を actionlint で確かめ、`PALUDARIUM_TEST_NODE` を設定するとJITの実Wasm試験が通ることを、この Mac で確かめる（設定しないと9件が失敗することは確認済み）。CIでの実行は、Build and Testで人の承認を得てから行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint .github/workflows/u11-acceptance.yml .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml
env PATH="$HOME/.cargo/bin:$PATH" PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node cargo test --locked -p paludarium-jit --lib bridge::tests::
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md
```

期待する結果：actionlint は指摘なしで終了コード0、JITの `bridge::tests::` は失敗0件。

## 今回Step76：記録の文言修正（R-06・R-07・R-08）

新しいテスト・スクリプト・CI実行はない。code-summary.mdとtraceability.jsonの文言だけを直す。Step72・Step74のスクリプトと結果JSONは再実行も変更もしない。確認は、次の正式sensorと、採用済みの正式検証コマンドでのcheckpoint再検証で行う。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md
```

## 今回Steps74〜75：再集計とcompiler・lockの結合（R-02・R-04・R-05）

新しいCI実行・push・外部送信は行わない。Step72の結果（`verification/step72-u9-coverage-recount.json`）は変更せず、参照するだけにする。保存済みjobログ `job-116962253357.log` のcompilerの記録行と、署名済みhead be45b36cの `Cargo.lock`・`fuzz/Cargo.lock`・`rust-toolchain.toml` のbytesに結びつける。headのbytesは、読み取り専用の `jj --ignore-working-copy file show` で取得する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/verification/step74_u9_coverage_binding.py
```

このスクリプトは結果を `verification/step74-u9-coverage-binding.json` に排他作成で保存する。保存するものは次のとおり。

- headのlock・toolchainのSHA-256（パスごと、`lock_sha256_by_path`）と、作業コピーとの一致・不一致
- jobログに記録されたcompiler
- Step72 JSONの `lock_sha256` 欄の訂正注記
- DA行数とTOTAL行数の差の原因（未確認であること）

照合が不一致なら終了コード1にする。照合できない項目は未照合と書き、成功とは扱わない。80%下限と3集合の値はStep72のものをそのまま使い、再計算も変更もしない。

## 今回Steps72〜73：U9固有coverageの現行再集計（R-02）

新しいCI実行・push・外部送信は行わない。署名済み現行head be45b36ce9d7a65719ba1f86cf6a0b018070741bの公式品質CI run 38897611874（job 116962253357）が、下記「U9 のテスト」節と同じ既存U9 coverageコマンド（packages・`--ignore-filename-regex`・`--fail-under-lines 80` 不変）を実行して公開した `u9-coverage-lcov` artifactを、U15 verification `full-quality-1792153236541522000/` の保存原本から再集計する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/verification/step72_u9_coverage_recount.py
```

このスクリプトは artifact digest と保存ZIPのSHA-256一致、ZIP内lcovのSHA、`verification/step20-fixed-proof.json` の旧13ファイル集合・追加10ファイル集合（各パス欠落・重複は拒否）を検査し、各集合と全23件の行数・カバー行数・割合と80%判定を `verification/step72-u9-coverage-recount.json` に保存する。いずれかの集合が80%未満なら終了コード1で失敗として記録する。旧541b値（旧13 2693/3202、追加10 2156/2397）は履歴として保持し置き換えない。これはU9固有coverageの現行値であり、Linux差分・Node／Safari・ASanの新実行、U15受理の証拠ではない。正式完了検査は採用済みの正式検証コマンド（`r05-r11-repair-01/final_candidate.py`、SHA-256 `d799bbb9…`）を正式checkpointで実行する。

## 今回Steps22〜24：記録と証拠の再確認

製品・既存試験・旧証拠を保持し、新しい重い試験は追加しない。現行manifestの担当ソース、依存、両lock、compiler、設定を保存原本へ照合する。旧実行と今回の照合を区別し、不一致は分類して未検証を明記する。既存の80%分母、30秒制限、mask、strict guardを維持する。以下の旧コマンドは履歴・必要時の再現手順であり、今回すべてを再実行する指示ではない。

正式検査はU9限定で行う。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md
```

独立レビュー後、承認済み最終確認コマンド `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py` を正式checkpointから実行する。検査対象を有限に記述し、U9専用の新しいcoverage・Linux差分・Safari実行の代替とは主張しない。不足した追加検証は具体化して人へ返す。

## Steps19〜21：最新ClippyとRust版統一

diff_u7.rsの2行と、製品/検証のRust固定版・実行script/CIの明示指定だけを最新公式確認版へ揃える。履歴証拠を書き換えず、実使用版・全変更path・両lockを保存する。以下の既存入口を最終ソースで実行する。

```bash
cargo fmt --all --check
cargo clippy --locked -p paludarium-host -p paludarium-kernel -p paludarium-runtime -p paludarium -p paludarium-harness --all-targets -- -D warnings
cargo deny --locked check advisories bans licenses sources
cargo test --locked -p paludarium-harness --test diff_u7 --test diff_u9 -- --nocapture
```

Steps16〜18のU9 coverage/production wasm/Node/本物Safari全caseの入口も最終ソースで再実行する。旧13productionファイル集合と追加10集合を分け、いずれも80%下限を維持する。Safariにも全入力before/after監査を追加し、同一module/native SHA、28秒operation/30秒whole-process watchdogとcleanupを確認する。失敗が後続成功に隠れないよう各実exitを保存して強制判定する。

重いASan/LSanは対象ごとのproduction dependency、実使用compiler、flags、suppressionの一致を証拠で示す場合だけ再利用する。設定/時点が変わることを記録し、旧全入力を新全入力と同一とは主張しない。不一致対象は必要な再検証を提案する。新canonicalは人の別承認まで実行しない。

## 追加Steps16〜18：現行実測

署名済みfork診断CIで製品を変更せず全入力・両lockを固定し、最新版ツールを公式確認して診断環境へ固定する。

```bash
cargo test --locked -p paludarium-harness --test diff_u9 -- --nocapture
RUST_TEST_THREADS=1 cargo llvm-cov --locked -p paludarium-host -p paludarium-kernel -p paludarium-runtime -p paludarium -p paludarium-harness --lib --test diff_u9 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|mmu|loader|types|vfs|jit|harness)/' --fail-under-lines 80 --lcov --output-path target/u9-coverage.lcov
python3 packages/paludarium-wasm/tests/generate-guests.py --check
python3 scripts/wasm-native-guests.py
bash scripts/build-wasm.sh
node --test packages/paludarium-wasm/tests/import-check.mjs
node packages/paludarium-wasm/tests/node-check.mjs packages/paludarium-wasm/paludarium.wasm target/production-wasm-evidence/native-results.json
cargo fuzz run --fuzz-dir fuzz --sanitizer address load_elf -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
```

native JSONは同CIで生成して記録する。既存coverage測定用instrumented CLIと環境変数を準備し、分母・除外を維持する。ASAN_OPTIONS=detect_leaks=1、既存fuzz/lsan.suppのLSAN_OPTIONS、最小C2回exit0、binary/symbols/corpus/crash、生ログと終了コードを保存する。署名Verifiedとsource before/after/currentを照合する。

本物Safariは既存step11-safari-diagnostic.mjsを用い、同CI module/native JSONで現行全ケースを実行する。COOP/COEP・crossOriginIsolated・同module SHA・既存28秒operation/30秒whole-process watchdog・driver/server cleanupを確認する。旧14件へ削減しない。権限不足、時間超過、失敗は未検証または失敗とする。U7のsyscall_args/vfs_paths/mmu_opsは全入力一致で限定再利用する。新canonicalは別途人の選択まで実行しない。

## 今回Steps13〜15の再確認

既存製品を保持し、今回の実行と保存された過去結果を分ける。U9担当と各検証の依存ソース・両lock・設定が一致する範囲だけ保存証拠を再利用する。最新ツールの版と実体を確認して、次の既存U9限定入口を使用する。

```bash
cargo test --locked -p paludarium-host --lib u9_ -- --nocapture
cargo test --locked -p paludarium-kernel --lib u9_ -- --nocapture
cargo test --locked -p paludarium-runtime --lib u9_ -- --nocapture
cargo test --locked -p paludarium-host --test u9_public_api
cargo test --locked -p paludarium-host --doc Terminal
cargo test --locked -p paludarium --test command u9_ -- --nocapture
```

native Linux差分の不足回収入口は既存 `cargo test --locked -p paludarium-harness --test diff_u9 -- --nocapture`。Mac/QEMUをnative Linuxと呼ばない。U9 coverage80%の測定対象・除外・分母、30秒watchdogを維持する。wasm/SafariやASanの依存不一致は未検証と記録し、最小追加検証案を人へ提示する。過去の全体カバレッジをU9専用合格へ代用せず、0件・skipを合格にしない。

## 実行と準備

固定nightlyとCargo.lockを使う。mise管理の実体を解決し、cargoコマンドはその実体で実行する。手順中のcargoはその実体を表す。差分テストはLinux x86-64実機CIで行い、手元Docker VMM結果と区別する。
最初のテスト実行前にU9専用モジュール/入口を作り、以下の--listで対象ケースが0件でないことを確認する。0件成功をPASSにしない。

- cargo test --locked -p paludarium-host --lib u9_ -- --list
- cargo test --locked -p paludarium-kernel --lib u9_ -- --list
- cargo test --locked -p paludarium-runtime --lib u9_ -- --list
- cargo test --locked -p paludarium-harness --test diff_u9 -- --list
- cargo test --locked -p paludarium --test command u9_ -- --list

準備後の実行は同じコマンドから -- --list を除く。Linux実機で bash tests/guests/u9/build.sh を先に実行し、生成ゲストを差分入口へ渡す。具体的な環境変数は入口実装と整合させて記録する。

## ケースと合否

## 今回の公開型回帰

既存Cargo設定を使い、新規依存は追加しない。cargo test --locked -p paludarium-host --test u9_public_api -- --listで5〜8件の存在を確認し、cargo test --locked -p paludarium-host --test u9_public_apiを実行する。cargo test --locked -p paludarium-host --doc Terminalで外部literal禁止のcompile_fail例を確認する。内部APIテストは実装後に書く。通常・Default・非端末・境界値を含める。

既存各u9_フィルタ・diff_u9・CLI command u9_を維持する。Linux実機CIではguestとnative期待値をその場で生成する。変更後の3OSテスト、U9対象coverage80%以上、Node/実Safariのproduction wasm既存14ケースのraw・source/artifact hashを保存する。ASan/fuzz/Windows race保存証拠は依存byte一致で再利用可否を判断し、不一致対象は必要な検証を行う。全体CIゲートは差分影響確認として一度行い、各Unitで反復しない。

旧canonicalのsource不一致は失敗として保存し、新ソース対応checkerとcommandの承認を取得する。保存済み成功を今回の実行へ読み替えない。

Host・Kernel・Runtimeは各5〜8件。TestingHostでstream別tty/寸法とstdin、stdout/stderrを制御し、通常・境界・失敗を含める。
syscall/ゲストケースを先に作りnative期待結果を実行時に取得してから実装する。内部部品のテストは実装後に書く。
差分はargv/envp、短いread/EOF、stdout/stderr、TCGETS/TIOCGWINSZ、非tty、bad fd、bad pointer、unknown request、dupされた標準fdを確認する。PTYはnative/guestで同じ設定と寸法を使い30秒watchdog付き。端末依存・OS依存の値を比較不能として隠す場合は理由と比較範囲を残す。
LinuxのU9対象行カバレッジ80%以上を測定し対象ファイル一覧と分母/分子を保存する。既存全体/U1カバレッジをU9合格の証拠にしない。
3OS内部テストとLinux差分を分け、macOS/Windows実機tty、wasm/Safari、現行fuzzは実行するまで未検証。coverageやfuzz不足はGAPとしてレビューに示し閾値を下げない。
ゲストfixtureは専用一時領域で生成/削除する。fake HostはOS呼び出しを模倣して差分の代わりにせず内部境界の確認に使う。
