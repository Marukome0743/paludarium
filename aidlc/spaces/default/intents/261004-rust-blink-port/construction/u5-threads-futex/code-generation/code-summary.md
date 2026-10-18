# U5 コード生成概要

## 現在の状態（2026-10-19 JST、Step34）

本節はStep34の記録である。U15のStep22〜28で製品のファイルが変わってfork `codex/build-and-test` へ送られた（head 27d05de1、e3c29d1d→8b415a7c→8360be2e→27d05de1、4つともVerified）ので、U5を確かめ直した（`reviews/review-12.md`、READY、Major 2・Minor 3）。checkpointで人がRequest Changesを選んだので、U5の記録で直せるR-08〜R-12を直した。U5の製品のコード・CI・workflow・ほかのUnitの記録は変えていない。traceability.jsonは、Step34bでNFR2・NFR8のtargetとnotesだけを変え、Step35で各行のnotesの先頭に時点の注記を足した（statusとidは変えていない）。

- **今の正式な確認コマンド（R-09・R-10）**：`aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の U15 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用、command SHA-256 `00f5c8832e04f7d27b30c6b445fdc30e0e5d233dfa5452e02c2c99368a08a159`）。下の節に出てくる候補（`verification/verify-current-u5-preview-bound.py`・`verify-current-u1-u7-u9-u3-u5.py`）、U2の `u2_candidate.py`、「人の新コマンド承認前に実行していません」「新コマンド承認…は未完了」は、それぞれの時点の記述である。U5のcheckpointはentry-fで確かめる。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べるので、U5の記録の変更はその結果に影響しない想定である（結果はcheckpointの記録が持つ）。
- **U5に関わる製品の変更**：U5の製品のファイル（`crates/`・`tests/guests/u5`・`scripts/u5-*`・fuzzの対象）は変わっていない。U5のsource-manifestにあった `u5-current-verification.yml`・`u5-native-diagnostic.yml`・`u5-quality.yml` は消えた（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）。
- **消えたworkflowのjobの今の場所**（review-12の確かめた点）：600秒のASan/LSanのfuzz `kernel_threads_u5`・`kernel_futex_u5` は `u14-fuzz.yml` の13対象にある。3OSのテストとfmt・clippy・依存の検査は `u14-quality.yml` と `ci.yml`。native 43件の差分 `diff_u5` は、差分テストのjobの `--test` 一覧にはなく、`ci.yml` のcoverageのjobの `--workspace` 実行の中だけで動く（`PALUDARIUM_U5_EMULATOR` は設定されている）。27d05de1のCI 8 runはすべて成功した（U12は人が認めた1 jobの再実行。記録はU15の `verification/ci-27d05de1/`）。
- **U5だけのcoverageは今は測られていない**：消えた `u5-quality.yml` が測っていたU5の固定13ファイルのcoverage（前回86.23%）は、今どのworkflowでも測られていない（R-14）。U5の製品のファイルを含むクレートを測るU9・U11のクレート単位の80%の下限（`ci.yml`・`u14-quality.yml`）と、workspace全体の80%の下限は残る。U5だけのcoverageを測る `scripts/u5-coverage.py`・`scripts/u5-coverage-native.py` は、`.github/workflows/`・`scripts/`・`tests/` のどこからも呼ばれていない（計画のときにgrepで確かめた）。これをCIに戻すかは、製品の変更なので次の製品の変更のpushで決める（人の判断、2026-10-19）。
- **source-manifest.json（R-08）**：writesから、消えた3本（`.github/workflows/u5-current-verification.yml`・`u5-native-diagnostic.yml`・`u5-quality.yml`）を外した。ほかのpathは変えていない。呼び元が消えた `.github/scripts/u5-current-diagnostic.py` と、呼び元の無い `scripts/u5-coverage.py`・`scripts/u5-coverage-native.py` は製品のファイルとして残っていて、消すと正式な確認コマンドがhead 27d05de1との違いで拒否するので、次のpushで扱う。
- **時点の注記（R-11・R-12）**：traceability.mdの表と「検証済み：source9aa14978」、NFR9の `nightly-2026-10-01`、下の節のcompiler・Nodeの値は、それぞれの時点の観測である。今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`。traceability.mdの見出しの直後にも同じ注記を足した（表は変えていない）。
- 「今回」「現行」で始まっていた見出しは「履歴：…（作成時の見出しは「…」）」にした（手順書の「今回の記録更新（Steps26〜28）」「今回の現行ソース再確認（Steps20〜22）」もStep34bで履歴にした）。本文は変えていない。
- **traceability.json（Step34b、人の判断）**：正式sensorのtraceabilityが、NFR2とNFR8のtargetの `.github/workflows/u5-quality.yml` が無いことで通らなかったので、人の判断（「案 A で進めてください。U5 の traceability.json の NFR2 を u14-fuzz.yml、NFR8 を ci.yml に替え、手順書に残った「今回」の見出し 2 つも履歴にしてください。」）に従い、NFR2のtargetを `.github/workflows/u14-fuzz.yml`、NFR8のtargetを `.github/workflows/ci.yml` に替え、notesの先頭に理由を書いた。status・id・ほかの行は変えていない。
- 未検証：この作業ではentry-fを実行していない（checkpointで実行する）。独立再レビューはこの記録の後に行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：確認候補修正（Steps29〜32）（作成時の見出しは「今回の確認候補修正（Steps29〜32）」）

