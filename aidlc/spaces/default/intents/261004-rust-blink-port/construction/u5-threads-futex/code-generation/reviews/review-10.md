## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-15T17:31:35Z
**Iteration:** 2
**Verdict Dictated:** no
**Request ID:** review:d0030fe092d9e9e26ce0dea9d9cf8989

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | crates/paludarium-kernel/src/threads.rs > ThreadGroup::set_timer（50–55行）; crates/paludarium-kernel/src/syscalls.rs > sleep（190–200行） | 別スレッドが共有 ITIMER_REAL を更新しても既存 sleep に通知されない。親が2秒 nanosleep、子が50ms sleep後に50msタイマーを設定して個別exitする限定ゲストで、SIGALRM終了は約100msではなく2.011秒後だった（下記実コマンド）。set_timer は値だけを変更し、親は更新前に計算した deadline の Host wait_until 内に留まり、他のworkerがなくなると期限を検査する実行主体がない。長いsleepではタイマーによる解除がその全期間停止する。これはU5が追加した共有process timerと既存待機の接続不良である。 | タイマー更新と待機を接続し、全workerが眠っていても更新後の期限で満了・配送するようにする。更新通知だけで nanosleep を誤って EINTR にせず、期限を再計算する仕組みを用意する。別スレッドからのタイマー設定・短縮・解除を、Host待機に入ったことを同期できる単体テストと有限native差分ケースで検証する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-kernel/src/threads.rs > thread_syscall（248–249行）・futex_wait（385–419行） | FUTEX_WAIT のsignal中断は常に -EINTR をRAXに設定して checkpointへ進み、SA_RESTART の再開状態を作らない。SA_RESTART付き SIGUSR1 handlerを登録し、親のtimeoutなしWAIT中に子がtgkill、続いてWAKEする限定ゲストは handler復帰後 -4を返した（下記実コマンド）。LinuxのWAIT/WAIT_BITSETはSA_RESTART付きhandler後に再開する。既存case21はSA_RESTARTなしのタイマー割込みだけなので27/27ではこの不一致を検出しない。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) | WAIT/WAIT_BITSETでhandler後の再開とSA_RESTARTなしのEINTRを分ける。相対timeout付きWAITも経過時間を引き継ぎ、再開で期限を延長しない。SA_RESTARTあり・なし、handler中の値変更、有限timeoutについてnative-first差分を追加する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json > coverage[].notes（FR2.3、FR9.1、NFR1、NFR2、NFR3、NFR7、NFR8） | 現在の要件対応表の証拠説明が旧 e8e23fbd、38ケース、3226/3797 coverage、旧 fuzz 実行回数のままであり、現 code-summary と final-proof の 9aa14978、43ケース、3256/3825、今回 fuzz 原本に対応していない。実装・テスト target は存在し、今回の品質成功自体は原本で確認できるため製品動作を妨げない。 | notes を今回の source と原本に合わせ、旧結果を記載する場合は履歴であることを明示する。 | Resolved (reviewer) |
| R-04 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification/step28-source-applicability.md > 保存された現行CIの適用範囲・正式再検証 | 承認済みverify-current-u1-quality-fixed.pyを実行したがexit1となり、現行品質照合のcurrent_bindingで`current/signed source mismatch`が発生した。監査は367入力中mise.tomlだけが相違すると明示しているが、この相違を記録するだけでは既存確認コマンドの完全一致条件を満たせず、今回の最終確認は未成立である。 | 失敗した現行と署名済み原本の差分を特定し、旧原本検査を保持したまま公式preview設定更新を厳密に別照合する確認方法を用意する。確認方法の変更を人に確認した後に再検証し、exit0になるまで完了確認成功と記録しない。 | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/code-generation-questions.md > Plan Approval | 正式生成された質問ファイルはH2が1個で、required-sectionsがpass:false・findings_count:1を返す。別の内容確認ファイルのLooks correctは存在するが、この構造検査の失敗そのものは解消していない。製品不具合や旧証拠の誤用を示す失敗ではない。 | 上流の質問生成形式または質問ファイルの構造検査対象を整合し、正式再生成後にrequired-sectionsを再実行する。それまではこの失敗を保持し、全文書検査成功と記載しない。 | Unresolved |

> R-05 Reviewer note: 検証済み：正式質問ファイルのrequired-sectionsはprocess exit0だがpass false、H2=1、findings_count1を再現した。計画／手順／summaryとtraceabilityは独立検査でPASSだが、これらで質問ファイル自身の構造FAILを解消したとは扱わない。質問生成形式／検査対象の整合が未解決であり、全書類検査成功とは記載しない。製品機能の失敗や旧証拠改変を示す結果ではない。

