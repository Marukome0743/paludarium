<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations

- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。

- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。

- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。
- 2026-10-08T11:32:58Z — U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。
- 2026-10-08T11:24:28Z — U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。
- 2026-10-08T11:11:57Z — 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。
- 2026-10-08T11:05:09Z — ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。

- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。
- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。
- 2026-10-08T06:28:40Z — U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982); CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance.

- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。
- 2026-10-08 — U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。
- 2026-10-08 — 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。
- 2026-10-08 — U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。
- 2026-10-08 — U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。

- 2026-10-08T02:14:35Z — 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。

- 2026-10-08T01:21:35Z — U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。
- 2026-10-08T00:36:15Z — U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。
- 2026-10-08T00:28:21Z — U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。
- 2026-10-08T00:19:19Z — U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。
- 2026-10-08T00:08:28Z — U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。
- 2026-10-07T23:58:36Z — U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。
- 2026-10-07T23:36:47Z — U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。
- 2026-10-07T23:28:42Z — U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-10-17T13:35:00Z — U1 Step72 の再レビュー（review-45、READY）の新しい Minor 2件（Step72 で足した receipt と job の照合・「attempt 2 は失敗した job だけ」の検査に回帰がない、result.json の claim_scope に module の結び付けが metadata 頼みという限界がない）は、人の指示で、次の binding の更新（U11 の Safari の2ファイルと U14 の記録の更新を許すとき）に必ず直す。人はこれを条件に修正後の checker（a7836f9b…）の採用を承認した。
- 2026-10-17T10:50:00Z — U14 Loop-back 1：Step31の見積りで、整数SSE群だけが確実に速くなる（約−13%〜−7%）、GPRは遅くなる、byte比較は向きが決まらないと出たため、人が「SSEだけ先に」を選び、Step35・36を今回は行わないことにした。Step32はsigned head 12d6a2f6（Verified、テスト4ファイルだけ）、u14-quality run 39025059974 attempt 1 の job 117374320550 で、15個の `sse-*` ケースすべてが native/interpreter/JIT-fallback で一致した（JITの翻訳を入れる前）。同じrunのfuzz `kernel_threads_u5` は `apt.llvm.org` へのcurl exit 7で準備段階で止まり、PR CI 39025046947のSafariはsession作成の時間切れ（既知）。どちらも失敗したjobだけを再実行した。Step33・34は手元で実装した（未push）。
- 2026-10-17T23:50:00Z — U14 Steps42〜43：計画との違いが2つある。(1) source-manifest.json は変えていない。12d6a2f6・1ceae86c の14 path はすでに `writes` にあり、engine の `validateUnitSourceManifestBytes` が `stage`・`unit`・`version`・`writes{path,repo}` 以外を拒否するため head を書く場所がない。commit ごとの表と署名 head は code-summary.md に書いた。(2) traceability.json に NFR7 を足していない。U14 の表と Unit 定義に NFR7 がなく、足すと新しい ID の追加になるため。Safari の修正は FR8.2 の注記と summary に書いた（NFR7 は U11 の表にある）。どちらも人の checkpoint で示す。
- 2026-10-18T00:15:00Z — U14 Step46 の入口 `u14_candidate_v2.py`（binding-07）を人が正式確認コマンドとして採用した。再レビュー（READY）の新しい Minor 3件（traceability の行に run 39028305765・39030957672 が attempt 2 で成功したことがない、NFR2・3・8 の参照先が FR8.2 だが fuzz・監査の run は FR8.1 にある、code-summary.md が Steps45〜46 と v2 に触れていない）は、次に U14 の記録を更新するとき（Build and Test での更新など）に直すと人に提示し、人はそれを条件に採用を承認した。
- 2026-10-18T00:30:00Z — U15 Step12 の再レビュー（READY）の新しい Minor 3件（新しい節の冒頭の「traceability.json は変えていない」が Step11 時点の文、traceability の先頭の文が計画の道しるべ1文より多い、`U15_acceptance: GAP` がどの表示か分かりにくい）は、次に U15 の記録を更新するときに直すと人に示し、人は U15 を承認した。
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs

- 2026-10-08T10:45:00Z — Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。

- 2026-10-08T10:28:48Z — Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。

- 2026-10-08T10:00:00Z — Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。

- 2026-10-08T09:54:32Z — ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。

