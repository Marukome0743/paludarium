# 機能設計（u2-integer-isa）：質問

## Sources

- `inception/units-generation/unit-of-work.md` の U2：probe と aube が使う整数命令・フラグ、未対応命令の SIGILL、原子的な命令の担当を決める。
- `inception/units-generation/unit-of-work-story-map.md`：FR1.3・FR1.6 は U2、スレッドの作成と futex は U5。
- `inception/requirements-analysis/requirements.md`：ネイティブとレジスタ・定義済みフラグ・メモリを比較する。未定義フラグは比較しない。
- `inception/contract-design/reviews/review-01.md` の R-02：lock・xchg・cmpxchg の原子操作と共有メモリの排他をどの Unit が実装するか未決。

整数命令の対象、既存デコーダの利用、差分テストを先に用意する順番、未定義フラグの除外、未対応命令の SIGILL は決定済みなので聞き直しません。

## Q1. lock 接頭辞付き命令や、メモリとの xchg・cmpxchg の原子性は、どの段階で実装しますか？

これらは、複数のスレッドが同じメモリを更新しても途中の状態を見せないための命令です。整数命令は U2、スレッドと futex は U5 に分かれているため、実装の担当をここで確定する必要があります。

A. U2 で Cpu の命令処理と Mmu の原子的な更新を実装する。ホストの並行テストで更新の不可分性も確かめ、ゲストの clone・futex を使う統合テストは U5 で加える（推奨）
B. U2 では責任分担と契約を設計し、原子的な命令の実装と並行テストは U5 にまとめる。U2 の完了記録には未対応として明示する
X. Other (please specify)

[Answer]: A. U2 で実装 (Recommended) — Cpu と Mmu の原子操作・ホストの並行テストを U2 で作り、ゲストの clone・futex を使う統合テストは U5 で追加する **Mode:** guided

## Consolidated Summary Confirmation

- 整数命令は、既定どおり probe と aube が使う範囲を対象にする（要件 FR1.3、Unit U2）。
- レジスタ・定義済みフラグ・メモリをネイティブの x86-64 Linux と比較し、未定義のフラグは命令・条件ごとに除外表を持つ。
- 未対応・不正な命令はゲストの SIGILL として扱い、エミュレータの panic にしない（要件 FR1.6）。
- Q1：lock・メモリ xchg・cmpxchg の原子性は U2 で実装する。Cpu は命令の意味論、Mmu は共有メモリの不可分な更新を担当する。
- 原子的な更新のホストの並行テストを U2 で実施し、ゲストの clone・futex を使う統合テストは U5 で追加する。
- 命令の差分テストを先に用意し、内部の部品の単体テストは実装後に書く（承認済みの Testing Posture）。

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
