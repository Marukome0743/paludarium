# U10 Step33 の内容確認

## Consolidated Summary（2026-10-19）

- Plan Approval：Step 33 を足した計画を Approve Plan で承認済み。
- 根拠：人の指示「ワークフローの順で進めてください。U1 の確かめ直しから始めて、…」と、U10 の確かめ直し（review-15、NOT-READY）の後の checkpoint での Request Changes（R-14〜R-19 を直す。test_evidence.py の一字一句の照合と測られていない測定は、記録に書き、製品の変更としてまとめて決める）。
- 直し方：traceability.json は行ごとに JSON として直し、27d05de1 の版と比べて変わった行を確かめる。
- 直すもの：R-14（FR9.1 の target を `u10-native-diagnostic.yml` に替え、要件書の定義に合う理由を書く。reverse から消えた workflow の行を外す）、R-15（manifest から消えた workflow を外し、U15 が変えた `ci.yml`・`test_evidence.py`、成り立たなくなった「e4f84768 と同じ」、呼び元の無い `.github/scripts/u10-current-diagnostic.py` を書く）、R-16（今のコマンドを entry-f と書き、古い見出しを「履歴：」にし、題名の「（独立レビュー待ち）」を外す）、R-17（古い toolchain に時点の印）、R-18（test_evidence.py の一字一句の照合のこと）、R-19（受け入れの今の場所と、今は測られていない Python core の coverage・実行ファイルを含む llvm-cov・aube の 4 操作の時間の記録）。
- 変えないもの：製品・CI・workflow・ほかの Unit の記録。手順書は計画のときに直した。
- 確かめ方：正式 sensor 2 件と、checkpoint での entry-f の exit 0。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
