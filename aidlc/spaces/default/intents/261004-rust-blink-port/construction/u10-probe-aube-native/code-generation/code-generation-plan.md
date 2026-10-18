# U10 probe・aube ネイティブLinux実行計画

## Summary

- Builds: Step31。U10が担当するファイルが、Build and Testで使った版（head e4f84768。U9 Step80の `u10-native-diagnostic.yml` の修正を含む）から変わっていないことを確かめ、今の正式確認コマンドで確かめ直す。製品・workflow・記録は変えない。
- Touches: この計画と手順書のStep31の節だけ。source-manifest.json・traceability.json（旧い封印の対象）は変えない。
- Tests: 新しいテスト・CIの実行はない。U10のsource-manifestの全ファイルがe4f84768と同じことを読み取りで確かめ、独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpointを行う。

## 今回の計画：Step31（Build and TestのLoop-back 1：変更がないことの再確認）

2026-10-18。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と、U1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。12d6a2f6・1ceae86cで変わったのは、U14のJIT・wasm・テストと `mise.toml` で、U10のsource-manifestのファイルは含まれない。1ceae86cのCIでは、U10の差分job（u12-quality・u13-qualityの中の `U10 fixed guests and fresh native differential`）も成功した。正式確認コマンドは、人の承認でU2の `verification/loopback1-next/u2_candidate.py` になっている。

