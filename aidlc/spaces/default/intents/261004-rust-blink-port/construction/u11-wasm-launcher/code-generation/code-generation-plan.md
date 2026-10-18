# U11 wasm と起動用 JS の実装計画

## Summary

- Builds: Step 29でSafariのsession作成の待ち時間の修正（Step 27と同じ内容）をやり直し、Step 30で新しい正式確認の入口（binding-04）を作る。U14の変更は先に署名head 1ceae86cとしてpush済みで、正式確認コマンドは人が採用したU2の `u2_candidate.py`（binding-03）になっている。`u11-browser-driver.mjs` はその固定する223個のcompiled sourceの1つなので、修正するとコマンドがexit 1になる。このため、2ファイルを署名付きでpushしてCIで本物のSafariを確かめた後、2ファイルの変更だけを足して許す入口を作り、人の採用の承認を受ける。人が約束したMinor（U2のREADME.mdに、旧い検査が封印時の計画・手順書だけを見ることを書く）もこの入口で直す。
- Touches: `packages/paludarium-wasm/tests/u11-browser-driver.mjs`・`u11-browser-driver.test.mjs`（Step 29）、U11の記録（code-summary.md・traceability.jsonの注記、`verification/loopback1-next/` の新しい入口とbinding-04・回帰・README.md）。製品、guest、workflow、lock、U1・U2の記録は変えない。
- Tests: 回帰1件を足して `node --test` を実行する。pushの前に差分を人に示して承認を受け、push後にCIで本物のSafariを確かめる（正式な性能測定は行わない）。新しい入口がexit 0、拒否の回帰がすべて期待どおり、正式sensor、独立再レビュー、採用の承認、checkpoint。

## 今回の対応：Step 29（Safariの待ち時間の修正のやり直し）

2026-10-17。Step 28でStep 27を取り消した理由は、`u11-browser-driver.mjs` が今の正式確認コマンドの固定する223個のcompiled sourceの1つで、変えるとコマンドがexit 1になることだった。その後、U14のLoop-back 1で、U14自身のJITの変更のために、新しい正式確認コマンドを作ることが承認された（U14 Step41）。Safariの時間切れはその後も起きている（PR CI run 39025046947 attempt 1、job 117375259180、`Safari session-creation: TimeoutError`、再実行で成功）。人は「先にSafariを直す」を選び、U14の変更と一緒にpushすることにした。

