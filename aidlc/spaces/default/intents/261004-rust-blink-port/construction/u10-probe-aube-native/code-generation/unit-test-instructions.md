# U10 単体・差分テスト実行手順

## 今回Step33〜36：確かめ直しの指摘を記録で直す

Step33〜36とも記録だけを直すので、新しい試験はない。どのStepも次の同じsensor 2件と同じ期待結果で確かめる。project rootで正式sensor 2件を実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/traceability.json
```

期待する結果：required-sectionsはpass、traceabilityはpass・findings 0（FR9.1のtargetを `u10-native-diagnostic.yml` に替え、消えたworkflowの逆引きの行を外した後）。checkpointでは今の正式な確認コマンド（`verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`、人が2026-10-19に採用）を実行する。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べる（`entry-f.py` の `verify_working_copy`）ので、exit 0になる想定で、結果はcheckpointの記録が持つ。

今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`。下の節の `git diff --quiet e4f84768` のexit 0の期待は、U15が27d05de1で `ci.yml` と `tests/guests/u10/runner-tests/test_evidence.py` を変え `u10-current-verification.yml` を消したので、今は成り立たない。下の節の正式確認コマンド（`u2_candidate.py` など）とtoolchainの版は、それぞれの時点のものである。

## 履歴：Step31（作成時の見出しは「今回Step31：変更がないことの再確認」）

新しいテスト・CIの実行はない。project rootで、U10のsource-manifestの全ファイルがe4f84768と同じであることを確かめる（読み取りだけ）。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/source-manifest.json'))['writes']))")
```

期待する結果：exit 0（差なし）。checkpointでは今の正式確認コマンド `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` がexit 0になる。

## 履歴：Step30：共有workflowの再確認（作成時の見出しは「前回Step30：共有workflowの再確認」）

新しいテストはない。U9が直したworkflowの書き方を actionlint で確かめる（shellcheck はインストール済みの 0.11.0 を明示する）。CIでの実行は、Build and Testで人の承認を得てから行う。

```sh
/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/code-summary.md
```

期待する結果：u10-native-diagnostic.yml の指摘0件。ci.yml は今回触れない87・203・226行目の既存4件（SC2086×2、SC1090×2）だけで、新しい指摘はない（このため終了コードは1）。sensorは2件とも pass。

## 履歴：Step29：参照の対応関係の明記（R-09）（作成時の見出しは「今回Step29：参照の対応関係の明記（R-09）」）

新しいテスト・スクリプト・guest実行・CI実行はない。code-summary.mdに1文を足すだけである。確認は下のStep26節と同じ正式sensor 2件で行い、そのあと採用済みの正式検証コマンドを正式checkpointで実行する。

## 履歴：Step28：裏付けファイルの明示（R-08）（作成時の見出しは「今回Step28：裏付けファイルの明示（R-08）」）

新しいテスト・スクリプト・guest実行・CI実行はない。code-summary.mdの参照文1つを直すだけである。確認は下のStep26節と同じ正式sensor 2件で行い、そのあと採用済みの正式検証コマンドを正式checkpointで実行する。

## 履歴：Step27：見出しと参照の修正（R-06・R-07）（作成時の見出しは「今回Step27：見出しと参照の修正（R-06・R-07）」）

新しいテスト・スクリプト・guest実行・CI実行はない。code-summary.mdに見出しを1つ足し、実行記録の参照を1文添えるだけである。確認は下のStep26節と同じ正式sensor 2件で行い、そのあと採用済みの正式検証コマンドを正式checkpointで実行する。

## 履歴：Step26：記録の文言修正（R-04・R-05）（作成時の見出しは「今回Step26：記録の文言修正（R-04・R-05）」。この節の「採用済みの正式検証コマンド（`final_candidate.py`）」はその時点のもの）

新しいテスト・スクリプト・guest実行・CI実行はない。code-summary.mdの文言だけを直す。確認は次の正式sensorで行い、そのあと、採用済みの正式検証コマンド（`final_candidate.py`、SHA-256 `d799bbb9…`）を正式checkpointで実行する。以下のSteps1〜25の手順は履歴であり、今回は再実行しない。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u10-probe-aube-native/code-generation/code-summary.md
```

## 履歴：確認参照修正（Steps22〜25）（作成時の見出しは「今回の確認参照修正（Steps22〜25）」）

今回実行するのは検証スクリプトの原本／現行参照分離と回帰である。以下のSteps1〜18のguest・CI・coverage手順は過去の実行履歴として保持し、今回新規実行したと主張しない。製品・既存試験・旧checker・旧原本は保持する。

旧 `validate_current_u10` の対応表期待hashを旧署名ソースまたは保存済み原本に結び付け、bytes完全一致を確認してから旧検査へ渡す。現行U10対応表は別に完全hash・構造・要件・適用範囲を照合する。旧checkerの検査条件を保持し、参照修正を一般的な差分許可や成功結果の置換へ広げない。

