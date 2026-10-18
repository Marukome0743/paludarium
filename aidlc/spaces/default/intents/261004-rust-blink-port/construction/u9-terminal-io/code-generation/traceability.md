# U9 要件と実装・証拠の対応

## Steps16〜18の現行分類

検証済み：fresh native Linux差分14、3 OS内部/API/doc/CLI、旧13ファイルcoverage84.1037%と追加10ファイル89.9458%、Node/本物Safari現行20ケース、load_elf601秒ASan/LSanを取得した。全294入力・両lock一致はSafari独立監査を除く各ジョブで確認。Safariは同じ署名SHA checkoutとmodule/native artifact SHA一致に限定する。

残る正式GAPはNFR3（最新Clippy exit101）、NFR8（cargo-deny未到達）、NFR9（製品pinと最新診断版の不一致）。全CIはfailureであり完了合格ではない。具体的な原ログ・最小未適用修正はverification/step16-findings.mdとstep16-linux-quality-job.log。正式状態はtraceability.jsonを参照する。

## Steps13〜15の履歴分類

今回macOS内部23/API6/compile_fail3/CLI2成功。現行U9 Linux差分・専用coverage・productionwasm/Safariは未検証。旧依存byte不一致につきFR9.1/NFR1/NFR2/NFR3/NFR8/NFR9をGAPへ更新した。正式な状態はtraceability.json、履歴成功は下の当時記録として区別する。最新同source U7 3ASan各601秒は対象限定再利用、load_elfのみ追加案。詳細step13-source-comparison.jsonとstep13-sanitizer-reuse.md。

## 保存履歴（現行合格へ読み替えない）

直接FR4/4.1/4.2、FR9.1と適用NFRを対象にする。OKは実装・テストtargetの対応で、未測定の全挙動を合格としない。

|ID|状態|target|
|---|---|---|
|FR4|OK|crates/paludarium-harness/tests/diff_u9.rs|
|FR4.1|OK|crates/paludarium-runtime/src/u9_tests.rs|
|FR4.2|OK|crates/paludarium-kernel/src/syscalls.rs|
|FR9.1|OK|tests/guests/u9/oracle.py|
|NFR1|OK|crates/paludarium-harness/tests/diff_u9.rs|
|NFR2|GAP|crates/paludarium-kernel/src/u9_tests.rs|
|NFR3|GAP|crates/paludarium-host/src/lib.rs|
|NFR4|OK|crates/paludarium-kernel/src/syscalls.rs|
|NFR5|OK|crates/paludarium-host/src/testing.rs|
|NFR6|N/A|U9に新しい速度目標なし。U10/U14担当の速度測定を本Unitで主張しない。|
|NFR7|OK|crates/paludarium-harness/tests/support/u9.rs|
|NFR8|OK|.github/workflows/ci.yml|
|NFR9|OK|rust-toolchain.toml|

NFR2/NFR3は現行600秒ASan未検証のGAP。macOS/Windows実機端末、wasm/Safari、probe/aube全体は未検証。NFR6にはU9専用性能目標がない。NativeLinuxの14ケースは実装前に期待結果を取得し、差分ごとにnativeを再実行する。

検証済み：署名af9b739dのCI7+native4 jobs成功、18 claimed source bytes一致。Linux U9追加実行可能製品行122/130＝93.846%（unchanged/deleted/tests/non-instrumented除外）、80%を満たす。coverageのGAPは解消し、NFR2/NFR3は現行600秒ASan未検証のGAPを維持する。
