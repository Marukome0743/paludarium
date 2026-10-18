# Build and Test の試験結果

2026-10-18 に、Loop-back 2 の後の版（head e3c29d1d）でまとめ直した（Modify。手順書と前回の記録は残し、結果を今の版に結び直した）。Loop-back 1 の後の結果（head 1ceae86c〜57a8c96f）と、その前（2026-10-17）の結果は「前回の結果（履歴）」に残す。

## 実行した版と環境

- 製品コード：fork `Marukome0743/paludarium` のブランチ `codex/build-and-test`、head `e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9`（GitHub で Verified）。
  - 57a8c96f からの差は U15 の 3 つの commit：bb197e04（版を 0.1.0 にそろえ、受け入れの証拠を作る部品を足す、11 ファイル）、a54315f9（初回の限定トークンと release gate の直し、12 ファイル）、e3c29d1d（最初の公開の再開と子プロセスの環境の許可リスト、7 ファイル）。Rust の製品コードの差は版の行（`Cargo.toml`・`Cargo.lock`・`fuzz/Cargo.lock`）だけで、JIT・interpreter は同じ。
  - CI 一式はすべてこの head で実行した。
  - 今の作業コピーと e3c29d1d の差は、ビルドの出力（`target/` の中）、手元用の `mise.toml`・`tools/aidlc-recovery/`、`aidlc/` の記録だけで、製品コードと試験は同じ。
- 道具：Rust nightly-2026-10-11（`rustc 1.101.0-nightly (6f5da406b 2026-10-10)`、Q5 で今の版のまま測ることにした）、Node 26.12.0（CI の JIT の判定と、手元の試験）、Python 3.15.0。
- この Mac：macOS（Apple Silicon）、`~/.cargo/bin/cargo`。手元の試験では `PALUDARIUM_TEST_NODE` に Node 26.12.0 の実体のパス（`~/.local/share/mise/installs/node/26.12.0/bin/node`）を渡した。最初は `node` の名前で渡し、mise の shim がこのフォルダで版を決められずに JIT の bridge の 21 件が「Node batch runner failed」で落ちた（道具の設定の問題で、製品の不具合ではない）。

## ビルド

| 確認 | 結果 | 証拠 |
|---|---|---|
| `cargo build --workspace --locked`（この Mac、head e3c29d1d のソース） | 成功（終了コード 0） | 2026-10-18 の手元の実行 |
| `cargo fmt --all --check`・`cargo clippy --locked --workspace --all-targets -- -D warnings`（この Mac） | 成功（どちらも 0） | 2026-10-18 の手元の実行 |
| wasm32 向けの decoder・mmu・cpu、production wasm | 成功 | PR ゲート run 39114018191 の `lint`・`production wasm` |

## 試験の結果

| 試験 | 結果 | 証拠 |
|---|---|---|
| この Mac のワークスペース全体の単体テスト | 809 成功・1 失敗・4 無視。失敗は `diff_u8` の `u8_runner_ready`（x86-64 Linux 以外では合格にしない作り。前回と同じ） | `cargo test --locked --workspace --no-fail-fast`（`PALUDARIUM_TEST_NODE` に Node 26.12.0、2026-10-18） |
| PR ゲート（`ci.yml`、23 job） | 全 job 成功（attempt 1） | run 39114018191 |
| 全品質（`u14-quality.yml`、34 job） | 全 job 成功（attempt 1） | run 39114108809 |
| macOS の品質（`u12-quality.yml`、29 job） | 全 job 成功（attempt 2） | run 39114110570。attempt 1 は Safari の 1 job だけ失敗（下の記録） |
| Windows の品質（`u13-quality.yml`、29 job） | 全 job 成功（attempt 1） | run 39114112207 |
| ファジング（`u14-fuzz.yml`、13 対象×600 秒、ASan/LSan） | 13 job すべて成功（attempt 1） | run 39114114216 |
| U1〜U14 の現行ソースの照合（`u1-u14-source-bound.yml`、7 job） | 成功（attempt 1） | run 39114116352 |
| 公開物の確認（`release-check.yml`） | 成功（attempt 1） | run 39114018143 |
| U15 の公開の部品（`tests/release`、手元） | 146 件成功。validate・package-check は終了コード 0、coverage は 4 ファイルとも 80% 以上 | U15 の `code-summary.md` の「現在の状態（2026-10-18 JST、Step18）」と Step17 の節 |

