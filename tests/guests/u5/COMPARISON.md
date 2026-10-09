# U5 native-first 比較

各 native x86-64 Linux CI 実行で oracle を生成する。`threads.c` は libc に依存せず、観測値を little-endian signed 64-bit で出力する。stdout、stderr、終了ステータス、定義されたメモリ観測値を完全一致で比較する。TID 数値は出力せず、clone 戻り値、parent TID、child TID、gettid の一致関係へ正規化する。アドレス、時刻、スケジューラの実行順序は比較しない。WAKE は waiter 登録まで繰り返し、sleep による順序推定を使わない。

| Cases | Behavior |
| --- | --- |
| 0–5 | mismatch, unmapped/unaligned address, empty WAIT/WAKE bitset, invalid timespec |
| 6–8 | relative WAIT and expired absolute monotonic/realtime BITSET deadlines |
| 9–11 | no waiters, invalid timespec pointer, unsupported realtime WAIT |
| 12–14 | clone TLS, child TID before execution, individual exit and clear_child_tid |
| 15–16 | parent individual exit retains child; exit_group terminates the process |
| 17–20 | private wake, bitset selection, shared bitset wake, valid tgkill lookup |
| 21–23 | signal interrupts WAIT, invalid flag dependency, parent TID invalid pointer |
| 24–26 | simultaneous locked increments, 100 mutex/condvar-style handoffs, shared wake |

`scripts/u5-native-observe.py --out target/u5-native-first` は全ケースを独立した30秒の process-group watchdog、kill/reap、raw log 付きで実行する。`--emulator target/debug/paludarium` を追加すると native 実行後に emulator と比較する。ケース16は17、他は0で終了する。native の不一致・エラー観測値はデータとして記録し、errno 表から推定しない。

ケース23は不正 CLONE_PARENT_SETTID ポインタに対する Linux の実動作を観測し、成功した clone を1に正規化する。Linux が parent-TID 書き込み失敗を無視した場合に clone が失敗すると仮定しない。

raw guest は後続ユニットの命令・ライブラリ依存を避けて Rust Mutex、Condvar、Rayon が必要とする同期プリミティブを検証する。完全な probe 実行は別途必要である。REQUEUE/CMP_REQUEUE/WAKE_OP の追加対応は実際の使用要件を観測した場合に行う。
