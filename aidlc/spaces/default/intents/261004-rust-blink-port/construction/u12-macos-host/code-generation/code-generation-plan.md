# U12 macOS Host — Code Generation Plan

## Summary

- Builds: Step13〜15。U12が担当するファイルが、Steps11〜12の修正を含むBuild and Testの版（head e4f84768）から変わっていないことを確かめ、今の正式確認コマンドで確かめ直す。checkpointでの人のRequest Changesにより、レビューのMinor（code-summary.mdが古いまま）をStep14で直し、その再レビューの新しいMinor 2件（履歴の節の下に残る「現行」の見出し、末尾の括弧書きのかかる範囲）を、2回目のRequest ChangesによりStep15で直す。製品・workflow・source-manifest.json・traceability.jsonは変えない。
- Touches: この計画と手順書のStep13〜15の節、code-summary.mdの冒頭の新しい節と、既存の見出し2つ・文1つへの履歴の表示だけ。
- Tests: 新しいテスト・CIの実行はない。U12のsource-manifestの全ファイルがe4f84768と同じことを読み取りで確かめ、独立再レビューと、今の正式確認コマンド（U11の `u11_candidate_v2.py`、hash付き）でのcheckpointを行う。

## 今回の計画：Step13〜15（Build and TestのLoop-back 1：変更がないことの再確認と、要約の更新）

2026-10-18。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）、U11のSafariの待ち時間の修正（2b8723ab・57a8c96f）、U1・U2・U11の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。これらで変わったのは、U14のJIT・wasm・テスト、U11の `packages/paludarium-wasm/tests/u11-browser-driver.mjs`・`.test.mjs`、`mise.toml` で、U12のsource-manifestのファイルは含まれない。U12のmacOSの品質（u12-quality）は、1ceae86c（run 39028303336）・2b8723ab（39044793102）・57a8c96f（39073501121）でいずれも成功した。正式確認コマンドは、人の承認でU11の `verification/loopback1-next/u11_candidate_v2.py`（`--entry-sha256`・`--binding-sha256` 付き）になっている。