途中の失敗の記録：

- run 39114110570 attempt 1（e3c29d1d）：Safari の job `u11-programs / differential (macos-latest, safari)`（job 117638480843）だけが落ちた。safaridriver が `session not created`（「Safari の起動を待つ間に時間切れ」）を返し、こちらの session 作成の待ち（60 秒）より前の 31 秒で止まった。人の判断で失敗した job だけを再実行し、attempt 2（job 117645706087）で成功した。1 回目の原本（run・job 一覧・ログ）は U15 の `verification/ci-e3c29d1d/u12-quality-39114110570/attempt-1/` に保存した。原因は確かめていない。下の NFR7 を参照。

## カバレッジ（行、native x86-64 Linux、PR ゲート run 39114018191 の `line coverage >= 80%`）

| 集計 | 行 | 割合 |
|---|---|---|
| workspace 全体 | 13037 / 13891 | 93.85% |
| U1 の 11 crate | 12566 / 13390 | 93.85% |
| U9 の対象 | 4955 / 5707 | 86.82% |
| U11 の Rust 5 crate（lcov から計算） | 5933 / 6829 | 86.88% |
| U3 の CPU・デコーダ 9 ファイル（alu・cpuid・crypto・exec・lib・softfloat・sse・state・decoder lib） | 2507 / 3031 | 82.71% |

- U11 の lcov は `verification/ci-e3c29d1d/ci-39114018191/u11-coverage-lcov/u11-coverage.lcov` に保存した（artifact の digest `sha256:549b55f5…`）。
- 注意（前回と同じ）：U3 の手順の表の TOTAL は 76.83% だが、これには CLI の `paludarium/src/cli.rs`・`main.rs`（0%）が入っている。U3 の目標は 9 ファイルの集合で、上の数字はその表から CLI の 2 ファイルを除いて計算した。U5・U6・U12・U13・U14・U15 の集合は、それぞれの品質 run（39114108809・39114110570・39114112207）の 80% の下限の手順が成功している。U15 の Python の 4 ファイルは公開物の確認 run 39114018143 の下限の手順が成功している。

## 速さの判定（FR8.3）

全品質 run 39114108809 の Node の job（「Frozen paired full-probe performance」）。artifact `u11-node` を U15 の `verification/ci-e3c29d1d/u14-quality-39114108809/u11-node/performance/observations.json` に保存した（ZIP の SHA-256 は API の digest と一致）。

- head e3c29d1d、Node v26.12.0。20 回すべて終了コード 0・PASS。
- 平均：JIT なし 5.2649 秒、JIT あり 4.5834 秒（JIT ありの方が約 12.9% 速い）。
- 1024 通りの符号反転による片側の正確検定：p = 1/1024 = 0.00098（< 0.05）。
- 判定：**合格**（`passed: true`）。測り直しはしていない（この run の 1 回の測定）。
- 参考：同じ版の系列で、1ceae86c（run 39030957672）・bb197e04・a54315f9（run 39096893624）でも p = 1/1024 で合格している。

## Safari の揺れ（NFR7）