- [ ] Step 29 — 修正と確認（FR5.3、FR9.2、NFR7）。Step 27の内容を同じとおりに行う：`u11-browser-driver.mjs` の `webdriverRequest(base, method, path, body)` に第5引数 `timeoutMs = 10000` を足して `AbortSignal.timeout(timeoutMs)` に使い、`safari()` の `POST /session` の呼び出しだけ `60000` を渡す。driverの起動待ち、navigation・script-reportの要求（10秒）、suite全体の `timeout`、guest 30秒、cleanupは変えない。`u11-browser-driver.test.mjs` に、待ち時間を短く渡すと応答の遅いendpointで中断されることを確かめる回帰を1件足す。この Mac で `node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` を実行する。2ファイルの差分とSHA-256を人に示し、承認を受けてから、この2ファイルだけを1つのcommitにして署名付きで `codex/build-and-test`（親 1ceae86c）へpushし、Verifiedとheadを確かめる。CIはPR CI（push で自動）と u12-quality（本物のSafariを含む）を使う。u14-qualityは正式な性能測定を含むので起動しない。Safariのjobが時間切れなく成功することを確かめる。
- [ ] Step 30 — 新しい正式確認の入口（2026-10-18追記）。U2の `verification/loopback1-next/u2_candidate.py`・binding-03・U1のchecker・旧い封印は変えずに呼び出す新しい入口（例：`u11_candidate.py`）と binding-04 を、U11の記録の `verification/loopback1-next/` に作る。binding-03から増やす許可は、(a) 上の2ファイルを新しいheadのbytes（`git cat-file blob` と作業コピーの両方で一致）で許すこと、(b) 新しいheadの署名・親（1ceae86c）と、そのheadのCI（PR CI・u12-quality）のrunとjobの成功を、hashで固定したJSONで束ねること、(c) このStepで変えるU11の記録（code-summary.md・traceability.json・この計画・手順書）の新しいbytes、だけにする。ほかの許可・検査は弱めない。あわせて、U2の承認時に約束したMinor（旧い検査は計画と手順書を封印時のbytesでしか見ないこと）を新しい入口のREADME.mdに書く。拒否の回帰（2ファイルの別のbytes、ほかのcompiled sourceの変更、別のhead、CIの欠落・失敗、U11記録の許可外の変更）を作って実行する。code-summary.mdに「現行Step29〜30」節を足し、traceability.jsonのFR5.3・NFR7の注記を更新する（分類・targetは変えない）。正式sensor 2件を実行し、独立再レビューのあと、新しい入口のコマンドの採用を人に提示して承認を受けてから、checkpointで実行する（FR5.3、NFR3、NFR7、NFR8）。
- [x] Step 31 — 再レビュー（iteration 1・2、READY）のMinor 2件（R-08・R-09）への対応（2026-10-18、人は「60 秒のテストを足す」「hash を固定する」を指定し、U11 checkpointでRequest Changesを選んだ。Step30の入口は、checkpointに進むために仮に採用した）。
  1. `packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` に回帰を1件足す：仮のWebDriverを使って `safari()` を動かし、`POST /session` の要求にだけ60000 msの待ち時間が渡り、ほかの要求は既定の10000 msのままであることを確かめる。製品のdriverの動き（待ち時間の値）は変えない。テストのために `u11-browser-driver.mjs` に差し込み口が要る場合は、既定の動きを変えない最小の変更にし、その差分も示す。この Mac で `node --test` を実行する。
  2. 変えたファイルの差分とSHA-256を人に示し、承認を受けてから、署名付きで `codex/build-and-test`（親 2b8723ab）へpushし、PR CIとu12-qualityで本物のSafariを確かめる（u14-qualityは起動しない）。
  3. 新しい入口とbindingを新しいheadに合わせて作り直す（binding-05。2b8723abの許可を新しいheadの許可に置き換え、許すファイルはSafariの2ファイルのままにする。Step30の入口とbinding-04は履歴として残す）。新しい入口は、コマンド行の引数 `--entry-sha256 <hex> --binding-sha256 <hex>` で自分自身とbindingのSHA-256を受け取り、実際のファイルと一致しなければ拒否する。これにより2つのhashが採用されるコマンド行そのものに入り、人の採用の承認で固定される。引数がない・一致しない場合の拒否を回帰に足す。
  4. 新しいheadのCI証拠、U11の記録（code-summary.md・traceability.json）を更新し、正式sensor 2件、独立再レビューのあと、新しいコマンド行（hashを含む）の採用を人に提示し、承認を受けてからcheckpointで実行する（FR5.3、NFR3、NFR7、NFR8）。

## 前回のSummary（Step 28）

- Builds: Step 27の変更を取り消す（人の判断）。`u11-browser-driver.mjs` はU14の速さの測定で使った223個の固定ソースの1つで、正式な確認コマンド（`final_candidate.py` → `compatibility.py` の `verify_physical`）がバイトを照合するため、Step 27の後の正式な確認が `compiled source changed` で終了コード1になった（`formal-candidate-1792227065324817000-13775`）。2ファイルを Step 27 の前のバイト（git HEAD と同じ）に戻す。Safariの揺れは今回は再実行と記録で扱い、待ち時間の修正は道具の版の更新（新しい正式な確認コマンドが必要）と一緒に後で行う。
- Touches: `packages/paludarium-wasm/tests/u11-browser-driver.mjs` と `packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` を元のバイトに戻す。code-summary.md と traceability.json の FR5.3 の注記に、取り消したことを書き足す（Step 27 の記録は消さない）。それ以外は変えない。
- Tests: 新規テストなし。元に戻した2ファイルのSHA-256が git の `@-` 系列の元のバイト（`jj file show -r 7eb1819f` または codex/build-and-test の head）と一致することと、`node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs`（既存8件）が通ることを確かめる。正式sensor、独立再レビュー、正式コマンドでのcheckpoint再検証（終了コード0に戻ること）を行う。

## 今回の差し戻し対応：Step 28（Step 27 の取り消し）

