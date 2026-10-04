# U4 検証記録

native syscall/guestケースを先行取得し、内部層testは実装後に追加した。expectationは各回native x86-64 Linuxから生成し、固定goldenにしない。全command/Red/Greenはunit evidence.mdに保存。

検証済み current: diff_u4 memory10/time8/signal23/live oracle3、計44件全通過。各差分親watchdog30秒、timeout時child kill/reap。内部U4 filterはCpu5/Host8/Kernel37/MMU10/Runtime11/Types5、計76件。exact scoped `cargo test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture`、live `cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture` はexit0。fmt/fuzzfmt/workspace clippy -D warningsもexit0。raw inventory/rt-provenance-quality-scoped-green.txt。

検証済み final gate: `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` exit0、Cargo Running sectionごとの最後の親summaryのみ計317pass/0fail/0ignore。U1diff16/U2diff38/U4diff44/parallel10を含む。5095行/321missed/93.70% >=80、regions90.73%。raw inventory/coverage-provenance-final.txt、SHA256 d34bcea1ccc21bb3da46f451373b94ffa4b777fd2fea63fe415610024e09f6ce。doctestはllvm-cov集計に含まない。

ASan逐次 `cargo fuzz run syscall_args --fuzz-dir fuzz -- -max_total_time=600 -timeout=30` は1136975runs/601秒、続くmmu_ops同optionsは1564316runs/601秒、runner exit0。既存LSAN suppressionを維持、他build/auditを重ねない。raw inventory/fuzz-syscall-provenance-final.txt、fuzz-mmu-provenance-final.txt。source captureはunit source-hashes-current.json、37paths、SHA2561283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c、最終再照合changed0。

Cargo.lock SHA2564cfdcc2b2c4a47789e4ee5dfb61d46b529193b3494a92de416e783f98ef2e7c4はinventory/cargo-deny-final.txtのexit0/全4category ok時から不変。同じdependency setのaudit証拠を再利用し、新audit実行とは扱わない。

配送順のnative Red（低RT番号、Process/Thread優先と別coalescing）およびclippy fixture OR-pattern/blocked同期faultfixture誤期待を保持する。旧311pass/93.48%・旧ASanと番号優先のみの中間899904/967303各601秒は履歴であり、上記finalと混同しない。過去MAP_SHARED古い期待とu2_alu30秒timeout、audit失敗も保持し、timeout原因を並行負荷と断定しない。

NFR5に根拠のない生産RT queue quotaはない。driver64syscall/64wait/Cpu64/MMU256予算は入力を有限にする試験条件。standardは番号＋target単位でcoalesce、各queueのRT同番号FIFO、低番号優先、Thread queue優先とSIGKILL最優先をnative/internalで確認。SI_QUEUE native-only観測はguest対応を意味しない。

固定probe/aubeのnative sample/static位置/bounded traceはsyscall-matrix.md、frameとpending比較条件はsignal-abi.md。全任意入力経路、CI remote/macOS/wasm/browser、全program emulator完走/U10、file-backed mmap/U7、guest clone/futex/U5は本検証の主張に含めない。性能値を測定/主張しない。
