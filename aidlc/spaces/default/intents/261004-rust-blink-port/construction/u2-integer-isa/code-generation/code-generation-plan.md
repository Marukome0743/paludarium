# U2 Integer ISA — Code Generation Plan

## 今回の計画：Step71（Build and TestのLoop-back 1：共有のabi.rsの再確認と正式確認のbinding更新）

2026-10-17。U14のLoop-back 1で、整数SSEのJIT（署名head 12d6a2f6・1ceae86c）のために、U2が担当する `crates/paludarium-wasm/src/abi.rs` が変わった（JITの状態の大きさ144を `paludarium_jit::STATE_BYTES`（400）に置き換え、`// SAFETY:` のコメントを更新）。1ceae86cのCI（PR・U12・U13・U14 quality・fuzz・source-bound）はすべて成功し、FR8.3の正式な性能測定は合格した。人はU1のStep71・72で作った新しい正式確認コマンド（`construction/u1-skeleton/code-generation/verification/loopback1-next/new_candidate.py`、checker `a7836f9b…`、binding-02）を採用し、U1は承認された。このコマンドは旧い正式確認の封印（`final-verifier-208fd965/consumer-v3/history-seal.json`）をそのまま使い、その封印にはこの計画とunit-test-instructions.mdのbytesが入っている。そのため、この計画を書き足すとコマンドはexit 1になる。人は「U2 で binding を更新」を選んだ。

- [x] Step 71 — 共有のabi.rsの再確認と正式確認のbinding更新（C12、NFR3、NFR8）。
  1. abi.rsの変更（1ceae86cと12d6a2f6の差分）を読み、U2の記録（code-summary.md・traceability.json・source-manifest.json）の主張（C12の境界、`unsafe` のSAFETYの説明、production wasmの状態の受け渡し）が今のsourceでも正しいかを確かめる。正しくない記述があれば、U2のcode-summary.mdに「現行Step71」節を足して直す。製品のsourceは変えない。
  2. U1の記録のchecker・binding・旧い封印は変えない。U2の記録の `verification/loopback1-next/` に、U1のcheckerをそのまま呼び出す新しい入口（例：`u2_candidate.py`）と新しいbinding（binding-03）を作る。binding-02から増やす許可は、この計画とunit-test-instructions.md、U2のcode-summary.md・traceability.jsonの、このStepの後の新しいbytesだけにする（各ファイルの旧いbytesは封印の値、新しいbytesはSHA-256で固定）。ほかの許可・検査は弱めない。
  3. U1の承認時に人と約束したMinor 2件を直す：(a) Step72で足した、receiptとjobの照合（job ID、attempt 1の成功、後のattemptでの再実行がないこと、artifactの作成順）と「attempt 2は失敗したjobだけの再実行」の検査に、それぞれ拒否の回帰を足す、(b) `result.json` の `claim_scope` の `performance_1ceae86c` に、moduleの結び付きがartifactのmetadataに頼っていてsourceのdigestがないという限界を書く。U1のcheckerの中身を変えずにできないものは、新しい入口の側で行う。
  4. 新しい入口がexit 0、回帰（U1の29件と、このStepで足す分）がすべて期待どおりであることを確かめる。件数と一覧をREADME.mdに書く。
  5. 正式sensor 2件を実行し、独立再レビューに進む。新しい入口のコマンドは、採用の承認（Construction Verification Commandの決定・回答・設定）を人から受けてから、U2のcheckpointで実行する。U1のcheckerでの成功は履歴とし、新しい入口の成功と読み替えない。
  6. 変えないもの：製品・CI・lock・mise.toml・.gitignore・U1とほかのUnitの記録・旧verification原本。

## 前回の計画（Step68〜70）

前回の実行対象はStep68〜70。Step64〜67の原本回収・14件回帰と全checker診断exit1、以前の正式失敗を履歴として保持する。新しい計画承認と内容確認の取得前には追加実装・検証を実行しない。

## Summary

- Builds: Step71。U14の変更で変わったU2担当の `abi.rs`（144→`STATE_BYTES`）を再確認し、U2の記録を必要なら直す。U2の計画・手順書が旧い封印に入っているため、U2の記録の変更だけを許す新しいbinding（binding-03）と、U1のcheckerを呼び出す新しい入口を作る。U1の承認時に約束したMinor 2件（receiptとjobの照合などの回帰、result.jsonの限界の記述）も直す。
- Touches: U2の記録（計画・手順書・code-summary.md・traceability.json・`verification/loopback1-next/`）。製品・CI・lock・mise.toml・U1とほかのUnitの記録・旧原本は変えない。
- Tests: 新しい入口がexit 0、回帰（U1の29件と追加分）がすべて期待どおり、正式sensor 2件、独立再レビュー。新しい入口は人が採用してからU2のcheckpointで実行する。

## 前回のSummary（Step68〜70）

- Builds: 共通checkerの時間項目を原本schemaに従って明示指定し、歴史／現行traceと既存全検査を保持する。
- Touches: 共通verify-current-u2-u11-revalidated.pyとU2限定の計画・局所回帰・成果物。製品と他Unit成果物は変更しない。
- Tests: 既存14件と時間項目8件の局所回帰、全checkerのレビュー前診断、正式sensor、正式完了検査。80%下限・30秒制限・strict guardを維持する。

## 今回の計画：Step68〜70（時間項目の明示指定）

68. [ ] 新Plan Approvalと内容確認後、successful(row, time_field='wall_seconds')へ時間項目の明示引数だけを追加し、U11の4環境rowsのcallsiteにだけtime_field='seconds'を指定する。U10 native/emulator/originalargv/runner/statとU11 nativeはwall_secondsを保持する。存在しない項目のfallbackは禁止し、数値型（bool拒否）、有限値、0<=t<=30、exit0、timed_out falseの全条件を保持する。既存歴史37／現行42・歴史原本hash・現行trace・全旧canonical検査を変更／削除せず、製品・他Unitを変更しない。診断のwall_seconds KeyError原本は保持する（NFR3.4/NFR7.1/NFR9.1）。
69. [ ] custom内部test-afterでU2 verification/test_step68_timing.pyへ8件の局所回帰（wall_seconds正常、明示seconds正常、必須項目欠落／fallback拒否、誤型とbool、非有限値、負値、30秒超過、exit／timed_out異常）を追加する。境界0／30も正常ケースで確認する。既存inventory8＋trace6を保持し、構文確認とloader readiness22件後、各局所suiteを外側30秒timeoutで実行しraw/exitを保存する。続いて修正checkerを外側600秒／子60秒の読取専用全経路診断として一度実行し、checker hash・開始終了・全stdout/stderr・実exitを保存する。新CI／重い製品試験を実行しない。追加不一致は具体GAPで停止し、診断を正式checkpoint証明にしない（NFR3.4/NFR7.1/NFR9.1）。
70. [ ] 修正・局所22件・全経路診断と既存証拠適用をU2成果物へ整合し、正式sensors後に全書込停止して独立レビューを取得する。正式完了検査はレビュー後の標準checkpointで実行し、必要な人のcommand承認を保持する。旧失敗を消さず、成功時も人のU2完了承認とU11復帰まで未完了とする。承認済みU11同時dispose修正へ戻り、U9再承認等を完了へ読み替えない。完全Testing Contract/custom順序/strict guard/80%/30秒/比較maskを維持する（NFR3.4/NFR7.1/NFR9.1）。

