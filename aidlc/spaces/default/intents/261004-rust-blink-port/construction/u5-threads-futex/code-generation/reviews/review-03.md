## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-09T15:48:24Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | New |

> R-01 Reviewer note: 検証済み：ThreadGroup::set_timer は各 owner inbox に timer_changed を保持し、SignalInbox::drain が通知種別を queue mutex 内で消費する。別 worker の drain_process は timer/control receipt を保持する。sleep は generation 差分がなくても timer receipt で元の deadline を再計算し、実 signal・外部中断・group 終了を優先する。独立実行の Kernel U5 27件が成功。同期テストが入口前、owner ack 後の再送、mask/ignore、外部中断、group 終了を検査する。最終 native 差分43件と86組の raw JSON/stdout/stderr を照合し、新38〜41は (0,0,1)、42は (-110,0,1)。既存待機中 set/shorten/disarm と futex/flock 回帰も成功。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| PATH=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-01-aarch64-apple-darwin/bin:$PATH /Users/mutoakio/.rustup/toolchains/nightly-2026-10-01-aarch64-apple-darwin/bin/cargo test --locked -p paludarium-kernel --lib u5_tests | PASS：27 passed; 0 failed; 73 filtered out | 独立実行。timer receipt、入口前 deadline、既存待機中 timer 更新、futex/flock metadata、restart 回帰を確認。最初の cargo 単独実行は PATH の rustc 1.99 を選び失敗したため、固定 toolchain bin を PATH に設定して再実行した。製品変更は行っていない。 |
| Python read-only：source-manifest の36 source claim と final-proof の SHA-256 を比較 | PASS：mismatches [] | 今回レビュー対象 source は最終証拠の bytes と一致する。 |
| Python read-only：preentry-final-differential-artifact/0〜42 の manifest と native/emulated JSON・stdout・stderr を比較 | PASS：43 manifest 一致、86 raw 結合、全 timeout false | 入口前の追加5ケースと既存38ケースの有限差分を確認。guest ready は timer syscall 完了後の atomic store、親は atomic load 後に待機へ入る。scheduler の推定で入口前順序を作っていない。 |
| Python read-only：最終 coverage JSON、run/job metadata、fuzz raw.log・exit.txt・lock hash | PASS：固定13 file 3256/3825=85.124183%、floor80。native37951856306 success、quality37951856624 attempt2全8 job success。threads18531279/futex9935154 runs、各601秒、exit0、lock before/after一致 | 同 head 9aa149786015ad9f789e8527cc30d7f30f2f9482 の結果。attempt1 coverage failure は残されており、成功した attempt2 と混同していない。今回レビューでは長時間 fuzz/3OS CI を再実行せず原本を検査した。 |
| Python read-only：production wasm SHA-256 と Node/Safari report | PASS：module18c7edb072830bd6148e408175b8d318516adef39018d9d190c8328e8a4d10ea。Node21/Safari21全 pass。Safari27.0.1 isolation/sharedMemory/cleanup true | 現 module の回帰証拠を確認。レビュー中の Safari 再起動は行っていない。wasm guest clone Worker の完成とは扱わない。 |
| Stage validation tools | 個別 validation command の指定なし | stage の required-sections/traceability は sensor 宣言。対応先は存在するが notes の旧結果混在を上記 Minor に記録した。候補 checker は sibling records を読むため、この限定レビューでは実行していない。 |

### Summary

R-01 のタイマー通知接続と待機入口前の偽 EINTR は、owner receipt の実装、同期回帰テスト、native と最終製品の43ケース原本で修正を確認した。Critical/Major の未解決指摘はなく、要件対応表の証拠説明に Minor 1件が残る。有限結果から全入力の正しさや後続 U11 の guest Worker 接続は主張しない。
