# U8 追加検証の内容確認

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

承認済みSteps13〜15に従い、製品・guest fixtureを保持し、新しい専用診断CI/helperで同一現行ソースのfresh Linux全29差分＋runner1、3OSのU8内部56件・U5内部33件・U6内部49件の回帰、fmt/Clippy/依存4検査を実行する。既存workspace全体coverage経路はempty profileからfresh U3 nativeとinstrumented CLI・U8/U5/U6差分を含めて実行し、同じ対象規則と全体80%下限を維持する。全入力・両lock・実使用compiler・設定・署名head/job・生ログ・実exitを保存する。ASanは対象ごとの依存閉包・compiler・flags・設定・原本が一致した範囲だけ保存結果を再利用する。U8のNode/Safari fork/exec/wait成功は未検証と区別する。wait4のEFAULTでもreapするLinux動作、既存C10、strict guard、30秒入力制限、比較maskを維持する。正式検査・独立レビューへ渡し、新最終確認コマンドは別承認後に実行する。

- Looks correct
- Request changes

[Answer]: Looks correct
