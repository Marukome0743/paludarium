# U11 現行検証の内容確認

## Consolidated Summary Confirmation

承認済みSteps14〜16に従い、最新ツールへ設定・lockを更新して、現行ソースのproduction wasmと固定probe/aubeを作ります。同一guestとmoduleをfresh Linux nativeとNode.js・Chromium・Firefox・本物Safariで比較し、各14ケース、C12境界、既存回帰、3OS品質、Rust/JSの定義済み範囲のcoverage80%以上を確認します。

全入力・両lock・実使用compiler・設定・原本ログを保存します。ASan/LSanの保存証拠は依存・compiler・設定・バイナリが一致する対象だけ再利用し、不一致の対象は600秒実行します。製品は保持し、大規模FSのdispose候補は限定再現を先に確認し、製品修正が必要なら具体的な最小案を提示します。strict guard、30秒制限、比較条件と測定分母を維持します。新しい最終確認コマンドは独立レビューと別承認後に実行します。

Does this all look correct before I generate the artifact?

[Answer]: Looks correct