- Loop-back 1 の直し（session の作成だけを 60 秒まで待つ。commit 2b8723ab・57a8c96f）の後、4 つの run で Safari の job が 1 回目で成功していた（下の「前回の結果（履歴）」）。
- 今回：e3c29d1d の U12 の品質 run 39114110570 の 1 回目で、Safari の job が落ちた。今度は safaridriver 自身が Safari の起動を待つ間に時間切れになった（31 秒）。前回の「こちらの待ち時間が短い」揺れとは別の種類で、今の直しでは防げない。e3c29d1d の PR ゲート run 39114018191 の Safari の job は 1 回目で成功した。
- 人の判断（Q9 の A）：NFR7 は **Not Met** とする。揺れは記録した。直し（session 作成が safaridriver 側の時間切れで失敗したときに 1 回だけやり直すなど）は、公開の前に製品をもう一度変えるときにまとめて行う。

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md | workspace・wasm32・production wasm のビルドが終了コード 0 | すべて成功 | 手元の build（2026-10-18）、run 39114018191 `lint`・`production wasm` | build-and-test | Met |
| NFR1 / FR9.1 | requirements.md NFR1・FR9.1 | 差分テストが fresh native x86-64 Linux と一致 | diff_u1〜u9・parallel_u2・U10 差分が成功 | run 39114018191 `differential tests (x86-64 Linux)`・U10 differential | build-and-test | Met |
| NFR3.2 | requirements.md NFR3 | fmt と clippy `-D warnings` が 0 件 | 0 件 | run 39114018191 `lint`、手元（2026-10-18） | build-and-test | Met |
| NFR3.3 | requirements.md NFR3、team.md Q5 | 各集合で行 80% 以上 | 93.85%・93.85%・86.82%・86.88%・82.71%、ほか各品質 run の下限の手順が成功 | 上のカバレッジの表 | build-and-test | Met |
| NFR3.1 | requirements.md NFR3 | `unsafe` がホスト接続部と JIT の外にない | forbid と lint が通る | run 39114018191 `lint` | build-and-test | Met |
| NFR2 / FR9.3 | requirements.md NFR2・FR9.3 | ファジング 13 対象×600 秒、終了コード 0 | 13 対象すべて成功 | run 39114114216 | build-and-test | Met |
| NFR8.1 | requirements.md NFR8 | `cargo deny` が通る | 成功 | run 39114018191 `dependencies` | build-and-test | Met |
| NFR8.2 | requirements.md NFR8 | Actions がすべて SHA 固定 | 外部の `uses:` 409 件のうち SHA 固定でないものは 0 件（ほかにリポジトリ内の workflow の呼び出しが 19 件） | `.github/workflows/*.yml` の検査（2026-10-18） | build-and-test | Met |
| NFR9 | requirements.md NFR9、Q5 | `rust-toolchain.toml` の nightly で CI と手元が同じ | nightly-2026-10-11 で統一 | 各 job の toolchain、手元の `rustc -V` | build-and-test | Met |
| NFR7 | requirements.md NFR7 | 時間切れの上限があり、揺れた試験は記録して直す | 上限は守られ、揺れは記録した。safaridriver 側の時間切れという新しい揺れ（run 39114110570 attempt 1）は直していない | 上の「Safari の揺れ」、Q9 の A | build-and-test | Not Met |
| FR5.1 | requirements.md FR5.1 | 3OS の単体テストが通る | 3OS とも成功 | run 39114018191 `unit tests (*)` | build-and-test | Met |
| FR5.2 / FR5.3 / FR9.2 | requirements.md FR5.2・FR5.3・FR9.2 | Node・Chromium・Firefox・本物 Safari で各 14 ケースが native と一致 | 4 環境とも成功（PR ゲートの Safari は 1 回目で成功、U12 の Safari は 2 回目で成功） | run 39114018191 `u11-programs`、run 39114108809、run 39114110570 | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Linux) | requirements.md FR6・FR7 | probe・aube・#1645 が native と一致 | 成功 | run 39114018191 U10 differential | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (macOS) | U12 の計画 | macOS native が fresh Linux と一致 | 成功 | run 39114110570 `macos-host` | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Windows) | U13 の計画 | Windows の guest が fresh Linux と一致 | 成功 | run 39114112207 `windows-host` | build-and-test | Met |
| FR7.4 / NFR6 | requirements.md FR7.4・NFR6 | aube 4 コマンドの時間を記録 | U10 差分の artifact に記録 | run 39114018191 の artifact `u10-differential` | build-and-test | Met |
| FR8.2 | requirements.md FR8.2 | 4 環境で JIT あり・なしが一致 | 成功 | run 39114108809 の wasm acceptance | build-and-test | Met |
| FR8.3 | requirements.md FR8.3 | JIT ありが有意水準 5% で速い | 平均 4.5834 秒 対 5.2649 秒（約 12.9% 速い）、p = 1/1024 = 0.00098 | run 39114108809、上の「速さの判定」 | build-and-test | Met |
| FR3.2 / NFR4 (Windows race) | U7 の計画 | symlink rename race が条件を満たす | 成功 | run 39114108809・39114112207 の Windows の job | build-and-test | Met |
| U15-PKG | U15 の計画 | 公開物の確認が通る | 成功（版 0.1.0 の 11 crate と npm tarball） | run 39114018143（`release-check.yml`） | build-and-test | Met |
| FR10.1 | requirements.md FR10.1、Q4・Q6・Q7 | 成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）を満たした後に公開 | 成功条件はそろい、版は 0.1.0 に決まり、公開の部品と手順（初回の限定トークン、再開、許可リスト）もそろった。upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、`u15-acceptance` の起動、tag は人の手順でまだ | `docs/release.md` の Owner hand-off、U15 の `code-summary.md` | build-and-test | Unverified |
| CI-BEFORE-MERGE | 各 Unit の Testing Contract と team.md Q7 | 選んだ試験をマージ前に CI で実行する | N/A | CI Pipeline, later in this plan, sets up CI to run these tests before merge | ci-pipeline | N/A |

