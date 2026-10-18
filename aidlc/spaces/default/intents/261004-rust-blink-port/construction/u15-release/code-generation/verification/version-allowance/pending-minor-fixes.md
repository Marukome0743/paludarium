# 次の入口の更新でまとめて直すこと（2026-10-18）

人は v3（`u15_candidate_v3.py` ebb67894…、`binding-10.json` 44f7c2a9…）を、独立レビュー `independent-review-03.md`（READY）の Minor 4 件を残したまま検証コマンドとして採用した。次に入口を更新するときに、次の 4 件をまとめて直す。

1. `claim_scope.u15_version.performance` に v1 の文「bb197e04 original checked and recorded only」が残っている。a54315f9 の原本も確かめて記録していることを書く。
2. `v2_layer` の MOVED の 2 行で、`new_sha256` は bb197e04 の値、`scope` の文は a54315f9 のもので、1 行の中で時点が食い違っている。どちらかにそろえるか、時点を明記する。
3. `README.md` の 77 行目の見出しが「v2（現行、未採用）」のまま。v2 は採用の後に v3 で置き換えられた履歴であることに直す。
4. 最初の v3（`ae9a0b7b…`／`c262b40e…`）はその場で書き換えたため、拒否された run `run-1792310402280740000-18124/` が指す入口の bytes が残っていない。今後は採用前でも版を分けて残す（hash と経緯は README にある）。

## v4 での対応（2026-10-18、入口 v4 `u15_candidate_v4.py`・`binding-11.json`）

v3 の 3 つのファイル（`u15_candidate_v3.py`・`binding-10.json`・`test_u15_candidate_v3.py`）は変えていない（v4 が `HISTORY_V3` として bytes で固定する）。直したのは v4 の出力と README だけである。

1. v4 の `claim_scope.u15_version.performance`（と日本語の `performance_ja`）は、bb197e04（run 39089194062）・a54315f9（run 39096893624）・e3c29d1d（run 39114108809）の原本をそれぞれ確かめて記録したこと、中の FR8.3 の根拠は今までどおり 1ceae86c であることを書く。v1 の文は v4 の claim scope に残らない（回帰 test_614）。
2. v4 の result.json の `v3_layer`（v3 の検査の記録）では、各行の値に `time_points` を付け、値ごとに時点を書く。v2 の層の行（`v3_layer.v2.u15.old_chain_files`）は、`old_sha256` が旧 chain の binding-v4 の固定、`new_sha256` が bb197e04 の blob（binding-09）であると書き、`scope` の文もこの時点の文にした（a54315f9 の文を入れない）。v3 の層の行には a54315f9 の時点を書き、層の先頭の `time_point` に「この層の『今のbytes』は v4 が view で見せた a54315f9 の bytes」と書く。今の bytes（e3c29d1d）の主張は `u15_e3c29d1d` と `allowance` にだけある（回帰 test_613・test_614）。
3. README の見出しを「v2（履歴、採用の後に v3 で置き換えた）」と「v3（採用済み、履歴）」に直し、v4 を「v4（未採用）」とした。
4. README の v4 の節に、採用の前でも入口と binding を上書きしないこと、本番の実行の拒否の後に直すときは v4 と拒否された run を残して v4b と binding-12 を新しく作ることを書いた。

## v4 の採用で残したもの（2026-10-18、独立レビュー 04 の Minor 6 件）

人は v4（`u15_candidate_v4.py` dfb0e03a…、`binding-11.json` fb466da7…）を「採用、Minor は次で」として検証コマンドに採用した。次に製品か入口を更新するときに、次の 6 件をまとめて直す（詳細と file:line は `independent-review-04.md` の Findings）。

1. 入口：`claim_scope.u15_old_chain.approval` に v2 の時点の承認文が時点の表示なしで残る。時点を明記するか外し、回帰の `FORBIDDEN` に足す。
2. 入口：README の v4 の節の「再実行していません」に「この入口を作る作業では」と範囲を足す（Safari の 1 job の再実行は人が選んだもの）。
3. （2026-10-18 の U15 Step24 で直した）製品：再開の判定で crates.io の owners と npm の maintainers を確かめない。手順書の確認に明記し、できれば API での確認を足す。
4. （2026-10-18 の U15 Step24 で直した。ただし下の「U15 の review-09 で残したもの」の 2 のとおり、npm の `deprecated` と `registry_state` の扱いが残る）製品：crates.io の `yanked` を見ない。yank 済みの版は一致としない形にして試験を足す。
5. （2026-10-18 の U15 Step24 で直した）製品・手順書：`publication-progress.json` を保存する手順だが、`release.yml` に artifact 化がない。手順書を直すか artifact にする。
6. （2026-10-18 の U15 Step24 で直した）試験：`test_resume_stops_on_different_present_digest` の名前、`registries_absent(approved=None)` の扱い、`approved_digests` の 3 分岐の拒否の試験。

