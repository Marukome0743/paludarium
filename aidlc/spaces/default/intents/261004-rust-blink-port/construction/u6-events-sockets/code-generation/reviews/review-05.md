## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T14:43:00Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-kernel/src/events.rs > EventCounter::write input_epoch; crates/paludarium-kernel/src/sockets.rs > SocketPairEnd::write input_epoch; crates/paludarium-kernel/src/epoll.rs > Interest::ready | 検証済み：EPOLLET 通知を受けた後、まだ未読の eventfd/socket に追加 write しても再通知されない。同一ELFの x86_64 Linux は再通知1件、現製品CLIは0件。epochを empty→nonempty のときだけ増やすため、今回の write が interest に見えない。追加データ・通知を待つゲストの epoll_wait が進まず、無期限待機では停止し得る。既存case20/46は追加write前に読み切る順序しか検査していない。 | 未読状態への追加writeを含むLinuxのET通知を保持する。eventfdとsocketの両方に、登録→write→wait→未読のまま追加write→waitのnative先行差分を追加し、再通知、drain後の再通知、ONESHOTを検査してから製品を修正する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/epoll.rs > dispatch の epoll_pwait old_mask 復帰; crates/paludarium-kernel/src/lib.rs > handle Outcome::Return 後 checkpoint | 検証済み：元maskでSIGALRMをblockし、epoll_pwaitの一時maskでunblockした間にSIGALRMが来ると、EINTRは返るがhandlerは実行されない。同一ELFはLinux(-4,1,1,0)、CLI(-4,0,1,0)。dispatchがcheckpointの配送より先にold_maskを戻すため、pending signalが再びblockedになる。既存case51はtimeout0・signalなしなのでこの順序を覆っていない。 | 一時maskで受けたsignalをhandlerへ配送する順序と、handler復帰時に元maskを回復する境界を設ける。元mask block→一時unblock→timer signal→EINTRとhandler1回→元mask復帰をnative先行ケースで検査し、通常待機・masked/ignored signal回帰を維持する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u6-events-sockets/code-generation/code-generation-plan.md > 今回の計画：Step19 | Step19は「source-manifestに今回変わったファイルは含まれない」と書いており、これはsource-manifest.jsonの31 leafと照合して事実である。しかしU6のproduction wasmのNode/本物Safari全102ケースの証拠は、module 4482b157…（head 11c033c7）で取得されたものである。このmoduleは `crates/paludarium-wasm`（`abi.rs`）からビルドされ、U14の変更でJIT stateの領域とjit_executeの受け渡しが変わったため、現headの1ceae86cから作るmoduleとは別物になる。U6のcode-summaryとStep19にはこの点が明記されていない。 | Step19に「U6のNode/Safari 102ケースの証拠はU14変更前のmodule 4482b157…に対するもので、U14後のmoduleに対する新しい実行ではない」と一文足す。「記録が今のsourceと合っている」という確認の範囲を、source-manifestの31 leafとU6の担当sourceに限ると書く。 | Resolved (reviewer) |
| R-04 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u6-events-sockets/code-generation/code-summary.md > 現行Step19〜20の節 (c) と末尾の箇条 | (c)と最後の箇条は「下の『今回Steps16〜18の現行実行』」「下の『今回Steps16〜18』の節」と書くが、その見出しは「履歴：Steps16〜18の現行実行（2026-10-17のStep19〜20の前）」に改名されており、見出し名が一致しない。読み手が対応する節を探しにくい。内容の誤りではない。 | 参照を「履歴：Steps16〜18の現行実行」の見出し名に合わせる。次回の記録更新のついででよい。 | New |

> R-03 Reviewer note: code-summary.md 先頭の「現行Step19〜20」節の(c)に、102ケースの証拠はU14変更前のmodule（4482b157…、head 11c033c7）に対するもので、1ceae86cのmoduleでは測り直していないと明記された。(d)で「記録が今のsourceと合っている」は記録とsource-manifestを照らした範囲で新しい実行ではないと限定された。module hashとheadは同ファイルの履歴節（4482b1574987…、head11c033c7）と一致する。run 39030957672はU14の4環境比較としてのみ書かれている。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (shell not permitted for this pass) | NOT RUN | 指示どおりシェルを使わず、ファイルの読み取りだけで確認した。sensorの結果は依頼文の記述に依存する。run 39030957672の内容は他Unitの記録で、読み取り範囲外のため確認していない。 |

### Summary

前回のMinor（R-03）は十分に解消された。証拠の対象module、U6の102ケースを今のmoduleで測り直していないこと、「現在のsourceと合っている」の意味の限定は、いずれも履歴節と矛盾なく書かれている。残るのは見出し名の参照のずれという軽微な点だけである。
