# U15 公開実装・ローカル検証

## 現在の状態（2026-10-18 JST、Step19〜21）

人は確認の方法として案1（層の積み重ねをやめ、e3c29d1dを起点にした新しい入口）を選び、案 `verification/entry-e3c29d1d-proposal.md` と計画のStep19〜21を承認した（Plan Approval、内容確認 `step19-21-summary-questions.md` はLooks correct）。製品・workflow・lockは変えず、push・CI・計測・公開もしていない。

- 新しい入口：`verification/entry-e3c29d1d/`。起点の記録（入口v4がe3c29d1dでexit 0になった検証 `435bc5e0-3818-4691-9d84-a9add39239d9` とその出力、e3c29d1dのCI 7 runの記録、artifactの一覧の記録 `ci-artifacts-e3c29d1d.json`、FR8.3の原本）とv1〜v4の12ファイルのbytesを固定し、v1〜v4はもう実行しない。毎回確かめるのは、署名と系譜（各commitのtreeも手元のgitと照合）、変わったファイルの一覧（binding・保存したcompare・手元のgit）、headの `aidlc/` の外の全追跡ファイルのbytes（違いを許すのは `.aidlc-version` と `mise.toml` だけ）、headに無いファイルの除外、CI（必須の7 workflowは入口に固定、jobの集合は起点より減らせない、認めた再実行だけattempt 2）、速さ（`U14 current full quality` に固定、ZIPのdigestは保存したAPIの記録から）。
- 版の経緯：
  - v1（`entry.py`・`binding-e01.json`）：本番の実行が手元のファイル12件で拒否された（`run-1792325657506892000-42086/refusal.json`）。
  - 人の判断：「git の無視＋2 つ」。git が無視するファイルと `.aidlc-version`・`.venv-u15/` を除外にした。
  - b（`entry-b.py`・`binding-e02.json`）：本番の実行はexit 0。独立レビュー01はNOT-READYで、Major 3件（無視の出どころを縛っていない、bindingで検査を緩められる、追跡ファイルのbytesの免除が広い）。
  - c（`entry-c.py` 44a8d9d0…、`binding-e03.json` fd55262c…）：3件を直した。無視の出どころはheadのtreeにある `.gitignore` だけを認め、git は `core.excludesFile=` を空にし、`GIT_*` の環境変数を外して呼ぶ。回帰106件（v1 30・b 36・c 40）が成功。本番の実行はexit 0（`run-1792327873535813000-33039/result.json`）で、起点との違いはU12のSafariの1 jobの再実行だけ。独立レビュー02はREADY（Minor 5件）。
- 採用：人は2026-10-18に、`entry-c.py` のコマンドを正式な確認コマンドとして承認した（`verification-command.txt`）。入口v4は履歴になる。
- 計画外の手順：
  - checkpointの検証の記録 `.aidlc-construction-checkpoints/u15-release/unit.json` は次の検証で上書きされる。そのため同じbytesの写し `verification/entry-e3c29d1d/base-checkpoint-435bc5e0.json` を置き、入口はそのSHA-256を固定した。
  - FR8.3のZIPのdigestの出どころとして、読み取りのGETでartifactの一覧を `ci-artifacts-e3c29d1d.json` に保存した。
  - 開発担当が `core.excludesFile=` の効き目を確かめたときに、shellで一時フォルダを作ってすぐ消した。何も残っていない。
- 残しているMinor：独立レビュー02の5件（`verification/entry-e3c29d1d/independent-review-02.md`）。次に入口かbindingを更新するときにまとめて直す。主なものは次の4つ。
  - `aidlc/` の行に付く注記が事実と違う。
  - 再実行の許可の件数に上限がない。
  - artifactの一覧の `repository_id`・`expired` を見ていない。
  - 利用者の git 設定を読む。
- 次の製品の変更（NFR7のSafariの直し、CIのworkflowの変更、残しているMinor）では、変更をそろえて1回だけpushし、CI一式を1回実行する。そのあと、新しいheadの `binding-e04.json` を作って採用を伺う。入口のコードは変えない。
- FR10.1とNFR8は実公開と公開後の照合までGAPのまま。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：現在の状態（2026-10-18 JST、Step18）（作成時の見出しは「現在の状態（2026-10-18 JST、Step18）」）

Step17の直し（下の「履歴：現在の状態（2026-10-18 JST、Step17）」）のあと、人の承認を受けてStep18を行った。

- 署名push：人が「push する」を選んだあと、Step17の7ファイル（`docs/release.md`、`scripts/release/check.py`・`policy.py`、`tests/release/test_api.py`・`test_check.py`・`test_policy.py`・`test_publish_adapter.py`）だけのcommitを、署名付きjjでfork `codex/build-and-test` へ送った。head e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9（親 a54315f9、GitHubでVerified）。7ファイルの作業コピーのbytesはcommitのblobと同じ。
- CI（e3c29d1d、7 run、すべてsuccess）：CI 39114018191（PR）、Release package checks 39114018143（PR）、U14 current full quality 39114108809（34 job）、U13 current full quality 39114112207、U14 fresh thirteen target ASan and LSan 39114114216、U1 U14 current-source evidence 39114116352、U12 current full quality 39114110570。U12は1回目に1 jobだけ失敗した（117638480843 「u11-programs / differential (macos-latest, safari)」、safaridriverがSafariの起動を待つ間の時間切れで31秒、runner側の揺れと判断。原因は確かめていない）。人が「失敗 job だけ再実行」を選び、2回目は29 jobすべてsuccess。1回目の原本は `verification/ci-e3c29d1d/u12-quality-39114110570/attempt-1/`。
- FR8.3（e3c29d1dで1回だけ測った値、測り直しなし）：run 39114108809のNode jobの `u11-node` の `performance/observations.json`（`verification/ci-e3c29d1d/u14-quality-39114108809/u11-node/`、ZIPのSHA-256はAPIのdigestと一致）で、インタプリタ平均5.2649、JIT平均4.5834（約12.9%短い）、p=1/1024、`pass: true`。
- 確認コマンドの入口v4（`verification/version-allowance/u15_candidate_v4.py` dfb0e03a…、`binding-11.json` fb466da7…）：v3を固定したbytesのまま実行し、e3c29d1dとそのCI 7 runを足す。許可は前と同じ15ファイルで広げていない。U12の2回目は、この1 runの1 jobだけを明示して認める。v3のMinor 4件はv4の出力とREADMEで直した（`pending-minor-fixes.md` の「v4 での対応」）。回帰163件成功、本番の実行はexit 0（`run-1792319052786132000-7821/`）、独立レビュー04（`independent-review-04.md`）はREADYでMinor 6件。人は「採用、Minor は次で」を選び、v4を確認コマンドとして承認した（`verification-command.txt`）。Minor 6件は `pending-minor-fixes.md` に残し、次に製品か入口を更新するときにまとめて直す。
- 手順書：`unit-test-instructions.md` の1行目のunittestは、`test_api` と `test_publish_adapter` が `discover` の形でしか読み込めないためexit 1になる（全件は2行目の `discover` で146件成功）。手順書を直すとPlan Approvalをもう一度受ける必要があるため、このattemptでは直していない。
- FR10.1とNFR8は、upstreamへの取り込み・`release` environment・初回トークン・Trusted Publisher・tag・実公開と公開後の照合（docs/release.md の Owner hand-off）までGAPのまま。`U15_acceptance: GAP` は、正式確認コマンド（今は `u15_candidate_v4.py`）が出力に書く欄の値で、U15の公開の受け入れが終わっていないことを示す。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：現在の状態（2026-10-18 JST、Step17）（作成時の見出しは「現在の状態（2026-10-18 JST、Step17）」）

U15の確認で人はRequest Changes（「先に R-16〜R-18 を直してください。」）を選び、そのあと「承認して進むが、他の指摘と一緒にまとめて直す」と決め直した。計画のStep17〜18をPlan Approvalで承認し、内容確認（`step17-18-summary-questions.md`）はLooks correct。このattemptではStep17だけを行った。Step18（署名push・CI・確認コマンドの入口の更新）はまだで、push・commit・CIの起動・tag・registryやネットワークへのアクセスはしていない。

- 作成・変更したファイル（Step17）：`scripts/release/check.py`、`scripts/release/policy.py`、`docs/release.md`、試験 `tests/release/test_check.py`・`test_api.py`・`test_policy.py`・`test_publish_adapter.py`。U15の記録は、この `code-summary.md`、`traceability.json`、`unit-test-instructions.md`。`release.yml` などのworkflow・`package.py`・`acceptance.py`・版のファイルは変えていない。
- R-16（Major、最初の公開が途中で止まったときの再開）：
  - `check.registries_absent(order, version, approved)` は、11のcrateの名前と `@paludarium/wasm` の有無を前と同じく調べ（200／404以外は止まる）、あるものについてだけ、承認済みのdigestと比べる。crates.ioは `/api/v1/crates/<name>/<version>` の `version.checksum`（`.crate` のSHA-256）、npmは `/<pkg>/<version>` の `dist.integrity`（tarballのSHA-512 integrity）。名前はあるが版がない、digestが違う、digestが読めない、承認済みのdigestがない、のどれか1つでもあれば `mismatched` に載り、`resume` は `false` になる。
  - 承認済みのdigestは `check.approved_digests(root, head)` が、公開jobがダウンロードした `target/u15/package-result.json`（`passed`・同じhead・`local_snapshot: false` を確かめる）と、ただ1つのnpm tarball（`tar_sha256` の一致を確かめる）から作る。registryに何かあるときだけ読む。
  - `check.authorize` は、申告（`first_publication: true`）があり、Trusted Publisherの申告がないときだけこの確認をする。`mismatched` が1つでもあれば、何も公開する前に「trusted publishers unregistered; first-publication resume refused: …」で止まる。文書に書かれた `registries_absent`・`registry_presence`・`registry_resume_verified` は捨て、その場の確認の結果だけを使う。
  - `policy.authentication` は、`registries_absent: true`、または `registry_resume_verified: true`（いずれも `True` そのもの）のときだけ初回トークンを認める。申告がなければ前と同じく拒否する。
  - 再開のとき、`publish_artifacts` は前と同じく、すでにある版は照合だけ（再uploadしない）、ない版だけを依存の順にuploadする。公開済みの版は消さず、上書きしない。
  - `docs/release.md` の手順(3)に、再開の手順（同じ `release.yml` のrunの公開jobを再実行する。承認とトークンの期限）と、crates.ioの新しいcrateの作成数の制限（11 crateを続けて作る前に確かめ、必要ならhelp@crates.ioに引き上げを頼む）を書いた。制限の具体的な数は確かめていない（ネットワークを使わないため）。
