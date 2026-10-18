# U10 最終確認コマンド候補（未実行）

候補：`python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py`。正式実行には AI-DLC の確認コマンド変更の承認が必要です。現時点では checker 実行や完了判定は行っていません。

読み取り専用 checker は以下を全て満たす場合だけ exit 0 とします。

1. source-manifest 37 パスの存在・一意性、traceability の reverse 一致を確認する。実行に関係する非 Markdown 31 パスの bytes を `jj --ignore-working-copy file show -r 26b76c01a72a050a57d12420365a73997d9a637e PATH` と比較する。文書の後続更新と実装 provenance を混同しない。
2. GitHub read-only API で同 SHA の署名 Verified/valid と run 38009664758 の head 一致、完了・成功を確認する。通常の 3 OS、lint、dependencies、wasm、Linux differential、line coverage と reusable U10 の metadata/native/differential 全必須ジョブが存在し成功していることを確認する。skipped や missing は合格にしない。
3. 同 run の未失効 artifact `u10-native-first`、`u10-differential`、`u10-native-metadata` をメモリ内 ZIP として読み、probe/aube bytes の SHA、static ELF 条件、固定 aube commit/lock、source 前後同一性、root deny bytes/hash、限定例外だけの派生設定、実ライセンス全文/hash と 4 audit 成功を照合する。記録された過去の native 結果を期待値に使わない。
4. fresh native 完了と differential 完了、同 binary hash、14 native rows と 16 emulator rows の名前集合を確認する。全 row の exit 0、timeout false、30 秒以内、probe 全8項目の exact PASS、node 不在、stdout/stderr/exit 一致、native/emulator 両方の #1645 を現在の比較関数で確認する。default-install の失敗を mounted 成功で代替しない。
5. native fixture と private/mounted fixture の元3ファイルが全て 0644 で一致すること、metadata oracle の regular-file type bits と 0755/0644/0 境界、operation の durable runner 記録を確認する。
6. 同 head の coverage ジョブの実際の出力と U3/U9 LCOV を照合し、workspace と各既存対象の line coverage が 80%以上であることを確認する。専用 U10 が include-ignored で実行され成功したログ、追加 runtime 7 件と Python 37 件の実行も確認する。
7. docs の wall time が同 run の4 native/emulator rows と一致し、未検証の背景負荷条件を成功条件に読み替えていないことを確認する。性能倍率や新しい速度 threshold は追加しない。

CI 結果取得後に実際の job 名・ID、artifact schema、coverage 分母を固定して checker を具体化します。全入力保証、将来のプラットフォーム、背景負荷停止の未観測条件を checker が保証したとは主張しません。
