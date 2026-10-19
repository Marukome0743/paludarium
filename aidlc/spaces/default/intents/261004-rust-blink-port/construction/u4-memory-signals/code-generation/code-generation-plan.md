# U4 メモリ・時刻・シグナルのコード生成計画

## 今回の計画：Step38（Build and TestのLoop-back 1：Testing Contractの更新と再確認）

2026-10-17。Build and TestのLoop-back 1で、U14の整数SSEのJIT（署名head 1ceae86c）とU1・U2の正式確認の更新を行った。その途中の記録の誤り（Code Generationの段階全体へのRequest Changes）で、Code Generationが作り直しになり、各Unitを順に確かめ直している。U4の担当のsourceは今回の変更に含まれない（変わったのはU14のJIT・wasm・テスト、U2のabi.rs、mise.toml）。この計画の「## Testing Contract」は、memory（project.mdの学び）の更新で古くなっていたため、`aidlc engine testing-posture render` の出力に置き換えた（contract `sha256:7ff27a24…`）。テストの方針そのもの（Methodology custom、Ordering、Standard、80%下限など）は変わらず、project層の学びが足されただけである。

- [ ] Step 38 — 製品・テスト・記録は変えない。今の正式確認コマンド（`construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py`）でU4のcheckpointを確かめる。独立再レビューで、U4の記録が今のsourceと合っていることを確かめる。Steps34〜37の結果（各600秒ASan/LSanなど）は履歴として保持し、今回の新しい実行とは数えない（NFR3、NFR9）。

## 前回の計画（Steps34〜37）

前回の実行対象はSteps34〜37。人の「現行ASan/LSanを実行する」に対応する。Steps1〜33は履歴として保持し、新しい計画承認と内容確認後に実行する。

## Summary

- Builds: Step38。製品は変えない。計画の古くなったTesting Contractを今の内容（`sha256:7ff27a24…`、方針は同じでproject層の学びが足されただけ）に置き換え、今の正式確認コマンドでU4を確かめ直す。
- Touches: この計画のTesting ContractとStep38の節だけ。製品・テスト・ほかの記録は変えない。
- Tests: 新しいテストの実行はない。独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpoint。Steps34〜37の結果は履歴として保持する。

## 前回のSummary（Steps34〜37）

- Builds: 既存U4のメモリ・時刻・シグナル実装を保持し、現在の担当ソースと検証証拠の対応を再確認する。
- Touches: U4の計画・検査手順・成果物・照合記録。製品不一致が見つかれば具体的な最小修正案を提示する。
- Tests: 現行ソースでsyscall_args/mmu_ops各600秒ASan/LSan、全関連ソースの一致、正式sensor、独立レビュー、承認済みcheckpoint検査。strict guard、80%下限、入力30秒制限を維持する。

## 今回の計画：Steps34〜37（現行ASan/LSan）

34. [ ] 現行製品・fuzz・lock・suppression全体のバイトを固定し、7eb1819fとの差分を確認する。既存隔離jj workspaceと実機x86-64 Linuxのfork CIを再利用し、診断workflowだけで2対象を検証する。使用ツールの最新リリースを確認し、診断環境へ最新版を固定して版・取得根拠・互換性を記録する。製品設定・lockは変更しない。署名付きjj push後にVerifiedとCI headを確認する。PR・mergeは作成しない（FR9.3、NFR2/3/8/9）。
35. [ ] 同一現行ソースでsyscall_args/mmu_opsを独立jobにより各600秒ASan/LSan実行する。seed1、timeout30、rss2048、既存max_len既定、detect_leaks=1、既存LSan suppressionを保持する。最小ASan終了診断、開始終了・非ゼロruns・exit、生ログ・環境版・binary hash/symbols・corpus/crash・source before/afterを常時保存する。短縮・異常終了・source差分・LSan無効化を合格としない（FR9.3、NFR2.2/3.4/7.1）。
36. [ ] CI成果物と現行全関連ソースの一致を独立確認し、成功した実測範囲のみU4のASan GAPを更新する。製品不具合は再現証拠と最小修正案を提示する。4成果物・manifest・検証記録を保存し正式sensorを再実行する。過去の成功、今回の有限実行、任意入力の未検証を区別する（全割当FR/BR/NFR）。
37. [ ] 書き込みを停止して新しい独立レビューを取得し、既存承認済みcanonical確認を実行する。人の完了承認後に次Unitへの遷移を確認する。並行セッションID競合の完全解消は別の未検証項目として保持する。strict guard、80%下限、30秒制限、Testing Contractを維持する（NFR3/7/9）。