- [ ] Step 28 — 取り消しと確認（FR5.3、NFR7、NFR9）。2ファイルを、Step 27 の前のバイト（fork `codex/build-and-test` の head e4f84768 にある版）に戻す。`jj --ignore-working-copy file show -r e4f84768 <path>` で元のバイトを得て、そのとおりに書き戻し、SHA-256 が一致することを確かめる。`node --test` で既存8件が通ることを確かめる。code-summary.md の冒頭に「現行Step28」節を加え、取り消した理由（正式な確認コマンドの封印、失敗した確認の出力フォルダ）、Safariの揺れの扱い（今回は再実行と記録、修正は後の作業）を書く。Step 27 の節は履歴として残す。traceability.json は分類・targetを変えず、FR5.3 の notes に取り消しを1文足す。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 前回のSummary（Step 27、取り消し済み）

- Builds: Build and TestのCIで、本物のSafariの確認がWebDriverのsession作成の段階で何度もタイムアウトした（揺れるテスト）。`packages/paludarium-wasm/tests/u11-browser-driver.mjs` の `webdriverRequest` は全要求の待ち時間を10秒に固定しており、新しいmacOSランナーでSafariを初めて起動するときに足りない。session作成の要求だけ待ち時間を60秒にする。ゲスト30秒・suite全体の期限・判定・cleanupは変えない。
- Touches: `packages/paludarium-wasm/tests/u11-browser-driver.mjs`（`webdriverRequest` に待ち時間の引数を足し、既定は10秒のまま、session作成だけ60秒）と `packages/paludarium-wasm/tests/u11-browser-driver.test.mjs`（回帰を1件足す）。製品、guest、workflow、source-manifest.json（2ファイルは記載済み）は変えない。直した後の署名付きpushとCIの再実行は、人がPRのAuto-fixで許可済み。
- Tests: 回帰1件（待ち時間の引数が渡され、既定は10秒のままであること）を足し、この Mac で `node --test` を実行する。CIの再実行で本物のSafariを確かめる。正式sensor、独立再レビュー、正式コマンドでのcheckpoint再検証を行う。

## 今回の差し戻し対応：Step 27（Safariのsession作成の待ち時間）

Build and Testで、承認を得てfork `codex/build-and-test` にpushしたCIで、`u11-programs / differential (macos-latest, safari)` が `Error: Safari session-creation: TimeoutError: The operation was aborted due to timeout; driver exit=null, signal=null, log=` で失敗した。PRゲート run 39009487698（job 117332375020）、run 39015770796 attempt 1（job 117348561712）、u12-quality run 39015780495 の attempt 1・2（attempt 2 は job 117355140969）。同じheadでも run 39015770796 attempt 2 と u14-quality run 39009460781 attempt 2 では成功しており、製品ではなく試験の道具の待ち時間が足りない揺れである（team.md：揺れたテストは記録して直す）。人は「今直す」を選んだ。

- [ ] Step 27 — 修正と確認（FR5.3、FR9.2、NFR7）。`u11-browser-driver.mjs` の `webdriverRequest(base, method, path, body)` に第5引数 `timeoutMs = 10000` を足して `AbortSignal.timeout(timeoutMs)` に使う。`safari()` の `POST /session` の呼び出しだけ `60000` を渡す。driverの起動待ち（10秒）、navigation・script-reportの要求（10秒）、suite全体の `timeout`、guest 30秒、cleanupは変えない。`u11-browser-driver.test.mjs` に、待ち時間を短く渡すと応答の遅いendpointで中断されること（既定より短い値が効くこと）を確かめる回帰を1件足す。この Mac で `node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs` を実行する。code-summary.mdの冒頭に「現行Step27」節を加え、失敗したrun・job、原因、変えた行、確認の結果、CIでの再実行はまだで未確認であることを書く。traceability.jsonは分類・targetを変えず、FR5.3のnotesに参照を足す。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 前回のSummary（Step 26）

- Builds: U11が持つ共有workflowをU9が直したため、U11は再レビューだけを受けた（承認済み）。

## 今回の差し戻し対応：Step26（共有workflowの再レビュー）

人の指示：「…同じ問題は u11-acceptance.yml・u10-native-diagnostic.yml（policy の指定なし）と u12-quality.yml（PALUDARIUM_TEST_NODE なし）にもあります。…手元への反映は、影響する Unit（U9〜U12）の再レビューを含めて正規の手順で進め、push と CI の前には承認を求めてください。」U11のsource-manifestが持つ `.github/workflows/u11-acceptance.yml`（build-oracle job：SHA固定の setup-python 3.15.0 を追加し、ゲストビルドを `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` に変更）、`.github/workflows/u10-native-diagnostic.yml`（native-first job：同じ変更）、`.github/workflows/ci.yml`（envに `PALUDARIUM_TEST_NODE: node`）は、U9のSteps77〜79で直し、承認済み。根拠はU15の `verification/u12-quality-38994430947/README.md`（run 38994430947 で `u11-programs / build-oracle` もゲストビルドの `cargo deny` で exit 1、そのため `u11-programs / differential` は skipped）。

