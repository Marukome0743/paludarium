# e3c29d1d を起点にした新しい確認コマンドの入口（Step 19〜20）

## 2026-10-19 の注記（Step29）

今の正式な確認コマンドは、版 f の `entry-f.py`＋`binding-e06f.json`（head 27d05de1、2026-10-19 に人が採用。intent 直下の `verification-command.txt` の 1 行目）です。下の「現行は版 c」「版 d は…まだ正式な確認コマンドではない」と、版の経緯の表の f の行の「採用の前」「本番の実行はまだ」は、それぞれ書いた時点の記述です。版 f の本番の実行は、下の「binding-e06f」節のとおり exit 0 でした。下の本文と、入口・binding・回帰のファイルは変えていません。

承認済みの計画 Step 19〜20 と、承認済みの案 `../entry-e3c29d1d-proposal.md` のとおりに作りました。v1〜v4 の層は重ねていません。入口は v1〜v4・旧 chain を import も実行もせず、それらの bytes が変わっていないことだけを確かめます。

**2026-10-19 追記（版 f）：独立レビュー 03（`independent-review-03.md`、READY、Minor 6）のあと、人の判断で版 f（`entry-f.py`＋`binding-e05f.json`）を作りました（下の「版 f」）。** 人の判断（原文）：「版 f で Minor 1（--no-replace-objects）と Minor 3（push 前の commit id に頼る回帰）を直してください。残りの Minor は次の更新で構いません。」版 f も採用の前で、版 e（`entry-e.py`・`binding-e05.json`・`test_entry_e.py`）は変えずに履歴として残します。

**2026-10-19 追記（人の判断で版 e）：新しい版 e（`entry-e.py`＋`binding-e05.json`）を作りました（下の「版 e」）。** 計画の Step 25・28 は「版 d」と書いていますが、版 d は GitHub の compare の 300 件の上限のため、`aidlc/` だけの commit a7aecb72（741 ファイル）を含む新しい head では必ず止まります。人は 2026-10-18 に「A で進めてください。各 commit の tree のハッシュで照らし合わせる入口の版 e を作り、独立レビューの後に採用を伺ってください。記録と製品は一緒に 1 回で push します。」と判断し、版 d を版 e に替えました。版 e も独立レビューと人の採用の前で、まだ正式な確認コマンドではありません。版 d は使わずに履歴として残します。

**2026-10-19 追記（Step 25）：新しい版 d（`entry-d.py`＋`binding-e04.json`）を作りました（下の「版 d」）。** 版 d は独立レビューと人の採用の前で、まだ正式な確認コマンドではありません。採用までは、人が 2026-10-18 に採用した版 c（`entry-c.py`＋`binding-e03.json`）が正式な確認コマンドのままです。次の段落は、版 c を作った時点の記述です。

**現行は版 c（`entry-c.py`＋`binding-e03.json`）です。** 版 v1（`entry.py`）と版 b（`entry-b.py`）は、上書きせず履歴として残しています（下の「履歴」）。どの版もまだ**正式な確認コマンドではありません**。採用（Step 21：独立レビューと人の承認）までは、今の入口 v4（`../version-allowance/u15_candidate_v4.py`、binding-11）が正式な確認コマンドのままです。入口と binding は採用の前でも上書きせず、直すときは新しい版を作ります。

## 版の経緯

| 版 | 入口・binding・回帰 | 本番の実行 | 次の版にした理由 |
|---|---|---|---|
| v1 | `entry.py`・`binding-e01.json`・`test_entry.py`（30 件） | exit 1：`run-1792325657506892000-42086/refusal.json` | 手元の `.aidlc-version` の bytes の違いと、head に無い 11 の path が除外の一覧に当たらなかった。人が判断した（下の判断 1） |
| b | `entry-b.py`・`binding-e02.json`・`test_entry_b.py`（36 件） | exit 0：`run-1792326450015585000-34598/result.json` | 独立レビュー `independent-review-01.md` が NOT-READY（Major 3、Minor 6） |
| c（2026-10-18 に採用） | `entry-c.py`・`binding-e03.json`・`test_entry_c.py`（40 件） | exit 0：`run-1792327873535813000-33039/result.json` | 計画 Step 25：compare の 300 件の上限と、独立レビュー 02 の Minor |
| d（使わない、履歴） | `entry-d.py`・`binding-e04.json`・`test_entry_d.py`（46 件） | exit 0：`run-1792335808099662000-95657/result.json` | compare の 300 件の上限で、a7aecb72 を含む head を通せない。人の判断で版 e に替えた |
| e（使わない、履歴） | `entry-e.py`・`binding-e05.json`・`test_entry_e.py`（31 件）・`commits-e3c29d1d.json` | 本番の実行はしていない | 独立レビュー 03 は READY（Minor 6）。人の判断で Minor 1・3 を版 f で直す |
| **f（採用の前）** | `entry-f.py`・`binding-e05f.json`・`test_entry_f.py`（34 件） | 本番の実行はまだ（push の後の新しい head で行う） | — |

## binding-e06f（head 27d05de1、2026-10-19、人が採用）

