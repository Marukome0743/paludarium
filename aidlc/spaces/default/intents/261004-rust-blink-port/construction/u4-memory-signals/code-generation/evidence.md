# U4 実装の検証記録

## 開始と runner baseline

- 承認ブリーフ `.aidlc-engine/u4-approved-implementation-brief.md` を全文読取。正式 `aidlc-testing-posture.ts verify --unit u4-memory-signals` は ok/approved/receiptValid/execution_allowed 全 true。
- `aidlc-state.ts unit start --stage code-generation --unit u4-memory-signals`：exit 0、UNIT_STARTED、2026-10-06T00:29:39Z。
- `$env:USERPROFILE/.cargo/bin/cargo.exe test --locked -p paludarium-kernel --lib tests::memory_syscalls_map_protect_unmap_and_brk -- --exact --nocapture`：exit 0、1 passed / 0 failed / 10 filtered。今回の Windows baseline 観測。Linux native 差分の合格を意味しない。
- 読取時 `tests/guests/insn/common.h` は存在しなかった。production は変更せず、U4 fixture に raw syscall helper を独立作成する。

- Linux readiness: `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u4 -- --list` exit 0、memory exact cases 8 tests / 0 benchmarks。case names: break, fixed_invalid_non_destructive, noreplace_non_destructive, protect_holes, shared_anonymous, unaligned_hint, unmap_holes_fault, zero_length（全て u4_memory_ prefix）。まだ意味論の実行合格ではない。
- 対象 compile 状態の read-only `docker exec 5795db602a73 ps ...` は container 完了・自動削除後だったため exit 1 `No such container`。runner 自体は上記 exit 0。

## 固定 native 取得対象の追加 syscall trace

検証済み：`docker run --rm --platform linux/amd64 -v paludarium-u2-rebuild-target:/cache:ro -v paludarium-work:/work -w /work paludarium-dev bash -lc '<下記>'` exit 0。

```sh
mkdir -p target/u4-evidence
sha256sum /cache/probe/x86_64-unknown-linux-musl/release/probe /cache/aube/x86_64-unknown-linux-musl/release/aube
timeout 30 strace -f -qq -e trace=mmap,munmap,mprotect,brk,clock_gettime,nanosleep,clock_nanosleep,rt_sigaction,rt_sigprocmask,rt_sigreturn,sigaltstack,kill,tkill,tgkill -o target/u4-evidence/probe-native-trace.txt /cache/probe/x86_64-unknown-linux-musl/release/probe > target/u4-evidence/probe-native.stdout.txt 2> target/u4-evidence/probe-native.stderr.txt
timeout 30 strace -f -qq -e trace=mmap,munmap,mprotect,brk,clock_gettime,nanosleep,clock_nanosleep,rt_sigaction,rt_sigprocmask,rt_sigreturn,sigaltstack,kill,tkill,tgkill -o target/u4-evidence/aube-version-native-trace.txt /cache/aube/x86_64-unknown-linux-musl/release/aube --version > target/u4-evidence/aube-version.stdout.txt 2> target/u4-evidence/aube-version.stderr.txt
```

hash は probe15e90407b6cc2dc8389048805475fb9c7b11d3e10f89c1da0d52dad7b1c99292、aubeff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a（固定 rebuild receipt と一致）。probe exit0: PASS tokio-timer / unix-stream-pair / rayon / mutex-condvar / fs-basic / fs-hardlink / fs-symlink / fs-flock。aube --version exit0: `2.6.1 linux-x64 (2026-10-05)`。

関連 trace 集計（両ファイル）：brk4、mmap92、mprotect46、munmap75、rt_sigaction10、rt_sigprocmask100、sigaltstack70。clock/sleep 等はこの sample では観測なし。VDSO 使用等の原因は未検証であり、raw native ケースで syscall ABI を追加確認する。native の選択した実行 sample であり、emulator の full probe/aube 合格ではない。raw txt は Linux volume `/work/target/u4-evidence/` に保存済みで、最終成果物へ回収する。
初回 memory command は container `bash -lc` が cargo PATH を変え、exit1 `cargo: command not found`。test 自体は実行されていない。`bash -c` に修正して実行し、semantic Red と区別する。

