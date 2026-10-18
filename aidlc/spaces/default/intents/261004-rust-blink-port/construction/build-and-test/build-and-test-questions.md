# Build and Test の質問

15 の Unit はすべて承認済みですが、各 Unit の合格の証拠は、それぞれ別の時点の版（コミット）で取ったものです。製品のコード（`crates/` など）は、CI の全項目が通った最後の版 `be45b36c` から変わっていません。一方で、今の作業コピーはまだどこにもコミット・push されていません。Build and Test では「今のソース全体で、決めた品質目標をすべて満たしているか」を確かめる必要があるため、次の点を決めてください。

## Q1. [品質エンジニア] 今のソースでの測り方

Linux の差分テスト・行カバレッジ 80%・Windows・本物の Safari・600 秒のファジングは、この Mac では正式に測れません（Docker は QEMU なので native Linux の証拠になりません）。どう測りますか。

A. 今の作業コピーをコミットしてフォーク（`Marukome0743/paludarium`、origin）の新しいブランチに push し、CI 一式を新しく実行して、その結果を証拠にする。この Mac でも単体テスト・lint・依存の検査を実行する（推奨）
B. この Mac でできる範囲だけ新しく実行し、Linux・Windows・Safari・ファジングは保存済みの CI の結果（`be45b36c` などの版）を、製品コードが同じであることを確かめたうえで再利用する
C. この Mac でできる範囲だけ実行し、ほかは「未確認」として記録する
X. Other (please specify)

[Answer]: A

## Q2. [開発者] 道具の版

いつもの方針では、作業の始めに道具を最新に上げます。いまの固定は Rust nightly-2026-10-11（最新は nightly-2026-10-17）、CI の Node 26.11.1（手元の最新は 26.12.0）、Playwright 1.64.0（最新は 1.64.1）です。ただし、上げると全 Unit の承認の後でソースが変わり、正式な確認コマンドの照合にも影響します。どうしますか。

A. 最新に上げてから測る。上げて壊れた場合は、そこで止めて相談する
B. 今の固定の版のまま測り、版を上げるのは次の CI Pipeline の段階で行う
C. 今の固定の版のまま測り、版を上げるのは別の作業にする
X. Other (please specify)

[Answer]: A

## Q3. [品質エンジニア] 時間のかかる確認

ファジング（13 対象を各 600 秒、ASan/LSan）と、JIT の速さの判定（FR8.3：Node の Worker で JIT あり・なし各 10 回、有意水準 5%）は時間がかかります。最後の `be45b36c` のファジングの実行は途中で取り消されています。速さは `208fd965` で測った結果を、コードの一致で結びつけています。今回どうしますか。

A. ファジングも速さも、今のソースで新しく 1 回ずつ実行する（推奨）
B. ファジングだけ新しく実行し、速さは前の測定の結びつけを使う
C. どちらも前の結果を、コードの一致を確かめたうえで使う
X. Other (please specify)

[Answer]: A

## Q4. [リリースエンジニア] 公開（FR10.1）の扱い

FR10.1（成功条件を満たしたら、タグを打って CI から crates.io と npm に公開し、公開の前に人が承認する）は、まだ公開していないので未達です。この計画には公開を受け持つ後の段階がありません（Operation フェーズはスキップ）。Build and Test では、満たしていない目標が残るとその時点で失敗として扱い、直し方をご相談することになります。どうしますか。

A. この段階では公開しない。FR10.1 は「未確認」として記録し、失敗として扱って直し方の相談に進む
B. この段階の中で公開まで行う（版の決定、Trusted Publisher などの設定はご自身で行っていただき、タグと公開の承認もいただく）
C. 公開は別の作業にする。FR10.1 は「未確認」として記録し、今回の合否の判断ではその点を受け入れたうえで進める
X. Other (please specify)

[Answer]: B

## Q5. [開発者] 道具の版の見直し

