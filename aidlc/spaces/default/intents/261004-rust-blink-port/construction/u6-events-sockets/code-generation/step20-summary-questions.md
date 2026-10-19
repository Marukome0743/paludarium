# U6 Step20 の内容確認

## Consolidated Summary（2026-10-19）

- Plan Approval：Step 20 を足した計画を Approve Plan で承認済み。
- 根拠：人の指示「ワークフローの順で進めてください。U1 の確かめ直しから始めて、…」と、U6 の確かめ直し（review-06、NOT-READY、Major 4・Minor 2）の後の checkpoint での Request Changes（U6 の記録を直す。測定を CI に戻すかは、残りの Unit を見てからまとめて決める）。
- 直すもの：R-05（traceability.json の NFR8 の target を `ci.yml`、NFR9 を `rust-toolchain.toml` に替える）、R-06（source-manifest.json から消えた 3 本を外す）、R-07（今の状態の節を足し、今のコマンド・toolchain・受け入れの今の場所を書く。古い記述はその時点のものとし、古い見出しは「履歴：」にする。traceability.json の古い notes に時点の印を足す）、R-08（U6 だけの測定 3 つが 27d05de1 からどこでも測られていないことと、NFR3・NFR7・FR2.4〜2.7 の OK の根拠が 11c033c7 時点の履歴であることを書く。status は変えない）、R-09（呼ばれていない U6 の道具 4 つ）、R-10（`diff_u6` は coverage の job の中）、R-04（見出し名の参照）。
- 変えないもの：製品・CI・workflow・ほかの Unit の記録。手順書は計画のときに直した。
- 確かめ方：正式 sensor 2 件と、checkpoint での entry-f の exit 0。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