- R-17（Minor）：`publication_environments` を許可リストにした。cargo（dry-runとupload）には `CARGO_ENVIRONMENT`（PATH・HOME・RUSTC・RUSTDOC・CARGO_HOMEなど）だけを渡し、`GH_TOKEN`・`GITHUB_TOKEN`・`ACTIONS_ID_TOKEN_REQUEST_*` は渡らない。npmには `NPM_ENVIRONMENT`（CI・GITHUB_ACTIONS・`ACTIONS_ID_TOKEN_REQUEST_URL`/`_TOKEN`・provenanceの文に入るGitHubの情報・RUNNER_ENVIRONMENT・setup-nodeの `NPM_CONFIG_USERCONFIG` と `NODE_AUTH_TOKEN`）だけを渡す。初回の公開では `NODE_AUTH_TOKEN` を限定トークンに置き換える。npmのリストは、npmのGitHub Actions向けprovenanceの作り方に合わせたもので、足りるかどうかは実公開でしか確かめられない（未検証）。
- R-18（Minor）：`docs/release.md` の手順(3)に、`paludarium*` は前方一致で `paludarium` で始まるほかの名前にも当たることを書き、11の名前を1つずつ指定することを勧めた。
- R-13（Minor）：下の「履歴：現在の状態（2026-10-18 JST、Loop-back 1）」の冒頭の「traceability.json…は変えていない」の後に、Step11の時点の文であることとStep12で説明文の先頭を変えたことの注記を足した（ほかの本文は変えていない）。
- R-14（Minor）：`traceability.json` のFR10.1・NFR8の説明文の先頭を、計画の道しるべの1文（「現行（2026-10-18 JST、Step17）：最新の状態はcode-summary.mdの「現在の状態（2026-10-18 JST、Step17）」節を参照。」）だけにし、その後の文は「履歴（Loop-back 2）：」「履歴（Loop-back 1）：」として残した。Loop-back 1で道しるべより多く足していた文（FR8.3の根拠・GAPのまま）も、「履歴（Loop-back 1）」の中に残している。status・target・idは変えていない。
- R-15（Minor）：`U15_acceptance: GAP` は、正式確認コマンド（今は `u15_candidate_v3.py`。前はU14の `u14_candidate_v2.py` などの入口）が標準出力のJSONと結果ファイルに書く欄 `U15_acceptance` の値である。U15の公開の受け入れ（FR10.1）が終わっていないことを示す固定の値で、`u15-acceptance` producer（`u15-acceptance.yml` の作るartifact）の結果ではない。
- 足した試験（19件、tests/releaseは127件から146件）：
  - `test_check.py`（9件）：`test_resume_when_present_versions_match`、`test_resume_refused_when_one_version_differs`、`test_resume_refused_for_npm_integrity_difference`、`test_resume_refused_when_version_absent_or_unreadable`、`test_resume_refused_without_approved_digest`、`test_approved_digests_loaded_only_when_present`、`test_resume_version_query_unknown_stops`、`test_cargo_children_get_no_github_or_oidc_request_variables`、`test_npm_child_gets_only_provenance_variables`。
  - `test_api.py`（4件）：`test_first_publication_resumes_when_present_versions_match`、`test_first_publication_resume_refused_on_one_difference`、`test_document_cannot_assert_resume`、`test_resume_without_first_publication_declaration_refused`。
  - `test_policy.py`（2件）：`test_first_publication_verified_resume_allowed`、`test_resume_flag_needs_declaration_and_exact_true`。
  - `test_publish_adapter.py`（4件）：`test_resume_uploads_only_remaining`、`test_resume_stops_on_different_present_digest`、`test_approved_digests_from_package_artifact`、`test_cargo_uploads_never_see_github_or_oidc_request_variables`。
  - 既存の `test_api.py` の初回の公開の試験の補助（`authorize_first`）に、承認済みdigestの読み込みを差し替える処理を足した。既存の試験の期待（「trusted publishers unregistered」での拒否）は変えていない。registryとGitHubはすべてメモリ上の偽物で、ネットワークには出ない。
- 手元の実行（2026-10-18、Python 3.15.0、coverage 7.16.2）：
  - 変更前のtests/release全件：127件成功（ベースライン）。
  - 手順書の1行目（`-m unittest tests.release.test_check tests.release.test_api tests.release.test_publish_adapter tests.release.test_policy -v`）：exit 1。68件を実行し、`test_api` と `test_publish_adapter` の2つのmoduleが読み込みで失敗した（`ModuleNotFoundError: No module named 'test_policy'`／`'test_package'`）。この2つは `from test_policy import …`・`from test_package import …` のように `tests/release` を探索の起点にする `discover` の形でだけ読み込める。読み込みの行はこのattemptで変えていない。同じ試験は2行目の `discover` で全件実行した。
  - tests/release全件（`discover`）：146件成功、exit 0。
  - `check.py --mode validate`：exit 0（`validated: true`、`version: 0.1.0`、`crates: 11`、`publish_eligible: false`）。
  - `check.py --mode package-check`：exit 0。coverageの `--append` で2回目を実行し、結果は `passed: true`、`local_snapshot: true`、source `3b85b96d…`、11 crate、npm tarball `deecec5f…`（0.1.0）、7ケース、`stable_supported: false`、`published: false`。1回目の実行では誤って標準エラーをファイル（`target/u15/` の下、0 bytes）に送ったので、そのファイルは消した。
  - coverage（unittestにvalidate・package-checkを `--append`）：acceptance.py 99.64%、check.py 96.85%、package.py 98.33%、policy.py 100%（合計98%、`--fail-under=80` exit 0、JSONで4ファイルすべてが80%以上）。
- 正式確認コマンド：今のv3（`u15_candidate_v3.py`）は、`docs/release.md`・`scripts/release/check.py`・`scripts/release/policy.py`・`tests/release/test_api.py`・`test_check.py`・`test_policy.py`・`test_publish_adapter.py` を署名a54315f9のbytesに固定しているので、Step17のあとは止まると見込まれる（実行していない）。入口の更新（v4）と入口v3のMinor 4件はStep18で行う。
- 確かめていないもの：本物のregistry・OIDC・初回トークンでの公開と再開、npmの許可リストで実際のprovenanceが作れること、crates.ioの新しいcrateの作成数の制限の値、公開jobの再実行で前のattemptの `u15-package` artifactを使えること。
- FR10.1とNFR8は実公開と公開後の照合までGAPのまま。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：現在の状態（2026-10-18 JST、Loop-back 2）（作成時の見出しは「現在の状態（2026-10-18 JST、Loop-back 2）」）

Build and TestのLoop-back 2（Steps13〜16）。人はBuild and TestでQ6「公開まで進める」、Q7「0.1.0」、Q8「U15に戻って行う」を選び、Step13〜14の後にQ1「CIのcoverageにacceptance.pyを足す」・Q2「validateの古い表示を直す」・Q3「自分のレビューの禁止を外す」・Q4「初回は限定トークンでCIから」を選んだ。

- 作成・変更したファイル（この attempt）：
  - Step13（版0.1.0）：`Cargo.toml`（workspaceの版と依存11件）、`Cargo.lock`（workspaceの13 crateの版の行）、`fuzz/Cargo.lock`（9 crateの版の行）、`packages/paludarium-wasm/package.json`、`README.md`（版の文の3行。CRLFの行は元のまま）、`docs/release.md`。
  - Step14（受け入れの証拠）：新規 `scripts/release/acceptance.py`、`.github/workflows/u15-acceptance.yml`（手動起動だけ、`contents: read`・`actions: read`）、`tests/release/test_acceptance.py`。`docs/release.md` に品質8目的と受け入れ5条件の対応表を書いた。
  - Step14b：`scripts/release/policy.py`（自分のレビューの禁止を必須から外す。必須レビュアーと管理者の迂回の禁止は必須。認証の方式の判定）、`scripts/release/check.py`（validateの表示、registryの存在確認、初回トークンとOIDCの切り替え）、`.github/workflows/release-check.yml`（coverageの対象を4ファイル）、`.github/workflows/release.yml`（初回トークンとOIDC）、`.github/workflows/u15-acceptance.yml`（初回の申告の入力）、試験 `test_policy.py`・`test_check.py`・`test_api.py`・`test_publish_adapter.py`・`test_acceptance.py`、`docs/release.md` の人の手順(2)〜(6)。
  - Step16（文書の部分）：`docs/release.md` の Owner hand-off (1)〜(6)。
