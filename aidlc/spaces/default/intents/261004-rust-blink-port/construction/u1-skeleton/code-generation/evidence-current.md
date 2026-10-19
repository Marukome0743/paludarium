# U1 sourceの検証記録

## 現行：Steps63〜66、62611品質修正

検証済み：verification/step66-quality-binding.json（SHA256 a31676a8dd8330ac04a7d6b712c387e857f244ed1d86cefd96d9af7800266184）は署名62611f2556c4caf1470a7eb4471269d92611db6e、U1 CI38392056273の7必要ジョブ・362入力、quality CI38392057138の34必須ジョブ・367入力、standalone ASan38392056163の13対象各601秒・345sourceを結合した。U1 hello6／diff16／frame200比較とfixed11package11302/12122は旧executions全述語で照合した。4環境の2mode各14caseは同一module／guest／oracle SHAとraw出力／filesystemの再計算を通過した。

検証済み：quality初回33成功・LLVM鍵取得curl7失敗のrun/jobsとjob115278500893原ログを保持した。attempt2はjit_cache job115289746913のみ新実行で成功し、成功33jobのGitHub複製IDを対応表へ保存して実行時刻・steps・原ログbytesを完全照合した。Windows10必須反復は各1000操作・交換成功・sentinel不変・cleanup・30秒watchdogを満たす。

検証済み：全116回帰が成功、107分類／targetは不変、旧b4cc・b451・b623のcontext全文と各canonical hashを履歴へ保持した。source-manifestは116件・重複0。旧全canonical単独診断59453はexit0で、旧360入力と旧main全述語を署名viewに保持した。新全checker診断85478もexit0で完走し、最終出力 `All thirty-four mandatory quality jobs and unchanged historical predicates passed.` を確認した。これはレビュー前診断であり、正式完了確認ではない。結果記録はverification/step66-diagnostic-result.json、完全stdoutはtool transcriptに保持する。

検証済み：正式traceability／required-sectionsは各exit0／pass:true／findings0（107分類、H2=20）。verification/step66-sensors.jsonへ実コマンドと観測結果を保存し、完全stdoutはtool transcriptに保持した。

未検証：独立レビュー・新最終確認コマンドの承認／正式実行・完了承認はこの記録時点で未完了。生の非必須性能診断はcomplete:true／passed:false（interpreter5.48059秒／JIT14.53658秒、p=1）として保持する。歴史jit_compile panic、初回crashの直接core欠落、セッションID競合の完全解消は別残件である。

## 履歴：Steps55〜62、b623 frame修正

検証済み：verification/step62-execution-binding.jsonは署名b623c7ca41ac7296826b171ee0ccc28b3a529ce9／CI38380449349／360入力／必要7jobと、11artifact・7job log・4metadataの22原本を結合する。旧executionsの全predicateは追加frame以外の10artifactへ明示投影して維持し、frame2種各100の計200比較原本を別に検査した。fixed11package11226/12041、workspace11698/12542でともに80%以上。ASan run38380449276の13対象各601秒・343source・両lock・compiler/settingsはverification/step62-sanitizer-binding.jsonとstep62-sanitizer-originalsへ保存した。

検証済み：旧b4ccとb451contextをhistoryへそのまま保存し、107分類・target不変と現行参照7回帰、5commit chain／限定6filepublication8回帰が成功。source-manifestへfixture2件と診断／回帰のapplication filesを追加した。新checkerは旧decoder canonicalのhashと旧355 signed inputsを固定し、旧main全predicateを旧source viewで維持する。現行360入力と旧355入力の役割は混ぜない。診断結果は以下へ記録し、正式確認は別途承認後に実行する。

検証済み：新checkerのレビュー前全診断はtool session 47012でexit0、旧canonical全検査と新execution／13 sanitizer照合を完走した。97回帰成功。親担当の正式required-sections（19 H2）／traceability sensorは両方exit0／PASS／指摘0件。source-manifestは112件・重複0。step62-diagnostic-result.jsonは結果記録であり、完全なstdoutはtool transcriptに保持され、架空のraw logを作成しない。

