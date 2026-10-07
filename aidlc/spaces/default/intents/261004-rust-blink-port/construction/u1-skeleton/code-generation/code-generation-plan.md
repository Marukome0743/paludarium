# コード生成の計画（u1-skeleton）

## 目的と範囲

U1 は、ネイティブの Linux で C と Rust の static-musl の hello world を最初から最後まで動かす細い一本です。合わせて、wasm のスレッドの確認を行います。

上流の成果物：
- `construction/u1-skeleton/functional-design/`（functional-spec.md・rules.md・entities.md）
- `construction/u1-skeleton/nfr-requirements/`（security-requirements.md・tech-stack-decisions.md）
- `inception/contract-design/contract-summary.md`（C1〜C11）
- `inception/units-generation/unit-of-work.md`（U1）

アプリケーションのコードはワークスペースの直下（`crates/` など）に置きます。記録のディレクトリには置きません。

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
  "input_sha256": "sha256:91ac3bd1188729834852fc936b408ee9ac202c44ab57bd4c296ebc553931bd12",
  "contract_sha256": "sha256:99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616"
}
```

## 手順

各手順の括弧内は、対応する要件・ルールです。

### Step 1：ワークスペースの土台

- [x] ルートの `Cargo.toml` に Cargo のワークスペースを作り、次のクレートを `crates/` の下に置く：`paludarium-types`、`paludarium-decoder`、`paludarium-mmu`、`paludarium-cpu`、`paludarium-loader`、`paludarium-vfs`、`paludarium-kernel`、`paludarium-host`、`paludarium-jit`、`paludarium-runtime`、`paludarium`（まとめ役とコマンド）、`paludarium-harness`（公開しない）（tech-stack-decisions）
- [x] `rust-toolchain.toml` で nightly を日付まで固定し、rustfmt・clippy・llvm-tools と、x86_64-unknown-linux-musl・wasm32-unknown-unknown を入れる（NFR9.1）
- [x] `[workspace.lints]` に clippy の設定を置く：`unwrap_used`・`expect_used`・`panic`・`undocumented_unsafe_blocks` を deny、`unsafe_op_in_unsafe_fn` を deny。各クレートは `[lints] workspace = true`。Host 以外のクレートに `#![forbid(unsafe_code)]`（NFR2.3、NFR3.1、NFR3.2）
- [x] `deny.toml`：ライセンスの許可の一覧、取得元は crates.io だけ、RustSec、禁止の一覧（webix・portabox・lanmower/blink の系列）（NFR8.1、NFR8.4）
- [x] `Cargo.lock` をコミットする前提で `.gitignore` を整える（NFR8.3）

### Step 2：テストの実行の準備

- [x] 各クレートに空のテストを 1 つ置き、`unit-test-instructions.md` の U1 のコマンドが通ることを確かめる
- [x] ネイティブの x86-64 Linux の実行環境を用意する。手元（Windows）では Linux のコンテナ（wslc。だめなら Docker Desktop）を使い、CI では ubuntu のランナーを使う。コンテナには musl-tools・binutils（objdump）・strace を入れる

### Step 3：差分テストの仕組みとゲスト（期待結果を先に用意する）

- [x] `paludarium-harness` に差分テストの仕組みを作る：x86-64 Linux でゲストを直接動かして標準出力・標準エラー・終了状態を記録し、エミュレータでの結果とバイト単位で比べる。1 件あたり 30 秒の時間切れを付ける（BR7.1、NFR1.1、NFR7.1）
- [x] ゲストを置く：`tests/guests/hello-c/hello.c`（write と exit だけ）と `tests/guests/hello-rs/`（`println!`）。CI と手元のコンテナで、musl と x86_64-unknown-linux-musl でビルドするスクリプトを置く（BR7.2）
- [x] 2 つのゲストの ELF の種類（ET_EXEC か ET_DYN）を確かめて記録する（BR1.4）
- [x] 2 つのゲストを strace で動かし、呼ばれる syscall の一覧を確かめる。BR3.3 の一覧と違えば、違いを `code-summary.md` に記録し、実装する一覧を直す（BR3.3）
- [x] 2 つのゲストを逆アセンブルし、実行される命令の一覧（SSE 系を含む）を作る（BR4.4、W7）
- [x] 命令ごとの差分テスト：命令をインラインアセンブリで実行してレジスタとフラグを出力する小さなゲスト（C）を、命令の一覧の分だけ用意する。未定義のフラグは出力から外し、外したものを表で持つ（NFR1.2）

