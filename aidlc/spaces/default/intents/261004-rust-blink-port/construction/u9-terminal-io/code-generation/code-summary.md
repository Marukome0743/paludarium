# U9 現行公開端末契約と検証

## 現在の状態（2026-10-19 JST、Step82）

本節はStep82の記録である。U15のStep22〜28で製品のファイルが変わってfork `codex/build-and-test` へ送られた（head 27d05de1、e3c29d1d→8b415a7c→8360be2e→27d05de1、4つともVerified）ので、U9を確かめ直した（`reviews/review-16.md`、READY、Minor 4）。checkpointで人がRequest Changesを選んだので、U9の記録で直せる3件（R-13・R-14・R-16）を直した。U9の製品のコード・CI・workflow・ほかのUnitの記録・traceability.jsonは変えていない。

- **今の正式な確認コマンド（R-16）**：`aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の U15 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用、command SHA-256 `00f5c883…a159`）。下の節に出てくる正式なコマンドや入口（U2の `u2_candidate.py` など）は、それぞれの時点のもの（履歴）である。U9のcheckpointはentry-fで確かめる。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べるので、U9の記録の変更はその結果に影響しない想定である（結果はcheckpointの記録が持つ）。
- **U9に関わる製品の変更**：U9のsource-manifestにあるworkflowのうち、`ci.yml`（`push` は `main` だけ）、`u11-acceptance.yml`（Safariのjobに暖機の手順、`continue-on-error: true`）、`u11-fuzz.yml`（古い作業ブランチの `push` を外した）が変わり、9つのworkflowが消えた（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）。U9の製品のコードは変わっていない。
- **U9の受け入れに要るものは残る**（review-16の確かめた点）：`ci.yml` の差分のjob（`diff_u9` を含む）とU9のcoverage 80%、`ci.yml` から呼ぶ `u11-acceptance.yml`（Node・Chromium・Firefox・実Safariの14ケース）と `u10-native-diagnostic.yml`。`pull_request` の起動は残る。27d05de1のCI 8 runはすべて成功した（U12は人が認めた1 jobの再実行。記録はU15の `verification/ci-27d05de1/`）。
- **source-manifest.json（R-13）**：writesから、27d05de1で消えた9つ（`.github/workflows/` の `native-diagnostic.yml`・`u11-firefox-diagnostic.yml`・`u11-native-first.yml`・`u2-production-sanitizers.yml`・`u5-quality.yml`・`u6-native-diagnostic.yml`・`u6-quality.yml`・`u8-native-diagnostic.yml`・`u9-current-verification.yml`）を外した（37件→28件）。ほかのpathは変えていない。
- **R-14**：下の「履歴：Steps77〜78」節の「変更した3 workflowは未実行」はその時点の記述である。3つ（`u11-acceptance.yml`・`u10-native-diagnostic.yml`・`ci.yml`）は27d05de1のCIで動いて成功した。
- **R-15（次のpushで扱う）**：`.github/scripts/u9-source-audit.py` は、呼び元の `u9-current-verification.yml` が消えたので、どこからも呼ばれない。製品のファイルで、消すと正式な確認コマンドがhead 27d05de1との違いで拒否するので、次の製品の変更のpushで扱う。
- 「現行」で始まっていた見出しは「履歴：…（作成時の見出しは「…」）」にした。本文は変えていない。
- 未検証：この作業ではentry-fを実行していない（checkpointで実行する）。独立再レビューはこの記録の後に行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：Steps77〜78：共有workflowのゲストビルドとJIT試験のNode指定（作成時の見出しは「現行Steps77〜78：共有workflowのゲストビルドとJIT試験のNode指定」）

### 変更した3行

Build and Testの準備中の人の指示（fork branch `codex/u15-macos-native`、commit ce0b746 で `u12-native-first.yml` のゲストビルドを揃えたこと、同じ問題が `u11-acceptance.yml`・`u10-native-diagnostic.yml` にもあること）に従い、U9のsource-manifestに含まれる次の3ファイルだけを1行ずつ変えた。

| ファイル | 行 | 変更前 | 変更後 |
|---|---|---|---|
| `.github/workflows/u11-acceptance.yml` | 24 | `run: bash scripts/u10-build-guests.sh target/guests/u10` | `run: python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` |
| `.github/workflows/u10-native-diagnostic.yml` | 41 | `run: bash scripts/u10-build-guests.sh target/guests/u10` | `run: python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` |
| `.github/workflows/ci.yml` | 22（workflowの `env`） | （なし） | `PALUDARIUM_TEST_NODE: node` |

- ゲストビルドの行は、be45b36cで成功している `.github/workflows/u14-native-first.yml` 53行目と同じコマンド（ce0b746の `u12-native-first.yml` と同じ形）である。`ci.yml` の行は `.github/workflows/u14-quality.yml` 21行目と同じである。
- `ci.yml` の行は人の指示の4ファイルに含まれないが、同じ原因（`PALUDARIUM_TEST_NODE` 不在）で通常CIの3OS単体試験とcoverageが失敗するため、承認済み計画Step 77に明示して足した。
- 閾値・mask・対象・他の行、actionのSHA固定、権限は変えていない。製品source、試験、スクリプト、他Unitの記録、`source-manifest.json` も変えていない（3ファイルは記載済み）。U12の `u12-native-first.yml`・`u12-quality.yml` はU12で扱う。

### 根拠

- U15 `construction/u15-release/code-generation/verification/u12-quality-38994430947/README.md`（run 38994430947：ゲストビルドでaubeの `cargo deny` がexit 1、`PALUDARIUM_TEST_NODE` 不在でJITの実Wasm試験9件とdiff_u14がpanic）。
- U15 `construction/u15-release/code-generation/verification/u12-workflow-fix-proposal.md`。

### この Mac での確認（実際の出力と終了コード）

- actionlint（承認済みコマンド、actionlint 1.7.12）：`/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint .github/workflows/u11-acceptance.yml .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml` は **終了コード3**。actionlintが呼んだmiseの `shellcheck` shimに版が設定されていない（`mise ERROR No version is set for shim: shellcheck`）ための実行失敗で、workflowの指摘ではない。期待した「指摘なし・終了コード0」は得られていない。
- 補足の確認（承認済みコマンドの代わりではない）：同じactionlintと3ファイルに `-shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck` を足して実行すると **終了コード1**。指摘は `ci.yml` の4件だけで、どれも今回変えていない行である：87行目 SC2086（info）、203行目 SC1090（warning）、226行目 SC1090（warning）とSC2086（info）。`u11-acceptance.yml`・`u10-native-diagnostic.yml` の指摘と、YAML・式・action参照の指摘は0件。この4件は計画の範囲（他の行を変えない）外なので直していない。
- JIT単体試験（承認済みコマンド、rustc 1.101.0-nightly (6f5da406b 2026-10-10)、Node v26.12.0）：`env PATH="$HOME/.cargo/bin:$PATH" PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node cargo test --locked -p paludarium-jit --lib bridge::tests::` は **終了コード0**、19 passed／0 failed／38 filtered out。計画の「57件」はこのフィルタの件数ではなく、crateのlib試験の全件数（19＋38）である。
- 補足：同じenvで `cargo test --locked -p paludarium-jit --lib -q` を実行し、**終了コード0**、57 passed／0 failed。どちらもビルド済みのものを使った（製品sourceは変えていない）。

上の2つ（終了コード3と、補足の終了コード1）はSteps77〜78の時点の記録として残す。

### Step 79（追加）：Pythonの準備とactionlintの扱い

承認済みの追加計画Step 79に従い、次の2か所だけに3行ずつ足した。他の行は変えていない。

| ファイル | job | 位置 | 足した行 |
|---|---|---|---|
| `.github/workflows/u11-acceptance.yml` | `build-oracle` | `actions/checkout`（`persist-credentials: false`）の直後、15〜17行目 | `uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`、`with:`、`python-version: '3.15.0'` |
| `.github/workflows/u10-native-diagnostic.yml` | `native-first` | `actions/checkout`（`persist-credentials: false`）の直後、30〜32行目 | 同上 |

- 足した3行は `.github/workflows/u14-native-first.yml` 25〜27行目と同じで、actionはコミットSHAで固定している。これでゲストビルドの行（u11-acceptance.yml 27行目、u10-native-diagnostic.yml 44行目。追加により3行ずれた）が使う `python` は3.15.0になる。
- `ci.yml`・権限・閾値・他のjob、製品source、試験、スクリプト、他Unitの記録、`source-manifest.json` は変えていない。

Step 79の後にこのMacで実行した結果（承認済みの現行instructionsのコマンド）：

- actionlint 1.7.12（shellcheck 0.11.0を明示）：`/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u11-acceptance.yml .github/workflows/u10-native-diagnostic.yml .github/workflows/ci.yml` は **終了コード1**。`u11-acceptance.yml`・`u10-native-diagnostic.yml` の指摘は0件。`ci.yml` の指摘は今回触れない行の既存4件だけで、新しい指摘はない。期待した結果と一致する。
- JIT単体試験：`env PATH="$HOME/.cargo/bin:$PATH" PALUDARIUM_TEST_NODE=/Users/mutoakio/.local/share/mise/installs/node/26.12.0/bin/node cargo test --locked -p paludarium-jit --lib` は **終了コード0**、57 passed／0 failed／0 ignored（実Wasmのbridge試験を含む）。ビルド済みのものを使った。

### Step 80（差し戻し）：差分jobへのheadの受け渡し

Build and Testで、承認を得てfork `codex/build-and-test` にpushしたCIで、`U10 fixed guests and fresh native differential / differential` が失敗した。

- 失敗したrun・job：PRゲート run 39009487698 の job 117332287585、u12-quality run 39009464565 の job 117331520277。
- 原因：`tests/guests/u10/differential.py` から呼ばれる `tests/guests/u10/evidence.py` 170〜171行目が、ゲストビルドの記録の `ci_head` と `os.environ.get('GITHUB_SHA')` を照合し、`ValueError('overlay artifact CI head binding mismatch')` を出した。`tests/guests/u10/build.py` 82行目は advisory policy 付きのとき `receipt['ci_head'] = os.environ.get('GITHUB_SHA')` を記録するが、差分の手順は `sudo unshare --net env ...` で起動しており、sudo が `GITHUB_SHA` を引き継がないため、差分側では値がない。Steps77〜79で policy を付けたことで、初めてこの照合が働くようになった。
- 変えた行（1行だけ）：

| ファイル | job・手順 | 行 | 変更前 | 変更後 |
|---|---|---|---|---|
| `.github/workflows/u10-native-diagnostic.yml` | `differential`・「Fresh native oracle then bounded C10 differential without network」 | 86 | `sudo unshare --net env PATH="$u10_bin:$PATH" RUSTC=...` | `sudo unshare --net env GITHUB_SHA="$GITHUB_SHA" PATH="$u10_bin:$PATH" RUSTC=...` |

- 変更後の行は `.github/workflows/u14-native-diagnostic.yml` 83行目と同じ形である。他の行、製品source、試験、スクリプト、他Unitの記録、`source-manifest.json`（記載済み）は変えていない。
- このMacでの確認：`/Users/mutoakio/.local/share/mise/installs/actionlint/1.7.12/actionlint -shellcheck /Users/mutoakio/.local/share/mise/installs/shellcheck/0.11.0/shellcheck-v0.11.0/shellcheck .github/workflows/u10-native-diagnostic.yml` は **終了コード0**、指摘0件。期待した結果と一致する。
- 未確認：この修正の後のCIでの再実行はまだで、差分jobが通るかは未確認である。署名付きpushとCIの再実行は、人がPRのAuto-fixで許可済みのBuild and Testの手順で行う。

### 既存の指摘（直していない）

`ci.yml` の次の4件は、今回の変更より前からある指摘で、計画の範囲（今回触れない行は変えない）の外にあるため直していない。

| 行 | 規則 | 重さ |
|---|---|---|
| 87 | SC2086（引用符なしの変数展開） | info |
| 203 | SC1090（定数でない `source`） | warning |
| 226 | SC1090（定数でない `source`） | warning |
| 226 | SC2086（引用符なしの変数展開） | info |

### 未確認のこと

- 変更した3つのworkflowは、まだCIで実行していない。push・CIの起動はしていない。CIでの確認はBuild and Testで人の承認を得てから行うので、それまでは未確認である。
- Step 79で `actions/setup-python`（3.15.0）を足したが、そのPythonで `build.py` の `u15-fixed-aube-zip9-name` が2つのworkflowで動くか、ゲストビルドとaubeの `cargo deny` が通るかは、CIで確かめるまで未確認である。
- actionlintの終了コードは、`ci.yml` の既存4件のため1のままである（0ではない）。

## 履歴：Steps74〜75：coverage再集計のcompiler・lockへの結合とR-04・R-05の訂正（作成時の見出しは「現行Steps74〜75：coverage再集計のcompiler・lockへの結合とR-04・R-05の訂正」）

### (a) compiler・lock・toolchainへの結合（R-02）

- 出典：Step72の結果 `verification/step72-u9-coverage-recount.json`（SHA-256 `4f1996981b424ba79422c50b564b809327bf216b955f5ad737a2546ded325bc1`）を読み取り専用で参照し、head `be45b36ce9d7a65719ba1f86cf6a0b018070741b`・run `38897611874`・job `116962253357` と3集合の値（旧13 2745/3251=84.44%、追加10 2154/2382=90.43%、全23 4899/5633=86.97%、いずれも80%以上）を再計算せずに引き継いだ。U15 verification `full-quality-1792153236541522000/run.json`（SHA-256 `b23028b808198c55261c56a38b5cb8930d9afc566bb871ae9c48ccebcc4550b6`）の `head_sha`・`head_commit.id` はbe45b36cと、`id` は38897611874と一致した。
- compiler：保存jobログ `job-116962253357.log`（SHA-256 `9c2f415eca2f6f50303a00a8e47ae1065e6f97f19dce90133b1b3e223f2f5d6d`）のrust-cache設定「Rust Versions」には、次の2行が記録されている。
  - `1.101.0-nightly x86_64-unknown-linux-gnu 6f5da406b56c2db6607202b63daee73aa8c61297`
  - `1.99.0 x86_64-unknown-linux-gnu b940084d7eb6a299eb4bfeb8e34901bc051e7ac4`
- jobログで分かるのは、rust-cacheが認識したtoolchainの版だけである。cargo llvm-covが実際に呼んだrustcの `-vV` 出力ではなく、2行のどちらがcoverageのビルドに使われたかもjobログからは確定しない。
- head be45b36cのbytesは `jj --ignore-working-copy file show -r be45b36ce9d7a65719ba1f86cf6a0b018070741b <path>`（読み取り専用）で取得し、作業コピーの同じファイルと比べた。

| パス | headのSHA-256 | 作業コピーとの一致 |
|---|---|---|
| `Cargo.lock` | `7d6e3daf90b93b97362e53ca63f8a0b18805f898e92c7d394a944941b62431a7` | 一致 |
| `fuzz/Cargo.lock` | `975f853836e161de8e71e46c0bca988ab9b7a0ece649e4d95c204695249c919b` | 一致 |
| `rust-toolchain.toml` | `44aa4c6a2433d14ec3af5705ec2176326051eb201e0be807a05dc333ee8b16ea` | 一致 |

- headの `rust-toolchain.toml` のchannelは `nightly-2026-10-11` である。
- jobログの「Lockfiles considered」には `Cargo.lock` と `rust-toolchain.toml` が含まれ、`fuzz/Cargo.lock` は含まれない（このcoverage jobのキャッシュ鍵は `fuzz/Cargo.lock` を見ていない）。jobログにはどのファイルのSHAも記録されていない。
- このjobは、jobログ364行目（`Restored from cache key "v0-rust-coverage-Linux-x64-e120b189-6c223cb7" full match: true.`）のとおり、`target/` をrust-cacheから復元している（full match）。そのため、head be45b36cのbytesとの結合はcheckoutした入力に対するものであり、全オブジェクトがこのjobで再ビルドされたことの証明ではない。

### (b) DA行数とTOTAL行数の差（R-04）

- lcovのDA行数（全23ファイル合計）5633と、jobのllvm-cov表のTOTAL行数5707の差は74行である。差の原因は確認していない（`cause: unconfirmed`）。Steps72〜73節の該当文も「原因は未確認」に言い換えた。

### (c) Step72 JSONの `lock_sha256` 欄の訂正（R-05）

- Step72 JSONの `lock_sha256` 欄には、ハッシュではなく未照合の文が入っている。また、その文の「wasm lock」は `fuzz/Cargo.lock` の誤称である。Step72 JSONは変更せず、訂正先をStep74 JSONの `lock_sha256_by_path` とした（同JSONの `step72_correction` に注記）。

### 実行と範囲の限定

- スクリプト：`verification/step74_u9_coverage_binding.py`（Python 3.15標準ライブラリのみ、引数なし）。結果：`verification/step74-u9-coverage-binding.json`（排他作成、`passed: true`、`failures` 0件、`new_ci_run: false`）。実行は終了コード0。
- 新しいCI実行・push・外部送信は行っていない。Linux差分・Node／Safari・ASanの新しい実行、全経路差分、U15の受理の証拠ではない。compilerはrust-cacheが認識した版の記録に限る。Step72のスクリプト・結果JSON、製品source、既存試験、旧証拠、`source-manifest.json`、CI設定は変更していない。

## 履歴：Steps72〜73：U9固有coverageの現行再集計と.gitignoreの位置づけ（作成時の見出しは「現行Steps72〜73：U9固有coverageの現行再集計と.gitignoreの位置づけ」）

### (a) U9固有coverageの現行再集計（R-02）

- 出典：署名済み現行head `be45b36ce9d7a65719ba1f86cf6a0b018070741b` の公式品質CI run `38897611874`（job `116962253357`「line coverage >= 80%」、conclusion success）。同jobが既存U9 coverageコマンド（packages・`--ignore-filename-regex`・`--fail-under-lines 80` 不変）で公開した artifact `u9-coverage-lcov`（id `12045136773`、digest `sha256:6b27a74d30f7286afb693713ecaa390752d0d12d7f4587445652314f0f10d5ef`）を、U15 verification `full-quality-1792153236541522000/` の保存原本から読んだ。保存ZIPのSHA-256はdigestと一致し、ZIP内 `u9-coverage.lcov` のSHA-256は `41bc3f7b336b180ae6ed68e02dac572e2d33f25d5822e93671631ada4c9bd1b6` である。
- 集計（lcovのDA行。各ファイルはSF 1件に一意に対応し、欠落・重複・統合なし。lcov全23 SFが23パスと一致）：

| 集合 | カバー行／行数 | 割合 | 80%下限 |
|---|---|---|---|
| 旧13ファイル（`step20-fixed-proof.json` の `coverage.original13.paths`） | 2745/3251 | 84.44% | 合格 |
| 追加10ファイル（同 `coverage.additional10.paths`） | 2154/2382 | 90.43% | 合格 |
| 全23ファイル | 4899/5633 | 86.97% | 合格 |

- 同jobログのU9 coverage stepのTOTAL行はLines 5707・Missed 767・86.56%で、lcovのDA行数5633との差（74行）の原因は未確認である（両方を結果JSONに記録し、同一とは扱わない）。jobログに実rustcの版は出力されておらず、compilerは未照合である（Steps74〜75で結合。現行Steps74〜75節を参照）。両lockのSHA-256もjobログに記録がなく、今回はinputs原本も読んでいないため未照合と明記した（結果JSONの `lock_sha256` 欄の「wasm lock」という表記は2つ目のlockの呼び名の誤りで、未照合という判定は変わらない）（Steps74〜75で結合。現行Steps74〜75節を参照）。
- スクリプト：`verification/step72_u9_coverage_recount.py`（Python 3.15標準ライブラリのみ、引数なし）。結果：`verification/step72-u9-coverage-recount.json`（`passed: true`、`new_ci_run: false`）。実行は終了コード0。
- 新しいCI実行・push・外部送信は行っていない。旧541b値（head `541b4396…`、run `38062686224`：旧13 2693/3202=84.10%、追加10 2156/2397=89.95%）は保存観測の履歴として保持し、今回の値で置き換えない。

### (b) `.gitignore` の位置づけ（R-03）

- `.gitignore` はU9の `source-manifest.json` の外にある、ビルドに使わない共有パスである。
- 2026-10-16のClaude Code harness追加で、そのAI-DLCブロックへ `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行が入り、これが再確認のきっかけになった。
- この変更はU9の製品コード・テスト・端末契約のどれにも影響しない。

