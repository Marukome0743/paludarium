AIDLC-UNIT: u14-jit-wasm
AIDLC-TESTING-CONTRACT: sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5

## Files and commands

Write and edit files yourself with your file tools, never through the shell (no heredoc, no `echo`, `printf`, or `python3` writing a file, no `sed -i`, no `mkdir`; the file-write tool creates any missing folder). A command the person asks for, or one the plan names (a package install, a build, a scaffolder, a migration, a formatter, a code generator, even a `mkdir`), still runs as written. Every file you make on your own, a scratch file, a helper script, a command's output, stays inside the project (nothing in /tmp or any folder outside it), and a command's output is read from the tool result, never sent to a file; a file the person asks for, or one the plan names, goes where they say. Quote a pattern meant for the program, not the shell (`--include='*.ts'`), and never start an argument with `=`: zsh, the macOS default shell, stops on both. Read, list, and search (your own knowledge files included) with your file tools where you have them; where the shell is your only way to read, use one plain read command (no `cd` before it, no pipe or second command after it). Run every AI-DLC command exactly as written, as a command of its own (no `cd` before it, no pipe or second command after it), keeping its path as written (never a full path): a shell line can stop and ask the person to approve it.

## The plan file

Tick each step's box in `aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-generation-plan.md` as you finish the step. That is the only change you make to that file.

## Approved plan

# U14 wasm JIT：コード生成計画

## Summary

- Builds: x86-64からwasmへの最小JIT、インタプリタとの差分、Node Workerの各10回性能比較。
- Touches: paludarium-jit、MMU/Runtime/wasm接続、起動用JS、U14専用テスト・診断CI。
- Tests: 内部4部品各7件以上、接続境界10件以上、4環境の実guest比較とcoverage80%以上、性能検定5%。

## 入力と現状

Unit定義U14、要件FR8.1〜FR8.3、NFR1/2/3/6/8、契約C9/C10/C12、components.mdのJitを実装する。既存NoopCodeCacheとnativeのインタプリタを保持する。現在RuntimeはNoopCodeCacheを利用し、JSはjit:trueを未実装として拒否する。製品JITの動作は未検証。

## 実装方針

Rust側でDecodedInstructionから制御フロー終端までの基本ブロックとwasmバイト列を生成し、既存Worker内のJSがWebAssembly.Module/Instanceを生成・管理する。独立Workerを追加せず、各guest Workerの共有メモリと既存状態ABIへ接続する。C9の同期呼び出しで実行できる接続を先に小さく確認する。状態・例外・syscall・kill・予算をインタプリタと揃える。対応命令はnative差分で先に固定し、未対応命令は状態を破壊せずフォールバックする。

メモリ読書きと命令fetchはMMUの権限・範囲・部分fault意味論を維持する。生成コードは生のhostポインタへ無検査アクセスしない。ページ世代・mapping世代を共有し、write/protect/unmap/remap/execの変更を他Workerでも実行前に検査する。コード取得から公開までの競合、複数ページ、実行中変更を含む原子性を設計し、古い世代の生成コードを実行しない。fallbackだけの成功をJIT成功と数えない。

## 手順

- [ ] Step 1 — 現行ソース・両lock・最新ツール・契約を固定し、既存JIT限定テストrunnerを確認する。既存CIと共有状態ABI、MMUの全書込み経路を監査し、必要な限定変更を一覧化する。FR8.1、NFR8。
- [ ] Step 2 — 実装前にU14命令/プログラム差分ケースとLinux native取得経路を用意する。整数・flags・分岐・メモリ・fault・未対応命令・自己書換えを含める。同じ固定probe/aubeと既存maskを使い、native原本を実機CIごとに取得する。承認済みの固定aube限定例外を専用設定・receipt検査へ実装し、crates.io unsafe-libyaml 0.2.11とlockを厳密照合してRUSTSEC-2024-0449だけを除外する。製品deny.tomlとprobe監査、固定source/lock、他advisoryと依存4監査を維持する。10境界回帰・既存U10 policy/evidence回帰・静的検査後、具体化した追加送信範囲を人へ提示しLinux CIを再実行する。初回失敗を保持する。FR8.2、NFR1/8。
- [ ] Step 3 — 内部4部品（ブロック抽出、wasm生成、世代付きキャッシュ、実行ブリッジ）を層ごとに実装し、その層の単体テスト各7件以上を追加・実行する。生成wasmの検証失敗、境界、状態復帰、フォールバックを含める。C9、FR8.1、NFR2/3。
- [ ] Step 4 — Runtime/MMU/wasm/JSを統合し、jit:false互換を維持してjit:trueを有効にする。接続境界10件以上（共有Worker invalidation、跨ページ、protect/unmap/remap、生成中write、fault、syscall、kill、trap、同時処理）と実wasm回帰を追加する。FR8.1/8.2、C10/C12。
- [ ] Step 5 — 同一署名ソース・module・固定guestでNode/Chromium/Firefox/本物Safariを比較する。各環境で既存14ケース以上をJITあり/なし両方でfresh Linux期待値と照合し、probe全8項目、aube、元argv、既存C12/U11/U13回帰を維持する。実際のJITブロック実行も証明する。FR6.3/7.2/8.2。
- [ ] Step 6 — 3OS品質と依存4検査、固定Rust JIT対象・変更JS・Python検証器各80%以上、既存workspace80%以上を確認する。新JIT生成器/キャッシュfuzzと依存変更のある既存対象を各600秒ASan/LSanで実行する（MMU最大4608バイト）。wasm専用ブリッジは実wasm境界で検査し、native sanitizerの代替と主張しない。Node Workerでprobe全体を各10回測定し、下記性能判定を行う。FR8.3、NFR2/3/6。
- [ ] Step 7 — 全入力・両lock・署名head・CI全ジョブ・原本digest・生測定を固定し、source-manifest/summary/traceabilityを更新する。正式検査・独立レビュー後、新確認スクリプトは旧検査をその旧ソースへ保持し現行U14を別照合する。最終確認コマンドの人の承認と正式検証・完了承認へ進む。

