## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-11T07:06:39Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | Resolved (reviewer) |
| R-03 | Major | packages/paludarium-wasm/index.mjs > createFileSystem / filesystem.dispose(), line 76 | 検証済み：同一 handle に対する同時の二重 dispose は冪等にならない。`Promise.allSettled([fs.dispose(), fs.dispose()])` を現行 package の実 Wasm で実行すると、一つは fulfilled、もう一つは PaludariumError(kind=internal) で rejected になる。disposed は最初の control 完了後にだけ更新されるため、二つ目も filesystem-drop を送り、ABI の stale handle 拒否に到達する。既存 u11-api-check.mjs は逐次二重呼出しだけを検査している。 | handle ごとに進行中の dispose Promise を共有し、同時呼出しが同じ結果を受け取るようにする。active lease による拒否後は再試行できる状態を保持する。同時二重呼出しの実 Wasm 回帰と、active 拒否後の release / dispose 成功を検査する。 | Resolved (reviewer) |

> R-01 Reviewer note: 検証済み：coordinatorのfilesystem-dropはsnapshotを生成せずABIのfilesystem_dropを呼び、PrivateFs.closeが単一state lockでIdleからClosedへ遷移した後にregistryを削除する。実production wasmのu11-api-check.mjsを独立実行し、34 MiB×2のsnapshot拒否、launcherを維持した同時dispose成功、active拒否、kill後の再試行をexit 0で確認した。

> R-02 Reviewer note: 検証済み（コード照合）：FileStat.mtime_nsはi128で、native_fs.rsのstat/cap_statはUNIX_EPOCH以前をchecked_negで表現する。Kernelのlinux_mtimeは負秒と非負ナノ秒へEuclidean除算する。Linux実ファイルのmetadataとFileHandle.statを-1 ns/-0.5 s/-1 sで検査するu7_mtime_retained_file_and_path_stat_pre_epochが存在する。native_fs.rsは署名済み旧原本と現行でhash一致。今回このLinux限定Rust試験は新規実行していないが、指摘したEIO変換は現行コードに存在しない。

> R-03 Reviewer note: 検証済み：FSごとのfilesystemDisposalを同期的に確保し、重複呼出しは同じcontrol結果を待つ。成功時だけdisposed/所有表を更新し、finallyで失敗後の再試行を可能にする。実wasm独立回帰で通常FSと68 MiB FSの同時2呼出しが成功し、active時は両方が拒否、kill/release後は同時再試行と逐次再呼出しが成功した。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| aidlc engine sensor-required-sections --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md --stage-slug code-generation | PASS; 6 H2; findings_count 0 | サマリーの必須構造を独立再検査した。 |
| aidlc engine sensor-traceability --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json --stage-slug code-generation | PASS; findings_count 0 | 宣言ID・coverage・参照先の正式検査が成功した。担当外要件のDeferredをU11の新規合格へ読み替えていない。 |
| /Users/mutoakio/.local/share/mise/installs/node/26.11.1/bin/node packages/paludarium-wasm/tests/u11-api-check.mjs packages/paludarium-wasm/paludarium.wasm | exit 0; U11 API: modes, ownership, concurrent disposal, large FS, busy rejection/retry, terminal validation, kill/release PASS | 実moduleでR-01/R-03の境界を独立再実行した。 |
| python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/step22_dispose_validation_test.py | 19 tests; OK; exit 0 | 入力追加/欠落、旧現行取り違え、guest/hash/期限、cleanup、coverage母集団とSCM cwd復帰を含む有限回帰が成功した。合成fixtureを実ブラウザ証拠の代替にしていない。 |
| jj --ignore-working-copy diff --from 2b3874eabda6fe6f1d1334202421db733445fd21 --to a19bea3549a77a0f665b20626d65049ecc6e2f6a --stat; independent current input hash audit | 2 files; 15 insertions/7 deletions; 329 inputs match | 差分はindex.mjsとu11-api-check.mjsのみ。Rust・固定guest・両lockの変更はない。公開async APIとsnapshot上限を維持する。 |
| Independent read-only saved CI/ZIP/guest audit | PASS; 5 ZIP digests; 98 extracted originals; 4 environments ×14 cases | attempt2の成功metadata、同一module/oracle/guest、各guest0〜30秒・exit0・timeoutなし、suite cleanupを照合した。Safari26.6.2の実観測を保持し、attempt1の失敗原本も確認した。producer/Node/Chromium/Firefoxの成功はattempt1から引き継がれたもので、全5ジョブの新規再実行とはしない。 |
| Independent saved sanitizer binary/raw hash audit and source review | PASS; seven binary/raw hashes; saved exit0/601 seconds | Rust変更なしの限定再利用。compiler/settingsを含む保存証拠との対応を確認した。今回の新規ASan/LSan実行とはしない。 |
| Candidate verify-current-u11-concurrent-dispose.py and step22_dispose_validation.py inspection | Historical/current references separated; full canonical command not executed | 固定hashの旧checkerを署名済みbaseline snapshotへ渡し、現行2ファイルbridgeと新CIを別に検査する。全スクリプトの正式実行・完了承認はこのレビューで代行していない。 |

### Summary

同時disposeの変更はFS単位の所有に閉じており、成功の冪等性、active拒否後の再試行、大規模FSの破棄を実moduleで確認した。新規指摘はなくREADYとする。旧ASan/品質証拠の限定再利用、CI再試行の由来、未実行の正式最終確認を区別しており、全プラットフォームの新規品質実行やセッションID競合の完全解消はこの判定の主張に含めない。
