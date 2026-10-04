# U2：整数命令の非機能要件

## Sources

ドキュメント根拠：要件書 `inception/requirements-analysis/requirements.md` NFR1〜NFR9、C1・C3・C4・C5 の `inception/contract-design/contract-summary.md`、U2 の `functional-design/functional-spec.md` と `rules.md`、確認済み `nfr-requirements-questions.md` に基づく。実装の合格を示す文書ではない。以下の要件はすべて実装後の検証対象であり、現時点の動作は未検証。

## Scope and Trust Boundaries

信頼しない入力は、ゲストの命令 bytes、レジスタ、アドレス、メモリ内容とアクセス権限。Decoder → Cpu → Mmu の境界で形・幅・範囲・権限を検査する。CpuState は Kernel.Thread が所有し、Cpu はその状態と AddressSpace だけを使う。Cpu からホスト OS・ファイル・ネットワークへ直接アクセスしない。syscall の実装、Vfs の指定ディレクトリへの制限、認証サービスは U2 の変更範囲に含まれない。

製品の資源上限は追加しない（NFR5）。テストの命令予算・メモリ量・時間切れは検証器の制御であり、ゲストへの新しい制限ではない。

## Threat Considerations

| 入力・境界 | 分類 | 影響 | 対応する要件 |
|---|---|---|---|
| 細工した命令、幅、算術、アドレスでホストの panic や範囲外アクセスを誘発 | Tampering / Elevation of Privilege | 高 | NFR2.1、NFR2.2、NFR3.1 |
| 読取不能なメモリや権限変更をまたいで値を取得する | Information Disclosure | 高 | NFR4.1、NFR2.1 |
| 競合更新で旧値を複数に配り、通常アクセスに途中の値を公開する | Tampering | 高 | NFR1.3、NFR7.1 |
| 長い反復、ゲストループ、大量の資源要求 | Denial of Service | 高 | NFR5.1、NFR7.1。製品の上限がないため使い切りの危険は残る |
| 比較器が未定義 flags を過剰に除外、または失敗入力を失う | Integrity / Repudiation | 中 | NFR1.1、NFR7.2 |

認証主体やネットワーク API を U2 は追加しないため Spoofing 用の認証方式は選定しない。ゲストデータに秘密が含まれ得るので、診断データはケースが指定する最小範囲を扱い、製品が任意のゲストメモリを自動で外部送信しない。ホストファイルの外側を読めないことは Vfs の担当であり、U2 のテスト結果から全体の隔離を主張しない。

## Detailed Requirements

