# U5 限定修正の内容確認

## 修正内容

承認済みSteps29〜32に従い、旧署名ソースで旧CIの全検査を保持する確認候補を作成する。現行mise.tomlはAI-DLC版2.11.0から2.11.1-preview.20261012.1への変更だけを別に厳密照合し、他設定・製品source・両lock・compilerの変更、欠落、余分な入力、symlink、原本改変を拒否する。実workspace・製品・AI-DLC本体・guard・旧checker・旧原本は変更しない。12境界以上の回帰と全スクリプト診断、正式検査・独立再レビュー後、別途承認された新コマンドで正式再検証する。新しい重い試験・外部送信を追加せず、coverage80%・guest30秒を維持する。U5完了承認後にU14へ戻る。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
