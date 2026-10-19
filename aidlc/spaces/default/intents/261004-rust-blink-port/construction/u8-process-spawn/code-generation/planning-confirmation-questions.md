# U8 計画前の確認質問

## Sources

- 要件 FR2.8、Unit U8、契約 C8。
- ユーザー回答：Rust Command の起動経路まで対応。
- ユーザー回答：終了待ちを基本に、停止／再開通知は対象プログラムで必要と確認できた場合に追加。

## Consolidated Summary Confirmation

U8 は fork 相当の clone、Rust Command の vfork 相当の起動経路、execve、wait4 を扱う。実行対象は仮想ファイルシステム内の static-musl ELF とし、存在しない実行ファイルには ENOENT を返す。子はエミュレータ内で実行し、ホストのプログラムは起動しない。wait4 は特定の子と任意の子、WNOHANG、通常終了とシグナル終了を基本とする。停止／再開通知は対象プログラムの必要性を確認して追加する。実装前に x86-64 Linux の差分ケースで期待結果を実測し、内部部品の単体テストは実装後に行う。U5 のスレッドと U6 の fd・イベントの挙動も回帰検証する。

この内容で U8 の計画とテスト手順を作成してよいですか？

[Answer]: Looks correct
