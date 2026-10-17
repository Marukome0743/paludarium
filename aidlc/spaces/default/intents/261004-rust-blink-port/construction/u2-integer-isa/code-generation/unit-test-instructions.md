# U2 Unit Test Instructions

## redo新attempt Step27〜29

新Summary Confirmation後に本書を保存して既存exact commandsと品質下限を確定した。製品bytes不変のため新testsなし、旧600秒ASanを現在成功へ転用しない。plan/本書/summary/traceabilityとmanifestの全保存後、レビュー中freezeへ渡す。

対象は3手順。新承認と別の内容確認後に現在95claimsとCI証拠を再照合し、実4produces plan/instructions/summary/traceabilityとmanifestを全保存する。同一製品へ重い再試験を追加せず、以下commandsは不足回収用として保持。既存4ASan GAPとwasm未検証、全品質下限を維持する。親diaryをレビュー前に確定し、依頼からterminalまで書込とjj snapshotを停止する。以下Step24〜26は先行attemptの手順として保持する。

## 新attempt Step24〜26の手順（macOSからの記録再確認）

今回の対象は3手順。新attemptのPlan Approvalと別の内容確認後に既存snapshotとCI bytesを照合し、同一製品への重い再試験は追加しない。下記commandsは不足回収用として保持する。親diaryの出力専用追記をレビュー依頼前に済ませ、4成果物・manifest・sourceを確定する。reviewrequest〜terminalの間は記録/source書込とjj snapshot操作を行わない。

この節が今回の実行手順であり、下記Windows/bootstrap/先行再確認の節は履歴として保存する。現在attemptのPlan Approvalとengine execution_allowed確認後にのみ実行する。macOSのmise管理ツールはインストール先globで実体を解決し、shim/mise execを使わない。Rustはrust-toolchain.tomlのnightly-2026-10-01を維持する。手元Linuxは `bash scripts/linux-dev.sh` のDocker VMMで実行し、QEMU観測を実機native期待値と呼ばない。実機x86-64 Linuxの差分期待値はfork CIの各runで生成する。

現在sourceと直近11job成功CI（production revision `4d52be0a6f3b11d6c11a62f96196985c9c280fdc`）のsource bytes/logを照合して再利用する。native diff38/parallel10は当該runの期待件数であり、内部filterの現在件数は承認後に確認する。旧exec.rs hashと197件/94.00%、旧600秒fuzzは変更後sourceの証拠へ転用しない。

不足がある場合のみ次のunit限定コマンドを直列実行する。0件・skip・timeout・mismatchを成功にしない。

```bash
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test parallel_u2 -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-cpu --lib u2_ -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-decoder --lib u2_ -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-mmu --lib u2_ -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-types --lib u2_ -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-kernel --lib u2_ -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 u2_segment_atomic_forms -- --exact --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 u2_atomic_gs_ -- --nocapture
```

REPの両vendor policyの現在exact内部test名とnative6ケース名は承認後にsourceで確認して記録し、未知vendorを推定・除外して通過させない。Runtimeの存在しないu2 filterは要求しない。共有consumerの既存3OS suiteは一致する直近CI証拠で確認する。lint不足時は次の限定コマンドを使う。

```bash
bash scripts/linux-dev.sh cargo fmt -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-kernel -p paludarium-harness -- --check
bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-kernel -p paludarium-harness --all-targets -- -D warnings
```

全体行coverage80%以上は独立overall CI gateでありunit filterで代替しない。新しいproduction修正時は必要なnative回帰・coverage・関係する各600秒ASanをconductorと確定して回収する。現在sourceのfuzz/wasm未検証を明記し、未実行を合格としない。30秒watchdog・mask・nightly pin・各600秒予算を保持する。linux-dev.sh同期は/work/target以外を除去するため同volumeのfuzz・実行と並行しない。性能評価は今回行わない。

## 先行Windows/bootstrap手順（履歴）

以下のコマンドは、この Windows workspace の Git Bash で実行する。native cargo の実体を使うため、最初に次の関数を定義する（shim と mise exec を通さない）。`scripts/linux-dev.sh` のコマンドは同スクリプトが用意する Linux 環境で cargo を実行する。

```bash
cargo() { "$HOME/.cargo/bin/cargo.exe" "$@"; }
```

PowerShell から Linux 用コマンドを起動する場合は、`& 'C:/Program Files/Git/bin/bash.exe' scripts/linux-dev.sh cargo ...` と同じ引数で呼ぶ。

