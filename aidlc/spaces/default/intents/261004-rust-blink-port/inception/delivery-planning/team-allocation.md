# 担当の割り当て：Rust 版 blink（paludarium）

上流の成果物：`bolt-plan.md`、`inception/practices-discovery/team-practices.md`。根拠は `delivery-planning-questions.md` の Q8 です。

**Bolt** とは、1 つの Unit を設計からコードまで通して作り、動くものを出すひと区切りです。**mob** とは、同じ作業を一緒に進める作業の組です。

## 体制

- チーム編成の工程は、この計画では飛ばしています。開発者はあなた一人です（意図書の関係者マップ）。
- 作る段階は、このセッションで、あなたと AI で進めます（Q8）。
- すべての Bolt を、AI の開発者（aidlc-developer-agent）が実装します。設計、レビュー、確認、承認は、このセッションの中で行います。
- チームごとに Unit を受け持つ方式（team ownership）は使いません。記録上の Unit Ownership は既定（solo）のままです。

## Bolt ごとの担当

| Bolt | Unit | 実装 | 確認と承認 |
|------|------|------|------------|
| B1〜B15 | U1〜U15（`bolt-plan.md` の順） | AI の開発者 | あなた（各 Unit の完了時） |

チームが 1 つなので、複数チームの間で計画を調整する表（Program Board）は作りません。