- 2026-10-08T09:20:00Z — U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。

- 2026-10-08T09:09:16Z — ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。

- 2026-10-08T08:47:00Z — U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。

- 2026-10-08T08:35:00Z — ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。
- 2026-10-08T08:18:25Z — U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。
- 2026-10-08T07:58:58Z — U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。

- 2026-10-08T01:42:09Z — U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions

- Step39〜41：Docker配布QEMUbinaryの独自patchや内部branchはdebugger未観測。公開10.2.3sourceと実測は一致するが同一binary sourceの完全証明とはしない。production wasm fullruntime/native依存解消と本番launcher/共有stdheap/入れ子Workerは後続実装の課題で、この検証計画では新規本番launcherを実装しない。
- 2026-10-08T06:28:40Z — U2 local LSan minimal-C failure directly occurs at clone tracer-thread creation with EINVAL; QEMU x86_64 binfmt and ptrace ENOSYS were observed under the same local image/capabilities. Exact rejected clone flag and QEMU-version behavior remain unverified; native CI succeeded using a separately identified rust:1-bookworm digest, so do not present the environments as a controlled identical-image comparison.
- 2026-10-08 — U2 traceabilityは実ASan GAP NFR2/NFR2.2/NFR3/NFR3.4の4件だけでFAIL、missing IDs/invalid entries/targets/orphans0。required-sectionsはPASS。現在sourceの各600秒ASanは未検証、古い1276258/1706799runs・旧coverageを流用しない。80%/30秒/nightly2026-10-01/各600秒/custom順序を維持し、全produces・manifest・証拠書込をレビュー前に終了、sourceと記録を固定して親担当へ引き渡す。
- 2026-10-08 — Safari報告更新後のcanonical native verifierはdocs/reports/wasm-threads.md差分でexit1。補助byte比較162files中160一致、差分は既知非ビルド.gitignoreと承認済みSafari文書だけ。runtime/source/test/build/CI bytesは不変だが正式検証成功へ読み替えない。Step35/36完了、Step37の正式検証・独立レビュー・完了確認は未完了。全記録書込を独立レビュー前に終了し親担当へ引き渡す。
- 2026-10-08 — U1限定required-sectionsはPASS/H2=7、traceabilityは全requirements fallback60FR/NFR不足でFAIL。47IDs/47対応・invalid entries/targets・GAP/orphan0を保持し、sensor FAILをPASSへ読み替えず親担当へ引き渡す。U1各600秒fuzz/wasm/実Safariは未検証。全成果物書込と本追記を独立レビュー前に終了し、正式結果記録まで書込・SCM snapshotを停止する。
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->

## Tradeoffs

- 2026-10-07T19:07:40.982475+00:00 — ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。

## Interpretations

- 2026-10-07T21:57:34.773869+00:00 — REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。

- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。
## U7 再開の観測（2026-10-08）

- U7のhuman Request Changesを受け、Windows raceの証拠表現とsummary見出しだけを修正した。Windowsは同名test登録成功とUnix専用本体実行を分け、並行root逃走を未検証と明記した。
- required-sections実経路 .codex/tools/aidlc-sensor-required-sections.tsでPASS、H2=2、findings0、exit0。誤った .codex/sensors/経路のModule not found/exit1も検証ログに保持した。
- 35claims/88ファイルの保存CI hash一致と担当17IDs、FR9.3/NFR2/NFR3 GAPを再確認。4producesとmanifestを今回summary後に保存し、製品・測定値・SCMを変更していない。
- 承認後のsummary本文変更はprotected receiptを失効させた。今後はsummary本文をPlan Approval前に確定し、承認後は所定のAnswer記録だけを行う。

- U7の35 source claimsを展開した88ファイルは署名付きCI 4d52be0aと全一致。旧snapshotとの差は5ファイルで、Host/VFS/Runtime等の依存変更により旧ASanとU7限定89.79%は現行合格証拠にしない。
- raw実機Linuxログでdiff_u7 63親case、U7内部81（CLI6/Host11/Kernel16/Runtime8/VFS40）を確認。Windows内部80はcfg差。CLI command全6のうちU7専用2であり、内部81に全6を二重加算しない。
- U7担当17IDへtraceabilityを限定し、FR9.3/NFR2/NFR3 GAPを保持する。4成果物、strict manifest、current evidence、88ファイルsnapshot、raw5ログ/CI2JSONとテスト名集計を今回確認後に保存した。

