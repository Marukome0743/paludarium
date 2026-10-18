# U14 性能・JE・親FR8の修正内容確認

## 修正範囲

- 承認済み計画Steps8〜14を実行する。Steps1〜7と元aube source/lock、U14限定rustls overlay、既存の成功・失敗原本を保持する。
- 先にJEのZF=1 taken／ZF=0 not-takenとJNEの正しい条件名をfixtureへ用意し、fresh x86-64 Linux native原本を取得する。その後interpreter・実Wasm JITを同じbytesへ照合し、CMP+JEの1block／2instructionsを直接確認する。
- 受理用releaseと分けたopt-in診断で、大量fallback、epoch/LRU、compile、JS遷移、block長、checkpointの費用を調べる。診断値を性能受理の標本へ使わない。
- 診断結果に沿い、既存decode情報による未対応命令の事前選別、negative LRU処理、warm bridge遷移を局所修復する。MMU世代確認・bytes照合・144-byte rollback・Worker間失効・module ID非再利用を維持する。budget実命令数化は診断で必要性を確認した場合のみ。
- 修復後の同じ署名head/module/guestで、4環境各28比較、固定coverage80%、依存変更した対象の各600秒ASan/LSan、Node Workerのprobe各10回を実行する。初回と同じseed/順序/warmup・片側正確検定p<0.05・平均改善・全20回成功を要求し、合格待ち再測定や外れ値除外をしない。
- 親FR8を対応表の両集合へ追加し、FR8.1/8.2/8.3の集約理由を記録する。性能未達中はFR8/FR8.3/NFR6をGAP、JE実測完了までは未検証とする。u9専用coverage不足も別に保持する。
- Testing Contractのcustom順序、30秒guest上限・kill/reap/cleanup、coverage分母、監査例外、比較maskを弱めない。旧checkerの全検査と失敗履歴を保持し、変更後source用の正式確認コマンドは独立レビュー後の別承認へ進める。

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
