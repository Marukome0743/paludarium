# CI の構成

2026-10-19 に、fork `Marukome0743/paludarium` のブランチ `codex/build-and-test`（head 27d05de1）の `.github/workflows/` を読み、入れた後の今の形に書き直した（最初の設計は 2026-10-18、head e3c29d1d で書いた）。人の回答は `ci-pipeline-questions.md`（Q1〜Q5 はすべて A、要約は Looks correct。2026-10-19 に確認し直した）。入力は、各 Unit の `construction/<unit>/code-generation/code-summary.md`（code-summary。各 Unit が作った workflow と、その正式な証拠の run。例：U15 の code-summary の先頭の「現在の状態」節は 27d05de1 の CI 8 run と Safari の 10 回の確認、CI の整理（Step23）を記録している）、`construction/build-and-test/build-and-test-summary.md`、`construction/build-and-test/test-results.md`。

## 方針

- 道具は GitHub Actions。手元の操作は Jujutsu（jj）で行う。trunk ベースで、短命なブランチから PR を作り、CI が通ってから `main` に squash マージする（team.md の Way of Working）。
- 最初はこの段階で設計だけを書いた（Q1 の A）。workflow の変更は、公開の前の製品の変更（U15 の Step22〜28、8360be2e・27d05de1）でまとめて入れ、27d05de1 で CI 一式 8 run と Safari の 10 回の確認がすべて成功し、新しい head の binding を作って正式な確認コマンドを採用した。この段階では、2026-10-19 の書き直しでも push も CI の起動もしていない。
- 入れた後に見つかった食い違い（下の「入れた後の食い違い」）は、Q5 の A のとおり、次の製品の変更でまとめて直す。
- 外部の action はすべて commit の SHA で固定する（27d05de1 で外部の `uses:` 217 件がすべて固定済み。ほかにリポジトリ内の workflow の呼び出しが 18 件）。workflow の既定の権限は `contents: read` で、要る job にだけ権限を足す（team.md の Deployment、project.md の Mandated）。

## いつ何が動くか（27d05de1 の今の形）

| きっかけ | workflow | 中身 | 合否の扱い |
|---|---|---|---|
| PR のたび（`pull_request`）と `main` への push | `ci.yml` | 23 job：lint（fmt・clippy `-D warnings`）、3OS の単体テスト、依存の検査（cargo deny）、x86-64 Linux の差分テスト、U10 の差分（fixture・native-first・differential）、wasm 4 環境の 14 ケース（Node・Chromium・Firefox・本物の Safari）、production wasm、行カバレッジ 80%、短いファジング 7 対象（`u11-fuzz.yml` を呼ぶ） | 必須チェック（Q4 の A）。1 つでも落ちたらマージしない |
| PR のたび | `release-check.yml` | 公開物の確認：版の一致、11 crate と npm tarball の package、隔離した consumer のビルド、import と実 Wasm の hello、U15 の Python 4 ファイルの行カバレッジ 80%。公開はしない | 必須チェック（Q4 の A） |
| 毎日（`schedule`）と手動 | `nightly.yml` | 作り直した（Q2 の A、8360be2e）：`u14-fuzz.yml`（13 対象×600 秒、ASan/LSan）と `u14-quality.yml`（3OS の全品質、wasm 4 環境、JIT あり・なしの一致、速さの判定）を呼ぶ。失敗したら Issue を作る（今と同じ `report-failure` の job、`issues: write` はこの job だけ） | マージは止めない。失敗は Issue にして直す（team.md の Testing Posture） |
| 手動（公開の前と、大きな変更の後） | `u12-quality.yml`・`u13-quality.yml`・`u14-quality.yml`・`u14-fuzz.yml`・`u1-u14-source-bound.yml` | macOS・Windows・全体の品質、ファジング、各 Unit の現行ソースの照合 | 公開の前に、公開する head で全部成功していること（`docs/release.md` の Owner hand-off の (5)） |
| 手動（と、`codex/build-and-test` へのそのファイルの push） | `u11-safari-stability.yml` | まっさらな macOS の runner で本物の Safari の差分の試験を 10 回動かし、落ちた回数とやり直した回数を数える（NFR7 の直しの効き目の確認） | 大きな Safari の変更の後に 1 回。27d05de1 の run 39143558642 で 10 回とも成功、やり直し 0 回 |
| 手動 | `u15-acceptance.yml` | 同じ head の公式 run から受け入れの証拠（`release-evidence.json`）を作る | 公開の前提 |
| 版の tag（`v*.*.*`） | `release.yml` | preflight → 同じ head の品質の確認 → package → 保護された `release` environment での人の承認 → crate を依存の順に公開 → npm 公開 → 公開後の照合 | 人の承認が要る。公開は tag からだけ |

