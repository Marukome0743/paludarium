# U4 Linux x86-64 signal ABI

native `signals.c` CASE14 は ucontext の mcontext offset40、sigmask296、stack16、siginfo addr16、mcontext fpregs184、mcontext size256、RSP/RIP/EFL index15/16/17 を実行時に出力する。frame のreturn pointer8byteを含め checked codec が使用する。handler RSP は16byte境界+8、red zone128byteを避け、全frame書込permissionを先に検査する。FP領域は64byte境界、保存済み XMM/MXCSR の roundtripを内部テストする。

fault observer は siginfo number/code/addr、ucontext RIP、trap/error/CR2、保持R12、定義済みflags mask `0xcd5` を比較する。native例外配送で設定されるRF等を整数flags差分として扱わない。CASE8/9/10/11/12の native/emulated stdout全量を比較する。execute resident page の PF error は21、virgin READ/PROT_NONE writeは6を nativeで観測し、MMU/C1 の immutable `fetch/mapped/present` metadataから組み立てる。residentは成功したread/fetchのlogical zero-page entryも含み、permission変更後の推測で作らない。

rt_sigreturnは固定保存frameの位置に限定せず、guest RSP-8からchecked headerを読む。canonical RIP/RSP、selectors、FP pointer/permission/MXCSRを検査し、privileged flags を guest編集で変更しない。通常 syscall returnで復元RAXを上書きしない。Linux sigcontextに FS/GS base fields はないため現在のthread baseを保持する。FS/GSをhandler内で変更した場合の追加native比較は未検証。

REPE/REPNEのcontinuationはhandlerへ持ち込まず、復元RIP/flags/count/indexが一致した場合だけ保存済みcontextを戻す。内部 `u4_signal_rep_budget_context_roundtrip` と `u4_signal_changed_rep_return_discards_continuation` は4097比較を1CPUbudgetで区切り、この条件を検査する。nested altstack、frame書込失敗の非破壊性、mask restore、malformed return、blocked pending、coalescingはKernel内部テストに含む。

native-only write oracleはblocking pipe+forkでSIGUSR1を注入し、SA_RESTART無しは frame RAX=-4/RIP=syscall後、ありはRAX=1/RIP=syscall位置と観測した。fixtureのfork/pipeはU4 guest実装を意味しない。Kernelは転送前write EINTRだけ再開contextを作る。nanosleepはSA_RESTARTでもEINTR、relative remainingを返しabsolute remainingは変更しない。

## pending target の比較条件

検証済み: native Process pending36→35はdefault35/handler35→36。同一Process queue kill→sigqueueはsi_code0→-1。同一Thread queue tkill→rt_tgsigqueueinfoは-6→-1。後二者のSI_QUEUEはnative観測専用で、ゲストsyscall対応の追加ではない。

kill35→tkill/tgkill36ではThread36がProcess35より先。同番号35でもThread -6→Process0。standard10のProcess/Thread各2回は各queue内でcoalesceし、Thread -6→Process0の2配送。live u4_realtime_order_native_oracleのmodes4/5/6/7でnativeと公開Kernelを比較する。PendingSignalのtyped targetはsi_code値から推測せず生成経路で付ける。SIGKILL最優先を保ち、mask/stop適格性と各queueの番号/FIFO選択を配送・restart previewで共有する。
