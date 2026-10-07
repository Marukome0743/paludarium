# U4 メモリ・時刻・シグナルのコード生成計画

2026-10-08 の復旧計画。Steps 1〜14 は過去実装の履歴として保持する。今回の実行対象は Steps 15〜18 のみであり、新しい計画承認後に開始する。要件にない別 Unit の機能を追加しない。

## Sources

- `inception/units-generation/unit-of-work.md` U4、`unit-of-work-story-map.md`：ストーリー工程を省略しているため FR2.2・FR2.9 を計画ステップへ対応させる。
- `inception/requirements-analysis/requirements.md` FR1.5、FR2.1、FR2.2、FR2.9、FR9.1、FR9.3、NFR1〜9。
- `inception/contract-design/contract-summary.md` C1/C2/C4/C5/C8/C10：型と提供側の責任、一方向依存、内部契約変更時の全利用側更新。
- 現行 `paludarium-kernel/src/{lib.rs,syscalls.rs}` は登録・mask・altstack を保持するが配送しない。fault は終了へ変換する。`paludarium-host/src/lib.rs` の時刻・待機 API は未実装。MMU は通常アクセス・mapping・atomic の共通同期を既に持つ（source 読取によるドキュメント根拠）。
- U4 の functional-design / nfr-requirements / nfr-design / infrastructure-design ディレクトリは現在存在しない。任意入力を創作せず、共有契約・要件と native 観測で具体化する。
- 直前の U2 workspace 検証成功は引継ぎ証拠。今回 U4 の合格を意味しない。U1/U2 再実装と任意の新依存追加を行わない。

## 実装範囲と境界

U4 は anonymous memory の mmap/munmap/mprotect/brk、Rust std/tokio が必要とする clock_gettime/nanosleep/clock_nanosleep、signal action/mask/altstack、同期例外と単一ゲスト thread への配送・return を扱う。ゲスト signal は Linux x86-64 ABI とする。file-backed mmap は VFS U7 の fd/backing が未実装であり、その取得・共有ファイル機能を先取りしない。native syscall inventory で U4 必須と判明した追加形は範囲内で回収し、未対応必須形を完了扱いしない。clone/futex は U5、SSE 実行は U3、wasm 実装は U11、JIT は U14。

Kernel が CpuState と signal 状態を所有し、Cpu は Kernel/Host を知らない。時刻・待機は Host だけが OS に接続する。signal frame はゲストメモリへ検査付きで直列化し、ホスト構造体・ポインタを cast しない。SSE register の保存は既存 CpuState の保存であり U3 命令実装を追加しない。MMU の共通同期を維持し、Host 呼び出し・任意 callback をその lock 内で実行しない。

## Steps

