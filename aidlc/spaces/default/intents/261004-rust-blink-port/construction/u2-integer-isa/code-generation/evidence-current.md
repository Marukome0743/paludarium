# U2 現在sourceとCI証拠の照合

## 現行Step52〜54：全Unitやり直し後のU2照合

今回Summary Confirmation `3a887c7b37a8bb5d996fe43b58eab51c90b4991490d66f7ab7d45b45fdbad231`後に実施。検証済み：read-only `jj --ignore-working-copy file show -r 7eb1819f52acede33e83775374dd4ee93edf643b <manifest writes[].path>`でmanifestの124ファイルを署名済み検証対象7eb1819fのraw bytesへ照合し、124/124一致・不一致0・欠落0。SHA256両値と各jj終了コードはverification/step52-source-claims-proof.json。manifestの担当/schemaと既存製品を維持し、U11承認済み作業・他Unitの成果物は変更していない。

ドキュメント根拠：U2 functional-spec/rules/entitiesと共有requirements、unit-of-work、C1/C3/C4/C5を読取確認。整数命令・例外・REP・MMU原子操作の担当、U5のguest clone/futex、U11のWorker、U14のJITの境界を保持する。既存traceability92 IDsのstatus/targetは変更しない。旧178da99e以前のCI・Safari・各601秒ASan/LSanとそのsource一致は各履歴当時の観測であり、7eb1819f全sourceの新実行成功へ転用しない。

今回の製品テスト再実行はなし。現在の署名/CI/coverageとの対応は共有verification/u10-current-proof.jsonの7eb1819f/CI38021278452を入力とし、承認済み `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py` を親の標準checkpointで確認する（この記録時点では未実行）。124claim一致から全workspace・全入力・全環境の一致や安全性を推定しない。現source全体の新ASan/LSan、今回のNode/Chromium/Firefox/本物Safari実行、並行セッションID競合の完全解消は未検証。strict guard、80%下限、30秒watchdog、各600秒fuzz、固定nightly、native先行/内部test-afterと比較maskは維持。

正式required-sections/traceabilityの実結果はverification/step53-sensors.jsonへ保存する。4producesとsource-manifestを今回内容確認のもとで保存し、Step54の独立レビュー・canonical checkpoint・人の完了承認・次Unit遷移は親へ引き渡す。

## 現行Step49〜51：保存証拠と対応表の確認

今回Summary Confirmation `b81c718d0776da2c51eb806cbdcb70e4f4d44ba3c008d5655931b140a30de232`後に実施した記録確認である。検証済み：source-manifestの124claimsは、read-only `jj --ignore-working-copy file show -r 178da99e88d1aea242c5141207887767a69fa670 <path>`とのSHA256比較で124/124一致、claim内の文書例外0。manifest SHA256 a3b68721fb3659100c1644729ed689235d5862a80cefb4ffa2847d9c07dc3ebaと全paths/両hashはverification/step49-source-claims-proof.jsonへ保存した。製品・U1・他Unitに変更はない。