### Validation Tool Results

U5の既読契約と現行計画・手順・summary・traceability、38 claimed pathsを対象に差分確認した。製品source／成果物／manifestは変更していない。Pythonは `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3`、Rustはnightly-2026-10-11のcargo／rustc実体を使用した。

| Tool | Result | Interpretation |
|---|---|---|
| `RUSTC=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-11-aarch64-apple-darwin/bin/rustc /Users/mutoakio/.rustup/toolchains/nightly-2026-10-11-aarch64-apple-darwin/bin/cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests::` | 検証済み：exit0、Host7／Kernel27／MMU6／Runtime6、計46件。全crate ignored0／failed0。 | wake-before-wait、spawn/join／panic、clone/TLS/TID、clear_child_tid、futex勝者／bitset／timeout／signal restart、timer metadata、共有MMU、worker終了／kill／回収の限定回帰成功。Linux native43差分や全入力の証明には代用しない。 |
| `python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/verification -p test_preview_source_binding.py -v` | 検証済み：22件、OK、exit0。 | preview版のexact bytes差分、旧現行inventory／hash、他tool・asset・source・lock変更、欠落／余分、symlink／linked parent／path escape拒否、repository accessの限定と成功・例外時復元を確認。合計68件の独立限定テストが成功した。 |
| U5 manifestと署名02375d54 blobの直接bytes照合 | 検証済み：38一意claims、欠落0、全38件が `02375d54d11e72a83fe3ec7be8e2beb28029658c` のblobと一致。旧62611からの担当差分は `crates/paludarium-runtime/src/workers.rs` 一件だけ。 | SCMは読取 `git cat-file`／`git diff` のみ。既存clone／futex queue／Host wait実装を再生成したものではない。 |
| workers.rsの差分読取とU5境界の確認 | 検証済み：変更はaccelerated時のcounted hook／eligible／hint接続とopt-in診断counter。通常run_cached経路、各budget境界のkill確認・Kernel checkpoint、Kernel.handle、exec時DecodeCache再生成、child spawn／spawn失敗時abandon／handle保存を保持する。 | U5のworker所有・回収・共有資源をJIT診断へ混同しない。futexの比較登録／wake／finishは同じqueue lock、MMU取得順序、勝者一回確定の既存契約を保持し、限定テストも成功した。 |
| `aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json` | 検証済み：exit0、pass true、missing／invalid／orphans／gaps空、findings_count0。 | U5の上流対応表検査成功。保存された他時点の実測や他Unitの未達が消えたという意味ではない。 |
| `aidlc engine sensor-required-sections --stage code-generation --output-path <U5 code-generationの対象ファイル>` | 検証済み：plan H2=10／instructions H2=11／summary H2=7、各exit0／pass true／findings0。questionsはexit0／pass false／H2=1／findings1。 | 全4対象に同じ正式入口を使用した。questionsの失敗をR-05として保持し、他3文書のPASSで上書きしない。 |
| 現在のConstruction Verification Command `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/diagnostic-v2/current-verifier/verify.py` | このレビューでは独立再実行していない。親提供記録：直近U2正式実行17:18:26〜17:28:55Z、proof先頭66e9ba9b、exit0／stderr0／evidence_unchanged true、allHistoricalPredicates PASS。 | 約10分の全chain重複と、許可外のsibling成果物参照を避けた。親提供記録はこのレビューの独立全実行・receipt独立読取とは区別する。不実行だけでREADYを拒否せず、38source照合と68限定回帰で今回の判断を補強した。 |
| 保存証拠の適用限界 | U5 summaryは旧専用Linux43差分／固定13ファイル3869/4487 coverage／threads・futex各601秒を当時の署名sourceへ限定し、現在の専用新測定とは主張していない。今回これらの重い試験は実行していない。 | 親が提示した現行35+7／全歴史predicate成功も、新しいU5専用coverage／fresh native／browser／600秒fuzzの今回実行へ読み替えない。JIT正式性能FAIL、現在NOT_REMEASURED、U9 coverage GAP、requirementsComplete falseを保持し、U5のREADYで解消したとは扱わない。 |

### Summary

U5の現行source整合と68件の限定回帰は成功し、新しいCritical／Major不備は確認しなかった。R-05の質問ファイル構造FAILはMinorとして残す。今回のREADYは全体検証の独立再実行や、新しい全環境・全入力の保証ではない。