### 範囲の限定

- 今回の結果はU9固有coverageの現行値だけである。Linux差分・Node／Safari・ASanの新しい実行、全経路差分、U15の受理の証拠ではない。製品source・既存試験・旧証拠・`source-manifest.json`・CI設定は変更していない。

## Steps22〜24：記録更新と証拠の適用範囲（2026-10-11 JST）

検証済み（今回のhash照合）：旧署名 `541b439668222710c7aa0f62afd508a8870d658c`／CI38062686224の316入力は309一致・7変更、U9 manifest37パスは36一致・1変更。旧raw87ファイルは87/87 hash一致。結果は `verification/step22-source-audit.json`。両lock、Cargo設定、Rust pin、LSan suppressionの6入力は6/6一致。製品・既存試験・旧原本・manifest・traceabilityを変更していない。以下のSteps1〜21と対応表の「現行」は各履歴時点を指す。

差異の分類：`native_fs.rs` はWindowsの100ns精度に合わせた既存mtimeテスト2件のみで、`#[cfg(test)]` 前の製品12120bytesは旧／現在ともSHA256 `bbe3820516c5f003475da68f8bf0fe2028e44c0c84ff7bd66517c0a314dc34a1`。U11 wasm `abi.rs`・`filesystem.rs`・`coordinator.mjs` は大規模FS破棄の製品変更、`u11-api-check.mjs` はその回帰追加、`u6-check.mjs` は総数assertの103→102整合。`u11-fuzz.yml` は起動条件・LLVM symbolizer・両lockとbinary記録の診断設定変更。これらを全入力不変とは扱わない。

