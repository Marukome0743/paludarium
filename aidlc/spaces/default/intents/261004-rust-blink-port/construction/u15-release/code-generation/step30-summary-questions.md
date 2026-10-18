# U15 Step30 の内容確認

## Consolidated Summary（2026-10-19）

- Plan Approval：Step 30 を足した計画を Approve Plan で承認済み。
- 根拠：Code Generation の段階を閉じるところで AI-DLC が止めた（`.github/workflows/native-diagnostic.yml`・`u2-production-sanitizers.yml` を消したことを、どの Unit のレビューも受け持っていない）。人は「U15 で Step30」を選び、AI-DLC は U15 だけの Code Generation を開き直した。
- 直すもの：U15 が Step23 で消した 21 の workflow のパスを U15 の source-manifest.json の writes に足す（51→72 件）。code-summary.md の Step29 の項の「manifest に入れない」を直し、Step30 の項を足す。
- 確かめ：承認の後の `aidlc engine orchestrate next` で、段階を閉じる確認がこの 2 件で止まらないこと。
- 変えないもの：製品・CI・workflow・入口・binding・ほかの Unit の記録。push・CI の起動はしない。
- 確かめ方：正式 sensor 2 件と、checkpoint での entry-f の exit 0。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
