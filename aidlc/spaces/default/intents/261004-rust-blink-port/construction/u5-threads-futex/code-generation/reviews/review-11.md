## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T14:32:00Z
**Iteration:** 3
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |
| R-04 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification/step28-source-applicability.md > 保存された現行CIの適用範囲・正式再検証 | 承認済みverify-current-u1-quality-fixed.pyを実行したがexit1となり、現行品質照合のcurrent_bindingで`current/signed source mismatch`が発生した。監査は367入力中mise.tomlだけが相違すると明示しているが、この相違を記録するだけでは既存確認コマンドの完全一致条件を満たせず、今回の最終確認は未成立である。 | 失敗した現行と署名済み原本の差分を特定し、旧原本検査を保持したまま公式preview設定更新を厳密に別照合する確認方法を用意する。確認方法の変更を人に確認した後に再検証し、exit0になるまで完了確認成功と記録しない。 | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-generation-questions.md > Plan Approval | 正式生成された質問ファイルはH2が1個で、required-sectionsがpass:false・findings_count:1を返す。別の内容確認ファイルのLooks correctは存在するが、この構造検査の失敗そのものは解消していない。製品不具合や旧証拠の誤用を示す失敗ではない。 | 上流の質問生成形式または質問ファイルの構造検査対象を整合し、正式再生成後にrequired-sectionsを再実行する。それまではこの失敗を保持し、全文書検査成功と記載しない。 | Accepted risk |
| R-06 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-summary.md > 「今回の確認候補修正（Steps29〜32）」の節 | この節は「現行367入力中366完全一致・mise.tomlのexact preview版差分だけ」と、2.11.1-preview.20261012.1 を現行の設定として現在形で書いている。実際の mise.toml は 2.11.1-preview.20261015.1 で、この記述はもう成り立たない。Step 33 の説明は計画にあるが、code-summary と unit-test-instructions の旧節には「履歴」と明記した但し書きがない。旧候補 verify-current-u5-preview-bound.py は今の mise.toml を拒否するはずだが、それは書かれていない。 | code-summary.md の先頭に Step 33 の短い節を足し、Steps29〜32 の mise.toml 差分と最終確認候補は 20261012.1 時点の履歴で、現在の正式確認コマンドは U2 の u2_candidate.py だと明記する。 | New |
| R-07 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-generation-plan.md > Step 33 の節 | Step 33 が確かめるのは source-manifest の 38 ファイルだけで、U5 の実行経路が使う別クレートは範囲外である。paludarium-runtime は paludarium-jit に依存し、今回 jit の block/bridge/emit/lib が変わった。ただし runtime/src/lib.rs の `Config.jit` の注記と `NoopCodeCache` の使用から、ネイティブ経路は JIT を使わず、U5 のネイティブ差分とカバレッジの結論は変わらないと読める。wasm の jit と abi の変更は、記録にある U9 の module・Node/Safari 証拠の再利用範囲に影響する。 | Step 33 の節に「manifest 外の依存クレート（jit、wasm abi）は変わったが、ネイティブ経路は NoopCodeCache で影響せず、U9 の module 証拠の再利用は履歴で、新しく主張しない」と一文足す。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| git diff --quiet e4f84768 -- (U5 manifest 38 paths) | 指揮役が実行して exit 0 と報告。私は shell を使わず再実行していない | manifest の 38 パスに変更クレート側のファイル（jit、wasm abi.rs、diff_u14.rs、tests/guests/u14、packages/paludarium-wasm）は含まれないことを、source-manifest.json を読んで確かめた。mise.toml も含まれない。したがって変更なしの結論は整合する |

### Summary

U5 の source-manifest は、U14 の JIT 変更ファイルとも mise.toml とも重ならず、Step 33（記録・製品とも変更しない）は manifest の範囲では正直で十分である。残りは code-summary にある旧 mise.toml の現在形の記述と、manifest 外の依存クレートの変更に触れていない点で、どちらも Minor にとどまる。
