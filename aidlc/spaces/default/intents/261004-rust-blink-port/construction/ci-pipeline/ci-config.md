# CI の構成

2026-10-18。fork `Marukome0743/paludarium` のブランチ `codex/build-and-test`（head e3c29d1d）の `.github/workflows/` を読んで書いた。人の回答は `ci-pipeline-questions.md`（Q1〜Q4 はすべて A、要約は Looks correct）。入力は、各 Unit の `construction/<unit>/code-generation/code-summary.md`（code-summary。各 Unit が作った workflow と、その正式な証拠の run。例：U15 の code-summary の「現在の状態（2026-10-18 JST、Step18）」は e3c29d1d の CI 7 run と公開の workflow を記録している）、`construction/build-and-test/build-and-test-summary.md`、`construction/build-and-test/test-results.md`。

## 方針

- 道具は GitHub Actions。手元の操作は Jujutsu（jj）で行う。trunk ベースで、短命なブランチから PR を作り、CI が通ってから `main` に squash マージする（team.md の Way of Working）。
- この段階では設計だけを書く（Q1 の A）。workflow の変更は、公開の前に製品をもう一度変えるとき（NFR7 の Safari の直しと、残している Minor）にまとめて行う。そのときに、正式な確認コマンドの入口の作り直しと CI 一式の再実行を 1 回で済ませる。この段階では push も CI の起動もしていない。
- 外部の action はすべて commit の SHA で固定する（今は外部の `uses:` 409 件がすべて固定済み）。workflow の既定の権限は `contents: read` で、要る job にだけ権限を足す（team.md の Deployment、project.md の Mandated）。

## いつ何が動くか（変更の後の形）

| きっかけ | workflow | 中身 | 合否の扱い |
|---|---|---|---|
| PR のたび（`pull_request`）と `main` への push | `ci.yml` | 23 job：lint（fmt・clippy `-D warnings`）、3OS の単体テスト、依存の検査（cargo deny）、x86-64 Linux の差分テスト、U10 の差分（fixture・native-first・differential）、wasm 4 環境の 14 ケース（Node・Chromium・Firefox・本物の Safari）、production wasm、行カバレッジ 80%、短いファジング 7 対象（`u11-fuzz.yml` を呼ぶ） | 必須チェック（Q4 の A）。1 つでも落ちたらマージしない |
| PR のたび | `release-check.yml` | 公開物の確認：版の一致、11 crate と npm tarball の package、隔離した consumer のビルド、import と実 Wasm の hello、U15 の Python 4 ファイルの行カバレッジ 80%。公開はしない | 必須チェック（Q4 の A） |
| 毎日（`schedule`）と手動 | `nightly.yml` | 作り直す（Q2 の A）：`u14-fuzz.yml`（13 対象×600 秒、ASan/LSan）と `u14-quality.yml`（3OS の全品質、wasm 4 環境、JIT あり・なしの一致、速さの判定）を呼ぶ。失敗したら Issue を作る（今と同じ `report-failure` の job、`issues: write` はこの job だけ） | マージは止めない。失敗は Issue にして直す（team.md の Testing Posture） |
| 手動（公開の前と、大きな変更の後） | `u12-quality.yml`・`u13-quality.yml`・`u14-quality.yml`・`u14-fuzz.yml`・`u1-u14-source-bound.yml` | macOS・Windows・全体の品質、ファジング、各 Unit の現行ソースの照合 | 公開の前に、公開する head で全部成功していること（`docs/release.md` の Owner hand-off の (5)） |
| 手動 | `u15-acceptance.yml` | 同じ head の公式 run から受け入れの証拠（`release-evidence.json`）を作る | 公開の前提 |
| 版の tag（`v*.*.*`） | `release.yml` | preflight → 同じ head の品質の確認 → package → 保護された `release` environment での人の承認 → crate を依存の順に公開 → npm 公開 → 公開後の照合 | 人の承認が要る。公開は tag からだけ |

速さの判定（FR8.3）は PR のゲートにしない（team.md の Testing Posture）。夜間と公開の前の確認で、1 回だけ測る（合格を待つ測り直しはしない）。

## 残す workflow と消す workflow（Q3 の A）

残す（20）：上の表の 10 個（`ci.yml`・`release-check.yml`・`nightly.yml`・`u12-quality.yml`・`u13-quality.yml`・`u14-quality.yml`・`u14-fuzz.yml`・`u1-u14-source-bound.yml`・`u15-acceptance.yml`・`release.yml`）と、それらが `workflow_call` で呼ぶ 10 個（`u10-native-diagnostic.yml`・`u11-acceptance.yml`・`u11-fuzz.yml`・`u12-fuzz.yml`・`u12-native-first.yml`・`u13-native-first.yml`・`u13-wasm-acceptance.yml`・`u14-native-diagnostic.yml`・`u14-native-first.yml`・`u14-wasm-acceptance.yml`）。