## 性能判定

FR8.3の対象は短いmicrobenchmarkではなくprobe全体。Node Workerの同じmodule/guest/引数を使用し、計測なしreleaseでJITなし/あり各10回、10ペアの順番を固定seedで均衡化して交互実行する。各回fresh Sessionを作り、guest実行開始から終了までを測りJITコンパイル時間を含める。module読込・準備時間も別記録する。計測前の共通warmupは測定10回へ含めず、数と条件を先に固定する。

片側の対応あり正確ランダム化検定を採用し、10ペアの全1024符号反転からp値を算出する。平均時間JITあり<なし、p<0.05、全20回のprobe全PASS・exit0・30秒以内・JIT実行証拠をすべて要求する。全標本・seed・順序・ツール版・速度差・p値・背景負荷を保存する。外れ値除外、成功するまで再測定、試験後の検定変更はしない。失敗は不足として報告し、性能をPR必須ゲートに変えない。

## 制限と変更管理

native JITと公開処理U15は対象外。旧native SIGSEGV・Windows race原因・ID競合の完全解消はこの計画で解決済みとしない。共有コード変更は影響Unitと証拠を監査し、旧証拠を現行へ無条件流用しない。snapshot上限、strict guard、guest30秒、既存比較mask、coverage分母を弱めない。C9同期接続で契約変更が必要と分かった場合は具体的差分を提示する。

## Testing Contract

```json
{
  "version": 1,
  "methodology": "custom",
  "source": "team",
  "ordering": "命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
  "scope": "rust-blink-port",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "私たちはテストを各 Bolt の成果物の一部として扱います。エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まるので、差分テストを中心に置きます。\n\n- **Methodology**: custom\n- **Ordering**: 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。\n\n補足：\n\n- **カバレッジ**（Q5）：行カバレッジ 80% を下限にします。測るのはネイティブの Linux です。あわせて「範囲内の命令のうち、差分テストが 1 件以上ある命令の割合」を記録します。決めた下限は Build and Test で下げません。\n- **差分テストの期待結果**（Q6）：期待結果は、**CI を実行するたびに x86-64 Linux のランナーで作り**、エミュレータの結果と比べます。期待結果をリポジトリに保存する方式は取りません。\n  - 比べるもの：命令の単位ではレジスタ・フラグ・メモリ、プログラムの単位では標準出力・標準エラー・終了コード。\n  - x86 で結果が未定義のフラグや値は比べません。命令ごとに「比べないもの」を表で持ちます。\n  - pid・時刻・乱数・アドレスなど、実行ごとに変わる値は、比べる前にそろえるか、比べる対象から外します。\n  - 段階 5 では、JIT ありと JIT なし（インタプリタ）の結果も同じ差分テストで比べます。JIT だけの意味論は持ちません。\n- **単体テスト**：層ごとに `cargo test` で書きます。テストやビルドの道具は外部のものを使ってよいです（Q1）。\n- **CI のゲート**（Q7）：\n  - 変更のたび（PR）：Linux・macOS・Windows の単体テスト、lint（`cargo fmt --check`、clippy の警告はエラー）、依存の検査（ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること、既知の脆弱性）、x86-64 Linux での差分テスト。通らなければマージしません。\n  - 段階ごと：その段階に入ったら、その段階の probe と aube の合格を必須にします。\n  - 夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）。失敗したら Issue にして直します。\n- **Safari**（Q12）：Safari での合格は、macOS の CI で本物の Safari を動かして確かめます。WebKit を使う別のテスト用ブラウザでは代えません。\n- **wasm**：paludarium が用意する起動用 JS とテストハーネスで、Node.js の Worker とブラウザ（Chromium 系・Firefox・Safari）で同じテストを動かします。テスト用のページには COOP/COEP の見出しを付けます。\n- **揺れるテスト**：スレッドを使うテストには時間切れの上限を付けます。揺れたテストは記録して直します。\n- 段階 5 の「JIT なしより速い」は、回数・統計量・差の大きさを要件分析で数値にしてから測ります。速さの測定は PR のゲートにしません。\n- Test Strategy は Standard です。量と種類はこの設定に従い、上の補足はそれに足すだけです。"
    },
    {
      "layer": "project",
      "text": "- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) \n\n- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) \n\n- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) \n\n- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) \n\n- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) \n\n- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) \n\n- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) \n\n- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) \n\n- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) \n\n- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) \n\n- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) \n\n- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) \n\n- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) \n\n- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) \n\n- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) \n\n- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) \n\n- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) \n\n- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) \n\n- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) \n\n- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) \n\n- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) \n\n- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) \n\n- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) \n\n- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) \n\n- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) \n\n- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) \n\n- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) \n\n- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) \n\n- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) \n\n- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) \n\n- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) \n\n- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) \n\n- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) \n\n- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) \n\n- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) \n\n- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) \n\n- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) \n\n- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) \n\n- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11)"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "custom",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Custom ordering - 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
      "Implementation and tests - preserve that exact ordering; do not convert it to layer-local TDD.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cc8e6bbb985d32c580aff1d457ccafb5f05a4b442140eb6cb6303d51ca2ba418",
  "contract_sha256": "sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5"
}
```

