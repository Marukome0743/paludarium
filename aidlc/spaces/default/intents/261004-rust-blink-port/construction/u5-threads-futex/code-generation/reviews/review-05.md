## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-10T06:22:35Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json` | 検証済み：command exit 0、pass false、findings_count 51、missing_from_upstream_ids 51。gaps/orphans/invalid_entries/invalid_targetsは空。 | 保存対応表はU5担当9 IDsのみ。全体要件の残り51 IDsに対する分類がsensor基準では欠落している。製品clone/futex欠落の証明とは扱わず、このsensorをPASSと報告しない。親の完了確認でこの文書制限を保持する。 |
| `aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-summary.md` | 検証済み：command exit 0、pass false、H2 0、findings_count 2。 | summaryは本文のみで必須H2構造を満たしていない。製品欠陥とは別の文書検査失敗であり、PASSと報告しない。成果物は本レビューでは編集しない。 |
| `/Users/mutoakio/.cargo/bin/cargo +nightly-2026-10-01 test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests:: -- --nocapture` | 検証済み：exit 0、Host7/Kernel27/MMU6/Runtime6、合計46 passed、0 failed、0 ignored。 | clone TLS/TID/dependencies、clear-child-tid、futex bitset/mismatch/fault/単一勝者、通知先行保持、timer metadataと実中断の区別、worker join/spawn失敗/killを現在sourceで確認。worker_panic_is_errorの意図したpanic出力はテスト成功として区別する。 |
| source-manifest存在検査とread-only `git show 7eb1819f52acede33e83775374dd4ee93edf643b:<path>` byte比較 | 検証済み：36 claims、欠落0、36関連pathsが現在7ebと全一致。 | 現在source bindingを旧9aa14978の417source/43差分/coverage/sanitizer/browser保存観測から区別した。旧全sourceと現在一致するとの主張はこの限定検査ではしない。 |
| 現在futex.rs、threads.rs futex_wait、inbox.rs owner receipt、Runtime workers.rsの限定読取り | 検証済み／ドキュメント根拠：compare/register/wakeは同queue mutex、MMUは後から取得。wake/timeout/interruptのfinishを同lockで決定し、owner drainがtimer/control種別を取得、process drainは種別を消さない。worker panicは製品Host errorとなりgroup停止とfinishへ進む。 | U5共有状態・Host worker・取消と回収の責務に新しい製品上の矛盾を確認しなかった。Linux native全43差分の新実行をこのコード確認で代替しない。 |

### Summary

検証済み：現在のU5限定46件と36pathsのsource bindingは成功し、新しい製品阻害要因は見つからなかったため製品レビューはREADY。限定sensor2件は保存文書の分類・見出し構造についてFAILであり、正式完了確認の成功とは同一視しない。Linux全43差分、80%coverage、各600秒sanitizer、Node/実Safari、全CIは再実行しておらず、歴史的証拠の適用範囲を超える成功を主張しない。