新helper／回帰はこのUnitのverificationディレクトリに限定する。正常な旧／現行分離、原本欠落・改変、現行改変、旧／現行取り違え、誤hash、構造／要件欠落、対象外変更等の12境界以上を検査する。実装後に正確な回帰コマンドを記録し、既存 `python3 scripts/u10-run.py --self-test` とPython44件も実行する。

新確認候補は旧全検査を保持して全診断を実行し、生のexitと失敗を確認する。診断は正式checkpointの代わりにしない。正式検査・独立再レビュー後、新コマンドの別承認を得て正式再検証する。新guest／CI・外部送信は追加せず、80%下限・30秒・strictを維持する。

## 履歴：現行ソース追加検証（Steps13〜15）（作成時の見出しは「承認された現行ソース追加検証（Steps13〜15）」）

（この節の「現行実行はnightly-2026-10-10」と「現在承認済みコマンド」はその時点のもの。今は `rust-toolchain.toml` の `nightly-2026-10-11` と entry-f・binding-e06f。）

現行実行はsource-lockとrust-toolchainに一致するnightly-2026-10-10の実体を使い、RUSTC/RUSTDOCも同版へ明示する。以下の10-01指定と旧CI成功は履歴であり、今回の実行手順として使用しない。製品・fixture・既存build/native/differential処理を維持し、新診断helper/workflow2パスのみ追加する。全326入力・両lock・実compiler/設定・署名head・before/after/current・原本exitを保存する。

内部Python44件（core21＋追加23）とrunner self-testを実行する。固定guestを新ビルドし、upstreamソース非改変・static ELF・限定CDLA全文hashとprobe/aube各依存4監査を確認する。ビルド後のnet namespaceでfresh native14を先に生成し、同guestをemulator16で比較する。include-ignoredで本体差分を実行し、append-only主比較と元argv追加結果、probe8/aube4、node不在・#1645・0644・状態遷移・30秒kill/reapを保持する。

3OS品質・既存回帰、空profilesからinstrumented CLI/U10差分を含む既存workspace全体80%を検査する。診断専用coverage.pyは公式最新版を確認して固定する。Python evidence.py/comparison.py/runner.pyの全実行可能行を固定集合で80%以上、追加5モジュールを別集合で報告し、統合実行も計測する。omit/除外pragmaや比較maskを追加しない。同head production wasmをビルドし、aube4操作の逐次時間を保存する。Node/本物SafariでのU10 guest成功は主張しない。

ASan保存証拠は132製品依存・両lock・実compiler・flags/settings・成功jobと601秒原本が一致する範囲だけ再利用する。旧承認済みcheckerを保持して新候補を作り、AST確認のみで独立レビューへ渡す。現在承認済みコマンドは `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3-u5-u6-u8.py`。新候補は別承認後に実行する。

## 履歴：Windows精度の限定修正（Steps16〜18）（作成時の見出しは「承認されたWindows精度の限定修正（Steps16〜18）」）

native_fs.rsのcfg(test)内mtime2件だけを変更し、Windowsは正負1/99ns→0、100/101ns→100nsと既存秒・大値、非Windowsは1nsの境界を検査する。製品処理・fixtureは不変。初回±1ns失敗と診断環境/入口失敗を保存する。

修正後の同一署名CIで上記Steps13〜15の全検査を再確認し、全326入力・両lock・実compiler/settings・before/after/current・実exitを照合する。Python44件、3OS品質/回帰、fresh native14/emulator16・元argv・限定CDLA、workspace/Python core80%、production wasm・aube時間、30秒・比較maskを維持する。ASan保存証拠はテスト限定変更でも依存・バイナリ・compiler/settingsを再評価し、未証明対象を合格扱いしない。旧checkerを保持して限定差分を結合する候補はASTのみ、別の人の承認後に実行する。

## 履歴（Steps1〜18の計画時の手順）：Setup（作成時の見出しは「Setup」）

（この節から最後の「Guest License Regression」までは、Steps1〜18の計画時の手順である。この節と次の節の `nightly-2026-10-01` はその時点のもので、今は `rust-toolchain.toml` の `nightly-2026-10-11`。`+nightly-…` を付けずに `rust-toolchain.toml` に従う。今の確かめ方は先頭の「今回Step33〜36」の節。）

Rust nightlyはrust-toolchain.tomlに合わせる。macOSでは既存mise shimが使えない場合、/Users/mutoakio/.rustup/toolchains/nightly-2026-10-01-aarch64-apple-darwin/bin/ のcargo/rustc実体を使う。Linux CIは固定nightlyとx86_64-unknown-linux-musl、musl-toolsを使用する。aube/probeは独立lock付きguestビルド。新テストrunnerはPython標準ライブラリと既存cargo testを用いる。

