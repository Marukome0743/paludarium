# U5 スレッドとfutexのコード生成計画

## Summary

- Builds: Step35。Step34の再レビュー（review-13）のMinor 3件（R-13 traceability.jsonを変えていないという食い違い、R-14 coverageの言い過ぎと呼ばれていないcoverageの道具、R-15 traceability.jsonの各行の時点の印）をU5の記録で直す。
- Touches: U5のcode-summary.md、unit-test-instructions.md、traceability.json（notesの先頭の注記だけ）、traceability.md。製品・CI・workflow・ほかのUnitの記録・source-manifest.jsonは変えない。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## 前回のSummary（Step34）

- Builds: Step34。U5の確かめ直し（review-12、READY、Major 2・Minor 3）のR-08〜R-12をU5の記録で直す。U5だけのcoverage（固定13ファイル）が今どのworkflowでも測られていないことも記録に書く。製品は変えない。
- Touches: U5の記録だけ（code-summary.md、traceability.md、unit-test-instructions.md、source-manifest.json、Step34bでtraceability.jsonのNFR2・NFR8のtargetとnotes）。製品・CI・workflow・ほかのUnitの記録は変えない。呼び元が消えた `.github/scripts/u5-current-diagnostic.py` と、U5だけのcoverageをCIに戻すかどうかは、製品の変更なので次のpushで決める。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## 今回の計画：Step35（Step34の再レビューのMinor R-13〜R-15を直す）

2026-10-19 JST。Step34・34bの再レビュー（review-13、READY、新しいMinor 3件）の後、checkpointで人がRequest Changesを選んだ（先にR-13〜R-15を直す。記録だけ。呼ばれていない疑いのcoverageの道具は次のpushで扱うと書く）。`scripts/u5-coverage.py` と `scripts/u5-coverage-native.py` は、`.github/workflows/`・`scripts/`・`tests/` のどこからも呼ばれていないことを計画の段階で読み取りで確かめた（grep、該当なし）。

- [x] Step 35 — **review-13のMinor 3件を記録で直す**。(1) R-13：code-summary.mdの「現在の状態（Step34）」節の冒頭の「traceability.jsonは変えていない」を「traceability.jsonはStep34bでNFR2・NFR8のtargetとnotesだけを変えた」に直す。手順書の「今回Step34」節の期待結果は、計画のときに「traceabilityはpass、findings 0（Step34bでNFR2・NFR8のtargetを替えた後）」に直した。(2) R-14：同じ節の「残るのはworkspace全体の80%の下限だけ」を「U5の固定13ファイルだけのcoverageは無い。U5の製品のファイルを含むクレートを測るU9・U11のクレート単位の80%の下限（`ci.yml`・`u14-quality.yml`）と、workspace全体の80%の下限は残る」に直す。呼び元が無い `scripts/u5-coverage.py`・`scripts/u5-coverage-native.py` を、`.github/scripts/u5-current-diagnostic.py` と並べて次のpushで扱うものに加える。traceability.jsonのNFR3のnotesの先頭に「2026-10-19：U5の固定13ファイルだけのcoverageは、27d05de1でu5-quality.ymlが消えてから測られていない（targetのscripts/u5-coverage.pyはどこからも呼ばれていない）。CIに戻すかは次の製品の変更のpushで決める。以下はその時点の記録。」を足す（statusとtargetは変えない）。(3) R-15：traceability.jsonで「今回Steps29〜32は…」で始まる各行のnotesの先頭に「（履歴：9aa14978〜62611f25時点の観測。今の状態はcode-summary.mdの先頭の節）」を足す。NFR8のnotesの先頭の注記に、`ci.yml` は実Safari 21件を動かさず（Safariは `u11-acceptance.yml`・`u11-safari-stability.yml`）、43件の差分は `ci.yml` のcoverageの `--workspace` の中で動くことを足す。traceability.mdの注記にも、製品のファイルが27d05de1まで変わっていないことの根拠としてU15の `verification/ci-27d05de1/product-changes-e3c29d1d-27d05de1.txt` への参照を足す（R-12の残り）。status・id・targetは変えない（NFR2・NFR8はStep34bのまま）。製品・CI・workflow・ほかのUnitの記録・source-manifest.jsonは変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR3、NFR8。