## Memory 修正前の native 比較
`bash scripts/linux-dev.sh bash -c 'set -o pipefail; mkdir -p target/u4-evidence; cargo test --locked -p paludarium-harness --test diff_u4 u4_memory_ -- --nocapture 2>&1 | tee target/u4-evidence/memory-red.txt; exit ${PIPESTATUS[0]}'` は exit 1、5 passed / 3 failed。shared anonymous は native 成功（page bytes 41/42）、emu -EINVAL。unaligned hint は native が指定アドレスを page-align して採用、emu は別アドレス。mprotect prot=8 は native 0、emu -EINVAL。このビットは PROT_SEM。無効固定 range の既存 mapping、NOREPLACE、zero length、brk、unmap 後 SIGSEGV は一致。全結果は production 修正前の観測。

## Memory 内部回帰と Linux 環境待機
検証済み: Windows `cargo test --locked -p paludarium-kernel --lib u4_memory_ -- --nocapture` exit0、8 passed、11 filtered。`cargo test --locked -p paludarium-mmu --lib u4_memory_ -- --nocapture` exit0、8 passed、19 filtered。MMU は production 変更なし、既存 checked-range/zero-fill/protection/brk 経路を追加回帰で確認。
Linux Green 初回は無出力のまま停滞し、Get-CimInstance で exact memory-green.txt command の Docker CLI PID25060 を再照合して停止、exit1で回収（テスト結果なし）。DOCKER を実体 `C:/Program Files/Docker/Docker/resources/bin/docker.exe` へ指定した再試行も無出力。自身 command の PID27376 のみ再照合して停止し exit1 で回収。Linux Green は未検証。
`docker.exe info --format {{.ServerVersion}}` を Start-Process/WaitForExit(30000) で読み取り診断: DOCKER_INFO_TIMEOUT30、stdout/stderr空。daemon 接続の停滞は観測、原因は未検証。他 project tar/container は停止していない。

## 中間保存（未完了）
`C:/Program Files/WSL/wslc.exe images` を Start-Process/WaitForExit(30000) で読み取り確認し WSLC_IMAGES_TIMEOUT30、stdout/stderr 空。自身の images CLI のみ停止した。Docker/wslc/user service は再起動していない。
Step1 以外は未完了。8 application paths を source-manifest.json と Get-FileHash SHA256 の source-hashes-current.json に保存した。time.c は未実行の native fixture scaffolding であり、time/signals production は未変更。最終 review / READY / 完了の成果物ではない。Linux raw native trace / memory Red は paludarium-work の /work/target/u4-evidence に保存済みで、daemon 復旧後の回収が必要。Native Green、time/signal ABI、inventory static callsites、全体 regression/coverage/fuzz は未検証。Windows内部16件を native 合格に代替しない。

## 復旧後の確認
正式 verify exit0、execution_allowed:true、reason:approved。Docker cp で保存済み Red/trace を docs/u4/inventory に回収。最終 source 同期後 memory native 差分8 passed/0 failed、exit0（memory-green-recovery.txt）。Linux内部 u4_tests:: は Host8+Kernel16+MMU8 passed。time native修正前0/8 failed・exit1、実装後8/8 passed・exit0（time-red.txt/time-green.txt）。成功 sleep は remaining sentinel 不変。
Signal native-first 15件は2 passed/13 failed、exit1。headers observer offsets は mcontext40、sigmask296、siginfo addr16、fpregs184、mcontext size256、uc_stack16、RSP/RIP/EFL index15/16/17。native MAPERR code1/trap14/err4、ACCERR code2/trap14/err7、ILL code2/trap6、FPE code1/trap0。flags比較mask0xcd5はstatus+DF、RF等の配送ビットを除く。raw signal-red.txt を保存。signal実装後の初回 cargo check は Mapping.len field が存在せず E0609/exit1。実在 field length に修正し再検証する。

