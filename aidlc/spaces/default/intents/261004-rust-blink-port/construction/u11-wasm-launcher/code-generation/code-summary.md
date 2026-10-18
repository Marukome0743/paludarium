# U11 実装サマリー

## 現行Step31（再レビューのMinor R-08・R-09への対応）（2026-10-18）

再レビュー（iteration 1・2、READY）のMinor 2件に対応した。人は「60 秒のテストを足す」（R-08）と「hash を固定する」（R-09）を指定し、U11のcheckpointでRequest Changesを選んだ。Step30の入口（`u11_candidate.py`、binding-04）は、checkpointに進むために仮に採用したもので、今は履歴である（下の「Step30の入口の扱い」）。製品（Rust・起動用JS・`u11-browser-driver.mjs` を含む）・guest・workflow・lock・mise.toml・.gitignore・source-manifest.json・ほかのUnitの記録・旧い証拠は変えていない。

### R-08：60秒の待ち時間の回帰（済み）

- `packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` に回帰「Safari session creation alone waits 60000 ms while other WebDriver requests keep 10000 ms」を1件足した。仮の safaridriver（`child_process.spawn` の差し替え）と仮の WebDriver（`fetch` の差し替え）で `safari()` を動かし、`AbortSignal.timeout` に渡った値を要求ごとに記録して、`POST /session` だけが 60000 ms、`GET /status`・`POST /session/s1/url`・`POST /session/s1/execute/sync`・`DELETE /session/s1` は既定の 10000 ms であること、driver が `SIGTERM` で止められることを確かめる。差し替えは `finally` で元に戻す。`u11-browser-driver.mjs` は変えていない（差し込み口は不要だった）。
- 署名commit：`57a8c96f610d6e02234354e5e4fb5cac068d5036`（fork `Marukome0743/paludarium` の `codex/build-and-test` の head）。親は `2b8723ab028ba6b037df08d0cfb51073a660f8cc`（その親は `1ceae86ce303a1019e97ac7d162ce0efa9fadd50`）、GitHubで `verified: true`／`reason: valid`、tree `425bf7c2059acfe59d1e061b22ec21066d84f382`。変更は試験の1ファイルだけ（GitHubのcommitの `files` と、手元の `git diff-tree 2b8723ab 57a8c96f` の両方で確認）。1ceae86cからの変更は、今までどおりSafariの2ファイルだけである。
- SHA-256（`git cat-file blob 57a8c96f:<path>` と作業コピーが一致）：`u11-browser-driver.mjs` は `2adf542264e881ebd683af4fe24707a5b5511d525b33c6bd9ff2d73f05a4e8f0`（2b8723abと同じ）、`u11-browser-driver.test.mjs` は `0fd118c3e8992a064fd0fcf301d86c82521882c17bf16b99e641a5aeb700865c`（2b8723ab）から `f8045c411a1077006d68d8cfb628029070e182366e195a0756d2a59d5fc9bf21`。
- この Mac の確認：`/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` は10件成功・失敗0件、終了コード0（2026-10-18）。本物のSafariは使っていない。
- CI（2026-10-18に読み取り専用の `gh api` で確認。このheadのrunは3件だけ）：
  - PR CI run 39073492190（attempt 1）：23 jobすべて成功。本物のSafariの `u11-programs / differential (macos-latest, safari)`（job 117517258710）は時間切れなく成功。
  - Release package checks run 39073492188（attempt 1）：1 job成功。
  - U12 current full quality run 39073501121：最新のattempt 2で29 jobすべて成功。attempt 1は `differential tests (x86-64 Linux)`（job 117515797287）だけが step 6（`cargo test --locked -p paludarium-harness --test diff_u1 … --test diff_u3 …`）で失敗した。原因は `u3_fresh_native_differential` の `unobserved native SHA profile: "GenuineIntel" signature 000606a6`で、U3のnative契約が、まだ観測していないrunnerのCPU（Intel、signature 000606a6）でのSHA命令の期待結果を使わずに止まる設計どおりの停止である（製品やSafariの結果ではない。期待結果を足す作業はしていない）。attempt 2はこのjobだけの再実行で、job 117520999193 が成功した。本物のSafariのjobはattempt 1（job 117517348944）で成功した（最新attemptの一覧では job 117521018499 として載り、開始時刻はattempt 2の開始より前）。
  - u14-quality（U14 current full quality）は正式な性能測定を含むので起動していない。
- 揺れについて：本物のSafariのsession作成は、2b8723abの2回に続き、このheadの2つのrunでも時間切れなく成功した。4回の成功であり、揺れが今後起きないことの保証ではない。

### R-09：hashを固定した新しい入口（作成のみ。未採用）

