# U5 native-first 比較

各 native x86-64 Linux CI 実行で oracle を生成する。`threads.c` は libc に依存せず、観測値を little-endian signed 64-bit で出力する。stdout、stderr、終了ステータス、定義されたメモリ観測値を完全一致で比較する。TID 数値は出力せず、clone 戻り値、parent TID、child TID、gettid の一致関係へ正規化する。アドレス、時刻、スケジューラの実行順序は比較しない。WAKE は waiter 登録まで繰り返し、sleep による順序推定を使わない。

| ケース | 動作 |
| --- | --- |
| 0–5 | 値不一致、未マップ・非整列アドレス、空 WAIT/WAKE bitset、不正 timespec |
| 6–8 | 相対 WAIT、期限切れ絶対 monotonic/realtime BITSET |
| 9–11 | waiter 不在、不正 timespec ポインタ、未対応 realtime WAIT |
| 12–14 | clone TLS、実行前 child TID、個別 exit、clear_child_tid |
| 15–16 | 親の個別 exit 後も子を保持、exit_group でプロセス終了 |
| 17–20 | private wake、bitset 選択、shared bitset wake、有効 tgkill 検索 |
| 21–23 | signal による WAIT 中断、不正 flag 依存関係、不正 parent TID ポインタ |
| 24–26 | 並行 locked increment、100 回 mutex/condvar 相当 handoff、shared wake |

`scripts/u5-native-observe.py --out target/u5-native-first` は全ケースを独立した30秒の process-group watchdog、kill/reap、raw log 付きで実行する。`--emulator target/debug/paludarium` を追加すると native 実行後に emulator と比較する。ケース16は17、他は0で終了する。native の不一致・エラー観測値はデータとして記録し、errno 表から推定しない。

ケース23は不正 CLONE_PARENT_SETTID ポインタに対する Linux の実動作を観測し、成功した clone を1に正規化する。Linux が parent-TID 書き込み失敗を無視した場合に clone が失敗すると仮定しない。

raw guest は後続ユニットの命令・ライブラリ依存を避けて Rust Mutex、Condvar、Rayon が必要とする同期プリミティブを検証する。完全な probe 実行は別途必要である。REQUEUE/CMP_REQUEUE/WAKE_OP の追加対応は実際の使用要件を観測した場合に行う。
