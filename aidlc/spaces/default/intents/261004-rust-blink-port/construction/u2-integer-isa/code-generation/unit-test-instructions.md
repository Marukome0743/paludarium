# U2 Unit Test Instructions

## 今回Step73：Step72のレビューのMinor 2件を直す

記録だけを直すので、新しい試験はない。project rootで正式sensor 2件（下のStep72の節と同じコマンド）を実行する。期待する結果も同じ：required-sectionsはpass、traceabilityは前と同じ（traceability.jsonを変えていない）、checkpointでは今の正式な確認コマンド（entry-f.py・binding-e06f.json）がexit 0になる想定で、結果はcheckpointの記録が持つ。

## 履歴：Step72（作成時の見出しは「今回Step72：確かめ直しの指摘を記録で直す」）

記録だけを直すので、新しい試験はない。project rootで正式sensor 2件を実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/traceability.json
```

期待する結果：
- required-sections は pass になる。
- traceability は、前と同じ結果（traceability.json を変えていない）になる。
- checkpoint では、今の正式な確認コマンド（`verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`、人が2026-10-19に採用）を実行する。U2 の記録は `aidlc/` の中にあり、entry-f は作業コピーの bytes を `aidlc/` の外だけで比べる（`entry-f.py` の `verify_working_copy`）ため、exit 0 になる想定である。結果は checkpoint の記録が持つ。

## 履歴：Step71（作成時の見出しは「今回Step71：共有のabi.rsの再確認と正式確認のbinding更新」）

（この節の入口 `u2_candidate.py` は2026-10-17時点の正式な確認の入口。2026-10-19からは上の Step72 の節のとおり entry-f・binding-e06f。）

製品のテストは追加しない。project rootで、新しい入口と回帰、sensorを実行する（入口のファイル名は作るときに決め、README.mdに書く）。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/test_u2_candidate.py
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-summary.md
```

期待する結果：新しい入口はexit 0。回帰は、U1の29件と、このStepで足す拒否（receiptとjobの照合の各項目、「attempt 2は失敗したjobだけ」、U2の記録の許可外の変更）がすべて期待どおり。sensor 2件はpass。新しい入口は、人が採用してからcheckpointで実行する。

## 前回Step68〜70：時間項目の明示指定

新Plan Approvalと内容確認後にのみ実行する。successfulの引数time_field既定wall_secondsを保持し、U11の4環境rowsだけsecondsを明示指定する。U10とU11 nativeはwall_secondsを維持し、fallbackは禁止する。数値型/bool拒否/有限/0<=t<=30/exit0/timed_out false、歴史と現行の全検査・旧診断失敗原本を保持する。製品・他Unitは変更しない。

U2 verification/test_step68_timing.pyの8件はwall_seconds正常、明示seconds正常、欠落とfallback拒否、誤型/bool、NaN/Infinity、負値、30秒超過、exit/timed_out異常。0と30の境界は正常ケースで検査する。実体Python・版とast.parse、loader readiness22件（旧8＋trace6＋時間8）を保存した後、各suiteを外側30秒timeoutで実行し、0件/skip/timeoutを成功にしない。

```text
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step61_inventory.py -v
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step64_trace_binding.py -v
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step68_timing.py -v
```

レビュー前の全経路診断commandは以下。外側600秒、子60秒、timeout時kill/reap、全raw/exit/開始終了/checker hashを保存する。診断は正式checkpoint証明ではない。追加不一致は具体GAPを提示し、全検査省略や未承認範囲修正で通さない。

```text
<resolved-python> -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py
```

成果物整合と正式sensors後に全書込停止・独立レビュー、標準checkpointの正式検査、人のU2完了承認とU11復帰へ進む。完全Testing Contract/80%/30秒/strictを保持し、新CIや製品重試験は行わない。

## 先行Step64〜67：歴史trace原本と現行traceの分離

新Plan Approvalと内容確認後にのみ実行する。完全Testing Contractと全旧検査、既存inventory8件、製品／他Unit変更禁止を維持する。c2481414のHistorical trace/proof binding differsは実測失敗として保持する。