- 入口は版 f（`entry-f.py`）のままで、binding だけを新しくした。binding-e05f までは上書きせずに残している。
- commit の並び：e3c29d1d → 8b415a7c（記録）→ 8360be2e（製品 45 件と記録 42 件）→ 27d05de1（`u11-safari-stability.yml` に push で起動する条件を足しただけ）。4 つとも Verified。記録は `commits-27d05de1.json`。
- 変わったファイル：aidlc/ の外が 45 件、aidlc/ の中が 766 件。
- CI：head の 8 run がすべて成功した。記録は `../ci-27d05de1/`（`build_records.py` は GitHub から読み取るだけ）。
  - 必須の 7 workflow に、U11 Safari stability（run 39143558642、10 回とも成功、やり直しは 0 回）を足した。その 12 job は、人の判断の原文を付けた新しい集合にしている。
  - U12 current full quality（run 39149189719）は attempt 2。attempt 1 では `u12-fuzz / fuzz (vfs_paths)`（job 117739162319）だけが、apt.llvm.org に接続できずに落ちた。fuzz は走っていない。人の判断で、その job だけをやり直した。
  - 8360be2e で動いた 5 run は履歴（`../ci-8360be2e-history/`）で、ここでは使わない。Step 27 の「CI 一式を 1 回だけ」とは違い、5 つは 2 回目の起動になった（人の判断）。
- FR8.3：U14 current full quality（run 39149187727）の u11-node で p=1/1024、passed: true。
- 本番の実行：`run-1792347449027149000-39214/` で exit 0（0.66 秒）。
- 人が採用した（2026-10-19、Approve）。正式な確認コマンドの SHA-256 は 00f5c883…。entry-c と binding-e03 は履歴になった。

## 版 f（独立レビュー 03 の Minor 1・3、2026-10-19、binding-e06f で採用。作成時の見出しは「採用の前」）

| ファイル | SHA-256 |
|---|---|
| `entry-f.py` | `185677712836e73d6a716657a24521c42581504550f9f398c5bb1ca7eaa4a46f` |
| `binding-e05f.json` | `5c9d99de2ebfb9fe48db7c9662e790d5f24b0feaa06ed2e2570c4863b2157fc0` |
| `test_entry_f.py` | `3b5061b3a865ab1334614a7b29b344bb74beeaa78253c9811773c5c70b95a476` |

版 e の検査をすべて残し、次を足しました。binding の名前は `binding-e05f.json`（入口は今までどおり `binding-e*.json` から SHA-256 で選ぶので、`e` で始まる名前にしました）。中身は binding-e05 と同じで、schema を版 f にし、履歴の固定に版 e の 3 ファイルと `commits-e3c29d1d.json` を足して 28 ファイルにしました（`commits-e3c29d1d.json` は起点の commit の記録として引き続き使います）。新しい head 用の binding は push の後に作ります。

- **Minor 1（replace ref）**：git を呼ぶすべての所で `--no-replace-objects` を付け、環境に `GIT_NO_REPLACE_OBJECTS=1` を入れました。さらに、系譜を確かめる前に、手元の git が本当の commit と違う親を答えうる状態を拒否します：shallow のリポジトリ（`rev-parse --is-shallow-repository` が `true`）と、grafts のファイル（`rev-parse --git-path info/grafts` の場所にファイルがある）。結果の `repository_state` に書きます。
- **Minor 3（push 前の commit id）**：版 e の回帰 28・31 は手元の a7aecb72 に頼っていました。版 f の回帰は、回帰の中で一時の git リポジトリ（このフォルダの中に作って消す）を作り、そこで確かめます：根の commit A、`aidlc/` の中の 350 ファイルと `docs/x.md` の計 351 ファイルを変える commit B、replace にだけ使う commit C。本当の作業コピーの commit id には頼りません（e3c29d1d と a54315f9 は push 済みの起点とその親です）。

### 回帰（版 f、34 件）

`discover -p 'test_entry_f.py'` で 34 件すべて成功、skip 0。e3c29d1d の bytes での正の対照は、版 e と同じく回帰専用の overlay（45 path）で示しています。

- 新しい回帰：一時のリポジトリで `git replace B C` を作ると、そのままの git は B の tree として C の tree を答えるが、入口は B の本当の tree と親を答え、本当の tree を書いた記録は通り、C の tree を書いた記録は拒否される（test_10）。grafts のファイルを置くと拒否（test_11）。`--depth 1` の shallow な clone では拒否され、その clone では B の親が見えないこと（test_12）。`verify()` で、リポジトリの状態の確認が系譜の前に行われること（test_13）。351 ファイルを変える commit で系譜と変わったファイルが通ること（test_28）。`aidlc/` の件数の多い・少ない・ハッシュの違い（test_31、一時のリポジトリで）。
- 検査を外すと落ちることを、`entry-f.py` のソースをメモリの中で書き換えて 9 通りで確かめました。対象は、フラグだけ・環境だけ・両方、shallow、grafts、状態の確認の呼び出し、履歴の entry-e の固定、tree、`aidlc/` の件数です。フラグと環境の両方を外すと、一時のリポジトリで入口の `git_tree(B)` が C の tree を答えることも、別に確かめました。
- フォルダ全体の `discover -p 'test_*.py'` は 217 件。失敗は 52 件（failures 32・errors 20）で、版 e・f の失敗は 0 件です。失敗はすべて v1・b・c・d の回帰で、作業コピーが変わったことと、生きている `unit.json` が置き換わったことによります。
- 版 e の回帰 28・31 は、手元の a7aecb72 が残っている間だけ通ります。版 e は履歴なので変えていません。