- [ ] Step 26 — 確認と記録（FR5.2、FR5.3、FR9.1、FR9.2）。actionlintで3ファイルを検査し、変更行に新しい指摘がないことを確かめる（ci.ymlの既存4件、87・203・226行目は既存の指摘として記録し、直さない）。code-summary.mdの冒頭に「現行Step26」節を加え、U9が直した3ファイルの変更内容・根拠・確認結果と、CIでの実行はまだで（Build and Testで人の承認後）、U11の4環境各14ケースの新しい実行結果は未確認であることを書く。traceability.jsonは分類・targetを変えず、FR9.2のnotesに今回の確認の参照を足す。source-manifest.jsonは変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、正式コマンドでのcheckpoint再検証に進む。

## 今回の限定修正：Steps23〜25

ユーザーの修正指定に従い、梱包漏れと検証手順の不一致に限定する。公開は行わない。

- [ ] Step 23 — 現行packageから実際のnpm tarballを生成して展開し、jit-support.mjs欠落によるimport失敗を保存する。package.jsonのfilesへ必須ファイルを追加し、配布対象JSの相対import/export先がtarball内に全て存在する検査を追加する。回帰検査では必須ファイルを除いた隔離fixtureが失敗することも確認し、ローカルsourceの存在で漏れを隠さない。（FR5.2、C12、NFR2/NFR8）
- [ ] Step 24 — 修正後のtarballをプロジェクト内の新しい隔離ディレクトリへ展開し、リポジトリの起動JSへフォールバックせず、配布package自身のindexと同梱wasmでcreatePaludarium・hello guest・stdout/exit・dispose/Worker cleanupを確認する。破損wasm/無効guest拒否など異常系と既存C12/dispose回帰も実行する。guest30秒・監督期限・品質下限を維持する。新guest/wasmをビルドする必要があれば固定toolchainで生成しhashを保存する。現存module/guestを使う場合は署名証拠との同一性を先に照合し、新ビルドと呼ばない。（FR5.2/FR5.3/FR9.1/FR9.2、NFR1/NFR2/NFR7）
- [ ] Step 25 — Current Setupを今回の再実行手順として更新し、古いPython3.15/nightly10/旧browser版は履歴へ移す。実使用Node/npm/Python/browserと既存固定Rustのpath/version・公式最新情報・実行可能性を確認し、必要ツールはmise経由で用意する。既存rust-toolchain.tomlを維持し、保存CIの実行版と今回の版を混同しない。ブラウザー準備失敗、Linux coverage/ASan等を新規実行しない範囲は具体的に残し、保存証拠の再利用は入力hash一致範囲だけとする。新梱包検査をCI/正式検証へ接続する必要性を確認し、旧367入力の成功を変更後ソースの合格に流用せず、必要な新検証入口を具体化して変更承認へ提示する。manifest/summary/traceabilityと生証拠を確定し、独立レビューへ渡す。（FR9.1/FR9.2、NFR1/NFR8/NFR9）

## 保存された限定修正：Steps20〜22（今回の新規実行ではない）

- [ ] Step 20 — 現行公開APIの同時dispose不具合を有限な実wasmで確認し、index.mjsの処理中Promiseを共有する最小修正を行う。成功後は冪等、失敗時は共有Promiseを解除して再試行可能にする。Rust・guest・snapshot上限・公開API形状を保持する（C12、FR5.2/5.3、NFR2/7）。
- [ ] Step 21 — 同時呼び出し、大規模FS、実行中拒否と終了後の再試行を回帰で確認する。修正後の同一module／guestでNode・Chromium・Firefox・本物Safariの既存14ケースとC12を再確認し、全製品JSの定義済みscopeでcoverage80%以上を維持する。30秒・比較mask・分母・cleanupを保持する。保存ASanはRustと依存・binary・compiler・設定の一致範囲で限定再利用する（FR9.1/9.2、NFR1/2/3/7/9）。
- [ ] Step 22 — 全入力・両lock・実使用ツール・生ログ・終了コードを保存し、manifest・summary・traceabilityと正式検査を更新する。書込みを停止して独立レビューを受ける。新最終確認コマンドが必要なら具体化して人の承認後に正式実行する。旧成功・未実行・失敗を今回の合格へ読み替えない（全割当FR/NFR）。

