# U3 単体テストと差分テスト

## 追加Steps28〜30：現行ソースの実測

製品変更なし、現行ソース・両lock・公式最新確認版を固定した署名CIで実行する。fresh正常23576/fault1162/CPUID12を既存native build入口から生成し、各30秒process-group kill/reap・exit0・行数・hash・stderrを検査する。3native絶対pathとFULL_REPLAYを供給し、欠落・skip・unknown profileを拒否する。

独立matrixは `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --no-report -- u3_tests::`、CPU40/Decoder12・ignored0を要求。Linux `cargo test --locked -p paludarium-harness --test diff_u3 -- --nocapture` と3OSのCPU/Decoder U3限定入口も同fresh入力で確認する。共有品質は別に `cargo llvm-cov clean --workspace` 後の `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80`。同9ファイルのLF/LHとJSON/LCOV/consoleを照合し、分母・package・除外を変えない。

ASanはcpu_u2/mmu_u2/decodeの3対象それぞれ `cargo fuzz run --fuzz-dir fuzz --sanitizer address <target> -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048`。ASAN_OPTIONS=detect_leaks=1、既存LSan suppression、最小C終了診断、binary/compiler/flags/corpus・実終了コード・時間・ソースbefore/afterを保存する。旧7対象をそのまま再利用しない。U9新4対象とproduction Node/本物Safari内U3関連7ケースは、全依存・両lock・実compiler/設定の一致を確認する範囲だけ再利用。旧unsupported-ttyの削除理由と現行端末回帰は区別して記録し、実端末動作の保証へ拡張しない。

全入力before/after/current、全raw hash、署名Verifiedと各gateの実exitを保存する。新canonical候補は人の別承認前に実行しない。失敗・権限不足・未到達を合格にしない。strict guard、80%、30秒、比較maskを維持する。

## 今回Steps25〜27の再確認

現在のrust-toolchain.tomlと実使用版を照合し、公式最新版を区切りで確認する。以下に残る旧nightly指定・過去コマンドは履歴であり、今回実行する版を上書きしない。製品を保持し、命令対応と保存証拠を現行ソース・両lock・compiler/設定へ照合する。U3 native matrixと共有CPU/Decoder9ファイル80%を別義務として扱う。native入力欠落・0件・skipを合格にしない。

限定入口は `cargo test --locked -p paludarium-cpu --lib u3_tests:: -- --list`、`cargo test --locked -p paludarium-decoder --lib u3_tests:: -- --list`、Linuxの `cargo test --locked -p paludarium-harness --test diff_u3 -- --list`。必要なnative観測を用意せずreplayを実行しない。ケース数と既存同source実測の一致を照合し、保存証拠の依存不一致は具体的な追加検証案として提示する。MacのLinux専用0件を成功にしない。

不足を埋めるLinux CI・coverage・production wasm/Node/本物Safari・600秒ASanの追加実行や製品修正は、具体範囲の計画変更として先に提示する。strict guard・80%・30秒・比較mask・測定対象は維持。現承認済みcanonicalは `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-aligned.py`。U3を十分検査しない境界を明記し、新候補を人の別承認前に実行しない。過去のcheckerを現在承認済みと扱わない。

## Runner and ordering
nightly-2026-10-01をrust-toolchain.tomlに従い使用する。Macでは ~/.cargo/bin/cargo +nightly-2026-10-01 の実体を使う。以下の各コマンドはStep 1で追加するU3専用入口を前提とする。未作成の入口を検証済みと扱わない。
命令のnative差分ケース/観測を先に作り、製品実装を後に行う。Decoder接続の単体テストはその実装後に行う。

## Unit-scoped commands
- CPU: ~/.cargo/bin/cargo +nightly-2026-10-01 test --locked -p paludarium-cpu --lib u3_tests:: -- --nocapture
- Decoder: ~/.cargo/bin/cargo +nightly-2026-10-01 test --locked -p paludarium-decoder --lib u3_tests:: -- --nocapture
- LinuxのU3 native収集: cargo test --locked -p paludarium-harness --test diff_u3 u3_native_observation -- --ignored --exact --nocapture
- LinuxのU3差分: cargo test --locked -p paludarium-harness --test diff_u3 -- --nocapture
- U3 guest build: bash tests/guests/u3/build.sh target/u3-guests
- Linux U3対象coverage: cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib u3_tests:: --fail-under-lines 80
各U3専用commandで対象case数0なら失敗とする。native収集入口は通常差分テストとは別に設け、集めただけで合格を記録しない。CI全体ゲートは計画Step 8で1回検証し、この単位のrunコマンドへ他Unitのsuiteを混ぜない。