## 追加 native boundary
Signal15件は実装後全通過（signal-green-first.txt）。timer割込み/SA_RESTART sleep 2件は初回 -ENOSYS vs native -EINTR の Red→Green2件。FP state pointer の64byte alignment は native0/emu40 のRed→Green1件。Kernel check の cast比較構文エラーは exit1、括弧で修正後に上記 native Green。
追加4件のnative-firstは各exit1: partial mprotectはnativeが穴手前をPROT_NONEへ変更しSIGSEGV、emuは旧permissionのまま正常終了。mmap offset1はnative -EINVAL/旧byte41保持、emu mapping成功。relocated sigframeはnative正常return、emu SIGSEGV。huge nanosleepはnative timerで-EINTR、emu -EINVAL。raw partial-protect-red.txt/offset-red.txt/relocated-red.txt/huge-sleep-red.txtを保存。巨大sleepのremaining predicateはfixtureがsec==0とsec>0を同時要求していたため、正常なpositive-sec predicateへ修正して再比較する。

### PageFault metadata の追加差分（検証済み）
- Red: execute RW resident page の error code は native 21 / emulated 5、virgin PROT_NONE/READ write は native 6 / emulated 7。raw `target/u4-evidence/{execute-fault-red,none-fault-red,virgin-readonly-red}.txt`。
- C1/C4 が fetch/mapped/present を fault 時に捕捉する型へ更新。全構築 consumer の修正途中で E0063（MMU の旧 Fault literal 4 件）を観測し、修正後 Windows `cargo test --locked -p paludarium-mmu -p paludarium-cpu -p paludarium-kernel --lib u4_tests:: --no-run` exit0。これはコンパイルのみ。
- Linux `scripts/linux-dev.sh bash -c 'cargo test --locked -p paludarium-harness --test diff_u4 fault_context -- --nocapture'` exit0、2 passed。raw `target/u4-evidence/fault-metadata-green.txt`。
- Linux `scripts/linux-dev.sh bash -c 'cargo test --locked -p paludarium-harness --test diff_u4 u4_signal_virgin_readonly_fault -- --exact --nocapture'` exit0、1 passed。raw `target/u4-evidence/virgin-readonly-green.txt`。
- native/emulated の stdout 全量と exit0 が一致。最終 shared-type regression、write restart、内部 signal/runtime tests、quality/coverage/fuzz は未実行。

### write restart native oracle / 内部確認
- 検証済み native: `scripts/linux-dev.sh bash -c 'cc -O1 -fno-inline -no-pie tests/guests/u4/write-restart-oracle.c -o target/u4-evidence/write-restart-oracle && timeout 30 target/u4-evidence/write-restart-oracle 0 && timeout 30 target/u4-evidence/write-restart-oracle 1'` exit0。stdout `restart=0 frame_rax=-4 frame_site=1 result=-4` / `restart=1 frame_rax=1 frame_site=0 result=1`。fork/pipe は native oracle のインフラのみ、guest U4 syscall 実装ではない。
- Windows `cargo test --locked -p paludarium-kernel u4_signal_write_restart_frame_matches_native_context -- --nocapture` Red exit1/0pass1fail、SA_RESTART frame RAX actual=-4 / expected=1。最初の fixture compile は E0599（未定義 Errno::EINTR）で、既存 Errno(4) 表現へ修正。修正後同じ command Green exit0/1pass。
- `cargo test --locked -p paludarium-kernel u4_signal_ -- --nocapture`: 追加 REP fixture の初回は11pass1fail。count3 では REP が完了するため continuation 未作成だった。既存 REP_CHUNK=4096 の観測に合わせ count4097 へ修正後 exit0/12pass。production修正は不要。
- Windows `cargo test --locked -p paludarium-runtime u4_tests:: -- --nocapture` exit0/8pass。kill native wait の内部ケースは channel recv_timeout3秒、完了後join。
- Windows `cargo test --locked -p paludarium-cpu u4_tests:: -- --nocapture` exit0/5pass。types `u4_fault_` exit0/5pass（その後承認済み instructions の `u4_tests::` moduleへ移動、Linux final確認待ち）。
- 最終 Linux scoped確認は `cargo test --locked -p paludarium-mmu -p paludarium-types -p paludarium-cpu -p paludarium-host -p paludarium-kernel -p paludarium-runtime --lib u4_tests:: -- --nocapture`。raw `target/u4-evidence/internal-u4-final.txt`、この追記時点では実行中で未検証。