## 入力と範囲

根拠：inception/units-generation/unit-of-work.md のU11、contract-design/contract-summary.mdのC2/C10/C12、requirements-analysis/requirements.mdのFR5.2/FR5.3/FR5.4/FR6.3/FR7.2/FR7.3/FR7.4/FR9.1/FR9.2、NFR1〜NFR4/NFR6〜NFR9。story工程省略のため直接FR/NFRを対応させる。U11固有の設計成果物は現在存在せず、共有契約と既存コードを根拠にする。

現状の読取確認：既存C12はcreatePaludarium/run/Web Streams/kill/disposeを持ち、共有Rust heapとnested Workerの実装がある。ttyはunimplemented、config_fileは初期mode指定なし。これらの観測だけで全guestの成功やguest cloneのWorker実行を証明しない。既存32-bit ABI/共有allocator/stack/TLSを詳しく棚卸しする。

U10の固定guest、専用fixture、限定ライセンス例外を継承する。Linux nativeはCIごとに同じguestバイナリで生成し、履歴の期待値を成功判定へ流用しない。既定はprivate VFS、ネットワーク禁止。ブラウザからホストmountを提供しない。JITはU14、ネイティブOS実行はU12/U13、公開はU15。C12に必要な追加は互換追加に限定し、破壊変更が必要なら実装前に人へ確認する。

## 保存された追加検証（Steps14–16、ツール版も当時の履歴）

初期監査は verification/current-audit.md。現U10署名head cb9797138313046b3cf9bbbfcab0515910b81215 / CI38095031011 の326入力は一致するが、旧U11の65入力中16変更、旧module/guest/compilerから入力が変わった。以下はこの計画の新しい承認・内容確認後に実行する。旧Steps1–13のチェックは歴史であり、現行合格を意味しない。

- [ ] Step 14: 公式最新を記録し、Playwright1.64.0（Chromium156.0.8078.4/rev1248、Firefox157.0/rev1555）、Node26.11.1、Python3.15.0、nightly-2026-10-10を検証環境へ同期する。更新箇所は既存spike package/lockとU11専用CI/config/runnerに限定し、ツールのライセンス/供給元、実体path/version、source-before/afterと326入力からの差を記録する。最新Pythonで準備/内部テストを再実行し、実browserのCOOP/COEP/Worker準備を成功させる。idleの二つの34MiBファイルを持つFSのsnapshot/disposeを外部有限監督下で限定再現し、失敗なら具体的最小修正を親へ報告する。この手順は製品修正を自動承認しない。（FR5.2/FR9.2、NFR2/NFR7/NFR8/NFR9）
- [ ] Step 15: 元の固定aube/probe sourceとlock、限定CDLA例外/製品denyを維持し、同じ新guestバイナリのfresh Linux nativeと現production wasmを同じ署名headで生成する。4環境へ同一hashを配り、元14ケース、stdout/stderr/exit/full filesystem/#1645/同一VFS状態保持を照合する。元のreporter/fixture0644・epoch0・cwd/env・time正規化・未定義値mask・C12既定/kill契約を保持する。guest30秒/suite600秒と全Worker/driver/process cleanupを守る。現共有ノードのU5/U6/U8単体・Linux差分を含む既存3OS/整形/clippy/依存4監査/production wasmとworkspace・U11 Rust/既存範囲80%を維持し、launcher全製品JS定義範囲80%を追加測定する。元7fuzz対象の依存/両lock/compiler/LLVM/settings/LSan suppression/instrumented binaryを保存成功へ厳密照合し、必要ならbuild-onlyで再結合する。一致しない対象だけ同じ600秒/入力30秒ASan+LSanを実行し、終了検査/exit/source一致を確認する。旧成功やbuild-onlyをfresh実行と数えない。（FR5.3/FR5.4/FR6.3/FR7.2/FR7.3/FR9.1/FR9.2、NFR1〜NFR4/NFR7〜NFR9）
- [ ] Step 16: 既知バックグラウンド負荷を止めて4環境のaube4操作を逐次記録し、同一headのmodule/guest/oracleと条件を結び付ける。fresh CI moduleをpackageへ反映してnpm pack dry-runを確認する（公開しない）。最新のtool/source/hash/raw artifactと326baseline＋実変更inventory、strict source-manifest、全割当FR/NFR対応trace、summaryを確定する。未検証/失敗/旧履歴を保持し、JS/Rust coverageとsanitizer再利用の適用範囲を明記する。親が新正式検証commandの具体化・人の変更承認・独立レビュー・U11完了承認を扱う。（FR5.2/FR7.4/FR9.1/FR9.2、NFR1/NFR6/NFR8）