検証済み（全診断、正式確認ではない）：最終helper SHA ddab606d63467412c47b0ac2fbeb71c61e7d9801ad548edc9aa5f0e0a7749ea5で新候補を実行し、exit0でした。旧全checkerの全34必須品質jobと全履歴predicateを保持して成功し、現行367入力中366完全一致・mise.tomlのexact preview版差分だけを確認しました。実行コマンドとterminal原出力はverification/step31-diagnostic-attempts.jsonに保存済みです。5 legacy moduleの直接・入れ子jj読取を監査し、限定proxyの成功時・例外時の参照復元を検査しました。独立レビュー、新コマンド承認、正式確認、U5完了承認は未完了です。

検証済み（局所回帰）：新しいpreview_source_binding.pyの22境界、既存quality_source_bindingの5件、source_bound_validationの33件、計60件がexit0でした。署名head62611f2556c4caf1470a7eb4471269d92611db6eの367入力を元のdigestへ照合し、現行入力との相違をmise.tomlのAI-DLC version値2.11.0→2.11.1-preview.20261012.1のexact bytesだけに限定します。他tool・取得元・asset・製品・両lock・compilerの変更、欠落、追加、symlink、旧現行混同は拒否します。

ドキュメント根拠：新候補verification/verify-current-u5-preview-bound.pyは旧verify-current-u1-quality-fixed.py・旧helper・bindingのhashを固定し、旧checker全体をプロジェクト内の新しい署名ソースviewで実行します。旧predicateを省略せず、jjの厳密な読み取りコマンドだけ実repositoryへ向け、その他の処理はviewを参照します。実workspaceの設定は変更しません。旧署名ソースの成功を現行の新規試験実行とは主張しません。

全診断の初回失敗と再開始はverification/step31-diagnostic-attempts.jsonに保存します。初回はjjの相対パス解決でexit1、次は最終helper版を実行し直すためSIGINTでexit130（superseded、合格ではない）でした。最終版の診断結果、正式sensor、独立レビュー、新コマンド承認後の正式検証はそれぞれ区別して記録します。製品・旧checker・原本・AI-DLC本体・guardは変更していません。

## 履歴：記録更新（Steps26〜28）（作成時の見出しは「今回の記録更新（Steps26〜28）」）

検証済み（今回の読み取り専用照合）：旧U5の320入力は285一致・35変更・欠落0、source-manifestの38担当パスは31一致・7変更でした。現行署名head62611f2556c4caf1470a7eb4471269d92611db6eに結合した保存済み品質CI38392057138の367入力は366一致、mise.tomlだけ公式AI-DLC preview更新により相違しています。製品・fixture・既存試験・AI-DLC本体・guardは今回変更していません。監査の範囲と相違はverification/step28-source-applicability.mdに記載しました。

ドキュメント根拠：保存済みstep66-quality-binding.jsonは全34必須品質ジョブ成功、同headのU1 CI38392056273とsanitizer CI38392056163の原本へ結合されています。後者のthreads/futexは各601秒、実compiler6f5da406bを記録しています。今回の作業では重い試験を再実行せず、この保存証拠の適用範囲を照合します。正式な全検査・独立レビュー・最終確認はこの記録更新後に行います。旧U5専用13ファイルcoverage86.23%を現行の新しいU5専用計測へ流用しません。

ドキュメント根拠：セッションIDの修正を含む公式previewを導入済みで、今回の計画承認・内容確認の記録経路は成功しています。全並行セッションの競合が完全解消したとの保証は未検証です。wasm共有機能・U11実guest証拠とU5単独clone/futex全入力保証は区別します。

## 過去Steps23〜25の限定確認と担当範囲