## Cases and targets
Standard: DecoderとCPU各処理群で最低5〜8件、正常1件と異常/境界2件以上を含める。命令・形式ごとのnative差分はこの最低件数に加える。入力は非同一laneのbitpattern、XMM上位lane保存/zeroing、GPR32zero拡張、同registeralias、aligned/unaligned/ページ境界、write fault、全rounding/NaN/Inf/±0/subnormal/DAZ/FTZ/例外を含む。
expectedは毎CIのnative実行から生成する。未定義bitや実装依存の値は根拠付きmask表で除外するが、定義済み値は除外しない。MMU/CPUは実物で境界を確認し、oracleをmockしない。
追加暗号はSHA256RNDS2/MSG1/MSG2、AESENC/AESENCLAST、PCLMUL selector00/11をnative-before-implementationで測る。全zero/非対称/高bit/XMM8〜15/alias/implicitXMM0/メモリ128bitとfaultのケースを含め、結果128bit・MXCSR/RFLAGS不変・fault前後stateを比較する。未追加の暗号形式はUnsupportedの境界検査を行う。native runnerのAES/SHA/PCLMUL feature非対応はskip合格にせず未検証とする。
CPUIDの詳細出力表とnative比較mask根拠はverification/u3-cpuid-crypto-contract.mdに従う。leaf0/1/7のsubleaf0と非0、80000000/80000001、範囲外leaf、reserved0、vendor順序、GPR上位32bit零、flags保存を検査する。仮想CPU出力はhost値コピーではなく契約assert。AES/SHA/PCLMUL/SSE familyの部分実装を広告1へしない。XSAVE/OSXSAVE/AVX/AVX2/AVX512と未実装x87/MMXは0、XGETBVはUnsupported。CPUID使用guestでdispatch結果を出力し、software fallbackを実測前に合格と扱わない。

## Deterministic target acquisition
Step2のaube対象は元base digest a96ea6d18d4062e38f16cfbadd8b4541d622f2527dd0a5eca1fb36d301da4e88、固定source1362/lock8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668、build date2026-10-05を保持する。build専用PATH date wrapperは`date -u +%Y-%m-%d`だけ固定し他呼出は実dateへ委譲、OS時計は変えない。空primerへ`touch -d @1791158400 /cache/empty-primer.rkyv.zst`を実施しstat値を記録する。`AUBE_PRIMER_PATH=/cache/empty-primer.rkyv.zst cargo build --release --locked --target x86_64-unknown-linux-musl -p aube --bin aube --target-dir /cache/aube`を同じsource path/toolchain/package/envで独立した空cacheから2回実行しbinary SHA一致を要求する。source前後全hash・wrapper呼出・mtime・compiler/package/image・binary/ELF/raw exitを保存する。取得新SHAは未決で旧ff54/5a/781fを上書きしない。固定binary artifactはhash付きrecordへ取得し、retention期限だけに依存しない。差が残れば実装前に原因と具体選択を戻す。
probeは人が選択した8source manifestとbinary29916d90ae1e6609a7b9019181df855ce3547366527a01137c88a894739e6ebd、8check native/DBI証拠を維持する。新固定aubeは同SHAの4networkless fixtureで30秒kill/reapとDBI block/raw encoding対応を取り直す。DBIはstate oracleではなく有限workloadのcoverage。host child Nodeをguest本体の命令集合へ混ぜず、未観測legacy候補は除外しない。
Linuxのworkspaceおよび対象CPU/Decoder行coverage80%以上。U3filterだけでは既存整数部分のcoverage不足が予想されるため、U3専用指示は不足を隠さず報告し、CIで既存CPU/Decoder suiteを含む対象crate測定も行う。未達なら同一実装の鏡テストで数を埋めず意味のある境界テストを追加する。
並行runner/watchdogは既存上限を維持。CPU/decodeの現行ASan+LSan各600秒以上、production wasm Node/実SafariはCI module同一hashを記録する。観測範囲を全入力や全ブラウザへ広げない。

## 現行完了確認（Steps11〜13）

既存上記コマンドとTesting Contractは保持する。今回の主作業は11195ad0の保存証拠とcurrent sourceの照合、U3記録完成であり、古い実装手順を反復しない。

- 承認済みchecker: `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-sha-prerequisite.py`
- U3対応表sensor: `aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u3-sse/code-generation/traceability.json`
- U3必須節sensor: `aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u3-sse/code-generation/code-summary.md`

source211/current-source-proof.json、fresh-native-proof.json、final-sanitizer-proof.json、production-proof.json、final-u3-lcov/u3-coverage.lcov、supplemental-change-inventory.jsonはverification/u1-sha-prerequisite配下を使用する。CPU/Decoder9製品fileの同じ分母2737/分子2225の80%以上を確認し、別分母74.78%を消去しない。CPU/decode各601秒を含む7ASanは179paths compiled sourceのhash適用範囲を明示する。実Safari21のmoduleはef8bfcc85dbe47d17866314dff8ad94b4b943ff1ecf0c61a7e02c8138ef74ac5と照合する。

checker成功は共有前提条件の検査であり、全assigned inventoryのU3意味論・ケース対応を代替しない。U3対応表で命令形式/実装file/差分case/比較maskまたは独立CPUID契約assertを全行確認する。固定binary、DBI有限観測、静的候補とchild Nodeは区別する。未対応行はGAPとして報告し、未実装family広告offを変更しない。追加試験が必要なら上記U3 scopedコマンドを使用し、製品修正が必要なら具体案を親へ報告する。