Step64：共通checkerの全historical original参照（両関数、current_binding、preserved/historical_hashes、trace reverse、source/CI、関連原本）を有限path／期待hash／時点の対応表へまとめる。jjのversioned evidenceから歴史U10 traceを生bytesで回収し、U2 verification/step64-historical-u10-traceability.jsonへ保存する。期待SHA2164fbd9af6bf6478c06ecf10ef3e3bc7d5dd3bb1a3be845e8855a5a13857764、source5b319a7072e698d8e7c2f94e4821bf584ec381fb、CI38010586387、歴史37を全て確認し、取得元revision/path/commandを保存する。現行原本は上書きせず、不足ならGAPで止める。

Step65：歴史論理pathと回収物理pathの対応を明示し元のhistorical_hashesを保持する。現行traceは別途sourcecb9797138313046b3cf9bbbfcab0515910b81215／CI38095031011とunit/draft/要求ID/reverse inventory/source条件を確認する。U2 verification/test_step64_trace_binding.pyの6件（歴史正常、現行正常、相互取り違え2件、歴史hash不一致、source/CI不一致）を内部test-afterで追加する。Python実体・版を保存し、ast.parse構文、loader readiness14件（旧8＋新6）を保存してから、各30秒外側timeoutで次を実行する。0件・skip・timeout・失敗は合格にしない。

```text
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step61_inventory.py -v
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step64_trace_binding.py -v
```

Step66：この計画／内容確認でレビュー前の全経路診断として以下を一度実行する。全体外側timeout600秒、子command既存60秒、timeout時kill/reapと失敗保存。新CI／重い製品試験や正式checkpoint操作は行わない。実体path・checker hash・開始終了・全raw・実exitを保存し、成功も正式完了証明と呼ばない。追加不一致は具体GAPとして提示する。

```text
<resolved-python> -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py
```

Step67：全記録を整合して正式required-sections/traceability sensorsを実行し、独立レビュー前に全書込停止する。レビュー後の正式完了検査は新commandの別人承認後のみ同checkerを実行し、診断原本と正式結果を別保存する。U2完了承認後にU11へ戻る。旧canonical・旧失敗・MMU4608／CPU/decode当時compilerの限定証拠と80%/30秒/strictを維持する。

## 先行Step61〜63：歴史37／現行42の限定修正

新Plan Approvalと内容確認後にのみ実施する。製品と他Unit成果物は変更せず、完全Testing Contract/customの内部test-after順序/strict guard/coverage80%/30秒/比較maskを維持する。前回の正式checkerのManifest inventory differsは実測失敗として保持する。

Step61：共通checkerの歴史37入力を旧canonicalの固定順序、歴史trace/proofと署名済み当時sourceへ結合する。現行42は現行manifestの先頭5件（.github/scripts/u10-current-diagnostic.py、.github/workflows/u10-current-verification.yml、crates/paludarium-host/src/native_fs.rs、tests/guests/u10/comparison_args.py、tests/guests/u10/runner-tests/test_comparison_args.py）＋旧37の順序を明示検査し、重複、欠落、余分、順序、各現在source／署名2b387／保存CI digestの不一致を拒否する。現行42から5件を除いて歴史原本へ偽装しない。歴史trace37を保持し現行42のtraceと呼ばない。EXTRA2件の検査も残し現行42中の該当pathへ対応させる。旧canonical全検査項目・既存3有限差分・共有5有限差分・MMU4608原本などを維持し、不足はGAPで止める。

Step62：U2 verification/test_step61_inventory.pyへ8件（歴史37正常、現行42正常、欠落、余分、重複、並べ替え、digest不一致、歴史／現行取り違え）の独立局所回帰を追加する。本体importでmain・外部照会・書込を行わない。Python実体をmiseインストール先globから解決し、版を保存する。両Pythonファイルをast.parseで読み取り限定構文確認した後、unittest loaderによるtest名とcountTestCases()をreadinessとして保存し、8件を確認する。30秒の外側timeoutを付けて以下を実行し、実command、全raw出力、実exit、件数、両source hashを保存する。0件、skip、timeout、失敗を合格にしない。

```text
<resolved-python> -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification -p test_step61_inventory.py -v
```

Step63：正式required-sections/traceability sensors、全成果物整合と書込停止後に独立レビューを取得する。共通checkerの正式commandは独立レビュー後の新しい人承認まで実行しない。承認対象の具体commandは以下で、実際のPython実体pathを確定して提示する。前回失敗と新結果を分離し、実exitと全出力を保存する。

```text
<resolved-python> -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py
```