速さの判定（FR8.3）は PR のゲートにしない（team.md の Testing Posture）。夜間と公開の前の確認で、1 回だけ測る（合格を待つ測り直しはしない）。

## 残す workflow と消した workflow（Q3 の A、8360be2e で入れた）

今の `.github/workflows/` は 21 ファイル：最初の設計で残すとした 20 個と、NFR7 の確認のために足した `u11-safari-stability.yml`（下の「入れた後の食い違い」の 2）。

残す（20、最初の設計）：上の表の 10 個（`ci.yml`・`release-check.yml`・`nightly.yml`・`u12-quality.yml`・`u13-quality.yml`・`u14-quality.yml`・`u14-fuzz.yml`・`u1-u14-source-bound.yml`・`u15-acceptance.yml`・`release.yml`）と、それらが `workflow_call` で呼ぶ 10 個（`u10-native-diagnostic.yml`・`u11-acceptance.yml`・`u11-fuzz.yml`・`u12-fuzz.yml`・`u12-native-first.yml`・`u13-native-first.yml`・`u13-wasm-acceptance.yml`・`u14-native-diagnostic.yml`・`u14-native-first.yml`・`u14-wasm-acceptance.yml`）。

消した（21、8360be2e）：各 Unit の作業中に使った診断・確かめの workflow。消したことは U15 の `source-manifest.json` が受け持つ（U15 の Step30）。`native-diagnostic.yml`、`u1-frame-diagnostic.yml`、`u1-source-bound-verification.yml`、`u2-production-sanitizers.yml`、`u3-current-verification.yml`、`u5-current-verification.yml`、`u5-native-diagnostic.yml`、`u5-quality.yml`、`u6-current-verification.yml`、`u6-native-diagnostic.yml`、`u6-quality.yml`、`u8-current-verification.yml`、`u8-native-diagnostic.yml`、`u9-current-verification.yml`、`u10-current-verification.yml`、`u11-browser-readiness.yml`、`u11-current-verification.yml`、`u11-firefox-diagnostic.yml`、`u11-native-first.yml`、`u11-native-metadata.yml`、`u14-cost-diagnostic.yml`。これらの run の記録と保存した原本は、各 Unit の `verification/` に残っている。

あわせて、残す workflow の `push` の条件から古い作業ブランチ（`codex/u12-macos-host`・`codex/u13-windows-host`・`codex/u14-jit-wasm`・`codex/native-x86-diagnostic` など）を外した。`ci.yml` の `push` は `main` だけにした（`pull_request` は残る）。

注意：workflow を消す・変えると、新しい head では正式な確認コマンドがその差を「変わったファイル」として確かめる。そのため、8360be2e・27d05de1 の変更は新しい binding（binding-e06f）に変わったファイルの一覧として書き、人の採用を受けた（下の「正式な確認コマンドとの関係」）。旧い入口 v1〜v4 の層の固定は、もう効かない（履歴）。

## `nightly.yml` の形（設計どおりに 8360be2e で入れた）

```yaml
name: Nightly
on:
  schedule:
    - cron: "17 18 * * *"
  workflow_dispatch:
permissions:
  contents: read
jobs:
  fuzz:
    uses: ./.github/workflows/u14-fuzz.yml        # 13 対象×600 秒、ASan/LSan
  quality:
    uses: ./.github/workflows/u14-quality.yml     # 3OS、wasm 4 環境、速さの判定
  report-failure:
    needs: [fuzz, quality]
    if: failure()
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Open an Issue
        env:
          GH_TOKEN: ${{ github.token }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          gh issue create --repo "$GITHUB_REPOSITORY" \
            --title "Nightly checks failed ($(date -u +%Y-%m-%d))" \
            --body "The nightly fuzzing or quality check failed: $RUN_URL"
```