限定再利用：U9のnative端末製品・guest・diff入口とそのRust依存は同一（native_fsの製品prefixを上記で分離）。旧Linux差分14件、3OS内部Linux24／macOS・Windows23、公開API6／compile_fail3／CLI2、coverage旧13ファイル2693/3202=84.10%・追加10ファイル2156/2397=89.95%は、同じ製品と測定対象に対する有限な保存結果として保持する。今回これらを新規実行していない。変更済みWindows mtimeテストの旧実行は現行テストの成功証拠としない。

限定ASan根拠：旧closure88入力は87一致・native_fsのテスト部のみ相違。旧実使用rustc `32dba69d69c5b10ea89a4042de8d0619f7756203`／LLVM23.1.3／cargo-fuzz0.13.2、両lock・target・suppression・flags・seed1／timeout30／rss2048／既定max_len4096は保存原本と同じ設定。旧4対象load_elf／syscall_args／vfs_paths／mmu_opsの601秒証拠と当時の同一instrumented binary再ビルド結果は履歴として維持する。今回binaryを再ビルドせず、現在binary同一の新実測は主張しない。U11診断workflowのsymbolizer設定変更後の実行へ旧証拠をそのまま置換しない。

未検証（今回）：U9専用の新しいLinux差分・coverage・3OS品質・Node／本物Safari・ASan実行。wasm製品が変わっているため旧Node／Safari20ケースは現行wasm成功へ再利用しない。必要なら承認済み手順のdiff_u9、固定13＋追加10 scopeのcoverage、同production module/nativeのNode／Safariを再実行する。ASanの新binary同一性が必要なら既存4対象を同compiler／設定で再ビルド照合し、不一致対象だけ600秒実行する。今回は追加試験を行う承認範囲ではない。

