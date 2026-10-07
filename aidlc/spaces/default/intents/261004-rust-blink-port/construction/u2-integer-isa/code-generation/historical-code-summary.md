# U2 コード生成概要

検証済み：整数命令・flags・REP再開と原子的メモリ操作を実装し、最新 Linux workspace 検証は189 unit/integration tests、U1 differential16、U2 differential35、host parallel10を含め0 failures。行 coverage93.64%（4231行、未実行269、regions89.85%）で80% gateを維持。必須整数formsの取得・分類・native case対応は固定source/新binaryで回収し、独立レビューへ渡す。全入力経路とprobe/aubeのemulator全program統合はU10で未検証。

## 実装

- C1 DivideErrorをArithmeticFaultへ変更しTypes/Cpu/Kernel全consumerを同時更新。KernelはSIGFPE、既存Runtimeの汎用fault受渡しは変更不要。
- Decoderは幅、string implicit operands、address32、prefix、scalar BMI VEX whitelistを拡張。未対応VEX SIMD/EVEX/XOPはUnsupported。外部decoder型は公開契約に漏らさない。
- Cpuはrotate/double shift/bit/count、carry chains/BMI、sign/flags/count branches、word stack/ENTER/XLAT、全string幅とLOCK/CMPXCHG/XADDを拡張。非REPfaultのregister rollback、ENTERのnative部分memory効果、REP CMPS/SCAS開始flags復元とBudgetStop継続情報を保持。
- Mmuはprivate dataをAddressSpace単位の共通Mutexで保護。normal read/write/fetch/initial writeと全mapping/typed atomicが参加。任意callbackなし、全範囲write権限preflight、compare失敗も検査。ENTER stack permission probeは同じlockで非書込検査。
- Harnessは外側30秒watchdog、kill/reap、native signal context、old-value oracle付き並行検証。既存dependencies/pin/core unsafe禁止を維持。CI差分とwhole-workspace80%、夜間CPU/MMU fuzz各600秒を追加。

## 実行した検証と証拠

Windows `cargo fmt --all -- --check` exit0; `cargo clippy --locked --workspace --all-targets -- -D warnings` exit0. Linux:
```
scripts/linux-dev.sh bash -c 'set -euo pipefail; cargo clippy --locked -p paludarium-harness -p paludarium-cpu -p paludarium-decoder -p paludarium-mmu --all-targets -- -D warnings; mkdir -p target/u2-evidence; RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80 2>&1 | tee target/u2-evidence/u2-workspace-coverage-final.log'
```
検証済み：exit0。最終ログは `target/u2-evidence/u2-workspace-coverage-final.log`（development volumeにも保存）。件数はCLI6+4、CPU26、Decoder17、Harness6、U1diff16、U2diff35、parallel10、Host6、Jit5、Kernel11、Loader8、Mmu19、Runtime6、Types9、Vfs5、計189。childの重複summaryは加算しない。llvm-covのdefault実行はdoctestを含まないため、ここでU2 doctest通過は主張しない。

検証済み：実装前native観測とRed/Greenのcommand・raw出力を `evidence.md` に記録した。DIV/IDIV4 contexts、REP CMPS/SCAS6 contexts、POP rollback、atomic fault3 contexts、ENTER fault3 contextsとaggregateを含む。Decoderのfocused testは整数ANDNを許可する一方VPXORを拒否し、word stackのoperand幅を確認する。CPU8件・MMU9件のU2内部テストは実装後に追加した。

初回coverageは失敗：U1diff11pass/5timeout（`insn_alu`,`insn_cmptest`,`insn_cond_cmov`,`insn_cond_jcc`,`insn_cond_set`）。各case30秒の上限は維持した。background traceは存在したが負荷による因果は **推測/未検証**。background終了後のserial条件で通過した。候補追加後の中間実行は93.55%のprofileを生成したが、tee directory不在でpipeline exit1。同じprofileのreportを再出力した。後続の幅修正後に、上記の保存成功した最終実行を行った。両失敗の記録を保持する。

検証済み：初期sourceのASan CPU/MMU各600秒はexit0（814758/1447800回）、ログ・入力は `target/u2-evidence/{u2-cpu-fuzz.log,u2-mmu-fuzz.log,u2-fuzz-evidence.tar}`。最終production sourceを再実行しCPU510864/MMU1173111回、各601秒、両方exit0。最終ログ・入力は `target/u2-evidence/{u2-cpu-fuzz-final.log,u2-mmu-fuzz-final.log,u2-fuzz-final-inputs.tar}` に回収した。Nightlyは各新targetと既存decoder/ELF targetの600秒を維持する。rustc1.101.0-nightly (21b707e3f2026-09-30)、pin nightly-2026-10-01は変更なし。cargo-denyはSHA固定CIの `cargo deny --locked check` を保持し、このunitのlocal実行は未検証。新しい外部product dependencyは追加していない。

## 棚卸しと残る限界

証拠は `docs/u2/inventory.md`、`differential-coverage.md`、`flag-masks.md` と `docs/u2/inventory/` 配下のJSON/body trace/native出力。固定source/lock/binary hashと#1645 fixtureを記録する。検証済み：native probe noargsとaube4操作は別々にexit0。entry sampleはloaderのみ。本体sampleはstdoutまたはfixture open起点を採用する。いずれも時間・命令数上限があり、complete_runtime_inventoryはfalseと明示する。