検証済み（過去Steps23〜25）：製品・fixture・比較規則を変更せず、専用診断の署名Verified head c8e119938eef951a07ab7080f3d6f0967db7358f／run38070022172の6jobが成功しました。全320入力（既存318＋専用診断2）、両lock、実compiler32dba69d69c5b10ea89a4042de8d0619f7756203／LLVM23.1.3を全jobのbefore/after/currentへ結合しています。原本426ファイルのhash、各実exit、署名・job metadataはverification/step25-current-proof.jsonとstep24-final-raw/に保存しました。

検証済み：毎回生成するx86-64 Linux native全43差分、ignored0、実exit0。Linux/macOS/Windows各Host7・Kernel27・MMU6・Runtime6の46件、ignored0、fmt・Clippy警告error・依存4検査の各実exit0。別empty profilesの既存13製品ファイルcoverage3869/4487=86.2269%、80%下限と同じファイル分母規則を維持しました。旧U5の3825行という数値を固定したのではなく、変更後の同13ファイルを4487行として測っています。30秒watchdog・kill/reap・mask・TID/時刻正規化は不変です。

検証済み：kernel_threads_u5 10,037,269 runs／601秒、kernel_futex_u5 9,033,344 runs／601秒、各実exit0、ASan/LSan symbolsあり。detect_leaks=1・既存最小iced-x86 suppression・seed1・timeout30・rss2048・既存default max_len4096、実compiler／binary hash／保守的依存union／flags／実runtime出力を保存しました。旧nightly10-01の成功は流用していません。

限定再利用：U9の現行316入力・実compiler・設定が一致するNode26.11.1／本物Safari26.6.2の20件からatomic、kill、simultaneous sessions、nested Worker、shared allocator/AddressSpace wait-notify等の実施済み共有機能だけを使います。同module4482b1574987ff62cc8f9f872e42e5dbe6f4fc91273103da6abc0dd8ffd18fe3とraw report、28/30秒制限、isolation/cleanupのbindingはverification/step25-browser-reuse.json。guest clone/futex43件やnative実Host割当、U11完了の代替ではなく、新しくbrowserを実行したとの主張もしません。

履歴の区別：旧7eb担当36は33一致・3変更（native_fs.rs、files.rs、u5-quality.yml）、旧9aa417は375一致・42変更・欠落0。確認原本はstep20-current-audit.json。最初のrun38069718184はWindows compilerパスとcontainerのpython不足、run38069878789はcontainerのpython不足で失敗しました。新専用workflow内だけを修正し、失敗原本とstep24-failed-attempts.jsonを保持しました。成功した最終runと混同しません。

最終確認候補verify-current-u1-u7-u9-u3-u5.pyは既存U1/U7/U9/U3確認へ新U5証拠を追加し、AST構文確認だけ成功しました。人の新コマンド承認前に実行していません。独立レビュー・最終確認・人の完了承認は親が担当します。並行セッションID競合の完全解消は未検証です。

承認済み独立上流割当による現在のU5必須集合はFR2.3、FR5.4、FR9.1、NFR1/2/3/5/7/8/9の10件です。以前の担当9件には共通のNFR5が抜けていました。NFR5は初期に資源上限を設けない方針で、U5thread実装のclone/registerとworker spawn/handlesにconfigured同時thread上限を追加していない根拠へ対応させています。TID表現可能範囲やHost spawn errorは保持し、無限資源を保証しません。共有requirements、Unit定義、C2/C4/C5/C8/C10に基づき、clone/futexとnative Host workerの範囲を確認します。wasm guest WorkerはU11、別プロセスfork/execはU8です。

## 歴史的な完成時snapshot

FR2.3/FR5.4のnative cloneスレッド実行とfutex WAIT/WAKE/bitsetを実装した。以下の全43差分・3OS品質・先行Unit差分・module Node/実Safari・固定13file coverage85.12%・両601秒sanitizerは、過去snapshot 9aa149786015ad9f789e8527cc30d7f30f2f9482（親がGitHub Verified確認）の観測です。final-proofはその原本へ結合し、当時の43ケース候補checkerはexit0。以前のe8e23fbd成功証拠はverification/intermediate-e8e23fbd-proof.jsonに保持した。これらを7eb1819全sourceの新しい品質実測とは主張しません。

## 実装の責務と境界

ThreadはCPU、signal mask、altstack、signal frames、pending signal、clear_child_tid、終了状態を所有する。Process identityとThreadGroupの共有registry・signal disposition・process pending/timer・futex queuesを分離する。cloneはregister/stack/TLSとparent/child TID、clear_child_tid zero+wakeを扱う。VM/SIGHAND/THREAD依存とflagsを検査する。別プロセスcloneはU8境界としてENOSYS。Files/fd table/cwdとMMUはclone flagsに応じて共有またはsnapshotを作る。futexはqueue lock下で比較と登録を行い、wake/timeout/interruptの勝者を一度だけ決める。

