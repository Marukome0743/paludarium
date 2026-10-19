# U7 単位限定テスト手順

## 今回Step48：共有のabi.rsの再確認

新しいテスト・CIの実行はない。U7の記録を直した場合は、project rootで正式sensor 2件を実行する。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u7-vfs/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u7-vfs/code-generation/code-summary.md
```

期待する結果：sensor 2件はpass。checkpointでは、今の正式確認コマンド `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` がexit 0になる。

## 前回Steps45〜47：Testing Contractと承認記録の更新

製品・既存試験・旧原本を保持し、公式renderの現行Testing Contractに沿ってU7記録だけを更新する。下記のU7限定runnerと保存証拠の適用範囲を先に確認し、担当ソース・依存・両lock・実使用compiler・設定が一致する範囲だけ再利用する。旧成功を今回の新しい実測へ読み替えず、不一致と未検証を記録する。新しい重い試験や製品修正が必要なら具体的な追加案へ返す。

正式sensorと独立レビュー後、承認済み `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py` を標準checkpointで実行する。このコマンドは有限の保存証拠確認であり、U7限定テストrunnerや今回の全VFS再実測と混同しない。既存coverage80%、guest30秒、fuzz600秒、比較maskと分母、strict guardを維持する。今回のU7最終確認・完了承認・U11遷移は実施前のため未検証とする。

## 履歴Steps40〜44：R-04の負mtime修正

Linux nativeの実ファイルでepoch前後・-1ns・負整数/小数秒・正時刻のpath statとopen-file fstatを先に取得し、現行EIOをRedとして保存する。負時刻をfloor秒と0以上10億未満のnsecに分けるLinux ABIへ合わせ、Host/VFS/Kernel/wasm利用側を整合する。変換・overflow・既存正値範囲・ABI byte符号の内部テストは実装後に追加し、native差分をGreenにする。mtimeに無関係なclock syscallを変更しない。

既存diff_u7とu7_/u11_のmtime回帰、wasm filesystem/ABI/JS decoderの影響する回帰を使用し、新ケースのexactコマンドと件数を確認して保存する。修正後source/設定/両lockを固定して、下記履歴に示すWindows exact回帰とLinuxの同scope llvm-cov80%+fresh diff_u7を再実行する。vfs_paths/syscall_args/mmu_opsの変更依存に各600秒ASan/LSanを適用し、seed1/timeout30/rss2048/既存max_len・suppression/detect_leaks1を保持する。最新ツール具体版、minimal ASan終了、全raw/exit/runs/binaryhash/symbols/corpus/crash/source before-afterを保存する。

修正前7eb固定のcanonicalは修正後ソースの合格証拠に読み替えない。新しい確認コマンドが必要なら、実行前に具体的なコマンドと照合範囲を提示して人の承認を取得する。正式sensorと独立レビュー後、選択された確認・完了承認へ進む。80%/30秒/600秒を下げず、R-04をU11へ先送りしない。

## 履歴Steps36〜39：不足4項目の現行再検証

承認後、現行全入力と両lockを固定して隔離診断CIへ配置する。公式情報で最新nightly/cargo-fuzz/cargo-llvm-cov/Actionsなどの具体版を確認・固定し、診断環境だけで使用する。製品設定・lockは変更しない。以下の版テンプレートは確認後の具体版へ解決してworkflowへ保存し、直接実行しない。

```sh
cargo +<確認済み最新nightly> test --locked -p paludarium-host --lib native_fs::u7_tests::u7_native_windows_symlink_rename_race -- --exact --test-threads=1 --nocapture
cargo +<確認済み最新nightly> llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1
cargo +<確認済み最新nightly> llvm-cov report --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --json --output-path target/u7-diagnostic-evidence/coverage.json
cargo +<確認済み最新nightly> fuzz run --fuzz-dir fuzz --sanitizer address vfs_paths -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
```

Windows fixture条件は既存テストの実symlink生成、victim1000以上、成功交換1以上、outside内容/一覧不変、whole-child30秒kill/reapとstrict cleanupを必須にする。Linux coverageは既存scope/除外/80%を維持し、同じinstrumented runのJSONを保存する。diff_u7の期待値は同CIでnativeから作り、0件やskipは成功にしない。ASAN_OPTIONS=detect_leaks=1、LSAN_OPTIONSは既存fuzz/lsan.supp絶対パス、最小ASan終了2回、600秒以上・非ゼロruns・exit0を確認する。両lockと全入力before/after/current一致、版、raw/exit、binaryhash/symbols、corpus/crashを常時保存する。

未達・製品不具合は具体的な再現と最小対応案を提示し、閾値やsuppressionを緩めない。1970年以前mtime課題はU11対応へ残す。正式sensor・独立レビューと既存承認済みcanonical checkpointを更新する。strict guard、80%/30秒/600秒と比較maskを維持する。

## 履歴Steps33〜35：現行ソースと証拠の再確認

計画承認と別の内容確認後に、U7 manifestを展開して現行ファイルと署名済み7eb1819f52acede33e83775374dd4ee93edf643bをバイト照合する。保存済みWindows隔離回帰・Linux差分・U7限定coverage・vfs_paths ASanは、実行時の全依存ソース・lock・suppression・設定の一致を確認できた範囲だけ再利用する。今回U4 syscall_argsの601秒成功は別の新実測として区別する。不足は未検証と具体的な限定検査案を提示する。

正式sensorは既存 sensor-traceability / sensor-required-sections をU7成果物へ実行する。新しい独立レビュー後、承認済み `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py` を標準checkpointで実行する。これは保存証拠の有限確認であり、新しいVFS全入力検証ではない。strict guard、80%下限、30秒制限、各600秒fuzz、既存比較maskを保持する。1970年以前のmtimeの既知課題を未修正のまま成功と記さない。

## 履歴Steps28〜32：Windows一時fixture隔離回帰

現在はplanningのみ。新Plan Approvalと内容確認後、ユーザー所有forkのwindows-latestでNativeFsのWindows専用test-only回帰を実行する。対象はCIが作ったtemporary fixtureのroot/pivot/outside sentinelだけで、実ユーザーファイル・外部システム・OS設定を操作しない。製品意味論は変更せず、観測不具合は再現情報と別修正計画へ返す。

承認後にAPIとrunnerを限定確認し、fixture内directory symlink作成を実際にassertする。権限不成立をskip成功とせず、stderr/exitを残してFAIL/未検証。root内pivotのsymlink/rename交換を専用スレッドで行い、NativeFsによるopen/write/create/stat/read_dir/link/rename/unlinkを1000回以上反復、成功交換1回以上、outside sentinel bytes/一覧不変を要求する。barrier/stop/join、handle解放、strict cleanupとwhole-child30秒watchdog（timeout時kill/reap、非ゼロexit）を用意し、子開始から終了までを監視する。test登録0件やfixture生成失敗をPASSにしない。

新test-only本体をmainとisolated診断workspaceへ同一bytesで用意し、Windows専用workflowから固定nightlyで次を実行する（API読取後に完全修飾test名を照合し、実行0件をfailにする）。PowerShellでnative exitを保存し、runner側に30秒子process watchdogを用いる。

```powershell
cargo +nightly-2026-10-01 test --locked -p paludarium-host --lib native_fs::u7_tests::u7_native_windows_symlink_rename_race -- --exact --test-threads=1 --nocapture
```

mutable jjとpushは実体jj/host権限を使いSSH署名を維持する。isolated診断bookmark codex/u2-asan-diagnosticへpush、connectorでhead Verifiedを確認する。新Windows workflowのみ必要runを起動し、main CI設定を変えない。workflow action SHA pinsを既存と同じ固定値にする。成功失敗にかかわらずOS/tool/env/fixture権限/iterations/exchanges/timeout/cleanup/stdout/stderr/exit/source before-after/CIhead/binary SHAをalways artifactへ保存し、実Windows本体の結果を旧Unix cfgテスト名成功と分ける。

Linuxは新しいfuzz/coverage実行として数えず、verification/step25-fuzz-proof.json（vfs_paths3132329/601秒）、step25-coverage-proof.json（4317/4772=90.4652%、diff_u7親63）、step25-syscall-reuse-proof.json（syscall_args1296522/601秒）とraw artifactを再照合する。178da99e/各CIbefore-after/currenthostの154関連paths一致を確認し、今回Windows cfg test-only差分だけを正確に分類する。Linux実行コードに影響しない根拠が不足ならGAPとし、下記既存exactscope/80%/600秒再測定手順を提示して親へ返す。保存Linux検査の条件はASan+LSan/address/seed1/timeout30/rss2048/defaultmaxlen/既存suppression/detect_leaks1/nightly固定のまま維持する。

main test-only変更がcanonical178固定検査へ与える差異はraw/exitで記録し、親のprotected verification-command選択へ返す。無断checker変更・条件除外はしない。限定sensors/4produces/manifestを実結果へ保存して書込を止める。Windowsが未実行またはFAILならFR3.2/NFR4 GAPを維持する。custom exact ordering、Standard各部品5–8、80%/30秒/600秒を維持し、今回guest意味論の実装はしない。

## 履歴：Steps21〜27の手順（Linux実測済み・Windows未実行）

新Plan Approvalと内容確認後、35 manifest claimsを展開して178da99eのsigned CI bytesと現在hostを照合し、Windows race本体・vfs_paths600秒ASan/LSan・U7限定coverage80%を実際のnative CIで検証する。過去88files/63差分/内部81・80/CLI専用2は履歴で、現行rawのcase名・親件数・条件を確認して記録する。必要なWindows test-only追加とisolated診断workflow以外の製品意味論・既存品質設定は変更しない。既存unit-scoped commandsは保持する。

旧U7限定89.79%と旧fuzz各601秒は履歴。現行全体coverageやU2/U4の成功をU7限定coverage/vfs_pathsへ代用しない。U4 syscall_argsの再利用は全製品意味論依存hash一致とtest-only差分の非該当根拠を確認してから行い、一致不成立ならGAPを維持する。QEMU runnerを使わずnative x86-64 Linuxで固定nightly/ASan+LSan readiness（最小C2回exit0）を確認する。

Windows旧race登録名成功はUnix本体の実行証拠ではない。新Windows専用testはretained NativeFs root内pivotをoutside directory symlink（権限により実在junction）と交換するattacker、outside sentinel、1000 victim反復、attack交換1回以上、共有barrier/stop/join、30秒whole-child kill/reapを要求する。fixture内の実reparse-point生成を先にassertし、権限なし/交換0/timeout/cleanup失敗はsilent skipせずFAIL/未検証。victimはopen/write/create/stat/read_dir/link/rename/unlinkをNativeFsから呼び、outside bytes/list不変を確認する。Windows handlesを閉じ、attackerをjoinしてからfixtureをstrict削除する。新テスト追加前にrunner/API確認、製品意味論の変更は観測不具合時の別計画とする。

native windows-latest（固定nightly、shellは既存CIに合わせる）で実行する新unit-scoped command：

```sh
cargo +nightly-2026-10-01 test --locked -p paludarium-host --lib native_fs::u7_tests::u7_native_windows_symlink_rename_race -- --exact --test-threads=1 --nocapture
```

isolated診断CIのnative x86-64 Linux（既存rust:1-bookworm/権限、/work mount、nightly-2026-10-01、cargo-fuzz0.13.2、ASAN_OPTIONS=detect_leaks=1）で実行：

```sh
LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp ASAN_OPTIONS=detect_leaks=1 cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address vfs_paths -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
```

既定max_lenを変更せず、最小ASan終了2回、非ゼロruns/600秒以上/exit0、source before-after、tool/env、ASan symbols/binaryhash、corpus/crash archiveを常時保存する。nightly scheduled runとは呼ばない。sourceに承認済みtest-only変更がある場合、178da99eとの厳密差分を申告し、新署名診断head/currenthost/CI before-after一致を確認する。

U7限定Linux測定のscope/除外/80%を既存手順と同じまま実行する（musl-toolsとllvm-tools-preview/cargo-llvm-covのreadinessを先に記録）：

```sh
cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1
cargo llvm-cov report --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --json --output-path target/u7-diagnostic-evidence/coverage.json
```

coverageはreport用再実行ではなく同じinstrumented runのJSONを保存し、全体/U1/U9の値に代えない。diff_u7は同じCIのnative期待値と比較し、現行通常CIがdiff_u7を含まない欠落を補う。raw/exit/covered-total/対象ファイル/除外/実tool version/hashをalways保存する。isolated workflowのみ追加し、既存mainCIは保持する。jj署名pushとconnectorVerified、artifact取得は親承認後。CI失敗でもログを保存し品質条件を緩めない。

旧review R-01/R-02 Resolvedと共有FR分類根拠を保持。実測成功したscopeだけGAPを更新し、任意入力・全UB・probe/aube全体・全wasm/全OSへ広げない。限定sensorsを保存する。canonicalが178da99e固定のため新test bytesを拒否する場合は拒否を保存し、親のprotected verification-command選択へ返す。検査器は無断変更しない。

```sh
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u7-vfs/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u7-vfs/code-generation/code-summary.md
```

固定nightly-2026-10-01、customの正確な順序、Standard各部品5–8、行80%、各guest/並行30秒、各ASan600秒、既存suppressionを維持する。今回はまだplanningのみ、本体未実行。以下は過去手順・実行説明で「今回」は当時のattemptを指す。

## 前提と現在の検証方針

今回の文書修正ではSteps 18–20だけを実行する。Windowsのu7_native_symlink_rename_raceはUnix専用本体を実行しないため、Windowsの並行root逃走確認は未検証と明記する。内部テストの登録・成功件数を本体の実行証拠に読み替えない。code-summary.mdのH2を最低2件にし、required-sectionsセンサーのPASSを記録する。製品・数値・既存GAP・SCMは変更しない。製品テストの再実行は不要。

ドキュメント根拠：Testing Contractのcustom ordering、Standard、Linux行80%以上、各guest/並行ケース30秒、各ASan fuzz target 600秒を維持する。rust-toolchain.tomlのnightlyを使う。MacではDocker DesktopのDocker VMMを維持し、Linuxコンテナ用scripts/linux-dev.shを使用する。Windows用PowerShell/Git Bashの呼出しは現在の実行手順に含めない。

保存済み実装について今回のSteps 15–17は署名付きネイティブx86-64 CIのソースとログを再照合する。Docker VMM内のamd64 QEMUの差を実機Linuxの意味論として扱わない。製品ソースは変更せず、過去のRed/Green/coverage/fuzzは測定時ソースと一致する範囲だけ証拠として使う。今回未実行のコマンドは未検証であり、下記は必要時に再現するためのU7限定コマンドである。

## runnerとネイティブ差分

最初のrunner確認はU7所属VFSクレートに限定する。

```sh
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1 --nocapture
```

ゲストsyscallはケースとLinux native期待結果を先に用意し、内部VFS/Host/Kernelの単体テストは実装後に作る。既存実装の過去の順序証拠はdocs/u7/inventory/diff-red.txt等を参照し、今回の再検証で過去の実装前Redを作り直したと主張しない。

各native/emulated guestには30秒の子プロセスwatchdogを維持する。diff_u7は63親caseを数え、childを二重加算しない。NULL stat、不正buffer/flags/dirfd、作成・read/write/seek/close、mkdir/unlink/rmdir、hard link、symlink/readlink、rename、getdents64、stat系、flockとdup所有権を確認する。stdout/stderr/終了状態、file bytes/種別/link count/errnoを比較し、非決定的なinode番号・pid・時刻の除外はdocs/u7/native-comparison.mdの限定範囲を使う。

## 単体・隔離・CLI接続

```sh
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium u7_ -- --test-threads=1 --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium --test command -- --test-threads=1 --nocapture
```

各部品5–8件以上、happy pathと少なくとも2つのerror/edge、重要境界のintegrationを確認する。MemFsのinode寿命、hard link共有、rename、offset/append/truncate/seek、relative cwd、非UTF-8/NUL、symlink loop、末尾slashと..を扱う。HostFsは各テスト独立のtemporary rootとoutside sentinelを使い、root外のread/create/write/link/rename/unlink/stat/read_dirへの効果がないことを観測する。mockだけでnative隔離を証明しない。flock並行・キャンセル・シグナル・close解放は30秒を維持する。Windowsでは開いたfixtureを閉じてからstrict removeする。guest cloneをU7で追加しない。

## coverage・lint・供給網

過去のU7限定測定89.79%（4203/4681）は測定時ソースの結果である。現在の依存が変更されていれば現在のU7限定coverageの証拠として使わず、NFR3のGAPを明記する。現在のCI全体/骨格coverageが80%を超えていてもU7限定測定へ読み替えない。

```sh
bash scripts/linux-dev.sh cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1
bash scripts/linux-dev.sh cargo fmt -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --check
bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --all-targets -- -D warnings
```

U7変更クレートの既存lib・専用diff・CLI integrationを測定し、未変更CPU等やharness基盤のreport行を除外する。covered/total・対象・コマンド・ソースhashを記録する。依存検査は既存cargo-deny CIのlicense/source/advisory結果とU7依存を照合する。閾値やwarning設定、action SHA pin、Cargo.lockを変更しない。全workspaceの正式な完了検証は親が既に承認されたcheckpointコマンドで実行する。

## ASanファジングと適用範囲

```sh
bash scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O vfs_paths -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
bash scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O syscall_args -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
```

各target 600秒、単一入力30秒、ASanと既存LSAN suppressionを保持する。重い処理は順次実行する。保存済みvfs_paths 859022 runs / 601秒、syscall_args 469436 runs / 601秒は過去の結果であり、targetと全依存のbytesが現在と一致するまで現在の合格とはしない。不一致ならFR9.3/NFR2/NFR3にGAPを残す。製品のquotaは追加しない。panic/ASan異常は再現入力とregressionへつなぐ。

証拠の再照合結果はU7 recordへ保存し、実コマンド・exit・テスト名・除外・hashを記す。U7の結果でprobe/aube全体、wasm/Safari/JIT、ホストマウントの全OS挙動を証明しない。

## 今回の照合結果

検証済み：Steps 15–17は保存済み署名CI11 jobsをbyte一致確認後に再利用した。製品変更・新規テスト実行なし。Linux差分63、内部Linux/macOS81・Windows80、CLI全6中U7専用2。旧600秒ASanとU7限定89.79%は現在証拠に流用せずGAPを保持する。raw行・条件・hashはevidence-current.mdとverification/を参照。上記コマンドは未実行の再現手順として保持する。
