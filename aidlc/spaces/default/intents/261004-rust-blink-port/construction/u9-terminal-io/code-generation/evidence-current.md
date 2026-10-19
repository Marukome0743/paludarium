# U9 現行公開端末契約と検証

## Steps22〜24：記録更新と証拠の適用範囲（2026-10-11 JST）

検証済み（今回のhash照合）：旧署名 `541b439668222710c7aa0f62afd508a8870d658c`／CI38062686224の316入力は309一致・7変更、U9 manifest37パスは36一致・1変更。旧raw87ファイルは87/87 hash一致。結果は `verification/step22-source-audit.json`。両lock、Cargo設定、Rust pin、LSan suppressionの6入力は6/6一致。製品・既存試験・旧原本・manifest・traceabilityを変更していない。以下のSteps1〜21と対応表の「現行」は各履歴時点を指す。

差異の分類：`native_fs.rs` はWindowsの100ns精度に合わせた既存mtimeテスト2件のみで、`#[cfg(test)]` 前の製品12120bytesは旧／現在ともSHA256 `bbe3820516c5f003475da68f8bf0fe2028e44c0c84ff7bd66517c0a314dc34a1`。U11 wasm `abi.rs`・`filesystem.rs`・`coordinator.mjs` は大規模FS破棄の製品変更、`u11-api-check.mjs` はその回帰追加、`u6-check.mjs` は総数assertの103→102整合。`u11-fuzz.yml` は起動条件・LLVM symbolizer・両lockとbinary記録の診断設定変更。これらを全入力不変とは扱わない。

限定再利用：U9のnative端末製品・guest・diff入口とそのRust依存は同一（native_fsの製品prefixを上記で分離）。旧Linux差分14件、3OS内部Linux24／macOS・Windows23、公開API6／compile_fail3／CLI2、coverage旧13ファイル2693/3202=84.10%・追加10ファイル2156/2397=89.95%は、同じ製品と測定対象に対する有限な保存結果として保持する。今回これらを新規実行していない。変更済みWindows mtimeテストの旧実行は現行テストの成功証拠としない。

限定ASan根拠：旧closure88入力は87一致・native_fsのテスト部のみ相違。旧実使用rustc `32dba69d69c5b10ea89a4042de8d0619f7756203`／LLVM23.1.3／cargo-fuzz0.13.2、両lock・target・suppression・flags・seed1／timeout30／rss2048／既定max_len4096は保存原本と同じ設定。旧4対象load_elf／syscall_args／vfs_paths／mmu_opsの601秒証拠と当時の同一instrumented binary再ビルド結果は履歴として維持する。今回binaryを再ビルドせず、現在binary同一の新実測は主張しない。U11診断workflowのsymbolizer設定変更後の実行へ旧証拠をそのまま置換しない。

未検証（今回）：U9専用の新しいLinux差分・coverage・3OS品質・Node／本物Safari・ASan実行。wasm製品が変わっているため旧Node／Safari20ケースは現行wasm成功へ再利用しない。必要なら承認済み手順のdiff_u9、固定13＋追加10 scopeのcoverage、同production module/nativeのNode／Safariを再実行する。ASanの新binary同一性が必要なら既存4対象を同compiler／設定で再ビルド照合し、不一致対象だけ600秒実行する。今回は追加試験を行う承認範囲ではない。

正式検査・独立再レビュー・最終確認は今回の有限記録更新を対象にする。承認済み `verify-current-u2-u11-revalidated.py` はU2／U11／U10の結合照合でありU9専用の新coverage／Linux差分／Safariの代替ではない。strict guard・80%下限・30秒制限・mask・測定分母を保持する。U11の同時dispose修正とID競合の完全解消は未検証。



## Steps19〜21：Clippy・実行compiler整合と現行検証（2026-10-11 JST）