Step30の入口とbinding-04は2b8723abのbytesを固定しているので、57a8c96fの試験のファイルの変更でexit 1になる（実行結果は `verification/loopback1-next/README.md`）。そこで、Step30の設計をそのまま使い、新しいheadに合わせた入口 `verification/loopback1-next/u11_candidate_v2.py` と binding-05 を作った。U2の入口 `u2_candidate.py`（`d88789d0b5af82a4de5a10c33d3daf365444c1ccfe6a5088b4bb5e7aefc2e586`）とbinding-03（`2b60e40e52c614fa3f93660e1594e36b39537cf7c549a1e1f918fe455f3bc14c`）、U1のchecker `new_candidate.py`（`a7836f9b880aed05b18d1f283f1cee4dadf79a420b8d8aaa6b3587a6652fc339`）とbinding-02（`6315b735647c310e5b9ac82291a56652830ff406ee98c43a0a31b2f7db70ecbb`）、旧い封印は、1 byteも変えずにSHA-256で固定して呼び出す。binding-04から変えたのは次の3つだけで、ほかの許可・検査は弱めていない：

- (a) Safariの2ファイルを57a8c96fのbytes（driver `2adf5422…`、試験 `f8045c41…`）で許す。作業コピー・`git cat-file blob 57a8c96f:<path>`・binding-05の新しいSHA-256の3つの一致を要求する。旧い値（1ceae86c＝be45＝compiled receiptのpin）は変えていない。許すファイルは今までどおりこの2つだけ。
- (b) 署名headを57a8c96fにし、chain `1ceae86c → 2b8723ab → 57a8c96f` を束ねる（どのcommitもVerified、GitHubと手元のgitの親子とtreeが一致、commitごとの変更ファイルがSafariの2ファイルの中にあり、1ceae86cからheadまでの変更がちょうど2ファイル）。そのheadのCI（上の3 run、最新attemptのjobの一覧、Safariのjobの成功、U12 qualityのattempt 1の失敗の記録、u14-qualityを起動していないこと）を、hashで固定したJSON `ci-57a8c96f.json`・`ci-jobs-57a8c96f.json` で束ねる。
- (c) U11の記録の許可を、このStepの新しいbytes（この節を足したcode-summary.md、FR5.3・NFR7の注記を足したtraceability.json、Step 31を足した計画、変えていない手順書）にする。許す記録は今までどおりこの4件だけで、計画はcheckboxの状態だけを無視した形で固定する。

新しい要件（R-09）：新しい入口は、コマンド行の引数 `--entry-sha256 <hex> --binding-sha256 <hex>` を必ず受け取り、自分自身のファイルとbinding-05のSHA-256を計算して、引数がない・形が違う・値が一致しない場合は、何も検査せずに終了コード2で止まる（stderrに `REFUSED:` と理由）。これで2つのhashが採用するコマンド行そのものに入り、人の採用の承認で固定される。

新しいコマンド（project rootで実行。2つの `<…>` には `verification/loopback1-next/README.md` の表の値を入れる）：

```text
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py --entry-sha256 <u11_candidate_v2.pyのSHA-256> --binding-sha256 <binding-05.jsonのSHA-256>
```

この節に2つのhashの値を書かないのは、binding-05がこの節を含むcode-summary.mdのbytesを固定し、入口がbinding-05のSHA-256を固定するため、書くと値が循環するからである。値はコマンド行で運ばれ、README.mdと親担当への報告に書く。

**人がこのコマンド行（2つのhashの値を含む）を採用してから、U11のcheckpointで実行する。** この作業では採用・登録をしていない。

### Step30の入口の扱い

`u11_candidate.py` とbinding-04、その実行結果（`run-*`）は履歴として残し、変えていない。binding-04の仮の採用は、checkpointに進むための一時的なもので、Step31の後は履歴である。57a8c96fの試験のファイルと、このStepで変えたU11の記録のため、今は終了コード1になる（README.mdの「実行結果」）。

## 現行Step29〜30（Loop-back 1）（2026-10-17〜18）

（この節は見出しを含めて当時のまま履歴として残す。traceability.json の参照を保つため。Step30の入口は上の「現行Step31」節のとおり履歴になった。）

Step 28で取り消したSafariのsession作成の待ち時間の修正を、Step 29でやり直してpushし、Step 30でその2ファイルを許す新しい正式確認の入口を作った。製品（Rust・起動用JS）・guest・workflow・lock・mise.toml・.gitignore・source-manifest.json・ほかのUnitの記録・旧い証拠は変えていない。

### Step 29：Safariの待ち時間の修正（済み）