### Step 4：共通の型（paludarium-types）

- [x] GuestAddr（ホストの整数との変換は検査付き）、Errno、ExitReason（syscall・page-fault・invalid-opcode・halt・budget-exhausted）、ExitStatus、Error を作る（C1、BR2.1）
- [x] 単体テスト（5〜8 件）

### Step 5：デコーダ（paludarium-decoder）

- [x] iced-x86 と yaxpeax-x86 の両方で包みを試作し、Step 3 の命令の一覧がデコードでき、wasm32 でビルドできるかを比べて 1 つを選ぶ。結果と理由を `code-summary.md` に記録する（tech-stack-decisions の Q1）
- [x] 選んだ crate を包む `decode(bytes, rip)` を作り、crate の型は外に出さない。範囲外の命令は Unsupported を返す（C3、ADR-006）
- [x] 単体テスト（5〜8 件）

### Step 6：Mmu（paludarium-mmu）

- [x] 4 KiB ページの 2 段のページテーブル（上は疎な表、下は 512 ページ分）で AddressSpace を作る。read・write・fetch・map・unmap・protect・set_break（C4、BR2.1〜BR2.3）
- [x] 範囲外・権限違反はフォールトを返し、panic しない（BR2.2、NFR2.1、NFR4.4）
- [x] 単体テスト（5〜8 件）

### Step 7：Cpu（paludarium-cpu）

- [x] CpuState（汎用レジスタ・rip・rflags・fs/gs のベース・xmm0〜15・mxcsr）と `run(state, mem, budget)` を作る（C5、entities.md の CpuState）
- [x] Step 3 の命令の一覧の命令を実装する。syscall 命令は rcx・r11 を設定して止まる。一覧にない命令は invalid-opcode（BR4.1、BR4.2、BR4.4）
- [x] 予算を使い切ったら budget-exhausted で止まる（BR4.3）
- [x] Step 3 の命令ごとの差分テストが通ることを確かめる。内部の部品の単体テスト（5〜8 件）を書く

### Step 8：Loader（paludarium-loader）

- [x] ELF の検査（x86-64・64 bit・リトルエンディアン・ET_EXEC か ET_DYN・PT_INTERP なし）、セグメントの配置、bss の 0 埋め、static-pie の基準アドレス 0x555555554000（BR1.1、BR1.2、BR1.4）
- [x] PT_LOAD の合計の大きさが 4 GiB を超える ELF は invalid-program にする（非機能要件のレビュー R-01 への対策。細工した ELF でホストのメモリを使い切らないため）
- [x] 最初のスタックと補助ベクタ（BR1.3）。AT_RANDOM は Host の乱数から取る
- [x] 単体テスト（5〜8 件）

### Step 9：Vfs（paludarium-vfs）

- [x] U1 の最小限：起動前にファイルを置き、パスで読めるようにする（C6、FR3.4 の先行）
- [x] 単体テスト（5 件）

### Step 10：Kernel（paludarium-kernel）

- [x] syscall の振り分け表と、表にない番号の -ENOSYS（BR3.1、BR3.2、NFR4.1）
- [x] Step 3 で確かめた一覧の syscall を実装する（BR3.3、BR3.4、BR2.3、BR5.1）。シグナルは登録だけで配送しない（BR4.5）
- [x] Cpu の止まった理由への応答：page-fault は SIGSEGV、invalid-opcode は SIGILL、halt は SIGSEGV で終わらせる
- [x] 単体テスト（5〜8 件）

