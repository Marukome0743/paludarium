# U2：非機能要件の確認

## Sources

- `inception/requirements-analysis/requirements.md` の NFR1〜NFR9。
- `inception/contract-design/contract-summary.md` の C1・C3・C4・C5 と、境界に時間切れ・再試行を設けない方針。
- `construction/u2-integer-isa/functional-design/functional-design-questions.md` Q1 と確認済み要約。
- `construction/u2-integer-isa/functional-design/functional-spec.md`、`rules.md`。
- 既定の道具と実行量は `construction/u1-skeleton/nfr-requirements/nfr-requirements-questions.md` Q2〜Q4、時間切れは同工程 `security-requirements.md` NFR7.1。ここでは回答を新しく作らず、既存の決定を引き継ぐ。

## 追加質問の判定

未決の製品方針はない。正しさ・堅さ・検証量は承認済みの要件から導く。実装の細部とテストケースの一覧はコード生成の計画で具体化する。性能の新しい目標値やゲストの資源上限は追加しない。wasm の共有メモリでの検証は U11、ゲスト clone・futex の統合は U5 のまま。

## Consolidated Summary Confirmation

- 命令のレジスタ・定義済みフラグ・メモリ・終了状態を、実行ごとに得る native x86-64 Linux の結果と比較する。反復比較の例外では RIP・count/index・flags も観測する。
- 不正な bytes、幅・アドレスの境界、ゼロ除算、権限違反はゲストの fault として処理する。エミュレータの panic や未定義動作を許さず、CPU・MMU などのコアは unsafe を禁止する。
- ファジングは既定の cargo-fuzz を使い、U2 の有界な命令実行を対象に加える。夜間 CI で対象ごとに 10 分実行し、検出が 0 件なら合格。発見入力は回帰テストにする。これは native と一致することの証明とは分けて扱う。
- 原子操作は通常アクセス・map/protect/unmap と共通の排他で守り、ホストの競合テストで更新の欠落・途中の値・ページ跨ぎを検査する。差分・並行ケースは既定の 1 件 30 秒で時間切れにし、揺れや時間切れを合格にしない。製品の実行時間や資源の上限とは区別する。
- Linux の行カバレッジ 80% 以上、fmt・clippy、既存テストの合格を維持し、命令の差分テスト保有率と形式別の未検証範囲も記録する。
- 現在の nightly 固定、既存デコーダの包み、Cargo.lock、cargo-deny と crates.io 限定の取得元を引き継ぐ。U2 で新しい依存や認証サービスは追加せず、Cpu からホストへの直接アクセスは設けない。

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct