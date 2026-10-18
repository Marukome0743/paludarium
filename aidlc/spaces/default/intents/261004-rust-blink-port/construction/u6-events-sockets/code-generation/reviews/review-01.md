## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Stage:** code-generation
**Unit:** u6-events-sockets
**Verdict:** NOT-READY
**Date:** 2026-10-09T18:13:04Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/events.rs > EventCounter::write input_epoch; crates/paludarium-kernel/src/sockets.rs > SocketPairEnd::write input_epoch; crates/paludarium-kernel/src/epoll.rs > Interest::ready | 検証済み：EPOLLET 通知を受けた後、まだ未読の eventfd/socket に追加 write しても再通知されない。同一ELFの x86_64 Linux は再通知1件、現製品CLIは0件。epochを empty→nonempty のときだけ増やすため、今回の write が interest に見えない。追加データ・通知を待つゲストの epoll_wait が進まず、無期限待機では停止し得る。既存case20/46は追加write前に読み切る順序しか検査していない。 | 未読状態への追加writeを含むLinuxのET通知を保持する。eventfdとsocketの両方に、登録→write→wait→未読のまま追加write→waitのnative先行差分を追加し、再通知、drain後の再通知、ONESHOTを検査してから製品を修正する。 | New |
| R-02 | Major | crates/paludarium-kernel/src/epoll.rs > dispatch の epoll_pwait old_mask 復帰; crates/paludarium-kernel/src/lib.rs > handle Outcome::Return 後 checkpoint | 検証済み：元maskでSIGALRMをblockし、epoll_pwaitの一時maskでunblockした間にSIGALRMが来ると、EINTRは返るがhandlerは実行されない。同一ELFはLinux(-4,1,1,0)、CLI(-4,0,1,0)。dispatchがcheckpointの配送より先にold_maskを戻すため、pending signalが再びblockedになる。既存case51はtimeout0・signalなしなのでこの順序を覆っていない。 | 一時maskで受けたsignalをhandlerへ配送する順序と、handler復帰時に元maskを回復する境界を設ける。元mask block→一時unblock→timer signal→EINTRとhandler1回→元mask復帰をnative先行ケースで検査し、通常待機・masked/ignored signal回帰を維持する。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 固定toolchain cargo test --locked -p paludarium-kernel --lib u6_ | PASS：44 passed;0 failed;100 filtered out | 既存テストは成功するが、今回の反証順序を検査していない。 |
| 固定toolchain cargo build --locked -p paludarium | PASS：Finished dev profile | 反証CLIは今回sourceから再build。build完了後にETのCLI結果を再実行して同じ不一致を確認した。 |
| 同一ELF Linux/CLI比較（下記） | FAIL：eventfd ET、socket ET、pwait signalの3観測不一致 | 保存期待や一般的説明を使わず、x86_64 Linuxで実測して製品と比較した。全実行exit0、stderr空、timeoutなし。 |
| Python read-only：31 source claim SHA-256とfinal-proof | PASS：全31一致、source inventory439、歴史inventory78 | 原本の対象製品とレビュー対象bytesが一致する。sibling construction実ファイルは読んでいない。 |
| Python read-only：final-differentialの69 manifest/JSON/raw stdout/stderr/timeout | PASS：69原本結合 | 非同一は52〜54の明示network policy例外と60の-9→137終了値対応のみ。既存69件の成功は今回の3追加観測を含まない。 |
| Python read-only：coverage/fuzz/module/browser原本 | PASS：固定9file2296/2726=84.225972%、floor80。events3612264/sockets2813162 runs各601秒exit0。wasm SHA一致。Node88とSafari raw88 pass | 既存品質結果は保持されている。実Safari補足は27.0.1、actual Safari native UI、webdriver_used=false。ブラウザの限定成功は今回のnative意味論不一致を反証しない。 |
| Stage validation tools | 個別validation command指定なし | required-sections/traceabilityはsensor宣言。候補checkerはsibling recordsを読むため実行せず、current unit原本を直接検査した。 |

### Reproduction evidence

検証環境：既存コンテナ `f9876282522f`（name `wonderful_haibt`、image `rust:1-bookworm`）。`docker exec f9876282522f uname -a` は `Linux f9876282522f 7.0.14-linuxkit ... x86_64 GNU/Linux`。先に `docker exec f9876282522f python3 -c` でselect.epollとos.eventfd/socket.socketpairを直接使い、両方の「未読再write」後にも1件のEPOLLET通知を確認した。

ソースは `tests/guests/u6/events.c` を読み、次の各case bodyだけをメモリ内で置換した。リポジトリのsourceは編集していない。

```c
case 20:ctl(e,1,fd,1|ET,1);put(fd,1);o[0]=wait(e,out,1,0);put(fd,1);o[1]=wait(e,out,1,0);get(fd,&x);o[2]=x;break;
case 46:e=ep();ctl(e,1,p[1],1|ET,7);S(1,p[0],"ab",2);o[1]=wait(e,out,1,0);S(1,p[0],"c",1);o[2]=wait(e,out,1,0);o[3]=S(0,p[1],b,3);break;
case 51:{U blocked=1UL<<13,mask=0,after=0;sc(14,0,(U)&blocked,0,8,0,0);alarm_us(20000);o[0]=sc(281,e,(U)out,1,500,(U)&mask,8);o[1]=signals;sc(14,2,0,(U)&after,8,0,0);o[2]=(after&blocked)!=0;break;}
```

Python subprocessでそのsource bytesを次のcompilerのstdinへ渡した。N=20/46の出力は `/tmp/u6-review-et-N`、N=51は `/tmp/u6-review-pwait-51`。

```text
docker exec -i f9876282522f gcc -x c -static -O1 -nostdlib -fno-stack-protector -fno-builtin -fno-asynchronous-unwind-tables -fcf-protection=none -mno-red-zone -fno-pie -no-pie -Wall -Wextra -Werror -DCASE=N -o /tmp/<output> -
docker cp f9876282522f:/tmp/<output> /private/tmp/<output>
docker exec f9876282522f /tmp/<output>
target/debug/paludarium /private/tmp/<output>
```

各実行はPython subprocess.run(capture_output=True,timeout=10)。stdoutはlittle-endian signed64×4。

| Probe / ELF SHA256 | Linux stdout hex / words | CLI stdout hex / words |
|---|---|---|
| u6-review-et-20 / a6e2f9b0b81767e049ec2fa10793ec7e8f685b7cff4bfb11b6c24117bc653aae | 0100000000000000010000000000000002000000000000000000000000000000 / (1,1,2,0) | 0100000000000000000000000000000002000000000000000000000000000000 / (1,0,2,0) |
| u6-review-et-46 / 06d476877a24b9c1941b0f1c868ce47bfe69ffd63642caa86f45aecd11cbf8a8 | 0000000000000000010000000000000001000000000000000300000000000000 / (0,1,1,3) | 0000000000000000010000000000000000000000000000000300000000000000 / (0,1,0,3) |
| u6-review-pwait-51 / b08bcb38deed904dd9cda0155c253b0c25d30a29cc33f0c114d476ca766d8bd4 | fcffffffffffffff010000000000000001000000000000000000000000000000 / (-4,1,1,0) | fcffffffffffffff000000000000000001000000000000000000000000000000 / (-4,0,1,0) |

### Summary

既存69差分と品質ゲートの成功を確認したが、未読状態への追加writeのET再通知とepoll_pwait一時unmask中のhandler配送を同一ELFで反証した。ET通知の欠落がゲストを停止させ得るため、この2境界を修正するまでNOT-READY。
