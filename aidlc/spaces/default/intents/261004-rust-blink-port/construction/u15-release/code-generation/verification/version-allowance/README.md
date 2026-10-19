# 版の行と旧 chain の固定を許す確認の入口（U15）

> 2026-10-18 追記：v4 の次は層を重ねず、e3c29d1d を起点にした新しい入口（`../entry-e3c29d1d/entry-c.py`）に移った。人がそれを正式な確認コマンドとして採用したので、このフォルダの v1〜v4 は履歴である。新しい入口は、ここの入口・binding・回帰の 12 ファイルの bytes だけを固定し、実行しない。下の「未採用」「採用済み」の見出しは、それぞれを書いた時点のもの。

## v4（未採用）：`u15_candidate_v4.py`（binding-11）

2026-10-18 JST。承認済みの計画 Step 18：「新しいheadに合わせて確認コマンドの入口を更新し、そのときに入口v3のMinor 4件（`verification/version-allowance/pending-minor-fixes.md`）も直す。回帰と独立レビューの後、検証コマンドとしての採用を人に伺う。」

- この入口は**採用されていません**。独立レビューと、人による採用の承認が残っています。`verification-command.txt` は変えていません。
- commit・push・CI の起動・再実行・性能の測定はしていません。GitHub へは読み取りの GET（と artifact の ZIP の GET）だけを使いました。
- **本番の実行：exit 0**（下の「v4 の実行結果」）。