## 大規模FS disposeの限定修正（Steps17–19、承認待ち）

検証済みの再現と具体案は verification/dispose-current-proposal.md。Steps14–16は保持し、その重いCI開始前にこの修正を実施する。snapshotの64MiB上限、C12の所有/active借用拒否/idempotence、guest30秒/suite600秒は変更しない。

- [ ] Step 17: 現行Wasmでidle 34MiB×2のcreate成功・snapshot拒否・dispose拒否という保存済み期待結果を確認する。PrivateFsのactive/stale判定を一つの状態lockで保持し、close成功後の既存Arcからのacquire/snapshot/removeも拒否する最小状態追加を実装する。filesystem_drop ABIは成功/拒否を返し、active時にはregistryを除去しない。coordinatorはsnapshotを生成せずこの結果だけでdispose応答を返す。（FR5.2、C12、NFR2/NFR7）
- [ ] Step 18: 実装後に正常idle・大規模idle・active拒否後の解放・stale拒否・二重dispose・close後acquire拒否・snapshot/remove拒否を含む7件以上のRust内部境界と実production moduleのJS API回帰を追加する。既存C12の所有違い/kill/借用テストを維持する。影響sourceと元7ASan依存を再照合し、不一致対象だけ承認済み600秒条件で実行する。新しいfresh moduleでSteps15の4環境14ケース・3OS・Rust/JS80%を満たす。（FR5.3/FR9.2、NFR1〜NFR4/NFR8）
- [ ] Step 19: 326baseline＋今回実変更、ABI内部結果と公開C12互換性、失敗再現/修正後証拠をsource/hash/traceへ記録する。Steps16のfresh pack/タイミング/正式command変更承認・独立review引渡しを実施する。未実行の判定を成功にしない。（FR9.1/FR9.2、NFR7/NFR8）

## 旧実装手順（Steps1–13、歴史として保持）

