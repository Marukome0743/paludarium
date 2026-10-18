# JIT性能とU9専用coverageの追加修復案

## 位置付けと保存対象

2026-10-16 JST。人のRequest Changes「JIT性能未達とU9専用coverage不足の両方を修正。旧検証と失敗記録を保持し、具体的な計画と検証手順を提示」に対する承認前の提案。製品修復・新診断・性能再測定はまだ開始していない。現在の順序では共有ソース変更後のU1再確認が先に要求されているため、この別文書を用意し、U14の正式plan/instructionsへの追加はその再確認後に行う。旧Steps1〜19の本文を消したり、過去の未達を成功に読み替えたりしない。

開始前に現行plan/instructions/summary/traceability/source-manifestと正式検証proofを、新しい証拠ディレクトリの履歴領域へ完全bytes保存する。13753b14、b79、a8、cd2、02375d54の失敗・診断・CI原本、元guest source/lock、build-copy overlayを保持する。現行canonical `verification/diagnostic-v2/current-verifier/verify.py`、binding、歴史投影、過去canonical一式は変更しない。新ソースの検証候補は別入口・別bindingとし、採用は改めて人の選択を受ける。

## 現在の根拠と未確定事項

追加診断後の状態：診断専用の直接実行と、同じ正式checkpoint起動の双方が成功した。正式側はproof79edf727、exit0・stderr0・証拠不変。元c9失敗の内側エラーは再現せず、直接原因は未特定。新たに再現したNode実体指定不足と捕捉stderrの未表示は修復対象として具体化したが、元失敗との同一性は主張しない。製品JIT性能の追加実装・正式20標本・U9再測定は未着手。

U1再確認の正式検証は2026-10-16 01:31:19〜01:40:32 JSTにexit1となった。proof `c9f79b0b-3d66-4ab6-9eca-1cf917579aaf` と証拠不変=trueを `verification/jit-u9-additional-repair-u1-failure.json` に完全保存した。外側verify.pyがhistorical.py fullの非0終了を受けたことだけが分かり、内側stderrは外側出力に伝播していない。原因未特定。先のU14正式検証exit0を今回U1の成功へ読み替えない。既存canonicalを書き換えず、別の診断入口で内側のstdout/stderr/exitを段階ごとに保持して切り分ける手順を、正式な追加計画の前提作業にする。成功待ちの無差別再試行は行わない。

- 検証済み：最新正式性能cd2はinterpreter平均5.581792195100001秒、JIT6.2825898274秒、約12.555%遅く、片側p=1。02375d54は正式性能未測定。
- 検証済み：02375d54の有限診断は100388 blocks、次のprepared block16、連続最大2。batchは中止を維持する。次RIPのmissingをunsupportedとは断定しない。
- ドキュメント根拠：CPUのDecodeCacheはRIP/epoch付きdirect-mapped cache、Runtimeは既存decode情報でeligibleを判定し、bridgeはcold時snapshot/extract/emit/prepare、warm時execute_readyを行う。MMU epoch・lock・rollbackは必要な意味論であり省略しない。
- 検証済み（予備集計のみ）：署名02375d54／run38761233683の保存済み専用 `quality/u9-coverage-lcov/u9-coverage.lcov` は23ファイルを含む。旧13は2766/3292行、追加10は2174/2415行で、旧13欠落なし。これはLF/LH予備集計であり、DA行・実行条件・測定対象・ソースへの独立結合が終わるまではU9 GAPを解消しない。
- 検証済み（集計境界の追加調査）：同LCOVの16ファイルでLF/LHとDA行の単純集計が異なり、素朴な一致assertは失敗した。例：host/lib.rsはLF/LH=228/187、DA=224/185。原因は未特定で、LLVMの正当な表現差とも原本不備ともまだ判定しない。この不一致を無視して合格にする検証器は作らない。
- 未検証：性能の時間寄与、fallbackの頻出site別分布、U9専用coverageの全ての受理条件。全体coverageと専用coverageを代用しない。

## 実施順序と成果物

正式計画への追加案は次のSteps20〜27とする。既存Steps1〜19は履歴と判定を保持する。U1再確認は人が承認済み、現在は共有CPU変更後のU2再確認が先行している。以下は正式U14 plan/instructionsへ取り込むための具体案であり、まだ製品実装の承認は記録されていない。

