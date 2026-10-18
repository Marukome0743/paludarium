## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-14T21:43:23Z
**Iteration:** 1
**Verdict Dictated:** no
**Request ID:** review:e5300f404a241b9530d8aa564e0fea5b

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | Resolved (reviewer) |
| R-03 | Major | packages/paludarium-wasm/index.mjs > createFileSystem / filesystem.dispose(), line 76 | 検証済み：同一 handle に対する同時の二重 dispose は冪等にならない。`Promise.allSettled([fs.dispose(), fs.dispose()])` を現行 package の実 Wasm で実行すると、一つは fulfilled、もう一つは PaludariumError(kind=internal) で rejected になる。disposed は最初の control 完了後にだけ更新されるため、二つ目も filesystem-drop を送り、ABI の stale handle 拒否に到達する。既存 u11-api-check.mjs は逐次二重呼出しだけを検査している。 | handle ごとに進行中の dispose Promise を共有し、同時呼出しが同じ結果を受け取るようにする。active lease による拒否後は再試行できる状態を保持する。同時二重呼出しの実 Wasm 回帰と、active 拒否後の release / dispose 成功を検査する。 | Resolved (reviewer) |
| R-04 | Critical | packages/paludarium-wasm/package.json > files; packages/paludarium-wasm/worker-support.mjs > jitImports import | 検証済み：worker-support.mjs が ./jit-support.mjs を無条件で import するが、npm pack --dry-run の全10 entriesに jit-support.mjs が含まれないため、配布パッケージの index.mjs はモジュール解決に失敗する。ローカルにはこのファイルが存在するので実Wasm API試験の成功では検出できない。 | jit-support.mjs を配布ファイル一覧へ追加し、配布対象ファイルだけで構成したパッケージの import と実Wasm起動を確認する。必要JSのimport先が全て梱包される検査を追加する。 | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/unit-test-instructions.md > Current Steps14–16 Setup / Current U11-scoped commands | 検証済み：現在という見出しの手順は Python3.15.0・nightly-2026-10-10 を指定するが、手元のPython実体は3.14.7、現在のrust-toolchain.tomlはnightly-2026-10-11である。Chromium/Firefox準備はChromium1248実体欠落、Safari準備はdriver-startup exit1で停止した。独立レビューでは指定Python、ブラウザ14件、Linux coverage80%、600秒ASan/LSanを新規実行できていない。 | 保存した実行時のツール指定と現在の再実行手順を明確に分け、Python/ブラウザ準備を満たした環境で不足する確認を行うか、保存済み有限観測の適用範囲と今回未実行の項目を明記する。 | Resolved (reviewer) |

> R-04 Reviewer note: 検証済み：実npm12.2.0 tarballは11 entriesでjit-support.mjsを含む。隔離展開packageのみのimport、同梱production wasmのhello stdout hellon・stderr空・exit0と自然Worker終了が独立試験で成功した。必須JSを除去したコピーのclosure/import拒否も含む7回帰が成功。

