# CI Pipeline の質問

今の CI（2026-10-18、fork `codex/build-and-test` の head e3c29d1d で読んだもの）：

- 道具は GitHub Actions で、`.github/workflows/` に 41 の workflow がある。外部の action は 409 件すべて commit の SHA で固定している。
- PR のたび：`ci.yml`（23 job。3OS の単体テスト、lint、依存の検査、x86-64 Linux の差分テスト、wasm 4 環境、カバレッジ 80%）と `release-check.yml`（公開物の確認）。`ci.yml` は `main` と古い作業ブランチ 5 つへの push でも動く。
- 正式な証拠に使った品質の workflow（`u12-quality.yml`・`u13-quality.yml`・`u14-quality.yml`・`u14-fuzz.yml`・`u1-u14-source-bound.yml`）は、手動の起動と、古い作業ブランチへの push でだけ動く。
- 夜間：`nightly.yml`（毎日、ファジングと wasm のスレッドの確認。失敗すると Issue を作る）。ただしファジングは musl の target のため全対象が失敗している（run 38967100569）。
- 公開：`release.yml`（版の tag で起動、保護された `release` environment の承認の後に公開）と `u15-acceptance.yml`（手動）。
- そのほかの 30 ほどは、各 Unit の作業中に使った診断・確かめの workflow で、古い作業ブランチへの push か手動でだけ動く。
- 注意：`.github/workflows/` の一部のファイルは、各 Unit の正式な確認コマンドが bytes を固定している。workflow を変えると、次の確認で入口の作り直し（v5）と CI 一式の再実行が要る。

## Q1. [リリースエンジニア] workflow を変える時期

この段階では CI の設計（どの変更でどの確認が動き、何がマージを止めるか）を書く。実際の workflow の変更をいつ行いますか。

A. 設計だけを書き、workflow の変更は、公開の前に製品をもう一度変えるとき（NFR7 の Safari の直しと、残している Minor）にまとめて行う。入口の作り直しと CI 一式は 1 回で済む（推奨）
B. この段階で workflow を変え、push・CI 一式・確認コマンドの入口 v5 まで行う
X. Other (please specify)

[Answer]: A

## Q2. [リリースエンジニア] 夜間の確認

team.md は、夜間にブラウザのテスト・速さの測定・ファジングを行い、失敗したら Issue にするとしている。今の `nightly.yml` はファジングが全対象失敗し、速さの測定とブラウザの差分テストは入っていない。どうしますか。

A. `nightly.yml` を、正式な証拠に使った workflow（`u14-fuzz.yml` の 13 対象×600 秒、`u14-quality.yml` の wasm 4 環境と速さの判定）を呼ぶ形に作り直す。失敗したら今と同じく Issue を作る（推奨）
B. `nightly.yml` のファジングの target だけを直し、ほかは今のまま
C. 今のまま（失敗の記録だけ）
X. Other (please specify)

[Answer]: A

## Q3. [リリースエンジニア] Unit の作業中に使った workflow

診断・確かめの workflow（30 ほど）は、古い作業ブランチへの push か手動でだけ動き、upstream の `main` に入っても普段は動かない。どうしますか。

A. 正式な証拠に使ったもの（PR のゲート、各品質、ファジング、ソースの照合、公開の 3 つと、それらが呼ぶもの）だけを残し、ほかは削除する。古い作業ブランチへの push の条件も外す。正式な確認コマンドが固定するファイルは、その固定を外す入口の更新とあわせて行う（推奨）
B. すべて残す（記録として）
X. Other (please specify)

[Answer]: A

## Q4. [リリースエンジニア] upstream の main の必須チェック

マージを止める必須チェックは、upstream の管理者（人）がブランチの保護で設定する。どれを必須にしますか。

A. `ci.yml` の全 23 job と `release-check.yml`（公開物の確認）。各品質・ファジング・速さは夜間と公開の前の確認にする（推奨）
B. `ci.yml` の 23 job だけ
C. A に加えて、各品質の workflow（3OS の全品質）も PR のたびに動かして必須にする（1 回あたり 30 分以上かかる）
X. Other (please specify)

[Answer]: A


## Q5. [リリースエンジニア] 設計どおりに入れた後に見つかった食い違い

CI の設計（Q1〜Q4 の A）は、U15 の Step22〜28 で入れた（8360be2e・27d05de1）。27d05de1 で CI 一式 8 run と Safari の 10 回の確認がすべて成功し、Build and Test は承認された（FR10.1 だけが公開前で Unverified、Accept failure）。読み直すと、設計と入れたものの間に次の食い違いがある。

