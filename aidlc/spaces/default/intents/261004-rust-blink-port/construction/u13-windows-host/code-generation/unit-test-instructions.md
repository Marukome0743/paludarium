# U13 Unit Test Instructions

## 今回Step16〜18：27d05de1の後の確かめ直しの指摘を記録で直す（2026-10-19。Step17・Step18も同じ確かめ方）

記録だけを直すので、新しい試験・CIの実行はない。project rootで、U13のmanifestのうち変わっていない20ファイルがe4f84768と同じであることを読み取りで確かめ、正式sensor 2件を実行する。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- .github/workflows/u13-wasm-acceptance.yml crates/paludarium-harness/tests/diff_u13.rs crates/paludarium-harness/tests/support/u13.rs crates/paludarium-host/src/lib.rs crates/paludarium-host/src/native_fs.rs crates/paludarium-host/src/u13_tests.rs crates/paludarium-host/src/windows.rs crates/paludarium-runtime/src/workers.rs scripts/u13-run.py tests/guests/u13/fixture.py tests/guests/u13/host_comparison.py tests/guests/u13/operation.py tests/guests/u13/oracle.py tests/guests/u13/runner-tests/test_boundaries.py tests/guests/u13/runner-tests/test_oracle.py tests/guests/u13/runner-tests/test_settings.py tests/guests/u13/runner-tests/test_stop.py tests/guests/u13/runner.py tests/guests/u13/settings.py tests/guests/u13/windows_job.py
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/traceability.json
```

期待する結果：git diffはexit 0（差なし）。ファイルは1つずつ挙げる（`tests/guests/u13` をディレクトリで指定すると、作業コピーにある `__pycache__` を拾うおそれがある）。required-sectionsはpass、traceabilityはpass・findings 0。manifestのほかの2ファイル（`.github/workflows/u13-native-first.yml`・`u13-quality.yml`）は8360be2eで変わったので、このgit diffには入れない（変わった中身はcode-summary.mdの先頭の節）。checkpointでは今の正式な確認コマンド（intent直下の `verification-command.txt` の1行目、U15の `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`、2026-10-19に人が採用）を実行し、exit 0になる想定。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べる。

下の節は、それぞれの時点の手順・記録である。下の節が挙げるU11の `u11_candidate_v2.py` は2026-10-18の時点の正式な確認コマンドで、今は使わない。下の節の「manifestの全ファイルがe4f84768と同じ」（exit 0）は2026-10-18の時点の期待結果で、今はworkflow 2つが違うのでexit 1になる。

## 履歴：Steps13〜15：変更がないことの再確認と、要約の更新（2026-10-18）（作成時の見出しは「今回Steps13〜15：変更がないことの再確認と、要約の更新」）

新しいテスト・CIの実行はない。project rootで、U13のsource-manifestの全ファイルがe4f84768と同じであることを確かめる（読み取りだけ）。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/source-manifest.json'))['writes']))")
```

期待する結果：exit 0（差なし）。code-summary.mdを直した後、冒頭に「現行Step13〜15」節があり、「現行」で始まる見出しが冒頭の節だけで、(d)がcheckpointでの検証結果を書き、`U15_acceptance: GAP` の意味が説明されていることを読んで確かめ、正式sensorを実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/code-summary.md
```

期待する結果：sensorはpass。checkpointでは今の正式確認コマンド（U11の `u11_candidate_v2.py`、`--entry-sha256 56870072…`・`--binding-sha256 a3d81077…` 付き）がexit 0になる。

## 履歴：Steps11〜12：workflowの修正（2026-10-17）（作成時の見出しは「前回Steps11〜12：workflowの修正」。actionlint 1.7.12・shellcheck 0.11.0はその時点の版で、`u13-native-first.yml`・`u13-quality.yml` はその後8360be2eで変わった）

新しいテストはない。変更する3つのworkflowの書き方を actionlint で確かめる（shellcheck はインストール済みの 0.11.0 を明示する）。CIでの再実行は Build and Test で行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u13-native-first.yml .github/workflows/u13-wasm-acceptance.yml .github/workflows/u13-quality.yml
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u13-windows-host/code-generation/code-summary.md
```

期待する結果：変えた行に新しい指摘がないこと。変更前からある指摘は行番号と内容を「既存の指摘」として記録し、直さない。sensorは2件とも pass。

## 履歴：Runner Readiness（Steps1〜10の計画時の手順。作成時の見出しは「Runner Readiness」）