現時点の検証済み readiness:
`cargo test --locked -p paludarium-cpu --lib tests::budget_exhaustion_stops_an_infinite_loop -- --exact`
exit 0、1 passed、0 failed、17 filtered out。cargo は `$env:USERPROFILE/.cargo/bin/cargo.exe` 実体を使用。mise 管理ツールは glob で実体を解決し mise exec を使わない。

以下は承認後に bootstrap する未作成 targets/filters の手順で、現在 runnable とする主張ではない。最初の executable testcase 前に `--list` の出力を保存し 0 tests は失敗扱いにする。

1. `cargo test --locked -p paludarium-cpu --lib u2_ -- --list`、types/decoder/mmu/kernel/runtime も同じ package 個別コマンドで確認する。変更 component ごと原則 5–8 件以上（MMU 8 件以上）、CPU は必要な全 matrix cases。実装後内部層 tests を作成するまで readiness は既存 exact test と harness bootstrap の concrete cases で示す。
2. `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 -- --list`、`scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test parallel_u2 -- --list`。前者は inventory に登録した normal/fault/REP cases 全件、後者は少なくとも 8 distinct atomic/race cases の非ゼロ count が必要。数を固定して範囲を縮めない。
3. 命令実装前に native guest case を build/run して raw regs/flags/memory/signal context を保存する。`tests/guests/u2/build.sh` の承認後追加する case-ID 選択引数で対象 cases のみ build。defined/preserved/undefined mask と条件を docs/u2/flag-masks.md に記録する。native run を毎回行い hard-coded expectations を使わない。
4. `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 -- --nocapture`。範囲内命令/forms と fault/REP contexts の mismatch 0、fail/skip/0 tests は pass にしない。各子プロセス outer watchdog 30 秒、timeout は kill/reap と失敗ログ。BudgetStop 後 REP start flags 復元を含める。
5. `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test parallel_u2 -- --nocapture`。8 件以上、old value unique、total/success counters、normal memory/mapping race、cross-page、readonly failed CMPXCHG、CMPXCHG16B alignment。30 秒を join 内のみで実装しない。
6. `cargo test --locked -p paludarium-types --lib u2_`、`cargo test --locked -p paludarium-decoder --lib u2_`、`cargo test --locked -p paludarium-mmu --lib u2_`、`cargo test --locked -p paludarium-cpu --lib u2_`、`cargo test --locked -p paludarium-kernel --lib u2_`、`cargo test --locked -p paludarium-runtime --lib u2_` を変更層ごと実行。すべて非ゼロ test count と 0 failures。guest-origin panic/host trap は失敗。
7. `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u1` は既存 16 tests が基準、CPU exact readiness を再実行する。既存 U1 の結果を壊さない。
8. `cargo fmt -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-kernel -p paludarium-runtime -p paludarium-harness -- --check` と `cargo clippy --locked -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-kernel -p paludarium-runtime -p paludarium-harness --all-targets -- -D warnings`。両者 exit 0。変更によって package list は source manifest と照合する。
9. 夜間 fuzz の専用 target 作成後 `scripts/linux-dev.sh cargo fuzz run --fuzz-dir fuzz cpu_u2 -- -max_total_time=600`。新規 mmu_u2（fuzz/fuzz_targets/mmu_u2.rs、登録は fuzz/Cargo.toml）も同様に各 600 秒。既存 decoder/ELF targets の各 600 秒を維持。ASan 有効、CPU bounded execution、seed/input 保存、エラー 0。tool options は `cargo fuzz --help` で bootstrap 時確認し対象限定 command を確定する。現時点 fuzz target/command options は未検証。

Linux workspace coverage 80% と cargo-deny/CI 全体 gates は別 overall gate。上記 unit filter suite の coverage 値で 80% 要件を置き換えない。artifact acquisition/inventory が未完了なら成功を宣言しない。揺れは seed/env/bytes を保存し retry による隠蔽をしない。


## 実装後の観測（計画時点との区別）

上の「未作成」「未検証」はPlan Approval前の観測を残したもの。承認済みのmethodology・実行順序・80%閾値・30秒watchdog・夜間各600秒は変更していない。現在のsource-manifestと実行済みtargetは以下。