timer更新通知のowner receiptはtimer metadata・signal・外部中断を区別する。sleep入口前にgenerationが既に進んでいてもmetadata receiptで元の期限を再計算する。別workerのprocess drainはowner通知種別を消さない。実signal/group終了/外部中断は優先し、metadataだけではsleep/futex/flockをEINTRにしない。timeoutなしWAIT/WAIT_BITSETはSA_RESTART frame作成前にRIP/RAXを再開値へ戻し、handler復帰後に値を再比較する。native実測に従いtimeout付き待機はSA_RESTARTでもEINTRを返す。

RuntimeはHostの実workerを使い、個別Kernel/Thread/DecodeCacheと共有AddressSpace/ThreadGroupを実行する。個別exit後も子終了を待ち、exit_group/fatal signal/killはgroupを停止する。spawn失敗/panic/Host errorはguest errno/signalと別の製品エラーとして扱い、handleを回収する。signal transportはSI_TKILLとprocess/thread宛先を保持する。

## 過去snapshotの検証原本

検証済み（9aa完成時の履歴）：製品変更前に全43native観測を取得し、追加38〜41は(0,0,1)、42は(-110,0,1)。旧製品で38/39/40が失敗する反証可能な再現を確認した。原本はverification/preentry-native-first-verified.md、preentry-native-first.log、preentry-before-differential.log、preentry-native-artifact/。元0〜37を保持し、比較はraw stdout/stderr/exit/timeoutと正規化した関係・経過区間boolを使う。

検証済み：局所Kernel100/Host39/Runtime39 libテスト、Kernel all-targets clippy -Dwarnings、fmt、現行CLI build。Kernel U5は新2テストを含む27件。join/channelで入口前通知、別worker process drain、ack後再送、masked/ignored signal、実中断とgroup終了の順序を確定する。既存Host entry後のset/shorten/disarm、futex/flock metadata regressionも成功。現行CLIの38/39/40はnative期待(0,0,1)と一致した。工具・コマンド・出力はverification/preentry-product-local.md。

検証済み：確定sourceの全43fresh差分、先行Unit差分、3OS品質と現module Node/実Safari21件。原本はverification/preentry-final-*。module SHAは18c7edb072830bd6148e408175b8d318516adef39018d9d190c8328e8a4d10ea、実Safari27.0.1はisolation/sharedMemory/cleanup true、4656ms。417sourceの同head差分は空。

検証済み：固定13製品file coverage3256/3825=85.12%、floor80。threads18531279runs/futex9935154runs、各601秒ASan/LSan、exit0、lock不変。quality37951856624はattempt2 completed success、native37951856306はsuccess。初回coverageはU3 unknown Intel profile signature000606a6で計測前失敗し、同source・変更なしの再実行で成功した。失敗原本も保持しU3 allowlist/閾値/sourceは変更していない。417source leaf・先行証拠73件を照合。候補checkerは43へ同期し承認済みcommand stringでexit0。過去成功を今回の完成へ流用していない。

## 過去の文書sensorと境界

検証済み：Step18時点の公式sensorは全体60 IDsとU5対応9 IDsの差51をmissingと報告しました（verification/step18-document-checks.jsonに履歴保存）。Step19の承認済み上流割当60行を配置し、独立Unit-aware候補は追加NFR5の欠落を検出しました。根拠あるNFR5対応後の候補はpass true/findings0、回帰27件は成功しています。

検証済み：今回CLI2.11.0の正式traceability検査は、担当10行だけの初回表に対してexit0/pass:false/findings50でした。要件原本と独立割当の全60 IDsを確認し、U5必須10行のOKを保持したまま他担当40行をDeferred・集約見出し10行をN/Aとして担当と根拠を明記しました。同じ正式コマンドの再実行はexit0/pass:true/findings0、required-sectionsもexit0/pass:true/findings0です。初回FAILと修正後原本はverification/step25-formal-sensors.jsonへ保存しました。framework・上流割当・製品は変更していません。旧Step18/19の経緯はverification/sensor-repair/assignment-finalization.mdとassignment-finalization.jsonへ保持します。

wasm guest Worker接続はU11、fork/execはU8。有限guest結果を後続命令/ライブラリ依存を含むprobe全量達成とは区別し、全入力保証は主張しない。U3未知CPU profile拒否の過去原本は保持し、oracle/allowlistは変更しない。

source-manifest.jsonはstage/unit/version/writesとrepo/pathのみ。初期fixtureと先行Unit依存の来歴はverification/source-provenance.jsonに保持する。独立レビュー・承認済みcanonical verification・人の完了確認は親が担当する。
