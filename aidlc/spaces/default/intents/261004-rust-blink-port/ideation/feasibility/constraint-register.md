# 制約の一覧：Rust 版 blink（paludarium）

上流の成果物：`aidlc/spaces/default/intents/261004-rust-blink-port/ideation/intent-capture/intent-statement.md`。根拠は `feasibility-questions.md` の回答（Q1〜Q9）です。

## 技術的な制約

| ID | 制約 | 種類 | 根拠 |
|----|------|------|------|
| C-T1 | エミュレータは Rust で実装する | 必須 | 意図書（Problem Statement） |
| C-T2 | 既存の実装は採用しない。デコーダを含め、外部の部品を使わずにすべて自作する | 必須 | Q1、Q9、Q2 |
| C-T3 | 他のプロジェクト（blink、nixvm など）は動作と設計を参考にするだけで、コードはコピーしない | 必須 | Q3 |
| C-T4 | ゲストは未改変の static-musl x86-64 Linux バイナリとする | 必須 | 意図書（Success Metrics。formicarium の probe と aube） |
| C-T5 | formicarium との境界は「wasm モジュール 1 つ＋起動用 JS」とする | 必須 | 意図書（Problem Statement） |
| C-T6 | wasm での動作確認用に、paludarium が起動用 JS と Node.js・ブラウザ用のテストハーネスを用意する | 必須 | Q4 |
| C-T7 | ネイティブ環境の合格条件は Linux・macOS・Windows のすべて | 必須 | Q5 |
| C-T8 | ゲストからは既定で仮想のファイルシステムだけが見える。ホストのファイルシステムをそのまま見せる方式は、選んだときだけ有効にする | 必須 | Q6 |
| C-T9 | JIT はまず wasm 向けに作る。効果は Node.js の Worker で、JIT ありとなしを比べて測る | 必須 | 意図書（Q9・Q10）、Q7 |
| C-T10 | wasm32 のメモリ上限（4GB）があるため、ゲストのアドレス空間はソフトウェア MMU で扱う | 技術的な前提 | 背景資料 cheerpx-oss.md [doc] |
| C-T11 | ブラウザでのスレッドには SharedArrayBuffer が要るので、ページは COOP/COEP 付きにする | 技術的な前提 | 背景資料 cheerpx-oss.md [doc] |

## 組織上の制約

| ID | 制約 | 根拠 |
|----|------|------|
| C-O1 | 開発は一人で行う。範囲と優先順位はすべて利用者が決める | 意図書（関係者マップ） |
| C-O2 | 期限はない。formicarium の PoC（既存の blink を使う）と並行して進める | 意図書（Initiative Trigger） |
| C-O3 | ブラウザ側（Worker・ページ・ファイルシステム）の本番実装と、formicarium への組み込みは範囲外で、formicarium が担う | 意図書（Initial Scope Signal）、Q4 |

## 規制・ライセンス上の制約

| ID | 制約 | 根拠 |
|----|------|------|
| C-R1 | paludarium は Apache-2.0 で公開する | README.md |
| C-R2 | Blink ベースの webix・portabox 系列は、参照も依存も禁止する（履歴にマルウェアがあった） | 背景資料 cheerpx-oss.md [doc] |
| C-R3 | 個人情報や業界規制の対象データは扱わない | [estimate] |

## 環境上の制約

| ID | 制約 | 根拠 |
|----|------|------|
| C-E1 | 開発と CI は GitHub を使う。必要ならクラウドの実行環境も使ってよい | Q8 |

## Assumptions & Open Questions

- [assumption] C-T2 の「外部の部品」には、ビルドやテストの道具（Rust のツールチェーン、wasm 用のツール、テスト用の補助）を含めない。要件分析で確かめる。