## 先行計画：Step64〜67（歴史trace原本と現行traceの分離）

64. [ ] 新Plan Approvalと内容確認後、正式検査c2481414の04:44:33Z Historical trace/proof binding differs失敗を保持する。両関数・current_binding・historical_hashes・preserved・trace reverse・source/CI・関連原本参照を全て有限対応表で監査し、同じ現行ファイルを歴史原本として読む箇所をまとめて特定する。期待SHA2164fbd9af6bf6478c06ecf10ef3e3bc7d5dd3bb1a3be845e8855a5a13857764の歴史U10 traceをjjのversioned evidenceから読取回収し、取得revision/path/commandと生bytesをU2 verification/step64-historical-u10-traceability.jsonへ保存する。全bytes hashが一致し、source5b319a7072e698d8e7c2f94e4821bf584ec381fb／CI38010586387・歴史37の対応が確認できた原本だけを使用する。見つからない／不一致ならGAPで止め、現行traceの加工・再ラベル・期待hash変更で通さない。他Unit原本は上書きしない（NFR3.4/NFR9.1）。
65. [ ] 共通checkerの歴史原本参照を最小修正し、歴史proofと回収traceを元のhistorical_hashesの論理path／期待hashへ明示対応させる。元の祖先・source/CI・歴史37・digest・EXTRA2・全実行結果検査を保持する。現行UNIT/traceability.jsonは別にsourcecb9797138313046b3cf9bbbfcab0515910b81215／CI38095031011・unit/draft・要求IDとreverse inventory・対応source条件を原本根拠と厳密照合する。現行42manifest検査をtrace37の代用品にしない。Step64の全参照監査で見つけた同原因箇所も有限修正し、旧canonical全検査や有限差分を削除しない。custom内部test-afterでU2限定test_step64_trace_binding.pyへ歴史原本正常・現行trace正常・現行を歴史へ取り違え・歴史を現行へ取り違え・歴史hash不一致・source/CI不一致の6件を追加し、既存inventory8件と構文／非ゼロreadiness／各30秒上限の局所実行を保存する（NFR3.4/NFR7.1/NFR9.1）。
66. [ ] この計画と内容確認で明示承認するレビュー前診断として、修正後共通checkerの全経路を一度実行する。実体Pythonとchecker hashを固定し、元の読取専用jj/API/artifact検査を省略せず、実command・開始終了・全stdout/stderr・実exitをU2へ保存する。子commandの既存timeout60秒を保持し、全体上限600秒、timeout時kill/reap・失敗保存とする。新CI／製品重試験は実行しない。この診断は正式checkpoint証明や人完了承認へ代用しない。別の不一致なら具体GAPと最小方針を提示し、同原因範囲を超える変更を自動追加しない（NFR3.4/NFR7.1/NFR9.1）。
67. [ ] 参照対応表・回収原本・修正／回帰／全経路診断の実結果をU2成果物へ整合し、正式sensors後に全書込停止して独立レビューを取得する。診断成功でも完了とせず、別の正式command承認後に再検証し、旧失敗を保持する。人のU2完了承認とU11復帰後、承認済み同時dispose修正へ戻る。完全Testing Contract/custom順序/strict guard/80%/30秒/比較maskとU9／U11未完了境界を維持する（NFR3.4/NFR7.1/NFR9.1）。

## 先行計画：Step61〜63（歴史37／現行42の限定修正）

61. [ ] 新Plan Approvalと内容確認後、両U10検査関数が同じ現行manifestへEXPECTED37を要求して実測失敗した記録を保持し、歴史37と現行42の順序付きinventoryを別々に検査する。現行manifestは追加5件が先頭、後続37件が旧EXPECTEDと同順序である。追加順序は.github/scripts/u10-current-diagnostic.py、.github/workflows/u10-current-verification.yml、crates/paludarium-host/src/native_fs.rs、tests/guests/u10/comparison_args.py、tests/guests/u10/runner-tests/test_comparison_args.py。歴史37は旧canonicalの固定リスト・歴史trace/proof・当時署名sourceへ結合し、現行42を37へ加工して歴史原本と呼ばない。現行42は現行manifest全件・重複なし・順序・各pathの現在bytesと署名2b3874eabda6fe6f1d1334202421db733445fd21／保存CI入力digestを厳密照合する。歴史traceの37件は歴史検査として保持し、現行manifest42の根拠と混同しない。EXTRAの既存2件の追加検査も保持し、現行42内の2件と明示対応させる。既存有限3差分・共有5差分と全native14/emulator16/originalargv/license/metadata/coverage/runner44/署名/CI/ASan/MMU/環境検査を一つも削除せず、共通checkerだけを最小修正する。不足bindingはGAPとし製品・他Unitを変更しない（NFR3.4/NFR7.1/NFR9.1）。
62. [ ] customの内部test-after順序でU2 verification/test_step61_inventory.pyへ独立した8件の局所回帰を追加する。歴史37正常、現行42正常、欠落、余分、重複、並べ替え、digest不一致、歴史／現行の取り違えをそれぞれ検査し、不正入力は明確に失敗させる。fixtureは各入力のpathとdigestを持つ有限データとし、本体と同じ関数を使うが期待する正常／拒否条件はテスト側に独立記述する。importでmain・外部照会・書込を実行しない。Python実体・版を記録し、構文確認、8件の非ゼロreadiness、30秒上限の局所実行と原本出力を保存する。旧canonicalと既存証拠は保持し、MMU4608の新CIや重い製品試験を反復しない。共通checkerの正式実行は新command承認後に限る（NFR3.4/NFR7.1/NFR9.1）。
63. [ ] 修正差分・歴史37／現行42の対応・回帰結果と既存MMU等の限定再利用をU2成果物に整合し、正式sensors後に全書込を停止して独立レビューを取得する。新しい共通checkerの具体commandを人が正式checkpointで承認した後に実行し、前回Manifest inventory differsの失敗を削除せず、新結果の実exit・出力・hashを保存する。不足／失敗は完了にせず、人のU2完了承認とU11への復帰を確認して承認済み同時dispose修正へ戻る。U9再承認・未修正の同時disposeをU2成功で完了としない。完全Testing Contract/custom順序/80%/30秒/strict guard/比較maskを維持する（NFR3.4/NFR7.1/NFR9.1）。

## 先行計画：Step58〜60（MMU条件不一致の限定追加）

