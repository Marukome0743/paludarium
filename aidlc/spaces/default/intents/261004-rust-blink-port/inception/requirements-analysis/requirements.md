# 要件書：Rust 版 blink（paludarium）

## 出どころ

上流の成果物：
- `ideation/intent-capture/intent-statement.md`（意図書）
- `ideation/scope-definition/scope-document.md`（範囲の文書）
- `ideation/scope-definition/intent-backlog.md`（バックログ）
- `ideation/feasibility/constraint-register.md`（制約の一覧）
- `inception/practices-discovery/team-practices.md`（チームの進め方）

根拠は `requirements-analysis-questions.md` の回答（Q1〜Q10）です。各要件の末尾の括弧に出どころを書きます。

## Intent Analysis

- **目的**：jart/blink と同等の x86-64 ユーザーモード Linux エミュレータを Rust で作り、安全性と保守性を上げる（意図書）。
- **成果**：未改変の static-musl の x86-64 Linux バイナリを、カーネルを起動せずに動かせること。動かす場所は、ネイティブの Linux・macOS・Windows と、wasm（Node.js の Worker とブラウザ）の両方（範囲の文書）。
- **最初の利用者**：formicarium。その先に、vivarium の CLI のバグ再現と、一般の OSS 利用がある（意図書）。
- **成功の判定**：probe と aube がすべての環境で動くこと。加えて、wasm 向け JIT で JIT なしより速くなること。最後に crates.io と npm に公開する（範囲の文書）。
- **要求の種類**：新規開発。複数の部品からなり、複雑さは高い。

## Glossary

| 用語 | 意味 |
|------|------|
| エミュレータ | 別の CPU 向けのプログラムを、その CPU の動きをまねて実行するソフトウェア |
| ユーザーモード | OS（カーネル）全体ではなく、アプリが OS に頼む機能（syscall）だけをまねる方式 |
| ゲスト | エミュレータの中で動かされるプログラム（x86-64 の Linux バイナリ） |
| ホスト | エミュレータ自身が動いている環境（Linux・macOS・Windows・wasm） |
| syscall | アプリが OS に処理を頼む呼び出し（ファイルを開く、スレッドを作る、など） |
| static-musl | 必要なライブラリ（musl libc）をすべて中に含めてビルドした Linux バイナリ |
| ELF | Linux の実行ファイルの形式 |
| デコーダ | 機械語のバイト列を「どの命令か」に変換する部品 |
| MMU | ゲストのメモリのアドレスを、ホストのメモリに対応させる仕組み。ここではソフトウェアで実装する |
| SSE | x86 の、複数のデータを一度に計算する命令群 |
| wasm | WebAssembly。ブラウザや Node.js で動く実行形式 |
| Worker | ブラウザや Node.js で、別のスレッドとして動く実行単位 |
| SharedArrayBuffer | 複数の Worker が同じメモリを共有するための仕組み |
| COOP/COEP | ページで SharedArrayBuffer を使えるようにするための HTTP の見出し |
| JIT | 実行中に、ゲストの命令をホスト（ここでは wasm）の命令に変換して速く動かす仕組み |
| probe | tokio・rayon・ファイル操作などが動くかを、項目ごとに PASS/FAIL で出す小さな Rust のプログラム |
| aube | Rust 製の Node.js パッケージマネージャ。vivarium で再現したい CLI の最初の例 |
| 差分テスト | 同じゲストを、ネイティブの x86-64 Linux とエミュレータの両方で動かして結果を比べるテスト |
| ファジング | でたらめな入力を大量に与えて、壊れないかを試すテスト |
| 仮想ファイルシステム | エミュレータの中だけにあるファイルシステム。ホストのファイルとは切り離されている |

## Functional Requirements

### FR1 ゲストの読み込みと命令の実行

- **FR1.1** static-musl の x86-64 ELF を読み込み、引数・環境変数・補助ベクタを積んで起動する（範囲の文書、制約 C-T4）。
  - 合否：hello world がネイティブの x86-64 Linux と同じ標準出力・終了コードで終わる。
- **FR1.2** 命令のデコードには既存のデコーダの crate（iced-x86 など）を使う。合わないところがあれば、その部分を自作する。対象は x86-64 の命令で、SSE 系までとする（team-practices の Way of Working、範囲の文書）。
  - 合否：probe と aube が実行する命令がすべてデコードできる（未対応の命令は FR1.6 で扱う）。