### stop / continue の native-first 補足
- `cc -O1 tests/guests/u4/stop-continue-oracle.c -o target/u4-evidence/stop-continue-oracle; timeout 30 ... mode0/1/2/3/4` は全exit0。stdout順は STOP19→exit7、TSTP20→exit7、blocked CONTでもSTOP19→exit7、STOP19中kill→signal9、blocked TSTP→stopped0/exit7。最終raw `target/u4-evidence/stop-continue-native.txt`。
- Kernel回帰 `cargo test --locked -p paludarium-kernel tests::u4_tests::u4_default_stop_is_not_process_termination -- --exact --nocapture` Red exit1/0pass1fail（Next::Exit）。修正後exit0/1pass。最初の短名--exactは0testsだったため成功証拠に使わない。
- Windows Runtime `cargo test --locked -p paludarium-runtime u4_tests:: -- --nocapture` exit0/11pass。停止中CPU/出力保持、SIGCONT resume、Session.kill、pending SIGKILLを検査。
- Linux `cargo test --locked -p paludarium-kernel -p paludarium-runtime --lib u4_tests:: -- --nocapture` exit0/30+11pass、raw stop-internal-green.txt。この時点の版より後にqueue容量/競合補足を追加。
- Windows Kernel `cargo test --locked -p paludarium-kernel --lib u4_tests:: -- --nocapture` exit0/32pass。追加inbox RT1000件 race、RT上限時のcontrol配送を含む。
- 初回 workspace coverage `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit1。既存Kernel memory testのMAP_SHARED→EINVAL期待がnative対応後のsourceに合わず38pass1fail。raw coverage-final.txtを保持、test期待はshared成功/zero fill/unmap確認へ更新。これは80%閾値変更ではない。
- clippy失敗はMMU collapsible_if、PFerror bit expression precedence、stop manual_range_patterns。全て表記だけ修正し、quality-stop-green.txt のfmt/fuzz-fmt/clippyはexit0。native oracleを毎回比較するtest-only追加後の最終qualityは後続確認。

### quota除去とSIGKILL優先順（観測記録）
- NFR5は初期の生産resource上限を設けないため、根拠のないRT pending/inbox 1024件上限を除去した。fuzz driverの64 syscall/64 wait/CPU64/256 MMU operation予算は試験入力の有限化であり、生産quotaではない。
- 最初の最終coverage再試行 `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit1。`diff_u2`の`u2_alu`が30秒watchdogで失敗し、37pass/1fail、TOTAL未取得。raw `target/u4-evidence/coverage-stop-final.txt`を保持。並行負荷の因果は未検証、閾値とwatchdogは変更しない。
- Windows `cargo test --locked -p paludarium-kernel u4_signal_realtime_queue_has_no_invented_quota -- --nocapture` Red exit1/0pass1fail。2048件の受理とlen確認後、配送は実際Signaled(32)、期待Signaled(9)。期待の根拠は次のnative比較で確認した。
- Linux `cargo test --locked -p paludarium-harness --test diff_u4 oracles::u4_stop_continue_native_oracle -- --exact --nocapture`：mode5（停止中RT2048→SIGKILL）はnative/Kernelとも `stopped=19 exit=-1 signal=9`。raw `stop-backlog-native-before-fix.txt`、exit0/1pass。停止中配送保留の一致を未停止時優先順の証拠に拡張しない。
- 同コマンドのmode6（停止中RT2048→SIGKILL→SIGCONT）はRed exit1/0pass1fail。native `stopped=19 exit=-1 signal=9` に対してKernel `stopped=19 exit=-1 signal=34`。raw `target/u4-evidence/stop-backlog-continue-red.txt`。SIGCONTによる停止解除後のSIGKILL優先を観測に合わせ修正した。
- 修正後Windows `cargo test --locked -p paludarium-kernel u4_ -- --nocapture` はexit0/32pass。`u4_signal_realtime_queue_has_no_invented_quota`、`u4_inbox_control_signal_survives_realtime_backlog`、`u4_inbox_sender_drain_race_preserves_realtime_count`を含む。Linux native Green/最終quality/fuzz/coverageはこの記録時点では未検証。