- [ ] Step 1: C2/C10/C12と既存wasm ABI・Worker所有・guest clone/futex・stdio・VFS状態を棚卸しする。ゲストスレッドと診断用Workerを区別し、共有Kernel/MMU/allocatorと個別stack/TLSの所有を明文化する。契約の自動timeoutなしと既存30秒watchdogの差も整理し、製品APIはkillによる停止、テストは外部期限という契約を満たす。（FR5.2/FR5.4、NFR2/NFR7）
- [ ] Step 2: U11専用runner/configを最小構成で作り、準備検査を成功させる。既存Node/実Safari手段を再利用し、Chromium/Firefoxを加える。各runコマンドをunit-test-instructions.mdへ確定する。（FR9.2、NFR7/NFR8）
- [ ] Step 3: 製品変更前に同一固定probe8項目＋all/environment、aube4操作のLinux native期待結果を生成する。fixtureの0644、args/env、node不在、#1645、stdout/stderr/exit、ファイル状態、正規化規則とhashを保存する。aube install→node_modules除去→frozen→listを同じセッション/VFSで成立させる境界を定義し、現wasmの不一致を保存する。（FR6.3/FR7.2/FR7.3/FR9.1、NFR1/NFR4）
- [ ] Step 4: wasm Hostの時計・乱数・待機・stdio・terminalの不足を実装し、各変更部品に7件の内部単体/境界テストを実装後に追加する。正常と2種以上の異常・境界を含める。Host以外へ直接ホスト機能を漏らさない。（FR5.2、NFR2/NFR4）
- [ ] Step 5: guest cloneを実際のWorkerへ割り当て、共有Session/Kernel/MMUの同一性、個別stack/TLS、futex wait/wake、子終了・join・killを実装する。診断だけの共有メモリ成功と区別し、実guestのrayon/mutex-condvar/tokioをStep3の期待値に照合する。変更部品ごと7内部テストと並行・終了・エラーの統合ケースを持つ。（FR5.4/FR6.3、NFR1/NFR2/NFR7）
- [ ] Step 6: ABIへ必要な初期file mode・terminal・VFS操作を検証付き互換追加で接続する。既存files既定0755を維持し、fixtureだけ0644にする。aube4操作で状態保持とnode_modules除去を実現する最小APIを選び、追加型/所有/権限を文書化する。必要があればprivate VFSの全4操作をU10でも追加照合し、製品不一致は保存して修正範囲を確認する。（FR7.2/FR7.3、NFR1/NFR4）
- [ ] Step 7: C12のTypeScript宣言、入力検証、Streams、ゲスト終了とエミュレータエラー（rip/bytes/syscall含む）、kill/disposeを完成する。境界8ケースを追加し、既存利用者と同時更新する。npm名は既存@paludarium/wasmを維持する。（FR5.2、C12、NFR2/NFR7）
- [ ] Step 8: 同一wasm/guestハッシュ、COOP/COEP付き共通ページとNode WorkerでU11差分を実行する。stdout/stderr/exitとfilesystem、probe全PASS、#1645を確認する。各guest操作はテスト側30秒で停止・子Worker回収。失敗と期限切れも成果物へ保存する。（FR5.3/FR6.3/FR7.2/FR9.2、NFR1/NFR4/NFR7）
- [ ] Step 9: Linux CIでfresh native＋同一wasmのNode/Chromium/Firefox、macOS CIで本物Safariを必須実行する。SafariはWebKit代替を使わず同じCI生成module/oracleを取得する。action SHA固定、依存監査と隔離を維持する。Safariが実行できない場合は未検証と記録し、成功へ読み替えない。（FR5.3/FR9.1/FR9.2、NFR8/NFR9）
- [ ] Step 10: 既存3OS単体/lint/依存/Linux差分/production wasmと各既存80%coverage下限を維持する。変更Rust部品はLinuxで80%行coverage、JSの新規内部部品も7件ずつ試験する。変更がfuzz対象へ及ぶ場合は依存一致を検査し、必要な既存600秒ASan/LSan検証をCIで再実行する。品質下限を下げない。（NFR1〜NFR3/NFR8/NFR9）
- [ ] Step 11: 4環境のaube4操作のwall timeを既知バックグラウンド作業終了後に逐次計測し、負荷条件・source/module/guest hashを保存する。CheerpX1.3.9の既存資料値と条件を並記し、異なる条件の速度比や合否閾値を作らない。（FR7.4、NFR6）
- [ ] Step 12: パッケージにwasm1つ＋起動JS/必要Worker群/型宣言/licenseを含むことをpack dry-runで確認する。README、C12使用例、COOP/COEP要件、失敗/cleanup/状態保持、実測範囲を説明する。公開は実行しない。（FR5.2、C12、NFR8）
- [ ] Step 13: 全変更source-manifest、FR/NFR対応traceability、実装サマリと生証拠を確定し、jjで署名コミット・CIとの同一性を照合する。正式verification commandは具体化後に変更承認を取得し、独立レビューとU11完了承認へ進む。（FR9.1/FR9.2、NFR1）

## 検証の境界

同じ承認済み公式reporter方針を既存U10差分runnerにも適用する。cases.jsonとnative APIの既定は保持し、差分runnerの比較用コピーでinstall/frozen双方のargvへappend-onlyを加える。厳密stdout/stderr/exit照合の後、元argvを別fixture/native観測で補足実行し、生stderrを保存しながらexit/stdout/timeout/probe/#1645を確認する。製品挙動・期限・品質下限は変更しない。verification/u10-reporter-regression.mdへ失敗と回帰試験を保存する。

承認済み修正（Firefox検証器）：Playwrightを既存spike依存の1.63.0へ固定し、対応ブラウザで既定設定の同一guestを検証する。1.62のFirefox debuggerが最適化wasmを無効にする上流原因と、隔離1.63の同一probe 3回成功を根拠とする。効果のなかったMMU候補2ファイルは署名済み47a38745の実装へ戻し、候補だけに追加したMMU coverageとmmu_ops/mmu_u2/cpu_u2の追加fuzzを除く。元のcoverage下限と7対象600秒fuzz、30秒期限は維持する。独立したsyscall_argsテストHostの待機quota修正と7回帰は残す。製品設定・browser prefs・profilerで合格を作らず、4環境14ケースのfresh同一head CIを必要とする。詳細はverification/firefox-driver-repair-proposal.md。