この計画では新CIや重い製品試験を追加しない。保存MMU4608とCPU/decodeの当時compiler条件を保持し、新実行と呼ばない。人のU2完了承認後にU11へ戻り、承認済み同時dispose修正を継続する。正式質問ファイルと承認記録は標準手順が生成し、手作りしない。

## 先行Step58〜60：MMU条件不一致の限定追加

mmu-verification-change-questions.mdのAnswerは追加範囲の承認。この更新計画の新Plan Approvalと内容確認後にのみ次を実施する。製品source・他Unit成果物は変更せず、Testing Contract/custom順序/strict guard/coverage80%/30秒と比較maskを維持する。

Step58：署名済みCIの同一snapshotでmmu_u2一対象を実行する。runner/toolの実体・実使用compiler full version/commit、toolchain/target/flags、全入力source before/afterと両Cargo.lock、既存suppression bytes/hashを固定し、同期・並行compile/trace/fuzzを重ねない。Linux snapshot内の具体target commandは以下。ASanを無効化せず、既存LSan suppressionを増やさない。

```bash
LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run --fuzz-dir fuzz mmu_u2 -- -max_len=4608 -max_total_time=600 -timeout=30 -rss_limit_mb=2048 -seed=1
```

raw stdout/stderr、実exit/runs/開始終了時刻、binary SHA256、全入力before/after、両lock、compiler/flags/settings、seed/corpus/crash、署名VerifiedとCI head SHA/run/job/artifactを成功失敗とも保存する。600秒予算の終了観測（保存例601秒）を確認し、短縮・panic・timeout・ASan/LSan異常をPASSにしない。旧mmu_u2の4096 bytes・601秒exit0は履歴として保持し、今回4608条件の成功と扱わない。CPU/decodeは一致するsource/compiler/flags/locks等の保存証拠のみ限定再利用し、現在再buildbinary同一は原本不足なら未検証を保持する。

Step59：`aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py`を実装する。旧canonicalは変更せず、39入力の3不一致/U11有限差分の明示supersession、履歴proof/trace、署名/祖先、artifact最新選択/成功job時刻、native14/emulator16/original argv、guest/compiler/locks/binary/receipt、license/deny/metadata、Rust80%/u3/u9 LCOV/runner44/timings、30秒/比較maskの全検査を保持する。U2担当124/trace92/正式sensors、7品質ASan原本・4環境14cases・JS420/449の母数449、今回MMU4608原本を現在sourceの有限bindingに追加する。旧成功やJS値で別の検査を代用しない。不足bindingはGAPとして停止する。構文確認は実使用Python実体で`ast.parse`による読取だけを行い、import/実行/pycache生成をしない。候補の正式実行コマンドは以下で、独立レビューと別command承認まで実行禁止。

```bash
python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py
```

Step60：実結果と適用範囲を成果物へ整合し、下記の既存正式U2 sensorsを実行して原本を保存する。全書込停止後に再レビュー、具体commandの正式checkpoint承認・実行、人のU2完了承認、engineのU11復帰を順に確認する。U11の承認済み同時dispose修正は復帰後の担当作業であり、今回U2の成功だけで完了としない。

```bash
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-summary.md
```

## 先行Step55〜57：承認不整合修復後の限定再確認

新しい計画承認と内容確認後にのみ実施する。U2 manifestの担当ソースと今回のU11共有変更を保存済みCI・fuzz・production wasm Node/実Safariの証拠へ照合し、bytes一致と適用範囲を確認する。既存U2実装・成果物・旧証拠を保持し、保存済み成功を今回の新試験と数えない。不一致や不足は具体的に提示し、製品修正・新しい重い検証へ自動拡張しない。

正式検査は以下の既存U2限定コマンドを使い、今回の実結果を保存する。

```bash
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-summary.md
```

記録を確定し書き込みを止めて独立レビューへ渡す。現行verification commandの今回ソースへの適用性を確認し、旧commandの不一致・失敗は履歴として保持する。新commandが必要なら具体的なコマンドと有限の確認範囲を提示し、人の新承認を正式checkpointで取得してから実行する。承認済み確認の結果を標準checkpointで扱い、人のU2完了承認後にengineがU11へ進めることを確認する。80%coverage・30秒watchdog・strict guard・各600秒fuzz設定・custom順序と比較maskを維持する。

