# U15 Step22〜28 の内容確認

## Consolidated Summary（2026-10-18）

- Plan Approval：Step 22〜28 を足した計画を Approve Plan で承認済み。
- 根拠：人の判断「Safari の揺れは PR の前に直す。できれば根本的に」と、指示「先に修正しましょう。提案通りお願いします。」。
- Step22（Safari）：
  - 試験の前に Safari を一度起動して閉じる暖機を入れる。
  - safaridriver 側の時間切れのときだけ、1 回やり直す。1 回目の失敗は残す。
  - 試験を足す。
  - 確認用の workflow で Safari を 10 回並べて動かし、効き目を数える。
- Step23（CI の整理）：
  - 作業用の workflow 21 個を消す。
  - 古いブランチの起動条件を外す。`ci.yml` の push は main だけにする。
  - 夜間の確認を `u14-fuzz` と `u14-quality` を呼ぶ形にする。
  - 必須の 7 workflow の名前は変えない。
- Step24（公開の部品）：
  - 再開の判定で owners と maintainers を確かめる。
  - yank 済みの版は一致としない。
  - 途中の記録を artifact に残す。
  - 試験を足す。tests/release 全件と coverage（各 80% 以上）を手元で実行する。
- Step25（入口の版 d）：
  - 変わったファイルの照合を aidlc/ の外に限る。
  - 入口の Minor 5 件を直す。
  - 回帰を足し、e3c29d1d で本番を 1 回実行する。独立レビューの後、採用を伺う。
- Step26：U15 の記録の Minor を直す。
- Step27：push の前に人の承認を受ける。記録の commit と製品の変更を 1 回で送る。CI 一式と Safari の 10 回の確認を 1 回だけ動かす。
- Step28：新しい head の binding（binding-e05）を作り、採用を伺う。そのあと U11 を確かめ直す。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
