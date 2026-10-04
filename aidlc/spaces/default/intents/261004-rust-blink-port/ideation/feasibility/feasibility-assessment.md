# 実現性の評価：Rust 版 blink（paludarium）

上流の成果物：`aidlc/spaces/default/intents/261004-rust-blink-port/ideation/intent-capture/intent-statement.md`（以下、意図書）。根拠は `feasibility-questions.md` の回答（Q1〜Q9）、背景資料 `aidlc/spaces/default/knowledge/documents/research/cheerpx-oss.md`、2026-10-04 の既存実装調査です。

ラベルの意味：
- **[verified]**：ページやリポジトリを読んで確かめた
- **[doc]**：そのプロジェクト自身の文書による
- **[estimate]**：判断による見積もり
- **[assumption]**：まだ確かめていない前提

## 結論

- **実現は可能です。** ただし、一人で進めるには規模の大きい長期の取り組みになります。[estimate]
- 丸ごと採用できる既存の Rust 実装はありません（下の調査結果を参照）。依頼文の「使えるものがなければ自分で作る」に当てはまるので、自作に進みます。[verified]
- 利用者の判断で、外部の部品も使わず、デコーダを含めてすべて自作します。他のプロジェクトは動作と設計を参考にするだけで、コードはコピーしません。（Q1、Q9、Q2、Q3）
- 規模を広げている主な要因は 3 つです。いずれも利用者が選んだもので、意図書の範囲と合っています。
  - デコーダの自作（Q9）
  - ホスト OS 3 つ（Q5）
  - JIT（意図書 Q8）
- 一番大きな不確実性は 2 つです。後続の工程で早めに確かめる必要があります。
  - wasm 上でのマルチスレッド（Rust の wasm スレッド対応と、Worker 間の同期）
  - Windows ホストでの Linux syscall の対応付け

## 既存実装の調査結果（2026-10-04）

調べ方：Web ページと GitHub・crates.io のページを読みました。コードの clone や実行はしていません。

| 候補 | ライセンス | 内容 | 判断 |
|------|------------|------|------|
| nixvm（github.com/KarpelesLab/nixvm） | MIT | Rust 製。x86-64 インタプリタと 60 以上の syscall（futex・epoll・eventfd・AF_UNIX）を持つ。x86-64 対応は発展途上で SSE2 まで、wasm 版はシングルスレッド、syscall は 1 つのロックで直列処理。作者は一人で crate は 0.0.3 [verified] | 参考にする（コードは使わない。Q3） |
| mwemu（github.com/sha0coder/mwemu） | Apache-2.0 | Rust 製。主な対象は Windows マルウェア解析 [verified] | 参考のみ |
| ax（github.com/xarantolus/ax） | AGPL-3.0 | Rust → wasm。対応命令が少なく、libc を使う ELF は動かない [verified] | 使わない |
| rish（github.com/ZSeven-W/rish） | MIT | Rust 製。カーネルを起動する方式 [verified] | 命令の意味論の参考のみ |
| iced-x86 / yaxpeax-x86 | MIT / 0BSD | Rust 製の命令デコーダ [verified] | 使わない（Q9：デコーダも自作）。命令の網羅性を確かめる参考にはできる |
| copy/v86 | BSD-2-Clause | x86 → wasm の JIT を持つ。32-bit のみ [verified] | JIT 設計の参考 |
| unicorn（Rust バインディング） | GPL-2.0 | QEMU 由来の C が本体 [doc] | 使わない |
| webix / portabox（Blink ベース） | — | 履歴にマルウェアがあった [doc] | **使用禁止** |

- Rust への blink の移植は見つかりませんでした。[verified]
- 背景資料で調べられた範囲でも、ユーザーモードの Linux エミュレーションと x86 → wasm の JIT の両方を持つ OSS はありませんでした。[doc]

## 技術的な実現性