検証済み：diff_u7.rsは8byte分割の `as_chunks::<8>().0.iter()` / `from_le_bytes(*bytes)` のみに修正。比較case・mask・mtime意味論は保持した。公式確認を行った2026-10-10 UTC時点のRust nightly-2026-10-10にrootと実行可能script/CI15設定を統一。日付の変化だけで準備中の版を再更新しない。版と全変更pathはverification/step19-official-tools.json・step19-toolchain-inventory.json・source-manifest.json。履歴文書の旧版は保存し、mise.tomlはroot原文を隔離checkoutへコピーしただけでツール設定は変えていない。

検証済み：署名GitHub Verified `541b439668222710c7aa0f62afd508a8870d658c` のCI `38062686224` で8ジョブ成功。3 OSのU9内部（Linux24・macOS/Windows23）・公開API各6・compile_fail各3・CLI各2は実exit0。Linux fmt/Clippy -D warnings、cargo-deny0.20.2のadvisories/bans/licenses/sources全4検査はexit0。sourceはSafari/U10も含む全316入力・両lockがbefore/after/current一致。署名・全job metadata・rawhashと実exitはverification/step20-fixed-proof.json、connector完全joblogと生JSONはstep20-retry-raw/。

検証済み：fresh native Linux diff_u7 64件・diff_u9 14件成功、ignored0。U9の旧13 production filesは2693/3202行（84.1036852%）、追加10filesは2156/2397（89.9457655%）、全23filesは4849/5599（86.6047508%）。旧13の集合を変更せず追加集合と分離し、80%を維持した。保存旧CIの2630行と今回3202行の増加も隠さない。production wasmと同CI fresh Linux native期待値をNode26.11.1・本物Safari26.6.2で全20case比較、case IDsとmodule/native SHAは同一。Safari17.512秒、COOP/COEP・sharedMemory・productionLauncher true、driver_reaped/server_closed true、実exit0。28秒operation/30秒whole-process watchdogを維持。Safari版はrunner付属の実測値で、最新版の主張ではない。

検証済み：U10固定probe/aubeのbuild.py選択compilerはroot/lockと同じnightly-2026-10-10。build実exit0、static ELF2本、固定aube revision・上流Cargo.lock・許可済み限定license例外を維持、guest依存audit2本exit0・source_unchanged true。製品build.pyとguest依存の意味論は変更していない。

検証済み（限定再利用）：旧load_elfとU7のsyscall_args/vfs_paths/mmu_ops各601秒ASan/LSanは、新compilerで各targetを再ビルドしたinstrumented binary SHAが4本全て完全同一。target依存8crate union88入力・両lock・既存suppressionも旧/新一致、実rustc commit32dba69d・LLVM23.1.3・cargo-fuzz0.13.2・address flagsが一致。seed1/timeout30/rss2048/detect_leaks1/既定max_lenを維持。詳細はverification/step20-sanitizer-reuse.jsonと新旧build/fuzz生ログ。600秒fuzzを今回再実行したとは呼ばない。旧294全入力は設定/テスト4pathが変わっており新316との全入力一致を主張しない。U1/U7の旧hello・coverage・Windows・fuzzは同一production dependency/compilerに対する限定再利用で、今回fresh executionはU7/U9差分とU9全検証のみ。

失敗履歴：旧38059659099はClippy exit101、次38062101203はU10build exit0の後、生成Python cache `tests/guests/u10/__pycache__/evidence.cpython-312.pyc` を入力扱いしaudit exit1で全CI failureだった。実Python sourceは保持して__pycache__だけ生成物として除外し、境界確認exit0後に全CIを再実行した。失敗はverification/step20-failed-audit.jsonとstep20-u10-failed-job.logに保存した。成功として読み替えない。

未完了：独立レビュー・新canonicalの人によるコマンド承認/実行・完了承認。候補 `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-aligned.py` は構文検査のみ、未実行。旧canonicalを保存し、候補は現在316の完全一致と旧raw内容検査を維持し、旧294との差分4pathを旧/新hashに固定する。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、全probe/aube実行、並行ID競合完全解消は未検証。strict guard・品質下限を維持。


