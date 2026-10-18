# Build and Test のまとめ

2026-10-18 に、Loop-back 2 の後の版（head e3c29d1d）でまとめ直した（Modify）。

## 全体の状態と前提

- 対象：15 Unit（u1-skeleton〜u15-release）の Code Generation の成果全体。入力は各 Unit の `construction/<unit>/code-generation/code-generation-plan.md`（Testing Contract を含む）、`unit-test-instructions.md`、`code-summary.md`。目標は `inception/requirements-analysis/requirements.md`（FR・NFR）、`construction/u1-skeleton/nfr-requirements/`・`construction/u2-integer-isa/nfr-requirements/`、team.md の Testing Posture から取った。
- Test Strategy：Standard。Testing Contract（全 Unit 共通、methodology custom）。
- 人の回答（`build-and-test-questions.md`）：Q1 フォークの CI 一式で新しく測る、Q2 は Q5 で見直し（今の固定の版で測り、最新への更新は後の別作業）、Q3 ファジングと速さを新しく実行、Q4 この段階で公開（FR10.1）まで行う、Q6 公開まで進める、Q7 版は 0.1.0、Q8 U15 に戻って版を書き換える、Q9 NFR7 は Not Met として直しを次にまとめる。Loop-back 2 の後の見直しの要約も人が確認した（Looks correct）。
- Loop-back 1（FR8.3 と NFR7）で U14・U11 に戻り、JIT の整数 SSE の変換と Safari の session 作成の待ち時間の修正を入れた。Loop-back 2（FR10.1）で U15 に戻り、版を 0.1.0 にし（bb197e04）、受け入れの証拠を作る部品と初回の限定トークンの扱いを足し（bb197e04・a54315f9）、U15 の確認での指摘 R-16〜R-18 を直した（e3c29d1d）。U1・U2・U15 の確かめ直しと承認を終え、正式な確認コマンドは入口 v4（`u15_candidate_v4.py`）になった。
- 測った版：fork `codex/build-and-test` の head `e3c29d1d`（CI 一式 7 run）。今の作業コピーの製品コードは `e3c29d1d` と同じ。
- ビルド：この Mac で `cargo build --workspace --locked`・fmt・clippy が成功（2026-10-18）。単体テストは 809 成功・1 失敗（x86-64 Linux 以外では合格にしない `u8_runner_ready`）・4 無視（`PALUDARIUM_TEST_NODE` に Node 26.12.0 の実体のパス）。

## 作った試験手順

| ファイル | 内容 |
|---|---|
| build-instructions.md | 道具の版、ビルド、CI での実行手順、よくある問題 |
| integration-test-instructions.md | Unit をまたぐ差分テスト、wasm 4 環境、macOS・Windows Host、JIT と interpreter、公開物の境界。Safari の session 作成の待ち時間（60 秒）を追記 |
| performance-test-instructions.md | FR8.3 の速さの判定（合否あり）と FR7.4 の時間の記録 |
| security-test-instructions.md | ファジング 13 対象、unsafe・clippy・依存・Actions の固定・隔離 |
| test-results.md | 今の版の結果、速さの判定、Safari の揺れ、前回・前々回の結果（履歴）、Loop-Back Log |
| cross-unit-traceability.md | Unit をまたぐ要件の対応の最終確認 |

## Unit ごとのカバレッジの期待