消す（21）：各 Unit の作業中に使った診断・確かめの workflow。`native-diagnostic.yml`、`u1-frame-diagnostic.yml`、`u1-source-bound-verification.yml`、`u2-production-sanitizers.yml`、`u3-current-verification.yml`、`u5-current-verification.yml`、`u5-native-diagnostic.yml`、`u5-quality.yml`、`u6-current-verification.yml`、`u6-native-diagnostic.yml`、`u6-quality.yml`、`u8-current-verification.yml`、`u8-native-diagnostic.yml`、`u9-current-verification.yml`、`u10-current-verification.yml`、`u11-browser-readiness.yml`、`u11-current-verification.yml`、`u11-firefox-diagnostic.yml`、`u11-native-first.yml`、`u11-native-metadata.yml`、`u14-cost-diagnostic.yml`。これらの run の記録と保存した原本は、各 Unit の `verification/` に残っている。

あわせて、残す workflow の `push` の条件から古い作業ブランチ（`codex/u12-macos-host`・`codex/u13-windows-host`・`codex/u14-jit-wasm`・`codex/native-x86-diagnostic` など）を外す。`ci.yml` の `push` は `main` だけにする。

注意：workflow を消す・変えると、新しい head では正式な確認コマンド（`entry-c.py`）がその差を「変わったファイル」として確かめる。そのため、新しい binding に変わったファイルの一覧を書き、採用を受けてから使う（下の「正式な確認コマンドとの関係」）。旧い入口 v1〜v4 の層の固定は、もう効かない（履歴）。

## 作り直す `nightly.yml` の形（設計）

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

- `u14-quality.yml` と `u14-fuzz.yml` に `workflow_call` の起動を足す（`u14-fuzz.yml` にはすでにある）。
- 呼ばれる側の権限は呼ぶ側の `contents: read` を超えない。速さの判定の artifact（`u11-node` の `performance/observations.json`）は、今と同じく run に残る。
- 今の `nightly.yml` の `wasm-threads-linux`・`wasm-threads-safari` は、`u14-quality.yml` の wasm 4 環境の確認に含まれるので外す。musl の target で全対象が失敗していた `fuzz` の job（run 38967100569）もこれで置き換わる。

## 成果物の置き場所

- crates.io：11 crate（types・decoder・mmu・host・vfs・loader・cpu・jit・kernel・runtime・paludarium）、版 0.1.0。harness・fuzz・Rust の Wasm adapter は公開しない。
- npm：`@paludarium/wasm`、版 0.1.0。provenance を付ける。
- 認証：最初の公開だけ、人が `release` environment の secret に置く対象と期限を絞ったトークンを使う。2 回目からは Trusted Publishing（OIDC）だけを使う（`docs/release.md`）。
- CI の artifact：各 run の artifact（カバレッジの lcov、差分の結果、速さの原本、公開物）は GitHub Actions に残る。正式な証拠に使ったものは、各 Unit と Build and Test の `verification/` に保存している。

## 正式な確認コマンドとの関係（2026-10-18 追記）

- 今の正式な確認コマンドは U15 の新しい入口 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py` である（人が 2026-10-18 に採用。`verification-command.txt`）。
- 入口は、必須の 7 workflow（`CI`・`Release package checks`・`U12 current full quality`・`U13 current full quality`・`U14 current full quality`・`U14 fresh thirteen target ASan and LSan`・`U1 U14 current-source evidence`）を入口の中に固定している。binding ではこの 7 つを減らせない。
- Q3 の A で残す workflow には、この 7 つがすべて入っている。そのため、作業用の workflow の整理はこのままできる。この 7 つのどれかを消す、または名前を変えるときは、入口の新しい版を作って人の採用を受ける。
- 次の製品の変更で workflow を変えたときは、新しい head の CI 一式の記録から新しい binding を作り、採用を伺う。

## 人が行う設定

- upstream の `main` のブランチの保護：必須チェックを `quality-gates.md` の表のとおりに設定し、管理者の迂回を禁止する。
- upstream の `release` environment：必須レビュアー 1 人以上、管理者の迂回の禁止（自分のレビューの禁止は任意、U15 の Q3）。
- 名前の所有、初回のトークン、Trusted Publisher の登録、tag：`docs/release.md` の Owner hand-off のとおり。
