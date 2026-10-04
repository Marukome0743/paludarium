# 実現性と制約：質問

## 調査の要点（質問の前提）

2026-10-04 に、Web ページと GitHub のリポジトリページを読んで調べました。コードの clone や実行はしていません。

- **blink と同等の Rust 実装で、丸ごと採用できるものは見つかりませんでした。** Rust への blink の移植も見つかっていません。
- **一番近いのは nixvm です**（github.com/KarpelesLab/nixvm、MIT）。
  - Rust 製で、x86-64 のインタプリタと 60 以上の syscall（futex・epoll・eventfd・AF_UNIX など）を持っています。
  - ただし x86-64 対応はまだ発展途上で、SSE は SSE2 までです。
  - wasm 版はシングルスレッドです。syscall は 1 つの大きなロックで直列に処理します。
  - 作者は一人で、スターは 2、crate は今日公開された 0.0.3 です。
- **命令デコーダは既存のものが使えます。**
  - iced-x86（MIT）：全命令に対応し、no_std と wasm にも対応しています。命令が読み書きするフラグの情報も取れます。
  - yaxpeax-x86（0BSD）：小さくて no_std です。
- **JIT の参考になる先行例**：copy/v86（BSD-2、32-bit のみ）と binarrow（AArch64 ゲスト、wasm 生成）。
- **使用禁止**：Blink ベースの webix・portabox 系列（履歴にマルウェアがありました）。

## Q1. 既存実装の扱いをどうしますか？

A. ハイブリッド：コアは自作し、デコーダなどの部品は既存の crate を使い、nixvm は設計の参考にする
B. nixvm を fork して、足りない部分（スレッドの並列化、SSE、wasm のマルチスレッド）を足していく
C. 外部の部品も使わず、すべて自作する
D. Not yet defined
X. Other (please specify)

[Answer]: C. 外部の部品も使わず、すべて自作する **Mode:** guided

## Q2. 命令デコーダは何を使いますか？

デコーダは、機械語のバイト列を「どの命令か・オペランドは何か」に変換する部品です。将来の JIT でも使います。

A. iced-x86（MIT。全命令に対応、フラグの読み書き情報あり、wasm 実績あり）
B. yaxpeax-x86（0BSD。小さく、wasm のサイズで有利）
C. 自作する
D. Not yet defined（設計の段階で比べて決める）
X. Other (please specify)

[Answer]: C. 自作する（Q9 の回答 B により、当初の回答 A から変更） **Mode:** guided

## Q3. 他のプロジェクトのコードを、どこまで取り込んでよいですか？

paludarium は Apache-2.0 です。blink は ISC、nixvm は MIT で、どちらも寛容なライセンスです。著作権表示を残せば取り込めますが、方針は決めておく必要があります。

A. 動作や設計を参考にするだけで、コードはコピーしない（独自実装）
B. 寛容なライセンス（ISC・MIT・BSD など）のコードは、著作権表示を残して取り込んでよい
C. blink のコードを直接 Rust に移植する（blink の派生物として ISC の表示を残す）
D. Not yet defined
X. Other (please specify)

[Answer]: A. 動作や設計を参考にするだけで、コードはコピーしない（独自実装） **Mode:** guided

## Q4. wasm での動作確認に使う起動用 JS とテスト用のハーネスは、誰が用意しますか？

意図書の成功条件では、probe が formicarium の Node.js Worker とブラウザで通る必要があります。一方で、ブラウザ側と formicarium への組み込みは範囲外です。前の工程のレビューで、この 2 つの関係があいまいだと指摘されました。

A. paludarium が wasm モジュール、最小限の起動用 JS、Node.js とブラウザ用のテストハーネスまで用意する。formicarium への本番の組み込みは formicarium 側で行う
B. paludarium は wasm モジュールと起動用 JS だけを用意する。動作確認は formicarium 側のハーネスで行う
C. Not yet defined
X. Other (please specify)

[Answer]: A. paludarium が wasm モジュール、最小限の起動用 JS、Node.js とブラウザ用のテストハーネスまで用意する。formicarium への本番の組み込みは formicarium 側で行う **Mode:** guided

