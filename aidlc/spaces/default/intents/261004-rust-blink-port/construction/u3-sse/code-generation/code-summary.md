# U3 SSE 現在ソースのコード生成記録

## 現在の状態（2026-10-19 JST）

本節は2026-10-19の確かめ直しの記録である。U15のStep22〜28で製品のファイルが変わってfork `codex/build-and-test` へ送られた（head 27d05de1、e3c29d1d→8b415a7c→8360be2e→27d05de1、4つともVerified）ので、U3を確かめ直した（`reviews/review-06.md`、READY、Major 2・Minor 4）。checkpointで人がRequest Changesを選んだので、U3の記録で直せるR-04〜R-09を直した。U3の製品のコード・CI・workflow・ほかのUnitの記録・traceability.jsonは変えていない。

- **今の正式な確認コマンド（R-04・R-09）**：`aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の U15 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用、command SHA-256 `00f5c883…a159`）。記録に出てくる `verification/verify-current-u1-u7-u9-aligned.py`・`verify-current-u1-u7-u9-u3.py`・U2の `u2_candidate.py` は、それぞれの時点の正式なコマンドや候補（履歴）で、下の節の「未実行」もその時点の記述である。U3のcheckpointはentry-fで確かめる。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べるので、U3の記録の変更はその結果に影響しない想定である（結果はcheckpointの記録が持つ）。
- **U3に関わる製品の変更**：U3のsource-manifestにある `ci.yml` は `push` が `main` だけになり、`u3-current-verification.yml` は消えた（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）。U3の製品のコードは変わっていない。
- **U3の受け入れに要るものは残る**（review-06の確かめた点）：`ci.yml` の `diff_u3`、native入力の生成、CPU/Decoderの80%の下限、3OS・lint・依存・production wasm。ASanは `u14-fuzz.yml`、Safariは `u11-acceptance.yml` と `u11-safari-stability.yml` で動く。27d05de1のCI 8 runはすべて成功した（U12は人が認めた1 jobの再実行。記録はU15の `verification/ci-27d05de1/`）。
- **toolchain（R-05）**：今は `rust-toolchain.toml` の `nightly-2026-10-11`。手順書の `+nightly-2026-10-01` と `u3_tests:: --fail-under-lines 80`（Steps19〜21で置き換え済み）はその時点のもので、手順書の先頭の節とその2つの見出しに注記した。
- **source-manifest.json（R-06）**：writesから、消えた `.github/workflows/u3-current-verification.yml` を外した。ほかのpathは変えていない。呼び元が消えた `.github/scripts/u3-current-diagnostic.py` は製品のファイルとして残っていて、消すと正式な確認コマンドがhead 27d05de1との違いで拒否するので、次の製品の変更のpushで扱う。
- **ASan（R-07）**：cpu_u2・mmu_u2・decodeのASanの今の裏付けは、`u14-fuzz.yml` のrun 39149194521（27d05de1、成功）である。下の節の旧い実行（消えたworkflowによるもの）は履歴である。
- **Node/Safari（R-08）**：下の節の「20ケース」「21ケース」とmoduleのハッシュはその時点のものである。今のSafariの確認は、U15の `u11-safari-stability.yml`（run 39143558642、まっさらなmacOSで10回とも成功）と、27d05de1のCIで成功した `u11-acceptance.yml` である。
- 古い「現行」「現在」の見出しは「履歴：…（作成時の見出しは「…」）」にした。本文は変えていない。
- 再レビュー（`reviews/review-07.md`）の後の追記：R-10として、手順書に残っていた見出し「現行完了確認（Steps11〜13）」も履歴にし、今の正式な確認コマンドの注記を1行足した。R-11（command SHA-256の末尾 `a159` の裏付け）は、checkpointの検証の記録が `00f5c8832e04f7d27b30c6b445fdc30e0e5d233dfa5452e02c2c99368a08a159` を示しており値が正しいので、直していない。
- 未検証：この作業ではentry-fを実行していない（checkpointで実行する）。独立再レビューはこの記録の後に行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：Steps25〜30（作成時の見出しは「Steps25〜30：2026-10-11の現行確認」）

検証済み：製品変更なし。署名Verifiedのhead `8864d5fcd39ffc7cca0415c0d089d61fe1a386d3`、診断CI `38066719757` の4job（Linux native/matrix/coverageと3OS scoped）が成功した。318入力（U9受入れ時の316入力＋U3診断helper/workflowの2入力）と両lockは各job before/after/currentのpath/hash集合が完全一致した。Windowsの並び順は保持し、path文字列をcasefoldせずduplicate・欠落・hash変更を拒否する。

検証済み：fresh native正常23576/fault1162/CPUID12、各exit0・stderr空・30秒未満・process group watchdogとreapを保存。独立 `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --no-report -- u3_tests::` はCPU40/Decoder12、ignored0。Linux `cargo test --locked -p paludarium-harness --test diff_u3 -- --nocapture` は11pass・2ignored・実exit0。ignoredはnative収集専用 `u3_native_observation` と指定rawの比較 `u3_saved_observation_replay` で、同fresh環境の追加 `-- --ignored --nocapture` により両方を2pass・ignored0・exit0で明示実行した。3OS scopedは同fresh入力でCPU40/Decoder12、ignored0。

検証済み：matrixからprofilesを消去し、別の `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80` を実行。選択済みCPU/Decoderの同9sourceファイルは2246/2758行=81.43582306018854%、実exit0。LCOV LF/LH・LLVM JSON・consoleの2758行/512未到達/81.44%が一致。inline cfg(test)を含む既存分母を変更せず、filter単独80%成功とは称さない。

検証済み：別署名head `97a642fd94b47abbd3612b7fa03fff1a741439a5` の初回CI `38066034107` で、cpu_u2/mmu_u2/decodeの3ASan jobだけが成功。各601秒、2,145,400/3,032,340/128,740,995 runs、actual exit0、最小C終了2回exit0、ASan/LSan symbols、compiler `32dba69d69c5b10ea89a4042de8d0619f7756203` / LLVM23.1.3 / cargo-fuzz0.13.2、seed1/timeout30/rss2048/detect_leaks1/既存suppressionを保存。最終318入力との差は診断2pathだけで、製品依存・両lock・fuzz target・compiler・実行設定は一致する。最終CIで600秒を重複実行したとは称さない。初回run全体は診断件数grep誤りのfailure、最終runの4成功jobとは別にbindする。

検証済みの限定再利用：U9新証拠 `38062686224` の保守的88入力compiled dependency unionと両lock/compiler/settingsが現行一致するため、load_elf/syscall_args/vfs_paths/mmu_opsの既存601秒・同一instrumented binary証拠を再利用する。本番Node/本物Safariの現行20ケースにはU3の7ケース（aes/cpuid/fault/float/packed/pclmul/sha）が全て含まれ合格。module `4482b1574987ff62cc8f9f872e42e5dbe6f4fc91273103da6abc0dd8ffd18fe3` とnative SHAは両環境で同一、製品316入力と実compiler/build flagsの一致に限定する。今回のfreshブラウザ実行、旧21ケース全体の再実行とは称さない。旧unsupported-ttyは既存u16 tty設定対応と矛盾するため復元しない。現行u11-api-check.mjsのtty設定境界/kill回帰の存在はドキュメント根拠であり、今回そのAPI回帰や実端末syscall動作を実行したとの保証はしない。

検証済み：136担当行の568対応変種（正常23384/fault1141）、補助9変種（正常192/fault21）が今回fresh rawの577変種・23576/1162へ一致した。CPUID12は別oracle。対応mappingソース9ファイルと固定probe/aubeは不変。全静的operand形・全SSE・任意入力・child Node命令集合・セッションID競合の完全解消は未検証。比較maskとexact AMD SHA profile拒否条件を変更しない。

失敗履歴：初回の実diff exit0に対して総数2passを誤指定した診断grep exit1、次run `38066422487` のWindows318入力の順序だけの比較FAIL（missing0/changed0）、誤bookmark pushの中間run `38066394535` cancelledを保存した。既存211入力は169一致/42変更、旧ASan179入力は142一致/37変更で、nightly10-01の旧成功を現行10-10のfresh実行へ読み替えない。最新ツールは公式配布を2026-10-10T15:47:02Zに確認した準備版を固定し、日付だけで更新を反復しない。

成果物根拠はこのUnitの `verification/step25-source-reuse.json`、`step26-latest-tools.json`、`step28-final-signature.json`、`step29-reuse-binding.json`、`step30-current-proof.json` と全raw。今回の実変更は診断helper/workflowの2pathのみ（manifest既存35＋2）。承認済みテスト指示・製品・後続Unit成果物は保持。新最終確認候補は `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3.py`。構文確認だけで未実行、人の別コマンド承認が必要。正式独立レビュー・完了承認は親担当。

## 以下は旧時点の履歴

## 履歴：確認範囲（作成時の見出しは「現在の確認範囲」）

Step22の検証済み現在結果：署名head91ca0c4e3a090f49c6ac1ffb1e5e2e1d8d0a183d、通常CI37909227452全8job成功（3OS、lint、依存、fresh native差分、本番wasm、coverage）。同head診断37909227274でfresh native正常23576/fault1162/CPUID12を生成し、U3 matrix CPU40/Decoder12、ignored0、exit0。共有CPU/Decoder全libraryは9sourceファイル2246/2758行=81.43582306018854%、exit0。明示LCOV LF/LH、LLVM JSON、consoleが一致する。DA行数2737/2229をLF/LHと誤集計した初報は別訂正証拠へ保存し合格分母に使わない。

Step22で変更したのはCI coverage jobのfresh native入力と30秒process-group watchdog・絶対パス環境。製品意味論は変更していない。現在211pathsは11195時点から既承認2testとci.ymlのみ異なり他208paths一致。2testはcfg(test)配下、CI設定は製品コンパイル入力ではないため、保存済み7ASan各601秒とNode/実Safari21の製品closure証拠を再利用する。再実行とは称さない。根拠step22-current-source.json、step22-main-source-delta.json、step22-final-metadata.json、step22-shared-coverage-proof.json。

履歴：Step19〜20のrun37907701693で共有80%とmatrixは成功したが、auto CI37907701758はnative env不足でcoverage replay2件NotPresentとなった。失敗rawを保持し、今回Step22の成功と混同しない。旧filter47.1356%も失敗履歴を維持し、人が選択した共有library80%と独立U3 matrixという新しい測定義務へ読み替えたことを明示する。

Steps15〜17の検証済み現在結果：test-only CPU/Decoder u3_tests.rsと隔離診断workflowを変更した。署名head01db3ea416fca9a6305d25c5f7207081e1f52152、run37886241090でfresh正常23576行/fault1162行/CPUID12行を生成し、CPU40件・Decoder12件が成功（ignored0）。同じ9sourceファイル2758行中1300行、47.13560551124003%でexit1、80%未達。分母には既存inline cfg(test)行も含み、全行が製品実装とは称さない。以下11195の検証は保存済み履歴として保持し、このfilter成功へ読み替えない。最終GAP/分類はverification/u3-current-sha-reuse/step17-final-gap-scope.json。製品意味論・元23成果物・2prefixは不変。Step18は未完、正式U3完了を主張しない。


検証済み：署名head `11195ad000415af6b320b8e0e4b64a46265fdb61`、CI `37858171955` の保存証拠を現在ソースへ照合した。今回はSteps11〜13の記録作業で、製品ソース・依存・CIを変更していない。先行23成果物と元2ファイルprefixを保持する。独立レビューと正式U3完了確認は未実施。

## 実装と変更ファイル

実際のU3製品・テスト・設定変更35 pathsをsource-manifest.jsonへ列挙した。CPUのexec/lib、sse/crypto/softfloat/cpuid、Decoderとnative encoding境界、共通typed浮動小数点faultとKernel delivery、Harness比較、native C/assembly生成器、production wasmのU3 fixture/ケース、CPU fuzz、既存CIを含む。今回のmanifestは過去のU3実装と共有SHA前提修復の実変更をまとめたもの。新しい製品書き込みはない。詳細hashと根拠は `verification/u3-current-sha-reuse/source-claims-proof.json` と `verification/u1-sha-prerequisite/supplemental-change-inventory.json`。

## 命令とケースの対応

検証済み：assigned legacy129 mnemonicと追加crypto7形式、計136行に対応するのは568ケース変種（正常23,384行・fault1,141行）。全nativeは補助9変種（正常192行・fault21行）を含む577変種、正常23,576行・fault1,162行であり、CPUID12行は別oracle。補助はPCLMUL即値80/eeのregister/high/alias/memory各4変種とstmxcsr1変種。集合差と各件数を既存rawから再集計した根拠は `verification/u3-current-sha-reuse/r02-case-partition-proof.json`。577全体を136行へ対応付けたとは称さない。対応表は `verification/u3-current-sha-reuse/inventory-case-audit.json`。native-before-implementationの順序は旧Step3観測証拠と実装履歴を保持する。今回の照合を新native実行へ読み替えない。

比較はXMM16本、RAX、MXCSR、512byteメモリ、定義済みRFLAGS mask0xcd5とfault/RIPを扱う。trap RFを除外する。SHA3形式はIntel16byte整列契約を実装し、観測済みexact AMD3signatureの6シナリオだけを独立した#GP/state不変検査へ分離する。他のnative状態を緩めずunknown profileはFAIL。CPUIDはhost値を転送せず8単体契約assertでvendor/leaf/zero reserved/flags等を確認し、未実装・部分family広告はoff。

## 固定ターゲットと履歴

probeは8source固定binary `29916d90ae1e6609a7b9019181df855ce3547366527a01137c88a894739e6ebd`。aubeは1,362 sourceと固定build条件、SOURCE_DATE_EPOCHを含む独立double buildでexact同一binary `d009267fa265ed854d14bdcbe99deb598d21ff79a385669a6f2ac0f5c329c8cc` を取得した。根拠は旧 `verification/step2-current-fixed-target-proof.json`。旧ff54/5a/781f、初回21byte差、PT/DBI初回失敗、prefix誤分類修正を履歴として保持する。

静的候補は埋込データ・到達可能性の不確実性を持つ保守的集合。有限DBIはnative workloadのcoverageでstate oracleではない。全静的prefix/register/displacement形・全入力・child Node全体のSSE集合を実装済みと認定しない。probe/aube全機能のguest完走はU10以降の担当。

## 品質とカバレッジ

11195時点の保存済み履歴：当時CIの3OS、lint警告0、依存検査、fresh差分、production wasm、coverageが成功。workspace93.13%。CPU/Decoder9source file（既存inline cfg(test)行を含む）のLCOVは2737行中2225行、81.29338691998538%。正確なCI commandは `.github/workflows/ci.yml` のU3測定で、Harness diff_u3を同測定へ含める。9source file（既存inline cfg(test)行を含む）の分母を変えず、他crateをU3分母へ含めない。

履歴GAP（Steps11〜13時点）：unit-test-instructionsの `--lib u3_tests:: --fail-under-lines 80` 単独filter commandには80%以上の保存実測がない。このcommandの成功を81.293%で代用しない。旧2990行の別object集合・unscoped report74.78%は `verification/u1-sha-prerequisite/coverage-proof.json` に理由とともに保持される。閾値は80%のまま。必要なLinux追加測定または手順との契約整合判断は親へ返す。

## ASan・LSan

検証済み保存履歴：11195の7 targetsは各601秒exit0、address sanitizer binary symbols、固定nightly2026-10-01、seed1、30秒timeout、rss2048、既存LSan suppression、最小C終了2回exit0、source179paths前後/current一致とcorpus hashを保存した。CPU2,123,261／decode77,005,138 runs。詳細は `verification/u1-sha-prerequisite/final-sanitizer-proof.json` とfinal-four/three-sanitizers raw。全UB・全任意入力がないという証明には拡張しない。nightly scheduled run実行とは呼ばない。

## Production wasm

検証済み：現行CI module SHA `ef8bfcc85dbe47d17866314dff8ad94b4b943ff1ecf0c61a7e02c8138ef74ac5` のproduction launcherでNodeとApple Safari27.0.1の21ケースが成功した保存証拠を照合する。U3 packed/float/crypto/CPUID/faultの7 guest fixtureを含み、crossOriginIsolated/shared memory、cleanupと28/30秒期限を維持。根拠は `verification/u1-sha-prerequisite/production-proof.json` とfinal-safari raw。同じmoduleを新たにSafari実行したとは言わない。全ブラウザ・任意ゲスト・JITへ一般化しない。

## 対応表と後続担当

traceabilityは共有60 FR/NFRを分類し、U3 subsetの実装/差分/品質だけをOKとする。syscall/VFS/端末/thread/launcher/各native backend/probe-aube全機能/JIT/releaseは具体後続Unit理由でDeferred、集約見出しと資源上限はN/A。NFR3は選択済み共有library80%と独立matrixの現在実測を対象とし、旧filter失敗は履歴を残す。

## 逸脱と未検証

Steps11〜13時点は新製品変更・新CI・重い試験なし。Steps15〜17では上記test-only診断を実測した。初回Windows errno5 PermissionDeniedの原因は未解明、最終同fixtureの1000反復/53交換/421一時共有競合/786ms、outside不変とstrict cleanup成功とは別履歴で保持する。U3全SSE family、AVX/EVEX/x87/MMX/XSAVE等、全入力は未検証・対象外を区別する。旧coverage filter失敗を成功へ改称しない。正式独立レビューと完了承認は親が担当し、まだ完了扱いしない。

## 検査証拠

今回checker1回と限定sensor2回の正確なcommand/exit/raw、source211と先行成果物保持、最終artifact hashは `verification/u3-current-sha-reuse/` に保存する。独立レビューは全書き込み停止後に親が行う。
