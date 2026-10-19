# U4 現在sourceと保存済み実機CIの照合

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

## redo新attempt Steps22〜24の保存

u4-redo-brief全文と新Summary Confirmation/UNIT_STARTED後にread-only git show4d52/SHA256で107claims/107snapshot一致・差異0、15trace target欠落0を確認。保存JSONの4d52/7+4jobs success、Bookwormの内部76全test名ok/差分44passを再確認した。今回の4produces plan/instructions/summary/traceabilityとmanifestを保存し、既存現在証拠とFR9.3/NFR2/NFR3 ASan GAPを保持する。旧fuzz/wasm未検証を合格へ読み替えず、新source/tests/重い再検証/SCM操作なし。親diaryを依頼前に終え、以後全書込とjj snapshotを固定する。下記19〜21は履歴。

## 新attempt Steps19〜21の結果

tool-produced verification/u4-rereview-brief.txtを全文読取し、新Plan Approval/Looks correct/UNIT_STARTED後に確認した。Python hashlib.sha256/read-only git show4d52be0aでmanifest107claimsとsnapshot107filesの現在bytes一致、差異/欠落0。manifest SHA256=842534ed17f52424a920b8f63948c6972b1c810d5424a62a9f05c0ef2fe4a446。既存manifest/snapshot/traceabilityは正確なため変更しない。

保存CI JSONはheadSha4d52be0a、7+4jobs全success。Bookworm raw1234は差分44pass。current-counts.jsonのCpu5/Host8/Kernel37/MMU10/Runtime11/Types5=76件の全test名に同rawのokが存在する。trace15target欠落0、FR9.3/NFR2/NFR3の現在ASan GAPを保持した。現在sourceの各600秒ASan/wasm/Safari未検証を旧成功で代用しない。製品不具合なし、新tests/重い検証/製品/U1/U2変更/SCM操作なし。80%/30秒/nightly2026-10-01/各600秒/masks/custom順序を保持する。

親diaryをレビュー依頼前に出力専用追記し、root引渡し後は正式結果までsource/成果物とSCM snapshotを固定する。前回reviewterminal失敗原因は未確定。下記Steps15〜18の実行説明は先行attemptの履歴として保持する。

## 承認と作業範囲

tool-produced `verification/u4-approved-brief.txt` を全文読取した。Testing Contract hash99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616のcustom順序と品質下限を維持。conductorの現在Plan Approval/Summary Confirmation/UNIT_STARTED後、Step15〜18だけを実行した。製品source、テスト、U1/U2記録、frameworkstate、SCM、review/lifecycleを書き換えていない。

共有requirements FR2.2/FR2.9・NFR1〜9、C1/C2/C4/C8の提供側所有とconsumer一括更新、components/units/story-mapは保持済みの入力。U4 functional-design/nfr-requirements/nfr-design/infrastructure-designはすべて不存在。計画の未実装Host/配送しないというSourcesは旧baselineであり、現在は時刻・待機・signal配送を実装済み。

## source bytesとCIの対応

検証済み：Python hashlib.sha256とread-only `git show 4d52be0a6f3b11d6c11a62f96196985c9c280fdc:<path>` でmanifest107pathsを比較し107 MATCH/0差異/0欠落。各SHA256と照合結果は reviewed-source-4d52be0a-current.tsv、現在snapshotは source-hashes-current.json。CI JSON headShaも同revisionで、conclusion success。

strict source-manifestはversion1/writes、従来107claimsを保持。共有CPU u2_tests/diff_u2は先行C1/C4変更のconsumer修正として既存claimを保持し、今回の新規U4実装とはしない。tests/guests/u4/build.shはU1復旧でLF修復済みのbytesを確認した。

旧source-hashes-current.jsonの37pathsは historical-source-hashes-current.jsonへ保存。15paths相違を validation-current.json に列挙した。旧snapshotを現在不変と称さない。

## native差分・内部6層の非ゼロ結果

