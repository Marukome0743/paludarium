# 意図書：Rust 版 blink（paludarium）

## Problem Statement

- jart/blink（C 製の x86-64 Linux ユーザーモードエミュレータ、ISC）と同等のものを Rust で再実装する。[desc]
- Rust で作り直す一番の理由は、安全性と保守性を上げることである。[Q1]
- 将来は、このエミュレータで formicarium のエミュレータコアを置き換える。境界は「wasm モジュール 1 つ＋起動用 JS」である。[desc]
- 最初に、blink と同等の既存 Rust 実装がないかを調べる。使えるものがなければ自分で作る。[desc]

## Target Customer

- formicarium：ブラウザ側と統合を担い、このエミュレータをコアとして使う。[Q2] [desc]
- vivarium：formicarium を通して、CLI のバグ再現に使う。[Q2]
- 一般の利用者：ユーザーモード x86-64 Linux エミュレータの OSS として使う。[Q2]
- ネイティブ環境（wasm ではない Linux / macOS / Windows）で使う人。[Q2]

## Success Metrics

- 必須条件 1：formicarium の合格判定用 probe（tokio・rayon・ファイル操作）が、ネイティブ環境で全項目通る。[Q3]
- 必須条件 2：同じ probe が、wasm モジュール 1 つ＋起動用 JS として、formicarium の Node.js Worker とブラウザでも全項目通る。[Q3]
- 「blink と同等」の範囲：probe と aube が必要とする範囲から始めて、そこから広げる。その中で、blink に欠けている eventfd・FUTEX_WAIT_BITSET・ホストに頼らない edge-triggered epoll も作る。[Q4]
- JIT の成功条件：JIT を有効にしても probe が全項目通り、かつ JIT なしより速くなる。比べる対象は、同じ環境で同じ probe を JIT ありとなしで実行した時間とする。[Q10]

## Initiative Trigger

- 期限はない。formicarium の PoC（既存の blink を使う）と並行して進める。[Q5]
- 動機は、安全性と保守性の高い Rust 版を自分たちで持つこと。[Q1]

## Initial Scope Signal

- workflow-selected のスコープは `rust-blink-port`。[scope]
- ユーザーが確かめた範囲（Q8）：既存実装の調査と採用・自作の判断、要件と設計、エミュレータコアの実装・テスト・CI。これに加えて JIT も含める。[Q8]
- JIT は、まず wasm 向け（x86-64 → wasm）を作る。ネイティブ向けは後で考える。[Q9]
- ブラウザ側（Worker・ページ・ファイルシステム）と formicarium への組み込み作業は、この範囲に含めない。[Q8]

## Assumptions & Open Questions

None.
