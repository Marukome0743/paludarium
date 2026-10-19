## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-19
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-summary.md > 現在の検証済み結果 / 正式検査・最終確認の境界 | 「現在の検証済み結果」は署名head 692264fa時点のCI・全体coverage 93.06%（11427行）・Clippy/deny 3OSの結果なのに、現行ソースの見出しのまま残っている。その後のU14（1ceae86c）で paludarium-jit と paludarium-wasm/src/abi.rs が変わったため、ワークスペース全体の分母・lint・coverageの結果は今のソースの結果ではない。また末尾は、未実行の旧「新最終確認候補」`verify-current-u1-u7-u9-u3-u5-u6-u8.py` を最終確認として示しており、Step16が指す今の正式確認コマンド（U2の `u2_candidate.py`）と食い違う。計画のStep16は「Steps13〜15は履歴」と書くが、summary側にはそれが書かれていない。 | code-summary.md の先頭に、この結果は692264fa時点の履歴であり1ceae86c以降のワークスペース全体の結果ではないと明記する。旧候補コマンドが今の正式確認コマンドに置き換わったことを書く。ただし内容は新しい実行と数えない。 | Resolved (reviewer) |
| R-02 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-generation-plan.md > Step 16 | Step16は「今の正式確認コマンド（U2の u2_candidate.py）」と書くだけで、コマンドの全文・ハッシュ・実行した結果が書かれていない。checkpointの合否がどの実行に基づくか、この計画だけでは追えない。他Unitの内容なので本レビューでは中身を確認していない。 | 実行後にコマンド全文と実exit・保存先を計画かsummaryに1行で記録する。 | Resolved (reviewer) |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-summary.md > 実コマンド・入力と責務 / ASanの限定再利用と未検証 / 失敗と歴史的証拠 | 「692264faの時点の結果」という注記は「履歴」節の中にだけあり、その後に続く別の節にはかかっていない。それらの節には「検証済み：…現行と一致する」「現行322の旧commit投影」「今回の正式sensor原本」のように、現行・今回を指す言い回しが残っている。読む人は、U14の変更後のsourceに対する確認結果と読み違えるおそれがある。 | 注記を最初の節だけでなく、692264fa時点の内容を含む節の冒頭にも一行ずつ付けるか、「以下この文書の末尾までは692264fa時点の履歴」と一度明示する。「現行」「今回」は、692264fa時点なのかStep16〜17なのかが分かる語に直す。 | Resolved (reviewer) |
| R-04 | Critical | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/traceability.json > coverage NFR8 (line 416-419), reverse rows (lines 440-449 and 736-748) | NFR8 の `target` が、U15 の Steps 22-28 で削除された `.github/workflows/u8-native-diagnostic.yml` のままである。reverse の行にも、削除済みの `u8-native-diagnostic.yml` と `u8-current-verification.yml` が `status: OK` で残っている。traceability sensor は存在しない target を拒否するので、このままでは gate を通らない。NFR8 の notes は、すでに存在しない workflow の run を根拠にしている。 | NFR8 の target を `.github/workflows/ci.yml` に置き換える（理由は「差分テスト」job が diff_u8 を実行している、ci.yml:125-150 の 143 行目）。または `crates/paludarium-harness/tests/diff_u8.rs` でもよい。削除した 2 つの workflow の reverse 行を消す。notes は「削除済み。現行は ci.yml の differential job」と書き直す。 | Resolved (reviewer) |
| R-05 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/source-manifest.json > writes (lines 9-11, 84-86) | manifest が、削除済みの `.github/workflows/u8-native-diagnostic.yml` と `.github/workflows/u8-current-verification.yml` を担当 path として今も挙げている。さらに `.github/workflows/ci.yml` は 27d05de1 で変更されており（push は main のみ。差分テストは diff_u1/u2/parallel_u2/u4/u9/u3/u8 をまとめて実行）、manifest の hash は変更前の ci.yml のものである。 | 削除した 2 path を writes から外す。ci.yml は現行 bytes で再記録する。 | Resolved (reviewer) |
| R-06 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-summary.md > 「現行Step16〜18」節（lines 5-9） | 見出しが「現行」で、「今の正式確認コマンド」を `u2_candidate.py` と書いているが、今の正式確認コマンドは entry-f.py（binding-e06f、2026-10-19 採用、command SHA-256 00f5c883…）である。この節は U8 が現行のコマンドを一度も示していない。また「検証はexit 0」「source-manifestの27 paths」は 2026-10-17 の状態であり、27d05de1 の CI 8 run（success）には触れていない。 | 節を日付付きの履歴（2026-10-17 時点）に改め、現行の確認コマンド（entry-f / binding-e06f）と、27d05de1 での U15 の変更による影響（workflow 削除、ci.yml 変更）を明記した新しい節を、先頭に追加する。 | Resolved (reviewer) |
| R-07 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/traceability.json > coverage NFR9 notes (line 425), NFR3 notes (line 389); code-summary.md lines 29, 37 | NFR9 の notes が、公式 2026-10-10 配布の nightly（実体 32dba69d…/LLVM 23.1.3）を現行のように「全4job同pin」と書いているが、`rust-toolchain.toml` の現行は `nightly-2026-10-11` である。NFR3 の notes は run 38089705214 の「全4jobs」「workspace 93.06%」を根拠にしているが、これは head 692264fa の値で、現行 ci.yml の job 名（unit tests / differential / coverage ほか）とは別物である。 | NFR9 と NFR3 の notes に「692264fa 時点の旧 pin・旧 run」と明記し、現行の pin（nightly-2026-10-11）と 27d05de1 の CI run（ci-27d05de1.json）への参照を追加する。旧い値を現行の合格として残さない。 | Resolved (reviewer) |
| R-08 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/unit-test-instructions.md > 「承認された現行ソース追加検証（Steps13〜15）」節 (lines 5-11), 「上記の U8 ファイル…計画時点では未実行」 (line 33), 「今は計画のため全 U8 テストは未検証」 (line 67) | 見出し「承認された現行ソース」と、line 11 の「現在の承認済みコマンドは verify-current-u1-u7-u9-u3-u5-u6.py」は古い。現行は entry-f.py である。line 33 と line 67 の「未実行」「未検証」は、U8 完了済みの今は事実と矛盾する。line 7 の 3OS 入口 `--lib u8_`（56件の個別記録）は、現行 ci.yml では U1_PACKAGES 全体の `cargo test` に置き換わっている。 | 見出しを履歴（Steps13〜15 時点）に改め、現行のコマンド、および 3OS の入口（ci.yml の `unit tests` job の全体実行）を書く。「未実行」「未検証」の文を、実施済みの記録に直す。 | Resolved (reviewer) |
| R-09 | Minor | .github/scripts/u8-current-diagnostic.py:14 | このスクリプトはどの workflow からも呼ばれなくなった（呼んでいたのは削除済みの `u8-current-verification.yml`）。さらに 14 行目の snapshot() が、削除済みの `.github/workflows/u8-current-verification.yml` を `read_bytes()` するので、実行すると FileNotFoundError で失敗する。traceability（lines 723-734）と manifest にはまだ載っている。 | スクリプトを削除するか、「履歴・実行不可」と明記する。traceability と manifest からも整理する。 | Unresolved |
| R-10 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-summary.md > 「実コマンド・入力と責務」「ASanの限定再利用と未検証」「失敗と歴史的証拠」「正式検査・最終確認の境界」 | 各節の先頭に「履歴」の注記はあるが、注記は「先頭の『現行Step16〜18』節を参照」と案内し、その節自体が古い（上記 Major）。そのため、案内の先が現行ではない。また line 55 の候補コマンド `verify-current-u1-u7-u9-u3-u5-u6-u8.py` は「未実行」のままだが、その後は entry-c → entry-f に置き換わっている。 | 上記の新しい先頭節ができたら、各節の参照先をそこへ変える。line 55 は「不採用・履歴」と明記する。 | Resolved (reviewer) |
| R-11 | Minor | .github/workflows/ci.yml:125-150, 152-268; .github/workflows/u11-fuzz.yml:14; .github/workflows/u14-fuzz.yml:14 | U8 が測っていたもののうち、現行で測られなくなったものを記録する。測られている: 差分 diff_u8（ci.yml:143）、3OS の単体テスト（U1_PACKAGES 全体、`u8_` を含む）、workspace 80% coverage、fmt/clippy/deny、ASan（kernel_threads_u5/kernel_futex_u5 を含む 13 対象、u14-fuzz と u11-fuzz）。測られなくなった: (a) U8 専用の native 診断 run（fresh Linux 29+runner1 の個別ログと、56件を実test名で個別記録する検査）。(b) 324 入力の before/after hash 照合と実 compiler/設定の記録。(c) U8 の browser（Node/Safari）での fork/exec/wait は、もともと未検証のまま。 | (a)(b) が U8 の合格に不要なら、U8 の記録にその旨を明記する。必要なら、他の Unit の gate（u14-quality、entry-f）に含まれているかを確認して記載する。再実行は求めない。 | Unresolved |
| R-12 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/traceability.json > coverage NFR8 notes (line 419); code-summary.md:8-9 | NFR8 は要件書で「供給網」（crates.io のみ、Apache-2.0 と両立するライセンス、Action の SHA 固定）と定義されている（requirements.md:153）。ci.yml は `dependencies` job の `cargo deny`（:111-123）と SHA 固定（:4-5）でこれを実際に満たすので、target は妥当。しかし、記録された理由は「差分テストのjobが diff_u8 を動かす」で、NFR8 の内容と合わない。notes の本文（3OS・差分の結果）も供給網の根拠ではない。これは review-06 の提案文を引き継いだ書き方である。 | NFR8 の理由を「ci.yml の dependencies job（cargo deny）と SHA 固定」に書き直す。次に traceability を更新するとき、または NFR8 の notes を整理するときでよい。 | New |
| R-13 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u8-process-spawn/code-generation/code-summary.md:5 | 「R-04〜R-11を直した」と書くが、R-09（スクリプトの削除）と R-11（測定の復帰）は直しておらず、記録と保留だけである。:10-11 を読めば分かるが、冒頭の一文は直したと読める。 | 冒頭の一文を「R-04〜R-08・R-10を直し、R-09・R-11は記録して人の判断に残した」と正確に書く。 | New |

