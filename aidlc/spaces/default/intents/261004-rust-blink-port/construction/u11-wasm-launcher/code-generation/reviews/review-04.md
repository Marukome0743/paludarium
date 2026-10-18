## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-14T11:50:51Z
**Iteration:** 2
**Verdict Dictated:** no
**Request ID:** review:f11983e64f25a3d6a946b2361ec87250

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | Resolved (reviewer) |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | Resolved (reviewer) |
| R-03 | Major | packages/paludarium-wasm/index.mjs > createFileSystem / filesystem.dispose(), line 76 | 検証済み：同一 handle に対する同時の二重 dispose は冪等にならない。`Promise.allSettled([fs.dispose(), fs.dispose()])` を現行 package の実 Wasm で実行すると、一つは fulfilled、もう一つは PaludariumError(kind=internal) で rejected になる。disposed は最初の control 完了後にだけ更新されるため、二つ目も filesystem-drop を送り、ABI の stale handle 拒否に到達する。既存 u11-api-check.mjs は逐次二重呼出しだけを検査している。 | handle ごとに進行中の dispose Promise を共有し、同時呼出しが同じ結果を受け取るようにする。active lease による拒否後は再試行できる状態を保持する。同時二重呼出しの実 Wasm 回帰と、active 拒否後の release / dispose 成功を検査する。 | Resolved (reviewer) |
| R-04 | Critical | packages/paludarium-wasm/package.json > files; packages/paludarium-wasm/worker-support.mjs > jitImports import | 検証済み：worker-support.mjs が ./jit-support.mjs を無条件で import するが、npm pack --dry-run の全10 entriesに jit-support.mjs が含まれないため、配布パッケージの index.mjs はモジュール解決に失敗する。ローカルにはこのファイルが存在するので実Wasm API試験の成功では検出できない。 | jit-support.mjs を配布ファイル一覧へ追加し、配布対象ファイルだけで構成したパッケージの import と実Wasm起動を確認する。必要JSのimport先が全て梱包される検査を追加する。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/unit-test-instructions.md > Current Steps14–16 Setup / Current U11-scoped commands | 検証済み：現在という見出しの手順は Python3.15.0・nightly-2026-10-10 を指定するが、手元のPython実体は3.14.7、現在のrust-toolchain.tomlはnightly-2026-10-11である。Chromium/Firefox準備はChromium1248実体欠落、Safari準備はdriver-startup exit1で停止した。独立レビューでは指定Python、ブラウザ14件、Linux coverage80%、600秒ASan/LSanを新規実行できていない。 | 保存した実行時のツール指定と現在の再実行手順を明確に分け、Python/ブラウザ準備を満たした環境で不足する確認を行うか、保存済み有限観測の適用範囲と今回未実行の項目を明記する。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| Manifest / differential inspection | 329 claimed pathsを全件読み取り、欠落0。保存署名a19bea3549a77a0f665b20626d65049ecc6e2f6aとの相違は32 paths。2b387→a19のdispose修正はindex.mjsとu11-api-check.mjsの2 files。 | 保存観測と現在sourceを区別。後続JIT差分でworker-support.mjsに必須importが追加されたがpackage filesは追加されていない。329 filesが全て今回新規変更という主張には読み替えない。 |
| Traceability / shared contracts | 63 upstream IDsのcoverageを確認。coverage targetsの存在チェックは欠落0。C2/C10/C12とU11、担当外Deferredの境界を確認。 | 同時disposeはC12の互換追加範囲。今回の梱包欠落はFR5.2のwasm＋起動JS配布を壊す。 |
| Node unit tests | Node26.11.1実体で指定5 test filesを --test 実行。32 passed / 0 failed / exit0。 | 契約7、driver8、filesystem7、Worker7、signed mtime3。browser実行を代替しない。 |
| Python runner readiness / unit tests | mise実体Python3.14.7で scripts/u11-run.py --self-test はexit0、unittest discoverは24 tests / OK / exit0。 | 指定Python3.15.0での実行は未検証。付属python3による結果と指定版の結果を同一視しない。 |
| Rust test --locked -p paludarium-kernel --test u11_fuzz_wait | 7 passed / 0 failed / exit0。 | 空pipe待機を含む有限quota回帰が成功。600秒fuzz実行ではない。 |
| Rust test --locked -p paludarium-host --lib wasm_tasks | 7 passed / 0 failed / exit0。 | task ownership / join / start failure / panic境界を確認。 |
| Rust test --locked -p paludarium-wasm --lib | 15 passed / 0 failed / exit0。 | PrivateFsのIdle/Active/Closedとsigned mtimeを確認。 |
| Rust test --locked -p paludarium-vfs --lib u11_tests | 8 passed / 0 failed / exit0。 | realtime時刻とhardlink共有、旧unsigned最大値の境界を確認。 |
| Rust test --locked -p paludarium-kernel --lib u11_tests | 7 passed / 0 failed / exit0。 | cwd正常/異常を確認。上記Rust計44 testsは手順が指定するnightly-2026-10-10実体で実行。 |
| Actual production Wasm API | node packages/paludarium-wasm/tests/u11-api-check.mjs packages/paludarium-wasm/paludarium.wasmを既存supervisorで外部60秒監督。exit0 / timed_out=false / process_group_cleaned=true。出力：U11 API: modes, ownership, concurrent disposal, large FS, busy rejection/retry, terminal validation, kill/release PASS。 | ローカル実moduleのC12同時dispose、68MiB、active拒否/kill後再試行が成功。梱包済みmoduleの起動確認ではない。 |
| Browser readiness chromium firefox | 既存supervisor外部60秒。child exit1 / timed_out=false / cleaned=true。Executable doesn't exist at chromium_headless_shell-1248。 | Chromium準備で停止、Firefoxまで未到達。14guestを開始しなかった。 |
| Browser readiness safari | 既存supervisor外部60秒。child exit1 / timed_out=false / cleaned=true。Safari driver-startup: driver exit=1。 | 本物Safariの準備未成立。保存済みSafari成功は今回の新規実行ではない。 |
| npm pack --dry-run --ignore-scripts --json | Node26.11.1付属npm11.20.0。既存cacheへの最初の実行はEPERM/exit255。project target cacheで再試行しexit0 / entryCount10、jit-support.mjsなし。 | Criticalを確認。公開・archive作成なし。旧npm12.2.0保存packの観測へ読み替えない。 |
| python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-preview13-bound.py | 独立実行exit0。All thirty-four mandatory quality jobs and unchanged historical predicates passed。367 current inputs中366 identical＋mise.toml exact preview delta、signed head62611f2556c4caf1470a7eb4471269d92611db6e、legacy_u10_checks passed。 | 保存CI・歴史述語の照合成功でありfresh guest実行ではない。U11 two-file CI bridgeも照合成功。U14性能・standalone jit_compile panic未解消を明記する出力は保持し、U11 dispose不具合へ混同しない。現在のnpm import欠落をこの保存証拠照合は検出しない。 |

