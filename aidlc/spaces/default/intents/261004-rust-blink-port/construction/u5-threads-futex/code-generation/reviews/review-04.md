## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-09T15:59:47Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |

> R-03 Reviewer note: 検証済み：traceability.json の全9 notes が現 source 9aa149786015ad9f789e8527cc30d7f30f2f9482 と preentry 原本を参照し、旧 e8e23fbd・旧 coverage・旧 fuzz 件数の現在結果への混在はない。FR2.3/FR9.1/NFR1/7/8 は43ケース、NFR3 は3256/3825、NFR2 はthreads18531279/futex9935154 runs・各601秒となり、原本を読み取り専用 assertion で照合した。全 target は存在し、code-summary と final-verification とも一致する。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| Python read-only：traceability 全9 notes と target、code-summary、final-proof、coverage JSON、fuzz raw.log/exit.txt を比較 | PASS：9 current-head notes and targets;3256/3825 floor80 13files;18531279/9935154 runs 601s raw | R-03 の全対象説明を確認。数値は保存原本に一致する。初回 coverage failure は履歴と明示され、現成功と区別されている。 |
| Python read-only：source-manifest 36 claim の SHA-256 と final-proof source を比較 | PASS：36 source hashes | 製品 source は前回の独立実行27テストと43差分が検証した bytes のまま。文書修正のため重い CI や fuzz は再実行していない。 |
| Python read-only：最終43 manifest の native/emulated と timeout を再照合 | PASS：43matching manifests、全 timeout false | 今回の要件対応表が指す差分結果を確認。前回は同原本の86 JSON/stdout/stderr 結合も検査済み。有限結果から全入力保証は主張しない。 |
| Python read-only：final-verification SHA-256、source snapshot、historical entries を比較 | PASS：final-verification hash 一致、417 source inventory、73 historical entries が intermediate-e8e23fbd-proof と一致 | 変更した検証記録の hash が再結合され、旧証拠の inventory は保持されている。sibling unit の実ファイルは読まず、現在 unit 内の proof に記録された73行を比較した。traceability は要件成果物として今回のレビュー対象そのものであり、proof の raw evidence hash 対象とは区別した。 |
| Stage validation tools | 個別 validation command の指定なし | required-sections/traceability は stage sensor 宣言。対象ファイルと対応先を確認した。sibling records を読む候補 checker は限定レビューの範囲外であり実行していない。 |

### Summary

R-03 の要件対応表と現検証結果の不整合は修正済みで、今回の文書説明は43ケース・現 coverage・現 fuzz 原本と一致する。未解決の新指摘はなく、製品 source を変えずに文書修正が完了している。