## 履歴の計画：Steps31〜33（全Unitやり直し後）

31. [ ] 新しい内容確認後に共有要件・C1/C2/C4/C5/C8/C10とU4 manifestの担当範囲を確認し、現行bytesを検証対象コミット7eb1819f52acede33e83775374dd4ee93edf643bへ照合する。旧178da99e以前のCI・fuzz証拠は履歴とし、再利用条件と未検証を明記する。メモリ・時刻・シグナルを再実装しない（FR2.2/FR2.9/FR9.1/FR9.3、NFR1/2/3/7/9）。
32. [ ] 今回の内容確認のもとで4成果物とsource-manifestを保存し、正式required-sections/traceability検査を実行する。担当要件と後続UnitのDeferredを保持し、ASan等の過去結果を現行全入力の保証や今回の新実行へ読み替えない。不一致があれば限定修正案を提示する（全割当FR/BR/NFR）。
33. [ ] 全書き込みを停止して新しい独立レビューを取得し、承認済み確認コマンドを標準checkpointで実行する。人の完了承認後に次Unitへの遷移を確認する。今回の経路の成功と並行セッションのID競合の完全解消を区別する。strict guard、80%下限、30秒watchdog、各600秒fuzz、比較mask、Testing Contractを維持する（NFR3.4/NFR7.1/NFR9.1）。

## Sources

## 履歴の指摘修正：Steps25〜30

今回の実行対象はSteps25〜30。Steps1〜24は当時の計画・実行履歴として保持する。ユーザーの「3の両方です。」に基づきU4 R-01の証拠時点表記を修正し、「未検証のASan項目を維持 これを検証して欲しいです。」に基づきsyscall_args/mmu_opsの実機検証を追加する。製品コード、既存テストと品質下限、U1/U2の承認済み成果物を保持する。U9の公開型修正は後続Unitで続ける。

25. [ ] U4 manifest107claimsを現在sourceと署名済み178da99e88d1aea242c5141207887767a69fa670へ照合し、現行CIのU4差分・内部テスト・3OS/lint/依存/coverage80%の該当ログを確認する。旧4d52 snapshot一致と旧CI数値をSteps22〜24当時の履歴へ限定し、af9bと178da99eの証拠を時点別に区別する。今回の照合を新製品テスト実行と数えない（FR2.2/2.9/9.1、NFR1/3/7/8/9）。
26. [ ] code-summary/evidence-currentの現行表記を修正し、対応表・required-sectionsの限定sensorと承認済みcanonical検査の結果を保存する。syscall_args/mmu_ops各600秒ASan GAPはSteps28〜30の実測結果を得るまで保持し、U2の4対象ASanやwasm14ケースをU4全体の合格へ転用しない。4成果物とmanifestを内容確認後に保存する（FR9.3、NFR2/3、全割当FR/NFR）。
27. [ ] Steps28〜30を含む全検証後に記録・出力専用diaryをレビュー前に確定し、全書込とjj snapshotを停止して独立レビューとUnit完了確認を更新する。新製品不具合や証拠不足が判明した場合は具体的な最小対応を提示する。80%/30秒/固定nightly/各600秒/masks/custom順序を保持する（NFR3/9）。

28. [ ] 署名済み178da99eを基準に既存isolated jj workspaceを再利用し、診断専用bookmarkのfork CIへsyscall_args/mmu_opsだけの診断workflowを追加する。現在checkoutの製品・CI・U1/U2成果物は変更しない。既存U2実機sanitizer workflowと同じx86-64 Linux/container、nightly-2026-10-01、cargo-fuzz0.13.2、LSan suppression、detect_leaks=1を維持し、最小ASan終了診断と環境版・source before hashを保存する。jj pushはhost権限で署名し、connectorでVerifiedとCI headを確認する。PR/mergeは行わない（NFR2/3/8/9）。
29. [ ] 同じ固定sourceのsyscall_argsとmmu_opsを実機Linuxの独立jobで各600秒ASan/LSan、seed1、timeout30、rss2048、既存max_len既定により実行する。fail-fast:false、raw logs/exit/開始終了/runs/環境・sanitizer symbols/binaryhash/source before-after/seed/corpus/crashを成功失敗にかかわらず保存する。既存suppressionを増やさずLSanを無効化せず、0件・短縮・異常終了を合格にしない。製品不具合は再現証拠を提示し、今回無断で製品修正しない（FR9.3、NFR2.2/3.4/7.1）。
30. [ ] fork CI成果物を取得し、全U4関連source・lock・fuzz設定・suppressionと現在bytesの一致、署名、target別exit・実行時間を独立確認する。実測が成功した対象だけGAPを更新し、失敗は原因・再現手順を残す。診断workflowの変更を製品source一致から明示的に分離し、証拠をU4 verificationへ保存する。Steps26/27の記録・sensor・独立レビュー・canonical完了確認へ戻り、任意入力や全UBの保証へ拡張しない（FR9.3、NFR2/3/9）。

