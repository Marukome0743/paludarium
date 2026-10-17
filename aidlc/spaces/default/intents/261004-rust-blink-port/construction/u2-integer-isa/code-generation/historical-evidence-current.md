# U2 現在sourceと保存済み証拠の照合

## 今回行った確認

検証済み：正式Codex `aidlc-testing-posture.ts verify --unit u2-integer-isa` はexit0、reason approved、execution_allowed/approved/contractValid/fingerprintValid/receiptValidすべてtrue。承認済みtool brief全文を読んでStep17〜19を実行した。application/U1/README/既存reviewは変更せず、新しいテスト・全体coverage・10分fuzz・guest rebuildは実行していない。

PowerShell Get-FileHash -Algorithm SHA256 による今回の読取：
- crates/paludarium-cpu/src/exec.rs: e5f052c58761a8d391d1bf438a7b8147b9300f9fa8c39fe1fa66f1d53ba9f4f0
- crates/paludarium-cpu/src/u2_tests.rs: 4b2680bdc99b5c3263f2472a6b4000b030810df0958fd76d82e896f529865d7f
- 本unit source-manifest.json: 40233c4c56fd123f8977c9a4fda94f58b38b32e9b8762bc58bae62f24bf972cc（95 claims、実ファイル欠落0）

CPU2ファイルは先行最終検証の保存SHAと一致し、manifestも再開準備前後で不変。他の全sourceについてこの2hashだけで不変を断定しない。現在のclaimsとC1/C3/C4/C5利用経路、FS/GS atomic linear address、CMPXCHG16B最終address alignment、ArithmeticFault consumer、REP continuation、native observer/外側watchdogの既存source・保存証拠を照合した。新たなproduction修正が必要なGAPは今回の照合では見つかっていない。

## 保存済み観測の再確認

以下は先行実行の証拠を今回読み直した結果で、新しいtest実行ではない。
- docs/u2/repairs/r01-workspace-coverage.txt:78 CPU31 passed、:450 U2diff38 passed、:527 parallel10 passed、:670 TOTAL lines4233/missed254/94.00%。先行実行exit0、全体197 parent tests。行coverageと意味論forms coverageを区別する。
- r01-segment-red.txt/r01-gs-fault-red.txt とgreen各ファイル：FS/GS/addr32/mapped decoy/final permission・alignmentのRed→Green。raw flags0x10ad7、mask0xcd5を保持。新しくnative baselineを作ったとは表現しない。
- r01-cpu-fuzz-final.txt:6030 Done1276258 runs in601seconds、r01-mmu-fuzz-final.txt:2223 Done1706799 runs in601seconds。先行単一runner全体exit0。初回filesystem読取失敗r01-cpu-fuzz-sync-failure.txtも保持。
- u2-cargo-deny.txt: advisories ok, bans ok, licenses ok, sources ok。先行Windows公式asset digest照合後の--locked check exit0。初回Linux missing-command失敗も履歴として保持。

## 固定取得とケース対応

build-receipt.jsonを今回読取：aube v2.6.1 revision bd94e42f54d3b5e3dd102716b7197f316cb5f4ed、lock8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668、新binary ff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a。固定builder image1e2dc83323f45ab604cca62dd57b27232149353c1017178f3c040f7bd46b5960。build command/primer/dirty snapshot/compilerはreceiptに保持される。probe binary15e90407b6cc2dc8389048805475fb9c7b11d3e10f89c1da0d52dad7b1c99292は原artifactと一致、dirty snapshotをreceiptに保持。

aube.form-comparison.jsonは旧新4658forms、differences空。classification.formsのGroup-Object categoryによる今回再集計はaube4658（整数3136/system190/U3 1332）、probe865（整数696/system3/U3 166）。native_casesのu2_* tokensをdiff_u2.rsと照合し未対応token0。幅/prefix/implicit operandとfamily/dimensionの対応表・補足memory/prefix casesを既存docsへ照合した。これは全静的bytesを同一配置で新しく実行した割合ではなく、対応表の存在と保存済みnative casesの照合である。bounded body sampleとcomplete_runtime_inventory:false、原artifactの歴史上のbuilder由来未確定を維持する。

## traceability・限界

security-requirements.mdの詳細NFR16件を抽出しtraceability.coverageへ照合、欠落0。coverage44/upstream28。従来複数refsを連結したtargetはStage定義に従う実在する単一implementation/test/config fileへ整合し、全追加refsをnotesに保存した。追加refs実ファイル欠落0。

未検証：全任意入力/経路、U10のemulator全program統合、U5guest clone/futex、U11wasm/macOS/Safari環境、U14JIT。今回保存証拠の再確認をそれらの新合格へ転用しない。80%/各case30秒/夜間各600秒/nightly pin/custom順序を維持。別projectのbackground buildは停止せず、性能測定を行わない。
最終jj追跡確認：mise glob実体で jj --config snapshot.max-new-file-size=2097152 file list を読み、manifest95claims NOT_TRACKED0。traceability全追加refs欠落0。source読取rgの一回は存在しないharness/build.rs指定でexit1だったが、src/lib.rsのTIMEOUT30秒/child killは出力された。誤パスは検証失敗として区別し、既存保存済み差分/並行通過の証拠を代替の新実行とはしない。
