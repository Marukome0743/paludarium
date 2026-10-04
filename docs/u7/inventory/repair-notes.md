# U7 差分テストの修正記録

全体検証でU7の5件が失敗しました。同じ63件を `--test-threads=1 --nocapture` で実行すると61件が成功し、末尾スラッシュの2件だけが失敗しました（`repair-before.txt`）。シンボリックリンク、リンク先への作成、名前変更による置換の3件は順番に実行すると成功しました。

ネイティブのゲストが共通の `/tmp/paludarium-u7-*` を使っていたため、各ケースのネイティブ・エミュレータ比較をmutexで直列化しました。既存の子プロセスと30秒のwatchdogは維持しています。

削除と名前変更の元パスが `/` で終わる場合、最終の項目をシンボリックリンクとして確認してから操作します。リンクならENOTDIRを返し、リンクと参照先を残します。O_CREATとO_DIRECTORYを同時に指定したopenは、メモリ・マウント・ネイティブの各実装で、ファイルを作る前にEINVALを返します。

検証済み：次のコマンドによる修正前後の結果を保存しています。

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1 --nocapture
# 修正前：61 passed; 2 failed、終了コード101。
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh bash -c 'cargo fmt --all && cargo test --locked -p paludarium-harness --test diff_u7'
# 修正後：通常の並列設定で63 passed; 0 failed、終了コード0。
```

`repair-after.txt` にネイティブとエミュレータの観測結果があります。

最初の正式な全体検証は、再ビルド中にETIMEDOUTで終了しました。テストの終了コードはありません（`repair-workspace-verification.json`）。ユーザーの「再実行する」という承認を受けて同じコマンドを再実行しました。

clippyでkernelの `files.rs` にitems_after_test_moduleを検出したため、StandardFileの処理内容を変えず、テストモジュールより前へ移しました。修正後、`scripts/linux-dev.sh cargo clippy --locked --workspace --all-targets -- -D warnings` は終了コード0で成功しました（`repair-clippy.txt`）。最終のローカル `cargo fmt --all --check` も成功しました。

正式な全体検証の再実行は成功しました（`repair-workspace-verification-retry.json`）。コマンドは `"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked --workspace`、終了コード0です。検証ツールの結果はready: true、verified: true、approved: false、errors: []、evidence_unchanged: trueでした。

これらは今回の修正の検証結果です。U7の残りの成果物・品質要件の完了や、承認の記録を意味しません。