正式検査・独立再レビュー・最終確認は今回の有限記録更新を対象にする。承認済み `verify-current-u2-u11-revalidated.py` はU2／U11／U10の結合照合でありU9専用の新coverage／Linux差分／Safariの代替ではない。strict guard・80%下限・30秒制限・mask・測定分母を保持する。U11の同時dispose修正とID競合の完全解消は未検証。



## Steps19〜21：Clippy・実行compiler整合と現行検証（2026-10-11 JST）

検証済み：diff_u7.rsは8byte分割の `as_chunks::<8>().0.iter()` / `from_le_bytes(*bytes)` のみに修正。比較case・mask・mtime意味論は保持した。公式確認を行った2026-10-10 UTC時点のRust nightly-2026-10-10にrootと実行可能script/CI15設定を統一。日付の変化だけで準備中の版を再更新しない。版と全変更pathはverification/step19-official-tools.json・step19-toolchain-inventory.json・source-manifest.json。履歴文書の旧版は保存し、mise.tomlはroot原文を隔離checkoutへコピーしただけでツール設定は変えていない。

検証済み：署名GitHub Verified `541b439668222710c7aa0f62afd508a8870d658c` のCI `38062686224` で8ジョブ成功。3 OSのU9内部（Linux24・macOS/Windows23）・公開API各6・compile_fail各3・CLI各2は実exit0。Linux fmt/Clippy -D warnings、cargo-deny0.20.2のadvisories/bans/licenses/sources全4検査はexit0。sourceはSafari/U10も含む全316入力・両lockがbefore/after/current一致。署名・全job metadata・rawhashと実exitはverification/step20-fixed-proof.json、connector完全joblogと生JSONはstep20-retry-raw/。