### コマンド行

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate_v4.py --entry-sha256 dfb0e03ae09c51ee3454c367dc7c1f072e6e1428f75f97a371555bb2143df5d0 --binding-sha256 fb466da7e8f7dadff7efb3645ee5e4f4a95c0eb867207be875387879cf6caca4
```

| ファイル | SHA-256 |
|---|---|
| 入口 `u15_candidate_v4.py` | `dfb0e03ae09c51ee3454c367dc7c1f072e6e1428f75f97a371555bb2143df5d0` |
| `binding-11.json`（入口の定数とも一致を要求） | `fb466da7e8f7dadff7efb3645ee5e4f4a95c0eb867207be875387879cf6caca4` |
| 回帰 `test_u15_candidate_v4.py`（163 件） | `4a225e0a72b00bf05a500853e76a93dff6ad101a6c15e061b31e909f70682bd4` |
| `ci-e3c29d1d.json`（binding-11 が固定） | `7f03c90352b2e926c4beb4764818d7c880844f4cdc433f6b7e0821d86be09eeb` |
| `ci-jobs-e3c29d1d.json`（binding-11 が固定） | `93380dd27715de3ec3f1f4720b0615a1d7e965bfecb9c034992755d0cdc522d1` |
| 性能の原本 `../ci-e3c29d1d/u14-quality-39114108809/u11-node/performance/observations.json` | `1abc62ff35bcffd3167e6a7de968abcb40ada4a7f5b8afdef4eb66646e03ff45` |
| artifact `u11-node`（id 12131882922）の ZIP `../ci-e3c29d1d/u14-quality-39114108809/artifact-zip/u11-node-12131882922.zip` | `606c3323f7ab72a8e070584ef20c8c78a515ef2a2d0b55fcf09b8da06b949415`（API の digest と同じ、1,332,216 bytes） |

### CI の記録（e3c29d1d）

「CI の記録の作り方」と同じく、読み取りの GET（runs・`attempts/N`・`attempts/N/jobs`・`actions/jobs/117638480843`・commits・compare `a54315f9...e3c29d1d`・branch・`runs?head_sha=`）の出力を file-write の道具で写し、同じ GET の結果と Python で比べて 24 項目（branch、commit 2、compare、run の一覧、run 7、最新の attempt の job 一覧 7、U12 の attempt 1 の job 一覧、失敗の step と job 名、保存済みの attempt 1 の原本 `../ci-e3c29d1d/u12-quality-39114110570/attempt-1/` の run.json・jobs.json）がすべて一致することを確かめました。

- 7 run：CI 39114018191、Release package checks 39114018143、U14 current full quality 39114108809（34 job）、U12 current full quality 39114110570、U13 current full quality 39114112207、U14 fresh thirteen target ASan and LSan 39114114216、U1 U14 current-source evidence 39114116352。
- U12 current full quality だけは attempt 2 です。attempt 1 で失敗したのは job「u11-programs / differential (macos-latest, safari)」（117638480843、step 8、safaridriver の session 作成の時間切れ、runner 側）の 1 つだけで、人がその job だけの再実行を選びました。attempt 2 はその job だけを再実行し（117645706087）、29 job すべて成功です。ほかの 6 run は attempt 1 のまま全 job 成功です。
- 各 run の job の集合は、binding-10 の `ci-jobs-a54315f9.json` にある同じ workflow の job の集合と同じです（新しい記録の写しを期待値にしていません）。

### 層の作り（v3 は a54315f9 を head として固定しているため）

- v3 は変えずに、記録済みの a54315f9 の証拠（署名 head・CI 8 run・性能の原本）の上で実行します。a54315f9 の記録は親の証明として残します。
- v4 は署名 head e3c29d1d（親 a54315f9、U15 Step 17 の 7 ファイル、Verified）と、その CI 7 run を足します。attempt 2 を許すのは U12 current full quality の 1 run だけで、attempt 1 の失敗は上の 1 job だけ、attempt 2 で再実行したのもその 1 job だけ、attempt 2 の job はすべて成功、job の集合は親と同じ、を要求します。ほかの run は attempt 1 でなければ拒否します。結果には `ci_rerun`（日本語と英語）として明記します。
- 許可の集合は v3 の 15 ファイルのままで、path は足していません。e3c29d1d で変わった 7 ファイル（`docs/release.md`・`scripts/release/check.py`・`scripts/release/policy.py`・`tests/release/test_api.py`・`tests/release/test_check.py`・`tests/release/test_policy.py`・`tests/release/test_publish_adapter.py`）は、どれも 15 の中にあります（`docs/release.md`・`tests/release/test_policy.py` は v3 の MOVED、ほかの 5 つは v3 の EXTRA_FILES）。v4 はこの 7 つの今の bytes が e3c29d1d の blob（binding-11 の固定）であり、a54315f9 の blob が v3 の固定（binding-10）と同じことを確かめ、v3 にはこの 7 つだけを a54315f9 の bytes として view で見せます。ほかの 8 つは、今の bytes・e3c29d1d・a54315f9 の blob・binding-10 の固定が同じです。
- v3 はその上で、記録どおりに v2・中の chain・旧 chain へそれぞれの古い bytes を見せます。v4 の旧 chain の親と validator の子にも同じ 15 ファイルの古い bytes を見せ、子は v4 を実行します（v4 は自分の `logical_child`・`guarded_run`・`run_old_chain` を持ちます）。
- **bytes の固定の 11 ファイルについて、このコマンドが証明するのは、今の bytes が U15 の承認済み Steps 13〜17 の署名済み head e3c29d1d の bytes であることだけです。中身は U15 のレビューと試験（と e3c29d1d の CI）で確かめるもので、このコマンドでは確かめていません。**（result.json の `allowance.exact_bytes_scope`・`exact_bytes_scope_en`、`not_claimed`、各行の `scope` にも書きます。）
- 性能（FR8.3）の原本（run 39114108809、1 回だけ測定）は確かめて記録するだけです。artifact の ZIP の SHA-256 が API の digest と同じで、原本がその ZIP の中の `performance/observations.json` と同じことも確かめます。値：JIT なし（インタプリタ）の平均 5.2649、JIT ありの平均 4.5834（約 12.9% 短い）、p = 0.0009765625（1/1024）、20 行（10 組）すべて成功、`pass: true`。中の FR8.3 の根拠は今までどおり 1ceae86c（binding-02）です。

### v3 の Minor 4 件への対応

`pending-minor-fixes.md` の「v4 での対応」に書きました。v3 のファイルは変えていません。

### 版の分け方（v3 の Minor 4 への対応）

今後は、採用の前でも入口と binding を上書きしない。v4 の本番の実行が拒否されて入口か binding を直す必要があるときは、v4（`u15_candidate_v4.py`・`binding-11.json`・`test_u15_candidate_v4.py`）と拒否された run のフォルダはそのまま残し、新しく v4b（`u15_candidate_v4b.py`）と binding-12 を作る。

### v4 の回帰（163 件）

`test_u15_candidate_v4.py`：exit 0。163／163、skip 0。

- v3 の回帰 147 件（`test_u15_candidate_v3.py`、`148960fa…` で固定。中で v2 の 132 件、その中で v1 の 116 件）を、変えずに実行しました。v3 の回帰は a54315f9 の作業ツリーを前提に書かれているため、**回帰の実行の間だけ**、Step 17 の 7 ファイルを a54315f9 の blob で見せる読み取り専用の overlay の中で実行します。これは試験の道具の側の設定で、入口の許可ではありません。
- v4 の 16 件（test_600〜615）：正の対照、v3 だけでは `docs/release.md`→`tests/release/test_policy.py`→`scripts/release/check.py` の順に止まり 7 ファイルの view で通ること、7 ファイルが e3c29d1d と違う・a54315f9 の bytes・欠ける・固定の違い、ほかの 8 つが違う、head・親・chain・commit のファイル一覧・Verified・branch・compare（一覧・base・件数・blob）、CI の run の失敗・未完了・head 違い・一覧・bytes だけの変更・run の欠け・workflow 違い・親の job の記録の bytes、ほかの run の attempt 2・U12 の attempt 1・失敗の許可の違い、job の失敗・欠け・件数・head・名前の変更（新しい記録を写して rebind しても親の集合で拒否）・attempt 1 の記録の追加、U12 の attempt 1 のほかの job の失敗・別の job／id の失敗・失敗の記録・件数・conclusion・attempt 2 の失敗・集合・ほかの job の再実行・attempt 1 の記録の欠け、性能の原本と artifact の ZIP（digest・大きさ・ZIP の欠け・項目の違い・中のファイルとの違い・ZIP の中にない）、16 個目の path（changed／unchanged への追加・欠け・入れ替え、定数）、旧 chain が今の作業ツリーと a54315f9 の view では止まり 15 ファイルの古い bytes で通り 7 つのどれが欠けてもそこで止まること、v3 の固定と binding-11、引数（exit 2、本物のプロセス）、旧 chain の子が v4 を実行することと `--logical-child`、結果の文が e3c29d1d の許可と食い違わないこと（a54315f9 を今の head とする文・v1 の性能の文が無いこと。検出の仕組みが v3 の文を実際に見つけることも確かめる）、Minor 4 件の対応、claim scope の層の記述。
- 参考：v3 の回帰を今の作業ツリー（e3c29d1d）でそのまま実行すると exit 1 です（v2 の 132 件は通り、binding-10 の 15 件は setUpClass で `moved file differs from binding/signed head: docs/release.md` で止まる）。v3 が a54315f9 の bytes を前提にしているためで、v4 の回帰の中では上の overlay で 147 件すべて通ります。

### v4 の実行結果（2026-10-18 JST）

- 入口（上のコマンド行）：**exit 0**。`run-1792319052786132000-7821/`（`u15_candidate_v4: PASS`、result.json `4a43fb4c…`）。
- 旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792319055265681000-7821/`（`source_compatibility: PASS`）。validator の子 4 件はすべて exit 0 で、どれも v4 を `--logical-child` で実行しました。旧 chain の親は、固定のある許可の 13 ファイルを view で読みました。
- result.json の v4 の文（`claimed`・`not_claimed`・`allowance`・`ci_rerun`・`claim_scope.u15_version`・`u15_old_chain`・`u15_e3c29d1d`）と `v3_layer` の各行に、e3c29d1d の許可と食い違う文が無いこと、v1 の性能の文が残っていないことも確かめました。
- `FR10_1: GAP`・`U15_acceptance: GAP`・`unit_completed: false`・`formal_command_adopted: false`・`new_measurement: false`・`new_ci: false`。この成功は採用前の確認であり、正式な checkpoint の実行ではありません。