## 履歴（Steps1〜18の計画時の手順）：Unit-scoped Commands（作成時の見出しは「Unit-scoped Commands」）

（この節の `+nightly-2026-10-01`・`--toolchain nightly-2026-10-01` はその時点のもの。今は `rust-toolchain.toml` の `nightly-2026-10-11`。）

Step 2で最初に次のコマンドが実行可能な最小runnerと準備検査を作り、成功を確認する。以後、runner設定を変えたら同じ準備検査を再実行する。

```sh
python3 scripts/u10-run.py --self-test
python3 -m unittest discover -s tests/guests/u10/runner-tests -p 'test_*.py'
```

固定guestビルドとnative期待結果を先に実行する。オプションはStep 2のrunner/configでこの形を実装する。

```sh
bash scripts/u10-build-guests.sh target/guests/u10
sudo unshare --net python3 scripts/u10-run.py --native-only --guest-dir target/guests/u10 --output target/u10/native
u10_cargo_home="${CARGO_HOME:-$HOME/.cargo}"
CARGO_HOME="$u10_cargo_home" cargo +nightly-2026-10-01 test --locked -p paludarium-harness --test diff_u10 --no-run
u10_cargo="$(rustup which --toolchain nightly-2026-10-01 cargo)"
u10_rustc="$(rustup which --toolchain nightly-2026-10-01 rustc)"
u10_bin="$(dirname "$u10_cargo")"
sudo unshare --net env PATH="$u10_bin:$PATH" RUSTC="$u10_rustc" CARGO_HOME="$u10_cargo_home" "$u10_cargo" test --locked --offline -p paludarium-harness --test diff_u10 -- --include-ignored --nocapture
```

（履歴：次の段落はその時点の記述。今の差分実行は `ci.yml` から呼ばれる `u10-native-diagnostic.yml` の differential で、27d05de1のCIで成功した。）検証済み：上記差分実行は x86_64 Linux 専用で、CI run 38010586387 の differential job 114090542018 と同じ手順です。固定guestを target/guests/u10 に用意し、実行時に fresh native oracle を生成して同じバイナリの C10 結果と比較します。任意の別guestディレクトリを使う場合だけ PALUDARIUM_U10_GUEST_DIR を指定します。外部CLIは使用しません。`--include-ignored` を外すと u10_differential は実行されず、子操作用テストだけ成功するため、差分成功の証拠にはできません。ビルドと依存取得は隔離前に完了させ、native と差分はネットワーク名前空間内で実行します。

## 履歴（Steps1〜18の計画時の手順）：Tests and Coverage（作成時の見出しは「Tests and Coverage」）

（この節の「行coverage80%以上をLinuxで維持する。U10内部部品の分母…」のうち、U10内部部品（Python core）の分母のcoverageは、27d05de1でU10のworkflowが消えてから測られていない。今も測られているのは `ci.yml` のworkspaceの行80%である。）

- ビルド証拠検査・結果比較・fixture/runner管理は各7件、計21件。正常例と少なくとも2種の異常/境界例を各部品に含める。
- probeの8項目、aube version/install/frozen/listを最低限すべて比較し、node不在・#1645・timeout・cleanupも検査する。Linux以外のプログラム合格は後続Unitに委ねる。
- 差分のnative期待値はCIごとに同一ビルドから生成。mockは内部の失敗/timeout/異常結果の単体検査だけに使い、nativeやemulatorの成功証拠の代わりにしない。
- fixtureは各runの専用一時領域へ置く。install→node_modules除去→frozen→listの状態遷移はnative/emulatorで一致させる。終了時の子孫回収とcleanupを確認する。
- 行coverage80%以上をLinuxで維持する。U10内部部品の分母とworkspaceの分母を明示し、既存Unitの証拠はソース一致が成立する範囲だけ再利用する。
- 各guest操作は30秒で停止・回収する。buildの時間上限はCI jobで別に設定し、guest timeoutをbuildへ流用しない。

## 履歴（Steps1〜18の計画時の手順）：Traceability（作成時の見出しは「Traceability」）

FR6.1〜FR6.4、FR7.1〜FR7.4、共通FR9.1/NFR1〜NFR4/NFR6〜NFR9を対象とする。story工程省略のためFRを使う。製品不一致があれば失敗を保存し、担当Unitの修正計画へ戻す。

## 履歴（Steps1〜18の計画時の手順）：Guest License Regression（作成時の見出しは「Guest License Regression」）

guest-license-change-proposal.mdの限定CDLA条件について、root設定全bytesの継承、webpki-root-certs@1.0.9だけの例外、別crate/別版の拒否、ライセンス全文とhashの保持、失敗時のsource-after記録を内部検査へ追加する。全4監査とroot製品監査を維持し、限定guest設定を製品ポリシーへ流用しない。