## Approved unit-test instructions

# U14 単体テスト手順

## Runnerと準備

既存runnerはRust cargo testとNode test runner。実装前の準備確認コマンドは `cargo test -p paludarium-jit --lib`（既存NoopCodeCache5件）。project固定Rust実体を解決して実行し、最新確認と更新は計画Step1で記録する。新テストがまだない段階の0件・skipを成功証拠にしない。

## U14限定コマンド

- 内部4部品：`cargo test -p paludarium-jit --lib u14_`。
- 共有接続：`cargo test -p paludarium-mmu --lib u14_`、`cargo test -p paludarium-runtime --lib u14_`。
- native差分：`cargo test -p paludarium-harness --test diff_u14 -- --nocapture`。
- JS境界：`node --test packages/paludarium-wasm/tests/u14-jit.test.mjs`。
- guest/4環境：`python3 scripts/u14-run.py acceptance`。
- 性能：`python3 scripts/u14-run.py performance`。
- 固定coverage：`python3 scripts/u14-run.py coverage`。
- U14 fuzz：`python3 scripts/u14-run.py sanitizers`。
- 検証器：`python3 -m unittest discover -s tests/guests/u14/runner-tests -p 'test_*.py'`。

新入口はStep2/6で作成する予定で、現在は未実装。入口はそのUnitの対象だけを実行し、内部で既存共有検査を必要に応じて一度実行する。包括的なcargo testやnpm testをUnitごとの通常コマンドへ入れない。

## テスト数と境界

内部4部品各7件以上（計28以上）。統合10件以上には自己書換え・他Workerの世代変更・生成中変更・ページ跨ぎ・mapping再利用・権限・部分fault・syscall・kill/trapを含める。命令差分は対応命令表と1件以上/命令の割合を記録する。4環境それぞれ14実guestケース以上をjit:false/trueで比較し、probe全項目を必須にする。fallback-onlyをJIT実行と数えない。

## データと測定

Linux実機で各CI実行時に期待結果を生成し、固定guest/module/head/両lockを一致させる。未定義flagsのみ既存表で除外する。mockは生成失敗などの内部境界に限定し、実wasm・実Worker・本物Safariの代替にしない。guestごとの30秒とkill/reap/cleanupを維持する。

Rust JIT crate（追加全製品ファイル）、変更JSとPython固定対象、および既存workspaceは行coverage80%以上。wasm専用経路はNode V8/実wasmテストの対象を別に固定して報告しnative coverageで検証済みにしない。測定対象一覧・生データ・分母・集計器を保存する。

## 性能・sanitizer

計画の片側対応あり正確ランダム化検定を測定前に固定する。全probeをNode WorkerでJITあり/なし各10回、全20回成功、平均改善かつp<0.05で合格。instrumentationのない実行を性能対象にする。新JIT fuzzおよび依存変更した既存対象は各600秒ASan/LSan、MMU最大入力4608バイト。compiler/binary/依存/設定の一致を証明できる旧対象だけ限定再利用する。

## 固定guest限定advisory例外の回帰

承認済み例外はU14専用設定でcrates.io unsafe-libyaml 0.2.11のRUSTSEC-2024-0449だけに適用する。`python3 -m unittest discover -s tests/guests/u14 -p 'test_guest_policy.py'`で10件以上の境界（正常、別ID、版、パッケージ、source、lock重複、root設定改変、生成設定/hash改変、他advisory失敗の伝播）を検査する。既存U10設定と証拠検査の回帰を維持し、製品deny.toml/probe/source/lockの不変を照合する。旧CDLA限定条件を完全に継承し、Linux CIで依存4監査とguest14＋元argv14比較を再確認する。これらはまだ未実装であり、例外を加えた設定の成功を無例外の監査成功と表現しない。

## 完了証拠

コマンドと実exit、テスト名/件数/skip、ソースと原本hash、署名済みCI全ジョブ、測定全標本を照合する。現行実行・履歴・未検証を分け、独立レビュー後に新最終確認コマンドを提示する。