- 手元の試験：tests/release 127件すべて成功（attempt の始めは71件）。`check.py --mode validate`・`--mode package-check` は exit 0（11 crateの0.1.0、crate外consumer、npm tarball 0.1.0、7ケース、`stable_supported: false` は前と同じ）。coverage（validate・package-checkを `--append`）：acceptance.py 99.64%、check.py 96.98%、package.py 98.33%、policy.py 100%。`cargo build --workspace --locked`・fmt・clippy は exit 0。
- 署名付きでforkへ送ったhead：
  - `bb197e04db6387eb0c37222c25f60814524ab173`（Step13〜14、親57a8c96f、11ファイル、Verified）。CI 7 runすべてattempt 1で成功（CI 39089163556、Release package checks 39089163510、U14 39089194062、U12 39089195709、U13 39089197410、ファジング 39089199122、ソースの照合 39089200731）。FR8.3はJITなし5.4858秒・JITあり4.5940秒、p=1/1024。
  - `a54315f9493d6e9fb8d4792ffcefd12203540311`（Step14b、親bb197e04、12ファイル、Verified）。CI 8 runすべてattempt 1で成功（U14 39096893624、U12 39096895814、U13 39096898087、ファジング 39096899756、ソースの照合 39096901200、Release package checks 39107620902・39108225338、CI 39108225399）。FR8.3はJITなし5.8458秒・JITあり4.6060秒（約21.2%速い）、p=1/1024、20回すべてexit 0（原本 `verification/ci-a54315f9/u14-quality-39096893624/u11-node/performance/observations.json`）。
  - PR #1（fork内のdraft）がforkのmainと `release-check.yml` でぶつかりpull_requestのrunが作られなかったため、人の指示でforkのmainに `804e4aa681460d8f52f04b67378fa65265f15f4c`（親ccfeef0b、`release-check.yml` をa54315f9の中身に合わせる1ファイル、Verified）を足した。ブランチのheadは変えていない。
- 正式確認コマンド：版の書き換えで旧コマンド（U14の `u14_candidate_v2.py`）が `Cargo.lock` で止まったため、版の行だけを認める入口を作った。人が採用した今のコマンドは `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate_v3.py --entry-sha256 ebb6789417b48d7e8e8ef3c5ae8919483a85eda0ea85ecda5fbf001d74c2e798 --binding-sha256 44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e`（独立レビュー `verification/version-allowance/independent-review-03.md` READY、回帰147件）。許可は15ファイルだけで、うち版の行だけの証明が4つ、a54315f9のバイト列の固定が11。固定した11ファイルの中身はこのコマンドではなく、U15のレビュー・試験とa54315f9のCIで確かめる。どの固定にも入らないのは `u15-acceptance.yml`・`acceptance.py`・`test_acceptance.py` の3つ。残るMinor 4件は `verification/version-allowance/pending-minor-fixes.md`。
- U1はこのコマンドの前の版（v2）で確かめ直し、人が承認した。
- 試験を書いたが実行していないもの：本物のregistry・OIDC・初回トークンでの公開とその後の照合（mockでは証明できない）。
- FR10.1（公開）とNFR8は、upstreamへの取り込み・`release` environment・初回トークン・Trusted Publisher・upstreamのmainのheadでの品質runと `u15-acceptance`・`v0.1.0` のtagと承認・公開後の照合（`docs/release.md` の Owner hand-off）が済むまでGAPのまま。upstreamへのsquash mergeでheadが変わるため、upstreamのmainのheadでCIと受け入れの証拠を作り直す必要がある。
- 計画との違い：Step 16 は手順を `docs/release.md` に書いた。人への引き渡し（各手順の時期と確かめ方を伝える）はU15の確認のときに行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：現在の状態（2026-10-18 JST、Loop-back 1）（作成時の見出しは「現在の状態（2026-10-18 JST、Loop-back 1）」）

Build and TestのLoop-back 1（Step11）。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）、U11のSafariの待ち時間の修正（2b8723ab・57a8c96f）、正式確認コマンドの更新の途中で、Code Generationの段階全体の作り直しのため、U15を確かめ直した。製品・workflow・traceability.json・source-manifest.jsonは変えていない。（Step17で足した注記：この文はStep11の時点のもの。Step12でtraceability.jsonのFR10.1・NFR8の説明文の先頭だけを変えた。下の「Step12」の箇条を参照。）

- U15の担当ファイル（source-manifestの28ファイル）は、e4f84768から変わっていない（`git diff --stat e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <全ファイル>` の出力が空）。
- FR8.3（JITありが速い）：今の根拠は、U14の署名1ceae86ce303a1019e97ac7d162ce0efa9fadd50のU14 quality run 39030957672で1回だけ測った正式性能である（JITなし平均4.5277275564秒、JITあり3.6349344776秒、約19.72%速い、片側p=1/1024。原本はU14の `verification/loopback1-next/perf-39030957672-observations.json`、詳細はU14のtraceability.jsonのFR8.3の行）。その前のBuild and Testのbd247f1e（run 39009460781）では不合格（p=529/1024）だった。下の履歴の節にある208fd965の旧測定の再利用（改善2.74%、p=7/1024）は、今の根拠ではない。
- 下の履歴の節の「be45の `u12-native-first.yml` は古いまま」は解消した。この修正（ゲストビルドに `--advisory-policy u15-fixed-aube-zip9-name` を付ける）はU12 Steps11〜12でe4f84768に取り込まれ、U12の品質CI（u12-quality、macOSの `macos-host` jobを含む）はe4f84768（run 39015780495、3回目の実行で成功）・1ceae86c（39028303336）・2b8723ab（39044793102）・57a8c96f（39073501121、1回目に差分テスト（x86-64 Linux）のjobが失敗し、失敗したjobだけを再実行した2回目で成功）で成功した。macOSがApple Silicon（arm64）だけであることは、履歴のce0bのrun 38996219364（host `aarch64-apple-darwin`）で確かめたもので、これらの新しいrunの `macos-host` のhostは確かめていない。
- 配布の検査：57a8c96fのRelease package checks（run 39073492188、attempt 1）が成功した。
- 今の正式確認コマンドは、人が採用した `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/verification/loopback1-next/u14_candidate_v2.py --entry-sha256 934f21bc9ca7f58d68a72dc9759df90ae1f28c63791600bb552039c3cfe0d23a --binding-sha256 425ae3e7554a84de78062723954317f0bb2bba99c41567773bc1752c63ecdd7e` である。2026-10-18のU15 checkpoint（Step11）での検証はexit 0だった。
- Step12（Step11の再レビューのMinorへの対応）で、この節のu12-qualityの箇条と最後の箇条、traceability.jsonのFR10.1・NFR8の行の先頭、手順書の参照先と期待結果、下の履歴の節の冒頭の注記を直した。
- FR10.1（公開）とNFR8（供給網の安全）は、実公開と公開後のregistryの照合までGAPのまま。版の決定、tag、名前所有と初回publish、Trusted Publisherと保護されたrelease environmentの設定（持ち主が設定する）が残っている。
- 下の節は、それぞれの時点の履歴として読む。下の節の本文にある「現行」「現在」「未実施」「未検証」は、その節を書いた時点のものを指す。`U15_acceptance: GAP` は、U15の公開の受入が未完了という表示である。（Step17で足した注記：この表示は正式確認コマンドの出力のJSONの欄 `U15_acceptance` の値。詳しくは先頭の「現在の状態（2026-10-18 JST、Step17）」節のR-15。）

## 履歴：現在の状態（2026-10-17）（作成時の見出しは「現在の状態（2026-10-17）」）

（履歴：2026-10-17時点の記述。今の状態は先頭の「現在の状態（2026-10-18 JST、Loop-back 1）」節）この節が U15 の現在の状態をまとめた唯一の場所。下の「（履歴）」付きの節は当時の記録で、本文は変えずに残している。履歴の節の記述とこの節が食い違うときは、この節が現在の状態を示す。Step9（独立レビュー `reviews/review-01.md` の Minor 5 件への対応、`step9-summary-questions.md` で Looks correct）では記録の整理と補足だけを行い、新しい CI・push・測定・公開・試験の実行はしていない。

### Steps の状態

| Step | 状態 |
|---|---|
| 1〜6 | 実装・単体 71 件（policy 21、package 16、check 15、API 11、publish adapter 4、統合 4）・package-check を記録済み。CI（release-check run `38897653085`、全品質 run `38897611874`）でも success（履歴「現行Steps7〜8」） |
| 7 | 公開前受理条件を記録済み（下の要件ごとの表）。ネイティブ macOS は Apple Silicon（arm64）だけ。FR8.3 は再利用した旧測定への結びつけ（独立レビュー review-01 は READY で、この結びつけを妥当と判断した） |
| 8 | 記録・sensor・独立レビュー（review-01：READY、Minor 5 件）まで記録済み |
| 9 | この節の追加と記録の補足（このあと正式 sensor、独立再レビュー、正式検証、人の完了承認） |
| 10 | 再レビューの指摘 N1・N2 への対応。読み取り専用の照合 `verification/step10_evidence_check.py` を 1 回実行し、`verification/step10-evidence-check.json`（passed true）の参照を下の主張に付けた（このあと正式 sensor、独立再レビュー、正式検証、人の完了承認） |

### 要件ごとの結果

| 要件 | 状態 | 根拠（証拠） | 再利用・限界 |
|---|---|---|---|
| FR6.3（probe 全項目 PASS） | PASS（FR5 の 7 環境） | Linux・Windows・Node・Chromium・Firefox・Safari：`verification/step7-acceptance-binding.json`（be45 の run `38897611874`）。macOS：`verification/step7a2-macos-binding.json`（ce0b の run `38996219364`） | macOS は arm64 だけ。macOS は be45 ではなく ce0b で動かした（下の「macOS の証拠と be45」） |
| FR7.2（aube 4 コマンドがネイティブと同じ） | PASS（7 環境） | 同上 | 同上 |
| FR7.3（#1645 の 0.0.0 再現） | PASS（7 環境） | 同上 | 同上 |
| FR8.2（JIT あり・なしが同じ） | PASS（wasm 4 環境：Node・Chromium・Firefox・Safari） | `verification/step7-acceptance-binding.json` | ネイティブ JIT は範囲外 |
| FR8.3（JIT ありが速い） | 旧測定に BOUND（再利用した測定。新しい測定ではない） | `verification/step7b-fr83-closure-02.json`、U14 `jit-u9-next/formal-ci-38840433942/`・`formal-analysis-208fd965-01/` | 下の「FR8.3 の再利用」の限界つき |
| FR10.1（公開） | GAP | — | 実公開・tag・Trusted Publisher・release environment は未実施 |
| NFR8（供給網の安全） | GAP | release.yml／release-check.yml の SHA 固定、`cargo deny --locked check` success | registry・OIDC・provenance の実照合は実公開なしでは示せない |
| NFR9（toolchain） | OK | `rust-toolchain.toml` の nightly-2026-10-11 をローカルと be45 の CI が rustc 1.101.0-nightly 6f5da406b として使用 | stable 1.99.1 は MSRV 1.101 で exit 101。stable 対応とは言わない |

