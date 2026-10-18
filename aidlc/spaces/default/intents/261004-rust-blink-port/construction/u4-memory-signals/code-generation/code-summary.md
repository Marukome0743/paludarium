# U4 メモリ・時刻・シグナルの現在source確認

## 今回Steps34〜36：現行ソースのASan/LSan実測

検証済み：[Linux CI38047281434](https://github.com/Marukome0743/paludarium/actions/runs/38047281434)、署名Verifiedの診断head f2fa1be53c4ebbaf50d62eae7de536d122029082でsyscall_args 1,263,808 runs / 601秒、mmu_ops 2,801,507 runs / 601秒。各exit0・source-compare0、最小C ASan終了診断各2回exit0、crash0。ASan/LSanの異常・panicをrawで観測しなかった。`verification/verify-step36-artifacts.py` exit0、結果は`verification/step36-artifacts-proof.json`。

検証済み：現行製品基準7eb1819fと診断checkoutの製品・fuzz・Cargo.lock・fuzz/Cargo.lock・suppressionなど291pathsの全hash一致、両CI source-before/afterも同集合・同bytes。診断headは新workflow1fileだけが基準と異なる。生成済みpackages/paludarium-wasm/paludarium.wasmはhostと基準で異なるためnative sanitizer source集合から明示的に除外した（生成binaryであり2targetの入力ではない）。U4の107担当claimsも現行基準との一致を保持。根拠はstep34-source-baseline.json、step34-complete-inputs-commit.json、step35-run.json、step35-artifacts.jsonとstep35-ci-artifacts/各targetの生ログ・環境・binaryhash/symbol・corpus archive。

nightly-2026-10-10、cargo-fuzz0.13.2、checkoutv7.0.1・upload-artifactv7.0.2を公式latest情報で確認しSHA/具体版で固定した。製品rust-toolchain.tomlは変更せず診断だけ最新nightlyを明示指定。Bookworm補助C compiler gcc12.2/llvm14は同distributionの最新配布packageであり上流最新を意味しない。ASAN_OPTIONS=detect_leaks=1、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、既存iced-x86 suppression、seed1、timeout30、rss2048、既定max_lenを維持。__asan_initと__lsan_do_recoverable_leak_check/内部DoLeakCheck symbolsを確認した。

初回38046999215は診断へ追加した非対応--lockedでfuzz開始前失敗し、生ログ/全artifactをstep35-initial-failure*へ保持。38047125821は601秒完走したがfuzz/Cargo.lock before/after収録不足のため今回PASS根拠に使わずstep35-incomplete-lock-artifactsへ保持。途中停止要求は権限不足HTTP403で拒否され、結果を削除/成功へ改変していない。完全収録版38047281434だけを今回合格とした。製品変更・PR・mergeなし、既存dirty workspaceを保持して/private/tmp/paludarium-u4-current-sanitizersを使用。

今回のU4二target各600秒ASan/LSan未検証を、この有限実測範囲だけ解消した。任意入力・全UB・他target・後続Unit全統合・並行セッションID競合の完全解消は未検証。80%下限・strict guard・30秒watchdog・custom native-first/internal-test-afterを維持し、coverage等の既存現行CIはrootの承認済みcanonical検査で照合する。正式sensor結果はstep36-*-sensor.json。新しい独立レビュー・checkpoint・人の承認・次Unit遷移はrootのStep37へ渡す。

## 以下Steps31〜33以前は各attempt当時の履歴

下記の未検証・現在・今回表記は当時の状態であり、今回の判定は上記Steps34〜36を参照する。

## 今回Steps31〜32：7eb1819fへの現行照合

検証済み：内容確認2f7ed06ad1ee6e2af4337f10a2541126dba95446ea8b70b478f3e39e965c9e22後、read-only `jj --ignore-working-copy file show -r 7eb1819f52acede33e83775374dd4ee93edf643b <path>` とSHA256でmanifest107担当ファイルを照合し、107一致・不一致0・欠落0。verification/step31-current-source-proof.jsonに全path/hashを保存した。今回製品変更・新テスト実行はない。共有要件とC1/C2/C4/C5/C8/C10の所有・一方向依存を保持する。

検証済み：旧Step30の178da99e実機ASan診断は保存された有限成功であり、現在の新実行ではない。154source/config baselineと現在は113一致・41変更（lock、syscall_args、Kernel/Host/MMU等）。verification/step31-historical-fuzz-compatibility.jsonに具体差異を保存。未検証：現行全sourceでのsyscall_args/mmu_ops各600秒ASan/LSan。旧1296522/3682821runs各601秒を現在合格へ転用しない。traceabilityの既存statusと後続Unit Deferredを保持し、OKは保存済み有限証拠の範囲であり、全入力や現行全sourceのfuzz完了を意味しない。

旧CI/coverage/差分44/内部76は各revision当時の履歴。現在7eb1819fのCIと80%gateの照合はrootの承認済み最終確認で実施する（この引渡し時点では未実行）。80%下限・30秒watchdog・各600秒fuzz・比較mask・custom native-first/internal-test-after・strict guardを維持する。後続U11の作業は変更しない。正式sensor実結果はverification/step32-*-sensor.jsonへ保存。独立レビュー、checkpoint、人の完了承認、次Unit遷移はStep33としてrootへ渡し、並行ID競合の完全解消は未検証。

## 以下はSteps1〜30当時の履歴

下記の「現行」「現在」「今回」は各attempt当時を指す。今回の現在値は上記Steps31〜32を参照する。

## 現行 Steps25〜30：署名済み178da99eの照合

検証済み：新 Plan Approval と Summary Confirmation a266ca8949de1a2afa316977f37656c96f0d10b49c5d71f14a59c6852ec482ff 後、製品変更なしで107/107 manifest claimsの現在SHA256が署名済み178da99e88d1aea242c5141207887767a69fa670に一致した。verification/step25-source-claims-proof.json に全path/hashを保存。canonical検査 exit0 は186 tracked pathsと承認済み docs/reports/wasm-threads.md の固定文書差分を確認（verification/step26-canonical.json）。

検証済み：最新CI37745425190の保存rawを verification/step25-main-ci-178da99e.log に複写して再確認した。U4差分44件成功（4008行）、Ubuntu内部6層76件（CPU5/Host8/Kernel37/MMU10/Runtime11/Types5）の個別名・行は step25-ci-observations.json。Hostの分割されたokも732〜734行で確認。新テスト実行ではない。3OS既存suite・lint・依存とcoverageは同じ署名済みheadの8jobs成功。全体92.68%（7591行）、U1対象83.04%（8053行）、U9対象82.55%（8423行）、全体と対象の80%下限を維持。

診断CIは製品CIと別枠。178da99eを親に新workflowのみ追加した署名済み02e24e835aa50c41943cf59cfff8730e65f2b028（Verified=true）のrun37755026547でsyscall_args/mmu_opsが完走した。現行結果は下記Step30を参照する。workflowはisolated workspaceだけ、正本copy step28-workflow.yml、署名/唯一のworkflow差分は step28-commit.json。U2の4-target ASanやproduction wasm14ケースは共有source確認として扱い、U4の全wasm動作・600秒target合格に一般化しない。

80%・30秒watchdog・nightly-2026-10-01・各600秒・custom native-first/internal-test-after順序を保持。main製品、既存CI、U1/U2記録を変更しない。任意入力・全UB・全runtime経路・probe/aube全guest・guest clone/futex（U5）・file-backed mmap統合・U4 wasm/Safari（U11）・JIT（U14）・handler内FS/GS変更の追加native比較は未検証。

## Step30 現行実機ASan/LSan結果

検証済み：[U4診断CI37755026547](https://github.com/Marukome0743/paludarium/actions/runs/37755026547)は署名Verifiedの02e24e835aa50c41943cf59cfff8730e65f2b028で両job success。製品基準178da99eとは新診断workflowだけが異なる。syscall_args 1,296,522 runs / 601秒、mmu_ops 3,682,821 runs / 601秒、各exit0・source-compare0。各jobの最小C ASan終了診断2回もexit0。ASan/LSanの異常・panicをrawに観測せず、既存iced-x86 suppression以外は追加していない。

nightly-2026-10-01・cargo-fuzz0.13.2・seed1・address sanitizer・detect_leaks=1・LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp・timeout30・rss2048・既定max_lenを実行ログで確認。検証commandはstep28-workflow.yml、全job rawは step29-job-{syscall_args,mmu_ops}.log、run/job/artifact metadataはstep29-{run,jobs,artifacts}.json。artifact取得はconnectorを優先し、ZIP参照をhost上へ展開する不足操作だけgh run downloadを使用した。

各targetのstep29-ci-artifacts/u4-asan-<target>/には target.log、settings.txt、environment.log、exit.txt、start.txt/end.txt、minimal-1/2-exit.txt、source-before/after.sha256、binary.sha256・binary-symbols.txt、corpus-before/after.tar がある。__asan_init symbolを確認。step28-source-baseline.jsonの154 tracked source/lock/config/suppression pathsと現在host/両CI before/after全hash一致。未追跡の生成wasmを混入させない。107 manifest claimsも同じ178da99eと全一致。corpus-afterはsyscall_args1733/mmu_ops1345files、両crash0。各raw/archiveのSHA256と開始終了時刻はstep30-artifacts-proof.json。

FR9.3/NFR2/NFR3のU4二targetに関する現在600秒ASan GAPをこの実測範囲でOKへ更新した。夜間scheduled-runが実行されたという意味ではない。全任意入力・全UB・全runtime・guest clone/futex・U4全wasm動作・後続Unitの達成は未検証。U2の4-target/production14ケースと今回U4の2-targetを混同しない。

対応表は初回sensorが48 findings（ASan3 GAP、共有FR45 IDs不足）だった実結果をstep26-traceability-initial.jsonに保存。共有要件とunit-of-workによる45 IDsの追加は集約見出しN/A・後続UnitDeferred（具体担当付き）、FR6.4はprobe項目変更なしでN/A。既存15 IDs/targetsを保持し、60 rowsと現在根拠を整合した。品質下限やsensorを弱めず、最後の限定sensor結果を別途保存する。

## 以下はSteps1〜24当時の履歴

以下の「現在」「今回」「現行」はそのattempt時点を指す。4d52 snapshot/CI/92.57%/旧fuzzは履歴であり、現在178da99eのbyte proofではない。af9bは中間revisionで、最新の根拠は上記178da99eと別枠U4診断CI。旧未検証表記は当時の状態として保存し、現在の判定は上記とStep30最終結果を参照する。

## redo新attempt Steps22〜24

検証済み：u4-redo-brief全文、新Summary Confirmation後に107claims/107snapshotの4d52bytes一致・差異0、15trace target欠落0、CI11jobs成功、内部76全test名ok/差分44passを再確認した。今回の実4produces plan/instructions/本summary/traceabilityとmanifestを全保存し、claims/schemaを保持した。FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証、全品質下限を維持する。製品変更・追加testsなし。親diaryを最後に確定し、引渡し後は全書込とSCM snapshotを停止する。不整合原因は未確定。

## 新attempt Steps19〜21の再確認

検証済み：u4-rereview-brief全文と新承認/内容確認後、read-only git show4d52be0aとSHA256で107claims/107snapshotの一致・欠落0を再確認した。manifest SHA256=842534ed17f52424a920b8f63948c6972b1c810d5424a62a9f05c0ef2fe4a446。strict v1 manifest/snapshot/traceabilityは変更不要で保持した。CI JSON7+4jobs全成功、Bookworm raw1234の差分44pass、current-counts.jsonの内部76全test名が同rawでokと確認した。trace15のtarget欠落0、FR9.3/NFR2/NFR3 GAP保持。新製品変更・新testsなし。

Step1〜18は履歴。今回も旧600秒ASanを現在passへ転用せず、wasm/Safari未検証と品質下限を保持した。親diaryをレビュー前に確定し、引渡し後は全source/成果物書込とjj snapshot操作を停止する。前回reviewterminal拒否の原因は未確定とする。

## 今回の結果

承認済み復旧Step15〜18を実行した。検証済み：U4 manifest107claimsは欠落0、現在bytesが署名済みproduction `4d52be0a6f3b11d6c11a62f96196985c9c280fdc` のCI対象に全一致。製品source・テスト・U1/U2凍結成果物を変更せず、既存実機CI証拠を再利用した。新しいテスト実行として数えない。

[CI37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838) の7jobsと [native37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927) の4jobsは全成功。U4差分44件、内部6層76件（MMU10/Host8/Kernel37/Runtime11/Cpu5/Types5）、3OS既存suite、lint/依存、全体行coverage92.57%を確認。親summaryとchild重複を区別した。80%下限を保持する。

## 実装・契約の現在値

既存anonymous mmap/munmap/mprotect/brk、typed Host clock/cancellable wait、signal action/mask/altstack、Linux x86-64 frame/returnと単一process/thread配送を確認。C1/C4のfault metadata、C2 Host clock/wait、C8 dispatcherとchecked signal codecの責任を保持する。CPUはHost/Kernelへ依存せず、MMU共通同期の中でHost waitを呼ばない。

signal frameはguest memoryへchecked codecで書き、REP continuationはhandlerから切り離して一致するreturn contextで復元する。target別pending/coalesceとThread/Process優先はlive oracleを含む既存native回帰で確認する。file-backed mmap、guest clone/futex、wasm/JIT統合は後続unitの境界として保持する。

計画Sourcesの「Host未実装」「配送しない」、Step1〜14の未作成説明は先行実装前のbaseline。現在値とは区別する。U4の個別functional/NFR/infra設計directoryは不存在で、共有requirements/components/contracts/units/story-mapを根拠にする。ストーリーを捏造しない。

## 更新した成果物

code-summary/evidence-current/traceability/source-manifest、現在snapshot source-hashes-current.json、validation-current.json、reviewed-source-4d52be0a-current.tsvを整合した。manifestはstrict version1 schema、107 owning pathsを保持。今回新application-sourceなし。旧summary/source-hashes/validation/traceabilityはhistorical-*へ保存し、evidence.mdとdocs/u4の先行raw/validationを改変していない。独立レビュー用ログはU4 verificationへコピーした。

## 残る品質GAP

未検証：現在sourceのsyscall_args/mmu_ops各600秒ASan。旧37paths snapshotから15pathsが変わり、syscall_args target自身とKernel/MMU/Host/Runtime/CPUなどの依存sourceが異なる。mmu_ops target単体が同じでも旧完走を現在プログラムへ転用しない。FR9.3/NFR2/NFR3はGAP。旧317件/93.70%とfuzz1136975/1564316各601秒は履歴。

既存nightly-2026-10-01、各600秒ASan、30秒watchdog、flags mask、coverage80%を保持し、Build and Testへ現在sourceでのfuzz確認を渡す。全任意入力、probe/aube emulator全program、wasm/browser、handler内FS/GS変更の追加native比較は未検証。性能測定なし。製品修正を必要とする新しい不具合は今回見つからなかった。