- 変えた行（Step 27と同じ内容）：`packages/paludarium-wasm/tests/u11-browser-driver.mjs` の `webdriverRequest(base, method, path, body, timeoutMs = 10000)` で `AbortSignal.timeout(timeoutMs)` を使い、`safari()` の `POST /session` の呼び出しだけ `60000` を渡す。`u11-browser-driver.test.mjs` に回帰「WebDriver request honours a supplied timeout against a slow endpoint」を1件足した。driverの起動待ち、navigation・script-reportの要求（10秒）、suite全体の `timeout`、guest 30秒、cleanupは変えていない。
- 署名commit：`2b8723ab028ba6b037df08d0cfb51073a660f8cc`（fork `Marukome0743/paludarium` の `codex/build-and-test` の head）。親は `1ceae86ce303a1019e97ac7d162ce0efa9fadd50`、GitHubで `verified: true`／`reason: valid`、tree `fa040e34136589ed580a980ead0d36f7ff70ec6f`。変更は上の2ファイルだけ（GitHubのcommitの `files` と、手元の `git diff-tree 1ceae86c 2b8723ab` の両方で確認）。
- SHA-256（`git cat-file blob` と作業コピーが一致）：`u11-browser-driver.mjs` は `e64fbac1f3f7dbf991d7fae5ee743f17813b6be44659b837ff4c07fa7eb63fa1`（1ceae86c、be45と同じ）から `2adf542264e881ebd683af4fe24707a5b5511d525b33c6bd9ff2d73f05a4e8f0`、`u11-browser-driver.test.mjs` は `3c9a5d5b6085f81140998d8a9d3f42220c4b708798df5ed7bce7b30efc2948c4` から `0fd118c3e8992a064fd0fcf301d86c82521882c17bf16b99e641a5aeb700865c`。
- この Mac の確認：`/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` は9件成功・失敗0件、終了コード0（2026-10-18にもう一度実行）。本物のSafariは使っていない。
- CI（2026-10-18に読み取り専用の `gh api` で確認。このheadのrunは3件だけ）：
  - PR CI run 39044785452（attempt 1）：23 jobすべて成功。本物のSafariの `u11-programs / differential (macos-latest, safari)`（job 117432507127）は時間切れなく成功。
  - Release package checks run 39044785445（attempt 1）：1 job成功。
  - U12 current full quality run 39044793102：最新のattempt 2で29 jobすべて成功。attempt 1は `u12-fuzz / fuzz (load_elf)`（job 117431272199）だけが step 8「Prepare the observed LLVM symbolizer for the decoder-table suppression」で失敗した。原因は `curl: (7) Failed to connect to apt.llvm.org port 443`（外部の取得先への接続の失敗で、fuzzの対象が動く前。一時的な失敗として記録し、製品やfuzzの結果とは扱わない）。attempt 2はこのjobだけの再実行で、job 117436023002 が成功した。本物のSafariのjobはattempt 1（job 117432917070）で成功した。
  - u14-quality（U14 current full quality）は正式な性能測定を含むので起動していない。
- 揺れについて：本物のSafariのsession作成は、このheadの2つのrunで2回とも時間切れなく成功した。2回の成功であり、揺れが今後起きないことの保証ではない。

### Step 30：新しい正式確認の入口（作成のみ。未採用）

今の正式確認コマンド（人が採用したU2の入口）は、上の2ファイルの変更でexit 1になる。2026-10-18に実行して確かめた：`REFUSED: compiled source changed: packages/paludarium-wasm/tests/u11-browser-driver.mjs`（出力 `construction/u2-integer-isa/code-generation/verification/loopback1-next/run-1792252935194891000-35673/refusal.json`）。理由は、U1のcheckerが223個のcompiled sourceのうち許した13件以外を、be45と1ceae86cのblobと一致することで固定しており、2ファイルはその13件に入っていないため。

新しい入口のコマンド（project rootで引数なし）：

```text
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate.py
```

新しい入口は、次のものを1 byteも変えずにSHA-256で固定して呼び出す：U2の入口 `u2_candidate.py`（`d88789d0b5af82a4de5a10c33d3daf365444c1ccfe6a5088b4bb5e7aefc2e586`）とbinding-03（`2b60e40e52c614fa3f93660e1594e36b39537cf7c549a1e1f918fe455f3bc14c`）、U1のchecker `new_candidate.py`（`a7836f9b880aed05b18d1f283f1cee4dadf79a420b8d8aaa6b3587a6652fc339`）とbinding-02（`6315b735647c310e5b9ac82291a56652830ff406ee98c43a0a31b2f7db70ecbb`）、旧い封印。binding-03から足す許可は次の3つだけである：

- (a) 上の2ファイルを、新しいheadのbytes（`git cat-file blob 2b8723ab:<path>`・作業コピー・binding-04の新しいSHA-256の3つが一致）で許す。旧い値は1ceae86c（＝be45＝compiled receiptのpin）のbytes。U1・U2の検査と旧い検査には、この2ファイルだけ旧いbytesを読取専用で見せる（U1と同じ `historical_child.View` を使う）。ほかのcompiled sourceは今までどおりbe45と1ceae86cのblobと一致を要求し、2b8723abのcommitが2ファイル以外を変えていないことも確かめる。
- (b) 新しいheadの署名・親（1ceae86c）と、そのheadのCI（PR CI・Release package checks・U12 quality）のrunとjobの成功を、保存したJSONで束ねる：`ci-2b8723ab.json`（SHA-256 `90c89da6256405ca46e9f99de7292b7b986cba3848c00f51000f0d339b0f5840`）と `ci-jobs-2b8723ab.json`（`84b2fdc45f82d3e91ae0767f4966895cc7bca4c6ce47662e545a99fd6fc43ccd`）。U12 qualityのattempt 1の失敗（load_elfの一時的な失敗）と、u14-qualityを起動していないことも記録する。照合はU1のcheckerの `verify_ci`・`verify_ci_jobs` をそのまま呼ぶ。
- (c) このStepで変えるU11の記録4件（この節を足したcode-summary.md、FR5.3・NFR7の注記を足したtraceability.json、計画、手順書）の新しいbytes。4件とも旧い封印には入っていない（封印にあるU11の記録570件は、封印の値と一致することをもう一度確かめる）ので、新しいbytesを固定するだけである。計画はU2と同じくcheckboxの状態だけを無視した形で固定する。

