<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-04T02:28:41Z — Q5 で選ばれなかった項目（ネイティブ向け JIT、動的リンクのバイナリ）は、範囲外とも必須とも扱わない。ネイティブ向け JIT は意図書どおり「後で考える」のまま、動的リンクは成功条件に含めない

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-04T02:28:41Z — Q1 で番号順（試作を先にしない）が選ばれた。実現性の評価では wasm のマルチスレッドを設計前に試作で確かめるよう勧めていたので、そのリスクは RAID ログの R2 として残る

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
