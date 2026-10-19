## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-11T02:43:01Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | packages/paludarium-wasm/coordinator.mjs > filesystem-drop; crates/paludarium-wasm/src/abi.rs > filesystem_snapshot | 検証済み：停止中のprivate VFSに34 MiBのファイルを2個配置すると作成は成功するが、dispose()はinternalエラーで失敗し資源を保持する。破棄前の占有確認が全内容のsnapshotを生成し、その64 MiB上限を占有・staleと誤判定するため、launcher全体を破棄しなければこのVFSを解放できない。 | 全内容を読み出さずにactive leaseを確認してVFSを解放するABIを用意し、launcherを維持したまま合計64 MiBを超える停止中VFSを破棄できる回帰試験を追加する。占有中の破棄拒否と二重破棄の既存動作も維持する。 | New |
| R-02 | Major | crates/paludarium-host/src/native_fs.rs > stat and cap_stat; crates/paludarium-host/src/fs.rs > FileStat.mtime_ns | 検証済み（コード差分）：mtime対応の追加で、1970年より前の合法なホストファイルのmetadata/fstatがduration_since(UNIX_EPOCH)の失敗をEIOへ変換する。以前は同じファイルのinode・size・mode・linksを返せたが、現在は時刻の表現範囲だけを理由にstat全体が失敗する。実ファイルでの再現は未検証。 | 負の秒を含むホストmtimeを表現できる型とguest statへの変換を定義し、metadataと開いたFileHandle.statの双方にmtime=-1秒の回帰試験を追加する。新しいmtimeフィールドによって既存ホストファイルのstatを失敗させない。 | New |
| R-03 | Major | packages/paludarium-wasm/index.mjs > createFileSystem / filesystem.dispose(), line 76 | 検証済み：同一 handle に対する同時の二重 dispose は冪等にならない。`Promise.allSettled([fs.dispose(), fs.dispose()])` を現行 package の実 Wasm で実行すると、一つは fulfilled、もう一つは PaludariumError(kind=internal) で rejected になる。disposed は最初の control 完了後にだけ更新されるため、二つ目も filesystem-drop を送り、ABI の stale handle 拒否に到達する。既存 u11-api-check.mjs は逐次二重呼出しだけを検査している。 | handle ごとに進行中の dispose Promise を共有し、同時呼出しが同じ結果を受け取るようにする。active lease による拒否後は再試行できる状態を保持する。同時二重呼出しの実 Wasm 回帰と、active 拒否後の release / dispose 成功を検査する。 | New |

> R-01 Not re-checked this round

> R-02 Not re-checked this round

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `aidlc engine sensor-traceability --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/traceability.json --stage-slug code-generation` | PASS; findings_count=0 | 検証済み：宣言、対象、上流 coverage の構造チェックに問題なし。 |
| `aidlc engine sensor-required-sections --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u11-wasm-launcher/code-generation/code-summary.md --stage-slug code-generation` | PASS; h2_count=5; findings_count=0 | 検証済み：summary の所定構造を満たす。 |
| 読取専用 Node 原本照合（fs.readFileSync / SHA256 / assertions） | 329 application 入力と helper 2 の現行 hash 一致。handoff hashes は builder plan / test instructions を読まず、それ以外すべて一致。7 binary/raw hash 一致、各 Done … runs in 601 second(s)、exit.txt=0、両 lock 前後一致。4環境 raw hash、14/14、module/oracle/guest hash 一致。package Wasm hash も一致。 | 検証済み：現行 source / evidence の有限結合を独立確認。新候補 checker は実行していない。 |
| `jj --ignore-working-copy diff --from b263121214981a549ad8bfb7ddb975de03226f58 --to 2b3874eabda6fe6f1d1334202421db733445fd21 --name-only` | `.github/workflows/u11-fuzz.yml` のみ | 検証済み：4環境・JS coverage・U5/U6・pack の再利用境界が現行 source binding と一致する。 |
| `jj --ignore-working-copy diff --from 2c690e123ec2e8f28ccc672c2b0d79d7f5aa90f8 --to 2b3874eabda6fe6f1d1334202421db733445fd21 --name-only` | u11-current-verification.yml、u11-fuzz.yml、u11-api-check.mjs の3件のみ | 検証済み：旧品質結果の限定再利用について、Rust 製品 / lock 不変という主張に矛盾なし。旧全体 run の失敗は保持されている。 |
| 実 Wasm 同時 dispose 再現（下記） | exit0; `[{"status":"fulfilled"},{"status":"rejected","reason":{"name":"PaludariumError","kind":"internal"}}]` | 検証済み：新 Major finding を再現。 |
| 独立診断 raw.log 6293–6297 と syscall binary SHA256 | 1284919 runs / 601秒、既存 table_de 抑制 12 / 552。binary dd720889…2dfce は新品質 syscall binary と一致。 | 検証済み：新診断の抑制一致と binary 同一性。旧失敗の allocation 同定は旧 binary 欠落により推測のままであり、成功への読み替えはない。 |

**同時 dispose の実行コマンド**

```sh
/Users/mutoakio/.local/share/mise/installs/node/latest/bin/node -e 'const {pathToFileURL}=require("node:url"); (async()=>{const {createPaludarium}=await import("./packages/paludarium-wasm/index.mjs");const launcher=await createPaludarium({wasmUrl:pathToFileURL(process.cwd()+"/packages/paludarium-wasm/paludarium.wasm")});try {const fs=await launcher.createFileSystem();console.log(JSON.stringify(await Promise.allSettled([fs.dispose(),fs.dispose()])));} finally {await launcher.dispose();}})().catch(e=>{console.error(e);process.exitCode=1;});'
```

### Summary

READY：Critical 0、Major 1。大規模 idle FS の dispose は snapshot 上限から分離され、単一 lock の lease / closed 状態と ABI registry 除去順序に破綻は見つからないが、同時二重 dispose の冪等性は修正候補として残る。現行7対象の有限 ASan/LSan 観測、実4環境の入力一致、CI Safari26.6.2 と逐次 Safari27.0.1 の区別は確認できた。旧 LSan stack の直接同定、OS全体負荷独占、Wasm固有分岐の80%実行率は未検証という記載を維持し、U9先行完了の再承認および候補正式 checker の承認・実行を済んだとは扱わない。