- `inception/units-generation/unit-of-work.md` U4、`unit-of-work-story-map.md`：ストーリー工程を省略しているため FR2.2・FR2.9 を計画ステップへ対応させる。
- `inception/requirements-analysis/requirements.md` FR1.5、FR2.1、FR2.2、FR2.9、FR9.1、FR9.3、NFR1〜9。
- `inception/contract-design/contract-summary.md` C1/C2/C4/C5/C8/C10：型と提供側の責任、一方向依存、内部契約変更時の全利用側更新。
- 現行 `paludarium-kernel/src/{lib.rs,syscalls.rs}` は登録・mask・altstack を保持するが配送しない。fault は終了へ変換する。`paludarium-host/src/lib.rs` の時刻・待機 API は未実装。MMU は通常アクセス・mapping・atomic の共通同期を既に持つ（source 読取によるドキュメント根拠）。
- U4 の functional-design / nfr-requirements / nfr-design / infrastructure-design ディレクトリは現在存在しない。任意入力を創作せず、共有契約・要件と native 観測で具体化する。
- 直前の U2 workspace 検証成功は引継ぎ証拠。今回 U4 の合格を意味しない。U1/U2 再実装と任意の新依存追加を行わない。

## 実装範囲と境界

U4 は anonymous memory の mmap/munmap/mprotect/brk、Rust std/tokio が必要とする clock_gettime/nanosleep/clock_nanosleep、signal action/mask/altstack、同期例外と単一ゲスト thread への配送・return を扱う。ゲスト signal は Linux x86-64 ABI とする。file-backed mmap は VFS U7 の fd/backing が未実装であり、その取得・共有ファイル機能を先取りしない。native syscall inventory で U4 必須と判明した追加形は範囲内で回収し、未対応必須形を完了扱いしない。clone/futex は U5、SSE 実行は U3、wasm 実装は U11、JIT は U14。

Kernel が CpuState と signal 状態を所有し、Cpu は Kernel/Host を知らない。時刻・待機は Host だけが OS に接続する。signal frame はゲストメモリへ検査付きで直列化し、ホスト構造体・ポインタを cast しない。SSE register の保存は既存 CpuState の保存であり U3 命令実装を追加しない。MMU の共通同期を維持し、Host 呼び出し・任意 callback をその lock 内で実行しない。

## Steps

