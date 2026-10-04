## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T22:02:15Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/functional-design/functional-spec.md > Workflows「反復と中断」手順 3・5、State Transitions の memory fault 行; aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/functional-design/rules.md > BR1.6; aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/functional-design/entities.md > CpuState | ドキュメント根拠：反復の成功ごとに必要なフラグを更新し、fault 時にも完了分の状態を返すという一律の規則は、REPE/REPNE CMPS/SCAS の例外時意味論と一致しない。Intel SDM の REP 項はこの場合、EFLAGS を命令開始前へ復元すると定義する。例えば初期 ZF=0 の REPE CMPS が一回の一致比較で ZF=1 となり、次の反復でページ fault になると、index/count は進んだままでも flags は命令開始前へ戻す必要がある。現在の規則では最後の比較の flags を公開する。予算切れで一旦 Runtime に戻った後に fault する場合も、元の flags を保持する状態がモデルにない。実装動作と native 再現は未検証。 | 反復命令を MOVS/STOS 等と条件比較 CMPS/SCAS に分け、REPE/REPNE CMPS/SCAS の fault 時に復元する flags、保持する index/count、faulting RIP を明記する。命令開始時 flags を内部予算中断をまたいで保持し、完了・fault・別命令への移行で破棄する状態と再開契約を CpuState または別の実行継続状態に定義する。少なくとも「成功反復後の page fault」と「予算中断後の page fault」で native の例外時レジスタ・flags と比較するケースを追加し、シグナル番号だけの比較にしない。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| PowerShell ConvertFrom-Json と BR の正規表現照合 | 検証済み：`rules=16 targets=16 unresolved= orphan=` | 16 規則はすべて coverage から参照され、存在しない BR と未説明の orphan はない。 |
| 上流 unit-of-work-story-map.md と要件の照合 | ドキュメント根拠：ユーザーストーリー工程を省略し FR を対応させる方針。U2 に FR1.3・FR1.6 を割り当てる | 独立した AC ID を新しく要求しない。割当 FR1.3・FR1.6 は traceability に存在し、対象規則へ解決する。追加の FR1.5・FR9.1・NFR は関連する境界・検証として整合する。 |
| C1/C3/C4/C5 と components.md の照合 | ドキュメント根拠：Kernel.Thread が CpuState を所有、Cpu は Kernel を呼ばず、Mmu は Cpu/Kernel に依存しない | 共通排他・原子更新の担当を U2、clone/futex 統合を U5 とする Q1 に整合。共有契約の範囲内で照合し、他 Unit の construction は読んでいない。 |
| Intel 公式 SDM 検索 | ドキュメント根拠：REP 項の CMPS/SCAS fault 特例を公式 PDF の検索結果で確認 | R-01 の外部根拠。結合 PDF の open はサイズ超過で失敗したため、ページ画像や native 実行を確認したとは主張しない。 |
| Stage definition | 指定の validation CLI はない。sensor は required-sections/upstream-coverage/linter/type-check/traceability | 独立の ID 検査を上記で実施。Rust 動作は設計レビューの検証対象ではなく未検証。 |
| Bash UTC timestamp | 検証済み：`date -u +"%Y-%m-%dT%H:%M:%SZ"` は `2026-10-04T22:02:15Z` | 推定日時を使わず、実出力を記録。 |

### 仕様根拠

[Intel 64 and IA-32 Architectures Software Developer’s Manual](https://cdrdv2-public.intel.com/835781/325462-sdm-vol-1-2abcd-3abcd-4.pdf)、Volume 2、REP/REPE/REPZ/REPNE/REPNZ の説明：REPE/REPNE CMPS/SCAS の fault 時に “EFLAGS value is restored to the state prior to the execution of the instruction.” と規定する。これは最後の成功反復の index/count を維持する規則とは別の、flags の復元規則である。

### Summary

原子操作の所有と共通同期、未対応命令の停止、毎回の native 期待値取得は共有契約と整合する。一方、反復比較命令の fault 状態と内部中断をまたぐ復元情報が欠け、記載どおりの実装では要求する x86 の状態と一致しないため NOT-READY。