## Steps16〜18：承認済み追加検証の結果（2026-10-10）

検証済み：製品変更なし。署名Verified `fa4cddce6c0af461f4223455aeff0c5fba0f40db`、CI `38059659099` はcompleted/failure。7ジョブ中6成功、Linux qualityの最新Clippyだけ失敗した。失敗を他の成功で読み替えない。各Linux production/coverage/ASanと3 OS qualityの294入力・両lockはbefore/after/current一致、source比較exit0。proofはverification/step16-fixed-proof.json、rawはstep16-raw/。Safariは同じ署名SHA checkoutと同じartifactを使用したが、Safari独立の294 before/after監査ファイルは未取得。

検証済み：fresh native Linux `diff_u9` 14/14成功・ignored0、diff/coverage/reportの実exit0。既存packagesと除外regexを保持した現行全23 production filesは4849/5599行（86.6047508%）。旧CI37773320167の13ファイルを全て保持した個別集計は2693/3202行（84.1036852%）、共有追加10ファイルは2156/2397行（89.9457655%）。旧13ファイルの2630行から現行3202行への増加を隠さず、追加10ファイルで旧scopeを置き換えない。原LCOV/JSONを保存した。80%の下限を変更していない。

検証済み：3 OSのU9内部（Linux24・macOS/Windows23）、公開API各6、compile_fail各3、CLI各2は実exit0・ignored0。Linux Host managedPTYのsubprocess helper結果は別途記録し二重計上しない。fmt成功後のClippyは`crates/paludarium-harness/tests/diff_u7.rs:154` の `chunks_exact_to_as_chunks` 新lintでexit101。cargo-denyはその後のコマンドにつき未到達・未検証。最小未適用差分と正確な引用はverification/step16-findings.md、connector取得の完全job logはstep16-linux-quality-job.log。

検証済み：production wasmを最新nightly-2026-10-10（元scriptと同じbuild-std/flags）で構築し、同CIのfresh native期待値とNode26.11.1・本物Safari26.6.2で現行全20ケース成功。case ID一致、module SHA `4482b1574987ff62cc8f9f872e42e5dbe6f4fc91273103da6abc0dd8ffd18fe3` とnative JSON SHA `62de7aebb39896bf11de30991cd6883527f558b52fb073cb104d76e7ccf22c69` は両環境で一致。SafariはCOOP/COEP・sharedMemory・productionLauncher true、16125ms、driver_reaped/server_closed true、実exit0。28秒operation/30秒whole-process watchdogを維持した。Safari版はCI image付属の観測値であり最新版だとは主張しない。

検証済み：load_elf ASan/LSanは17,380,733 runs / 601秒、fuzz・最小C2回・source比較exit0、ASan/LSan symbolsを確認。seed1、timeout30、rss2048、既定max_len、detect_leaks1、既存suppressionを維持。U7のsyscall_args/vfs_paths/mmu_ops各601秒は同294入力に限って再利用する。任意入力・全UBの保証、夜間scheduled実行とは呼ばない。

未完了：NFR3（Clippy警告ゼロ）、NFR8（最新cargo-denyの全4検査）、NFR9（製品pin nightly-2026-10-01と診断/local nightly-2026-10-10の整合）をGAPに保持。製品修正・toolchain更新は今回範囲に含めない。正式検査/独立レビュー/新しい最終確認コマンド承認/完了承認は未完了。別名候補 `verification/verify-current-u1-u7-u9.py` を具体化したが未実行で、CI failureを拒否する。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、全probe/aube、並行ID競合完全解消は未検証。

## Steps13〜15の履歴：追加検証前（2026-10-10）

