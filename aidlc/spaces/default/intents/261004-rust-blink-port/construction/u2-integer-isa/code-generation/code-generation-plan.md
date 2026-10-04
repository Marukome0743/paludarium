# U2 Integer ISA — Code Generation Plan

Status: Plan Approval 待ち。以下は未実行の計画。アプリケーション変更は禁止。

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

## 根拠・境界

ドキュメント根拠: U2 functional-design と NFR requirements の READY 設計、C1/C3/C4/C5、unit-of-work、FR1.3/1.6/9.1 を適用する。stories は生成されていないため架空の AC を作らない。原子命令・MMU indivisible operation・ホスト並列検証は U2、guest clone/futex は U5。SSE は U3、probe/aube 全体統合は U10、JIT は U14。これは probe/aube が必要とする U2 整数命令の範囲を縮める理由ではない。

検証済み: `cargo test --locked -p paludarium-cpu --lib tests::budget_exhaustion_stops_an_infinite_loop -- --exact` は exit 0、1 passed、0 failed、17 filtered out。現在の runner readiness の根拠である。U2 専用ターゲットと filters は未作成で未検証。

ソース観測: CPU の Stop に DivideError が存在し CpuState に REP continuation はない。MMU の read/write/fetch と map/unmap/protect の既存入口をすべて同じ同期機構へ接続する必要がある。現状の原子性・REP fault semantics は未検証。

取得元観測: `../formicarium/guest/probe/{Cargo.toml,Cargo.lock,src/main.rs,src/futex_deadline.rs,src/page_fault_race.rs,src/bin/hello.rs,src/bin/exit3.rs}` がある。`../formicarium/scripts/build-guests.sh:17-18` は aube canonical repository `https://github.com/aubepkg/aube.git`、ref `v2.6.1`。`../formicarium/scripts/measure-aube.mjs` は --version/install/install --frozen-lockfile/list と `fixtures/sessions/aube-1645.txt` を指定する。immutable revisions、guest artifact hashes、完全な命令/forms inventory、runtime traces は未取得。承認前に大きな build は行わない。

## 実行計画（Plan Approval 後のみ）

