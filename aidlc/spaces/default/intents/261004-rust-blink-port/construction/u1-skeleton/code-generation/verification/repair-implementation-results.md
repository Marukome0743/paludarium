# 承認済み修復 Steps 21–24 の実装結果

## 実装

- MOVQ と PUNPCKLQDQ の legacy XMM 形式を decoder/CPU に追加。MOVQ の XMM 上位64bitのゼロ化、PUNPCKLQDQ の異なる下位64bitと自己参照を差分ゲスト・内部単体テストで確認する。MMX/AVX は追加しない。
- REP 比較の fault flags は `CpuState.rep_fault_flags` による明示的モデル選択。`RepFaultFlags::RestoreInitial` を既定として従来の Intel モデルを維持し、`PreserveCompleted` で観測済み AMD モデルを扱う。production はホスト CPU を検出しない。
- native 観測ゲストが CPUID vendor を stderr に出力し、`diff_u2` fixture だけが Intel/AMD の対応するモデルを選択する。未知 vendor は明示的に失敗する。比較 mask `0xcd5`、30秒 watchdog、nightly pin、coverage 80% 下限を変更しない。
- U4/U7 の build.sh は、それぞれ5/4箇所の CRLF を LF に変更。ビルド処理の内容は変更しない。

## 実装前の native 期待結果

検証済み：`native-expectations-37672366086.log` の AMD EPYC 7763 と `native-expectations-ubuntu22-37672834343.log` で、MOVQ の上位64bitは0、異なる PUNPCKLQDQ の上位64bitは source の下位64bit、自己参照は両半分に元の下位64bit。`native-red-bookworm-37672366086.log` で現実装の `insn_sse` が InvalidOpcode として失敗した後に実装した。

検証済み：AMD の REP 初回 fault は flags `8d5`、部分実行後/budget 後の CMPS は `44`、SCAS は `0`。`native-final-bookworm-d32185db.log` の GenuineIntel Xeon Platinum 8573C は CMPS/SCAS の部分実行後/budget 後でも `8d5` であり、一律 AMD モデルでは4件が失敗した。両 native 観測を得てから明示的モデルに修復した。

ドキュメント根拠：[Intel SDM Volume 2](https://cdrdv2-public.intel.com/789581/325383-sdm-vol-2abcd.pdf) の REP の説明は fault 時の初期 EFLAGS 復元を要求する。AMD の保持動作は実機観測による根拠であり、Intel 文書を AMD の仕様として引用しない。AMD 著作の Volume 3 rev3.36 §1.2.6 は repeat prefixes を説明しているが、Intel と同じ rollback をそこで要求していない（[AMD 著作のPDFミラー](https://www.scs.stanford.edu/~zyedidia/docs/x86/amd-manual-v3.pdf)）。公式 rev3.37 portal/API は404で取得できず、最新版の同箇所は未検証。

## 手元 Docker VMM の結果

すべて `bash scripts/linux-dev.sh <command>` から直列実行。手元の「native」側は QEMU を介しており、実機の期待結果とは呼ばない。

| コマンド | 結果と証拠 |
| --- | --- |
| `cargo test --locked -p paludarium-harness --test diff_u1 insn_sse -- --exact --nocapture`（実装前） | 0 pass / 1 fail、MOVQ InvalidOpcode。`docker-vmm-sse-red.log` |
| `cargo test --locked -p paludarium-harness --test diff_u1`（SSE実装後） | 16 pass。`docker-vmm-sse-green.log` |
| `cargo test --locked -p paludarium-decoder -p paludarium-cpu --lib` | decoder18 / CPU39 pass。`docker-vmm-repair-unit.log`（その時点では単一 AMD モデル） |
| `cargo test --locked -p paludarium-cpu --lib`（明示的両モデル） | CPU39 pass。両モデルの開始時/17回後/4096回後と fetch fault を確認。`docker-vmm-dual-rep-unit.log` |
| `cargo test --locked -p paludarium-harness --test diff_u2 fault -- --nocapture --test-threads=1`（明示的両モデル） | parent9 pass / 1 fail。REP6件は全通過、QEMU vendor は AuthenticAMD。失敗は既知 ENTER allocation のみ。`docker-vmm-dual-rep-diff.log` |
| `cargo test --locked -p paludarium-harness --test diff_u4 -- --test-threads=1` | 32 pass / 12 fail。全 guest 生成後、QEMU の trapno=-1、signal stderr、brk、fault error 値等で差分失敗。`docker-vmm-repair-u4.log` |
| `cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1` | 59 pass / 4 fail。host/plain の open_errors と huge_invalid_buffer の errno/0 不一致。`docker-vmm-repair-u7.log` |
| `cargo test --locked -p paludarium-harness --lib coverage::tests -- --nocapture` | 2 pass、命令 census 68/68。`docker-vmm-repair-census.log` |
| `cargo fmt --all --check`（明示的両モデル） | exit0。`docker-vmm-dual-rep-fmtcheck.log` |
| `cargo clippy --locked -p paludarium-cpu -p paludarium-decoder -p paludarium-harness --all-targets -- -D warnings`（明示的両モデル） | exit0。`docker-vmm-dual-rep-clippy.log` |

検証済み：`bash -n tests/guests/u4/build.sh` と `bash -n tests/guests/u7/build.sh` は exit0。構文検査だけを guest 生成成功の根拠にはしない。

ENTER allocation の手元差は、QEMU が ENTER で停止せず後続の `_exit` call で fault するため rip_delta=-61。以前の実機 Intel/AMD は ENTER 自体の rip_delta=0 で一致する。Docker の未通過項目を pass に読み替えたり、実機 CI の基準を緩めたりしない。

## 最終 native gate

明示的両モデルの最終 native run `37674781864`、全体 CI `37674781868` は root が回収する。実装担当のこの報告時点では、その最新 gate 結果は未検証。macOS/Windows の Host U7 に見つかった別件は root が追加計画を扱い、この承認済み範囲では Host を変更していない。