## 前回の計画：Step34（確かめ直しの指摘を記録で直す）

2026-10-19 JST。U15のStep22〜28（push、head 27d05de1）で、U5のmanifestにある `u5-current-verification.yml`・`u5-native-diagnostic.yml`・`u5-quality.yml` が消え、正式な確認コマンドがU15の `entry-e3c29d1d/entry-f.py`・`binding-e06f.json` に替わった。U5の確かめ直し（review-12、READY、Major 2・Minor 3）の後、checkpointで人がRequest Changesを選んだ（先にR-08〜R-12を直す。U5だけのcoverageが今は測られていないことも記録に書き、CIに戻すかは次のpushで決める）。人の指示：「ワークフローの順で進めてください。U1 の確かめ直しから始めて、ファイルが変わった Unit を順に確かめ直し、U15 のレビューと完了確認、U11 の確かめ直しまで進めてください。」

- [x] Step 34 — **確かめ直しの指摘を記録で直す**。(1) R-09・R-10：code-summary.mdの先頭に「現在の状態（2026-10-19 JST、Step34）」節を足し、今の正式な確認コマンドは `verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用）で、記録に出てくる候補（`verify-current-u5-preview-bound.py`・`verify-current-u1-u7-u9-u3-u5.py`）やU2の `u2_candidate.py`、「承認前に実行していない」「承認は未完了」はその時点の記述であることを書く。U5の製品のファイルは変わっていないこと、消えた3本のworkflowのjobの今の場所（600秒のfuzz `kernel_threads_u5`・`kernel_futex_u5` は `u14-fuzz.yml`、3OSのテストとfmt・clippy・依存は `u14-quality.yml` と `ci.yml`、`diff_u5` は `ci.yml` のcoverageのjobの `--workspace` 実行の中だけ）と、**U5だけのcoverage（固定13ファイル、前回86.23%）は今どのworkflowでも測られておらず、workspace全体の80%の下限だけが残る**こと、これをCIに戻すかは次の製品の変更のpushで決めることを書く。27d05de1のCI 8 runがすべて成功したこと（U12は人が認めた1 jobの再実行）も書く。(2) R-08：source-manifest.jsonのwritesから、消えた3本（`.github/workflows/u5-current-verification.yml`・`u5-native-diagnostic.yml`・`u5-quality.yml`）を外し、理由（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）を新しい節に書く。呼び元が消えた `.github/scripts/u5-current-diagnostic.py` は残っていて次のpushで扱うことも書く。(3) R-11・R-12：traceability.mdの見出しの直後に、表と3行目の「検証済み：source9aa14978」はその時点（head 9aa14978）の観測で、NFR9の `nightly-2026-10-01` などtoolchain・compiler・Nodeの値もその時点のものであり、今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`、今の状態はcode-summary.mdの先頭の節であることを1行で足す（表は変えない）。code-summary.mdの新しい節にも同じことを書く。(4) 「今回」「現行」で始まる古い見出しは「履歴：…（作成時の見出しは「…」）」にする（本文は変えない）。unit-test-instructions.mdの先頭に「今回Step34」節を足し、Step33の見出しを履歴にする。製品・CI・workflow・ほかのUnitの記録・traceability.jsonは変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR3、NFR8、NFR9。

### Step34の追加（2026-10-19、人の判断）

Step34の作業の後、正式sensorのtraceabilityが `NFR2: target file does not exist: .github/workflows/u5-quality.yml` と `NFR8: …` で通らなかった（27d05de1で `u5-quality.yml` が消えたため。Step34の記録の直しによるものではない）。人の判断（原文）：「案 A で進めてください。U5 の traceability.json の NFR2 を u14-fuzz.yml、NFR8 を ci.yml に替え、手順書に残った「今回」の見出し 2 つも履歴にしてください。」

