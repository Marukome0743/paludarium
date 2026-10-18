## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-18T01:20:00Z
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
| R-07 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md > 見出し「現行Step27：Safariのsession作成の待ち時間」 | Step 27 の節の見出しが「現行」のまま残っている。直前の「現行Step28」節が取り消しと理由を明記しており、本文もStep 27を履歴と述べるため誤読の恐れは小さい。ただし、見出しだけを拾う読み手には、60秒の待ち時間変更が今のソースにあるように見える。traceability.json がこの見出し名で参照している点も理由として書かれている。 | 次に記録を更新する機会に、見出しの冒頭へ「取り消し済み（履歴）」と添えるか、traceability.json の参照名と合わせて直す。今回のゲートを止める必要はない。 | Accepted risk |
| R-08 | Minor | packages/paludarium-wasm/tests/u11-browser-driver.test.mjs > test "WebDriver request honours a supplied timeout against a slow endpoint" | 回帰は webdriverRequest が第5引数の timeoutMs を使うことだけを確かめている。safari() が POST /session にだけ 60000 を渡すこと（今回の修正の本体）と、他の要求が 10000 のままであることは、どのテストも確かめていない。呼び出し側の 60000 が消えても全テストが通る。 | 余力があれば、safari() の session 作成の待ち時間を定数に切り出して試験で確かめるか、CI の Safari job で session 作成が成功した記録を根拠として残す。採用前に必須ではない。 | New |
| R-09 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/README.md > 「この方法の限界」 | 入口の SHA-256 と binding-04 の SHA-256 は README にだけあり、code-summary.md には無い（binding-04 が code-summary.md を固定し、入口が binding-04 を固定するので循環を避けるため）。README 自体はどの binding にも固定されていない。この循環の説明は正直で妥当だが、採用時に人が README の値を信頼する形になる。 | 採用時のコマンド承認では、README の値ではなく、実際のファイルの SHA-256 を人が読み直して確かめる。必要なら README の SHA-256 を承認記録に写す。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| ファイルの読取のみ（shell 不使用の指示） | u11-browser-driver.mjs と .test.mjs、binding-04.json、u11_candidate.py、README.md、code-summary.md、run-1792253730296513000-37372/result.json を読んだ。result.json は u11_candidate PASS、binding_sha256 と checker_sha256 が README の値と一致、U2 入口・binding-03・U1 checker・binding-02 の SHA-256 が定数と一致。 | 実行はしていない。保存された証拠と、コードの読取による判断である。 |

### Summary

Safari の修正は最小で正しい（webdriverRequest の既定 10000 を保ち、POST /session だけ 60000、試験を1件追加）。入口は U2 入口・binding-03・U1 checker・binding-02・旧封印を SHA-256 で固定してそのまま実行し、足した許可は Safari の2ファイル（path は定数で限定）、head/CI、U11 の4記録だけで、緩めた検査は見つからなかった。CI の束ね方（3 run、attempt 1 の load_elf 失敗の記録、Safari job の成功確認、u14-quality の不起動、commit の files と git の差分がちょうど2ファイル）も健全で、残るのは Minor 2件のみ。
