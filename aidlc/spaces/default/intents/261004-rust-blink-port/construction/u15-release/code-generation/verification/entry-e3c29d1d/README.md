# e3c29d1d を起点にした新しい確認コマンドの入口（Step 19〜20）

承認済みの計画 Step 19〜20 と、承認済みの案 `../entry-e3c29d1d-proposal.md` のとおりに作りました。v1〜v4 の層は重ねていません。入口は v1〜v4・旧 chain を import も実行もせず、それらの bytes が変わっていないことだけを確かめます。

**現行は版 c（`entry-c.py`＋`binding-e03.json`）です。** 版 v1（`entry.py`）と版 b（`entry-b.py`）は、上書きせず履歴として残しています（下の「履歴」）。どの版もまだ**正式な確認コマンドではありません**。採用（Step 21：独立レビューと人の承認）までは、今の入口 v4（`../version-allowance/u15_candidate_v4.py`、binding-11）が正式な確認コマンドのままです。入口と binding は採用の前でも上書きせず、直すときは新しい版を作ります。

## 版の経緯

| 版 | 入口・binding・回帰 | 本番の実行 | 次の版にした理由 |
|---|---|---|---|
| v1 | `entry.py`・`binding-e01.json`・`test_entry.py`（30 件） | exit 1：`run-1792325657506892000-42086/refusal.json` | 手元の `.aidlc-version` の bytes の違いと、head に無い 11 の path が除外の一覧に当たらなかった。人が判断した（下の判断 1） |
| b | `entry-b.py`・`binding-e02.json`・`test_entry_b.py`（36 件） | exit 0：`run-1792326450015585000-34598/result.json` | 独立レビュー `independent-review-01.md` が NOT-READY（Major 3、Minor 6） |
| **c（現行）** | `entry-c.py`・`binding-e03.json`・`test_entry_c.py`（40 件） | exit 0：`run-1792327873535813000-33039/result.json` | — |

人の判断と指示：

1. 2026-10-18、選んだ選択肢「git の無視＋2 つ」：「git が無視するファイル（.gitignore、git check-ignore で読み取りだけ）を除外にし、.aidlc-version（bytes の違いを許す）と .venv-u15/ を除外の一覧に足す。入口と binding は新しい版（entry-b.py・binding-e02.json）で作り直す」
2. 独立レビュー 01（NOT-READY）の Major 3 件と Minor を、coordinator 経由の指示で版 c として直す（git の無視は head の tree にある `.gitignore` の規則だけ、bytes の違いを許す追跡ファイルは 2 つだけ、binding で検査を緩められないこと）。

## 版 c（現行）

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
