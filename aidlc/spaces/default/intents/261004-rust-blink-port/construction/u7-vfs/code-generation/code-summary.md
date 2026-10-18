# U7 ファイルシステム：現在の実装と証拠

## 現行Step48（Loop-back 1）：共有のabi.rsの再確認

2026-10-17。製品・既存試験・source-manifest・traceability.json・旧証拠は変更していない。新しいテスト・CIは実行していない。

検証済み：`git diff e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d 1ceae86ce303a1019e97ac7d162ce0efa9fadd50 -- crates/paludarium-wasm/src/abi.rs` を読んだ。変わったのは `WorkerJit` の `execute_ready`／`execute` だけで、状態の型が `&mut [u64; 18]` から `&mut paludarium_jit::JitState`（`crates/paludarium-jit/src/bridge.rs` で `[u64; STATE_WORDS]`、`STATE_WORDS`＝50）へ、`jit_execute` に渡す長さが144から `paludarium_jit::STATE_BYTES`（50×8＝400）へ変わり、`// SAFETY:` のコメントに「ちょうどSTATE_BYTES（GPR・RFLAGS・RIP・XMM0〜15）」が加わった。U7が使う `filesystem_new`／`filesystem_drop`／`filesystem_remove`／`filesystem_snapshot`／`session_from_config_fs` のファイルシステムの部分は、この2コミットの間で変わっていない。同じ範囲でU7の他のパス（`crates/paludarium-wasm/`・vfs・host・kernel・runtime・`diff_u7.rs`・`fuzz/`）の変更はabi.rsの1ファイル（30行追加・7行削除）だけ。作業コピーのabi.rsは1ceae86cと一致する。

検証済み：abi.rsのSHA-256は、5fa16398で49a84734…、Steps45〜46の照合記録（`verification/step46-current-claims.json` の current と `reviewed-source-c7c63e52e0fe.tsv`）で947fab46…、e4f84768で f5fd27da…、1ceae86cと現在の作業コピーで 8619137da7f8df65207a8e22e86055db7ea62624340de72b2f73dbceea69d81f。

訂正：上のSteps45〜46の節にある「wasm abi/filesystemの相違はU11のIdle/Active/Closedとdispose処理であり」は、947fab46の時点の記録として残す。今のabi.rsには当てはまらない。今のabi.rsと5fa16398の差には、U11の `filesystem_drop` の close 処理に加えて、U14のJITの橋渡し（`jit_prepare`／`jit_execute` のimport、`WorkerJit`、`config_jit`、`session_jit_stat`、`u14-cost-profile` の診断用export、`session_from_config_fs` の code cache の接続）と、今回の `JitState`／`STATE_BYTES` の変更が入っている。また、Steps45〜46で現行として記録した947fab46は、今のabi.rsとも e4f84768 のabi.rsとも一致しない。947fab46からf5fd27daまでの変化はStep48の読み取り範囲の外で、ここでは分類していない。step46の照合値は当時の記録であり、今のabi.rsのbyte一致の根拠には使わない。

確認したが訂正が要らないもの：traceability.jsonにはabi.rs・JITの状態・ABIの長さについての主張がない。mtimeのsigned128 snapshot codecなどwasm境界の記述は署名5fa16398のCIでの当時の観測であり、今回の変更はファイルシステムのexportに触れていないので、分類とtargetは変えない。code-summary.mdの「JIT未検証」の記述は今も正しい。U7はJITの状態の大きさ・ABIを検証したとは主張せず、その検証はU14とU2 Step71の担当である。

未検証：今のabi.rsでのU7限定coverage・wasmのファイルシステム境界の再実行、947fab46→f5fd27daの変化の内容。strict guard・80%・guest30秒・fuzz600秒・既存maskは保持する。独立再レビュー・checkpoint・完了承認は別途扱う。

検証済み：正式sensor 2件をproject rootで実行した。`aidlc engine sensor-traceability --stage code-generation --output-path …/u7-vfs/code-generation/traceability.json` は pass true・findings 0（gaps・orphans・invalid なし）。`aidlc engine sensor-required-sections --stage code-generation --output-path …/u7-vfs/code-generation/code-summary.md` は pass true・H2 13件・findings 0。この結果の記入後に2件を同じコマンドで再実行し、同じくpassを確認してから書き込みを止めた。

## 今回Steps45〜46：現行Contractと有限再確認（2026-10-11）

