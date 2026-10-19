# U15 Step7補足の内容確認

## Consolidated Summary（2026-10-17）

- Plan Approval：Step7補足を追記した計画を Approve Plan で承認済み。
- 7a（ネイティブmacOS、FR6.3・FR7.2・FR7.3）：起動直前に fork の `codex/u14-jit-wasm` の head が be45b36c であることを読み取りで確かめ、`gh workflow run u12-quality.yml --repo Marukome0743/paludarium --ref codex/u14-jit-wasm` を 1 回だけ起動する。push・workflow 変更・性能測定はしない。完了後に run・job・ログ・artifact を読み取り専用で保存し、digest を照合して macOS を判定する。失敗は原本を保存して止め、再試行しない。
- 7b（FR8.3）：新しい測定はしない。性能 runner が読む入力が旧正式性能（208fd965）と be45 で一致するかをローカルの照合スクリプトで確かめ、全部一致すれば旧測定を「再利用した測定」として結びつけ、違えば GAP のままにする。
- u15-acceptance producer は公開段階（FR10.1）に回す。公開設定は、その段階で必要な操作とタイミングを人に伝える。
- 結果を code-summary.md・traceability.json に反映し、正式 sensor、独立レビュー、正式検証、人の完了承認へ進む。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
