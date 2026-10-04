# RAID ログ：Rust 版 blink（paludarium）

上流の成果物：`aidlc/spaces/default/intents/261004-rust-blink-port/ideation/intent-capture/intent-statement.md`。根拠は `feasibility-questions.md` の回答（Q1〜Q9）と `feasibility-assessment.md` です。

評価は 高・中・低 の 3 段階です。いずれも判断による評価です [estimate]。

## Risks（リスク）

| ID | リスク | 起こりやすさ | 影響 | 対策 |
|----|--------|--------------|------|------|
| R1 | 命令の意味論（特にフラグと SSE）の誤りが、気づかれずに残る | 高 | 高 | ネイティブの x86-64 Linux で同じゲストを動かして結果を比べる差分テストを、最初から作る |
| R2 | wasm 上のマルチスレッド（Worker、SharedArrayBuffer、Atomics）が、Rust の wasm スレッド対応の制約で思うように作れない | 中 | 高 | 設計の前に小さな試作で確かめる。結果を設計に反映する |
| R3 | Windows ホストで Linux の syscall（flock、シンボリックリンク、socketpair、futex 相当）の対応付けが難しく、合格条件を満たすのに時間がかかる | 高 | 中 | ホスト OS ごとの差を 1 か所に閉じ込める設計にする。Windows は段階を分けて後に回す |
| R4 | 範囲が大きく（デコーダ自作、3 つの OS、JIT）、一人の開発では長期化して止まる | 高 | 高 | scope-definition と delivery-planning で段階に区切り、段階ごとに動くものを出す |
| R5 | wasm でのソフトウェア MMU が遅く、JIT がないと実用にならない | 中 | 中 | 意図書どおり JIT を範囲に含める。早い段階から Node.js の Worker で速さを測る |
| R6 | 信頼できないゲストのバイナリが、ホストのファイルや資源に触れる | 中 | 高 | 既定は仮想ファイルシステムにする（Q6）。ホストのファイルを見せる方式は、選んだときだけ有効にする |
| R7 | 参考にした blink などのコードを、意図せず写してしまう | 低 | 中 | 参考にするのは動作と設計だけにする（Q3）。コードを読んだ範囲を記録する |

## Assumptions（前提）

| ID | 前提 | 確かめる時期 |
|----|------|--------------|
| A1 | [assumption] 「外部の部品を使わない」には、ビルドやテストの道具を含めない | 要件分析 |
| A2 | [assumption] Rust で wasm のマルチスレッドを作る方法が実用になる | 設計の前の試作 |
| A3 | [assumption] GitHub Actions の Linux・macOS・Windows の実行環境で、ネイティブの合格条件を CI で確かめられる | CI の設計 |
| A4 | [assumption] 規模の見積もり（合計 10〜21 か月）は、段階 1 の実績で見直す | 段階 1 の完了時 |

## Issues（課題）

| ID | 課題 | 状態 |
|----|------|------|
| I1 | 前の工程のレビュー指摘：wasm での成功条件とブラウザ側の範囲外の関係があいまいだった | 解決（Q4：起動用 JS とテストハーネスは paludarium が用意し、本番の組み込みは formicarium が行う） |
| I2 | 前の工程のレビュー指摘：JIT の成功条件の比べ方が決まっていなかった | 一部解決（Q7：Node.js の Worker で比べる）。何を測るか（probe の全体か、項目ごとか）は要件分析で決める |
| I3 | Q1（すべて自作）と Q2（iced-x86 を使う）が食い違っていた | 解決（Q9：デコーダも自作する） |

## Dependencies（依存）

| ID | 依存先 | 内容 |
|----|--------|------|
| D1 | formicarium | 境界（wasm モジュール 1 つ＋起動用 JS）の取り決めと、probe の内容を合わせる |
| D2 | Node.js とブラウザ（Chromium 系・Firefox・Safari） | SharedArrayBuffer、Worker、Atomics の対応状況 |
| D3 | Rust のツールチェーン | wasm ターゲットとスレッド対応 |
| D4 | GitHub（Actions） | 3 つの OS での CI。必要ならクラウドの実行環境で補う（Q8） |

## Assumptions & Open Questions

- [assumption] 上の Assumptions（A1〜A4）は、どれもまだ確かめていない。それぞれの確かめる時期に確認する。
