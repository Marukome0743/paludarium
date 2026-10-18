# U13 Windows Host code summary

## 現行Step13〜15（Build and TestのLoop-back 1）

2026-10-18。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）、U11のSafariの待ち時間の修正（2b8723ab・57a8c96f）と正式確認コマンドの更新の途中で、Code Generationの段階全体の作り直しのため、U13を確かめ直した。製品・workflow・source-manifest.json・traceability.jsonは変えていない。

- (a) U13の担当source（source-manifestの全ファイル）は、上の変更で変わったファイル（U14のJIT・wasm・テスト、U11の `packages/paludarium-wasm/tests/u11-browser-driver.mjs`・`.test.mjs`、`mise.toml`）を含まない。作業コピーはe4f84768（Steps11〜12のworkflowの修正を含む）と同じである（`git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- <source-manifestの全ファイル>` がexit 0）。
- (b) 下の「履歴：Steps11〜12」節の「CIでの再実行はまだで、修正後のjobが通るかは未確認」は、その時点の記述である。その後、U13の品質CI（u13-quality）は、e4f84768（run 39015782530）と1ceae86c（39028305765）で、どちらも2回目の実行で成功した。2b8723ab・57a8c96fでは、u13-qualityは起動していない。
- (c) 下の節が挙げるU13確認スクリプト・確認候補は、その時点のものである。今の正式確認コマンドは、人が採用した `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py --entry-sha256 56870072810100fa97456ced54a0732e8696489dcb297fa38aa17c0a39978ca7 --binding-sha256 a3d81077e557df7acee86878656360088880b13a75c4c100a68aa748c0450905` である。
- (d) 2026-10-18のStep14のあとのU13 checkpointで、今の正式確認コマンドでの検証はexit 0（`source_compatibility: PASS`、`u11_candidate_v2: PASS`、`old_chain_source_compatibility: PASS`、`U15_acceptance: GAP`）だった。Step14でこの節を書く前に手元で同じコマンドを実行したときもexit 0だった。
- (e) `U15_acceptance: GAP` は、全体の受入を担うU15がまだ完了していないことを示す既知の表示である。U1〜U12のcheckpointでも同じく出ており、U13の不合格を意味しない。
- (f) Step15（checkpointでの人のRequest Changes）で、再レビューのMinorに対応して(d)をcheckpointでの検証結果に書き直し、(e)を足し、この節の見出しを「現行Step13〜15」にした。
- 下の節は、それぞれの時点の履歴として読む。下の節の本文にある「現行」「未実施」「未検証」は、その節を書いた時点のものを指す。

## 履歴：Steps11〜12（作成時の見出しは「現行Steps11〜12」）

Build and Testで、fork `codex/build-and-test`（head bd247f1e）の `U13 current full quality`（run 39009466368）が2つのjobで失敗した。この差し戻しに対し、workflow 3ファイルだけを直した。製品source、試験、スクリプト、source-manifest.json、他Unitの記録は変えていない。

失敗したjob：

- job 117328658441 `unit tests (windows-latest)`：JITの実Wasm試験（paludarium-jit `bridge::tests`）が `PALUDARIUM_TEST_NODE must name actual current Node executable` でpanicした。`u13-quality.yml` のenvにこの変数がなかった。
- job 117328658403 `u13-oracle / native-first`：step「Fixed unmodified guests with license audits」で `bash scripts/u10-build-guests.sh` がadvisory policyを渡さず、aubeの `cargo deny ... check` がexit status 1で止まった。`u13-quality.yml` が呼ぶ `u13-wasm-acceptance.yml` も同じ呼び方だった。

変更した行と根拠（U9の `u11-acceptance.yml`、U12の `u12-quality.yml` と同じ修正）：

- `.github/workflows/u13-native-first.yml` 50行目：`bash scripts/u10-build-guests.sh target/guests/u10 2>&1 | tee ...` を `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name 2>&1 | tee target/u13-native-first/build.log` に置き換えた。このjobにはsetup-python 3.15.0がすでにある。`tests/guests/u10/build.py` は `--advisory-policy` の選択肢に `u15-fixed-aube-zip9-name` を持つ。
- `.github/workflows/u13-wasm-acceptance.yml`：build-oracle jobの `actions/checkout` の直後に `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`（`python-version: '3.15.0'`）を足し（15〜17行目）、ゲストビルドの行（旧24行目、現27行目）を `python tests/guests/u10/build.py target/guests/u10 --advisory-policy u15-fixed-aube-zip9-name` に置き換えた。
- `.github/workflows/u13-quality.yml` 22行目：workflowの `env` の `CARGO_TERM_COLOR: always` の次に `PALUDARIUM_TEST_NODE: node` を足した。