未解消：初回native faultはcore欠落のため直接のRIP証明がない。元ELFの独立再現とleavewの65536 bytes誤windowはstep57-frame-cause-proposal.mdを根拠とする。全品質CI38380449837のFirefox／Safari／Windows失敗原本はstep62-quality-originalsのjob-115242598839.log／job-115242598843.log／job-115239244722.log。U14ブラウザ、性能、Windows raceとID競合をU1の有限成功で解消済みにしない。独立レビュー・新コマンド承認・正式実行・完了承認は未完了。

## 現行：旧JS測定先の再構成（2026-10-12、Steps48〜50）

検証済み：旧固定一時先が消失した正式確認exit1の原因を、保存342入力と同じbytesの検査時再構成で修復した。旧V8原本83 JSONのURL、旧checker／validator／collectorと保存414snapshotは変更せず、実行前後hash一致。既存33回帰＋再構成8境界＝41件成功。既存先の完全一致再利用では既存ファイルを削除せず、新規先だけ所有inode／bytes照合の非再帰cleanupを行う。排他・symlink／祖先symlink・foreign bytes／余分・検査中source変更を拒否し、任意のhostile actorに対するrace-proof保証は主張しない。

検証済み：承認済み確認スクリプトのレビュー前全診断exit0、保存83原本の旧aggregate完全一致、旧U12全検査と現行362入力・署名済みCI・実hello6・固定coverageまで成功。終了後の旧一時先不存在も確認。原本の再計算とCI証拠照合であり、新しいguest／coverage測定ではない。詳細・command・実exit・不変hashはverification/step50-historical-js-reconstruction.md、step50-diagnostic-result.json、step50-full-diagnostic.log。

未検証：R-05初回native SIGSEGV原因、R-06のMac Linux専用diff0件／旧canonical exit1の解消、今回の正式sensor・再レビュー・checkpoint・完了承認、U13全体とID競合の完全解消。既存失敗原本、362入力／両lock・80%下限・guest30秒を維持する。

## 履歴：R-04修正（2026-10-12）

検証済み：e2d3f316206974ef098fd9bdc85d94a8376a51f8／CI38171135965の最新原本へ結合した。hello3はnative/emulator計6の実終了0を新receiptで確認し、他13差分は状態同値性だけとした。固定11package coverage92.8832%、33回帰成功。成功6jobの実行引継ぎとcoverage再実行は14 API recordの全step/時刻/原job IDsで区別し、旧failureも保持した。詳細はverification/r04-exit-evidence-repair.mdとcurrent-source-bound-results.md。

未検証：native u2_frame_forms初回SIGSEGVの原因完全解消、正式再レビュー／最終確認／完了承認、U13全体とID解消。下記R-04前の実exit0推論は反証済みで、現行の根拠へ使わない。

## 履歴：R-04前Steps44〜47（2026-10-12）

検証済み：最終署名17231f7a0cdfe9da8659497d963979690db1c2b3と現行362入力一致、CI38169414877は7必須ジョブsuccess。fresh hello3／diff16、固定11package・42files・10196/10974行=92.9105%、workspace10668/11475行=92.9673%、18回帰を今回実測した。原ZIP9件はAPI digest完全一致。詳細は verification/current-source-bound-results.md、current-u1-originals-manifest.json、current-u1-observation-binding.json。旧342＋72支援の414snapshot全predicateは歴史層として保持し、現行実測と分離する。

未検証：今回の独立レビュー・正式確認・完了承認、U13全体・セッションID競合の完全解消。現行本番wasm4環境／11ASanは今回新規実行していない。以下の「現行」は各履歴時点の表現であり、今回362入力の成功主張に転用しない。

## 履歴：Step38〜40の担当説明修正（178da99e）

今回Summary Confirmation `01e6d98e3147d0b715a7b5f4045ee7fce1deb952f9cba824b09f6f8f9bf89228`後、FR5.4のDeferredを保持し、notesの担当へU5を追加した。共有unit-of-work.mdのU5はゲストのnative thread割当、U11はwasm Host/LauncherのWorker割当、U12/U13はmacOS/Windows backendである。C2の共有Host traitとBR6.1を維持する。107 coverage行中、他106行とupstream_idsは同一であり、verification/step38-traceability-preservation.jsonにbefore/after hashと検査を保存した。製品ソースは変更していない。