- [x] Step 34b — **traceability.jsonのtargetと手順書の見出し**。(1) traceability.jsonのNFR2のtargetを `.github/workflows/u14-fuzz.yml`、NFR8のtargetを `.github/workflows/ci.yml` に替え、それぞれのnotesの先頭に「2026-10-19：27d05de1で `u5-quality.yml` が消えたため、targetを今そのjobを動かしているworkflowに替えた（NFR2の600秒のfuzzは `u14-fuzz.yml`、NFR8の品質のゲートは `ci.yml`）。以下はその時点の記録。」を足す。status・id・ほかの行は変えない。(2) unit-test-instructions.mdに残った見出し「今回の記録更新（Steps26〜28）」「今回の現行ソース再確認（Steps20〜22）」を「履歴：…（作成時の見出しは「…」）」にする（本文は変えない。計画のときに書いた）。(3) code-summary.mdの「現在の状態（Step34）」節に、この2つを書く。そのあと正式sensor 2件（traceabilityはpassになる想定）、独立再レビュー、checkpointの検証、人の承認に進む。NFR2、NFR8。

## 前回のSummary（Step33）

- Builds: Step33。U5が担当するファイルが、Build and Testで使った版（head e4f84768）から変わっていないことを確かめ、今の正式確認コマンドで確かめ直す。製品・試験・記録は変えない。
- Touches: この計画と手順書のStep33の節だけ。
- Tests: 新しいテスト・CIの実行はない。U5のsource-manifestの全ファイルがe4f84768と同じことを読み取りで確かめ、独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpointを行う。

## 今回の計画：Step33（Build and TestのLoop-back 1：変更がないことの再確認）

2026-10-17。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と、U1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。12d6a2f6・1ceae86cで変わったのは、U14のJIT・wasm・テストと `mise.toml` で、U5のsource-manifestのファイルは含まれない。正式確認コマンドは、人の承認でU2の `verification/loopback1-next/u2_candidate.py` になっている。下のSteps29〜32で述べた「最終確認候補」は、その時点の履歴である。