### Step 11：Host（paludarium-host）

- [x] Host の trait（C2 の U1 の範囲と、乱数の口）と、std を使うネイティブの実装（標準入出力、乱数）。3 つの OS でビルドとテストが通る形にする（BR6.1）
- [x] 単体テスト（5 件）

### Step 12：Jit の口、Runtime、コマンド

- [x] `paludarium-jit`：何もしない CodeCache（C9）
- [x] `paludarium-runtime`：Session と、スレッドの実行ループ（W3）。kill の要求を予算の区切りで確かめる（BR4.3）
- [x] `paludarium`：公開 API の再公開と、コマンド `paludarium [options] <program> [args...]`。`--env` を受け付け、`--no-jit` は受け付けて何もしない（ネイティブには JIT がない）。`--mount` と知らないオプションは終了コード 2。プログラムはゲストの `/<ファイル名>` に置き、argv[0] は指定した文字列。終了コードはゲストの値、128 + シグナル、エミュレータのエラーは 70（BR5.2〜BR5.4、C11）
- [x] 単体テスト（各 5〜8 件）

### Step 13：結合（細い一本の確認）

- [x] Step 3 の差分テストで、C と Rust の hello world がネイティブと一致することを確かめる（NFR1.1）
- [x] 実行時間を記録する（NFR6.1）

### Step 14：ファジング

- [x] `fuzz/` に cargo-fuzz の対象を作る：デコーダの包み、ELF の読み込み、Mmu の操作の並び、syscall の引数（非機能要件のレビュー R-02 への対策）（NFR2.2）
- [x] 手元のコンテナで、各対象を短く動かして panic がないことを確かめる

### Step 15：CI

- [x] `.github/workflows/ci.yml`：3 つの OS でビルドと単体テスト、fmt、clippy（`-D warnings`）、cargo-deny、ubuntu で差分テストと cargo-llvm-cov（行カバレッジ 80% 未満で失敗）。action は SHA で固定し、既定の権限は読み取りだけ（NFR3.3、NFR8.1〜NFR8.3、team.md の Testing Posture）
- [x] `.github/workflows/nightly.yml`：ファジング（対象ごとに 10 分）と wasm のスレッドの確認（NFR2.2、BR8.1）

### Step 16：wasm のスレッドの確認

- [x] `spikes/wasm-threads/`：2 つの Worker が SharedArrayBuffer を共有し、片方が待ち、もう片方が書いて起こす確認用のプログラム（Rust の wasm32 に atomics などを付けたビルド）と、JS（BR8.1）
- [x] Node.js での確認スクリプト、COOP/COEP の見出しを付けて配る小さな配信のスクリプト、ブラウザの自動操作（Chromium 系・Firefox は自動操作の道具、Safari は safaridriver）
- [x] 結果の報告 `docs/reports/wasm-threads.md`：環境ごとの合否と版、Worker を作るのは Host の wasm 用の実装と起動用 JS のどちらが妥当か、その理由、必要なツールチェーンの設定（BR8.2）。手元で動かせない環境（Safari など）は nightly の CI の結果で埋める

### Step 17：文書と対応表

- [x] README に、ビルドと実行の手順、差分テストの動かし方、U1 の状態を書く
- [x] `code-summary.md`、`source-manifest.json`、`traceability.json` を作る

## 申し送り（前の工程のレビューの残り）

- 機能設計のレビュー R-09（C1・C2 への追加を contract-summary.md に反映していない）：コードでは追加を実装し、`code-summary.md` に、取り決めへの追加として記録する
- 機能設計のレビュー R-10（`--no-jit` を U1 で受け付けるか）：受け付けて何もしない（Step 12）
- 非機能要件のレビュー R-01・R-02：Step 8 と Step 14 で扱う