- [ ] Step 31 — U10のsource-manifestの全ファイルについて、作業コピーが e4f84768 と同じであることを読み取りで確かめる（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <paths>`）。違いがあれば止めて報告する。記録は変えない。独立再レビューのあと、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。
- [ ] Step 32 — 再レビュー（iteration 2、READY）のMinor 2件への対応（人のRequest Changes）。製品・workflow・source-manifest.json・traceability.json（旧い封印の対象）は変えない。code-summary.md（封印の対象外）の先頭に「現行Step31〜32（Build and TestのLoop-back 1）」節を足し、次を書く：(a) U10の担当sourceは12d6a2f6・1ceae86cの変更に含まれず、e4f84768から変わっていないこと（`git diff --quiet` exit 0）、(b) 「現行Step30」節の「CI未実行」はその時点の記述であり、その後、e4f84768（PR CI 39015770796、u12-quality 39015780495、u13-quality 39015782530）と1ceae86c（u12-quality 39028303336、u13-quality 39028305765）のCIで、U10の差分jobを含めて成功したこと、(c) 「現行Step26」節が挙げるU1の `final_candidate.py` はその時点の正式確認コマンドであり、今の正式確認コマンドは人が採用した `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` であること、(d) 2026-10-18のU10 checkpointの検証はexit 0だったこと。古い節の本文は変えない。正式sensor 2件を実行し、独立再レビューと今の正式確認コマンドでのcheckpointに進む。

## 前回のSummary（Step30）

- Builds: Build and Testからの差し戻し（人の指示）。U10が持つ共有workflowをU9・U12が直したため、U10は再レビューだけを受ける。U10自身の製品・workflowは変えない。code-summary.mdに、変更されたworkflowとCI未実行であることを記録する。
- Touches: U10のcode-summary.mdだけ。製品、fixture、workflow、source-manifest.json・traceability.json（どちらもhistory-sealの封印対象）は変えない。push・CI起動はしない（Build and Testで人の承認を得てから）。
- Tests: 新規テストなし。actionlint（shellcheck 0.11.0を明示）でU10が持つ変更済みworkflowを検査し、正式sensor、独立再レビュー、正式コマンドでのcheckpoint再検証を行う。

## 今回の差し戻し対応：Step30（共有workflowの再レビュー）

人の指示：「…同じ問題は u11-acceptance.yml・u10-native-diagnostic.yml（policy の指定なし）と u12-quality.yml（PALUDARIUM_TEST_NODE なし）にもあります。…手元への反映は、影響する Unit（U9〜U12）の再レビューを含めて正規の手順で進め、push と CI の前には承認を求めてください。」U10のsource-manifestが持つ `.github/workflows/u10-native-diagnostic.yml`（ゲストビルドを `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` に変更し、SHA固定の setup-python 3.15.0 を追加）と `.github/workflows/ci.yml`（envに `PALUDARIUM_TEST_NODE: node`）は、U9のSteps77〜79で直し、承認済み。根拠はU15の `verification/u12-quality-38994430947/README.md`（run 38994430947 で U10 の native-first job もゲストビルドの `cargo deny` で exit 1）。

- [ ] Step 30 — 確認と記録（FR6.1、FR7.1、FR7.2、FR9.1）。actionlintで `u10-native-diagnostic.yml` と `ci.yml` を検査し、変更行に新しい指摘がないことを確かめる（ci.ymlの既存4件、87・203・226行目は既存の指摘として記録し、直さない）。code-summary.mdの冒頭に「現行Step30」節を加え、U9が直した2ファイルの変更内容・根拠・確認結果と、CIでの実行はまだで（Build and Testで人の承認後）、U10のfresh native・probe・aubeの新しい実行結果は未確認であることを書く。traceability.jsonとsource-manifest.jsonは封印対象なので変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 承認された現行ソース追加検証（Steps13〜15）

Steps1〜12と旧証拠は履歴として保持する。旧7eb証拠と現行の44パス変更・追加、Rust10-01→10-10の差を新規実行と区別する。詳細はverification/current-audit-proposal.md。

- [ ] Step 13 — 新診断 `.github/scripts/u10-current-diagnostic.py` と `.github/workflows/u10-current-verification.yml` だけを追加し、現行324入力＋2診断入力・両lock・実compiler・設定のbefore/after/currentを固定する。公式最新版を確認して診断ツールを固定する。既存source-lockとrust-toolchainのnightly-2026-10-10を使用する。固定aube v2.6.1/bd94e42fとprobeを新ビルドし、aube upstream1365入力の非改変、lock、static ELF、binary hash、root deny全bytes継承、webpki-root-certs1.0.9限定CDLA全文hash、probe/aubeの各依存4検査を保存する。製品・fixture・既存ビルド処理を変更しない。
- [ ] Step 14 — 同一署名済みheadのx86-64 Linuxネットワーク名前空間内でfresh native14を先に取得し、同guestのemulator16と比較する。probe8、aube4、all/environment、default VFS追加操作、append-only主比較と元argv追加結果、node不在・#1645・0644 fixture・install/frozen/list状態・子孫回収を保持する。include-ignoredで差分本体を必ず実行する。内部44件、3OS品質・既存回帰、空profilesから既存workspace全体coverage80%以上を実測する。Python evidence/comparison/runnerの全実行可能行を固定3モジュール集合として80%以上確認し、追加build/native/differential/metadata/comparison_argsの5モジュールを別集合で報告する。統合実行を含め、除外pragma/omitや比較maskを追加しない。同head production wasmビルドとaube4操作の逐次wall timeを保存する。30秒guest制限・kill/reapを維持し、失敗・0件・skipを合格にしない。
- [ ] Step 15 — 132製品依存・両lock・実compiler32dba/LLVM23.1.3・flags・設定・成功job・601秒原本が一致するASan保存証拠だけを限定再利用する。新fuzzやU10のNode/Safari合格とは主張しない。署名Verified head・CI実exit・全入力・生ログ・coverage分母を結合し、4成果物・strict manifest・全60要件の独立分類による正式検査を更新して独立レビューへ渡す。新最終確認候補は構文確認までとし、人の別承認後に実行する。strict guard、80%下限、30秒制限、先行Unitの成果物を維持し、ID競合の完全解消と背景負荷完全ゼロは未検証とする。

## 承認されたWindows精度の限定修正（Steps16〜18）

Steps13〜15の初回・中間結果は履歴として保存する。詳細はverification/step14-windows-time-proposal.md。WindowsのSystemTimeは100ns単位であり、旧±1ns期待値2件の失敗を製品のmtime変換不具合と混同しない。

- [ ] Step 16 — crates/paludarium-host/src/native_fs.rsのcfg(test)内の既存mtimeテスト2件だけを修正する。Windowsでは正負1/99nsを0、100/101nsを100nsとして検査し、既存の秒・大値境界も100ns単位に合わせる。非Windowsは1ns精度の期待値と正負・大値境界を維持する。製品mtime_nsと公開型・fixtureは変更しない。修正差分を厳密に固定し、既存失敗原本・公式仕様を保存する。
- [ ] Step 17 — 修正後の同一署名headでSteps13〜14の固定guest新ビルド・限定CDLA監査・fresh Linux native14/emulator16・元argv・内部44件・3OS品質/回帰・workspace80%・Python core3全行80%と追加5別集合・production wasm・aube4時間を再確認する。全326入力・両lock・before/after/currentと原本exitを保存し、30秒・kill/reap・比較mask・分母を維持する。古い実行は修正後の成功へ読み替えない。
- [ ] Step 18 — native_fs.rsのテスト限定差分を機械的に分類し、ASanの132依存・実compiler・flags/settings・バイナリ・原本の再利用条件を再評価する。一致を証明できない対象は未検証として具体的追加案を提示する。旧先行checkerを保持し、限定差分と新CIを厳密に結合する新候補をAST検査のみで準備する。4成果物・manifest・全要件の正式検査を更新して独立レビューへ渡す。先行Unitの再確認が必要なら通常の手順で扱う。strict guard、80%下限、30秒制限を維持し、新最終確認コマンドは別承認後に実行する。

## Sources

- inception/units-generation/unit-of-work.md：U10の担当はLinux。wasm・macOS・WindowsはU11・U12・U13。
- inception/units-generation/unit-of-work-story-map.md：ユーザーストーリー工程は省略済み。FR6.1〜FR6.4、FR7.1〜FR7.4と共通NFRに対応する。
- inception/requirements-analysis/requirements.md：毎回CIでnative期待値を生成、networkなし、static-muslのみ。
- inception/contract-design/contract-summary.md：C10 SessionとC11 CLIを利用する。
- docs/u2/inventory/rebuild/build-receipt.json：aube v2.6.1、revision bd94e42f54d3b5e3dd102716b7197f316cb5f4ed の隔離ビルド実績。新ビルド成功の代用にはしない。
- formicarium/guest/probe/src/main.rs：項目の振る舞いと名称だけを参照し、自分で実装する。他プロジェクトのコードを写さない。

## Implementation Steps

- [ ] Step 1 — 既存CLI/Harness・固定ソース・probe項目一覧・#1645 fixture・CheerpX背景資料を照合する（FR6.1、FR6.4、FR7.1、FR7.3、FR7.4）。依存ライセンスとcrate取得元を確認。formicariumの8項目との一覧比較を保存し、項目変更が必要なら実装前に人へ返す。
- [ ] Step 2 — scripts/u10-run.py と tests/guests/u10/cases.json の最小runner/configを用意し、単体のrunner準備検査を実行できる状態にする（FR9.1、NFR7）。実行コマンドはunit-test-instructions.mdに固定する。nativeとemulatorの各操作に30秒の上限、子孫停止と回収を用意する。新しい全体成功をまだ主張しない。
- [ ] Step 3 — probeの8項目とaube version/install/frozen/list、node不在、#1645のケース・入力fixture・比較仕様を実装より先に定義する（FR6.1、FR7.2、FR7.3、NFR1）。環境・cwd・入力・network不在を揃え、pid/path/時刻等の変動値の正規化を明示。出力の欠落やFAILを正規化で消さない。
- [ ] Step 4 — paludarium独自のprobeを tests/guests/u10/probe/ に作る（FR6.1、FR6.2、FR6.4）。8項目の標準実行をformicariumの項目一覧に合わせ、tokio multi-thread timer、UnixStream pair、rayon4並列、Mutex/Condvar、作成/hardlink/symlink/flockを扱う。ゲストcrateはworkspace外、lock付き、static-muslでビルドする。
- [ ] Step 5 — scripts/u10-build-guests.sh と source-lock.json を作り、公式aube固定revisionを専用target/source領域でビルドする（FR7.1、NFR8、NFR9）。既存のprimer条件を調べて記録し、ソース非改変・lock・toolchain・ビルド引数・SHA256・ELF static属性・exitを保存する。ビルド不可なら停止して扱いを相談する。guest-license-change-proposal.mdの具体案に従い、webpki-root-certs@1.0.9のCDLA-Permissive-2.0だけを専用build出力のaube監査設定で許可し、CDLA全文をguest binaryのartifactへ添付する。root deny.tomlの全bytesを保持して当該1件だけを追加し、probe監査はroot設定を使う。全4監査をビルド前に実行し、root/生成設定/ライセンスhashと例外をreceiptへ記録する。成功・失敗双方で固定ソースbefore/after一致を記録し、不一致は成功にしない。source-lock、build.py、evidence.py、対応内部テスト、diagnostic workflowの保持対象を更新する。別crate・別版の一般許可はしない。
- [ ] Step 6 — 所有forkのx86-64 Linux CIでStep 3のnative期待結果を先に取る（FR9.1、NFR1）。probe8 PASS/exit0、同一aubeによる4コマンドとnode不在を観測し、#1645の0.0.0再現を確認する。出力・exit・fixture状態・時間を保存する。過去ログは履歴として保持し、期待値をリポジトリ固定にはしない。
- [ ] Step 7 — crates/paludarium-harness/tests/diff_u10.rs と support/u10.rs を実装し、C10/C11で同じguest bytesを現在のエミュレータへ渡す（FR6.3、FR7.2、FR7.3）。先にnativeで得た結果とstdout/exitを比較しstderrとguest filesystem状態を診断として保存する。default VFSへfixtureを配置し、必要なmounted fixtureも境界を限定する。
- [ ] Step 8 — 内部のビルド証拠検証・結果比較・fixture/runner管理の3部品に各7単体テストを実装後に追加し実行する（NFR1、NFR2、NFR4、NFR7、NFR8）。改ざんhash/非static ELF、FAILや欠落項目、stdout/exit不一致、変動値、timeout/cleanup、fixture汚染、network/node不在を含む。期待結果を自身の出力で作らない。
- [ ] Step 9 — 現在の製品によるプログラム差分を実機CIで実行する（FR6.3、FR7.2、FR7.3、FR9.1）。製品の不足や不一致は最小再現・担当Unit・失敗ログを記録する。成功条件を弱めず、製品修正が必要な場合は修正対象と回帰を具体化した計画を人へ提示してから進める。
- [ ] Step 10 — .github/workflows/ci.yml と u10-native-diagnostic.yml に固定ビルド・毎回のnative期待結果・U10差分・coverageを接続する（NFR3、NFR8、NFR9）。jjで対象ソースだけ署名付きcommit/pushし、3OS unit/lint/deps、U8等の既存回帰、production wasm buildの現行head一致を照合する。公開・PR作成はこの計画に含めない。
- [ ] Step 11 — バックグラウンド負荷を除いてnative/emulatorのaube4操作のwall timeを測り、CheerpX 1.3.9背景資料と条件を併記する（FR7.4、NFR6）。速さの合否下限を新設しない。Linux行coverage80%以上と既存品質下限を検査し、未測定を明示する。
- [ ] Step 12 — docs/u10/ と README、code-summary.md、source-manifest.json、traceability.jsonを確定する（全担当FR/NFR）。Linux合格と後続環境の未検証を区別し、固定head・CI・生ログ・実行コマンド・分母を添える。独立レビューと現在ソースに合う人が承認した最終確認を経てU10完了承認へ進む。

## Acceptance and Boundaries

- probeは各項目PASS、全体exit0。aube4コマンドは同一fixture状態からnativeとstdout/exitが一致する。frozenは初回install後node_modulesを除いた状態で開始し、listはfrozen後を使う。#1645はnative自体で再現を確認してから比較する。
- 固定aubeは v2.6.1 / bd94e42f54d3b5e3dd102716b7197f316cb5f4ed を既存根拠に沿って使用する。古いbinaryの歴史上のビルド由来を新ビルドで証明しない。
- native側もnetworkとnodeを利用できない同条件で走らせ、共有ホストPATHのnodeを偶然使わせない。必要ならnetwork隔離runnerを使用する。
- 内部3部品各7件、プログラム12項目を最低量とする。単体のケース数とプログラム全体のrunner数は別々に報告する。
- 80%行coverage、既存lint/依存/unsafe/timeoutの下限を維持する。重い既存fuzzは対象ソース一致が確認できる証拠のみ再利用し、不一致なら現在ソースで必要対象を実測する。新しい全入力保証はしない。
- U10固有のfunctional/NFR/infra設計ディレクトリは存在しない。新しいAC/BR番号を作らず直接FR/NFRで追跡する。DB/API/frontendは対象なし。
- 単体のrunner readinessはStep 2で確認する。完全なguest実行に必要なbuildとenvironment設定はStep 5〜6で揃え、Step 7の差分実行より先にnative完了を確認する。

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

## 今回の記録更新（Steps19〜21）

製品・既存試験・旧証拠は保持する。今回の対象はAI-DLC preview更新後のTesting Contractと承認記録の整合、および保存証拠の適用範囲の照合である。重い試験や外部送信を追加しない。

- [ ] Step 19 — 正式なrender出力でTesting Contract全体を置換し、更新後の計画承認と必要な内容確認を記録する。既存の80%下限、ゲスト30秒制限、strict guardを維持する。
- [ ] Step 20 — 現行の担当ソース・両lockと保存証拠の適用範囲を照合し、過去の実行と今回の照合を区別して記録する。正式検査と独立再レビューを行い、不足や失敗は保持する。製品修正や追加実行が必要なら具体案を提示する。
- [ ] Step 21 — 承認済みの最終確認コマンドで検証し、U10の完了承認後にU14へ戻る正式手順を進める。コマンド変更が必要なら別途承認を得る。AI-DLC本体とguardは変更しない。

## 承認された確認参照の限定修正（Steps22〜25）

旧最終確認は `validate_current_u10` が更新後の `traceability.json` を旧 `CURRENT_TRACE_SHA` と直接比較し、`Trace original digest differs` でexit1となった。失敗原本とレビュー指摘は保持する。今回の追加は検証参照の修正に限り、新しいguest・CI・coverage・ASan実行や外部送信を追加しない。

- [ ] Step 22 — 旧対応表の取得元と期待hashを旧署名済みソース・保存原本から特定する。同じ参照原因を確認候補の依存経路で監査し、旧原本の完全hash一致を必須にする。旧checkerと旧検査条件を変更せず、新helperで検証時だけ旧参照へ正しい原本を渡す。
- [ ] Step 23 — 現行U10対応表を別経路で完全hash・構造・担当要件と適用範囲へ照合する新確認候補を作る。旧／現行の取り違え、原本欠落・改変、余分な差分、hash不一致、構造・要件の欠落を拒否する正常／境界回帰を12件以上実装する。成功を仮定する置換、全体の検査省略、一般的な差分許可はしない。
- [ ] Step 24 — 回帰と既存内部44件を実行し、旧全検査を保持した新候補を診断として最後まで実行する。正式検査と独立再レビューへ渡す前に全書込みを完了し、旧実行と現行の照合を区別する。診断の成功を正式完了証明へ代用しない。
- [ ] Step 25 — 新しい最終確認コマンドを具体化して別途承認を得た後、正式再検証とU10完了承認を行い、U14へ戻る。旧記録・80%下限・guest30秒制限・strict guardを維持し、追加不一致は未解消として報告する。

## 今回の指摘対応：Step26（R-04・R-05）

ユーザーは、U10 checkpointの再確認（iteration 3、判定READY）でRequest Changesを選び、R-04とR-05への対応を指定した。再確認のきっかけは、2026-10-16のClaude Code harness追加で、ルート `.gitignore` のAI-DLCブロックに `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行が入ったことである。ルート `.gitignore` はU10のsource-manifest（42パス）に含まれない。その後、Construction Verification Commandとして `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py`（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）が人の承認で採用され、U10のcheckpointでもこのコマンドが実行される（2026-10-17の再確認時はexit 0、source_compatibility PASS、U15_acceptance GAP）。

