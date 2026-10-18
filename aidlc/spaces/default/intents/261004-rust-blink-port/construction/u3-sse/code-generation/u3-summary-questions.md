# U3 実装前の確認

## Sources
承認済みcode-generation-plan.mdとunit-test-instructions.mdに基づく。計画内容の変更はない。

## Consolidated Summary Confirmation
承認済みの10ステップに従う。専用runnerの準備、probe/aubeのSSE命令の棚卸し、native期待結果の生成を先に行い、その後Decoder・CPUを実装する。丸め・MXCSR・例外・メモリ境界、3OS CI、coverage80%、ASan/LSan、本番wasmと実Safariを検証する。対象命令の網羅性が確定しなければ製品実装前に人へ判断を戻し、全量達成を主張しない。先行Unitの成果物を維持する。
- Looks correct
- Request changes
[Answer]: Looks correct