## 判定

Build and Test は**失敗**（FR10.1 が Unverified、NFR7 が Not Met）。FR8.3 は e3c29d1d でも合格し、ほかの目標はすべて Met。NFR7 は Q9 の A のとおり、直しを公開の前の製品の変更にまとめる。FR10.1 は人の手順（upstream への取り込みから tag まで）が終わるまで Unverified のまま。

人の選択（2026-10-18）：Build Failure の問いで Accept failure を選んだ。この失敗を記録したまま段階の承認の場に進む（Loop-back は使っていない。使った数は 2/3 のまま）。

## 正式な確認コマンドの変更（2026-10-18）

この結果をまとめた後、U15 の Code Generation で、e3c29d1d を起点にした新しい確認コマンドの入口を作り、人が採用した。製品は変わっていない（head は e3c29d1d のまま）ので、上の試験・CI・測定の結果と判定はそのまま有効で、やり直していない。

- 今の正式な確認コマンド：`/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py --entry-sha256 44a8d9d0388db18fb5730dd54e5bb40f178a309536f39b48dde90d1f5eaf1a5a --binding-sha256 fd55262c37b6a50f71c58a677786a8af9aa7469defb3910853da64eadcbbf316`（`verification-command.txt`）。
- 確かめること：
  - 起点（入口 v4 が e3c29d1d で exit 0 になった記録、CI 7 run、FR8.3 の原本）をハッシュで固定し、もう一度は実行しない。
  - 毎回、署名と系譜、変わったファイル、head の追跡ファイルすべての bytes、CI、速さの原本を確かめる。
- U15 の checkpoint：このコマンドで exit 0（約 0.6 秒、v4 のときは約 47 秒）。変わったファイルは 0。
- 入口 v1〜v4（`construction/u15-release/code-generation/verification/version-allowance/`）は履歴になった。新しい入口はその bytes だけを固定する。
- 次に製品を変えて新しい head にするときは、入口のコードは変えない。新しい binding を作り、採用を伺う。

## 前回の結果（履歴、2026-10-18、Loop-back 1 の後、head 1ceae86c〜57a8c96f）

ここに残す結果は Loop-back 2 の前の版のもので、今の版の合格の証拠にはしない。見出しと本文は当時のまま（見出しの深さだけ 1 段下げた）。

### 実行した版と環境

- 製品コード：fork `Marukome0743/paludarium` のブランチ `codex/build-and-test`。
  - 今の head `57a8c96f`（Safari の session 作成の待ち時間の修正と、その試験）。CI・U12 の品質・公開物の確認はこの head で実行した。
  - その前の head `1ceae86c`（U14 の JIT の整数 SSE の変換）。U14・U13 の全品質、ファジング、ソースの照合はこの head で実行した。
  - `1ceae86c` と `57a8c96f` の差は 2 ファイル（`packages/paludarium-wasm/tests/u11-browser-driver.mjs` とその試験 `u11-browser-driver.test.mjs`）だけで、Rust の製品コード・JIT・lock は同じ。
  - 今の作業コピーと `57a8c96f` の差は、ビルドの出力（`target/` の中）、手元用の `mise.toml`・`tools/aidlc-recovery/`、`aidlc/` の記録だけで、製品コードと試験は同じ。
- 道具：Rust nightly-2026-10-11（`rustc 1.101.0-nightly (6f5da406b 2026-10-10)`、Q5 で今の版のまま測ることにした）、Node 26.12.0（CI の JIT の判定）、Python 3.15.0。
- この Mac：macOS（Apple Silicon）、`~/.cargo/bin/cargo`。

### ビルド

