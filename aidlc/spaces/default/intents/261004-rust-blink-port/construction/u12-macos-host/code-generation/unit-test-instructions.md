# U12 macOS Host — Unit Test Instructions

## 今回Step13：変更がないことの再確認

新しいテスト・CIの実行はない。project rootで、U12のsource-manifestの全ファイルがe4f84768と同じであることを確かめる（読み取りだけ）。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u12-macos-host/code-generation/source-manifest.json'))['writes']))")
```

期待する結果：exit 0（差なし）。checkpointでは今の正式確認コマンド（U11の `u11_candidate_v2.py`、`--entry-sha256 56870072…`・`--binding-sha256 a3d81077…` 付き）がexit 0になる。

## 今回Steps14〜15：code-summary.mdの更新

新しいテスト・CIの実行はない。code-summary.mdの冒頭に「現行Step13〜15」節があり、「現行」で始まる古い見出しが残っておらず（冒頭の節を除く）、古い候補の文が履歴と分かる表示になっていることを読んで確かめ、正式sensorを実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u12-macos-host/code-generation/code-summary.md
```

期待する結果：sensorはpass。checkpointでは今の正式確認コマンドがexit 0になる。

## 前回Steps11〜12：workflowの修正

新しいテストはない。変更する2つのworkflowの書き方を actionlint で確かめる（shellcheck はインストール済みの 0.11.0 を明示する）。CIでの実行は、Build and Testで人の承認を得てから行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u12-native-first.yml .github/workflows/u12-quality.yml
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u12-macos-host/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u12-macos-host/code-generation/code-summary.md
```

期待する結果：今回変えた2行に新しい指摘がないこと。変更前からある指摘があれば、行番号と内容を「既存の指摘」として記録し、直さない。sensorは2件とも pass。

## Runner Readiness and Tools

更新範囲：nightly-2026-10-11を製品pin・固定guest・現行CI・wasmに統一する。公式確認版Python3.15.0／coverage7.16.2／llvm-cov0.9.1／deny0.20.2／fuzz0.13.2、Actions最新releaseのcommit SHAを使用する。cargo実体に加えRUSTC／RUSTDOCも同じtoolchain実体へ指定する。旧10-10 readiness8件は診断履歴として区別する。

計画承認後、最新の公式版を確認し使用実体・compiler -Vv・Python版・llvm-cov版・cargo-deny版を保存する。mise管理toolはこのMacの実install pathを解決する。以下cargo/pythonはその実体で実行する表記であり、版を推測しない。

最初の差分期待値取得より前に実行可能な既存入口：
```sh
python3 scripts/u10-run.py --self-test
cargo test --locked -p paludarium-host --lib u4_tests:: -- --test-threads=1
```
runner readinessが失敗したら期待先の工程へ進めない。Linux期待値は固定guestをfresh build後、Linuxネットワーク隔離環境で既存native-only入口を使う。U12専用runnerの生成後は下記入口へ限定する。

## U12 Scoped Commands

```sh
cargo test --locked -p paludarium-host --lib u12_tests:: -- --test-threads=1
cargo test --locked -p paludarium-host --test u12_public_api -- --test-threads=1
python3 -m unittest discover -s tests/guests/u12/runner-tests -p 'test_*.py' -v
python3 scripts/u12-run.py --self-test
python3 scripts/u12-run.py --guest-dir target/guests/u10 --native target/u12/native/observations.json --output target/u12/macos
cargo llvm-cov --locked -p paludarium-host --lib u12_tests:: --json --output-path target/u12/host-coverage.json
cargo llvm-cov --locked -p paludarium-host --test u12_public_api --no-clean --json --output-path target/u12/host-coverage.json
```

新しいU12 script／test入口はStep2／4で作る予定であり現在は未存在。coverage集計は事前固定したnative Host6ファイルの実行可能行を対象に、両実行のprofileを合算する。専用集計器で80%以上をfail条件として検査し、対象外を途中で増やさない。Python runnerのcoverageはtests/guests/u12の製品比較部品を対象に80%以上。

## Test Cases and Fixtures

内部3部品各7件以上（21件）と実PTY統合7件以上。portable時計・期限到達・cancel・wake-before-wait・thread join・stdio・random、FS errno／flock／symlink escape／負mtime／bytes path、Darwin端末属性変換を検査する。PTYは本物macOS OS接続、tempdirは各テストで独立し権限0644を明記する。RecordingHostのstubは変換の単体検査だけに使い、native guest／PTY成功の証拠へ代用しない。

固定guestはprobe8項目＋all／node不在とaube4操作の14ケース以上。同一guest hash／source-lock／build receiptとfresh Linux native原本を使い、元argv・#1645・stdout／stderr／exit／filesystemを検査する。既存の比較maskだけ維持し、OS差で新maskを足して不一致を消さない。

## Isolation, Evidence and Regression

追加のcompiler移行検査：同じ最終署名headでfresh Linux既存差分・workspace80%・3OS品質・production wasm＋4環境各14ケース以上を実行する。旧7手順の保存ASan再利用方針は履歴で、更新後は11対象を各600秒新規実行する。Linux実機隔離CI、ASAN_OPTIONS=detect_leaks=1、既存fuzz/lsan.supp原本とsymbolizer条件、入力30秒を維持する。

対象別コマンドは `cargo fuzz run --fuzz-dir fuzz --sanitizer address TARGET -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048`。TARGETはcpu_u2／mmu_u2／decode／load_elf／mmu_ops／syscall_args／vfs_paths／kernel_threads_u5／kernel_futex_u5／kernel_events_u6／kernel_sockets_u6へ一つずつ置換する。cpu_u2だけ `-max_len=4096`、mmu_u2だけ `-max_len=4608` を追加する。対象別compiler・依存・両lock・binary・設定・生ログ・開始終了・実exitを保存し、旧binary一致の推定で新実行を省かない。

guest1操作30秒、実PTY子processは30秒以内にkill／wait／cleanup。時間・timeout・実exit・ignored0・非0case数を保存。ネットワークの封鎖、fixture外のsentinel不変を検査する。macOS native結果とLinux oracle、旧履歴を区別する。

CI専用jobは3OSのHost／既存Unit回帰と品質監査を一度だけ実行する。これら共有回帰の全suite命令はU12専用test命令へ混ぜずCIで管理する。共有製品変更後のwasm／Node／本物Safariの実行とASan条件照合を追加する。重い検査は同compiler・deps・config・binary一致する保存証拠だけ再利用し、未成立は未検証として報告する。新canonicalは独立レビューと人のコマンド承認後に正式実行する。