| 追加Step | 固定する成果物 | 合否・先へ進む条件 |
|---|---|---|
| 20 基準と起動準備 | 新履歴保存、source/lock/compiler/Nodeのmanifest、Node実体readiness、子ログ保存仕様 | 旧canonical/binding/失敗proofのSHA不変。Node実体未指定・shim・別versionは開始前失敗。原c9原因未特定を保持 |
| 21 U9集計仕様 | 固定13/追加10 scope、LCOV/JSON/report比較、専用集計器と拒否回帰 | 旧13欠落0、追加集合との重複0、同じbinary/profdataの定義を説明できること。不明なLF/LH対DA差を無視しない |
| 22 U9不足取得 | 同headの専用raw、実コマンド/exit、nativeケース、source before/after | 13集合と10集合の双方80%以上。必要入力と実行条件が保存原本で不足する場合だけ追加取得。最終修復で依存が変われば再測定 |
| 23 JIT有限診断 | schema3 site/counter原本、対照付きWorker/Wasm chunk測定、償却表 | 各mode1回・全8PASS/exit0、30秒/180秒とcleanup。時間寄与を計測していないcounterから捏造しない |
| 24 最小性能修復 | 選択したhotness/negative lookupの具体差分と固定閾値 | 一般的なpolicy、epoch/space/Worker分離、正確budget/rollback。必要な新ISAが未特定なら別計画に戻る |
| 25 正しさと品質 | 部品回帰、JE/native、4環境、3OS、固定coverage、必要fuzz原本 | 既存品質下限維持。0件/skip/別sourceを合格にしない。全20標本の性能受理はまだ実行しない |
| 26 正式性能 | 新headで固定20標本の初回report | 同一diagnostic-off module/guest、全PASS、実JIT実行、平均改善かつ片側p<0.05。失敗なら保存して修復計画へ戻る |
| 27 証拠結合 | 新current verifier候補、旧023読取投影、更新trace/summary/manifest | 旧全predicateを保持。独立レビュー・新command採用・正式実行・人の完了確認。exit0と全要件達成を区別 |

前提の検証起動修復候補：Node実体の指定をreadinessで必須化し、`PALUDARIUM_TEST_NODE`を固定する別入口を用意する。限定診断で、未指定かつshim解決時はU14 102件中1失敗、明示した26.12.0実体では102件成功を確認した。旧b79 bindingが26.11.1をPATHへ追加する副作用へ現在の試験準備を依存させない。さらに捕捉した子stdout/stderrを例外時に保存・表示する。旧canonical/bindingは保持する。診断付き全実行は成功して元c9失敗を再現していないため、元失敗の直接原因をこのNode不足と断定しない。失敗原因の未特定と、新たに再現した起動前提不足を分けて扱う。

1. **基準固定と履歴保存**。署名head、全変更path、source closure、workspace/fuzz両lock、Rust/compiler/LLVM、Node/V8、Python、coverage集計器を固定する。最新情報とproject pinを作業の区切りで照合し、測定中は更新しない。旧検証proof79d569f4のexit0とevidence_unchanged=trueは過去の実行として保持する。

2. **U9の測定と検証器の接続不足を切り分ける**。旧13ファイル集合を初期LCOVから固定し、追加10集合を別に固定する。新規 `scripts/u9-coverage-check.py` と `tests/guests/u9/test_coverage_check.py` を作る。まず保存済み02375d54原本の独立監査を行い、公式artifactのhead/run/job/digest、全source before/after、compiler/locks、diff_u9の実行件数と実exit、測定コマンド、LCOVの各SF/DA、欠落・重複・非整数・負count・LF/LH整合を確認する。13集合と10集合を各80%以上で別判定し、分子分母・全ファイル別結果・未実行行を出力する。総合23集合だけで片側の不足を隠さない。元130追加行の旧専用指標も歴史として保持し、現在の行番号へ機械的に流用しない。

