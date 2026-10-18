# U3 SHA memory alignment 契約の確認

## Sources
verification/step8-sha-memory-proof.json、verification/step8-sha-memory-contract-decision.md。署名head0408a2e8c6ba129fc3034870bd0fb8554c350d42、診断run37809419737。AMD EPYC7763の2 runnerとIntel Xeon8573Cの1 runnerで各3反復、同一encoding/input/sourceを確認。AMDは非整列accessibleで成功・跨PROT_NONEで#PF、Intelは両者#GP。Intel SDM Rev089 Table2-21とSHA参照先は16-byte alignment条件を定める。AMD全機種への一般化・AMD仕様上の許容は未確認。

## Question
SHA256RNDS2/MSG1/MSG2の非整列メモリoperandについて、仮想CPUの契約とnative比較をどう固定しますか？
- A: Intel SDMの整列契約を採用する（推奨）。16-byte整列必須、非整列はread前に#GP。native全rowを保存し、整列caseは厳密比較する。非整列6rowのみ、観測済みAMD profileとの差を明示して同値主張から外し、独立した#GP/RIP/destination不変テストを必須にする。Intel nativeは全状態を比較し、未確認profileは失敗とする。広域maskやcase削除はしない。
- B: 観測AMD型の非整列許容を固定する。Intel SDMとの不一致とIntel native側の比較除外を明示し、仮想CPUの独立契約テストを必須にする。hostごとに意味論は切り替えない。
- X: Other (please specify)
[Answer]: Intel SDMの16バイト整列契約を推奨

## Consolidated Summary Confirmation
SHA256RNDS2/MSG1/MSG2のメモリoperandは、hostに依存しないIntel SDMの16-byte整列契約へ固定する。非整列はメモリread前に#GPとし、RIP・destination・状態不変を独立契約テストで検証する。native全rowを保存し、整列caseおよびIntel nativeは厳密比較を維持する。観測済みAMD profileで差が再現した非整列6rowだけはprofile差異を明示し、native同値の主張から外す。未確認profileは成功へ丸めず失敗とし、広域mask・case削除・coverage80%基準の引下げを行わない。修正後のfresh native/3OS/lint/coverage、本番wasm・実Safari、変更ソースclosureに対応した各600秒ASan/LSanを確認する。先行Unit25成果物は維持し、共有ソース変更後の完了確認を更新する。
- Looks correct
- Request changes
[Answer]: Looks correct