---

## v3（採用済み、履歴）：`u15_candidate_v3.py`（binding-10）

人は v3（`ebb67894…`／binding-10 `44f7c2a9…`）を、独立レビュー `independent-review-03.md`（READY）の Minor 4 件を残したまま検証コマンドとして採用しました。v4 はこの v3 を履歴として bytes で固定し、変えずに中から呼びます。以下は採用の時点までの記録です（見出しのほかは変えていません）。

### 15 ファイルへの拡張（採用した版、2026-10-18 JST）

最初の v3 の実行（下の記録）が旧 chain の `.github/workflows/release-check.yml` で拒否された後、人が承認しました：「この 7 ファイルも a54315f9 のバイト列の固定で許可に足し、もう一度実行してください。中身は U15 のレビューと試験で確かめる、と明記してください。」v3 は未採用なので、その場で直しました（v2 とすべての run フォルダは変えていません）。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate_v3.py --entry-sha256 ebb6789417b48d7e8e8ef3c5ae8919483a85eda0ea85ecda5fbf001d74c2e798 --binding-sha256 44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e
```

| ファイル | SHA-256 |
|---|---|
| 入口 `u15_candidate_v3.py` | `ebb6789417b48d7e8e8ef3c5ae8919483a85eda0ea85ecda5fbf001d74c2e798` |
| `binding-10.json` | `44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e` |
| 回帰 `test_u15_candidate_v3.py`（147 件） | `148960fa85fcc8074bc833e4c9d9aa086431b993b6990781cdb5b60fe970b068` |

- 足した許可（`old_chain_extra`、入口の定数 `EXTRA_FILES` で固定）：`.github/workflows/release-check.yml`・`.github/workflows/release.yml`・`scripts/release/check.py`・`scripts/release/policy.py`・`tests/release/test_api.py`・`tests/release/test_check.py`・`tests/release/test_publish_adapter.py`。古い bytes は旧 chain の binding-v4 の固定・bb197e04・57a8c96f・1ceae86c・be45 の blob（7 つとも同じ）、今の bytes は a54315f9 の blob と binding-10 の固定です。古い bytes は旧 chain の親と validator の子にだけ見せます（v2 と中の chain はこの 7 つを読みません）。
- 許可の集合はちょうど 15 ファイル（`ALLOWED_PATHS_15`）：版の行だけの証明 4 つ（Cargo.lock・fuzz/Cargo.lock・package.json・Cargo.toml）と、bytes の固定 11（README.md・docs/release.md・tests/release/test_package.py・tests/release/test_policy.py と上の 7 つ）。
- **bytes の固定の 11 ファイルについて、このコマンドが証明するのは、今の bytes が U15 の承認済み Steps 13〜14b の署名済み head a54315f9 の bytes であることだけです。中身は U15 のレビューと試験（と a54315f9 の CI）で確かめるもので、このコマンドでは確かめていません。**（result.json の `allowance.exact_bytes_scope`・`exact_bytes_scope_en`、`not_claimed` にも日本語と英語で書きます。）
- 採用済みの chain のどの固定にも入っていない Step 14b のファイルは `.github/workflows/u15-acceptance.yml`・`scripts/release/acceptance.py`・`tests/release/test_acceptance.py` の 3 つだけで、このコマンドは bytes を確かめません（commit と compare の一覧だけ）。
- 回帰：exit 0。147／147、skip 0（v2 の 132 件を bb197e04 の作業ツリーの overlay の中で変えずに実行し、v3 の 15 件）。足したもの：test_507（16 個目のファイル `scripts/release/package.py`・`acceptance.py` の追加、1 つの欠け、binding-v4 のほかの固定の変更で旧 chain が拒否）、test_508（8 ファイルの view では旧 chain が `release-check.yml` で止まり、15 ファイルでは通り、7 つのどれが欠けてもそこで止まる）、test_512（15 ファイルの許可と食い違う文が無いこと。8 ファイルだけ・「そのまま拒否される」・「ほかの 10 ファイル」などの文を検出できることも確かめる）、test_514（7 つそれぞれが a54315f9 と違う・古い bytes・欠ける・固定の違い・古い固定の違い・entry のキー、binding-v4 の変更）。
- **本番の実行：exit 0**。`run-1792310923712980000-25769/`（`u15_candidate_v3: PASS`）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792310925721954000-25769/`（`source_compatibility: PASS`）。validator の子 4 件はすべて exit 0。旧 chain の親は、固定のある許可の 13 ファイルを view で読みました。result.json に 15 ファイルの許可と食い違う文が無いことも確かめました。`FR10_1: GAP`・`U15_acceptance: GAP`・`formal_command_adopted: false`。