検証済み：fresh native Linux diff_u7 64件・diff_u9 14件成功、ignored0。U9の旧13 production filesは2693/3202行（84.1036852%）、追加10filesは2156/2397（89.9457655%）、全23filesは4849/5599（86.6047508%）。旧13の集合を変更せず追加集合と分離し、80%を維持した。保存旧CIの2630行と今回3202行の増加も隠さない。production wasmと同CI fresh Linux native期待値をNode26.11.1・本物Safari26.6.2で全20case比較、case IDsとmodule/native SHAは同一。Safari17.512秒、COOP/COEP・sharedMemory・productionLauncher true、driver_reaped/server_closed true、実exit0。28秒operation/30秒whole-process watchdogを維持。Safari版はrunner付属の実測値で、最新版の主張ではない。

検証済み：U10固定probe/aubeのbuild.py選択compilerはroot/lockと同じnightly-2026-10-10。build実exit0、static ELF2本、固定aube revision・上流Cargo.lock・許可済み限定license例外を維持、guest依存audit2本exit0・source_unchanged true。製品build.pyとguest依存の意味論は変更していない。

検証済み（限定再利用）：旧load_elfとU7のsyscall_args/vfs_paths/mmu_ops各601秒ASan/LSanは、新compilerで各targetを再ビルドしたinstrumented binary SHAが4本全て完全同一。target依存8crate union88入力・両lock・既存suppressionも旧/新一致、実rustc commit32dba69d・LLVM23.1.3・cargo-fuzz0.13.2・address flagsが一致。seed1/timeout30/rss2048/detect_leaks1/既定max_lenを維持。詳細はverification/step20-sanitizer-reuse.jsonと新旧build/fuzz生ログ。600秒fuzzを今回再実行したとは呼ばない。旧294全入力は設定/テスト4pathが変わっており新316との全入力一致を主張しない。U1/U7の旧hello・coverage・Windows・fuzzは同一production dependency/compilerに対する限定再利用で、今回fresh executionはU7/U9差分とU9全検証のみ。

