# 品質のゲート

2026-10-18 に、Build and Test が記録した確認の命令（`construction/build-and-test/build-instructions.md`・`integration-test-instructions.md`・`performance-test-instructions.md`・`security-test-instructions.md`）と、その結果（`test-results.md`）をもとに書いた。2026-10-19 に、Build and Test のまとめ直し（head 27d05de1）の結果に合わせて書き直した。人の回答は `ci-pipeline-questions.md`（Q1〜Q5 はすべて A、要約は Looks correct。2026-10-19 に確認し直した）。

## マージを止めるゲート（upstream の `main` の必須チェック、Q4 の A）

設定は upstream の管理者がブランチの保護で行う。必須チェックの名前は、27d05de1 の PR ゲート run 39143561947 と公開物の確認 run 39143562106 の job の名前のとおり（e3c29d1d の run 39114018191・39114018143 と同じ名前）。

| ゲート | 必須チェック（job の名前） | 合格の条件 | Build and Test での結果（27d05de1） | 要件 |
|---|---|---|---|---|
| 整形と lint | `lint` | `cargo fmt --all --check` と `cargo clippy --locked --workspace --all-targets -- -D warnings` が 0 件。`unsafe` の禁止と `// SAFETY:` の lint が通る | 成功 | NFR3.1・NFR3.2 |
| 3OS の単体テスト | `unit tests (ubuntu-latest)`・`unit tests (macos-latest)`・`unit tests (windows-latest)` | `cargo test --locked` が全件成功 | 成功 | FR5.1 |
| 依存の検査 | `dependencies` | `cargo deny --locked check`：ライセンスが Apache-2.0 と両立する、取得元が crates.io だけ、既知の脆弱性なし | 成功 | NFR8.1、project.md の Mandated |
| x86-64 Linux の差分テスト | `differential tests (x86-64 Linux)` | diff_u1〜u9・parallel_u2 が、同じ run で作った native の期待結果と一致 | 成功 | NFR1・FR9.1 |
| U10 の差分 | `U10 fixed guests and fresh native differential / fixture-metadata-oracle`・`/ native-first`・`/ differential` | probe・aube・#1645 が native と一致。aube 4 コマンドの時間を記録 | 成功 | FR6.3・FR7.2・FR7.3（Linux）・FR7.4・NFR6 |
| wasm 4 環境 | `u11-programs / build-oracle`、`u11-programs / differential (ubuntu-latest, node)`・`(ubuntu-latest, chromium)`・`(ubuntu-latest, firefox)`・`(macos-latest, safari)` | 14 ケースが native と一致（Safari は本物の Safari） | 成功 | FR5.2・FR5.3・FR9.2 |
| production wasm | `production wasm (shared Rust heap, nested Workers)` | wasm32 のビルドと、共有の Rust heap・入れ子の Worker の確認が通る | 成功 | BT-BUILD |
| 短いファジング | `u11-fuzz / fuzz (load_elf)`・`(syscall_args)`・`(vfs_paths)`・`(kernel_threads_u5)`・`(kernel_futex_u5)`・`(kernel_events_u6)`・`(kernel_sockets_u6)` | 各対象が終了コード 0 | 成功 | NFR2（短い確認） |
| 行カバレッジ | `line coverage >= 80%` | workspace・U1・U9・U3 の各集合で 80% 以上（`--fail-under-lines 80`） | 93.86%・93.85%・86.82%・82.71%（U11 は 86.86%） | NFR3.3、team.md の Q5 |
| 公開物の確認 | `release-check.yml` の job | 版の一致、11 crate と npm tarball の package、隔離した consumer のビルド、import と実 Wasm の hello、U15 の Python 4 ファイルの行カバレッジ 80%。公開はしない | 成功 | FR10.1 の前提、NFR8・NFR9 |

- 下限は下げない。試験を外す、skip にする、0 件で成功にすることはしない（team.md の Testing Posture、Build and Test の受理条件）。
- 揺れたテストは記録して直す。スレッドを使うテストには時間切れの上限がある（NFR7）。Safari の session の作成が safaridriver 側の時間切れで失敗する揺れ（e3c29d1d の run 39114110570 attempt 1）は、公開の前の製品の変更（U15 の Step22〜23）で、`u11-acceptance.yml` の Safari の job の暖機と、この時間切れのときだけ 1 回やり直す driver で直した。27d05de1 の `u11-safari-stability.yml`（run 39143558642）で 10 回とも成功、やり直し 0 回（Build and Test で NFR7 は Met。確認は暖機のある PR の Safari の経路だけで、やり直しの経路は本物の Safari では動いていない、という注記つき）。揺れが出たときは、今までどおり人の判断で失敗した job だけを再実行し、1 回目の原本を残す。

## マージを止めないゲート（夜間、Q2 の A）

| ゲート | 中身 | 合格の条件 | 失敗したとき |
|---|---|---|---|
| 夜間のファジング | `u14-fuzz.yml`：13 対象×600 秒、ASan/LSan | 13 対象すべて終了コード 0 | Issue を作って直す。今の `nightly.yml` では、`u14-quality.yml` の中の `u13-fuzz` でも同じ fuzz が走り、2 回になっている（`ci-config.md` の「入れた後の食い違い」の 1、次の製品の変更で直す） |
| 夜間の全品質 | `u14-quality.yml`：3OS の全品質、wasm 4 環境、JIT あり・なしの一致（FR8.2）、速さの判定（FR8.3） | 34 job すべて成功。速さは JIT ありが有意水準 5% で速い（片側の正確検定） | Issue を作って直す。速さは合格を待つ測り直しをしない |

## 公開の前のゲート

公開する head（upstream の `main` の head）で、次がすべて成功していること（`docs/release.md` の Owner hand-off の (5)、`scripts/release/policy.py` の `REQUIRED` 8 目的と `ACCEPTANCE` 5 条件）。

- `ci.yml`、`release-check.yml`、`u12-quality.yml`（macOS）、`u13-quality.yml`（Windows）、`u14-quality.yml`（全体と速さ）、`u14-fuzz.yml`、`u1-u14-source-bound.yml`。
- `u15-acceptance.yml` が作る受け入れの証拠（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）。
- `release` environment での人の承認。

squash で取り込むと head が変わるので、fork で得た結果は使わず、upstream の head で作り直す。

## Construction → Operation の境界の確認

結果は `aidlc/spaces/default/intents/261004-rust-blink-port/verification/phase-check-construction.md` に書いた（2026-10-19 に書き直した）。FR10.1（公開）が未対応・Unverified のため「未解決あり」。NFR7 は 27d05de1 で Met になった。Operation フェーズはこのワークフローではスキップしている（team.md の Deployment）。

正式な確認コマンドは U15 の入口の版 f `entry-f.py`・`binding-e06f.json`（2026-10-19 に人が採用。2026-10-18 の `entry-c.py` は履歴）で、上の必須チェックのうち `CI`・`Release package checks` と、公開の前のゲートの 5 つの workflow の成功を、保存した CI の記録で確かめる（`ci-config.md` の「正式な確認コマンドとの関係」）。