58. [ ] 計画承認・内容確認後、製品sourceを変更せず、署名済みCIの同一snapshotでmmu_u2一対象だけをASan/LSan、seed1、max_len4608 bytes、max_total_time600秒、timeout30秒、rss_limit_mb2048、既存suppressionで実行する。全入力source before/after、両Cargo.lock、実使用compiler full version/commit・toolchain/flags、binary hash、raw出力、実exit/runs/開始終了時刻、corpus/crash、署名・CI SHA/run/jobを成功失敗にかかわらず保存する。旧4096条件601秒exit0は保持し4608成功と扱わない。CPU/decodeは適用条件一致の保存証拠だけを限定再利用し、新実行と数えない。新製品不具合はGAPとして提示し範囲を拡張しない（NFR2.2/NFR3.4/NFR7.1/NFR9.1）。
59. [ ] 既存verify-current-u10-probe-aube-native.pyの全検査項目を保持する新verify-current-u2-u11-revalidated.pyをrecord直下verificationに実装し、構文のみ確認する。旧39入力の3不一致とU11共有有限差分を現在署名source・保存原本へ明示結合し、履歴proof/trace、署名/祖先、artifact最新選択・成功job時刻、native14/emulator16/original argv、guest/compiler/lock/binary、license/deny/receipt/metadata、Rust80%/LCOV/runner44/timings、30秒と比較maskを一つも省略しない。U2担当124/trace92/正式sensors、7品質ASan・4環境14cases・JS母数449、今回MMU4608原本の適用条件を追加する。不足bindingは具体GAPで停止し、ignoreや歴史原本書換で解消しない。候補の正式実行は独立レビューと別command承認後のみ（NFR3.4/NFR7.1/NFR9.1）。
60. [ ] 今回MMU条件・実測結果・checker全検査保持・有限bindingを成果物へ整合し、正式U2 sensors後に書込停止して新しい独立レビューを取得する。具体的確認コマンドを正式checkpointで別途人承認後に実行し、失敗・拒否・未検証を保持する。人のU2完了承認後、engineのU11復帰を確認して承認済み同時dispose修正へ戻る。U9再承認や未修正の同時dispose、全入力安全性をU2結果だけで完了としない。Testing Contract/custom順序/strict guard/80%/30秒/比較maskを維持する（NFR3.4/NFR7.1/NFR9.1）。

## 先行計画：Step55〜57（承認不整合修復後）

55. [ ] 新しい計画承認と内容確認後、U2 manifestの担当ソース、今回のU11共有変更、保存済みCI・fuzz・production wasm Node/実Safari証拠のbytesと適用範囲を照合する。既存整数命令・wasm・共有heapの実装と成果物を保持し、必要な照合記録と正式required-sections/traceability sensorの現行結果を保存する。旧成功を新実行と数えず、不一致は具体的に提示する。製品変更・新たな重い検証へ自動拡張しない（FR1.3/FR1.6/FR9.1、C1/C3/C4/C5、全割当FR/BR/NFR）。
56. [ ] 全記録を確定して書き込みを止め、新しい独立レビューを取得する。現行verification commandの今回ソースへの適用性を確認し、旧commandの不一致・失敗を保持する。新commandが必要なら具体的コマンドと有限の確認範囲を提示し、人の新しい承認を正式checkpointで取得してから実行へ進む。80%下限・30秒watchdog・strict guard・custom順序と比較maskを維持する（NFR3.4/NFR7.1/NFR9.1）。
57. [ ] 承認済み確認コマンドを標準checkpointで実行し、成功・拒否・未検証を区別して保存する。人のU2完了承認後、engineがU11へ進めることを確認してU11作業へ戻す。U2成功だけで全入力・全環境や並行セッションのID競合の完全解消を断定しない（NFR3.4/NFR7.1/NFR9.1）。

## 履歴の計画：Step52〜54（全Unitやり直し後）

52. [ ] 新しい内容確認後、U2設計と共有契約、manifestの担当と現行bytesを照合する。署名済み7eb1819f52acede33e83775374dd4ee93edf643bと現在の担当ソースの一致範囲を記録し、178da99e以前の証拠は履歴として区別する。既存の整数命令・wasm・共有heapを再実装しない（FR1.3/FR1.6/FR9.1、C1/C3/C4/C5）。
53. [ ] 今回の内容確認のもとで4成果物とsource-manifestを保存し、正式required-sections/traceability検査を行う。既存担当要件、後続UnitのDeferred、未検証の限界を保持する。新しい製品不一致があれば限定修正案を提示し、品質下限や比較maskを弱めない（全割当FR/BR/NFR）。
54. [ ] 成果物を確定して書き込みを止め、新しい独立レビューを取得し、承認済み確認コマンドを標準checkpointで実行する。人の完了承認後に次Unitへの遷移を確認する。各操作の成功・拒否を区別し、U1/U2経路の成功だけで並行セッションのID競合の完全解消とは呼ばない（NFR3.4/NFR7.1/NFR9.1）。

## 履歴Step42〜48：R03と製品wasm実装

ユーザーのRequest Changesで製品wasm実装へ範囲を拡張した。旧source変更禁止は今回必要なHost/launcher/shared heap/Worker実装についてのみ上書き。U1承認済み成果物とDocker設定は変更しない。共有契約U11 u11-wasm-launcherがwasmHost/起動JS/SABAtomicsとNode/ブラウザを担当し、U5がguest thread/futex kernel/Host/Runtimeを担当。今回は要求された起動・hello・整数/fault/atomic・共有heap/入れ子Workerの必要範囲を実装し、U5全体、VFS mount/network、JIT、probe/aube全統合へ拡張しない。完全Testing Contract以下は変更しない。

