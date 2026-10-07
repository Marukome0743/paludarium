# U2 コード生成の現在source確認

## 今回の結果

検証済み：承認済みStep20〜23を実行し、U2の95source claimsとCI対象127pathsがproduction revision `4d52be0a6f3b11d6c11a62f96196985c9c280fdc` のbytesに一致した。今回はU2記録だけを更新し、製品・テスト・U1凍結成果物は変更していない。現在の実機CI証拠を照合して再利用し、テストを再実行したとは表現しない。

[CI37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838) の7jobsと [native37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927) の4jobsは成功。実機Linux U2差分38件・ホスト並行10件、3OS既存suite、fmt/clippy、依存検査、全体行coverage92.57%を確認。80%下限を維持した。詳細ログ・source snapshotは evidence-current.md と verification/ にまとめ、レビューにU1記録の読取を要求しない。

## 現在の実装と契約

C1 ArithmeticFaultはKernelでSIGFPEへ渡り、C3の幅/prefix/暗黙operandをC5が解釈する。C4のtyped atomicと通常アクセス/mappingは共通同期に参加する。FS/GS atomicの最終linear address、failed compareのwrite preflight、128-bit alignment、REP再開を現在sourceとnative回帰へ照合した。

REPfault flagsは明示的なCpuState policyで、既定 `RestoreInitial` はIntel設計の開始flags復元を維持する。`PreserveCompleted` は観測済みAMD EPYC modelで、productionがhost CPUを検出して変更することはない。native差分fixtureだけがobserverのCPUID vendorに応じて選択し、未知vendorを失敗にする。start/partial/budget/fetchの両model内部testsは通過。現在native runnerはAMD、Intel成功はe081時点の履歴で、関連7sourceのbytes一致を確認した。

固定inventoryはaube4658forms（整数3136/system190/U3 1332）、probe865forms（整数696/system3/U3 166）。分類分母とnative-case参照を保持する。追加15/15命令群の対応はfamilyの対応であり、全static bytesや任意入力の一致率ではない。probe/aube全program統合はU10、clone/futexはU5、wasmはU11、JITはU14へ残る。

## 更新した記録と所有境界

code-summary.md、evidence-current.md、traceability.json、source-manifest.jsonの現claim照合snapshot、およびplan Step20〜23のチェックを更新。先行summary/evidence-current/traceabilityは historical-* に保存し、evidence.mdと旧reviewsを保持した。manifestのstrict schemaと95 owning pathsを維持し、共有CPU/observerのREP修復は現在source確認対象として説明する。新しいapplication-sourceは作成・変更・削除していない。

## 品質の限界

未検証：REP修復後の現在sourceで各600秒ASanを実行していない。過去のCPU/MMU fuzz成功は旧sourceの履歴であり、NFR2.2とfuzzを含むNFR2/NFR3/NFR3.4はtraceabilityでGAPにした。既存nightly各600秒、30秒watchdog、nightly-2026-10-01、比較mask、coverage80%を変更していない。

未検証：全vendor・任意入力/経路、完全runtime inventory、probe/aube emulator全program、wasm/Safari/JIT統合。今回のCI成功をこれらの証明に使わない。具体的な新製品不具合は今回の照合では見つからず、独立reviewと完了判定はconductorへ渡す。