- [ ] Step 26 — code-summary.mdの記録更新（R-04・R-05）とレビューの準備。code-summary.mdのH1の直後に「## 現行Step26：ルート.gitignoreの位置づけと正式検証コマンド」節を加え、次を記録する。(a) R-04：ルート `.gitignore` はU10のビルド、テスト、probe、aubeの入力ではない。manifestに含めない、ビルド対象外の共有パスである。2026-10-16のharness追加で上の2行が入ったことが再確認のきっかけになった。U10のmanifestにある `tests/guests/u10/.gitignore` と `tests/guests/u10/probe/.gitignore` は変わっていない。(b) R-05：checkpointで実行する正式コマンドは採用済みの `final_candidate.py`（上のSHA-256）である。「最終候補」節の `verify-current-u1-u7-u9-u3-u5-u6-u8-u10.py` は、採用前の候補として履歴に残す（構文確認のみで未実行のまま）。その実行結果を今回の成功とは扱わない。既存の節の本文は変えない。ただし「最終候補」節の段落の先頭に「（履歴：採用前の候補。現行の正式コマンドは現行Step26節を参照）」を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む。新しいguest実行・CI・Node／Safari・ASanやU15の受理は主張しない（NFR8、NFR9、全担当FR/NFR）。

## 今回の指摘対応：Step27（R-06・R-07）