他の行、閾値、SHA固定、権限、比較条件は変えていない。

確認の結果：

- actionlint 1.7.12（shellcheck 0.11.0を明示）を3ファイルに対して変更前と変更後に実行し、どちらもexit 0で指摘は0件だった。既存の指摘はない。
- CIでの再実行はまだで、修正後のjobが通るかは未確認である。再実行はBuild and Testで行う。

## 実装

NativeHostのWindows端末接続を追加した。kernel32のGetStdHandle、GetFileType、GetConsoleMode、GetConsoleScreenBufferInfoをhost-owned bufferで呼び、LinuxゲストABIのtermios subsetとwinsizeへ明示変換する。入力側consoleで画面寸法が必要な場合はread-only CONOUT$、出力側で入力modeが必要な場合はread-only CONIN$の所有handleを取得し、Dropで閉じる。製品はSetConsoleModeを呼ばない。テストだけが独立した子プロセスのconsole状態を設定する。

redirected stdin/stdout/stderrはNone、null／INVALID_HANDLE_VALUEはEBADF、未知flag・不正なviewportはEINVAL。既存NativeFsのcapabilityパス隔離、Windows regular-file mode、symlink権限検査、hard linkとflockを維持した。追加crate、固定guest、両lock、Rust compiler、comparison maskは変更していない。

## 上流と対象

`inception/requirements-analysis/requirements.md`、`inception/units-generation/unit-of-work.md`、`inception/units-generation/unit-of-work-story-map.md`、`inception/contract-design/contract-summary.md`のC2/C10/C11、Windows Host・端末・固定probe/aube・隔離・検証要件に対応する。共有NativeFsのWindows O_DIRECTORYも実測した不一致に基づく最小修正として扱う。他Unitの記録は保持する。Windowsの全console機能や任意guestの完全互換は未検証である。

## 実装前期待値と比較

製品変更前の署名head2b05e541でfresh isolated Linuxのprimary14と元argv14を取得し、同一probe/aubeの原本・build receipt・限定CDLA四監査・node不在・#1645を検査した。`verification/step2-native-oracle.md`と原本が順序を示す。Windows比較は同じLinux ELFをnative Windows Rust harnessへ読み込み、primary14＋default VFS2、元argv14＋default VFS2を実行する。Linux ELFをWindows OSへ直接execする主張ではない。

Windows runnerは子プロセスをCREATE_SUSPENDEDで生成し、kill-on-close Job Objectへ所属させてから再開する。30秒を超える場合はJob全体を停止し、プロセスと子孫の終了を確認してhandleを閉じる。失敗原本は保持し、時間切れや未実行を合格にしない。Guest environmentとWindows loader用SystemRootを区別する。

## 履歴：検査（作成時の見出しは「現行検査」）

検証済み：署名head832abd0fb9c67f20af0fbb8b58119f019c1f9f4a、fresh CI38236916982の全29ジョブが成功した。現行署名入力361、実write22件、累積公開差分21件を照合した。Runtimeは一時診断を完全撤去してU12署名基準と同じbytesへ復元したため、実writeと累積差分を区別する。Windows内部25＋実console7＋helper1の33件、Python35件、3OS品質・回帰、計測なしguest32操作と独立計測付きprimary16操作が成功した。全入力・両lock・実compiler・署名・job logs・全ZIP API digest・展開bytesを照合した。

検証済み：Host固定6ファイル904/1015行＝89.064%、共通5ファイル656/750＝87.467%、Windows固有248/265＝93.585%、Python固定7ファイル250/276＝90.580%。同CI production module／guestでNode・Chromium・Firefox・本物Safari各14ケースが成功した。fresh JS固定5ファイル426/455行＝93.626%をV8原本82件から再集計した。11対象各600秒以上のASan/LSan、MMU最大4608バイト、Linux共通scopeも全確認候補で検査した。検証の分母、guest30秒、比較条件は維持した。

