# U15 Step7 ローカル照合の内容確認

## Consolidated Summary（2026-10-17）

- Plan Approval：U15 の 8 Step 計画は承認済み（変更しない）。Step7 の送信部分（署名 head be45b36c と CI 実行）は実施済み。
- 人の選択（2026-10-17「ローカル照合で Step7」）：push・新しい CI 実行・新しい性能測定・公開・tag は行わない。
- FR6.3・FR7.2・FR7.3・FR8.2：be45b36c の保存済み CI 原本（全品質 run 38897611874 の artifact・job ログ、専用 native run 38897611887 の原本）から、FR5 の各環境で probe 全項目 PASS、aube 4 コマンドの native との一致、#1645 の再現、JIT あり・なしの一致を、読み取り専用の照合スクリプトで確かめる。
- FR8.3：be45 の性能測定は skipped。be45 の通常 Wasm module と旧正式性能の module（fb2f…）の全 bytes 一致に加え、probe・JS・oracle・ビルド条件が旧正式性能の原本と一致するかを確かめる。全部一致すれば旧測定（JIT 平均改善 2.7357%、片側 p=0.0068）を be45 に結びつけ、一つでも違えば FR8.3 は GAP のままにする。
- u15-acceptance producer：実公開（release.yml の publish）でだけ読まれ、upstream の公式 run・Trusted Publisher・release environment・人の公開承認を前提とするため、公開段階に回す。FR10.1 と同じ GAP として記録する。
- 記録：結果を code-summary.md・traceability.json に反映し、照合スクリプトと結果を U15 verification に保存する。製品・試験・workflow・他 Unit の固定ファイルは変更しない。そのあと sensor、独立レビュー、正式検証、人の完了承認へ進む。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