### FR8.3 の再利用（保存原本で確かめた事実）

- 再利用した run `38840433942`（U14 current full quality、`.github/workflows/u14-quality.yml`、workflow_dispatch、head `208fd9652528fbb9002a7bd25c0cb1f2105a5738`）には attempt が 2 つある。
  - attempt 1：completed／**failure**（U14 原本 `formal-ci-38840433942/official-run-final.json`、run_attempt 1、updated_at 2026-10-16T02:39:55Z）。34 job のうち failure は Safari job `116781223111` `u11-programs / differential (macos-latest, safari)` の 1 件だけで、step 12「Compare identical fourteen cases in both execution modes」が失敗した（`verification/u15-macos-native-38996219364/reused-run-38840433942-attempt1-jobs.json`。job 数 34・success 以外が この 1 件だけ・Node job `116781223162` が success であることは `verification/step10-evidence-check.json` の `c_reused_run_38840433942.attempts.attempt1` で照合済み）。原因は WebDriver の session 作成要求の 10 秒 timeout で、guest の観測は両 mode とも 0 行（U14 `formal-safari-208fd965-refusal-proof.md`）。比較の不一致ではない。
  - attempt 2：Safari job だけを再実行し（job `116783397511`、success）、run は completed／**success**（U14 原本 `retry-attempt2-official-run.json`、および今回保存した `reused-run-38840433942-current.json`：run_attempt 2、conclusion success、updated_at 2026-10-16T02:44:54Z）。attempt 2 の 34 job はすべて success（`verification/step10-evidence-check.json` の `c_reused_run_38840433942.attempts.attempt2`：job 数 34、success 以外 0 件、Node job `116783399354` success、Safari job `116783397511` success。`current_run`：run_attempt 2、conclusion success、head_sha `208fd9652528fbb9002a7bd25c0cb1f2105a5738`）。
  - 照合結果 JSON `step7b-fr83-closure-02.json` の `old_run.conclusion: failure` は attempt 1 の値。レビューの「run 全体は failure」も attempt 1 を指す。現在の API の値（attempt 2 の success）とは矛盾しない。照合結果 JSON は変更していない。
- 性能の数値は **attempt 1 の Node job `116781223162`**（`u11-programs / differential (ubuntu-latest, node)`、success）の step 14「Frozen paired full-probe performance」（success、02:36:20〜02:38:31Z）から得たもの。attempt 2 の Node job `116783399354` は GitHub が付け替えた ID で、step と時刻が attempt 1 と同じ（再実行ではない。U14 `formal-safari-208fd965-retry-proof.json` の `node_steps_and_timestamps_unchanged: true`、`no_performance_remeasurement: true`）。Safari job では性能 step は skipped で、Safari の失敗は性能の数値に関係しない。
- 数値：インタプリタ平均 5.856590694899998 秒、JIT 平均 5.696370400100001 秒、改善 2.7357263491%、片側 p = 7/1024（0.0068359375）、seed 5321、warmup 各 1、10 対。
- **runner のハードウェアは比べられない**：測定は当時の GitHub-hosted ubuntu runner（Node job のログでは image ubuntu-24.04 version 20261012.334.1、Azure northcentralus）で行われた。runner の CPU・負荷・image は照合の入力に含まれず、後の run と同じ・管理された条件とは言えない。この再利用は「runner が読む入力が同じ」ことに基づくもので、同じハードウェアで測り直したことを意味しない。be45 や公開 head での新しい性能は主張しない。
- **closure の照合の限界**：`step7b_fr83_closure_02.py` は、JS の import を正規表現で取り出している。対象は二重引用符の静的 import（`from "…"`、`import "…"`、`import("…")`）と `new URL("…", import.meta.url)` だけ。静的 import（`from '…'`、`import '…'`）と `new URL(` の単一引用符・template literal・複数行にまたがる書き方は取り出せず、見落としても未解決として報告されない。動的な `import(` は別の検査で拾う：`step7b_fr83_closure_02.py` の 126 行目 `NON_LITERAL_IMPORT`（正規表現 `\bimport\s*\(\s*(?!")`、151 行目で closure の各ファイルに適用、302 行目で `non_literal_dynamic_imports` に記録）は、`import("` とすぐ続く形以外のすべて（単一引用符・template literal・変数・`(` と `"` の間の空白や改行）を含むファイルを未確認として GAP 側に数える。その結果は 208fd965・be45b36c とも 0 件（`verification/step10-evidence-check.json` の `b_non_literal_dynamic_import_detection`。以前のこの節の「引用符で始まらない `import(`」は、正しくは「二重引用符がすぐ続かない `import(`」で、単一引用符・template literal の動的 import はこの検査で拾われる。Step10 で記述を直した）。結論は「見つけた 10 ファイルが両 commit で全 bytes 一致した」ことに依っており、それ以外の書き方の import が存在しないことまでは証明していない。履歴の節にある「runner が読む入力はすべて一致」「10 ファイルすべて一致」は、この範囲で読む。

### macOS の証拠と be45（保存した API 応答で確かめた事実）

- `verification/u15-macos-native-38996219364/commit-ce0b7464.json`：sha `ce0b746497c662b2404a1f80153d53390d400e9d`、`verification.verified: true`、`reason: valid`（verified_at 2026-10-17T02:46:13Z）、親は `be45b36ce9d7a65719ba1f86cf6a0b018070741b` の 1 つ。変更ファイルは `.github/workflows/u12-native-first.yml`（modified、+1／−1）と `.github/workflows/u15-macos-native.yml`（added、+94）の 2 つだけ。
- `compare-be45-ce0b.json`：status `ahead`、ahead_by 1、behind_by 0、total_commits 1、merge base は be45。files は上と同じ 2 つだけ。
- これで、履歴の節「現行Step7補足 7a'」の限界にあった「API の応答原本は保存していない」は解消した。
- ただし **`u12-native-first.yml` の修正（ゲストビルドに `--advisory-policy u15-fixed-aube-zip9-name` を付ける 1 行）は branch `codex/u15-macos-native` の ce0b にしかなく、be45 の系列には入っていない**。be45 の `u12-native-first.yml` は古いビルドの行（`bash scripts/u10-build-guests.sh target/guests/u10`）のまま（compare の patch で確認）。be45 で dispatch した `u12-quality`（履歴「現行Step7補足」7a の run `38994430947`）は、この行のゲストビルドで失敗した。公開する最終 head では、この修正を取り込んで同じ head の証拠を新しく取る必要がある。取り込まないと、この macOS の証拠は作り直せない。
- macOS の証拠は Apple Silicon（arm64、host `aarch64-apple-darwin`）だけ。Intel の macOS は試していない。

### 正式検証

- 正式検証コマンドは、mise で入れた npm 12.2.0 のファイルを bytes まで封印して照合する。この npm-npm のディレクトリは 2026-10-17 12:03 JST ごろに環境から消え、正式検証は一度 exit 1 になった。人の選択「npm 12.2.0 を入れ直す」により mise で入れ直した後、封印された 6,792 ファイルはすべて一致し、最後の checkpoint で正式コマンドは exit 0（audit：CHECKPOINT_VERIFICATION_RECORDED、2026-10-17T03:13:00Z、Exit Code 0、Verified true）。封印 `history-seal.json` の `observed_immutable` は 6,792 件で、Step10 の読み取り専用照合ですべて存在し、row が 1 つずつで、現在の SHA-256 と bytes が記録値と一致した（不一致 0 件。うち npm-npm 12.2.0 の 563 件も不一致 0 件。`verification/step10-evidence-check.json` の `a_history_seal`）。これは照合時点の一致で、正式検証の再実行ではない。
- Step9 の後の正式検証は、このあと進行役が行う。

### 残る項目

- 公開段階：版の決定、tag、名前所有と初回 publish、Trusted Publisher と保護された release environment の設定（持ち主が設定する）、`u15-acceptance` producer の接続、実公開と公開後の registry 照合。FR10.1 と NFR8 はそれまで GAP。
- be45 の `u12-native-first.yml` は古いまま（上の「macOS の証拠と be45」）。公開 head への取り込みと同じ head での証拠の取り直しが必要。
- FR8.3 は再利用した旧測定。公開 head で新しい性能を主張するには、別の承認された測定が必要。

## 履歴：Step7補足 7a'：ネイティブmacOSの証拠（2026-10-17）（作成時の見出しは「現行Step7補足 7a'：ネイティブmacOSの証拠（2026-10-17） （履歴）」）

人が承認した 7a'（`verification/u12-workflow-fix-proposal.md`、`step7a2-summary-questions.md` で Looks correct）の結果。外部への操作は、be45 を親にした 1 commit の署名 push 1 回だけ（進行役が実施）。この節の照合は保存原本の読み取りだけで、push・CI 起動・ネットワーク・試験・エミュレータの実行・性能測定はしていない。製品・試験・metadata は変更していない。

### 送信した head と製品 source