3. **不足したU9証拠だけを追加取得**。Step2の全条件が保存済み原本で成立すれば、現行headについて証拠接続を修復し、新規測定とは呼ばない。最終JIT修復でU9測定closureが変わる場合、または必要な実行条件が原本に無ければ、最終署名headで既存専用測定を再実行する。80%未達なら未実行行のU9意味論に対応するテストを追加する。対象はHost/Kernel/Runtime/CLIの端末API、stdin短read/EOF、stdout/stderr、isatty/ioctl、bad fd/pointer/request、dup、PTY cleanup、公開constructor/compile_fail。閾値引下げ・ファイル除外・0件/skip成功は行わない。製品不具合が無ければcoverageのためだけに製品を変えない。

4. **JIT費用を有限に切り分ける**。既存feature専用診断に、already-decoded boundaryの分類、negative-hintの再利用/衝突、cold snapshot/extract/emit、prepare、warm executeの件数を追加する。siteキーはaddress-space/epoch/RIP/分類、固定容量16384、overflowを別計数する。ランキングは保持した集合に限定し、overflow時は全体の頻出順位と断定しない。既存CPU/MMU/flags、LRU、module ID、prepare/execute回数を観測のために変更しない。未対応命令の追加実装や新たなmemory readを診断へ混ぜない。時刻取得は命令ごとに入れず、別の限定microbenchmarkで各段階を1024回のchunk単位で測る。fixtureはcold/negative/warm、短block/既存最大block、epoch変更を固定し、時計費用と観測有無の対照を保存する。nativeの速度をWasmの時間寄与と呼ばず、実Worker/Wasm経路を測る。probeは診断各mode1回、guest30秒・外側180秒・全8PASS/exit0・cleanupを維持する。

5. **確認できた費用に対する既存ISA内の修復**。第一候補はcold/短blockのcompile・prepareを償却できない問題への一般的なhotness admission、第二候補はnegative hint/DecodeCache衝突による反復探索の削減。`N × (interpreter費用 − warm実行費用 − epoch等の必要費用) > cold生成・prepare費用` を満たせるか、Step4の実測で候補を選ぶ。数値・閾値・bounded cache容量・失効条件を実装前に記録する。hotness待ちはdeterministic unsupportedと区別し、後からJITへ昇格できるようにする。address-space/epoch変更、eviction、counter overflow、別Workerで状態を混用しない。probe/ELF名や既知RIPの特別扱い、jit:trueを常時interpreterにする回避は行わない。既定CodeCache利用側の契約、実命令数budget、kill/syscall/fault境界、144byte rollbackと共有lockを維持する。

   この段階で十分な改善の根拠が得られなければ、修復を済んだことにしない。頻出unsupported命令の追加が必要なら、具体的なopcode/operand幅/flags/例外/memory意味論、native差分fixtureと変更pathを別計画にして承認へ戻す。今回の提案は未特定ISA追加とbatch実装の包括承認を求めない。

6. **正しさと品質を先に確認**。変更部品ごと7件以上、JS変更時8件以上、U9検証器は欠落/重複/別head/別source/coverage不足等の拒否回帰を用意する。JE taken/not-taken、prepare中write、epoch/map/protect/unmap、自己書換え、同slot衝突、budget0/1/63/64/不足、kill、syscall、fault、bridge例外を確認する。実WasmをNode実体へ必ず結び付け、skipを成功にしない。fresh Linux native13、4環境各28比較＋filesystem32、3OS、依存4監査、固定Rust/JS/Python/workspace/U9各80%を維持する。変更依存closureのfuzzは各600秒ASan/LSan、MMU4608byte上限を維持する。不変対象を再利用する場合はsource/lock/compiler/flags/suppression/binary一致を示し、成立しない対象だけ再実行する。

7. **新headで正式性能を1回評価**。Step6成功後、同一の診断無効release module・fresh native oracle・固定probeを使い、既存runnerでwarmup各1、各mode10回＝全20標本を1回だけ取得する。固定seed/順序/1024符号反転、全probe成功、実JIT実行、30秒制限、平均改善かつ片側p<0.05を維持する。先に背景負荷を止め、同一module/head/guest/locksと版・負荷の記録を保存する。同binaryで合格待ち再試行はしない。失敗・欠測・timeoutはそのまま保存して原因と次の差分計画へ戻し、初回や中間失敗を置換しない。

