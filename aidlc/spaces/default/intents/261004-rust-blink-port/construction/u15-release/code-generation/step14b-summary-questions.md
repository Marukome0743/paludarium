# U15 Step14b の内容確認

## Consolidated Summary（2026-10-18）

- Plan Approval：Step 14b を足した計画を Approve Plan で承認済み。
- 根拠：Step13〜14 の後の人の判断（Q1「足す」・Q2「直す」・Q3「禁止を外す」・Q4「限定トークンで CI から」）。
- (1) `.github/workflows/release-check.yml` の coverage の固定集合に `scripts/release/acceptance.py` を足し、4 ファイルそれぞれ 80% 以上を確かめる。
- (2) `scripts/release/check.py` の validate で、版が決まっているときは "release version" を出さない。単体 1 件を足す。
- (3) `scripts/release/policy.py` の `protected_environment` で、自分のレビューの禁止を必須から外す。必須レビュアー 1 人以上と管理者の迂回の禁止は必須のまま。`docs/release.md` の手順 (2) を直す。
- (4) 最初の公開だけ、対象と期限を絞ったトークン（人が `release` environment の secret に置くもの）で `release.yml` から公開できるようにする。`release_gate` は「Trusted Publisher 登録済み」か「最初の公開の申告があり、11 crate と `@paludarium/wasm` がどの registry にもまだ無い」ときだけ認める。2 回目からは OIDC だけ。トークンの作り方・置き場所・公開後の失効と Trusted Publisher の登録を手順に書く。
- 試験：単体（申告なしで拒否、申告ありで既存の version があれば拒否、申告ありで未公開なら許可、トークンの値が出力・文書に出ない）、既存の統合試験、tests/release 全件・validate・package-check・coverage（4 ファイル各 80% 以上）。
- push・CI の起動はこの段階ではしない（前にもう一度確認する）。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
