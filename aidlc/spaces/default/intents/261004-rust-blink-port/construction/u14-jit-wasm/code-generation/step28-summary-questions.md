# U14 再確認の内容確認（Step28）

## Consolidated Summary（Step28、2026-10-17）

- Plan Approval：改訂計画（Step28）を Approve Plan で承認済み。旧 Steps1〜27・失敗原本は履歴として保持する（Step27 は未完了のまま）。
- 差し戻し理由（U14 checkpoint の再確認 iteration 2 での Request Changes）：R-04 — code-summary.md の「新しい正式検証コマンドは未採用」を改め、checkpoint で実行する採用済み正式コマンド `final_candidate.py`（SHA-256 `d799bbb9…`）と旧候補との関係、実行記録（checkpoint の検証記録と出力ディレクトリの `result.json`）を明記する。R-05 — ルート `.gitignore` が U14 のビルド・テスト・JIT・wasm の入力ではなく、manifest（91 パス）に含めない共有パスであること、2026-10-16 の harness 追加で2行が入り再確認が起きたことを明記する。
- 方法：code-summary.md の末尾に「## 現行Step28：正式検証コマンドとルート.gitignoreの位置づけ」節を加える。実行のたびに新しい出力ディレクトリが作られ、最新の実行は `unit.json` の `verification.stdout_tail` に記録されることも書く。「保存した失敗と残る確認」節の最終段落の先頭に「履歴」の注記だけを足す。
- 範囲：U14 の code-summary.md だけ。製品、CI、source-manifest.json、traceability.json、旧証拠は変更しない。新しいスクリプト・CI 実行・性能測定・外部送信はない。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
