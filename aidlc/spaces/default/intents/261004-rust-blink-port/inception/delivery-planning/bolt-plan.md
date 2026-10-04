# Bolt の計画：Rust 版 blink（paludarium）

上流の成果物：
- `inception/units-generation/unit-of-work.md`
- `inception/units-generation/unit-of-work-dependency.md`
- `inception/units-generation/unit-of-work-story-map.md`
- `inception/contract-design/contract-summary.md`
- `inception/practices-discovery/team-practices.md`

根拠は `delivery-planning-questions.md` の回答（Q1〜Q9）です。

**Bolt** とは、1 つの Unit を設計からコードまで通して作り、動くものを出すひと区切りです。この計画では、1 つの Unit を 1 つの Bolt にします（Q3）。

## 進め方

- **順番**：1 つずつ進めます。1 つの Unit の設計からコードまでを終えてから、次の Unit に進みます（Q4）。記録上の設定は `Construction Iteration: unit-major`、`Construction Execution: serial` で、既定のままです。
- **確認**：各 Unit の完了時に、人が結果を確かめます（Q4）。
- **ブランチ**：短命なブランチから Pull Request を作り、`main` に squash で入れます。1 Bolt が `main` 上の 1 コミットになります（team-practices の Way of Working）。
- **確認コマンド**：各 Unit の完了時に実行するコマンドは、U1 の完了時に決めます（Q9）。
- **細い一本**：最初の Bolt は、細い一本（walking skeleton）です。walking skeleton とは、全体を最初から最後まで通す最小の版のことです。
- **並べ方**：U1 の後は、リスクの大きいものを先にします（Q1）。各 Bolt を WSJF（価値・急ぎ・リスクの大きさを足して、作業量で割った点数）で並べました（Q2）。点数と理由は `risk-and-sequencing-rationale.md` にあります。

## Bolt の順番

| 順 | Bolt | Unit | 細い一本 | 依存（済んでいる必要があるもの） |
|----|------|------|----------|----------------------------------|
| 1 | B1 | U1 u1-skeleton | ✅ | なし |
| 2 | B2 | U4 u4-memory-signals | | U1 |
| 3 | B3 | U2 u2-integer-isa | | U1 |
| 4 | B4 | U5 u5-threads-futex | | U4（と、原子的な命令のために U2） |
| 5 | B5 | U6 u6-events-sockets | | U5 |
| 6 | B6 | U9 u9-terminal-io | | U1 |
| 7 | B7 | U3 u3-sse | | U2 |
| 8 | B8 | U7 u7-vfs | | U1 |
| 9 | B9 | U8 u8-process-spawn | | U5, U7 |
| 10 | B10 | U10 u10-probe-aube-native | | U3, U6, U7, U8, U9 |
| 11 | B11 | U11 u11-wasm-launcher | | U10 |
| 12 | B12 | U13 u13-windows-host | | U10 |
| 13 | B13 | U12 u12-macos-host | | U10 |
| 14 | B14 | U14 u14-jit-wasm | | U11 |
| 15 | B15 | U15 u15-release | | U11, U12, U13, U14 |

どの Bolt も、その時点で依存の済んだ Unit だけを作ります。依存関係（`unit-of-work-dependency.md`）は守っています。

## 各 Bolt

### B1：U1 u1-skeleton（細い一本）

- **通すもの**：ELF の読み込み → デコード → 整数命令の最小限 → ソフトウェア MMU → `write`・`exit_group`・`brk` → ホストの標準出力。この流れを、ネイティブの Linux で最初から最後まで通します。
- **完了の条件**：
  - static-musl の hello world を、ネイティブの x86-64 Linux で直接動かした結果と、エミュレータで動かした結果を比べます。標準出力と終了コードが一致することを、コマンドで示します。
  - CI（3 つの OS での単体テスト、lint、依存の検査）が通ります。
  - **wasm のスレッドの確認結果を報告します**（Q7）。確認するのは次の 2 点です。
    - SharedArrayBuffer を共有した Worker で、アドレスで待つ・起こすが動くか
    - Worker を誰が作るのが妥当か
  - 確認コマンドを決めて記録します（Q9）。
- **確かめたい仮説**：部品を Host の trait を通して一方向につないだ構成で、hello world がネイティブと同じに動くこと。そして、同じ trait が wasm でも成り立ちそうなこと。
- **見せるもの**：`paludarium ./hello` の出力と終了コードを、ネイティブの `./hello` と並べて見せます。あわせて、wasm のスレッドの確認の報告を見せます。
- **判断点**：wasm の確認の結果が悪ければ、B2（U4）と B4（U5）に入る前に、Mmu・Host の trait・取り決め C2・C4 の形を見直します（Q7）。

### B2：U4 u4-memory-signals