### 最初の v3（履歴、8 ファイル）

以下は最初の v3（入口 `ae9a0b7b…`、binding-10 `c262b40e…`、回帰 `9b7d3c96…`）の記録で、変えていません。

2026-10-18 JST。人の承認：「この案で u15_candidate_v3.py と binding-10.json を作り、回帰と独立レビューの後に採用を伺ってください。」採用済みのコマンドは v2（`u15_candidate_v2.py` `b78f867e…` と binding-09 `687fee0c…`）で、v3 はこれを履歴として bytes で固定し、変えずに中から呼びます。

- **本番の実行は exit 1 でした**：`REFUSED: current source changed: .github/workflows/release-check.yml`（下の「v3 の実行結果」）。8 ファイルの外のファイルなので、許可は広げずに止めています。
- commit・push・CI の起動はしていません。GitHub へは読み取りの GET だけを使いました。

### コマンド行

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate_v3.py --entry-sha256 ae9a0b7b1e40f4d7bb3d5f130c16d80fccaf1fa9e5605f1425744fbd098b516d --binding-sha256 c262b40e2c0d79934b3f7281c4d81998c6b957ad877aafc8b9f8aa3347395b54
```

| ファイル | SHA-256 |
|---|---|
| 入口 `u15_candidate_v3.py` | `ae9a0b7b1e40f4d7bb3d5f130c16d80fccaf1fa9e5605f1425744fbd098b516d` |
| `binding-10.json`（入口の定数とも一致を要求） | `c262b40e2c0d79934b3f7281c4d81998c6b957ad877aafc8b9f8aa3347395b54` |
| 回帰 `test_u15_candidate_v3.py`（146 件） | `9b7d3c96304d470de6c01805b9308db860ea9cc2d473bac4339990328947c423` |
| `ci-a54315f9.json`（binding-10 が固定） | `ab5ea24caf7378bd8a2ee7367f01234d77930a1b0e317a965b3978e85a502def` |
| `ci-jobs-a54315f9.json`（binding-10 が固定） | `11e2d9b9da19ac49f519edae2b4edadc5e104a7fd77a047434d454b239120070` |

CI の記録は、読み取りの GET（runs・`attempts/1/jobs`・commits・compare・branch・`runs?head_sha=`）の出力を file-write の道具で写し、同じ GET の結果と Python で比べて 21 項目すべてが一致することを確かめました。

### 層の作り（v2 は bb197e04 を head として固定しているため）

- v2 は変えずに、記録済みの bb197e04 の証拠（署名 head・CI・性能の原本）の上で実行します。bb197e04 の記録は親の証明として残します。
- v3 は署名 head a54315f9（親 bb197e04、U15 Step 14b の 12 ファイル、Verified）と、その CI 8 run（attempt 1、全 job 成功）を足します。各 run の job の集合は、binding-08 にある bb197e04 の同じ workflow の job の集合と同じであることを要求します（新しい記録の写しを期待値にしません）。性能の原本（run 39096893624、`../ci-a54315f9/.../performance/observations.json` `6d3d389e…`）は確かめて記録するだけです。
- 8 ファイルの集合は変えません。Step 14b で変わったのは `docs/release.md`・`tests/release/test_policy.py` だけです。v3 はこの 2 つの今の bytes が a54315f9 の blob（binding-10 の固定）であり、bb197e04 の blob が v2 の固定（binding-09）と同じことを確かめ、v2 にはこの 2 つだけを bb197e04 の bytes として view で見せます。ほかの 6 つ（版の 4 つ・`README.md`・`tests/release/test_package.py`）は、今の bytes・a54315f9・bb197e04 の blob が同じことを確かめます。
- v2 は 8 ファイルを古い bytes として中の chain に見せ、v3 は同じ古い bytes を旧 chain の親と validator の子に見せます。

### v3 の回帰（146 件）

`test_u15_candidate_v3.py`：exit 0。146／146、skip 0。

- v2 の回帰 132 件（`test_u15_candidate_v2.py`、`57c0727f…` で固定）を、変えずに実行しました。v2 の回帰は bb197e04 の作業ツリーを前提に書かれているため、**回帰の実行の間だけ**、Step 14b の 12 ファイルを bb197e04 の blob で見せる読み取り専用の overlay の中で実行します。これは試験の道具の側の設定で、入口の許可ではありません（入口は MOVED の 2 つだけを v2 に bb197e04 の bytes で見せます）。
- v3 の 14 件（test_500〜513）：正の対照、v2 だけでは `docs/release.md`→`tests/release/test_policy.py` の順に止まること、MOVED の 2 つが a54315f9 と違う・bb197e04 の bytes・欠ける・固定の違い、ほかの 6 つが違う、head・親・chain・commit のファイル一覧・親違い・未 Verified・branch・compare（一覧・base・件数・blob）、CI の run の失敗・未完了・head 違い・attempt・一覧・bytes だけの変更・run の欠け・workflow 違い、job の失敗・欠け・件数・head、性能の原本、9 つ目のファイル（MOVED・STAY への追加、欠け、ほかの compiled source）、旧 chain が 8 ファイルの外の Step 14b の 7 ファイルで拒否すること、v2 の固定と binding-10、引数（exit 2、本物のプロセス）、旧 chain の子の guard と `--logical-child`、結果の文が 8 ファイルの許可と食い違わないこと（3 ファイルだけ・bb197e04 への固定 4 つ・署名 head bb197e04 という文が無いこと）、claim scope の層の記述。

### v3 の実行結果（2026-10-18 JST）

- 入口（上のコマンド行）：**exit 1**。`run-1792310402280740000-18124/`
  - `REFUSED: current source changed: .github/workflows/release-check.yml`
  - 止まった段：旧 chain（U1 の `r05-r11-repair-01/final_candidate.py` の `source_pins`、`binding-v4.json`）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792310404289690000-18124/`（refusal）。validator の子は起動していません。
  - その前の段（binding-10 の検査、a54315f9 の head と CI、v2 の検査とその中の U14・U11・U2・U1）はすべて通りました。
  - 旧 chain の binding-v4 が固定し、a54315f9 で変わり、8 ファイルの外にあるファイルは 7 つです：`.github/workflows/release-check.yml`・`.github/workflows/release.yml`・`scripts/release/check.py`・`scripts/release/policy.py`・`tests/release/test_api.py`・`tests/release/test_check.py`・`tests/release/test_publish_adapter.py`。この 7 つで bb197e04 の bytes を見せれば `source_pins` が通ることは test_508 で確かめました（validator の中身はその先なので未確認）。
  - 指示のとおり、許可は広げていません。この 7 つをどう扱うかは、人の判断が必要です。