| 確認 | 結果 | 証拠 |
|---|---|---|
| `cargo build --workspace --locked`（この Mac、head 57a8c96f のソース） | 成功（終了コード 0） | 2026-10-18 の手元の実行 |
| `cargo fmt --all --check`・`cargo clippy --locked --workspace --all-targets -- -D warnings`（この Mac） | 成功（どちらも 0） | 2026-10-18 の手元の実行 |
| wasm32 向けの decoder・mmu・cpu、production wasm | 成功 | PR ゲート run 39073492190 の `lint`・`production wasm` |

### 試験の結果

| 試験 | 結果 | 証拠 |
|---|---|---|
| この Mac のワークスペース全体の単体テスト | 809 成功・1 失敗・4 無視。失敗は `diff_u8` の `u8_runner_ready`（x86-64 Linux 以外では合格にしない作り。前回と同じ） | `cargo test --locked --workspace --no-fail-fast`（`PALUDARIUM_TEST_NODE` を設定、2026-10-18） |
| PR ゲート（`ci.yml`、23 job） | 全 job 成功（attempt 1） | run 39073492190（head 57a8c96f） |
| 全品質（`u14-quality.yml`、34 job） | 全 job 成功（attempt 2） | run 39030957672（head 1ceae86c） |
| macOS の品質（`u12-quality.yml`、29 job） | 全 job 成功（attempt 2） | run 39073501121（head 57a8c96f）。attempt 1 は U3 の差分テストだけ失敗（下の記録） |
| Windows の品質（`u13-quality.yml`、29 job） | 全 job 成功（attempt 2） | run 39028305765（head 1ceae86c）。attempt 1 は U3 の差分テストだけ失敗（下の記録） |
| ファジング（`u14-fuzz.yml`、13 対象×600 秒、ASan/LSan） | 13 job すべて成功 | run 39028307842（head 1ceae86c） |
| U1〜U14 の現行ソースの照合（`u1-u14-source-bound.yml`、7 job） | 成功 | run 39028309948（head 1ceae86c） |
| 公開物の確認（`release-check.yml`） | 成功 | run 39073492188（head 57a8c96f） |

途中の失敗の記録（どれも製品の不具合ではなく、再実行で成功）：

- run 39073501121 attempt 1（57a8c96f）・run 39028305765 attempt 1（1ceae86c）：U3 の差分テスト `u3_fresh_native_differential` が `unobserved native SHA profile: "GenuineIntel" signature 000606a6` で止まった。U3 の差分テストは、期待結果を確かめていない CPU のランナーでは合格にしない作りで、前回（run 39015782530）と同じ。
- run 39044793102 attempt 1（2b8723ab）：`load_elf` のファジングの準備で `apt.llvm.org` につながらなかった（curl exit 7）。前回（run 39012177352）と同じ外の要因。

### カバレッジ（行、native x86-64 Linux、PR ゲート run 39073492190 の `line coverage >= 80%`）

| 集計 | 行 | 割合 |
|---|---|---|
| workspace 全体 | 13039 / 13891 | 93.87% |
| U1 の 11 crate | 12568 / 13390 | 93.86% |
| U9 の対象 | 4940 / 5707 | 86.56% |
| U11 の Rust 5 crate（lcov から計算） | 5917 / 6829 | 86.65% |
| U3 の CPU・デコーダ 9 ファイル（alu・cpuid・crypto・exec・lib・softfloat・sse・state・decoder lib） | 2507 / 3031 | 82.71% |

- U11 の lcov は `verification/ci-57a8c96f/ci-39073492190/u11-coverage-lcov/u11-coverage.lcov` に保存した。
- 注意（前回と同じ）：U3 の手順の表の TOTAL は 76.83% だが、これには CLI の `paludarium/src/cli.rs`・`main.rs`（0%）が入っている。U3 の目標は 9 ファイルの集合で、上の数字はその表から CLI の 2 ファイルを除いて計算した。U5・U6・U12・U13・U14・U15 の集合は、それぞれの品質 run（39030957672・39073501121・39028305765）の 80% の下限の手順が成功している。

### 速さの判定（FR8.3）

全品質 run 39030957672 の Node の job（「Frozen paired full-probe performance」）。artifact `u11-node` を `verification/ci-1ceae86c/u14-quality-39030957672/u11-node/performance/observations.json` に保存した。

