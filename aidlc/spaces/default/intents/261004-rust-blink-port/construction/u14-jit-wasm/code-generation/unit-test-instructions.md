# U14 単体テスト手順

## 今回Steps45〜46：指摘への対応と新しい入口

新しい製品のテスト・CI・性能測定は行わない。project rootで、次を実行する（`<entry>`・`<binding>` は `u14_candidate_v2.py` と `binding-07.json` のSHA-256）。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/test_u14_candidate_v2.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/u14_candidate.py --entry-sha256 0eeaea6a662710834550df9560d534bf7a1dafa1e171ffb7b691da6249c9d5b0 --binding-sha256 f2931589a867d6506d54ea2a972ba7a0ca69a65fc18f956ab5b48acd77d16d21
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/u14_candidate_v2.py --entry-sha256 <entry> --binding-sha256 <binding>
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md
```

期待する結果：回帰は全件成功・skip 0。仮採用のコマンド（`u14_candidate.py`、binding-06）は、Step45の変更で想定どおりexit 1（拒否の理由を記録する）。新しい入口はexit 0。sensorは2件ともpass。traceability.jsonの親FR8とNFR1・2・3・8、FR6.3・7.2の行に「現行」と「履歴（208fd965）」の区別があり、statusとtargetが変わっていないことを読んで確かめる。

## 前回Steps42〜44：記録の更新と新しい確認の入口

新しい製品のテスト・CI・性能測定は行わない。project rootで、次を実行する（`<entry>`・`<binding>` は入口と `binding-06.json` のSHA-256）。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/test_u14_candidate.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py --entry-sha256 56870072810100fa97456ced54a0732e8696489dcb297fa38aa17c0a39978ca7 --binding-sha256 a3d81077e557df7acee86878656360088880b13a75c4c100a68aa748c0450905
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/u14_candidate.py --entry-sha256 <entry> --binding-sha256 <binding>
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md
```

期待する結果：回帰は全件成功・skip 0。今の正式確認コマンド（U11 v2）は、U14の記録の変更で想定どおりexit 1（拒否の理由を記録する）。U14の記録を変える前は exit 0 であることも先に確かめる。新しい入口はexit 0。sensorは2件ともpass。

拒否の回帰で確かめること：U14の記録の別のbytes・欠落、許可外のpath、ほかのcompiled sourceの変更、別のhead、入口とbindingのhashの違い・引数の欠落と順の違い、U11の入口とbinding-05の差し替え、`--logical-child` の分岐のhash検査（R-10）。正の対照も入れる。

## 前回Steps31〜41：費用の測定と、整数SSEのJIT

Step31は実施済み（記録は `verification/loopback1-cost/`。`--baseline-head` には完全なSHA `e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d` を渡した）。人の選択「SSEだけ先に」により、Step35（GPR）とStep36（byte比較）は今回は行わない。

Step31（費用の測定、製品は変えない。project rootで実行）：

```sh
python3 -B scripts/build-u14-cost-profile.py --kind diagnostic --baseline-head e4f84768
python3 -B scripts/build-u14-cost-profile.py --kind acceptance-control --baseline-head e4f84768
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node packages/paludarium-wasm/tests/u14-cost-microbench.mjs target/u14-cost-profile/diagnostic.wasm target/u14-cost-profile/diagnostic.wasm.receipt.json target/u14-loopback1-cost/microbench
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node packages/paludarium-wasm/tests/u14-length-microbench.mjs target/u14-cost-profile/diagnostic.wasm target/u14-cost-profile/diagnostic.wasm.receipt.json target/u14-loopback1-cost/length
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node packages/paludarium-wasm/tests/u14-cost-null-microbench.mjs target/u14-cost-profile/diagnostic.wasm target/u14-cost-profile/diagnostic.wasm.receipt.json target/u14-loopback1-cost/null
```

期待する結果：3つのmicrobenchがexit 0。blockごとの固定費用、命令あたりのinterpreterとJITの費用、block長ごとの時間を `verification/loopback1-cost/` に記録し、Step30のblock長の分布から群ごとのprobe全体の時間の変化を見積もる。前後で正式確認コマンドがexit 0のままであること、製品のファイルが変わっていないことを確かめる。見積りで全部足しても数%以上速くならない場合は、実装に進まず人に相談する。

Steps32〜41の手元のコマンド（project rootで実行）：

```sh
PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node ~/.cargo/bin/cargo test --locked -p paludarium-jit -p paludarium-cpu -p paludarium-wasm
PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node ~/.cargo/bin/cargo test --locked --workspace --no-fail-fast
~/.cargo/bin/cargo fmt --all --check
~/.cargo/bin/cargo clippy --locked --workspace --all-targets -- -D warnings
~/.cargo/bin/cargo build --locked -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu --target wasm32-unknown-unknown
/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u14-*.test.mjs
python3 -m unittest discover -s tests/guests/u14 -p 'test_*.py'
```

期待する結果：

