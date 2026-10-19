## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-10T04:12:57Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | New |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| aidlc engine now | 2026-10-10T04:12:57Z | レビュー日時の実出力。 |
| jj --ignore-working-copy diff --from 5b319a7072e698d8e7c2f94e4821bf584ec381fb --to 7eb1819f52acede33e83775374dd4ee93edf643b（manifest対象を指定） | 共有Runtime/VFSのmtime・cwd追加、wasm ABI/private VFS、実guest Worker、起動JS、専用比較器・CIの差分を確認 | 契約C2/C10/C12とFR5・FR6・FR7・FR9を照合。sibling constructionは読まず、sourceは変更していない。 |
| /Users/mutoakio/.local/share/mise/installs/node/24.21.0/bin/node --test packages/paludarium-wasm/tests/u11-contract.test.mjs packages/paludarium-wasm/tests/u11-filesystem.test.mjs packages/paludarium-wasm/tests/u11-worker-support.test.mjs packages/paludarium-wasm/tests/u11-browser-driver.test.mjs | tests 29; pass 29; fail 0; exit 0 | 契約、fixture比較、bulk-copy所有、Worker import、WebDriver境界の既存試験は成功。large-VFS破棄の境界はカバーしていない。 |
| Node v24.21.0の実production moduleによるlarge-VFS境界再現 | filesystem created with 68 MiB; dispose FAIL internal Error: filesystem disposal rejected (active or stale handle); launcher.dispose後exit 0 | 1件目のMajorを実行で確認。両ファイルは個別のbuffer上限以内で、guest実行もactive leaseもない。 |
| native_fs.rsの限定jj差分とFileStatの読取 | stat/cap_stat双方がduration_since(UNIX_EPOCH).map_err(EIO)、mtime_nsはu64 | 2件目のMajorの条件と失敗分岐をコード上で確認。確認手順：許可された一時fixtureのmtimeを-1秒に設定し、NativeFs.metadataとopenしたFileHandle.statを実行する。実機試験は未検証。 |
| final-7eb-ciのNode/Chromium/Firefoxとfinal-7eb-safari-attempt3のobservations.json・suite-supervisor.jsonをNodeで集計 | 各14ケースcomplete=true、全行pass/exit0/timeoutなし、監督exit0/cleanup=true | 検証済み（保存生証拠）：Node24.21.0、Chromium153.0.8010.12、Firefox155.0、実Safari26.6.2。同じmodule f459285f6bdc6f282d409533cc3daf25af3d46860a6cb86adb074f93fd242d1f、oracle 6df71b705f1826a5e6bd65bd7233a989f2911ff964d016b1ac28824bee81ac60。手元wasmも同module hash。旧Safari準備失敗は成功へ読み替えていない。 |
| final-7eb-ci/u11-coverage-lcov/u11-coverage.lcovのLF/LH集計 | 5657/6559 = 86.24790364384815% | 80%下限を満たすLinux native cfgの測定。wasm固有分岐の実行coverageや全入力の正しさの証明ではない。 |
| Stage validation-tools / formal checker | stageにvalidation-tools指定なし。verify-current-u11-wasm-launcher.pyは未実行 | 正式checkerは人の変更承認待ちというdispatch条件を維持。600秒fuzzと全CIは再実行していない。 |

### Reproduction Detail

large-VFSの再現は以下のread-only Node invocationで行った。製品sourceと成果物は変更していない。

```sh
/Users/mutoakio/.local/share/mise/installs/node/24.21.0/bin/node -e '(async()=>{ const {createPaludarium}=await import("./packages/paludarium-wasm/index.mjs"); const {pathToFileURL}=await import("node:url"); const l=await createPaludarium({wasmUrl:pathToFileURL(process.cwd()+"/packages/paludarium-wasm/paludarium.wasm")}); const timer=setTimeout(()=>process.exit(2),20000); try { const fs=await l.createFileSystem({files:{"/a":new Uint8Array(34*1024*1024),"/b":new Uint8Array(34*1024*1024)}}); console.log("filesystem created with 68 MiB"); try {await fs.dispose();console.log("dispose PASS");} catch(e){console.log("dispose FAIL", e.kind, e.message);} } finally {await l.dispose();clearTimeout(timer);} })()'
```

追加の1900階層snapshot観測は15秒の外部期限まで完了しなかったが、性能・deadlock・trapの原因を区別できていないため、指摘には採用していない。入力上限・深さに対する保証は未検証。

### Summary

共有Kernel/MMU、Worker個別stack/TLS、private VFS lease、guest停止とエミュレータエラーの境界は実装と有限の4環境受入証拠で追跡できる。Criticalなし・Major2件というレビュー基準に従うREADYであり、上記の破棄失敗とhost stat回帰を修正する必要、および正式検証・人の完了承認を代替しない。
