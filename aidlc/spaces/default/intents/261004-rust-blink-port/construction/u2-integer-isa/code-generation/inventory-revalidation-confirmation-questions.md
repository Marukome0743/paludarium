# U2 Steps61〜63 内容確認

## Consolidated Summary Confirmation

承認済みSteps61〜63に従い、共通checkerの歴史37入力と現行42入力の混同を最小修正する。歴史37は旧固定順序・歴史trace/proof・当時署名sourceへ結合し、現行42は追加5件と旧37件の全順序・重複なし・各source digestを現行manifest、署名source、保存CI入力へ厳密照合する。現行入力を加工して歴史原本と呼ばず、旧canonicalの全検査、EXTRA2件と有限差分の検査を保持する。

内部test-afterの順序で、歴史37正常、現行42正常、欠落、余分、重複、並べ替え、digest不一致、歴史／現行取り違えの8件の局所回帰を追加し、構文・非ゼロreadiness・30秒上限の実行結果を保存する。製品と他Unit成果物を変更せず、新CIや重い製品試験を追加しない。前回Manifest inventory differsの実測失敗、MMU4608原本と保存CPU/decode証拠の限定適用を保持する。

正式sensorと成果物整合後に書込を停止し、独立レビューを取得する。共通checkerの正式実行は新しいコマンドの人承認後に行い、成功・失敗・未検証を分けて保存する。人のU2完了承認後にU11へ戻り、承認済み同時dispose修正を継続する。完全Testing Contract、custom順序、strict guard、coverage80%、30秒制限と比較条件を維持する。

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
