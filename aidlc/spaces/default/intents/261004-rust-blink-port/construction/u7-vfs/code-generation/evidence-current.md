# U7 現在ソースの証拠照合：Steps28–32

## 現行Steps40〜43：R-04修正と実測（2026-10-10）

検証済み：修正前CI38052956638/head aa332cf7359c95051598ef2b367ae3e44b5a37aaでLinux nativeの6境界を先に取得し、負3ケースのEIO差分Red（test exit101）を保存した。Host/VFS/wasmのmtimeをi128 nanosecondsへ揃え、従来u64正値範囲を保持した。Kernelはfloor秒・非負nanosecondsとchecked EOVERFLOWへ変換する。wasm snapshotはsentinel/version2のsigned128へ更新し、JS decoderは旧u64形式も読み取り、切断・未知版・過大countを拒否する。独立clock syscallは変更していない。

検証済み：署名Verified head5fa16398eae31ec178bfd93d3029b24ee31ac5e5、CI38053646678は6/6 jobs成功。全294入力・両lockは各jobのbefore/after/current一致。担当manifest43claims/96filesも署名headと一致。fresh native stat/fstatの-1秒/-0.5秒/-1ns/0/1ns/1.5秒は全6 raw値一致、diff_u7親64成功。Host/VFS/Kernel/wasm境界324 Rust testsと2 doc tests、Node32 tests、wasm32 check・fmt・clippy全exit0。旧wasm配布binaryを新runtime実測の根拠には使わない。

検証済み：同じU7 scope/除外/80% gateで7067/7939=89.01624889784607%。Windowsは実symlink権限true、1000反復/43交換、outside不変、strict cleanup、whole-child572ms/exit0。ASan/LSanはvfs_paths3675837、syscall_args1455696、mmu_ops3003322 runs、各601秒/exit0。seed1・timeout30・rss2048・既定max_len・既存suppression・detect_leaks1を維持し、最小C各2回exit0、binaryhash/symbols/corpusと全rawを保存した。

検証済み：coverage補足CI38053960030/head79baa5d6f7c0ec8afa7e2d3e2cf85ffcfcca648cは同294入力・同scope・同coverageで成功。19 hash0警告は重複3関数で、測定対象行の欠落0。6境界のnative/emulated rawは同runログ467〜478行に保存。証拠はverification/step43-fixed-proof.json、step43-coverage-mapping-proof.json、step43-raw/、step44-source-claims-proof.json。

未検証：任意入力・全UB・全OS・全ブラウザruntime・probe/aube/JIT・並行セッションID競合の完全解消。新canonical verify-current-u7-r04.pyは具体化済みで、親によるコマンド承認前は実行しない。正式sensor・独立レビュー・完了承認は別途記録する。strict guard、80%、30秒、各600秒を維持する。

## 以下は修正前の履歴

以下の「現行」「未修正」「U11対応」は当時の記録であり、今回の修正後の判定は上記Steps40〜43を優先する。旧成功は修正後の証拠として再利用しない。


## 現行Steps36〜38（2026-10-10）：不足4項目の再実行

検証済み：CI38050439711、署名Verified head459591c798152d3098779f3050acb734f382ac55、全3job成功。Step36全291入力・両lock、現行7eb1819fの88担当ファイルを保持。診断workflow以外の製品/テスト/lock変更なし。tool最新版と公式取得URLはverification/step36-tool-versions.json。