- **FR1.3** 整数命令とフラグの意味論を実装する（バックログ IB2）。
  - 合否：命令単位の差分テストで、レジスタ・フラグ・メモリがネイティブと一致する。未定義のフラグは比べない。
- **FR1.4** SSE 系の命令を、probe と aube が使う範囲で実装する（バックログ IB7）。
  - 合否：FR1.3 と同じ。
- **FR1.5** ゲストの 64-bit のアドレス空間を、ソフトウェア MMU で扱う。wasm32 のホストでも同じに動く（制約 C-T10）。
  - 合否：ゲストのアドレスへの読み書きが、ネイティブと wasm で同じ結果になる。範囲外の読み書きはゲストへのページフォールト（SIGSEGV）になる。
- **FR1.6** デコードできない命令や未実装の命令は、ゲストに SIGILL を送る。エミュレータ自身は panic しない（project.md の Mandated）。
  - 合否：未定義命令を含むテストで、ネイティブと同じくゲストが SIGILL で終わる。

### FR2 Linux の syscall

- **FR2.1** 実装した syscall だけを明示的に扱う。ゲストの syscall を番号のままホストに渡さない。未実装の syscall には ENOSYS を返す（project.md の Mandated・Forbidden）。
  - 合否：未実装の syscall を呼ぶテストで ENOSYS が返る。
- **FR2.2** メモリの syscall（mmap・munmap・mprotect・brk など）を実装する（バックログ IB3）。
- **FR2.3** スレッドと同期：スレッドの作成（clone）と futex を実装する。FUTEX_WAIT_BITSET を含む（意図書）。
  - 合否：probe の rayon と Mutex/Condvar の項目が PASS。
- **FR2.4** eventfd2 を実装する（意図書）。
- **FR2.5** edge-triggered の epoll を、ホストの epoll に頼らずに実装する（意図書）。
  - 合否（FR2.4・FR2.5）：probe の multi-thread tokio のタイマーの項目が PASS。
- **FR2.6** AF_UNIX の socketpair を実装する（意図書、Q9）。
  - 合否：probe の `UnixStream::pair` の項目が PASS。
- **FR2.7** ネットワーク（AF_INET などの通信と名前解決）は、どのホストでも使えないものとしてエラーを返す（Q9）。
  - 合否：AF_INET のソケットを作ると、決めたエラーが返る。aube の名前解決は失敗するが、aube の 4 コマンドはネイティブと同じ結果になる（FR7.2）。
- **FR2.8** 別のプログラムの起動：fork 相当の clone と execve を実装する。仮想ファイルシステムにある static-musl のバイナリはエミュレータの中で起動し、ないものは ENOENT を返す。子の終了は wait4 などで受け取れる（Q10）。
  - 合否：仮想ファイルシステムの中の別の static-musl バイナリを起動して終了コードを受け取れる。存在しないパスの execve で ENOENT が返る。
- **FR2.9** 時刻と待機（clock_gettime・nanosleep など）、シグナルの登録とマスク（rt_sigaction・rt_sigprocmask など）を、Rust の std と tokio が使う範囲で実装する（意図書）。
- **FR2.10** パスに NULL が渡された stat 系の syscall は EFAULT を返す（背景資料の CheerpX の不具合を繰り返さない）。
  - 合否：`stat(NULL)` 相当のテストで EFAULT が返り、エミュレータが止まらない。

### FR3 ファイルシステム

- **FR3.1** 既定では、ゲストに仮想ファイルシステムだけを見せる（制約 C-T8）。
- **FR3.2** 選んだときだけ、ホストの指定したディレクトリをゲストに見せる。`..` やシンボリックリンクで、その外へ出られないようにする（project.md の Mandated）。
  - 合否：ディレクトリの外を指すパスやシンボリックリンクへのアクセスがエラーになる。
- **FR3.3** ファイルの作成・読み書き・hard link・symlink・flock・rename・read_dir・stat 系の操作に対応する（意図書）。
  - 合否：probe のファイル操作の項目が PASS。
- **FR3.4** 起動の前に、ゲストのバイナリやテスト用のファイルを仮想ファイルシステムに置ける（Q10、FR7）。