- head 1ceae86c、Node v26.12.0（V8 14.6.202.34-node.39）、AMD EPYC 9V74。warmup は成功、20 回すべて終了コード 0・PASS。
- 平均：JIT なし 4.5277 秒、JIT あり 3.6349 秒（JIT ありの方が 19.7% 速い）。10 対の差はすべて JIT ありが速い（0.79〜1.06 秒）。
- 1024 通りの符号反転による片側の正確検定：p = 1/1024 = 0.00098（< 0.05）。
- 判定：**合格**（`passed: true`、`result.pass: true`）。測り直しはしていない（この run の 1 回の測定）。
- 今の head 57a8c96f との差は Safari の道具の 2 ファイルだけで、測った JIT・interpreter・probe と同じ。ただし公開（FR10.1）の前提には、公開する head と同じ head の受け入れの証拠が要る（`docs/release.md` の Owner prerequisites の 5）。

### Safari の揺れ（NFR7）

- 前回：Safari の WebDriver の session 作成が、要求の待ち時間（10 秒固定）を超えて 4 回揺れた。
- 修正：session の作成（`POST /session`）だけを 60 秒まで待ち、ほかの要求は 10 秒のままにした（commit 2b8723ab）。待ち時間が session の作成だけに効くことを確かめる試験を足した（commit 57a8c96f、`u11-browser-driver.test.mjs`）。
- 修正の後の結果：4 つの run で Safari の job（`u11-programs / differential (macos-latest, safari)`）がすべて 1 回目で成功した。

| run | head | 結果 |
|---|---|---|
| CI 39044785452 | 2b8723ab | attempt 1 で成功 |
| U12 の品質 39044793102 | 2b8723ab | attempt 1 で成功（attempt 1 の失敗は `load_elf` のファジングの準備だけ） |
| CI 39073492190 | 57a8c96f | attempt 1 で成功 |
| U12 の品質 39073501121 | 57a8c96f | attempt 1 で成功（attempt 1 の失敗は U3 の差分テストだけ） |

- 揺れた試験を記録して直すという条件を満たしたので、NFR7 は Met とする。

### Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| BT-BUILD | build-instructions.md | workspace・wasm32・production wasm のビルドが終了コード 0 | すべて成功 | 手元の build（2026-10-18）、run 39073492190 `lint`・`production wasm` | build-and-test | Met |
| NFR1 / FR9.1 | requirements.md NFR1・FR9.1 | 差分テストが fresh native x86-64 Linux と一致 | diff_u1〜u9・parallel_u2・U10 差分が成功 | run 39073492190 `differential tests (x86-64 Linux)`・U10 differential | build-and-test | Met |
| NFR3.2 | requirements.md NFR3 | fmt と clippy `-D warnings` が 0 件 | 0 件 | run 39073492190 `lint`、手元（2026-10-18） | build-and-test | Met |
| NFR3.3 | requirements.md NFR3、team.md Q5 | 各集合で行 80% 以上 | 93.87%・93.86%・86.56%・86.65%・82.71%、ほか各品質 run の下限の手順が成功 | 上のカバレッジの表 | build-and-test | Met |
| NFR3.1 | requirements.md NFR3 | `unsafe` がホスト接続部と JIT の外にない | forbid と lint が通る | run 39073492190 `lint` | build-and-test | Met |
| NFR2 / FR9.3 | requirements.md NFR2・FR9.3 | ファジング 13 対象×600 秒、終了コード 0 | 13 対象すべて成功 | run 39028307842（head 1ceae86c） | build-and-test | Met |
| NFR8.1 | requirements.md NFR8 | `cargo deny` が通る | 成功 | run 39073492190 `dependencies` | build-and-test | Met |
| NFR8.2 | requirements.md NFR8 | Actions がすべて SHA 固定 | `uses:` 406 件のうち SHA 固定でないものは 0 件 | `.github/workflows/*.yml` の検査（2026-10-18） | build-and-test | Met |
| NFR9 | requirements.md NFR9、Q5 | `rust-toolchain.toml` の nightly で CI と手元が同じ | nightly-2026-10-11 で統一 | 各 job の toolchain、手元の `rustc -V` | build-and-test | Met |
| NFR7 | requirements.md NFR7 | 時間切れの上限があり、揺れた試験は記録して直す | 上限は守られた。Safari の session 作成の揺れを記録し、session 作成だけを 60 秒待つ修正（試験つき）の後、4 つの run で 1 回目に成功 | 上の「Safari の揺れ」、commit 2b8723ab・57a8c96f | build-and-test | Met |
| FR5.1 | requirements.md FR5.1 | 3OS の単体テストが通る | 3OS とも成功 | run 39073492190 `unit tests (*)` | build-and-test | Met |
| FR5.2 / FR5.3 / FR9.2 | requirements.md FR5.2・FR5.3・FR9.2 | Node・Chromium・Firefox・本物 Safari で各 14 ケースが native と一致 | 4 環境とも成功（Safari は 1 回目で成功） | run 39073492190 `u11-programs`、run 39030957672 | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Linux) | requirements.md FR6・FR7 | probe・aube・#1645 が native と一致 | 成功 | run 39073492190 U10 differential | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (macOS) | U12 の計画 | macOS native が fresh Linux と一致 | 成功 | run 39073501121 `macos-host` | build-and-test | Met |
| FR6.3 / FR7.2 / FR7.3 (Windows) | U13 の計画 | Windows の guest が fresh Linux と一致 | 成功 | run 39028305765 `windows-host` | build-and-test | Met |
| FR7.4 / NFR6 | requirements.md FR7.4・NFR6 | aube 4 コマンドの時間を記録 | U10 差分の artifact に記録 | run 39073492190 の artifact `u10-differential` | build-and-test | Met |
| FR8.2 | requirements.md FR8.2 | 4 環境で JIT あり・なしが一致 | 成功 | run 39030957672 の wasm acceptance | build-and-test | Met |
| FR8.3 | requirements.md FR8.3 | JIT ありが有意水準 5% で速い | 平均 3.6349 秒 対 4.5277 秒（19.7% 速い）、p = 1/1024 = 0.00098 | run 39030957672、上の「速さの判定」 | build-and-test | Met |
| FR3.2 / NFR4 (Windows race) | U7 の計画 | symlink rename race が条件を満たす | 成功 | run 39030957672・39028305765 の Windows の job | build-and-test | Met |
| U15-PKG | U15 の計画 | 公開物の確認が通る | 成功 | run 39073492188（`release-check.yml`） | build-and-test | Met |
| FR10.1 | requirements.md FR10.1、Q4 | 成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）を満たした後に公開 | 成功条件はそろったが、まだ公開していない。公開に要る設定（版の決定、名前の所有、Trusted Publisher、release environment）と、公開する head と同じ head の受け入れの証拠がまだない | `docs/release.md` の Owner prerequisites | build-and-test | Unverified |
| CI-BEFORE-MERGE | 各 Unit の Testing Contract と team.md Q7 | 選んだ試験をマージ前に CI で実行する | N/A | CI Pipeline, later in this plan, sets up CI to run these tests before merge | ci-pipeline | N/A |

### 判定

Build and Test は**失敗**（FR10.1 が Unverified）。FR8.3 と NFR7 は Met になり、FR10.1 のほかの目標はすべて Met。FR10.1 は Q4 の B のとおりこの段階の中で公開まで行うが、公開に要る設定は人が行うため、その手順と時期を人に伝えて進め方を相談する。

## 前々回の結果（履歴、2026-10-17、head bd247f1e〜e4f84768）

ここに残す結果は Loop-back 1 の前の版のもので、今の版の合格の証拠にはしない。

- PR ゲート run 39015770796（e4f84768）、全品質 run 39009460781（bd247f1e）、macOS run 39015780495、Windows run 39015782530、ファジング run 39009468398、ソースの照合 run 39009462882、公開物の確認 run 39009470191：いずれも最終的に全 job 成功（Safari の session 作成のタイムアウトで再実行したものを含む）。
- カバレッジ（run 39015770796）：workspace 93.47%、U1 93.44%、U9 86.56%、U11 87.04%、U3 82.71%。
- 速さの判定（run 39009460781、head bd247f1e、AMD EPYC 7763）：JIT なし 5.4972 秒、JIT あり 5.4987 秒、p = 529/1024 = 0.5166 で**不合格**。artifact は `verification/ci-bd247f1e/u14-quality-39009460781/u11-node/performance/observations.json`。
- 途中の失敗（直したもの）：run 39009466368（Windows の単体テストと `u13-oracle`、U13 Steps11〜12 で修正）、run 39009487698・39009464565（U10 の差分テストの `GITHUB_SHA`、U9 Step 80 で修正）、run 39012177352（apt.llvm.org への接続失敗）。
- 前回の判定：失敗（FR8.3 と NFR7 が Not Met、FR10.1 が Unverified）。人が Retry with fix を選び、Loop-back 1 で U14・U11 の Code Generation に戻った。