性能の証拠：1ceae86cの性能の原本とmoduleのreceiptは、binding-02のまま今までどおり束ねる。2b8723abの変更は試験の道具の2ファイル（WebDriverのdriverとその試験）だけで、module（Rust・起動用JS）は変えていない。新しい性能測定はしていない。

入口とbinding-04自身のSHA-256、回帰の一覧と件数、実行結果（終了コード）とsensorの結果は、`verification/loopback1-next/README.md` に書く。この節に入口とbinding-04のSHA-256を書かないのは、binding-04がこの節を含むcode-summary.mdのbytesを固定し、入口がbinding-04のSHA-256を固定するため、書くと値が循環するからである。

この入口はまだ採用されていない。独立再レビューのあと、人が採用（Construction Verification Commandの決定）してから、checkpointで実行する。

## 現行Step28：Step 27 の取り消し（2026-10-17）

人の判断に従い、Step 27 の変更を取り消した。下の「現行Step27」節は見出しを含めて当時のまま履歴として残す（traceability.json の参照を保つため）が、その変更はもう現行のソースにない。

取り消した理由：`packages/paludarium-wasm/tests/u11-browser-driver.mjs` は、U14の速さの測定で使った223個の固定ソースの1つである。正式な確認コマンド（`final_candidate.py` → `compatibility.py` の `verify_physical`）はこれらのソースのバイトをSHA-256で照合する（封印）。Step 27 の後の正式な確認は `ValueError: compiled source changed` で終了コード1になった。出力フォルダは `aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792227065324817000-13775/`（`0.stderr.bin` にこの例外がある）。

戻したもの：`u11-browser-driver.mjs` と `u11-browser-driver.test.mjs` の2ファイルを、Step 27 の前のバイト（fork `codex/build-and-test` の head e4f84768 の版。git HEAD と同じ）に戻した。製品・guest・workflow・source-manifest.json・ほかのUnitの記録は変えていない。

確認結果（検証済み）：

- `git diff --quiet e4f84768 -- <2ファイル>` は終了コード0（差分なし）。gitのblob IDも一致した（`.mjs` は `bf4c33f341da78e67d23a8d4316e4bae6128fd4c`、`.test.mjs` は `c2e598687232a8dcaaeca93baa05b3584247c1c1`）。
- 戻した後のSHA-256：`u11-browser-driver.mjs` は `e64fbac1f3f7dbf991d7fae5ee743f17813b6be44659b837ff4c07fa7eb63fa1`、`u11-browser-driver.test.mjs` は `3c9a5d5b6085f81140998d8a9d3f42220c4b708798df5ed7bce7b30efc2948c4`。
- この Mac で `/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` を実行し、既存8件が成功・失敗0件、終了コード0。

Safariの揺れの扱い：CIの本物のSafariがWebDriverのsession作成で10秒のタイムアウトになる揺れ（Step27節のrun・job）は、今回は直さない。揺れたときは再実行し、そのrun・jobを記録する。待ち時間の修正は、道具の版の更新（新しい正式な確認コマンドが必要）と一緒に後の作業で行う。揺れは解消しておらず、未解決として残る。

未確認：正式コマンドでのcheckpoint再検証（終了コード0に戻ること）と独立再レビューは、この節を書いた時点ではまだ行っていない。

## 現行Step27：Safariのsession作成の待ち時間（2026-10-17）

Build and Testからの差し戻し（人は「今直す」を選択）に従い、本物のSafariの確認がWebDriverのsession作成で揺れる問題だけを直した。製品・guest・workflow・source-manifest.json（2ファイルは記載済み）は変更していない。

失敗したrun・job：`u11-programs / differential (macos-latest, safari)` が `Error: Safari session-creation: TimeoutError: The operation was aborted due to timeout; driver exit=null, signal=null, log=` で失敗した。PRゲート run 39009487698（job 117332375020）、run 39015770796 attempt 1（job 117348561712）、u12-quality run 39015780495 の attempt 1・2（attempt 2 は job 117355140969）。同じheadで run 39015770796 attempt 2 と u14-quality run 39009460781 attempt 2 は成功した。

原因：`packages/paludarium-wasm/tests/u11-browser-driver.mjs` の `webdriverRequest` が全要求の待ち時間を `AbortSignal.timeout(10000)` に固定していた。新しいmacOSランナーでSafariを初めて起動する `POST /session` が10秒を超えることがあり、製品ではなく試験の道具の待ち時間が足りない揺れである。

変えた行：

