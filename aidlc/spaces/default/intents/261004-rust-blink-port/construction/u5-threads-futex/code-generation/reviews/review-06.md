## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-10T07:01:18Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `/Users/mutoakio/.local/share/mise/installs/bun/1.4.2/bin/bun test aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification/sensor-repair/tests/traceability.test.ts` | 検証済み：Bun1.4.2、exit0、27 pass、0 fail、31 expect、392ms。 | 独立上流による担当・共通欠落、participants、他Unit除外、不正・欠落・重複割当、draft拒否、既存AC/zeroUnit/詳細NFR/BR、target/status/pathの失敗検出が成功。対象は隔離コピーであり、導入TSとのbyte一致も別途確認した。 |
| `/Users/mutoakio/.local/share/mise/installs/bun/1.4.2/bin/bun .codex/tools/aidlc-sensor-traceability.ts --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json` | 検証済み：exit0、pass true、findings_count0、全gap/invalid/missing配列は空。 | 導入済みTSのUnit-aware resolverは承認済み60行の上流割当からU5の10IDsを解決して成功する。対応表自身を期待集合に使っていない。 |
| `aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json` | 検証済み：exit0、pass false、findings_count50、missing_from_upstream_ids50。 | native既定経路は旧組込みの全体要件検査を使用する状態が残る。TS直接成功を正式native成功と読み替えない。assignment-finalizationとsummaryはこの配布制限を正しく未完了として記載し、Step18/19を未tickに保持している。 |
| `aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-summary.md` | 検証済み：exit0、pass true、H2 5、findings_count0。 | 前回のsummary構造欠落は修正されている。 |
| source-manifest36pathsのread-only `git show 7eb1819f52acede33e83775374dd4ee93edf643b:<path>` byte比較、および導入TSと隔離toolsのbyte比較 | 検証済み：36 source pathsは7ebと全一致。aidlc-unit-requirements.tsとaidlc-sensor-traceability.tsは導入版と回帰対象コピーが同bytes。 | エミュレータ製品変更なしと、実際にレビューした修正の同一性を確認。全CIを再実行したとは扱わない。 |
| 承認済みunit-requirement-assignments.json、requirements、Unit/story対応とresolverの限定読取り | ドキュメント根拠／検証済み：60行のowner/participants/allは独立上流入力。resolverは未知requirement/Unit、owner関連重複、未分類・重複行をFAILにし、stories ACとUnitなし経路を保持する。U5はFR2.3/FR5.4/FR9.1、NFR1/2/3/5/7/8/9。 | NFR5を除外せず初期thread上限無し方針へ対応し、TID表現範囲とHost資源エラー、他Unit範囲を保持している。無限資源や全入力成功は主張していない。 |

### Summary

修正TSと承認済み上流割当、U5対応表・概要の実装内容はREADY。native既定sensorはなおFAIL50であり、今回のREADYはU5全作業完了や正式配布更新完了の承認ではない。管理されたframework source修正・native build/release/update後の正式command成功が未完了として残り、親の続行範囲と完了checkpointで解決すべき条件を保持する。