1. [ ] **Runner と baseline（FR9.1、NFR1/7/9）**：承認後、既存 exact kernel test を非ゼロ件で実行して baseline を記録する。U4 専用 `diff_u4.rs` / support watchdog と guest build script を先に bootstrap し、`--list` でケース件数を検査する。最初の実行可能差分ケース以前に runner を準備する。未作成 target を現在 runnable と称さない。
2. [ ] **取得・ABI inventory（FR2.2/2.9、NFR1/8）**：U2 で固定した probe/aube の source/revision/lock/binary receipt を読み、関連 syscall の static callsite と bounded native trace を追加採取する。bin hash・command・trace 到達範囲と Linux x86-64 ABI の syscall 番号、構造体 field offset、flags/errno を `docs/u4/syscall-matrix.md` へ固定する。loader 初期化だけの trace と本体を区別し、未取得の必須 syscall/form は GAP とする。コピー元として他 project の source を使わない。
3. [ ] **memory native ケース先行（FR2.2/1.5、NFR1/2）**：`tests/guests/u4/memory.c` を用意し、毎回 native の戻り値・errno・領域内容・fault context を取得する。len 0/overflow/非整列、hint、MAP_FIXED replacement、NOREPLACE overlap と非破壊、private/shared anonymous、ページ丸め、穴を跨ぐ unmap/protect、brk grow/shrink/failure を比較する。未定義・実行依存アドレスは関係値へ正規化する。現在の emulator 不一致を修正前に保存する。
4. [ ] **memory 実装（FR2.2/1.5、NFR2/3/4/5）**：Kernel の引数検証と MMU の mapping transaction を native 観測へ合わせる。range 検証前に MAP_FIXED の旧 mapping を消さない。permission / execute fault と MAPERR/ACCERR を区別する必要があれば C1/C4 typed fault を拡張し、Cpu/Loader/Kernel/Runtime/Jit/全 test consumer を同一変更で整合させる。64-bit GuestAddr、checked conversion、lazy pages と code generation invalidation を維持する。
5. [ ] **memory 内部テスト・Green（FR2.2、NFR1/2/3）**：実装後に `paludarium-mmu/src/u4_tests.rs` 8 件以上、Kernel memory tests 8 件以上を追加する。failed transaction 不変、ページ跨ぎ permission、cache invalidation、atomic と map/protect の同期を含める。memory 差分を Green にし、観測と型の対応を記録する。
6. [ ] **clock / sleep native ケース先行（FR2.9、NFR1/7）**：`tests/guests/u4/time.c` で clock ids、timespec signed range、NULL/EFAULT、invalid tv_nsec、zero sleep、relative/absolute deadline、割込みと remaining の native 結果を取得する。時刻そのものは一致させず単位・範囲・単調性と成功/errno、remaining bounds を比較し、正規化表を作る。性能値は測らない。
7. [ ] **clock / sleep 実装と内部テスト（FR2.9、NFR2/3/7）**：C2 に typed monotonic/realtime clock と bounded/cancellable wait を追加する。NativeHost・RecordingHost・既存 mock 全実装を更新し、他層から std::time/std::thread を呼ばない。Kernel に clock_gettime/nanosleep と inventory に必要な clock_nanosleep を明示登録する。相対・絶対 deadline、overflow、EINTR/rem を扱う。Host/Kernel 各 8 件以上の内部テストを実装後に書き、fake clock の deterministic ケースと native 差分を実行する。
8. [ ] **signal ABI・配送 native ケース先行（FR2.9、NFR1/2）**：`tests/guests/u4/signals.c` と raw syscall/restorer assembly で registration/query、mask、SIGKILL/SIGSTOP 制約、SIG_DFL/SIG_IGN、SA_SIGINFO/SA_ONSTACK/SA_NODEFER/SA_RESETHAND/SA_RESTART、nested handler、blocked pending と unblock、SIGSEGV/SIGILL/SIGFPE、rt_sigreturn を観測する。siginfo の si_code/si_addr、ucontext の fault RIP/RSP/register/rflags、mask、altstack、handler 順序と return 後状態を比較する。Linux 配送由来 flags と未定義 flags は mask を根拠付きで明記する。tgkill/tkill/kill の単一 process/thread 自己配送が std/tokio またはケースに必要なら U4 の明示 dispatcher に追加する。
9. [ ] **signal frame / return 実装（FR2.9、NFR2/3/4）**：`paludarium-kernel/src/signals.rs` に checked siginfo/ucontext/rt frame codec、restorer、red zone/stack alignment、nested frame と altstack 状態を実装する。frame 全 range の permission を検査して失敗を guest fault として処理し、host panic にしない。rt_sigreturn は検証して GPR/RIP/RSP/rflags/fs/gs/SSE 状態・mask・altstack を復元する。無効 frame、noncanonical context、reserved flags と frame 改変は native 観測に合わせ、guest RAX を syscall の通常 return で上書きしない。
10. [ ] **signal 配送と wait 接続（FR2.9、NFR1/2/7）**：Kernel に process actions/thread mask/pending/synchronous fault の型と配送 checkpoint を作る。不可 block signals、標準 signal の重複、ignored/default/handler を扱う。Runtime は budget 境界と syscall/fault 前後で配送し、kill 要求を bounded wait 中にも処理する。fault RIP と U2 repeatContinuation を保存し、handler の実行 context で古い REP context を誤使用せず、return の context 変更に応じ整合させる。restartable syscall と EINTR、absolute/relative sleep remaining は native-first で確定する。MMU lock を保持して sleep しない。
11. [ ] **signal / Runtime 内部テスト・Green（FR2.9、NFR1/2/3/7）**：Kernel signal 8 件以上、Runtime 8 件以上、必要 C1 codec 5 件以上の内部テストを実装後に追加。fault context、frame 書込失敗、mask restore、nested altstack、malformed return、blocked pending、restart/EINTR、kill cancellation、REP fault handler return を含む。native signal 差分は独立ケース 12 件以上、time 6 件以上、memory 8 件以上を最低計画件数とし、inventory 必須形が増えれば追加する。ゼロ tests / skip を pass にしない。
12. [ ] **変更層の回帰・configuration（FR9.1、NFR3/7/8/9）**：U4 scoped commands と変更された shared contract consumer の既存 regression を実行し、全 workspace gate は別途一回実施する。fmt/clippy 警告 0、固定 nightly/Cargo.lock/crates.io/cargo-deny、SHA 固定 actions を維持する。CI に U4 differential target と syscall/memory fuzz を接続する。Linux workspace line coverage 80% を維持し、下げて通さない。
13. [ ] **fuzz（FR9.3、NFR2/3）**：`fuzz/fuzz_targets/syscall_args.rs` と `mmu_ops.rs` に U4 memory/time/signal frame 生成を足す。fake clock、bounded Cpu budget と wait により毎入力を有限にする。pinned nightly ASan の夜間各 600 秒予算を維持し、変更 source に対するローカル bounded run の具体結果を記録する。失敗再現・source revision と runner condition を保存し、別 project process を停止しない。
14. [ ] **成果物・manifest（全割当 FR/NFR）**：`docs/u4/{syscall-matrix.md,signal-abi.md,validation.md}` と unit の code-summary / traceability を完成させる。native expectation を固定 goldens にせず、実行時取得にする。source-manifest version 1 に変更/作成/削除した全 application-source を列挙し、generator/shell/scaffolding が書いた source も含める。build cache/生成 binary は除き、必要証拠は追跡可能な .txt で保存する。未達・未検証を GAP として残す。root に独立 review 用に固定して渡す。