Q2（最新に上げてから測る）の範囲を調べると、Rust nightly・CI の Node・Playwright の固定は 38 ファイルにあり、U7 以外の 14 Unit の担当ソースにまたがる。そのうち U14 の workflow（`u14-native-first.yml`・`u14-cost-diagnostic.yml`・`u14-fuzz.yml` など）は正式な確認コマンド（`final_candidate.py`）がバイト単位で固定しており、変えるとすべての checkpoint でそのコマンドが失敗する。どう進めますか。

A. 今の固定の版のまま今回の Build and Test を測り、版を記録する。版を上げる作業は、新しい正式な確認コマンドとあわせて、後で別の作業にする
B. 今すぐ 38 ファイルを上げ、新しい正式な確認コマンドを作って承認を受け、14 Unit を再レビューしてから測る
C. Rust だけ（`rust-toolchain.toml` と封印されていない workflow）を今上げ、U14 の封印された workflow と Node・Playwright は後にする
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- 測り方（Q1：A）：今の作業コピーをコミットして、フォーク（origin）の新しいブランチに push し、CI 一式を新しく実行して、その結果を証拠にする。この Mac でも単体テスト・lint・依存の検査を実行する。push と CI の起動は、その前にもう一度承認をいただく。
- 道具の版（Q2：A を Q5：A で見直し）：今回の Build and Test は今の固定の版（Rust nightly-2026-10-11 など）のまま測り、使った版を記録する。最新への更新（Rust nightly-2026-10-17、CI の Node 26.12.0、Playwright 1.64.1）は、新しい正式な確認コマンドとあわせて、後で別の作業にする。
- 時間のかかる確認（Q3：A）：ファジング（13 対象×600 秒、ASan/LSan）と、JIT の速さの判定（FR8.3）を、今のソースで新しく 1 回ずつ実行する。
- 公開（Q4：B）：この段階の中で公開（FR10.1）まで行う。版の決定と Trusted Publisher・release environment などの設定はご自身で行い、タグと公開の承認もいただく。
- 準備として済んだこと：U9・U12 で workflow を直し（ゲストビルドの advisory policy、`PALUDARIUM_TEST_NODE`、setup-python）、U1・U9〜U12 の再レビューと承認を終えた。CI ではまだ動かしていない。

（Loop-back 1 の後、2026-10-18 に見直した要約）

- 進め方：Loop-back 1 の後の Build and Test は Modify で行う。既存の手順書と記録を残し、結果だけをまとめ直す。Q1〜Q5 の回答はそのまま使う。
- FR8.3（JIT の速さ）：U14 の全品質 run 39030957672（head 1ceae86c、attempt 2、34 job すべて成功）の速さの判定で、JIT ありの平均 3.635 秒、JIT なしの平均 4.528 秒、p = 1/1024 ≈ 0.00098（< 0.05）、20 回すべて終了コード 0。Met にする。今の head 57a8c96f との差は Safari の道具の 2 ファイル（`u11-browser-driver.mjs` とその試験）だけで、JIT の製品コードは同じ。
- NFR7（揺れる試験）：Safari の session 作成だけを 60 秒待つ修正（2b8723ab・57a8c96f、試験つき）の後、4 つの run（CI 39044785452・39073492190、U12 39044793102・39073501121）で Safari の job が 1 回目で成功した。Met にする。U12 の run の 1 回目の失敗は Safari ではなく、既に分かっている外の要因（U3 の未確認の Intel の CPU signature 000606a6、apt.llvm.org への接続失敗）で、その記録も残す。
- ほかの目標の証拠も、Loop-back 前の版（bd247f1e・e4f84768）の run から、今の版の run に結び直す（57a8c96f：CI 39073492190・U12 39073501121・release 39073492188、1ceae86c：U13 39028305765・ファジング 39028307842・ソースの照合 39028309948・U14 39030957672）。行カバレッジは workspace 93.87%、U1 93.86%、U9 86.56%、U11 86.65%、U3 の 9 ファイル 82.71%。
- FR10.1（公開）：FR8.3 が合格したので公開の前提はそろうが、まだ公開していないので Unverified のまま。そのため今回の判定は、FR10.1 が残るあいだは「失敗」のまま。Q4 の B のとおり、まとめ直しの後に、公開に必要な設定（版の決定、名前の所有、Trusted Publisher、release environment、同じ head の受け入れの証拠）と、それが要る時期をお知らせする。


