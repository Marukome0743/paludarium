# U10 の実行時間

検証済み：署名済み実装 head `26b76c01a72a050a57d12420365a73997d9a637e`、Actions run `38009664758` の fresh native / emulator の 4 操作の wall time です。各値は同じ固定 ELF、fixture、環境条件の observations row から転記しました。操作別の制限時間は 30 秒であり、速度の合格閾値や倍率は新設しません。

| 操作 | fresh native 秒 | emulator 秒 |
| --- | --- | --- |
| --version | 0.007861 | 0.572972 |
| install | 0.031686 | 13.116191 |
| install --frozen-lockfile | 0.013288 | 12.136367 |
| list | 0.003235 | 0.371807 |

文書根拠：チーム保存の一次調査 `aidlc/spaces/default/knowledge/documents/research/cheerpx-oss.md` は、2026-10-03 の CheerpX 1.3.9 について version 0.3–0.7 秒、初回 install 1.8–5.7 秒、frozen 1.3–3.6 秒、list 0.17–0.65 秒を報告します。i586 GNU/glibc、WebVM、依存調整と statx 用 LD_PRELOAD、Node 10.24 を含む別条件です。今回の x86-64 static-musl / Node 不在の Linux 計測との直接の性能比較や倍率計算には使いません。

検証済み：専用 differential ジョブでは依存取得と Rust テスト実行ファイルのビルドを先に完了させ、その後に隔離実行を開始しました。固定 ELF の guest ビルドも先行ジョブで完了しています。計測中にこのハーネスがビルドを並行起動することはなく、native と emulator の各 guest 操作を逐次実行しました。根拠は run 38009664758 の native-first/differential 成功ログ、workflow の順序、および observations の各 row です。この既知の負荷を停止した範囲を計測条件とします。

未検証：OS や共有ホストの背景負荷が完全にゼロであることは確認しません。数値は上記の限定した計測条件の観測です。さらに制御したベンチマークが必要な場合は、専用 Linux runner で利用者の背景タスクを停止し、実行前後のプロセス、load average、CPU 数を記録し、同じ固定 ELF と新しい fixture で 4 操作を逐次実行する方法を提案します。追加計測や OS の負荷ゼロを達成したとの主張はしません。
