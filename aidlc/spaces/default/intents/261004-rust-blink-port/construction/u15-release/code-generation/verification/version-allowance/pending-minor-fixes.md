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
3. 製品：再開の判定で crates.io の owners と npm の maintainers を確かめない。手順書の確認に明記し、できれば API での確認を足す。
4. 製品：crates.io の `yanked` を見ない。yank 済みの版は一致としない形にして試験を足す。
5. 製品・手順書：`publication-progress.json` を保存する手順だが、`release.yml` に artifact 化がない。手順書を直すか artifact にする。
6. 試験：`test_resume_stops_on_different_present_digest` の名前、`registries_absent(approved=None)` の扱い、`approved_digests` の 3 分岐の拒否の試験。
