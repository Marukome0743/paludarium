# セキュリティ要件（u1-skeleton）

上流の成果物：
- `construction/u1-skeleton/functional-design/functional-spec.md`
- `construction/u1-skeleton/functional-design/rules.md`
- `inception/requirements-analysis/requirements.md`（NFR1〜NFR9）
- `inception/contract-design/contract-summary.md`

根拠は `nfr-requirements-questions.md`（Q1〜Q4）、`aidlc/spaces/default/memory/project.md` の Mandated・Forbidden、`team.md` の Testing Posture・Code Style・Deployment です。

u1-skeleton は library 種類なので、性能・拡張性・信頼性・観測の要件書は作りません。U1 に関わるそれらの要件（NFR1・NFR6・NFR7 など）も、ここにまとめます。

## 信頼の境界

| 境界 | 外側（信頼しない） | 内側 | U1 での入口 |
|------|--------------------|------|-------------|
| B1 ゲストとエミュレータ | ゲストのプログラム（ELF の中身、命令のバイト列、メモリの値、syscall の引数） | Loader・Decoder・Cpu・Mmu・Kernel | ELF の読み込み、命令の実行、syscall |
| B2 エミュレータとホスト | — | Host の trait の実装 | 標準入出力、乱数（AT_RANDOM） |
| B3 コマンドの利用者 | コマンドの引数と指定されたファイル | Cli | `paludarium [options] <program> [args...]` |
| B4 供給網 | 外部の crate、GitHub Actions の action | ワークスペース | 依存の追加、CI |

## 脅威（STRIDE）と対策

| 脅威 | 種類 | 起こりやすさ | 影響 | 対策（要件 ID） |
|------|------|--------------|------|------------------|
| 細工した ELF でエミュレータを壊す（範囲外の読み書き、panic） | Tampering・DoS | 高 | 高 | NFR2.1、NFR2.2、NFR2.3 |
| 細工した命令のバイト列でデコーダを壊す | Tampering・DoS | 高 | 高 | NFR2.1、NFR2.2 |
| ゲストの syscall をホストに素通しさせ、ホストを操作する | Elevation of Privilege | 中 | 高 | NFR4.1 |
| ゲストのアドレスでホストのメモリを読み書きする | Information Disclosure・EoP | 中 | 高 | NFR4.4、NFR3.1 |
| ゲストからホストのファイルやネットワークに触れる | Information Disclosure | 中 | 高 | NFR4.2、NFR4.3 |
| 悪意のある依存や、書き換えられた action が混ざる | Tampering | 低 | 高 | NFR8.1、NFR8.2、NFR8.3 |
| エラーの表示でホストの内部の情報を出しすぎる | Information Disclosure | 低 | 低 | NFR2.4 |

否認（Repudiation）と、なりすまし（Spoofing）に当たる要素は、U1 にはありません。U1 は利用者の認証も、外部との通信も持たないためです。

## 要件

### NFR1 正しさ

| ID | 要件 | 合否 |
|----|------|------|
| NFR1.1 | C と Rust の static-musl の hello world を、CI の x86-64 Linux で直接動かした結果とエミュレータの結果で比べ、標準出力・標準エラー・終了状態がバイト単位で一致する | CI の差分テストが通る |
| NFR1.2 | U1 で実装した命令ごとに、命令単位の差分テスト（レジスタ・フラグ・メモリ）を持つ。未定義のフラグは比べず、その一覧を表で持つ | 命令の一覧のすべてに差分テストがある |

### NFR2 堅さ

| ID | 要件 | 合否 |
|----|------|------|
| NFR2.1 | どんな ELF・命令のバイト列・syscall の引数でも、エミュレータは panic せず、未定義動作にもならない。失敗はゲストへのシグナル、-errno、エミュレータのエラー（終了コード 70）のどれかになる | NFR2.2 のファジングと単体テストで確かめる |
| NFR2.2 | cargo-fuzz の対象を、デコーダの包みと ELF の読み込みの 2 つ用意する。夜間の CI で対象ごとに 10 分ずつ回し、panic・未定義動作の検出（AddressSanitizer）が 0 件なら合格。見つかった入力は回帰テストに加える（Q2） | 夜間の CI の結果 |
| NFR2.3 | 製品のコード（テスト以外）では `unwrap`・`expect`・`panic` を clippy で禁止する | clippy が通る |
| NFR2.4 | エミュレータのエラーの表示は、種類・命令のアドレス・バイト列・syscall の番号に限る。ホストのパスや環境変数は出さない | エラーの表示の単体テスト |

