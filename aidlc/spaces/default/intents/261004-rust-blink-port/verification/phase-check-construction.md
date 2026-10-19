# Construction → Operation の境界の確認

2026-10-18。CI Pipeline の段階の Step 5 として書いた。

## 判定

**未解決あり**。Construction → Operation へは進めない状態。ただし、このワークフローでは Operation フェーズをスキップしている（team.md の Deployment：ブラウザ側の本番実装と formicarium への組み込みは formicarium が担う）。残る項目は下の「未解決の項目」のとおり、人の手順と次の製品の変更で扱う。

## 確かめたこと

| 確認 | 結果 | 根拠 |
|---|---|---|
| 全 Unit が作られ、試験された | はい。15 Unit（u1-skeleton〜u15-release）の Code Generation は承認済みで、Build and Test は head e3c29d1d の CI 7 run（最終的にすべて成功）で試験した | `construction/build-and-test/test-results.md` |
| 各 Unit の `code-generation/traceability.json` がある | はい。15 ファイルすべてある | 下の表 |
| 各 Unit の対応表に未解決の指摘がない | U15 以外はなし（GAP・ORPHAN が 0 件）。U15 は FR10.1 と NFR8 が GAP（実公開と公開後の照合がまだのため） | 下の表 |
| Unit をまたぐ FR・NFR の対応 | 不合格。未対応は FR10.1 の 1 件 | `construction/build-and-test/cross-unit-traceability.md`、`aidlc engine sensor-traceability --stage build-and-test`（2026-10-18） |
| Build and Test の目標 | FR10.1 が Unverified、NFR7 が Not Met。ほかはすべて Met。人は Accept failure を選び、段階を承認した | `construction/build-and-test/test-results.md` の Target Verification Matrix と判定 |
| CI のゲートが Build and Test の確認の命令を守らせる | はい（設計として）。PR のゲート（`ci.yml` の 23 job と `release-check.yml`）が lint・3OS の単体テスト・依存の検査・差分テスト・wasm 4 環境・カバレッジ 80% を、夜間と公開の前の確認が全品質・ファジング・速さの判定を受け持つ。upstream の必須チェックの設定は人が行い、workflow の変更（夜間の作り直し、作業用の workflow の整理）は次の製品の変更で行う | `construction/ci-pipeline/quality-gates.md`・`ci-config.md` |

## Unit ごとの対応表（`construction/<unit>/code-generation/traceability.json`）

| Unit | OK | Deferred | N/A | GAP |
|---|---|---|---|---|
| u1-skeleton | 55 | 40 | 12 | 0 |
| u2-integer-isa | 44 | 33 | 15 | 0 |
| u3-sse | 10 | 39 | 11 | 0 |
| u4-memory-signals | 15 | 34 | 11 | 0 |
| u5-threads-futex | 10 | 40 | 10 | 0 |
| u6-events-sockets | 13 | 37 | 10 | 0 |
| u7-vfs | 16 | 34 | 10 | 0 |
| u8-process-spawn | 10 | 40 | 10 | 0 |
| u9-terminal-io | 12 | 38 | 10 | 0 |
| u10-probe-aube-native | 17 | 33 | 10 | 0 |
| u11-wasm-launcher | 20 | 42 | 1 | 0 |
| u12-macos-host | 15 | 46 | 0 | 0 |
| u13-windows-host | 15 | 46 | 0 | 0 |
| u14-jit-wasm | 11 | 0 | 0 | 0 |
| u15-release | 1 | 0 | 0 | 2（FR10.1・NFR8） |

Deferred は、その要件を担当するほかの Unit に回した行で、Unit をまたぐ対応（`cross-unit-traceability.md`）で、FR10.1 を除くすべてがどれかの Unit で作られていることを確かめた。

## 未解決の項目

- **FR10.1（公開）**：版は 0.1.0 に決まり、公開の部品と手順はそろった。upstream への取り込み、`release` environment の保護、名前の所有と初回の公開、Trusted Publisher、upstream の head での品質 run と `u15-acceptance`、`v0.1.0` の tag と承認は人の手順（`docs/release.md` の Owner hand-off）で、まだ終わっていない。U15 の NFR8 の GAP（registry・OIDC・初回トークン・provenance の実照合）も、実公開で確かめる。
- **NFR7（揺れるテスト）**：safaridriver 側の時間切れという Safari の新しい揺れ（run 39114110570 attempt 1）。Build and Test の Q9 の A のとおり、公開の前に製品をもう一度変えるときに直す。
- 次の製品の変更でまとめて行うもの：NFR7 の直し、CI の workflow の変更（`ci-config.md`）、残している Minor（U15 の入口 v4 のレビュー 04 の 6 件、U15 の Unit のレビュー 07 の 4 件、U1・U14 の Minor）。そのあと CI 一式と正式な確認コマンドの入口の作り直しを 1 回で行う。

## 正式な確認コマンド（2026-10-18 追記）

U15 の確認の後、正式な確認コマンドは e3c29d1d を起点にした新しい入口 `entry-c.py` に変わった。U15 の checkpoint はこのコマンドで exit 0。製品は変わっていないので、上の判定（未解決あり）は変わらない。

## 人の承認

- [ ] この境界の確認の結果を確かめた（CI Pipeline の段階の承認で確かめる）
