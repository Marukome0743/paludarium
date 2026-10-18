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
| R-08 | Minor | packages/paludarium-wasm/tests/u11-browser-driver.test.mjs > test "WebDriver request honours a supplied timeout against a slow endpoint" | 回帰は webdriverRequest が第5引数の timeoutMs を使うことだけを確かめている。safari() が POST /session にだけ 60000 を渡すこと（今回の修正の本体）と、他の要求が 10000 のままであることは、どのテストも確かめていない。呼び出し側の 60000 が消えても全テストが通る。 | 余力があれば、safari() の session 作成の待ち時間を定数に切り出して試験で確かめるか、CI の Safari job で session 作成が成功した記録を根拠として残す。採用前に必須ではない。 | Resolved (reviewer) |
| R-09 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/README.md > 「この方法の限界」 | 入口の SHA-256 と binding-04 の SHA-256 は README にだけあり、code-summary.md には無い（binding-04 が code-summary.md を固定し、入口が binding-04 を固定するので循環を避けるため）。README 自体はどの binding にも固定されていない。この循環の説明は正直で妥当だが、採用時に人が README の値を信頼する形になる。 | 採用時のコマンド承認では、README の値ではなく、実際のファイルの SHA-256 を人が読み直して確かめる。必要なら README の SHA-256 を承認記録に写す。 | Resolved (reviewer) |
| R-10 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py > main, logical_child | 内部の --logical-child の分岐はコマンド行の hash 検査（command_line_pins）を通らない。ただし入口の SHA-256 の一致と binding の SHA-256 の一致を自分で確かめ、書き込み先は既存の run- フォルダーに限られ、旧 chain の子としてしか使われないため、実害は見つからなかった。 | 次に入口を作り直す機会に、この分岐が hash 検査を通らない理由を README に1行書くか、分岐にも同じ検査を通す。今回は止める必要はない。 | New |

> R-08 Reviewer note: 新しい試験は仮の safaridriver（spawn の差し替え）と仮の fetch で runBrowser("safari") を最後まで動かし、AbortSignal.timeout に渡った値を要求ごとに記録して、GET /status 10000、POST /session 60000、POST /session/s1/url 10000、POST /session/s1/execute/sync 10000、DELETE /session/s1 10000 の完全一致を要求する。driver が SIGTERM で止まることと spawn の引数も確かめる。差し替えは finally で元に戻し（spawn は syncBuiltinESMExports で ESM 側にも戻す）、AbortSignal.timeout の包みは元の関数を呼ぶだけで残る timer は unref されるため、漏れや他の試験への影響は見つからなかった。u11-browser-driver.mjs は変わっていない（2adf5422…）。60000 を 10000 に変えると完全一致が崩れるので、この試験が落ちる。

> R-09 Reviewer note: 入口は main の先頭で --entry-sha256 と --binding-sha256 をこの順に要求し、形式、自分自身のファイルの SHA-256、binding-05.json の SHA-256、入口の定数との一致を確かめ、不一致なら何も検査せず何も書かずに exit 2 で止まる。コマンド行そのものに2つの hash が入るので、人の採用の承認で固定される。正常終了時にも入口の bytes が検査中に変わっていないことを再確認する。

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| ファイルの読取のみ（shell 不使用） | run-1792277217598397000-59240/result.json は u11_candidate_v2 PASS で、command_line の entry_sha256 56870072…、binding_sha256 a3d81077… が入口の定数・binding と一致。binding-05 は chain 1ceae86c、2b8723ab、57a8c96f、3 run（CI 39073492190、Release 39073492188、U12 39073501121 attempt 2）、attempt 1 の失敗 117515797287 の記録、Safari の job の id、u14-quality の不起動、Step30 の5ファイルの履歴 pin を持つ。 | 実行はしていない。保存された結果とコードの読取による判断である。 |
| binding-04 との比較（読取） | 緩んだ検査は見つからなかった。許可は Safari の2ファイル（path は定数）と U11 の4記録（定数）のままで、binding-03、binding-02、U1 の checker の pin は同じ。commit ごとの変更ファイルが Safari の2ファイルの部分集合であることに加え、1ceae86c から head までの差分がちょうど2ファイルであることを要求する。Safari の job は run ごとに bound な job id と成功を要求する点が強くなった。Step30 の入口・binding-04・CI JSON は履歴として hash で固定される。 | 検査は強くなっただけである。 |
| U11 の記録（読取） | code-summary の「現行Step31」節は、head、親、tree、SHA-256、10件成功、3 run の job 数、attempt 1 の Intel 000606a6 による停止（設計どおりの停止で、原因は製品でも Safari でもない）を、binding-05 と整合して記している。計画の Step 31 は完了済みで、Step 29・30 の記述は変わっていない。 | 記録は正確である。 |

### Summary

R-08 は仮の spawn と fetch で 60000 と 10000 の分担を要求ごとに完全一致で確かめる試験で直り、R-09 は引数なしを先に拒否する2つの hash 付きコマンド行で直った。binding-04 から緩んだ検査はなく、CI の束ね方も健全で、残るのは Minor 1件だけである。