検証済み：46回帰、全確認候補のレビュー前診断exit0（139.820秒、script前後SHA一致、stderr空）。原本はverification/step10-retry2-diagnostic.*、受入索引はverification/step10-acceptance-evidence.json。旧U1全確認はe2dの全362入力へ厳密に結び付け、旧U12全検査も保持した。これは履歴の証拠照合であり、新U13実行の代替ではない。独立レビュー・新最終確認コマンドの正式承認・U13完了承認は未実施である。

## 失敗履歴と限定修正

run38234815316は28成功・Windows receipt失敗。通常32操作の後、最新cargo-llvm-covのwrapperフラグを古いreceiptが見落とし、計測付きguest実行前に停止した。既定wrapper経路を維持し、その実フラグ・marker・対象crateを明示検査するworkflow一件修正後、上記fresh runが全成功した。旧確認候補のWindows区切りキー不一致も、原本不変・固定7ファイル衝突拒否の読取adapterで修正した。両失敗と生ログを保持した。Windows exeのbytesはartifactに含まれず、そのSHAは署名workflowが実機で計算したreceiptによる証拠である。

以下は以前のhead／runにおける調査履歴であり、記載された未検証状態はその時点のもの。

run38142190344は28/29成功。署名bytes修正後の全7監査・Windows内部33・Python32は成功したが、mounted aube installがdirectory openのEACCESで失敗した。短い実Windows診断でplain cap_std directory openのraw Windows error5と、maybe_dir(true)の成功を対比し、NativeFs O_DIRECTORYへWindows限定maybe_dirを追加した。訂正後のfocused Windows I/O境界は成功し、2flagでdirectoryが開けること、regular-file ENOTDIRとcreate-plus-directory EINVALを維持することを確認した。旧失敗・訂正・未実行のguest/coverageはverification/step6-windows-directory-cause.mdへ分離して記録した。ローカルmacOS Host92件、fmt、Clippyも成功した。全guest比較と最終coverageはまだ未検証である。

run38140731434は29中28成功、専用Windows jobはguest開始前のroot policy hash拒否で失敗した。短い監査run38142014430でWindowsのcore.autocrlf=trueによりdeny.toml・両lock・toolchain・fixture3件の全7ファイルが署名LFからCRLFへ変換されたことを実bytesで確認した。denyの署名hashはLinux receipt期待値に一致し、Windows CRLFのhashだけが異なる。checkoutでcore.autocrlf=falseを指定し、guest前の全7署名bytes一致を必須化した。監査原本と修正はverification/step6-windows-checkout-cause.mdに記録する。guard・fixture・mask・測定分母の緩和はない。修正後のWindows guestとcoverage成功はまだ未検証である。

旧head6d507701は29中25成功・4失敗、次head e449c7deは29中27成功・2失敗。初回Windows mtime fixtureはread-only handleへの更新でAccessDeniedとなり、fixtureをread/writeで開く限定修正後に成功した。fmt module orderも修正後成功。初回Safariはsession creationでguest未実行、e449では4環境各14が成功した。U7 Windows race fixtureの一時AccessDeniedはe449で観測し、5b7cの同条件既存Windows unitは成功した。U7製品・テストは変更していない。Dedicated Windowsのshasum不足はhashlibへ置換した。全失敗raw logと各run metadataを別保存する。

旧U12確認スクリプトは改変せず、署名342入力と歴史的支援72ファイルの414 snapshotで全検査を診断実行してexit0。snapshot origin、exact union、digest、symlink、欠落・追加・重複・旧現行取り違えの8回帰も成功した。これは旧時点の証拠照合であり、現在のWindows guest合格の代替ではない。

## Coverageと梱包

固定測定対象はverification/coverage-scopes.mdへ列挙する。Windows Host6ファイル、共通5ファイル、Windows固有windows.rs、Python core7ファイルを別々に80%以上とする。Linux共通5ファイルも既存LCOVから独立に照合する。4環境guest各14、C12、JS固定5ファイルの80%以上、3OS品質、Linux差分と11対象各600秒ASan/LSanを現行headへ結合する。MMU最大4608バイト、guest30秒、strict guardを維持する。

U13確認スクリプトは旧検査と現行検査を分離し、全診断exit0を確認して正式検査と独立レビューへ渡す。正式確認コマンドと完了承認は親の正式手順で行う。初回native SIGSEGV原因、Windows race fixtureの一時失敗原因、並行セッションID競合の完全解消は未検証である。
