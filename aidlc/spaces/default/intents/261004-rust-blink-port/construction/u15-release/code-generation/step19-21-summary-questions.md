# U15 Step19〜21 の内容確認

## Consolidated Summary（2026-10-18）

- Plan Approval：Step 19〜21 を足した計画を Approve Plan で承認済み。
- 根拠：人が案 1（層の積み重ねをやめ、e3c29d1d を起点にした新しい入口）を選び、案 `verification/entry-e3c29d1d-proposal.md` を承認した。除外の一覧には `mise.toml` と `tools/aidlc-recovery/` を入れる。
- Step 19：`verification/entry-e3c29d1d/entry.py` を作る。起点の記録（入口 v4 が e3c29d1d で exit 0 になった検証、CI 7 run、FR8.3 の原本）と v1〜v4 の bytes を固定し、もう実行しない。毎回確かめるのは、署名と系譜、変わったファイルの一覧、製品の全ファイル（除外あり）、CI（認めた 1 job だけ attempt 2）、速さの原本、upstream の tree の一致（後で使う）。
- Step 20：最初の binding（head は e3c29d1d、差は 0）と回帰を作る。回帰は各検査を外すと落ちる形にする。本番で 1 回実行して exit 0 を確かめる。拒否されたら除外を広げずに報告する。入口と binding は上書きしない。
- Step 21：独立レビューを受け、READY の後に、正式な確認コマンドとして採用するかを伺う。採用までは入口 v4 が正式な確認コマンドのまま。
- この 3 手順では、製品・workflow・lock を変えない。push・CI・計測・公開もしない。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
