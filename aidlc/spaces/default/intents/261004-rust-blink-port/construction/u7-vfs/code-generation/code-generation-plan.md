# U7 ファイルシステム：実装計画

## 範囲と根拠

ドキュメント根拠：`inception/units-generation/unit-of-work.md` のU7、`unit-of-work-story-map.md`、`inception/requirements-analysis/requirements.md` のFR3.1–FR3.4、FR2.10、NFR1–NFR9、`inception/contract-design/contract-summary.md` のC2/C6/C8/C10/C11。ストーリー工程は省略されているため、FRを手順に直接対応させる。U7固有のfunctional/NFR/infrastructure設計は存在しない。

既定のMemFs、明示指定されたホストディレクトリのマウント、作成・読み書き・hard link・symlink・flock・rename・read_dir・stat、起動前配置を完成させる。ゲストstat系のNULLパスにはEFAULTを返す。既存のhello world、整数命令、メモリ・シグナルの挙動を維持する。スレッド作成・プロセス起動・ソケット・端末・SSE・wasm・JITはそれぞれの担当Unitに残す。

## 変更面と設計

- `crates/paludarium-vfs/src/`：inode、ディレクトリ、パス解決、OpenFile、リンク、メタデータ、ロック、マウント合成。`FileSystem::read_file/stat`の現利用側との互換を保ち、必要な内部型変更は利用側も同時に更新する。
- `crates/paludarium-host/src/`：型付きHostFs能力とネイティブのディレクトリ能力。OSファイル操作はここに閉じ込める。VFSからstd::fsを呼ばず、依存循環を作らない。
- `crates/paludarium-kernel/src/`：FD表・共有open-file description・cwd、明示的syscall追加、checked guest bufferとLinux x86-64 ABIの変換。
- `crates/paludarium-runtime/src/`、必要な`loader/src/`・公開API/CLI：preloadとマウントを接続し、既定はホスト非公開。
- `crates/paludarium-harness/tests/diff_u7.rs`、`tests/guests/u7/`、各クレートの`u7_`テスト、`fuzz/fuzz_targets/vfs_paths.rs`・既存syscall_args、CI/nightly、必要なCargo manifests/lock、`docs/u7/`。

影響はVFS/Host/Kernel/Runtime境界にまたがる。CPU・decoder・MMUの命令やフォールト意味論の変更は計画しない。Loaderや既存APIの追従はC6利用側に限定する。

パス解決はinodeから逐次行い、symlink展開と`..`を単なる事前lexical normalizationで済ませない。rootを越える参照、symlink loop、NUL/長さ、非UTF-8、末尾slash、relative cwd、follow/nofollowを型付きerrnoで扱う。ホストはrootの開いたディレクトリ能力から相対操作する。`canonicalize`で検査後に絶対パスを再openする方式は採用しない。安全なRust APIを持つcrates.io依存を評価し、ライセンス・逃走防止・symlink/rename競合を実測してから導入する。依存選定・安全性は現時点で未検証で、確認を実装手順に含める。

FD番号とopen-file descriptionを分離し、offsetとflock所有者を共有する。unlink後のopen inode寿命、hard linkのlink count、rename置換、cross-mount EXDEV、同一inode操作、append・truncate・seekを扱う。flockはshared/exclusive/nonblocking・変換・close解放と、阻塞時のキャンセル/シグナルを既存Host待機境界で実装する。ゲストファイル数・サイズに独自quotaは追加しない（NFR5）。symlinkのLinux規定やファジング一入力の有限予算は製品quotaと分ける。

## 順序付き実装手順

