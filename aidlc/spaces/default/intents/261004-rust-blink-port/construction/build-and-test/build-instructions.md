# ビルド手順（Build and Test）

この手順は、15 Unit の Code Generation の成果（各 Unit の `code-generation-plan.md`・`unit-test-instructions.md`・`code-summary.md`）をまとめて、今のソース全体を 1 回ビルドして確かめるためのものです。人の回答（`build-and-test-questions.md`）に従い、正式な証拠はフォーク（`Marukome0743/paludarium`、origin）の CI で取り、この Mac では補助の確認を行います。

## 前提

- 版の固定：Rust は `rust-toolchain.toml` の nightly（nightly-2026-10-11）、依存は `Cargo.lock`（`--locked`）。Q5 の回答により、今回は今の固定の版のまま測り、使った版を記録する（下の「道具の版」）。
- この Mac の道具：`cargo` は `~/.cargo/bin/cargo`（mbx の shim は無効なので PATH の先頭に `~/.cargo/bin` を置く）。Node は `~/.local/share/mise/installs/node/26.12.0/bin/node`、actionlint は `~/.local/share/mise/installs/actionlint/1.7.12/actionlint`、shellcheck は `~/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck`。
- JIT の実 Wasm 試験は Node の実体が必要：`PALUDARIUM_TEST_NODE=<node の絶対パス>`。設定しないと `paludarium-jit` の `bridge::tests` 9 件が失敗する（この Mac で確認済み）。CI では各 workflow の env に `PALUDARIUM_TEST_NODE: node` を持つ。
- native x86-64 Linux・Windows・本物の Safari・600 秒のファジングはこの Mac では正式に測れない（Docker は QEMU のため native Linux の証拠にしない）。

## 道具の版（Q2 を Q5 で見直し：今の版で測り、更新は後の別作業）

今回の Build and Test は今の固定の版で測り、CI の各 job で実際に使った版（`rustc -Vv`、`node --version` など）を記録する。最新への更新は、正式な確認コマンド（`final_candidate.py`）が U14 の workflow をバイト単位で固定しているため、新しい正式な確認コマンドとあわせて後で別の作業として行う。2026-10-17 時点で確認した最新と今の固定（更新の作業のための記録）：

| 道具 | 今の固定 | 最新 | 置き場所 |
|---|---|---|---|
| Rust nightly | nightly-2026-10-11（`rust-toolchain.toml` と workflow 48 か所）、nightly-2026-10-10（workflow など 85 か所、履歴の診断を含む） | nightly-2026-10-17 | `rust-toolchain.toml`、`.github/workflows/*.yml`、`scripts/*` |
| Node（CI） | '24'（4 か所）、'26.11.1'（7 か所）、'26.12.0'（13 か所） | 26.12.0 | `.github/workflows/*.yml` |
| Playwright | 1.64.0 | 1.64.1（U11 の記録） | `packages/*`、`spikes/*` の package 定義と lock |

後の更新の作業では、`rust-toolchain.toml` を正本とし、workflow の明示の版をそろえる。固定は 38 ファイルにあり、U7 以外の 14 Unit の担当ソースにまたがるので、Code Generation に戻して再レビューと承認を受ける。履歴の診断 workflow は、変えると記録と食い違うので、変えるかどうかを一覧にしてから決める。上げた結果ビルドや試験が壊れた場合は、そこで止めて人に相談する。

## ビルド

この Mac（補助）：

```sh
env PATH="$HOME/.cargo/bin:$PATH" cargo build --workspace --locked
env PATH="$HOME/.cargo/bin:$PATH" cargo build --locked -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu --target wasm32-unknown-unknown
bash scripts/build-wasm.sh
```

CI（正式）：`.github/workflows/ci.yml` の各 job が `rust-toolchain.toml` の版でビルドする（3OS の `test`、`lint`、`production-wasm`、`differential`、`coverage`、呼び出す `u11-acceptance.yml`・`u11-fuzz.yml`・`u10-native-diagnostic.yml`）。

## ビルドの確認

- `cargo build --workspace --locked` が終了コード 0（この Mac で 2026-10-17 に確認：1.21 秒、0 エラー。マニフェストの `license` と `license-file` の重複について警告 3 件あり）。
- wasm32 向けの decoder・mmu・cpu のビルドが通る（CI の `lint` job）。
- `scripts/build-wasm.sh` が production の `packages/paludarium-wasm/paludarium.wasm` を作る（CI の `production-wasm` job）。

## CI での実行（Q1：フォークで CI 一式）

1. 今の作業コピー（コミットしていない変更を含む）を jj でコミットする。大きすぎて取り込めない検証用の原本（1 MiB を超えるファイル）はコミットに含めない。
2. フォークの新しいブランチ用の bookmark を作り、`jj git push --remote origin --bookmark <branch>` で署名付きで送る。**push と CI の起動の前に、人の承認を得る**（人の指示）。
3. 送った head で次を実行する（どれも必須）：`ci.yml`（PR ゲート一式）、`u14-quality.yml`（JIT・U9 を含む全品質）、`u1-u14-source-bound.yml`、`u12-quality.yml`（macOS の `macos-host`）、`u13-quality.yml`（Windows）、`u14-wasm-acceptance.yml`（4 環境）、`u14-fuzz.yml`（13 対象×600 秒、Q3）、`release-check.yml`、`u11-safari-stability.yml`（Safari の 10 回、NFR7）。速さの判定（FR8.3、Q3）は `u14-quality.yml` の Node の job（「Frozen paired full-probe performance」）で 1 回だけ行う。（2026-10-19 注記：以前は `u14-cost-diagnostic.yml` の手順と書いていたが、このworkflowは U15 の Step23（8360be2e）で消えた。27d05de1 の判定は `u14-quality.yml` の run 39149187727 で測った）
4. 失敗したら原本（run・job・ログ・artifact）を保存し、再試行で上書きしない。

## よくある問題

- `PALUDARIUM_TEST_NODE must name actual current Node executable` で JIT の試験が panic する：Node の絶対パスを設定する。
- aube のゲストビルドで `cargo deny` が exit 1：`python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` を使う（`scripts/u10-build-guests.sh` は policy を渡さない）。U9・U12 で主要な workflow は直した。
- `mbx cargo shim: mbx is not active on PATH`：`~/.cargo/bin` を PATH の先頭に置く。
- actionlint が exit 3 で止まる：mise の shellcheck shim に版がないため、`-shellcheck <0.11.0 の実体>` を指定する。
