# 外からの待ちの一覧：Rust 版 blink（paludarium）

上流の成果物：`bolt-plan.md`、`inception/requirements-analysis/requirements.md`、`inception/contract-design/contract-summary.md`。根拠は `delivery-planning-questions.md` の Q5 です。

**Bolt** とは、1 つの Unit を設計からコードまで通して作り、動くものを出すひと区切りです。

## 一覧

| 待つもの | 持ち主 | かかる時間 | 待つ Bolt | 遅れたときの手 |
|----------|--------|------------|-----------|----------------|
| aube のソースと固定する版（#1645 が再現する版） | aube の upstream（aubepkg/aube） | 版を選ぶだけ（数日） | B10 | 背景資料で再現を確かめた v2.6.1 を候補にする。static-musl でビルドできなければ、B10 で扱いを決め直す |
| formicarium の probe の項目の一覧 | formicarium（同じ持ち主） | formicarium の PoC の進み方しだい | B10（FR6.1、FR6.4） | formicarium の要件書（FR5.1）の 4 項目で先に作り、変わったら両方を同時に直す |
| GitHub Actions の macOS の実行環境で、本物の Safari を動かせること | GitHub | 確かめるだけ（数日） | B11 | 動かせなければ、必要に応じてクラウドの macOS の実行環境を使う（実現性 Q8） |
| crates.io と npm の Trusted Publishing | crates.io、npm | 確かめるだけ（数日） | B15 | 使えなければ、対象と期限を絞ったトークンを使う（team-practices の Deployment） |

## そのほか

- 外部のチームとの受け渡しや、承認を待つ必要はありません。開発者は一人で、承認者もあなたです。
- 外部の API やデータの提供を待つ必要もありません。ゲストはネットワークを使いません（FR2.7）。