### 残している Minor（次の更新で直す、人の判断）

独立レビュー 03 の Minor 2（test_34 の `co_varnames` の行は意味がない）、Minor 4（13 か所の書き換えの確かめは、手順と出力をフォルダに残していない。版 f の 9 通りも同じ）、Minor 5（起点と違う head での `verify()` 全体の回帰がない）、Minor 6（正の対照は overlay の 45 path と本当の作業コピーについては何も言わない。本当の作業コピーでの確認は、新しい head で初めて行う）。

## 版 e（人の判断、2026-10-19、使わない。作成時の見出しは「版 e（人の判断、2026-10-19、採用の前）」）

| ファイル | SHA-256 |
|---|---|
| `entry-e.py` | `c362be77807fef060e006c06d3754b12deb026f974d028fd739b0b2dab0a78f9` |
| `binding-e05.json` | `6fa2750643a3cadeca5836864ec3a3b6349075c57f22725924a453d49eec1c9d` |
| `test_entry_e.py` | `6a1604590a7ec29cc77ed27a4ea6049d636f9de49a45c262cb44ff3e4dea6a42` |
| `commits-e3c29d1d.json` | `0f5d46245fc1ac3658bb228b5679377bf479f99afffe34706dba9453cce5a888` |

版 d の検査をすべて残し、系譜と変わったファイルの照合だけを替えました。

- **系譜（各 commit の tree のハッシュ）**：binding の `commit_records` が指す保存した記録（`GET repos/Marukome0743/paludarium/commits/<sha>` の `sha`・`parents[].sha`・`commit.tree.sha`・`commit.verification.verified`／`reason` の写し。SHA-256 で固定）が、起点から head までの並びの commit をちょうど含むこと（足りない・多い・重なりは拒否）。どの commit も Verified（`reason: valid`）、tree のハッシュが手元の `git rev-parse <sha>^{tree}` と同じ、親が手元の git の親と同じで、並びの前の commit と同じ。手元の `rev-list base..head` の並びも同じ。tree のハッシュが同じなので、GitHub と手元の git でその commit の全ファイルの中身が同じ、という主張にしています（git のハッシュ SHA-1 に衝突がないことが前提）。`commits-e3c29d1d.json` は 2026-10-19 に読み取りの `gh api` GET で e3c29d1d の記録を保存したものです。
- **変わったファイル（手元の git だけ）**：`git diff-tree -r --no-renames e3c29d1d head` で数えます。`aidlc/` の外は binding の `changed_files` とちょうど同じ（人が読める一覧）、`aidlc/` の中は binding の `aidlc_changed`（`count` と、並べた一覧の SHA-256。UTF-8、1 行に 1 つ、`\n` でつなぎ最後に改行なし）と同じことを求めます。
- **GitHub の compare は使いません**（ファイルの一覧も、`status`・`ahead_by`・`behind_by`・`merge_base` も見ない）。系譜は上の記録と手元の git で確かめます。保存した CI の記録に compare があっても読みません（回帰 test_34）。
- ほか（全追跡ファイルの bytes、除外、CI、速さ、git の設定の遮断、再実行の上限 2）は版 d のまま。履歴の固定は 24 ファイル（v1〜v4 の 12 と、`entry.py`〜`entry-d.py`・`binding-e01〜e04`・`test_entry.py`〜`test_entry_d.py` の 12）。
- binding は、e3c29d1d（差 0）用の `binding-e05.json` だけを作りました。新しい head 用は、push の後に CI と各 commit の記録を保存してから `binding-e06.json` として作ります。

### 回帰（版 e、31 件）

`discover -p 'test_entry_e.py'` で 31 件すべて成功、skip 0。

- **e3c29d1d の bytes での正の対照は overlay で示しています。** 今の作業コピーは Step 22〜24 の製品の変更を持つので、そのままでは e3c29d1d と違います（test_00 で、overlay なしでは拒否されることを確かめる）。setUpClass が手元の git から、e3c29d1d の blob と違う・無い追跡ファイルをその blob として見せ、除外に当たらない未追跡のファイルを無いとして見せる回帰専用の overlay を作ります（45 path。一覧は回帰の標準エラーに出す。`aidlc/` の path は入らない）。本番の実行は、push の後の新しい head で行います（今は行っていません）。
- 新しい回帰：tree の不一致（head・親・欄なし）、記録の親と手元の親の違い、並びの親の違い・並びの順・手元の順の違い、未署名（`verified: false`・`reason` 違い・文字列の `"true"`・欄なし）、記録に無い commit・多い commit・重なり、記録のファイルの固定・形・repository、保存した e3c29d1d の記録が手元の git から作った記録と同じこと、301 件以上（a7aecb72 の 741 ファイル）を変えた commit でも系譜と変わったファイルが通ること、`aidlc/` の外の一覧の多い・少ない・並び、`aidlc/` の件数の多い・少ない・ハッシュの違い、`aidlc_changed` の形、compare を空・違う値・無しにしても結果が変わらないこと。版 d から引き継いだ作業コピー・CI・速さ・履歴・コマンド行の回帰。
- 新しい検査を外すと落ちることを、`entry-e.py` のソースをメモリの中で 1 か所ずつ書き換えて 13 か所で確かめました（署名、tree、手元の親、並びの親、記録の網羅、重なり、記録の固定、手元の順、`aidlc/` の外の一覧、`aidlc/` の件数、ハッシュ、`aidlc_changed` の形、履歴の entry-d の固定）。
- フォルダ全体の `discover -p 'test_*.py'` は 183 件で、失敗は 52 件（failures 32・errors 20）。どれも v1・b・c・d の回帰で、本当の作業コピーを e3c29d1d と比べるもの（製品の変更のため）と、生きている `unit.json` が置き換わったことによるもの。版 e の 31 件は 0 件失敗。古い版の回帰は履歴なので変えていません。

