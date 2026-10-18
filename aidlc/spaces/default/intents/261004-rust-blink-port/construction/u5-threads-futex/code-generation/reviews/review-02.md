## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-09T13:54:48Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Unresolved |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |

> R-01 Reviewer note: 元の長時間遅延はset_timerの通知とsleepのgeneration再計算で修正された。しかし「制御通知だけではEINTRにしない」という必要条件が、通知がsleep開始前に届く順序で残る。子がsetitimer解除→共有ready=1→個別exit、親がready確認→200ms nanosleepすると、signalなしでも5/5で-4を返し4–8msで終了した。場所：crates/paludarium-kernel/src/syscalls.rs > sleep、182行のgeneration採取と213–226行の分岐。新generationを入口で既に採取すると215行はfalse、queue空でreceived=falseなので219行もfalse、既存control_wake由来のInterruptedが226行からEINTRへ落ちる。crates/paludarium-kernel/src/inbox.rs > drain（87行）が制御通知の種別を返さずackする。元の停止は解消したためCriticalからMajorに下げる。必要作業：generation差分だけに頼らずownerが受け取った制御通知の種別も使い、実signal・group終了以外の通知はdeadline再計算へ進める。Host待機の前に解除通知が届く順序を同期した単体テストとnative-first有限ゲストへ追加する。

> R-02 Reviewer note: thread_syscallがtimeoutなしWAIT/WAIT_BITSETのSA_RESTART handler frame作成前にRIP/RAXを再開値へ戻す。追加native30/31（wake）、34/35（handler値変更後の再比較）、32/33（SA_RESTARTなし）、36/37（timeoutあり）のraw結果とemulated結果が一致。timeout付きについては追加native実測のEINTRを保持し、相対期限の再実行による延長を避けている。futex_signal_frame_restarts_only_untimed_sa_restartはprivate WAIT、monotonic/realtime BITSET、timeout有無、flag有無の18組合せを検査する。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| stage frontmatter確認 | validation tools指定なし | 前回読込み済みstage定義を適用。 |
| aidlc engine now | 2026-10-09T13:54:48Z | Dateの実測値。 |
| manifest限定SHA256照合 | source 36 matches 36 | 全36claimed pathsの現workspace bytesはfinal-proof source hashと一致。 |
| raw differential限定照合 | raw differential 38 /38 pass | 各ケースのnative/emulated JSON・manifest・stdout・stderr・exit・timeoutを直接照合。追加27–29はHost待機中の更新を扱うが、今回の待機開始前通知を扱わない。 |
| 現CI run原本metadata確認 | native37937844111・quality37937843999、head e8e23fbd4f2f8410885522df57cdc4094c77c4d2、completed success | 旧f29cdの成功を現sourceへ流用していない。final-proofの3OS各jobも同headでsuccess。 |
| 現coverage原本JSON確認 | 3226/3797=84.961811956808%、floor80、固定13file | 分母のfile集合と下限は前回と同じ、修正で対象行数は増えている。 |
| 現fuzz原本末尾・exit・lock確認 | threads12631309/futex9242228 runs、各601秒、exit0、lock_equal True | 保存済みASan/LSan成功を確認。重いCI/fuzzは再実行していない。 |
| 現Node/Safari原本JSON・wasm bytes確認 | Node26.9.0・Safari27.0.1は各21case pass、module SHA256 755adf8c6ed5ff48c829ec2607d441a01eff5f89c38adce7d420e9905139e34e | 現moduleのbytes hashとfinal-proofは一致。guest Worker接続の全量達成とは扱わない。 |
| pipe経由限定ELF・待機前タイマー解除 | 5/5でnanosleep=-4、elapsed0.004–0.008秒 | owner通知がsleep入口より前に届く順序で残存問題を再現。 |

### R-01の残存条件と再現