| 領域 | 見立て | 根拠 |
|------|--------|------|
| 命令デコーダ（自作） | 可能。x86-64 の命令の形式は公開仕様で決まっている。ただし、SSE 系まで含めると量が多い | Q9、[estimate] |
| 命令の意味論（ALU・フラグ・SSE） | 可能。正しさの確認が最大の課題。ネイティブの x86-64 Linux で同じゲストを動かして結果を比べる差分テストで確かめられる | [estimate] |
| ソフトウェア MMU | 必要。wasm32 のメモリは 4GB までなので、ゲストの 64-bit アドレス空間をそのまま置けない。blink も wasm 相当の環境ではページテーブル方式になり、約 4 倍遅いとされる | 背景資料 [doc] |
| syscall 層 | 可能。probe と aube に必要な範囲から作る。その中で eventfd2・FUTEX_WAIT_BITSET・ホストに頼らない edge-triggered epoll を作る（blink にもない） | 意図書（Q4）、背景資料 [doc] |
| ゲストのスレッド（ネイティブ） | 可能。ゲストのスレッドをホストのスレッドに割り当てる（blink と同じ） | 背景資料 [doc] |
| ゲストのスレッド（wasm） | 不確実性が高い。SharedArrayBuffer、Worker、Atomics による待ち合わせが要る。Rust の wasm スレッド対応は、ターゲットとツールチェーンの選び方に左右される | [assumption] 設計前に試作で確かめる |
| ホスト OS 3 つ | Linux は素直。macOS は futex や epoll に相当するものが違うので対応付けが要る。Windows はファイル（シンボリックリンクの権限、flock）、ソケット、待ち合わせの対応付けが最も大きい | Q5、[estimate] |
| 起動用 JS とテストハーネス | 可能。Node.js の Worker と COOP/COEP 付きのページで動かす | Q4、背景資料 [doc] |
| JIT（wasm 向け） | 可能だが大きい。背景資料の見積もりでは、命令ごとにインタプリタを呼ぶ最小の JIT で 4〜8 週、よく使う整数命令を展開するものはさらに 4〜8 か月 | 背景資料 [estimate]、意図書（Q9） |

## 規模の見積もり

[estimate] 一人で、期限なし（意図書 Q5）の前提で、控えめに見積もっています。根拠は背景資料の JIT 見積もりと、blink の機能範囲（デコーダ、ALU/SSE、MMU、178 個の syscall）です。

| 段階 | 内容 | 見積もり |
|------|------|----------|
| 1 | デコーダ、整数命令、MMU、最小の syscall。ネイティブの Linux で static-musl の hello world が動く | 2〜4 か月 |
| 2 | スレッド、futex、eventfd、epoll、ソケット、ファイル操作。ネイティブの Linux で probe が全項目通る | 3〜6 か月 |
| 3 | wasm ビルド、起動用 JS、テストハーネス。Node.js の Worker とブラウザで probe が通る | 2〜4 か月 |
| 4 | macOS・Windows ホスト | 2〜5 か月 |
| 5 | wasm 向け JIT（最小版） | 1〜2 か月以上 |

合計の目安は 10〜21 か月です。この数字は判断による見積もりで、精度は低いです。後の工程（scope-definition、delivery-planning）で、段階ごとに区切って見直します。

## 規制とコンプライアンス

- 個人情報や機密データは扱いません。業界の規制（PCI・HIPAA・SOC 2・GDPR など）の対象になる要素は見当たりません。[estimate]
- **ライセンス**
  - paludarium は Apache-2.0 です。
  - 他のプロジェクトのコードはコピーせず、動作と設計を参考にするだけです。このため、他のライセンスの義務は生じない見込みです。（Q3）[estimate]
- **安全性**
  - 信頼できないゲストのバイナリを動かす場面があります。
  - そこで、既定ではゲストに仮想のファイルシステムだけを見せます。ホストのファイルシステムをそのまま見せる方式は、選んだときだけ有効にします。（Q6）
- **供給網**
  - Blink ベースの webix・portabox 系列は使用禁止です。依存に入れないことを確かめる必要があります。[doc]
  - 外部の部品を使わない方針（Q1・Q9）は、依存に由来するリスクも減らします。

## 実行環境と費用

- 開発と CI は GitHub を使います。必要なら、クラウドの実行環境も使ってよいことになっています。（Q8）
- **3 つの OS でのテスト**
  - GitHub Actions には Linux・macOS・Windows の実行環境があります。これで足りる見込みです。[assumption] 料金と実行時間の上限は、CI の設計で確かめます。
  - ネイティブの x86-64 Linux との差分テストは、x86-64 の Linux 実行環境で行います。[estimate]
- **JIT の効果の比較**
  - Node.js の Worker で、同じ probe を JIT ありとなしで実行して比べます。（Q7）
  - 自動化しやすく、CI でも回せます。[estimate]

## Assumptions & Open Questions

- [assumption] 「外部の部品を使わない」（Q1・Q9）は、エミュレータの成果物に組み込むコードの話とする。ビルドやテストの道具（Rust のツールチェーン、wasm 用のツール、テスト用の補助）は含まない。要件分析で確かめる。
- [assumption] Rust で wasm のマルチスレッドを作る方法（ターゲットとツールチェーン）が実用になる。設計の前に小さな試作で確かめる。
- [assumption] GitHub Actions の 3 つの OS の実行環境で、ネイティブの合格条件を CI で確かめられる。
- [assumption] 規模の見積もり（合計 10〜21 か月）は判断による見積もりで、段階 1 の実績で見直す。
