# 速さの試験手順（Build and Test）

## 対象

- **FR8.3（合否あり）**：Node.js の Worker で probe 全体を JIT あり・なしで各 10 回実行する。JIT ありの実行時間が JIT なしより短く、その差が有意水準 5% で統計的に意味があること。検定は U14 で決めた方法（10 対、固定 seed、warmup 各 1、1024 通りの符号反転による片側の正確検定で p < 0.05、平均が改善、20 回すべて PASS・exit 0・30 秒以内、JIT 実行の証拠あり。外れ値の除外や合格を待つ再測定はしない）。
- **FR7.4・NFR6（記録だけ）**：aube 4 コマンドの実行時間を測って記録する。目標値は置かない。
- 速さの測定は PR のゲートにしない（team.md Testing Posture）。

## 実行（Q3：今のソースで新しく 1 回）

品質の CI（`u14-quality.yml` など）が成功した後に、同じ head で 1 回だけ実行する。push と CI の起動は人の承認後に行う。

```sh
"$U14_NODE" packages/paludarium-wasm/tests/u14-performance-check.mjs <control.wasm> target/u11/native/observations.json target/guests/u10 <output>
```

`<control.wasm>` は `scripts/build-u14-cost-profile.py --kind acceptance-control` で作り、native の観測は同じ run の `scripts/u11-run.py --native-only` から作る。CI では `.github/workflows/u14-cost-diagnostic.yml` の手順を使う。

## 記録するもの

- head、run、job、Node の版、runner の CPU 情報
- 20 回分の実行時間、平均、改善率、p 値、各回の終了コード
- JIT が実際に使われた証拠（fallback だけの実行を JIT の成功と数えない）
- aube 4 コマンドの native とエミュレータの時間（背景資料の CheerpX 1.3.9 の値と並べる）

## 前回の結果（履歴）

署名 head 208fd965、run 38840433942：interpreter 平均 5.856590694899998 秒、JIT 平均 5.696370400100001 秒、改善 2.7357263491%、p = 7/1024 = 0.0068359375。今のソースでの新しい測定ではないので、今回の合否には使わない。