### 最終sourceのscoped Greenと区間証拠
- Linux逐次command: `cargo fmt --all -- --check && cargo fmt --manifest-path fuzz/Cargo.toml -- --check && cargo clippy --locked --workspace --all-targets -- -D warnings && cargo test --locked -p paludarium-kernel -p paludarium-runtime --lib u4_ -- --nocapture && cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture`。runner session33159 exit0、Kernel32/Runtime11/live oracle2pass。oracle raw `target/u4-evidence/quota-kill-scoped-green.txt`。mode6 native/Kernelとも `stopped=19 exit=-1 signal=9`。write restartなしはframe_rax=-4/frame_site=1/result=-4、ありは1/0/1で毎回native比較した。
- 最終source capture: `Get-FileHash -LiteralPath <sourcepath> -Algorithm SHA256` をmanifestのdocs以外36pathへ適用。`source-hashes-current.json` のSHA256は `c26b01abddbb35d568ec705bc0c3a834237ab2bd9aaa516f26b076ce4225e65b`、subjectは `u4-final-production-quota-removal-sigkill-priority`。その後application sourceを変更していない。
- ASan逐次runnerは `LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run syscall_args --fuzz-dir fuzz -- -max_total_time=600 -timeout=30`、続いて同設定の `mmu_ops`。syscall_argsは `Done 348580 runs in 601 second(s)`、次区間へ進んだ。既存suppressionはiced decoderの既知leak用であり新しいsuppressionを追加していない。mmu区間/full runner exitはこの追記時点で未取得。
- Windows最終cargo-deny初回試行は保存dir `target/u4-evidence` 欠落でOut-File失敗、log未生成。shellのexit0をaudit成功とは扱わず、依存audit未検証として保持。fuzz2区間終了後にdirを作成して再実行する。

### 最終fuzzと依存audit
- Linux逐次fuzz runner session75949はexit0。ASan `syscall_args` は348580runs/601秒、`mmu_ops` は987393runs/601秒。raw `target/u4-evidence/fuzz-syscall-final.txt` / `fuzz-mmu-final.txt`。2区間ともmax_total_time600/timeout30、既存LSAN suppression、最終36sourceの版。新しいsource修正やsuppressionを加えず完了した。
- host保存dir作成後のcargo-deny再試行はsandboxのadvisory DB `db.lock` readonlyでexit1。raw `docs/u4/inventory/cargo-deny-readonly-failure.txt`。同じ公式実体の `--locked check` をrequire_escalatedで再実行しexit0、`advisories ok, bans ok, licenses ok, sources ok`。raw `docs/u4/inventory/cargo-deny-final.txt`。実体は `Get-ChildItem target/u2-tools/cargo-deny*/cargo-deny.exe | Select-Object -First 1` で取得、PATHへUSERPROFILE/.cargo/binを追加した。
- coverage開始前 `docker.exe ps --format '{{.ID}} {{.Names}} {{.Command}}'` はemdash-emdash-1/emdash-db-1の2serviceだけを返した。fuzz/denyは終了済みで、今回の `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` を単独runner session48580へ起動した。これは並行負荷の因果や性能値の証明ではない。raw `target/u4-evidence/coverage-quota-final.txt`、結果取得待ち。

