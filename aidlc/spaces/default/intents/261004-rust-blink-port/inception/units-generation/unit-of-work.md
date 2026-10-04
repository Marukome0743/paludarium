# 作業単位（Unit）：Rust 版 blink（paludarium）

上流の成果物：
- `inception/domain-design/components.md`（12 部品）
- `inception/domain-design/decisions.md`（ADR-001〜ADR-008）
- `inception/requirements-analysis/requirements.md`（FR・NFR）

根拠は `units-generation-questions.md` の回答（Q1〜Q4）と、承認済みの分割の計画です。

## 方針

- **最初の Unit**：U1 は、ネイティブの Linux で hello world を端から端まで動かす細い一本です（team-practices の Walking Skeleton、Q1）。
- **その後の Unit**：機能ごとに分けます（Q1）。大きさは、1 つが数週間で終わる程度にします（Q2）。
- **コードの置き方**：Cargo のワークスペースに、部品ごとのクレートを置きます（`paludarium-decoder` など）。公開するのは、まとめ役のクレート `paludarium`、コマンド、npm のパッケージです（Q3）。
- **Unit とクレートの関係**：1 つの Unit が複数のクレートにまたがることがあります。たとえば U1 は、ほぼすべてのクレートの最初の版を作ります。後の Unit は、そのクレートに機能を足していきます。
- **作る順番**：この文書は依存関係（トポロジー）だけを決めます。実際の順番は Delivery Planning で決めます。

## Unit の一覧

| Unit ID | Directory | Kind | 大きさ | 配置 |
|---------|-----------|------|--------|------|
| U1 | u1-skeleton | library | L | ワークスペース全体の土台（各クレートの最初の版、Cli、CI） |
| U2 | u2-integer-isa | library | L | `paludarium-cpu`（整数命令）と差分テスト |
| U3 | u3-sse | library | M | `paludarium-cpu`（SSE 系） |
| U4 | u4-memory-signals | library | M | `paludarium-mmu`・`paludarium-kernel` |
| U5 | u5-threads-futex | library | L | `paludarium-kernel`・`paludarium-host`・`paludarium-runtime` |
| U6 | u6-events-sockets | library | M | `paludarium-kernel` |
| U7 | u7-vfs | library | M | `paludarium-vfs`・`paludarium-kernel` |
| U8 | u8-process-spawn | library | M | `paludarium-kernel`・`paludarium-loader` |
| U9 | u9-terminal-io | library | S | `paludarium-kernel`・`paludarium-host`・`paludarium-runtime` |
| U10 | u10-probe-aube-native | packaging | M | probe のクレート、aube のビルド、Harness |
| U11 | u11-wasm-launcher | library | XL | `paludarium-host`（wasm 用）、起動用 JS（npm）、Harness（Node.js・ブラウザ） |
| U12 | u12-macos-host | library | M | `paludarium-host`（macOS 用） |
| U13 | u13-windows-host | library | L | `paludarium-host`（Windows 用） |
| U14 | u14-jit-wasm | library | XL | `paludarium-jit` |
| U15 | u15-release | packaging | S | 公開の CI、パッケージの設定 |

## 各 Unit の定義

### U1 u1-skeleton：細い一本（hello world）

- **内容**：ネイティブの Linux で static-musl の hello world を、最初から最後まで動かします。通す道筋は次のとおりです。
  1. ELF の読み込み
  2. デコード（既存の crate を包む）
  3. 最小限の整数命令の実行
  4. ソフトウェア MMU
  5. `write`・`exit_group`・`brk`
  6. ホストの標準出力
- **含めるもの**：
  - ワークスペースの土台（`rust-toolchain.toml` で nightly を固定、`[workspace.lints]`）
  - 各部品のクレートの最初の版：Decoder・Mmu・Cpu・Loader・Kernel・Vfs（ELF を置くだけの最小限）・Host（ネイティブの Linux）・Runtime・Cli
  - 差分テストの最小限（hello world の標準出力と終了コードを、ネイティブと比べる）
  - CI の土台（3 つの OS での単体テスト、lint、依存の検査）
  - 未実装の syscall に ENOSYS を返す仕組み（FR2.1）
  - ファジングの入口（FR9.3）
- **wasm のスレッドの確認**：Host の trait を通したまま、wasm で小さく確かめます（決定 D22）。確かめる内容は 2 つです。
  - SharedArrayBuffer を共有した Worker で、アドレスで待つ・起こすが動くか
  - Worker を誰が作るのが妥当か（ドメイン設計のレビュー指摘 R-01・R-02）
- **完了の条件**：hello world の標準出力と終了コードが、ネイティブと一致することをコマンドで示します。そのうえで、人が結果を確かめます。
- **注意点**：
  - 後の Unit が書き直さずに済むよう、ホストの機能は最初から Host の trait を通します（ADR-007）。
  - `unsafe` は Host の中だけに置きます。

### U2 u2-integer-isa：整数命令とフラグ

- **内容**：probe と aube が使う範囲の整数命令とフラグの意味論をそろえ、命令ごとに差分テストを持ちます（FR1.3）。未定義の命令には SIGILL を返します（FR1.6）。
- **注意点**：
  - 未定義のフラグは比べません。比べないものの表を作ります。
  - 原子的な命令（lock 接頭辞付きの命令、xchg）の担当を決めます（レビュー指摘 R-02）。