- head `ce0b746497c662b2404a1f80153d53390d400e9d`（親 `be45b36ce9d7a65719ba1f86cf6a0b018070741b`）を branch `codex/u15-macos-native` へ送信。GitHub の verified=true（reason valid）と compare be45…ce0b（ahead_by 1、`modified .github/workflows/u12-native-first.yml` と `added .github/workflows/u15-macos-native.yml` の 2 ファイルだけ）は進行役が API で確かめた事実。照合スクリプトはその API 応答の原本を持たないため再確認はしておらず、代わりに手元の `jj --ignore-working-copy`（読み取り）で、親が be45 であること、変更が同じ 2 ファイルだけであることを確かめた。
- ce0b は be45 と **workflow 2 ファイルだけが違う**。製品 source・試験・スクリプト・lock は be45 と同じなので、**この macOS の結果は be45 の製品 source に当てはまる**。
  - `u12-native-first.yml` の差は 49 行目の 1 行だけ：`bash scripts/u10-build-guests.sh target/guests/u10` → `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name`。be45 の `scripts/u10-build-guests.sh` は `python3 tests/guests/u10/build.py <dir>` を呼ぶだけなので、違いは advisory policy の指定（U14 品質と同じ）と python/python3 の名前。ゲストのビルド手順で、製品 source ではない。
  - `u15-macos-native.yml` は `push: branches: [codex/u15-macos-native]` だけで起動し、`permissions: contents: read`。`u12-oracle` の呼び出しと `macos-host` job は be45 の `u12-quality.yml` の該当部分と文字列として同じ（steps 無変更。`macos-host` は u12-quality にある `U1_PACKAGES` を使っていない）。
  - CI が記録した lock 入力（`Cargo.lock` `7d6e3daf…`、`fuzz/Cargo.lock` `975f8538…`、`rust-toolchain.toml` `44aa4c6a…`、`tests/guests/u10/source-lock.json` `97a64e53…`）は be45 の bytes と一致。
- 作業コピーは送信後に戻した：`u12-native-first.yml` は be45 と同じ `3ecaaa72…`、`u15-macos-native.yml` は存在しない（照合スクリプトで確認）。

### run と原本

