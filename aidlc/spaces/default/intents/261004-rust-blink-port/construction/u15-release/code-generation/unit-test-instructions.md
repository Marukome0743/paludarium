# U15 限定検証手順

## 今回：Step19〜21（e3c29d1dを起点にした新しい入口）

Runnerは標準のunittestを使う（新しいPython依存は入れない）。入口は検証の道具なので、実装の後に回帰を書いて実行する（test-after）。commandはすべて `verification/entry-e3c29d1d/` の中のファイルに限る。製品のファイルは変えない。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d -p 'test_*.py' -v
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry.py --entry-sha256 <entry.py の SHA-256> --binding-sha256 <binding-e01.json の SHA-256>
```

期待する結果：
- 回帰はすべて成功し、skip は 0 件。
- 本番の実行は exit 0 で、新しい `run-<ns>-<pid>/result.json` ができる。
- 結果の `excluded` に、除外の一覧に当たったファイル（`mise.toml`、`tools/aidlc-recovery/` の 2 ファイル、`target/`・`__pycache__/` の下など）が書かれる。
- 結果の `changed_paths` は空になる。

拒否されたときは、`refusal.json` を残して止まり、理由を人に伝える。除外の一覧は勝手に広げない。

Step21 で採用されるまでは、今の正式な確認コマンド（入口 v4）が有効なまま。このあいだ、v1〜v4 の入口・binding・回帰の bytes は変えない。

## 実施済み：Step17〜18（R-16〜R-18と残しているMinorの直し）

Runnerは既存のunittestをそのまま使う。Step17は実装の後に試験を書いて実行する（test-after）。commandはすべてU15の `tests/release` とU15の部品に限る。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest tests.release.test_check tests.release.test_api tests.release.test_publish_adapter tests.release.test_policy -v
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest discover -s tests/release -p 'test_*.py' -v
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode validate
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode package-check
```

期待する結果：最初の公開の再開は、すでにある版がすべて承認済みのdigestと一致するときだけ残りを公開し、1つでも違えば拒否する。申告なしでは拒否する。cargoの子プロセスに `GH_TOKEN` と `ACTIONS_ID_TOKEN_REQUEST_*` が渡らない。npmの子プロセスには要る変数だけが渡る。tests/release全件は前の127件を減らさない。coverageは下の「Step14b」の方法（validate・package-checkを `--append`）で4ファイル各80%以上。

Step18のpush・CI・入口の更新は、計画のとおり人の承認を受けてから行う。

### Step17の実行結果（2026-10-18、手元、Python 3.15.0・coverage 7.16.2）

- 変更前のtests/release全件（2行目と同じ形）：127件成功（ベースライン）。
- 1行目：exit 1。68件を実行し、`test_api` と `test_publish_adapter` の2つのmoduleが読み込みで失敗した（`ModuleNotFoundError: No module named 'test_policy'`／`'test_package'`）。この2つは `from test_policy import …`・`from test_package import …` で同じフォルダの試験を読むので、`tests/release` を起点にする2行目の `discover` の形でだけ読み込める。読み込みの行はStep17で変えていない。この2つのmoduleの試験は2行目で全件実行した。
- 2行目：146件成功、exit 0（127件に19件を足した。減らした試験・skipはない）。
- 3行目（validate）：exit 0（`validated: true`、`version: 0.1.0`、`crates: 11`、`publish_eligible: false`）。
- 4行目（package-check）：exit 0。coverageの `--append` の実行（2回目）で結果を読んだ：`passed: true`、`local_snapshot: true`、11 crate、npm tarball 0.1.0、7ケース、`stable_supported: false`、`published: false`。
- coverage（下の「Step14b」の方法：unittestの後にvalidateとpackage-checkを `coverage run --append`）：acceptance.py 99.64%、check.py 96.85%、package.py 98.33%、policy.py 100%。`coverage report --fail-under=80` はexit 0、JSONで4ファイルすべての存在と各80%以上を確かめた（exit 0）。
- 実行していないもの：Step18（push・CI・入口の更新）、正式確認コマンド（v3は、Step17で変えた7ファイルをa54315f9のbytesに固定しているので止まると見込まれる。入口の更新はStep18）、本物のregistry・OIDC・初回トークンでの公開と再開。

## 実施済み：Step13〜16（Loop-back 2：版0.1.0と公開の準備）

Runnerは既存のunittest（下の「Runnerの準備」）をそのまま使う。Step13とStep14は実装の後に試験を書いて実行する（test-after。ゲストの命令・syscallの単位ではないため）。commandはすべてU15の `tests/release` とU15の部品に限る。

