# 独立レビュー 01：`u15_candidate_v2.py`（binding-09、未採用）

2026-10-18 JST。反証を目的とした独立レビューです。対象は `u15_candidate_v2.py`・`binding-09.json`・`test_u15_candidate_v2.py`、それが包む v1 `u15_candidate.py`（binding-08）と、採用済みの U14 `u14_candidate_v2.py`（binding-07）です。照らした承認は `../version-allowance-proposal.md` と、人の後の決定（Cargo.toml は版の行だけの証明、README.md・docs/release.md・tests/release の 2 つは bb197e04 のバイト列の固定、package.json の receipt の扱いはそのまま）です。

**Verdict:** NOT-READY

## 確かめたこと

| 項目 | 結果 |
|---|---|
| 固定の値（SHA-256） | 入口 `8ceb46bd…`、binding-09 `687fee0c…`（入口の定数と一致）、回帰 `30a106d1…`、v1 入口 `6a5077ae…`、binding-08 `f20954e1…`、v1 回帰 `6573bc6c…`、v1 の拒否 run の refusal.json `8e1a6543…`・children.json `4f53cda1…`、U14 入口 `934f21bc…`、binding-07 `425ae3e7…`、案 `df38caab…`、`ci-bb197e04.json` `cf63cbe3…`、`ci-jobs-bb197e04.json` `88b8aa40…`。すべて実ファイルと一致しました。 |
| 8 ファイルの bytes | 古い bytes は 57a8c96f と 1ceae86c で同じ blob、新しい bytes は bb197e04 の blob と作業ツリーで同じ。binding-09 の `old_sha256`／`new_sha256` 5 件とも一致しました（Cargo.toml `82e45acf…`→`5a8c319b…` など）。`git diff 57a8c96f bb197e04 -- Cargo.toml` は版の行 12 行だけでした。 |
| 署名済み head と CI | bb197e04 の親は 57a8c96f。変更は 11 ファイル。保存した CI の 7 run はどれも head bb197e04・completed・success・attempt 1。job 一覧の件数は total_count と一致。commits の 2 件は verified true。binding-08 の `attempt_1_failures`・`allowed_skipped` は空でした。いずれも binding-08 の固定のもとで、U1 の `verify_ci`／`verify_ci_jobs` が変えずに使われています。 |
| 許可の範囲 | `ALLOWED_PATHS` は入口の定数で 8 ファイルに固定。binding の `old_chain_files` は 5 キーとの完全一致を要求（9 つ目のキーと欠けは拒否）。view の対応は `verify` で 8 パスとの完全一致を確かめ、`main` でもその 8 パスだけに絞って旧 chain の親に渡しています。exact-bytes の 4 ファイルは、今の bytes が binding の固定値・bb197e04 の blob と同じことを要求。Cargo.toml は、新しい bytes の固定に加えて、構文（`expected==n`）と行（変わった行の数・内容・属する表）の両方で版の行だけの差であることを証明しています。古い bytes は binding-v4 の固定・57a8c96f・1ceae86c・be45 の 4 つの一致を要求しています。 |
| 中の検査を弱めていないか | v1 の `verify_history`・`verify_head`・`verify_versions` と U14 の `verify` を、固定した bytes から変えずに呼んでいます。旧 chain（`final_candidate.main`、validator の子 4 件）も変えずに実行し、`source_compatibility=='PASS'`・子 4 件の exit 0・親が固定のある 6 ファイルを view で読んだこと・再検査で結果が同じことを要求しています。v1 にあった検査で、v2 で抜けたものは見つかりませんでした。 |
| result.json の主張 | `FR10_1: GAP`・`U15_acceptance: GAP`・`unit_completed: false`・`formal_command_adopted: false`。exact-bytes の範囲（内容はこのコマンドで確かめていない）は、`allowance.exact_bytes_scope` と `not_claimed` に書かれています。ただし下の M1 のとおり、矛盾する文が残っています。 |

## 実行した結果

