# U15 Step17〜18 の内容確認

## Consolidated Summary（2026-10-18）

- Plan Approval：Step 17〜18 を足した計画を Approve Plan で承認済み。
- 根拠：U15 の確認での Request Changes（「先に R-16〜R-18 を直してください。」）と、そのあとの「U15 の番で R-16〜R-18 と残している Minor をまとめて直す」という指示。
- (1) R-16（Major）：最初の公開が途中で止まったときの再開。申告があり、registry にすでにある crate と npm の版が、承認済みの `.crate` の SHA-256 と npm tarball の integrity にすべて一致するときだけ、残りだけを公開して続ける。1 つでも違えば拒否する。`docs/release.md` の手順 (3) に再開の手順と、crates.io の新しい crate の作成数の制限を書く。
- (2) R-17（Minor）：`publication_environments` を子プロセスごとの許可リストにする。cargo には `GH_TOKEN`・`ACTIONS_ID_TOKEN_REQUEST_*` を渡さず、npm には provenance に要る変数だけを渡す。
- (3) R-18（Minor）：`docs/release.md` の `paludarium*` が前方一致でほかの名前にも当たることを書き、11 の名前を 1 つずつ指定することを勧める。
- (4) U15 の記録の Minor：R-13（code-summary.md の注記）、R-14（traceability.json の先頭の文の整理）、R-15（`U15_acceptance: GAP` の説明）。
- 試験：単体（再開：一致すれば残りだけ・1 つでも違えば拒否・申告なしでは拒否、許可リスト：cargo に `GH_TOKEN` と OIDC の変数が渡らない・npm に要る変数だけ）、tests/release 全件・validate・package-check・coverage（4 ファイル各 80% 以上）を手元で実行する。
- Step 18（push・CI・確認コマンドの入口 v4 と v3 の Minor 4 件の直し・独立レビュー・採用の伺い）は、push の前に人の承認を受けてから進める。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