すべての Unit で、native Linux で測る行カバレッジ 80% 以上（team.md Q5）。Unit ごとの集合は各 `unit-test-instructions.md` のとおり（例：U3 は CPU/Decoder 9 ファイル、U5 は固定 13 ファイル、U6 は固定 9 ファイル、U9 は旧 13・追加 10 ファイル、U11 は Rust 5 crate と JS 5 ファイル、U12 は Host 6 ファイル、U13 は Host 6・共通 5・Windows 固有、U14 は JIT・feature 集合・JS・Python、U15 は Python 4 ファイル）。workspace 全体と U1 の 11 crate も 80% 以上。今回の実測は workspace 93.85%、U1 93.85%、U9 86.82%、U11 86.88%、U3 82.71%（run 39114018191）。

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md | workspace・wasm32・production wasm のビルドが終了コード 0 | すべて成功 | 手元の build（2026-10-18）、run 39114018191 `lint`・`production wasm` | build-and-test | Met |
| NFR1 / FR9.1 | requirements.md NFR1・FR9.1 | 差分テストが fresh native x86-64 Linux と一致 | diff_u1〜u9・parallel_u2・U10 差分が成功 | run 39114018191 `differential tests (x86-64 Linux)`・U10 differential | build-and-test | Met |
| NFR3.2 | requirements.md NFR3 | fmt と clippy `-D warnings` が 0 件 | 0 件 | run 39114018191 `lint`、手元（2026-10-18） | build-and-test | Met |
| NFR3.3 | requirements.md NFR3、team.md Q5 | 各集合で行 80% 以上 | 93.85%・93.85%・86.82%・86.88%・82.71%、ほか各品質 run の下限の手順が成功 | test-results.md のカバレッジの表 | build-and-test | Met |
| NFR3.1 | requirements.md NFR3 | `unsafe` がホスト接続部と JIT の外にない | forbid と lint が通る | run 39114018191 `lint` | build-and-test | Met |
| NFR2 / FR9.3 | requirements.md NFR2・FR9.3 | ファジング 13 対象×600 秒、終了コード 0 | 13 対象すべて成功 | run 39114114216 | build-and-test | Met |
| NFR8.1 | requirements.md NFR8 | `cargo deny` が通る | 成功 | run 39114018191 `dependencies` | build-and-test | Met |
| NFR8.2 | requirements.md NFR8 | Actions がすべて SHA 固定 | 外部の `uses:` 409 件のうち SHA 固定でないものは 0 件（ほかにリポジトリ内の workflow の呼び出しが 19 件） | `.github/workflows/*.yml` の検査（2026-10-18） | build-and-test | Met |
| NFR9 | requirements.md NFR9、Q5 | `rust-toolchain.toml` の nightly で CI と手元が同じ | nightly-2026-10-11 で統一 | 各 job の toolchain、手元の `rustc -V` | build-and-test | Met |
| NFR7 | requirements.md NFR7 | 時間切れの上限があり、揺れた試験は記録して直す | 上限は守られ、揺れは記録した。safaridriver 側の時間切れという新しい揺れ（run 39114110570 attempt 1）は直していない | test-results.md の「Safari の揺れ」、Q9 の A | build-and-test | Not Met |
| FR5.1 | requirements.md FR5.1 | 3OS の単体テストが通る | 3OS とも成功 | run 39114018191 `unit tests (*)` | build-and-test | Met |
| FR5.2 / FR5.3 / FR9.2 | requirements.md FR5.2・FR5.3・FR9.2 | Node・Chromium・Firefox・本物 Safari で各 14 ケースが native と一致 | 4 環境とも成功（PR ゲートの Safari は 1 回目で成功、U12 の Safari は 2 回目で成功） | run 39114018191 `u11-programs`、run 39114108809、run 39114110570 | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Linux) | requirements.md FR6・FR7 | probe・aube・#1645 が native と一致 | 成功 | run 39114018191 U10 differential | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (macOS) | U12 の計画 | macOS native が fresh Linux と一致 | 成功 | run 39114110570 `macos-host` | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Windows) | U13 の計画 | Windows の guest が fresh Linux と一致 | 成功 | run 39114112207 `windows-host` | build-and-test | Met |
| FR7.4 / NFR6 | requirements.md FR7.4・NFR6 | aube 4 コマンドの時間を記録 | U10 差分の artifact に記録 | run 39114018191 の artifact `u10-differential` | build-and-test | Met |
| FR8.2 | requirements.md FR8.2 | 4 環境で JIT あり・なしが一致 | 成功 | run 39114108809 の wasm acceptance | build-and-test | Met |
| FR8.3 | requirements.md FR8.3 | JIT ありが有意水準 5% で速い | 平均 4.5834 秒 対 5.2649 秒（約 12.9% 速い）、p = 1/1024 = 0.00098 | run 39114108809、test-results.md の「速さの判定」 | build-and-test | Met |
| FR3.2 / NFR4 (Windows race) | U7 の計画 | symlink rename race が条件を満たす | 成功 | run 39114108809・39114112207 の Windows の job | build-and-test | Met |
| U15-PKG | U15 の計画 | 公開物の確認が通る | 成功（版 0.1.0 の 11 crate と npm tarball） | run 39114018143（`release-check.yml`） | build-and-test | Met |
| FR10.1 | requirements.md FR10.1、Q4・Q6・Q7 | 成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）を満たした後に公開 | 成功条件はそろい、版は 0.1.0 に決まり、公開の部品と手順（初回の限定トークン、再開、許可リスト）もそろった。upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、`u15-acceptance` の起動、tag は人の手順でまだ | `docs/release.md` の Owner hand-off、U15 の `code-summary.md` | build-and-test | Unverified |
| CI-BEFORE-MERGE | 各 Unit の Testing Contract と team.md Q7 | 選んだ試験をマージ前に CI で実行する | N/A | CI Pipeline, later in this plan, sets up CI to run these tests before merge | ci-pipeline | N/A |

