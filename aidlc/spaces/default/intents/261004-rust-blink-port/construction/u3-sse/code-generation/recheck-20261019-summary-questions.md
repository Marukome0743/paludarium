# U3 確かめ直しの記録の直し（2026-10-19）の内容確認

## Consolidated Summary（2026-10-19）

- Plan Approval：「今回の計画：確かめ直しの指摘を記録で直す（2026-10-19）」を足した計画を Approve Plan で承認済み。
- 根拠：人の指示「ワークフローの順で進めてください。U1 の確かめ直しから始めて、…」と、U3 の確かめ直し（review-06、READY、Major 2・Minor 4）の後の checkpoint での Request Changes（先に R-04〜R-09 を直す。呼び元が消えた製品の道具は次の push）。
- 直すもの：R-04・R-09（今の正式な確認コマンドを entry-f・binding-e06f と書き、古い入口と「未実行」はその時点の記述とする）、R-05（手順書の `+nightly-2026-10-01` と置き換え済みの `u3_tests:: --fail-under-lines 80` に注記。今は `nightly-2026-10-11`）、R-06（source-manifest.json から `u3-current-verification.yml` を外す。`.github/scripts/u3-current-diagnostic.py` は次の push）、R-07（ASan の今の裏付けは run 39149194521）、R-08（Safari の今の確認は `u11-safari-stability.yml` の run 39143558642 と `u11-acceptance.yml`）。
- 直し方：code-summary.md の先頭に「現在の状態（2026-10-19 JST）」節を足し、古い「現行」「今回」の見出しは「履歴：」にする（本文は変えない）。手順書の先頭の新しい節と 2 つの見出しの注記は計画のときに書いた。製品・CI・workflow・traceability.json は変えない。
- 確かめ方：正式 sensor 2 件と、checkpoint での entry-f の exit 0。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
