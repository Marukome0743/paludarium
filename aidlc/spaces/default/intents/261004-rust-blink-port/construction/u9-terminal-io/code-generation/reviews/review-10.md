## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | crates/paludarium-host/src/lib.rs > 新規公開型 TerminalAttributes / TerminalInfo | 検証済み：Host両型とRuntime TerminalInfoのnon_exhaustive、全フィールドを値変換なしで受け取るconst constructorをsourceで再確認した。Default既存値と外部literal禁止docを保持し、19claimsは署名現行91ca0c4eと全byte一致する。保存CI37773320167の外部6件/doc3件は旧API修復時点の証拠であり、現在CIや保存ASan/Safari再利用と区別している。 | 追加対応なし。non_exhaustive、値を保持するconstructor、Defaultと外部構築禁止の回帰証拠、各source時点を維持する。 | Resolved (reviewer) |
| R-02 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/code-summary.md > Steps22〜24：記録更新と証拠の適用範囲 | 検証済み：U9固有coverageの原本は署名541b4396／CI38062686224の旧13ファイル2693/3202と追加10ファイル2156/2397である。現在b79では旧13に含まれるHost/libのmacOS・Windows backend接続とRuntime/libのCodeCache接続が変わり、compilerも更新されている。現在の全体coverage成功、限定テスト33件、Linux差分14件は確認できたが、変更後の同じU9固有集合の80%測定は今回確認していない。本文は旧結果の有限適用と新測定未実行を明記しており、未測定を成功とする主張はしていない。 | 次にU9固有coverageの現在値を主張する際は、既存手順のLinux coverageを同じ旧13／追加10集合・除外・80%下限で実行し、現行head・compiler・locks・分子分母・rawへ結合する。それまでは541bの値を保存観測として保持し、全体coverageで置き換えない。 | Unresolved |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/source-manifest.json > writes | `.gitignore` は source-manifest.json の37パスに含まれていない。code-summary.md はこれを「既知のexact .gitignore差」として別枠で扱っており、今回の変更（AI-DLC ブロックへの `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行）はビルド・実行・テスト・U9 の端末契約のいずれにも影響しない。ただしエンジンが共有ソースとして束縛している経路が manifest から読み取れず、今後の再束縛の原因が追跡しづらい。 | 次回の成果物更新時に、`.gitignore` を非ビルド共有パスとして manifest またはサマリの該当節に明示するか、束縛対象から外す。今回は製品・テストに影響しないためブロックしない。 | Resolved (reviewer) |
| R-04 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/verification/step72-u9-coverage-recount.json > job_log.all23_matches_total_lines | lcovのDA行数5633とjobログTOTALの5707行が一致せず（差74行）、`all23_matches_total_lines` は false。要約は「数え方が異なる」と説明するが、その理由は検証されていない推測である。 | 要約の該当文を「差の原因は未確認」と言い換えるか、llvm-covの行数定義で差が説明できる根拠を添える。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/verification/step72-u9-coverage-recount.json > lock_sha256 | 欄名が `lock_sha256` だが値は「unverified」の文章で、「wasm lock」という誤称も含む。誤称は要約で訂正済みだが、JSON自体は誤称のまま。 | 次に成果物を更新するとき、欄名を `lock_sha256_status` などにするか、JSONに訂正注記を付ける。compiler・lockを束縛したい場合は、同CIのinputs原本が残っていれば読んで照合する。 | New |

> R-02 Reviewer note: 現行head be45b36c・公式CI run 38897611874 のlcov原本からU9固有値（旧13 2745/3251=84.44%、追加10 2154/2382=90.43%、全23 4899/5633=86.97%）を、同一集合・同一コマンド（packages・ignore-filename-regex・--fail-under-lines 80）で再集計した点は解消。ただし要求された「compiler・lockへの束縛」は未達（rustc版・両lockのSHAはjobログにも保存inventoryにも無く、未照合と明記）。開示は正直で、値はMinorの範囲。

> R-03 Reviewer note: code-summary.md の「(b) .gitignore の位置づけ」が、manifest外のビルドに使わない共有パスであること、追加2行、U9の製品コード・テスト・端末契約への影響なしを明記しており、要求を満たす。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| step72_u9_coverage_recount.py のコード精査 | 要約の主張どおり | digest==ZIP SHA（read_lcov）、サイズ、ZIP内が単一メンバー、集合の重複・重なり・各パスの一致数が丁度1、80%判定、`open("x")` の排他作成、job成功・run/head照合を実装済み。lcovの23 SFと23パスが一致し、unmatched・merge重複は0。 |
| JSONと要約・手順書の数値照合 | 一致 | 2745/3251、2154/2382、4899/5633、lcov SHA 41bc3f7b…、digest 6b27a74d…、TOTAL 5707/767/86.56%が、JSON・code-summary・unit-test-instructionsで整合。旧541b値は履歴として保持。 |
| jobログのU9 coverageコマンド | 同一 | `-p host -p kernel -p runtime -p paludarium -p harness --lib --test diff_u9 --test command --ignore-filename-regex 'paludarium-(cpu\|decoder\|mmu\|loader\|types\|vfs\|jit\|harness)/' --fail-under-lines 80` が手順書の記載と一致し、80%下限は不変。 |
| compiler・lock | 未照合 | inventory.json はartifact id・SHA・サイズのみで、rustcやlockのハッシュは記録されていない。他のinputs原本の有無は、Read/Glob/Grepの制約（Bash禁止、一覧不可）のため確認できていない。 |
| 他Unit・製品sourceの未変更 | 確認できず | 差分を取れない（Bash禁止）。要約は変更なしと述べており、新規物はスクリプトとJSONに限られると読めるが、独立検証はしていない。 |

### Summary

U9固有coverageの再集計は、同じ集合・コマンド・80%下限で、現行headの公式CI原本に基づき内部整合しており、過大な主張（新規CI、差分、Node／Safari、ASan、U15受理）もありません。R-03は解消、R-02は値の面では解消し、compiler・lockの束縛だけが未達の開示済みMinorです。Criticalなし、Majorなしのため READY です。