### FR4 入出力と実行環境

- **FR4.1** 引数・環境変数・標準入力・標準出力・標準エラーを扱う（Q8）。
- **FR4.2** 端末の機能を扱う。tty かどうかの判定（ioctl の TCGETS など）と画面の幅（TIOCGWINSZ）をゲストに返せる（Q8）。
  - 合否：ゲストの `isatty` と画面の幅の取得が、設定した値を返す。

### FR5 ホスト

- **FR5.1** ネイティブの Linux・macOS・Windows で動く（制約 C-T7）。
- **FR5.2** wasm モジュール 1 つと起動用 JS として動く（制約 C-T5）。
- **FR5.3** wasm 版は、Node.js の Worker と、COOP/COEP 付きのページのブラウザ（Chromium 系・Firefox・Safari）で動く。Safari は macOS の CI で本物を使って確かめる（範囲の文書、team-practices の Testing Posture）。
- **FR5.4** ゲストのスレッドを、ネイティブではホストのスレッドに、wasm では Worker に割り当てる（バックログ IB12）。

### FR6 probe

- **FR6.1** paludarium に、formicarium と同じ項目の probe を持つ。項目は次のとおりで、項目ごとに PASS/FAIL を出す（Q2、意図書）。
  - multi-thread tokio runtime のタイマー
  - `UnixStream::pair`
  - 4 並列の rayon `par_iter` と Mutex/Condvar
  - ファイルの作成・hard link・symlink・flock
- **FR6.2** probe は static-musl の x86-64 でビルドする。
- **FR6.3** probe が、FR5 のすべての環境で全項目 PASS になる（意図書）。
- **FR6.4** probe の項目を formicarium と変えるときは、両方を同時に変える（Q2）。

### FR7 aube

- **FR7.1** paludarium の CI で、版を固定した aube のソースから static-musl の x86-64 版をビルドする（Q4）。
- **FR7.2** aube の 4 コマンド（`--version`、初回 `install`、frozen install、`list`）が、FR5 のすべての環境で、ネイティブの x86-64 Linux と同じ標準出力・終了コードになる（Q3）。
- **FR7.3** aube の不具合 #1645 の再現（frozen install と `aube list` が `0.0.0` を表示する）が、ネイティブと同じに起きる（Q3）。
- **FR7.4** 4 コマンドの実行時間を測って記録し、背景資料の CheerpX 1.3.9 上の値と並べる。目標値は置かない（Q5）。

### FR8 JIT

- **FR8.1** wasm 向けに、x86-64 の命令を wasm に変換する JIT の最小版を作る（意図書）。
- **FR8.2** JIT を有効にしても、probe が全項目 PASS になる。JIT ありと JIT なし（インタプリタ）の結果を、差分テストで比べる（意図書、team-practices の Testing Posture）。
- **FR8.3** 速さの合否：Node.js の Worker で probe 全体を JIT あり・なしで各 10 回実行する。JIT ありの実行時間が JIT なしより短く、その差が有意水準 5% で統計的に意味がある（Q1）。検定の方法は設計で決める。

### FR9 検証の仕組み

- **FR9.1** 差分テスト：CI を実行するたびに x86-64 Linux のランナーで期待結果を作り、エミュレータの結果と比べる（team-practices の Testing Posture）。
- **FR9.2** 起動用 JS とテストハーネス：Node.js の Worker と 3 種類のブラウザで、同じテストを動かせる（制約 C-T6）。
- **FR9.3** ファジング：デコーダ・ELF の読み込み・syscall の引数・仮想ファイルシステムのパスに、でたらめな入力を与える（project.md の Mandated）。

### FR10 公開

- **FR10.1** 成功条件（FR6.3、FR7.2、FR7.3、FR8.2、FR8.3）を満たしたら、crates.io と npm にパッケージを公開する。公開はタグを打って CI から行い、公開の前に人が承認する（範囲の文書、team-practices の Deployment）。

## Non-Functional Requirements