検証済み：承認済みcanonical `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。全186 tracked application filesを同じ署名済み178da99eへ照合し、docs/reports/wasm-threads.mdの厳密hashによる既存文書例外だけを区別した。CI37745425190の8jobs、sanitizer37745425204の4jobs、native37745425183の2jobsは同一SHAで成功。実コマンド・stdout/stderr/exitはverification/step49-native-ci.jsonとstep49-native-ci.log。保存済み証拠の再確認であり、新しい製品テスト実行とは数えない。

検証済み：既存step47-proof/CI metadata/step45実Safari証拠の内容とhashを照合しverification/step49-evidence-reuse.jsonに集約した。Node/実Safari14ケース、production CI wasm SHA cb37fa85a9818f96b821785e3d1a8538ec0cb078ca5e79223ee3839053ba3e78、shared Rust heap/nested Workers、CPU2155757/MMU3189042/decode142758823/load_elf23166884 runs・各601秒ASan+LSan exit0・source154before/after/host一致を保持する。全体92.68%・U1対象83.04%・U9対象82.55%の80%gateは同runの証拠。固定nightly-2026-10-01、seed1、timeout30、rss2048、CPUmax_len4096/MMU4608、既存suppression・比較mask・native先行/内部test-afterを変更しない。診断push CIの観測でありscheduled nightly実行とは呼ばない。

未検証：任意guest/任意入力の完全保証・全UB不在、guest clone/futex全意味論、JIT、Chromium/Firefox今回実行、mount/network、probe/aube全統合。共有C1/C3/C4/C5・Host境界を維持し、U5/U11/U14等の全機能完了へ広げない。U4証拠表記修正とU9公開型修正は後続対応として未完了。Step51の独立レビュー・正式Unit完了確認は親担当である。

検証済み：限定sensorの実コマンド・stdout/stderr・exit・passはverification/step50-sensors.jsonに保存した。traceability/required-sectionsは両方exit0/pass:true/findings0、H2=13。今回4producesとmanifestは上記内容確認後に保存し、124claimsと既存traceability分類を保持する。

## 履歴：以下はStep1〜48当時の記録

以下の「現行」「今回」「未検証」「未実装」「GAP」は各先行記録時点の状態であり、Step49〜51の現在sourceに対する主張へ転用しない。旧4d52/af9b、local LSan失敗、診断wrapper、旧CIと最新178da99e production観測を区別する。現在値は上記確認とstep49/50証拠を参照する。

## 履歴Step42〜48：実 production wasm と R03 修正

検証済み：新 paludarium-wasm cdylib と C12 JS launcher が既存 Config/Session→loader/Vfs/kernel/CPU/MMU を実行する。WasmHost を target gating し、native semantics は変更しない。共有 build-std/atomics の Rust allocator/Arc/Mutex/OnceLock、独立 stack/TLS、coordinator→nested Worker、正常 return 後の解放、trap 時の全 heap 破棄を実装した。manifest124 claims が実ファイルを列挙する。詳細は production-wasm-notes.md。

検証済み：実機 native6 ELF の先行期待値と SHA を照合し、Node/本物Safari 各14ケース PASS。hello出力/exit0、integer42、atomic146、Kernel SIGFPE8、stdin input\n、kill9、4同時Session、shared Rust allocator256操作、同一 AddressSpace atomic2000、wait0/notify1、factory再初期化、active stdin待ちdisposeを確認した。旧CPU wrapper136を製品signalと読み替えない。

検証済み：最終 fork CI head178da99e88d1aea242c5141207887767a69fa670、署名Verified=true、CI37745425190の8jobs全success。Linux/macOS/Windows、fmt/clippy/dependencies、native差分、production Node14件、lines全workspace92.68%/U1対象83.04%/U9対象82.55%（各80%以上）。CI生成wasm SHA cb37fa85a9818f96b821785e3d1a8538ec0cb078ca5e79223ee3839053ba3e78 を実Safari27.0.1で14件PASS、1871ms、COOP/COEP/crossOriginIsolated/cleanup=true。ローカル生成module SHA5c76de…とはbytes異なるので同一binaryと表現しない。verification/step45-production-wasm/ci-safari-report.json、step47-production-ci-artifacts/、step47-coverage.log が実測。

検証済み：R03全fetch/poll/cleanupにdeadline、最外process-group watchdog30秒。応答しないdriverは28400.43msで非ゼロ終了、残留なし。旧Step40履歴は変更しない。verification/step43-watchdog/unresponsive-proof.json。

未検証：任意全guest/全UB不在、guest clone/futex全意味論、JIT、mount/network、Chromium/Firefox、probe/aube全統合。後続Unit全体の完了を推定しない。検証済み：最終sourceのCI37745425204でCPU2155757/MMU3189042/decode142758823/load_elf23166884 runs、各601秒、ASan+LSan終了exit0、source154件before/after/host一致。seed1・timeout30・rss2048・max_len4096/4608・既存suppression維持。verification/step47-proof.json を参照。nightly/80%/30秒/custom orderingを維持する。


## 履歴Step39〜41：clone切り分けと製品wasmの適用限界

検証済み：Step39の同一C source/hashで64caseのclone比較検査PASS（verification/step39-clone-proof.json、step39-clone-diagnosis.md）。local QEMU10.2.3はflagsなし/SIGCHLDだけ成功42、残るflags15組/SIGCHLDとsignal0全16組はEINVAL。native実機x86-64 Linuxは32組すべて成功42。ptraceはlocal ENOSYS/native成功、最小LSan local終了1/native2回0。VM経路ではSIGHAND/THREAD/SYSVSEMの必須flags不足、fork経路ではFS/FILES/UNTRACEDと非SIGCHLDが拒否され、単一flagだけを原因とはしない。同version公開QEMU sourceとの一致はドキュメント根拠で、配布binary内部branch/独自patchは未検証。LSan直接失敗点はclone EINVALによるtracer生成失敗。local customimageとnative CI imageは別image。native run37739732442/headb44049356ce2537720487310bd15b1fcf0217c88 Verified=true。

検証済み：Step40でactual production APIs/起動経路を読取確認。production Session/ConfigはRust APIだがwasm export/JS production launcherは存在せず、spikes/wasm-threadsは別module。固定nightly2026-10-01でcargo build --locked --release --target wasm32-unknown-unknown -p paludariumはexit101、isolated full Session wrapperもexit101。paludarium-hostの無条件cap-std/cap-fs-ext/fs2依存からerrno0.3.14がtargetOS unknown unsupportedのcompile_error。production-build.log/full-runtime-build.log、full-runtime-Cargo.toml/full-runtime-lib.rsに失敗と構成を保存。loader→Vfs→Host/kernel/runtimeもこのfull buildの阻害対象。製品修正や新本番launcher実装は行っていない。

検証済み：製品CPU/MMU/decoder/typesをリンクした独立診断cdylibはwasm32 release/locked build exit0。同一core.wasmをNode24.21.0 Workerと本物Safari27.0.1/macOS Workerで各3cases実行、外側30秒watchdog、Safari COOP/COEP・crossOriginIsolated=true、両exit0。整数exit syscall引数42、atomic exit syscall引数146、DIVのCPU ArithmeticFaultを診断encoding136として観測。実機nativeの同guest SHA（integer42/atomic146/divide_fault SIGFPE=-8）との限定比較PASS。ArithmeticFault136はwrapperの診断値で、Kernelのguest signal配送やstdout/exit全runtimeの成功ではない。native helloのstdout hello\n/exit0は取得済みだがwasm hello/runtime実行はbuild阻害で未検証。

具体証拠：verification/step40-wasm/{Cargo.toml,Cargo.lock,src/lib.rs,core.wasm,core-build.log,production-build.log,full-runtime-build.log,guest-hashes.json,node-check.mjs,node-report.json,safari-check.mjs,safari-report-host.json,proof.json}。native期待はverification/step39-ci-artifacts/u2-native-guests/results.json。Safari初回sandbox fetch失敗はsafari-report.jsonに保存しhost権限再実行で実Safari結果を取得。proofはwasm/source/全診断artifact hashes、nativeguest hash比較、3cases×2環境、限定passを記録。production127source baseline一致、95claims再照合はverification/step41-source-claims-proof.json。

未実装/未検証：core module memoryはshared=false、imports0。共有std heap、製品moduleを共有する入れ子Worker、production launcher/host/runtime/loaderのwasm実行は未検証。独立Workerがsingle-memory moduleを実行できることからthread共有を推定しない。共有inception/units-generation/unit-of-work.md:124〜131のU11 u11-wasm-launcherがwasmHost/起動JS/SABAtomicsとNode/Chromium/Firefox/Safariを担当。thread/futex kernel/Host/Runtime意味論はU5、JITはU14の責任を保持。Step37四target各601秒ASan+LSan成功、実Safari spike、af9b unit/diff/80%gateは別証拠。全入力/全UB/全vendorの合格を主張しない。nightly/80%/30秒/custom順序を維持。


## 履歴Step36〜38：fork実機x86-64 Linux診断CI

検証済み：[診断run37736496982](https://github.com/Marukome0743/paludarium/actions/runs/37736496982)、SSH署名済みhead77663b7982857cba841c91d4b23b44287bb8e29bで4jobs成功。af9b739d742a9552f44fc1515646c862b19e5de2基準のisolated jj workspaceへ診断workflowだけを追加した。製品source127pathsはbaseline/CI container before-after/現在hostで全hash一致（verification/step36-ci-source-baseline.json、step37-ci-artifacts-proof.json）。診断SHAと既存af9b CI37713953347/native37713953340のunit/differential/coverage証拠は別枠であり、診断を既存suiteの新実行とは数えない。main checkout/U1/製品sourceの変更なし。

検証済み：cpu_u2=2104569、mmu_u2=4900201、decode=86019257、load_elf=16609257 runs、すべて601秒・exit0/source-compare-exit0。各bundleの最小C ASan終了診断は2回ともexit0。native x86_64 Linux container、nightly-2026-10-01、cargo-fuzz0.13.2、ASan binary symbols、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、ASAN_OPTIONS=detect_leaks=1、seed1、timeout30、rss2048を確認。CPU max_len4096/MMU4608を維持。sanitizer異常・LSan fatalは観測0。これは診断用push CI実行でありscheduled nightly実行とは呼ばない。

具体証拠：verification/step37-ci-jobs.json、step37-ci-raw.log、step37-ci-artifacts-proof.json。4bundleはverification/step37-ci-artifacts/u2-asan-{cpu_u2,mmu_u2,decode,load_elf}/で、各target.log、exit.txt、start.txt/end.txt、source-before.sha256/source-after.sha256、source-compare-exit.txt、settings.txt、environment.log、binary-symbols.txt/binary.sha256、minimal-{1,2}-exit.txt、minimal-settings.txt、corpus-before.tar/corpus-after.tarを保存。proofに各archive SHA256と全artifactファイルhash、実測runs/秒数・全checksを記録。verify-step37-ci-artifacts.pyの検査PASSを根拠とする。

検証済み：先行Step33〜35のlocal失敗は保持。rootの追加診断verification/step36-local-diagnostic.md、step36-local-binfmt.txt、step36-local-ptrace.txt、step36-local-lsan-syscalls.logに、同image/権限のQEMU x86_64登録、ptrace ENOSYS、最小C LSanのclone(...CLONE_UNTRACED...) EINVAL、Failed spawning a tracer threadを保存。直接失敗点はLSan tracer thread生成。推測：QEMU user-mode制約との整合性が高いが拒否された個別clone flag/版固有原因は未検証。既存suppressionやLSanを弱めず実機CIで合格を回収した。

検証済み：connector保存step37-ci-run.json/step37-ci-artifacts.json、step38-source-claims-proof.jsonの95/95現在claims一致、step36-ci-workflow.ymlのexactcopyも参照。CI rust:1-bookwormのpull digestはsha256:114c7a4425406451c2866b6aafe69fe29b1b298832db1277d411ac73c82d04d6（step37-ci-raw.log:74/1822/5667/14299）。Docker config imageIDは未記録でdigestをimageIDとは呼ばない。local customimage6666753bとCI imageは異なるため完全同一image比較ではない。localのclone EINVAL/ptrace ENOSYSとCI成功を分け、個別clone flag/版固有原因は未検証とする。

対応範囲：NFR2/NFR2.2/NFR3/NFR3.4の不足した現行fuzz証拠を回収しU2責任範囲のOKへ更新。NFR3は既存unsafe禁止/lint/80%coverageと今回fuzzを組み合わせる。全体FR9.3は後続syscall_args/VFSを含むためDeferred維持。任意入力完全保証・全UB不在・native意味論一致・全vendor・production wasm・共有std heap・入れ子Worker・他Unitの合格へ推定しない。旧4d52 metrics/旧r01 fuzz/local失敗は履歴。以下の4GAP維持/新CI未検証/未実行という記述は各過去時点の観測で、現行状態は本節を参照。80%/30秒/nightly/各600秒/custom順序を保持する。


## 履歴Step33〜35：CPU/MMU各600秒ASan（失敗証拠）

検証済み：承認後に既存Docker image6666753bed3a753ce9f178d5a76bd91ff1de45cf6918a273fe9a43892eb51971を使い、単一同期snapshot/同containerでcpu_u2→mmu_u2を順次実行。固定nightly-2026-10-01、cargo-fuzz0.13.2、ASan、seed1、timeout30、rss2048、max_len4096/4608、既存LSan suppressionを維持した。cpu_u2は636751 runs/601秒、mmu_u2は910789 runs/601秒だが、両方終了時にLeakSanitizer fatalでexit1、総command exit1。ASan本体の入力処理中に異常は観測しなかったが、終了検査を含む合格ではない。raw cpu_u2.log/mmu_u2.logと各start/end/exit、corpus-before/after.tar、source-before/after.sha256はverification/に保存。

検証済み：source before/after cmp exit0。host127実ファイルは全一致、containerのみ32件はmacOS tar由来の._AppleDouble metadata（sourceではないがraw159件に保持）。hostとのSHA照合と実時刻はverification/step35-current-asan-proof.json。実process環境に-Zsanitizer=address、ASAN_OPTIONS=detect_odr_violation=0（cargo-fuzz設定）、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、固定nightlyを確認し、両binaryのASan symbolsをstep33-sanitizer-runtime.txtに保存。Docker実argsはCAP_SYS_PTRACE/seccomp=unconfined/stack=-1、uid0、LinuxKit7.0.14、aarch64Docker上amd64image。ptrace_scope pathは存在しない。step33-docker-inspect.json/step33-docker-info.txtが実構成。

検証済み：製品に依存しない最小C main{return0;}をcc12.2/ASan/同image・権限・LSanenvで2回確認し、両exit1・同LSan fatal（step35-minimal-asan.txt）。終了処理のrunner問題を再現した。推測：amd64エミュレーションとptrace制約が原因候補であり、実QEMUbinfmt未確認のため原因確定ではない。ドキュメント根拠：[QEMU user emulation](https://www.qemu.org/docs/master/user/main.html)のptrace制約、[LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html)の終了検査説明。LSan無効化・suppression追加・retryによる合格化は行わない。

GAP：NFR2/NFR3/NFR2.2/NFR3.4の4GAPを維持。decoder/ELF等の現行600秒、production wasm、共有std heap、入れ子Worker、任意入力安全性は未検証。実機native差分38/並行10と80%下限の保存af9b CIは別証拠として保持する。再開手順：LSan終了検査を実行できるx86-64 Linux runnerでunit-test-instructions.mdの同一snapshot/seed/予算/品質条件をそのまま実行し、両exit0とsource不変を回収する。今回source変更なし。


## 履歴Step30〜32：af9bの記録照合

検証済み：今回Summary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3、UNIT_STARTED後、jj --ignore-working-copy file show -r af9b739d742a9552f44fc1515646c862b19e5de2 <path>とSHA256でU2 manifest95claimsを独立照合し、95/95一致・欠落0。verification/source-bytes-af9b739d-current.json/.tsvが今回のbyte proof。元のreviewed-source-4d52be0a-current.tsvは95files中2差異、verification/workspace-ci-source-match.tsvは127files中9差異で、旧snapshot一致を現在の根拠へ転用しない。既存95claims/schemaを保持し、製品・テスト・CI・U1成果物の変更はない。

検証済み：署名済みaf9bのCI37713953347（7jobs）/native37713953340（4jobs）成功をstep30-native-ci.logで再確認。ci-jobs-37713953347.json/ci-jobs-37713953340.jsonとci-native-bookworm.log/ci-coverage.logは同SHAのU1保存証拠をU2 verificationへコピーした。コピーは新テスト実行ではない。全162application filesの比較はU1で承認された厳密hash文書例外を含む共有検査で、U2 claims全一致は別に独立確認した。

検証済み：ci-native-bookworm.log:862はU2差分38pass/0fail、2003はホスト並行10pass/0fail。source名と保存rawログ対応はstep30-test-correspondence.json：CPU14/decoder9/MMU9/types1/kernel1のU2内部tests全存在・実行済み。CPU全39のsummaryには後続U4等を含み、U2専用件数として扱わない。u2_segment_内部5、u2_segment_atomic_forms差分1、u2_atomic_gs_差分2のexact名を保存ログで確認し、新filter実行とは数えない。REP両model内部tests（u2_repeat_data_fault_applies_explicit_flags_model／u2_repeat_fetch_fault_applies_explicit_flags_model_and_clears_context）もok。CMPS/SCAS start/partial/budget native6casesはAuthenticAMD観測で38suite内、Intelは先行証拠。mask0xcd5、外側30秒kill/reapを維持する。

検証済み：ci-coverage.log:2340は全体7155行/未実行524=92.68%、2802はU1対象packages6905/1171=83.04%。両80%gate成功、分母は後続共有実装を含みU2専用coverageではない。3OS/lint/依存の成功は同runのjobsで確認。4d52の92.57%/82.71%、旧197/94.00%、旧fuzz各601秒は履歴。

ドキュメント根拠/検証済み：C1 ArithmeticFault→Kernel SIGFPE、C3 forms、C4 typed atomicと全アクセス共通同期、C5 REP continuation/FS-GS最終addressの既存source対応を保持。inventory/rebuild receiptは固定取得・builder履歴。再集計aube4658=整数3136+system190+U31332、probe865=整数696+system3+U3166、native_case tokens欠落0（step30-inventory-correspondence.json）。全static encoding実行やcomplete runtime inventoryとは主張しない。15/15 family対応、U5 clone/futex・U10 program全体・U11 wasm・U14 JITの境界を維持する。

対応表：既存44行のstatus/targetを保持し、共有requirements fallback48IDsを担当分類で追加した（92IDs/92対応）。FR5.4はU5 native thread割当とU11 wasm Worker割当を明記。NFR4/NFR6既存OKはU2の詳細責任への対応であり全製品のmount/network/JIT合格ではない。検査の実結果はverification/step31-sensors.json。

履歴（Step30〜32時点）：当時は現行sourceの各600秒ASan証拠がなく、重いfuzz/全suite再実行なしで4GAPを保持した。現在はStep33〜35でCPU636751/MMU910789各601秒を実行済みだが両LSan終了fatal/exit1のためNFR2/NFR3/NFR2.2/NFR3.4の4GAPを維持する。新fork診断CI結果はまだ未検証。単独Safari spikeからU2 production wasm・共有std heap・入れ子Worker・任意入力安全性を推定しない。nightly-2026-10-01、各600秒、80%、30秒、比較mask、custom順序を維持する。

以下のStep1〜29・4d52観測はすべて当時の履歴。本文中の「現在」「今回」「差異0」はその時点に限り、現行af9bへの一致・今回新実行を意味しない。


## 履歴：Step27〜29（4d52時点）の新内容確認後保存

u2-redo-brief全文と新Summary Confirmation/UNIT_STARTED後にread-only git show4d52/SHA256でmanifest95claims一致、snapshot95/CI対象127pathsの差異0を再確認した。保存JSON7+4jobs全success、trace44target欠落0、NFR2/NFR3/NFR2.2/NFR3.4 GAPを確認。新4produces plan/instructions/summary/traceabilityとmanifestを全保存し、現在CIの差分38/並行10と品質証拠を保持した。旧fuzzを現在600秒ASanへ転用せずwasm未検証も維持。製品変更・新tests・SCM操作なし。親diaryを依頼前に確定し、以後全書込を停止する。下記Step24〜26は先行attemptの履歴。

## 履歴：Step24〜26（4d52時点）の確認結果

tool-produced verification/u2-rereview-brief.txtを全文読取し、記録済みPlan Approval/Looks correct/UNIT_STARTED後に照合した。Python hashlib.sha256とread-only git show4d52be0aで95claims一致、欠落0を確認。exec.rs/u2_tests.rsのSHA256は下記snapshotと同じ。manifest SHA256=f63868dd93dda0e9138225540f9b4967915329441dfe1d6eb35d5ab0de12b0a7。manifest/既存snapshot/traceabilityは変更を要さないため保持した。

保存CI JSONのheadSha4d52be0a、7+4jobs全successを再確認。Bookworm raw475/480のREP両model内部test ok、861の差分38pass、1884の並行10passを確認した。44trace targets欠落0、NFR2/NFR3/NFR2.2/NFR3.4はGAP。旧600秒ASan/未実行wasmを現在合格へ流用しない。現在bytesが不変の製品へ新テスト/再取得/重いDocker検証を追加していない。新製品不具合なし、U1/U4凍結成果物・SCM書込みなし。

日記は親construction/code-generation/memory.mdへ出力専用heading anchored追記をレビュー依頼前に完了する。rootへの引渡し後は正式レビュー結果まで全書込みとSCM snapshot操作を停止する。前回不整合の原因は未確定。下記Step20〜23の実行説明は先行attemptの履歴として保持する。80%/30秒/nightly2026-10-01/各600秒/比較mask/custom順序は変更しない。

## 履歴：Step20〜23の実行境界

今回の対象は承認済みStep20〜23。tool-produced `verification/u2-approved-brief.txt` を読取、Testing Contract hash `99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616` を維持した。conductorが現在attemptのPlan ApprovalとSummary Confirmation、UNIT_STARTEDを記録した後に照合した。新しい製品変更・テスト実行・再build・fuzz・SCM書込・lifecycle操作は行っていない。Steps1〜19のチェックは履歴。

## 履歴：4d52時点のsource byte照合

検証済み：Python hashlib.sha256でworking filesを読み、read-only `git show 4d52be0a6f3b11d6c11a62f96196985c9c280fdc:<path>` のraw bytesと比較した。manifest95claimsは95/95 MATCH、欠落0。`reviewed-source-4d52be0a-current.tsv` に各path/SHA256を保存。crates/tests/fuzz/scripts/workflowsとCargo.toml/Cargo.lock/rust-toolchain.toml/deny.tomlを `git ls-tree -r --name-only` で列挙し127/127 MATCHを確認、`verification/workspace-ci-source-match.tsv` に保存した。SCMの変更はない。

- exec.rs SHA256: `e660a4c0cc569a679e3c6dcf3511e782415196bc59786bc29eb16fc77ef1015e`
- u2_tests.rs SHA256: `dc80918a12a451e743f9bb0eabd8120fb4849019db698faa6a70494607d67827`

旧exec.rsのe5f052…との一致主張は現在には適用しない。旧95claimsとschemaを保持し、既にclaimされたCPU lib/exec/state/u2_tests・diff_u2/observe.cをREPmodelの現在確認対象として扱う。U1のSSE追加、Host/VFS cleanupはU2の新規実装成果とは数えない。

## 履歴：4d52のnative/3OS品質証拠

検証済み：miseインストール実体のgh2.102.0で次のread-only操作を実行しexit0。JSONのheadShaは双方4d52be0a…、status completed、conclusion success。

```bash
gh run view 37695518838 --repo Marukome0743/paludarium --json headSha,status,conclusion,jobs
gh run view 37695518927 --repo Marukome0743/paludarium --json headSha,status,conclusion,jobs
```

実出力は `verification/ci-37695518838.json` と `verification/native-37695518927.json`。7jobs（3OS単体、差分、lint、dependencies、coverage）と4jobs（workspace、bookworm、期待観測2runner）が全success。CI実行コマンドはコピーしたraw jobログに保持する。

| 証拠 | 確認結果 |
| --- | --- |
| verification/final-bookworm-4d52be0a.log | AuthenticAMD、CPU全39、U2diff38、parallel10、U1diff16 passed |
| verification/final-ubuntu-4d52be0a.log | 実機Linux whole-workspace成功 |
| verification/final-mac-4d52be0a.log | macOS existing suite成功 |
| verification/final-windows-4d52be0a.log | Windows existing suite成功 |
| verification/final-coverage-4d52be0a.log:2187 | whole-workspace lines7030/missed522、92.57% |
| 同ログ:2617 | U1対象packages lines6780/missed1172、82.71% |

両行coverageは下限80%で実行。件数はchildの重複summaryを加算しない。静的sourceのu2_ test関数名とBookwormの `test ... ok` を照合：CPU14/decoder9/MMU9/types1/kernel1が全存在・実行済み。これは新しいfilter実行ではない。Runtimeには不存在のu2_filterを要求せず既存suite証拠を使う。

## REP modelと設計の対応

ドキュメント根拠：U2 functional-spec/rules BR1.6・NFR1.2の開始flags復元はIntel SDMを根拠とする。現在の既定 `RepFaultFlags::RestoreInitial` がこの契約を維持する。追加 `PreserveCompleted` はAMD EPYCのnative観測を反映する明示modelであり、全AMD製品を保証する一般仕様と主張しない。CPUからHost/Kernelを呼ばず、CPUIDによるmodel選択はnative diff fixture内だけにある。

検証済み：`u2_tests::u2_repeat_data_fault_applies_explicit_flags_model` はCMPS/SCAS、完了0/17/4096と内部budget再開について両policyを確認。`u2_tests::u2_repeat_fetch_fault_applies_explicit_flags_model_and_clears_context` はfetchfaultと継続context破棄を両policyで確認。Bookwormログで両test ok。

native6casesは `u2_cmps_fault_start/partial/budget`、`u2_scas_fault_start/partial/budget`。現在ログ:628/638/648/789/799/809にAuthenticAMDが報告され、38suite全件通過。mask0xcd5を維持。observerのvendor欠落/未知値はassertionで失敗し、flags出力からpolicyを逆算しない。

Intel実機成功は `verification/native-final-bookworm-e0818962.log`（job112975354218）の履歴：GenuineIntel、両内部test ok、native6casesと38suite通過。read-only git showでe0818962と現在のCPU lib/exec/state/u2_tests、decoder lib、diff_u2.rs、observe.cの7filesがbytes一致した。現在runをIntelで再実行したとは表現しない。Docker VMM/QEMUのENTER/ALU差を実機native結果と混ぜない。

## 固定inventory・契約・traceability

全U2 functional-design/NFR requirements、shared components/contracts/requirements/units/story-mapを読取。U2 nfr-design/infrastructure-design directoryは存在せず、内容を捏造しない。story-mapはストーリー工程を飛ばしFRを割当している。C1 ArithmeticFault consumer、C3 decoder forms、C4共通同期typed atomic、C5 CPU/continuationのsourceを照合し、U5/U10/U11/U14の境界を保持する。

`docs/u2/inventory/rebuild/build-receipt.json` を読み、固定aube revision bd94e42f54d3b5e3dd102716b7197f316cb5f4ed、lock8960ea…、binaryff54cffe…、probe binary15e90407…と原artifact一致を確認。隔離builderとdirtysource receiptは履歴。form-classification再集計aube4658=3136整数+190system+1332U3、probe865=696整数+3system+166U3。全native_case tokensの存在と幅/prefix/implicit operand対応は固定inventoryの対応表であり、全静的bytesのnative実行を意味しない。complete_runtime_inventory:falseと原artifact歴史上のbuilder未確定を保持する。

traceability44coverageの実file targets欠落0、詳細NFR16件欠落0。NFR2.2とfuzzを含むNFR2/NFR3/NFR3.4をGAPとし、旧notes/metricsは historical-traceability.json に保存した。旧summary/evidence-currentも historical-* に保存、evidence.md/旧reviewは保持。

## 残る品質GAPと確認方法

履歴（Step30〜32時点）：当時は現在sourceのCPU/MMU各600秒ASan未実行だった。現在はStep33〜35でCPU636751/MMU910789各601秒実行済み、両LSan終了fatal/exit1。verification/step35-current-asan-proof.jsonとcpu_u2.log/mmu_u2.logが現在の失敗証拠で、4GAPを維持する。旧r01成功1276258/1706799 runsはREP変更前sourceの履歴で合格へ転用しない。新fork診断CI結果はまだ未検証。LSan終了検査を含む各600秒成功証拠が必要。CPU max_len4096、MMU4608、timeout30、rss_limit_mb2048、固定nightly/ASanを維持し、linux-dev.sh同期との並行を禁止する。

未検証：wasm Worker/Safari、guest clone/futex、probe/aube emulator全program、全任意入力/全vendor、JIT。「追加Docker/QEMU検証を実行しなかった」はStep30〜32の履歴。Step33〜35では現在sourceのCPU/MMU各601秒を実行しLSan終了失敗を記録した。新fork診断CI結果はまだ未検証。30秒watchdog/nightly-2026-10-01/600秒ASan/80%/mask/custom orderingを変更せず、性能測定・別projectbackground停止も行っていない。

検証済み：Step31 traceabilityはpass:false/findings4で実GAP NFR2/NFR2.2/NFR3/NFR3.4のみ。missing IDs/invalid entries/invalid targets/orphansは0。required-sectionsはpass:true/H2=7。exit0をPASSへ読み替えず、未実施ASanを保留としてBuild and Testへ渡す。全produces・manifest・証拠の書込を終了し、独立レビュー前に固定する。
