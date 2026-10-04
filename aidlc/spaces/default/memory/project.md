# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent and cannot be changed from chat. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER ゲストの syscall を番号のままホストに渡す（面談 Q11 A）。 (affirmed 2026-10-04)

- NEVER 他のプロジェクト（jart/blink、nixvm など）のコードを写す。動作と設計を参考にするだけにする（実現性の工程 Q3、制約 C-T3）。 (affirmed 2026-10-04)

- NEVER Blink ベースの webix・portabox の系列と、その元になった Blink のフォーク `lanmower/blink` を、参照・依存・取得・実行する（履歴にマルウェアがあった。制約 C-R2、背景資料 `knowledge/documents/research/cheerpx-oss.md`）。 (affirmed 2026-10-04)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS 外部のクレートや道具を使うときは、著作権・ライセンスに問題がないことを確かめ、著作権やライセンスの問題に関わるものは自作する（面談 Q1）。 (affirmed 2026-10-04)

- ALWAYS 既存のクレートや道具に不具合や上手くいかないところがあれば、その部分は自作する（面談 Q1・Q14）。 (affirmed 2026-10-04)

- ALWAYS ゲストが実装していない syscall を呼んだら `ENOSYS` を返す。実装した syscall だけを明示的に扱う（面談 Q11 A）。 (affirmed 2026-10-04)

- ALWAYS ゲストにホストのファイルを見せる方式でも、`..` やシンボリックリンクで、指定したディレクトリの外へ出られないようにする（面談 Q11 B）。 (affirmed 2026-10-04)

- ALWAYS ゲストからどんな入力（命令のバイト列、メモリ、syscall の引数、ELF の中身）が来ても、エミュレータが panic せず、未定義動作にもならないようにし、ファジングで確かめる（面談 Q11 C）。 (affirmed 2026-10-04)

- ALWAYS GitHub Actions の action はコミットの SHA で固定する（面談 Q11 D）。 (affirmed 2026-10-04)

- ALWAYS Rust のクレートの依存は crates.io からだけ取る。ワークスペースの中のクレートを除き、git などほかの取得元からの依存は入れない（面談 Q11 D）。 (affirmed 2026-10-04)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- 承認済みの計画（rust-blink-port）は JIT を範囲外としていたが、Q8 でユーザーが JIT を範囲に含めた。以降の工程（scope-definition など）で JIT の段階分けを扱う必要がある (learned 2026-10-04) <!-- cid:261004-rust-blink-port:intent-capture:4840a2a8b12d2b7e282f64ceb1b717b9d8f28ed863646294933554af21f84eb7 -->
- Q1（すべて自作）と Q2（iced-x86 を使う）が食い違っていたので、追加質問 Q9 で確かめた。回答は B で、デコーダも自作することになり、Q2 の回答を C に変えた (learned 2026-10-04) <!-- cid:261004-rust-blink-port:feasibility:0bf80174637020827e2e7719a34f5c71cf7ba3097b814e8ed7a3596aea047483 -->
- Q5 で選ばれなかった項目（ネイティブ向け JIT、動的リンクのバイナリ）は、範囲外とも必須とも扱わない。ネイティブ向け JIT は意図書どおり「後で考える」のまま、動的リンクは成功条件に含めない (learned 2026-10-04) <!-- cid:261004-rust-blink-port:scope-definition:efeec5b7b1cbf3db1b266b738b0e6684ee2bd7a6bd5f5ac64cf536073b64dede -->
- Q1 の B（段階 1 の設計時に wasm のスレッドを小さく確かめる）は、範囲の定義で選んだ番号順を変えるものではなく、設計の中での確認として扱った。段階 3 まで待たずに R2 の兆しをつかむため (learned 2026-10-04) <!-- cid:261004-rust-blink-port:approval-handoff:f6acd2bc4b3eb3465832195d4dc201b9c8e4ebeba7e8eb960d209e987b37bc98 -->
- 面談の途中で、ユーザーが技術選定の方針を変えた（外部のものは基本的に使ってよい。著作権・ライセンスに関わるもの、不具合があるものは自作）。Q1 と Q13 の回答をこの方針に置き換え、Q14 でデコーダを iced-x86 などの既存のものに戻した。実現性の工程の決定 D10 と制約 C-T2 はこの方針で上書きされる (learned 2026-10-04) <!-- cid:261004-rust-blink-port:practices-discovery:cbff2b9477367e95ba8ac6bf4ed95edee323a8f90e449253f5993bec190c8236 -->
- WSJF の点数では U12（macOS）が U13（Windows）より上だったが、Q1 の「Windows を先に」と Q6 の心配を優先して U11・U13 を先にした。U5 の前の U2 は、依存関係の文書にない依存（原子的な命令）を作業単位のレビュー指摘から加えた (learned 2026-10-04) <!-- cid:261004-rust-blink-port:delivery-planning:5545184ba131e6ef0f9402a37e52ad440e65943335fcf6f91f88b5633f0b298d -->