検証済み：公式Testing Contract 7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5を反映し、別の内容確認後に記録照合を実施した。製品・既存試験・manifest・traceabilityは変更していない。旧43claims/96展開ファイルは92一致、4相違。diff_u7はClippy対応のbyte decodingだけ、native_fsはWindows精度のテスト2件だけが相違し、Hostの製品mtime処理は不変。wasm abi/filesystemの相違はU11のIdle/Active/Closedとdispose処理であり、旧wasm証拠を現行disposeへ流用しない。読取コマンドは `git diff 5fa16398eae31ec178bfd93d3029b24ee31ac5e5 -- crates/paludarium-harness/tests/diff_u7.rs crates/paludarium-host/src/native_fs.rs crates/paludarium-wasm/src/abi.rs crates/paludarium-wasm/src/filesystem.rs`。

検証済み：旧294入力は284一致・10相違、Cargo.lockとfuzz/Cargo.lockは旧原本と一致。相違にはRust固定版・wasm build/consumer/test・U10 lockも含まれるため、旧U7全入力一致や旧coverage89.02%・旧compilerでのASanを現行全体の新測定として主張しない。現行U11 source-hashesと別に照合し、保存済み現行品質CI38104676911／MMU追加証拠を扱う承認済み有限checkerへ引き渡す。数値とSHAは verification/step46-current-claims.json と step46-dependencies.json に保存した。

未検証：今回の新しいU7限定coverage、fresh Linux差分・Windows隔離の再実行、U7全OS・全入力、U11同時dispose修正完了、並行セッションID競合の完全解消。旧89.02%は履歴であり、測定分母を変えず現行限定再利用可否を独立レビューへ渡す。正式sensor・独立レビュー・最終checkpoint・完了承認はこの更新後に別途扱う。strict guard・80%・guest30秒・fuzz600秒と既存maskを保持する。

## 履歴Steps40〜43：R-04修正と実測（2026-10-10）

検証済み：修正前CI38052956638/head aa332cf7359c95051598ef2b367ae3e44b5a37aaでLinux nativeの6境界を先に取得し、負3ケースのEIO差分Red（test exit101）を保存した。Host/VFS/wasmのmtimeをi128 nanosecondsへ揃え、従来u64正値範囲を保持した。Kernelはfloor秒・非負nanosecondsとchecked EOVERFLOWへ変換する。wasm snapshotはsentinel/version2のsigned128へ更新し、JS decoderは旧u64形式も読み取り、切断・未知版・過大countを拒否する。独立clock syscallは変更していない。

検証済み：署名Verified head5fa16398eae31ec178bfd93d3029b24ee31ac5e5、CI38053646678は6/6 jobs成功。全294入力・両lockは各jobのbefore/after/current一致。担当manifest43claims/96filesも署名headと一致。fresh native stat/fstatの-1秒/-0.5秒/-1ns/0/1ns/1.5秒は全6 raw値一致、diff_u7親64成功。Host/VFS/Kernel/wasm境界324 Rust testsと2 doc tests、Node32 tests、wasm32 check・fmt・clippy全exit0。旧wasm配布binaryを新runtime実測の根拠には使わない。

検証済み：同じU7 scope/除外/80% gateで7067/7939=89.01624889784607%。Windowsは実symlink権限true、1000反復/43交換、outside不変、strict cleanup、whole-child572ms/exit0。ASan/LSanはvfs_paths3675837、syscall_args1455696、mmu_ops3003322 runs、各601秒/exit0。seed1・timeout30・rss2048・既定max_len・既存suppression・detect_leaks1を維持し、最小C各2回exit0、binaryhash/symbols/corpusと全rawを保存した。

検証済み：coverage補足CI38053960030/head79baa5d6f7c0ec8afa7e2d3e2cf85ffcfcca648cは同294入力・同scope・同coverageで成功。19 hash0警告は重複3関数で、測定対象行の欠落0。6境界のnative/emulated rawは同runログ467〜478行に保存。証拠はverification/step43-fixed-proof.json、step43-coverage-mapping-proof.json、step43-raw/、step44-source-claims-proof.json。

未検証：任意入力・全UB・全OS・全ブラウザruntime・probe/aube/JIT・並行セッションID競合の完全解消。新canonical verify-current-u7-r04.pyは具体化済みで、親によるコマンド承認前は実行しない。正式sensor・独立レビュー・完了承認は別途記録する。strict guard、80%、30秒、各600秒を維持する。

## 以下は修正前の履歴

以下の「現行」「未修正」「U11対応」は当時の記録であり、今回の修正後の判定は上記Steps40〜43を優先する。旧成功は修正後の証拠として再利用しない。


## 今回Steps36〜38：現行実機CI（2026-10-10）

検証済み：製品・テスト・lock・主CI変更なし。隔離jj診断head459591c798152d3098779f3050acb734f382ac55は署名Verified、CI38050439711のWindows・Linux coverage/diff・ASan全3job成功。製品/テスト/fuzz/設定291入力と両Cargo.lockはCI before/after/currentが一致（step36-all-input-proof.json、step37各proof）。最新公式nightly2026-10-10、cargo-fuzz0.13.2、cargo-llvm-cov0.9.1とActions SHAを診断環境へ固定した。

