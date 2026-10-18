## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T08:49:18Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | Resolved (reviewer) |
| R-03 | Major | packages/paludarium-wasm/index.mjs > createFileSystem / filesystem.dispose(), line 76 | 検証済み：同一 handle に対する同時の二重 dispose は冪等にならない。`Promise.allSettled([fs.dispose(), fs.dispose()])` を現行 package の実 Wasm で実行すると、一つは fulfilled、もう一つは PaludariumError(kind=internal) で rejected になる。disposed は最初の control 完了後にだけ更新されるため、二つ目も filesystem-drop を送り、ABI の stale handle 拒否に到達する。既存 u11-api-check.mjs は逐次二重呼出しだけを検査している。 | handle ごとに進行中の dispose Promise を共有し、同時呼出しが同じ結果を受け取るようにする。active lease による拒否後は再試行できる状態を保持する。同時二重呼出しの実 Wasm 回帰と、active 拒否後の release / dispose 成功を検査する。 | Resolved (reviewer) |
| R-04 | Critical | packages/paludarium-wasm/package.json > files; packages/paludarium-wasm/worker-support.mjs > jitImports import | 検証済み：worker-support.mjs が ./jit-support.mjs を無条件で import するが、npm pack --dry-run の全10 entriesに jit-support.mjs が含まれないため、配布パッケージの index.mjs はモジュール解決に失敗する。ローカルにはこのファイルが存在するので実Wasm API試験の成功では検出できない。 | jit-support.mjs を配布ファイル一覧へ追加し、配布対象ファイルだけで構成したパッケージの import と実Wasm起動を確認する。必要JSのimport先が全て梱包される検査を追加する。 | Resolved (reviewer) |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/unit-test-instructions.md > Current Steps14–16 Setup / Current U11-scoped commands | 検証済み：現在という見出しの手順は Python3.15.0・nightly-2026-10-10 を指定するが、手元のPython実体は3.14.7、現在のrust-toolchain.tomlはnightly-2026-10-11である。Chromium/Firefox準備はChromium1248実体欠落、Safari準備はdriver-startup exit1で停止した。独立レビューでは指定Python、ブラウザ14件、Linux coverage80%、600秒ASan/LSanを新規実行できていない。 | 保存した実行時のツール指定と現在の再実行手順を明確に分け、Python/ブラウザ準備を満たした環境で不足する確認を行うか、保存済み有限観測の適用範囲と今回未実行の項目を明記する。 | Resolved (reviewer) |
| R-06 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/unit-test-instructions.md > 今回Steps23〜25：配布パッケージと再実行手順 | 今回は新preview互換canonical、fresh tarballの実Wasm起動/C12、ブラウザ・coverage・ASanを独立再実行していない。canonicalはU1所有入口と他Unit原本を読むため今回の読取範囲外、pack/実guestは生成出力とguest起動を伴うため設定差に限定した本レビューでは繰り返さなかった。Python24件とJS32件の成功だけではこれらの新実行を証明しない。 | 保存済み梱包/実Wasm/CIの入力同一性と適用時点を保持し、正式checkpointで承認済み互換canonicalの実exitと入力不変を確認する。今回未実行の項目を新規成功と記載しない。 | Accepted risk |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| node --test packages/paludarium-wasm/tests/u11-browser-driver.test.mjs | PASS: tests 9, pass 9, fail 0, exit 0 (新しい回帰 "WebDriver per-request timeout aborts a slow endpoint" 約556ms) | builder の報告と一致。仮の HTTP サーバーでの確認であり、本物の Safari の確認ではない。 |

### Summary

変更は計画の Step 27 どおりで最小である。`webdriverRequest` は第5引数 `timeoutMs = 10000` を `AbortSignal.timeout` に使い、`POST /session`（u11-browser-driver.mjs 37行目）だけが 60000 を渡す。driver 起動待ち（10秒）、`/status`・navigation・script-report・`DELETE` の各要求（10秒）、suite の `timeout`（u11-browser-check.mjs は 600000）、guest 30秒、比較と合否判定は変わっていない。`webdriverRequest` の呼び出しは u11-browser-driver.mjs の中とそのテストだけで、他の呼び出し元（u11-browser-ready.mjs、u11-browser-check.mjs、u14-check.mjs）は `runBrowser` 経由のため影響を受けない。

外側の期限に収まる。session 作成の最悪増分は +50 秒で、ジョブの timeout-minutes は 25（u11-current-verification.yml）、suite は supervise が 600 秒で打ち切る。60秒の待ちが外側の監視を超えて黙って長引くことはない。新しい回帰は、500ms で応答する仮の endpoint に対し 50ms 指定で `TimeoutError`、既定では成功を確かめる。修正前のコードは第5引数を無視して 50ms 指定でも成功するため、`assert.rejects` が失敗し、この回帰は修正前に失敗する。時間差が 10 倍あるので揺れにくい。code-summary.md の「現行Step27」節と traceability.json の FR5.3 notes は、失敗した run、原因、変えた行、確認結果を正確に書き、CI の再実行が未確認であることを明記している。実績の過大な主張はない。
