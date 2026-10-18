## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-09T13:00:37Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | New |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| stage frontmatter確認 | validation tools指定なし | 追加の指定validatorはない。 |
| aidlc engine now | 2026-10-09T13:00:37Z | Dateの実測値。 |
| jj --ignore-working-copy diff --from af9b739d --to @ -- crates/paludarium-runtime/src/lib.rs crates/paludarium-kernel/src/syscalls.rs crates/paludarium-kernel/src/signals.rs | exit0、共有timer/ThreadState/workerへの変更を確認 | jj通常diffはsnapshot書込権限で失敗したため、読取専用モードに切替。 |
| source-manifestとfinal-proofの限定SHA256照合 | manifest paths 36 hash matches 36 mismatches [] | 36 claimed pathsの現workspace bytesは提出証拠のsource hashと一致。全workspace・他Unit constructionの読取りはしていない。 |
| U5保存raw stream/JSON/manifest照合 | raw differential 27 /27 pass | 各ケースのnative/emulated stdout・stderr・exit・timeoutを照合。今回の2ケースを含む全入力保証ではない。 |
| U5 CI原本metadata/coverage/fuzz原本確認 | quality37930448184 attempt2とnative37930448234はf29cd713ef59646b605743e3228569d8822f6638でsuccess。固定13file 3083/3751=82.1914%。threads12639279/futex14316438 runs、各601秒、exit0、lock before/after一致 | 保存済み成功結果を確認。重いCI/fuzzは再実行していない。 |
| U5保存Node/Safari原本確認 | Node26.9.0と実Safari27.0.1は21ケースpass | browser結果はwasm guest cloneの検証とは扱わない。 |
| pipe経由限定ELF・共有timer | timer_cross_thread 142 elapsed 2.011 stderr（空） | 既存ローカルCLIで遅延を再現。提出sourceでも同じ処理順を確認した。 |
| pipe経由限定ELF・futex SA_RESTART | futex_sa_restart 0 elapsed 0.089 futex_result -4 stderr（空） | handler復帰後の-EINTRを再現。Linux上でこの新規ゲストのnative実行は未検証、期待動作はLinux公式man-pagesの根拠。 |

### 限定検証の根拠と再現コマンド

実装の根拠：ThreadGroup::set_timerは共有値の代入だけ。sleepはwait_untilから戻るまでexpire_timerを再度呼ばない。Hostのnative_waitは渡された固定deadlineとcancellationだけを検査する。Runtimeは親workerを同期実行し、その完了後にExecution::finishへ入るので、finishが親sleep中にタイマーを検査することもない。[setitimer(2)](https://man7.org/linux/man-pages/man2/setitimer.2.html)はITIMER_REAL満了時のprocess SIGALRM生成を定めている（ドキュメント根拠）。

以下は実行したコマンド。ELFはPythonメモリ中で組み立て、pipeの/dev/fdを通して既存CLIへ渡した。製品・テスト・証拠ファイルは書き換えていない。CLIのこのレビュー中の再buildと、この新規2ゲストのLinux native実行は未検証。判定は再現だけでなく提出sourceの上記処理順にも基づく。

```sh
python3 -c 'import os,struct,subprocess,time; base=0x400000; code=bytearray();
def mov(reg,v):
 code.extend(bytes([0x48+(reg>=8),0xb8+(reg%8)])+struct.pack("<Q",v))
def sc(n,*args):
 mov(0,n)
 for r,v in zip([7,6,2,10,8,9],args):mov(r,v)
 code.extend(b"\x0f\x05")
sc(56,0x10900,base+0x1f000,0,0,0);code.extend(b"\x48\x85\xc0\x0f\x84");jump=len(code);code.extend(bytes(4));sc(35,base+0x1000,0);sc(231,0);child=len(code);struct.pack_into("<i",code,jump,child-jump-4);sc(35,base+0x1010,0);sc(38,0,base+0x1020,0);sc(60,0);blob=bytearray(0x1100);blob[:64]=struct.pack("<16sHHIQQQIHHHHHH",b"\x7fELF\x02\x01\x01"+bytes(9),2,62,1,base+120,64,0,0,64,56,1,0,0,0);blob[64:120]=struct.pack("<IIQQQQQQ",1,7,0,base,base,len(blob),0x20000,4096);blob[120:120+len(code)]=code;struct.pack_into("<qq",blob,0x1000,2,0);struct.pack_into("<qq",blob,0x1010,0,50000000);struct.pack_into("<qqqq",blob,0x1020,0,0,0,50000);r,w=os.pipe();os.write(w,blob);os.close(w);start=time.monotonic();p=subprocess.run(["target/debug/paludarium",f"/dev/fd/{r}"],pass_fds=(r,),capture_output=True,timeout=5);os.close(r);print("timer_cross_thread",p.returncode,"elapsed",round(time.monotonic()-start,3),"stderr",p.stderr.decode())'
```

```text
timer_cross_thread 142 elapsed 2.011 stderr
```

```sh
python3 -c 'import os,struct,subprocess,time; base=0x400000; code=bytearray();
def mov(reg,v):
 code.extend(bytes([0x48+(reg>=8),0xb8+(reg%8)])+struct.pack("<Q",v))
def sc(n,*args):
 mov(0,n)
 for r,v in zip([7,6,2,10,8,9],args):mov(r,v)
 code.extend(b"\x0f\x05")
sc(13,10,base+0x1000,0,8);sc(56,0x10900,base+0x1f000,0,0,0);code.extend(b"\x48\x85\xc0\x0f\x84");jump=len(code);code.extend(bytes(4));sc(202,base+0x1040,128,0,0,0,0);code.extend(b"\x48\x89\x05");disp=len(code);code.extend(bytes(4));struct.pack_into("<i",code,disp,0x1048-(120+disp+4));sc(1,1,base+0x1048,8);sc(231,0);child=len(code);struct.pack_into("<i",code,jump,child-jump-4);sc(35,base+0x1020,0);sc(234,1,1,10);sc(35,base+0x1020,0);sc(202,base+0x1040,129,1,0,0,0);sc(60,0);handler=base+120+len(code);code.extend(b"\xc3");restorer=base+120+len(code);sc(15);blob=bytearray(0x1100);blob[:64]=struct.pack("<16sHHIQQQIHHHHHH",b"\x7fELF\x02\x01\x01"+bytes(9),2,62,1,base+120,64,0,0,64,56,1,0,0,0);blob[64:120]=struct.pack("<IIQQQQQQ",1,7,0,base,base,len(blob),0x20000,4096);blob[120:120+len(code)]=code;struct.pack_into("<QQQQ",blob,0x1000,handler,0x14000000,restorer,0);struct.pack_into("<qq",blob,0x1020,0,50000000);r,w=os.pipe();os.write(w,blob);os.close(w);start=time.monotonic();p=subprocess.run(["target/debug/paludarium",f"/dev/fd/{r}"],pass_fds=(r,),capture_output=True,timeout=5);os.close(r);print("futex_sa_restart",p.returncode,"elapsed",round(time.monotonic()-start,3),"futex_result",struct.unpack("<q",p.stdout)[0] if len(p.stdout)==8 else p.stdout,"stderr",p.stderr.decode())'
```

```text
futex_sa_restart 0 elapsed 0.089 futex_result -4 stderr
```

### Summary

共有所有権、futex登録の不可分性、終了・joinの通常経路と提出済み有限検証は確認できたが、別workerのタイマー更新が既存待機に伝わらず、SA_RESTART付きfutexもLinuxと異なる。Critical 1件、Major 1件のため完成実装としては修正が必要である。
