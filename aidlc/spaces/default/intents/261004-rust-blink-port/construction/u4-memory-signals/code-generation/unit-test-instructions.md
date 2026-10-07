# U4 単体・差分テスト手順

## 2026-10-08 復旧時の実行方針

下記の準備・成功値は過去実装の履歴であり、今回の現在 source の証明として自動採用しない。現在 runner と専用 test files を先に確認し、署名済み CI 4d52be0a の該当ログと現在 bytes の一致で結果を再利用する。再利用できない範囲だけ下記 exact U4 commands を実行する。新規 product defect の syscall/guest ケースは native-first、内部層は test-after。

手元は macOS arm64。mise の Rust/cargo 実体を glob で解決し、nightly-2026-10-01 と --locked を維持する。差分の合否は実機 x86-64 Linux の GitHub Actions で確認する。Docker Desktop は Docker VMM を維持し、scripts/linux-dev.sh の QEMU 結果と実機の結果を混同しない。手元の失敗があれば原因と該当ケースを記録する。

今回は現在 source と各 CI case を対応させる記録復旧が中心。現在ソースでの ASan syscall_args/mmu_ops 各600秒は証拠が結び付かなければ未検証/GAP として Build and Test に渡す。履歴の完走値を現在成功と記さない。件数、比較mask、30秒watchdog、coverage80%、各600秒、依存・toolchainは維持する。

## 現在の観測と準備

Rust cargo test が既存 runner。直前 U2 の workspace success は保存済みの引継ぎ証拠で、U4 target/filter はまだ存在しない。今回 Part 1 では tests を実行していない。以下は承認後に bootstrap し、件数を検査して初めて runnable とする。方法は native-first syscall/guest と内部 layer test-after の custom、Standard（各 component 5〜8 件以上）。

Windows の cargo は実体を使う。native differential は x86-64 Linux で `scripts/linux-dev.sh` から同じ cargo command を実行する（単純な container 作業は wslc 優先、既存 script の必要な環境には Docker を使う）。guest compiler は static x86-64、取得時に version/build args を証拠へ保存。Rust は `rust-toolchain.toml` の nightly、すべて `--locked`。性能測定はしない。

## Runner readiness と exact commands

既存 runner の baseline（承認後、期待 1 件。現在再実行していない）：

```sh
cargo test --locked -p paludarium-kernel --lib tests::memory_syscalls_map_protect_unmap_and_brk -- --exact --nocapture
```

専用 target を作成し、最初の差分実行前に一覧を確認する。初期 memory ケースは 8 件、最終は memory 8 / time 6 / signal 12 の合計 26 件以上。未存在 target / ゼロ件は readiness 失敗。

```sh
cargo test --locked -p paludarium-harness --test diff_u4 -- --list
cargo test --locked -p paludarium-harness --test diff_u4 u4_memory_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u4 u4_time_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u4 u4_signal_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u4 -- --nocapture
```

内部 tests は該当層実装後に作成する。module 名 `u4_tests` として登録し、同 filter の件数を検査する。以下の計画件数は新規件数の下限であり、既存の zero match を pass にしない。

```sh
cargo test --locked -p paludarium-mmu --lib u4_tests:: -- --nocapture
cargo test --locked -p paludarium-kernel --lib u4_tests:: -- --nocapture
cargo test --locked -p paludarium-host --lib u4_tests:: -- --nocapture
cargo test --locked -p paludarium-runtime --lib u4_tests:: -- --nocapture
```

期待：MMU 8、Kernel memory 8 / time 8 / signal 8、Host 8、Runtime 8 件以上。C1/Cpu を変更した場合のみそれぞれ `cargo test --locked -p paludarium-types --lib u4_tests:: -- --nocapture`（5 件以上）、`cargo test --locked -p paludarium-cpu --lib u4_tests:: -- --nocapture`（5 件以上）を追加する。未変更層に空 filter を要求しない。

共有 consumer を変更した時の既存回帰は U4 の単体 command とは分けて evidence に記録し、root の workspace checkpoint で全体を確認する。本手順の run commands は U4 専用 file/filter のみであり、全 workspace sweep を unit command に追加しない。

## データ・native 比較

memory は MAP_FIXED/NOREPLACE、partial unmap/protect、overflow、brk、permission/fault の各 errno/メモリ内容と fault RIP/addr/code をケースにする。アドレスは offset/相対関係へ正規化し、bad request 前後の非破壊性を検査する。

time は fake Host の固定 clock で内部テストする。native の実時刻を固定期待値にしない。成功/errno、tv_nsec 範囲、単調性、sleep の deadline/remaining と割込みを比較し、実行依存値の正規化を明記する。