## 先行attemptの復旧手順（Steps15〜18の履歴）

15. [ ] **現状・runner 確認（FR2.2/2.9、NFR1/7/9）**：共有契約、既存 U4 source manifest、native ABI/inventory、専用 diff_u4 と内部 u4_ filters を確認する。過去の未作成・43件・76件・coverage/fuzz 成功を当時の source に限定し、現在ソースの対応表を作る。既存テストの一覧と実機 CI の非ゼロ件結果で readiness を確認する。
16. [ ] **現在ソースと CI の証拠照合（FR9.1、NFR1/3/8/9）**：署名済み 4d52be0a の CI 7ジョブ・native 4ジョブと手元の application/build files を照合し、U4 差分44件、内部各層、3OS、lint、依存、coverage80% gate の該当ログを対応させる。現在 bytes が一致する証拠のみ再利用する。不足は exact unit commands で追加検証し、Docker VMM/QEMU と実機 x86-64 Linux の結果を区別する。
17. [ ] **不足と修正（FR2.2/2.9/9.3、NFR2/3/7）**：製品不具合が見つかった場合に限り、syscall/guest は実機 native 期待と修正前 Red を先に記録して最小修正、内部層は test-after で検証する。U1/U2 の承認済み source を変更する必要があれば root に返し、完了証拠を無断で変えない。現在 source と結び付かない syscall_args/mmu_ops 各600秒 ASan は未検証/GAP として残し、Build and Test で回収する。30秒watchdog・80%coverage・nightly固定・各600秒を下げない。
18. [ ] **成果物と独立レビュー（全割当FR/NFR）**：現在 source の snapshot、code-summary、traceability、厳密な version1 source-manifest を整合させる。旧 evidence/source hashes/validation は履歴として保存し、旧 fuzz を現在合格へ流用しない。全必須 ID と既存 OK target を確認し、未達は GAP。独立レビュー後は対象 source と4成果物を固定し、正式検証・完了確認へ渡す。

## 先行attemptの記録再確認手順（Steps19〜21の履歴）

