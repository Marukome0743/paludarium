# U14 aube lock overlay修復：内容確認

## Consolidated Summary Confirmation

- 元aube source/tag/revisionと元Cargo.lockを保持し、U14ビルド用コピーだけrustls 0.23.45から0.23.46へ更新する。
- 元lock SHA256 8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668と更新lock SHA256 b8d403f2c449da8eb104cca0cbd1c9f1f61ade8249615c246ae6cc8cd531db0eを厳密照合し、rustls一件のversion/checksum以外の変更を拒否する。
- 元sourceとビルド用source、元lockと更新lockをreceiptで分離する。通常U10/U11/U12/U13経路と製品workspace/fuzzのlockは維持する。監査例外は増やさない。
- 拒否回帰14件以上と既存証拠/policy/runner回帰、固定Python coverage80%以上を検証する。更新guestのnative期待値と同じbinaryを使い、4環境・性能・対象600秒ASan/LSanを再検証する。
- 初回CI失敗と現在coverage未成立を保持し、旧成功を更新guestの成功へ流用しない。既存u14実装とU11梱包修正を保持する。

承認済み計画に沿って、この内容で修復を実装してよいですか？

- Looks correct
- Request changes

[Answer]: Looks correct