## Q5. ネイティブ環境では、どの OS をホストとして合格条件に含めますか？

前の工程では、ネイティブ環境（Linux・macOS・Windows）で使う人も利用者に入りました。ゲストの Linux の syscall（futex、epoll、flock など）をホスト OS の機能に対応させる手間は、OS ごとに大きく違います。特に Windows は差が大きいです。

A. Linux（x86-64 と arm64）だけを合格条件にする。他の OS は後で
B. Linux と macOS を合格条件にする
C. Linux・macOS・Windows のすべてを合格条件にする
D. Not yet defined
X. Other (please specify)

[Answer]: C. Linux・macOS・Windows のすべてを合格条件にする **Mode:** guided

## Q6. ゲストのプログラムを、ホストからどこまで隔離しますか？

vivarium では、他人が報告したバグを再現するために、信頼できないバイナリを動かすことがあります。ゲストからホストのファイルが見えるかどうかは、安全性に直結します。

A. ゲストは仮想のファイルシステムだけを見る。ホストのファイルは、明示的に指定したディレクトリだけを見せる
B. ネイティブ環境では、ホストのファイルシステムをそのまま見せてよい（qemu-user や blink と同じ）
C. 両方を選べるようにし、既定は A にする
D. Not yet defined
X. Other (please specify)

[Answer]: C. 両方を選べるようにし、既定は A にする **Mode:** guided

## Q7. JIT の速さは、どの環境で比べますか？

前の工程のレビューで、JIT の成功条件「JIT なしより速くなる」の比べ方が決まっていないと指摘されました。JIT はまず wasm 向けに作ります。

A. Node.js の Worker で比べる
B. ブラウザ（Chromium 系）で比べる
C. Node.js の Worker とブラウザの両方で比べる
D. Not yet defined（要件分析で決める）
X. Other (please specify)

[Answer]: A. Node.js の Worker で比べる（聞き直しで確定） **Mode:** guided

## Q8. 開発と CI で使える環境に制約はありますか？

A. GitHub（Actions と Pages）だけを使う。クラウドのアカウントや有料サービスは使わない
B. GitHub に加えて、必要ならクラウドの実行環境も使ってよい
C. Not yet defined
X. Other (please specify)

[Answer]: B. GitHub に加えて、必要ならクラウドの実行環境も使ってよい（聞き直しで確定） **Mode:** guided

## Q9. Q1 と Q2 の回答の関係を確かめます

Q1 では「外部の部品も使わず、すべて自作する」を選び、Q2 では「iced-x86（外部の crate）をデコーダに使う」を選びました。この 2 つは食い違って見えます。どちらの意味ですか？

A. 外部の部品は使わない、の例外としてデコーダだけ iced-x86 を使う
B. 外部の部品は使わない、を優先する。デコーダも自作する（Q2 は C に変える）
C. Q1 の「自作」は、エミュレータの中身（CPU・MMU・syscall・スレッド）のことを指す。デコーダやテスト用などの汎用の crate は、必要に応じて使ってよい
D. Not yet defined
X. Other (please specify)

[Answer]: B. 外部の部品は使わない、を優先する。デコーダも自作する（Q2 は C に変える） **Mode:** guided

## Consolidated Summary Confirmation

- Q1・Q9：既存実装は採用せず、外部の部品も使わずにすべて自作する
- Q2：命令デコーダも自作する（Q9 により A から C に変更）
- Q3：他のプロジェクトは動作や設計を参考にするだけで、コードはコピーしない（独自実装）
- Q4：paludarium が wasm モジュール、最小限の起動用 JS、Node.js とブラウザ用のテストハーネスまで用意する。formicarium への本番の組み込みは formicarium 側で行う
- Q5：ネイティブ環境の合格条件には、Linux・macOS・Windows のすべてを含める
- Q6：ゲストの隔離は、仮想ファイルシステムだけを見せる方式とホストをそのまま見せる方式を選べるようにし、既定は仮想ファイルシステムにする
- Q7：JIT の効果は Node.js の Worker で、JIT ありとなしの時間を比べて測る
- Q8：開発と CI は GitHub に加えて、必要ならクラウドの実行環境も使ってよい

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