- [ ] Step 13 — U12のsource-manifestの全ファイルについて、作業コピーが e4f84768 と同じであることを読み取りで確かめる（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <paths>`）。違いがあれば止めて報告する。記録は変えない。独立再レビューのあと、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。
- [ ] Step 14 — code-summary.mdを今に合わせる（レビューのMinor、人のRequest Changes）。冒頭に「現行Step13〜14」節を足し、(a) Step13のgit diffがexit 0だったこと、(b) Steps11〜12の「未確認」はその時点の記述で、その後u12-qualityが1ceae86c（run 39028303336）・2b8723ab（39044793102）・57a8c96f（39073501121、差分テストのjobだけ再実行した2回目で成功）で成功したこと、(c) 末尾の節の `verify-current-u12-macos-host.py` は採用前の候補で、今の正式確認コマンドはU11の `u11_candidate_v2.py`（hash付き）であること、(d) 今の正式確認コマンドでのcheckpointの検証がexit 0だったこと、を書く。既存の「現行Steps11〜12」の見出しを「履歴：Steps11〜12（作成時の見出しは「現行Steps11〜12」）」に変え、末尾の最終candidateの文の前に「（履歴：採用前の候補。現行の正式コマンドは先頭の「現行Step13〜14」節を参照）」を足す。他の本文は変えない。そのあと正式sensorを実行し、独立再レビューを受け、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。
- [ ] Step 15 — Step14の再レビューの新しいMinor 2件を直す（人の2回目のRequest Changes）。(1) code-summary.mdの「## 現行検証と再実行」の見出しを「## 履歴：検証と再実行（作成時の見出しは「現行検証と再実行」）」に変える。(2) 末尾の括弧書きを「（履歴：この段落はStep10時点の記述で、次に挙げる `verify-current-u12-macos-host.py` は採用前の候補である。現行の正式コマンドは先頭の「現行Step13〜15」節を参照）」に変える。(3) 冒頭の節の見出しを「現行Step13〜15」に変え、最後の「下の節は、それぞれの時点の履歴として読む。」を「下の節は、それぞれの時点の履歴として読む。下の節の本文にある「現行」は、その節を書いた時点の現行を指す。」に変え、Step15で直したことを1項目足す。他の本文は変えない。そのあと正式sensorを実行し、独立再レビューを受け、今の正式確認コマンドでcheckpointを検証し、人の承認を受ける（NFR3、NFR8）。

## 前回のSummary（Steps11〜12）

- Builds: Build and Testからの差し戻し（人の指示）。U12のworkflow 2つを直す：`u12-native-first.yml` のゲストビルドを `--advisory-policy u15-fixed-aube-zip9-name` 付きに揃え（ce0b746と同じ形）、`u12-quality.yml` のenvに `PALUDARIUM_TEST_NODE: node` を足す。U9で直した共有workflow（ci.yml・u10-native-diagnostic.yml・u11-acceptance.yml）も含めて再レビューを受ける。
- Touches: `.github/workflows/u12-native-first.yml`（49行目）と `.github/workflows/u12-quality.yml`（workflowのenv）だけ。製品source、試験、スクリプト、source-manifest.json（2ファイルは記載済み）、他Unitの記録は変えない。push・CI起動はこの段階では行わない（Build and Testで人の承認を得てから）。
- Tests: 新規テストなし。actionlint（shellcheck 0.11.0を明示）で2ファイルを検査する。CIでの実行はBuild and Testで承認後に行う。正式sensor、独立再レビュー、正式コマンドでのcheckpoint再検証を行う。

## 今回の差し戻し対応：Steps11〜12（workflowの修正）

Build and Testの準備中に、人が次を指示した：「fork の branch codex/u15-macos-native（commit ce0b746）で、u12-native-first.yml のゲストビルドを --advisory-policy u15-fixed-aube-zip9-name に揃えました。同じ問題は u11-acceptance.yml・u10-native-diagnostic.yml（policy の指定なし）と u12-quality.yml（PALUDARIUM_TEST_NODE なし）にもあります。…手元への反映は、影響する Unit（U9〜U12）の再レビューを含めて正規の手順で進め、push と CI の前には承認を求めてください。」根拠はU15の `verification/u12-quality-38994430947/README.md`（run 38994430947：u12-native-first.yml 49行目のゲストビルドで aube の `cargo deny` が exit 1、u12-quality.yml に `PALUDARIUM_TEST_NODE` がなくJITの実Wasm試験9件とdiff_u14がpanic、そのため `macos-host` jobはskipped）。u11-acceptance.yml・u10-native-diagnostic.yml・ci.ymlはU9（Steps77〜79）で直し、承認済み。

- [ ] Step 11 — workflowの修正（FR6.3、FR7.2、FR7.3、NFR3）。(1) `.github/workflows/u12-native-first.yml` 49行目の `bash scripts/u10-build-guests.sh target/guests/u10 2>&1 | tee target/u12-native-first/build.log` を、ce0b746と同じ `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name 2>&1 | tee target/u12-native-first/build.log` に置き換える（このjobには setup-python 3.15.0 がすでにある）。(2) `.github/workflows/u12-quality.yml` のworkflowの `env` に、`u14-quality.yml` 21行目と同じ `PALUDARIUM_TEST_NODE: node` を1行足す。他の行・閾値・SHA固定・権限は変えない。
- [ ] Step 12 — 確認と記録。actionlintで2ファイルを検査する。code-summary.mdの冒頭に「現行Steps11〜12」節を加え、変更した2行と根拠、確認の結果、CIでの実行はまだで（Build and Testで人の承認後に行う）未確認であることを書く。traceability.jsonは分類・targetを変えず、FR6.3のnotesに今回の修正の参照を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## Scope and Current Evidence

根拠：unit-of-work.md U12、story-map FR5.1／FR6.3／FR7.2／FR7.3／FR9.1、contract-summary C2、requirements NFR1〜4・NFR7〜9。ユーザーストーリー工程は省略されているためFRを各Stepへ対応させる。

検証済み（ソース読み取り）：NativeHostのstdio/random、clock.rs、threads.rs、capabilityベースnative_fs.rsは既にnative共通実装。lib.rsのterminal_infoはLinux x86-64だけに実装され、macOSでは常にNoneを返す。Darwinの端末構造体とLinux guestのTerminalAttributesは同一ABIではない。macOS実guest・PTYの今回の動作は未検証。既存のLinux／wasm成功をmacOS成功へ読み替えない。U12固有のfunctional/NFR/infrastructure文書は存在しない。

既存Host traitと公開TerminalInfo constructor、固定probe/aube・CDLA限定条件、VFSの既定隔離とC10を保持する。Windows固有機能・JIT・公開は後続Unitへ残す。不要なHost全面書換えはしない。

## Implementation Steps

更新後の実行順：Step1で最新tool統一、Step8のfresh Linux期待値取得をStep2の期待先へ組み込み、Steps2〜6でmacOSを実装検査する。Steps8〜9の最終source検証を完了してStep7／10の正式sensor・レビューへ進む。Step7で検証前のレビューは行わない。

Step1の具体的更新：Rust製品pin・固定guest source-lockのtoolchain・scripts/build-wasm.sh・通常ci.ymlと呼び出すu11-acceptance.yml／u11-fuzz.yml／u10-native-diagnostic.yml、新U12診断CIをnightly-2026-10-11へ統一する。固定guest revision・lock・license条件は保持。公式確認済みPython3.15.0／coverage7.16.2／llvm-cov0.9.1／deny0.20.2／fuzz0.13.2と最新Actions SHAを使用し実cargo／RUSTC／RUSTDOCを保存。歴史用診断workflowと旧検証原本は更新せず保持する。

- [ ] Step 1 — 現行source・両lock・Rust pin・Host/C2接続と既存U4/U5/U7/U9テストを棚卸しする。最新Rust・Python・coverage・依存監査・Actions版を公式配布情報で確認し、使用版／実体／更新理由を記録する。必要な更新はU12に必要な範囲だけ設定とlockへ反映し、広い更新が必要なら具体化して人へ提示する。（FR5.1、NFR8、NFR9）
- [ ] Step 2 — 実行前runner readinessを既存U10 self-testとHost限定テスト入口で確認し、U12専用入口・CI土台を作る。Linux x86-64で固定guestをビルドし、ネットワーク隔離されたfresh nativeの14ケース以上を先に観測する。guest hash、fixture0644、argv／env／stdout／stderr／exit／状態／時間を保存し、macOS比較の期待結果を固定する。（FR6.3、FR7.2、FR7.3、FR9.1）
- [ ] Step 3 — DarwinのPTY／非端末挙動を先に観測する。Linux guestが必要とする端末属性・サイズの対応を明示し、lib.rsのmacOS分岐と専用macos.rsへ最小接続を実装する。Darwin errno／termiosをそのままguestへ渡さず、host-ownedバッファのみ扱う。既存portable時計・待機・FSは保持し、再現した不足だけ最小修正する。（FR5.1、C2、NFR3、NFR4）
- [ ] Step 4 — 実装後に内部層のU12限定テストを書く。portable時刻／thread／I/O境界7件、FS／errno／隔離境界7件、Darwin端末変換7件を最低数として、各名前・実行数・ignored0を保存する。実PTY統合7件で非端末、属性、正サイズ、ゼロサイズ、stderr別stream、エラー、資源解放を検査する。未知のflag対応は無言で捨てず根拠と範囲を示す。（FR5.1、NFR2〜4、NFR7）
- [ ] Step 5 — 同じ未改変static-musl x86-64 guestをmacOS native emulatorで実行しfresh Linux14ケース以上と比較する。probe8項目＋all／node不在、aube4操作・#1645・元argvを保持する。default VFSとhost mountのfixture隔離、負mtime、symlink escape／flockのmacOS境界も検査する。各guest30秒・timeoutなし・cleanup・実exitを要求し、macOS上のLinux ELF直接実行やRosettaをnative oracleに代用しない。（FR6.3、FR7.2、FR7.3、NFR1、NFR4、NFR7）
- [ ] Step 6 — macOS実機CIでU12限定実行とcoverageを取得する。測定対象はHost native実行経路 lib.rs／clock.rs／threads.rs／native_fs.rs／fs.rs／新macos.rs（テスト専用・wasm専用は対象外を事前明記）、総実行可能行の80%以上を維持する。Python U12比較部品も80%以上。3OSの既存Host／U5／U7／U9回帰・fmt／Clippy／依存4監査をCIで確認する。共有Rust変更があればproduction wasm／Node／本物Safari回帰も同じsourceで確認し、ASanは依存・compiler・設定・binary一致で限定再利用、不一致対象は600秒再検証する。（NFR2、NFR3、NFR8、NFR9）
- [ ] Step 7 — 全入力・両lock・実compiler・署名head・CI job／attempt・原本ログ／exit／before-after sourceを結合し、source-manifest・code-summary・traceabilityを作る。未検証／失敗／旧証拠を区別し、正式sensorと独立レビューへ渡す。新最終確認scriptは既存全検査を保持してU12を追加し、正式実行前にコマンドの承認を受ける。（FR9.1、NFR1〜9）

## Test Configuration and Change Boundaries

- [ ] Step 8 — 更新compilerでfresh Linux期待値をguest動作実装前に取得し、最終署名sourceでLinux既存差分・workspace coverage80%以上・3OS品質とproduction wasmを再検証する。同一固定guest/moduleをNode／Chromium／Firefox／本物Safari各14ケース以上でfresh Linuxと比較する。C12・既存Rust／JS coverage80%・元argv・mask・分母を維持し、失敗と再実行attemptを保存する。（FR5.1、FR5.3、FR6.3、FR7.2、FR9.1、NFR1、NFR3、NFR9）
- [ ] Step 9 — 同じ最終署名sourceと最新compilerで11対象cpu_u2／mmu_u2／decode／load_elf／mmu_ops／syscall_args／vfs_paths／kernel_threads_u5／kernel_futex_u5／kernel_events_u6／kernel_sockets_u6を各600秒ASan／LSan実行する。cpu最大4096・mmu最大4608・入力30秒・既存抑制原本とsymbolizer条件を維持し、依存／両lock／compiler／binary／設定／原本／実exit／開始終了を保存する。旧compilerの保存結果は今回の代用にしない。（NFR2、NFR3、NFR7、NFR9）
- [ ] Step 10 — Step8〜9を含む全入力と署名head・CI全job／attemptを結合し、旧329入力とU11 baselineの厳密bridgeで旧全検査を保持する新canonicalを作る。正式sensor・独立レビューへ引渡し、新確認コマンドを人が承認した後に正式実行する。未検証・失敗・旧履歴を区別する。（FR9.1、NFR1〜9）

旧承認7手順は上記Steps1〜7の履歴として保持した。人の「更新と追加検証を承認」により、toolchain統一と追加Steps8〜10が現在の検査範囲となる。Step6の旧ASan条件再利用方針よりStep9の新11対象実行を優先し、compiler不一致を例外で隠さない。

追加候補：crates/paludarium-host/src/macos.rs、src/u12_tests.rs、tests/u12_public_api.rs、tests/guests/u12/、scripts/u12-run.py、.github/scripts/u12-current-diagnostic.py、.github/workflows/u12-current-verification.yml。lib.rs／Cargo.toml／Cargo.lockは接続・必要なDarwin依存だけ。テストのfilter／coverage分母／deadlineは定義して固定し、skipや0件を成功扱いしない。既存のU11完成記録と全finished Unitは保持する。

## Open Validation Limits

Darwin端末flagとLinux guestの対応、既存native_fsのmacOS errno境界、実機の処理時間、Host限定80%の到達、CI push権限は未検証。再現結果が計画範囲を超える場合は原因・最小差分・追加検証を具体化して人へ返す。現時点では計画だけであり製品変更・テスト実行・pushを行っていない。

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

