# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:285194a531299dbca99507b2b38f4eca3e55599a274d3d3389a97b9bc412e4f8 -->

- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:26340bb8ac959d9cee4cca7e0ab4c992ee0f37a096b48a7296b66fa5ba552c22 -->

- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:23a124f976b5bdf667dc3bbeecfe978548604009a384d1075a5f144e8c6b04ef -->

- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:103813e0718b13cb5739d5c0b20460b769a604d55d09e864d857315601cb6616 -->

- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:98db3e4218f1afb89e341c2b1c719855f15757e3faa539708a197ea3b2ecbb5d -->

- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:f2234a671c0216acfb63b4cfe3e90aa5c2972436d70207a09558cec402a5275d -->

- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:094c8ba52946c88b0a8cbd821a62c5882d82649460e5ae7fd46dbc84ce5e67e0 -->

- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:cb7f200a7ff9180f285b097cc5fda44ad9a45acccb3c8d9dccff1bbca0d4ce66 -->

- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:18f42b9a329c58602decfcde4a9e94bf6bb55fd4890797fb5d7f78ae5727c296 -->

- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:8cc6ecfaddb3d27a688ef0575232fc7b4975564dd8c4228fa515ba0d1f6000c9 -->

- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:ff027867e1ca80d3eefd1dc788acd17a5809557cbc01f8982d22d335e2e94b6b -->

- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:40fc26c91862f2b3fe4e71f2599e9048aef1c35312420021c5e3624f0b47888e -->

- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:28e1f00d35c9c30f8421f8cc12caab5e03ca130d5d705b723c15b7e3195fdba0 -->

- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:a3e547ef56cd4dd112661d2ed8c47fd09701ce1c0e6aa3307f1a9aaa059fd642 -->

- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:cdf350691531f6f612f4ac5b52f6cb1492cda528cc1c0cb5706e174e409e9016 -->

- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:eb1b0c709abfc1ae010a6a184e012f2879bda227d29957e408e5f6f43d397379 -->

- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:509ad493281bf9a764806b36e1ed2bfe24174f648944ab044fed55dee239b35c -->

- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:b866f91dcc9d2f009461af6352a31f132bb0db192b2b6b028927f4f0852671aa -->

- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:5aab5c07bdbc9ec8f764384588a47655c50637e7b31c324151d4ed2767ade909 -->

- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:21a1d95e01879d268f4e20b19b3ac5337b5fb8b2e61e96f654d923b85af00c77 -->

- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:d49ebb15ba8851c242a8145b83e44683387eb2f2278fea609d681b254807d5ce -->

- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:e3ce011f63aeeca5bedc4a14a2ce15160c623e18cf34573e5cc9f63cdf730d31 -->

- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:526c8b764e3ad36fc0f9486f9b6a88cd285e68b7c7007f2a99f1e466866ba9b1 -->

- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:01ee5163fa4adccd14f53539587284d7a611c0babf7f2b607518771da1176850 -->

- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:e5be2cd7a48b255cd806bf4d7f34e8eed2fff901683b2b6ae6888b1ffbc1c929 -->

- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:1a5290bee68291a1d34b5a8b66d1eb2f937227a800ab39041962a76bab77c9eb -->

- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:472b2b723b2c807123601f4dead9133ce1e4a460b5fb4e8dcf8de7babd76d33a -->

- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:de1fc4d331ccb94fae83035ac7bff5ee10199e5e5c00ae62011982306645ffb6 -->

- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:98532439eca402556701461e08b238ffc74690b745d73cd47f18177a28fece3e -->

- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:df1a8bd3ad2fed86897166f65cc125abeb23310c0dd3c75c02ba9c9aae6e36c8 -->

- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:8d83522ce5b35f048ab05eedd8121176eebc6da3315899885332a9098dc46659 -->

- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:e9695d202791885f8726e2ad9e8b87d6d61efc6105099b42a1ac7246d14cb618 -->

- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:1f1ee388fcef73ea90f75a9871f7a1a52b8d7cc34ba5f8c4e72ee85cc0b5f4d9 -->

- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:e5358a60e0385fee8d2c6df34f9080a4ff363db3e6219c55b8bc661452695cb9 -->

- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:ea3b4b336d5fdabd918eae2880c142ef0eb41055ef7f2d372a21d12853ff9fbd -->

- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:6512061ecdfa44e55ed9913065afebf413f8680b85f62880869acaff1f032f76 -->

- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:72799ee5fccde188251ba89407ad3cce3b09d88b10dfc6edc931739a22ba9ac5 -->

- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:3a12972ef8e989db7dea35ec944a6c7a66c75ab6854cdc310455cae546857cae -->

- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11) <!-- cid:261004-rust-blink-port:code-generation:8052d1d29862636960e8cabdb9ba25ff9be6ce3bc9b2b49f4ce10b9b43e9add2 -->

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent and cannot be changed from chat. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER ゲストの syscall を番号のままホストに渡す（面談 Q11 A）。 (affirmed 2026-10-04)

- NEVER 他のプロジェクト（jart/blink、nixvm など）のコードを写す。動作と設計を参考にするだけにする（実現性の工程 Q3、制約 C-T3）。 (affirmed 2026-10-04)

- NEVER Blink ベースの webix・portabox の系列と、その元になった Blink のフォーク `lanmower/blink` を、参照・依存・取得・実行する（履歴にマルウェアがあった。制約 C-R2、背景資料 `knowledge/documents/research/cheerpx-oss.md`）。 (affirmed 2026-10-04)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS 外部のクレートや道具を使うときは、著作権・ライセンスに問題がないことを確かめ、著作権やライセンスの問題に関わるものは自作する（面談 Q1）。 (affirmed 2026-10-04)

- ALWAYS 既存のクレートや道具に不具合や上手くいかないところがあれば、その部分は自作する（面談 Q1・Q14）。 (affirmed 2026-10-04)

- ALWAYS ゲストが実装していない syscall を呼んだら `ENOSYS` を返す。実装した syscall だけを明示的に扱う（面談 Q11 A）。 (affirmed 2026-10-04)

- ALWAYS ゲストにホストのファイルを見せる方式でも、`..` やシンボリックリンクで、指定したディレクトリの外へ出られないようにする（面談 Q11 B）。 (affirmed 2026-10-04)

- ALWAYS ゲストからどんな入力（命令のバイト列、メモリ、syscall の引数、ELF の中身）が来ても、エミュレータが panic せず、未定義動作にもならないようにし、ファジングで確かめる（面談 Q11 C）。 (affirmed 2026-10-04)

- ALWAYS GitHub Actions の action はコミットの SHA で固定する（面談 Q11 D）。 (affirmed 2026-10-04)