## 現在の共有sourceに対するU1確認

今回の再開始では、下記Step 21〜25を実行する。追加のStep 24aは3OS検証で見つかったHostの限定修復であり、新しい承認後に実行する。Step 18〜20も過去の確認履歴であり、現在の合格証拠ではない。U2のREP回帰とU4/U7のゲストビルドは、発見した失敗を直すための限定した関連修正として扱う。

Step1〜17の[x]は先行実装の履歴であり、今回の承認や最新sourceの検証完了を示さない。今回の対象は既存U1実装とU1が所有するshared sourceの再確認・文書整合である。後続U2の独立source/test/docは作り直さず、そのsourceをU1 manifestへ追加しない。記録済み機能回答・Testing Contract・80%下限・30秒watchdog・nightly pinを維持する。

### Step 18：既存実装・回答・証拠の現在値を照合する

- [x] U1の既存source-manifest claims、C1〜C11利用側、writeのゼロ/部分結果回帰と既存命令census66件の対応を確認する。U2で共有sourceに加えられたArithmeticFault、typed atomics/common MMU synchronization、FS/GS linear addressを現在の共通sourceとして説明し、U1追加実装の成果とは数えない（BR3.4、BR4.1〜BR4.4、NFR1.1〜1.2）。
- [x] 最新sourceの保存済み検証（docs/u2/repairs/r01-workspace-coverage.txt、同fuzzとcargo-deny）からU1 diff16・Kernel write回帰・全workspace197件/94.00%を照合する。先行102件/87.11%と最新の分母を区別する。production変更がなければ同じ検証を反復しない（NFR3.3、NFR8.1）。

### Step 19：不足するU1確認のみ回収する

- [x] 証拠が不足または新規source修正が必要な場合だけunit-test-instructionsのexact U1 testsを実行する。命令/syscall修正はnative expectationまたは有限mockのRed先行→修正→Green、内部layerテストは実装後のcustom順序を保持する。未検証wasm環境、U1 fuzz各target、decoder候補比較の歴史的記録は不足を明記し、合格を推定しない（BR8.1〜8.2、BR9.1、NFR2.2）。

### Step 20：現在値と履歴を区別して成果物を確定する

- [x] U1 code-summary/traceability/source-manifestと必要なU1説明文だけを整合させる。build/cacheを除き、shell/scaffolding/generatorが書いたU1 application-sourceを全て列挙する。独立reviewへ渡し、記録済み回答から今回の承認を捏造しない（全BR/詳細NFR）。

### Step 21：修復用runnerと現在の失敗を固定する

- [x] Docker VMMと固定nightlyを維持し、scripts/linux-dev.shのstack無制限設定によるcompiler起動・image構築の修復を確認する。forkのUbuntu/Bookworm実機CIと手元Dockerのログを区別し、CPU・musl・ゲスト命令列を記録する。古い197件/94.00%を現在の合格証拠として引用しない（NFR1.1、NFR3.3）。

### Step 22：hello-cに必要なSSE命令を修復する

- [x] MOVQ/PUNPCKLQDQの非対称64bit値、上位64bitの扱い、自己参照をnative差分ゲストに追加し、実機期待結果と現実装の失敗を先に確認する。デコーダとCPUに必要なlegacy XMM形式を実装し、その後内部単体テストを追加する。hello-cでさらに不足が判明した場合も、命令censusとnative期待結果を先に確定して必要最小限の命令だけ扱う（BR4.4、NFR1.2）。

### Step 23：REPとゲストビルドの失敗を修復する