## Step14：単独filter commandの追加測定

承認後、native x86-64 Linuxの隔離fork診断CIだけで実行する。nightly-2026-10-01をRUSTUP_TOOLCHAINで固定し、`cargo llvm-cov clean --workspace` で空profilesを確認してから、列挙された次のcommandを変更せず実行する。

`cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib u3_tests:: --fail-under-lines 80`

失敗しても同じprofilesから `cargo llvm-cov report --lcov --output-path target/u3-filter-coverage-evidence/coverage.lcov` と `cargo llvm-cov report --json --output-path target/u3-filter-coverage-evidence/coverage.json` を取得し各exitを保存する。report取得の成功と元commandの80%合否は別。原commandには除外regex・追加package・Harness差分を加えない。source211before/after、署名head、tool versions、raw、対象fileとLF/LHを常時保存する。80未満ならmissing linesの具体test案を親へ返し、製品/testをこの診断scopeで変更しない。旧9製品file81.293%や74.78%履歴は保持する。

workflow草案と211署名基準inventoryは `verification/u3-current-sha-reuse/u3-filter-coverage.workflow-draft.yml` と `u3-filter-source-baseline.draft.json`。承認前にはlive workflowへコピー、jj push、CI、上記測定を実行しない。

## Steps15〜18 fresh native replay と filter coverage

既存build入口 `bash tests/guests/u3/build.sh target/u3-guests` をnative x86-64 Linuxで実行し、`target/u3-guests/observe`、`target/u3-guests/fault-observe`、`target/u3-guests/cpuid-observe` のraw stdout/stderr/exitを毎CI採取する。各processは既存30秒kill/reap watchdog内。PALUDARIUM_U3_NATIVE_OBSERVATIONS、PALUDARIUM_U3_NATIVE_FAULTS、PALUDARIUM_U3_NATIVE_CPUIDをこのfresh結果のpathへ設定し、欠落・空行・未対応feature・unknown profileはFAIL。固定expectedへ置換しない。

空profilesから `cargo llvm-cov clean --workspace` の後、`cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80 -- u3_tests::` を実行する。既存ignored replayの移行と新境界testは承認後に実装し、現時点で検証済みとは扱わない。測定は同じ9製品ファイル、80%を維持。LCOV/JSON/profile/native/raw/source before-afterを常時保存し、後続reportにdependencyが加わる場合は測定分母との差を明記する。

不足行はStep14時点exec1076、CPU lib364、Decoder263、sse197、alu189、softfloat100、crypto53、state8。fresh native replayで正常/例外経路を測り直した後、残るU3関連境界だけを追加する。80達成を保証せず、無関係な分岐しか残らない場合は具体的な残GAPを親へ返す。既存81.293%は異なるcommandの履歴を保つ。

## Steps19〜21：共有library品質gateと独立U3 matrix

人のoption1選択によりfilter単独80%義務を置き換える。旧47.1356%失敗は履歴保持し、成功と称さない。fresh native生成と3環境path/FULL_REPLAYはSteps15〜18の手順を維持する。

1. 空profilesで `cargo llvm-cov clean --workspace`。
2. U3独立matrix: `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --no-report -- u3_tests::`。CPU40/Decoder12件、ignored0、fresh正常23576/fault1162/CPUID12・unknown profile拒否を必須とする。matrix成功を80%測定成功へ置換しない。
3. 再び `cargo llvm-cov clean --workspace`。
4. 共有品質gate: `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80`。同じ9sourceファイルと80%を維持し、追加package/除外/テスト改名なし。LCOV/JSONのpackage省略reportに依存が加わる差は明示し、9ファイルのLF/LHとconsoleを照合する。

native/matrix/shared gateの各exit、before/after source211、profile、toolchain、署名metadataをalways保存する。現2test-only差分以外の製品は不変、既存ASan/Node/実Safariはcompiled closure一致の根拠付き再利用。新正本checkerは既存を弱めず追加型とし、人のcommand承認前には実行しない。

## Step22：既存Linux CI coverageへのfresh入力供給

reviewable草案はverification/u3-current-sha-reuse/step22-ci.patch-draft。承認後だけmain CIのcoverage jobへ適用する。既存 `bash tests/guests/u3/build.sh target/u3-guests`、3binaries各30秒process-group deadline、native行数23576/1162/12、exit0/stderr空を要求しreceipt/rawをalways保存する。3absolute env path/FULL_REPLAYを同jobに設定、既存workspace/U1/U9/U3 80%各commandとpackage/除外を変えない。選択済み共有CPU/Decoder80%・独立U3 matrixの成功は別保存する。

隔離fork署名push後の最終同headの3OS unit、lint、dependencies、fresh differential、coverage、production wasm全8jobsの成功を要求する。旧NotPresent失敗は保持する。変更はCI設定1pathのみ、現2testファイル不変。新checkerは追加exact deltaを検査し旧checkerを保持、人のcommand承認前は未実行。