失敗履歴：旧38059659099はClippy exit101、次38062101203はU10build exit0の後、生成Python cache `tests/guests/u10/__pycache__/evidence.cpython-312.pyc` を入力扱いしaudit exit1で全CI failureだった。実Python sourceは保持して__pycache__だけ生成物として除外し、境界確認exit0後に全CIを再実行した。失敗はverification/step20-failed-audit.jsonとstep20-u10-failed-job.logに保存した。成功として読み替えない。

未完了：独立レビュー・新canonicalの人によるコマンド承認/実行・完了承認。候補 `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-aligned.py` は構文検査のみ、未実行。旧canonicalを保存し、候補は現在316の完全一致と旧raw内容検査を維持し、旧294との差分4pathを旧/新hashに固定する。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、全probe/aube実行、並行ID競合完全解消は未検証。strict guard・品質下限を維持。


## Steps16〜18：承認済み追加検証の結果（2026-10-10）

検証済み：製品変更なし。署名Verified `fa4cddce6c0af461f4223455aeff0c5fba0f40db`、CI `38059659099` はcompleted/failure。7ジョブ中6成功、Linux qualityの最新Clippyだけ失敗した。失敗を他の成功で読み替えない。各Linux production/coverage/ASanと3 OS qualityの294入力・両lockはbefore/after/current一致、source比較exit0。proofはverification/step16-fixed-proof.json、rawはstep16-raw/。Safariは同じ署名SHA checkoutと同じartifactを使用したが、Safari独立の294 before/after監査ファイルは未取得。

検証済み：fresh native Linux `diff_u9` 14/14成功・ignored0、diff/coverage/reportの実exit0。既存packagesと除外regexを保持した現行全23 production filesは4849/5599行（86.6047508%）。旧CI37773320167の13ファイルを全て保持した個別集計は2693/3202行（84.1036852%）、共有追加10ファイルは2156/2397行（89.9457655%）。旧13ファイルの2630行から現行3202行への増加を隠さず、追加10ファイルで旧scopeを置き換えない。原LCOV/JSONを保存した。80%の下限を変更していない。

検証済み：3 OSのU9内部（Linux24・macOS/Windows23）、公開API各6、compile_fail各3、CLI各2は実exit0・ignored0。Linux Host managedPTYのsubprocess helper結果は別途記録し二重計上しない。fmt成功後のClippyは`crates/paludarium-harness/tests/diff_u7.rs:154` の `chunks_exact_to_as_chunks` 新lintでexit101。cargo-denyはその後のコマンドにつき未到達・未検証。最小未適用差分と正確な引用はverification/step16-findings.md、connector取得の完全job logはstep16-linux-quality-job.log。

検証済み：production wasmを最新nightly-2026-10-10（元scriptと同じbuild-std/flags）で構築し、同CIのfresh native期待値とNode26.11.1・本物Safari26.6.2で現行全20ケース成功。case ID一致、module SHA `4482b1574987ff62cc8f9f872e42e5dbe6f4fc91273103da6abc0dd8ffd18fe3` とnative JSON SHA `62de7aebb39896bf11de30991cd6883527f558b52fb073cb104d76e7ccf22c69` は両環境で一致。SafariはCOOP/COEP・sharedMemory・productionLauncher true、16125ms、driver_reaped/server_closed true、実exit0。28秒operation/30秒whole-process watchdogを維持した。Safari版はCI image付属の観測値であり最新版だとは主張しない。

検証済み：load_elf ASan/LSanは17,380,733 runs / 601秒、fuzz・最小C2回・source比較exit0、ASan/LSan symbolsを確認。seed1、timeout30、rss2048、既定max_len、detect_leaks1、既存suppressionを維持。U7のsyscall_args/vfs_paths/mmu_ops各601秒は同294入力に限って再利用する。任意入力・全UBの保証、夜間scheduled実行とは呼ばない。