ユーザーはStep26後のU10 checkpointでRequest Changesを選び、R-06とR-07への対応を指定した。正式コマンドの実行記録は、checkpointの証拠ファイル `aidlc/spaces/default/intents/261004-rust-blink-port/.aidlc-construction-checkpoints/u10-probe-aube-native/unit.json` と、各実行の出力ディレクトリ（U1 verification `r05-r11-repair-01/formal-candidate-<id>/`）に残っている。2026-10-17の再確認（iteration 3の後）の出力は `formal-candidate-1792186532618870000-51059`、Step26の後の出力は `formal-candidate-1792187027222463000-56058` で、どちらもexit 0、source_compatibility PASS、U15_acceptance GAPである。

- [ ] Step 27 — code-summary.mdの構成と参照の修正（R-06・R-07）。(1) R-06：「現行Step26」節の後に続く、見出しのない導入段落3つ（「今回追加したSteps22〜25では…」「今回の対象はSteps19〜21の記録更新です…」「検証済み：42担当パスに欠落なし…」）の直前に、`## 概要（Steps19〜25の履歴）` というH2を1つ加える。段落の本文は変えない。(2) R-07：「現行Step26」節のR-05の項目にある「2026-10-17の再確認ではexit 0、source_compatibility PASS、U15_acceptance GAPでした。」の直後に、実行記録の参照（checkpoint証拠ファイル `.aidlc-construction-checkpoints/u10-probe-aube-native/unit.json` と、出力ディレクトリ `construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792186532618870000-51059/`）を1文で添える。証拠ファイルには最新の実行が記録され、今後の再検証で更新されることも書く。その他の文と節は変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR8、NFR9）。

