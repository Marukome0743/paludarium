# 設計判断の記録（ADR）：Rust 版 blink（paludarium）

上流の成果物：
- `inception/requirements-analysis/requirements.md`
- `inception/practices-discovery/team-practices.md`

根拠は `domain-design-questions.md` の回答（Q1〜Q6）です。

## ADR-001: Kernel と Vfs を別の部品にする

- **Context**：syscall の受付とプロセス・スレッドの管理に加え、ファイルの中身とパスの解決が要る。ホストのファイルを見せる方式でも、指定ディレクトリの外へ出さないことを保証する必要がある（project.md の Mandated、FR3.2）。
- **Decision**：Kernel と Vfs を分ける。ファイルの中身・パスの解決・flock は Vfs が担い、Kernel はファイル記述子から Vfs を呼ぶ（Q1）。
- **Consequences**：
  - 良い点：ディレクトリの外へ出さない保証を Vfs だけで確かめられる。ファジングの対象を絞れる。
  - 悪い点：ファイル記述子（Kernel）と Inode（Vfs）の間の参照を、境界をまたいで扱う必要がある。
- **Alternatives Rejected**：
  - Kernel にまとめる案：部品は少なくなるが、Kernel が大きくなりすぎる。

## ADR-002: スレッドのレジスタの状態は Kernel が持つ

- **Context**：clone・execve・シグナルの配送は、スレッドのレジスタの状態を読み書きする。Cpu はその状態を実行に使う。
- **Decision**：Kernel がプロセスとスレッドを持ち、レジスタの状態（汎用レジスタ・フラグ・SSE レジスタ）もスレッドの一部として持つ。Cpu は渡された状態を実行するだけ（Q2）。
- **Consequences**：
  - 良い点：Cpu が状態を持たないので、Cpu を単独でテストしやすい。Jit も同じ状態を使える。
  - 悪い点：実行ループは、Kernel のスレッドの状態を Cpu に渡す必要がある。
- **Alternatives Rejected**：
  - Cpu が持つ案：clone やシグナルのたびに、Kernel が Cpu の中の状態を操作する必要があり、依存が逆向きになる。

## ADR-003: futex・epoll・eventfd は Kernel が持ち、Host は最小の道具だけを用意する

- **Context**：epoll はホストに頼らずに作る要件がある（FR2.5）。wasm では、待つ手段は Atomics の wait と notify しかない。macOS と Windows には Linux の futex がない。
- **Decision**：futex（FUTEX_WAIT_BITSET を含む）・epoll（edge-triggered）・eventfd の仕組みは、Kernel が自分で持つ。Host が用意するのは「アドレスで待つ」「起こす」「時間付きで眠る」の 3 つだけ（Q3）。
- **Consequences**：
  - 良い点：すべてのホストで同じ意味になる。Host の実装が小さくなる。
  - 悪い点：Kernel の中で待ち行列を正しく作る必要があり、競合の不具合が入りやすい。差分テストとスレッドのテストで確かめる。
- **Alternatives Rejected**：
  - futex をホストの同等の機能に任せる案（Q3 の B）：ホストごとに意味がずれ、wasm では使えない。

## ADR-004: Cpu は止まった理由を返し、実行ループが Kernel を呼ぶ

- **Context**：syscall 命令・ページフォールト・未対応の命令では、Cpu から Kernel に処理を渡す必要がある。依存を一方向にする決まりがある（team-practices の Code Style）。
- **Decision**：Cpu は止まった理由（ExitReason）を返して止まる。スレッドごとの実行ループ（Runtime）がその理由を見て Kernel を呼び、終わったら Cpu を再開する。Cpu は Kernel を知らない（Q4）。
- **Consequences**：
  - 良い点：Cpu → Kernel の依存がなくなり、循環しない。Cpu を差分テストで単独で確かめられる。Jit も同じ形で止まれる。
  - 悪い点：syscall のたびに実行ループを経由するので、少し遅くなる。
