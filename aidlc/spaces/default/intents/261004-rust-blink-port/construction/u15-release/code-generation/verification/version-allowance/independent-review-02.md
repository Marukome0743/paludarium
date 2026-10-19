# 独立レビュー 02：`u15_candidate_v2.py`（review-01 の修正後、未採用）

2026-10-18 JST。`independent-review-01.md` の 3 件の指摘に対する修正を、もう一度レビューしました。前回と同じ方法で、反証を目的にしています。

**Verdict:** READY

## 確かめたこと

| 項目 | 結果 |
|---|---|
| 固定の値（SHA-256） | 入口 `b78f867e…`、binding-09 `687fee0c…`（前回から変わらず、入口の定数とも一致）、回帰 `57c0727f…`。v1 の入口 `6a5077ae…`・binding-08 `f20954e1…`・v1 の回帰 `6573bc6c…` も変わっていません。README の表とコマンド行も新しい値と一致しています。 |
| 検査を変えていないか | 新しい入口の 1〜267 行目（docstring・定数・`check_pins`・`v1`・`allowed_paths`・`load_binding`・`verify_base`・`verify_history_v1`・`old_chain_pins`・`cargo_toml_diff`・`verify_old_chain_files`・`verify`・`logical_child`・`guarded_run`・`run_old_chain`）を、前回レビューした版と 1 行ずつ比べました。違いはありませんでした。`main` で変わったのは、result.json の `claimed`／`not_claimed` を `statements()` から取ることと、`allowance_statement` を足したことだけです。検査の順番・内容・拒否の条件は同じです。変わったのは 268 行目より後ろの、主張の文の定数（`CLAIMED_V2`・`ALLOWANCE_V2`・`UNPINNED_ADDED`・`NOT_CLAIMED_V2`）、`statements()`、`u15_scope_v2` です。 |
| 回帰の変更 | test_400〜414 は変わっていません（docstring が 1 行増えて行番号がずれただけです）。`V2_TEST_COUNT` は 15 から 16 になり、test_415 が足されました。test_415 には、v1 自身の 3 ファイルの文を検出できることを確かめる陽性の対照があり、意味のない常時合格の試験ではありません。v1 の suite の固定（`6573bc6c…`）と件数 116 は変わっていません。 |

## 実行した結果

- 回帰 `test_u15_candidate_v2.py`：**exit 0**。132／132 件が成功、skip 0（binding-08 の suite 116 件 = U14 93 件 + U15 23 件、binding-09 の 16 件）。
- 候補のコマンド行（1 回）：**exit 0**。出力は `version-allowance/run-1792295210879479000-59675/`（`u15_candidate_v2: PASS`）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792295212292971000-59675/`（`source_compatibility: PASS`、`U15_acceptance: GAP`、`unit_completed: false`）。この実行で、この 2 つのフォルダが新しくできました。
- 新しい result.json の文字列をすべて調べました。「3ファイル以外の差」「それらを許さない」「3ファイルで許す」は、どこにも残っていません。残っている「3ファイル」は v1 の `claimed[0]`・`claimed[1]` だけで、どちらも Cargo.lock・fuzz/Cargo.lock・package.json の 3 つについて正しい主張です。`FR10_1: GAP`・`U15_acceptance: GAP`・`unit_completed: false`・`formal_command_adopted: false` も保たれています。

## 前回の指摘

| ID | Now | Severity | Note |
|---|---|---|---|
| M1（v1 の 3 ファイルの文が v2 の出力に残る） | Fixed | Major | 文は 3 か所で置き換えられています。result.json の `not_claimed[0]` は「8ファイル以外の差を許すこと…版の行だけの証明4つ…bb197e04のbytesへの固定4つ…だけである」になりました。`claim_scope.u15_version.scope` は `ALLOWANCE_V2`（8 ファイル）、`u15_version.claimed`／`not_claimed` は v2 の `statements()` になっています。`statements()` は、v1 の `NOT_CLAIMED[0]` が「3ファイル以外の差」で始まることを確かめてから外すので、v1 の文が変わればここで止まります。v1 の bytes は変えていません。回帰 test_415 で守られています。 |
| m2（bb197e04 で足された固定のない 3 ファイル） | Fixed | Minor | `not_claimed[2]` で、`scripts/release/acceptance.py`・`tests/release/test_acceptance.py`・`.github/workflows/u15-acceptance.yml` の作業ツリーの bytes をこのコマンドは固定していないこと（確かめるのは commit と compare のファイル一覧に入っていることだけ）を明記しています。この文はコードの動きと合っています（compare の blob を照合するのは `VERSION_FILES` だけです）。検査そのものは足していません。検査は前回どおり、採用済みの chain の範囲から来る性質のままです。 |
| m3（`CLAIMED_V2[1]` の書き方） | Fixed | Minor | 「旧chainのbinding-v4の固定・57a8c96f・1ceae86c・be45のblob」と、コードが確かめる 4 つにそろいました（test_415 で確かめています）。 |

## 新しい指摘

| Severity | Location | Finding | Required action |
|---|---|---|---|
| — | — | Critical・Major・Minor のどれにあたる新しい欠陥も見つかりませんでした。補足：修正前の run（`run-1792294223452925000-96601/`、`run-1792294558646092000-3308/`）の result.json には、M1 の誤った文が残っています。README はこの 2 つを修正前の履歴だと明記しています。履歴の bytes を変えないという方針どおりで、欠陥とは扱いません。 | なし |

## 主張しないこと

- exact-bytes の 4 ファイルの内容が正しいこと。
- 固定のない 3 ファイルの作業ツリーの bytes。
- FR10.1・U15 の受け入れ・unit の完了・正式な確認コマンドとしての採用（人の承認が必要）。
- 保存した CI の JSON が GitHub の今の状態と一致すること（このレビューでは GitHub に問い合わせていません）。

## 片付け

このレビューでは scratch のファイルを作っていません。書いたのはこのファイルだけです。