- [x] 実機でも失敗したREP4ケースについて、初期flags、ページ準備、fault/restart、CPU差を観測し、公式仕様と照合する。期待結果を先に確定し、原因が観測コードならゲスト、CPU意味論なら共有CPUだけを修正する。定義済みflagsのmaskを外して合格させない（NFR1.1〜1.2）。
- [x] tests/guests/u4/build.shとu7/build.shの混在CRLFをLFへ修正し、native Linuxで構文検査・ゲスト生成と関係する差分テストを確認する。他unitの機能追加や再実装は行わない。

### Step 24：修復後の検証

- [x] unit-test-instructionsの関係する限定コマンドをDocker VMMと実機Linuxで実行する。ENTER/ALUのDocker固有差は実機結果と区別し、30秒watchdogは維持する。更新したfork CIで既存suiteを確認し、fmt/clippy・依存検査・native行coverage80%以上を確認する。未通過項目は未検証または失敗として残し、nightlyを変更しない。

### Step 24a：3 OS検証で判明したHostの限定修復（追加承認対象）

- [x] macOS/Windowsのnative_fs::u7_testsを実装前に実行し、lock競合のOS errno35/33とLinux guest EAGAIN11の不一致、Windows hardlink links1対2、fixture終了時OS error32を保存する。OS番号をguestへ直接流す経路を修正し、同じguestエラーを返す回帰を確認する。無関係なHost APIの改善は加えない。
- [x] WindowsのFileStatリンク数を実際のmetadataから取得する。test fixtureは保持したNativeFs/関連handleを解放してから一時ディレクトリを削除し、cleanupのpanicで実際のテスト結果を隠さない。cleanup失敗を無視して合格させず、root外アクセス防止と既存lock/link/I/Oテストを保持する。
- [x] native_fs.rsと必要最小限のHostテスト・metadata/error変換だけを追加修復範囲とする。内部layerの順序はTesting Contractのtest-afterとし、既存失敗の再現ログを先に記録する。3OS Host回帰、3OS既存suite、Intel/AMD native差分、lint/依存、全体とU1限定coverage80%以上を確認し、manifest/traceabilityを追加した実ファイルへ更新する。

### Step 24b：Windows Runtimeマウントテストのcleanup（追加承認対象）

- [x] crates/paludarium-runtime/src/tests.rsのu7_runtime_mountだけで、remove_dir_allの直前にdrop(fs)とdrop(s)を追加する。両方が保持するmount root handleを解放してから削除し、cleanup失敗は引き続きunwrapで失敗させる。production Runtimeやmount機能は変更しない。Windows CIのOS error32ログを修正前の根拠として保持する。
- [x] Runtimeの当該テストとlibテスト、fmt/clippy、3OS既存suite、実機Linux差分、全体/U1 coverage80%以上を確認する。関連テストファイルは既存manifest claim内。30秒watchdog、nightly固定版、比較mask、2フックを保持する。

### Step 24c：Windows VFS共通fixtureの同種cleanup修復

- [x] crates/paludarium-vfs/src/mount.rsのtest専用Fixtureだけで、保持するMountedFsを空のMountedFsへreplaceしてdropし、root handleを解放してから既存remove_dir_allを実行する。production、mount意味論、assertion、cleanup errorのunwrapを保持する。WindowsのRuntime25件通過後に共通Drop:366で16件がOS error32になったログを修正前の証拠として残す。
- [x] mount回帰16件、VFS lib全件、fmt/clippy、3OS既存suite、実機Linux差分、全体/U1 coverage80%以上を確認する。source-manifestへ関連testのowning fileを追加する。これは同じ復旧で見つかった同種cleanupの限定修復で、以前の承認対象を変更済み内容へ読み替えない。

### Step 25：成果物と復旧の確定

- [x] code-summary、traceability、source-manifestと現在sourceのsnapshotを更新し、関連修復ファイルとunit所有を明記する。独立レビューへ渡す。plan-approval-guard/continue-workflowの2フックの登録と回復テストを確認し、rejected reportが必要な場合はその前に両フックを復元・検証する。過去のレビューや承認を今回へ転用しない。