- `not_claimed` の「Step 14b のほかの 10 ファイル」の文は、採用済みの chain が固定していないもの（`.github/workflows/u15-acceptance.yml`・`scripts/release/acceptance.py`・`tests/release/test_acceptance.py`）はこのコマンドで bytes を確かめないこと、固定しているもの（上の 7 つ）はそのまま拒否されることを書いています。

---

## v2（履歴、採用の後に v3 で置き換えた）：`u15_candidate_v2.py`（binding-09）

v2 は人が採用し、その後 a54315f9 で v3 に置き換えました。以下の「この入口は採用されていません」などの文は、v2 を作った時点の記述です。

2026-10-18 JST。binding-08 の本番の実行が旧 chain の `Cargo.toml` の固定で拒否された後、人が次のように承認しました（coordinator 経由）：「Cargo.toml は版の行だけの証明、README.md・docs/release.md・tests/release の 2 つは bb197e04 のバイト列の固定で許可を足し、もう一度実行してください。package.json の照合の扱いもそれでよいです。」

- この入口は**採用されていません**。独立レビューと、人による採用の承認が残っています。
- commit・push・CI の起動・性能測定はしていません。GitHub への新しい問い合わせもしていません（CI の記録は binding-08 のものをそのまま使います）。
- **本番の実行は exit 0 でした**（下の「v2 の実行結果」）。

