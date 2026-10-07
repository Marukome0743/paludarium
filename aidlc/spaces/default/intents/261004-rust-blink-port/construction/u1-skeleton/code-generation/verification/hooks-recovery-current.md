# 2フックの復旧確認

## 検証済み

`.codex/hooks.json:70` に PreToolUse の `aidlc engine adapter codex plan-approval-guard`、同138行に Stop の `aidlc engine adapter codex continue-workflow` が登録されている。無効化していない。

実行コマンド：`/Users/mutoakio/.local/share/mise/installs/bun/latest/bin/bun test tools/aidlc-recovery/recovery.test.ts`

出力：`9 pass / 0 fail / 37 expect() calls`。診断・parkの許可、未承認application変更とcommand chainingの拒否、hook設定の復旧、terminal errorでのStop終了、custom scopeのresume、symlink経由変更の拒否を確認した。

## 運用

`rejected report` が必要となった場合も、その直前に両フックの登録と上記テストを再確認する。登録と隔離fixtureの回帰成功は、将来のすべてのhook動作を保証するものではない。