- [x] Step 33 — U5のsource-manifestの全ファイルについて、作業コピーが e4f84768 と同じであることを読み取りで確かめる（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <paths>`）。違いがあれば止めて報告する。記録は変えない。独立再レビューのあと、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。

## 前回のSummary（Steps29〜32）

前回のSteps29〜32は、人が承認した確認スクリプトの限定修正である。旧CIの全検査を保持し、mise.tomlのAI-DLC版2.11.0から2.11.1-preview.20261012.1への変更だけを別に厳密照合する。製品・AI-DLC本体・guard・旧checker・原本を保持し、新しい重い試験と外部送信は追加しない。Steps26〜28の記録照合と旧専用試験は履歴として保持する。

- Builds: 旧署名ソースの全検査と現行設定差分を分離する確認候補。
- Touches: U5記録・検証helper・回帰、新しい最終確認候補。旧checker・製品・fixture・CIを保持する。
- Tests: 設定差分の正常・異常境界12件以上と既存回帰、全スクリプト診断、正式検査・独立再レビュー。最終確認コマンドは別途承認後に実行する。

## 今回の限定修正（Steps29〜32）

- [x] Step29：旧署名head62611f2556c4caf1470a7eb4471269d92611db6eのmise.toml原本と現行bytesを固定する。許す差分はAI-DLCのversion値2.11.0→2.11.1-preview.20261012.1だけとし、他tool・取得元・asset指定・両lock・compiler・製品sourceの一致を要求する。旧全checkerを変更せずに実行する署名ソースviewと現行入力検査を分離し、実workspaceを書き換えない。
- [x] Step30：新helperと確認候補をU5記録内／intent verificationへ作る。正常2件、想定外version、他tool変更、asset変更、source変更、lock変更、欠落、余分な入力、symlink、旧／現行混同、原本digest改変の12境界以上を検査する。旧検査の省略・全mise.toml除外・hashの再基準化を行わない。
- [x] Step31：全検査の診断で旧証拠と現行設定を照合し、結果を診断として保存する。正式sensorと独立再レビューを行い、判定を指定しない。旧失敗原本と質問ファイルの既知構造FAILを保持する。
- [x] Step32：別途承認された新しい最終確認コマンドで正式再検証する。U5の完了承認後に正式な順序でU14へ戻る。strict guard、coverage80%下限、guest30秒、旧全検査・原本を維持する。

## 承認された追加検証（Steps23〜25）

- [x] Step 23: 現行製品・fixtureを変更せず入力集合と両lockを固定する。U5専用診断CI/helperを準備し、全入力のbefore/after/current SHA、実使用Rust/compiler・ツール版、設定、署名済みcommitとCI jobの結合を保存する。追加診断ファイルも入力集合へ明示する。最新ツールは公式情報と照合し、追加の製品設定変更が必要なら具体的最小案を提示する。旧417入力の375一致・42変更、旧ASan compiler 21b707e3fと現行32dba69d6の相違を履歴として保持し、旧成功を流用しない。
- [x] Step 24: 同一現行ソースのx86-64 Linuxで毎回fresh native期待結果を生成し、既存全43ケースのdiff_u5を実行する。既存13製品ファイル・同じ分母規則のLinux coverage80%以上、3OSのU5限定Host7/Kernel27/MMU6/Runtime6（計46、ignored 0）、fmt/Clippyと依存4検査を実行する。kernel_threads_u5/kernel_futex_u5を各600秒以上ASan/LSanで実行し、生ログ・実exit・実使用compiler・instrumentation・両lock・入力一致を保存する。30秒入力制限、比較mask、kill/reap、閾値を維持する。失敗・0件・skipを合格にせず、原因と必要修正を報告する。
- [x] Step 25: Node/本物Safariの共有メモリ・nested Worker・simultaneous sessions・kill等はU9の現行証拠の依存ソース・module・compiler・設定一致と対象ケースを明示して限定再利用し、guest clone/futex43件やnative実Host割当の代替にしない。新CIの全入力とraw証拠を結合してcode-summary・traceability・source-manifestを更新し、正式検査と独立レビューへ渡す。新U5証拠を検証する最終確認候補は構文確認までとし、コマンド変更承認後に実行する。strict guard、80%下限、30秒制限を維持し、ID競合の完全解消は未検証と区別する。

## 今回の再確認（Steps20〜22）

- [x] Step 20: FR2.3/FR5.4/FR9.1、NFR1/2/3/5/7/8/9。現行U5担当ソース、共有契約、両lock、Rust固定版と実使用compilerを確認する。旧7eb1819の有限46テスト・36担当パスと旧9aa1497の417入力・43差分・13ファイルcoverage・ASan・browser証拠を履歴として区別し、現行入力へ照合する。担当・共通要件は独立した上流割当から取得する。最新ツールは作業の区切りで公式情報を確認し、更新が必要なら影響と最小変更を提示する。
- [x] Step 21: U5限定の内部テストを実行し、件数・skip・終了コードを保存する。Linux fresh native43件、固定13ファイルcoverage80%、3OS、kernel_threads_u5/kernel_futex_u5各600秒ASan/LSan、本番wasmのNode/本物Safariについて、依存ソース・両lock・実使用compiler・設定・測定対象の一致範囲を調べる。有限46件を全品質検証の代替にしない。保存結果の再利用は根拠を限定し、不足する重い検証は具体的な追加実行案として人へ提示する。この段階では製品・fixture・CIを変更しない。
- [x] Step 22: 今回確認した結果と未検証をcode-summary・traceability・source-manifestへ反映し、正式検査と独立レビューへ渡す。sensorの過去FAILを現在の結果とみなさず、正式コマンドの実出力を記録する。承認済み最終確認コマンドが新しいU5証拠を検証できない場合は候補を用意し、変更承認後に実行する。strict guard、coverage80%下限、入力30秒制限、比較maskと測定分母を維持する。全体のセッションID競合解消は実測した範囲を超えて主張しない。

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

## Sources

- inception/requirements-analysis/requirements.md: FR2.3、FR5.4、FR9.1、NFR1〜3/7〜9。
- inception/units-generation/unit-of-work.mdとunit-of-work-story-map.md: U5はcloneによるスレッド作成とfutex、ホストスレッドへの割当を担当。別プロセスのfork/execはU8。
- inception/contract-design/contract-summary.md: C2 Host、C4共有メモリ、C5 CPU、C8 Kernel、C10 Runtime。
- inception/domain-design/components.md: ThreadとFutexWaitQueueをKernelが所有、実行ループをRuntimeが所有。
- 検証済みの構造確認: kernel/src/lib.rsのThread、spawn_initial、handleとruntime/src/lib.rsの単一スレッド実行ループを検索で確認。U5の詳細設計文書は未作成。

## Scope and completion

cloneのスレッド用flags、TLS、parent/child TID、clear_child_tid、exitとexit_groupの区別、futex WAIT/WAKE/WAIT_BITSET/WAKE_BITSETとprivate/shared key、timeout、値不一致、異常アドレス、割込みを扱う。probeのrayon/Mutex/Condvarが必要とする追加操作は使用実態を調査し、必要なものを明示して実装する。ゲストsyscallをホストへ番号のまま転送しない。共有メモリと原子的命令の整合を検査し、Host境界の外でstd::threadを直接呼ばない。

ネイティブの実スレッドでゲスト実行ループを動かす。wasm側のWorker接続はU11と境界を共有し、U5では製品の共有状態とHost契約を用意する。既存のwasmスレッドprobe成功をゲストclone成功と同一視しない。未実装のflags/操作は明示的エラーとする。共有ソース変更後、先行Unit成果物を維持して現行ソースの完了確認を更新する。

## Steps

- [x] Step 1: FR2.3/FR5.4。Kernel/Runtime/Host/MMUの現状と共有所有権、signal/fd/TLS境界を調査し、具体的変更ファイルとclone/futex操作一覧を記録する。
- [x] Step 2: FR9.1/NFR7。U5専用native guest runnerと比較ハーネス、単体テストfilter、30秒process-group watchdogを準備し実行可能性を検証する。
- [x] Step 3: FR2.3/NFR1。実装前にclone/TLS/TID/exit、WAIT/WAKE/bitset/timeout/mismatch/EFAULT/EINVAL/割込みの有限差分ケースを用意し、fork CIのx86-64 Linuxで毎回native期待結果を生成する。順序依存値とTIDは比較規則を明記する。
- [x] Step 4: FR5.4/NFR2。共有アドレス空間・process/thread/fd/signal所有権を安全なRustで整備し、Hostの実スレッド起動・待機契約へ接続する。MMU/CPUの原子性、終了・join・killでの資源回収を実装し、内部部品の境界テストを書く。
- [x] Step 5: FR2.3。cloneスレッドflags、child register/stack/TLS、TID書込とclear_child_tid wake、exit/exit_groupを実装し、Step3のnative差分を通す。プロセスcloneをU8担当として明示する。
- [x] Step 6: FR2.3/NFR7。futex key/待機登録/比較と登録の不可分性/bitset/期限/割込み/起床を実装し、lost wakeと競合を検査する。内部部品は各5〜8件以上の正常・境界・異常テストを持つ。
- [x] Step 7: FR2.3/FR5.4。Runtimeの実スレッド実行とKernelへ統合し、rayon/Mutex/Condvar相当のU5限定guestでnativeとの差分、終了・kill・同時メモリ操作を検証する。probe全量達成は後続機能の依存と区別する。
- [x] Step 8: NFR3/8/9。固定nightly/locked、3OS単体・fmt/clippy・依存・native差分のfork CIとLinux coverage80%以上、対象fuzz各600秒ASan/LSanを確認する。本番wasmの回帰と実Safariを対象変更に応じて実行する。失敗や未検証は具体的に記録し下限を緩めない。
- [x] Step 9: FR9.1/NFR1。先行Unit成果物を維持し共有変更後の完了確認、source-manifest、traceability、code-summary、差分比較規則と検証証拠を更新する。独立レビューと人の完了確認へ渡す。

## Additional steps: 待機開始前のtimer通知

既存Step1〜9の本文・完了記録と旧source証拠は保持する。以下は待機開始前に届くtimer制御通知による偽EINTRだけを修正する追加計画であり、新しい完了判定には全追加stepが必要である。製品・fixture変更はこの計画とテスト手順のPlan Approval、および必要な具体的設計summary確認を得てから開始する。

- [x] Step 10: FR2.3/NFR1。現行sleep入口が新generationを採取済みの場合と、SignalInbox owner drainが通知種別を失う場合を限定調査する。変更候補はKernel inbox.rs/syscalls.rs/threads.rs、必要なfiles.rs待機境界と既存U5 tests。timer制御通知の種別をowner acknowledgementで保持・取得し、実signal・group終了・外部停止と区別する具体的設計を記録し、必要summary確認を得る。既存mask・queue mutex・process/thread配送・通知先行保持を壊さない。
- [x] Step 11: FR9.1/NFR7。製品変更前に既存0〜37を保持して追加38〜42の有限guestを作る。38:子disarm完了→ready→親relative nanosleep。39:子がsleepより後のtimerを設定→ready→親relative nanosleep。40:子がset/shorten/disarmを反復して完了→ready→親relative nanosleep。41:同じdisarm先行順序で親absolute clock_nanosleep。42:disarm先行順序で親timeout付きfutex待機。全43ケースのrunner/harness/build/比較表を一致させ、30秒watchdog・kill/reap・raw観測を保持する。readyのrelease/acquire関係でtimer syscall完了が親待機入口より前と確定し、生時刻・TIDを比較しない。
- [x] Step 12: FR2.3/NFR1。fixture/harness最小adapterだけをrootへpush-readyで渡し、製品は未変更で停止する。x86-64 Linux CIで全43native観測を取得し、新ケースのerrno・handler回数・経過区間bool・exit/stdout/stderrを実測から確定する。保存済oracleや一般規則で期待を推定しない。rootのnative-first証拠確認後のgoを受けて初めて製品修正へ進む。
- [x] Step 13: FR2.3/NFR2。ownerがackしたtimer通知種別でsleep期限再計算へ進め、入口前通知でも偽EINTRにしない。generationは待機中変更の再計算に併用し、実signal/group終了/外部停止は維持する。実装後にHost同期単体テストを追加する：通知が入口前・Host entry後・再計算中、set/shorten/disarm反復、別worker process drain、通知＋masked/ignored/実signal/group終了、futex/flockへのmetadata-only通知、owner ack/send競合。待機開始前の順序はchannel/barrierで確定し、sleepによる順序推定だけに頼らない。scope外の機能を追加しない。
- [x] Step 14: FR9.1/NFR1。現source CLIをbuildし、限定再現と全43fresh native差分を通す。既存38ケース、とくにuntimed SA_RESTART再開/handler値変更・timed EINTR・timer待機中更新を保持する。build/runner/harness/比較表/候補checkerの件数とraw manifestを43へ厳密に同期する。canonical verificationの承認済みcommand stringは変更せず、内部checkerの対象件数・証拠だけを更新する。
- [x] Step 15: NFR3/8/9。rootが安定sourceを限定commit/pushしVerifiedを確認する。既存417claimed source leafと先行証拠73件を保持して同source検証を再結合し、必要な新pathが出た場合はschemaに従い明示して全claimを再検査する。3OS fmt/clippy/tests/deny・先行Unit差分・全43差分、固定13製品fileのLinux coverage80%以上、threads/futex各600秒ASan/LSanとlock不変、本番の現module Node/実Safariを検証する。旧成功証拠は歴史として保持し、新source完了へ流用しない。閾値・timeout・対象を緩めない。
- [x] Step 16: FR9.1/NFR1。全新証拠をraw run head/job/commit/module/stream/hashへ結合し、source-manifest（stage/unit/version/writes、repo/pathのみ）・code-summary・traceability・原本検証記録を製品truthへ更新する。候補checkerを再実行して全43・先行Unit保存・coverage/sanitizer/browserを照合した後、製品と必須成果物をfreezeして親へ独立レビューを依頼する。独立review完了後、rootが承認済みcanonical verificationを同じcommand stringで実行し、人のcheckpointへ渡す。review履歴等のbookkeepingは製品成果物へ転記しない。

追加ケースのtimer値とsleep/timeout値、経過区間boolの境界は有限実行と既存watchdogを維持するようfixture実装時に具体化し、native-first段階の比較表へ記録する。実測が想定と異なる場合もnative観測を優先し、条件を弱めて合格にしない。

## Risks and boundaries

### 今回の記録更新（Steps26〜28）

- [x] Step26：正式renderのTesting Contractを保持し、手順・現行共有ソース・保存証拠の差分を照合する。coverage80%、guest30秒、strict guardと既存固定対象を維持する。
- [x] Step27：Unit限定の正式検査と独立再レビューを行う。現行CI・保存専用証拠・未検証を区別し、不足を無条件の再利用で隠さない。
- [x] Step28：承認済み最終確認コマンドで照合し、U5の再確認承認後に通常の順序でU14へ戻る。AI-DLC本体と製品コードは変更しない。

- [x] Step 19: FR9.1/NFR1。sensor-repair-investigation.mdの修正案に沿ってtraceability sensorを修正する。storiesなし・Unitありの経路は独立した上流割当からFR/NFRを取得し、共通要件を含める。storiesありのAC経路とUnitなしの全体経路、詳細NFR/BR追加、target/status/path検査を維持する。U5のupstream_idsを期待集合の根拠にせず、9 IDsをコードへ固定しない。主担当・関係Unit・全Unit共通の意味を分離し、NFR割当の不足・未知Unit・割当の矛盾は理由付きFAILとする。既存frameworkのテスト配置と更新方法を確認し、隔離したテスト用コピーで回帰を実行してから実sensorへ適用する。担当1件削除、共通1件削除、他Unit要件、壊れた割当、storiesあり、Unitなし、詳細NFR/BR、不正target/statusを検証する。U5の正式sensorを再実行し、結果に応じて対応表を正しい上流割当に整合させる。全要件の一括OKや失敗除外を行わずguard strictを維持する。

- [x] Step 18: FR9.1/NFR1。今回差し戻された文書検査を修正する。code-summary.mdへ内容に対応するH2見出しを追加する。traceabilityの51 ID欠落について、検査コマンドが全体要件を入力しているのか、U5割当要件を落としているのかを共有契約・Unit定義から確認する。U5割当9要件の対応と実在する製品・テストパスを検査し、他Unitの要件をU5が実装したと偽って追加しない。Unit限定の正式検査を実行し、全体検査との対象の違いと原本出力を保存する。古い9aa1497の証拠は過去snapshotとして区別し、今回確認した7eb1819の有限テスト46件とsource照合を正確に記載する。製品・fixture・CI設定・閾値は変更せず、独立レビューと承認済みcanonical確認を再実行する。

- [x] Step 17: FR9.1/NFR1。文書整合修正だけを行う。Plan Approval後にtraceability.jsonの全7notesを走査し、現在結果の主張をhead9aa149786015ad9f789e8527cc30d7f30f2f9482、全43件、coverage3256/3825、threads18531279runs/futex9935154runs・各601秒、preentry-final原本パスへ揃える。過去証拠は歴史と明示して保持する。traceability.md/code-summary/final-proof/source inventoryの対応も読み取り専用で照合し、変更した文書の証拠hashだけを再結合する。417sourceの同head不変を確認して既存CIを再利用し、製品・fixture・workflowを変更せず重いCIを繰り返さない。承認済みcanonical command stringを維持して候補照合を再実行し、成果物freeze後に親が新しい独立レビューとcanonical verificationを実行して人のcheckpointへ渡す。閾値・ケース・timeout・保存証拠を緩めない。

共有MMU・Thread管理の変更は大きい。Step1で確定する具体設計が承認内容から変わる場合は現行計画を更新し、適用中の承認規則に従う。タイミング依存の待機テストはbarrier等で確定的に構成しsleepだけに頼らない。wasm guest Worker、別プロセスclone、eventfd/epollは担当Unitの完了と区別し、今回未検証の動作は未検証と記録する。
