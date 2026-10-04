## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-06T07:20:11Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/lib.rs > Kernel::checkpoint / syscall restart preview; crates/paludarium-kernel/src/signals.rs > queue / next_pending; aidlc/spaces/default/intents/261004-rust-blink-port/construction/u4-memory-signals/code-generation/traceability.json > FR2.9 / NFR5 | 検証済み：前回の公開 API 反例（queue_signal 36→35、checkpoint）は現在 Exit(Signaled(35)) を返し、前回独立観測の native_default_signal=35 と一致する。独立 u4_ 回帰は76 passed / 0 failed、低番号RT、mask/FIFO、target別coalesce、同期fault、Thread優先、両SA_RESTART状態、SIGKILL/stop/cancellationを含む。ソースはProcess/Thread provenanceを保持し、配送とrestart previewが同じnext_pendingを使う。ドキュメント根拠：保存された最終native比較はdefault/handler/混在番号に加えkillとtkill/tgkillの異なるqueue順も一致する。従来の単純到着順による終了原因の差は解消した。 | 追加修正なし。追加native回帰と内部回帰を現在のCI対象に保持する。 | Resolved |

### Independent Validation

| Check | Observed result | Interpretation |
|---|---|---|
| source-manifest / capture | 検証済み：107 claims、missing 0。manifest SHA256 d5af3e67ab3424552850e1762d8f64b331cddc3a2165818626c7e9c9f77d72bd。production37 paths、changed 0。capture SHA256 1283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c。 | 現在固定されたソースと証拠の対応を確認した。 |
| sections / traceability | 検証済み：planの6 sectionsと必要成果物を確認。traceability15 targetsはmissing 0、FR/NFR割当とcurrent/historical receiptsを照合。 | 過去311pass/93.48%と現在317pass/93.70%が区別されている。 |
| scoped Rust tests | 検証済み：下記command exit0、76 passed / 0 failed。CPU5、Host8、Kernel37、MMU10、Runtime11、Types5。 | R-01修正の限定回帰と既存memory/time/signal/Runtime境界を独立実行した。 |
| public Kernel API counterexample | 検証済み：cargo build / rustc stdin probe / executionはexit0、Exit(Signaled(35))。 | 前回の具体的な36終了を再現しなくなった。 |
| saved final Linux receipt integrity | 検証済み：coverage-provenance-final.txtのSHA256はvalidation-current.jsonのd34bcea1ccc21bb3da46f451373b94ffa4b777fd2fea63fe415610024e09f6ceと一致。runner別親summary合計317。 | 保存済み証拠の同一性と集計を独立確認した。Linux suiteを新規再実行したという意味ではない。 |
| saved coverage / differential / quality | ドキュメント根拠：coverage-provenance-final.txt line828はU4diff44 passed、line1122は5095 lines /321 missed /93.70%。rt-provenance-quality-scoped-green.txtにfmt/fuzzfmt/clippyと内部76/live3の成功。 | 品質下限80%を維持し、現sourceでの保存結果を評価した。 |
| saved final ASan / dependency audit | ドキュメント根拠：fuzz-syscall-provenance-final.txt line2580は1136975 runs/601 seconds、fuzz-mmu-provenance-final.txt line3394は1564316 runs/601 seconds。evidence.mdは逐次runner exit0を記録。Cargo.lockは既存deny4category成功時のhashと不変。 | 中間番号選択だけのfuzz結果で最終target修正を代用していない。不要な広域再実行を要求しない。 |

独立実行した限定test command：

```powershell
& "$env:USERPROFILE/.cargo/bin/cargo.exe" test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture
```

確認された追加testsは `u4_signal_realtime_selection_keeps_fifo_and_masks`、`u4_signal_pending_targets_keep_number_order_fifo_and_coalescing`、`u4_signal_synchronous_fault_selects_thread_pending_queue`、`u4_signal_thread_target_restart_preview_matches_delivery`、`u4_signal_restart_preview_uses_selected_realtime_handler`。既存 `u4_signal_realtime_queue_has_no_invented_quota`、inbox backlog/race、write restart frame、stop/continue/kill回帰も通過した。

### Counterexample Recheck

前回と同じ最小公開API probeを現在のcargo build生成物へ再linkした。具体的なRust入力：

```rust
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
```

`cargo.exe build --locked -p paludarium-kernel -p paludarium-host -p paludarium-cpu -p paludarium-mmu -p paludarium-types` の後、`rg --files target/debug -g '*.rlib' / '*.rmeta'` で各crateの最新生成物を解決し、`rustc.exe --edition=2024 --crate-name u4_review_order - -o target/u4-review-order.exe` に各crateのrlib/rmetaを`--extern`、各metadata directoryを`-L dependency=...`で渡した。stdin入力は上記、実行 `& './target/u4-review-order.exe'` のstdoutは `Exit(Signaled(35))`、exit0。詳細の動的引数組立ては前回reviewのReproductionと同一である。製品ソースを変更していない。

現在保存native比較の具体物：`docs/u4/inventory/rt-provenance-quality-scoped-green.txt` lines135–151と`coverage-provenance-final.txt` lines464–470は、mode0 default35、mode1 35:0→36:0、mode3 10:0→35:0、mode4/5 36:-6→35:0、mode6 35:-6→35:0、mode7 10:-6→10:0のnative/Kernel一致を記録する。native-only同番号Process FIFOは35:0→35:-1、Thread FIFOは35:-6→35:-1（lines130/132）。`tests/guests/u4/realtime-order-oracle.c` と `crates/paludarium-harness/tests/support/u4_oracles.rs` の対応modeを読み、全signalsをmaskしてenqueue後にunmaskする手順、handler内のmask、既定終了のwaitpid観測を確認した。SI_QUEUEはnative observer/内部metadata回帰の証拠で、guest syscall実装を主張していない。

追加native再実行は未検証：読取専用fixtureマウントを使う `docker.exe run --rm --network none -v 'C:/Users/Jam/Documents/aletheia-works/paludarium/tests/guests/u4:/fixtures:ro' paludarium-dev bash -c 'cc -O1 /fixtures/realtime-order-oracle.c -o /tmp/u4-review-rt && for mode in 0 1 2 3 4 5 6 7 8; do printf "mode=%s " "$mode"; timeout 5 /tmp/u4-review-rt "$mode" || exit; done'` はstdoutなしで待機し、中断exit1。これを成功/native差分不一致のどちらにも数えていない。R-01のnative基準は前回独立観測と上記保存済み最終比較を使用した。

中断後の `docker.exe ps --filter 'ancestor=paludarium-dev' --format '{{.ID}} {{.Names}} {{.Command}}'` はexit0・出力なし。稼働中の当該imageのcontainerは観測されず、他containerへの停止/削除を行っていない。

### Summary

R-01をResolvedとして保持する。現在の具体的反例再検査、限定76回帰、source/capture/receiptの照合で未解消のblocking defectは観測されなかった。remote CI、macOS/wasm、全任意入力、probe/aube全program完走まで検証したとは解釈しない。