## 準備状況

- build-ready：はい。この Mac と CI でビルドできる（nightly-2026-10-11）。
- test-ready：はい。CI 一式を fork `codex/build-and-test`（head e3c29d1d）で実行し、結果は `test-results.md` に記録した。
- deployment-ready：まだ。版は 0.1.0 に決まり、公開の部品と手順（`docs/release.md` の Owner hand-off）はそろったが、upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、同じ head の `u15-acceptance`、tag が人の手順で残っている。NFR7 の直しも残る。
- 判定：**失敗**（FR10.1 が Unverified、NFR7 が Not Met）。FR8.3 は e3c29d1d でも合格した。

## 既知の制限と残っていること

- 正式な確認コマンドは、この結果をまとめた後に、U15 の新しい入口 `entry-e3c29d1d/entry-c.py` へ変わった（人が採用、2026-10-18）。製品は変わっていないので、結果と判定はそのまま（`test-results.md` の「正式な確認コマンドの変更」）。

- FR10.1 の公開に、人が行う手順が要る（`docs/release.md` の Owner hand-off）：(1) fork `codex/build-and-test` から upstream の main への取り込み、(2) upstream の `release` environment の作成と保護（必須レビュアー、管理者の迂回の禁止）、(3) 11 crate と `@paludarium/wasm` の名前の所有と初回の公開の方法（対象と期限を絞ったトークン）、(4) Trusted Publisher の登録、(5) main の head での品質 run と `u15-acceptance` の起動、(6) `v0.1.0` の tag と environment の承認。squash で取り込むと head が変わるため、CI と受け入れの証拠は upstream の head で作り直す。
- NFR7：safaridriver 側の時間切れという新しい Safari の揺れ（run 39114110570 attempt 1）。Q9 の A のとおり、公開の前に製品をもう一度変えるときに直す。
- 残している Minor：U15 の入口 v4 の独立レビュー 04 の 6 件（`construction/u15-release/code-generation/verification/version-allowance/pending-minor-fixes.md`、再開の判定の owners と yank を含む）、U15 の Unit のレビュー（review-07）の 4 件、U1・U14 の Minor。次に製品か記録を更新するときにまとめて直す。
- 作業コピーの `aidlc/` の記録はまだコミットしていない。
- U3 の差分テストは、期待結果を確かめていない Intel の CPU（signature 000606a6）のランナーで止まる作り（今回は起きなかった）。
- 11 crate の `Cargo.toml` に `license` と `license-file` が両方あり、cargo が manifest の警告を出す（ビルドは成功）。今回は直していない。
- `nightly.yml`（main）のファジングは musl target のため全対象が失敗している（run 38967100569）。今回の正式なファジングは `u14-fuzz.yml` を使う。
- `ci.yml` に actionlint の既存の指摘 4 件（87・203・226 行目）、`u12-quality.yml` に 5 件がある。今回は直していない。
- `PALUDARIUM_TEST_NODE: node` はランナーにある Node の版に依存する（U9・U12 のレビューの指摘）。手元でも、mise の shim が版を決められないフォルダでは JIT の bridge の試験が落ちるため、実体のパスを渡す。
- 道具の版を最新に上げる作業（Rust nightly、CI の Node、Playwright）は、Q5 のとおり後の別作業。