## 今回の指摘対応：Step28（R-08）

ユーザーはStep27後のU10 checkpointでRequest Changesを選び、R-08への対応を指定した。出力ディレクトリ `formal-candidate-1792186532618870000-51059/` には `result.json`（`"source_compatibility": "PASS"`、`"head": "be45b36ce9d7a65719ba1f86cf6a0b018070741b"`）と、各検査の `*.receipt.json`・`*.result.json` がある。exit 0 そのものは、エンジンの検証記録（checkpointの証拠ファイル）に残る。

- [ ] Step 28 — 裏付けファイルの明示（R-08）。code-summary.mdの「現行Step26」節のR-05の項目で、Step27で足した参照文の出力ディレクトリの部分を、ディレクトリ内の `result.json`（`source_compatibility` が `PASS`、`head` が be45b36c）を指す形にする。あわせて、終了コード0はcheckpointの検証記録に、判定は `result.json` にあることを分けて書く。その他の文と節は変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR8、NFR9）。

## 今回の指摘対応：Step29（R-09）

ユーザーはStep28後のU10 checkpointでRequest Changesを選び、R-09への対応を指定した。正式コマンドは実行のたびに、U1 verification `r05-r11-repair-01/` の下に新しい `formal-candidate-<id>/` を作る。checkpointの証拠ファイル `unit.json` は最新の実行だけを記録し、その出力先は `verification.stdout_tail` の `output` に書かれる。そのため、特定の「最新」ディレクトリ名を文書に書いても、次の再検証でずれる。

- [ ] Step 29 — 参照の対応関係の明記（R-09）。code-summary.mdの「現行Step26」節のR-05の項目で、Step28の参照文の直後に1文を足す。足す内容は次のとおり。51059は2026-10-17の再確認（iteration 3の後）の初回の実行である。正式コマンドは実行ごとに新しい出力ディレクトリを作る。checkpointの最新の実行の出力先と判定は、`unit.json` の `verification.stdout_tail` に記録される。どの実行も、同じ採用済みコマンド（SHA-256 `d799bbb9…`）で、同じ判定項目（source_compatibility、U15_acceptance）を出す。特定の最新ディレクトリ名は書かない。その他の文と節は変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR8、NFR9）。