モックは内部異常系のみに使い、実Worker・native・browserの合格へ代えない。成功証拠はsource/module/guest/oracle/runごとに紐付ける。実行不能・未実装・不一致は未検証/GAPとして残し、全入力/全browser版の保証を主張しない。追加依存はライセンスと供給元を確認し、限定guest CDLA例外を製品へ流用しない。

## Testing Contract

```json
{
  "version": 1,
  "methodology": "custom",
  "source": "team",
  "ordering": "命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
  "scope": "rust-blink-port",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "私たちはテストを各 Bolt の成果物の一部として扱います。エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まるので、差分テストを中心に置きます。\n\n- **Methodology**: custom\n- **Ordering**: 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。\n\n補足：\n\n- **カバレッジ**（Q5）：行カバレッジ 80% を下限にします。測るのはネイティブの Linux です。あわせて「範囲内の命令のうち、差分テストが 1 件以上ある命令の割合」を記録します。決めた下限は Build and Test で下げません。\n- **差分テストの期待結果**（Q6）：期待結果は、**CI を実行するたびに x86-64 Linux のランナーで作り**、エミュレータの結果と比べます。期待結果をリポジトリに保存する方式は取りません。\n  - 比べるもの：命令の単位ではレジスタ・フラグ・メモリ、プログラムの単位では標準出力・標準エラー・終了コード。\n  - x86 で結果が未定義のフラグや値は比べません。命令ごとに「比べないもの」を表で持ちます。\n  - pid・時刻・乱数・アドレスなど、実行ごとに変わる値は、比べる前にそろえるか、比べる対象から外します。\n  - 段階 5 では、JIT ありと JIT なし（インタプリタ）の結果も同じ差分テストで比べます。JIT だけの意味論は持ちません。\n- **単体テスト**：層ごとに `cargo test` で書きます。テストやビルドの道具は外部のものを使ってよいです（Q1）。\n- **CI のゲート**（Q7）：\n  - 変更のたび（PR）：Linux・macOS・Windows の単体テスト、lint（`cargo fmt --check`、clippy の警告はエラー）、依存の検査（ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること、既知の脆弱性）、x86-64 Linux での差分テスト。通らなければマージしません。\n  - 段階ごと：その段階に入ったら、その段階の probe と aube の合格を必須にします。\n  - 夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）。失敗したら Issue にして直します。\n- **Safari**（Q12）：Safari での合格は、macOS の CI で本物の Safari を動かして確かめます。WebKit を使う別のテスト用ブラウザでは代えません。\n- **wasm**：paludarium が用意する起動用 JS とテストハーネスで、Node.js の Worker とブラウザ（Chromium 系・Firefox・Safari）で同じテストを動かします。テスト用のページには COOP/COEP の見出しを付けます。\n- **揺れるテスト**：スレッドを使うテストには時間切れの上限を付けます。揺れたテストは記録して直します。\n- 段階 5 の「JIT なしより速い」は、回数・統計量・差の大きさを要件分析で数値にしてから測ります。速さの測定は PR のゲートにしません。\n- Test Strategy は Standard です。量と種類はこの設定に従い、上の補足はそれに足すだけです。"
    },
    {
      "layer": "project",
      "text": "- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) \n\n- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) \n\n- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) \n\n- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) \n\n- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) \n\n- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) \n\n- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) \n\n- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) \n\n- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) \n\n- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) \n\n- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) \n\n- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) \n\n- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) \n\n- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) \n\n- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) \n\n- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) \n\n- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) \n\n- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) \n\n- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) \n\n- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) \n\n- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) \n\n- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) \n\n- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) \n\n- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) \n\n- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) \n\n- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) \n\n- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) \n\n- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) \n\n- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) \n\n- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) \n\n- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) \n\n- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) \n\n- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) \n\n- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) \n\n- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) \n\n- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) \n\n- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) \n\n- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) \n\n- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11)"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "custom",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Custom ordering - 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
      "Implementation and tests - preserve that exact ordering; do not convert it to layer-local TDD.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cc8e6bbb985d32c580aff1d457ccafb5f05a4b442140eb6cb6303d51ca2ba418",
  "contract_sha256": "sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5"
}
```

