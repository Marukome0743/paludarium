# 結合テスト手順（Build and Test）

エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まる（team.md Testing Posture、NFR1）。結合テストの中心は、Unit をまたぐ差分テストと、wasm の 4 環境での受け入れ試験である。期待結果は CI を実行するたびに x86-64 Linux のランナーで作り、保存した期待値は使わない（FR9.1）。

## 対象と境界

| 境界 | 試験 | 入口 | 環境 |
|---|---|---|---|
| ELF 読み込み→デコーダ→CPU→MMU→syscall→Host（U1〜U9 の主要経路） | diff_u1・diff_u2・parallel_u2・diff_u3・diff_u4・diff_u5・diff_u6・diff_u7・diff_u8・diff_u9 | `cargo test --locked -p paludarium-harness --test <name> -- --nocapture` | native x86-64 Linux（CI） |
| probe 8 項目・aube 4 コマンド・#1645（U10、FR6・FR7） | diff_u10（`--include-ignored`）、`scripts/u10-run.py --native-only` | `.github/workflows/u10-native-diagnostic.yml` | native Linux、`unshare --net` |
| wasm launcher と production wasm（U11、FR5.2・FR5.3・FR9.2） | Node・Chromium・Firefox・本物 Safari 各 14 ケース | `.github/workflows/u11-acceptance.yml`、`u14-wasm-acceptance.yml` | Linux CI と macOS CI |
| macOS Host（U12） | diff_u12、native 14＋2 と元 argv 14＋2 | `.github/workflows/u12-quality.yml` の `macos-host` | macOS CI |
| Windows Host（U13） | guest 32 件、instrument あり 16 件 | `.github/workflows/u13-quality.yml` | Windows CI |
| JIT と interpreter（U14、FR8.2） | diff_u14、4 環境×28 比較、filesystem 32 件 | `u14-quality.yml`、`u14-wasm-acceptance.yml` | Linux CI、ブラウザ |
| 公開物（U15、FR10.1 の前提） | 11 crate の package、隔離 registry、npm tarball の 7 境界 | `scripts/release/check.py --mode package-check`、`release-check.yml` | この Mac と CI |

## 実行

CI（正式。push と起動は人の承認後）：`ci.yml` の `differential`・`u11-programs`・`u10-programs`・`production-wasm` job、`u12-quality.yml`、`u13-quality.yml`、`u14-quality.yml`、`u14-wasm-acceptance.yml`。

この Mac（補助）：差分テストは macOS では cfg により 0 件で終了コード 0 になるため、合格の証拠にしない。この Mac では次だけを実行する。

```sh
env PATH="$HOME/.cargo/bin:$PATH" PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node cargo test --locked -p paludarium --test command -- --nocapture
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B scripts/release/check.py --mode package-check
```

## 期待する結果

- すべての差分テストが fresh native と一致する（比べないフラグ・値は各 Unit の表のとおり）。
- 4 環境の各 14 ケースが native と一致する。
- 30 秒の watchdog で止まった試験は失敗として記録し、揺れた試験は記録して直す（NFR7）。
- Safari の WebDriver は、session の作成（`POST /session`）だけを 60 秒まで待つ。ほかの要求の待ち時間は 10 秒のまま（`packages/paludarium-wasm/tests/u11-browser-driver.mjs`、試験は `u11-browser-driver.test.mjs`。Loop-back 1 の修正、commit 2b8723ab・57a8c96f）。
- Safari の session 作成が safaridriver 側の時間切れ（`"error":"session not created"` と「timed out while connecting to a Safari instance」の両方を含む失敗）で失敗したときだけ、Safari を止めて 1 回だけやり直す。1 回目の失敗は `session_retry` と stderr に残し、ほかの失敗はやり直さない。`u11-acceptance.yml` の Safari の job は試験の前に Safari を一度起動して閉じる（暖機、失敗しても job を落とさない）。効き目は `u11-safari-stability.yml`（まっさらな macOS の runner で 10 回）で確かめる（U15 Step22〜23、commit 8360be2e。27d05de1 の run 39143558642 で 10 回とも成功、やり直し 0 回）。U13・U14 の Safari の job（`u13-wasm-acceptance.yml`・`u14-wasm-acceptance.yml`）には暖機が無く、driver の中のやり直しだけが効く。
- カバレッジの扱いは単体テストと合わせて行う（行カバレッジ 80% 以上、native Linux で測る）。

## テストデータ

- ゲストは各 `tests/guests/u*/build.sh`（U10 は `tests/guests/u10/build.py` と固定 source-lock）でその場でビルドする。
- 期待結果は同じ CI run の native 実行から作る。pid・時刻・乱数・アドレスなどは、比べる前にそろえるか比べない。