未完了：NFR3（Clippy警告ゼロ）、NFR8（最新cargo-denyの全4検査）、NFR9（製品pin nightly-2026-10-01と診断/local nightly-2026-10-10の整合）をGAPに保持。製品修正・toolchain更新は今回範囲に含めない。正式検査/独立レビュー/新しい最終確認コマンド承認/完了承認は未完了。別名候補 `verification/verify-current-u1-u7-u9.py` を具体化したが未実行で、CI failureを拒否する。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、全probe/aube、並行ID競合完全解消は未検証。

## Steps13〜15の履歴：追加検証前（2026-10-10）

検証済み：製品変更なし。現行署名5fa16398eae31ec178bfd93d3029b24ee31ac5e5とU9 manifest19パスは19/19一致（verification/step13-current-claimed.json）。保存7069538fの19パスは12一致・7変更、保存187パスは140一致・47変更。旧ASan/Windowsの各155パスは114一致・41変更（verification/step13-source-comparison.json）。下のSteps8〜12「現行」は当時の履歴であり、今回の実行証拠ではない。

検証済み：macOS aarch64で最新nightly-2026-10-10実体cargo/rustc/rustdocを使用。U9内部Host7/Kernel8/Runtime8（計23）、公開API6、Host compile_fail2+Runtime1（計3）、CLI2が成功、全exit0・ignored0。内部23/API6/CLI2は実行前に--listで非0を確認。Linux限定Host managedPTYはmacOS cfgで対象外であり今回成功件数へ足さない。rawはverification/step14-*.log。最初のcargo単独実体呼出しはPATH上rustc1.99との混在でexit101、RUSTC/RUSTDOCを最新実体へ固定して実行した。製品のrust-toolchain.toml nightly-2026-10-01は変更せず、診断環境との区別を残す。

検証済み：U7の最新601秒ASan/LSan syscall_args 1,455,696、vfs_paths 3,675,837、mmu_ops 3,003,322（CI38053646678）は各294入力・両lockのbefore/after/current一致、exit0。共有proof109 rawhashも一致。これは同一sourceの対象限定安全性証拠の再利用でありU9専用coverage・端末差分の代用ではない（verification/step13-sanitizer-reuse.md）。

未検証：現行U9 Linux native diff_u9 14ケース、同U9測定scope coverage80%、現行production wasm/Node/本物Safari既存14ケース。旧証拠の依存source/lockが変わったため現行合格へ再利用しない。旧load_elf/cpu_u2/mmu_u2/decodeの依存closureも変化している。U9に直接影響するELF→argv/envpのload_elfは新規601秒診断が必要、他3対象をU9完了のために無条件反復しない。現行全体clippy/3OS/供給網の今回実行は未実施。macOS/Windows実端末backend、wasm tty、Chromium/Firefox、任意入力・全UB、並行ID競合完全解消は未検証。

## 追加検証前の提案履歴（後にSteps16〜18を承認）

正式sensor実行：traceabilityは6GAP（FR9.1/NFR1/NFR2/NFR3/NFR8/NFR9）、missing/invalid/orphan0。required-sectionsはplan/instructions/summary各PASS。step15-sensors.json。macOSのdiff_u9 --listはcfgにより0件、現行Linux差分の成功として扱わない（step14-diff-list.log）。Step15は独立レビュー・追加証拠・最終確認・完了承認待ち。

製品を変更せず、現行全294入力と両lockを固定した診断CIで、(1)fresh native oracleを各実行生成するdiff_u9、(2)既存Host/Kernel/Runtime/CLIのU9 scope・除外regex・分子分母を維持したLinux coverage80%以上、(3)現行production wasmを再ビルドし同run native期待値とNode/本物Safariの現行全ケース（過去14件以上）を比較、(4)load_elfのみ600秒ASan/LSan（seed1・timeout30・detect_leaks1・既存suppression・最小C診断維持）を追加する。3OS U9内部/API/doc/CLI・fmt/clippy・依存検査は診断CIに併せて記録し、対象0件/skipを成功にしない。既存30秒watchdog・比較条件・coverage分母を維持する。全入力・両lock・生ログ・exit・署名を保存する。Windows隔離と3ASanは同一sourceのU7証拠をhash対応で再利用する。

具体入口：`bash tests/guests/u9/build.sh target/guests/u9`、`cargo test --locked -p paludarium-harness --test diff_u9 -- --nocapture`、ci.yml U9 coverageの既存cargo llvm-covコマンド、`bash scripts/build-wasm.sh`、`node packages/paludarium-wasm/tests/node-check.mjs packages/paludarium-wasm/paludarium.wasm target/production-wasm-evidence/native-results.json`、本物Safariで同じrunChecksを実行する既存browser入口、`cargo fuzz run load_elf --sanitizer address -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048 -seed=1`。追加範囲承認後に実体の最新tool版・正確なwasm/Safari commandを固定し実行する。現行canonical verify-current-u1-u7-r04.pyはU9の未取得結果を検証しないため、それだけをU9完了証拠にしない。

## Steps8〜12 現行ソース確認（2026-10-08）

検証済み：Host TerminalAttributes/TerminalInfo と Runtime TerminalInfo は non_exhaustive と全フィールドconstructorを持ち、外部literal利用側を移行。Default・ioctl意味論を保持。外部crate6件、compile_fail doc3件、Host/Kernel/Runtime U9内部23件（macOS）、CLI2件が成功。source-manifestの19パスが正規一覧。