> R-04 Reviewer note: traceability.json:416-419 の NFR8 target は `.github/workflows/ci.yml`（存在する）に替わり、notes に日付付きの理由がある。reverse（lines 428-725）から消えた `u8-native-diagnostic.yml` と `u8-current-verification.yml` の行は無くなり、25 行（manifest と同じ 25 path）。NFR3/NFR8/NFR9 の status と id は変わっていない。ただし NFR8 の target を選んだ理由の書き方は新規 R-12 を参照。

> R-05 Reviewer note: source-manifest.json の writes は 25 件で、削除済み 2 workflow は無い。manifest は path のみで hash を持たないため、ci.yml の hash 再記録は不要（summary の説明どおり）。

> R-06 Reviewer note: code-summary.md:3-14 の新しい先頭節に、今の正式確認コマンド（entry-f / binding-e06f）、toolchain（rust-toolchain.toml:3 の nightly-2026-10-11）、U8 に関わる変更（ci.yml の push は main のみ、2 workflow 削除）、27d05de1 の CI 8 run 成功（ci-27d05de1.json の runs_listed_for_head.total_count 8、全て success、U12 は attempt 2）が書かれている。旧節は line 16 で「履歴」に改名され、本文は同じ意味のまま。

> R-07 Reviewer note: traceability.json:389 の NFR3 notes と :425 の NFR9 notes の先頭に、692264fa 時点の履歴である旨と、今の pin・CI 記録の場所が 1 回ずつ付いた。