## 履歴Step52〜54：現行ソースと承認経路の再確認

全Unitやり直し後の実行対象は計画Step52〜54。新しい計画承認と内容確認を取得し、U2 manifestの担当ファイルと署名済み7eb1819f52acede33e83775374dd4ee93edf643bのbytesを照合する。既存の整数命令・wasm実装と過去の検査手順は保持し、旧CI・fuzz・Safariの成功を今回の新実行へ読み替えない。

正式検査は既存のsensor-traceability/sensor-required-sectionsコマンドをU2成果物へ実行する。独立レビュー後の最終確認は、既に承認された `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py` を標準checkpointで実行する。検査の有限範囲を明記し、U2の全入力・全環境を保証したとは扱わない。

不一致がある場合だけ具体的不足と必要な限定検査・修正案を提示する。新しい検査コマンドが必要なら人の選択を取得する。strict guard、80%coverage下限、30秒watchdog、各600秒fuzz設定、Testing Contractのcustom順序と比較maskを維持する。レビュー開始後は成果物・manifest・担当ソースの書き込みを停止する。次Unitへの遷移を確認しても並行セッションのID競合の完全解消は未検証として区別する。

## 履歴Step49〜51：保存証拠と対応表の限定確認

今回の製品sourceは変更しない。先行Step42〜48の手順は実装・検証当時の履歴であり、存在しなかった製品crate/launcherの説明を現在の不足とは読まない。manifest claimsと178da99e署名済みCI、production wasm Node/実Safari14case、4targets各601秒ASan/LSanの保存証拠を照合する。新しいテスト実行とは数えない。

```bash
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-summary.md
```

canonical完了検査は人が承認した既存コマンドをUnit checkpointで実行する。coverage80%、30秒、固定nightly、各600秒、既存test configurationと未検証の適用限界を保持する。不足が判明した場合だけ具体的限定検査を提示し、旧sourceの成功を現在へ転用しない。

## 今回Step42〜48の検査契約（新承認後のみ）

承認後まずStep42の設計/API読取を行い、製品wasm crate名、target gated Host能力、launcher ABI、shared Rust heap初期化/allocator/stack/TLS/Worker契約を根拠付きで確定する。現時点で製品crate/launcherが存在しないため存在しないcommandを実行済み/readiness成功と表現しない。実装後コマンドのpackage/pathは確定設計とmanifestに合わせて記録する。固定nightly2026-10-01、custom native-first/internal-test-after、80%/30秒を維持。

R03：safari-checkのstatus/session/navigation/execute/deleteを含む全fetchに同一30秒絶対deadlineのAbortSignalを渡す。cleanup自身も無限待機禁止、driver.kill/server.close/Worker terminateをfinallyで回収。応答しないHTTP fixtureでprocess timeout・非ゼロexit・残留processなしを検査。正常な実Safari caseは別回帰。最外process watchdogも30秒でkill/reapし、内部タイマーだけを外側の保証と呼ばない。

Native runner：現行guest ELF bytes/hashをCIのx86-64 Linuxで各30秒以内に実行しhello stdout/stderr/exit、integer exit、atomic exit、divide fault signalを取得。production Session wasmの出力/exit/faultと比較し、CPU診断encoding136だけをKernel SIGFPE成功としない。期待結果はCIごとにnative取得する。

製品wasm：固定nightlyでfull workspace対象と新production wasm crateをlocked release build。Node Worker/実SafariのCOOP/COEPページから本番launcherを呼び、同じConfig/guestと同じmoduleで非ゼロケースを実行。hello実出力、正常/エラーexit、kill/cancel、未対応capability errno、実Kernel fault配送を観測。内部Host/ABI/loader/runtimeテストは実装後、命令変更はnative期待を先行させる。

共有heap/nested：imported shared memoryとbuild-std/atomicsの製品moduleをroot/nested Workerへ渡し、stack/TLS個別化、初期化一度、共有Rust allocatorの同時alloc/free、共有同期型/guest MMU atomic、wait/notify、終了/kill/timeoutを検査。単純なSharedArrayBufferや別instanceの同一memory読書きだけでstd heap/thread成功を主張しない。実現不能/API設計変更/unsafe追加なら具体GAPと根拠をrootへ返す。U11起動/Host、必要なthread/futex統合はU5、全後続Unit実装へは広げない。

