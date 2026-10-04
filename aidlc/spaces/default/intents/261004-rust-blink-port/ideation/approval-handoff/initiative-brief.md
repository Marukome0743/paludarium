# 取り組みの概要：Rust 版 blink（paludarium）

上流の成果物（`ideation/` 以下）：
- `intent-capture/intent-statement.md`
- `intent-capture/stakeholder-map.md`
- `feasibility/feasibility-assessment.md`
- `feasibility/constraint-register.md`
- `scope-definition/scope-document.md`
- `scope-definition/intent-backlog.md`

## 意図と解くべき問題

- **何を作るか**：jart/blink と同等の x86-64 ユーザーモード Linux エミュレータを、Rust で作ります。理由は、安全性と保守性を上げるためです（意図書）。
- **使い道**：将来、formicarium のエミュレータコア（wasm モジュール 1 つ＋起動用 JS）を置き換えます。vivarium での CLI のバグ再現と、一般の OSS 利用にも使います（意図書、関係者マップ）。

## 市場での裏付け

- 市場調査の工程は、このワークフローでは飛ばしました。
- 代わりに、実現性の検討で既存の Rust 実装を調べました。丸ごと採用できるものはありませんでした（実現性の評価）。

## 実現性とリスクの要点

- **実現性**：実現は可能です。一人で進めるには規模の大きい長期の取り組みで、目安は合計 10〜21 か月です（判断による見積もり。実現性の評価）。
- **作り方**：デコーダを含めてすべて自作します。他のプロジェクトは動作と設計を参考にするだけです（制約 C-T2、C-T3）。
- **重いリスク**：

| ID | リスク | 対策 |
|----|--------|------|
| R1 | 命令の意味論の誤り | 最初からネイティブとの差分テストを作る |
| R2 | wasm のマルチスレッドが作れない | 段階 1 の設計の時点で wasm のスレッドを小さく確かめる（approval-handoff Q1） |
| R4 | 範囲が広く長期化して止まる | 段階ごとに動くものを出す |

## 範囲の境界

- **含むもの**：
  - デコーダ、命令の実行（SSE 系まで）、ソフトウェア MMU、static-musl の ELF の読み込み
  - probe と aube に必要な syscall、スレッド、仮想ファイルシステム
  - ホスト：Linux・macOS・Windows・wasm（Node.js の Worker と Chromium 系・Firefox・Safari）
  - 起動用 JS とテストハーネス、wasm 向け JIT の最小版、CI、パッケージ公開
- **含めないもの**：
  - 32-bit x86、AVX・AVX-512
  - ブラウザ側の本番実装と formicarium への組み込み
  - ネイティブ向け JIT（後で考える）
- **進め方**：段階 1〜5 を番号の順に進めます。最初の区切りは、ネイティブの Linux で hello world が動くことです。

## 画面の試作

画面がないので、試作の工程は飛ばしました。

## 体制

- 開発者はあなた一人で、範囲と優先順位もあなたが決めます（関係者マップ）。
- 期限はなく、formicarium の PoC と並行して進めます（意図書）。

## 進めるかどうかの判断

**Go**。今の範囲のまま、要件と設計（Inception）に進みます（approval-handoff Q2）。

## Assumptions & Open Questions

- [assumption] aube は static-musl の x86-64 向けにビルドできる（範囲の文書）。
- [assumption] Safari は、Worker と SharedArrayBuffer を使ったマルチスレッドに十分対応している（範囲の文書）。
- [assumption] 「外部の部品を使わない」には、ビルドやテストの道具を含めない（RAID ログ A1）。