検証済み：Windows専用fixtureは実symlink生成成功、1000victim反復、49交換、outside不変、strict cleanup、whole-child watchdog817ms/exit0。Linux同instrumented runのfresh native差分diff_u7は親63成功、既存scope/除外のcoverage6988/7864=88.8606%、80%gateとJSON exit0。vfs_pathsは3422797 runs/601秒、address+detect_leaks=1/既存LSAN suppression/seed1/timeout30/rss2048/defaultmax_len、最小C2回/本体/全input比較exit0。生ログ・binaryhash/symbols・corpus/crashをstep37-rawへ保存した。

検証済み：LLVMの19件mismatched warningはhash0の重複3関数。別clean同scope診断CI38051169927/head7928dcf0（Verified）はfloor/JSON/dump全exit0、同coverage結果と291入力一致。Host2関数の全source範囲は同名の有効profileで集計済み、Types1関数は既存除外。対象行の欠落なし（step37-coverage-mapping-proof.json）。診断オプション非対応/JSON出力混在の失敗2runも保持した。

## 現行検証の制限

ドキュメント根拠：1970年以前mtimeのNativeFs stat/cap_stat EIOは未修正、承認済みU11対応。負時刻回帰・任意入力/全UB/全OS/全wasm/probe/aube/JITおよび並行セッションID競合の完全解消は未検証。今回の有限CI成功だけへ主張を限定し、strict guard・80%・30秒・600秒・custom Testing Contractを維持する。以下Steps33〜34の未検証記載は再測定前の履歴である。

## 今回Steps33〜34：現行照合（2026-10-10）

検証済み：製品・テスト・設定変更なし。35 claimsの88ファイルが署名済み7eb1819f52acede33e83775374dd4ee93edf643bとraw bytes一致。`jj --ignore-working-copy file show -r <baseline> <path>` の比較結果はverification/step33-source-proof.json。歴史的成果物59件のhashは59/59一致（step33-saved-evidence-integrity.json）。

検証済み：旧Linux fuzz／coverage／Windowsの154依存listingは現行113一致・41相違。Host/VFS/Kernel/Cargo.lock等が変化したため、旧Windows1000反復/55交換、diff63、coverage90.4652%、vfs_paths3132329/601秒を現行合格に再利用しない（step33-evidence-compatibility.json）。U4新CI38047281434／f2fa1be5のsyscall_args1263808回/601秒/exit0は291依存・両lock含むbefore/after/current一致。この有限target証拠はvfs_paths／U7 coverageの代替ではない。今回新しい製品テスト・CIは実行していない。

## 現行の不足と既知課題

未検証：現行U7限定coverage80%、vfs_paths600秒、Windows一時fixture並行隔離、Linux diff_u7現行専用再実行。次の確認はunit-test-instructions.md記載の同scope・80%・600秒・30秒コマンドを現行source固定native Linux／Windowsで実行し、依存・lock・設定・生ログ・exitを保存する。

ドキュメント根拠：native_fs.rs:66–73/349–358のstat/cap_statは1970年以前のmodifiedでduration_since(UNIX_EPOCH)失敗をEIOへ変換する。現行で未修正、承認済みU11対応に残す。負時刻の実行回帰は未検証。strict guard・80%・30秒・各600秒・custom Testing Contractを維持する。

## 以前の実測記録

以下の「現在」「今回」は当時の実測を指す。現行への適用可否は上記Steps33〜34を優先する。

## 実装と現在の証拠

既存VFS/Kernel/Runtime/CLIの製品意味論を保持。NativeFs test moduleへWindows-only一時fixture回帰を追加した。署名Verified head8cba60d9…/Windows CI37765054790で1000反復・完全交換55・共有違反有限retry473、symlink権限・outside不変・strictcleanup確認、子exit0/881ms（30秒上限）。154 CI before/after/currenthost hash厳密一致、35manifest claims/88filesは署名診断headと一致。具体command/raw/hashはevidence-current.mdとverification/step31-windows-proof.json。

## 品質と制限

初回Windows101失敗と中間CRLF差を履歴保存し、最終LF runだけを正本に採用。FR3.2/NFR4はこの有限fixture観測範囲のOK。Linux vfs_paths3132329/601秒・U7限定90.4652%/diff63・syscall_args1296522/601秒はWindows-only test差の非影響を厳密復元確認した再利用で、新実行ではない。任意入力/全UB/全OS全挙動/U7 wasm/probe/aube/JIT等は未検証、NFR6 N/A保持。