Native品質回帰：Linux/macOS/Windows既存suite、fmt/clippy警告0、cargo-deny、実機Linux全workspace llvm-cov --fail-under-lines 80。新sourceのCPU/MMU/decode/load_elf各600秒ASan/LSan、seed1、timeout30、rss2048、CPUmax_len4096/MMU4608。suppression/時間を弱めず、always artifactsにraw logs/source before-after/binaryhash/seed/corpus/crash/exit/時刻を保存。旧source成功は新製品証拠に転用しない。Actions SHA固定、署名付きjj push/connector Verified確認。実装後source-manifest/traceabilityと具体commandsを整合し、全書込確定後に独立review。

## 今回Step39〜41：追加検証手順

承認後にclone-flags診断Cをisolated workspaceへ作り、固定したsource hashの同じprobeをlocal image6666753bとfork native Linuxで実行する。glibc clone callback、別stack、wait/reapを使用し、VM/FS/FILES/UNTRACEDの16組合せを独立child/外側30秒watchdogで検査する。CLONE_VMなしでもchild回収可能なsignal設定を固定してflags以外の差を記録する。LSanの実syscall flagsと同じsignal0の組合せも別に確認し、通常SIGCHLD結果と混同しない。ptrace readinessは別processで確認。全errno・timeout・exitを保存し、失敗を成功に読み替えない。

製品wasmのreadiness commandは `cargo +nightly-2026-10-01 check --locked -p paludarium-runtime --target wasm32-unknown-unknown`。承認後にexport/launcherと依存を読取り、必要componentを固定toolchainへ追加する。実行wrapperはisolated workspaceの診断専用packageで、製品cratesをpath依存として実際にリンクする。wrapperの具体build/Node/Safari実行commandは実API確認後に記録する。未知のproduction exportを創作せず、0cases/build-only/spike-onlyをproduction実行PASSにしない。guest期待値はnative runnerで先に確認し、実装変更を行う場合のcustom順序を守る。製品launcher未実装なら新規本番実装に広げず具体不足を報告する。

本物Safariは既存有効化を利用し、COOP/COEP下の実wasm moduleで出力/exit・整数/fault/atomicを確認。共有heap/入れ子Workerは製品moduleで実行できなければ未検証のまま残す。既存U1 spikeをproduction wasmの代替証拠にしない。既存品質下限とASan成功証拠を維持する。

## 今回Step36〜38：fork実機Linux診断（新承認後のみ）

基準はaf9b739d742a9552f44fc1515646c862b19e5de2。isolated jj workspaceをこのrevisionから作り、診断専用bookmark codex/u2-asan-diagnosticに必要最小workflowだけ追加する。現checkoutへのworkflow追加、製品変更、PR/mergeは禁止。jj pushはSSH署名維持・host権限で実行し、push後connector commit metadataのVerifiedとhead SHAを確認する。CI操作はconnector優先。dispatch機能がないためpushで起動し、ghは不足するActions読取/log取得だけに使う。

実機ubuntu x86-64 runnerのuname/lscpu、container image ID、rustc/cargo/cargo-fuzz version、ASan symbols、ASAN_OPTIONS/LSAN_OPTIONS、最小C ASan main{return0;}のstdout/stderr/exitを保存。固定nightly-2026-10-01/既存suppressionを使用する。baseline/host/container/CI headの製品paths全bytehash一致を証明し、診断workflow差のみ許容する。mainCI checkerのaf9b CI/native証拠へ診断SHAを混在させない。

承認後workflow内で同snapshotを固定し、次のfuzz設定を同runner順次または同SHA job matrixで実行する。両U2target間のsyncは禁止。decoder/load_elf既存max_len等は既存nightly設定を承認後に読み取り維持し、未検証の値を創作しない。

```bash
export LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address cpu_u2 -- -seed=1 -max_total_time=600 -max_len=4096 -timeout=30 -rss_limit_mb=2048
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address mmu_u2 -- -seed=1 -max_total_time=600 -max_len=4608 -timeout=30 -rss_limit_mb=2048
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address decode -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address load_elf -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
```

