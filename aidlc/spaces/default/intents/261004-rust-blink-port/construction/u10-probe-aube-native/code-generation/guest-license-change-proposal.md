# U10 固定aubeゲストの限定ライセンス例外案

## 再現結果

検証済み: native-first CI [38003529731](https://github.com/Marukome0743/paludarium/actions/runs/38003529731) でprobeと固定aubeのstatic-muslビルドは成功した。その後、aubeのcargo-denyは終了コード4（licenses）で停止した。aube-dependencies.log728–738はwebpki-root-certs1.0.9のCDLA-Permissive-2.0が明示許可されていないことを唯一のerrorとして示す。同8225行は `advisories ok, bans ok, licenses FAILED, sources ok`。重複版のwarningは既存warn方針どおりである。

検証済み: build-receipt.jsonのprobe SHA256は3e2a3c772017bfc6cb5dd275c83b6d4f730bc7f219bfad8b1266f0a4cb66b5a9、aubeは38a4b38f6cf485a2de3a2aab8df9e71aa17ee1f0f4263d687ae0fa5e15c163b4。aube Cargo.lockは固定hash8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668と一致。失敗receiptにはsource_before1365件があるが、例外終了前のsource_after/source_unchangedはない。したがって今回ビルド後ソース非改変は未検証、native probe/aube実行と#1645も未実行である。

## 一次資料と解釈

ドキュメント根拠: [webpki-root-certs1.0.9公式manifest](https://github.com/rustls/webpki-roots/blob/v/1.0.9/webpki-root-certs/Cargo.toml) はCDLA-Permissive-2.0を宣言し、Mozilla由来の信頼CA証明書データを提供するcrateと説明する。[公式LICENSE](https://github.com/rustls/webpki-roots/blob/v/1.0.9/webpki-root-certs/LICENSE) は[LICENSE-CCADB](https://github.com/rustls/webpki-roots/blob/v/1.0.9/LICENSE-CCADB)を指す。

ドキュメント根拠: [CDLA-Permissive-2.0本文](https://cdla.dev/permissive-2-0/) 1.1はデータの利用・改変・共有を認め、2.1は共有データとともに当該契約全文を提供する条件を置く。3.1は計算結果に制約を課さない。

推測（条文からの技術的採用判断）: Apache-2.0製品と、元ライセンスを保持した証明書データの併存に矛盾する再ライセンスやcopyleft条件は見当たらない。製品のApache-2.0への再ライセンスとは扱わず、CDLA全文を当該ゲストbinaryの配布物に添える。本案はこの固定外部ゲストにだけ許可する。CDLA公式compatibilityページはpassword-protectedであり、公式のApache互換宣言を確認したとは主張しない。

## 提案する正確な変更

1. root deny.tomlを変更しない。probe監査も現行root設定で継続する。
2. aube監査用の設定を専用build出力領域 `target/guests/u10/aube-deny.toml` に毎回生成する。内容はその時点のroot deny.tomlの全bytesを保持して、以下だけを末尾へ追加する。これ以外の例外は設けず、別crate・別版のCDLAは拒否を維持する。

```toml
[[licenses.exceptions]]
crate = "webpki-root-certs@1.0.9"
allow = ["CDLA-Permissive-2.0"]
```

ドキュメント根拠: [cargo-deny licenses exceptions](https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html#exceptions) はcrate単位の限定許可をサポートする。[cargo-deny0.20.2 PackageSpec](https://github.com/EmbarkStudios/cargo-deny/blob/0.20.2/src/cfg/package_spec.rs#L95) の `@` はExact照合へ変換するため、1.0.9以外へ広がらない。

3. `cargo deny --manifest-path <fixed-aube>/Cargo.toml --config <output>/aube-deny.toml --locked check` を実行し、advisories/bans/licenses/sourcesの全4種を維持する。confidence-threshold0.93、未知registry/git拒否、禁止crate、脆弱性、yanked拒否を変えない。監査はビルド前へ移す。
4. crates.io取得済みwebpki-root-certs1.0.9のLICENSE全文を `target/guests/u10/licenses/webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt` に保存する。ライセンスファイルhash、crate名/版/取得元、root設定hash、生成設定hashと例外をreceiptに記録し、binaryと一緒にCI artifactへ添付する。
5. 成功/失敗双方のfinallyで固定aubeソースafter snapshotを記録し、beforeと比較する。source変更があれば成功扱いにしない。root設定の全項目が一致し追加例外が上記1件だけであることを内部テストで検査し、別crate/別版の例外は拒否する。
6. 次CIで全監査・両static ELF・ソース非改変・native先行実行を再検証する。品質下限80%や既存製品CIの依存ポリシーを変えない。nativeで#1645が再現しなければ計画Step6に従って止める。

## 計画への追記案と承認範囲

既存Step5の固定guest buildに「webpki-root-certs1.0.9だけのCDLA例外設定を専用build出力へ生成し、CDLA全文をguest artifactへ添付する。root deny.tomlは維持し、全4監査とbefore/after照合を実行する」を追記する。source-lock.jsonにこの1件の例外を明記、build.py/evidence.pyと対応内部検査、workflowのlicense/config artifact保持を更新する。承認前にこれらのapplicationファイルは変更しない。

選択肢: **限定例外案を承認 / 方針を変更**。承認はroot依存ポリシー変更や別ライセンスの一般許可を含まない。