Step13（版の一致、単体2件を `tests/release/test_policy.py` に追加）とStep14（`tests/release/test_acceptance.py` の単体8件以上と統合2件）：

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest tests.release.test_policy tests.release.test_acceptance -v
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest discover -s tests/release -p 'test_*.py' -v
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode validate
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode package-check
```

1行目はこの2つのファイルだけ、2行目はtests/releaseの全件（既存の件数を減らさない）。package-checkは版0.1.0の11 crateとnpm tarballで、隔離consumerのビルドとimport・実Wasmのhelloが通ること。

coverage（固定集合に `acceptance.py` を足す。既存3部品の80%は変えない）：

```sh
.venv-u15/bin/python -B -m coverage run --data-file=target/u15/python.coverage --include='*/scripts/release/policy.py,*/scripts/release/package.py,*/scripts/release/check.py,*/scripts/release/acceptance.py' -m unittest discover -s tests/release -p 'test_*.py'
.venv-u15/bin/python -B -m coverage json --data-file=target/u15/python.coverage -o target/u15/python-coverage.json
.venv-u15/bin/python -B -m coverage report --data-file=target/u15/python.coverage --fail-under=80
```

JSONで4ファイル全部の存在と各80%以上を確かめる。

版の書き換えの確認（Step13）：

```sh
git diff -U0 -- Cargo.lock fuzz/Cargo.lock
env PATH="$HOME/.cargo/bin:$PATH" cargo build --workspace --locked
env PATH="$HOME/.cargo/bin:$PATH" cargo fmt --all --check
env PATH="$HOME/.cargo/bin:$PATH" cargo clippy --locked --workspace --all-targets -- -D warnings
```

期待する結果：lockの差はworkspaceのcrateの `version = "0.0.0"` → `"0.1.0"` の行だけ。ビルド・fmt・clippyは終了コード0。

Step14b（人の判断への対応）：実装の後に、上の1〜2行目のunittest（`tests.release.test_policy`・`tests.release.test_acceptance` に、`tests.release.test_check` と `tests.release.test_publish_adapter` を足す）、tests/release全件、validate、package-check、coverage（4ファイル各80%以上）を実行する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest tests.release.test_policy tests.release.test_acceptance tests.release.test_check tests.release.test_publish_adapter -v
```

期待する結果：自分のレビューの禁止がなくても、必須レビュアーと管理者の迂回の禁止がそろえば通り、どちらかが欠ければ拒否される。最初の公開は、申告ありで未公開のときだけ通り、トークンの値は出力・文書に現れない。

coverageの注意：上の3行のcoverageはunittestだけを測る。release-check.ymlのCIと同じく、validateとpackage-checkを `coverage run --append` で足して測る（package.pyはpackage-checkを含めて初めて測れる）。下限は下げない。

Step15のCI（push・起動の前に人の承認を受ける）と、Step16の人の手順は、計画のとおり。実公開・OIDCの交換・初回の名前の登録はmockでは証明できないので、それまでFR10.1・NFR8はGAPのまま。

## 実施済み：Step12（Step11の再レビューのMinorへの対応）

新しいテスト・CI・測定・公開はない。code-summary.mdとtraceability.jsonを直した後、Step11と同じ2件のsensorを実行する。期待する結果：required-sectionsはpass、traceabilityは既存のFR10.1・NFR8のGAPだけで `pass: false`（statusとtargetは変えていない）。checkpointでは今の正式確認コマンドがexit 0になる。

## 実施済み：Step11（Loop-back 1：変更がないことの再確認と、現在の状態の更新）

新しいテスト・CI・測定・公開はない。project rootで、U15のsource-manifestの全ファイルがe4f84768から変わっていないことを確かめる（読み取りだけ）。

```sh
git diff --stat e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/source-manifest.json'))['writes']))")
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/traceability.json
```

期待する結果：git diffの出力は空。required-sectionsはpass。traceabilityは、実公開まで既存のFR10.1・NFR8のGAPで `pass: false`（gapsがこの2件だけで、ほかのfindingsがないこと）。（Step12で、この行の「sensorは2件ともpass」を実際の結果に合わせて直した。）code-summary.mdで「現行」「現在」で始まる見出しは新しい「現在の状態（2026-10-18 JST、Loop-back 1）」節だけであることを読んで確かめる。checkpointでは今の正式確認コマンド（U14の `u14_candidate_v2.py`、`--entry-sha256 934f21bc…`・`--binding-sha256 425ae3e7…` 付き）がexit 0になる。

## 実施済み：Step10（N1・N2への対応）