各targetをexit捕捉して失敗後も残る対象を実行し、rawlog/start/end/runs/exit、source before/after、seed/corpus/crash、sanitizer/toolchain/環境を常時uploadする（ActionsはSHA固定、if: always()）。コンパイル時間とfuzz本体600秒を分け、0件/短縮/timeout/LSan異常を成功にしない。診断workflowだけの修正と再実行は可能だがLSan無効化・suppression追加・時間短縮は禁止。製品不具合はrootへ報告する。80%gate/custom順序/30秒watchdogは維持する。

Step38で旧未実行表記をCPU636751/MMU910789各601秒LSan終了失敗という実結果/履歴へ訂正し、実機CIの実測範囲だけNFR2/2.2/3/3.4 GAPを更新する。他fuzz/wasm/任意入力を推定しない。sensors/全記録/出力専用diaryを確定して独立reviewへ渡す。現在21runsのCI/native成功は夜間fuzz実行の証拠ではない。

## 今回Step33〜35：現在source CPU/MMU各600秒ASan

新Plan Approvalと別のLooks correctが成功するまで下記は実行しない。Docker availabilityは未検証。既存Docker VMMを保持。runner不可なら原因と未検証を残し、Docker Desktopを利用可能にして同じ手順を再開する。fixed nightly/ASanが使えない場合は指定componentを準備し、pin・600秒・sanitizerを変更しない。

準備確認のexact commands（承認後のみ）：

```sh
docker info
docker image inspect paludarium-dev
```

image不在時は既存linux-dev.shのci/linux-dev/Dockerfileによる構築を使う。host version/image IDとsource SHA256を保存する。一度だけ同期する下記呼出しを使い、2target終了と回収まで再sync・別compile/trace/fuzzを重ねない。

```sh
bash scripts/linux-dev.sh bash -c '
set -euo pipefail
evidence=target/u2-evidence/current-asan
mkdir -p "$evidence" fuzz/corpus/cpu_u2 fuzz/corpus/mmu_u2 fuzz/artifacts/cpu_u2 fuzz/artifacts/mmu_u2
uname -a > "$evidence/environment.txt"
rustc +nightly-2026-10-01 -Vv >> "$evidence/environment.txt"
cargo +nightly-2026-10-01 -V >> "$evidence/environment.txt"
cargo +nightly-2026-10-01 fuzz --version >> "$evidence/environment.txt"
find crates tests fuzz/fuzz_targets -type f -print0 | sort -z | xargs -0 sha256sum > "$evidence/source-before.sha256"
sha256sum Cargo.toml Cargo.lock rust-toolchain.toml fuzz/Cargo.toml fuzz/lsan.supp >> "$evidence/source-before.sha256"
tar -cf "$evidence/corpus-before.tar" fuzz/corpus/cpu_u2 fuzz/corpus/mmu_u2 fuzz/artifacts/cpu_u2 fuzz/artifacts/mmu_u2
printf "seed=1\nsanitizer=address\nnightly=2026-10-01\n" > "$evidence/run-settings.txt"
export LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp
for target in cpu_u2 mmu_u2; do
  max_len=4096
  if [ "$target" = mmu_u2 ]; then max_len=4608; fi
  date -u +%Y-%m-%dT%H:%M:%SZ > "$evidence/$target-start.txt"
  set +e
  cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address "$target" -- -seed=1 -max_total_time=600 -max_len="$max_len" -timeout=30 -rss_limit_mb=2048 > "$evidence/$target.log" 2>&1
  status=$?
  set -e
  printf "%s\n" "$status" > "$evidence/$target-exit.txt"
  date -u +%Y-%m-%dT%H:%M:%SZ > "$evidence/$target-end.txt"
done
find crates tests fuzz/fuzz_targets -type f -print0 | sort -z | xargs -0 sha256sum > "$evidence/source-after.sha256"
sha256sum Cargo.toml Cargo.lock rust-toolchain.toml fuzz/Cargo.toml fuzz/lsan.supp >> "$evidence/source-after.sha256"
set +e
cmp "$evidence/source-before.sha256" "$evidence/source-after.sha256" > "$evidence/source-compare.log" 2>&1
status=$?
set -e
printf "%s\n" "$status" > "$evidence/source-compare-exit.txt"
tar -cf "$evidence/corpus-after.tar" fuzz/corpus/cpu_u2 fuzz/corpus/mmu_u2 fuzz/artifacts/cpu_u2 fuzz/artifacts/mmu_u2
[ "$(cat "$evidence/cpu_u2-exit.txt")" = 0 ] && [ "$(cat "$evidence/mmu_u2-exit.txt")" = 0 ] && [ "$(cat "$evidence/source-compare-exit.txt")" = 0 ]
'
```