- push で起動した run `38996219364`「U15 native macOS evidence」（`.github/workflows/u15-macos-native.yml`、event push、attempt 1）：head ce0b、completed/**success**。
  - job `117289254101` `u12-oracle / native-first`（ubuntu-latest）success。ゲストビルド・native 14 ケース・lock 不変の各 step が success、native・original・build の exit はすべて 0。
  - job `117290641871` `macos-host`（macos-latest）success。全 step success。
- 原本：`verification/u15-macos-native-38996219364/`（run.json、jobs.json、artifacts.json、2 job のログ、artifact ZIP 2 件）。
  - `u12-native-first` `12087885679`：保存 ZIP の SHA-256 `ca64045f…` が公式 digest と一致、14,274,551 bytes、workflow_run の head は ce0b。
  - `u12-macos-host` `12087297829`：保存 ZIP の SHA-256 `616028b0…` が公式 digest と一致、115,084 bytes、workflow_run の head は ce0b。
  - macos-host のログに「downloaded artifact の digest `ca64045f…`」と「uploaded artifact の digest `616028b0…`」があり、macOS の比較が保存した native 期待値の ZIP を使ったことを結びつけた。
- 照合：読み取り専用の `verification/step7a2_macos_binding.py`（Python 3.15.0 標準ライブラリ、引数なし、ZIP はメモリ上で読む、SHA256 `803ded79c1ebc92643ba588491511923666fd20012460d93186b1939e6f85d7d`）を 1 回実行。exit 0、`failed_checks` は空。結果は排他作成の `verification/step7a2-macos-binding.json`（SHA256 `ea784789188762bf452ed6ef1cc11f9e38fdd015fd1176e9b5669241139b48b7`）。

### macOS の結果（ケースごと、スクリプトが自分で比較）

harness の判定は使わず、各ケースで終了コード・stdout・stderr をネイティブ Linux の期待値（同じ run の `u12/native/observations.json`）と比べた。正規化は ANSI 色、fixture の root（ネイティブ側の `fixture_root`／`fixture_root/fixture/app` と、エミュレータ側の独立した語の `/`）、経過時間（`in <n>ms|s`）だけ。

| ケース | 終了コード（native／macOS） | stdout | stderr |
|---|---|---|---|
| probe-tokio-timer・unix-stream-pair・rayon・mutex-condvar・fs-basic・fs-hardlink・fs-symlink・fs-flock（8 件） | 各 0／0 | 各一致（`PASS <項目>`） | 各一致（空） |
| probe-all | 0／0 | 一致（8 項目すべて PASS） | 一致 |
| probe-environment | 0／0 | 一致（`PASS node-absent ENOENT`） | 一致 |
| aube version | 0／0 | 一致（`2.6.1 linux-x64 (2026-10-17)`） | 一致 |
| aube install | 0／0 | 一致 | 一致（`+ filedep@1.0.0`、`+ linked@2.0.0`） |
| aube install --frozen-lockfile | 0／0 | 一致 | 一致（`+ filedep@0.0.0`、`+ linked@0.0.0`） |
| aube list | 0／0 | 一致（`filedep 0.0.0`、`linked 0.0.0`） | 一致 |

- **FR6.3（probe 全 8 項目 PASS）：PASS**。ネイティブと macOS の両方で 8 項目と probe-all が PASS し、3 つの出力がすべて一致。
- **FR7.2（aube 4 コマンドがネイティブと同じ）：PASS**。4 コマンドとも stdout と終了コードが一致し、stderr も一致（比較は `--reporter=append-only` 付きの引数）。元の引数（`comparison-original`）でも 4 コマンドの stdout・終了コード・stderr が正規化後に一致した（補足）。
- **FR7.3（#1645 の 0.0.0 再現）：PASS**。ネイティブと macOS の両方で frozen install が `filedep@0.0.0`・`linked@0.0.0`、`aube list` が `filedep 0.0.0`・`linked 0.0.0` を出し、一致。
- 補足（判定には使っていない）：既定 VFS の 2 ケース（version、install）は macOS で終了コード 0。harness のログの合格行「U12 native host: fourteen Linux comparisons and two default VFS cases passed」が 2 回（append-only と元の引数）ある。

### 付随する記録

- compiler.txt：macOS は `rustc 1.101.0-nightly (6f5da406b 2026-10-10)`、host `aarch64-apple-darwin`（runner は Apple Silicon の macOS）。ネイティブ Linux 側は同じ版で host `x86_64-unknown-linux-gnu`。
- inputs-before／after：macOS（Cargo.lock・fuzz/Cargo.lock・rust-toolchain.toml）、native（加えて source-lock.json）とも前後一致。
- coverage-scope.json：native Host 6 ファイル（clock・fs・lib・macos・native_fs・threads）で 970/1068 行＝**90.82%**（80% 以上）。比較 harness の Python 3 ファイルは 107/109＝98.17%。
- ゲスト binary：probe `0e8a3188…`、aube `69d2e5a9…`。期待値・macOS 結果・ZIP 内の bytes が一致。ゲストは CI のたびにビルドするため、be45 の他の run の aube（Windows `22f5444c…`、wasm `b5c85689…`）とは bytes が違う。比較は同じ run の期待値とだけ行った。

### 限界

- この run は性能を測っていない。FR8.3 については何も加えない。
- 結果は ce0b での実行で、be45 そのものでの run ではない。be45 に当てはめる根拠は「違いが workflow 2 ファイルだけ」という読み取り確認。
- GitHub の verified と compare の応答原本は保存しておらず、進行役の確認を記録しているだけ。
- macOS の runner は arm64 の 1 種類だけ。Intel の macOS は試していない。

### Step7 全体の状態（この節の時点）

| 要件 | Linux | macOS | Windows | Node | Chromium | Firefox | Safari | 判定 |
|---|---|---|---|---|---|---|---|---|
| FR6.3 | PASS | **PASS（この節）** | PASS | PASS | PASS | PASS | PASS | PASS |
| FR7.2 | PASS | **PASS（この節）** | PASS | PASS | PASS | PASS | PASS | PASS |
| FR7.3 | PASS | **PASS（この節）** | PASS | PASS | PASS | PASS | PASS | PASS |
| FR8.2 | 対象外 | 対象外 | 対象外 | PASS | PASS | PASS | PASS | PASS（wasm 4 環境） |

- Linux・Windows・wasm 4 環境の値は `verification/step7-acceptance-binding.json`（be45 の保存原本）。macOS は上の照合。
- FR8.3：`verification/step7b-fr83-closure-02.json` で **旧測定（208fd965、run 38840433942）に BOUND**。再利用した測定で、新しい測定ではない。3 入力の「runner の結果は同じ」という判断は独立レビューで確かめる必要がある。
- u15-acceptance producer：公開段階（FR10.1）に回す（計画の Step7補足どおり）。FR10.1 は GAP のまま。
- Step7 の checkbox：FR6.3・FR7.2・FR7.3 が FR5 の 7 環境すべてで PASS、FR8.2 が wasm 4 環境で PASS、FR8.3 の結果を記録したため、**付けた**。正式 sensor、独立レビュー（FR8.3 の判断を含む）、採用済み正式コマンドでの checkpoint 検証、人の完了承認はこの後に進行役が行う。

## 履歴：Step7補足：macOS dispatch の結果と FR8.3 の closure 照合（2026-10-17）（作成時の見出しは「現行Step7補足：macOS dispatch の結果と FR8.3 の closure 照合（2026-10-17） （履歴）」）

人が承認した計画の「Step7補足」7a・7b の結果。7a で外部へ行った操作は承認済みの dispatch 1 回だけで、再実行・push・workflow の変更・性能測定はしていない。7b は新しい測定をしていない。製品・試験・workflow・metadata は変更していない。

### 7a：ネイティブ macOS（FR6.3・FR7.2・FR7.3）— 失敗、GAP のまま

（→ 冒頭の「現行Step7補足 7a'」で、ネイティブ macOS の FR6.3・FR7.2・FR7.3 は PASS に置き換えた。次の記述は当時のもの）

- 起動：`gh workflow run u12-quality.yml --repo Marukome0743/paludarium --ref codex/u14-jit-wasm`（1 回）。run `38994430947`、head `be45b36ce9d7a65719ba1f86cf6a0b018070741b`、event `workflow_dispatch`、conclusion **failure**。
- 原本：`verification/u12-quality-38994430947/`（run.json、jobs.json、artifacts.json、失敗 7 job のログ）。説明と SHA-256 は同じフォルダの `README.md`。
- 26 job のうち failure 7、skipped 3、success 16。
  - failure：`u12-oracle / native-first` 117283723586、`u11-programs / build-oracle` 117283723440、U10 `native-first` 117283723628、単体試験 ubuntu 117283723599・macos 117283723553・windows 117283723538、`line coverage >= 80%` 117283723508。
  - skipped：`macos-host` 117284079494（`u12-oracle` の失敗による）、`u11-programs / differential`、U10 `differential`。
  - success：lint、dependencies、x86-64 Linux 差分、production wasm、U10 fixture-metadata-oracle、u12-fuzz 11 件（jobs.json 上の fuzz target は 11 件）。
- 原因 1（ゲストのビルド）：`scripts/u10-build-guests.sh` が `tests/guests/u10/build.py` を `--advisory-policy` なしで呼ぶため、aube の `cargo deny ... aube-deny.toml --locked check` が exit 1（`job-117283723586.log` 1155〜1156 行。build-oracle は 949〜950 行、U10 native-first は 951〜952 行）。be45 の U14 品質は `--advisory-policy u15-fixed-aube-zip9-name` を付けている（`u14-native-first.yml` 53 行、`u14-wasm-acceptance.yml` 27 行）が、`u12-native-first.yml` 49 行・`u11-acceptance.yml` 24 行・`u10-native-diagnostic.yml` 41 行は付けていない。deny が挙げた advisory の中身は artifact 内のログにあり、未確認。
- 原因 2（単体試験）：3 OS とも `paludarium-jit` の実 Wasm bridge 試験 9 件が `crates/paludarium-jit/src/bridge.rs` 680 行で panic（「PALUDARIUM_TEST_NODE must name actual current Node executable」、`job-117283723599.log` 946〜947 行、結果 `48 passed; 9 failed` 1289 行）。u14-quality.yml は workflow の `env` に `PALUDARIUM_TEST_NODE: node`（21 行）を持つが、u12-quality.yml の `env` は `CARGO_TERM_COLOR` だけ。
- coverage job：同じ環境変数の不足で `crates/paludarium-harness/tests/diff_u14.rs` 20 行が「actual Node executable: NotPresent」で panic し、`cargo test` が exit 101（`job-117283723508.log` 876〜877 行、908〜910 行）。coverage の割合は出ていない。
- 関係する workflow・スクリプト・試験 11 ファイルの現在の bytes は、`verification/signed-source-1792152592092090000.json` の be45 の値と一致することを読み取りで確かめた。
- 判定：`macos-host` が動かず、ネイティブ macOS の観測がない。**FR6.3・FR7.2・FR7.3 のネイティブ macOS は GAP のまま**。計画どおり再実行はしていない。直すには workflow の変更（advisory policy の指定と `PALUDARIUM_TEST_NODE`）と新しい署名 head が必要で、人への別の案として扱う。
- 未確認：artifact の ZIP 本体は保存していないため、ZIP の digest の照合はしていない（artifacts.json の公式 digest 18 件だけを保存）。

### 7b：FR8.3 — 旧測定を be45 に結びつけた（再利用した測定）

- 最初の照合 `verification/step7b-fr83-closure.json`（`step7b_fr83_closure.py`、SHA256 `1b2bba66…`）は GAP だった。原因は照合スクリプトの不具合で、`new URL("coordinator.mjs", import.meta.url)` の literal を bare specifier と誤って分類し、Worker から読む `coordinator.mjs`・`execution.mjs` が closure から抜けた。この結果は原本として変更せずに残す。
- 修正版 `verification/step7b-fr83-closure-02.json`（`step7b_fr83_closure_02.py`、SHA256 `6b32f4e5…`）が最初の結果を置き換える。exit 0、`failed_checks` は空、`fr83_binding: BOUND_TO_OLD_MEASUREMENT`。runner が読む入力（JS 10 ファイル、通常 Wasm module、probe、oracle の使う部分、runner の引数、workflow の差分 job・見出し・呼び出し元、Node の版、seed・順序・warmup）はすべて一致した。
- bytes は違うが runner の結果は同じと機械的に確かめた入力（`raw_differs_but_runner_effect_equal`）が 3 つある：
  - `oracle.fixture_root`（実行ごとに変わる一時ディレクトリ名。正規化後の期待 stdout・stderr の hash が一致）
  - workflow の build-oracle job（差は advisory policy の 1 行 `u14-fixed-aube` → `u15-fixed-aube-zip9-name` だけ。その出力の module・probe・oracle は直接比較して一致）
  - `packages/paludarium-wasm/package.json`（`repository` と `publishConfig` の追加だけで、Node が読む欄は同じ）
- 結びつけた測定は**再利用した測定で、新しい測定ではない**：head 208fd965、run `38840433942`、インタプリタ平均 5.856590694899998 秒、JIT 平均 5.696370400100001 秒、改善 2.7357263491%、片側 p = 7/1024（0.0068359375）。
- この結びつけは、上の 3 入力の「runner の結果は同じ」という機械的な判断に依っている。この判断は独立レビューで確かめる必要がある。

### この節の後の状態

- Step7 の checkbox は付けない（7a が失敗し、FR6.3・FR7.2・FR7.3 のネイティブ macOS が GAP のため）。（→ 冒頭の「現行Step7補足 7a'」で macOS が PASS になり、Step7 の checkbox を付けた）
- 下の「現行Step7」節の FR8.3 の判定（GAP）は、この節の 7b で置き換えた。ネイティブ macOS の GAP はこの節でも変わらない。

## 履歴：Step7：公開前受理条件のローカル照合（2026-10-17）（作成時の見出しは「現行Step7：公開前受理条件のローカル照合（2026-10-17） （履歴）」）

人の選択「ローカル照合で Step7」（`step7-local-summary-questions.md`、Looks correct）に基づく。保存済みの原本を読んで照合しただけで、push、CI の起動、ネットワーク、試験・エミュレータ・ブラウザ・probe・aube の実行、新しい性能測定、公開、tag、registry 操作は行っていない。製品・試験・workflow・metadata・他 Unit のファイルは変更していない。

### 照合の方法

- 読み取り専用の照合スクリプト `verification/step7_acceptance_binding.py`（Python 3.15.0 標準ライブラリだけ、引数なし、ZIP はメモリ上で読む）を 1 回実行した。exit 0、`failed_checks` は空。結果は排他作成の `verification/step7-acceptance-binding.json`（SHA256 `515cc804625597fc816dc1ca992c71e45684b462048a3147161abfdebd58aa9d`）に 1 回だけ書いた。スクリプトの SHA256 は `e574a2976d4c1bfea29b2c5a70a56ee613990feefccb52e5c884f93005c2a7b6`。
- 原本の真正性：全品質 run `38897611874` と専用 native run `38897611887` について、run・34 job／2 job が head be45b36c で completed/success、job ログが全 job 分あり、artifact 32 件／2 件すべてで保存 ZIP の SHA256 が公式 digest と一致し、サイズ一致・未失効・同じ run と head であることを確かめた。
- 環境ごとに、job ログにある「download した artifact の digest」と「upload した artifact の digest」で、job・期待値・結果の artifact を結びつけた。比較は harness の判定をそのまま使わず、スクリプトが自分で行った（終了コード・stdout・stderr。正規化は ANSI 色、fixture の root パス、経過時間だけ。ネイティブ実行系の root `/` は独立した語の `/` だけを置き換える。harness より厳しい）。
- FR5 の環境は requirements.md の FR5.1〜5.3 から読んだ：ネイティブの Linux・macOS・Windows、wasm の Node.js Worker・Chromium 系・Firefox・Safari（7 環境）。

### FR5 の環境ごとの結果

| 環境 | FR6.3 probe 全項目 PASS | FR7.2 aube 4 コマンド | FR7.3 #1645 再現 | FR8.2 JIT あり・なし | 証拠（job／artifact） |
|---|---|---|---|---|---|
| ネイティブ Linux | PASS | PASS | PASS | 対象外 | job `116965577321`／`u10-differential` `12044628027`（`sha256:5fba4b5d…`）。結果 `observations.json` `1dc7ab68…`、同じ job で新しく得た期待値 `native/observations.json` `d368510d…`。元の引数での比較（stdout・終了コード）も一致 |
| ネイティブ macOS | **GAP**（→ 7a' で PASS） | **GAP**（→ 7a' で PASS） | **GAP**（→ 7a' で PASS） | 対象外 | 2 つの run の原本に、macOS のネイティブホストで probe・aube を期待値と比べた job・artifact がない。macOS の job は Rust 単体試験 `116962253307` と Safari（wasm）`116965093505` だけ。推定しない（→ 冒頭の「現行Step7補足 7a'」で run `38996219364` の原本により PASS に置き換え） |
| ネイティブ Windows | PASS | PASS | PASS | 対象外 | job `116964624066`（windows-latest）／`u13-windows-host` `12044404207`（`sha256:5fad42b3…`）。`windows/comparison/observations.json` `ce678542…`。期待値は同じ run の `u13-native-first` `12044459100`（`sha256:bed566b8…`）の `u13/native/observations.json` `61cd5154…`（ゲスト bytes probe `0e8a3188…`・aube `22f5444c…` と一致）。元の引数での比較も一致 |
| Node.js Worker | PASS | PASS | PASS | PASS | job `116965093681`／`u11-node` `12045491019`（`sha256:43e3ba92…`）、`observations.json` `6d6404f5…`。Node `v26.12.0` |
| Chromium | PASS | PASS | PASS | PASS | job `116965093652`／`u11-chromium` `12045287007`（`sha256:abc406e6…`）、`observations.json` `a25513e4…`。版 156.0.8078.4 |
| Firefox | PASS | PASS | PASS | PASS | job `116965093521`／`u11-firefox` `12045585533`（`sha256:75957b9e…`）、`observations.json` `f5b221e1…`。版 157.0 |
| Safari（本物、macOS runner） | PASS | PASS | PASS | PASS | job `116965093505`（macos-latest、「Enable actual Safari on CI runner」success）／`u11-safari` `12045122242`（`sha256:eff7ab8b…`）、`observations.json` `4289ba7f…`。版 26.6.2 |

- wasm 4 環境の共通入力：`u11-acceptance-inputs` `12044986847`（`sha256:abd26c7b…`）。期待値 `target/u11/native/observations.json` `511d104a…`（receipt `3a6dba5c…` が同じ値を指す）、通常 Wasm module `fb2fdb51…`、probe `f09911e4…`、aube `b5c85689…`。各環境の結果に記録された module・期待値・ゲストの hash がこれらと一致した。
- FR7.2：4 コマンドとも全環境で stdout と終了コードがネイティブと一致した。stderr も全環境で一致した（比較は `--reporter=append-only` を付けた引数。元の引数での比較はネイティブ Linux と Windows で stdout・終了コードが一致）。
- FR7.3：ネイティブと各環境の両方で、frozen install の報告が `filedep@0.0.0`・`linked@0.0.0`、`aube list` が `filedep 0.0.0`・`linked 0.0.0` を出し、ネイティブと一致した。
- FR8.2：wasm 4 環境で、JIT ありの 14 件がネイティブと一致し、JIT なし（インタプリタ）と終了コード・stdout・stderr がすべて同じだった。probe の全行で JIT が実際に block を実行していた（例：probe-all の executedBlocks は Node 10246、Chromium 12682、Firefox 18147、Safari 3911）。JIT は wasm 向けだけ（FR8.1）で、ネイティブの JIT は範囲外のため、wasm 4 環境で判定した。
- 補足（判定には使っていない）：専用 native run `38897611887` の `u13-native-first` `12044926703`（`sha256:91b82b31…`）の期待値 `u13/native/observations.json` `2993740b…` は、全品質 run の Windows 比較に使った期待値と 14 行とも結果が一致した。ただしゲストの binary hash は一致しない（別のビルド）。

### 結論（FR6.3・FR7.2・FR7.3・FR8.2）

- FR8.2 は wasm 4 環境すべてで成り立つ（be45 の保存原本で確認）。
- FR6.3・FR7.2・FR7.3 は、7 環境のうち 6 環境で成り立つが、**ネイティブ macOS の証拠がないため GAP**。（→ 冒頭の「現行Step7補足」7a で u12-quality を dispatch したが失敗し、GAP のまま。→ その後、冒頭の「現行Step7補足 7a'」で macOS も PASS になり、7 環境すべてで成り立つ）macOS のネイティブホストでの照合は、u12 系 workflow（`u12-native-first.yml` など）を be45 または後の head で実行して原本を得る必要があり、今回の範囲（push・CI 起動なし）の外。

### FR8.3：旧正式性能を be45 に結びつけられるか

旧測定（再利用の候補であり新しい測定ではない）：head 208fd965、手動 run `38840433942`、Node job `116781223162`、インタプリタ平均 5.856590694899998 秒、JIT 平均 5.696370400100001 秒、片側 p = 7/1024（0.0068359375）、seed 5321、warmup 各 1、10 対。原本は U14 `jit-u9-next/formal-analysis-208fd965-01/` と `formal-ci-38840433942/`。

| 入力 | 旧測定（208fd965） | be45 | 一致 |
|---|---|---|---|
| 通常 Wasm module | `fb2fdb51…` | `fb2fdb51…` | 一致 |
| probe ゲスト | `f09911e4…` | `f09911e4…` | 一致 |
| 期待値（oracle） | `b18979f8…` | `511d104a…` | **不一致**（期待値は CI のたびに新しく作るため bytes が異なる） |
| `packages/paludarium-wasm/package.json` | `c3c0950d…` | `def04cf8…` | **不一致**（U15 の公開 metadata の変更） |
| runner と JS（u14-performance-check／u14-performance／u11-programs／u11-contract、index・worker-support・filesystem-snapshot・coordinator・execution・jit-support の各 .mjs） | — | — | 10 ファイルすべて一致 |
| Node の版 | v26.12.0 | v26.12.0（同じ job の受理比較 step。性能 step は skipped で観測なし） | 一致 |
| seed・順序・warmup | seed 5321、10 対の固定順、warmup 各 1 | 同じ（`u14-performance.mjs`・`u14-performance-check.mjs` の bytes 一致から） | 一致 |
| runner の引数 | `node packages/paludarium-wasm/tests/u14-performance-check.mjs packages/paludarium-wasm/paludarium.wasm target/u11/native/observations.json target/guests/u10 target/u11/node/performance` | 文字列は同じ（下の注） | 文字列は一致、呼び出し元 workflow の bytes は不一致 |

- 注：照合スクリプトは runner の引数を `u14-quality.yml` から探したが、実際の step は呼び出し先の `.github/workflows/u14-wasm-acceptance.yml` にあるため、結果 JSON では `runner_arguments.equal=false`（取り出せなかった）と記録されている。スクリプトの実行後に読み取りだけで追加確認した：`u14-wasm-acceptance.yml` は 208fd965 `27502387…`、be45 `64226429…`（現在のファイルも `64226429…`）で bytes が異なるが、be45 の「Frozen paired full-probe performance」step の `run:` 文字列は旧測定のログの命令と同じ。`u14-quality.yml` は両 head とも `e5a8f555…` で一致。この追加確認は結果 JSON には含まれない。
- （→ 冒頭の「現行Step7補足」7b で置き換え：修正した照合 `step7b-fr83-closure-02.json` で旧測定を be45 に結びつけた。次の記述は当時のもの）判定：**FR8.3 は GAP のまま**。期待値と package.json の bytes が異なり、性能 step を呼ぶ workflow の bytes も異なるため、旧測定を be45 に結びつけない。be45 では性能 step が skipped で、新しい性能の合格も主張しない。同じ module での合格待ちの再測定はしない（計画どおり）。

### u15-acceptance producer

- 公開段階に回す（FR10.1 と同じ GAP）。`u15-acceptance` は `scripts/release/check.py` と `tests/release/test_api.py` が参照するだけで、どの workflow も upload しない（照合スクリプトで `.github/workflows/*.yml` に該当 0 件を確認）。実公開（release.yml の publish 経路）でだけ読まれ、upstream aletheia-works/paludarium の公式 run、Trusted Publisher、保護された release environment、人の公開承認が前提になる。持ち主は、時期を知らされたときに Trusted Publisher と environment を設定する。不在を成功へ読み替えない。

### Step7 の状態

- Step7 の checkbox は付けない。FR6.3・FR7.2・FR7.3 がネイティブ macOS で GAP のため（FR8.3 の GAP と producer の公開段階送りは記録済み）。（→ FR8.3 は冒頭の「現行Step7補足」7b で旧測定に結びつけた。macOS の GAP は 7a の後も残る。→ 冒頭の「現行Step7補足 7a'」で macOS の GAP も解消し、checkbox を付けた）
- 下の「現行Steps7〜8」節のうち、専用 native run `38897611887` を「原本未保存・照合できなかった」とする記述と、「Step7で残る不足」の最初の 2 項目は、この節で置き換えた（原本は `verification/native-38897611887-20261017/` に保存済みで、真正性を照合済み）。

## 履歴：Steps7〜8：署名CIの結果と記録の完成（2026-10-17）（作成時の見出しは「現行Steps7〜8：署名CIの結果と記録の完成（2026-10-17） （履歴）」）

人の選択「記録を完成させる」（`step7-8-summary-questions.md`、Looks correct）に基づく記録の更新。今回は保存済み原本と現在のファイルを読んで照合しただけで、製品・試験・workflow・metadataの変更、push、CI実行、試験の再実行、公開、tag送信、registry操作は行っていない。照合は読み取り専用の `verification/step7-8-records-check.py`（Python 3.15.0、exit 0、出力はtool結果のみで保存なし）で行った。

### Steps1〜6の照合（検証済み）

- source-manifest.jsonの28 pathsはすべて現存し、現在のSHA256が `verification/publication-candidate.json` の28件、`verification/signed-source-1792152592092090000.json`（head `be45b36ce9d7a65719ba1f86cf6a0b018070741b`、888行）の該当28行とすべて一致した（28/28、28/28）。manifestとcandidateのpath集合も一致。
- 888行全体では847行が現在と一致し、41行が相違した。相違はすべてU15の28 paths外で、AI-DLCの記録（aidlc-state.md、audit、U1/U2/U4/U7の記録、memory、intents.json、verification-command.txt）、`.gitignore`、`AGENTS.md`、`mise.toml`、他Unitの診断workflow 5件（u1-r04-current-verification、u4-current-sanitizers、u7-current-verification、u7-r04-native-first、u7-r04-verification）。be45送信後の別作業による差であり、be45のCI結果を現在の作業コピー全体の合格とは呼ばない。U15の28 pathsについてはbe45のCIが現在のbytesを対象にしている。
- 単体・統合の保存原本 `verification/final-unit-71-1792148706406974000`：exit 0、timeout false、stdout/stderrのSHA256がreceiptと一致、`Ran 71 tests`/`OK`。内訳はpolicy 21、package 16、check 15、API 11、publish adapter 4、統合4（各部品8件以上、統合4件の計画どおり）。
- package-checkの保存原本 `verification/final-package-1792148710031913000`：exit 0、36.423秒、timeout false、stderr空、streamsのSHA256一致。11 crateの配布物と、同じnpm tarの7境界（provenance、相対import、import、hello、invalid、missing JS拒否、corrupt Wasm拒否）を含む。
- 試験とpackage-checkの再実行は行っていない（保存原本の照合のみ）。

### Step7：be45の署名CI（保存原本で検証済みの範囲）

- 全品質 run `38897611874`（U14 current full quality、push、attempt 1）：head be45b36c、completed/success。保存原本 `verification/full-quality-1792153236541522000/` の jobs.json で34 jobすべてsuccess（3OS単体、lint、dependencies＝`cargo deny --locked check`、80% coverage、x86-64 Linux差分、production wasm、windows-host、jit-coverage、u14-python-coverage、U10 native-first/差分、u13-oracle、u13-fuzz 13件、u11-programs のNode/Chromium/Firefox/Safari差分）。job log 34件のIDはjobs.jsonと一致。artifact catalog 32件はすべてbe45発行・未失効で、保存ZIP 32件の全bytes SHA256とサイズがinventory.jsonと一致。
- 正式性能：u11-programs の4 job（Safari、Firefox、Chromium、Node）の `Frozen paired full-probe performance` stepはすべて skipped。新しい性能測定は行われておらず、性能の合格をbe45へ主張しない。旧性能の再利用判断は保留のまま（`final-quality-capture-01.md`）。
- release-check run `38897653085`（Release package checks、`.github/workflows/release-check.yml`、workflow_dispatch）：head be45b36c、completed/success。job `packages` の全stepがsuccess：固定ツール準備、release単体＋mock統合（ログ上 `Ran 71 tests`）、静的設定、実11 crate＋隔離registry＋同じnpm tarball、固定3部品の各80%、artifact upload。公開・tag・OIDCのstepはなく、release-check.ymlに `cargo publish`／`npm publish`／`id-token` はない。`verification.json` は passed true、actual_publication false、new_performance_measurement false。保存ZIP `u15-package.zip` のSHA256一致、51 members。CIのtoolchainは `nightly-2026-10-11`（rustc 1.101.0-nightly 6f5da406b）、package結果は `stable_supported: false`、`published: false`。
- CIでの固定3部品のline coverage：policy 80/80＝100%、package 177/180＝98.333%、check 187/194＝96.392%（除外0）。ローカル値と同じで、各80%以上。
- U1 run `38897611994`（U1 U14 current-source evidence）：head be45b36c、completed/success、7 job（3OS単体、lint、dependencies、80% coverage、差分）すべてsuccess。原本はU1側の `construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/be45-ci-completion-1792153024044351000/`（読み取りのみ。U1の記録は変更していない）。
- （→ 上の「現行Step7：公開前受理条件のローカル照合」で原本保存・照合済み。次の記述は当時のもの）専用native run `38897611887`：completed/successという記述は `verification/name-repair-publication-result-01.md` の追記にあるだけで、run.json・jobs.jsonなどの原本はU15にもU1にも保存されていない。今回は照合できなかった。全品質runのnative系job（U10 native-first、u13-oracle）はsuccessを原本で確認したが、専用runの代わりとはしない。

### Step7で残る不足（Step7のcheckboxは未完了のまま）

- （→ 上の「現行Step7」節で解消）専用native run `38897611887` の原本保存と照合（ネットワーク取得が必要。今回の作業範囲外）。
- （→ 上の「現行Step7」節で照合結果と公開段階送りを記録）FR6.3/7.2/7.3/8.2/8.3 の公開前受理条件を最終sourceへ結合する `u15-acceptance` artifactのproducerは、`scripts/release/check.py` と `tests/release/test_api.py` が参照するだけで、どのworkflowにも接続されていない。旧性能の再利用判断も保留のまま。不在を成功へ読み替えない。
- R-05・R-11の指摘解消と新しい正式コマンドの採用は、別途の検証と人の承認が必要（`final-quality-capture-01.md`）。

### Step8：記録の更新（この節）

- 本節の追加、下の「未実行の検証・残る不足」への注記、traceability.jsonのnotes更新を行った。source-manifest.jsonの28 pathsは正しいため変更していない。
- 状態の変更はNFR9のGAP→OKのみ（traceability.json参照）。根拠：`rust-toolchain.toml` の `nightly-2026-10-11` を、ローカル（`verification/local-module-comparison.json`）とbe45のCI（release-checkと全品質run）がともに rustc 1.101.0-nightly 6f5da406b として使用した。stableで使えないこと（MSRV 1.101要求でexit 101）は記録どおりで、stable対応とは主張しない。
- FR10.1はGAPのまま：実公開、tag、Trusted Publisher、release environmentの設定はいずれも未実施。NFR8もGAPのまま（registry・OIDC・provenanceの実照合は実公開なしでは示せない）。
- 正式sensor、独立レビュー、採用済み正式コマンドでのcheckpoint検証、人の完了承認は、この記録の後に進行役が行う。Step8のcheckboxは記録部分の完了を示すだけで、レビューや承認の完了を意味しない。

## 作成・変更ファイル

Application source 28 pathsをsource-manifest.jsonとverification/publication-candidate.jsonに固定した。3つのrelease部品、7つの試験ファイル、2つのworkflow、公開metadata15ファイル、docs/release.mdが対象。変更前の物理357ファイルをverification/before-u15.zipに保存した。これはjj208の全内容と同じという主張ではない。親が署名済みbaseと限定比較して送信する。

## 実装判断

policyは11公開crateの依存DAG・版・registry、署名head、main到達性、実environmentと人の承認、同headの品質証拠を検査する。継承されたworkspace依存も解決後にgit/custom registryを拒否する。HarnessとRust Wasm adapterは非公開。0.0.0は公開版として拒否する。

packageはproject内の隔離コピーとloopback sparse registryを使い、実11crateとcrate外consumer、通常Wasm、同一npm tarの7境界を検査する。checkは実argv/tool/compiler/選択された非秘密環境・raw streams/exit/timeout/cleanupと前後hashを保存する。Cargo publishの再組立は承認済みcrate digestとの一致が必要で、未知のregistry結果や部分公開を自動retryしない。

release-checkは非公開検査のみ。releaseは実設定された保護environmentをpreflightで検査し、publish jobだけOIDC権限を持つ。新actionは公式latest tagから解決したSHAへ固定。upstream以外へ公開先を置換しない。

## 実行済み試験とcoverage

検証済み：実装後に単体policy21/package16/check15、API11、publish adapter4、統合4、合計71件が成功。mockは公開/OIDCの実証ではない。最終原本はverification/final-unit-71-1792148706406974000。

検証済み：最終package-checkは36.423秒/exit0/timeout false/stderr空。verification/final-package-1792148710031913000、target/u15/package-result-final.json、target/u15/package-1792148710531463000に原本を保持。実11crate、隔離registry経由nightly consumer、production Wasm、同じtarのprovenance/relative import/import/hello/invalid cleanup/missing JS/corrupt Wasmの7件が成功。source/locks前後不変。local source digest47d83a896dca86c04dbc62ab44995f969edd205c4bfb912931bf92ebda2f9525を使用し、未送信のlocal buildをCI実行と呼ばない。

固定3ファイルのline coverageはpolicy80/80=100%、package177/180=98.333%、check187/194=96.392%。target/u15/python-coverage-final.json。各80%を維持し、除外0。actionlint1.7.12 -shellcheck=で両workflowの構文検査exit0（shellcheck実行ではない）。

## 初回失敗・制約

初回のuv cache権限不足、missing tool receipt、consumer workspace指定不足、共有Cargo cache権限不足、段階実装中の未完packageを別原本として保持。stable1.99.0の初回失敗を保持し、最新1.99.1でも実probe exit101：全11crateのMSRV1.101要求。stable対応とは主張しない。最終stable receiptのRUSTUP_TOOLCHAIN表示は旧1.99.0だが、実cargo/RUSTC/RUSTDOCは1.99.1の絶対path/SHAでありstderrもrustc1.99.1を確認している。

verification/freeze.py初回はbootstrap済みの空__init__.pyを変更必須と誤判定して拒否し、未生成のまま修復した。最終manifestには同bytesのbootstrap pathも所有として含む。

## 未実行の検証・残る不足

> 2026-10-17 注記：この節はbe45の署名CIより前に書いた内容で、原文のまま残す。「新署名CI…は未実行」と、NFR9の「新CI未実行」は、冒頭の「現行Steps7〜8：署名CIの結果と記録の完成（2026-10-17）」で置き換えた（全品質 `38897611874`、release-check `38897653085`、U1 `38897611994` はsuccessを原本で確認。専用native `38897611887` は原本未保存。→ その後、冒頭の「現行Step7」節で原本保存・照合済み）。u15-acceptance producerの未接続、release environment未設定、名前所有・初回publish・Trusted Publisher・公開版・tag・実公開の未実施、FR10.1とNFR8のGAPは、今も有効。

新署名CIと全既存品質/source-bound原本の照合は未実行。Step7は未完。最終sourceのFR6.3/7.2/7.3/8.2/8.3受理証拠を出すu15-acceptance producerは最終canonicalレビュー/採用後の接続が必要であり、不在を成功へ変えない。旧正式性能の同一binary再測定は行わない。

upstream/forkともrelease environmentは未設定、現在のaccountはupstream admin/push権限なし。名前所有、初回publish、Trusted Publisher、正確な公開版、tagと実公開は未承認/未実施。FR10.1はGAP、NFR8/9も新CI未実行範囲をGAPとして残す。公開認可をこの計画承認から推定しない。旧U1–U14記録/canonical/bindingと全失敗は変更していない。
