# 現在sourceの検証記録（2026-10-08）

## 最終sourceとCI

検証済み：4d52be0a6f3b11d6c11a62f96196985c9c280fdc、GitHub verified:true/reason:valid。CI37695518838は全7jobs、native37695518927は全4jobs成功。実行コマンド・CPU・test名・件数はverification/final-{ubuntu,bookworm,mac,windows,coverage}-4d52be0a.log。詳細とリンクはcode-summary.md。

Windows Host25/Runtime25/VFS45件通過。Ubuntu/BookwormのAMD EPYC7763で全workspaceが通過し、両方の差分はU1 16/U2 38/U4 44/U7 63件。全体行coverage7030/未実行522=92.57%、U1対象11packages6780/未実行1172=82.71%。両下限80%を維持する。

Intel e081の全workspace成功は先行証拠。e081→最終のCPU・decoder・REP observer/fixture・SSE guestはjj diff0。最終runのIntel全workspace再実行とは呼ばない。

## 期待結果・修復前失敗・手元検証

verification/repair-implementation-results.md、host-repair-results.md、runtime-cleanup-results.md、vfs-cleanup-results.mdと各ログを参照。SSE native期待結果とRedは実装前、内部単体はtest-after。Windows修復前raw32はHost/Runtime/VFSの各strict cleanupに記録され、後片付けの失敗を実際の機能assertionの失敗と断定しない。

Docker限定検証の通過とQEMU oracle差による全workspace失敗を区別する。ENTER allocation faultやsignal/errno差のログは保持する。

## 静的照合と所有

検証済み：python3 aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/check-current-source.py、exit0。103claims/108files、欠落・未追跡・現在U1 snapshot不一致0。上流47/対応47・OK target欠落0、census68根拠欠落0。Cargo.lock SHA256553b2b8d7670426ed73c51f1d756b93a6a8b26bc427de87afa01a15f60264b27。

U7以前のsnapshotとの差5filesはLF/Host/Runtime/VFSの関連修復。以前のsnapshotは履歴として保持し、独立後続unit成果物を作り直さない。現在のmanifest/traceabilityは実ファイルの対応であり、全quality targetの合格宣言ではない。以前の本文はevidence-before-host-repair-20261008.mdへ保持した。

## 復旧と未検証

検証済み：plan-approval-guardとcontinue-workflowは登録済み、bun test tools/aidlc-recovery/recovery.test.tsは9pass/0fail/37assertions。rejected reportの直前にも両方を再確認する。

未検証：今回のwasm/Safari、U1各fuzz再実行、decoder候補比較の歴史的ログ。固定nightly、各600秒、coverage80%、30秒watchdog、比較maskを維持する。先行197件/94.00%等の値を現在の合格へ転用しない。