検証済み：製品変更なし。現行署名5fa16398eae31ec178bfd93d3029b24ee31ac5e5とU9 manifest19パスは19/19一致（verification/step13-current-claimed.json）。保存7069538fの19パスは12一致・7変更、保存187パスは140一致・47変更。旧ASan/Windowsの各155パスは114一致・41変更（verification/step13-source-comparison.json）。下のSteps8〜12「現行」は当時の履歴であり、今回の実行証拠ではない。

検証済み：macOS aarch64で最新nightly-2026-10-10実体cargo/rustc/rustdocを使用。U9内部Host7/Kernel8/Runtime8（計23）、公開API6、Host compile_fail2+Runtime1（計3）、CLI2が成功、全exit0・ignored0。内部23/API6/CLI2は実行前に--listで非0を確認。Linux限定Host managedPTYはmacOS cfgで対象外であり今回成功件数へ足さない。rawはverification/step14-*.log。最初のcargo単独実体呼出しはPATH上rustc1.99との混在でexit101、RUSTC/RUSTDOCを最新実体へ固定して実行した。製品のrust-toolchain.toml nightly-2026-10-01は変更せず、診断環境との区別を残す。

検証済み：U7の最新601秒ASan/LSan syscall_args 1,455,696、vfs_paths 3,675,837、mmu_ops 3,003,322（CI38053646678）は各294入力・両lockのbefore/after/current一致、exit0。共有proof109 rawhashも一致。これは同一sourceの対象限定安全性証拠の再利用でありU9専用coverage・端末差分の代用ではない（verification/step13-sanitizer-reuse.md）。

未検証：現行U9 Linux native diff_u9 14ケース、同U9測定scope coverage80%、現行production wasm/Node/本物Safari既存14ケース。旧証拠の依存source/lockが変わったため現行合格へ再利用しない。旧load_elf/cpu_u2/mmu_u2/decodeの依存closureも変化している。U9に直接影響するELF→argv/envpのload_elfは新規601秒診断が必要、他3対象をU9完了のために無条件反復しない。現行全体clippy/3OS/供給網の今回実行は未実施。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、任意入力・全UB、並行ID競合完全解消は未検証。

## 追加検証前の提案履歴（後にSteps16〜18を承認）

正式sensor実行：traceabilityは6GAP（FR9.1/NFR1/NFR2/NFR3/NFR8/NFR9）、missing/invalid/orphan0。required-sectionsはplan/instructions/summary各PASS。step15-sensors.json。macOSのdiff_u9 --listはcfgにより0件、現行Linux差分の成功として扱わない（step14-diff-list.log）。Step15は独立レビュー・追加証拠・最終確認・完了承認待ち。

製品を変更せず、現行全294入力と両lockを固定した診断CIで、(1)fresh native oracleを各実行生成するdiff_u9、(2)既存Host/Kernel/Runtime/CLIのU9 scope・除外regex・分子分母を維持したLinux coverage80%以上、(3)現行production wasmを再ビルドし同run native期待値とNode/本物Safariの現行全ケース（過去14件以上）を比較、(4)load_elfのみ600秒ASan/LSan（seed1・timeout30・detect_leaks1・既存suppression・最小C診断維持）を追加する。3OS U9内部/API/doc/CLI・fmt/clippy・依存検査は診断CIに併せて記録し、対象0件/skipを成功にしない。既存30秒watchdog・比較条件・coverage分母を維持する。全入力・両lock・生ログ・exit・署名を保存する。Windows隔離と3ASanは同一sourceのU7証拠をhash対応で再利用する。

具体入口：`bash tests/guests/u9/build.sh target/guests/u9`、`cargo test --locked -p paludarium-harness --test diff_u9 -- --nocapture`、ci.yml U9 coverageの既存cargo llvm-covコマンド、`bash scripts/build-wasm.sh`、`node packages/paludarium-wasm/tests/node-check.mjs packages/paludarium-wasm/paludarium.wasm target/production-wasm-evidence/native-results.json`、本物Safariで同じrunChecksを実行する既存browser入口、`cargo fuzz run load_elf --sanitizer address -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048 -seed=1`。追加範囲承認後に実体の最新tool版・正確なwasm/Safari commandを固定し実行する。現行canonical verify-current-u1-u7-r04.pyはU9の未取得結果を検証しないため、それだけをU9完了証拠にしない。