8. **証拠と対応表を更新して独立確認**。旧canonical/bindingと旧失敗を全て保持した別の新検証候補を作る。U9二集合、最終source-bound実行、正式性能原標本、rollback/JE、各品質と過去全predicateを新候補へ結合する。FR8/FR8.3/NFR6は新性能の全受理条件を満たした場合だけ、NFR3はU9を含む必要な全品質条件を満たした場合だけ更新する。sensor・独立レビュー後、新しい正式コマンド採用と完了確認を人に提示する。検証器exit0と全要件達成を区別する。

## 具体的な検証入口

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

## 変更範囲と承認境界

| 対象path | 変更目的 | 変更しない境界 |
|---|---|---|
| `crates/paludarium-cpu/src/lib.rs` / `jit_cost.rs` | 拒否hint/衝突とfeature専用site観測、選択した最小hot path修復 | Noop/既定CodeCache、命令意味論、budget/kill/syscall/fault |
| `crates/paludarium-jit/src/lib.rs` / `cache.rs` / `bridge.rs` | cold admissionと必要なlookup費用の削減、feature対照fixture | epoch/space検査、lock、144byte rollback、既存ISA |
| `crates/paludarium-runtime/src/workers.rs` | 上記policyの接続とWorker局所性 | checkpoint、killとprocess状態 |
| `crates/paludarium-wasm/src/abi.rs` / `packages/paludarium-wasm/jit-support.mjs` | 診断専用payloadと測定境界 | 通常moduleの診断exports0、配布import closure |
| `scripts/build-u14-cost-profile.py` / cost-profile runner/tests | schema3/receipt/source収集の整合 | 元schema2原本、旧109fieldsと失敗記録 |
| 新 `packages/paludarium-wasm/tests/u14-cost-microbench.mjs` と回帰 | 実Worker/Wasmのchunk計時、固定fixture・対照 | 正式性能runner、固定20標本の受理条件 |
| 新 `scripts/u9-coverage-check.py` / `tests/guests/u9/coverage-scope.json` / `test_coverage_check.py` | 二集合・来歴・計測定義を固定した独立判定 | 既存13集合、80%下限、旧LCOV/JSON |
| 必要な `.github/workflows/u14-cost-diagnostic.yml` / `u14-wasm-acceptance.yml` / `u1-u14-source-bound.yml` 接続 | 新検証器の組込み、最終source計測、原本保持 | 必須job/監査を減らさない。正式性能は品質成功後の1回だけ |
| 新record配下 `verification/jit-u9-next/` | Node明示readiness・stdout/stderr/exit保持、新bindingと旧023読取view | 現行/旧canonical全てのbytesと既存predicate |

新coverage計測を行う場合は、JSON/LCOV/reportに加えてprofdata・対象instrumented binaryの識別子とSHA、compiler/LLVM・全flagsを保存し、必要な再現用原本も新成果物へ束縛する。診断ログには開始前readinessと終了後exit/timeout/cleanupを記録し、子の失敗を一般的なCalledProcessErrorだけへ縮約しない。元c9で欠けたログを後から生成して埋め戻すことはしない。

新診断は旧schema2/109fields原本と混同しない新version・新outputへ保存し、制限付きsite表は別payloadとする。通常feature無効moduleの診断exportsは0のまま、配布static importを追加しない。新しいU9集計器・固定scope・回帰ファイルをsource収集へ明示追加し、収集漏れ・別compiler・別head・欠落payloadを拒否する。

予定対象はCPU `lib.rs`/`jit_cost.rs`、JIT `lib.rs`/`cache.rs`/`bridge.rs`、Runtime `workers.rs`、feature専用Wasm ABI/JS・診断builder/runner/tests、および新U9集計器/testsと必要な専用CI接続。実変更前に差分manifestを固定する。U9製品への変更はStep3で再現した不足に限り、その場合は対象test・理由を追加する。ゲスト元source/lock、通常依存、監査例外、性能runnerの受理条件は変更しない。

外部実行が必要な段階で具体diff/manifestを提示し、既存fork `codex/u14-jit-wasm` へ署名付きjj送信、Verified/head/bytesを確認する。正式性能stepを診断だけのCIへ無条件追加せず、品質成功後の明示した1回に限定する。この提案の保存は正式Plan Approvalや新canonical採用を意味しない。