### コマンド行

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate_v2.py --entry-sha256 b78f867e4baf0a2ccae6f0b6daf4751383069db7913f58fc78a6375b63183ed5 --binding-sha256 687fee0c4a25147aab064ff101b742a8145d5cb46ea608295146745a524e3649
```

| ファイル | SHA-256 |
|---|---|
| 入口 `u15_candidate_v2.py` | `b78f867e4baf0a2ccae6f0b6daf4751383069db7913f58fc78a6375b63183ed5` |
| `binding-09.json`（入口の定数とも一致を要求。review-01 の修正では変えていない） | `687fee0c4a25147aab064ff101b742a8145d5cb46ea608295146745a524e3649` |
| 回帰 `test_u15_candidate_v2.py`（132 件） | `57c0727fbfe71716fbd386227292f8d69171d7b5e7ac499f5e277c188fd53b7f` |

### 独立レビュー 01（NOT-READY）への対応

`independent-review-01.md` の指摘はどれも結果の文で、検査は変えていません。v1 の bytes も変えていません。

- Major：v2 の result.json と claim scope に、v1 の 3 ファイルの文（v1 の `not_claimed[0]`「3ファイル以外の差…この入口はそれらを許さない」、`u15_version.scope`「版の行…だけを3ファイルで許す」）が残っていました。v2 では、これらを v2 の事実の文（`ALLOWANCE_V2`：許すのは 8 ファイルだけ、版の行だけの証明 4 つと bb197e04 の bytes への固定 4 つ）に置き換えました。result.json には `allowance_statement` としても書きます。test_415 は、v2 の文と claim scope に 8 ファイルの許可と食い違う文（3 ファイルだけを許すという文）があれば失敗します。検出の仕組みが v1 の文を実際に見つけることも同じ試験で確かめています。
- Minor：bb197e04 で足された 3 ファイル（`scripts/release/acceptance.py`・`tests/release/test_acceptance.py`・`.github/workflows/u15-acceptance.yml`）の作業ツリーの bytes は、このコマンドでは固定していない（採用済みの chain の範囲の外。commit と compare の一覧だけを確かめる）ことを `not_claimed` に足しました。bytes は U15 のレビュー・試験と CI で確かめます。
- Minor：`CLAIMED_V2[1]` の古い bytes の書き方を、コードと同じ「binding-v4 の固定・57a8c96f・1ceae86c・be45 の blob」にそろえました。

修正前の候補の run（`run-1792294223452925000-96601/`、レビューの run `run-1792294558646092000-3308/`）は履歴として残します。その result.json には修正前の文が入っています。

### v1（binding-08）との違い

- v1 の入口 `u15_candidate.py` をそのバイト列（`6a5077ae…`）で確かめてから実行し、その関数（署名 head と CI・性能の原本の検査、3 ファイルの版の証明、package.json の receipt の扱い、U14 と案の履歴、claim scope）を変えずに呼びます。署名 head・CI・版の 3 ファイルの値は binding-08 のものを使います。v1 の入口・binding-08・その回帰・拒否された run（`run-1792293531741241000-82551/` の refusal.json・children.json）は履歴として bytes を固定します。
- 足した許可（入口の定数で固定、合わせて 8 ファイル）：
  - `Cargo.toml`：構文と行で、`workspace.package.version` と内部の依存 11 件（`{ path = "crates/<name>", version }`）の `version` が `"0.0.0"` → `"0.1.0"` に変わるだけで、ほかのキー・値・表・行は同じことを証明します。古い bytes は旧 chain の binding-v4 の固定・57a8c96f・1ceae86c・be45 の blob、新しい bytes は bb197e04 の blob です。
  - `README.md`・`docs/release.md`・`tests/release/test_policy.py`・`tests/release/test_package.py`：bytes の固定だけの許可。古い bytes は binding-v4 の固定・57a8c96f（と 1ceae86c・be45）の blob、新しい bytes は bb197e04 の blob（binding-09 の固定）。**この許可が証明するのは、bytes が U15 の承認済み Steps 13〜14 の署名済み head bb197e04 の bytes であることだけです。内容は U15 のレビューと試験で確かめるもので、このコマンドでは確かめていません**（result.json の `allowance.exact_bytes_scope` にも書きます）。
- 8 ファイルすべてを、変えていない `historical_child.View` で古い bytes として、中の検査（U14・U11・U2・U1）、旧 chain の親、validator の子に見せます。旧 chain の親が固定のある 6 ファイルを view で読んだことも確かめます。

### v2 の回帰（132 件）

`test_u15_candidate_v2.py`：exit 0。132／132、skip 0（下の 116 件と v2 の 16 件。test_415 は review-01 の対応で足しました）。

- v1 の回帰 116 件（`test_u15_candidate.py`、`6573bc6c…` で固定）をそのまま実行：116／116、skip 0（U14 の 93 件と U15 の 23 件）。
- v2 の 15 件（test_400〜414）：正の対照、v1 の 3 ファイルの view では旧 chain が `Cargo.toml` で止まり 8 ファイルでは通ること（1 ファイルでも欠けるとそこで止まること）、`Cargo.toml` のほかのキー（edition・license・lints・依存の追加・profile・package 表）、ほかの版の値、依存の path・キーの変更、行の形・行数・構文、bytes 固定の 4 ファイルと `Cargo.toml` が bb197e04 と違う・古い bytes・欠ける、古い固定の違い・種類の入れ替え・binding-v4 の変更、9 つ目のファイル（binding への追加、ほかの compiled source、旧 chain のほかの固定 `scripts/release/check.py`）、binding-09 の base・v1・キーの集合・schema、v1 の入口・binding-08 の bytes、v1 の履歴、引数（exit 2、本物のプロセスも）、旧 chain の子の guard、`--logical-child`、claim scope。15／15、skip 0。

### v2 の実行結果（2026-10-18 JST）

- review-01 の修正後の入口（上のコマンド行）：**exit 0**。`run-1792294967905224000-92020/`（`u15_candidate_v2: PASS`）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792294969312562000-92020/`（`source_compatibility: PASS`）。この result.json に、3 ファイルだけを許すという文が無いことも確かめました。
- 修正前（履歴）：入口 `8ceb46bd…` で exit 0、`run-1792294223452925000-96601/`。旧 chain の出力は `formal-candidate-1792294225151985000-96601/`（`source_compatibility: PASS`、`U15_acceptance: GAP`、`unit_completed: false`）。validator の子 4 件はすべて exit 0。
- 結果は `FR10_1: GAP`・`U15_acceptance: GAP`・`formal_command_adopted: false`・`new_measurement: false`・`new_ci: false` です。この成功は採用前の確認であり、正式な checkpoint の実行ではありません。