## Steps8〜12 現行ソース確認（2026-10-08）

検証済み：Host TerminalAttributes/TerminalInfo と Runtime TerminalInfo は non_exhaustive と全フィールドconstructorを持ち、外部literal利用側を移行。Default・ioctl意味論を保持。外部crate6件、compile_fail doc3件、Host/Kernel/Runtime U9内部23件（macOS）、CLI2件が成功。source-manifestの19パスが正規一覧。

検証済み：署名7069538f1bdadb62e275f0c8c4f580ac3b70e9b5、CI37773320167の8jobs成功（3OS/lint/deny/native差分14/coverage/production wasm）。Linux行coverageはworkspace92.67%、U1 83.08%、U9対象scope82.66%。旧追加行122/130とは別分母。verification/step11-metadata.json、step11-run-37773320167.log。

検証済み：新CI生成本番module＋同CI native期待値でNode/実Safari27.0.1各14ケースPASS。Safari16861ms、COOP/COEP・sharedMemory・nestedWorker・Rust共有allocator/AddressSpace・wait/notify・active disposeの確認。stdout/statusは6guest nativeと一致。28/30秒watchdog不変。step11-production-wasm/、step11-node.log、step11-safari-third.json/log。初回sandbox /status接続失敗とCUA無応答中断はstep11-safari-history.mdに保存。

検証済み：syscall_args1250323、vfs_paths3202926、load_elf18110999、cpu_u2 3088147、mmu_u2 3418642、decode75149340、各601秒ASan+LSan exit0、最小C各2回exit0、seed1・detect_leaks1・既存suppression固定、155paths before/after/host一致、crashなし。step11-sanitizer-proof.jsonと各step11 artifact raw。VFS専用run37773925007/署名0dc8ca8bは7069538fから診断workflow1追加のみで製品bytes同一。

検証済み：同現行head Windows run37773320171、fixture1000反復/交換34/共有違反retry311/597ms、outside不変・strictcleanup・exit0、155source paths一致。旧8cbaの154paths/1000/55/473/881msは履歴として維持。fixture本体を変更していない。

187application/build/doc pathsを署名CI bytesと照合済み（既知のexact .gitignoreおよびSafari documentary差のみ）。新external API test1追加が旧186/154から187/155となった理由。主CI/Windowsfixture/他Unit成果物は変更せず、隔離workflowは製品manifestに含めない。旧canonicalはsource変更を検出してexit1、step11-old-canonical.log保持。新completion checkerは具体化後、人のcommand承認前には実行しない。

未検証：macOS/Windowsの実端末backend、wasm tty（明示unsupported）、Chromium/Firefox、probe/aube全体、guest clone/futex/JIT/任意ゲスト、全入力/全UB保証。各600秒は有限固定seed診断であり夜間scheduled runとは呼ばない。80%/30秒/nightly2026-10-01/600秒は保持。

## Steps1〜7 当時の履歴（以下は当時のsource/CI/未検証状態）

# U9 現在の実装・検証証拠

## native期待結果を取得した順序

検証済み：guest14ケースとoracle.pyを製品実装前に用意した。初回native runnerはstdin/input重複指定のValueErrorで失敗し、guest意味論の失敗として扱わない。raw native-oracle-initial-failure.logを保持。Python runnerを修復し、実regular tempfileを用意した署名commit fd468eed4b9fd86680ef8bea4583d403720aaa4fでnative run37712962944全4jobs success。ubuntu-latest job113102874492、ubuntu22 job113102874511の各14行・exit0はnative-oracle-ubuntu-latest.log/native-oracle-ubuntu-22.04.log。両結果を全文確認後にHost/Kernel/Runtimeを実装した。

