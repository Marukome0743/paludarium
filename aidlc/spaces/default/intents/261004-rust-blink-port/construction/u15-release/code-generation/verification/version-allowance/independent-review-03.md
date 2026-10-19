# 独立レビュー 03：`u15_candidate_v3.py`（binding-10、15 ファイル、未採用）

2026-10-18 JST。反証を目的とした独立レビューです。対象は `u15_candidate_v3.py`・`binding-10.json`・`test_u15_candidate_v3.py`・`ci-a54315f9.json`・`ci-jobs-a54315f9.json` と README の v3 の節です。採用済みの v2（`b78f867e…`、binding-09 `687fee0c…`）を、v3 が変えずに包んでいることも確かめました。照らした承認は、新しい署名済み head a54315f9 とその CI 8 run、許可をちょうど 15 ファイルにすること、人の追加の承認（「この 7 ファイルも a54315f9 のバイト列の固定で許可に足し、もう一度実行してください。中身は U15 のレビューと試験で確かめる、と明記してください。」）です。

**Verdict:** READY

## 確かめたこと

| 項目 | 結果 |
|---|---|
| 固定の値（SHA-256） | 入口 `ebb67894…`、binding-10 `44f7c2a9…`（入口の定数と一致）、回帰 `148960fa…`、`ci-a54315f9.json` `ab5ea24c…`、`ci-jobs-a54315f9.json` `11e2d9b9…`、性能の原本 `6d3d389e…`。どれも実ファイルと一致しました。v2 の入口・binding-09・v2 の回帰（`57c0727f…`）と、v1・binding-08 も変わっていません。 |
| 署名済み head | a54315f9 の親は bb197e04 で、git の差は 12 ファイル（Step 14b）でした。作業ツリーの HEAD は a54315f9 です。製品のファイルで head と違うのは、`mise.toml` と `tools/aidlc-recovery/` だけでした。保存した commits の 2 件は verified true で、親の並びも合っています。 |
| CI の 8 run | 8 run とも head a54315f9・completed・success・attempt 1 で、id は承認どおりです（U14 39096893624、U12 39096895814、U13 39096898087、fuzz 39096899756、source-bound 39096901200、release-check 39107620902（workflow_dispatch）・39108225338（pull_request）、CI 39108225399）。job はすべて success で、件数は total_count と一致します。 |
| CI の照合のしかた | 入口は U1 の `verify_ci`／`verify_ci_jobs` を変えずに使います。job の期待値は binding-08 にある bb197e04 の同じ workflow の job の集合で、新しい記録の写しではありません。run の名前の集合（8 件、Release package checks は 2 件）は完全一致が必要です。compare の 12 ファイルすべてについて、blob が local git と同じことを要求しています（v1 では版の 3 ファイルだけでした）。 |
| 15 ファイルの bytes | 1ceae86c・57a8c96f・bb197e04・a54315f9・作業ツリーの bytes を、ファイルごとに比べました。STAY の 6 つは、a54315f9・bb197e04・作業ツリーで同じで、`stay_files` と一致します。MOVED の 2 つ（docs/release.md・test_policy.py）は、bb197e04 の blob が binding-09 の固定と同じで、今の bytes は a54315f9 の blob と `moved_files.new_sha256` に一致します。EXTRA の 7 つは、古い bytes が 1ceae86c・57a8c96f・bb197e04 の blob（どれも同じ）で、binding-v4 の固定と一致します（入口は be45 との一致も要求しています）。今の bytes は a54315f9 の blob と binding-10 に一致します。 |
| 許可の範囲 | `MOVED`・`STAY`・`EXTRA_FILES` は入口の定数です。binding の各集合は、定数と完全一致が必要です（16 個目の追加・欠け・集合の入れ替えは拒否されます）。`ALLOWED_PATHS_15` は 15 件、`OTHER_STEP14B==OUTSIDE_PINS`（3 件）を要求しています。v2 の `ALLOWED_PATHS` は 8 件のままであることを、v2 の読み込みのときに確かめています。v2 に見せる view は MOVED の 2 つだけです。旧 chain の親には 15 ファイルだけを見せ、view が 15 パスをちょうど覆うことを確かめています。7 つを v2 と中の chain に見せないことも確かめています（view が重ならないこと）。 |
| 中の検査 | v2 の `verify` を、固定した bytes から変えずに呼んでいます。その中で binding-08、U14（binding-07）、U11、U2、U1 が動き、bb197e04 の記録の上で検査されます。v3 側では次を要求しています：v2 が MOVED を view で読んだこと、旧 chain の `source_compatibility==PASS`、validator の子 4 件の exit 0、binding-v4 が固定する許可の 13 ファイルを親が view で読んだこと、再検査で結果が同じこと。v2・v1 の検査で、v3 で抜けたものは見つかりませんでした。 |
| 出力の文 | 承認どおりの文があります。exact-bytes の 11 ファイルについて、このコマンドが証明するのは a54315f9 の署名済み bytes であることだけで、中身は U15 のレビュー・試験と a54315f9 の CI で確かめる、という文が、`allowance.exact_bytes_scope`／`_en`・`not_claimed[1]`・行ごとの `scope` にあります。採用済みの chain の固定の外にあるのは u15-acceptance.yml・acceptance.py・test_acceptance.py の 3 つだけ、という文が `not_claimed[2]` にあります。`FR10_1: GAP`・`U15_acceptance: GAP`・`unit_completed: false`・`formal_command_adopted: false` も入っています。result.json の文字列をすべて調べ、15 ファイルの許可と食い違う文（8 ファイルだけ・3 ファイルだけ・それらを許さない、など）が無いことを確かめました。 |