- **完了の条件**：mmap・munmap・mprotect・brk と、ページフォールトを差分テストで確かめます。時刻とシグナルの基本も確かめます。
- **確かめたい仮説**：ソフトウェア MMU で、Linux のメモリの振る舞いをネイティブと同じに再現できること。
- **見せるもの**：メモリを使う小さなゲストが、ネイティブと同じ結果になること。

### B3：U2 u2-integer-isa

- **完了の条件**：整数命令とフラグを、命令単位の差分テストで確かめます。原子的な命令（lock 接頭辞付きの命令、xchg、cmpxchg）を含めます。未定義の命令では SIGILL になります。
- **確かめたい仮説**：命令単位の差分テストで、意味の誤りを早く見つけられること（Q6 の心配 C）。
- **見せるもの**：命令ごとの差分テストの一覧と、その合否。

### B4：U5 u5-threads-futex

- **完了の条件**：スレッドを作れること。futex（FUTEX_WAIT_BITSET を含む）で待ち合わせができること。スレッドのテストには時間切れの上限を付け、安定して通ることを確かめます。
- **確かめたい仮説**：Host の最小の道具（待つ・起こす・眠る）の上に、Kernel の中で futex を作れること（ADR-003）。
- **見せるもの**：複数のスレッドが Mutex と Condvar で待ち合わせるゲストが、ネイティブと同じに動くこと。

### B5：U6 u6-events-sockets

- **完了の条件**：eventfd2、ホストに頼らない edge-triggered の epoll、socketpair、タイマーが動くこと。AF_INET ではエラーを返すこと。
- **確かめたい仮説**：tokio の multi-thread runtime が使う仕組みを、ホストに頼らずに再現できること。
- **見せるもの**：tokio のタイマーと `UnixStream::pair` を使うゲストが動くこと。

### B6：U9 u9-terminal-io

- **完了の条件**：引数・環境変数・標準入出力・tty の判定・画面の幅が、設定どおりにゲストに見えること。
- **見せるもの**：`isatty` と画面の幅を表示するゲスト。

### B7：U3 u3-sse

- **完了の条件**：probe と aube が使う範囲の SSE 系の命令を、差分テストで確かめます。
- **見せるもの**：SSE を使うゲストが、ネイティブと同じ結果になること。

### B8：U7 u7-vfs

- **完了の条件**：
  - 仮想ファイルシステムで、作成・hard link・symlink・flock・rename・read_dir・stat 系の操作が動くこと。
  - ホストのディレクトリを見せる方式で、指定ディレクトリの外へ出られないこと。
  - パスが NULL の stat 系で EFAULT が返ること。
- **確かめたい仮説**：パスの解決を 1 か所に集めることで、外へ出さない保証をファジングで確かめられること。
- **見せるもの**：probe のファイル操作の項目が、ネイティブの Linux で PASS になること。

### B9：U8 u8-process-spawn

- **完了の条件**：仮想ファイルシステムの中の static-musl のバイナリを起動し、終了コードを受け取れること。ないものでは ENOENT が返ること。
- **見せるもの**：別のゲストを起動するゲスト。

### B10：U10 u10-probe-aube-native

- **完了の条件**：
  - probe の全項目が、ネイティブの Linux で PASS になること。
  - static-musl 版の aube の 4 コマンドと、#1645 の再現が、ネイティブと一致すること。
  - 実行時間を記録すること。
- **確かめたい仮説**：段階 2 の目標（ネイティブの Linux で probe と aube が動く）を満たせること。
- **見せるもの**：probe の PASS/FAIL の一覧と、aube の出力をネイティブと並べたもの。
- **判断点**：aube を static-musl でビルドできない場合や、node がないときに aube がネイティブと違う振る舞いをする場合は、ここで扱いを決め直します。

### B11：U11 u11-wasm-launcher

- **完了の条件**：Node.js の Worker と、Chromium 系・Firefox・Safari で、probe と aube がネイティブと同じ結果になること。
- **確かめたい仮説**：wasm でマルチスレッドのゲストが動くこと（Q6 の心配 A）。
- **見せるもの**：ブラウザで aube の 4 コマンドを動かした結果。

### B12：U13 u13-windows-host

- **完了の条件**：Windows のホストで、probe と aube がネイティブの Linux と同じ結果になること。
- **確かめたい仮説**：Windows でも、Host の trait の中で Linux の振る舞いを再現できること。

### B13：U12 u12-macos-host

- **完了の条件**：macOS のホストで、probe と aube がネイティブの Linux と同じ結果になること。

### B14：U14 u14-jit-wasm

- **完了の条件**：
  - JIT ありでも probe が全項目 PASS になり、結果が JIT なしと一致すること。
  - Node.js の Worker で各 10 回実行し、JIT ありの方が速いことを有意水準 5% で示すこと。
- **確かめたい仮説**：最小の JIT で、インタプリタより速くできること。

### B15：U15 u15-release

- **完了の条件**：タグを打つと CI から crates.io と npm に公開されること。公開の前に人が承認すること。
- **判断点**：nightly 専用のクレートを公開してよいかを、公開の前に決めます。
