# U4 コード生成の質問

## Plan Approval

既存実装の Steps 1〜14 は履歴として保存し、今回 Steps 15〜18（現在ソース・runner確認、署名済み実機CIとの照合、不足時の最小修正、証拠整合と独立レビュー）を実行します。Testing Contract と unit-test-instructions.md の品質下限・順序・正確な実行範囲を含めて承認しますか。現在ソースの600秒ASanを証明できない場合は GAP とし、Build and Test で回収します。

[Approval Fingerprint]: sha256:v3:dcf836f44a830927cf662e0469915fafba93bc7351585f950cb563c958f00d8b
[Planned Source]: be3c84d12bb3dd3166528167fc5d26dc5f2e8aa8e3112fa0c72ccdd2e8308bd2

- Approve Plan
- Request Changes

[Answer]: Approve Plan

## Consolidated Summary Confirmation

U4 の今回の対象は Steps 15〜18 のみです。既存のメモリ・時刻・待機・シグナル実装と専用テストを点検し、署名済み 4d52be0a の実機 CI と現在ファイルの一致で証拠を更新します。不足があれば対象を絞って追加検証し、製品不具合は native-first／内部 test-after の順序で最小修正します。Docker VMM を維持し、QEMU と実機の結果を区別します。旧検証記録を履歴として保持し、現在ソースの syscall_args/mmu_ops 各600秒 ASan は証明できなければ未検証/GAP として Build and Test へ渡します。30秒watchdog・80%coverage・固定nightly・各600秒は維持し、成果物を整合させ独立レビューを受けます。U1/U2 の承認済み成果物を無断で変更しません。

この内容で成果物の更新に進んでよいですか。

- Looks correct
- Request changes

[Answer]: Looks correct

