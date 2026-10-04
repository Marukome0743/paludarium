## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-06T05:35:00Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/lib.rs > Kernel::checkpoint pending selection, line 174; crates/paludarium-kernel/src/signals.rs > queue, line 90; aidlc/spaces/default/intents/261004-rust-blink-port/construction/u4-memory-signals/code-generation/traceability.json > FR2.9 / NFR5 | 検証済み：異なる番号の RT signal が配送前に pending になると、Linux の低い番号優先ではなく到着順で配送する。36→35 を pending にした native は既定動作で signal 35 により終了するが、公開 Kernel API は Exit(Signaled(36)) を返した。checkpoint は SIGKILL 以外を最初の配送可能要素で選び、queue は末尾へ追加するため、ゲストの終了原因が変わる。既存の RT 大量 queue テストおよび 43 差分では、この異なる番号の逆順 pending を反証できていない。 | 配送可能な RT signal の異なる番号間では低い番号を優先し、同じ番号内の FIFO、mask、停止中の配送制限、標準 signal の coalesce、SIGKILL 優先を保持する。36→35 を配送前に pending にした native と Kernel の比較回帰を追加し、既定終了と handler 配送順を確認する。配送対象を事前参照する restart 判定も最終の選択と一致させる。対応後の差分結果を evidence / traceability に反映する。 | New |

### Validation Tool Results

| Check | Result | Interpretation |
|---|---|---|
| manifest / current source hashes | 検証済み：manifest 92 paths、missing 0。source-hashes-current.json の production 36 paths は hash mismatch 0。追加再現後も mismatch 0。 | 固定された対象ソースを評価した。レビューによる製品変更なし。 |
| artifact sections / traceability references | 検証済み：plan 6、unit-test-instructions 5、code-summary 4 の H2 sections。traceability の target 15 件は missing 0。 | 必須成果物および直接参照先は存在する。 |
| scoped Rust tests | 検証済み：下記 cargo test は exit 0、71 passed / 0 failed（CPU 5、Host 8、Kernel 32、MMU 10、Runtime 11、Types 5）。 | frame、restart、stop/continue/kill、cancellation、RT quota などの既存回帰は成功するが、R-01 の反例は残る。 |
| saved Linux coverage / native differential receipts | ドキュメント根拠：docs/u4/inventory/coverage-quota-final.txt の line 812 は diff_u4 43 passed、line 1101 は TOTAL line coverage 93.48%。validation-current.json は最終 Linux suite 311 passed / 0 failed を記録。 | 独立再実行ではなく保存済み観測。全 RT 番号間の順序を保証する証拠ではない。 |
| saved linter / type-check / ASan receipts | ドキュメント根拠：evidence.md / validation-current.json に fmt、fuzz fmt、clippy 成功。cargo-deny-final.txt line 1 は advisories / bans / licenses / sources ok。fuzz-syscall-final.txt line 1257 は 348580 runs / 601 seconds、fuzz-mmu-final.txt line 2637 は 987393 runs / 601 seconds の完了を記録。独立 cargo build は exit 0。 | 広域 suite / 10 分 fuzz は再実行しなかった。保存済み証拠と現在 source hash を区別した。 |
| CI / bounded test targets | ドキュメント根拠：.github/workflows/ci.yml line 96 の diff_u4、line 111 の coverage threshold 80、nightly.yml line 40 の max_total_time 600 / timeout 30。tests/support/u4.rs は子プロセス watchdog の kill と wait を実装。 | 対象検証の継続実行と timeout 後の回収をソースで確認した。 |

独立テストの実行コマンド：

```powershell
& "$env:USERPROFILE/.cargo/bin/cargo.exe" test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture
```

### R-01 Reproduction

反証可能な主張：「36、35 がともに pending で配送可能になる場合、Kernel の既定終了 signal は Linux native と同じ 35 になる。」下記の独立観測でこの主張は否定された。両方を queue に入れてから checkpoint を呼ぶため、36 の単独配送後に 35 が到着するケースではない。