- **NFR1 正しさ**：命令単位・プログラム単位の差分テストで、ネイティブの x86-64 Linux と一致する。比べないもの（未定義のフラグ、実行ごとに変わる値）は表で持つ（team-practices の Testing Posture）。
- **NFR2 堅さ**：ゲストからどんな入力が来ても、エミュレータが panic せず、未定義動作にもならない。ファジングで確かめる（project.md の Mandated）。
- **NFR3 安全性と保守性の指標**：次の 4 つを満たす（Q7）。
  - `unsafe` がホスト接続部と JIT の外にない（`#![forbid(unsafe_code)]` で確かめる）
  - clippy の警告がゼロ
  - 行カバレッジ 80% 以上（Linux のネイティブで測る）
  - ファジングで panic や未定義動作が出ない
- **NFR4 隔離**：既定は仮想ファイルシステム（FR3.1）。ホストのファイルを見せても、指定したディレクトリの外へ出られない（FR3.2）。ネットワークは使えない（FR2.7）。syscall は番号のままホストに渡さない（FR2.1）。
- **NFR5 資源**：ゲストが使えるメモリ・スレッド・ファイルの上限は、最初は設けない（Q6）。
- **NFR6 速さ**：JIT なしの速さに目標は置かず、測って記録する（FR7.4）。JIT の合否は FR8.3。
- **NFR7 安定**：スレッドを使うテストには時間切れの上限を付ける。揺れたテストは記録して直す（team-practices の Testing Posture）。
- **NFR8 供給網**：依存の crate は crates.io からだけ取り、ライセンスが Apache-2.0 と両立することを確かめる。GitHub Actions はコミットの SHA で固定する（project.md の Mandated）。
- **NFR9 ツールチェーン**：nightly の Rust を `rust-toolchain.toml` で固定し、CI と手元で同じものを使う（team-practices の Code Style）。

## Constraints

- Rust で実装する（制約 C-T1）。
- 外部のものは基本的に使ってよい。著作権やライセンスの問題に関わるものは自作する。既存のものに不具合や合わないところがあれば、その部分は自作する（project.md の Mandated。制約 C-T2 を上書き）。
- 他のプロジェクトのコードは写さない。Blink ベースの webix・portabox の系列と `lanmower/blink` は使わない（project.md の Forbidden）。
- ゲストは static-musl の x86-64 Linux バイナリに限る（制約 C-T4）。
- formicarium との境界は「wasm モジュール 1 つ＋起動用 JS」（制約 C-T5）。
- 一人で開発し、期限はない（制約 C-O1、C-O2）。
- 開発と CI は GitHub。必要ならクラウドの実行環境も使ってよい（制約 C-E1）。
- 段階 1〜5 を番号の順に進める。最初の区切りは、ネイティブの Linux での hello world（範囲の文書）。

## Assumptions

- [assumption] aube は static-musl の x86-64 向けにビルドできる（Q4）。ビルドできなければ、そこで扱いを決め直す。
- [assumption] Safari は、Worker と SharedArrayBuffer を使ったマルチスレッドに十分対応している。また、GitHub の macOS ランナーで本物の Safari を自動で動かせる。
- [assumption] iced-x86 などのデコーダは、wasm32 でもビルドでき、SSE 系までに対応している。
- [assumption] wasm でスレッドを使う方法が、nightly の Rust で実用になる。段階 1 の設計で小さく確かめる。

## Out of Scope

- 32-bit x86 のゲスト、AVX・AVX-512 の命令（範囲の文書）
- ブラウザ側の本番実装と formicarium への組み込み（formicarium の担当）
- ネイティブ向けの JIT（後で考える）
- 動的リンクのバイナリ（成功条件に含めない）
- AF_INET などのネットワーク（FR2.7）
- 資源の上限（NFR5。最初は設けない）

## Open Questions

- aube の install は `node --version` を起動する。仮想ファイルシステムに node がないとき（FR2.8 で ENOENT）、aube がネイティブと同じ振る舞いになるかは未確認。#1645 の再現の比較条件に影響しうる。
- nightly の Rust でしかビルドできないと、crates.io で公開したライブラリの利用者が限られる。公開の前に、stable で使えるかを見直す。
- Windows の開発機では、差分テストの期待結果を手元で作れない。手元での確かめ方（WSL を使うかなど）は決まっていない。
- FR8.3 の検定の方法（例：片側のマン・ホイットニーの U 検定）は設計で決める。
- 資源の上限を設けないので、信頼できないバイナリがメモリやスレッドを使い切るおそれがある。後で上限を設けるかを見直す。
