# U7 native比較の対象

検証済みの結果は `inventory/diff-*.txt` にある。`tests/guests/u7/files.c` はraw Linux x86-64 syscallを発行し、`build.sh` がstatic guestを作る。`diff_u7` は毎回native runnerで期待結果を取得し、同じguestをemulatorで実行する。期待結果の固定ファイルはリポジトリへ保存しない。

|値|比較方法・除外理由|
|---|---|
|標準出力・標準エラー|バイト単位で全体を比較する。file bytes・readlink targetはguest出力にも含める。|
|終了状態|exit code / signalを比較する。|
|syscallエラー|Linux負errnoをguest出力として比較する。NULL stat系、invalid FD/buffer、empty path、flagsを含む。|
|inode種別・サイズ・link count|statの意味を持つフィールドをguestで抽出し比較する。|
|inode番号・device番号|nativeと仮想inodeの採番が異なるため値そのものを出力しない。同一inode/hardlink関係は操作結果とlink countで検査する。|
|pid・実時間・アドレス|このfile corpusでは出力しない。各実行で異なる値を恒等比較する対象にしない。|
|stat uid/gid・timestamp|本corpusでは比較しない。完全なLinux stat全フィールド互換の合格は主張しない。|
|directory entry順序|Linux read_dirの順序が未保証なので、native getdents corpusでは返却有無・EOF/エラーを比較する。内部directory回帰は名前集合を確認する。|
|内部フラグ・レジスタ|file programの観測対象は上記program結果である。命令別フラグ比較は既存担当Unitに残す。|

MemFsのケースと、明示的に独立したtemporary Host rootを`/tmp`へmountするケースを実行する。Hostケースのguest programはprivate preloadから起動する。各親テストは別のchildへ委譲し、whole-child watchdogが30秒でkill/reapする。子の `1 passed` を親ケース数に足さない。

この比較はU7のfile probe相当部分に限定する。probe全体・aube全体・platform固有mount・browser/wasm/JITの合格とは扱わない。未検証の境界やplatformは `verification.md` で明示する。