- Step32：整数SSE群の新しい差分ケースが、CIのfresh x86-64 Linuxとinterpreterで一致する（JITを入れる前）。比べるのはXMM0〜15・GPR・RIP・flags。
- Steps33〜34：変更した部品ごとに7件以上、JS境界で8件以上の新しい単体テストが通る。rollbackの400 byte全部の復元、shift数32以上、PACKUSWBの飽和、PSHUFDのimm8、fallback（memory operand・VEX・prefix）、自己書換え、epoch変更、別Workerの変更、evictionを含む。手元の `diff_u8` の `u8_runner_ready` は、x86-64 Linux以外では合格にしない作りなので失敗が残る（既知）。
- Step37：Step30の診断の仕組みでprobeを数え直し、新しい形式がblockに入る割合を記録する。Step31の費用の測定をもう一度行い、見積りと比べる。手元の診断用probeでJITありが遅かった理由を、診断用buildとacceptance-control buildを比べて切り分ける。
- Step38：CI（PR・全品質・U12・U13・fuzz・source-bound）がすべて成功してから、正式な性能測定を1回だけ行う。受理条件は、平均がJITありの方が速く、片側p<0.05、全20回PASS・exit0・30秒以内、JITの実行の証拠があること。
- Step40・41：`mise.toml` は今のbytesに `"npm:npm" = "12.2.0"` の1行を足しただけ。新しい正式確認コマンドがexit 0、拒否の回帰（mise.tomlの別の変更を含む）が全部拒否する。そのあと正式sensor 2件を実行する。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md
```

## 履歴：Step30：JITの効果が出ない原因の診断（Loop-back 1の第1段階）

製品のテスト・CI実行・push・正式な性能測定はない。製品の作業コピーは変更しない。以下のStep29以前の節は履歴であり、今回は再実行しない。

1. 診断の前に、採用済みの正式確認コマンドを実行し、exit 0であることを記録する。

   ```sh
   /Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py
   ```

2. 診断用の数える仕組み（`target/u14-diagnosis/` の下、作業コピーの外）を、命令数が分かっている既存のU14 native fixtureで確かめる。総命令数と形式ごとの数が期待どおりであること、未知の形式が「その他」に数えられること、counterが溢れないことを確かめる。期待どおりでなければprobeの集計に進まない。
3. fixed probe（CI artifact `u11-acceptance-inputs` から取得、SHA-256を記録）を、元argvでnative interpreterで1回実行する。外側の上限は600秒。probeの8項目の結果とexit 0を確かめる。
4. 実行された命令の形式ごとの数、今のJIT対応形式と候補の形式ごとのJITで扱える命令の割合、block長の分布を、`verification/loopback1-diagnosis/` に保存する。
5. 診断の後に、もう一度正式確認コマンドを実行し、exit 0のままであることと、作業コピーの製品ファイルが変わっていないこと（`jj diff --stat` で `crates/`・`packages/`・`.github/`・`tests/` に差分がないこと）を記録する。

## 履歴：Step29：code-summary.mdの固定bytesへの復元

新しいテスト・CI実行はない。code-summary.mdを、正式コマンドが固定したbytesに戻す。復元後、次のコマンドでSHA-256が `223488c21a911afdff961538442e4d6dfe1b8985fe91a7281a2c93c7a8a46edd`、大きさが6746 bytesであることを確かめる（読み取りだけ）。

```sh
shasum -a 256 aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md
```

そのあと、下のStep28節と同じ正式sensor 2件を実行し、採用済みの正式検証コマンドを正式checkpointで実行する。

## 履歴：Step28：記録の更新（R-04・R-05）（作成時の見出しは「今回Step28：記録の更新（R-04・R-05）」）

新しいテスト・スクリプト・CI実行・性能測定はない。code-summary.mdの記録だけを直す。確認は次の正式sensorで行い、そのあと採用済みの正式検証コマンド（`final_candidate.py`、SHA-256 `d799bbb9…`）を正式checkpointで実行する。以下のSteps20〜27などの手順は履歴であり、今回は再実行しない。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md
```

## 履歴：Steps20〜27：JIT性能とU9専用coverage（作成時の見出しは「今回Steps20〜27：JIT性能とU9専用coverage」）

この節が今回の追加実装・検証手順である。以下に保存したSteps15〜19およびSteps8〜14の本文は当時の履歴・継続条件であり、その「今回」や未実装という表記を新しい実行結果と読み替えない。旧手順は一括再実行せず、追加計画のStep20→27を順守する。製品実装・新計測はPlan Approval後。元c9失敗の直接原因未特定、U5 R-05 Minor、現FR8/FR8.3/NFR3/NFR6 GAPを保持する。

### 保存と起動準備（Step20）

変更前plan/instructionsはintent直下 `verification/jit-u9-next/historical-before-plan-revision/` に保存済み。既存proof/失敗原本・旧canonical/bindingを改変しない。新成果物はU14 code-generation配下 `verification/jit-u9-next/`、実行scratchは `target/u14-additional-repair/`。実行ごとに一意run directoryを作り、既存outputがあれば上書きせず停止する。

ツールはproject pinと実体globを区切りで照合し、測定中は更新しない。下の変数は旧節の実体例を現物確認して設定する。Nodeのreadinessはrealpathが実行可能な実体でshimでないこと、`--version` が今回manifestと一致することを確認し、`PALUDARIUM_TEST_NODE`へ同じ実体を明示する。RustはcargoだけでなくRUSTC/RUSTDOC/RUSTUP_TOOLCHAIN/PATHを同じpinへ揃える。新検証候補はこの準備を自分で検査し、旧historical bindingのPATH副作用へ依存しない。

```sh
export PALUDARIUM_TEST_NODE="$U14_NODE"
"$U14_NODE" --version
"$U14_PYTHON" --version
"$U14_CARGO" --version
"$U14_RUSTC" --version --verbose
"$U14_PYTHON" -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/verification/inner-log-diagnostic -p 'test_observer.py' -v
```

元c9の内側stderrは取得できておらず、後から埋めない。新入口はstage名・実argv/cwd・source/compiler/locks、開始終了・exit/signal/timeoutを保存し、子stdout/stderrは失敗時に完全bytes＋SHA/sizeを排他的createで保存して元例外を再送出する。表示tailの省略と原本保存を区別する。成功／check=False／bytes／入れ子例外・timeoutの拒否回帰を含め、成功待ち再実行はしない。

### U9固定集合と集計差（Steps21〜22）