## U13 の承認で残したもの（2026-10-19、U13 の review-08 の Minor 1 件）

人は U13（Code Generation の確かめ直し、Step16〜18）を、review-08 の Minor 1 件を残したまま承認した。次に U13 の記録を更新するときに直す（詳細は `construction/u13-windows-host/code-generation/reviews/review-08.md`）。

1. 記録：U13 の `code-generation-plan.md` に「前回のSummary」という見出しが 3 つ並ぶ（Step17・Step16・Steps13〜15）。節の見出しの「前回」「前々回」と同じく、Step の古い順に「前々回」「3 回前」などに揃えるか、相対の言葉を外して Step 名だけにする。

## 入口 f の独立レビュー 04 で残したもの（2026-10-19、`verification/entry-e3c29d1d/independent-review-04.md`）

入口 f（`entry-f.py`）は、この Minor 2 件と注記 2 件を残したまま、binding-e06f とともに人が正式な確認コマンドとして採用した。次に入口を作り直すときに直す。

1. 試験：`test_entry_f.py` は `test_entry_e.py` を削った写しで、上位集合になっていない。`entry-f.py` に残っている検査のうち、鎖の端と並びの検査（e の test_23 の 2 つ目のケース）、記録の `tree` の欠落と `parents` がリストでない場合、別の親を模したケース、`commit_records` のキーなどのケースが無くなった。
2. 試験：test_10 は、`--no-replace-objects` と `GIT_NO_REPLACE_OBJECTS=1` のどちらか片方だけを外しても通る（どちらも単独で replace ref を辿らないため）。それぞれが単独で効くことを示していない。upstream の head に使う `git_has_commit` は、replace ref に対して動かしていない。
3. 注記：test_11 は `info/grafts` のファイルを拒否することを示すが、手元の git がそのファイルに従うことは示していない（今の git は grafts を無視することがある）。拒否は安全側の近似で、観測した攻撃ではない（対応は不要）。
4. 注記：入口の bytes と binding は作業コピーから固定していて、push した head の tree からではない。`aidlc/` のファイルの中身は比べない。これは not_claimed の一覧にある（対応は不要）。

## U15 の review-09 で残したもの（2026-10-19、製品・workflow の 3 件）

人の方針（workflow の直しは記録に書き、あとでまとめて決める）に従い、次の製品の変更でまとめて直す（詳細は `construction/u15-release/code-generation/reviews/review-09.md`）。

1. workflow：`nightly.yml` が `u14-fuzz.yml` を直接呼び、さらに `u14-quality.yml` の中の `u13-fuzz` も同じ fuzz を呼ぶので、毎晩同じ fuzz が 2 回走る。
2. 製品：取り消しの確認で、npm の `deprecated` を見ていない（チームの方針は crates.io の yank と npm の deprecate）。authorize は `yanked` が明示の false でなければ拒否するが、公開の繰り返しの `registry_state` は `yanked` が無い場合を通す。
3. 文書：`docs/release.md` に内部の Step・review の番号が残っている。`construction/ci-pipeline/ci-config.md` の「残す(20)」に `u11-safari-stability.yml` が載っていない。

## U15 の承認で残したもの（2026-10-19、U15 の review-10 の Minor 1 件）

人は U15（Step29）を、review-10 の R-32 を残したまま承認した。次にこの台帳を更新するときに直す。

1. 記録：この台帳の「v4 の採用で残したもの」の 1・2（入口 v4 の `claim_scope.u15_old_chain.approval` と README の v4 の節）に、v4 が履歴の入口になったこと（今の正式な確認コマンドは版 f）を書き、直すか閉じるかの印を付ける。

## CI Pipeline の確かめ直しで残したもの（2026-10-19、CI Pipeline の Q5 の A）

`construction/ci-pipeline/ci-config.md` の「入れた後の食い違い」のとおり、次の製品の変更でまとめて直す。夜間の fuzz が 2 回走ることは、上の「U15 の review-09 で残したもの」の 1 と同じ。

1. workflow：`u11-safari-stability.yml` が作業ブランチ `codex/build-and-test` へのそのファイルの push の起動条件を持つ（GitHub の手動起動が fork の既定のブランチの workflow しか起動できなかったため、人の判断で足した）。`ci-config.md` の残す一覧に足し、push の起動条件を外すか `main` に替える。
