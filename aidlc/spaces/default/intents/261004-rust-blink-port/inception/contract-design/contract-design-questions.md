# 取り決めの設計：質問

Unit の依存関係（`unit-of-work-dependency.md`）と部品の一覧（`components.md`）から、取り決め（契約）が要る境界を挙げました。

- **内部の境界**（同じプロセスの中で、Rust の型と関数で呼び合う）：Host の trait、Cpu が止まった理由（ExitReason）、Kernel の syscall の振り分け、Vfs の API、Mmu の API、Decoder の API、Jit と実行ループの口
- **外部の境界**（外の人が使う）：
  - Runtime の公開 API（crates.io のライブラリ）
  - コマンド（Cli）
  - 起動用 JS（npm のパッケージ。formicarium との境界）

## Q1. 内部の取り決めは、どう表し、誰が持ちますか？

A. Rust の trait と型で表し、提供する側のクレートが持つ。複数のクレートで使う小さな型（GuestAddr・errno・ExitReason など）は、共通の小さなクレート（例：`paludarium-types`）にまとめる
B. すべての内部の取り決めを、1 つの取り決め専用のクレートに集める
C. Not yet defined
X. Other (please specify)

[Answer]: A. Rust の trait と型で表し、提供する側のクレートが持つ。共通の小さな型は paludarium-types にまとめる **Mode:** guided

## Q2. 起動用 JS（formicarium が使う境界）の API の形はどうしますか？

A. ES モジュールの Promise ベース：`createPaludarium({ wasmUrl })` で用意し、`run({ program, args, env, files, tty, stdin, onStdout, onStderr })` が終了状態（終了コードかシグナル）で解決する。途中で止める `kill()` を持つ
B. Web Streams ベース：標準入出力を ReadableStream・WritableStream でつなぐ。それ以外は A と同じ
C. Not yet defined（U11 で決める）
X. Other (please specify)

[Answer]: B. Web Streams ベース：標準入出力を ReadableStream・WritableStream でつなぐ。それ以外は A と同じ（createPaludarium で用意し、run が終了状態で解決し、kill() を持つ） **Mode:** guided

## Q3. 公開する取り決め（Rust の API・コマンド・JS の API）の版の付け方と、壊す変更の扱いはどうしますか？

A. セマンティック バージョニングに従う。0.x の間は、minor を上げて壊す変更をしてよい。壊す変更は変更履歴に書き、JS の API を壊すときは事前に formicarium 側と合わせる
B. 最初から 1.0 として、壊す変更は major を上げるときだけにする
C. Not yet defined
X. Other (please specify)

[Answer]: A. セマンティック バージョニング。0.x の間は minor で壊す変更をしてよい。変更履歴に書き、JS の API を壊すときは事前に formicarium と合わせる **Mode:** guided

## Q4. 境界での失敗は、どう返しますか？

A. エミュレータ自身の問題（未実装・内部の矛盾）と、ゲストの終了（終了コードやシグナル）を型で分ける。Rust では `Result<ExitStatus, Error>`、JS では「終了状態で解決」と「エミュレータのエラーで reject」に分ける。エラーには、命令のアドレス・バイト列・syscall の番号を添える
B. どちらもまとめて 1 つのエラー型で返す
C. Not yet defined
X. Other (please specify)

[Answer]: A. エミュレータ自身の問題とゲストの終了を型で分ける。Rust は Result<ExitStatus, Error>、JS は終了状態で解決・エラーで reject。エラーに命令のアドレス・バイト列・syscall の番号を添える **Mode:** guided

## Q5. コマンド（Cli）の使い方の形はどうしますか？

A. `paludarium [options] <program> [args...]`。主な options は、ホストのディレクトリを見せる `--mount <host>:<guest>`、環境変数の `--env KEY=VALUE`、JIT を切る `--no-jit`（ネイティブでは JIT はない）。ゲストの終了コードで終わる
B. Not yet defined（U1 で決める）
X. Other (please specify)

[Answer]: A. paludarium [options] <program> [args...]。--mount <host>:<guest>、--env KEY=VALUE、--no-jit など。ゲストの終了コードで終わる **Mode:** guided

## Consolidated Summary Confirmation

- Q1：内部の取り決めは Rust の trait と型で表し、提供する側のクレートが持つ。共通の小さな型（GuestAddr・errno・ExitReason など）は paludarium-types にまとめる
- Q2：起動用 JS の API は Web Streams ベース。標準入出力を ReadableStream・WritableStream でつなぎ、createPaludarium で用意し、run が終了状態で解決し、kill() を持つ
- Q3：セマンティック バージョニング。0.x の間は minor で壊す変更をしてよい。変更履歴に書き、JS の API を壊すときは事前に formicarium と合わせる
- Q4：エミュレータ自身の問題とゲストの終了を型で分ける。Rust は Result<ExitStatus, Error>、JS は終了状態で解決・エラーで reject。エラーに命令のアドレス・バイト列・syscall の番号を添える
- Q5：コマンドは paludarium [options] <program> [args...]。--mount、--env、--no-jit など。ゲストの終了コードで終わる

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