42. [ ] 承認後に実Host/Runtime/Vfs/wasm ABIとU11/U5契約を読み、実装前に設計契約を確定する。native-only依存/型のtarget gating、WasmHostのstdio/random/clock/wait/cancel/未対応capabilityの明示errno、製品wasm crate/exportとConfig/SessionのABI、JS Worker起動/終了/kill/output/errorを定義。共有Rust heapは固定nightly build-std/atomics＋imported shared WebAssembly.Memory、初期化一度だけ、各Worker固有stack/TLS、同期allocator/標準同期型、memory grow所有者、nested Workerへの同一module/memory引渡しを設計する。別instanceの同一memory接続だけを共有Rust heap成功と扱わない。既存APIで安全に実現できない、追加unsafe/契約変更が必要なら具体変更と阻害をrootへ提示し、未確定の危険な初期化を実装しない（C1/C3/C4/C5/C10、NFR3.1/4.1/5.1、U11/U5）。
43. [ ] R03 Safari診断runnerの全操作を30秒絶対deadlineで囲む。AbortControllerでstatus/session/navigation/execute/delete等すべてのfetchを中断し、poll sleepも残時間以内。finallyのcleanupにも残時間/独立短deadlineを設けdriver/server/workerを確実回収、最外process watchdogでハングをkill/reap。応答しないWebDriver fixtureで30秒以内の非ゼロ終了/cleanupを検証し、実Safari正常結果も回帰する（NFR7.1/7.2）。
44. [ ] 意味論実装より先に同一guest bytesの実機x86-64 Linux期待値をCIで取得する。hello stdout/stderr/exit、整数、DIVfault(signal)、atomicを30秒watchdogで比較し、共有heap/nested Worker用の観測条件も先に固定。native期待を保存定数へ置換せず各CIで再生成。新wasm runnerの非ゼロcase readinessを確認（FR1.3/1.6/9.1、BR1.7/2.1〜2.5/4.1）。
45. [ ] native-only cap-std/cap-fs-ext/fs2等とNativeHost実装を適切にcfg/target依存へ分離し、WasmHostを実能力に沿って実装。製品wasm crate/exportと起動JS/Worker launcherを追加し実Session/loader/kernel/CPU/MMU/decoder/Vfs経路でhello/output/exitと整数/fault/atomicを実行。未対応mount/network等を成功返却せず明示する。内部層は実装後に単体/境界テスト、命令意味論変更が必要ならnative Red先行→変更→Greenを守る（U11、NFR2.1/3.1/4.1/5.1）。
46. [ ] 確定設計で実製品moduleの共有Rust heapと入れ子Workerを実装。root Worker→nested Workerで同一memory/module/host状態を共有し、異なるstack/TLS、同時allocation/deallocationとguest共有MMU atomic、wait/notify、終了/kill/timeout、二重初期化防止を非ゼロケースで観測。Node Workerと本物Safari Workerの双方で同じ製品起動経路を検査し、COOP/COEP/crossOriginIsolatedを確認。Rust標準allocator/同期型の共有を検証できなければ具体GAPを残し完了扱いにしない（U11＋必要U5 integration、NFR7.1）。
47. [ ] 固定nightly2026-10-01で製品full wasm build、scoped unit/boundary、native3OS regression、fmt/clippy/依存、Linux workspace coverage80%gateを実行。変更sourceに紐付けたCPU/MMU/decode/load_elf各600秒ASan+既存LSan suppression・seed1・timeout30・rss2048（CPU4096/MMU4608）を実機CIで回収。旧af9b/診断SHAの結果を新sourceの成功へ転用しない。CI Actions SHA固定、JJ SSH署名付きpushとconnector Verified/head確認。実Safari、Node、native raw logs/source/binary/seed/corpus/exitを保存（NFR2.2/3.2〜3.4/8.1/9.1）。
48. [ ] 製品source-manifestへ実際の新crate/JS/生成scaffold/sourceと変更pathsを列挙し、summary/evidence/traceabilityに新実測と旧履歴を分離して反映。診断wrapperを製品launcherの根拠にしない。共有heap/入れ子Worker/guestthreadの実証範囲と未対応能力を明記。sensors/全記録/出力専用diary確定後に独立reviewへ渡し、review中は全書込停止（FR/BR/NFR適用範囲、U11/U5）。

設計上の未確定事項（Step42で根拠を確認）：既存Host traitのブラウザ非同期能力を同期Sessionから扱うABI、Worker固有stack/TLSの初期化方法とshared allocatorの正当性、guest thread要求が今回の共有heapテストに必要な範囲。新unsafeや共有contractの意味変更が必要なら具体設計判断をrootへ返し、Rust std共有を未検証のまま成功としない。

## 履歴Step39〜41：cloneフラグ切り分けと製品wasm検証

39. [ ] 同じlocal image6666753b・権限・toolchainでLSanのcloneフラグ（VM/FS/FILES/UNTRACED）を全組合せの独立child probeで切り分ける。各childを30秒watchdogで回収し、flags/errno/child exit/QEMU登録・versionを保存。fork native x86-64 Linuxでも同じ診断C source/hashを実行し、kernelの不正組合せとQEMU制限を区別する。ptraceを別probeで確認。LSan無効化・製品修正・Docker設定変更は行わない。原因を特定できなければ観測限界を明記する。
40. [ ] actual production cratesとwasm起動経路を読取確認し、固定nightlyでwasm32 buildを実行する。既存起動経路があればその経路をNode Worker/本物Safariで実行する。起動用export/launcherが未実装なら、isolated workspaceの診断wrapperから実製品CPU/MMU/decoder/loader/runtimeを可能な範囲でリンク・実行し、hello guest出力/exitと整数・fault・atomicケースをnative期待値と比較する。診断wrapperをproduction launcherの完成と呼ばず、共有heap/入れ子Workerは実際に同じ製品moduleで確認できた範囲だけ報告する。COOP/COEP、非ゼロcase数、raw/browser/workerログ、source/binary hashesを保存。製品実装が不足する場合は具体的な阻害箇所と後続Unitを示し、本番起動経路の未検証を隠さない。新しい本番launcher実装はこの検証計画には含めない。
41. [ ] 個別flagsの比較結果と製品wasmのbuild/実行/未実装境界をU2 summary/evidence/traceabilityへ反映する。既存4target ASan各601秒成功、実Safari spike、af9b品質gateは別証拠として保持。80%/30秒/nightly/custom順序を維持し、全記録・出力専用diary・sensorsを確定して独立reviewと完了確認へ渡す。診断専用fork workflowの修正/pushは署名付きjjで行い、PR/mergeやU1凍結成果物変更をしない。

## Testing Contract