測定前に新 `tests/guests/u9/coverage-scope.json`（未実装）へ以下の具体path集合と各80%を固定する。pathはrepo相対へ正規化し、SF prefixは記録したCI workspaceにだけ対応付ける。未知prefix、path escape、別source、欠落／重複／余分SF、DAの重複・非整数・負count、根拠のないLF/LH差を拒否する。Rust test-only sourceを後から除外したり、二集合を合算して片側不足を隠したりしない。

旧13（初期専用LCOVから固定）：
```text
crates/paludarium-host/src/clock.rs
crates/paludarium-host/src/fs.rs
crates/paludarium-host/src/lib.rs
crates/paludarium-host/src/native_fs.rs
crates/paludarium-host/src/testing.rs
crates/paludarium-kernel/src/files.rs
crates/paludarium-kernel/src/inbox.rs
crates/paludarium-kernel/src/lib.rs
crates/paludarium-kernel/src/signals.rs
crates/paludarium-kernel/src/syscalls.rs
crates/paludarium-runtime/src/lib.rs
crates/paludarium/src/cli.rs
crates/paludarium/src/main.rs
```

追加10（保存023 LCOVとの差集合）：
```text
crates/paludarium-host/src/threads.rs
crates/paludarium-host/src/wasm_tasks.rs
crates/paludarium-kernel/src/epoll.rs
crates/paludarium-kernel/src/events.rs
crates/paludarium-kernel/src/futex.rs
crates/paludarium-kernel/src/null.rs
crates/paludarium-kernel/src/processes.rs
crates/paludarium-kernel/src/sockets.rs
crates/paludarium-kernel/src/threads.rs
crates/paludarium-runtime/src/workers.rs
```

保存023 LCOVのLF/LH予備集計は2766/3292・2174/2415、旧13欠落0だが、16ファイルにDAとの集計差がある。未検証のまま合格へ接続しない。固定LLVMの小fixtureと同じinstrumented binary/profdataでJSON・LCOV・reportを比較して定義を説明する。説明できなければ新専用計測を行い、原本不足を解消するまでGAP。正当な表現差を再現できても、従来の80%定義を有利な分母へ切り替えない。

集計器実装後に7件以上の拒否回帰を実行する（欠落、重複、負値、別head、改変source、compiler/locks不一致、集合の片側不足、LF/LH差、原本digest違い）。既存原本で全来歴が証明できれば新計測とは呼ばず接続修復とする。足りない場合、または最終JIT差分が測定closureを変えた場合は最終署名headで専用jobを再実行する。native guest／env／instrumented CLI／coverage cleanを既存jobと同条件で準備し、0件／ignoreをnative成功にしない。coverageが80%未満なら不足した意味論のテストを追加し、製品変更は実際の不具合に限定する。

### 有限診断・修復と受理順序（Steps23〜27）

Step23は各mode1回、guest30秒／外側180秒、probe8PASS・exit0・timeout=false・cleanup。feature専用site表は16384、space/epoch/RIP/分類でキー化、overflowを別報告し、保持集合のみを順位付けする。新schema3は旧109fields/schema2原本を保持し、正確なfield一覧を固定する。無効feature exports0・通常package import closureを維持する。no-touch回帰は観測前後のentries/LRU/negative hint/prepare・execute/CPU・MMU不変を確認する。

別の実Worker/Wasm microbenchmarkは固定cold/negative/warm、short/max block、epoch変更fixtureを各64chunks×1024operations、chunk両端だけで計時する。CPU結果とcounterで実経路を証明し、時計／loop／観測なし対照・cold resetを含む計時範囲・単位・分母を保存する。native測定やcounterから時間寄与を推定したものをWasm実測と呼ばない。

Step24は実測の償却式 `N*(interpreter-warm-必要epoch費用)>cold生成・prepare` からhotness admissionまたは反復探索削減を選び、閾値・容量・失効・overflowを実装前に記録する。hotness待ちをunsupportedへ恒久登録しない。別Worker/space/epoch、同slot衝突、eviction、counter overflow、後からの昇格を検査する。新ISAが必要ならopcode/幅/flags/fault/native fixture・変更pathを別計画に具体化し、再承認まで停止する。batch・probe固有最適化・常時interpreter化は行わない。

Step25は変更内部部品各7件以上／JS8件以上。JE taken/not-takenのfresh Linux native13と同bytes interpreter／実Wasm CMP+JE（1block/2instructions）、prepare中write、epoch/map/protect/unmap、自己書換え、同slot衝突、budget0/1/63/64/不足、kill/syscall/fault、144byte rollback、bridge例外と配布import／実Wasm helloを確認する。4環境各28比較＋filesystem32、3OS・依存4監査、固定Rust/JS/Python/workspace/U9各80%、変更closureのfuzz各600秒ASan/LSan・MMU4608を維持する。不変原本の再利用はsource/両lock/compiler/flags/suppression/binary一致が条件。

Step26はStep25成功後に背景負荷を止め、同じdiagnostic-off release module/fixed guest/fresh native/headで共通warmup各1＋各mode10回、固定seed/順序と1024符号反転で一度だけ正式評価する。全20回probe全PASS・exit0・30秒以内・実JIT実行・平均改善・片側p<0.05を全て必要とする。失敗や欠測は新outputへ保持し、同binaryの合格待ち再測定をしない。diagnostic-only CIにperformance stepを無条件接続しない。

Step27で新source-bound成果物と原標本を新検証候補へ結合し、旧全predicateを保持する。FR8/FR8.3/NFR6は性能の全条件成立時だけ、NFR3はU9を含む必要品質の全条件成立時だけ更新する。新script自体のexit0を要件達成と呼ばない。sensor・独立レビュー・新コマンド正式採用・正式検証・人の完了確認へ進む。

### 追加Stepsの検証コマンド