---

## v1（履歴）：`u15_candidate.py`（binding-08）

以下は v1 の時点の記述で、変えていません。

2026-10-18 JST。人が承認した案 `../version-allowance-proposal.md`（SHA-256 `df38caab…`、binding-08 の `spec` で固定）の 2（入口）と 3（回帰）の記録です。

- この入口は**採用されていません**。独立レビューと、人による採用の承認が残っています。engine への登録もしていません。
- commit・push・CI の起動・再実行・性能測定はしていません。GitHub へは読み取りの GET だけを使いました。
- **本番の実行は exit 1 でした**（下の「実行結果」）。中の旧 chain が、許可の外のファイル `Cargo.toml` で拒否しました。案のとおり、許可は広げずにここで止めています。

## コマンド行

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u15-release/code-generation/verification/version-allowance/u15_candidate.py --entry-sha256 6a5077aef1034f6276c2806c66d0cfb62550812ee95217de92f7c7931b638cc0 --binding-sha256 f20954e14dc761f4dc0172d775af3c2602f8f2887539c900fa2319ba33b30262
```

| ファイル | SHA-256 | 役割 |
|---|---|---|
| `u15_candidate.py` | `6a5077aef1034f6276c2806c66d0cfb62550812ee95217de92f7c7931b638cc0` | 入口 |
| `binding-08.json`（入口の定数 `BINDING_SHA256` とも一致を要求） | `f20954e14dc761f4dc0172d775af3c2602f8f2887539c900fa2319ba33b30262` | 版の許可・署名 head・CI |
| `test_u15_candidate.py` | `6573bc6c158199bd1466aa076bdee307e9d82da7503a6cb3d48403572f37e10a` | 回帰（116 件） |
| `ci-bb197e04.json` | `cf63cbe35390f51126b553baa08f7c9fdf841d4549f4ba4c9efa490913282a50` | bb197e04 の commit・compare・run（binding-08 が固定） |
| `ci-jobs-bb197e04.json` | `88b8aa40479506414b3ef683a94d9a2111ed4814b86d41e414cd522373aa2ae4` | 7 run の attempt 1 の job（binding-08 が固定） |

このREADMEは入口もbindingも固定していません。

## 入口がすること

コマンド行の約束（`--entry-sha256`・`--binding-sha256` の順、引数や hash の違いは検査の前に exit 2 で何も書かない、拒否は exit 1 と `refusal.json`、合格は exit 0 と `result.json`、どちらも新しい `run-<ns>-<pid>/`、`--logical-child` も最初に同じ hash 検査）は U14 の入口と同じです。

1. U14 の入口 `u14_candidate_v2.py`（`934f21bc…`）を、そのバイト列を SHA-256 で確かめてから実行し、binding-07（`425ae3e7…`）をそのまま使います。U14・U11・U2・U1 の検査と旧 chain は、どれも変えずに呼びます。U14 の入口・binding-07・その回帰・README は履歴として bytes を固定します。
2. 新しく許すのは、入口の定数で固定した 3 ファイルの版の差だけです。
   - (a) 古い bytes は 57a8c96f・1ceae86c・be45 の git blob と同じ。binding-02 の receipt の固定は、receipt を作った 208fd965 の blob と同じ。2 つの lock では receipt の固定も古い bytes と同じです。
   - (b) 今の bytes は署名済み head bb197e04 の blob と、binding-08 の値に同じ。
   - (c) 構文（TOML・JSON）と行の両方で、差が版だけであることを証明します。`Cargo.lock` は workspace の 13 crate、`fuzz/Cargo.lock` は 9 crate（名前の集合は入口の定数）の `version` が `"0.0.0"` → `"0.1.0"` に変わるだけで、package の数・順番、ほかの欄（source・checksum・dependencies）、ほかの package（外部 crate と `paludarium-fuzz`）は同じ。変わった行は版の行だけで、その前の行はその crate の `name` の行です。`package.json` は最上位の `"version"` だけが変わり、ほかのキー・値・キーの順番と bytes（版の値を除く）は同じです。
   - (d) bb197e04 は Verified、親は 57a8c96f、local git と保存した compare の変更は既知の 11 ファイルだけ。保存した 7 run（CI・Release package checks・U14 current full quality・U12・U13・U14 fuzz・U1 U14 current-source evidence）は、U1 の `verify_ci`・`verify_ci_jobs` を変えずに使って、その head で attempt 1 のまま完了・全 job 成功を確かめます。bb197e04 で 1 回だけ測った性能の原本（run 39089194062、`../ci-bb197e04/.../performance/observations.json`、`47aafefc…`）は U1 の `verify_performance` で確かめて記録するだけです。
3. この 3 ファイルだけを、変えていない `historical_child.View` で古い bytes として中に見せ、U14 の入口の `verify` と旧 chain（親の `final_candidate.main` とその validator の子）を実行します。ほかのファイルは今のまま読みます。

### 案の文言と違う 1 点（人の確認が必要）

案と依頼では「古い bytes = binding-02 の receipt の固定」としていました。調べると、`packages/paludarium-wasm/package.json` では成り立ちません。

- receipt（`acceptance-control.wasm.receipt.json`）は 208fd965 で作ったもので、`package.json` の固定 `c3c0950d…` は 208fd965 の blob です。
- 208fd965 と be45 の間で `repository` と `publishConfig` が足されたため、57a8c96f・1ceae86c・be45 の blob は `def04cf8…` です。
- U1 の検査は、許可していない compiled source を be45 と 1ceae86c の blob で固定していて、receipt の値とは比べていません。今までの合格もこの形です。

そのため入口では、`package.json` について「receipt の固定 = 208fd965 の blob」と「古い bytes = 57a8c96f・1ceae86c・be45 の blob」を別々に確かめ、両者が違うことを定数 `RECEIPT_IS_OLD`（2 つの lock だけ）で固定しました。今の bytes に対する許可は広げていません。

## CI の記録の作り方

`gh api` の読み取りの GET だけを使いました（runs・`attempts/1/jobs`・commits・compare・branch・`runs?head_sha=`）。出力を file-write の道具で JSON に写し、そのあと同じ GET の結果と保存した JSON を Python で比べて、7 run・7 job 一覧・2 commit・compare がすべて一致することを確かめました。dispatch・rerun・push・書き込みはしていません。

## 回帰（116 件）

`test_u15_candidate.py`：exit 0。116 件／期待 116 件、skip 0、全件成功。

- U14 の回帰 93 件（`test_u14_candidate_v2.py`、`aab2a01a…` で固定。U11 の 73 件と U14 の 20 件）を、3 ファイルだけを古い bytes で見せた view の中で、変えずに実行しました。
- U15 の 23 件（test_300〜322）：正の対照、U14 の入口だけでは `Cargo.lock`→`fuzz/Cargo.lock`→`package.json` の順に止まること、外部 crate の版・checksum・依存（workspace と外部）の変更、`paludarium-fuzz` の版の変更、`0.1.0` 以外の版（`0.1.1`・`0.0.0`・`1.0.0`・`0.1.0-rc.1`）、lock の package の数・順番・最上位・行の形・改行・UTF-8・構文、`package.json` のほかのキー・入れ子の値・キーの追加・削除・順番・空白・重複キー、今の bytes が bb197e04 と違う・欠ける、古い固定と receipt の固定の違い、4 つ目のファイル（binding への追加、ほかの compiled source、旧 chain の `Cargo.toml` の固定）、署名 head・親・chain、CI の run の失敗・未完了・head 違い・未 Verified・親違い・branch・commit のファイル一覧・compare・blob・run 一覧・bytes だけの変更・run 名、job の失敗・skip・欠け・件数・head・attempt、性能の原本、base・U14 の入口・binding-07、履歴・spec、binding の固定と引数（exit 2）、本物のプロセスの exit、旧 chain の子の guard、`--logical-child` の境界と hash 検査、claim scope。

## 実行結果（2026-10-18 JST）

1. 回帰：上のとおり exit 0。
2. 新しい入口（上のコマンド行）：**exit 1**。`run-1792293531741241000-82551/`
   - `REFUSED: current source changed: Cargo.toml`
   - 止まった段：旧 chain（U1 の `r05-r11-repair-01/final_candidate.py` の `source_pins`。`binding-v4.json` が 40 ファイルを be45 の時点の bytes で固定している）。旧 chain の出力は `u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792293533080890000-82551/`（refusal）。旧 chain の子は起動していません（`children.json` は空）。
   - その前の段（binding-08 の検査、3 ファイルを古い bytes で見せた U14・U11・U2・U1 の検査）はすべて通りました。
   - `binding-v4.json` が固定し、bb197e04 で変わったファイルは 6 つです：`Cargo.toml`・`README.md`・`docs/release.md`・`packages/paludarium-wasm/package.json`（この入口の許可の中）・`tests/release/test_package.py`・`tests/release/test_policy.py`。最初に止まったのが `Cargo.toml` です。この 6 つで 57a8c96f の bytes を見せれば `source_pins` が通ることは回帰 test_311 で確かめました（旧 chain の validator の中身はその先なので未確認です）。
   - 案の「2 の最後」のとおり、許可は広げていません。
3. 今の正式なコマンド（U14 の `u14_candidate_v2.py`、binding-07）をもう一度実行：exit 1。`REFUSED: compiled source changed: Cargo.lock`。出力は `u14-jit-wasm/code-generation/verification/loopback1-next/run-1792293546510087000-82616/`（履歴として残します）。

## 次に人が決めること

旧 chain の `binding-v4.json` が固定する 5 ファイル（`Cargo.toml`・`README.md`・`docs/release.md`・`tests/release/test_package.py`・`tests/release/test_policy.py`）の差を、どう扱うかです。版の行だけの差ではないもの（`docs/release.md` の 178 行の追加、試験の追加など）を含むので、同じ方法の許可では足りません。案の 2 の最後のとおり、許可を足す案をもう一度見せてから決めます。

## 主張しないこと

- 3 ファイル以外の差を許すこと。
- FR10.1 と U15 の受け入れ（`U15_acceptance` は GAP のまま）、unit の完了、正式な確認コマンドとしての採用。
- bb197e04 での性能（FR8.3）の正式な合格。bb197e04 の原本は検査して記録するだけで、module の receipt には束ねていません。中の性能の根拠は今までどおり 1ceae86c（binding-02）です。
- 新しい測定・CI・build・publish。