1. [x] **Runner と baseline（FR9.1、NFR1/7/9）**：承認後、既存 exact kernel test を非ゼロ件で実行して baseline を記録する。U4 専用 `diff_u4.rs` / support watchdog と guest build script を先に bootstrap し、`--list` でケース件数を検査する。最初の実行可能差分ケース以前に runner を準備する。未作成 target を現在 runnable と称さない。
2. [x] **取得・ABI inventory（FR2.2/2.9、NFR1/8）**：U2 で固定した probe/aube の source/revision/lock/binary receipt を読み、関連 syscall の static callsite と bounded native trace を追加採取する。bin hash・command・trace 到達範囲と Linux x86-64 ABI の syscall 番号、構造体 field offset、flags/errno を `docs/u4/syscall-matrix.md` へ固定する。loader 初期化だけの trace と本体を区別し、未取得の必須 syscall/form は GAP とする。コピー元として他 project の source を使わない。
3. [x] **memory native ケース先行（FR2.2/1.5、NFR1/2）**：`tests/guests/u4/memory.c` を用意し、毎回 native の戻り値・errno・領域内容・fault context を取得する。len 0/overflow/非整列、hint、MAP_FIXED replacement、NOREPLACE overlap と非破壊、private/shared anonymous、ページ丸め、穴を跨ぐ unmap/protect、brk grow/shrink/failure を比較する。未定義・実行依存アドレスは関係値へ正規化する。現在の emulator 不一致を修正前に保存する。
4. [x] **memory 実装（FR2.2/1.5、NFR2/3/4/5）**：Kernel の引数検証と MMU の mapping transaction を native 観測へ合わせる。range 検証前に MAP_FIXED の旧 mapping を消さない。permission / execute fault と MAPERR/ACCERR を区別する必要があれば C1/C4 typed fault を拡張し、Cpu/Loader/Kernel/Runtime/Jit/全 test consumer を同一変更で整合させる。64-bit GuestAddr、checked conversion、lazy pages と code generation invalidation を維持する。
5. [x] **memory 内部テスト・Green（FR2.2、NFR1/2/3）**：実装後に `paludarium-mmu/src/u4_tests.rs` 8 件以上、Kernel memory tests 8 件以上を追加する。failed transaction 不変、ページ跨ぎ permission、cache invalidation、atomic と map/protect の同期を含める。memory 差分を Green にし、観測と型の対応を記録する。
6. [x] **clock / sleep native ケース先行（FR2.9、NFR1/7）**：`tests/guests/u4/time.c` で clock ids、timespec signed range、NULL/EFAULT、invalid tv_nsec、zero sleep、relative/absolute deadline、割込みと remaining の native 結果を取得する。時刻そのものは一致させず単位・範囲・単調性と成功/errno、remaining bounds を比較し、正規化表を作る。性能値は測らない。
7. [x] **clock / sleep 実装と内部テスト（FR2.9、NFR2/3/7）**：C2 に typed monotonic/realtime clock と bounded/cancellable wait を追加する。NativeHost・RecordingHost・既存 mock 全実装を更新し、他層から std::time/std::thread を呼ばない。Kernel に clock_gettime/nanosleep と inventory に必要な clock_nanosleep を明示登録する。相対・絶対 deadline、overflow、EINTR/rem を扱う。Host/Kernel 各 8 件以上の内部テストを実装後に書き、fake clock の deterministic ケースと native 差分を実行する。
8. [x] **signal ABI・配送 native ケース先行（FR2.9、NFR1/2）**：`tests/guests/u4/signals.c` と raw syscall/restorer assembly で registration/query、mask、SIGKILL/SIGSTOP 制約、SIG_DFL/SIG_IGN、SA_SIGINFO/SA_ONSTACK/SA_NODEFER/SA_RESETHAND/SA_RESTART、nested handler、blocked pending と unblock、SIGSEGV/SIGILL/SIGFPE、rt_sigreturn を観測する。siginfo の si_code/si_addr、ucontext の fault RIP/RSP/register/rflags、mask、altstack、handler 順序と return 後状態を比較する。Linux 配送由来 flags と未定義 flags は mask を根拠付きで明記する。tgkill/tkill/kill の単一 process/thread 自己配送が std/tokio またはケースに必要なら U4 の明示 dispatcher に追加する。
9. [x] **signal frame / return 実装（FR2.9、NFR2/3/4）**：`paludarium-kernel/src/signals.rs` に checked siginfo/ucontext/rt frame codec、restorer、red zone/stack alignment、nested frame と altstack 状態を実装する。frame 全 range の permission を検査して失敗を guest fault として処理し、host panic にしない。rt_sigreturn は検証して GPR/RIP/RSP/rflags/fs/gs/SSE 状態・mask・altstack を復元する。無効 frame、noncanonical context、reserved flags と frame 改変は native 観測に合わせ、guest RAX を syscall の通常 return で上書きしない。
10. [x] **signal 配送と wait 接続（FR2.9、NFR1/2/7）**：Kernel に process actions/thread mask/pending/synchronous fault の型と配送 checkpoint を作る。不可 block signals、標準 signal の重複、ignored/default/handler を扱う。Runtime は budget 境界と syscall/fault 前後で配送し、kill 要求を bounded wait 中にも処理する。fault RIP と U2 repeatContinuation を保存し、handler の実行 context で古い REP context を誤使用せず、return の context 変更に応じ整合させる。restartable syscall と EINTR、absolute/relative sleep remaining は native-first で確定する。MMU lock を保持して sleep しない。
11. [x] **signal / Runtime 内部テスト・Green（FR2.9、NFR1/2/3/7）**：Kernel signal 8 件以上、Runtime 8 件以上、必要 C1 codec 5 件以上の内部テストを実装後に追加。fault context、frame 書込失敗、mask restore、nested altstack、malformed return、blocked pending、restart/EINTR、kill cancellation、REP fault handler return を含む。native signal 差分は独立ケース 12 件以上、time 6 件以上、memory 8 件以上を最低計画件数とし、inventory 必須形が増えれば追加する。ゼロ tests / skip を pass にしない。
12. [x] **変更層の回帰・configuration（FR9.1、NFR3/7/8/9）**：U4 scoped commands と変更された shared contract consumer の既存 regression を実行し、全 workspace gate は別途一回実施する。fmt/clippy 警告 0、固定 nightly/Cargo.lock/crates.io/cargo-deny、SHA 固定 actions を維持する。CI に U4 differential target と syscall/memory fuzz を接続する。Linux workspace line coverage 80% を維持し、下げて通さない。
13. [x] **fuzz（FR9.3、NFR2/3）**：`fuzz/fuzz_targets/syscall_args.rs` と `mmu_ops.rs` に U4 memory/time/signal frame 生成を足す。fake clock、bounded Cpu budget と wait により毎入力を有限にする。pinned nightly ASan の夜間各 600 秒予算を維持し、変更 source に対するローカル bounded run の具体結果を記録する。失敗再現・source revision と runner condition を保存し、別 project process を停止しない。
14. [x] **成果物・manifest（全割当 FR/NFR）**：`docs/u4/{syscall-matrix.md,signal-abi.md,validation.md}` と unit の code-summary / traceability を完成させる。native expectation を固定 goldens にせず、実行時取得にする。source-manifest version 1 に変更/作成/削除した全 application-source を列挙し、generator/shell/scaffolding が書いた source も含める。build cache/生成 binary は除き、必要証拠は追跡可能な .txt で保存する。未達・未検証を GAP として残す。root に独立 review 用に固定して渡す。

