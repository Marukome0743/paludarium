# U15 Step13〜16 の内容確認

## Consolidated Summary（2026-10-18）

- Plan Approval：Step13〜16（Build and Test の Loop-back 2：版 0.1.0 と公開の準備）を追記した計画を Approve Plan で承認済み。
- 根拠：Build and Test で人が Q6「公開まで進める」、Q7「0.1.0」、Q8「U15 に戻って行う」を選んだ。
- Step13：workspace の版とcrate 間の依存 11 件、`package.json` を 0.1.0 にする。`Cargo.lock`・`fuzz/Cargo.lock` は workspace の crate の版の行だけを変え、外部 crate の版は変えない。fuzz crate・harness・Rust Wasm adapter は非公開のまま。`README.md`・`docs/release.md` の文を直す。単体 2 件を足し、tests/release 全件・validate・package-check・build・fmt・clippy を手元で実行する。
- Step14：`REQUIRED` 8 目的と `ACCEPTANCE` 5 条件の対応表を `docs/release.md` に書き、`scripts/release/acceptance.py` と手動起動だけの `.github/workflows/u15-acceptance.yml` を作る。`trusted_publishers_registered` は人の申告（既定 `false`）。単体 8 件以上と統合 2 件、新部品も coverage 80% 以上。
- Step15：fork への署名 push と CI の起動は、その前に人の承認を受ける。速さの判定は新しい head で 1 回だけ。版のファイルを持つほかの Unit は AI-DLC の手順で確かめ直す。
- Step16：upstream で人が行う手順（PR の取り込み、`release` environment、名前の所有と初回の公開、Trusted Publisher、main の head での品質 run と `u15-acceptance`、`v0.1.0` の tag と承認）を、時期と確かめ方を添えて書き、人に伝える。U15 は公開そのものをしない。FR10.1 は公開と照合が済むまで GAP のまま。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