### U3 u3-sse：SSE 系の命令

- **内容**：probe と aube が使う範囲の SSE 系の命令を実装します（FR1.4）。AVX・AVX-512 は範囲外です。

### U4 u4-memory-signals：メモリ・時刻・シグナル

- **内容**：
  - メモリの syscall（mmap・munmap・mprotect・brk）を、ページフォールト（SIGSEGV）まで含めて実装します（FR2.2）。
  - 時刻と待機（clock_gettime・nanosleep）と、シグナルの登録・マスク・配送を実装します（FR2.9）。

### U5 u5-threads-futex：スレッドと futex

- **内容**：
  - スレッドの作成（clone）を実装します。
  - Kernel の中で futex（FUTEX_WAIT_BITSET を含む）を作ります（FR2.3、ADR-003）。
  - Host には「アドレスで待つ・起こす・時間付きで眠る」を足します。
  - ゲストのスレッドをホストのスレッドに割り当てます（FR5.4）。
- **注意点**：スレッドを使うテストには、時間切れの上限を付けます（NFR7）。

### U6 u6-events-sockets：イベントとソケット

- **内容**：
  - eventfd2、ホストに頼らない edge-triggered の epoll、AF_UNIX の socketpair、タイマーを実装します（FR2.4〜FR2.6）。
  - AF_INET などのネットワークは、エラーを返します（FR2.7）。

### U7 u7-vfs：ファイルシステム

- **内容**：
  - 仮想ファイルシステム（既定）を作ります（FR3.1）。
  - ホストの指定ディレクトリを見せる方式を作り、外へ出られないようにします（FR3.2）。
  - 作成・hard link・symlink・flock・rename・read_dir・stat 系の操作を実装します（FR3.3）。
  - 起動前にファイルを置けるようにします（FR3.4）。
  - パスが NULL の stat 系には EFAULT を返します（FR2.10）。

### U8 u8-process-spawn：別のプログラムの起動

- **内容**：fork 相当の clone、execve、wait4 を実装します。仮想ファイルシステムにない実行ファイルには ENOENT を返します（FR2.8）。

### U9 u9-terminal-io：入出力と端末

- **内容**：引数・環境変数・標準入出力に加えて、tty の判定と画面の幅を扱います（FR4.1、FR4.2）。

### U10 u10-probe-aube-native：probe と aube（ネイティブの Linux）

- **内容**：
  - formicarium と同じ項目の probe を、paludarium に持ちます（FR6.1、FR6.2）。
  - CI で、版を固定した aube のソースから static-musl 版をビルドします（FR7.1）。
  - ネイティブの Linux で、probe の全項目、aube の 4 コマンド、#1645 の再現がネイティブと一致することを確かめます（FR6.3、FR7.2、FR7.3）。
  - 実行時間を記録します（FR7.4）。
- **注意点**：
  - aube を static-musl でビルドできなければ、ここで扱いを決め直します（要件書の Assumptions）。
  - node がない場合の aube の振る舞いも、ここで確かめます（要件書の Open Questions）。

### U11 u11-wasm-launcher：wasm と起動用 JS

- **内容**：
  - wasm のビルドと、wasm 用の Host（Worker・SharedArrayBuffer・Atomics）を作ります。
  - 起動用 JS（Launcher）を作ります。
  - Node.js とブラウザ用のテストハーネスを作ります（FR5.2、FR5.3、FR9.2）。
  - probe と aube が、Node.js の Worker と Chromium 系・Firefox・Safari で動くことを確かめます（FR6.3、FR7.2）。
- **注意点**：U1 での確認の結果をもとに、Worker を誰が作るか、Worker 間で共有する状態をどう扱うかを決めます（レビュー指摘 R-01・R-02）。

### U12 u12-macos-host：macOS のホスト

- **内容**：macOS 用の Host を作り、probe と aube がネイティブと同じ結果になることを確かめます（FR5.1）。

### U13 u13-windows-host：Windows のホスト

- **内容**：Windows 用の Host を作り、probe と aube がネイティブと同じ結果になることを確かめます（FR5.1）。
- **注意点**：シンボリックリンクの権限、flock、待機の機能が、Linux と大きく違います（RAID ログ R3）。

### U14 u14-jit-wasm：wasm 向けの JIT

- **内容**：
  - x86-64 の命令列を wasm に変換する、最小版の JIT を作ります（FR8.1）。
  - JIT ありとなしの結果を差分テストで比べます（FR8.2）。
  - Node.js の Worker で各 10 回実行し、JIT ありの方が速いことを有意水準 5% で確かめます（FR8.3）。
- **注意点**：メモリの範囲の検査を省かないこと。書き換えられたページの変換結果を、他の Worker でも捨てること（レビュー指摘 R-02）。

### U15 u15-release：公開

- **内容**：タグを打つと、CI から crates.io と npm に公開します。公開の前に人が承認します（FR10.1）。Trusted Publishing を優先します。
- **注意点**：nightly 専用のクレートを公開してよいかを、公開の前に見直します（要件書の Open Questions）。

## Assumptions & Open Questions

- [assumption] Unit の大きさ（S〜XL）は相対的な見積もりで、U1 の実績で見直す。
- U1 での wasm のスレッドの確認結果によっては、U11 の内容と大きさが変わる。