## 今回の復旧手順

15. [x] **現状・runner 確認（FR2.2/2.9、NFR1/7/9）**：共有契約、既存 U4 source manifest、native ABI/inventory、専用 diff_u4 と内部 u4_ filters を確認する。過去の未作成・43件・76件・coverage/fuzz 成功を当時の source に限定し、現在ソースの対応表を作る。既存テストの一覧と実機 CI の非ゼロ件結果で readiness を確認する。
16. [x] **現在ソースと CI の証拠照合（FR9.1、NFR1/3/8/9）**：署名済み 4d52be0a の CI 7ジョブ・native 4ジョブと手元の application/build files を照合し、U4 差分44件、内部各層、3OS、lint、依存、coverage80% gate の該当ログを対応させる。現在 bytes が一致する証拠のみ再利用する。不足は exact unit commands で追加検証し、Docker VMM/QEMU と実機 x86-64 Linux の結果を区別する。
17. [x] **不足と修正（FR2.2/2.9/9.3、NFR2/3/7）**：製品不具合が見つかった場合に限り、syscall/guest は実機 native 期待と修正前 Red を先に記録して最小修正、内部層は test-after で検証する。U1/U2 の承認済み source を変更する必要があれば root に返し、完了証拠を無断で変えない。現在 source と結び付かない syscall_args/mmu_ops 各600秒 ASan は未検証/GAP として残し、Build and Test で回収する。30秒watchdog・80%coverage・nightly固定・各600秒を下げない。
18. [x] **成果物と独立レビュー（全割当FR/NFR）**：現在 source の snapshot、code-summary、traceability、厳密な version1 source-manifest を整合させる。旧 evidence/source hashes/validation は履歴として保存し、旧 fuzz を現在合格へ流用しない。全必須 ID と既存 OK target を確認し、未達は GAP。独立レビュー後は対象 source と4成果物を固定し、正式検証・完了確認へ渡す。

## 予定する変更 paths と影響

- `crates/paludarium-types/src/lib.rs`（必要 typed fault/errno）、`crates/paludarium-mmu/src/{lib.rs,u4_tests.rs}`（C4）。共有 C1/C4 consumers の `crates/paludarium-cpu/src/{lib.rs,exec.rs,u4_tests.rs}`、Loader/Jit の必要な match/fixture を同一変更で更新する。
- `crates/paludarium-kernel/src/{lib.rs,syscalls.rs,signals.rs,u4_tests.rs,tests.rs}`（C8）、`crates/paludarium-host/src/{lib.rs,testing.rs,u4_tests.rs}`（C2）、`crates/paludarium-runtime/src/{lib.rs,u4_tests.rs,tests.rs}`（C8/C10）。Host を実装する既存 test mock も全検索して更新する。
- `crates/paludarium-harness/tests/{diff_u4.rs,support/u4.rs}`、`tests/guests/u4/{build.sh,memory.c,time.c,signals.c,restorer.S}`、必要な `tests/guests/build.sh`、`fuzz/fuzz_targets/{syscall_args.rs,mmu_ops.rs}`、`.github/workflows/ci.yml` と fuzz workflow（現在 path を実装時に確認）、`docs/u4/*`。
- C1/C2/C4/C8 は cross-crate 影響が大きい。変更前に exact diff と consumer 一覧を確認し、U1/U2 artifacts とレビュー記録は変更しない。API/DB/UI/deployment は本 Unit に該当せず新規作成しない。公開 API が必要に変わるなら変更履歴を記録する。

## Assumptions & Open Questions

Linux x86-64 native の ABI/errno/配送観測を実装の基準とする。すべての任意 signal/clock 拡張を無制限に追加するという意味ではなく、std/tokio と固定対象の必須 inventory を取得・対応させる。現在、人に選択を求める未決 product policy はない。native 観測が共有契約・要求と両立しない場合は具体的な evidence を root に返して停止する。

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