1. [x] Runner bootstrap。`crates/paludarium-harness/tests/{diff_u2.rs,parallel_u2.rs}` と必要な harness support、`tests/guests/u2/{build.sh,observe.c}` を用意する。最初の executable testcase 前に、新 harness ターゲットの `--list` が実際の bootstrap ケースを列挙することを検査する。内部層の `u2_` filter は各層の実装後にテストを追加した時点で非ゼロ件数を確認する（Step 4〜12）。まだ作っていない内部層テストを bootstrap の前提にしない。空集合を成功と扱わない。既存 exact readiness と承認後 bootstrap を区別する。BR4.1/NFR7.1。
2. [x] ソース取得・inventory を固定する。probe の sibling source tree/lock を読み、jj で immutable revision と dirty source の hash を記録する。aube の v2.6.1 を immutable commit に解決し jj で取得、既存 scripts の Git 操作をそのまま実行しない。static-musl artifacts の SHA256、toolchain/build args、session fixture hashes を `docs/u2/inventory.md` に記録。objdump の静的 forms と Linux runtime traces を突き合わせ、probe と aube 4 コマンド/#1645 の全整数 forms、幅、prefix、implicit operands を case ID に対応付ける。取得不能・未分類は具体的 GAP として残し U2 完了を宣言しない。BR1.1/BR4.2/FR1.3。
3. [x] 実装に先立ち native differential ケースを作り実行する。`tests/guests/u2/*.c` と harness observer で raw register/memory/flags、defined/preserved/undefined masks、入力条件、signal/fault RIP/context を取得する。CI ごとに native を再実行し期待値を生成する。normal、fault、REP restart、atomic parallel ケースを準備し、各 child に外側 30 秒 watchdog、kill/reap を実装する。未提供 native runner を PASS にしない。BR1.3/4.1/NFR1.1-1.3/7.1-7.2。
4. [x] C1 の arithmetic fault を既存 DivideError と照合し、`crates/paludarium-types/src/lib.rs`、CPU、`crates/paludarium-kernel/src/{lib.rs,tests.rs}`、`crates/paludarium-runtime/src/lib.rs`、harness の全消費箇所を同じ変更で整合させる。DIV/IDIV zero と quotient overflow を guest SIGFPE に変換し host panic を起こさない。内部型の実装後に `u2_` tests を追加する。C1/BR1.7/FR1.6/NFR2.1。
5. [x] Decoder 接続を `crates/paludarium-decoder/src/lib.rs` と types で拡張する。必要な全 widths/forms、REX/high8、address32/RIP/FS/GS、LOCK/REP legality、128-bit register pair、必要最小 fetch を扱う。外部 decoder 型を public contract に漏らさない。実装後 5–8 件以上の層テストを追加し invalid prefix と truncated fetch を分ける。C3/BR1.1-1.4/3.1-3.2。
6. [x] MMU の `crates/paludarium-mmu/src/{lib.rs,tests.rs}` に typed atomic request/result を実装する。arbitrary callback を lock 内で実行しない。normal read/write/fetch、initial writes、map/unmap/protect、atomic が共通同期を使う。public-to-public 再入を避ける private helpers と共有 address-space synchronization を設計し sequential consistency を保つ。全 bytes の permission/page validation を mutation 前に完了する。実装後少なくとも 8 件: cross-page/nonaligned、unmapped、read-only、failed CMPXCHG write permission、mapping競合、normal/atomic競合、old value、128-bit。C4/BR2.1-2.4/NFR1.3/4.1。
7. [x] native ケースを先に追加・実行してから CPU `src/{alu.rs,exec.rs,state.rs,lib.rs}` の move/extend/LEA、integer arithmetic/logic/flags を全 inventory forms 実装する。8/16 partial preservation、32 zero extension、high8/REX、carry/borrow/overflow、defined vs preserved flags を検証する。CPU は Kernel/Host に依存しない。FR1.3/C5/BR1.2-1.4。
8. [x] native ケースを先に追加・実行してから shift/rotate/bit operations、multiply/divide を実装する。count masks、zero-count flags、signed limits、quotient overflow、implicit operands の各 semantic dimension を検証する。BR1.3/1.7/NFR2.1。
9. [x] native ケースを先に追加・実行してから stack/control flow と fault commit を実装する。全 memory destinations を prevalidate し、非 REP fault では instruction-start regs/flags/RIP を維持する。invalid LOCK/UD2/unsupported を SIGILL とし、necessary fetch fault と混同しない。BR1.5/3.1-3.2/FR1.6。
10. [x] native ケースを先に追加・実行してから REP MOVS/STOS/LODS/CMPS/SCAS、DF/address32/count を実装する。REPE/REPNE CMPS/SCAS の fault は完了 count/index を保持し instruction-start flags を復元する。`CpuState` の repeatContinuation に start RIP/identity/start flags を保存し BudgetStop 後も再取得しない。正常終了/fault/別命令で unused context を消す。fault before/after iteration、page crossing、BudgetStop を跨ぐ fault のケースを比較する。BR1.6/NFR1.2。
11. [x] native ケースを先に追加・実行してから LOCK arithmetic、XCHG implicit lock、CMPXCHG/XADD/CMPXCHG8B/16B を inventory 通り実装する。各命令から MMU one-operation を呼び read/write split を禁止。readonly failed compare、16-byte alignment、page crossing を比較する。ホスト parallel old-value uniqueness、total/success count、normal access と map/protect/unmap race を bounded child tests で検証する。guest clone/futex は U5。BR2.1-2.5/NFR1.3/7.1。
12. [x] 内部層ごと実装後に happy-path/境界/fault の `u2_` unit tests を追加し実行する（原則 component ごと 5–8 件、CPU matrix は必要に応じ超過）。関係する Kernel/Runtime signal 消費と public API を同時検証し core unsafe 禁止と一方向依存を保つ。FR1.6/NFR2.1/3.1/4.1。
13. [x] `docs/u2/{inventory.md,flag-masks.md,differential-coverage.md}` を完成させ、命令割合と forms/semantic dimensions の対応・未実施一覧を分けて記録する。範囲内命令の differential case 1 件以上を数値で検査し、全 forms の不足を成功扱いしない。U1 `diff_u1` と既存 CPU readiness regression を再実行する。BR4.2/NFR3.3-3.4。
14. [x] `fuzz/fuzz_targets/{cpu_u2.rs,mmu_u2.rs}` と `fuzz/Cargo.toml`、既存 CI nightly 設定を更新し bounded CPU execution、固定 region/permissions/instruction budget を使う。新規 cpu_u2/mmu_u2 と既存 decoder/ELF fuzz の各 target をそれぞれ夜間 600 秒・ASan、seed/input を保存。新 product dependency は導入せず core unsafe を使わない。NFR2.2/8.1。
15. [x] unit-scoped fmt/clippy と差分/並列/内部 tests を実行し、Linux workspace 行 coverage 80% の既存 overall gate を別途維持する（unit subset coverage で代替しない）。nightly-2026-10-01、Cargo.lock、crates.io 制限、cargo-deny、Actions SHA を維持し閾値を下げない。NFR3.2-3.4/8.1/9.1。速度評価は U2 に追加しない。
16. [x] 実装後のみ code-summary.md、traceability.json、README、source-manifest.json を作成し FR/BR/16 detailed NFR を実行ログへ接続する。source claims は build 成果物/cache を除き、generator/shell/scaffolding が書いた application-source も全て実ファイルとして列挙する。未検証と取得 GAP を明示しレビュー・completion は conductor に渡す。






