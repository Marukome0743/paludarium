# AI-DLC 2.10.0 の検証確認処理の修正

認証済みのレビュー判定がGuard Policyを適用した後、確認処理が古いソース指紋を再比較していました。そのため、relaxedで許可される変更でもREADYのレビューを拒否していました。

修正はソースの鮮度判定を既存のレビュースキャナに委ねます。レビューの認証、成果物との結び付け、ソースの存在とバイパス禁止は維持しています。検証時には既存の監査機能で許可された変更を記録し、新しい検証証拠を作成します。古い承認を再利用する修正ではありません。

ソース修正の再適用：

```powershell
./scripts/repair-aidlc-checkpoints.ps1
```

miseで管理する実際のBun実行ファイルを使います。

```powershell
$bunBin = Get-ChildItem "$env:LOCALAPPDATA/mise/installs/bun/*/bun.exe", "$env:LOCALAPPDATA/mise/installs/bun/*/bin/bun.exe" -ErrorAction SilentlyContinue | Select-Object -Last 1 -ExpandProperty FullName
& $bunBin .codex/tools/aidlc-orchestrate.ts next
& $bunBin .codex/tools/aidlc-bolt.ts checkpoint --action status --unit u1-skeleton --kind skeleton
```

指示されたcontinueトークン、検証、承認の手順に従います。確認処理は修正済みのプロジェクトソースから実行してください。通常の公式実行ファイルにはこのローカル修正は含まれていません。

ネイティブ実行ファイルはTypeScriptを内蔵していますが、再ビルドした実行ファイルを公式インストールに上書きすると整合性検査に失敗します。最初にその方法で適用した実行ファイルは、保存済みの公式バックアップへ戻しました。公式のバージョン情報・チェックサムは書き換えていません。runtime配下に置いた私のバックアップ2ファイルは、公式ファイル一覧との相違を避けるため、元の一時保存先へ移しました。

検証済み：復元後の `aidlc doctor` は問題0件、機械側11項目と整合性12項目が成功しました。診断時のPATHには、この処理内で実際のaidlcコマンドとClaude実行ファイルのディレクトリを追加しています。ユーザー環境全体のPATHを変更した結果ではありません。監査記録の未コミットと、後回しにしたsession-endの警告は別に表示されました。

回帰テストは `scripts/aidlc-checkpoint-regression.test.ts` です。現在のU1レビュー証拠を利用し、relaxedの受理とstrictの拒否を確認する診断用テストで、状態を書き換えません。検証前に2件成功を確認しました。検証・承認状態を前提にするため、移植可能なfixture一式ではありません。

公式更新はローカルソース修正を上書きすることがあります。必要なら修正スクリプトで再適用し、新しい検証証拠と必要な人の承認を取得してください。
# jj 内部データによるレビュー失効の修正

検証済み：2026-10-07のU7レビュー保存は、
`workspace source changed after REVIEW_REQUESTED iteration 1` で拒否された。
`jj status` の変更は監査ログのみ、`source-bytes-final.json` の34ファイルは
SHA256不一致0件だった。一方、AI-DLCの保存済みソース一覧には
`.jj/repo/op_store/` と `.jj/working_copy/tree_state` などが含まれていた。
レビュー依頼後のコミットが、SCM内部データを変更していた。

再適用スクリプトは、CodexとClaudeの `aidlc-lib.ts` にある
`SOURCE_FINGERPRINT_HARD_EXCLUDED_NAMES` に `.jj` を追加する。
公式配布バイナリや署名・チェックサムは変更しない。

検証済み：`bun test scripts/aidlc-jj-source-regression.test.ts` は
1件成功・0件失敗・5 assertions。
SCM内部データの更新は識別値を変えず、通常の実装変更は検知する。
`.jj.ts` のような実ソースのファイル名も除外されない。

既存の依頼ID `review:d2afaf9587b51bf74ee0c49a15851669` は旧識別値に
結び付いている。レビューのNOT-READY文書は保存済みだが、正規の完了receiptは
未記録。依頼や監査を手編集して再基準化しない。
U7の実装修正対象は、末尾slash作成/rename、symlink経由cwd、ゼロバイトwrite。
これらの修正と再検証は未完了である。