### 最終coverageと証拠回収
- session48580 exit0、TOTAL lines5049/missed329/93.48%、regions90.44%。`docs/u4/inventory/coverage-quota-final.txt` SHA256 `96bf067957de48d651a92689b43f9f5d936704968113d0858ab9ea410c657116`。全Cargo Running sectionの最後の親summaryのみ集計して311pass/0fail/0ignore。U1差分16/U2差分38/U4差分43/parallel10。隔離child1件のsummaryを加算しない。`validation-current.json` にrunner別内訳を保存した。llvm-covのこの集計にdoctestは含まない。
- 前回timeoutしたu2_aluはraw146–151行でchild1pass/0fail、今回30秒watchdog内に通過した。原因を負荷と断定したり性能比較値に使用しない。
- 終了後、`docker create --label aidlc.u4.evidence-copy=true -v paludarium-work:/work:ro paludarium-dev` の自分のhelperから `/work/target/u4-evidence/.` を `target/u4-evidence-copy` へdocker cpし、helperを削除。追跡可能な `.txt`/`.json`だけを `docs/u4/inventory` へ保存した。source sync/build/fuzzを重ねず、他containerを停止しない。
- core8crateの `src/lib.rs` に対する `rg -n '^#!\[forbid\(unsafe_code\)\]'` は全8件一致し、最終workspaceコンパイルも通過した（Types8/Loader8/Runtime7/MMU14/Kernel10/Decoder11/Cpu8/VFS8行）。Host境界のOS接続とcore禁止を区別する。
- 引継ぎbuild receiptは `docs/u4/inventory/upstream-build-receipt.json` へ原bytesをコピーして保存した。新buildを行ったと表現せず、U4で再観測したbinary hash/static位置/有限native traceと対応させる。

### 最終成果物・claims照合
- manifest version1/stage code-generation/unit u4-memory-signalsの92claimsは全実在。jj実体をmise globで解決した `jj file list` はexit0、92/92追跡、untracked/ignored0。`source-claims-check.json`に結果を保存した。build成果物/compiled binary/cacheをclaimへ含めず、generator/shell/config/docs/必要raw evidenceは列挙した。
- traceability15targetsは全て単一の既存workspace-relative file。最終source36pathのSHA256はcaptureと全一致。plan14stepsの完了markを更新し、Testing Contractやmethodology/品質下限を変更しない。
- manifest SHA256は `ed834d3cbc3ab8ae1699918a31b9e1c7f48690de2c704d477ac5ee0c502c0ca9`。codegen4produces、manifest、evidence/source hash/current validationとU4docsを固定してrootへ引き渡す。workflow routing/review/unit completionは実行していない。

### RT配送順のnative先行補足（現在未完了）
- 正式Codex `aidlc-testing-posture.ts verify --unit u4-memory-signals` はexit0/execution_allowed:true/approved:true/contractValid:true。user-facing reasonは `The plan-approval check is off; continue with the current plan and test instructions without a new approval.`。現在のplan/instructionsで継続許可を確認した。
- 新fixture最初のcompileはAddressSpaceにread_u32がなくE0599。raw `rt-order-fixture-compile-failure.txt` を保持し、既存read_u64からcodeの低32bitを読む形へ修正した。native未実行のcompile失敗をsemantic Redとは扱わない。
- `cargo test --locked -p paludarium-harness --test diff_u4 oracles::u4_realtime_order_native_oracle -- --exact --nocapture` はRed exit1/0pass1fail。raw `rt-process-order-red.txt`：default native35/Kernel36、handler native35→36/Kernel36→35、混在native10→35/Kernel35→10。同一process queueのkill→sigqueueはnative code0→-1を観測した。
- 初期FIFO候補のkill→tkillは別queueである。raw `rt-order-all-modes-red.txt` にnative35:-6→35:0 / Kernel35:0→35:-6を保存。同一queue FIFOの反例として解釈せず、Process/Thread provenance欠落の限定差として保持する。
- C8のKernel handle契約、unit-of-work.md75–79行U4 signal配送、requirements.md80行FR2.9に単一threadの混在を除外する記載はない。現send_signalはkill(code0)とtkill/tgkill(code-6)を同じuser constructorへ渡す。最小provenance区別を修正する必要があり、clone/guest rt_sigqueueinfoの新規実装はしない。
- 中間selectorはSIGKILL→eligible標準→低番号RT→同番号FIFO、restart previewも同selector。Linux `fmt/fuzz-fmt/clippy && cargo test --locked -p kernel/runtime/mmu/host/cpu/types --lib u4_ && cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture` はexit0、内部73/live3pass。正確な全package commandは `rt-order-quality-scoped.txt` とtool出力。追加FIFO/maskと低番号handlerの両SA_RESTART flag回帰を含む。
- 中間source37paths digest `2aec5d176374b56935f24fd9d4c2670853f240a8e1ce2079002d3b2c1c34e339`。旧source/validationは `source-hashes-before-rt-order.json` / `validation-before-rt-order.json` へ保存。Cargo.lock hash不変なので前回cargo-deny4okをそのlockへ適用し、不要なauditを再実行しない。中間ASan runnerの終了後にprovenance sourceを更新し、最終検証を取り直す。