（Loop-back 2 の後、2026-10-18 に見直した要約）

- 進め方：Loop-back 2（U15 で版を 0.1.0 にし、公開の準備と R-16〜R-18 を直した）の後の head e3c29d1d で、Modify で結果をまとめ直す。手順書と前回の結果は残し、結果を今の版に結び直す。Q1〜Q9 の回答はそのまま使う。
- 証拠：e3c29d1d の CI 7 run（PR ゲート 39114018191 の 23 job、全品質 39114108809 の 34 job、macOS の品質 39114110570 の 29 job、Windows の品質 39114112207 の 29 job、ファジング 39114114216 の 13 対象×600 秒、ソースの照合 39114116352 の 7 job、公開物の確認 39114018143）が、すべて最終的に成功した。U12 の Safari の 1 job だけが 1 回目に落ち、人の判断で再実行して 2 回目で成功した。手元（この Mac）では、ビルド・fmt・clippy が終了コード 0、単体テストは 809 成功・1 失敗（`diff_u8`：x86-64 Linux でしか合格にしない試験）・4 無視だった。
- カバレッジ（PR ゲート run 39114018191）：workspace 93.85%、U1 93.85%、U9 86.82%、U11 86.88%、U3 の 9 ファイル 82.71%。
- FR8.3：e3c29d1d で 1 回だけ測り、JIT あり 4.5834 秒・JIT なし 5.2649 秒（約 12.9% 速い）、p = 1/1024 で合格した（run 39114108809）。Met にする。
- NFR7：Q9 の A のとおり Not Met にする。safaridriver 側の時間切れという新しい揺れで、直しは公開の前に製品をもう一度変えるときにまとめて行う。
- FR10.1：版は 0.1.0 に決まり、公開の部品はそろったが、upstream への取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、tag が人の手順（`docs/release.md` の Owner hand-off）でまだ終わっていないので Unverified のまま。
- 判定：失敗（FR10.1 が Unverified、NFR7 が Not Met）。Loop-back 2 の結果を Loop-Back Log に記録する。


（U15 の確認コマンドの入口の作り直しの後、2026-10-18 に見直した要約）

- 進め方：U15 の Code Generation で e3c29d1d を起点にした新しい確認コマンドの入口（`entry-e3c29d1d/entry-c.py`）を作り、人が採用した。製品は変わっていない（head は e3c29d1d のまま）ので、試験・CI・測定はやり直さず、記録に確認コマンドが変わったことだけを書き足す。
- 書き足すこと：今の正式な確認コマンドが `entry-c.py`（`binding-e03.json`）であること、U15 の checkpoint がこのコマンドで exit 0（約 0.6 秒）になったこと、入口 v1〜v4 は履歴になったこと。
- 結果と判定は前回のまま：FR8.3 は Met、NFR7 は Not Met（Q9 の A）、FR10.1 は Unverified。判定は失敗。人が前回 Accept failure を選んだ扱いも変えない。

- Looks correct
- Request changes

[Answer]: Looks correct

## Requested Changes Feedback

What should change?

[Answer]: ごめんなさい、Approve に変更します。（変更なし。Request changes は選び間違いで、要約は Looks correct とする）

## Q6. [リリースエンジニア] 公開（FR10.1）の進め方