signals は action/mask、unblockable、default/ignore、pending/nesting、altstack、SIGSEGV/ILL/FPE の siginfo/ucontext、return、malformed frame、EINTR/restart を観測する。ネイティブ signal number だけで合格にせず fault RIP/RSP/保持 GPR/メモリ/定義済み flags と mask を比較する。rflags の Linux 配送 bit と未定義 bit は比較 mask の根拠を保存する。FP/SSE の ABI 保存は既存 register data の roundtrip で、未実装 SSE 命令に依存しない fixture とする。

mock は RecordingHost を拡張した fake clock/wait、制御された interrupt を使う。各 test は独立 memory/Kernel/thread を作り、他 test と mutable state を共有しない。host OS syscall 番号への透過 forwarding は禁止。fixture の native 失敗と emulator mismatch を区別し、各 run の command/status/stdout/stderr/test count を unit evidence に保存する。expectation は毎回 native から取得し、golden を固定しない。

## 有限実行・品質

native と emulator の各差分には既存 30 秒 watchdog を適用し、時間切れ時には child kill/reap。sleep/handler loop/blocked signal を含め親から停止可能な subprocess に隔離する。待機中も cancellation を扱う。timeout/skip/ゼロ件を pass にしない。

Linux 全 workspace line coverage 80%以上、fmt/clippy warnings 0、cargo-deny、crates.io、固定 nightly と SHA 固定 CI は全体 gate の別責務で維持する。閾値を下げない。最終 evidence に測った source revision を記す。

U4 が変更する exact fuzz targets は `fuzz/Cargo.toml` の `syscall_args` と `mmu_ops`。承認後の ASan 実行は pinned nightly の Linux で以下を行い、各予算 600 秒と入力当たり有限 budget を保持する（夜間設定も同じ）。現在は未実行。fake Host と bounded guest CPU により hang を防ぐ。

```sh
cargo fuzz run syscall_args --fuzz-dir fuzz -- -max_total_time=600 -timeout=30
cargo fuzz run mmu_ops --fuzz-dir fuzz -- -max_total_time=600 -timeout=30
```

失敗は再現入力を保存し、修正した source と対応を記録する。背景 build と fuzz/coverage を重ねて速度を主張せず、別 project の process は停止しない。

## 承認後の現在観測（計画時点との区別）

冒頭の未作成/未実行はPart1作成時の観測である。現在は専用 `diff_u4` が実在し、memory10/time8/signal23/live oracle2の計43件を持つ。内部filterも非ゼロで、MMU10/Host8/Kernel32/Runtime11/Cpu5/Types5。過去の全量成功と最終sourceでの新実行を混同せず、具体結果を `evidence.md` と `docs/u4/validation.md` へ保存する。

追加live oracleのrunnable commandは `cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture`（期待2件）。毎回native-only observerをbuildし、write EINTR/SA_RESTARTのframeと単一process stop/continue/killの状態をKernelへ比較する。native fixtureのfork/pipeはguest clone/futexの実装を意味しない。

最終quota/priority修正後のLinux `cargo test --locked -p paludarium-kernel -p paludarium-runtime --lib u4_ -- --nocapture` は32+11pass、上記oracleは2pass。fmt/fuzzfmt/clippyもexit0。fuzz/coverage/deny最終結果はこの追記時点で未完了。期待件数/順序/30秒/80%/各600秒は変更しない。

最終結果追記: Linux workspace coverage gateはexit0、親summary311pass（U4差分43を含む）、line coverage93.48%。ASan syscall_args348580runs/601秒とmmu_ops987393runs/601秒、runner exit0。cargo-deny4category ok/exit0。これらの新実行を上記Part1/中間観測と区別し、rawは `docs/u4/inventory/`、具体集計は `validation-current.json` に保存した。方法・順序・品質下限は変更していない。

## 配送先選択修正後の current scoped commands

上記43件/Kernel32/311coverageは過去sourceの結果として保持する。現在diff_u4は44件（memory10/time8/signal23/live3）、内部6層は76件（MMU10/Host8/Kernel37/Runtime11/Cpu5/Types5）。最終scoped command `cargo test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture` は76pass、`cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture` は3pass。raw rt-provenance-quality-scoped-green.txt。native oracleはRT番号/default、同番号queue FIFO、Process/Thread混在順とqueue別standard coalesceも比較する。guest rt_sigqueueinfo/cloneを追加しない。

最終source37paths hashはsource-hashes-current.json。最新ASan/coverageは区間終了後の別raw/resultに記録し、旧成功で代用しない。methodology/native-first、内部test-after、親watchdog30秒、coverage80%、ASan各600秒は変えない。Cargo.lockは既存deny全4okの測定時とSHA256不変なので同じdependency setのaudit証拠を再利用する。

最終配送先修正の結果: workspace gate exit0、親317pass/0fail/0ignore、5095行/321missed/93.70%。U4diff44、ASan syscall1136975/MMU1564316各601秒、runner exit0。source37 captureとlock不変の証拠はvalidation-current.json/source-hashes-current.json。これは旧311passと中間成功に対する新実行であり、旧失敗は保持する。