```json
{
  "version": 1,
  "methodology": "custom",
  "source": "team",
  "ordering": "命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
  "scope": "rust-blink-port",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "私たちはテストを各 Bolt の成果物の一部として扱います。エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まるので、差分テストを中心に置きます。\n\n- **Methodology**: custom\n- **Ordering**: 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。\n\n補足：\n\n- **カバレッジ**（Q5）：行カバレッジ 80% を下限にします。測るのはネイティブの Linux です。あわせて「範囲内の命令のうち、差分テストが 1 件以上ある命令の割合」を記録します。決めた下限は Build and Test で下げません。\n- **差分テストの期待結果**（Q6）：期待結果は、**CI を実行するたびに x86-64 Linux のランナーで作り**、エミュレータの結果と比べます。期待結果をリポジトリに保存する方式は取りません。\n  - 比べるもの：命令の単位ではレジスタ・フラグ・メモリ、プログラムの単位では標準出力・標準エラー・終了コード。\n  - x86 で結果が未定義のフラグや値は比べません。命令ごとに「比べないもの」を表で持ちます。\n  - pid・時刻・乱数・アドレスなど、実行ごとに変わる値は、比べる前にそろえるか、比べる対象から外します。\n  - 段階 5 では、JIT ありと JIT なし（インタプリタ）の結果も同じ差分テストで比べます。JIT だけの意味論は持ちません。\n- **単体テスト**：層ごとに `cargo test` で書きます。テストやビルドの道具は外部のものを使ってよいです（Q1）。\n- **CI のゲート**（Q7）：\n  - 変更のたび（PR）：Linux・macOS・Windows の単体テスト、lint（`cargo fmt --check`、clippy の警告はエラー）、依存の検査（ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること、既知の脆弱性）、x86-64 Linux での差分テスト。通らなければマージしません。\n  - 段階ごと：その段階に入ったら、その段階の probe と aube の合格を必須にします。\n  - 夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）。失敗したら Issue にして直します。\n- **Safari**（Q12）：Safari での合格は、macOS の CI で本物の Safari を動かして確かめます。WebKit を使う別のテスト用ブラウザでは代えません。\n- **wasm**：paludarium が用意する起動用 JS とテストハーネスで、Node.js の Worker とブラウザ（Chromium 系・Firefox・Safari）で同じテストを動かします。テスト用のページには COOP/COEP の見出しを付けます。\n- **揺れるテスト**：スレッドを使うテストには時間切れの上限を付けます。揺れたテストは記録して直します。\n- 段階 5 の「JIT なしより速い」は、回数・統計量・差の大きさを要件分析で数値にしてから測ります。速さの測定は PR のゲートにしません。\n- Test Strategy は Standard です。量と種類はこの設定に従い、上の補足はそれに足すだけです。"
    },
    {
      "layer": "project",
      "text": "- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) \n\n- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) \n\n- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) \n\n- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) \n\n- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) \n\n- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) \n\n- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) \n\n- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) \n\n- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) \n\n- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) \n\n- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) \n\n- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) \n\n- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) \n\n- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) \n\n- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) \n\n- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) \n\n- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) \n\n- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) \n\n- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) \n\n- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) \n\n- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) \n\n- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) \n\n- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) \n\n- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) \n\n- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) \n\n- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) \n\n- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) \n\n- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) \n\n- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) \n\n- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) \n\n- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) \n\n- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) \n\n- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) \n\n- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) \n\n- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) \n\n- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) \n\n- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) \n\n- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) \n\n- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11)"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "custom",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Custom ordering - 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
      "Implementation and tests - preserve that exact ordering; do not convert it to layer-local TDD.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cc8e6bbb985d32c580aff1d457ccafb5f05a4b442140eb6cb6303d51ca2ba418",
  "contract_sha256": "sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5"
}
```

## 根拠・境界（先行attemptの履歴）

ドキュメント根拠: U2 functional-design と NFR requirements の READY 設計、C1/C3/C4/C5、unit-of-work、FR1.3/1.6/9.1 を適用する。stories は生成されていないため架空の AC を作らない。原子命令・MMU indivisible operation・ホスト並列検証は U2、guest clone/futex は U5。SSE は U3、probe/aube 全体統合は U10、JIT は U14。これは probe/aube が必要とする U2 整数命令の範囲を縮める理由ではない。

検証済み: `cargo test --locked -p paludarium-cpu --lib tests::budget_exhaustion_stops_an_infinite_loop -- --exact` は exit 0、1 passed、0 failed、17 filtered out。現在の runner readiness の根拠である。U2 専用ターゲットと filters は未作成で未検証。

ソース観測: CPU の Stop に DivideError が存在し CpuState に REP continuation はない。MMU の read/write/fetch と map/unmap/protect の既存入口をすべて同じ同期機構へ接続する必要がある。現状の原子性・REP fault semantics は未検証。

取得元観測: `../formicarium/guest/probe/{Cargo.toml,Cargo.lock,src/main.rs,src/futex_deadline.rs,src/page_fault_race.rs,src/bin/hello.rs,src/bin/exit3.rs}` がある。`../formicarium/scripts/build-guests.sh:17-18` は aube canonical repository `https://github.com/aubepkg/aube.git`、ref `v2.6.1`。`../formicarium/scripts/measure-aube.mjs` は --version/install/install --frozen-lockfile/list と `fixtures/sessions/aube-1645.txt` を指定する。immutable revisions、guest artifact hashes、完全な命令/forms inventory、runtime traces は未取得。承認前に大きな build は行わない。

## 実行計画（Plan Approval 後のみ）