- `u11-browser-driver.mjs`：`webdriverRequest(base, method, path, body, timeoutMs = 10000)` とし、`AbortSignal.timeout(timeoutMs)` に使う。`safari()` の `POST /session` の呼び出しだけ `60000` を渡す（理由のコメントを1行追加）。driverの起動待ち（10秒）、`/status`・navigation・script-report・`DELETE /session` の要求（10秒）、suite全体の `timeout`、guest 30秒、cleanupは変えていない。
- `u11-browser-driver.test.mjs`：回帰「WebDriver per-request timeout aborts a slow endpoint」を1件追加した。500ms後に応答する仮のendpointに対し、`timeoutMs = 50` では `TimeoutError` で中断され、既定（10秒）では応答 `{ late: true }` を受け取ることを確かめる。修正前のコードでは第5引数が無視されるため、この回帰は失敗するはずである（コードからの推論で、修正前のコードでの実行はしていない）。

確認結果（検証済み）：この Mac で `/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` を実行し、9件成功・失敗0件、終了コード0（新しい回帰は約556ms）。本物のSafariは使っていない（endpointは試験の中の仮のHTTPサーバー）。

未確認：修正後のCIでの再実行（本物のSafariでのsession作成）はまだ行っていない。60秒で足りるか、揺れがなくなったかは未確認であり、以下の節の保存済みCI成功を今回の合格へ読み替えない。

## 現行Step26：共有workflowの再レビュー（2026-10-17）

Build and Testからの差し戻し（人の指示）に従い、U11のsource-manifestが持つ共有workflow 3ファイルをU9が直した（U9 Steps77〜79、承認済み）ことへの再確認だけを行った。U11自身の製品・起動用JS・guest・workflowは変更していない。source-manifest.jsonは3ファイルを記載済みのため変更していない。

U9が直した内容：

- `.github/workflows/u11-acceptance.yml`（build-oracle job）：checkout直後にSHA固定の `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`（`python-version: '3.15.0'`）を追加し、ゲストビルドを `bash scripts/u10-build-guests.sh target/guests/u10` から `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` へ変更した。
- `.github/workflows/u10-native-diagnostic.yml`（native-first job）：同じsetup-pythonの追加と同じゲストビルドの変更。
- `.github/workflows/ci.yml`：workflow冒頭の `env` に `PALUDARIUM_TEST_NODE: node` を追加した。

根拠：U15の `verification/u12-quality-38994430947/README.md`。run 38994430947 で `u11-programs / build-oracle` がゲストビルドの `cargo deny` で exit 1 になり（`scripts/u10-build-guests.sh` が `--advisory-policy` を渡さないため、aubeの依存修復overlayが入らない）、そのため `u11-programs / differential` は skipped だった。また、`PALUDARIUM_TEST_NODE` がないとJITの実Wasm試験がpanicする。

確認結果（検証済み）：actionlint 1.7.12（shellcheck 0.11.0を明示）で3ファイルを検査し、終了コードは1。u11-acceptance.yml と u10-native-diagnostic.yml の指摘は0件。ci.yml の指摘は今回触れていない87・203・226行目の既存4件（87行目SC2086、203行目SC1090、226行目SC1090とSC2086）だけで、変更行に新しい指摘はない。既存4件は直していない。確認時の3ファイルのSHA256は、u11-acceptance.yml `110814c31068926031cecad79cecc28c4078c257f8cd04ad2310d4a6872ed724`、u10-native-diagnostic.yml `ab30fbc6e735d42b8d8b30a34d39da6924a0e98aa2bc9099ae89ef556b9b7fad`、ci.yml `e6fa99300970910855150118c7de9f761a17a2242d33abdcfa888e473ca31c5d`。なお、gitのHEAD（7eb1819f）との差分には、上の変更のほかに以前の作業によるaction SHA・nightly版・Node版の更新も含まれる。今回はそれらを新たに検証したとは扱わない。

未確認：変更後のworkflowはまだCIで実行していない（push・CI起動は、Build and Testで人の承認を得てから行う）。そのため、U11の4環境（Node・Chromium・Firefox・本物Safari）各14ケースについて、変更後のworkflowでの新しい実行結果はない。以下の節の保存済みCI成功を、変更後のworkflowの合格へ読み替えない。

## 今回Steps23〜25：配布物修正（2026-10-14）

検証済み：package.jsonのfilesへjit-support.mjsだけを追加した。修正前の実tarball10entryは隔離importでERR_MODULE_NOT_FOUNDになり、修正後の実tarball11entryは全JS依存閉包とimportに成功した。配布物のみのJSと同梱production wasmでcreatePaludarium、固定helloのstdout `hello\n`・stderr空・exit0、同時/二重dispose、dispose後拒否と自然process終了を確認した。missing-JS・破損wasm・無効guestも拒否する新7testsはexit0。リポジトリJSへのfallbackはなく、Rust・固定guest・既存wasmは変更していない。

検証済み：公式最新Node26.11.1/npm12.2.0/Python3.15.0を確認し、不足npm/Pythonをmiseで導入した。最新実体で新7testsと既存C12/disposeを各外部60秒のprocess-group監督下で実行し、exit0/timed_out=false/process_group_cleaned=true。既存JS32testsもexit0。wasm SHAfea988…は保存production CI原本と一致、hello SHA67eeda…は固定manifestと一致する限定再利用で、新ビルドではない。

