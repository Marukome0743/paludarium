## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T05:59:38Z
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
| actionlint 1.7.12 (shellcheck 0.11.0) on u11-acceptance.yml, u10-native-diagnostic.yml, ci.yml | exit 1: ci.yml 87 (SC2086), 203 (SC1090), 226 (SC1090, SC2086) のみ | 既存4件のみで、変更行（ci.yml の env 22行目、u11-acceptance.yml、u10-native-diagnostic.yml）に新しい指摘はない。期待どおり。 |

### Summary

U11 の build-oracle ジョブでは、SHA 固定の setup-python（3.15.0）が checkout 直後に入り、ゲストビルドは `python tests/guests/u10/build.py ... --advisory-policy u15-fixed-aube-zip9-name` になった。この引数は build.py の argparse の choices と一致し、u14-native-first.yml・u14-wasm-acceptance.yml とも同じ pin と呼び出しである。後続の `python3 -m unittest`、`sudo unshare ... python3 scripts/u11-run.py`、`bash scripts/build-wasm.sh` は PATH 上の python3 を使うか python に依存しないので、そのまま動く。ci.yml の `u11-programs` は `uses: ./.github/workflows/u11-acceptance.yml` で、reusable workflow 側の `workflow_call` と一致する。トップレベルの env は呼び出し先へ継承されないが、U11 のジョブはそれを使わず、害はない。permissions も既存の読み取りだけのままである。code-summary の「現行Step26」節は、検証済み（actionlint）と未確認（変更後の CI は未実行で、4環境14ケースの新しい結果はない）を分けて書いており、過大な主張はない。traceability の FR9.2 の ids・status・targets は変わっていない。Build and Test でこの3つの workflow を CI 実行して確認するまでは、CI 通過は主張できない。
