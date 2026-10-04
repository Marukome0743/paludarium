# U2：使用する道具と選定方針

## Sources

ドキュメント根拠：確認済み `nfr-requirements-questions.md`、要件書 NFR3・NFR8・NFR9、契約 C1・C3・C4・C5、U2 機能設計と workspace の `Cargo.toml`・`rust-toolchain.toml`。既存選定を引き継ぎ、U2 のための新しい製品依存を予定しない。実装動作は未検証。

## Decisions

| 対象 | 選定 | 理由・責任 |
|---|---|---|
| 言語とツールチェーン | 既存の Rust workspace、固定 nightly | NFR9.1。pin を変えず手元と CI を合わせる |
| 命令デコード | 既存の paludarium-decoder の包みを拡張 | 外部 crate の型を Cpu と Jit の契約に漏らさず、形式・prefix・幅・暗黙 operands を渡す。必要な意味論は Cpu で実装 |
| 整数意味論 | paludarium-cpu、共通停止理由は paludarium-types | Kernel を呼ばず ExitReason を返す。ArithmeticFault の追加は Runtime/Kernel 等の全利用側を同じ変更で更新 |
| 原子的メモリ更新 | paludarium-mmu の共通同期 | 通常アクセスと mapping 操作も参加する。初期実装は AddressSpace 単位の直列化を許す。Cpu が任意の callback を排他中に実行しない |
| 反復の再開 | CpuState の repeatContinuation | 命令開始時 flags を内部 BudgetStop からの再開をまたいで保持。Kernel.Thread の所有モデルを維持 |
| 正しさの観測 | 既存 Harness、native x86-64 Linux の子プロセス | 毎回の native 期待値。signal context から fault 時の RIP/count/index/flags を取得。観測器の失敗をゲストの停止と混ぜない |
| 並行検証 | Rust のホストスレッド、ケースごとの外側 watchdog | 同じ AddressSpace の競合を 30 秒で検査。ゲスト clone/futex は U5、wasm Worker は U11 |
| ファジング | 既定の cargo-fuzz/libFuzzer、Linux、AddressSanitizer | 有界な命令実行を追加し夜間各対象 10 分。比較器や無制限のゲスト実行を fuzz 入力から起動しない |
| 品質・供給網 | 既存 cargo test、rustfmt、clippy、cargo-llvm-cov、cargo-deny | NFR3・NFR8 を維持し、Linux 行カバレッジ下限 80%。crate 取得元と lockfile を変更しない |
| ホスト接続・公開 API | 既存 Runtime/Kernel/Host の契約 | Cpu に直接の OS 接続を追加しない。内部契約の追加は全利用側を同じ変更で合わせる |

## Tradeoffs

AddressSpace 単位の同期は細粒度の更新より直列化が増えるが、通常アクセス・ページ跨ぎ・mapping と原子操作を一つの契約で守れる。NFR6 に従い U2 では速度の新しい閾値を追加しない。最適化するときも、同じ差分・並行テストを維持する。

夜間の fuzz は不正入力による異常の検出用であり、命令意味論の合格は native 差分テストで判断する。sanitizer の検出が 0 件でも、全入力の UB 不在を証明したことにはならない。

## Assumptions & Open Questions

None.

## Deferred Integration

ゲスト clone/futex の統合は U5、wasm shared heap と Worker での実際の同期は U11、SSE は U3、JIT は U14。probe/aube の命令一覧の出どころと取得手順は U2 のコード生成計画で確定する。未取得の一覧から全命令対応を主張しない。