- `u14-quality.yml` に `workflow_call` の起動を足した（`u14-fuzz.yml` にはもとからある）。入れた `nightly.yml` には、この設計に加えて `report-failure` の job に `timeout-minutes: 10` がある。
- 呼ばれる側の権限は呼ぶ側の `contents: read` を超えない。速さの判定の artifact（`u11-node` の `performance/observations.json`）は、今と同じく run に残る。
- 前の `nightly.yml` の `wasm-threads-linux`・`wasm-threads-safari` は、`u14-quality.yml` の wasm 4 環境の確認に含まれるので外した。musl の target で全対象が失敗していた `fuzz` の job（run 38967100569）もこれで置き換わった。新しい `nightly.yml` の定期の実行はまだ起きていない（fork の既定のブランチは `main` で、この変更はまだ `codex/build-and-test` にある）。

## 入れた後の食い違い（Q5 の A：次の製品の変更でまとめて直す）

1. 夜間の fuzz が 2 回走る：`nightly.yml` の `fuzz` の job が `u14-fuzz.yml` を呼び、`quality` の job が呼ぶ `u14-quality.yml` の中の `u13-fuzz` の job も同じ `u14-fuzz.yml` を呼ぶ。直すときは、`nightly.yml` の `fuzz` の job を外すか、`u14-quality.yml` の `u13-fuzz` を呼び出しの入力で外せるようにする。`report-failure` の `needs` も合わせて直す。
2. `u11-safari-stability.yml` が上の「残す（20）」の一覧になく、作業ブランチ `codex/build-and-test` へのそのファイルの push の起動条件を持つ（GitHub の手動起動が fork の既定のブランチにある workflow しか起動できなかったため、人の判断で足した）。直すときは、残す一覧に足し、push の起動条件を外すか `main` に替える。
3. どちらも `construction/u15-release/code-generation/verification/version-allowance/pending-minor-fixes.md` に記録している。

## 成果物の置き場所

- crates.io：11 crate（types・decoder・mmu・host・vfs・loader・cpu・jit・kernel・runtime・paludarium）、版 0.1.0。harness・fuzz・Rust の Wasm adapter は公開しない。
- npm：`@paludarium/wasm`、版 0.1.0。provenance を付ける。
- 認証：最初の公開だけ、人が `release` environment の secret に置く対象と期限を絞ったトークンを使う。2 回目からは Trusted Publishing（OIDC）だけを使う（`docs/release.md`）。
- CI の artifact：各 run の artifact（カバレッジの lcov、差分の結果、速さの原本、公開物）は GitHub Actions に残る。正式な証拠に使ったものは、各 Unit と Build and Test の `verification/` に保存している。

## 正式な確認コマンドとの関係（2026-10-18 追記、2026-10-19 更新）

- 今の正式な確認コマンドは U15 の入口の版 f `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が 2026-10-19 に採用。intent 直下の `verification-command.txt` の 1 行目）である。2026-10-18 に採用した `entry-c.py`（版 c）は履歴。
- 入口は、必須の 7 workflow（`CI`・`Release package checks`・`U12 current full quality`・`U13 current full quality`・`U14 current full quality`・`U14 fresh thirteen target ASan and LSan`・`U1 U14 current-source evidence`）を入口の中に固定している。binding ではこの 7 つを減らせない。
- Q3 の A で残す workflow には、この 7 つがすべて入っている。そのため、作業用の workflow の整理はこのままできる。この 7 つのどれかを消す、または名前を変えるときは、入口の新しい版を作って人の採用を受ける。
- binding-e06f は、この 7 つに加えて `U11 Safari stability`（run 39143558642）の 12 job を、人の判断の原文を付けた集合として入れている。
- 次の製品の変更で workflow を変えたときは、新しい head の CI 一式の記録から新しい binding を作り、採用を伺う。

## 人が行う設定

- upstream の `main` のブランチの保護：必須チェックを `quality-gates.md` の表のとおりに設定し、管理者の迂回を禁止する。
- upstream の `release` environment：必須レビュアー 1 人以上、管理者の迂回の禁止（自分のレビューの禁止は任意、U15 の Q3）。
- 名前の所有、初回のトークン、Trusted Publisher の登録、tag：`docs/release.md` の Owner hand-off のとおり。