**検証済み**：以下のコマンドは製品・テストファイルを書かず、メモリ中のELFをpipeの/dev/fd経由で既存ローカルCLIに渡す。子のready storeはsetitimer(disarm)の後、親のnanosleepはready loadの後であり、signal handlerもsignal送信もタイマー満了もない。開始前に届いた制御通知だけで200ms sleepがEINTRになる。**未検証**：このレビュー中のCLI再buildと、この新規限定ゲストのLinux native実行。判定根拠は実測に加え、現sourceのgeneration/received/Interrupted分岐を直接確認したことにある。

```sh
python3 -c 'import os,struct,subprocess,time; base=0x400000; code=bytearray();
def mov(reg,v):
 code.extend(bytes([0x48+(reg>=8),0xb8+(reg%8)])+struct.pack("<Q",v))
def sc(n,*args):
 mov(0,n)
 for r,v in zip([7,6,2,10,8,9],args):mov(r,v)
 code.extend(b"\x0f\x05")
sc(56,0x10900,base+0x1f000,0,0,0);code.extend(b"\x48\x85\xc0\x0f\x84");jump=len(code);code.extend(bytes(4));loop=len(code);code.extend(b"\x83\x3d");d=len(code);code.extend(bytes(4));struct.pack_into("<i",code,d,0x1040-(120+d+5));code.extend(b"\x00\x74");code.append((loop-(len(code)+1))&255);sc(35,base+0x1000,0);code.extend(b"\x48\x89\x05");d=len(code);code.extend(bytes(4));struct.pack_into("<i",code,d,0x1048-(120+d+4));sc(1,1,base+0x1048,8);sc(231,0);child=len(code);struct.pack_into("<i",code,jump,child-jump-4);sc(38,0,base+0x1020,0);code.extend(b"\xc7\x05");d=len(code);code.extend(bytes(4));struct.pack_into("<i",code,d,0x1040-(120+d+8));code.extend(struct.pack("<I",1));sc(60,0);blob=bytearray(0x1100);blob[:64]=struct.pack("<16sHHIQQQIHHHHHH",b"\x7fELF\x02\x01\x01"+bytes(9),2,62,1,base+120,64,0,0,64,56,1,0,0,0);blob[64:120]=struct.pack("<IIQQQQQQ",1,7,0,base,base,len(blob),0x20000,4096);blob[120:120+len(code)]=code;struct.pack_into("<qq",blob,0x1000,0,200000000);
for i in range(5):
 r,w=os.pipe();os.write(w,blob);os.close(w);start=time.monotonic();p=subprocess.run(["target/debug/paludarium",f"/dev/fd/{r}"],pass_fds=(r,),capture_output=True,timeout=5);os.close(r);print("metadata_before_sleep",i,p.returncode,"elapsed",round(time.monotonic()-start,3),"result",struct.unpack("<q",p.stdout)[0] if len(p.stdout)==8 else p.stdout,"stderr",p.stderr.decode())'
```

```text
metadata_before_sleep 0 0 elapsed 0.008 result -4 stderr
metadata_before_sleep 1 0 elapsed 0.004 result -4 stderr
metadata_before_sleep 2 0 elapsed 0.004 result -4 stderr
metadata_before_sleep 3 0 elapsed 0.004 result -4 stderr
metadata_before_sleep 4 0 elapsed 0.004 result -4 stderr
```

内部テストtimer_set/shorten/cancel_recomputes_existing_host_sleep相当の3件はHost待機entryを受け取った後に更新するため、この入口より前の順序は対象外。追加native27–29もreadyの後に子を遅延させて待機中更新を狙う。残存条件は、この検証境界と現sourceの分岐を反証可能に示している。

### Summary

元のCriticalな期限遅延とfutex再開の不一致は解消したが、R-01の制御通知だけでEINTRを返さない条件がMajorとして残る。Critical 0、未解消Major 1のため所定判定基準ではREADYであり、指摘なしの判定ではない。