旧canonicalはtest-only1file差でexit1を保持。新checker案は旧全186paths/3OS/4fuzz/Safari14検査を維持しWindows exacthash-bound証拠を追加、手動exit0。protected command承認/独立review/checkpointは親担当。60 IDs/旧R-01・R-02 Resolved、完全Testing Contractのcustom exact ordering・80%/30秒/600秒/nightly固定を保持した。

## 以前の記録

以下のWindows未実行GAP・主source不変はSteps21–27当時の履歴であり、今回の実測とtest-only差へ適用しない。

# Steps21–27 履歴

## 実装と現在の証拠

既存MemFs/Host mount/Kernel FD/syscall/Runtime preload/CLIを保持し、主repoの製品・test・CI変更0。35claims/88filesを署名178da99eと現在hostで照合した。isolated診断workflowだけ署名pushし、Verified head eafa5ac6aa9c9cc134dbba923b3e082f8b5e4d05のCI37760390069でLinux検査を実測した。

検証済み：vfs_paths3132329 runs/601秒、ASan+LSan exit0、最小C2回exit0、sanitizer error観測0。U7限定coverage4317/4772=90.4652%、80%gate exit0、diff_u7親63 passed/0 failed。両CI source before/after・baseline178・現在host154paths一致。U4 syscall_args1296522 runs/601秒は全依存hash一致を確認した再利用であり新実行ではない。具体コマンド/raw/JSON/exit/ASan symbols/corpus hashはevidence-current.mdとverification/step25-{fuzz,coverage,syscall-reuse}-proof.json。

## 品質GAPと制限

Windows並行root逃走本体は安全性チェックで停止との親報告後の中止指示に従い未実行・未検証、FR3.2/NFR4 GAP。Step23とWindowsを含むStep22/24/25の全体達成checkboxを付けない。Linux/macOS既存隔離回帰とWindows登録成功を区別する。FR9.3/NFR2/NFR3は今回有限target/scopeの検査達成に限定したOKであり、全任意入力/全UB/全OS/全wasmへの保証ではない。NFR6 N/A、probe/aube/U7 wasm/JIT等未検証を維持。

Testing Contractのcustom/native期待値先行/internal test-after、80%/600秒/30秒/nightly固定を保持。既存17 IDsと43 fallbackの60 ID分類、旧R-01/R-02 Resolvedを保持。主source manifest35claimsは不変。独立review/正式checkpointは親担当。

## 以前の記録

以下の4d52/旧81・80件/89.79%/ASan未測定・3GAP表記はSteps1–20時点の履歴であり、現在の結果には適用しない。

# Steps1–20 の履歴

## 実装と現在の証拠

既存のMemFs、明示Host mount、inode/OpenFile、Kernel FD/file syscall、Runtime preload/mount、CLI接続を保持した。今回のSteps 15–17では製品を変更せず、35 claims/88ソースファイルと現行署名CIのbyte一致を確認し、記録を整合した。変更面の正規一覧はstrict source-manifest.json。

ドキュメント根拠：FR2.10/FR3.1–3.4、C2/C6/C8/C10/C11。Hostは保持root capabilityから相対操作し、既定MemFsはprivate。VFSはsymlink展開と..を順に解決し、FDは共有open-file descriptionのoffset/flock所有権とunlink後inode寿命を保持する。既存Host errno/link metadata、VFS/Runtime fixture解放の修復を現在証拠へ反映した。

検証済み：CI7＋native4の11 jobs成功（head4d52）。Linux差分63親case、U7内部Linux/macOS81・Windows80、CLI integration全6中U7専用2。Host raceは内部Host11に含む1登録名で、本体の実行証拠はLinux/macOSに限定する。Windowsでは同名テストのUnix専用本体を実行せず、並行root逃走は未検証。名前・raw行・実コマンド・exitはevidence-current.mdとverification/current-counts.json。coverage全体92.57%とU1限定82.71%は80%成功だがU7限定測定へ読み替えない。

## 品質GAPと制限


旧snapshot88中5相違、両fuzz targetの旧依存全体一致は確認できない。旧U7限定89.79%およびvfs_paths859022/syscall_args469436各601秒は歴史的結果。FR9.3/NFR2/NFR3は現在600秒ASanとU7限定coverage未検証のGAPを維持した。traceability.jsonはU7担当17 IDsのみ、実ファイルtarget、NFR6のN/A理由を保存した。

Testing Contractのcustom順序、80%/600秒/30秒、nightly固定と依存方針を保持した。今回実装を再生成せず旧Red/Greenを歴史として保持する。probe/aube全体、wasm/Safari/JIT、stat全フィールドや全OS全Host挙動は未検証。詳細と再現手順はevidence-current.mdとunit-test-instructions.md。