- Windows: `cargo +nightly-2026-10-10 test --locked -p paludarium-host --lib native_fs::u7_tests::u7_native_windows_symlink_rename_race -- --exact --test-threads=1 --nocapture`。1000反復/49交換/442共有競合、実symlink=true、outside/cleanup=true、child817ms/exit0。291 before/after/current一致、登録0/skipなし。rawはstep37-raw/windows/、proofはstep37-windows-coverage-proof.json。
- Linux: unit-test-instructionsの承認済みexact scope/除外/80%コマンドをnightly2026-10-10で実行。fresh native diff_u7親63成功/0失敗、同run JSON lines6988/7864=88.86063072227874%、floor/report/291比較exit0。rawはstep37-raw/coverage/。
- ASan/LSan: `cargo +nightly-2026-10-10 fuzz run --fuzz-dir fuzz --sanitizer address vfs_paths -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048`。3422797 runs/601秒、max_len既定4096、ASAN_OPTIONS=detect_leaks=1、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、最小C2回/本体exit0、291 before/after/current一致。binaryc700856fdb85dda6d28c6a0dab269f3756f8cad3ab7348c06db97a61f3bf920dとASan/LSan symbols/corpus/crashをstep37-raw/asan/保存。step37-fuzz-proof.jsonに全rawhash。

検証済み：coverage警告19件はhash0の重複TerminalInfo::new8/TerminalAttributes::default3/ExitStatus::command_exit_code8件。Host2関数はJSON有効profilecount9/11で全98–109/129–143範囲集計、Typesは既存regex除外のため対象行欠落なし。署名Verified head7928dcf0、CI38051169927のclean同scope再測定はfloor/JSON/dump全exit0、元とtotals一致、diff63/291一致。step37-coverage-mapping-proof.jsonとstep37-raw/coverage-mapping/を参照。診断途中の-debug非対応38050705083と-dump JSON混在38050937551は各rawを保持、製品失敗とは分類しない。

未検証：1970年以前mtime既知EIOは承認済みU11修正へ残し、負時刻回帰未実行。全OS/任意入力/全UB/wasm/probe/aube/JIT/ID競合完全解消への一般化なし。旧実測と今回は区別し、strict guard・80%/30秒/600秒を維持する。以下は再実行前の履歴。

## 現行Steps33〜34（2026-10-10）

検証済み：step33-source-proof.jsonに35claims/88filesの署名7eb1819f52acede33e83775374dd4ee93edf643b raw-byte一致88/88。保存成果物hash59/59一致はstep33-saved-evidence-integrity.json。製品・テスト・設定変更なし。

検証済み：step33-evidence-compatibility.jsonで旧Linux ASan・coverage・Windows各listing154pathsの113一致/41相違、before/after一致を確認。HostFS/VFSmtime/Kernel/lockを含むため旧Windowsfixture、Linux diff63、U7 coverage4317/4772=90.4652%、vfs_paths3132329/601秒は歴史的成功のみ。現行への流用不可。

検証済み：新U4 syscall_args CI38047281434/f2fa1be53c4ebbaf50d62eae7de536d122029082の291inputs（両lock含む）before/after/current291一致。1263808回/601秒/exit0は同target有限ASan/LSanの統合証拠として再利用。vfs_paths・U7coverage・Windowsfixtureの代わりにはしない。

ドキュメント根拠：native_fs.rs:66–73/349–358のstat/cap_statはpre1970 modifiedをduration_sinceの失敗でEIOへ変換し、mtime_nsはu64。未修正で承認済みU11に残る。負時刻実行テストは未検証。GAP7件、Deferred/N/A割当保持。正式sensorはstep34-sensors.jsonに保存する。

未検証の次手：unit-test-instructions.mdのLinux diff_u7／U7限定llvm-cov80%／vfs_paths600秒／Windows exactfixtureを現行固定sourceで実行し、全依存・lock・suppression・設定・生ログ・exitを照合する。既存strict/80%/30秒/600秒/custom順序を変更しない。

## 以下はSteps28〜32当時の履歴

以下の現在source一致やPASSは当時のsourceを指し、現行への適用範囲は上記を優先する。

## 実Windows一時fixture回帰

