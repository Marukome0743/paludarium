# U8 Step17 の内容確認

## Consolidated Summary（2026-10-19）

- Plan Approval：Step 17 を足した計画を Approve Plan で承認済み。
- 根拠：人の指示「ワークフローの順で進めてください。U1 の確かめ直しから始めて、…」と、U8 の確かめ直し（review-06、NOT-READY）の後の checkpoint での Request Changes（U8 の記録の R-04〜R-11 を直す。測られていない測定を CI に戻すかは、まとめて決める）。
- 直し方：traceability.json は行ごとに JSON として直し、27d05de1 の版と比べて変わった行を確かめる。
- 直すもの：R-04（NFR8 の target を `ci.yml` に替え、reverse から消えた 2 本の行を外す）、R-05（source-manifest.json から消えた 2 本を外す）、R-06（今の状態の節を足し、古い見出しは「履歴：」にする）、R-07（NFR3・NFR9 の notes に時点の印）、R-08（手順書の注記。計画のときに書いた）、R-09（`.github/scripts/u8-current-diagnostic.py` は呼び元が無く実行すると失敗する）、R-10（古い案内先と不採用の候補コマンド）、R-11（受け入れの今の場所と、今は測られていないもの）。
- 変えないもの：製品・CI・workflow・ほかの Unit の記録。
- 確かめ方：正式 sensor 2 件と、checkpoint での entry-f の exit 0。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