## 新しい確認の計画

上記Step1〜16、初期source観測、旧Plan Approvalと実装証拠は先行attemptの履歴である。今回の対象は現在のU2 source・固定inventory・保存済み検証の対応を再確認し、新しい承認の後に独立reviewへ渡すことである。初期の『未作成』『DivideError』『未取得』は計画作成当時の状態で、現在の状態とは区別する。U1とU2の既存READY成果物、application sourceは今回のPart1では変更しない。

検証済み：今回読取のexec.rs SHA256=e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0は保存済み最終検証source値と一致。U2 source-manifest.json SHA256=40233c4c56fd123f8977c9a4fda94f58b38b32e9b8762bc58bae62f24bf972cc。これだけで他の全sourceの不変を断定せず、承認後にclaimsと証拠対応を確認する。今回renderの完全Testing Contractをそのまま保持した。

17. [x] 現在のsourceと検証器の準備を確認する。U2 manifest claimsと既存source、C1/C3/C4/C5 consumer、FS/GS全atomic linear address、REP continuationを保存済み最終証拠と照合する。docs/u2/repairs/r01-workspace-coverage.txtのU2差分38/host parallel10/CPU31、全体197/94.00%、各nativeケース30秒watchdogとrunner存在を確認。旧実行を今回の新実行とは表現しない（FR1.3/1.6/9.1、NFR1.1〜1.3/3.3/7.1）。
18. [x] pinned source/lock/builder/binary receipt、aube4658/probe865分類分母と整数forms3136/696、幅/prefix/implicit operandのnativeケース対応、取得履歴・bounded trace限界を照合する。未分類または必須case証拠の欠落が見つかれば具体GAPを残す。production不変なら再取得・全実装・各10分fuzz・全体coverageを重複実行しない。新しい意味論修正が本当に必要ならnative Red先行→修正→Green、内部tests-afterというcustom順序を維持し、関係するunit限定commandsと必要な全体gate/fuzzを回収する。80%/30秒/nightly pinを変更しない（BR1.1/4.2、NFR2.2/3.1〜3.4/8.1/9.1）。
19. [x] 承認後の確認結果をU2 code-summary/traceability/evidenceへ現在値と履歴を分けて記録し、source-manifestの全application-sourceを確認して独立reviewへ引き渡す。U1 artifacts、既存READY review、application/shared docsは不要に編集しない。macOS/wasm/U5/U10/U14や任意全入力の合格へ範囲を広げない。別projectのbackground wasm buildは停止せず、速さの測定はしない（全割当BR/詳細NFR）。

