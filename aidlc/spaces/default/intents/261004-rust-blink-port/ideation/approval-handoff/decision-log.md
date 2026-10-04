# 決定の記録：Ideation（2026-10-04）

上流の成果物は `ideation/` 以下の各工程の質問ファイルと成果物です。ここでは、Ideation で決まったことを工程の順に並べます。

| # | 工程 | 決定 | 根拠 |
|---|------|------|------|
| D1 | 計画づくり | カスタムの計画 `rust-blink-port`（18 工程）で進める。Guard Policy は relaxed | 計画の承認 |
| D2 | 意図の整理 | 背景資料 cheerpx-oss.md を formicarium から paludarium の knowledge に写して使う | intent-capture の資料の質問 |
| D3 | 意図の整理 | 作り直す一番の理由は、安全性と保守性を上げること | intent-capture Q1 |
| D4 | 意図の整理 | 利用者は formicarium、vivarium、一般の OSS 利用者、ネイティブ環境で使う人 | intent-capture Q2 |
| D5 | 意図の整理 | 成功条件：probe がネイティブ・Node.js の Worker・ブラウザで全項目通る | intent-capture Q3 |
| D6 | 意図の整理 | 「blink と同等」は必要な範囲から広げる。blink に欠けている eventfd・FUTEX_WAIT_BITSET・ホストに頼らない epoll も作る | intent-capture Q4 |
| D7 | 意図の整理 | 期限なし。formicarium の PoC と並行 | intent-capture Q5 |
| D8 | 意図の整理 | 決定者はあなた一人。共有は AI-DLC の記録と承認ゲート | intent-capture Q6、Q7 |
| D9 | 意図の整理 | JIT を範囲に含める。まず wasm 向け。成功条件は、probe が通ったまま JIT なしより速いこと | intent-capture Q8〜Q10 |
| D10 | 実現性 | 既存実装は採用せず、デコーダも含めてすべて自作する | feasibility Q1、Q2、Q9 |
| D11 | 実現性 | 他のプロジェクトのコードはコピーせず、動作と設計を参考にするだけ | feasibility Q3 |
| D12 | 実現性 | 起動用 JS と Node.js・ブラウザ用のテストハーネスは paludarium が用意する | feasibility Q4 |
| D13 | 実現性 | ネイティブの合格条件は Linux・macOS・Windows のすべて | feasibility Q5 |
| D14 | 実現性 | ゲストの隔離は、仮想ファイルシステムが既定。ホストを見せる方式も選べる | feasibility Q6 |
| D15 | 実現性 | JIT の速さは Node.js の Worker で比べる | feasibility Q7 |
| D16 | 実現性 | 開発と CI は GitHub。必要ならクラウドも使ってよい | feasibility Q8 |
| D17 | 範囲 | 段階 1〜5 を番号の順に進める | scope-definition Q1 |
| D18 | 範囲 | 最初の区切りは、ネイティブの Linux で hello world が動くこと | scope-definition Q2 |
| D19 | 範囲 | aube も Must。3 つのネイティブ OS と wasm（3 種類のブラウザ）で動くことを成功条件に加える | scope-definition Q3、Q4 |
| D20 | 範囲 | 32-bit x86 と AVX・AVX-512 は範囲外 | scope-definition Q5 |
| D21 | 範囲 | 成功条件を満たしたら crates.io と npm に公開する | scope-definition Q6 |
| D22 | 着手の承認 | R2 は、段階 1 の設計の時点で wasm のスレッドを小さく確かめる | approval-handoff Q1 |
| D23 | 着手の承認 | Go。要件と設計に進む | approval-handoff Q2 |

## 途中で変わった決定

- D9：計画づくり（D1）の時点では、JIT は範囲外でした。intent-capture Q8 で範囲に入りました。
- D10：feasibility Q2 で、いったん「iced-x86 を使う」と答えました。Q9 で「デコーダも自作する」に変わりました。

## Assumptions & Open Questions

None.
