# U4 syscall 対応表

固定取得対象は隔離 rebuild の引継ぎreceiptをコピーした `inventory/upstream-build-receipt.json` と同じartifact。receiptは原記録を変更せず保持し、U4でbinary hashを再観測した。コピーを新しいbuild実行とは扱わない。

|対象|SHA256|静的 syscall 位置数|native 操作|
|---|---|---:|---|
|probe|15e90407b6cc2dc8389048805475fb9c7b11d3e10f89c1da0d52dad7b1c99292|109|引数なし、exit0、8 checks PASS|
|aube|ff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a|258|`--version`、exit0、2.6.1 linux-x64|

原取得 source/lock/compiler/image/build arguments は上記 receipt と source snapshot に固定済み。aube revision は `bd94e42f54d3b5e3dd102716b7197f316cb5f4ed`、probe は `d0bc647364c7cf48cd4cfd96af8ad863194636fe` と dirty snapshot。U4 では再buildしていない。static callsite は `objdump -d` の syscall 位置を全列挙した。両 artifact は stripped、`nm` は no symbols だったので位置数を syscall 番号数や到達経路数とは扱わない。

`strace -f -qq` の選択 native 操作で観測した U4 syscall は brk4、mmap92、mprotect46、munmap75、rt_sigaction10、rt_sigprocmask100、sigaltstack70（両操作合計）。この有限 trace はすべての任意入力経路を保証しない。clock/sleep はこの sample では観測していない。VDSO が理由という説明は未検証。時計・待機 ABI は専用 native fixture で独立検証する。probe/aube 自体の emulator 完走は U10 の確認事項で、native PASS を emulator PASS と記載しない。

|syscall/ABI|U4 実装範囲|native case / 内部根拠|
|---|---|---|
|mmap9|anonymous private/shared、length round、hint、FIXED、NOREPLACE、checked offset/range|`memory.c` CASE0/1/2/3/7/9|
|mprotect10|page alignment、PROT_SEM、holeまでのprefix適用、code generation更新|CASE4/8、MMU partial_protect test|
|munmap11 / brk12|hole、rounding、shrink/regrow、失敗時current brk|CASE5/6、MMU/Kernel memory tests|
|clock_gettime228|REALTIME0 / MONOTONIC1、16byte timespec、bad pointer/id|`time.c` CASE0/1/2、Host fake clock|
|nanosleep35 / clock_nanosleep230|relative/absolute、checked timespec、remaining、EINTR、巨大durationclamp|CASE3〜7、`signals.c` CASE16/17/19|
|rt_sigaction13 / rt_sigprocmask14|32byte action、8byte mask、unblockable、default/ignore、coalescing|`signals.c` CASE0〜4/6/7|
|sigaltstack131|24byte stack、ONSTACK/disable、nested frame|CASE5、Kernel nested_altstack|
|rt_sigreturn15|checked ucontext/siginfo/fpstate、relocated frame、modified return、invalid context|CASE8〜15/18/20〜22、Kernel signal tests|
|kill62 / tkill200 / tgkill234|単一guest threadへの配送、番号/対象検査、標準coalescing/RT queue|CASE1〜7、Runtime/Kernel tests|
|setitimer38|ITIMER_REAL、virtual timer、one-shot/interval、NULL disarm|CASE16/17/19、Kernel periodic_timer|
|write1 interruption|転送前 EINTR の SA_RESTART frame RAX/RIP、partial write非再開|native-only `write-restart-oracle.c`、Kernel restart test、既存短いwrite回帰|

file-backed mmap は U7、clone/futex と複数 guest thread は U5。単一threadの現在 mask は Kernel が所有し、U5 で thread state に移す必要がある。その他 clock id / timer class と全任意 signal 拡張は未検証。単一process SIGSTOP/TSTPのstop/continue、停止中kill、RT2048件backlog後のkill/continueはnative-only observerの7mode、Kernel/Runtime内部ケースにより検証する。Runtimeは停止中CPUを実行せず、Host waitを10msで区切り、signal inboxとkillにより起床できる。生産RT queueに任意quotaは設けない。

guest compiler は `musl-gcc` wrapper、観測 version は `x86_64-linux-gnu-gcc (Debian 12.2.0-14+deb12u1) 12.2.0`。fixture の build flags は `tests/guests/u4/build.sh` に明記し、signal observer は `-mgeneral-regs-only` で未実装 SSE 命令に依存しない。
