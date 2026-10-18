## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-18 (the brief carried no `Date for this review:` line, so the date is from the session)
**Iteration:** 2
**Verdict Dictated:** no

対象：版 c（`entry-c.py`、`binding-e03.json`、`test_entry_c.py`、`ci-artifacts-e3c29d1d.json`、`README.md`、`run-1792327873535813000-33039/result.json`）。比較先は `independent-review-01.md` の Major 3 件・Minor と、新しく入った穴の有無。指示どおりシェルは使わず、読み取りだけで確かめた。回帰 106 件は再実行していない（報告どおりとして扱う）。

### 前回の指摘の確認

| 前回 | 結果 | 根拠 |
|---|---|---|
| Major 1（git の無視の出どころ） | 直った | `entry-c.py:266` で受け入れる出どころを「head の tree にある `.gitignore`」に限る。`:191-204` で他の出どころ（`.git/info/exclude`、全体設定、未追跡の `.gitignore`）は無視と認めず `foreign` に回し、`:269` で `unexpected` になって拒否。`:105` の `-c core.excludesFile=` と `:138-142` の `GIT_*` 除去も入った。`test_entry_c.py:128-152` が解析・差し替えた git の答えでの全体の拒否・環境変数と XDG の fixture まで確かめる（test_05 は実 git を使う）。 |
| Major 2（binding が緩められる） | 直った | 必須 7 workflow を入口に固定（`:86-87`）し、binding の `workflows` が含まなければ拒否（`:386`）。`base_job_sets` も 7 と一致を要求（`:359`）。上書きは空・基準を減らす場合を拒否（`:399-401`）、0 job の run も拒否（`:408`）。性能の workflow は固定（`:88`、`:421`）。ZIP の digest・大きさ・artifact id・run と head への所属は、保存した API の artifact 一覧から取る（`:422-435`、binding から `digest` 欄を撤去）。`test_entry_c.py:250-257, 277-293, 319-340` が対応。 |
| Major 3（追跡ファイルの免除） | 直った | `:252-259` が head の tree の全ファイルを回して bytes を比べ、免除は `paths_bytes_may_differ` の 2 つだけ。名前の除外は head に無いパスだけ（`:262`）。`test_entry_c.py:167-190` が `tools/aidlc-recovery/`・`target/`・`.venv-u15/` などの下の追跡ファイルの違い・欠けを拒否することを確かめる。symlink にすり替えた祖先フォルダは、`files` に入って `unexpected` になり拒否される（`:223, :233, :269`）。 |
| Minor（回帰の常に真の行・環境依存） | 直った | 常に真の行は無く、特定の path の期待は `exists()` の時だけ（`test_entry_c.py:113-116`）。基準の記録の中身の検査は、入口の固定をテストの中だけ差し替えて確かめる（`:348-369`）。 |
| Minor（`tree_equal` の範囲・局所 git の回帰） | 直った | 範囲は結果と README に明記（`entry-c.py:458`、README 行 47）、回帰は `test_81`。 |
| Minor（head 以外の commit の tree） | 直った | `entry-c.py:333` が chain の全 commit で照合、`test_entry_c.py:230-233`。 |
| Minor（README の 13/12、v1 と b の混在） | 直った | README 行 69・93 が 12、版ごとの節に整理。 |
| Minor（checkpoint の写し） | 一部 | `entry-c.py:317` で id の欠け・空を拒否、`test_62`。計画外の手順であることは README 行 71-73 に書いたが、code-summary への記録は未了（README は coordinator が行うと書く）。 |

### Findings

**Prior findings**

| ID | Now | Severity | Note |
|---|---|---|---|

**New findings**

