## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-18
**Iteration:** 1
**Verdict Dictated:** no

対象：確認コマンドの入口 v4（`u15_candidate_v4.py`、`binding-11.json`、`test_u15_candidate_v4.py`、`ci-e3c29d1d.json`、`ci-jobs-e3c29d1d.json`、README の v4 の節、`pending-minor-fixes.md`、本番の実行 `run-1792319052786132000-7821/`）と、U15 Step 17 の製品差分（`scripts/release/check.py`、`policy.py`、`docs/release.md`、`tests/release/test_api.py`・`test_check.py`・`test_policy.py`・`test_publish_adapter.py`）。シェルは使わず、ファイルと保存された出力だけで確かめた。以下の `V` は `.../verification/version-allowance/`。

### 確かめたこと（file:line 付き）

**A. v4 の入口と binding**

- 許可の集合は v3 と同じ 15 ファイルで、広がっていない。`u15_candidate_v4.py:72-74` の `ALLOWED_PATHS_15` を、`v3()`（`:128`）と `verify_constants`（`:143`）が v3 の `ALLOWED_PATHS_15` との一致で要求する。16 個目の path は `verify_files`（`:252-254`）が `changed`/`unchanged` の集合一致で拒否し、`test_608`（`test_u15_candidate_v4.py:233-254`）が `scripts/release/package.py`・`acceptance.py` の追加で拒否することを確かめる。result.json の `allowed_paths`（`run-…/result.json:2722-2738`）も 15 ファイル。
- 変わった 7 ファイルは今の bytes = e3c29d1d の blob = binding-11 の固定、a54315f9 の blob = binding-10 の固定である。`verify_files`（`:257-266`）が `e['a54315f9_sha256']==pins[p]==sha(par[p])` と `sha(current)==e['e3c29d1d_sha256']==sha(new[p])` と両者が違うことを要求する（`pins` は binding-10 の 3 区分から作る `v3_pins`、`:166-170`）。ほかの 8 つは `:269` で 4 者（今・固定・e3c29d1d・a54315f9）の一致を要求する。`HEAD_FILES` が v3 の `MOVED` と `EXTRA_FILES` の部分集合の和であることも `:145` で固定。
- v3 は固定された bytes から実行され、そのまま呼ばれる。`v3()`（`:120-130`）は `V3_ENTRY_SHA256` を確かめてから `exec`、`HISTORY_V3`（`:66-67`）が v3 の入口・binding-10・回帰を bytes で固定する。v3 に見せるのは `verify`（`:282`）の `view_class()(a5_map)` の 7 ファイルだけで、`a5_map` は `verify_files` が `HEAD_FILES` から作る（`:263`）。`:283` が 7 つ全てを v3 が view 越しに読んだことを要求する。
- 旧 chain の子は v4 を実行する。`guarded_run`（`:310`）の `actual` は `SELF --logical-child`。`children.json:9-19` ほか 4 件はどれも `u15_candidate_v4.py --logical-child`、`exit 0`、stderr 空。`test_612`（`test_u15_candidate_v4.py:306`）が引数の並びを固定する。
- attempt 2 の許可は 1 run・1 job だけである。`verify_head`（`:217-219, :225`）は `attempt_1_failures` の完全一致、run 39114110570 だけ attempt 2、ほかは attempt 1 を要求し、`verify_rerun`（`:183-195`）は attempt 1 の失敗がちょうど 1 job（名前と id 117638480843、`failure`）、失敗の記録が 1 件、attempt 2 の全 job が success、job の集合が親と attempt 1 の両方と同じ、`started_at >= run_started_at` の job がその 1 つだけ、を要求する。`ci-jobs-e3c29d1d.json:71-134` の実データがそれに合う（attempt 2 の 29 job、再実行は Safari の `117645706087` だけ）。`test_606`（`:178-214`）は 20 以上の変異でそれぞれ拒否する。
- job の集合は親の記録から来る。`parent_job_sets`（`:172-181`）は binding-10 の `ci_jobs`（SHA-256 固定）から取り、`jobs_entry['expected']`（`:220`）に使う。`test_605`（`:168-177`）は新しい記録を書き換えて rebind しても拒否されることを確かめる。
- result.json は誇張していない。`FR10_1:'GAP'`、`U15_acceptance:'GAP'`、`unit_completed:false`、`formal_command_adopted:false`、`new_measurement:false`、`new_ci:false`（`result.json:2804-2809`）。11 ファイルの中身は証明しないと 2 言語で明記（`:2594-2596, :2778-2779`）。Safari の失敗の原因は「確かめていない」と書き、attempt 2 の成功を再発しない証明にしていない（`:2547`）。CI は「保存したJSONのみ、live 問い合わせなし」（`:2803`）。
- v3 の Minor 4 件：(1) v1 の性能の文は v4 の claim scope に残らない（`result.json:2550, :2552`、`test_614:347-350`）。(2) `v3_layer` の各行に `time_points` が付き、v2 の MOVED の行の `scope` も bb197e04 の時点の文になった（`result.json:485-534`）。(3) README の見出しは「v2（履歴…）」「v3（採用済み、履歴）」「v4（未採用）」（`README.md:3, :69, :145`）。(4) 版の分け方の規則が README に入った（`README.md:48-50`）。v3 の 3 ファイルは `HISTORY_V3` で bytes 固定されており、その場の上書きは検出される。
- 回帰の数は整合する。`V4_TEST_COUNT=16`（`test_600`〜`test_615` の 16 メソッド）、147 + 16 = 163（README の 163）。
- 検出できない回帰は見つからなかった。`test_613` は検出器が v3 の文を実際に見つけること（`:318-319`）、`test_614` は v1 の文が `scope3` にはあって `out` には無いこと（`:347, :350`）を確かめるので、チェックを外すと落ちる。