今回の証拠はverification/packaging-current-proof.jsonとpackaging-current-setup.md。最新Playwright1.64.1に対し既存lock1.64.0、Chromium準備はrev1248不在でexit1。今回の新規ブラウザー14guest、Linux coverage、ASan/LSan、3OS CIは未実行。保存結果と旧失敗は履歴として保持し、新実行へ読み替えない。品質80%下限は変更していない。

検証候補verification/verify-packed-current.pyは旧preview13入口/述語を保持し、package.jsonのjit-support挿入だけを厳密照合・旧package入力へ投影する。新test2ファイルを固定hashで照合し、別段で最新実体npm/Nodeによるfreshpackと60秒cleanupを要求する。旧367入力の成功だけを現在package成功へ流用しない。正式登録・独立レビュー・完了は親担当が扱う。現行の再実行手順は専用setupを正本とし、以下のツール版/コマンド/CI成功は各当時の保存記録である。

## 保存された修正と検証結果（2026-10-11）

大規模idle FSのdisposeがsnapshotの64MiB制限に巻き込まれる不具合を、二つの34MiBファイルで実再現した。承認済みの最小修正でPrivateFsのIdle/Active/Closed状態を単一lockで管理し、ABIのdispose成功時だけregistryを除去する。coordinatorの不要snapshot生成を廃止した。snapshot上限、active借用拒否、公開C12の二重dispose/所有/kill契約を保持する。新Rust7境界＋既存7が14/14、signedmtimeを含むfilesystem15/15、実Wasmの大規模disposeとC12が成功した。

最新ツールはNode26.11.1/Python3.15.0/Playwright1.64.0/nightly-2026-10-10/npm12.2.0。署名head `b263121214981a549ad8bfb7ddb975de03226f58` はGitHub Verified/valid。326baseline＋追加3applicationの329入力、CIが使うrecord helper2を同署名bytesへ照合した。専用CI `38103577222` は全jobs成功。fresh固定guest/native/current moduleに対し、Node26.11.1/Chromium156.0.8078.4/Firefox157.0/本物Safari26.6.2の各14が成功し、module/oracle/guest hashesの全一致を原本で確認した。U5差分43・U6差分84が成功、全5製品JS coverage420/449（93.5412%）が成功した。Workerを含む全fileの測定を確認した。証拠はverification/current-unaffected-proof.json、原本はverification/final-current-ci。CI負荷独占は未検証なので、秒数は生観測としてcurrent-timings.mdに保存する。

fresh CI module `fea98818013c28be329f48107bb2a6aa4b8faaa1c5013e3b6200f6a7c98983dd` を実package生成物へ反映し、npm12.2のpack dry-runはfilesystem-snapshot.mjsを含む10entry・wasm1個で成功した。公開はしていない。既存cacheのEPERMと新npmのJSON形式変更で止まった準備記録も保持した。同module/guest/oracleで実Node→Chromium→Firefox→本物Safari27.0.1を逐次実行し、各14成功・cleanupを確認した。既知build/npm/guest背景負荷を止めた条件と生秒数はcurrent-sequential-timing-proof.json/current-sequential-timings.mdへ保存した。OS全体の負荷独占は未検証である。

前CI `38102925303` はfresh guest/native/Wasmビルドに成功したが、U5/U6の出力ディレクトリ作成でPermission deniedとなった。差分テストと4環境consumerは未実行だった。sudoで作成された親ディレクトリを避けるため、専用CIの出力/uploadを `target/u11-shared-regressions` に揃えた。比較条件と製品は変更していない。Node付属npm11.20.0と承認済み12.2.0の差も保持し、consumerで12.2.0を明示する。

直前head `2c690e123ec2e8f28ccc672c2b0d79d7f5aa90f8` の専用CI `38102192380` はNode/Chromium156.0.8078.4/Firefox157.0/本物Safariのguest各14が成功したが、JS coverage359/449（79.955%）で失敗した。分母を保持して既存diagnosticsのshared allocator/AddressSpace/futex/TLS境界を実APIテストへ追加し、local386/449（85.97%）を確認した。最終CIの測定は別に確定する。

保存した実失敗：同製品head2cの品質CI `38102192489` はsyscall_argsが1324097回/601秒実行後、LSanで552 bytes/12 allocationsを検出して失敗した。raw.log6624/6627/6809行と成果物を保持し、旧成功へ読み替えない。独立診断CI `38103817696` は公式LLVM symbolizer24.0.0を明示し1284919回/601秒/exit0、既存抑制 `iced_x86::decoder::table_de` が12allocations/552bytesへ一致したことを実測した。旧binaryがなく旧stackの直接同定はできないため、旧失敗が同じtableだったという因果の同定は推測と明記する。製品修正・保存入力の再実行・抑制追加は行っていない。準備だけで停止した先行2runも保持する。