検証済み：[Windows CI37765054790](https://github.com/Marukome0743/paludarium/actions/runs/37765054790)、署名Verified head8cba60d9a3d33da53c0040732f90b737b10d0476。実symlink権限=true、victim1000反復・完全交換55回・共有違反32の有限retry473回、outside sentinel bytes/一覧不変、strictcleanup=true、子exit0、親whole-child881ms（30秒上限）、exact test1 passed/0failed/0ignored。Windows Server/固定nightly等環境・binary hash・build/test exit0・rawはverification/step30-lf-ci-artifacts/u7-windows-fixture、connector jobrawはstep30-lf-windows-job.log。独立proofはstep31-windows-proof.json（SHA877c0cfda5a71b211e8389950c9fc0f9bc162941968a007e5f2212b3e7f591ff）。test binary SHA8adc0b46d152aefe3de75bc3e08e19e24d03f679952bd1b052d4caa658153e41。

検証済み：CI before/after/currenthost154paths厳密hash一致、CRLF正規化による代用なし。baseline178から主source差はNativeFsのWindows-only cfg(test)追加1fileだけ。新blockとseparator空行を除くと旧bytes完全復元、製品・Linux実行codeは不変。final NativeFs SHA1888c7aeccc4c10fbb6ba75bf3a57045a5ad7e44f0ea8d3e816fe893b99a9fc1、baseline c88d9d93f55e800f77418e6c32333cfeeced3a0a19fbbcf49a70a3c039751342。patch/proofはstep31-windows-test-only.patch、step31-test-only-proof.json。35claims/88filesは現在host/署名診断head全件一致（step31-source-claims-proof.json）。manifestの既存NativeFs claimがtest-only差を含む。診断workflowはisolatedのみでmain CIを変更していない。

## 失敗履歴とLinux証拠再利用

検証済み：初回run37764175990はsymlink権限/build成功後、fixture交換のWindows sharing violation32でchild101・FAIL。raw/artifactとstep31-initial-failure-proof.jsonを保持し、隔離assert到達前の失敗をPASSに変更しない。親指示に従い32だけを25秒内retryし、他errnoは即fail、30秒whole-child/1000反復/交換>0/outside/cleanup条件を維持した。中間run37764657443は44交換/495競合/844msで成功したが130filesのcheckout CRLF変換があったためstrict currentbytes証拠へ採用しない。最終runはcheckout stepだけの一時GIT_CONFIG envでLFを保持し、OS/global設定を変更せず厳密154hash一致を取得した。中間rawも保持。

検証済み：Linux vfs_paths3132329/601秒、U7 coverage4317/4772=90.4652%/80%gate exit0、native diff_u7親63、U4 syscall_args1296522/601秒は保存証拠を再利用。154pathsの153がbaseline178と同一、残るNativeFsはWindows-only test追加でLinux/production bytesを復元確認した（step31-test-only-proof.json）。新Linux実行とは呼ばず、品質閾値・fixednightly・seed1・ASan/LSan・suppression・600秒/30秒を維持する。

## 完了検査と適用境界

検証済み：旧canonicalはNativeFs1file差を正しく拒否したexit1（step31-canonical-result.json）、無断変更せず保持。新レビュー可能な案は共有record/verification/verify-native-ci-with-safari-and-windows-report.py。旧186files/CI3OS/4fuzz/Node・realSafari14/evidencehash検査を維持し、NativeFs exactbaseline/exactfinalhash・Windows cfg testonly差・署名finalCI/raw/154hash・Linux再利用を追加、手動exit0。protected command選択・人の承認は親担当で、手動成功を承認receiptと扱わない。

FR3.2/NFR4は実測したWindows fixture範囲のOKへ更新した。有限回帰であって任意入力・全UB・全OS全挙動・U7 productionwasm・probe/aube・JIT・stat全フィールドの保証ではない。旧R-01/R-02 Resolved、60 IDsの分担分類とNFR6 N/A、完全Testing Contract custom順序と80%/30秒/600秒/nightly-2026-10-01を維持。正式独立review/checkpoint/diaryは親担当。

## 最終文書検査

検証済み：traceability pass=true/findings0/exit0（60 IDs、GAP0）、required-sections pass=true/findings0/exit0。新checker案の手動再確認exit0。sensor command/stdout/exitはverification/step32-validation.json、新checker完了exit0/stdoutはstep32-canonical-final.json（初回保存yieldと区別）。保護command承認・正式完了は親担当。

## 以前の記録

以下のSteps21–27のWindows未実行/GAP/主source変更0と4d52等は当時の履歴である。現在のWindows実測と新test-only1file差は上記に限定する。

# Steps21–27 履歴

検証済み：今回の主workspaceの製品・test・CI bytes変更は0。strict manifest35 claims/88実ファイルは署名済み178da99e88d1aea242c5141207887767a69fa670と現在hostで一致（verification/step21-source-baseline.json）。診断workflowのみisolated jj workspaceへ追加した。署名head eafa5ac6aa9c9cc134dbba923b3e082f8b5e4d05はconnector Verified=true、差分は親02e24e8から新U7 workflow1件のみ（step24-commit.json/step24-workflow.yml）。main workflowは不変。

## 現行Linux実測

検証済み：[U7診断CI37760390069](https://github.com/Marukome0743/paludarium/actions/runs/37760390069)の2 jobs成功。vfs_pathsは3132329 runs/601秒、exit0、ASan/LSan最小C終了2回ともexit0。固定nightly-2026-10-01、cargo-fuzz0.13.2、address、seed1、timeout30、rss2048、default max_len、ASAN_OPTIONS=detect_leaks=1、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.suppを保持した。native x86_64、binary __asan_initを確認、panic/sanitizer fatalの観測0、corpus933 files/crash0。実コマンドはstep24-workflow.yml、環境/raw/exit/symbols/inputsはverification/step25-ci-artifacts/u7-asan-vfs_paths、job rawはstep25-fuzz-job.log、独立照合はstep25-fuzz-proof.json。binary記録SHA775c63043d9e6556c023d2c6786637e58aa6cf036afec3177b4c871453fa46a4、corpus-after.tar SHA39a0de507da83656225d980ce65b5caa3c6a99e2aab9f4f03ad076af6141ad9c。

検証済み：承認済みU7 scope/exclusionをそのまま使うLinux llvm-cov --fail-under-lines80はexit0、report exit0。lines4317/4772=90.46521374685666%、diff_u7親63 passed/0 failed（native期待値を同runで生成して比較）。JSON・raw・実コマンド・環境・exitはverification/step25-ci-artifacts/u7-linux-coverage、job rawはstep25-coverage-job.log、照合はstep25-coverage-proof.json。wholeworkspace/U1 coverageと混同しない。

検証済み：両job source-before/after、178da99e baseline、診断head、現在hostの154関連製品/依存/config paths全hash一致（step24-source-baseline.json、step25-fuzz-proof.json、step25-coverage-proof.json）。U4 syscall_args1296522 runs/601秒/exit0を同154paths一致により再利用した（run37755026547、head02e24e8、step25-syscall-reuse-proof.json）。コピーや再照合を新fuzz実行とは呼ばない。通常178da99e CIの保存ログではu7_登録成功Ubuntu/macOS83・Windows82（step21-ci-observations.json）で、旧81/80と区別する。最新通常CIはdiff_u7を含まないため、今回Linux診断CIで不足を補った。

## 未完了と適用境界

未検証：Windows並行root逃走本体は安全性チェックで停止したとの親報告・明示中止指示に従い実行せず、新Windows code/testも作らなかった（step23-windows-not-executed.json）。旧Windows同名登録テスト成功はUnix専用本体の実行証拠ではない。Step23未完、Step22/24/25はWindowsを含むため全体checkbox未完のまま、Linux部分のみ達成。FR3.2/NFR4 GAPを保持し、Windows本体の隔離を合格としない。

検証済み：FR9.3/NFR2/NFR3の今回U7適用target（VFS paths/syscall args）の600秒検査とU7限定80% floorを達成した。有限の入力・保存corpusで観測した範囲であり、任意入力/全UB/全OSを保証しない。probe/aube全体、U7 production wasm/Safari/JIT、stat全フィールド、外部rename後の既存dirfd identityは未検証。NFR6 N/Aを維持。既存17 IDs/targetを保持し共有fallback43 IDsをUnit分担に基づきDeferred/N/A分類、計60 IDs。Testing Contract custom順序/80%/30秒/nightly/600秒と旧R-01/R-02 Resolvedを保持した。正式review/checkpointは親担当。

## 最終記録検査

検証済み：canonical exactcommand exit0、署名178da99eの186pathsと既知documentary report差を確認。required-sections pass=true/findings0/exit0。traceabilityはexit0だがpass=false/findings2（FR3.2/NFR4のWindows未検証GAP）、missing/orphan/invalid0。実コマンド・stdout・exitはverification/step26-validation.json。検査不合格をPASSとして扱わない。

## 以前の記録

以下の4d52 bytes/CI/coverage・旧snapshot・「現在ASan/U7 coverage未測定」「3 GAP」は当時の履歴だけであり、今回178da99e/診断headの結果へ適用しない。

# Steps1–20 時点の履歴（4d52照合・未測定表記）

検証済み：今回のSteps 15–17は記録の再照合のみ。製品変更・新規テスト実行なし。現在Testing Contract sha256:99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616のcustom順序と80%/600秒/30秒、nightly-2026-10-01を保持する。

## ソースと測定来歴

検証済み：strict version1 manifestの35 claims（docs/u7/inventory/はディレクトリclaim）を88実ファイルへ展開し、live bytesと署名付きCIコミット4d52be0a6f3b11d6c11a62f96196985c9c280fdcを全件照合した。不一致0。現在snapshotはreviewed-source-4d52be0a-current.tsv、詳細はverification/source-reconciliation.json。製品・guest・fuzz・依存lock・nightly・歴史資料を含む既存所有範囲を維持し、今回新しく実装したという意味ではない。

実コマンド：`git show 4d52be0a6f3b11d6c11a62f96196985c9c280fdc:<path>` 各88ファイルexit0、Python hashlib.sha256/live byte比較全件true。読取のみ。旧reviewed-source-ce367e764aae.tsvの88ファイル中5相違：tests/guests/u7/build.sh、Host native_fs.rs/lib.rs、VFS mount.rs、Runtime tests.rs。docs/u7/inventory/source-bytes-final.jsonの34ファイルも同じ5相違。旧snapshotを更新せず保持した。

検証済み：fuzzの両targetとローカル依存の保守的union50ファイルは現行CIと全件一致（verification/fuzz-dependency-source-match.json）。旧source-bytes-finalはそのうち22ファイルだけを記録し、28ファイルの当時bytesは未記録。既知の相違はHost lib.rs/native_fs.rsとVFS mount.rs。両target単体のbytes一致から依存全体の同一性を推定しない。ce367e764aaeは保存snapshotのラベルで、git showではinvalid object name/exit128だったため、SCMコミットとしての比較には使っていない。

## 現行CI

検証済み：[CI 37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838)7 jobsと[native 37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927)4 jobsは同じheadSha4d52、11件すべてsuccess。verification/ci-37695518838.jsonとnative-37695518927.jsonにjob名・URL・コマンド・完了状態を保存した。Linux/macOS/Windows、fmt、clippy -D warnings、cargo deny --locked checkが成功。旧Windows/Linuxコンテナ測定と現在native CIを区別する。

検証済み：native Bookworm実コマンド `cargo test --locked --workspace --no-fail-fast` はraw final-bookworm-4d52be0a.log:340、ジョブsuccess（exit0）。diff_u7は1807行で63 passed/0 failed。Ubuntu nativeでも63件。内訳はMemFs33/Host30（末尾slash各1を含む）。期待結果はCI実行時にnative x86-64 Linuxで生成し、毎ケースのnative/emulatedプログラム結果を比較する。子の1 passedを重複加算しない。差分名はverification/current-counts.jsonの63 unique names。

検証済み：U7内部名前付き親テストはLinux/macOS81件＝CLI6、Host11、Kernel16（FD8/syscall8）、Runtime8、VFS40（MemFs24/mount16）。WindowsはCLI non_utf8のcfg(unix)除外により80件＝CLI5と他層同数。raw各OSログのテスト名/行はcurrent-counts.json。CLI command integrationは全6成功、そのうちU7専用はu7_cli_root_mount_keeps_private_programとu7_cli_mount_missing_root_is_emulator_errorの2件（Bookworm430/433、全体結果437）。内部CLI6や全command6をU7専用2に二重加算しない。macOS/Windowsのdiff_u7はcfgにより実行されず、Linux差分を他OSのnative意味論証拠と扱わない。

検証済み：並行root逃走回帰u7_native_symlink_rename_race本体の実行証拠はLinux/macOSに限定する（Bookworm1919、macOS391）。Host11に含む1親caseで、子結果を数えない。native_fs.rs:513の#[cfg(unix)]ブロック内に攻撃スレッド、外部sentinel、30秒whole-child kill/reapがある。Windows424行の同名test成功は登録されたテスト関数の成功であり、Unix専用本体の攻撃スレッド・sentinel・watchdogは実行しない。Windows内部80件は登録名の成功件数であって、このrace本体の実行証拠ではない。Windowsの並行root逃走は未検証。VFS u7_flock_shared_and_release/u7_open_shared_lock_dropとKernel u7_syscall_flock_cancelは各層件数内。guest flock/dup_closeはnative差分63内。guest cloneの新設・独立U7 parallel suiteの存在は主張しない。diff_u7はmutexでnative/emulated組を直列化しsupport/u7.rsの30秒watchdogを保持する。

検証済み：coverageジョブの `cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit0、raw final-coverage-4d52be0a.log:2187にwholeworkspace7030 total/522 missed＝92.57%。同ジョブのU1 package限定stepはexit0、2617行に6780 total/1172 missed＝82.71%。この2値はU7限定coverageではない。現在U7限定coverageの再測定は未検証。

## 歴史的結果とGAP

ドキュメント根拠：docs/u7/inventory/coverage-final.txtは旧U7限定4203/4681＝89.79%、旧diff63/command6のexit0。fuzz-vfs-final-retry.txtはvfs_paths859022 runs/601秒、fuzz-syscall-final.txtはsyscall_args469436 runs/601秒、両旧exit0。依存相違があるので現在のASan合格または現在U7限定80%の証拠へ流用しない。FR9.3/NFR2/NFR3はGAP。再現コマンドはunit-test-instructions.mdの各600秒ASanとU7限定llvm-covであり、閾値を下げず次の検証に残す。

ドキュメント根拠：旧Red→Greenのcustom実装順序はdocs/u7/inventory/diff-red.txt等。今回既存コードの実装前Redを取り直したとは主張しない。現在のC2/C6/C8/C10/C11境界はHostのcapabilityからVFS、Kernel、Runtimeへ一方向で、root以外をambient reopenしない。

未検証：probe/aube全体、browser/wasm/Safari/JIT、stat uid/gid/timestamp全フィールド、ホスト外部rename後の既存dirfd identity、全OSの全errno同等性。現在3OSのHost/Runtime/VFS単体回帰の成功は、これら全挙動の証明ではない。NFR6はU7専用性能目標がなくN/A（速度評価はU10/U14）。

## 文書修正の検証

検証済み：Windowsの同名raceテストはUnix専用本体を実行しないため、本体の並行root逃走証拠をLinux/macOSへ限定した。成功登録件数80をWindows race実行証拠と扱わない。code-summaryは実改行のH2見出し2件を持ち、required-sectionsセンサーはPASS、findings0、exit0。実コマンド・stdout・初回経路誤りexit1と整合確認はverification/document-revision-validation.json。35 claims/88 liveソースの保存CI hash一致、17 IDs/既存target、FR9.3/NFR2/NFR3 GAPを再確認した。製品テストの再実行や閾値変更はない。