検証済み：承認済みcanonical `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。署名済み178da99e88d1aea242c5141207887767a69fa670と現行186 tracked application filesのbytesを照合し、厳密hashで確認したSafari報告の文書例外だけを区別した。CI37745425190の8jobs、sanitizer37745425204の4jobs、native37745425183の2jobsを同じSHAとして確認した。stdout/stderr/exitはverification/step39-native-ci.jsonとstep39-native-ci.logに保存した。保存済みCI証拠の再確認であり、この文書修正で製品テストを再実行したものではない。

検証済み：共有ソースの最新証拠はU2 verification/step47-proof.jsonとstep47-ci-metadata.jsonである。native3OS、lint/依存、全体92.68%・U1対象packages83.04%の両80%gateを保持する。U2が取得したproduction wasm Node/実Safari14ケース、共有Rust heap・nested Workers、およびCPU/MMU/decode/load_elf各601秒ASan+LSanは、その限定観測として参照しU1新規実装とは数えない。guest clone/futex全体、任意guest・任意入力の完全保証、JIT、Chromium/Firefox今回再検証、U1 mmu_ops/syscall_argsの現在600秒ASanは未検証。夜間scheduled run実行とは呼ばない。30秒watchdog・nightly-2026-10-01・各600秒・比較mask・両フックを保持する。

検証済み：限定sensorの実コマンド・stdout/stderr・exit・passはverification/step39-sensors.jsonへ保存した。traceabilityとrequired-sectionsは両方exit0/pass:true/findings0（107対応、H2=11）である。Step40の独立レビューと正式完了確認は親担当であり、この記録で完了済みとはしない。U4/U9の指摘もそれぞれのUnitで扱う。

## 履歴：以下はStep1〜37当時の記録

以下の旧「現在」「今回」「未完了」「未検証」は各記録時点の観測であり、178da99eの現在bytesへの主張ではない。4d52/af9bのCI件数・source比較・旧Safari未検証状態を現行結果へ転用しない。今回の現在値は上のStep38〜40とstep39証拠で確認する。

## 履歴af9b：Step32〜34

検証済み：Summary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後、read-only git show af9b739d742a9552f44fc1515646c862b19e5de2:<path>でmanifest全103claimsを展開した108filesを比較し107一致、既知非ビルド.gitignore例外のみ。source-bytes-af9b739d-current.jsonへ全hash/CIhashを保存した。旧source-bytes-current.jsonと以下4d52証拠は履歴。47IDs/47対応、OK target欠落0。claims/trace status/閾値を変えていない。

検証済み：python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci.py、exit0。CI37713953347の7jobsとnative37713953340の4jobs成功、署名済みaf9bと全162 tracked application files一致（既知.gitignore例外を除く）。出力はverification/step32-native-ci.log。新しい製品テスト実行はなく現行bytesのCI再利用。

同af9b U9採取rawログをrootがU1 verificationへコピーした。ci-native-bookworm.log:525〜527はhello3cases成功、542行はU1差分16pass/0fail。ci-coverage.log:2340は全体7155/524miss=92.68%、2802はU1対象11packages6905/1171miss=83.04%。両80%gate成功、後続共有実装を含むpackage分母。ci-jobs-37713953347.jsonとci-jobs-37713953340.jsonが11job証拠。3OS成功・lint/依存成功を同runのjobsで確認する。

今回Summary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13eに対応して4producesとstrict v1 manifestを保存。instructionsの旧Step29〜31説明を履歴として区別し、今回Step32〜34を追記した。wasm/SafariとU1各target現行600秒ASanは未検証、旧結果を合格へ流用しない。30秒watchdog/nightly2026-10-01/80%/600秒/masks/2フック/Docker VMMを保持。rootの日記はレビュー前に完了し、全書込を終えて固定する。製品・CI変更なし。

Step32〜34時点（履歴）の限定sensorの実コマンド/exit/stdoutはverification/step34-sensors.json。required-sectionsはpass:true/H2=7。traceabilityはpass:false：47IDs内のinvalid entries/targets・GAP・ORPHANは0だが、stories不在時の全requirements fallbackが60個のFR/NFRをmissing_from_upstream_idsとして要求した。47IDsを保持する承認範囲に従い集合を増補せず、この未解決sensor結果をrootへ報告した。初回はtraceabilityへsummary経路を渡してinvalid JSONを返したため、正しいtraceability.json経路で再実行した。exit0をsensor PASSへ読み替えていない。

旧source-bytes-current.jsonは4d52時点の履歴であり、現行sourceに対して8claimed filesが異なるという先行レビュー指摘を保持する。現行一致の根拠は今回更新したsource-bytes-af9b739d-current.jsonで、旧snapshotの一致は現在の合格根拠としない。

## 履歴：Step29〜31の再保存（4d52時点）

u1-redo-brief全文と新Summary Confirmation後に103claims/108filesを再照合し、snapshot差異0、4d52一致107files/別作業.gitignore例外を確認。trace47件のOK target欠落0。新製品変更・新testsなし。今回の4produces（plan/instructions/summary/traceability）とsource-manifestを全て保存し、既存のCI11jobs/U1差分16/coverage92.57%・82.71%と未検証fuzz/wasm/Safariを保持した。日記を依頼前に終了しレビュー中は全書込・SCM snapshotを固定する。先行Step26〜28は履歴。

## 履歴：4d52のsourceとCI

検証済み：4d52be0a6f3b11d6c11a62f96196985c9c280fdc、GitHub verified:true/reason:valid。CI37695518838は全7jobs、native37695518927は全4jobs成功。実行コマンド・CPU・test名・件数はverification/final-{ubuntu,bookworm,mac,windows,coverage}-4d52be0a.log。詳細とリンクはcode-summary.md。

Windows Host25/Runtime25/VFS45件通過。Ubuntu/BookwormのAMD EPYC7763で全workspaceが通過し、両方の差分はU1 16/U2 38/U4 44/U7 63件。全体行coverage7030/未実行522=92.57%、U1対象11packages6780/未実行1172=82.71%。両下限80%を維持する。

Intel e081の全workspace成功は先行証拠。e081→最終のCPU・decoder・REP observer/fixture・SSE guestはjj diff0。最終runのIntel全workspace再実行とは呼ばない。

## 期待結果・修復前失敗・手元検証

verification/repair-implementation-results.md、host-repair-results.md、runtime-cleanup-results.md、vfs-cleanup-results.mdと各ログを参照。SSE native期待結果とRedは実装前、内部単体はtest-after。Windows修復前raw32はHost/Runtime/VFSの各strict cleanupに記録され、後片付けの失敗を実際の機能assertionの失敗と断定しない。

Docker限定検証の通過とQEMU oracle差による全workspace失敗を区別する。ENTER allocation faultやsignal/errno差のログは保持する。

## 履歴：4d52の静的照合と所有

検証済み：python3 aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/check-current-source.py、exit0。103claims/108files、欠落・未追跡・現在U1 snapshot不一致0。上流47/対応47・OK target欠落0、census68根拠欠落0。Cargo.lock SHA256553b2b8d7670426ed73c51f1d756b93a6a8b26bc427de87afa01a15f60264b27。

U7以前のsnapshotとの差5filesはLF/Host/Runtime/VFSの関連修復。以前のsnapshotは履歴として保持し、独立後続unit成果物を作り直さない。現在のmanifest/traceabilityは実ファイルの対応であり、全quality targetの合格宣言ではない。以前の本文はevidence-before-host-repair-20261008.mdへ保持した。

## 復旧と未検証

検証済み：plan-approval-guardとcontinue-workflowは登録済み、bun test tools/aidlc-recovery/recovery.test.tsは9pass/0fail/37assertions。rejected reportの直前にも両方を再確認する。

未検証：今回のwasm/Safari、U1各fuzz再実行、decoder候補比較の歴史的ログ。固定nightly、各600秒、coverage80%、30秒watchdog、比較maskを維持する。先行197件/94.00%等の値を現在の合格へ転用しない。

## 履歴：Step26〜28の記録再確認（4d52時点）

検証済み：新attemptのPlan Approval/内容確認後、103claimsを108filesへ展開しread-only `git show 4d52be0a:<path>`とSHA256で照合した。107files一致、`.gitignore`のみ別作業の保持済み設定変更として相違。現在snapshot108filesは全一致し、manifest所有範囲は追加していない。詳細はverification/rereview-source-4d52be0a.json。`.gitignore`変更の動作検証を旧CI成功とは呼ばない。

保存済みCI7+native4jobsと同じ製品bytesを再利用し、新規テスト実行として数えない。Bookworm raw524〜526行のhello_c/hello_rs/引数付きhello_rs、541行のU1差分16pass、coverage raw2187/2617行の92.57%/82.71%を確認した。上流47件/対応47件、OK target欠落0、source欠落0。新製品不具合・追加test必要性は見つからず製品修正なし。

wasm/Safari・U1各targetの現在600秒ASanは未検証のまま。traceabilityのOKは実装・設定・報告の対応であり未測定項目の合格を意味しない。30秒watchdog・nightly2026-10-01・各600秒・両coverage80%を保持。2フックはrootが有効性を確認し、今回rejected reportの原因を特定したとは主張しない。日記をレビュー依頼前に確定し、以後はrootの独立レビュー記録までsource/成果物/SCM snapshot操作を停止する。

## Step35：共有要件の担当分類

今回Summary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRの行・status・targetを保持し、要件fallback60FR/NFRを追加して107IDs/107対応へ更新した。U1範囲は実在source/test/configへOK、後続完全機能と未検証fuzzはDeferred、集約見出しと資源上限非適用は理由付きN/A。後続Unit実装をU1成果へ転用しない。CIの証拠名を実在ci-jobs-37713953347.json/ci-jobs-37713953340.jsonへ修正した。検査結果はverification/step35-traceability.json。旧Step34のFAILは履歴として保持する。

## Step36〜37：実Safariと文書差分の確認

今回Summary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、検証済み：本物のSafari 27.0.1/macOS 27.0.1 build26A434、固定nightly-2026-10-01で単独wasm spikeがexit0。crossOriginIsolated=true、waitNotifyPassed=true、wait result0、value42、waited201ms、notify woke1、total216ms（5秒以内）。verification/safari-local-20261008-pass.jsonが生結果。Remote Automationによる初回blockedログを保持し、夜間CIの実行結果と区別する。Node/Chromium/Firefoxは過去の結果で今回再実行ではない。U1各fuzz現行600秒ASan、共有stdヒープ、入れ子Worker、エミュレータ全体のSafari動作は未検証。

検証済み：verification/step37-application-bytes.jsonで署名済みaf9bと全162 application filesを再比較し160一致。差分は既知非ビルド.gitignoreと承認対象docs/reports/wasm-threads.mdのみ。runtime/source/test/build/CI bytesは不変。旧Step32の全一致はSafari報告更新前の履歴である。U1既存103claims・Safari報告claimを保持した。

未完了：canonical verification/verify-native-ci.pyはexit1、Current source differs from tested commit: docs/reports/wasm-threads.md。stdoutのCI7jobs/native4jobs成功と現在sourceの全一致を混同しない。verification/step37-native-ci.logへ保存。検証器・除外条件・CIを変更せず、Safari報告を戻さず、親担当へこの拒否を引き渡す。Step37の正式検証・独立レビュー・完了確認は未完了。

検証済み：人が選択した完了検査 `python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。元のverify-native-ci.pyは保持し、署名済みCIと異なるSafari文書・実測証拠の厳密hash対応だけを新検査で確認した。CI7jobs/native4jobs成功、全162 tracked application filesをaf9bへ照合し、既知.gitignoreと承認済みSafari報告以外の差分を認めない。実行ログはverification/step37-approved-native-ci.log。元の検査exit1は履歴であり、今回選択済み検査の成功と区別する。独立レビュー・Unit完了確認は引き続き未完了。
