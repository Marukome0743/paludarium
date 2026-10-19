## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-10T17:27:51Z
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
| sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json | PASS、exit 0、findings 0 | 要件原本から独立に抽出した60 IDsと全対応集合が一致。U5必須10 OK、他担当40 Deferred、集約10 N/Aで他Unitの実装をU5のOKにしていない。 |
| sensor-required-sections：plan、instructions、summary | 3件PASS、exit 0、findings 0 | 必須文書構造を満たす。 |
| step25-formal-sensors.jsonの初回・修正後原本 | 初回exit0/pass:false/findings50；修正後exit0/pass:true/findings0 | exit0だけを成功にせず、全体要件の分類追加による文書整合を記録する。frameworkと製品を変更していない。 |
| 隔離checkoutのjj --ignore-working-copy file showとdiff | 38/38担当パスがc8e119938eef951a07ab7080f3d6f0967db7358fと一致；直前U3 headから診断helper/workflowの2pathのみ追加 | 製品・fixture・比較規則不変の主張を確認した。rootにcommitが未取得だったため、親から指定された隔離checkoutを読取り専用で使用した。 |
| 入力・原本の独立ハッシュ検査 | 現在320入力・両lock一致；6ジョブのbefore/after各320一致；426 rawhash一致；proof SHA bac8a9fafae99f13b5c94bc1ad9aaddbd2bfcaf4589746f66af0452ea7f02d44一致 | 全実行と現在のsource対応を独立に確認した。 |
| GitHub connector fetch_workflow_run_jobs | CI38070022172全6ジョブcompleted/success | 保存されたjob成功を独立に確認。署名Verifiedは保存GitHub verification receiptで確認した。 |
| differential-manifest.jsonと生ログ・比較契約の読取 | ケース0〜42の43件、native/emulated全一致、timeoutなし、case16終了17・他0 | fresh Linux native生成、TID関係・経過区間boolの既存正規化、30秒watchdog・kill/reapを維持する。有限のtimer guestと正確な内部同期検査を区別している。 |
| 3OS lib.logと品質exit原本 | 各Host7/Kernel27/MMU6/Runtime6、計46、failed/ignored0；fmt・Clippy・依存4検査の実exit各0 | 0件やskipを合格にしていない。 |
| 固定13ファイルLCOVの独立再集計 | ファイル集合・各DA行数/実行行がproofと一致、3869/4487＝86.22687764653443% | 旧13ファイルと従来の分母規則を保持し、旧3825行を現在の分母として使っていない。80%下限を満たす。 |
| kernel_threads_u5 / kernel_futex_u5の生ログ・symbols・compiler/settings | 各601秒、10037269/9033344 runs、実exit0、__asan_init/__lsan symbolsあり；実rustc32dba69d/LLVM23.1.3、address、seed1/timeout30/rss2048/detect_leaks1/suppression | 保守的80入力dependency hashと両lockが現在一致。旧nightly10-01の結果を現行fuzzへ流用していない。 |
| 固定U9 proof/reuse 2ファイルとの照合 | U9の316全入力・保守的88入力closureが現行一致 | 直前の独立U9レビューで確認した同module/native SHA、Node/Safari20の共有機能だけを限定再利用する。guest clone/futex43件、native Host割当、U11完了、今回fresh browser実行とは呼ばない。 |
| verify-current-u1-u7-u9-u3-u5.py AST構文検査 | 構文OK、未実行 | 人のコマンド変更承認を待つ候補として扱った。 |

### Summary

検証済み：現行製品不変の再確認として、C2/C4/C5/C8/C10のスレッド・futex・worker境界と証拠の適用範囲に新しい不整合は確認されなかった。futex比較と登録のqueue lock、wake/timeout競合の一度だけの決定、Host workerへの割当と回収、NFR5の設定上限を追加しない責務分担を確認した。旧失敗・過去snapshot・今回の実行・限定browser再利用を区別した範囲でREADYとする。

未検証：任意入力の完全な安全性、全probe/aube機能、wasm guest Worker接続のU11完了、並行セッションID競合の完全解消。NFR5は無限資源を保証する主張ではない。新canonicalの実行と人の完了承認は親担当の後続手順として残る。
