# U2 並行テストの監視区間修正

## 症状と修正

検証済み：修正前の `u2_parallel_runner_bootstrap` は単独実行でも
`outer 30-second watchdog expired` で失敗した（終了コード101）。
実行コマンドと出力は `bootstrap-before.txt` に保存した。

ソース根拠：このケースの `run_case` は監視開始後に
`ensure_guests_built` を呼び、全ゲストをコンパイルしていた。
`OnceLock` は監視用の子プロセスには引き継がれない。
既存の `diff_u2` と同様、親プロセスでビルドを完了してから監視を開始し、
子プロセスではビルド済みの同じゲストを native と emulator で比較する。
2つのゲストの並行実行、stdout/stderr/終了状態の比較、30秒の監視上限を維持する。

## 対象検証

修正前：
`"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test parallel_u2 u2_parallel_runner_bootstrap -- --exact --nocapture`

修正後：
`"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test parallel_u2 -- --nocapture`

検証済み：修正後は10件成功・0件失敗、終了コード0。
`u2_parallel_runner_bootstrap` の子プロセスは13.40秒で成功した。
出力は `bootstrap-after.txt`。この所要時間は性能測定値として扱わない。

## 全体検証と静的チェック

検証済み：`cargo fmt --all --check` は終了コード0。

検証済み：
`"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo test --locked --workspace`
は終了コード0。U2チェックポイントの証跡IDは
`ab56fdea-813a-4214-82b2-9f19f346db97`、`evidence_unchanged: true`。
証跡のコピーは `bootstrap-workspace-verification.json`。

検証済み：
`"C:\Program Files\Git\bin\bash.exe" scripts/linux-dev.sh cargo clippy --locked -p paludarium-harness --test parallel_u2 -- -D warnings`
は終了コード0。出力は `bootstrap-clippy.txt`。
