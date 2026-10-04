# U1 再確認：Linux 検証環境の停止

## 検証済みの結果

- U1 の独立レビューは新規指摘なし。`REVIEW_COMPLETED` と `UNIT_COMPLETED` の正式な記録が成功した。
- 新しい確認の全体テストは開始前に失敗した。承認済みコマンドは `"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked --workspace`。
- 正式な checkpoint verification の ID は `99578da9-5f30-42cb-8133-654da17a7504`、終了コード1、`evidence_unchanged: true`、`verified: false`。製品テストの失敗を観測した結果ではなく、Docker API へ接続できなかった結果である。

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

## 環境の復旧を試した結果

- Docker Desktop の実体を `Start-Process -WindowStyle Hidden` で起動したが、その後の `docker info --format '{{.ServerVersion}}'` は終了コード1。
- `wsl.exe --list --running --quiet` は終了コード0、出力なし。
- `docker desktop start --help` で正式な起動オプションを確認し、`docker desktop start --detach` を実行。起動開始の表示後、続く `docker info` は再び終了コード1。
- 起動ログの 2026-10-07T10:50:58.836425300Z に次のエラーを観測。10:51:04 および再試行後の10:57:40には Linux API pipe の閉鎖を観測した。

```text
resetting socket forwarder: preparing vsock listener:
listening on AF_UNIX vsock 1999:
rename <HOME>\AppData\Local\Docker\vm-data\00000002.000007cf
<HOME>\AppData\Local\Docker\vm-data\00000002.000007cf.stale:
The file cannot be accessed by the system.
```

## 未検証のまま残す事項

今回の新しい全体テストは未完了。U1 の新しい skeleton checkpoint は未承認。U7 の既存指摘も未修正。Docker の内部データを削除・手修正していない。Windows や WSL 全体の再起動も実行していない。