| Severity | Location | Finding | Required action |
|---|---|---|---|
| Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py > walk_working_copy 行 226、run-1792327873535813000-33039/result.json 行 36-52 | 名前で除外した全フォルダの行に「中の追跡ファイルは比べる」という注記が付くが、`aidlc/` には当てはまらない（`head_tree` が `aidlc/` の追跡ファイルを最初から外している、`:162`）。`.git/`・`.jj/` は追跡ファイルを持たないので無害だが、`aidlc/` の行は注記が事実と違う。主張（`CLAIMED_*` の 4 番目）は「`aidlc/` の外」と限定しているので、注記だけの問題。 | `aidlc/` の行だけ注記を「`aidlc/` の中は比べない」に変えるか、注記を `top_level` のうち `aidlc` 以外に限る。 |
| Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py > verify_ci 行 388-410、verify_rerun 行 362-375 | binding が緩められる点はほぼ塞がったが、残りは 2 つ。(1) 再実行の許可は run ごとの 1 job に限られるが、run の数は上限が無く、必須 workflow（ASan や Safari など）にも付けられる。承認の文は有無しか確かめない（not_claimed に明記済み）。(2) `REQUIRED_WORKFLOWS` を入口に固定したので、正当な workflow の削除や改名も新しい入口の版が要る。どちらも「binding の SHA-256＝人の承認」の前提の範囲。 | 再実行を許す run の数を `differences_from_base.reruns` に出している（出力済み）ので、採用の承認のときに人がそこを読む運用でよい。必要なら、必須 workflow への再実行の許可を 1 回に制限する。 |
| Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py > verify_performance 行 431-435、ci-artifacts-e3c29d1d.json | 保存した artifact の一覧は binding が指す、`gh api` の写しと自称するファイルで、入口はハッシュの一致しか確かめない（CI の記録と同じ信頼の水準）。一覧にある `workflow_run.repository_id` と `expired` は検査しない。ZIP は同じ digest でも別の repository の run に属しうる（run id と head は見る）が、`arts['repository']`（`:424`）で repository は binding に結びつく。 | 次の head の記録を作るときに、`repository_id` が fork のものと同じことと `expired: false` を検査に足す（任意）。 |
| Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-c.py > git() 行 105・138-147 | `GIT_*` と `core.excludesFile` は塞いだが、利用者・システムの git 設定（`~/.gitconfig`、`/etc/gitconfig`）は引き続き読まれる。`check-ignore --no-index`・`ls-tree`・`cat-file` が設定で動く外部コマンド（例：`core.fsmonitor`）を起動する経路は通常ないので実害は小さい。出どころが head の `.gitignore` に限られたため、無視の判定を設定でゆがめる経路は残っていない。 | 任意：`-c core.fsmonitor=false -c core.hooksPath=/dev/null` などを足すか、README に「利用者の git 設定は読む」と書く。 |
| Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/entry-e3c29d1d/README.md 行 71-73 | 写しの checkpoint の記録は計画外の手順のまま。README に理由と同じ bytes であることの確認（版 b・c の本番の実行の `equal to the pinned copy`）は書いてあるが、計画・code-summary への記録は未了。 | 計画 Step 19 の注か code-summary に、写しを置いたことと理由を書く（coordinator の作業）。 |

### 新しい穴の確認

- **binding で緩められる点**：変更ファイルの一覧は局所 git と一致を要求、起点の記録・履歴・除外の一覧は入口と完全一致、必須 workflow・job の集合・性能の workflow・digest の出どころは入口か保存した記録に固定。残るのは再実行の許可と承認の文だけ（上の Minor）。上書きや追加の workflow は足すだけで減らせない。
- **git の呼び出し**：許可リストの読み取りコマンドだけ（`:104, :146`、`test_90`）。環境の `GIT_*` を外し、`core.excludesFile` を空にする。`git_has_commit`（`:152-154`）は許可リストを通らないが、`cat-file -e` で読み取りのみ。
- **追跡ファイルの比較**：head の tree のループに変わったので、名前の除外・symlink・祖先のすり替え・欠け・種類の違いを取りこぼす経路は見つからなかった。
- **主張の過大さ**：result.json と CLAIMED は、中身の正しさ・実公開・FR10.1 の GAP・採用していないこと・署名を局所で確かめていないこと・承認の文の真偽を、いずれも未主張として明記している。過大な主張は `aidlc/` 行の注記だけ（上の Minor）。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 版 c の本番の実行（`run-1792327873535813000-33039/result.json`） | PASS、exit 0。head＝起点、変更 0、675 件中 673 件の bytes 一致、`accepted_gitignore_sources` は head の 4 つの `.gitignore`、7 run・再実行 1 件、FR8.3 p=1/1024 | 読んで整合を確かめた。認めない出どころの無視は 0。 |
| 回帰（`test_entry_c.py` 40 件、全体 106 件） | 数は 40 件で README と一致。各拒否は 1 つの入力だけを変えて、その検査の文言を確かめる形 | 再実行はしていない。常に真の行は見つからなかった。 |
| 指示によるシェル・検証ツールの実行 | 実行していない | 読み取りのみ。 |

### Summary

前回の Major 3 件（git の無視の出どころ、binding による検査の緩和、追跡ファイルの bytes 免除）はいずれも入口のコードと回帰で直っており、直しによる新しい穴は見つからなかった。残るのは `aidlc/` 行の注記の誤り、再実行の許可の運用、記録の写しの計画への記録といった Minor だけで、判定は READY。採用の伺いでは、`differences_from_base`（再実行 1 件のみ）を人が読むことを前提にしてよい。