### Execution Details

Node実体は `/Users/mutoakio/.local/share/mise/installs/node/latest/bin/node`（v26.11.1）、Python補足試験は `/Users/mutoakio/.local/share/mise/installs/python/latest/bin/python3`（3.14.7）。Rustは各表のargvを `/Users/mutoakio/.rustup/toolchains/nightly-2026-10-10-aarch64-apple-darwin/bin/cargo` に渡し、`RUSTC=/Users/mutoakio/.rustup/toolchains/nightly-2026-10-10-aarch64-apple-darwin/bin/rustc` を設定した。Nodeのunit argvは `--test packages/paludarium-wasm/tests/u11-contract.test.mjs packages/paludarium-wasm/tests/u11-browser-driver.test.mjs packages/paludarium-wasm/tests/u11-filesystem.test.mjs packages/paludarium-wasm/tests/u11-worker-support.test.mjs packages/paludarium-wasm/tests/u7-mtime-snapshot.test.mjs`。Python unit argvは `-m unittest discover -s tests/guests/u11/runner-tests -p 'test_*.py'`。

npm再試行は上記Node実体で同配下の `lib/node_modules/npm/bin/npm-cli.js pack --dry-run --ignore-scripts --json --cache=/Users/mutoakio/Documents/paludarium/target/u11-review-npm-cache` をpackages/paludarium-wasmで実行した。初回jj diffはworking-copy snapshotの権限エラーで失敗、`jj --ignore-working-copy diff`で読取差分を取得した。保存署名の329bytes比較はread-only `git show` を使用した。今回のレビューはsource・成果物・品質下限を変更していない。

Linux native fresh oracle、4環境×14guest、80%coverageのLinux測定、7対象各600秒ASan/LSan、Wasm再buildは重複実行しなかった。Mac上の指定Python/ブラウザ準備が満たされず、保存済み有限CI照合は新規実行の代替としない。coverage80%という保存主張について今回新しく測定したcoverageはない。

### Summary

同時dispose修正は実Wasmと限定回帰で成功したが、現在の配布設定は無条件importされるJIT補助JSを梱包しないため配布版が起動できない。保存済み成功とローカルsourceでの成功を分け、パッケージそのものの起動確認が必要である。
