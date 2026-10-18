# U2 Steps58〜60 内容確認

## Consolidated Summary Confirmation

承認済みSteps58〜60に従い、製品コードを変更せず、現行ソースのmmu_u2一対象を最大入力4608 bytes・600秒・seed1・timeout30秒・rss2048、既存ASan/LSan suppressionで署名済みLinux CIにて検証する。全入力before/after・両lock・実使用コンパイラ・binary hash・原本ログと実exitを保存する。旧4096 bytesの成功と今回を区別する。

旧最終確認の全検査項目を保持する `verification/verify-current-u2-u11-revalidated.py` を実装し、構文確認する。不一致3入力と共有変更は有限の現行証拠で結合し、無視・旧ソース偽装・検査削除で通さない。正式実行は独立レビューと別途のコマンド承認後に行う。正式sensor・再レビュー・最終確認・U2完了承認を経て、承認済みU11同時dispose修正へ戻る。strict guard、coverage80%、30秒制限と比較条件を維持する。

Does this all look correct before I generate the artifact?
Looks correct / Request changes
[Answer]: Looks correct