## 回帰の設計（v2 の suite を overlay の中で動かすこと）

`main()` は、Step 14b の 12 ファイルを bb197e04 の blob で見せる `Overlay` の中で、v2 の suite（132 件）を実行します。この overlay が本物の入口の実行に漏れることは無いと判断しました。理由は次のとおりです。

- `Overlay`（`u1-skeleton/.../loopback1-next/test_new_candidate.py`）は、テストのプロセスの中で `builtins.open` と `io.open` を差し替えるだけです。書き込みの mode で開くと拒否します（読み取り専用）。`__exit__` で元に戻すので、`with` から例外で抜けても戻ります。
- ディスクには何も書きません。git の blob（`git_blobs`）は git の object から読むので、overlay の影響を受けません。子のプロセスも overlay を引き継ぎません。suite の中の子のプロセスは、hash の不一致で exit 2 になる、何も書かない起動だけです。
- 本物の入口の実行は、別のプロセスです（今回は私が直接起動しました）。v3 の 15 件は overlay を抜けた後に `setUpClass` で `u3c.verify` を実際の作業ツリーで実行します。v2 の suite の中の v2 のモジュールと、`u3c.v2()` が読むモジュールは別のインスタンスなので、キャッシュも共有しません。
- 入口そのものは overlay を使いません。v2 に見せるのは MOVED の 2 つだけです（`verify` の `bb_map`）。test_501 で、overlay なしの v2 だけでは docs/release.md で止まることを確かめています。

## 実行した結果

- 回帰 `test_u15_candidate_v3.py`：**exit 0**。147／147 件が成功、skip 0、FAIL・ERROR は 0 件（v2 の suite 132 件 = binding-08 の suite 116 件 + binding-09 の 16 件、それと binding-10 の 15 件）。
- 候補のコマンド行（1 回）：**exit 0**。出力は `version-allowance/run-1792311246399316000-29857/`（`u15_candidate_v3: PASS`）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792311248137069000-29857/`（`source_compatibility: PASS`、`U15_acceptance: GAP`、`unit_completed: false`）。validator の子 4 件（old_predicates ×2・current_semantics・package_semantics）はすべて exit 0 でした。旧 chain の親が view で読んだのは 13 ファイルです。この実行で、この 2 つのフォルダが新しくできました。

## 指摘

| Severity | Location | Finding | Required action |
|---|---|---|---|
| Minor | result.json の `claim_scope.u15_version.performance`（v1 の `u15_scope` の欄がそのまま残る） | 「inner FR8.3 binding unchanged (1ceae86c); bb197e04 original checked and recorded only」のままです。同じ欄の `head` は a54315f9 に書き換わっています。v3 は a54315f9 の性能の原本（run 39096893624）も確かめて記録していますが（`u15_a54315f9.head.performance_a54315f9`、`claimed[8]`）、この欄はそれを書いていません。誤りではありませんが、head と性能の欄で指す時点がずれて見えます。 | 次に入口を直すときに、この欄を「bb197e04 と a54315f9 の原本は確かめて記録するだけ」に合わせます。 |
| Minor | result.json の `v2_layer.u15.old_chain_files`（MOVED の 2 行） | 行の `new_sha256` は v2 の値（bb197e04 の blob）のままです。一方で `scope` は「今のbytesが…a54315f9のbytesであることだけ」に書き換えられています。`v2_layer` に注記はありますが、1 行の中で値と文の時点が違います。 | 値を変えずに、`scope` を v2 の層の文として区別するか、a54315f9 の値は `u15_a54315f9.files` を見るように注記します。 |
| Minor | README の 77 行目の見出し「v2（現行、未採用）」 | v3 の入口と coordinator は v2 を「採用済み」としていますが、README の見出しは古いままです。 | README の見出しを今の状態に合わせます（入口と binding の bytes には関係しません）。 |
| Minor | 最初の v3（入口 `ae9a0b7b…`、binding-10 `c262b40e…`）の扱い | 未採用だったため、その場で書き換えられています。拒否された run `run-1792310402280740000-18124/` が指す入口の bytes は、もうありません。README には hash と経緯が書いてあるので、追跡の手がかりは残っています。 | 必要と判断するなら、今後は、拒否された run を出した入口を別の名前で残します。今回は README の記録で足りるとします。 |

Critical と Major の指摘はありません。

## 主張しないこと

- exact-bytes の 11 ファイルと、固定の外の 3 ファイルの中身や bytes が正しいこと。
- FR10.1・U15 の受け入れ・unit の完了・v3 の正式な採用（人の承認が必要）。
- 保存した CI の JSON が GitHub の今の状態と一致すること（このレビューでは GitHub に問い合わせていません）。

## 片付け

このレビューでは `review-scratch/` を作っていません。書いたのはこのファイルだけです。
