<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-04T06:54:13Z — 面談の途中で、ユーザーが技術選定の方針を変えた（外部のものは基本的に使ってよい。著作権・ライセンスに関わるもの、不具合があるものは自作）。Q1 と Q13 の回答をこの方針に置き換え、Q14 でデコーダを iced-x86 などの既存のものに戻した。実現性の工程の決定 D10 と制約 C-T2 はこの方針で上書きされる

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-04T06:54:13Z — Q10 で最初から nightly にした。crates.io で公開するライブラリが nightly 専用になると利用者が限られるので、公開の前に stable で使えるかを見直す必要がある。Q6 で期待結果を毎回 CI の Linux で作ることにしたので、Windows の開発機では差分テストを手元で回せない
