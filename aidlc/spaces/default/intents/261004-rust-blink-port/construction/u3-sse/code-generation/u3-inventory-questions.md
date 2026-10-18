# U3 SSE対象の追加調査

## Sources
verification/step2-inventory-decision.md と verification/step2-inventory-gap.json。承認済み計画Step2の網羅性不足に対する範囲判断。

## Question
対象SSE命令の確定をどう進めますか？
- A: 追加調査を行う（推奨）。fork Linux CIで固定binary照合、encoding分類、固定workloadのnative完走観測を行い、未確定候補を保守的に残して対象表を確定する。
- B: 保守的な対象集合を先に確定する。静的候補からlegacy SSEを広めに実装・差分検証する計画へ変更し、動的網羅性の未検証境界を別記する。
- X: Other
[Answer]: 追加調査
