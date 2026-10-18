## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-13T18:51:48Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |
| R-04 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification/step28-source-applicability.md > 保存された現行CIの適用範囲・正式再検証 | 承認済みverify-current-u1-quality-fixed.pyを実行したがexit1となり、現行品質照合のcurrent_bindingで`current/signed source mismatch`が発生した。監査は367入力中mise.tomlだけが相違すると明示しているが、この相違を記録するだけでは既存確認コマンドの完全一致条件を満たせず、今回の最終確認は未成立である。 | 失敗した現行と署名済み原本の差分を特定し、旧原本検査を保持したまま公式preview設定更新を厳密に別照合する確認方法を用意する。確認方法の変更を人に確認した後に再検証し、exit0になるまで完了確認成功と記録しない。 | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-generation-questions.md > Plan Approval | 正式生成された質問ファイルはH2が1個で、required-sectionsがpass:false・findings_count:1を返す。別の内容確認ファイルのLooks correctは存在するが、この構造検査の失敗そのものは解消していない。製品不具合や旧証拠の誤用を示す失敗ではない。 | 上流の質問生成形式または質問ファイルの構造検査対象を整合し、正式再生成後にrequired-sectionsを再実行する。それまではこの失敗を保持し、全文書検査成功と記載しない。 | Unresolved |

> R-04 Reviewer note: 検証済み：新候補の入力監査を独立実行し、署名head62611f2556c4caf1470a7eb4471269d92611db6eの367入力中366完全一致と、mise.tomlのAI-DLC版2.11.0→2.11.1-preview.20261012.1だけのexact bytes差分を確認した。旧checker、quality helper、bindingをhash固定し、旧legacy.main全体を署名ソースviewで実行するため、完全一致条件を全mise除外へ緩めていない。候補の全診断exit0は保存記録の根拠であり、このレビューで新たに全診断した結果ではない。新コマンドの正式承認・正式最終確認・完了承認は未完了として維持する。

> R-05 Reviewer note: 検証済み：正式required-sectionsを再実行し、管理されたcode-generation-questions.mdはH2が1個、pass:false、findings_count:1だった。別のstep32-summary-questions.mdのLooks correctは確認できるが、この構造FAILを解消したとは扱えない。概要はこの失敗を保持しており、今回の確認候補修正の製品・証拠検査を否定する結果ではない。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification -p test_preview_source_binding.py | exit0、22件成功 | 検証済み。想定外version、他tool・asset・source・lock、欠落・追加、digest、symlink、旧現行混同、限定jj routingと5module参照復元を検査する。 |
| cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests:: | exit0、Host7／Kernel27／MMU6／Runtime6、計46件、ignored0 | 検証済み。nightly-2026-10-11の実体cargoを、同toolchainのRUSTC／RUSTDOC明示指定で実行したmacOS内部回帰。Linux43差分・3OS・coverageの新規実行とは区別する。 |
| 新helperのcompare_inputsを使った独立367入力監査 | exit0、366一致、exact_preview_delta:mise.toml | 検証済み。全367入力の署名bytesをreadonly jj file showで再取得し、現行safe_readと元digestへ照合した。helper SHA ddab606d63467412c47b0ac2fbeb71c61e7d9801ad548edc9aa5f0e0a7749ea5、候補 SHA1214b817960798c1bb1448969145242104b378114f3c403a30689fe46d9987d9も一致。 |
| aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json | exit0、pass:true、findings_count:0 | 検証済み。正式Unit対応表検査に新しい欠落なし。 |
| aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-generation-questions.md | exit0、pass:false、H2=1、findings_count:1 | 検証済み。R-05継続。コマンドexit0と構造合格は区別する。 |
| step31-formal-sensors.jsonのplan／instructions／summary | 保存出力はpass:true、findings_count:0 | ドキュメント根拠。このレビューではこれら3件を再実行せず、現行文書と保存結果を読んだ。 |
| step31-diagnostic-attempts.jsonの全候補診断 | 最終session43232はexit0、先行exit1／exit130を保持 | ドキュメント根拠。全34必須品質jobと全履歴predicateを保持した保存診断。新候補の長時間全診断をこのレビューでは再実行しておらず、正式checkpoint合格の主張ではない。既存38回帰を含む計60回帰の保存成功も同様に区別する。 |
| 旧承認済みverify-current-u1-quality-fixed.py | 前レビューでexit1、current/signed source mismatch | 既知失敗の保持。変更していない旧checkerを今回同条件で再実行していない。新候補は旧checker全体を署名viewへ適用し、現行preview差分を別照合する。 |

### Summary

今回の候補は旧の署名済み原本・全検査を保持しながら、公式preview版だけの現行設定差分を限定して照合する。新しい阻害指摘はなくREADYとするが、質問構造のMinorは継続し、新コマンドの正式承認と正式再検証を済ませるまではU5完了確認成功とは記録できない。