結果をまとめ直した結果、FR8.3（JIT の速さ）と NFR7（Safari の揺れ）は Met になり、公開の成功条件（FR6.3・FR7.2・FR7.3・FR8.2・FR8.3）はそろった。残る目標は FR10.1（公開）だけで、公開していないあいだは Build and Test は失敗のまま。Q4 の B（この段階で公開まで行う）で進めるには、`docs/release.md` の Owner prerequisites のうち、次をご自身で行っていただく必要がある：(1) 版の決定（11 crate と npm を同じ版にする。決まったら私が版を書き換え、その head で CI と `u15-acceptance` の受け入れの証拠を作り直す）、(2) 11 crate と `@paludarium/wasm` の名前の所有と、初回の公開（crates.io の Trusted Publishing は公開済みの crate にしか登録できないため、初回は owner の API トークンが要る）、(3) upstream の `release.yml` と `release` environment を Trusted Publisher として各 crate と npm に登録、(4) upstream の管理者による `release` environment の作成と保護（必須レビュアー、自分のレビューの禁止、管理者の迂回の禁止）。どう進めますか。

A. 公開まで進める。まず版を決めていただき、私が版の変更と同じ head の証拠を作る。(2)〜(4) は、必要な時点でお知らせしてからご自身で行っていただく
B. 公開は後の別作業にする。FR10.1 は Unverified のまま記録し、Build and Test の失敗をどう扱うかを決める
X. Other (please specify)

[Answer]: A

## Q7. [リリースエンジニア] 公開する版

今は 11 crate（workspace の `version`）と `@paludarium/wasm` がどちらも `0.0.0` で、`docs/release.md` は `0.0.0` のまま公開しないとしている。team.md の Deployment では、段階ごとに 0.x 版を出してよいとしている。決まった版に、私が workspace・crate 間の依存・npm をそろえて書き換え、その head で CI と受け入れの証拠を作り直す。どの版にしますか。

A. 0.1.0（最初の公開）
B. 0.5.0（段階 5 の JIT まで済んだことを版で表す）
X. Other (please specify)

[Answer]: A

## Q8. [リリースエンジニア] 版の書き換えの進め方

0.1.0 への書き換えは `Cargo.toml`（workspace の `version` と crate 間の依存 11 件）・`Cargo.lock`・`fuzz/Cargo.toml`・`fuzz/Cargo.lock`・`packages/paludarium-wasm/package.json`・`README.md`・`docs/release.md` に及ぶ。これらは承認済みの 12 Unit（U1・U2・U4・U5・U6・U7・U8・U10・U11・U12・U14・U15）の担当ソースで、Build and Test の中で書き換えると各 Unit の正式な確認コマンドがソースの変化で失敗する。どう進めますか。

A. U15（公開）の Code Generation に戻り、版の書き換えを U15 の計画として Plan Approval を受けて行う。ファイルを持つほかの Unit は確かめ直しだけ行う。そのあと CI 一式と受け入れの証拠を作り直して Build and Test に戻る（推奨）
B. 公開は後の別作業にする（Q6 を B に変える）。FR10.1 は Unverified のまま記録し、Build and Test の失敗をどう扱うかを決める
X. Other (please specify)

[Answer]: A

## Q9. [品質エンジニア] Safari の新しい揺れ（NFR7）の扱い

U15 の後の head e3c29d1d で CI 一式を実行し、7 run すべて最終的に成功した。ただし U12 の品質 run 39114110570 の 1 回目で、Safari の job（`u11-programs / differential (macos-latest, safari)`）だけが落ちた。safaridriver 自身が「Safari の起動を待つ間に時間切れ」と答え、こちらの 60 秒の待ちより前の 31 秒で止まっている。前回直した「こちらの待ち時間が短い」揺れとは別の種類で、今の直し（session 作成だけ 60 秒待つ）では防げない。人の判断で失敗した job だけを再実行し、2 回目で成功した（1 回目の原本は保存済み）。team.md は「揺れたテストは記録して直す」としている。NFR7 をどう判定しますか。

A. Not Met として記録し、直し（session 作成が safaridriver 側の時間切れで失敗したときに 1 回だけやり直すなど）は、公開の前に製品をもう一度変えるときにまとめて行う。Build and Test は FR10.1 でもともと失敗のまま（推奨）
B. Met のままにする。1 回だけの外の揺れとして記録し、直さない
C. 今すぐ直す。U11 の Code Generation に戻り（Loop-back 3）、直してから CI 一式と確認コマンドの入口を作り直す
X. Other (please specify)

[Answer]: A