- **Alternatives Rejected**：
  - Cpu が Kernel を直接呼ぶ案（Q4 の B）：Cpu が Kernel に依存し、層が一方向でなくなる。

## ADR-005: Jit は独立した部品にする

- **Context**：JIT は段階 5 で加わり、インタプリタと同じ結果になることを差分テストで確かめる（FR8.2）。
- **Decision**：Jit を独立した部品にする。実行ループが変換済みのものがあれば使い、なければ Cpu で実行する。Jit は Decoder と Mmu を使う（Q5）。
- **Consequences**：
  - 良い点：JIT の有無を設定で切り替えられ、ありとなしを比べやすい。段階 1〜4 は Jit なしで進められる。
  - 悪い点：Cpu と Jit で命令の意味論を二重に持つことになる。差分テストでそろっていることを確かめる。
- **Alternatives Rejected**：
  - Cpu の中に入れる案（Q5 の B）：Cpu が大きくなり、Jit なしの段階でも Jit の都合が Cpu に入り込む。

## ADR-006: デコーダは既存の crate を Decoder で包んで使う

- **Context**：技術選定の方針は「基本的に外部のものを使ってよい。著作権・ライセンスに関わるもの、不具合があるものは自作」（project.md の Mandated）。デコーダは iced-x86 などを使うと決めた（practices-discovery Q14）。
- **Decision**：Decoder の部品で既存の crate を包む。ほかの部品にはこの部品の型だけを見せる。
- **Consequences**：
  - 良い点：crate に不具合や合わないところがあれば、Decoder の中だけで差し替えや一部の自作ができる。
  - 悪い点：包むための変換のコストがかかる。
- **Alternatives Rejected**：
  - crate の型を各部品で直接使う案：差し替えるときに影響が広がる。
  - 最初から自作する案：方針が変わったので採らない。

## ADR-007: ネイティブと wasm の違いは Host だけに閉じ込める

- **Context**：ホストは Linux・macOS・Windows・wasm の 4 種類（FR5）。ほかの層から std::thread・std::fs・std::time を直接呼ばない決まりがある（team-practices の Code Style）。
- **Decision**：Host の部品に、ホストの機能の trait を置き、ネイティブ用と wasm 用の実装を持つ。unsafe を許すのは Host と Jit だけ（team-practices の Code Style）。
- **Consequences**：
  - 良い点：Kernel・Vfs・Runtime はホストを知らずに書ける。段階 1 の細い一本から trait を通せば、段階 3 で書き直さずに済む。
  - 悪い点：trait の設計を誤ると、wasm に移すときに trait を変える必要がある。段階 1 の設計で wasm のスレッドを小さく確かめる（決定 D22）。
- **Alternatives Rejected**：
  - ホストごとに cfg で各部品の中を分ける案：違いがあちこちに散らばる。

## ADR-008: 使い方はライブラリ・コマンド・wasm の 3 つにする

- **Context**：利用者には formicarium（wasm）、一般の OSS 利用者、ネイティブ環境で使う人がいる（意図書）。パッケージを crates.io と npm に公開する（FR10.1）。
- **Decision**：Runtime の API（ライブラリ）、ネイティブのコマンド（Cli）、wasm モジュールと起動用 JS（Launcher）の 3 つを用意する（Q6）。
- **Consequences**：
  - 良い点：利用者ごとに合う入口がある。差分テストではコマンドを使える。
  - 悪い点：公開する入口が 3 つになり、互換性を保つ対象が増える。
- **Alternatives Rejected**：
  - ライブラリだけにする案：ネイティブで手軽に試せない。
  - コマンドだけにする案：formicarium や他のプログラムから組み込めない。

## Assumptions & Open Questions

- [assumption] wasm では、ゲストのメモリを SharedArrayBuffer に置き、すべての Worker で共有できる（ADR-007）。段階 1 の設計で確かめる。