1. [ ] Runner bootstrap。`crates/paludarium-harness/tests/{diff_u2.rs,parallel_u2.rs}` と必要な harness support、`tests/guests/u2/{build.sh,observe.c}` を用意する。最初の executable testcase 前に、新 harness ターゲットの `--list` が実際の bootstrap ケースを列挙することを検査する。内部層の `u2_` filter は各層の実装後にテストを追加した時点で非ゼロ件数を確認する（Step 4〜12）。まだ作っていない内部層テストを bootstrap の前提にしない。空集合を成功と扱わない。既存 exact readiness と承認後 bootstrap を区別する。BR4.1/NFR7.1。
2. [ ] ソース取得・inventory を固定する。probe の sibling source tree/lock を読み、jj で immutable revision と dirty source の hash を記録する。aube の v2.6.1 を immutable commit に解決し jj で取得、既存 scripts の Git 操作をそのまま実行しない。static-musl artifacts の SHA256、toolchain/build args、session fixture hashes を `docs/u2/inventory.md` に記録。objdump の静的 forms と Linux runtime traces を突き合わせ、probe と aube 4 コマンド/#1645 の全整数 forms、幅、prefix、implicit operands を case ID に対応付ける。取得不能・未分類は具体的 GAP として残し U2 完了を宣言しない。BR1.1/BR4.2/FR1.3。
3. [ ] 実装に先立ち native differential ケースを作り実行する。`tests/guests/u2/*.c` と harness observer で raw register/memory/flags、defined/preserved/undefined masks、入力条件、signal/fault RIP/context を取得する。CI ごとに native を再実行し期待値を生成する。normal、fault、REP restart、atomic parallel ケースを準備し、各 child に外側 30 秒 watchdog、kill/reap を実装する。未提供 native runner を PASS にしない。BR1.3/4.1/NFR1.1-1.3/7.1-7.2。
4. [ ] C1 の arithmetic fault を既存 DivideError と照合し、`crates/paludarium-types/src/lib.rs`、CPU、`crates/paludarium-kernel/src/{lib.rs,tests.rs}`、`crates/paludarium-runtime/src/lib.rs`、harness の全消費箇所を同じ変更で整合させる。DIV/IDIV zero と quotient overflow を guest SIGFPE に変換し host panic を起こさない。内部型の実装後に `u2_` tests を追加する。C1/BR1.7/FR1.6/NFR2.1。
5. [ ] Decoder 接続を `crates/paludarium-decoder/src/lib.rs` と types で拡張する。必要な全 widths/forms、REX/high8、address32/RIP/FS/GS、LOCK/REP legality、128-bit register pair、必要最小 fetch を扱う。外部 decoder 型を public contract に漏らさない。実装後 5–8 件以上の層テストを追加し invalid prefix と truncated fetch を分ける。C3/BR1.1-1.4/3.1-3.2。
6. [ ] MMU の `crates/paludarium-mmu/src/{lib.rs,tests.rs}` に typed atomic request/result を実装する。arbitrary callback を lock 内で実行しない。normal read/write/fetch、initial writes、map/unmap/protect、atomic が共通同期を使う。public-to-public 再入を避ける private helpers と共有 address-space synchronization を設計し sequential consistency を保つ。全 bytes の permission/page validation を mutation 前に完了する。実装後少なくとも 8 件: cross-page/nonaligned、unmapped、read-only、failed CMPXCHG write permission、mapping競合、normal/atomic競合、old value、128-bit。C4/BR2.1-2.4/NFR1.3/4.1。
7. [ ] native ケースを先に追加・実行してから CPU `src/{alu.rs,exec.rs,state.rs,lib.rs}` の move/extend/LEA、integer arithmetic/logic/flags を全 inventory forms 実装する。8/16 partial preservation、32 zero extension、high8/REX、carry/borrow/overflow、defined vs preserved flags を検証する。CPU は Kernel/Host に依存しない。FR1.3/C5/BR1.2-1.4。
8. [ ] native ケースを先に追加・実行してから shift/rotate/bit operations、multiply/divide を実装する。count masks、zero-count flags、signed limits、quotient overflow、implicit operands の各 semantic dimension を検証する。BR1.3/1.7/NFR2.1。
9. [ ] native ケースを先に追加・実行してから stack/control flow と fault commit を実装する。全 memory destinations を prevalidate し、非 REP fault では instruction-start regs/flags/RIP を維持する。invalid LOCK/UD2/unsupported を SIGILL とし、necessary fetch fault と混同しない。BR1.5/3.1-3.2/FR1.6。
10. [ ] native ケースを先に追加・実行してから REP MOVS/STOS/LODS/CMPS/SCAS、DF/address32/count を実装する。REPE/REPNE CMPS/SCAS の fault は完了 count/index を保持し instruction-start flags を復元する。`CpuState` の repeatContinuation に start RIP/identity/start flags を保存し BudgetStop 後も再取得しない。正常終了/fault/別命令で unused context を消す。fault before/after iteration、page crossing、BudgetStop を跨ぐ fault のケースを比較する。BR1.6/NFR1.2。
11. [ ] native ケースを先に追加・実行してから LOCK arithmetic、XCHG implicit lock、CMPXCHG/XADD/CMPXCHG8B/16B を inventory 通り実装する。各命令から MMU one-operation を呼び read/write split を禁止。readonly failed compare、16-byte alignment、page crossing を比較する。ホスト parallel old-value uniqueness、total/success count、normal access と map/protect/unmap race を bounded child tests で検証する。guest clone/futex は U5。BR2.1-2.5/NFR1.3/7.1。
12. [ ] 内部層ごと実装後に happy-path/境界/fault の `u2_` unit tests を追加し実行する（原則 component ごと 5–8 件、CPU matrix は必要に応じ超過）。関係する Kernel/Runtime signal 消費と public API を同時検証し core unsafe 禁止と一方向依存を保つ。FR1.6/NFR2.1/3.1/4.1。
13. [ ] `docs/u2/{inventory.md,flag-masks.md,differential-coverage.md}` を完成させ、命令割合と forms/semantic dimensions の対応・未実施一覧を分けて記録する。範囲内命令の differential case 1 件以上を数値で検査し、全 forms の不足を成功扱いしない。U1 `diff_u1` と既存 CPU readiness regression を再実行する。BR4.2/NFR3.3-3.4。
14. [ ] `fuzz/fuzz_targets/{cpu_u2.rs,mmu_u2.rs}` と `fuzz/Cargo.toml`、既存 CI nightly 設定を更新し bounded CPU execution、固定 region/permissions/instruction budget を使う。新規 cpu_u2/mmu_u2 と既存 decoder/ELF fuzz の各 target をそれぞれ夜間 600 秒・ASan、seed/input を保存。新 product dependency は導入せず core unsafe を使わない。NFR2.2/8.1。
15. [ ] unit-scoped fmt/clippy と差分/並列/内部 tests を実行し、Linux workspace 行 coverage 80% の既存 overall gate を別途維持する（unit subset coverage で代替しない）。nightly-2026-10-01、Cargo.lock、crates.io 制限、cargo-deny、Actions SHA を維持し閾値を下げない。NFR3.2-3.4/8.1/9.1。速度評価は U2 に追加しない。
16. [ ] 実装後のみ code-summary.md、traceability.json、README、source-manifest.json を作成し FR/BR/16 detailed NFR を実行ログへ接続する。source claims は build 成果物/cache を除き、generator/shell/scaffolding が書いた application-source も全て実ファイルとして列挙する。未検証と取得 GAP を明示しレビュー・completion は conductor に渡す。






## 先行attemptの再確認計画（Step17〜19の履歴）

## 現在attemptの実行対象：Step49〜51

今回の対象は以下の3手順のみ。Step1〜48は先行attemptの履歴として保持し、製品wasm・共有heap・nested Workersを再実装しない。U1の修正済み成果物を保持し、ユーザーが依頼したU4/U9の修正は後続の各Unitへ引き継ぐ。

49. [ ] U2 manifest全claimsと署名済み178da99e88d1aea242c5141207887767a69fa670の保存証拠を照合する。CI8jobs、ASan/LSan4targets各601秒、native診断2jobs、production wasm Node/実Safari14cases、coverage80%gateを適用範囲付きで確認する。新実行と数えず、不足を具体的に報告する（FR1.3/1.6/9.1、NFR1/2/3/7）。
50. [ ] U2対応表とrequired-sectionsの限定sensorを実行し、結果を保存する。code-summary/evidence-currentへ現行sourceとの対応を追記し、旧CI/LSan失敗/診断wrapperの観測と区別する。現在の4成果物とmanifestを内容確認後に保存し、旧承認を今回へ転用しない。Testing Contract、80%、30秒、固定nightly、各600秒と比較maskを保持する（全割当FR/BR/NFR）。
51. [ ] 記録と出力専用diaryをレビュー前に確定し、全書込・jj snapshotを止めて独立レビューとcanonical Unit完了検査を受ける。新しい製品変更や重い試験の反復は行わず、具体的不足が見つかれば最小対応を提示する。U4の証拠表記とU9の公開型修正は未完了の後続対応として保持する（NFR3.4/9.1）。

上記Step1〜16、初期source観測、旧Plan Approvalと実装証拠は先行attemptの履歴である。今回の対象は現在のU2 source・固定inventory・保存済み検証の対応を再確認し、新しい承認の後に独立reviewへ渡すことである。初期の『未作成』『DivideError』『未取得』は計画作成当時の状態で、現在の状態とは区別する。U1とU2の既存READY成果物、application sourceは今回のPart1では変更しない。

検証済み：今回読取のexec.rs SHA256=e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0は保存済み最終検証source値と一致。U2 source-manifest.json SHA256=40233c4c56fd123f8977c9a4fda94f58b38b32e9b8762bc58bae62f24bf972cc。これだけで他の全sourceの不変を断定せず、承認後にclaimsと証拠対応を確認する。今回renderの完全Testing Contractをそのまま保持した。

