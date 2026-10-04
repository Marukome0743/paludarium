# ドメイン設計：質問

要件書（`requirements.md`）とチームの進め方（`team-practices.md` の Code Style にある層の分け方）をもとに、部品（コンポーネント）の分け方で決めることを質問にしました。

## 前提：部品の候補

チームの進め方には、decoder・cpu・mmu・loader・linux（syscall）・vfs・host・jit の層に分け、依存は一方向にすると書かれています。これを部品の候補にしました。

- **Decoder**：機械語を命令に変換する（既存の crate を包む）
- **Cpu**：レジスタ・フラグを持ち、命令を実行する（インタプリタ）
- **Mmu**：ゲストのアドレス空間と、読み書きの権限を管理する
- **Loader**：ELF を読み込み、最初のスタック（引数・環境変数）を積む
- **Kernel**：syscall を受け付け、プロセス・スレッド・ファイル記述子・シグナル・futex・epoll などを扱う
- **Vfs**：仮想ファイルシステムと、ホストのディレクトリを見せる仕組み
- **Host**：ホストごとの違い（スレッド、時刻、待機と起床、標準入出力、端末、ホストのファイル）を 1 か所にまとめる。ネイティブ用と wasm 用の実装を持つ
- **Jit**：wasm 向けの JIT
- **Runtime**：外から使う入口。設定を受け取り、ゲストを起動して終了コードを返す
- **Launcher**（JS）：wasm モジュールを Worker で起動する
- **Harness**：差分テスト・probe・aube のテストを動かす

## Q1. Kernel と Vfs は、別の部品に分けますか？

A. 分ける。Kernel は syscall の受付とプロセス・スレッド・待機などを担い、ファイルの中身とパスの解決は Vfs が担う
B. まとめて 1 つの Kernel にする（部品は少なくなるが、Kernel が大きくなる）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 分ける。Kernel は syscall の受付とプロセス・スレッド・待機などを担い、ファイルの中身とパスの解決は Vfs が担う **Mode:** guided

## Q2. スレッドのレジスタの状態は、どの部品が持ちますか？

ゲストのスレッドごとに、レジスタやフラグの状態があります。

A. Kernel がプロセスとスレッドを持ち、レジスタの状態もスレッドの一部として持つ。Cpu は渡された状態を実行するだけ
B. Cpu がレジスタの状態を持ち、Kernel はスレッドの番号で参照する
C. Not yet defined
X. Other (please specify)

[Answer]: A. Kernel がプロセスとスレッドを持ち、レジスタの状態もスレッドの一部として持つ。Cpu は渡された状態を実行するだけ **Mode:** guided

## Q3. futex・epoll・eventfd などの「待つ」仕組みは、どこで作りますか？

要件では、epoll はホストの epoll に頼らずに作ることになっています（FR2.5）。

A. Kernel が futex・epoll・eventfd の仕組みを自分で持つ。Host は「あるアドレスで待つ」「起こす」「時間付きで眠る」という最小の道具だけを用意する（wasm では Atomics、ネイティブでは OS の同等の機能）
B. futex はホストの同等の機能（Linux の futex、macOS・Windows の対応する機能）にそのまま任せ、epoll と eventfd だけ Kernel で作る
C. Not yet defined
X. Other (please specify)

[Answer]: A. Kernel が futex・epoll・eventfd の仕組みを自分で持つ。Host は「あるアドレスで待つ」「起こす」「時間付きで眠る」という最小の道具だけを用意する **Mode:** guided

## Q4. Cpu と Kernel のつなぎ方はどうしますか？

ゲストが syscall 命令を実行したり、ページフォールトを起こしたりすると、Cpu から Kernel に処理を渡す必要があります。

A. Cpu は「syscall が来た」「フォールトが起きた」などの理由を返して止まる。スレッドごとの実行ループ（Runtime の一部）がその理由を見て Kernel を呼び、終わったら Cpu を再開する。Cpu は Kernel を知らない
B. Cpu が Kernel を直接呼ぶ（呼び出し用の決まった型を通す）
C. Not yet defined
X. Other (please specify)

[Answer]: A. Cpu は理由を返して止まる。スレッドごとの実行ループ（Runtime の一部）が Kernel を呼び、Cpu を再開する。Cpu は Kernel を知らない **Mode:** guided

## Q5. Jit は Cpu とどう分けますか？

A. Jit は独立した部品にする。実行ループが、Jit に変換済みのものがあればそれを使い、なければ Cpu（インタプリタ）で実行する。Jit は Decoder と Mmu を使う
B. Jit を Cpu の中に入れる
C. Not yet defined
X. Other (please specify)

[Answer]: A. Jit は独立した部品にする。実行ループが変換済みのものを使い、なければ Cpu（インタプリタ）で実行する。Jit は Decoder と Mmu を使う **Mode:** guided

## Q6. ネイティブ版は、どの形で使えるようにしますか？

A. ライブラリ（Runtime の API）と、コマンド（例：`paludarium ./hello`）の両方
B. ライブラリだけ
C. コマンドだけ
D. Not yet defined
X. Other (please specify)

[Answer]: A. ライブラリ（Runtime の API）と、コマンド（例：paludarium ./hello）の両方 **Mode:** guided

## Consolidated Summary Confirmation

- 部品の候補：Decoder・Cpu・Mmu・Loader・Kernel・Vfs・Host・Jit・Runtime・Launcher（JS）・Harness
- Q1：Kernel と Vfs は分ける。ファイルの中身とパスの解決は Vfs が担う
- Q2：Kernel がプロセスとスレッドを持ち、レジスタの状態もスレッドの一部として持つ。Cpu は渡された状態を実行するだけ
- Q3：futex・epoll・eventfd の仕組みは Kernel が持つ。Host は「アドレスで待つ・起こす・時間付きで眠る」の最小の道具だけを用意する
- Q4：Cpu は止まった理由を返すだけ。スレッドごとの実行ループ（Runtime）が Kernel を呼び、Cpu を再開する。Cpu は Kernel を知らない
- Q5：Jit は独立した部品。実行ループが変換済みのものを使い、なければ Cpu で実行する。Jit は Decoder と Mmu を使う
- Q6：ネイティブ版は、ライブラリ（Runtime の API）とコマンドの両方で使える

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