### 確かめていないこと（版 e）

版 c・d の「確かめていないこと」に加えて：tree のハッシュの一致が中身の一致を意味するのは SHA-1 の衝突がないことが前提であること。保存した commit の記録が GitHub の今の状態と同じであること（確認のときに問い合わせない）。本番の実行（新しい head で行う）。

## 版 d（Step 25、2026-10-19、使わない。作成時の見出しは「版 d（Step 25、2026-10-19、採用の前）」）

| ファイル | SHA-256 |
|---|---|
| `entry-d.py` | `7c73492e0b269770bfdea0a63b8f1bd3d87a44b47bc9d091268b375b69e4fac2` |
| `binding-e04.json` | `0fca5fc33f62f9a36262c3ee562b7f61ef31c49cb29ebddeb4d76aaecc8e1981` |
| `test_entry_d.py` | `5548a3b0df1b662d19148f8e5ac24b450ef3955cac0a645b2044cdd6861d916b` |

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-d.py --entry-sha256 7c73492e0b269770bfdea0a63b8f1bd3d87a44b47bc9d091268b375b69e4fac2 --binding-sha256 0fca5fc33f62f9a36262c3ee562b7f61ef31c49cb29ebddeb4d76aaecc8e1981
```

版 c の検査はすべて残し、次を変えました。

- **変わったファイルは `aidlc/` の外だけで照合**：binding の `changed_files` には `aidlc/` の外のパスだけを書きます（`aidlc/` のパスを書くと拒否）。手元の git（`diff-tree`）の `aidlc/` の外の一覧と、保存した compare の `aidlc/` の外の一覧が、binding とちょうど同じことを求めます。GitHub の compare は 300 件までしか返さないので、保存した compare のファイル数が **300 件未満**（切り詰められていない）でなければ拒否します。compare の `aidlc/` の行は比べません（blob も見ない）。`aidlc/` の中は手元の git だけで数え、結果の `aidlc_changed_paths` に件数と、並べた一覧の SHA-256（UTF-8、1 行に 1 つ、`\n` でつなぎ最後に改行なし）を書きます。
- **独立レビュー 02 の Minor**：名前で除外したフォルダの行の注記を、`aidlc/` は「中は比べない」、`.git/`・`.jj/` は「追跡ファイルを持たない」に直しました。再実行の許可は binding あたり 2 つまで（`MAX_RERUNS`。結果の `differences_from_base.rerun_limit`）。保存した artifact の一覧の u11-node は `expired` が `false` で、`workflow_run.repository_id` が fork の id（`1408718913`、2026-10-18 に読み取りの `gh api repos/Marukome0743/paludarium` で確かめた）でなければ拒否します。git は利用者・システムの設定を読みません（`GIT_CONFIG_GLOBAL` を null device、`GIT_CONFIG_NOSYSTEM=1`、`-c core.fsmonitor=false`）。checkpoint の記録の写しを置いたこと（Minor 5）は、code-summary に書きました。
- **履歴の固定**：v1〜v4 の 12 ファイルに、この入口の前の版（`entry.py`・`entry-b.py`・`entry-c.py`・`binding-e01〜e03`・`test_entry.py`・`test_entry_b.py`・`test_entry_c.py`）の 9 ファイルを足して 21 ファイル。除外の一覧は版 c と同じです。

### 回帰（版 d、46 件）

`discover -p 'test_entry_d.py'` で 46 件すべて成功、skip 0（製品の変更 Step 22〜24 の前の作業コピーで。変更の後は、本当の作業コピーを e3c29d1d と比べる 14 件が作業コピーの違いで落ちる。新しい head の binding で確かめ直すのは Step 28）。新しく足した回帰：`aidlc/` の行の注記（test_09）、利用者の設定を読まないこと（壊れた `~/.gitconfig` と `$XDG_CONFIG_HOME/git/config` の一時 fixture。そのままの git は失敗し、入口の git は通る。test_05b）、`aidlc/` のパスを binding に書くと拒否（test_20）、compare の `aidlc/` の行は比べず、製品の行の多い・少ない・重なりは拒否（test_21）、手元の commit a7aecb72（`aidlc/` だけ 741 ファイル）で、300 件ちょうどの compare は拒否・299 件なら通り件数 741 と一覧の SHA-256 が出る（test_22）、一覧の SHA-256 の決まり（test_23）、再実行の許可の上限（test_47）、`expired`・`repository_id`（test_53）、履歴の 21 ファイル（test_63）、binding-e01〜e03 を渡すと拒否（test_64）。

新しい検査を外すと落ちることを、`entry-d.py` のソースをメモリの中で 1 か所ずつ書き換えて 11 か所で確かめました（ファイルは変えない）：300 件の上限→test_22、binding の `aidlc/` のパス→test_20・22、手元の一覧を `aidlc/` の外に限ること→test_22、compare の製品の一覧→test_21・22、重なり→test_21、再実行の上限→test_47、`repository_id`→test_53、`expired`→test_53、`GIT_CONFIG_GLOBAL`→test_05・05b、`aidlc/` の注記→test_09、履歴の entry-c の固定→test_01 ほか 19 件。

フォルダ全体の `discover -p 'test_*.py'` は 152 件のうち 4 件が失敗します（v1 の test_01・test_61、b の test_61、c の test_62）。どれも「生きている `unit.json` が起点の写しと同じ bytes」を前提にした回帰で、その記録が後の checkpoint（id `8123d7af-98e1-40a1-8c30-577c39f6e10c`）で置き換わったために落ちます。v1・b・c の回帰は履歴なので変えていません。版 d の test_62 は、置き換わった場合と同じ場合の両方を確かめます。

### 本番の実行（版 d、2026-10-19）

製品の変更（Step 22〜24）より前に、上のコマンドを 1 回実行し、**exit 0**。出力は `run-1792335808099662000-95657/result.json`（`c4cb4e11be0ec2d2baf7f64e0bf0ceeb716a9a648c21d00fc52cf357cc91d656`）。head＝起点＝e3c29d1d、`changed_paths` は空、`aidlc_changed_paths` は 0 件、675 ファイルのうち 673 が head と同じ bytes（残りは `.aidlc-version`・`mise.toml`）、`excluded_by_name` 27・`excluded_by_git_ignore` 10、`live_checkpoint_record` は「後の checkpoint（`8123d7af…`）に置き換わった。写しを使う」。

### 次の head での注意（Step 28）

手元の commit a7aecb72 は `aidlc/` だけで 741 ファイルを変えます。e3c29d1d から新しい head までの compare はこれを含むので、ファイル数が 300 件に達し、版 d は計画どおり「切り詰められているかもしれない」として拒否します。binding-e05 を作る前に、この扱い（例：compare を区間に分ける、または各 commit の tree の一致で代える）を人に伺う必要があります。

### 確かめていないこと（版 d）

版 c の「確かめていないこと」に加えて：`aidlc/` の中の変わったファイルが GitHub の compare と同じであること（手元の git だけで数える。GitHub の記録とは各 commit の tree の一致だけで結びつく）。

人の判断と指示：

1. 2026-10-18、選んだ選択肢「git の無視＋2 つ」：「git が無視するファイル（.gitignore、git check-ignore で読み取りだけ）を除外にし、.aidlc-version（bytes の違いを許す）と .venv-u15/ を除外の一覧に足す。入口と binding は新しい版（entry-b.py・binding-e02.json）で作り直す」
2. 独立レビュー 01（NOT-READY）の Major 3 件と Minor を、coordinator 経由の指示で版 c として直す（git の無視は head の tree にある `.gitignore` の規則だけ、bytes の違いを許す追跡ファイルは 2 つだけ、binding で検査を緩められないこと）。

## 版 c（2026-10-18 に採用。版 d の採用までは正式な確認コマンド。作成時の見出しは「版 c（現行）」）

| ファイル | SHA-256 |
|---|---|
| `entry-c.py` | `44a8d9d0388db18fb5730dd54e5bb40f178a309536f39b48dde90d1f5eaf1a5a` |
| `binding-e03.json` | `fd55262c37b6a50f71c58a677786a8af9aa7469defb3910853da64eadcbbf316` |
| `test_entry_c.py` | `371e87e56200cb23444a512627e468825b341cc1f6e012fd80848cc56f82e8b4` |
| `ci-artifacts-e3c29d1d.json` | `5f0ea0815149c918feae5ae0ad330f5f645a41807f5a7ba53cd51be637cf62c5` |
| `base-checkpoint-435bc5e0.json` | `b304628676add2c0f5f5603db279b2ad1e3acbe602bbed8068deeb898be10b06` |

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py --entry-sha256 44a8d9d0388db18fb5730dd54e5bb40f178a309536f39b48dde90d1f5eaf1a5a --binding-sha256 fd55262c37b6a50f71c58a677786a8af9aa7469defb3910853da64eadcbbf316
```