17. [ ] 現在のsourceと検証器の準備を確認する。U2 manifest claimsと既存source、C1/C3/C4/C5 consumer、FS/GS全atomic linear address、REP continuationを保存済み最終証拠と照合する。docs/u2/repairs/r01-workspace-coverage.txtのU2差分38/host parallel10/CPU31、全体197/94.00%、各nativeケース30秒watchdogとrunner存在を確認。旧実行を今回の新実行とは表現しない（FR1.3/1.6/9.1、NFR1.1〜1.3/3.3/7.1）。
18. [ ] pinned source/lock/builder/binary receipt、aube4658/probe865分類分母と整数forms3136/696、幅/prefix/implicit operandのnativeケース対応、取得履歴・bounded trace限界を照合する。未分類または必須case証拠の欠落が見つかれば具体GAPを残す。production不変なら再取得・全実装・各10分fuzz・全体coverageを重複実行しない。新しい意味論修正が本当に必要ならnative Red先行→修正→Green、内部tests-afterというcustom順序を維持し、関係するunit限定commandsと必要な全体gate/fuzzを回収する。80%/30秒/nightly pinを変更しない（BR1.1/4.2、NFR2.2/3.1〜3.4/8.1/9.1）。
19. [ ] 承認後の確認結果をU2 code-summary/traceability/evidenceへ現在値と履歴を分けて記録し、source-manifestの全application-sourceを確認して独立reviewへ引き渡す。U1 artifacts、既存READY review、application/shared docsは不要に編集しない。macOS/wasm/U5/U10/U14や任意全入力の合格へ範囲を広げない。別projectのbackground wasm buildは停止せず、速さの測定はしない（全割当BR/詳細NFR）。

## 先行attemptの復旧計画（Step20〜23の履歴）

Step1〜19のチェックとexec.rsの旧SHA256は過去の対象sourceに対する記録である。U1復旧で共有CPU/REPと観測fixtureが変更されたため、旧hash一致・197件/94.00%・各600秒fuzzを現在sourceの合格証拠へ転用しない。Testing Contractは上記完全JSONを保持する。stories未生成のため架空のstory/ACは作らず、既存FR/BRと固定inventoryへ各手順を対応付ける。

20. [ ] 承認後、全U2設計/NFR/契約/unitsと現在sourceを読み、固定inventory・C1/C3/C4/C5 consumer・manifest claims・source bytesを照合する。REPfaultの明示policy（Intel RestoreInitial既定、AMD PreserveCompleted）とvendor選択を行うnative差分fixture、start/partial/budget/fetch回帰を、U2のBR1.6・NFR1.1〜1.2へ接続する。旧Step10の一律flags復元は当時の設計記録として保持し、現在の両modelの検証事実と区別する。runner/filtersの非ゼロ件数と30秒watchdogを確認する（FR1.3/1.6/9.1、BR1.1〜1.7/2.1〜2.5/4.2）。
21. [ ] 直近production CI source `4d52be0a6f3b11d6c11a62f96196985c9c280fdc` の11job成功ログを実際のsource bytesと照合し、native U2 diff38/parallel10、3OS・lint・依存・全体/U1 coverageの証拠を適用範囲付きで再利用する。現在の内部filter件数は承認後に確認し、旧CPU31などを現在件数と推定しない。不足がある場合だけunit-test-instructionsのexact限定回帰を実行する。Docker VMM/QEMUの観測は実機native期待値と分ける（NFR1.1〜1.3/3.2〜3.4/7.1〜7.2/8.1）。
22. [ ] 現在sourceで必要な修正が見つかった場合は具体GAPと最小変更をconductorへ提示し、許可された範囲で命令native期待結果・Redを先に確定してから実装、内部層tests-afterで確認する。production変更時は必要なnative差分・全体80%gate・関係fuzzを回収する。既存各600秒ASan・nightly-2026-10-01・比較mask・30秒watchdogを弱めない。古いfuzzと未実行wasmは現在sourceでは未検証と記録する（NFR2.1〜2.2/3.1/4.1/8.1/9.1）。
23. [ ] U2 code-summary/traceability/source-manifest/evidenceを現在source snapshotと検証ログに更新する。shell/generator作成sourceと関連共有sourceの所有境界を列挙し、履歴と現在証拠・未検証を分けて独立reviewへ渡す。U1凍結artifacts/sourceと他unit機能を変更せず、取得済みinventoryの分母を縮めない（全割当FR/BR/詳細NFR）。

## 先行attemptの記録再確認計画（Step24〜26の履歴）

## redo新attemptの計画（承認後のみ）

27. [ ] 現在95claims/snapshot、固定inventory・契約・REP両modelを4d52be0aの保存CI11jobsと再照合する。一致範囲で差分38/並行10、内部非ゼロ、3OS/lint/依存/coverage証拠を再利用し新実行と数えない。不足だけ既存exact commandsで回収する（FR1.3/1.6/9.1、NFR1/3/7）。
28. [ ] 新Summary Confirmation後に実4producesであるplan/unit-test-instructions/code-summary/traceabilityとsource-manifestを全て保存する。既存claims/schemaと正確な証拠を保持し、現在各600秒ASanのNFR2/NFR3/NFR2.2/NFR3.4 GAPとwasm未検証を維持する。製品不具合はrootへ返し自動修正しない。80%/30秒/nightly2026-10-01/各600秒/masks/custom順序を保持する（全FR/BR/NFR）。
29. [ ] 親construction/code-generation/memory.mdへ読取なしheading anchored追記をレビュー前に完了する。全書込を終え、reviewrequestからterminalまでsource/成果物とjj snapshot/commit操作を停止してrootへ渡す。前回不整合原因は未確定として扱う（NFR3.4/9.1）。

## 履歴：Step30〜32の記録確認

ドキュメント根拠：U1で確認した現行署名済みCI commitはaf9b739d742a9552f44fc1515646c862b19e5de2。U2の既存記録は4d52時点のため、現在sourceへそのまま転用しない。stories未生成のためFR/BR/詳細NFRを手順へ対応付け、架空のACは作らない。今回の対象は既存実装と証拠の再照合および要件担当分類であり、整数命令の範囲や品質下限は変更しない。