commandは `bash tests/guests/u9/build.sh target/guests/u9` と `python3 tests/guests/u9/oracle.py target/guests/u9`。argvの空文字/二語引数とenv値、stdin3bytes/EOF、stdout/stderr、pipeTCGETS/winsize、badfd、stdinPTY TCGETS/winsize/EFAULT/unknown/dup、regularfile、closedfd、stdout非端末を含む。

PTY入力はiflag/oflag/lflag0、cflag0xbf、line0、cc6=1、寸法rows37/columns101/pixel0で固定する。期待出力は各native実行から取得し、保存logはaudit用途のみ。stat/time/住所/pidなどの除外を使わず、stdout/stderr/exitを全byte比較する。runtime期待の固定ファイルは作らない。

## ローカル実行（Docker VMM、QEMU診断）

全commandのprefixは `bash scripts/linux-dev.sh`。cargoはコンテナの固定nightly。native意味論の最終証明にDockerだけを使わない。

|command suffix|exit/結果|raw log|
|---|---|---|
|cargo test --locked -p paludarium-harness --test diff_u9 -- --list|0、14 tests/0benchmarks|tool stdout、implementation-notes.md|
|bash -c 'bash tests/guests/u9/build.sh && python3 tests/guests/u9/oracle.py target/guests/u9'|0、14行|verification/docker-oracle-diagnostic.log|
|cargo test --locked -p paludarium-host -p paludarium-kernel -p paludarium-runtime --lib u9_ -- --nocapture|0、Host8/Kernel8/Runtime8|verification/local-internal.log|
|cargo test --locked -p paludarium-harness --test diff_u9 -- --test-threads=1 --nocapture|0、14親cases|verification/local-diff-u9.log|
|cargo test --locked -p paludarium --test command u9_ -- --nocapture|0、2tests|verification/local-cli-clippy.log|
|cargo clippy --locked -p paludarium-host -p paludarium-kernel -p paludarium-runtime -p paludarium-harness -p paludarium --all-targets -- -D warnings|初回101（新規未整形と不要mut）、修正後0|verification/local-cli-clippy.log / local-fmt-clippy-final.log|
|cargo fmt --all --check|0|verification/local-fmt-clippy-final.log|

HostのLinux managedPTY childはHost8の中の1親case、child1passを合計へ重複加算しない。非Linuxはこのcaseのcfg除外でHost7。Kernel8/Runtime8はfakeHostとchecked-memory/guestABI/Config接続の内部テストで実装後に追加した。CLI2は空引数維持とstdout/stderr分離。差分14はnative/emulated組全体に30秒kill/reap watchdog、Python guestにも30秒timeoutを保持。PTY helperも30秒を保持し、失敗・timeoutをskipしない。

## 最終CIと未検証

最終CIとソース一致・coverageを取得済み（後続の最終結果）。ci.ymlはLinux差分にdiff_u9を追加し、Host/Kernel/Runtime/CLI/harness対象の広いクレートcoverage80% gateとLCOV artifactを生成する。この分母はU9変更行限定ではない。現在U9の600秒ASan fuzzは未検証、NFR2/NFR3 GAP。macOS/Windows NativeHost端末照会はNoneを返し、実機tty動作の合格を主張しない。fakeHost/Configで内部機能を確認する。wasm/Safariとprobe/aube全体は未検証。取得した証拠だけでこの節を更新する。

## 取得途中の記録とrunner確認（履歴）

検証済み：18 claimed source filesはread-only `git show af9b739d742a9552f44fc1515646c862b19e5de2:<path>`各exit0でlive bytesと全件一致した（verification/source-bytes-current.json）。native run37713953340の全4jobs成功、CI37713953347のcoverage以外6jobs成功は親から取得したログを照合した。native differential ci-native-differential.log:1189は14親cases passed。coverage成功とはまだ扱わない。