引数や固定の誤りは exit 2 で何も書きません。拒否は exit 1 で `refusal.json`、成功は exit 0 で `result.json` を、新しい `run-<ns>-<pid>/` に排他作成します。binding は、このフォルダの `binding-e*.json` のうち SHA-256 がコマンド行と同じもの 1 つです（binding-e01・e02 を渡すと schema の違いで拒否します）。

### 確かめること

- (0) **起点の記録と履歴**：起点の記録（checkpoint の検証 `435bc5e0-3818-4691-9d84-a9add39239d9` の写し、その出力 `../version-allowance/run-1792320136065939000-60394/result.json`、`ci-e3c29d1d.json`・`ci-jobs-e3c29d1d.json`・`ci-artifacts-e3c29d1d.json`、FR8.3 の原本と u11-node の ZIP）と、履歴（v1〜v4 の入口・binding-08〜11・回帰の 12 ファイル）の SHA-256。固定は入口に書き、binding は同じものを書かなければ拒否します。記録の中身も照合します（exit 0・verified・evidence_unchanged、command の SHA-256＝command_label の SHA-256、command_label が v4 の入口と binding-11 の SHA-256 を持つこと、stdout の SHA-256・bytes 数・最後の行の出力フォルダと PASS、result.json の PASS と固定）。生きている `unit.json` は、写しと同じ bytes、別の id に置き換わった（理由を書く）、無い、のどれかでなければ拒否します（id が欠けている・空なら拒否）。
- (1) **署名と系譜**：保存した記録で head と起点から head までの各 commit が Verified、親が並びのとおり、各 commit の tree が手元の git と同じ。手元の git（`rev-list --parents`・`rev-list base..head`）の並びも同じ。署名そのものは保存した記録の Verified を信じ、手元では確かめません。
- (2) **変わったファイル**：binding の一覧・手元の git（`diff-tree`）・保存した compare（head が起点と違うとき）がちょうど同じ。compare の各 blob も手元の git と同じ。
- (3) **今の作業コピー**：
  - head の tree の `aidlc/` の外の**全ファイル**（e3c29d1d では 675）を、head の blob と bytes で比べます。bytes の違いを許すのは `.aidlc-version` と `mise.toml` の 2 つだけです（無いのは拒否）。名前の除外（`target/`・`node_modules/`・`__pycache__/`・`.DS_Store`・`tools/aidlc-recovery/`・`.venv-u15/` など）に当たる場所の追跡ファイルも、除外せずに比べます（独立レビューの Major 3）。
  - head の tree に**無い** path は、名前の除外に当たるか、head の tree にある `.gitignore` の規則で git が無視するものでなければ拒否します。git の無視は、読み取りの `git -c core.excludesFile= check-ignore -z -v -n --no-index --stdin` を 1 回だけ、`GIT_*` の環境変数を外して実行し、規則の出どころが head の tree にある `.gitignore`（bytes を比べ済み）であるものだけを認めます。`.git/info/exclude`・`core.excludesFile`（既定の `~/.config/git/ignore` を含む）・未追跡の `.gitignore` の規則は認めず、`ignored_by_a_source_not_accepted` に書いて拒否します（独立レビューの Major 1）。`!` で始まる打ち消しの規則に当たったものは無視されないとして扱います。
  - 結果は `excluded_by_name`（名前で除外）と `excluded_by_git_ignore`（git の無視で除外。当たった `.gitignore` の場所・行・規則つき）に分けて列挙します。名前で除外したフォルダの行には「未追跡の中身だけ。中の追跡ファイルは比べる」と書きます。
