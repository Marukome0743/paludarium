# U11 packaging repair — confirmed scope

## Consolidated Summary Confirmation

今回の修正は、承認済みSteps23〜25だけを実施する。

- jit-support.mjsをnpm配布物へ含め、必須JSのimport/export先の梱包漏れを検出する。
- 実tarballを隔離展開し、配布物だけでimport、同梱production wasm、固定hello guest、stdout/exit、disposeとWorker cleanupを確認する。
- 現環境の再実行手順と過去のツール版・保存証拠を分離し、実行できないブラウザー・coverage・sanitizer項目は未検証として明記する。
- 既存Rust実装・固定guest・品質下限・期限を維持する。必要な新検証コマンドは具体化して変更承認へ提示する。npm公開は実行しない。

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
