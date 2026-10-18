# U12 更新計画の実装前確認

## Consolidated Summary Confirmation

承認済みSteps8〜10を含む更新計画に従い、最新Rust nightly 2026-10-11と検証ツールへ統一します。同一署名ソースで3OS品質・fresh Linux差分／coverage80%以上・production wasmとNode／Chromium／Firefox／本物Safari各14ケース・11対象各600秒ASan／LSanを確認します。U12は既存NativeHostを活用してmacOS端末接続を追加し、内部3部品各7件以上・実PTY7件・macOS guest14ケース以上を検証します。MMU最大4608バイト、ゲスト30秒制限、strict guard、比較条件を維持します。旧検査・成功と失敗原本を保持し、compiler変更前の証拠を現行の合格へ流用しません。fresh Linux期待値を製品のゲスト動作変更前に取得します。不足や計画外修正は具体化して提示します。新最終確認コマンドは独立レビューと別承認後に実行します。

Does this all look correct before I generate the artifact?

[Answer]: Looks correct
