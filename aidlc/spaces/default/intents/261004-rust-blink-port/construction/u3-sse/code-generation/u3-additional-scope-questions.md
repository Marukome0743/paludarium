# U3 追加調査後の対象・実装範囲判断

## Sources
verification/step2-inventory-completion-assessment.md と step2-additional-investigation-proof.json。rootでraw191ファイルのサイズ・SHA256を照合し不一致0。旧aube再現未達、観測7crypto forms、CPUID未実装を判断対象にする。

## Question
aubeをビルド日2026-10-05・空primer mtime1791158400で再固定し、命令の機能選択をどの範囲で計画しますか？同条件の再ビルドでSHA一致を確認してから新targetを採用し、旧target・記録は維持します。
- A: 観測した暗号7形式とCPUID契約をU3へ追加する（推奨）。SHA256RNDS2/MSG1/MSG2、AESENC/AESENCLAST、PCLMULの2形式と必要なCPUID機能広告を具体設計・native差分ケースへ追加する。未実装機能は広告せず、AVX/EVEX/x87/MMXは無断追加しない。
- B: CPUIDとsoftware fallbackを先に検証する。暗号命令の追加は保留し、明示した機能契約でfallback経路を選ぶこととnativeとの出力一致を検証する。暗号を不要とする結論は未検証のまま出さない。
- X: Other (please specify)
[Answer]: 暗号7形式とCPUID契約をU3へ追加する

## Consolidated Summary Confirmation
追加調査・対象選択を反映した10ステップで実装を進める。aubeは同じ固定ソース・ビルド日2026-10-05・空primer時刻1791158400で独立2回ビルドし、SHA一致を確認してから新対象を固定する。SHA256の3形式、AESの2形式、PCLMULの2形式をnative差分ケース先行で追加する。CPUIDはPaludariumVMの仮想leaf表を実装し、ホスト値を転送せず、未対応・部分対応の機能を広告しない。全familyの追加命令は自動追加しない。80%coverage、3OS、各600秒ASan/LSan、本番wasm・実Safari、先行Unitの成果物維持を継続する。製品動作は未検証。
- Looks correct
- Request changes
[Answer]: Looks correct