- [x] Step 1 — U7変更面とC6/C2境界を確定し、既存互換を記録する。FR3.1–3.4、FR2.10、NFR3/4/9。
- [x] Step 2 — 既存Rust runnerと単位限定コマンドを確認する。まず既存VFS 5テストを実行し、`u7_`名前空間/専用diffターゲットと30秒境界を用意する。NFR1/7/9。
- [x] Step 3 — 実装前にLinuxでsyscall/ゲストのケースを作る。open/openat/create/read/write/close/lseek、mkdir/unlink/rmdir、link/linkat、symlink/readlink、rename/renameat、getdents64、stat/fstat/lstat/newfstatat、flockを対象とし、必要なdup/fcntl FD操作も最小限含める。NULL・不正buffer・flags・dirfd・エラー・リンク/rename/lockを含め、ネイティブ期待結果と現実装の失敗を生ログで残す。FR3.3/2.10、NFR1。
- [x] Step 4 — inode/ディレクトリ・パス・OpenFileの内部型と解決を実装し、その後に5–8件以上の単体テストを各部品へ追加して実行する。FR3.1/3.3、NFR2/4/5。
- [x] Step 5 — MemFsの作成・読み書き・リンク・unlink・rename・read_dir・stat・preloadを実装し、その後に内容/offset/寿命/エラー単体テストを追加して実行する。FR3.1/3.3/3.4。
- [x] Step 6 — FD表とfile syscallのguest-memory/ABI境界を実装し、Step 3の差分をgreenにする。実装後にKernelの5–8件以上の単体テストを追加して実行する。NULL statはguest EFAULTで継続する。FR3.3/2.10、NFR1/2/4。
- [x] Step 7 — flock所有権・競合・変換・阻塞/キャンセルを実装し、ネイティブと差分比較する。実装後にロック内部状態の単体テストを追加して実行する。guest cloneを新設せず、複数FD/共有descriptionとHost側の有限並行ケースで検証する。FR3.3、NFR7。
- [x] Step 8 — ホストのrootディレクトリ能力、型付きHostFs、crates.io依存の出所/ライセンスを検証して実装する。実装後に許可root内操作とroot外参照・symlink/rename競合・hard link・cross-mountの5–8件以上の単体/隔離テストを追加して実行する。FR3.2、NFR4/8。
- [x] Step 9 — Mount合成・Session/Loader/preload・CLIに接続する。先にネイティブと比較するゲストケースを用意してから実装し、内部Runtime接続テストは実装後に追加する。未指定時のホスト非公開と起動前配置を確認する。FR3.1/3.2/3.4。
- [x] Step 10 — file probeに相当する作成/hard link/symlink/flockをU7のゲスト差分で検証する。probe全体・aube全体の合格は担当U10と混同しない。標準出力・標準エラー・終了状態・ファイルの内容/種別/link countなどを比較し、pid/inode番号/時刻の除外を記録する。FR3.3/9.1、NFR1。
- [x] Step 11 — VFSパス/操作列fuzzとU7 syscall_args入力を追加する。nightlyに各600秒、各ケース30秒を維持し、順次実行してpanic/ASan違反・再現入力を保存する。FR9.3、NFR2/3/7。
- [x] Step 12 — U7単位限定coverageでLinux行80%以上、fmt/clippy警告ゼロ、cargo-deny、CI action SHA、依存lockを検証する。既存workspaceの正式検証は承認済みcheckpointコマンドで確認する。NFR3/8/9。
- [x] Step 13 — U7 raw evidence・native比較除外一覧・変更API/使用法・source manifest・FR/NFR traceability・code-summaryを完成させる。測定した件数だけ記録し、未検証を合格にしない。NFR1–9。
- [ ] Step 14 — independent review用にソースと成果物を固定し、指摘の必要修正だけを行って再検証する。checkpointの承認と次Unit選択は親担当へ返す。

## 検証の合否

custom orderingをそのまま適用し、ゲストsyscallはネイティブケースを先に、VFSなど内部部品は実装後に単体テストを実行する。Standardの各部品5–8テスト、happy pathと少なくとも2つのerror/edge、重要境界のintegrationを満たす。Linux行80%以上・30秒diff/並行・各10分fuzz・unsafe禁止・依存検査を下げない。ホスト隔離はチェック後openの競合ケースまで観測する。U12/U13の固有ホスト実装やU11ブラウザ合格を本Unitで主張しない。

## 承認と未確定点

実装開始前の初回Plan Approvalを待つ。HostFs依存の具体名と細部のerrno/ABI選択は、上記ネイティブ/供給網検証で確定する。FR/NFRの対象・数値・隔離条件は変更しない。追加の人への質問は現時点ではない。
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