新しい試験・CI・push・測定・ネットワークはない。U15 verificationに置く読み取り専用の照合スクリプトを1回だけ実行する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/step10_evidence_check.py
```

結果は `verification/step10-evidence-check.json` に排他作成で保存する。そのあと正式sensor 2件と、採用済みの正式検証コマンドでのcheckpoint検証で確認する。

## 実施済み：Step9（レビュー指摘への対応）

新しい試験・CI・push・測定はない。記録の整理と補足だけを行う。GitHubの応答の保存は次の読み取りだけとする。

```sh
gh api repos/Marukome0743/paludarium/commits/ce0b746497c662b2404a1f80153d53390d400e9d
gh api repos/Marukome0743/paludarium/compare/be45b36ce9d7a65719ba1f86cf6a0b018070741b...ce0b746497c662b2404a1f80153d53390d400e9d
```

確認は正式sensor 2件（traceability・required-sections）と、採用済みの正式検証コマンドでのcheckpoint検証で行う。

## 実施済み：Step7補足 7a'（workflow修正とmacOS証拠）

`verification/u12-workflow-fix-proposal.md` のとおり2ファイルを用意し、be45b36cを親にした1 commitとして署名pushする（外部送信1回）。

```sh
jj git push --remote origin --bookmark codex/u15-macos-native
```

送信後に `gh api repos/Marukome0743/paludarium/commits/<head>` でverified、`gh api repos/Marukome0743/paludarium/compare/be45b36ce9d7a65719ba1f86cf6a0b018070741b...<head>` で変更ファイルが2つだけであることを確かめる。push で起動した `U15 native macOS evidence` runの完了後、原本を読み取り専用で保存してZIPのdigestを照合する。失敗は原本を保存して止まり、再試行しない。

## 実施済み：Step7補足（7a ネイティブmacOS、7b FR8.3）

7a：起動直前に `gh api repos/Marukome0743/paludarium/branches/codex/u14-jit-wasm --jq .commit.sha` がbe45b36ce9d7a65719ba1f86cf6a0b018070741bであることを確かめ、次の1回だけ起動する。

```sh
gh workflow run u12-quality.yml --repo Marukome0743/paludarium --ref codex/u14-jit-wasm
```

完了後、run・jobs・各jobログ・artifactを読み取り専用で `verification/u12-quality-<run id>/` に保存し、ZIPのSHA-256を公式digestと照合する。macOS hostの結果とnative Linuxの期待値の比較は、読み取り専用の照合スクリプトで行う。失敗は原本として保存し、再試行しない。

7b：新しい測定はしない。U15 verificationに読み取り専用の照合スクリプトを置き、`/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B <script>` で1回実行する。runnerが読む入力の旧測定とbe45での一致を確かめ、結果JSONを排他作成で保存する。

## 対象と状態

以下の手順は実施済み。結果と、実施しなかったもの（実公開など）は code-summary.md の「現在の状態（2026-10-18 JST、Loop-back 1）」と、その時点の記録の「履歴：現在の状態（2026-10-17）」を参照する。対象はscripts/releaseの3部品、2つのrelease workflowと配布metadata。既存U14の正式証拠・失敗・承認は保持する。

## Runnerの準備

実装前にPython実体を確認し、以下でunittestが起動することを確認する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest --help
```

この後、tests/releaseの最小runner/configを用意してから各部品の実装とtest-afterへ進む。新Python3部品の正常/境界/異常を各8件、計24件以上、外部command境界の統合4件を用意する。commandは全て当Unitに限定する。

## 単体・統合command

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest discover -s tests/release -p 'test_*.py' -v
```

実装後の統合入口：

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode validate
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode package-check
```

validateはpolicy/metadata/workflow構成、package-checkは隔離copy内のCargo package/consumer build/npm pack/展開後importと実Wasm helloを検査する。これらのmodeはpublishとtag送信をしない。実装前には入口が存在しないので、先にrunner準備を完了する。

## Coverage

実装開始時に最新対応版を確認したcoverage.pyをproject内環境へ導入し、版を固定して実行する。既存環境のものを無条件で更新しない。環境のPython実体で次を実行する（作成先はproject内 .venv-u15、CIも同じ固定版）。

```sh
.venv-u15/bin/python -B -m coverage run --data-file=target/u15/python.coverage --include='*/scripts/release/policy.py,*/scripts/release/package.py,*/scripts/release/check.py' -m unittest discover -s tests/release -p 'test_*.py'
.venv-u15/bin/python -B -m coverage json --data-file=target/u15/python.coverage -o target/u15/python-coverage.json
.venv-u15/bin/python -B -m coverage report --data-file=target/u15/python.coverage --fail-under=80
```

JSONで3ファイル全部の存在と各80%以上を追加確認する。総合80%だけで片側不足を隠さず、pragmasやファイル除外で下限を下げない。共通Rust/JS/workspace/U9の既存下限は変更しない。

## データ・mock・原本

正常fixtureは実manifestとschemaから作り、異常は一項目ずつ変更する。policyのrepo/head/tag/quality responses、tarball/crate、process resultを型とschemaへ照合する。mockはネットワーク/uploadを記録するadapter境界だけで使う。mockの成功を実OIDCやregistry公開の成功と呼ばない。package-checkは本物のCargo/npmと生成配布物を使い、全member bytes/digestと実tool実体を保持する。

子processにはtimeout/kill/reapを設け、stdout/stderr/実exitと失敗時原本を排他的出力へ保存する。各runの出力pathをresultへ記載し、source/lock前後同一を確認する。秘密値をenvironment dumpへ記録しない。

## CIと公開の区別

release-check workflowのCIは同head/sourceを拘束する。元の署名CIとclosure一致が確認できる不変対象だけ再利用する。ゲスト期待値が必要な新規CIは同runのx86-64 Linuxで取得する。

未検証の初回registry登録・Trusted Publisher・environment保護・正式version・stable利用可否は計画Step1/5/6で具体化する。実公開は別の明示承認後にrelease workflowで行い、公開後registryから得たversion/digest/provenanceまで確認する。それまでは実公開E2EとFR10.1を未検証として保持する。