- `scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u2 --test parallel_u2 -- --nocapture`：現在35差分/10並行case。最終sourceはLinux全workspace coverage runでも両targetが非ゼロ件数・全通過。Windows上のcfg除外targetをrunner readinessにしない。
- `cargo test --locked -p paludarium-decoder --lib u2_`：現在9追加case（全17件）。BMI VEXとword stackのexact filtersは `tests::u2_integer_vex_does_not_enable_simd_vex`、`tests::u2_word_stack_forms_keep_two_byte_operand_width`。
- `cargo test --locked -p paludarium-mmu --lib u2_`：現在9追加case（全19件）。MMU追加test moduleは `u2_tests`。`u2_tests::u2_stack_write_probe_preserves_bytes_and_observes_protection` がexact名。
- `cargo test --locked -p paludarium-cpu --lib u2_`：8追加case（全26件）。`cargo test --locked -p paludarium-types --lib u2_` と `cargo test --locked -p paludarium-kernel --lib u2_` は各1consumer追加case。
- Runtime sourceは変更していないので、新規Runtime `u2_` filterを要求しない。0件を通過扱いにしない。既存Runtime6caseは `cargo test --locked -p paludarium-runtime --lib` または最終whole-workspace regressionで確認する。Jit/Host/Loader/Vfsも既存workspace regressionで確認済み。
- 現在のwhole-workspace gate：`scripts/linux-dev.sh bash -c 'set -euo pipefail; mkdir -p target/u2-evidence; RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80 2>&1 | tee target/u2-evidence/u2-workspace-coverage-final.log'`。189parent unit/integration tests、93.64%（4231行/未実行269）、exit0。childの重複summaryを件数へ加算しない。
- `cargo fmt --all -- --check`、`cargo clippy --locked --workspace --all-targets -- -D warnings` はWindows最終sourceでexit0。Linux変更targetのscoped clippyもexit0。元の七package表は実装前の候補であり、Runtime無変更をsource-manifestと区別する。
- `cargo fuzz run --help` でcargo-fuzz0.13.2/`--fuzz-dir`/既定ASanを確認。最終source：`scripts/linux-dev.sh cargo fuzz run --fuzz-dir fuzz cpu_u2 -- -max_total_time=600 -max_len=4096 -timeout=30 -rss_limit_mb=2048`（mmu_u2はmax_len4608）。LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、両方exit0、各601秒。最新実行/seed/input/logはevidence.mdとtarget/u2-evidenceに記録。

実際のWindows cargoは `~/.cargo/bin/cargo.exe`、mise管理toolはversionを固定せず実体globを使う。原artifactのprovenanceと再buildによる新inventoryのreceiptはdocs/u2/inventory.mdへ分離し、取得不足をcase成功に置き換えない。

最終追記（承認済みmethodology/順序/閾値の変更なし）：固定sourceのisolated rebuildと新native/static/body取得は docs/u2/inventory/rebuild/build-receipt.json を参照。追加memory-source/prefixの u2_bmi_forms/u2_frame_forms は各exact1件通過、decoder tests::u2_word_stack_forms_keep_two_byte_operand_width は66 49 9d implicit_size8追加assertionを含めexact1件通過。production変更なし。189件/93.64%および最終ASan600秒は同じproductionの先行workspace検証、追加test-only分はfocused検証で回収した。Runtimeは変更せず既存6件のworkspace regressionを根拠とし、u2 filter0件を合格に数えない。local cargo-denyは未実行で、保持したSHA固定CI/overall Build-Testで確認する。

## FS/GS atomic address 修正後の検証

検証済み：`u2_segment_atomic_forms` は修正前0 passed/1 failed（出力449232bytes、最初の差分byte109）。nativeではtarget=0x10/decoy=0x1122334455667788、emulatorではtarget=0/decoy=0x1122334455667798となった。`u2_atomic_gs_` は修正前0 passed/2 failedで、期待したfaultの代わりにBudgetExhaustedとなった。最初のfixture compileはextended asmの% escape不足で失敗し、fixtureのみ修正した。

全7atomic経路を最終linear addressへ変更した。addr32はoffsetを切り詰めた後FS/GS baseを加算し、CMPXCHG16B alignmentとpermissionも最終addressで検査する。LEAのoffset計算は維持する。検証済み：修正後 `cargo test --locked -p paludarium-harness --test diff_u2 u2_segment_atomic_forms -- --exact --nocapture` は1 passed、`cargo test --locked -p paludarium-harness --test diff_u2 u2_atomic_gs_ -- --nocapture` は2 passed。FS/GS・mapped decoy・4GiB超target・全LOCK経路・scalar/pair compare成功失敗をnativeと比較した。signal context raw flags=0x10ad7、比較mask=0xcd5で例外配送RF/IF等を除外する。