1. 夜間の fuzz が 2 回走る：`nightly.yml` が `u14-fuzz.yml` を直接呼び（`fuzz` の job）、さらに `u14-quality.yml` の中の `u13-fuzz` の job も同じ `u14-fuzz.yml` を呼ぶ（U15 の review-09 の指摘、`pending-minor-fixes.md` に記録済み）。
2. 設計にない workflow：NFR7 の確認のために足した `u11-safari-stability.yml`（手動と、`codex/build-and-test` へのそのファイルの push で起動）が、「残す（20）」の一覧にない。push の起動条件は、GitHub の手動起動が fork の既定のブランチにある workflow しか起動できなかったため、人の判断で足したもので、作業ブランチの名前が入っている。

どう扱いますか。

A. この段階では設計の記録（`ci-config.md`・`quality-gates.md`）を今の形に合わせて書き直し、1・2 の直し（夜間の fuzz を 1 回にする、`u11-safari-stability.yml` を残す一覧に足し、作業ブランチの push の起動条件を外すか main に替える）は、Q1 の A のとおり次の製品の変更でまとめて行う。workflow は今は変えず、push も CI の起動もしない（推奨）
B. 今すぐ workflow を直す。U15 の Code Generation に戻って直し、署名 push と CI 一式、新しい head の binding と採用をやり直す
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- 時期（Q1：A）：この段階では CI の設計（`ci-config.md`・`quality-gates.md`）だけを書く。workflow の変更は、公開の前に製品をもう一度変えるとき（NFR7 の Safari の直しと、残している Minor）にまとめて行い、入口の作り直しと CI 一式を 1 回で済ませる。この段階では push も CI の起動もしない。
- 夜間（Q2：A）：`nightly.yml` を、`u14-fuzz.yml`（13 対象×600 秒）と `u14-quality.yml`（wasm 4 環境と速さの判定）を呼ぶ形に作り直す設計にする。失敗したら Issue を作る。
- 作業用の workflow（Q3：A）：正式な証拠に使ったものとそれらが呼ぶものだけを残し、ほかは削除し、古い作業ブランチへの push の条件も外す設計にする。正式な確認コマンドが固定するファイルは、入口の更新とあわせて扱う。
- 必須チェック（Q4：A）：upstream の `main` のブランチの保護で、`ci.yml` の全 23 job と `release-check.yml` を必須にする（設定は upstream の管理者が行う）。各品質・ファジング・速さは、夜間と公開の前の確認にする。
- Construction → Operation の境界の確認：`verification/phase-check-construction.md` に書く。Unit をまたぐ要件の対応は FR10.1 が未対応で、Build and Test は FR10.1 が Unverified、NFR7 が Not Met のまま（人が Accept failure を選んだ）なので、境界の確認は「未解決あり」と記録する。Operation フェーズはこのワークフローではスキップしている。


（U15 の確認コマンドの入口の作り直しの後、2026-10-18 に見直した要約）

- Q1〜Q4 の回答と、CI の設計（`ci-config.md`・`quality-gates.md`）はそのままにする。製品と workflow は変わっていない。
- 書き足すこと：今の正式な確認コマンドが U15 の新しい入口 `entry-e3c29d1d/entry-c.py` になったこと。新しい入口は、必須の 7 workflow を入口の中に固定していて、binding で減らせないこと。Q3 の A で残す workflow にこの 7 つはすべて入っているので、整理はそのままできる。ただし、この 7 つのどれかを消したり名前を変えたりするときは、入口の新しい版が要ること。
- 境界の確認（`verification/phase-check-construction.md`）の判定は「未解決あり」のまま（FR10.1・NFR7）。

（U15 の Step22〜30 と Build and Test のまとめ直しの後、2026-10-19 に見直した要約）

- Q1〜Q4 の回答はそのまま。CI の設計は U15 の Step22〜28（8360be2e・27d05de1）で入れ終わり、27d05de1 で CI 一式 8 run と Safari の 10 回の確認がすべて成功した。`ci-config.md`・`quality-gates.md` を「設計」から「入れた後の今の形」に書き直す（head 27d05de1、必須チェックの job の名前は PR ゲート run 39143561947 と公開物の確認 run 39143562106 のとおり）。
- 今の正式な確認コマンドは U15 の `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（2026-10-19 に人が採用）。entry-c は履歴。
- Q5 の A：夜間の fuzz が 2 回走ること（`nightly.yml` の `fuzz` と `u14-quality.yml` の `u13-fuzz`）と、`u11-safari-stability.yml` が残す一覧にないこと・作業ブランチの push の起動条件を持つことは、記録に書き、次の製品の変更でまとめて直す（`pending-minor-fixes.md` にも記録済み・追記する）。workflow は変えず、push も CI の起動もしない。
- NFR7 は Build and Test で Met（10 回の確認は暖機のある PR の Safari の経路だけ、という注記つき）。
- 境界の確認（`verification/phase-check-construction.md`）は、FR10.1（公開前、Unverified、Accept failure）が残るので「未解決あり」のまま。NFR7 の Not Met は解消したので、その記述を直す。

- Looks correct
- Request changes

[Answer]: Looks correct
