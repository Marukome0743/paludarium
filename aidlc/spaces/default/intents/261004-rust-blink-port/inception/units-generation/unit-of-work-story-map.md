# 要件と Unit の対応：Rust 版 blink（paludarium）

上流の成果物：`inception/requirements-analysis/requirements.md`。

この計画ではユーザーストーリーの工程を飛ばしているので、ストーリーの代わりに機能要件（FR）を Unit に対応させます。

## 対応表

| 要件 | 内容 | Unit ID | Directory | ほかに関わる Unit |
|------|------|---------|-----------|-------------------|
| FR1 | ゲストの読み込みと命令の実行 | U1 | u1-skeleton | U2, U3 |
| FR1.1 | static-musl の ELF の読み込みと起動 | U1 | u1-skeleton | |
| FR1.2 | 既存のデコーダの crate を使う | U1 | u1-skeleton | U3 |
| FR1.3 | 整数命令とフラグ | U2 | u2-integer-isa | U1 |
| FR1.4 | SSE 系の命令 | U3 | u3-sse | |
| FR1.5 | ソフトウェア MMU | U1 | u1-skeleton | U4, U11 |
| FR1.6 | 未対応の命令で SIGILL | U2 | u2-integer-isa | |
| FR2 | Linux の syscall | U4 | u4-memory-signals | U1, U5, U6, U7, U8 |
| FR2.1 | 実装した syscall だけを扱い、未実装は ENOSYS | U1 | u1-skeleton | |
| FR2.2 | メモリの syscall | U4 | u4-memory-signals | |
| FR2.3 | スレッドと futex | U5 | u5-threads-futex | |
| FR2.4 | eventfd2 | U6 | u6-events-sockets | |
| FR2.5 | edge-triggered epoll | U6 | u6-events-sockets | |
| FR2.6 | socketpair | U6 | u6-events-sockets | |
| FR2.7 | ネットワークはエラー | U6 | u6-events-sockets | |
| FR2.8 | 別のプログラムの起動 | U8 | u8-process-spawn | |
| FR2.9 | 時刻・待機・シグナル | U4 | u4-memory-signals | |
| FR2.10 | NULL パスの stat 系は EFAULT | U7 | u7-vfs | |
| FR3 | ファイルシステム | U7 | u7-vfs | |
| FR3.1 | 既定は仮想ファイルシステム | U7 | u7-vfs | U1 |
| FR3.2 | ホストのディレクトリを見せ、外へ出さない | U7 | u7-vfs | |
| FR3.3 | ファイルの操作 | U7 | u7-vfs | |
| FR3.4 | 起動前のファイルの配置 | U7 | u7-vfs | U1 |
| FR4 | 入出力と実行環境 | U9 | u9-terminal-io | |
| FR4.1 | 引数・環境変数・標準入出力 | U9 | u9-terminal-io | U1 |
| FR4.2 | 端末の機能 | U9 | u9-terminal-io | |
| FR5 | ホスト | U11 | u11-wasm-launcher | U1, U12, U13 |
| FR5.1 | ネイティブの Linux・macOS・Windows | U1 | u1-skeleton | U12, U13 |
| FR5.2 | wasm モジュールと起動用 JS | U11 | u11-wasm-launcher | |
| FR5.3 | Node.js の Worker と 3 種類のブラウザ | U11 | u11-wasm-launcher | |
| FR5.4 | ゲストのスレッドの割り当て | U5 | u5-threads-futex | U11 |
| FR6 | probe | U10 | u10-probe-aube-native | U11, U12, U13 |
| FR6.1 | formicarium と同じ項目の probe | U10 | u10-probe-aube-native | |
| FR6.2 | probe を static-musl でビルド | U10 | u10-probe-aube-native | |
| FR6.3 | probe がすべての環境で PASS | U10 | u10-probe-aube-native | U11, U12, U13 |
| FR6.4 | probe の項目は formicarium と同時に変える | U10 | u10-probe-aube-native | probe の項目の一覧を U10 で持ち、formicarium の一覧と突き合わせる |
| FR7 | aube | U10 | u10-probe-aube-native | U11, U12, U13 |
| FR7.1 | static-musl 版 aube のビルド | U10 | u10-probe-aube-native | |
| FR7.2 | 4 コマンドがネイティブと一致 | U10 | u10-probe-aube-native | U11, U12, U13 |
| FR7.3 | #1645 の再現がネイティブと一致 | U10 | u10-probe-aube-native | U11, U12, U13 |
| FR7.4 | 実行時間の記録 | U10 | u10-probe-aube-native | U11 |
| FR8 | JIT | U14 | u14-jit-wasm | |
| FR8.1 | wasm 向け JIT の最小版 | U14 | u14-jit-wasm | |
| FR8.2 | JIT でも probe が PASS し、結果が一致 | U14 | u14-jit-wasm | |
| FR8.3 | JIT ありの方が統計的に速い | U14 | u14-jit-wasm | |
| FR9 | 検証の仕組み | U1 | u1-skeleton | U11 |
| FR9.1 | 差分テスト | U1 | u1-skeleton | すべての Unit |
| FR9.2 | 起動用 JS とテストハーネス | U11 | u11-wasm-launcher | |
| FR9.3 | ファジング | U1 | u1-skeleton | U2, U7 |
| FR10 | 公開 | U15 | u15-release | |
| FR10.1 | crates.io と npm への公開 | U15 | u15-release | |

## 複数の Unit にまたがる要件

- **FR5.1**：U1（Linux）、U12（macOS）、U13（Windows）に分かれます。
- **FR6.3・FR7.2・FR7.3**：U10（ネイティブの Linux）、U11（wasm）、U12・U13（macOS・Windows）のそれぞれで確かめます。
- **FR9.1**：差分テストは U1 で作り、すべての Unit が命令や syscall を足すたびにケースを足します。

## Unit の中での順番

各 Unit の中では、次の順で作ります（team-practices の Testing Posture）。

1. 命令・syscall・プログラムの差分テストのケースを先に用意し、ネイティブでの期待結果を決める
2. 実装する
3. 内部の部品の単体テストを書く

## 網羅の確認

- **要件の側**：すべての要件が、Unit に割り当たっています。FR6.4 は、U10 が probe の項目の一覧を持ち、formicarium の一覧と突き合わせることで扱います。
- **Unit の側**：すべての Unit が、少なくとも 1 つの要件を持っています。U12 と U13 は FR5.1 を、U15 は FR10.1 を持ちます。