- 回帰 `test_u15_candidate_v2.py`：**exit 0**。131／131 件が成功、skip 0（binding-08 の suite 116 件 = U14 93 件 + U15 23 件、binding-09 の 15 件）。
- 候補のコマンド行（依頼のとおり 1 回）：**exit 0**。出力は `version-allowance/run-1792294558646092000-3308/`（`u15_candidate_v2: PASS`）。旧 chain の出力は `u1-skeleton/.../r05-r11-repair-01/formal-candidate-1792294560513867000-3308/`（`source_compatibility: PASS`、`U15_acceptance: GAP`、`unit_completed: false`）。この実行で、この 2 つのフォルダが新しくできました。
- 変異の実験（`review-scratch/probe_unpinned.py`。実ファイルは変えず、回帰の読み取り専用の Overlay を使用）：bb197e04 で変わった 11 ファイルのうち 8 ファイルの外にある 3 ファイル（`scripts/release/acceptance.py`・`tests/release/test_acceptance.py`・`.github/workflows/u15-acceptance.yml`）の作業ツリーの bytes を変えても、`verify` と旧 chain の `source_pins` はどちらも PASS でした。この 3 ファイルは binding-v4 も中の chain も固定していません（m2）。実験の後、3 ファイルが bb197e04 と同じままであることを `git diff` で確かめました。

## 指摘

| Severity | Location | Finding | Required action |
|---|---|---|---|
| Major | `u15_candidate_v2.py` の `main`（`not_claimed=[*V.NOT_CLAIMED,...]`）と `u15_scope_v2`（v1 の `u15_scope` の `u15_version` をそのまま残す）。実際の run `run-1792294558646092000-3308/result.json`・`run-1792294223452925000-96601/result.json` | v2 の result.json の `not_claimed[0]` に、v1 の文「3ファイル以外の差（Cargo.toml・README.md・docs/release.md・scripts/release・tests/release・CIの定義など）を許すこと。**この入口はそれらを許さない**」がそのまま入っています。`claim_scope.u15_version.scope` にも「版の行（0.0.0 → 0.1.0）だけを**3ファイルで**許す」とあり、`u15_version.not_claimed` にも同じ文があります。どれも v2 の入口では事実と違います。v2 は Cargo.toml・README.md・docs/release.md・tests/release の 2 ファイルを許しています。正しい記述（`allowance`・`u15_old_chain`・`CLAIMED_V2`）と同じ記録の中で食い違っており、読む人は「この 5 ファイルは古い bytes のまま封じられている」と誤って受け取れます。採用の判断に使う正式な記録としては、保証を実際より大きく見せる誤りです。回帰 test_414 はこの矛盾を検出しません。 | v2 の result.json と claim_scope で、v1 の `NOT_CLAIMED[0]` と `u15_version.scope`／`not_claimed[0]` を v2 の事実に合う文に置き換えます（または「binding-08 の時点の記述」とはっきり区別できるキーに移します）。たとえば「8ファイル以外の差を許すこと。Cargo.toml は版の行だけ、4ファイルは bb197e04 の bytes だけを許す」とします。v1 の入口の bytes は変えません。「8ファイルを許す」と矛盾する文が result.json に残っていないことを確かめる回帰を足し、入口・binding・README の固定の値を更新したうえで、もう一度レビューします。 |
| Minor | `verify_head`（v1）と中の chain の固定の範囲 | bb197e04 で足された `scripts/release/acceptance.py`・`tests/release/test_acceptance.py`・`.github/workflows/u15-acceptance.yml` は、git の commit の一覧と compare では確かめています。一方、作業ツリーの bytes はどの検査も固定していません。変えても PASS になることを上の実験で確かめました。採用済みの chain の範囲から来ている性質で、今回の許可で弱くなったわけではありません。ただ、`claimed` の「変更は既知の11ファイルだけ」は git の上の話であり、作業ツリーの bytes の話ではありません。 | 作業ツリーのこの 3 ファイルの bytes をこのコマンドでは確かめていないことを、`not_claimed` に一文足して明記します。必要と判断するなら、bb197e04 の blob との一致の確認を足す案を人に示します（許可を広げる変更ではありません）。 |
| Minor | `CLAIMED_V2[1]` | 古い bytes を「binding-v4 の固定・57a8c96f の blob」とだけ書いています。コードは 1ceae86c と be45 の blob との一致も要求していて、README と Cargo.toml の文（`CLAIMED_V2[0]`）とも書き方がそろっていません。過大な主張ではなく、表現の不足です。 | M1 を直すときに、「57a8c96f・1ceae86c・be45 の blob」とそろえます。 |

## 主張しないこと

- exact-bytes の 4 ファイルの内容が正しいこと（このレビューでも確かめていません）。
- FR10.1・U15 の受け入れ・unit の完了・正式な確認コマンドとしての採用。
- 保存した CI の JSON が GitHub の今の状態と一致すること。このレビューでは GitHub に問い合わせていません。確かめたのは、binding-08 の固定と、記録の中身の整合だけです。

## 片付け

`review-scratch/probe_unpinned.py` はこのレビューで作ったもので、レビューの後に `review-scratch/` ごと削除しました。