## Loop-Back Log

### Loop-back 1 — 2026-10-17T09:05:47Z

- **Diagnosis**：FR8.3 は head bd247f1e で JIT あり 5.4987 秒・JIT なし 5.4972 秒、p = 0.5166 で不合格。前回の合格（208fd965、改善 2.74%、p = 0.0068）とほぼ同じ製品コードでも差が出ず、JIT の効果が小さくランナーの揺れに埋もれていると考えられる（原因は未確定）。NFR7 は、Safari の WebDriver の session 作成の待ち時間（10 秒固定）が足りずに 4 回揺れ、修正は正式な確認コマンドの封印（U14 の 223 個の compiled source）のため取り消した。
- **Root-cause stage**：code-generation（U14 の JIT の実装と、U11 の Safari の試験の道具）。
- **Planned fix**：U14 の Code Generation に戻り、JIT が効かない原因を切り分けて効果を上げる変更をする。あわせて Safari の session 作成の待ち時間を延ばす。どちらも封印された compiled source を変えるため、この差だけを認める新しい正式な確認コマンドを作り、人の承認を受ける。具体的な変更は U14 の計画で示し、Plan Approval を受ける。
- **Estimated impact**：手間は原因の切り分けに半日〜1 日、改善に数日（効果の大きさは未確定）。費用は CI の実行時間だけ。リスクは大きい（新しい正式な確認コマンドが必要、改善しても有意差に届かない可能性がある）。
- **人の選択**：Retry with fix（2026-10-17）。
- **結果**（2026-10-18 に記録）：U14 で整数 SSE の差分テストのケース（12d6a2f6）と JIT での変換（1ceae86c）を足し、run 39030957672 で FR8.3 が合格した。Safari は session 作成だけを 60 秒待つ修正（2b8723ab・57a8c96f）で、4 つの run で 1 回目に成功した。人は Code Generation の U1〜U15 の確かめ直しを承認した。

### Loop-back 2 — 2026-10-18T01:27:17Z

- **Diagnosis**：FR10.1（公開）が Unverified。公開の成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）はそろったが、版が `0.0.0` のままで、`scripts/release/policy.py` と `docs/release.md` は `0.0.0` の公開を認めない。人は Q6 で公開まで進め、Q7 で版を 0.1.0 に決めた。版の書き換えは承認済みの 12 Unit の担当ソース（`Cargo.toml`・`Cargo.lock`・`fuzz/`・`package.json`・`README.md`・`docs/release.md`）に及ぶ。
- **Root-cause stage**：code-generation（U15 の公開の準備。版が未決定のまま）。
- **Planned fix**：人の Q8 の選択に従い、U15 の Code Generation に戻る。workspace・crate 間の依存 11 件・npm を 0.1.0 にそろえ、lock と文書を合わせる。U15 の計画として Plan Approval を受ける。ファイルを持つほかの Unit は確かめ直しだけ行う。そのあと、その head で CI 一式と `u15-acceptance` の受け入れの証拠を作り直し、Build and Test に戻る。名前の所有と初回の公開、Trusted Publisher、`release` environment は、必要な時点で人に伝えて人が行う。
- **Estimated impact**：手間は版の書き換えに 1〜2 時間、12 Unit の確かめ直しと CI 一式・ファジングの再実行に半日ほど。費用は CI の実行時間だけ。リスクは中くらい（各 Unit の正式な確認コマンドの照合の更新が要る。製品の動きは変わらない）。
- **人の選択**：Q6 A（公開まで進める）、Q7 A（0.1.0）、Q8 A（U15 に戻って行う）、2026-10-18。
- **結果**（2026-10-18 に記録）：U15 の Code Generation で版を 0.1.0 にし（bb197e04）、受け入れの証拠を作る部品と初回の限定トークンの扱いを足し（bb197e04・a54315f9）、U15 の確認での指摘 R-16〜R-18 を直した（e3c29d1d）。U1・U2 の確かめ直しと U15 の承認を終え、正式な確認コマンドは入口 v4（`u15_candidate_v4.py`）になった。e3c29d1d の CI 7 run は最終的にすべて成功し、FR8.3 も合格した。FR10.1 は人の手順を待つため Unverified のまま、NFR7 は新しい揺れで Not Met（Q9 の A）。