検証済み：実装後 `cargo test --locked -p paludarium-cpu --lib u2_segment_ -- --nocapture` は5 passed。全19opcode×FS/GS、final address alignment、write権限、unmapped fault、failed pair compareのzero-extensionを補完した。`cargo clippy --locked --workspace --all-targets -- -D warnings` はexit0。

検証済み：背景compile/trace終了後 `RUST_TEST_THREADS=1 cargo llvm-cov --locked --workspace --fail-under-lines 80` はexit0。parent tests197（CPU31/U2diff38、その他は先行189件の構成と同じ）、lines4233/missed254/94.00%、regions90.20%。30秒watchdogと80%閾値は維持した。修正前後のrawログは `docs/u2/repairs/` に保存する。先行189件/93.64%および先行fuzzは修正前sourceの履歴として保持する。

検証済み：Linux `cargo deny --locked check` の初回はexit1（no such command: deny）。その後rootが公式cargo-deny0.20.2 Windows asset（SHA256 975a22143262fd27476d19ee00c7af67978426e40e1dee94eed6bbade1cf87dc、release metadata digest一致）をtarget/u2-toolsへ取得し、`cargo-deny.exe --locked check` はexit0、advisories/bans/licenses/sources全ok。local未実行GAPはこの後続観測で解消した。

最終修正sourceのASan検証：単一runnerで `LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run --fuzz-dir fuzz cpu_u2 -- -max_total_time=600 -max_len=4096 -timeout=30 -rss_limit_mb=2048`、続いてmmu_u2（max_len4608）を逐次実行し、CPU1276258/MMU1706799 runs、各601秒、両方exit0。CPU既存iced table suppression12件のみ。ログは `docs/u2/repairs/r01-{cpu,mmu}-fuzz-final.txt`、入力archiveは `target/u2-evidence/r01-fuzz-inputs.tar`。Windows fmt --all -- --check もexit0。
初回CPU fuzzはexit1：No such file or directory: fuzz/corpus/cpu_u2 とASan suppressions file読取失敗。途中に証拠回収用linux-dev.sh同期を呼んだ。同scriptは/work/target以外を除去する実装だが、失敗時点との直接因果は推測/未検証。失敗ログを `r01-cpu-fuzz-sync-failure.txt` に保持し、同期終了後の単一直接docker runnerで両600秒を最初から回収した。後続では同期/compile/traceを重ねなかった。
検証対象production exec.rs SHA256=e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0。CPU内部test source SHA256=4b2680bdc99b5c3263f2472a6b4000b030810df0958fd76d82e896f529865d7f。閾値、watchdog、nightly予算、Testing Contractは変更していない。

## 先行attemptのU2再確認手順（履歴）

既存のbootstrap説明・過去の189件/93.64%は当時の観測である。保存済み最終productionの証拠はdocs/u2/repairs/r01-workspace-coverage.txt（U2 diff38、parallel10、CPU31、全workspace197、94.00%）、r01-cpu-fuzz-final.txt（1276258 runs）、r01-mmu-fuzz-final.txt（1706799 runs、各601秒）、u2-cargo-deny.txt（4項目ok）。今回はまだ再実行していない。exec.rs hash一致とclaims/receipt照合でsource不変が確認できたら、これらを再確認の根拠に使い、全体suite/fuzzの反復を要求しない。

不足や関係source変更がある場合だけ実行するunit限定commands（現在のfixture/filterが存在することを先に確認し、0件を合格にしない）：
```
cargo test --locked -p paludarium-harness --test diff_u2
cargo test --locked -p paludarium-harness --test parallel_u2
cargo test --locked -p paludarium-cpu --lib u2_segment_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u2 u2_segment_atomic_forms -- --exact --nocapture
cargo test --locked -p paludarium-harness --test diff_u2 u2_atomic_gs_ -- --nocapture
```
期待件数は順に38、10、5、1、2。native/parallelはLinuxで実行し、毎回native期待値を生成する。全体80% gateと600秒ASan予算は別の品質確認として維持し、新しいproduction修正がある場合だけ必要な再実行を判断する。Runtime未変更のu2_filter0件をPASSとして使わない。

scripts/linux-dev.shはsync時に/work/target以外を除去するため、live fuzzとの並行呼出しは禁止。同じvolumeの実行を逐次化し、完了後に証拠回収する。今回の別project background buildは停止せず、性能値の比較を行わない。先行timeout/tee/fixture/fuzz filesystem失敗は履歴として保持する。