## 配送先 pending queue の native 観測と限定修正

検証済み: `scripts/linux-dev.sh bash -c 'cargo test --locked -p paludarium-harness --test diff_u4 oracles::u4_realtime_order_native_oracle -- --exact --nocapture > target/u4-evidence/rt-provenance-red.txt 2>&1; result=$?; cat target/u4-evidence/rt-provenance-red.txt; exit $result'` は exit1、親0pass/1fail。mode4/5（kill35→tkill/tgkill36）は native `36:-6,35:0`、Kernel逆順。mode6同番号35は native `35:-6,35:0`、Kernel逆順。mode7 standard10をProcess/Threadそれぞれ2回送るとnativeは `10:-6,10:0`、Kernelは `10:0` のみ。native同一Thread queue観測は `35:-6,35:-1`、同一Process queueは `35:0,35:-1`。後者のSI_QUEUEはnative観測専用で、guest rt_sigqueueinfoを実装した主張ではない。

配送順は単なる番号だけでは決まらない。PendingSignalはtyped Process/Thread targetを保持し、SIGKILL最優先の後、Thread pendingをProcess pendingより先に選ぶ。各queue内でstandard優先、低いRT番号優先、同番号FIFO。standard coalescingは番号とtargetの組に限定する。kill/public queue/host inbox/timerはProcess、tkill/tgkillと同期faultはThread。配送とwrite restart previewは同一selectorを使う。単一process/thread内の既存kill系の意味を修正し、clone等の範囲を追加しない。

検証済み中間証拠: 番号優先のみのsourceのASan逐次runner session65047はexit0、syscall_args899904/601秒、mmu_ops967303/601秒。raw `fuzz-syscall-rt-order-final.txt` / `fuzz-mmu-rt-order-final.txt`。以後のtarget修正に対する最終fuzz証拠として代用しない。

検証済み失敗: `rt-provenance-quality-scoped.txt` はexit1。fmt後clippyがfixture OR-patternにmanual_range_patternsを検出、内部/native tests前に停止した。`4..=7`へ機械的修正し、同期ArithmeticFaultのThread配送回帰も追加した。最終再実行は別名 `rt-provenance-quality-scoped-final.txt` に保存し、結果は未取得時点では合格と扱わない。

検証済み: `rt-provenance-quality-scoped-final.txt` の再実行はexit1、Kernel36pass/1fail（同期fault fixtureがblocked SIGFPEをhandler配送と誤期待）。blocked同期faultの既存policyは変更せず、unmasked同期faultのThread優先へfixtureを修正した。

