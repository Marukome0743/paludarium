## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-05T04:55:19Z
**Iteration:** 1

**Review artifact:** `aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/code-generation-plan.md`

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | crates/paludarium-cpu/src/exec.rs > Exec::alu 行264、unary 行304、cmpxchg 行762、xchg 行792/804、xadd 行829、cmpxchg_pair 行850 | 検証済み：GS base を有効な cell に設定して `lock incq %gs:0` を実行する同一 ELF は native で exit0・stdout `2a00000000000000`、emulator で exit139・stdout/stderr 空となる。ソース確認：これらの原子操作は `self.address()` を MMU に渡し、通常 read/write および原子的 bit 操作が使う `self.linear()` の FS/GS base 加算を省く。BR1.4 はメモリアクセスで fs/gs 基底を考慮することを要求する。segment-relative の有効なアクセスが異なる場所へアクセスし、未マップなら故障、マップ済みなら別のデータを更新し得る。後者および fault address0 の実行観測は未検証。 | 各原子操作のアドレスを FS/GS base を含む linear address に統一し、CMPXCHG16B の alignment 判定も最終 linear address で行う。修正前に native の期待値を取得し、FS/GS と非ゼロ base を使う LOCK ALU/unary、XCHG、XADD、CMPXCHG、CMPXCHG8B/16B の差分回帰を追加する。base を加える前の別セルを同時にマップして誤更新がないこと、addr32 では offset を切り詰めてから base を加えること、最終アドレスの権限と alignment を検証する。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| ステージ定義 | validation_tools: none | 必須外部 CLI は指定されていない。選択的ソース照合と具体的再現を使用した。 |
| PowerShell ConvertFrom-Json / 分類集計 / case token 照合 | aube total4658：整数3136、system190、U3 1332。probe total865：整数696、system3、U3 166。整数分類の native case token は diff_u2.rs にすべて存在 | 検証済み：全行の分類と参照の存在を確認。全 encoding を実行した証拠、全経路到達、意味論の正しさの証明には使わない。 |
| PowerShell NFR/BR coverage ID・manifest existence 検査 | NFR ids not covered / BR ids not covered / Manifest absent はすべて空 | 検証済み：適用 ID の欠落と存在しない source claim は検出されなかった。 |
| 凍結ソースでの Linux focused 再現（主導側実行、レビュー中に結果受領） | `gcc -x assembler -nostdlib -static -o target/u2-evidence/review-gs target/u2-evidence/review-gs.s`、`cargo build --locked -p paludarium` 成功。`timeout 30 target/u2-evidence/review-gs` native exit0 / hex2a00000000000000。`timeout 30 target/debug/paludarium target/u2-evidence/review-gs` emulator exit139 / stdout空。stderr回収 exit0 / 空 | 検証済み：R-01 の native/emulator 差を確認。結果は Linux volume `/work/target/u2-evidence/review-gs{.s,.native.stdout,.native.stderr,.emu.stdout,.emu.stderr}`。比較対象の guest と source は修正していない。 |
| evidence.md / code-summary.md / 実装・テスト照合 | REP の命令開始 flags/identity 継続、fault restore、ENTER の部分 memory effects、66 49 9d の qword POPF、共通 MMU lock/full permission preflight を実装と該当ケースで確認 | ドキュメント根拠・ソース確認。189 tests / 93.64% lines、各600秒 fuzz の成功は記録されたコマンドと出力の根拠であり、このレビューでは全体を再実行していない。最後の test-only 3件を coverage/fuzz 再測定と混同しない。 |

### Reproduction

同じ入力を native と emulator で実行する。以下の assembly を target 一時領域で ELF 化した（レビューは application source を変更していない）。GS を使うため、native libc の FS/TLS へ依存しない。

```asm
.data
.balign 8
cell: .quad 41
.text
.global _start
_start:
    mov $158, %eax
    mov $0x1001, %edi
    lea cell(%rip), %rsi
    syscall
    lock incq %gs:0
    mov $1, %eax
    mov $1, %edi
    lea cell(%rip), %rsi
    mov $8, %edx
    syscall
    mov $60, %eax
    xor %edi, %edi
    syscall
```

### Summary

GS 原子アクセスの具体的な native 差があるため NOT-READY。取得 receipt、全 static forms の分類、native-before-implementation の記録、差分・内部・並列・fuzz の根拠と限界は区別されている。local cargo-deny 未実行は既存の明示 GAP として Build/Test・CI で確認する事項であり、今回の Critical 指摘とは別である。