ドキュメント根拠／推測の区別：上流LLVMの現行[LCOV exporter](https://github.com/llvm/llvm-project/blob/main/llvm/tools/llvm-cov/CoverageExporterLcov.cpp)では、DAはcoverage iterator、LF/LHはfile summaryから出力される別の経路である。これが今回の差を説明する可能性はあるが、project固定LLVMに対する再現確認は未検証。上流mainの実装を固定版の測定成功の証拠にはしない。

U9集計器の受理仕様を実装する前に、上記LF/LH対DA差をproject固定LLVMで最小fixtureから再現し、同じbinary/profdataからJSON・LCOV・reportを出して対応を確認する。LLVM公式は同じcoverage dataのJSON/LCOV exportを提供する（[llvm-cov export](https://www.llvm.org/docs/CommandGuide/llvm-cov.html#llvm-cov-export)）。この文書だけでは今回の差の原因を説明できないため、正当な表現差なら元の測定定義を維持して両集計を分け、再現根拠を保存する。説明が成立しなければ未検証のまま新しい専用JSON/LCOVと実行ログを取得する。新計測では同一profdataから `cargo llvm-cov report --json` も保存し、二つのファイル集合をそれぞれ集計する。coverageの定義や分母を有利な方へ後から切り替えない。

以下のcargo/node/pythonは、実施前にproject pin・実体globから解決した `$U14_CARGO`、`$U14_NODE`、`$U14_PYTHON` を使う。RustはRUSTC/RUSTDOC/RUSTUP_TOOLCHAIN/PATHも同じpinへ揃える。shellのshimやmise execは使わない。Linux専用コマンドはx86-64 Linux実機CIで実行し、Macの0件を合格にしない。新規チェック名は提案段階・未実装。

```sh
# 実装後の新規集計器回帰（未実装）
"$U14_PYTHON" -B -m unittest discover -s tests/guests/u9 -p 'test_coverage_check.py' -v

# U9の既存ケースとfresh native差分
bash tests/guests/u9/build.sh target/guests/u9
"$U14_CARGO" test --locked -p paludarium-host --test u9_public_api
"$U14_CARGO" test --locked -p paludarium-host --doc Terminal
"$U14_CARGO" test --locked -p paludarium-harness --test diff_u9 -- --nocapture
"$U14_CARGO" test --locked -p paludarium --test command u9_ -- --nocapture

# 現行workflowと同じU9専用計測。既存のnative guest/env/CLI準備も同じjobから継承する
RUST_TEST_THREADS=1 "$U14_CARGO" llvm-cov --locked -p paludarium-host -p paludarium-kernel -p paludarium-runtime -p paludarium -p paludarium-harness --lib --test diff_u9 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|mmu|loader|types|vfs|jit|harness)/' --fail-under-lines 80 --lcov --output-path target/u9-coverage.lcov

# 既存JIT/CPU/Runtimeと実Node bridge。PALUDARIUM_TEST_NODEへ同じNode実体を設定する
"$U14_CARGO" test --locked -p paludarium-cpu -p paludarium-jit -p paludarium-runtime --all-features --lib
"$U14_CARGO" test --locked -p paludarium-harness --test diff_u14 -- --nocapture

# 診断とcontrolは別出力。$U14_HEADは実際に送信・Verified確認した40桁SHA
"$U14_PYTHON" -B scripts/build-u14-cost-profile.py --kind diagnostic --baseline-head "$U14_HEAD"
"$U14_PYTHON" -B scripts/build-u14-cost-profile.py --kind acceptance-control --baseline-head "$U14_HEAD"

# control生成後に配布integrationを起動する。missing inputをskipにしない
PALUDARIUM_U14_CONTROL_WASM=target/u14-cost-profile/acceptance-control.wasm "$U14_NODE" --test packages/paludarium-wasm/tests/u14-cost-profile.test.mjs packages/paludarium-wasm/tests/u14-control-distribution.test.mjs packages/paludarium-wasm/tests/u14-jit.test.mjs

# 同runのfixed guestとfresh native oracle。元source/lockとbuild-copy overlayを分離する
"$U14_PYTHON" -B tests/guests/u10/build.py target/guests/u10 --advisory-policy u14-fixed-aube
sudo unshare --net "$U14_PYTHON" -B scripts/u11-run.py --native-only --guest-dir target/guests/u10 --output target/u11/native

# 各mode1回の診断、正式性能とは別の新ディレクトリ
"$U14_NODE" packages/paludarium-wasm/tests/u14-cost-profile-check.mjs target/u14-cost-profile/diagnostic.wasm target/u11/native/observations.json target/guests/u10 target/u14-additional-repair/diagnostic

# 新規の実Worker/Wasm chunk測定入口（未実装）。既存固定probeの性能受理とは別
"$U14_NODE" packages/paludarium-wasm/tests/u14-cost-microbench.mjs target/u14-cost-profile/diagnostic.wasm target/u14-cost-profile/diagnostic.wasm.receipt.json target/u14-additional-repair/microbench

# 品質成功後に一度だけ。4引数は同runで作ったcontrol/module・oracle・guest・新output
"$U14_NODE" packages/paludarium-wasm/tests/u14-performance-check.mjs target/u14-cost-profile/acceptance-control.wasm target/u11/native/observations.json target/guests/u10 target/u14-additional-repair/performance
```

oracle/guestパスは既存 `.github/workflows/u14-wasm-acceptance.yml` のproducer/性能起動と照合済み。CLI引数の静的照合であり、新headでの実行は未検証。missing inputは停止する。新microbenchmarkはcold/negative/warmとshort/max blockを固定fixtureで測り、各64chunk×1024operation、両端でのみ時刻を取る。冷状態の準備やscratch resetは計時対象へ含めるか別列にするかをschemaで明記し、1回と1024回を取り違えない。counterとCPU結果から実経路を確認し、報告する時間には単位・分母・計時範囲を持たせる。観測・loop費用の対照も保存する。新入口は未実装であり成功と記録しない。coverageは計測前cleanとinstrumented CLI/native環境の準備を含む既存job全体を再現し、単独行だけを別環境で走らせて同条件と呼ばない。

U9新規集計器は次のCLIを実装して回帰する（現時点では未実装）。scopeは旧13/追加10の具体pathと80%を固定、evidence manifestはhead/run/job/artifact digest・実行コマンド/exit・compiler・両lock・source before/afterを持つ。LCOVだけを渡して来歴成功を主張できるモードは作らない。

```sh
"$U14_PYTHON" -B scripts/u9-coverage-check.py --lcov target/u9-coverage.lcov --scope tests/guests/u9/coverage-scope.json --evidence target/u9-coverage-evidence.json --output target/u9-coverage-verdict.json
```


## 旧Steps15〜19の手順（履歴原文を保持）

## 履歴：Steps15〜19：観測用診断だけ（作成時の見出しは「今回Steps15〜19：観測用診断だけ」）

今回の実行範囲は1block方式を維持したno-touch観測、同source診断/control build、有限1回ずつの診断と品質確認だけである。後続Steps8〜14のコマンドは既存の実施記録・継続条件であり、正式性能20標本を再実行する許可ではない。batch、新命令、受理条件変更は別の実装計画承認が必要。cd2/a8/b79/13753の失敗原本と凍結canonical/bindingを変更しない。

開始時はmise設定と実体globで最新・project pinを照合し、測定中は版を変えない。現在確認済みのPython3.15/Node26.12の実体とproject Rust pinを使う以下の変数を各独立したshell行で設定する。更新が必要なら区切りで設定/lock/回帰影響を提示し、shim/mise execへ戻さない。Rustはrust-toolchain.tomlのpinを保持する。

```text
U14_PYTHON=/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3
U14_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node
U14_CARGO=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-11-aarch64-apple-darwin/bin/cargo
U14_RUSTC=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-11-aarch64-apple-darwin/bin/rustc
U14_INPUT=aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/jit-repair/ci-cd2de605/quality/u11-acceptance-inputs
```

内部部品は実装後の層ごとの回帰とする。次RIP peekはno-touchで、entries/LRU/negative hint/prepare・execute回数/ID/CPU state/世代が前後不変かを各変更部品7件以上で確認する。実際の1block実行からchainを集計し、仮想の連鎖をdecode/実行して作らない。interpreter介在、別space/epoch、衝突/eviction、missing、budget/kill、終了時flush、counter overflow/private collector並列を含める。新schema/version2と正確なfield一覧を固定し、旧88field/version1を履歴と分ける。JS8件以上で旧版/欠落/重複/非整数/overflow/別receipt/source/module、無効featureを拒否する。

```text
env RUSTC="$U14_RUSTC" RUSTC_WRAPPER= PALUDARIUM_TEST_NODE="$U14_NODE" "$U14_CARGO" test --locked -p paludarium-cpu -p paludarium-jit -p paludarium-runtime --all-features --lib
env RUSTC="$U14_RUSTC" RUSTC_WRAPPER= "$U14_CARGO" check --locked --manifest-path fuzz/Cargo.toml --bins
"$U14_NODE" --check packages/paludarium-wasm/tests/u14-cost-profile-check.mjs
"$U14_NODE" --test packages/paludarium-wasm/tests/u14-cost-profile.test.mjs packages/paludarium-wasm/tests/u14-jit.test.mjs
"$U14_PYTHON" -B -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py' -v
```

Linux専用U3/native回帰を含むfeature集合は、既存jit-coverage jobと同じfresh native生成/profile/環境変数4件を用意して実行する。macOS上の既存ignore/0testをLinux実測へ読み替えない。既存packed-distribution.test.mjsはU11_NPMを要求し、旧U11 module SHAへ固定されているため、その旧成功はcanonicalの歴史検査で保持する。新control moduleの配布境界は、既存診断test内に明示入力PALUDARIUM_U14_CONTROL_WASMを受けるimport/実Wasm hello/自然cleanup回帰を追加して検査する。旧U11期待hashを新moduleへ置き換えず、単なるimport成功で実起動を代替しない。

同じ変更sourceから両buildを作る。builderの現行CLIは`--kind diagnostic|acceptance-control`と`--baseline-head <40hex>`のみである。localはGITHUB_SHAを偽装せずlocal:<sourceDigest>とcd2 baselineを分離する。buildは旧record内原本を変更せず、target内のkind別出力を使う。

```text
"$U14_PYTHON" -B scripts/build-u14-cost-profile.py --kind diagnostic --baseline-head cd2de60517151445010e2b2ecf28684dc1f1b1a5
"$U14_PYTHON" -B scripts/build-u14-cost-profile.py --kind acceptance-control --baseline-head cd2de60517151445010e2b2ecf28684dc1f1b1a5
"$U14_NODE" --input-type=module -e 'import assert from "node:assert/strict"; import {readFileSync} from "node:fs"; import {createHash} from "node:crypto"; const load=n=>JSON.parse(readFileSync(`target/u14-cost-profile/${n}.wasm.receipt.json`,"utf8")); const d=load("diagnostic"),c=load("acceptance-control"); assert.equal(d.source_digest,c.source_digest); assert.deepEqual(d.source_files,c.source_files); assert.deepEqual(d.locks,c.locks); for(const n of ["diagnostic","acceptance-control"]){const bytes=readFileSync(`target/u14-cost-profile/${n}.wasm`);assert.equal(createHash("sha256").update(bytes).digest("hex"),load(n).module_sha256);const e=WebAssembly.Module.exports(new WebAssembly.Module(bytes)).filter(x=>x.name.startsWith("u14_cost_"));assert.equal(e.length,n==="diagnostic"?6:0);} console.log("same-source receipts/module SHA and control diagnostic exports0 PASS");'
```

新runnerの4位置引数は現行parserと同じである。現cd2のu11組はprobe f09911e4…、aube c7bb2b5d…、oracle689c606c…であり、異なるu13組を混ぜない。module/source/locksとguest/oracleの実SHAをreceiptと照合してから、背景の重いbuild/testを止め、以下を1回だけ実行する。

build後、診断実測に重ねず、先に追加する同source controlの配布境界回帰を実行する。以下の環境変数は今回追加するtest入力契約であり、既存CLIの新引数ではない。入力欠落をskip成功にしない。

```text
env PALUDARIUM_U14_CONTROL_WASM=target/u14-cost-profile/acceptance-control.wasm "$U14_NODE" --test packages/paludarium-wasm/tests/u14-cost-profile.test.mjs
```

```text
"$U14_NODE" packages/paludarium-wasm/tests/u14-cost-profile-check.mjs target/u14-cost-profile/diagnostic.wasm "$U14_INPUT/target/u11/native/observations.json" "$U14_INPUT/target/guests/u10" target/u14-prepared-chain-v2
```

各modeはfresh factory1回、guest30秒・外側180秒、probe8PASS/exit0/timeout=false、kill/reap/cleanup。interpreter側のJIT counter混入を拒否する。観測原本・supervisor・診断/control receiptsを新record証拠directoryへfile toolで保存し、旧88field/旧診断を上書きしない。追加counterで測るのは率/回数/bytes/停止理由であり、約0.70秒の時間費用・速度改善・p値の証拠ではない。時間寄与とbreak-evenが根拠不足ならbatchへ進まず、次の診断提案だけを返す。

固定80%は旧JIT5files、追加CPU/JIT/runtime feature集合、JS6files、Python6files、workspace/U1集合を維持し、変更診断codeを除外しない。Rust coverageは既存workflowのfresh native前提を満たすLinux診断専用CIで次を行う。actual cargo-llvm-covもmise実体を解決し、PATHをactual tool directoriesへ限定して`cargo llvm-cov`を使う。Python coverage moduleは既存project内target/u14-overlay-toolsの実体を使用し、不在ならproject設定を確認して復旧する。

```text
cargo llvm-cov --locked -p paludarium-jit --all-features --lib --fail-under-lines 80 --lcov --output-path target/u14-jit.lcov
cargo llvm-cov --locked -p paludarium-cpu -p paludarium-jit -p paludarium-runtime --features u14-cost-profile --lib --fail-under-lines 80 --lcov --output-path target/u14-cost-profile.lcov
env PYTHONPATH=target/u14-overlay-tools "$U14_PYTHON" -B -m coverage run --data-file=target/u14/python.coverage --include='*/scripts/u14-run.py,*/scripts/build-u14-cost-profile.py,*/tests/guests/u14/guest_policy.py,*/tests/guests/u14/lock_overlay.py,*/tests/guests/u10/build.py,*/tests/guests/u10/evidence.py' -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py'
env PYTHONPATH=target/u14-overlay-tools "$U14_PYTHON" -B -m coverage report --data-file=target/u14/python.coverage --fail-under=80
env PYTHONPATH=target/u14-overlay-tools "$U14_PYTHON" -B -m coverage json --data-file=target/u14/python.coverage -o target/u14/python-coverage.json
```

必要な外部実行は具体manifest/diffを提示して親が署名送信・Verified/head/bytesを照合する。新診断専用workflowは既存native/3OS/依存4監査/4環境各28比較/固定coverage/変更closure13fuzz各600秒/MMU4608の必要jobを接続するが、正式performance stepを持たない。旧fullqualityをそのまま起動すると正式20標本も走るため、今回は起動しない。不変証拠の再利用はsource/locks/compiler/flags/suppression/binary一致を明記し、成立しなければ該当品質検証を新sourceで行う。新診断や品質検証は正式性能の合格を意味しない。FR8/FR8.3/NFR6と旧全失敗・u9不足を保持し、batch/新命令/正式性能受理は別の計画承認へ進める。

## 既存Steps8〜14：性能・JE・親FR8（履歴と継続条件）

以下は追加修復の実行手順。後続の初回構築／overlay手順は履歴と継続条件として保持する。現在の計画承認と内容確認後に実行し、診断値・初回性能失敗・修復後の受理測定を分離する。Testing Contractのcustom順序、固定80%、guest30秒、MMU4608 bytes／各600秒ASan/LSanを維持する。

既存runner準備は、project固定Rust/Node/Pythonの実体を解決して、次の対象限定入口で行う。`cargo`等の表記は実体を指す。Linux専用差分のmacOS上0件を成功にしない。

```text
cargo test --locked -p paludarium-jit --lib u14_ -- --list
cargo test --locked -p paludarium-harness --test diff_u14 -- --list
node --check packages/paludarium-wasm/tests/u14-jit.test.mjs
python3 -B -m unittest discover -s tests/guests/u14 -p test_validation.py -v
```

JE fixtureとcase対応を先に13件へ整合し、既存U14 native専用CIで新`je-zf1-taken`／`je-zf0-not-taken`の原本を取得してから性能修復へ進む。JNE旧名も実条件へ合わせ、faultはcase名で選択する。CIのnative処理は元のnetwork namespace・30秒制限・同じguest/引数/flags maskを保持する。fixtureのsource、compiler、binary、case bytesとrawを保存する。

診断用の新入口は作成後に`node --check packages/paludarium-wasm/tests/u14-cost-profile-check.mjs`で準備を確認する。CLIは既存性能runnerと同じ4引数に揃える。

```text
node packages/paludarium-wasm/tests/u14-cost-profile-check.mjs <diagnostic-module> <fresh-native-observations.json> <guest-dir> <diagnostic-output-dir>
```

probe各mode1回・guest30秒・kill/reap/cleanup。診断counterはnegative hit/miss、epoch失効、LRU更新、compile数/時間、JS遷移、block長、checkpoint数を含める。無効時の計測不在と診断専用feature/build/出力を検査する。診断receiptは受理runnerが拒否する。内部collector7件以上と、新runnerの正常・欠落項目・別module/head・timeout・失敗・cleanup等7件以上を実装後に検査する。runner回帰は既存U14集約入口から実行する。

性能修復は診断で確認した費用へ限定し、既存decode情報による事前選別、negative LRU削減、warm bridge遷移削減を順に検証する。共通の命令対応条件、prefix/operand幅、negative epoch失効、eviction/clock exhaustion、JS cache miss/改変bytes/例外rollback、生成中write・他Worker変更・mapping変更を含む各変更部品7件以上・JS8件以上を追加する。budget実命令数化が必要な場合は0/1/63/64/残予算未満、syscall/kill/faultの境界を検査し、既定CodeCache利用側の互換を保つ。共有epoch/lockを省かない。

```text
cargo test --locked -p paludarium-jit --lib u14_ -- --nocapture
cargo test --locked -p paludarium-cpu --lib u14_ -- --nocapture
cargo test --locked -p paludarium-mmu --lib u14_ -- --nocapture
cargo test --locked -p paludarium-runtime --lib u14_ -- --nocapture
node --test packages/paludarium-wasm/tests/u14-jit.test.mjs
python3 -B -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py' -v
cargo test --locked -p paludarium-harness --test diff_u14 -- --nocapture
```

`PALUDARIUM_TEST_NODE`はprojectのNode実体へ指定し、bridge内のNode不在をskip成功へしない。JE実Wasm回帰はCMP+JEのみで1block/2instructionsを必須にし、ZF=1でtarget、ZF=0でfallthroughのRIPとflagsをinterpreterへ照合する。Linux差分では13ケースすべてのnative/interpreter/JITを同じIDへ結合し、partial/fallback-only成功を拒否する。

修復後の署名headで、既存4環境runner各28比較と固定coverage入口を実行する。診断featureを無効にした同一release module/guestで、既存`u14-performance-check.mjs`の各10回・固定seed/順序/warmup・1024符号反転・平均改善かつ片側p<0.05を維持する。全20回probe全PASS/exit0/30秒以内・実JIT実行証拠を要求する。初回13753b14と後続b79の失敗は保持し、同binaryで合格待ち再試行しない。全標本、背景負荷、module/head/guest/locks、compilerとツール版を保存する。

新JIT2 fuzzと依存変更した既存対象は既存U14 fuzz workflowで各600秒ASan/LSanを逐次実行する。除外・suppressionを増やさず、再利用は全入力・compiler・binary等の一致が立証できる対象だけに限定する。Rust/JS/Python/workspace各固定分母80%を維持し、変更診断/選別コードを分母から外さない。追加source/test/config/CIはmanifestに含め、旧canonicalと全旧検査を保持して変更後の新source用checkerを独立レビューと別のコマンド承認へ渡す。

親FR8はFR8.1/8.2/8.3の集約とし、性能未達中はFR8/FR8.3/NFR6をGAPへ揃える。JEも上記実行が未完了なら未検証とする。対応表の親欠落、誤集約、性能失敗をOKにする改変を拒否する検証を追加し、`aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/traceability.json`で正式確認する。sensorsのGAPは性能合格の代替にしない。u9専用coverage不足は別に保持する。

## Runnerと準備

既存runnerはRust cargo testとNode test runner。実装前の準備確認コマンドは `cargo test -p paludarium-jit --lib`（既存NoopCodeCache5件）。project固定Rust実体を解決して実行し、最新確認と更新は計画Step1で記録する。新テストがまだない段階の0件・skipを成功証拠にしない。

## U14限定コマンド

- 内部4部品：`cargo test -p paludarium-jit --lib u14_`。
- 共有接続：`cargo test -p paludarium-mmu --lib u14_`、`cargo test -p paludarium-runtime --lib u14_`。
- native差分：`cargo test -p paludarium-harness --test diff_u14 -- --nocapture`。
- JS境界：`node --test packages/paludarium-wasm/tests/u14-jit.test.mjs`。
- guest/4環境：`python3 -B scripts/u14-run.py --environment <node|chromium|firefox|safari> --wasm <module> --native <fresh-native-observations.json> --guests <guest-dir> --output <output-dir>`。
- 性能：`node packages/paludarium-wasm/tests/u14-performance-check.mjs <module> <fresh-native-observations.json> <guest-dir> <output-dir>`。
- 固定coverage：`.github/workflows/u14-quality.yml` の `jit-coverage`／`u14-python-coverage` と `.github/workflows/u14-wasm-acceptance.yml` の固定JS coverage。
- U14 fuzz：`.github/workflows/u14-fuzz.yml` の13対象（旧11＋U14 2対象）、各600秒。
- 検証器：`python3 -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py'`。

新入口はStep2/6で作成する予定で、現在は未実装。入口はそのUnitの対象だけを実行し、内部で既存共有検査を必要に応じて一度実行する。包括的なcargo testやnpm testをUnitごとの通常コマンドへ入れない。

## テスト数と境界

内部4部品各7件以上（計28以上）。統合10件以上には自己書換え・他Workerの世代変更・生成中変更・ページ跨ぎ・mapping再利用・権限・部分fault・syscall・kill/trapを含める。命令差分は対応命令表と1件以上/命令の割合を記録する。4環境それぞれ14実guestケース以上をjit:false/trueで比較し、probe全項目を必須にする。fallback-onlyをJIT実行と数えない。

## データと測定

Linux実機で各CI実行時に期待結果を生成し、固定guest/module/head/両lockを一致させる。未定義flagsのみ既存表で除外する。mockは生成失敗などの内部境界に限定し、実wasm・実Worker・本物Safariの代替にしない。guestごとの30秒とkill/reap/cleanupを維持する。

Rust JIT crate（追加全製品ファイル）、変更JSとPython固定対象、および既存workspaceは行coverage80%以上。wasm専用経路はNode V8/実wasmテストの対象を別に固定して報告しnative coverageで検証済みにしない。測定対象一覧・生データ・分母・集計器を保存する。

## 性能・sanitizer

計画の片側対応あり正確ランダム化検定を測定前に固定する。全probeをNode WorkerでJITあり/なし各10回、全20回成功、平均改善かつp<0.05で合格。instrumentationのない実行を性能対象にする。新JIT fuzzおよび依存変更した既存対象は各600秒ASan/LSan、MMU最大入力4608バイト。compiler/binary/依存/設定の一致を証明できる旧対象だけ限定再利用する。

## 固定guest限定advisory例外の回帰

承認済み例外はU14専用設定でcrates.io unsafe-libyaml 0.2.11のRUSTSEC-2024-0449だけに適用する。`python3 -m unittest discover -s tests/guests/u14 -p 'test_guest_policy.py'`で10件以上の境界（正常、別ID、版、パッケージ、source、lock重複、root設定改変、生成設定/hash改変、他advisory失敗の伝播）を検査する。既存U10設定と証拠検査の回帰を維持し、製品deny.toml/probe/source/lockの不変を照合する。旧CDLA限定条件を完全に継承し、Linux CIで依存4監査とguest14＋元argv14比較を再確認する。これらはまだ未実装であり、例外を加えた設定の成功を無例外の監査成功と表現しない。

## U14限定rustls lock overlay修復

計画Step 2の追加内部境界。新 `tests/guests/u14/lock_overlay.py` と変更 `tests/guests/u10/build.py`／`evidence.py` を実装した後に、正常1 package更新と14件以上の拒否回帰を追加して実行する。guestプログラム期待値は更新binaryの実機Linuxで先に取得し、後続JIT実装・差分と比較する。Testing Contractのcustom順序を変えない。

元aube source/tag/revisionと元Cargo.lock SHA256 `8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668` を保存する。U14ビルドコピーだけ、rustls0.23.45→0.23.46のversion/checksum2行を更新し、overlay SHA256 `b8d403f2c449da8eb104cca0cbd1c9f1f61ade8249615c246ae6cc8cd531db0e` と604中1 package差分を検証する。checksumは `48e13bd8c0e9365c43cfa5c9e8f9ad49d3c8444926c9aac819e0e4dc503c8fdf`、crates.io source・依存一覧・他603 packageは不変。設定は `tests/guests/u10/source-lock.json` の別U14 overlay項目に固定し、既存aube元lock設定を変更しない。

receiptは元source/元lockとbuild source/build lockを別のsnapshot/digestで保持し、前後不変とコピー間の許可差分を両方検証する。旧receipt・U14以外の通常経路を維持し、元lockとoverlayの取り違えを拒否する。metadata・cargo-deny・cargo build --lockedは新lockへ束縛し、ignoreは既存RUSTSEC-2024-0449だけ。新4rustls advisoryも他の新advisoryも除外しない。

限定コマンド：

- overlay拒否回帰：`python3 -B -m unittest discover -s tests/guests/u14 -p 'test_lock_overlay.py'`。
- 既存U14 policy：`python3 -B -m unittest discover -s tests/guests/u14 -p 'test_guest_policy.py'`。
- U14集約入口：`python3 -B -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py'`。既存34件と追加overlay回帰を含める。
- 共有証拠の対象限定回帰：`python3 -B -m unittest discover -s tests/guests/u10/runner-tests -p 'test_evidence.py'`、`python3 -B -m unittest discover -s tests/guests/u10/runner-tests -p 'test_policy.py'`。
- Python固定分母：`python3 -B -m coverage run --data-file=target/u14/python.coverage --include='*/scripts/u14-run.py,*/tests/guests/u14/guest_policy.py,*/tests/guests/u14/lock_overlay.py,*/tests/guests/u10/build.py,*/tests/guests/u10/evidence.py' -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py'`、`python3 -B -m coverage report --data-file=target/u14/python.coverage --fail-under=80`、`python3 -B -m coverage json --data-file=target/u14/python.coverage -o target/u14/python-coverage.json`。`.github/workflows/u14-quality.yml` のU14 Python coverageも同じ対象に固定する。新helperと変更build/evidenceを分母から除外して成功させない。

拒否対象は元lock/source digest不一致、rustls重複/欠落、旧新版違い、registry/checksum違い、別package・依存一覧変更、更新lock digest違い、U14以外への適用、receipt元/更新lock取り違え、元/build source改変、ignore追加、他advisory失敗伝播の14件以上。検査設定・snapshot・coverage下限・guest30秒process-group cleanupを弱めない。

更新guest buildはU14専用CIで依存4監査を先に通し、同じ新binaryをfresh Linux native14＋元argv14、命令11、4環境それぞれ14ケース×JITなし/あり、各10回性能へ渡す。新binary/module/headと元/overlay/workspace/fuzz各lockを証拠へ固定する。Rust/JS/Python/workspace80%以上、新JITと依存変更した既存対象600秒ASan/LSanを維持し、旧実測は履歴と区別する。更新guest・監査・全比較・coverage・性能・sanitizerの成功は実行前には未検証とする。

## 完了証拠

コマンドと実exit、テスト名/件数/skip、ソースと原本hash、署名済みCI全ジョブ、測定全標本を照合する。現行実行・履歴・未検証を分け、独立レビュー後に新最終確認コマンドを提示する。