> R-05 Reviewer note: ドキュメント根拠・検証済み：Steps23–25専用Current Setupが現在の再実行手順を定義し、旧nightly10/当時のbrowser・CI手順を履歴へ分離した。Node26.11.1/npm12.2.0/Python3.15.0実体で今回の試験を確認。固定Rustの正本と、今回未実行のbrowser/Linux coverage/ASan/3OS CIが明記され、保存観測をfresh実行と数えない。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| env U11_NPM="$U11_NPM" "$U11_NODE" --test packages/paludarium-wasm/tests/packed-distribution.test.mjs | exit0 / 7 passed / 0 failed。実tarball SHA256 3e8bd962bac7b4cd8ef46d524be646ebf08021eab48b3310975be6466e0ea5e8、11 entries、jit-support.mjsあり。 | 正常配布、必須JS閉包、隔離import、実Wasm helloとdispose、必須JS欠落、破損wasm、無効guestを確認。リポジトリJSへfallbackしない。 |
| Packed actual Wasm hello | stdout hello\n、stderr空、status exited/code0、packed dispose PASS。 | 子ハーネスが展開packageのindexとwasmを読む。固定helloだけを配布外の独立入力として渡す。子の自然process終了を要求するので参照されたWorker残留は期限内成功に読み替えられない。 |
| "$U11_NODE" packages/paludarium-wasm/tests/u11-api-check.mjs packages/paludarium-wasm/paludarium.wasm | 既存supervisor外部60秒。exit0 / timed_out=false / process_group_cleaned=true。U11 API: modes, ownership, concurrent disposal, large FS, busy rejection/retry, terminal validation, kill/release PASS。 | 既存C12・68MiB・同時dispose・active拒否後の再試行が独立実行で成功。 |
| "$U11_NODE" --test packages/paludarium-wasm/tests/u11-contract.test.mjs packages/paludarium-wasm/tests/u11-browser-driver.test.mjs packages/paludarium-wasm/tests/u11-filesystem.test.mjs packages/paludarium-wasm/tests/u11-worker-support.test.mjs packages/paludarium-wasm/tests/u7-mtime-snapshot.test.mjs | exit0 / 32 passed / 0 failed。 | 既存JS境界を維持。新規browser受入やcoverage測定の代替ではない。 |
| "$U11_PYTHON" aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-preview13-bound.py | exit1。ValueError: non-configuration input changed: packages/paludarium-wasm/package.json。 | 記録された旧正式入口は変更後のpackageを正しく拒否した。失敗を保存成功へ読み替えない。候補はまだ正式採用前である。 |
| "$U11_PYTHON" aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/verify-packed-current.py | 独立手動実行exit0。All thirty-four mandatory quality jobs and unchanged historical predicates passed。末尾freshpack 7/7、exit0 / timed_out=false / process_group_cleaned=true / 1.576221208秒。 | Python3.15.0で旧述語と新段の両方が成功。34jobsは保存CI原本・hash照合であり新CI起動ではない。新段の実packを別に要求しており、保存CIだけでは候補の成功にならない。人の正式コマンド変更承認はこのレビューで代替しない。 |
| Candidate projection and pins inspection | 元preview13 wrapperをSHA256で固定。現在packageは署名原本のworker-support.mjs直後にjit-support.mjsを一度だけ追加したbytesと等しい。new test2 filesのSHA256を独立計算し両pin一致。 | 投影はROOTのpackage.jsonだけに限定。旧検査には旧bytesを渡し、finallyでsafe_readを復帰する。検査後に実packageとtest bytesの不変を要求し、別段で現在packageを実packする。実ファイル・旧述語・品質下限を改変しない。 |
| Source manifest and traceability | manifest331 pathsを全件確認。今回のpackage追加とpacked-distribution.test.mjs / packed-distribution-child.mjsを含む。coverage targets欠落0。packaging_repairに今回fresh範囲とhistorical_only範囲あり。 | 63-IDの既存配分と担当外Deferredを維持。今回Steps23–25は梱包修正・限定回帰であり、過去329入力や後続Unit全体を今回の変更/完成とは扱わない。 |
| Module and guest provenance | wasm SHA256 fea98818013c28be329f48107bb2a6aa4b8faaa1c5013e3b6200f6a7c98983dd、hello SHA256 67eeda7b49312fed76e36b13d8d8c8717902e0d0b0517656df491302f1e488fb。実tarball wasmと保存production観測、固定guest manifestの一致を回帰で確認。 | 既存module/guestの限定再利用。今回の新buildや新oracle取得ではない。 |

### Execution and Scope

上表の実体はU11_NODE=`/Users/mutoakio/.local/share/mise/installs/node/26.11.1/bin/node`、U11_NPM=`/Users/mutoakio/.local/share/mise/installs/npm-npm/12.2.0/node_modules/.bin/npm`、U11_PYTHON=`/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3`。Node v26.11.1、npm12.2.0、Python3.15.0の実使用を確認し、shim/mise execを使用していない。独立packはtarget/u11-packed/run-Y8Bpjy、候補内の再packはtarget/u11-packed/run-Uo5FGmであり、双方の同一tarball SHAを観測した。npm公開は実施していない。

新規browser14guest/本物Safari、Linux coverage80%測定、600秒ASan/LSan、3OS CIは今回未実行。これらは現行setupとsummaryで明示された範囲外・保存観測であり、今回の新規成功を主張しない。旧browser準備のChromium1248欠落、Playwright既存lock1.64.0と記録された公式1.64.1との差、旧失敗も保存されている。候補の旧チェーンが出すU14 browser/performance、standalone jit_compile panic、session-ID未解消の境界は保持し、梱包修正で解決したとは扱わない。

今回のpackage変更は必須JSの同梱だけで、Rust・guest・wasm・品質floorの変更はない。配布試験は新しい実tarballを生成し、closureの外部参照・package外への相対参照を拒否する。Node childは30秒、各npm/tar/childは60秒、候補のfreshpack全体は既存process-group supervisorの60秒監督である。親から進行確認を求められた際に対象プロセスIDをread-onlyで取得したが、続くCPU/経過確認の時点で既に終了しており、PTYの実exit0を最終根拠とした。重複の全検証は起動していない。

### Summary

梱包漏れは実配布物のimportと実Wasm起動で修正確認でき、再実行手順は現在の道具と保存証拠を分離している。承認されたSteps23–25の変更はREADYであり、候補検証コマンドの正式採用と後続Unitの未解消事項は別の判断として残る。