この最小symbolizer設定を実品質workflowへ反映した最終署名head `2b3874eabda6fe6f1d1334202421db733445fd21` はVerified/valid、CI `38104676911` の元7対象が全て601秒/exit0で成功した。全binary原本/hash・両lock不変・compiler32dba69/LLVM23.1.3・settings/抑制原本を照合した。品質syscall binaryは独立診断のdd720...と同一、ASan/LSan/symbolizer/seed/期限設定も同一である。品質run自体は1928613回・抑制件数表示なしで成功したので、独立診断の12/552を品質runの観測へ転記しない。current-quality-proof.jsonとsymbolizer-diagnosis.mdに根拠・限界を保存する。

最終headと4環境source b263は329入力中328が同一、差はu11-fuzz.ymlだけであり、4環境/JS/U5U6/packの実入力を明示結合した。品質head2cからの差はworkflow2件と新JS APIテスト1件だけで、Rust製品/試験/lock/compiler設定不変。個別3OS単体/lint/依存/Linux差分/production wasm成功はこの範囲で再利用し、旧full run failureは保持する。native coverageはworkspace10680/11475（93.07%）、U1 10208/10974（93.02%）、U3 LCOV2246/2758（81.44%）、U9 4851/5601（86.61%）、U11 5823/6723（86.61%）。wasm固有分岐全体の80%実行率は主張しない。

現行manifestは329、traceは63IDを宣言し担当外要件を上流ownerへDeferredとした。U9が直接claimするu11-fuzz.ymlの品質設定変更を明記し、U9成果物は変更していない。U9の先行完了/正式検査はこの変更後まだ再承認されておらず、親担当が正規再確認を扱う。候補正式checker verify-current-u11-repaired.pyは構文確認のみで未実行。新正式commandの人の承認・独立review・完了承認は親担当が進める。

以下の旧実装・旧CI記録は歴史であり、現行の全検証成功を意味しない。

## 今回の同時dispose修正（Steps20〜22）

検証済み：index.mjsのFS破棄は処理中Promiseを共有する。成功後は冪等、失敗後は共有Promiseを解除して再試行できる。通常FS・68MiB FSの同時呼び出し、active時の同時拒否とkill後の再試行を実production wasmで確認した。Rust、固定guest、snapshot上限は変更していない。修正前exit1と修正後exit0の原本はverification/step20-concurrent-dispose-before.jsonとstep21-dispose-results/api-supervisor.jsonに保存した。

署名head a19bea3549a77a0f665b20626d65049ecc6e2f6aは2b387から公開APIとAPI回帰の2ファイルだけを変更し、全329入力を署名bytesへ照合した。CI38118128088はattempt1のSafari session作成timeoutで失敗し、その全原本を保持した。本人の再実行後attempt2の本物Safari26.6.2が14件成功し、成功済みproducer/Node/Chromium/Firefoxは同じ時刻・artifact IDでGitHubが引き継いだ。全5を新規再実行したとは主張しない。

検証済み：同一module/oracle/guest hashでNode26.11.1、Chromium156.0.8078.4、Firefox157.0、本物Safari26.6.2の各14ケースが成功した。guestは各0〜30秒、suiteの終了・子process cleanupも成功。C12の同時dispose回帰はNode jobのsupervisor原本で成功した。JS定義scopeの全5製品ファイルは426/455行（93.626%）、未測定ファイルなし。JSON objectのkey順序を実行順へ代用せず、exact14集合と値/hashを照合し、signed runnerの実行配列を別に厳密照合した。

7ASan/LSanの601秒証拠はRust・依存・compiler・binary・設定が一致する範囲で限定再利用し、今回新規fuzzを実行したとは主張しない。旧確認スクリプトを固定hashのまま保持し、旧329入力・2helper・U2追加64claimの計395原本を署名2b387へ照合したimmutable snapshotで歴史検査を実施する。SCMのcwdは実repoへ固定し、ROOTはfinallyで復帰する。新確認候補verify-current-u11-concurrent-dispose.pyは現行2ファイルbridgeと新CIを別検査する。正式コマンド承認・独立レビュー・完了承認は親担当が扱う。セッションID競合の完全解消は未検証。

## 実装

既存production wasmと起動用JSを拡張した。guest cloneは共有Rust heap・Kernel・MMUを保持した実Workerへ割り当て、各Workerにstack/TLSを持たせる。診断Workerとguest Workerを区別し、登録・待機・join・kill・fatal cleanupの所有を接続した。製品のguest自動30秒停止を除き、テスト側で30秒期限とsuite全体600秒の回収を行う。

C12へ互換追加した`createFileSystem`/`run({filesystem})`はlauncher所有のprivate VFSを保持する。実行中のsnapshot/remove/disposeと別launcher・破棄済みhandleを拒否する。既存files既定0755を維持し、明示mode0644、terminalサイズ、絶対cwd、型付きエラー情報を接続した。Streams、終了、kill/disposeの既存契約を維持する。

人の承認を受けて最小mtime対応を追加した。MemFs既定時計はepoch0を維持し、runtimeはHostのrealtime時計を注入する。create/write/truncateとhardlinkの同一inode時刻を扱い、native statとguest stat・snapshotへ秒/ナノ秒を渡す。