**B. Step 17 の製品差分（review-06 の R-16／R-17／R-18）**

- R-16（再開）：`registries_absent`（`check.py:148-168`）は、名前が 1 つでも存在し `approved` がある時だけ、存在する名前ごとに承認済み版を問い合わせ、版が無い（`:163`）、digest が読めない（`:164`）、承認済み digest が無いか違う（`:165`）をすべて `mismatched` に入れる。`resume` は `mismatched` が空の時だけ true。`authorize`（`:230-237`）は `mismatched` があれば、何も公開する前に拒否する。文書の値は `:229` で捨てる。宣言なし（`first_publication` が true でない）では検査自体を行わず、`policy.authentication`（`policy.py:76-77`）が「first かつ verified」を要求するので拒否される。`approved_digests`（`check.py:173-183`）は package artifact が無い・head 違い・`local_snapshot` が false でない・tarball が違う場合に止まる。`publish_artifacts` は `authorize` を再度呼び（`:275`）、存在する版を `registry_state` で承認済み digest と照合し（`:305`）、アップロード前に `actual==result['crates']` を要求する（`:280`）。テスト：`test_check.py:140-176`、`test_api.py:80-101`（`test_document_cannot_assert_resume`、`test_resume_without_first_publication_declaration_refused`＝`loaded==[]`）、`test_policy.py:70-77`。
- R-17（環境）：`publication_environments`（`check.py:188-202`）は許可リストで作る。`CARGO_ENVIRONMENT`（`:99`）に `GH_TOKEN`／`GITHUB_TOKEN`／`ACTIONS_ID_TOKEN_REQUEST_*` は無く、dry-run の環境にはトークンが入らず、cargo の upload にはモードのトークン 1 つだけが `CARGO_REGISTRY_TOKEN` として入る。npm（`:104-107`）は `CI`／`GITHUB_ACTIONS`／OIDC の要求変数／provenance が名指す GitHub の文脈／`NPM_CONFIG_USERCONFIG`／`NODE_AUTH_TOKEN` だけで、first-publication では `NODE_AUTH_TOKEN` が npm のトークンになり、crates.io のトークンは入らない。`:308, :312, :325` で正しい環境が渡る。レシートは非機密キーの白名単のみ（`:40`）、`publication-progress.json` はトークンを持たない（`:332`）、`check.main` が出力するのは `published/head/version/authentication` だけ。テスト：`test_check.py:178-203`、`test_publish_adapter.py:126-136`。
- R-18（文書）：`docs/release.md:182-194` の `paludarium*` は接頭辞一致であり、11 の名前を 1 つずつ列挙するのを推奨する、と直っている。R-16 の手順書（`:208-233`）とレート制限の注意（`:208-214`）も入った。

### Findings

**Prior findings**

| ID | Now | Severity | Note |
|---|---|---|---|

（このレビューへ渡された prior findings の行は無い。review-06 の R-16／R-17／R-18 は上の B で、Step 17 の差分が解消していることを確かめた。）

**New findings**

