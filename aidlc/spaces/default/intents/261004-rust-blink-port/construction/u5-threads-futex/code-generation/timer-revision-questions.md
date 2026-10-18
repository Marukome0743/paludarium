# U5 タイマー通知修正の確認

## Concrete design

- inbox の queue mutex 内で TimerChanged / Interrupted の通知種別を保持し、所有者が消費した種別を取得する。別 worker の process drain は所有者の通知を消さない。
- 実シグナル・group 終了・外部中断を優先する。タイマー変更だけなら、待機入口前の通知でも元の deadline を保持して再計算する。待機中の変更には generation も併用する。Host API と所有権の境界は維持する。
- 既存38ケースに、入口前 disarm・set・反復変更・absolute sleep・timed futex の5ケースを追加する。子の timer syscall 完了後の release/acquire 同期で入口前順序を確定する。
- 待機200ms、set1秒、反復1秒→500ms→disarmを4回。経過150〜600msを比較用 bool にし、期待結果は全43ケースの Linux 実測で決定する。30秒 watchdog と品質下限は維持する。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