19. [ ] **現在bytesと証拠の再確認（FR2.2/2.9、FR9.1、NFR1/3/7/8/9）**：既存manifest107claimsとsnapshotを現在sourceへ照合し、署名済み4d52be0aのCI7+native4jobs、内部6層76件、差分44件、3OS/lint/依存/coverageの証拠を一致範囲で再利用する。旧実行を新実行と数えず、不足時のみ既存exact commandsを使う。共有契約の責任と固定ABI/inventoryを保持する。
20. [ ] **記録最小整合（全割当FR/NFR）**：U4 code-summary/traceability/source-manifest/evidenceと必要snapshotを現在値へ整合する。現在syscall_args/mmu_ops各600秒ASan未検証のFR9.3/NFR2/NFR3 GAPを保持し、旧完走を現在PASSへ流用しない。製品不具合が見つかればrootへ返して自動的に修正範囲を広げない。U1/U2凍結成果物を保持し、80%/30秒watchdog/nightly固定/各600秒/比較maskを下げない。
21. [ ] **レビュー前固定（NFR3/9）**：親construction/code-generation/memory.mdへ読取なしheading anchored追記をレビュー依頼前に済ませ、全記録とsourceを固定してrootへ渡す。reviewrequestからterminal記録まで全workerの書込みとjj snapshot/commit操作を停止する。前回レビュー不整合の原因は未確定として扱い、独立レビューの正式記録はrootが行う。

## redo新attemptの手順（承認後のみ）

22. [ ] 現在107claims/snapshotと4d52be0a保存CI11jobs、内部76件/差分44件、3OS/lint/依存/coverage証拠を再照合する。source一致範囲で再利用し新実行と数えず、不足だけ既存exact commandsで確認する（FR2.2/2.9/9.1、NFR1/3/7/8/9）。
23. [ ] 新Summary Confirmation後に実4produces plan/unit-test-instructions/code-summary/traceabilityとsource-manifestを全保存する。正確なclaims/schemaと現在証拠を保持し、FR9.3/NFR2/NFR3の各600秒ASan GAPとwasm未検証を維持する。製品不具合はrootへ返し自動修正しない。80%/30秒/nightly固定/各600秒/masks/custom順序を保持する（全FR/NFR）。
24. [ ] 親construction/code-generation/memory.mdへ読取なしheading anchored追記をレビュー前に完了する。全書込を終え、reviewrequestからterminalまでsource/成果物とjj snapshot/commit操作を停止してrootへ渡す。旧review不整合原因は未確定として扱う（NFR3/9）。

## 先行実装の変更 paths と影響（履歴）

- `crates/paludarium-types/src/lib.rs`（必要 typed fault/errno）、`crates/paludarium-mmu/src/{lib.rs,u4_tests.rs}`（C4）。共有 C1/C4 consumers の `crates/paludarium-cpu/src/{lib.rs,exec.rs,u4_tests.rs}`、Loader/Jit の必要な match/fixture を同一変更で更新する。
- `crates/paludarium-kernel/src/{lib.rs,syscalls.rs,signals.rs,u4_tests.rs,tests.rs}`（C8）、`crates/paludarium-host/src/{lib.rs,testing.rs,u4_tests.rs}`（C2）、`crates/paludarium-runtime/src/{lib.rs,u4_tests.rs,tests.rs}`（C8/C10）。Host を実装する既存 test mock も全検索して更新する。
- `crates/paludarium-harness/tests/{diff_u4.rs,support/u4.rs}`、`tests/guests/u4/{build.sh,memory.c,time.c,signals.c,restorer.S}`、必要な `tests/guests/build.sh`、`fuzz/fuzz_targets/{syscall_args.rs,mmu_ops.rs}`、`.github/workflows/ci.yml` と fuzz workflow（現在 path を実装時に確認）、`docs/u4/*`。
- C1/C2/C4/C8 は cross-crate 影響が大きい。変更前に exact diff と consumer 一覧を確認し、U1/U2 artifacts とレビュー記録は変更しない。API/DB/UI/deployment は本 Unit に該当せず新規作成しない。公開 API が必要に変わるなら変更履歴を記録する。

## Assumptions & Open Questions

Linux x86-64 native の ABI/errno/配送観測を実装の基準とする。すべての任意 signal/clock 拡張を無制限に追加するという意味ではなく、std/tokio と固定対象の必須 inventory を取得・対応させる。現在、人に選択を求める未決 product policy はない。native 観測が共有契約・要求と両立しない場合は具体的な evidence を root に返して停止する。

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