| # | Severity | Location | Finding | Required action |
|---|---|---|---|---|
| 1 | Minor | `V/run-1792319052786132000-7821/result.json:2595`（`claim_scope.u15_old_chain.approval`）。出所は `u15_candidate_v4.py:405`（`dict(scope['u15_old_chain'])` が v3 の文をそのまま引き継ぐ） | `u15_old_chain.approval` が v2 の時点の承認文「README.md・docs/release.md・tests/release の2つは bb197e04 のバイト列の固定で許可を足す」のまま残っている。同じ層の `claimed`（`:2587`）と `exact_bytes_scope`（`:2594`）は e3c29d1d の固定を言うので、1 つの `u15_old_chain` の中で時点が食い違う。v3 の Minor 2 と同じ種類の問題で、`test_613` の `FORBIDDEN` はこの文を拾えない。誇張ではなく、時点の書き忘れ。 | 次に入口を更新する時（v4b 以降）に、この文へ「v2 の時点の承認の引用」と時点を明記するか、`u15_old_chain` から外す。回帰の `FORBIDDEN` に `bb197e04のバイト列の固定` を足す。採用の妨げではない。 |
| 2 | Minor | `V/README.md:8` と `:32` | README:8 は「commit・push・CI の起動・再実行・性能の測定はしていません」と書くが、同じ節の README:32 は U12 の Safari の job を人が再実行したと書く。前者は「この入口を作る作業では」の意味だが、単独で読むと食い違う。 | README:8 に「この入口を作る作業では。e3c29d1d の CI の再実行（Safari の 1 job）は人が選び、`ci_rerun` に記録した」と範囲を足す。 |
| 3 | Minor | `scripts/release/check.py:157-168`、`docs/release.md:175-178` | 再開の検査は「存在する名前の版と digest が承認済みと同じ」ことだけを確かめ、その名前の所有者（crates.io の owners、npm の maintainers）は確かめない。承認済みの `.crate` と bytes まで同じものを第三者が先に公開していれば、再開が通る。固定の toolchain と公開された source から再現できる可能性は低いが、ゼロではない。手順書（`docs/release.md:175-178`）は所有を人が確認するとしているので、現状は人の確認に依っている。 | 公開の前に、手順の step 3 の確認に「各 crate の owners と npm の maintainers が自分たちであること」を明記する。可能なら次の Step で owners／maintainers の API 確認を足す。今の Unit の完了は妨げない。 |
| 4 | Minor | `scripts/release/check.py:134-146`（`published_digest`） | crates.io の版の応答にある `yanked` を見ない。承認済みの版が yank されていても、digest が同じなら「一致」として再開が通る。手順書は yank しないよう指示しているが、コードは強制しない。 | `published_digest` で `yanked` が真なら `unreadable` または別の理由で `mismatched` にし、テストを 1 件足す。 |
| 5 | Minor | `docs/release.md:216-218`、`.github/workflows/release.yml`（`upload-artifact` が無い）、`check.py:331-332` | 再開の手順は「`publication-progress.json` とログを保存する」ことを前提にするが、`release.yml` はこのファイルを artifact にしないので、job が終わると runner ごと消える（これは Step 17 より前からの状態）。再開の判定自体は live の registry 検査で行うので安全性には影響しないが、手順書の指示が実行できない。 | 手順書を「ログと job の画面を保存する」に直すか、`finally` の後で progress を artifact にする。 |
| 6 | Minor | `tests/release/test_publish_adapter.py:62, :107-116`、`check.py:158` | (a) `test_resume_stops_on_different_present_digest` は `check.authorize` を差し替えて実行する（`:62`）ので、実際に拒否するのは既存の `registry_state`（`check.py:305`）であり、R-16 の新しい検査ではない（R-16 側の同等の試験は `test_api.py:87-91` にある）。名前が実際より強く読める。(b) `registries_absent` は `approved=None` で名前が存在すると `present` 非空・`mismatched=[]` を返す（`:158`）。今の呼び出しは必ず `approved` を渡すので害は無いが、`mismatched` が空だから安全、と読む将来の呼び出しの罠になる。(c) `approved_digests` の `passed`／`local_snapshot`／tarball 本数の分岐（`:178-179`）に拒否のテストが無い（head 違いと tarball の違いだけある）。 | (a) 試験名を実態に合わせる。(b) `approved is None` で名前が存在する場合は `resume=False` に加えて `mismatched` に理由を入れるか、`approved` を必須にする。(c) 3 分岐に試験を足す。 |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 本番の実行 `run-1792319052786132000-7821/`（保存された出力の読み取り） | `u15_candidate_v4: PASS`、旧 chain の `source_compatibility: PASS`、子 4 件 `exit 0` で stderr 空、`FR10_1`/`U15_acceptance` は `GAP` | 実行の結果は上の A の確認と整合する。 |
| 回帰（README の記録の読み取り） | 163／163、skip 0（v3 の 147 + v4 の 16） | 数は `test_u15_candidate_v4.py:25-26` の定数とメソッド数に一致。このレビューでは実行していない。 |
| ハッシュの再計算 | 未実施 | シェルが使えないため、入口・binding・回帰の SHA-256 は再計算していない。コード定数（`:62, :64, :95`）・binding-11・result.json（`:4-9`）・README の値の相互一致だけを確かめた。入口の `--entry-sha256` が実ファイルのハッシュと一致することは、実行のたびに `check_pins`（`:111`）が強制する。 |
| view-calls の記録 | 未読 | ファイル名に実行時刻の ns が含まれ、フォルダを列挙できなかったため読めていない。旧 chain の親が view 越しに許可の古い bytes を読んだことは、`run_old_chain` の検査（`:339`）と result.json の `old_chain` で間接的に確かめた。 |

### Summary

入口 v4 は、許可の 15 ファイルを広げず、7 つの変更を e3c29d1d と a54315f9 の両方の blob で固定し、v3 を固定した bytes のまま呼び、attempt 2 を 1 run・1 job に限っている。result.json に誇張はなく、v3 の Minor 4 件は実際に直っている。Step 17 の差分は R-16（不一致・欠落・読めない digest・宣言なしは公開前に拒否、文書は再開を主張できない）、R-17（cargo に GitHub／OIDC 要求の変数を渡さず、npm には provenance と first-publication のトークンだけを渡し、トークンは出力されない）、R-18 を満たす。Critical・Major は無く、Minor 6 件はどれも採用を妨げない。