- (4) **CI**：保存した head の CI の記録が binding の workflow の集合をちょうど含み、全部 completed・success、attempt 1。workflow の集合は、入口に固定した e3c29d1d の必須の 7 つ（CI・Release package checks・U1 U14 current-source evidence・U12/U13/U14 current full quality・U14 fresh thirteen target ASan and LSan）を含まなければ拒否します（binding は足せるが減らせない）。attempt 2 を認めるのは、binding で名前と id を挙げた job だけで、保存した attempt 1 の job の一覧（`ci-jobs-<head>.json` の `attempt_1`）でその 1 job だけが失敗し、ほかは全部成功、attempt 2 で再実行したのもその job だけ、を確かめます（e3c29d1d では U12 run 39114110570 の job 117638480843、attempt 1 のほかの 28 job は成功）。各 run の job の集合は `ci-jobs-e3c29d1d.json` の同じ workflow と同じ。新しい集合は binding の `job_sets` に人の承認の文とともに書いたときだけ認め、基準の集合を含み空でないこと（減らせない）を求めます。0 job の run は拒否します。
- (5) **速さ（FR8.3）**：性能の workflow は入口で `U14 current full quality` に固定。その各 run について、保存した API の artifact の一覧（`ci-artifacts-<head>.json`。e3c29d1d では 2026-10-18 に読み取りの `gh api` GET で保存し、同じ GET と 32 件すべて一致することを確かめた）の中で、u11-node がちょうど 1 つ、id が binding と同じ、`workflow_run` の id と head がその run と head、ZIP の SHA-256 と大きさがその一覧の digest と大きさと同じ、ZIP の中の `performance/observations.json` が原本と同じ bytes、head が同じ、`passed`・`complete`・`result.pass` が true（独立レビューの Major 2。digest は binding ではなく保存した API の記録から取ります）。
- (6) **upstream の head**：binding に `upstream` があるときだけ。upstream の head U が保存した記録で Verified、U の tree が head の tree と同じ（手元の git に U があればそれでも）、U の CI が (4) を満たすこと。binding-e03 では使いません。**注意**：比べるのは tree 全体（`aidlc/` を含む）です。upstream に取り込むときに `aidlc/` の記録などが違うと、製品のファイルが同じでも一致せず拒否されます（安全側）。使う前に、upstream の実際の tree で一致するかを確かめてください。
- 結果の先頭の `differences_from_base` に、基準（e3c29d1d）からの違い（足した workflow、job の集合の上書き、再実行、変わったファイル、性能の run、upstream）を書きます。

