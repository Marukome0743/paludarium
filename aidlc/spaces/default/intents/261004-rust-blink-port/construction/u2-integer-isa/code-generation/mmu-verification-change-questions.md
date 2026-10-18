# U2 MMU条件不一致と最終確認更新

## 追加範囲の確認

独立レビューで、保存済みmmu_u2は最大入力4096 bytes、U2の承認済み契約は4608 bytesという不一致を確認した。保存結果の601秒・exit0は保持するが、4608条件の成功として扱わない。

修正案：製品コードを変更せず、現行の同一ソース・両lock・実使用コンパイラでmmu_u2だけを `-max_len=4608 -max_total_time=600 -timeout=30 -rss_limit_mb=2048`、既存ASan/LSan・seed1・suppression条件で実行する。署名済みCI、入力before/after、binary hash、生ログ、実exitを保存する。CPU/decodeは適用条件が一致する保存証拠のみ限定再利用する。4096条件の旧結果と今回を区別する。

既存の最終確認コマンドの全検査項目を保持し、不一致3入力とU11共有差分を有限の現行証拠へ結合した新確認スクリプト `aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py` を実装・構文確認する。候補の正式実行は独立レビューと別途のコマンド承認後に行う。strict guard、coverage80%、30秒制限と比較条件を維持する。修正後の成果物を再レビューし、U2完了承認後にU11の承認済み同時dispose修正へ戻る。

Q: 上記の限定追加検証と確認スクリプト更新を承認しますか？
A) 限定追加検証と更新を承認
B) 変更内容を指定する
[Answer]: 限定追加検証と更新を承認