- ALWAYS Rust のクレートの依存は crates.io からだけ取る。ワークスペースの中のクレートを除き、git などほかの取得元からの依存は入れない（面談 Q11 D）。 (affirmed 2026-10-04)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- 承認済みの計画（rust-blink-port）は JIT を範囲外としていたが、Q8 でユーザーが JIT を範囲に含めた。以降の工程（scope-definition など）で JIT の段階分けを扱う必要がある (learned 2026-10-04) <!-- cid:261004-rust-blink-port:intent-capture:4840a2a8b12d2b7e282f64ceb1b717b9d8f28ed863646294933554af21f84eb7 -->
- Q1（すべて自作）と Q2（iced-x86 を使う）が食い違っていたので、追加質問 Q9 で確かめた。回答は B で、デコーダも自作することになり、Q2 の回答を C に変えた (learned 2026-10-04) <!-- cid:261004-rust-blink-port:feasibility:0bf80174637020827e2e7719a34f5c71cf7ba3097b814e8ed7a3596aea047483 -->
- Q5 で選ばれなかった項目（ネイティブ向け JIT、動的リンクのバイナリ）は、範囲外とも必須とも扱わない。ネイティブ向け JIT は意図書どおり「後で考える」のまま、動的リンクは成功条件に含めない (learned 2026-10-04) <!-- cid:261004-rust-blink-port:scope-definition:efeec5b7b1cbf3db1b266b738b0e6684ee2bd7a6bd5f5ac64cf536073b64dede -->
- Q1 の B（段階 1 の設計時に wasm のスレッドを小さく確かめる）は、範囲の定義で選んだ番号順を変えるものではなく、設計の中での確認として扱った。段階 3 まで待たずに R2 の兆しをつかむため (learned 2026-10-04) <!-- cid:261004-rust-blink-port:approval-handoff:f6acd2bc4b3eb3465832195d4dc201b9c8e4ebeba7e8eb960d209e987b37bc98 -->
- 面談の途中で、ユーザーが技術選定の方針を変えた（外部のものは基本的に使ってよい。著作権・ライセンスに関わるもの、不具合があるものは自作）。Q1 と Q13 の回答をこの方針に置き換え、Q14 でデコーダを iced-x86 などの既存のものに戻した。実現性の工程の決定 D10 と制約 C-T2 はこの方針で上書きされる (learned 2026-10-04) <!-- cid:261004-rust-blink-port:practices-discovery:cbff2b9477367e95ba8ac6bf4ed95edee323a8f90e449253f5993bec190c8236 -->
- WSJF の点数では U12（macOS）が U13（Windows）より上だったが、Q1 の「Windows を先に」と Q6 の心配を優先して U11・U13 を先にした。U5 の前の U2 は、依存関係の文書にない依存（原子的な命令）を作業単位のレビュー指摘から加えた (learned 2026-10-04) <!-- cid:261004-rust-blink-port:delivery-planning:5545184ba131e6ef0f9402a37e52ad440e65943335fcf6f91f88b5633f0b298d -->
- 人が承認・採用のときに残すと決めたMinorの指摘（U1 Step72の回帰2件、U14 Step46の記録3件、U15 Step12の記録3件、入口v3の記録4件）は、次にそのUnitの記録や確認コマンドの入口を更新するときにまとめて直す。直すまでの間は、各Unitの記録やpending-minor-fixes.mdに残しておく。 (learned 2026-10-18) <!-- cid:261004-rust-blink-port:code-generation:72a939018eadcc8db7c312c9dc765379c95ef58421a1e2a4216269fdc4666933 -->
- U14 Loop-back 1：試算で確実に速くなるのは整数SSE群だけ（約−13%〜−7%）で、GPRは遅くなり、byte比較は向きが決まらなかったため、人が「SSEだけ先に」を選び、GPRとbyte比較の変換（Step35・36）は行わなかった。整数SSEの変換の後、FR8.3は1ceae86c・bb197e04・a54315f9でp=1/1024で合格した。 (learned 2026-10-18) <!-- cid:261004-rust-blink-port:code-generation:1fdc35894484d53656c790468fdff21b4f72265dfff58eac430d37e9f707b5fe -->
- CI の workflow の変更は、次の製品の変更（NFR7 の Safari の直しと残している Minor）と一緒にまとめて行う。`.github/workflows/` の一部は正式な確認コマンドが bytes を固定しており、変えるたびに入口の作り直しと CI 一式が要るため（CI Pipeline の Q1 の A）。 (learned 2026-10-18) <!-- cid:261004-rust-blink-port:ci-pipeline:185ff505fcf5b3a151eb6db60f1afafdeb8c7a46dd12e81f184e470b6c12ba5e -->
- 正式な確認コマンドは、e3c29d1d を起点にした入口 `entry-e3c29d1d/entry-c.py`（人が 2026-10-18 に採用）。新しい head では入口の層を重ねず、binding（binding-e04 など）だけを書き直して採用を伺う。入口も binding も上書きせず、直すときは新しい版を作る。v1〜v4 の入口は履歴で、bytes だけを固定する。 (learned 2026-10-18) <!-- cid:261004-rust-blink-port:code-generation:9590516b8920663aca80ef116254b6e73f7d52d267184ccf130ad1b9f937aab8 -->