> R-08 Reviewer note: unit-test-instructions.md:3-14 の新しい先頭節が、今の確認コマンド・今の 3OS の入口（ci.yml:70-91 の `test` job が U1_PACKAGES 全体を実行、kernel/mmu/runtime を含む）を書き、:14 で「未実行」「未検証」「現在の承認済みコマンド」が当時の記述だと明記している。:16 の見出しは履歴に改名済み。古い本文（:24, :46, :80）が残るのは、注記で補う方針と整合する。

> R-09 Reviewer note: `.github/scripts/u8-current-diagnostic.py:14` は削除済みの `u8-current-verification.yml` を読むため、実行すると失敗する。summary:11 に「履歴・実行不可、削除は次の製品 push で決める」と記録された。依頼どおり「記録済み・判断は人に委ねる」として扱い、READY を妨げない。

> R-10 Reviewer note: summary:7 が、旧節の「先頭の『現行Step16〜18』節を参照」の案内は新しい先頭節を指すこと、候補 `verify-current-u1-u7-u9-u3-u5-u6-u8.py` は不採用・履歴であることを書いた。

> R-11 Reviewer note: summary:10 が、今の受け入れの場所（ci.yml:143 の diff_u8、`test` job、80% coverage、u11-fuzz.yml:14 と u14-fuzz.yml:14 の kernel_threads_u5/kernel_futex_u5）と、今は測られていないもの（U8 専用 native 診断、56 件の個別記録、324 入力の hash 照合）を、もともと未検証の browser 実行と分けて記録した。実在を確認した。CI に戻すかは人の判断として保留中。READY を妨げない。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| traceability sensor | 未実行（Read のみ）。依頼文では 0 findings で pass と報告 | 全 target の実在までは確かめていない。NFR8 の `ci.yml` と reverse の path は確認した。 |
| 手作業の突き合わせ | manifest writes 25 件と reverse 25 行の path が一致し、削除済み 2 workflow だけが無い。ci.yml、u11/u14-fuzz.yml、rust-toolchain.toml、ci-27d05de1.json の記述は一致 | 記録は実際の状態と整合 |

### Summary

review-06 の Critical と Major は、記録の修正で閉じている。manifest と reverse の整理、日付付きの履歴化、今の確認コマンドと toolchain の追記は正確で、過大な主張はない。残るのは NFR8 の理由の書き方と冒頭の表現の Minor 2 件、および人の判断待ちの R-09・R-11（Minor）だけなので READY。