30. [ ] 現在U2 manifest全claims、固定inventory、C1/C3/C4/C5とREP両modelを現行af9bの保存済みCI7+native4jobsへ照合する。署名、source bytes、U2差分38/並行10および内部テストの非ゼロ件数、3OS/lint/依存/行coverage80%の証拠を確認し、4d52と旧fuzzの観測を履歴として区別する。不足がある場合だけ既存unit限定のテストコマンドで確認し、native実行不可をPASSにしない（FR1.3/FR1.6/FR9.1、BR1.6/BR4.1/BR4.2、NFR1.1〜1.3/NFR3.3/NFR7.1）。
31. [ ] 既存BR/詳細NFRの対応とGAPを保持し、共有requirementsのFR/NFR全IDをU2担当・後続担当・非該当に分類してtraceabilityへ反映する。後続要件は共有Unit定義を根拠にDeferredとし、FR5.4はU5のnative thread割当とU11のwasm Worker割当も含め担当説明を確認する。NFR2/NFR3/NFR2.2/NFR3.4の現在sourceに結び付いた各600秒ASan証拠が不足する場合はGAPを残し、任意入力の安全性・本番wasm・probe/aube全体・JITを合格としない。required-sections/traceability検査の実結果を保存する（全割当FR/BR/NFR）。
32. [ ] 内容確認後にU2 plan/instructions/summary/traceability/source-manifestと証拠を保存し、現行af9bと過去4d52を明示して独立レビューへ渡す。親diaryは出力専用でレビュー前に確定し、以後成果物とclaimed sourceの書込を停止する。新たな製品不具合が見つかった場合は具体的GAPと必要な最小修正を提示し、U1の承認済み成果物を変更しない。80%・30秒watchdog・nightly-2026-10-01・各600秒ASan・比較maskとcustom順序を維持する（NFR2.2/NFR3.4/NFR7.1/NFR9.1）。

## 今回の計画：Step33〜35（新Plan Approvalと内容確認後のみ）

現在sourceのCPU/MMU各600秒ASanを測定して残る品質GAPを実測範囲で扱う。製品source・U1成果物は変更しない。完全Testing Contract、custom順序、80%coverage、30秒watchdog、nightly-2026-10-01、各600秒、比較maskを保持する。Docker availability/ASan runnerは現在未検証。

33. [ ] Docker接続と既存Linux runner、固定nightly/ASanの準備を確認する。host/container環境、image ID、source SHA256、lock/target/suppression、seed1、初期corpus/archiveを記録。一度だけ同期した同一snapshotを使い、両target終了と証拠回収まで再sync・並行compile/trace/fuzzを禁止。runner不可なら理由・未検証と再開手順を残し、条件を弱めない（NFR2.2/NFR7.1/NFR9.1）。
34. [ ] cpu_u2（max_len4096）、次にmmu_u2（max_len4608）を同一containerで各600秒ASan・seed1・timeout30・rss2048により逐次検査する。各exit・開始終了・実行量・sanitizer raw出力・corpus/artifactsを保存。CPU失敗も記録してMMUを確認し、短縮・未実行・timeout・panic・ASan異常をPASSにしない。LSan既存suppressionを増やさない（NFR2.2/NFR3.4）。
35. [ ] source before/after hash、raw logs、各exit/timing、sanitizer、seed/corpusを証拠化し、実測CPU/MMUだけについてNFR適用範囲を更新。他target・任意入力・production wasm・std heap・入れ子Worker・全vendor合格は推定しない。失敗/runner不可ならGAPを保持。既存CI/80%証拠と限定検査を保持し、成果物・出力専用diary確定後に独立レビューへ渡す。製品修正が必要なら別途最小変更を提示する（NFR2/NFR3/NFR2.2/NFR3.4）。

## 今回のStep36〜38（新承認後のみ）

Request Changes対象は旧未実行表記修正とfork実機x86-64 Linux CIでの原因調査。Step33〜35はCPU636751/MMU910789各601秒・LSan終了fatal/exit1の履歴。完全Testing Contract、custom順序、80%、30秒watchdog、nightly-2026-10-01、各600秒を保持。storiesなし、架空ACを生成しない。

36. [ ] af9b739d742a9552f44fc1515646c862b19e5de2基準のisolated jj workspaceを作成し、診断専用bookmark codex/u2-asan-diagnosticへ必要最小workflowのみ追加。SSH署名付きjj pushでfork CIを起動し署名/SHAを確認（PR/mergeなし）。現checkout/U1/製品sourceを変更しない。native ubuntu x86-64 runnerとLinux containerの固定toolchain/ASan/LSan readiness、最小C終了診断、全関連source bytehashを固定（NFR2.2/7.1/9.1、C1/C3/C4/C5）。
37. [ ] 同SHA固定snapshotでcpu_u2/mmu_u2/decoder/load_elfを各600秒ASan、既存LSan suppression、seed1、timeout30、rss2048で実行。CPU max_len4096/MMU4608、decoder/load_elf既存設定保持。同runner順次または同SHA固定job matrixを使用し、rawlogs/exit/runs/timing/toolversion/sanitizer/source/corpus/crashを常時upload。Actions SHA固定維持。失敗原因を診断し必要なdiagnostic-only workflow修正で再実行できるが時間/LSan条件を弱めない。製品不具合はroot判断（NFR2/2.2/3/3.4/8.1）。
38. [ ] 旧未実行表記を実結果/履歴へ修正し実測範囲だけGAP更新。任意入力/production wasm/共有std heap/入れ子Workerへ推定しない。summary/evidence/traceability/manifest、狭いsensors、出力専用diary確定後に独立review。現workflow21runsはCI/nativeのみでnightly証拠ではない。af9b native差分38/並行10・80%gateは別証拠として保持（FR1.3/1.6/9.1、BR1.1/1.6/2.1〜2.5/4.2、NFR2/2.2/3/3.4/9.1）。

## Step24〜26の説明と手順（履歴）

Step1〜23の完了・旧承認・reviewは履歴。製品を再実装せず、完全Testing Contractを保持し、現在証拠を新しいレビュー記録へ接続する。U1/U4凍結成果物を変更しない。

24. [ ] 現在U2 snapshot/manifest、固定inventory、C1/C3/C4/C5、Intel RestoreInitial／AMD PreserveCompletedのREP両modelを照合する。署名済み4d52be0aのCI7+native4jobsに現在bytesが一致する範囲でnative差分38/並行10、内部非ゼロ件数、3OS/lint/依存/coverage証拠を再利用する。新実行と区別し、不足だけ既存限定commandsで回収する（FR1.3/1.6/9.1、BR1.6/4.2、NFR1.1〜1.3/3.3/7.1）。
25. [ ] U2 code-summary/traceability/source-manifest/evidenceと必要snapshotを最小整合する。旧fuzzを現在600秒ASanの合格へ転用せず、wasm/現在fuzz未検証と取得範囲の限界を保持する。新製品不具合があればrootへ返し、自動で実装範囲を広げない。80%/30秒watchdog/nightly2026-10-01/各600秒とflags maskを保持する（全割当FR/BR/NFR）。
26. [ ] 親construction/code-generation/memory.mdへ出力専用heading anchored追記をレビュー依頼前に済ませ、記録とsourceを固定してrootへ渡す。reviewrequestからterminal記録までは全worker書込とjj snapshot/commit操作を停止する。前回不整合の原因を断定せず、rootの独立reviewへ渡す（NFR3.4/9.1）。
