# U10 current-source 検証の証拠更新

検証済み：旧 checker は U10 完了時の署名5b319a7072e698d8e7c2f94e4821bf584ec381fb / CI38010586387 と現在ソースを比較していました。後続の承認済み変更で native.py の optional extra_snapshot/prepare_fixture、differential.py の比較用 reporter、runtime、CI が進んだため、最初の native.py byte 比較で停止しました。未承認の実装変更を修復するための差戻しではなく、current-source 検証の証拠バインディングが古いことが原因です。

履歴 final-proof.json と traceability.json の bytes は保持しています。新しい u10-current-proof.json は現在の署名7eb1819f52acede33e83775374dd4ee93edf643b / CI38021278452を明示的に結びます。checker は旧署名が新署名の祖先であること、履歴hash、元37パスと追加comparison_args/testの全bytes、署名Verified/valid、同head全23ジョブ成功を検査します。

最新同名・非失効artifactを選び、proofのIDと一致すること、成果物created_atが成功した担当ジョブのstarted_at〜completed_at内であることを確認します。再試行APIの転送されたjob IDを成果物作成時刻の代替にはしません。native14/emulator16の同reporter比較ではstdout/stderr/exitを検査し、original-argvのnative14/emulator16は既存compare_originalによる安定結果照合と生stderr保持、#1645再現を追加検査します。期限30秒、static ELF、完全なライセンス監査、fixture0644、coverage80%は維持しています。

検証済み：`python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/test_verify_current_u10.py` は9テスト成功。stale/pending証拠、追加source欠落、誤った署名/古いartifactID/ジョブ時間外、timeout・非有限durationの拒否を含みます。

検証済み：ユーザーが修復を許可した既存コマンド `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py` はexit0。出力は `Verified finite U10: signed 7eb1819f52acede33e83775374dd4ee93edf643b, CI 38021278452, native14/emulator16, fixture0644, full guest audits, existing80% floors. No all-input/platform guarantee.` です。U11全体の完了や全入力保証は主張しません。

変更範囲はintent verification配下のchecker、focused tests、補足proof、本原因文書のみです。アプリケーションソースやU1/U11レビュー済み成果物は変更していません。