## 差分検証

製品実装前のfresh Linux native14ケースと失敗した既存wasm結果を保存した。最終CIは同一ビルドのguest・module・fresh native oracleをNode、Chromium、Firefox、本物Safariへ渡す。aubeのinstall→node_modules除去→frozen→listを同じprivate VFSで実行する。stdout/stderr/exit、fixture全inventory、mode、symlink、hardlink、内容hash、#1645を照合する。

初期fixture時刻とcwd/HOME/TMPDIRを同じ値へ揃える。生成lockfile時刻は各側の実statとの整合を検査後、明示的に正規化する。公式append-only reporterを双方のinstall/frozenへ指定する変更は人が承認した。元のprogress付き不一致を生証拠として保持する。固定aubeの根拠と比較規則はfilesystem-comparison.mdを参照する。

## 検証済みと残件

検証済み：Python24件、JS29件、実wasmのC12境界、Host task/VFS mtime/kernel cwdの内部試験、workspace check・fmt・clippy、npm pack dry-run。NodeとChromiumの14ケース、公式reporterを使ったFirefox153.0の14ケースはローカル実行で成功した。Safariの準備検査はmacOS CIの実Safari26.6.2で成功した。

署名source `47a38745c37c25d66cb3c580c055c25139b0b6e3`のCI `38016346988` はFirefox probe-all期限とsyscall_args fuzz期限で失敗した。Safariは同headの制御再実行で14件成功したが、全体の完了扱いにしない。U11対象Rustの同CI LCOV集計5657/6559行（86.2479%）はこの旧sourceの観測である。native cfgの対象集計であり、wasm固有分岐の80%実行率を意味しない。

syscall_argsはfuzz専用Hostのwait_on quota不足をdecoded empty-pipe回帰で確認し、最小修正後7件成功した。Firefoxは3回のtask traceでWorker maxactive6と逐次進行を観測した。MMU候補は単体試験に成功してもLinux Firefoxの3回ずつで改善しなかった。上流Playwrightのdebugger設定が最適化wasmを無効にする根拠を確認し、隔離1.63の既定Firefoxで同一probeが3回4.50〜5.37秒で成功した。人が承認した修正に従い既存依存を1.63へ更新しMMU候補を47aへ戻した。候補専用coverage/fuzz追加は除き、元の品質下限と7対象600秒fuzz、30秒期限を維持する。最終同head全CI38021278452は成功した。詳しい生証拠はverification/syscall-wait-regression.md、mmu-read-path.md、firefox-driver-repair-proposal.mdに保存する。

source-manifest.jsonとverification/source-hashes.jsonは署名source `7eb1819f52acede33e83775374dd4ee93edf643b` の65変更パスを記録する。fuzz修正3ファイル、spike依存2ファイル、診断workflow、U10reporter比較修正3ファイルを含み、撤回MMU候補は含まない。traceability.jsonは全jobs成功のCI `38021278452` に結びdraft=falseへ確定した。正式検証コマンドの変更承認・独立レビュー・完了承認は親担当が進める。

CI38020455766ではU11の4環境が成功し、coverageはworkspace10512/11311（92.94%）、U1 10127/10897（92.93%）、U3 LCOV2246/2758（81.44%）、U9 LCOV4770/5524（86.35%）、U11 LCOV5656/6559（86.23%）だった。ただし既存U10の元reporter差分が遅いC10のheartbeat stderrで失敗したため全体は未完了。同じ承認済みappend-only比較をU10runnerへ適用し、元argvの補足生観測を保持する最小テスト修正を適用した。後述の最終署名headで全CIを再検証し成功した。

新head7ebのCI38021278452はattempt3で全jobs成功。Node/Chromium/Firefox/本物Safari各14ケースが同一module/oracle/guest hashで成功した。主生結果はverification/final-7eb-ci、最新Safari成功はverification/final-7eb-safari-attempt3（job114126928791）へ別保存し、先行Safari準備失敗を成功へ読み替えない。aube4操作の秒数と負荷条件はtimings.mdへ記録した。coverage raw job114124851606のartifact期間に一致する集計はworkspace10514/11311（92.95%）、U1 10126/10897（92.92%）。LCOVはU3 2246/2758、U9 4770/5524、U11 5657/6559（86.25%）。completeなNodeconsumerのmodule hashを検証してCI wasmをパッケージ生成物へ反映し、pack dry-runは9entry・wasm1つで成功、公開はしていない。U3とvfs_pathsは同head再実行で成功し、7対象の各600秒ASan/LSan fuzzは全成功した。既存3OS単体/lint/依存/Linux差分/production wasmも成功した。再実行履歴と準備失敗の原因未確定は保持する。

## 梱包と範囲

pack dry-runではwasm1個、起動JS、coordinator/execution/Worker補助、型宣言、README、Apache-2.0 LICENSEを含む9ファイルを確認した。READMEにCOOP/COEP、状態保持、所有、mode/cwd/terminal、停止とエラーを説明する。npmへの公開は行っていない。JIT、ホストmount、ネットワーク機能は本Unitの対象外。
