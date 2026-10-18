# U14 追加診断の内容確認

## 確定した範囲

- 承認済み計画Steps15〜19の観測用診断だけを実装する。既存1block方式、公開契約、MMU世代・共有lock・bytes照合・trap rollbackを保持する。
- 次RIPの同epoch positive translation・同Worker preparedの有無、実イベントの連続長、停止理由、lookup回数・比較bytesを観測する。peekはcache/LRU/hint/prepare/execute/CPU stateを変えない。
- 診断schemaをversion2へ更新し、旧88field原本と分離する。各変更内部部品7件以上・JS境界8件以上の回帰で不変条件と不正入力の拒否を確認する。
- 同sourceの診断/control両moduleのreceipt・SHA・locksを照合し、controlの診断exports0と実Wasm起動を確認する。
- 重い背景処理を止め、既定のu11 guest/oracle対応組で各modeをfresh factoryで1回だけ診断する。guest30秒、8PASS・exit0・kill/reap/cleanupを要求する。
- 固定coverage80%、既存JE・4環境比較・sanitizerの品質条件、旧検証・全失敗原本・9件のGAPを保持する。新証拠は別の出力先へ保存する。
- batch製品実装・命令追加・正式20標本の性能再測定は今回に含めない。回数・割合を時間寄与や性能改善の証明へ読み替えず、診断後に次の修復方針を提示する。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