native の pending 取得順：

```powershell
& 'C:/Program Files/Docker/Docker/resources/bin/docker.exe' run --rm --network none paludarium-dev python3 -c 'import signal,os; s={35,36}; signal.pthread_sigmask(signal.SIG_BLOCK,s); os.kill(os.getpid(),36); os.kill(os.getpid(),35); print(signal.sigwaitinfo(s).si_signo,signal.sigwaitinfo(s).si_signo)'
# exit 0: 35 36
```

native の既定動作も同じ番号優先で終了する：

```powershell
$native=@'
import os,signal
s={35,36}
r,w=os.pipe(); r2,w2=os.pipe(); pid=os.fork()
if pid==0:
 os.close(r); os.close(w2); signal.pthread_sigmask(signal.SIG_BLOCK,s); os.write(w,b'R'); os.read(r2,1); signal.pthread_sigmask(signal.SIG_UNBLOCK,s); os._exit(99)
os.close(w); os.close(r2); os.read(r,1); os.kill(pid,36); os.kill(pid,35); os.write(w2,b'U'); _,status=os.waitpid(pid,0); print('native_default_signal='+str(os.WTERMSIG(status)))
'@
& 'C:/Program Files/Docker/Docker/resources/bin/docker.exe' run --rm --network none paludarium-dev python3 -c $native
# exit 0: native_default_signal=35
```

公開 Kernel API による最小再現。製品ソースや manifest を変更せず、stdin から probe を compile した。rlib と rmeta は現在の cargo build が生成した実体から解決する。

```powershell
& "$env:USERPROFILE/.cargo/bin/cargo.exe" build --locked -p paludarium-kernel -p paludarium-host -p paludarium-cpu -p paludarium-mmu -p paludarium-types
$libs=@(rg --files target/debug -g '*.rlib')
$metas=@(rg --files target/debug -g '*.rmeta')
$argsList=@('--edition=2024','--crate-name','u4_review_order','-','-o','target/u4-review-order.exe')
foreach($d in ($metas|ForEach-Object{Split-Path $_ -Parent}|Sort-Object -Unique)){$argsList+=@('-L',('dependency='+$d))}
foreach($n in @('kernel','host','cpu','mmu','types')){
 $lib=$libs|Where-Object{(Split-Path $_ -Leaf) -like ('libpaludarium_'+$n+'-*')}|ForEach-Object{Get-Item -LiteralPath $_}|Sort-Object LastWriteTime -Descending|Select-Object -First 1
 $meta=[IO.Path]::ChangeExtension($lib.FullName,'.rmeta')
 $argsList+=@('--extern',('paludarium_'+$n+'='+$meta),'--extern',('paludarium_'+$n+'='+$lib.FullName))
}
$src=@'
use std::sync::Arc;
use paludarium_kernel::{Kernel,Thread};
use paludarium_host::testing::RecordingHost;
use paludarium_cpu::CpuState;
use paludarium_mmu::AddressSpace;
use paludarium_types::GuestAddr;
fn main(){
 let mut k=Kernel::new(Arc::new(RecordingHost::new()));
 let mut t=Thread{tid:1,cpu:CpuState::new(GuestAddr(0x10000),GuestAddr(0x40002000))};
 let m=AddressSpace::new();
 k.queue_signal(36).unwrap(); k.queue_signal(35).unwrap();
 println!("{:?}",k.checkpoint(&mut t,&m));
}
'@
$src|& "$env:USERPROFILE/.cargo/bin/rustc.exe" @argsList
if($LASTEXITCODE -eq 0){& './target/u4-review-order.exe'}
# build / compile / execution exit 0: Exit(Signaled(36))
```

### Summary

検証済みの R-01 はゲストの終了原因を変える実行時の互換性欠陥であり、readiness を阻害する。既存の限定テストと保存済み広域証拠は有効だが、この具体的反例の修正と回帰確認が必要である。
