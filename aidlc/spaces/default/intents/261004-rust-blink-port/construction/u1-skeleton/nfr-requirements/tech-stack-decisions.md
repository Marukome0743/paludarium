# 技術選定（u1-skeleton）

上流の成果物：
- `construction/u1-skeleton/functional-design/functional-spec.md`
- `inception/contract-design/contract-summary.md`
- `inception/practices-discovery/team-practices.md`

根拠は `nfr-requirements-questions.md`（Q1〜Q4）と `team.md` の Way of Working・Testing Posture・Code Style・Deployment です。外部のものを使うときの方針（ライセンスに問題がないこと、不具合があればその部分を自作すること）は `project.md` の Mandated に従います。

## 言語とツールチェーン

| 対象 | 選定 | 理由 |
|------|------|------|
| 言語 | Rust | 制約 C-T1 |
| ツールチェーン | nightly を `rust-toolchain.toml` で日付まで固定する。コンポーネントは rustfmt・clippy・llvm-tools、ターゲットは x86_64-unknown-linux-musl と wasm32-unknown-unknown | team.md の Code Style（Q10）。wasm のスレッドと cargo-fuzz に nightly が要る |
| ビルド | Cargo のワークスペース | Units Generation の Q3 |

## ワークスペースのクレート（U1 で作るもの）

| クレート | 部品 | U1 での中身 |
|----------|------|-------------|
| `paludarium-types` | 共通の型（C1） | GuestAddr、Errno、ExitReason、ExitStatus、Error |
| `paludarium-decoder` | Decoder（C3） | 既存のデコーダの crate の包み |
| `paludarium-mmu` | Mmu（C4） | 4 KiB ページの 2 段のページテーブル |
| `paludarium-cpu` | Cpu（C5） | hello world に要る命令（BR4.4） |
| `paludarium-loader` | Loader（C7） | ELF の読み込みと最初のスタック |
| `paludarium-vfs` | Vfs（C6） | ELF を置くだけの最小限 |
| `paludarium-kernel` | Kernel（C8） | U1 の syscall（BR3.3） |
| `paludarium-host` | Host（C2） | ネイティブの Linux 用の実装。`unsafe` を許す唯一のクレート |
| `paludarium-jit` | Jit の口（C9） | 何もしない実装 |
| `paludarium-runtime` | Runtime | Session と実行ループ |
| `paludarium` | まとめ役と Cli（C10・C11） | 公開 API の再公開とコマンド |
| `paludarium-harness` | Harness（公開しない） | 差分テストとファジングの入口 |

## 外部の crate と道具

| 対象 | 選定 | ライセンス | 理由 |
|------|------|------------|------|
| 命令デコーダ | iced-x86 と yaxpeax-x86 を U1 で両方試す。hello world の命令がデコードでき、wasm32 でビルドできる方を選び、結果を記録する（Q1） | MIT・0BSD | team.md の Way of Working（Q14） |
| カバレッジ | cargo-llvm-cov | MIT・Apache-2.0 | 行カバレッジ 80% を U1 から強制（Q4） |
| 依存の検査 | cargo-deny | MIT・Apache-2.0 | ライセンス・取得元・脆弱性・禁止の一覧（Q3） |
| ファジング | cargo-fuzz（libFuzzer） | MIT・Apache-2.0 | 夜間に対象ごとに 10 分（Q2） |
| C のゲストのビルド | musl の gcc（CI の Linux で musl-tools を使う） | MIT（musl） | 最小の hello world（functional-design Q1） |
| Rust のゲストのビルド | x86_64-unknown-linux-musl ターゲット | — | Rust の hello world（functional-design Q1） |

## CI

| 対象 | 選定 |
|------|------|
| 実行環境 | GitHub Actions（ubuntu・macos・windows のランナー）。必要ならクラウドの実行環境も使ってよい（Ideation の決定 D16） |
| PR ごと | 3 つの OS でビルドと単体テスト、`cargo fmt --check`、clippy（`-D warnings`）、cargo-deny、x86-64 Linux での差分テスト、カバレッジ 80% の検査 |
| 夜間 | cargo-fuzz（対象ごとに 10 分）、wasm のスレッドの確認 |
| action | コミットの SHA で固定し、既定の権限は読み取りだけ |

## wasm のスレッドの確認（U1 の中の確認）

| 対象 | 選定 | 理由 |
|------|------|------|
| ビルド | wasm32-unknown-unknown に、スレッドに要る機能（atomics・bulk-memory など）を付けて、nightly でビルドする。必要な設定を記録する | functional-spec の W6 |
| Node.js | 現行の LTS 版 | Worker と SharedArrayBuffer |
| Chromium 系・Firefox | ブラウザの自動操作の道具で開く（候補：Playwright） | functional-design Q3 |
| Safari | macOS のランナーで本物の Safari を、Safari の WebDriver（safaridriver）で開く | team.md の Testing Posture（本物の Safari） |
| 配信 | COOP/COEP の見出しを付けて配る小さな配信の仕組み（Node.js のスクリプト） | SharedArrayBuffer に要る |

## Assumptions & Open Questions

None.