### NFR3 安全性と保守性の指標

| ID | 要件 | 合否 |
|----|------|------|
| NFR3.1 | `unsafe` は Host のクレートだけで許す。ほかのクレートには `#![forbid(unsafe_code)]` を付ける。`unsafe` には `// SAFETY:` の理由を書く（`clippy::undocumented_unsafe_blocks` と `unsafe_op_in_unsafe_fn` を deny） | ビルドと clippy が通る |
| NFR3.2 | clippy の警告をゼロにする（`-D warnings`） | CI の lint が通る |
| NFR3.3 | 行カバレッジを U1 から 80% 以上にする。Linux のネイティブで cargo-llvm-cov で測り、下回れば CI を落とす（Q4） | CI のカバレッジの検査が通る |

### NFR4 隔離

| ID | 要件 | 合否 |
|----|------|------|
| NFR4.1 | ゲストの syscall を番号のままホストに渡さない。表にない番号には -ENOSYS を返す | 未実装の番号を呼ぶテストで -ENOSYS |
| NFR4.2 | U1 では、ゲストが見るのは仮想ファイルシステムだけ。`--mount` は受け付けず、引数の誤りとして終了コード 2 で終わる | `--mount` を渡すテスト |
| NFR4.3 | U1 ではネットワークの syscall（socket など）を実装しないので、-ENOSYS になる | socket を呼ぶテストで -ENOSYS |
| NFR4.4 | ゲストのアドレスはホストのアドレスと型で分け、Mmu を通してしか読み書きしない。範囲外はゲストへのフォールトになる | Mmu の単体テストとファジング |

### NFR5 資源

| ID | 要件 | 合否 |
|----|------|------|
| NFR5.1 | 資源の上限は設けない（要件書の NFR5）。U1 ではプロセスもスレッドも 1 つなので、上限がなくても使い切りの経路は brk・mmap に限られる | 該当なし（記録だけ） |

### NFR6 速さ

| ID | 要件 | 合否 |
|----|------|------|
| NFR6.1 | 目標は置かない。CI で hello world の実行時間を記録する | CI の記録がある |

### NFR7 安定

| ID | 要件 | 合否 |
|----|------|------|
| NFR7.1 | 差分テストには、1 件あたり 30 秒の時間切れの上限を付ける。同じ入力で結果が揺れたら、記録して直す | CI の設定 |

### NFR8 供給網

| ID | 要件 | 合否 |
|----|------|------|
| NFR8.1 | cargo-deny を PR の CI で回す。ライセンスは Apache-2.0 と両立するもの（MIT・Apache-2.0・BSD・ISC・0BSD・Unicode など）だけを許し、取得元は crates.io だけ、既知の脆弱性（RustSec）があれば失敗させる（Q3） | CI の依存の検査が通る |
| NFR8.2 | GitHub Actions の action はコミットの SHA で固定する。ワークフローの既定の権限は読み取りだけにする | CI の定義の確認 |
| NFR8.3 | `Cargo.lock` をコミットし、CI では `--locked` を付ける | CI の設定 |
| NFR8.4 | Blink ベースの webix・portabox の系列と `lanmower/blink` は、依存にも参照にも使わない。cargo-deny の禁止の一覧に入れる | cargo-deny の設定 |

### NFR9 ツールチェーン

| ID | 要件 | 合否 |
|----|------|------|
| NFR9.1 | nightly の Rust を `rust-toolchain.toml` で日付まで固定し、CI と手元で同じものを使う | `rust-toolchain.toml` がある |

## Assumptions & Open Questions

None.