- U4の独立再レビューは新規指摘なしで正式登録され、checkpoint verifyがexit 0、human Approveが記録された。
- U7はWindows手順と過去のcoverage/ASanの適用範囲を修復するSteps 15–17として再計画した。製品変更は計画しない。
- U7 Plan Approval後のjj記録コミットでprotected receiptが失効した。現在の作業状態で再承認を取り直し、verify execution_allowed:true、summary Looks correct、begin成功を確認した。承認・レビューから完了までSCM操作を行わない。
- 全体CI coverageをU7限定coverageへ転用せず、過去のASanは全依存の一致を確認し、不一致ならGAPを保持する。

## Open questions
- 2026-10-08T13:06:33.169132+00:00 — U3 Step2 inventory completeness is unresolved: pinned probe/aube build receipts exist, but runtime inventory is incomplete and static SIMD/x87 classification is not a complete SSE inventory. Product semantics remain unchanged pending evidence-backed scope decision.

## Interpretations
- 2026-10-08T13:11:35.139319+00:00 — User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation; preserve approval contract and existing Unit artifacts.

## Open questions
- 2026-10-08T14:02:27.219381+00:00 — U3 additional investigation obtained finite native DBI completion for probe8 checks/aube4 operations and verified191 raw hashes. Oldaube binary remains unreproduced; controlled date is insufficient and oldprimer mtime is missing. Human must choose reproducible aube repin and observed crypto/CPUID scope before product implementation.

## 2026-10-08T15:12:18.752784+00:00 — U3固定対象とnative観測

初回独立build run37791775873は全入力比較を通過したがbinary SHA不一致。root独立byte比較で31,471,776 bytes中21 bytes差（offset640–659と26012621）、C時刻14:25:42/14:25:12を確認。SOURCE_DATE_EPOCH=1791158400の再試行run37794036866は全job成功。rootが保存binary2本を比較しexact_equal=true、SHA d009267fa265ed854d14bdcbe99deb598d21ff79a385669a6f2ac0f5c329c8ccを確認。先行Unit25成果物はサイズ/SHA変更なし。新対象4fixture DBI run37795989102成功（raw stderr時間差保持）。初回native oracle37797799132 job成功、leadは4,416行+CPUID12行/shape/feature条件を検証。これらはエミュレータ意味論のPASSではない。Step3境界観測拡張中。


## U1 shared SHA prerequisite repair — current authorized execution

Human permitted preserving originals and appending only plan/instructions Step41–43. Other23 artifact preservation remains required. Current PlanApproval verified execution_allowed true; SummaryConfirmation b37a5f1a9f53ee7a7ea4831ec0d02611dd7016707ecc404261391529a256c078 recorded before generation. Original2 backups and byte-prefix proof retained under intent verification/u1-sha-prerequisite-plan-baseline. Developer executing shared SHA alignment repair, precise six observed AMD-profile divergences, both80%coverage gates and changed-source verification. Previous realSafari21 success belongs to pre-fix module and will not replace final-module verification. No implementation or CI success claimed yet.


## Current SHA prerequisite verification results before independent review

Developer reported SHA6 contract tests Red0/6, Green6/6; 23576 normal plus1162 fault raw comparisons with exactly6 observedAMD divergences classified; new Intel a06d1 observed all6 strict#GP/state unchanged and full strictreplay. Final signed head11195ad000415af6b320b8e0e4b64a46265fdb61 Verified. CI37858171955 all8jobs success, workspace93.13%, U1 93.23%, U9 82.73%. Root independently counted final-u3-lcov/u3-coverage.lcov exact9CPU/Decoderfiles2737lines2225covered81.29338691998538%; unrelated downstream74.78%display includes CLI outside scopedreport, retained. Final Node/realSafari27.0.1 21/21 pass; seven finalASan/LSan targets601s/exit0 and179sourcebeforeaftercurrentmatch reported. PriorWindows errno5 failure retained unresolvedcause, finalWindows unchangedHostfixture pass. U1 originalmanifest kept perhuman23artifactpreservation; supplementalchangeinventory needed because u3_tests/diff_u3/oraclepaths not in preservedmanifest. FormalUnit completion notclaimed. Developerfinalevidencefreeze pending; rootreview follows when stopped.