検証済み：追加15整数命令群はENTER/XLATとLEAVE/PUSHF/POPF16を含めnativeケースを実行した。列挙した必須候補の命令群に未実装はない。memory-sourceのADCX/ADOX/MULX/SHLX/SHRXも補足し、exact `u2_bmi_forms` 1件でnative/emu全出力一致。production修正は不要だった。対象program全体のfeature dispatchと全未観測経路は未検証。ドキュメント根拠：SIMD/x87、syscall/thread/wasm/Jit統合は後続unit。原artifactの歴史上のimage/source対応は未確定。隔離再buildはprobe/aubeともexit0。probeは原binaryとhash一致、新aubeは新hashと全4658正規化form内容・count差分0を固定した。receiptと全フォーム分類を docs/u2/inventory/rebuild/ に保存し、必須取得gateを回収した。

独立レビューとunit/stage完了はconductorが担当する。 最終sourceのCPU/MMU ASan600秒も通過した。cargo-deny overall checkはBuild/Test/CIで確認する。閾値やtimeoutは変更していない。


検証済み：新probe native8 PASS、新aube4操作native exit0、本体sampleは5718/7670/7693/6774命令でbudget停止。分類分母はaube4658（整数3136/system190/U3 1332）、probe865（整数696/system3/U3 166）、未分類0。対応表はfamily/dimensionのnative case対応であり、静的全bytesを同じ配置で全量実行した割合ではない。原artifactの歴史上のbuilder由来は未確定。
追加prefix検証はBMI/frame各exact1件とdecoder幅exact1件が通過。66 49 9dのword push fixtureはnative途中終了したためqword準備へ修正し、失敗とGreenをevidenceに保持した。production変更なし。189件/93.64%・最終600秒fuzzは同じproductionの先行検証で、後続test-only追加はfocused検証を実行した。


## FS/GS atomic address 修正後の検証

検証済み：`u2_segment_atomic_forms` は修正前0 passed/1 failed（出力449232bytes、最初の差分byte109）。nativeではtarget=0x10/decoy=0x1122334455667788、emulatorではtarget=0/decoy=0x1122334455667798となった。`u2_atomic_gs_` は修正前0 passed/2 failedで、期待したfaultの代わりにBudgetExhaustedとなった。最初のfixture compileはextended asmの% escape不足で失敗し、fixtureのみ修正した。

全7atomic経路を最終linear addressへ変更した。addr32はoffsetを切り詰めた後FS/GS baseを加算し、CMPXCHG16B alignmentとpermissionも最終addressで検査する。LEAのoffset計算は維持する。検証済み：修正後 `cargo test --locked -p paludarium-harness --test diff_u2 u2_segment_atomic_forms -- --exact --nocapture` は1 passed、`cargo test --locked -p paludarium-harness --test diff_u2 u2_atomic_gs_ -- --nocapture` は2 passed。FS/GS・mapped decoy・4GiB超target・全LOCK経路・scalar/pair compare成功失敗をnativeと比較した。signal context raw flags=0x10ad7、比較mask=0xcd5で例外配送RF/IF等を除外する。

検証済み：実装後 `cargo test --locked -p paludarium-cpu --lib u2_segment_ -- --nocapture` は5 passed。全19opcode×FS/GS、final address alignment、write権限、unmapped fault、failed pair compareのzero-extensionを補完した。`cargo clippy --locked --workspace --all-targets -- -D warnings` はexit0。

検証済み：背景compile/trace終了後 `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit0。parent tests197（CPU31/U2diff38、その他は先行189件の構成と同じ）、lines4233/missed254/94.00%、regions90.20%。30秒watchdogと80%閾値は維持した。修正前後のrawログは `docs/u2/repairs/` に保存する。先行189件/93.64%および先行fuzzは修正前sourceの履歴として保持する。

検証済み：Linux `cargo deny --locked check` の初回はexit1（no such command: deny）。その後rootが公式cargo-deny0.20.2 Windows asset（SHA256 975a22143262fd27476d19ee00c7af67978426e40e1dee94eed6bbade1cf87dc、release metadata digest一致）をtarget/u2-toolsへ取得し、`cargo-deny.exe --locked check` はexit0、advisories/bans/licenses/sources全ok。local未実行GAPはこの後続観測で解消した。

最終修正sourceのASan検証：単一runnerで `LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run --fuzz-dir fuzz cpu_u2 -- -max_total_time=600 -max_len=4096 -timeout=30 -rss_limit_mb=2048`、続いてmmu_u2（max_len4608）を逐次実行し、CPU1276258/MMU1706799 runs、各601秒、両方exit0。CPU既存iced table suppression12件のみ。ログは `docs/u2/repairs/r01-{cpu,mmu}-fuzz-final.txt`、入力archiveは `target/u2-evidence/r01-fuzz-inputs.tar`。Windows fmt --all -- --check もexit0。
初回CPU fuzzはexit1：No such file or directory: fuzz/corpus/cpu_u2 とASan suppressions file読取失敗。途中に証拠回収用linux-dev.sh同期を呼んだ。同scriptは/work/target以外を除去する実装だが、失敗時点との直接因果は推測/未検証。失敗ログを `r01-cpu-fuzz-sync-failure.txt` に保持し、同期終了後の単一直接docker runnerで両600秒を最初から回収した。後続では同期/compile/traceを重ねなかった。
検証対象production exec.rs SHA256=e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0。CPU内部test source SHA256=4b2680bdc99b5c3263f2472a6b4000b030810df0958fd76d82e896f529865d7f。閾値、watchdog、nightly予算、Testing Contractは変更していない。

## 再開後の現在source確認

今回の観測と先行test実行を区別した詳細は evidence-current.md。承認済みStep17〜19はapplication/U1/README/既存review変更なしで証拠を照合した。exec.rs・CPU test sourceの保存hash一致、manifest95claims不変、分類分母4658/865とnative_case参照、詳細NFR16件の対応を確認。先行197件/94.00%・ASan各601秒・cargo-deny4項目okを再確認し、新実行とは数えない。全任意経路と後続unit統合の未検証は維持。