| ID | 要求・合格条件 | 検証方法 |
|---|---|---|
| NFR1.1 | 対象となる各命令形式を native x86-64 Linux と比較し、レジスタ・定義済み flags・メモリの不一致 0 件。保持 flags は入力値も検査。未定義の除外は形式・幅・入力条件ごとの表を持つ | ケース ID、入力 bytes、raw 出力、比較マスク、差分を保存。期待結果は実行ごとに作る |
| NFR1.2 | 未対応・不正は SIGILL、メモリ違反は SIGSEGV、除算例外は SIGFPE。faulting RIP と未完了更新を確かめる。REPE/REPNE CMPS/SCAS は開始時 flags 復元、完了 count/index 保持に一致する | native の signal context と Cpu 停止状態を比較。成功反復後 fault と BudgetStop 後同じ fault のケースを含める |
| NFR1.3 | lock・メモリ xchg・cmpxchg 系の更新が不可分。通常 read/write/fetch と map/protect/unmap にも共通同期が効く。比較交換の不成功でも必要な書込権限を検査する | 同じ AddressSpace を共有するホスト競合テストで合計値・成功回数・旧値一意性・途中値非公開・ページ跨ぎ・権限違反時の部分更新なしを検査。ゲスト clone/futex の統合は U5 |
| NFR2.1 | bytes の長さ、幅、整数計算、アドレス変換、ページ境界、権限を検査し、ゲストの不正入力で明示的 panic や未定義動作を起こさない。違反は設計済みのゲスト fault、検証器の失敗、または内部エラーとして区別する | 不正 prefix、短い fetch、境界アドレス、ゼロ除算・商の overflow、読取専用 cmpxchg、反復の途中 fault の回帰テスト |
| NFR2.2 | cargo-fuzz に有界な Cpu 実行を追加。夜間 Linux CI で対象ごとに 10 分、panic・AddressSanitizer による異常検出 0 件を合格条件とする。発見入力を回帰ケースにする | 固定して記録したメモリ領域・権限、初期状態、有限の命令予算で fuzz。入力と seed、実行量、検出結果を残す。native 一致や全 UB 不在の証明とはしない |
| NFR3.1 | Cpu・Mmu・Decoder・Types などのコアで unsafe を禁止。Host/Jit 以外に増やさない | `#![forbid(unsafe_code)]` とビルド。新しい unsafe が必要なら U2 の計画を見直す |
| NFR3.2 | fmt 合格、clippy 警告 0。製品の unwrap・expect・panic の禁止を維持 | `cargo fmt --all -- --check`、`cargo clippy --locked --workspace --all-targets -- -D warnings`。既存の lint 設定を緩めない |
| NFR3.3 | Linux native の workspace 行カバレッジ 80% 以上。範囲内命令の差分ケース保有率と、形式・幅・prefix ごとの未検証範囲を別に報告 | cargo-llvm-cov。行の網羅と意味論の網羅を混同せず、対象命令表に出どころ・分母を記録 |
| NFR3.4 | 安全性の回帰を CI と fuzz で検出。既存の U1 テストを含め、失敗を 0 件にする | unit/differential と NFR2.2 の記録。sanitizer の検出 0 件から全入力の安全性を証明したと主張しない |
| NFR4.1 | 全メモリアクセスを Mmu に通し、guest u64 をホストのアドレスや OS 呼出しにそのまま変換しない。fetch は実行権限を検査。Cpu から Kernel/Host を呼ばない | 権限・境界テストと依存関係の確認。共有排他に参加しないアクセス経路がないことをレビュー |
| NFR5.1 | メモリ・スレッド・ファイルの製品上限を U2 で追加しない。使い切りやホスト OOM の防止は保証しない | 変更と公開設定の確認。検証器の制限を製品の資源制限と区別 |
| NFR6.1 | インタプリタの新しい速度目標を設定しない。性能測定を行う場合は実行環境・負荷・ケースを記録し、正しさの合否とは分ける。JIT の速度合否は U14 | コード生成の検証記録。無負荷で測定し、U2 の完了に JIT 成功を含めない |
| NFR7.1 | 差分・ホスト競合ケースの時間切れは 1 件 30 秒。終了しないケース、worker/barrier が停止したケースは失敗。測定の速さの合否ではない | 外側の watchdog で子プロセスを終了し回収する。worker の join だけに頼らない。timeout を PASS/SKIP にしない |
| NFR7.2 | 同じ入力で結果が揺れたらケース・入力・seed・環境・raw 観測を記録して直す。合格までの再実行で失敗を隠さない | CI の失敗記録。未定義 flags、観測器の失敗、native 非実行をそれぞれ区別 |
| NFR8.1 | 新しい製品依存は予定しない。既存の依存は crates.io のみ、許可ライセンス、RustSec 検査、Cargo.lock と --locked を維持 | cargo-deny、lockfile 差分、CI の SHA 固定。将来の追加は同じ検査を受ける |
| NFR9.1 | 手元と CI で rust-toolchain.toml の固定 nightly と同じ component を使う。U2 は pin を変更しない | rustc/cargo の版と CI 設定を検証記録に残す |

## Assumptions & Open Questions

None.

## Verification Status

文書は要件の具体化であり、実装の検証は未実施。Code Generation の計画で実際のコマンド・ケース・成果物への対応を確定し、Build and Test の記録に目標・実測・合否を残す。wasm Worker での共有状態と Safari を含む実環境は U11 の検証範囲に残る。