各target rawログでASan instrumentation、seed1、runsとlibFuzzer終了行の600秒実行を確認する。cargo-fuzzコンパイル時間をfuzz時間へ足さず、開始終了だけから成功を推定しない。exit非0・panic・timeout・sanitizer異常は失敗で、CPU失敗を隠さず同じsnapshotでMMUも確認する。既存iced-x86 LSan table suppressionを追加・拡大しない。準備不足はset -eでfuzz開始前に停止する。

両target終了後、再syncを起こさないread-only container/volume操作で証拠を回収する。source-before/after hashをhost sourceとも照合し、raw logs・exit・start/end・run-settings・Docker image ID/host version・corpus-before/after archiveとhashをU2 verificationへ保存する。seed/corpus入力を保持しtarget/cacheをsource-manifestへ足さない。

成功でも有界CPU/MMU試行だけの証拠。他fuzz target・全入力安全性・production wasm・shared std heap・nested Workerへ一般化しない。NFR2/NFR3/NFR2.2/NFR3.4を実測適用範囲で更新し、未実行部分はGAPを維持する。80%workspace gate・30秒watchdog・固定nightly・各600秒・比較mask・custom順序を保持する。以下Step1〜32の説明は履歴。

## 履歴：Step30〜32の実施結果

Summary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後、95claimsをaf9bと独立照合し全一致、保存CI37713953347/native37713953340のdiff38/parallel10と内部CPU14/decoder9/MMU9/types1/kernel1を実名で照合した。今回のsource/log対応はverification/step30-test-correspondence.json。新実行はなく、以下exact commandsは不足回収用。旧4d52snapshot2/9差異を保持し、旧coverage/fuzzを現在合格へ流用しない。現行全体92.68%/U1対象83.04%、両80%gate維持。4ASan GAPとproduction wasm未検証を保つ。以下Step1〜29は履歴。

## 履歴：Step27〜29（4d52時点）

新Summary Confirmation後に本書を保存して既存exact commandsと品質下限を確定した。製品bytes不変のため新testsなし、旧600秒ASanを現在成功へ転用しない。plan/本書/summary/traceabilityとmanifestの全保存後、レビュー中freezeへ渡す。

対象は3手順。新承認と別の内容確認後に現在95claimsとCI証拠を再照合し、実4produces plan/instructions/summary/traceabilityとmanifestを全保存する。同一製品へ重い再試験を追加せず、以下commandsは不足回収用として保持。既存4ASan GAPとwasm未検証、全品質下限を維持する。親diaryをレビュー前に確定し、依頼からterminalまで書込とjj snapshotを停止する。以下Step24〜26は先行attemptの手順として保持する。

## 履歴：Step24〜26（4d52時点）の手順（macOSからの記録再確認）

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

## 今回のStep30〜32の確認手順

固定Testing Contract、80%・30秒watchdog・nightly pin・各600秒ASanを維持する。保存済みaf9b CIと現在sourceの一致を確認した範囲で既存テスト結果を利用し、新実行と区別する。4d52やそれ以前の結果は履歴として保持する。不足がある場合だけ以下のU2限定コマンドを実行する。native期待値はLinux x86-64で毎回生成し、macOSのnative非実行や0件filterを合格に数えない。

```sh
cargo test --locked -p paludarium-harness --test diff_u2
cargo test --locked -p paludarium-harness --test parallel_u2
cargo test --locked -p paludarium-cpu --lib u2_segment_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u2 u2_segment_atomic_forms -- --exact --nocapture
cargo test --locked -p paludarium-harness --test diff_u2 u2_atomic_gs_ -- --nocapture
```

期待件数38/10/5/1/2を実際の現在テストと保存ログに照合する。新製品修正を要する場合は命令native期待結果を先行して回収し、内部層は実装後にテストするcustom順序を守る。旧fuzzを現在sourceの各600秒ASanの合格へ転用せず、不足するNFRはGAPとしてBuild and Testへ渡す。単独Safari spikeの合格からU2の本番wasm・共有std heap・入れ子Workerの合格を推定しない。品質・coverageの全体ゲートは保存CIを根拠に別途確認し、U2限定テストで置き換えない。

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
