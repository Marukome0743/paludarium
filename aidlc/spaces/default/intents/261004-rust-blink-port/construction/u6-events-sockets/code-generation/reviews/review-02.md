## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Stage:** code-generation
**Unit:** u6-events-sockets
**Verdict:** READY
**Date:** 2026-10-09T18:59:39Z
**Iteration:** 2
**Request:** review:e8cb6bb15e0e523256e03f9a43d44a94
**Source:** e33cfbb4bf1daefea2efa00d8c6a1f5f35848ef6

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/events.rs > EventCounter::write input_epoch; crates/paludarium-kernel/src/sockets.rs > SocketPairEnd::write input_epoch; crates/paludarium-kernel/src/epoll.rs > Interest::ready | 検証済み：EPOLLET 通知を受けた後、まだ未読の eventfd/socket に追加 write しても再通知されない。同一ELFの x86_64 Linux は再通知1件、現製品CLIは0件。epochを empty→nonempty のときだけ増やすため、今回の write が interest に見えない。追加データ・通知を待つゲストの epoll_wait が進まず、無期限待機では停止し得る。既存case20/46は追加write前に読み切る順序しか検査していない。 | 未読状態への追加writeを含むLinuxのET通知を保持する。eventfdとsocketの両方に、登録→write→wait→未読のまま追加write→waitのnative先行差分を追加し、再通知、drain後の再通知、ONESHOTを検査してから製品を修正する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/epoll.rs > dispatch の epoll_pwait old_mask 復帰; crates/paludarium-kernel/src/lib.rs > handle Outcome::Return 後 checkpoint | 検証済み：元maskでSIGALRMをblockし、epoll_pwaitの一時maskでunblockした間にSIGALRMが来ると、EINTRは返るがhandlerは実行されない。同一ELFはLinux(-4,1,1,0)、CLI(-4,0,1,0)。dispatchがcheckpointの配送より先にold_maskを戻すため、pending signalが再びblockedになる。既存case51はtimeout0・signalなしなのでこの順序を覆っていない。 | 一時maskで受けたsignalをhandlerへ配送する順序と、handler復帰時に元maskを回復する境界を設ける。元mask block→一時unblock→timer signal→EINTRとhandler1回→元mask復帰をnative先行ケースで検査し、通常待機・masked/ignored signal回帰を維持する。 | Resolved (reviewer) |

> R-01 Reviewer note: 検証済み：成功writeごとの入力epoch更新により、前回のeventfd/socket未読追加write反証ELFがLinuxと現CLIで一致した。C67–72の追加write・drain・ONESHOT原本も一致。C79–81と新単体テストでeventfd readおよびsocket write segment消費によるOUT callbackを確認した。同期単体 `u6_et_unread_write_during_host_wait` はHost待機内の追加writeを検査する。

> R-02 Reviewer note: 検証済み：epoll_pwaitの一時maskで配送対象を選び、旧maskをsignal frameへ保存してからhandler用maskへ切り替える実装となった。前回反証ELFはLinuxと現CLIの双方で(-4,1,1,0)。C73–78原本と `u6_pwait_handler_uses_temporary_mask_and_returns_original` がEINTR、handler到達、NODEFER/action mask、sigreturn時の旧mask復帰を検査する。masked/ignored/metadataの非handler復帰も単体で成功。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 独立Mac単体実行 | `PATH=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-01-aarch64-apple-darwin/bin:$PATH /Users/mutoakio/.rustup/toolchains/nightly-2026-10-01-aarch64-apple-darwin/bin/cargo test --locked -p paludarium-kernel --lib u6_`：exit0、49 passed、0 failed | 新callback・待機同期・一時mask配送・旧mask復帰の回帰を含む。 |
| 独立CLI再buildと前回反証ELF再実行 | 同nightlyの `cargo build --locked -p paludarium`：exit0。`docker exec f9876282522f /tmp/u6-review-et-20` / `target/debug/paludarium /private/tmp/u6-review-et-20` は双方(1,1,2,0)。同様に `u6-review-et-46` は双方(0,1,1,3)、`u6-review-pwait-51` は双方(-4,1,1,0)。各exit0、stderr空、各subprocess timeout10秒。 | image `rust:1-bookworm`、container `wonderful_haibt` / `f9876282522f`、x86_64 Linux。同一ELFの前回反証が修正後に解消した。 |
| 現U6 raw差分の独立照合 | `verification/revision-final-differential/*/manifest.json` と各native/emulated stdout bytesを照合。84ケース＋fresh timer反復10件＝94記録、timeoutなし。相違はC52–54の承認済みnetwork拒否とC60のnative -9 / CLI137のみ。C67–81はexit/stdout/stderr/timeout全一致。 | C67–81の結果をsummaryのpassフラグだけで判断していない。network例外とsignal終了正規化はCOMPARISON.mdの境界に合致。 |
| 現head・source・証拠hash照合 | manifestの31 leafをfinal-proof source hashへ独立照合：全一致。currentU配下のevidence_hashes 1619ファイルを独立SHA256照合：全一致。production wasm SHA256 `91c0f246b9043c996e40ba2fc80308dfae85d3f42ed99d0ea078e236a34d364e` 一致。 | 439 sourceの全workspace再読は行わず、指定31 leafを検査した。source比較原本は439件、歴史保存リストは78件。 |
| 同head CI原本 | `revision-final-native-run.json`：37974655062、現head、native-first/differential成功。`revision-final-quality-run.json`：37974654964、現head、coverage・両fuzz・production-wasm・3OS・preceding-native-diff全8job成功。 | 重いCIの再実行をせず、currentUコピーのrun/job/log/rawを確認した。 |
| coverage・sanitizer原本 | 固定9production filesのcoverage JSON：2352/2785＝84.4524%、floor80。events raw：`Done 2739611 runs in 601 second(s)`、sockets raw：`Done 2533386 runs in 601 second(s)`。 | 分母・下限・600秒要求を維持。今回のtraceability notesは現headと今回原本へ対応する。 |
| Node・実Safari原本 | Node103件、Safari raw103件、各unique case103/all pass。Safari保存reportのresultsとUTF-8 raw reportは完全一致。metadataはSafari27.0.1、actual Safari native UI、webdriver_used=false。 | 現moduleと証拠hashを照合。U11へ明示されたguest Worker/Tokio境界と、今回の非threaded guest・既存shared Rust worker成功を区別している。 |
| canonical checker | 実行していない。親のexit0報告は独立レビューの実行結果として扱わない。 | historical sibling recordsを読むため指定readscopeから除外。上記currentU raw/hashの手動検査で反証した。 |

### Reproduction Evidence

前回から保持したELFのSHA256はeventfd `a6e2f9b0b81767e049ec2fa10793ec7e8f685b7cff4bfb11b6c24117bc653aae`、socket `06d476877a24b9c1941b0f1c868ce47bfe69ffd63642caa86f45aecd11cbf8a8`、pwait `b08bcb38deed904dd9cda0155c253b0c25d30a29cc33f0c114d476ca766d8bd4`。今回双方のraw stdoutは順に `0100000000000000010000000000000002000000000000000000000000000000`、`0000000000000000010000000000000001000000000000000300000000000000`、`fcffffffffffffff010000000000000001000000000000000000000000000000`。

### Summary

前回の両指摘は実装境界と独立再実行の双方で解消を確認した。指定された有限比較・品質・Wasm境界内で新しい反証可能な欠陥は見つからず、READYとする。任意入力やLinux全packet容量・U11 guest Worker対応までの成功を推論していない。