git は読み取りのコマンド（`rev-parse`・`rev-list`・`ls-tree`・`diff-tree`・`cat-file`・`check-ignore`）だけです。確認のときに GitHub への問い合わせ・ネットワーク・build・CI・測定・公開はしません。全体を 2 回確かめて結果が同じことも確かめます。

### 回帰（版 c、40 件）

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d -p 'test_*.py' -v
```

2026-10-18：`test_entry_c.py` 40 件すべて成功、skip 0、exit 0。`discover -p 'test_*.py'` では v1 の 30 件・b の 36 件と合わせて 106 件、すべて成功。製品のファイルは変えていません（入口の回帰専用の OVERLAY、`unittest.mock` による入口の定数・git の答えの差し替え、メモリの中の JSON・ZIP。一時フォルダはこのフォルダの中に作って消す）。

- **手元への依存**：正の対照（test_01）は、この Mac の本当の作業コピーを使います。head の tree に無い手元の path がどれも名前の除外か head の `.gitignore` の規則に当たる間だけ通ります。`.agents/`・`.venv-u15/` などの特定の path についての期待は、その path が手元にあるときだけ確かめます。件数（675・673）は head の tree から決まる数として確かめます。
- 版 c で足した回帰：head の `.gitignore` の規則で無視される未追跡のファイルが通る。`.git/info/exclude`・全体設定のファイル・未追跡の入れ子の `.gitignore` の規則は、出力の解析でも、git の答えを差し替えた全体の確認でも拒否される。`GIT_DIR`・`GIT_WORK_TREE`・`GIT_INDEX_FILE`・`GIT_CONFIG_*` を環境に置いても git がそれを使わず、`XDG_CONFIG_HOME` の `git/ignore` も読まれない（一時フォルダの fixture で）。追跡ファイルが `tools/aidlc-recovery/`・`target/`・`node_modules/`・`__pycache__/`・`.DS_Store`・`.venv-u15/` の下にある場合（head の tree に 1 つ足して見せる）に、違い・欠けが拒否され、同じなら比べた数に入る。bytes の違いを許すのは 2 つだけ。必須の workflow を減らすと拒否。job の集合の上書きが基準を減らす・空だと拒否、足すだけなら承認の文つきで通り違いに出る。0 job の run の拒否。性能の workflow の固定。digest・大きさ・artifact id・run と head への所属・u11-node の数・artifact の一覧の head と bytes が保存した記録と違うと拒否。binding に `digest` を書くと拒否。基準の記録の中身（exit 1・verified false・evidence_unchanged false・unit 違い・command の SHA-256・v4 以外の command・stdout・出力フォルダ・result.json の PASS と固定）を、入口の固定をテストの中だけ差し替えて確かめる。生きている `unit.json` の id の欠け・空・文字列でないものの拒否。系譜の各 commit の tree・手元の親。upstream が手元の git にある場合（tree 違いで拒否、同じなら通る）と repository の違い。v1・b のファイル・run・レビューが残っていて、binding-e01・e02 は拒否される。
- 各回帰がその検査を外すと落ちることを、`entry-c.py` のソースをメモリの中で 1 か所ずつ書き換えて 27 か所で確かめました（ファイルは変えない）。例：出どころの検査を外すと test_03・test_04、`GIT_*` の除去を外すと test_05、必須の workflow を外すと test_41、追跡ファイルの比較を外すと test_10・test_11・test_12・test_15 が落ちます。

### 本番の実行（版 c、2026-10-18）

上のコマンドを 1 回実行し、**exit 0**。出力は `run-1792327873535813000-33039/result.json`（`d70fbf464acb9a4097e80806aea0db7501fca17a2a2bb5158dc8a947ed1f7fc5`）です。head＝起点＝e3c29d1d、`changed_paths` は空、`differences_from_base` は再実行 1 つ（U12 run 39114110570）のほかは空、head の tree の `aidlc/` の外の 675 ファイルのうち 673 が head の blob と同じ bytes（残りの 2 つは bytes の違いを許した `.aidlc-version`・`mise.toml`）、認めない出どころの無視は 0。

- `excluded_by_git_ignore`（10）：`.agents/`・`.claude/`・`.codex/`・`aidlc.settings.local.json`・`*.profraw` の 4 つ・`packages/paludarium-wasm/paludarium.wasm`・`spikes/wasm-threads/pkg/`（どれもルートの `.gitignore` の規則）。
- `excluded_by_name`（27）：`.aidlc-version`・`mise.toml`（どちらも bytes が head と違う）、`.git/`・`.jj/`・`.venv-u15/`・`aidlc/`、`tools/aidlc-recovery/` の 2 ファイル、`target/` の 6 フォルダ、`node_modules/` の 1 フォルダ、`__pycache__/` の 12 フォルダ（2＋4＋2＋6＋1＋12＝27）。

### checkpoint の記録の写しについて（計画外の手順）

`base-checkpoint-435bc5e0.json` は、承認済みの計画（Step 19 (0)）に無い手順で置いた写しです。起点の記録 `.aidlc-construction-checkpoints/u15-release/unit.json` は次に checkpoint の検証をすると上書きされる（この入口を採用して検証すると、その時点で上書きされる）ため、同じ bytes の写しを v1 を作るときにこのフォルダに置き（`cmp` で同じことを確かめた）、入口はその写しの SHA-256 を固定して照合します。版 b・c の本番の実行では `live_checkpoint_record: equal to the pinned copy` で、写しが原本と同じ bytes であることを確かめています。code-summary への記録は coordinator が行います。

### 確かめていないこと（版 c）

- 変わったファイルの中身が正しいこと（この入口が証明するのは bytes と CI の結果だけ。中身は各 Unit のレビュー・試験と head の CI で確かめる）。
- head に無い除外したもの・`.aidlc-version` と `mise.toml` の手元の差の中身、`aidlc/` の中のファイル、ファイルの mode（実行ビット）。`.gitignore` の規則が適切であること。
- 起点より前の各 Unit の細かい照合（U1 の module receipt、U14 の compiled source の closure、旧 chain の validator）をもう一度実行したこと。e3c29d1d で通った記録をハッシュで引き継いだだけです。
- 保存した記録が GitHub の今の状態と同じであること。署名は保存した記録の Verified を信じています。
- 再実行・job の集合の上書きの承認の文が本当に人のものであること（文の有無だけを確かめる。binding の SHA-256 の採用が人の承認になる）。
- 実公開、FR10.1 と U15 の受け入れ（GAP のまま）、unit の完了、正式な確認コマンドとしての採用。
- 新しい測定・CI・build・publish。

## 履歴：版 b（entry-b.py、binding-e02）

| ファイル | SHA-256 |
|---|---|
| `entry-b.py` | `95dcedc719224b5a1355266304dab1368a1b03c0f1f0016f95c64095792c1ff6` |
| `binding-e02.json` | `66c54627be2abf6fb76588a47416bbfeb4f0acaa7ced191bdff3902b6ee27e02` |
| `test_entry_b.py` | `67f55f175a7b5fda936a4fcd4de1d7aad7b46690e42c84c328c15c0f86ab97e8` |

人の判断 1 のとおり、v1 に名前の除外 `.venv-u15/`・`.aidlc-version`（bytes の違いを許す）と、head の tree に無い path への git の無視（`git check-ignore -z -v -n --no-index --stdin`）を足した版です。回帰 36 件はすべて成功、本番の実行は exit 0（`run-1792326450015585000-34598/result.json`。`excluded_by_git_ignore` 10、`excluded_by_name` 27：2＋4＋2＋6＋1＋`__pycache__/` 12）。この節は、作った時点で 13 と書いた `__pycache__/` の数を 12 に直しています。

独立レビュー 01（NOT-READY）の指摘：git の無視の規則の出どころを確かめない（`.git/info/exclude`・全体設定・未追跡の `.gitignore`・`GIT_*` の環境変数が効きうる）、binding が必須の workflow・job の集合・性能の workflow と digest の出どころを緩められる、名前の除外が追跡ファイルの bytes の比較まで免除するのに主張がそれを言っていない、の Major 3 件と Minor。版 c で直しました。

## 履歴：版 v1（entry.py、binding-e01）

| ファイル | SHA-256 |
|---|---|
| `entry.py` | `10472d80f4cc5e4422469cb9d0e10f19ddebe64562ad0a0c33d9d50a98dfc961` |
| `binding-e01.json` | `670294220a09c34f23e3c4472db4b61876159573e41abbf0b48afe2f38a6b74b` |
| `test_entry.py` | `422e9e5f022acf4320fb143d89dd5f676a92fbe84a9c0d3a16c4cf3d0a316b17` |

計画 Step 19 の除外の一覧（`aidlc/`・`.git/`・`.jj/`、途中の `target/`・`node_modules/`・`__pycache__/`、`.DS_Store`、`mise.toml`（bytes の違いを許す）、`tools/aidlc-recovery/`）だけを使う最初の版です。回帰 30 件はすべて成功（正の対照は、下の 11 の path を「無い」とし `.aidlc-version` を head の blob として見せたもの）。

本番の実行（2026-10-18）は **exit 1**（拒否）で、原本は `run-1792325657506892000-42086/refusal.json` に残しています。止まった段は `(3) working copy`。head の tree と違う、または除外の一覧に当たらない手元の path は次のとおりでした。

- bytes の違い：`.aidlc-version`（head は `2.11.1-preview.20261016.1`、手元は `2.11.1-preview.20261017.1`）
- head に無いもの：`.agents/`・`.claude/`・`.codex/`・`.venv-u15/`・`aidlc.settings.local.json`・`default_14032388851307854129_0_{15492,17992,18002,18017}.profraw`・`packages/paludarium-wasm/paludarium.wasm`・`spikes/wasm-threads/pkg/`

除外の一覧は広げず、人に伝えました。そのあと人が判断し（判断 1）、版 b を作りました。