検証済み最終 scoped Green: `scripts/linux-dev.sh bash -c 'set -e; (cargo fmt --all -- --check && cargo fmt --manifest-path fuzz/Cargo.toml -- --check && cargo clippy --locked --workspace --all-targets -- -D warnings && cargo test --locked -p paludarium-kernel -p paludarium-runtime -p paludarium-mmu -p paludarium-host -p paludarium-cpu -p paludarium-types --lib u4_ -- --nocapture && cargo test --locked -p paludarium-harness --test diff_u4 oracles:: -- --nocapture) > target/u4-evidence/rt-provenance-quality-scoped-green.txt 2>&1; tail -n 85 target/u4-evidence/rt-provenance-quality-scoped-green.txt'` session35024 exit0。内部76pass（Cpu5/Host8/Kernel37/MMU10/Runtime11/Types5）、live oracle3pass。mixed modes4/5/6/7は全native/Kernel出力一致、Process/Threadそれぞれの同番号FIFOはnative観測とmetadata内部回帰で確認。同期fault Thread選択、mask、standard queue別coalesce、SIGKILL、write SA_RESTART previewと配送共通selectorも内部回帰成功。

最終production capture: `Get-FileHash -Algorithm SHA256`で37pathsを保存。`source-hashes-current.json` SHA256=`1283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c`。旧番号優先のみは `source-hashes-intermediate-rt-number-only.json`。Cargo.lockは`4cfdcc2b2c4a47789e4ee5dfb61d46b529193b3494a92de416e783f98ef2e7c4`で既存cargo-deny4category成功時から不変。同じlock/dependency setのaudit証拠として再利用し、source変更後新auditを実行したとは記録しない。

最終 ASan runner session73076を開始: `scripts/linux-dev.sh bash -c 'set -e; export LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp; cargo fuzz run syscall_args --fuzz-dir fuzz -- -max_total_time=600 -timeout=30 > target/u4-evidence/fuzz-syscall-provenance-final.txt 2>&1; tail -n 6 target/u4-evidence/fuzz-syscall-provenance-final.txt; cargo fuzz run mmu_ops --fuzz-dir fuzz -- -max_total_time=600 -timeout=30 > target/u4-evidence/fuzz-mmu-provenance-final.txt 2>&1; tail -n 6 target/u4-evidence/fuzz-mmu-provenance-final.txt'`。開始時点でexit/count未取得。Linux sync/build/auditは重ねない。

検証済み最終source: runner73076 exit0、syscall_args1136975runs/601秒、mmu_ops1564316runs/601秒。`RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80`（scripts/linux-dev.sh bash -c、stdout/stderrをcoverage-provenance-final.txtへ保存しcargo exitを返す）session23606 exit0。Running section末尾の親summaryだけを集計し317pass/0fail/0ignore、U1diff16/U2diff38/U4diff44/parallel10、5095行/321missed/93.70%、regions90.73%。raw docs/u4/inventory/coverage-provenance-final.txt SHA256d34bcea1ccc21bb3da46f451373b94ffa4b777fd2fea63fe415610024e09f6ce、validation-current.jsonに各runner集計。doctestを集計しない。

`Get-FileHash -Algorithm SHA256`で37application pathsを再照合しchanged0、capture SHA2561283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c。Docker own read-only helperで終了済みrawを回収しhelperのみrm、docs/u4/inventoryは67files。新旧失敗/成功のrawを保持し、同じsourceで不要なbroad再実行をしない。

最終claim照合（検証済み）: glob解決したjj実体の `jj file list` exit0、source-manifest107claimsのuntracked/ignored0。`Get-FileHash -Algorithm SHA256`再照合37paths changed0。traceability15single-file targets全実在、NFR1〜9全割当。承認済みbriefのTesting Contract JSON blockとplanのblockをCRLF正規化だけで比較し完全一致true。具体proof source-claims-check.json。manifestSHA256d5af3e67ab3424552850e1762d8f64b331cddc3a2165818626c7e9c9f77d72bd、sourcecaptureSHA2561283c795fc00e0228ce2c7bab21853271a93c3d4f51b3b6c905bbe60c98d617c。必要rawを捨てず追跡可能txtでclaimし、generator/shell/config/docsの全U4書込を含める。最終品質/source/evidence整合後、独立検証へ渡すため編集を停止する。
