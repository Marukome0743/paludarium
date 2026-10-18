# U15 Step7補足 7a' の内容確認

## Consolidated Summary（2026-10-17）

- Plan Approval：7a'（workflow修正とmacOS証拠）を追記した計画を Approve Plan で承認済み。
- 変更：`.github/workflows/u12-native-first.yml` のゲストビルド1行を `--advisory-policy u15-fixed-aube-zip9-name` 付きの呼び出しに揃え、新規 `.github/workflows/u15-macos-native.yml`（push on `codex/u15-macos-native` のみ、u12-native-first の呼び出しと macos-host job の写し）を足す。製品・試験・他の workflow は変えない。
- 送信：be45b36c を親にした 1 commit（この2ファイルだけ）を、bookmark `codex/u15-macos-native` で署名 push する（外部送信1回）。他の branch・fork main・upstream・tag・registry は触らない。送信後に verified と変更ファイル2つだけを確かめ、作業コピーを元の bytes に戻す。
- 結果：run の原本を読み取り専用で保存・digest 照合し、macOS の FR6.3・FR7.2・FR7.3 を判定する。失敗は原本を保存して止め、再試行しない。
- そのあと記録を更新し、正式 sensor、独立レビュー、正式検証、人の完了承認へ進む。AI-DLC preview の更新は U15 の承認後に行う。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