検証済み：verification/final-bookworm-4d52be0a.logは実機AuthenticAMDの全workspace success、diff_u4 44passed。構成はmemory10/time8/signal23/live3。差分期待は実行ごとnativeで作り、固定goldensを使わない。

CargoのRunning unittests sectionからpackageを識別し、`test ...u4_tests::... ok` の一意名を集計した。verification/current-counts.jsonに全名を保存：MMU10、Host8、Kernel37、Runtime11、Cpu5、Types5、計76。Host/Typesは関数名のu4_接頭辞ではなくu4_tests moduleでfilterされるので、関数名だけの0件をPASSとして扱っていない。すべて現在sourceのtest名と一致した。新しいscoped commandを実行したとは記録しない。

実行コマンドはrawに保持。現在不足がなく新テストを必要としなかったため、承認済み限定commands/重いDocker QEMU workspaceを追加実行していない。QEMUのtrapno/ENTER/ALU観測差を実機native証拠へ転用しない。

## CI・3OS・品質

独立レビュー用に必要なログをU4 verificationへコピーし、U1/U2成果物を読まずに確認できるようにした。

| 証拠 | 結果 |
| --- | --- |
| verification/ci-37695518838.json | 3OS単体、differential、lint、dependencies、coverageの7jobs success |
| verification/native-37695518927.json | workspace/Bookworm/2expectation jobsの4jobs success |
| verification/final-bookworm-4d52be0a.log | U4差分44、内部76の個別test ok |
| verification/final-ubuntu-4d52be0a.log | 実機Linux whole-workspace success |
| verification/final-mac-4d52be0a.log | macOS existing suite success |
| verification/final-windows-4d52be0a.log | Windows existing suite success |
| verification/final-coverage-4d52be0a.log:2187 | 全体7030行/未実行522、92.57% |
| 同ログ:2617 | U1対象packages6780行/未実行1172、82.71% |

このCIは新しいU4-only test実行ではない。両coverage80%gateを保持し、unit subsetで全体gateを代替しない。nightly固定版と依存lock/Actions pinを維持。support/u4.rsは全ケース外側30秒watchdogでkill/reapする。sourceのC2 clock/wait、C4共通Mutex、C8明示dispatch、C1fault metadataを読取し、CPU crate dependenciesはtypes/decoder/mmuだけでHost/Kernelへの逆依存なしを確認した。

## ABI/inventoryと履歴

docs/u4/syscall-matrix.md、signal-abi.md、validation.mdを読取。固定probe/aube receiptsは履歴として維持。static syscall位置109/258は到達経路・syscall番号数ではない。有限native traceにclock/sleepがないことを対応不要の証拠にせず、専用time fixture8件のnative結果を用いる。siginfo/ucontext offset、mask0xcd5、pending target順、REP budget returnの各内部/native回帰が現在CIで通る。

docs/u4/validation.mdの317passed/93.70%と旧ASan完走は先行sourceの記録であり、このreconciliationの現在結果ではない。旧summary/validation/traceability/hashをhistorical-*へ保存、evidence.mdとRed/Green失敗履歴は保持した。

## 未検証・handoff

現在sourceのsyscall_args/mmu_ops各600秒ASanは未検証。syscall_args.rs自身が旧hashと異なり、mmu_ops.rsは同じでも共有MMU/CPU/Kernel/Host/Runtime依存が異なる。旧1136975/1564316runs各601秒を転用しない。FR9.3/NFR2/NFR3をtraceability GAPにした。夜間targetと各600秒ASan/timeout30を維持し、Build and Testで現在sourceに結び付ける。その他15割当FR/NFRは既存implementation/test/config targetの欠落0を確認した。

未検証：任意入力・全runtime経路・probe/aube emulator全program/U10、guest clone/futex/U5、file-backed mmap関連統合、wasm/Safari/U11、JIT/U14、handler内FS/GS変更の追加native比較。これらへ現在CIを一般化しない。新製品defectは今回見つからず、追加のproduction修正を行わない。
