# Build and Test のまとめ

2026-10-19 に、U15 の Step22〜30 と U1〜U15 の確かめ直しの後の版（head 27d05de1）でまとめ直した（Modify、Q10 の A）。前の版（e3c29d1d、2026-10-18）でのまとめは、`test-results.md` の「履歴：head e3c29d1d の結果」に結果を残している。

## 全体の状態と前提

- 対象：15 Unit（u1-skeleton〜u15-release）の Code Generation の成果全体。入力は各 Unit の `construction/<unit>/code-generation/code-generation-plan.md`（Testing Contract を含む）、`unit-test-instructions.md`、`code-summary.md`。目標は `inception/requirements-analysis/requirements.md`（FR・NFR）、`construction/u1-skeleton/nfr-requirements/`・`construction/u2-integer-isa/nfr-requirements/`、team.md の Testing Posture から取った。
- Test Strategy：Standard。Testing Contract（全 Unit 共通、methodology custom）。
- 人の回答（`build-and-test-questions.md`）：Q1 フォークの CI 一式で新しく測る、Q2 は Q5 で見直し（今の固定の版で測り、最新への更新は後の別作業）、Q3 ファジングと速さを新しく実行、Q4 この段階で公開（FR10.1）まで行う、Q6 公開まで進める、Q7 版は 0.1.0、Q8 U15 に戻って版を書き換える、Q9 NFR7 は Not Met として直しを公開の前の製品の変更にまとめる、Q10 27d05de1 で Modify（証拠を結び直し、この Mac でビルドと単体テストを実行し直す）。要約は人が確認した（Looks correct）。
- Loop-back 1（FR8.3 と NFR7）で U14・U11 に戻り、JIT の整数 SSE の変換と Safari の session 作成の待ち時間の修正を入れた。Loop-back 2（FR10.1）で U15 に戻り、版を 0.1.0 にし、公開の部品をそろえた。そのあと Q9 の A のとおり、U15 の Step22〜28 で NFR7 の直し（Safari の暖機と 1 回だけのやり直し）、CI の整理、公開の部品の Minor を入れ、head 27d05de1 で CI 一式と Safari の 10 回の確認を行った。U1〜U15 の確かめ直しと承認は 2026-10-19 に終わった。
- 測った版：fork `codex/build-and-test` の head `27d05de1`（CI 一式 8 run と Safari の 10 回の確認）。今の作業コピーの製品コードは `27d05de1` と同じ。
- ビルド：この Mac で `cargo build --workspace --locked`・wasm32・fmt・clippy が成功（2026-10-19）。単体テストは 809 成功・1 失敗（x86-64 Linux 以外では合格にしない `u8_runner_ready`）・4 無視。tests/release 156 件と Safari の道具の試験 14 件も成功（`verification/local-27d05de1/`）。
- 正式な確認コマンド：U15 の `verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（intent 直下の `verification-command.txt` の 1 行目、2026-10-19 に人が採用）。

## 作った試験手順

| ファイル | 内容 |
|---|---|
| build-instructions.md | 道具の版、ビルド、CI での実行手順、よくある問題 |
| integration-test-instructions.md | Unit をまたぐ差分テスト、wasm 4 環境、macOS・Windows Host、JIT と interpreter、公開物の境界。Safari の session 作成の待ち時間（60 秒）、safaridriver 側の時間切れのときだけの 1 回のやり直しと暖機、Safari の 10 回の確認を追記 |
| performance-test-instructions.md | FR8.3 の速さの判定（合否あり）と FR7.4 の時間の記録 |
| security-test-instructions.md | ファジング 13 対象、unsafe・clippy・依存・Actions の固定・隔離 |
| test-results.md | 今の版（27d05de1）の結果、速さの判定、Safari の揺れ、前の版の結果（履歴）、Loop-Back Log |
| cross-unit-traceability.md | Unit をまたぐ要件の対応の最終確認 |

## Unit ごとのカバレッジの期待

すべての Unit で、native Linux で測る行カバレッジ 80% 以上（team.md Q5）。Unit ごとの集合は各 `unit-test-instructions.md` のとおり（例：U3 は CPU/Decoder 9 ファイル、U5 は固定 13 ファイル、U6 は固定 9 ファイル、U9 は旧 13・追加 10 ファイル、U11 は Rust 5 crate と JS 5 ファイル、U12 は Host 6 ファイル、U13 は Host 6・共通 5・Windows 固有、U14 は JIT・feature 集合・JS・Python、U15 は Python 4 ファイル）。workspace 全体と U1 の 11 crate も 80% 以上。今回の実測は workspace 93.86%、U1 93.85%、U9 86.82%、U11 86.86%、U3 82.71%（PR ゲート run 39143561947）。

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md | workspace・wasm32・production wasm のビルドが終了コード 0 | すべて成功 | `verification/local-27d05de1/`（2026-10-19）、run 39143561947 `lint`・`production wasm` | build-and-test | Met |
| NFR1 / FR9.1 | requirements.md NFR1・FR9.1 | 差分テストが fresh native x86-64 Linux と一致 | diff_u1〜u9・parallel_u2・U10 差分が成功 | run 39143561947 `differential tests (x86-64 Linux)`・U10 differential | build-and-test | Met |
| NFR3.2 | requirements.md NFR3 | fmt と clippy `-D warnings` が 0 件 | 0 件 | run 39143561947 `lint`、`verification/local-27d05de1/fmt.log`・`clippy.log` | build-and-test | Met |
| NFR3.3 | requirements.md NFR3、team.md Q5 | 各集合で行 80% 以上 | 93.86%・93.85%・86.82%・86.86%・82.71%、ほか各品質 run の下限の手順が成功 | 上のカバレッジの表 | build-and-test | Met |
| NFR3.1 | requirements.md NFR3 | `unsafe` がホスト接続部と JIT の外にない | forbid と lint が通る | run 39143561947 `lint` | build-and-test | Met |
| NFR2 / FR9.3 | requirements.md NFR2・FR9.3 | ファジング 13 対象×600 秒、終了コード 0 | 13 対象すべて成功 | run 39149194521 | build-and-test | Met |
| NFR8.1 | requirements.md NFR8 | `cargo deny` が通る | 成功 | run 39143561947 `dependencies` | build-and-test | Met |
| NFR8.2 | requirements.md NFR8 | Actions がすべて SHA 固定 | 外部の `uses:` 217 件のうち SHA 固定でないものは 0 件（ほかにリポジトリ内の workflow の呼び出しが 18 件、workflow は 21 ファイル） | `.github/workflows/*.yml` の検査（2026-10-19、27d05de1 の作業コピー） | build-and-test | Met |
| NFR9 | requirements.md NFR9、Q5 | `rust-toolchain.toml` の nightly で CI と手元が同じ | nightly-2026-10-11 で統一 | 各 job の toolchain、`verification/local-27d05de1/versions.txt` | build-and-test | Met |
| NFR7 | requirements.md NFR7 | 時間切れの上限があり、揺れた試験は記録して直す | 上限は守られ、e3c29d1d の揺れは記録して直した（暖機と 1 回だけのやり直し）。27d05de1 の 10 回の確認で 10 回とも成功、やり直し 0 回。注記：確認は暖機のある経路だけ、やり直しの経路は本物の Safari では動いていない | 上の「Safari の揺れ」、run 39143558642 | build-and-test | Met |
| FR5.1 | requirements.md FR5.1 | 3OS の単体テストが通る | 3OS とも成功 | run 39143561947 `unit tests (*)` | build-and-test | Met |
| FR5.2 / FR5.3 / FR9.2 | requirements.md FR5.2・FR5.3・FR9.2 | Node・Chromium・Firefox・本物 Safari で各 14 ケースが native と一致 | 4 環境とも成功（Safari の job は、PR ゲートと U13・U14 の品質 run では attempt 1、U12 の品質 run では最新の attempt で成功。Safari の 10 回の確認も成功） | run 39143561947 `u11-programs`、run 39149187727、run 39143558642 | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Linux) | requirements.md FR6・FR7 | probe・aube・#1645 が native と一致 | 成功 | run 39143561947 U10 differential | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (macOS) | U12 の計画 | macOS native が fresh Linux と一致 | 成功 | run 39149189719 `macos-host` | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Windows) | U13 の計画 | Windows の guest が fresh Linux と一致 | 成功 | run 39149192303 `windows-host` | build-and-test | Met |
| FR7.4 / NFR6 | requirements.md FR7.4・NFR6 | aube 4 コマンドの時間を記録 | U10 差分の artifact に記録 | run 39143561947 の U10 differential の artifact | build-and-test | Met |
| FR8.2 | requirements.md FR8.2 | 4 環境で JIT あり・なしが一致 | 成功 | run 39149187727 の wasm acceptance | build-and-test | Met |
| FR8.3 | requirements.md FR8.3 | JIT ありが有意水準 5% で速い | 平均 4.5488 秒 対 5.7522 秒（約 20.9% 速い）、p = 1/1024 = 0.00098 | run 39149187727、上の「速さの判定」 | build-and-test | Met |
| FR3.2 / NFR4 (Windows race) | U7 の計画 | symlink rename race が条件を満たす | 成功 | run 39149187727・39149192303 の Windows の job | build-and-test | Met |
| U15-PKG | U15 の計画 | 公開物の確認が通る | 成功（版 0.1.0 の 11 crate と npm tarball） | run 39143562106（`release-check.yml`） | build-and-test | Met |
| FR10.1 | requirements.md FR10.1、Q4・Q6・Q7 | 成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）を満たした後に公開 | 成功条件はそろい、版は 0.1.0、公開の部品と手順もそろった（owners・yanked の確認を含む）。upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、`u15-acceptance` の起動、tag は人の手順でまだ | `docs/release.md` の Owner hand-off、U15 の `code-summary.md` | build-and-test | Unverified |
| CI-BEFORE-MERGE | 各 Unit の Testing Contract と team.md Q7 | 選んだ試験をマージ前に CI で実行する | N/A | CI Pipeline, later in this plan, sets up CI to run these tests before merge | ci-pipeline | N/A |

## 準備状況

- build-ready：はい。この Mac と CI でビルドできる（nightly-2026-10-11）。
- test-ready：はい。CI 一式と Safari の 10 回の確認を fork `codex/build-and-test`（head 27d05de1）で実行し、結果は `test-results.md` に記録した。
- deployment-ready：まだ。版は 0.1.0、公開の部品と手順（`docs/release.md` の Owner hand-off）はそろったが、upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、同じ head の `u15-acceptance`、tag が人の手順で残っている。
- 判定：**失敗**（FR10.1 が Unverified）。NFR7 は直しと 10 回の確認で Met（注記つき）、FR8.3 は 27d05de1 でも合格した。

## 既知の制限と残っていること

- FR10.1 の公開に、人が行う手順が要る（`docs/release.md` の Owner hand-off）：(1) fork `codex/build-and-test` から upstream の main への取り込み、(2) upstream の `release` environment の作成と保護（必須レビュアー、管理者の迂回の禁止）、(3) 11 crate と `@paludarium/wasm` の名前の所有と初回の公開の方法（対象と期限を絞ったトークン）、(4) Trusted Publisher の登録、(5) main の head での品質 run と `u15-acceptance` の起動、(6) `v0.1.0` の tag と environment の承認。squash で取り込むと head が変わるため、CI と受け入れの証拠は upstream の head で作り直す。
- NFR7 の注記：Safari の 10 回の確認は、暖機を入れた `u11-acceptance.yml` の経路だけを確かめた。U13・U14 の Safari の job には暖機が無い。やり直しは 0 回だったので、やり直しの経路が本物の Safari で動いた証拠はない（根拠は仮の safaridriver での単体の試験）。
- 残している Minor：U15 の `construction/u15-release/code-generation/verification/version-allowance/pending-minor-fixes.md` にまとめている（入口 f の独立レビュー 04 の 2 件と注記、U15 の review-09・review-10 の製品・workflow・台帳の件、U13 の review-08 の 1 件など）。そのうち次の製品の変更でまとめて直すもの：nightly で同じ fuzz が 2 回走ること、取り消しの確認で npm の `deprecated` を見ず `registry_state` が `yanked` の無い場合を通すこと、`docs/release.md` の内部の番号と `ci-config.md` の一覧。
- CI の Node の版の食い違い（`u11-acceptance.yml`・`u11-safari-stability.yml` は 26.11.1、ほかと手元は 26.12.0）と、JS の製品ファイルの coverage 80% が PR のゲートでは測られず夜間と手動の `u14-wasm-acceptance.yml` だけで測られること（U11 の記録）。次に workflow を変えるときにまとめて決める。
- 作業コピーの `aidlc/` の記録（U1〜U15 の確かめ直しと、この Build and Test のまとめ直し）はまだコミットしていない。作業コピーには `__pycache__/*.pyc` などのビルドの出力も入っていて、コミットの前に扱いを決める必要がある。
- U3 の差分テストは、期待結果を確かめていない Intel の CPU（signature 000606a6）のランナーで止まる作り（今回は起きなかった）。
- 11 crate の `Cargo.toml` に `license` と `license-file` が両方あり、cargo が manifest の警告を出す（ビルドは成功）。今回は直していない。
- `PALUDARIUM_TEST_NODE: node` はランナーにある Node の版に依存する（U9・U12 のレビューの指摘）。手元でも、mise の shim が版を決められないフォルダでは JIT の bridge の試験が落ちるため、実体のパスを渡す。
- 道具の版を最新に上げる作業（Rust nightly、CI の Node、Playwright）は、Q5 のとおり後の別作業。