raw ci-linux-unit.log/ci-macos-unit.log/ci-windows-unit.log/ci-native-bookworm.logの名前再集計はverification/final-ci-counts.json。Linux/Bookworm Host8・Kernel8・Runtime8・CLI2、macOS/Windows Host7・Kernel8・Runtime8・CLI2を確認。Linux Host managedPTYのみcfgによって非Linuxにはない。非Linux実機ttyは未検証のまま。

検証済み：承認手順の5 --list commandを再実行しexit0、順に8/8/8/14/2 tests・各0benchmarks（verification/local-filters-list.log）。差分入口の初回14件検出は実装前に行い、Host/Kernel/Runtime/CLIの個別--listは実装後の初回実行より後に確認した。後のlistingを実行前の証拠へ遡及しない。各初回の実テスト結果でも非ゼロ件数を確認した。customのnative期待取得→guest/syscall実装、内部層実装→単体テストの順序は保持した。

## 最終署名CI・coverageとソースbinding

検証済み：署名commit af9b739d742a9552f44fc1515646c862b19e5de2（GitHub verified=true/reason=valid）でCI37713953347の7jobs、native37713953340の4jobsすべてsuccess。親のcanonical verify-native-ci.pyはexit0で11jobsと162tracked application filesのsource一致を確認。U9自身のread-only git showによる18 claimed files/live/snapshotのbyte一致も確認した。

再現CI：[CI37713953347](https://github.com/Marukome0743/paludarium/actions/runs/37713953347)、[native37713953340](https://github.com/Marukome0743/paludarium/actions/runs/37713953340)。Linux実機のcommand `cargo test --locked -p paludarium-harness --test diff_u1 --test diff_u2 --test parallel_u2 --test diff_u4 --test diff_u9 -- --nocapture` はexit0、ci-native-differential.log:1189でU9親14 passed/0 failed。native-bookwormのworkspace全体もexit0。毎native差分実行時にoracle.pyが期待結果を生成する。各OSのU9名前・件数はfinal-ci-counts.json。

coverage job113106033576はexit0。ci-coverage.log:2340はwholeworkspace7155 total/524 missed＝92.68%、2802はU1 packages6905 total/1171 missed＝83.04%、3172はU9対象クレート全体2596 total/453 missed＝82.55%。最後のクレート分母はHost/Kernel/Runtime/CLI（harness報告除外）既存行を含み、U9新規行の割合ではない。

検証済み：LCOV artifact11523113003のarchive SHA256は8be7b3c2dcf12df7fcd30a8ae960e55d4e8d71003c764a2c346a11ede043f8c9（ci-coverage.log:3196）。取得したverification/u9-coverage.lcovを、oracle親fd468eed→af9b739dの6製品source file追加行と交差させた。LCOV DAが実行可能として観測した追加行130中122 covered＝93.84615384615384%、floor80 PASS。unchanged/deleted/test/non-instrumentedを除外する。詳細scopeと未coverage8行はu9-added-line-coverage.json。

独立再集計の実コマンド：read-only `git show fd468eed4b9fd86680ef8bea4583d403720aaa4f:<path>`各exit0、Python difflib.SequenceMatcher(autojunk=False)でlive追加行を抽出、LCOVのSF/DA行へ交差しcounts>0をcoveredとして集計した。exit0、同じ122/130。結果はverification/u9-added-line-coverage-independent-check.json。これは追加実行可能製品行の測定であり全ファイル・全条件のcoverage100%を主張しない。

現在U9限定coverage80%の不足は解消した。現行600秒ASan fuzzは実行していないためNFR2/NFR3 GAPを維持する。macOS/Windows NativeHost実機端末は未検証かつ照会実装はNoneであり、fakeHost/仮想Config機能の成功から実機ttyを推定しない。未知ioctl、TCSETS等の端末制御、stdin以外をnativeTTYへ接続したguest差分、異なるline disciplineの全挙動は本corpusで未検証。Linux NativeHost自体はmanaged stdinPTY・pipe stdoutの実機内部testで確認した。
