# U3追加検証の内容確認

## Consolidated Summary Confirmation

承認済みSteps28〜30に従い、製品を変更せず同一現行ソース・両lock・最新公式確認版を固定した署名CIでfresh Linux native正常23576/fault1162/CPUID12、独立U3 matrix CPU40/Decoder12（ignored0）、Linux diff_u3、同fresh入力による3OSのU3限定テストを実行します。空profilesから共有CPU/Decoder9ファイルcoverage80%以上を別に測定し、cpu_u2/mmu_u2/decodeを各600秒ASan/LSanで実行します。U9新ASan4対象とNode/本物SafariのU3関連ケースは、依存・両lock・実compiler・設定が一致する範囲だけ再利用し、新規実行と呼びません。strict guard、30秒制限、80%下限、比較mask・測定対象を維持します。入力前後/current・署名・生ログ・実exitを保存し、正式検査と独立レビューへ渡します。失敗・欠落・skipを合格にしません。新しい最終確認コマンドは別承認前に実行しません。

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
