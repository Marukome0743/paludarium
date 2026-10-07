# U4 メモリ・時刻・シグナル実装

anonymous private/shared mmap、munmap/mprotect/brk、typed Host realtime/monotonic clockとcancellable wait、clock_gettime/nanosleep/clock_nanosleep、ITIMER_REAL、checked Linux x86-64 signal frame/returnと単一guest process/threadの配送を実装した。KernelがCpuStateを所有し、CpuはKernel/Hostへ依存しない。Host waitをMMU lock内で呼ばず、syscall番号をhostへ透過転送しない。

memoryのhint/rounding/FIXED/NOREPLACE/offset preflightとholeまでのmprotect prefixをnativeに合わせた。C1/C4 fault metadataはfetch/mapped/presentを発生時に固定しconsumerを同一変更で更新。signal codecはsiginfo/ucontext/FP状態、nested altstack、mask/privileged flags、canonical context、malformed returnを扱う。REP continuationはhandlerへ持ち込まずreturn context一致時だけ復元する。stop/continueと停止中kill、wait cancellation、転送前write SA_RESTARTをRuntimeへ接続した。

配送先はtyped Process/Threadで保持する。SIGKILL最優先の後Thread queueをProcess queueより先に選び、各queue内はstandard優先・低いRT番号優先・同番号FIFO。standard coalescingは番号とtargetの組ごと。kill/host inbox/timerはProcess、tkill/tgkillと同期faultはThread。配送とwrite restart previewは同じselectorを使う。生産RT queueに根拠のないquotaを設けない。

## 現在の検証済み事項

最終scoped commandは `cargo test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture`、76pass（Kernel37/Runtime11/MMU10/Host8/Cpu5/Types5）。`cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture` はlive3oracle通過。fmt/fuzzfmt/workspace clippy warnings0もexit0。raw `docs/u4/inventory/rt-provenance-quality-scoped-green.txt` に保存済み、完全commandと結果はevidence.md。

native mixed modes4/5（kill35→tkill/tgkill36）は36:-6→35:0、mode6同番号35は-6→0、mode7standard10はtargetごとcoalesceして-6→0、修正後Kernel全出力一致。修正前逆順/配送欠落のRedも保持する。native-only Process/Thread各queueのSI_QUEUE FIFO観測と内部metadata回帰を対応させ、guest rt_sigqueueinfoを追加したとは主張しない。mask、SIGKILL、stop/continue、同期fault、restart previewを内部/既存live回帰で確認した。

専用diff_u4はmemory10/time8/signal23/live3の計44件。最終workspaceで44件全通過を確認した。37application pathsの最終captureは `source-hashes-current.json`、SHA256 `1283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c`。最終ASan逐次runner exit0、syscall_args1136975/mmu_ops1564316 runs、各601秒（予算600/timeout30）。最終 `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit0、親summary317pass/0fail/0ignore（U1差分16/U2差分38/U4差分44/parallel10）、5095行/321missed/93.70%。raw coverage-provenance-final.txt SHA256 d34bcea1ccc21bb3da46f451373b94ffa4b777fd2fea63fe415610024e09f6ce。詳細validation-current.json、doctest集計なし。

Cargo.lock SHA256 `4cfdcc2b2c4a47789e4ee5dfb61d46b529193b3494a92de416e783f98ef2e7c4` は既存 `cargo-deny --locked check` exit0/advisories,bans,licenses,sources全ok時から不変。同じdependency setのaudit証拠を再利用し、新auditを実行したとは記録しない。

## 保持する履歴

番号/target選択修正前のworkspace coverageは311pass/0fail/0ignore、5049行/329missed/93.48%、raw `coverage-quota-final.txt`。旧ASan syscall348580/MMU987393各601秒、番号優先のみの中間ASan syscall899904/MMU967303各601秒もrunner exit0。すべて現在sourceの最終証明から区別し、旧hash/validationを保存する。

初回MAP_SHAREDの古い期待、U2 u2_aluの30秒watchdog、clippy fixture OR-pattern、blocked同期fault fixtureの誤期待、配送順native Redと依存audit保存dir/readonly失敗を削除しない。timeout原因を背景負荷と断定しない。閾値80%、差分30秒、ASan各600秒を維持する。

## 検証の限界

固定probe8checks/aube versionのnative sampleとstatic syscall位置/bounded traceはdocs/u4/syscall-matrix.md。emulator全program完走・全任意入力経路の証明ではない。CI remote/macOS/wasm/browser、追加clock拡張、handler内FS/GS base変更の追加native比較は未検証。file-backed mmap/U7、guest clone/futex/U5、SSE/U3、wasm/U11、JIT/U14は対応unitへ残す。性能測定/主張を行わない。

## 成果物

code-generation-plan.md、unit-test-instructions.md、code-summary.md、traceability.json、source-manifest.json。evidence.md、source hashes、validation-current.json、docs/u4のABI/検証/trace説明と追跡rawを独立検証に用いる。U1/U2成果物・レビューは変更しない。最終sourceと証拠を整合し、rootの独立検証用に固定する。