検証済み：署名7069538f1bdadb62e275f0c8c4f580ac3b70e9b5、CI37773320167の8jobs成功（3OS/lint/deny/native差分14/coverage/production wasm）。Linux行coverageはworkspace92.67%、U1 83.08%、U9対象scope82.66%。旧追加行122/130とは別分母。verification/step11-metadata.json、step11-run-37773320167.log。

検証済み：新CI生成本番module＋同CI native期待値でNode/実Safari27.0.1各14ケースPASS。Safari16861ms、COOP/COEP・sharedMemory・nestedWorker・Rust共有allocator/AddressSpace・wait/notify・active disposeの確認。stdout/statusは6guest nativeと一致。28/30秒watchdog不変。step11-production-wasm/、step11-node.log、step11-safari-third.json/log。初回sandbox /status接続失敗とCUA無応答中断はstep11-safari-history.mdに保存。

検証済み：syscall_args1250323、vfs_paths3202926、load_elf18110999、cpu_u2 3088147、mmu_u2 3418642、decode75149340、各601秒ASan+LSan exit0、最小C各2回exit0、seed1・detect_leaks1・既存suppression固定、155paths before/after/host一致、crashなし。step11-sanitizer-proof.jsonと各step11 artifact raw。VFS専用run37773925007/署名0dc8ca8bは7069538fから診断workflow1追加のみで製品bytes同一。

検証済み：同現行head Windows run37773320171、fixture1000反復/交換34/共有違反retry311/597ms、outside不変・strictcleanup・exit0、155source paths一致。旧8cbaの154paths/1000/55/473/881msは履歴として維持。fixture本体を変更していない。

187application/build/doc pathsを署名CI bytesと照合済み（既知のexact .gitignoreおよびSafari documentary差のみ）。新external API test1追加が旧186/154から187/155となった理由。主CI/Windowsfixture/他Unit成果物は変更せず、隔離workflowは製品manifestに含めない。旧canonicalはsource変更を検出してexit1、step11-old-canonical.log保持。新completion checkerは具体化後、人のcommand承認前には実行しない。

未検証：macOS/Windowsの実端末backend、wasm tty（明示unsupported）、Chromium/Firefox、probe/aube全体、guest clone/futex/JIT/任意ゲスト、全入力/全UB保証。各600秒は有限固定seed診断であり夜間scheduled runとは呼ばない。80%/30秒/nightly2026-10-01/600秒は保持。

## Steps1〜7 当時の履歴（以下は当時のsource/CI/未検証状態）

# U9 入出力と端末

## 実装と境界

HostにStreamId別のterminal_info、Linux guest向けtermios属性と寸法を追加した。RecordingHostはstreamごとに設定可能で既定は非端末。Linux x86-64 NativeHostだけが固定TCGETS/TIOCGWINSZを照会し、guest requestとguest pointerをHostへ渡さない。

KernelはFDの共有descriptionから元streamを識別し、dupされた標準fdにも対応する。通常file/closedfdと区別し、Linux guest ABIのtermios36 bytes、winsize8 bytesを明示的にlittle-endianへ変換してchecked guest memoryへ書く。unknown requestはENOTTY、invalid fdはEBADF、ttyへの不正bufferはEFAULT。

Runtime Config.tty=NoneはHost stream別状態を維持する。Someは全標準streamの明示仮想端末と寸法を優先し、Host属性は保持、非端末Hostでは決定的Linux既定属性を使う。既存argv/envp/read/write経路を維持した。変更18ファイルの正規一覧はsource-manifest.json。

## 検証と品質の残件

検証済み：製品実装前に署名oracle fd468eed、native run37712962944の実機Linux2runnerで14ケースを取得した。expected outputをruntime fixtureへ固定保存せず、diff_u9は各CI実行でnativeを再実行する。

検証済み：Docker VMM診断はHost8/Kernel8/Runtime8、差分14、CLI2が成功、fmt --all --checkと対象5cratesのall-targets clippy -D warningsはexit0。DockerはQEMUなので実機Linuxの最終結果とは区別する。source-bytes-current.jsonは署名CI af9b739dに18 claimed sourceを結び付けるsnapshotであり、正式な承認receiptではない。

検証済み：署名commit af9b739d742a9552f44fc1515646c862b19e5de2でCI37713953347の7jobs＋native37713953340の4jobs成功。Linux実機差分14、Host/Kernel/Runtime内部Linux8/8/8・macOS/Windows7/8/8、CLI2が成功。18 claimed source bytesは当該CIと全件一致する。

検証済み：Linux U9追加実行可能製品行122/130＝93.846%、80%を満たす。oracle親fd468eedからの追加行のうちLCOVが実行可能として観測した6製品ファイルを測り、既存・削除・テスト・非計測行を除外した。独立byte/LCOV再集計でも同じ値。全体92.68%、U1 packages83.04%、U9対象クレート全体82.55%は別の分母でありU9限定値と混同しない。

未検証：現行各600秒ASan fuzz、macOS/Windows実機tty、wasm/Safari、probe/aube全体。NFR2/NFR3はfuzzのGAPを維持する。80%/600秒/30秒とnightly固定を下げない。個別Host/Kernel/Runtime/CLIの--listは初回実テストより後に確認したため、実行前のlisting証拠へ遡及しない。詳細な来歴・scope・コマンドとraw行はevidence-current.md。