既存Rustテスト入口を先に確認する。以下はU9のHost公開API境界に限定したrunnerの準備確認で、U13完成の証拠にはしない。

```text
cargo test --locked -p paludarium-host --test u9_public_api
```

Rustはrust-toolchain.tomlの版を使う。Windowsのmiseツールはインストール先の実体を解決する。新規入口の最初の実行前にファイルとテスト名の存在、列挙件数を確認する。

## 履歴：U13 Commands（Steps1〜10の計画時の手順。作成時の見出しは「U13 Commands」）

以下は実装済みのU13専用入口。新しい署名headでの最終実行は未完了であるため（2026-10-19 注記：その時点の記述。その後、署名head 832abd0fのCI 38236916982と、27d05de1のu13-quality run 39149192303で実行され成功した）、実行前に引数と件数を照合し、0件／skipを成功にしない。

```text
cargo test --locked -p paludarium-host --lib u13_
python3 -m unittest discover -s tests/guests/u13/runner-tests -p "test_*.py"
python3 scripts/u13-run.py --emulator <diff_u13の実ビルドしたテスト実行形式> --guests <同CIの固定guestディレクトリ> --native-report <同CIのfresh-Linux報告JSON> --output <新規U13報告>
python3 scripts/u13-run.py --original-argv --emulator <同じ非instrumented実行形式> --guests <同じ固定guestディレクトリ> --native-report <同CIの元argv fresh-Linux報告JSON> --output <別の元argv U13報告>
```

専用runnerはこの引数を実装し、Rustテストの全U13名にu13_を含める。実console／ConPTY検査も同filterで実行できるようにし、端末の前提確認は子プロセス内で行う。正確なtarget一覧は専用CIに明記する。

## 履歴：Cases and Ordering（Steps1〜10の計画時の手順）

差分ケースとfresh Linux期待結果をHost修正前に確定する。内部部品は実装後に単体テストを書く。

- 端末変換7件以上：stdin／stdout／stderr、非端末、無効handle、mode変換、winsize境界。
- NativeFs7件以上：hard link、symlink、権限不足、flock競合／解放、外部パス拒否、strict cleanup。
- 待機7件以上：value mismatch、wake-before-wait、期限、cancel、wake数、join、並行性。
- 実Windows端末7件以上：console／ConPTY、redirect、幅、stream別、エラー、設定非変更、終了時cleanup。
- guest14件以上：既存probe8項目とaube4操作、node不在／#1645を保持。元argvとdefault VFSは別に記録する。

## 履歴：Coverage and Quality（Steps1〜10の計画時の手順）

LinuxのHost共通実行可能ファイル・Python coreを測定前に列挙して80%以上。Windows固有ファイルはWindowsで別に80%以上。Linuxの分母から除いたWindows行を検証済みとしない。3OSの既存回帰・fmt／Clippy・依存4検査は専用CIで実行するが、上記のUnitコマンドを全workspace再実行へ置き換えない。

通常Windows guest比較は独立targetディレクトリへRust coverageなしでビルドし、primary14＋default2と元argv14＋default2の計32件を必須・continue-on-errorなしで検査する。元argv・fixture・30秒・比較maskは保持する。coverageは同じ署名head・compiler・guest bytesの別instrumented実行形式でprimary14＋default2と内部境界から測定する。固定Host6／共通5／Windows1、Python7、JS5の分母と80%下限は変更しない。Python coverageは通常32件と既存35回帰の実経路も測定する。

各buildのhead／compiler／binary SHA256／RUSTFLAGS／CARGO_ENCODEDRUSTFLAGS／targetディレクトリを原本へ記録し、通常実行へinstrument-coverageが含まれず、coverage実行には含まれることを厳密に照合する。一時Runtime observer、Host透過trace、25秒watchdog、diagnostic input／job／skipが残った測定を最終合格へ使用しない。Testing Contractのcustom orderingはそのまま適用する。

## 履歴：Fixtures and Boundaries（Steps1〜10の計画時の手順）

同一static-musl guest・固定aube・両lockを使う。隔離一時fixture、標準出力／標準エラー／exit／ファイル状態を保持する。mockは純粋なmode変換・errno・runnerの停止境界に限定し、実端末・guest比較・symlink権限の代わりにしない。guest30秒、ASanは影響対象600秒、MMU最大4608バイト。失敗原本を保持し、依存／compiler／binary／設定一致の証拠だけ再利用する。
