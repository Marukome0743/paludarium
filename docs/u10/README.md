# U10 probe / aube 検証

検証済み：署名済み実装ソース `26b76c01a72a050a57d12420365a73997d9a637e` の Actions run `38009664758` は、通常 CI と必須 U10 reusable workflow の全11ジョブが成功しました。fresh native14 / emulator16 の全操作が成功し、stdout/stderr/exit が一致しました。

独自 probe の標準項目は `tokio-timer`、`unix-stream-pair`、`rayon`、`mutex-condvar`、`fs-basic`、`fs-hardlink`、`fs-symlink`、`fs-flock` です。単独 8 実行、全項目実行、node がない環境の診断を行います。aube は v2.6.1 のコミット `bd94e42f54d3b5e3dd102716b7197f316cb5f4ed` を固定し、`--version`、`install`、node_modules を削除した後の `install --frozen-lockfile`、`list` を実行します。

ネイティブ実行はネットワーク namespace 内で行い、エミュレータのネットワークも無効にします。ビルド時の依存取得は隔離実行前に完了させます。専用ジョブでは `cargo test --locked --offline -p paludarium-harness --test diff_u10 -- --include-ignored --nocapture` を実行します。通常 workspace テストでは外部固定 ELF が必要な親テストは ignored ですが、専用必須ジョブがこれを実行します。

同じ ELF の native 結果を毎回先に取得し、stdout、stderr、exit を比較します。ANSI の色、正確な fixture パス、aube の経過時間表記だけを明示的に正規化します。各操作は 30 秒以内に終了しなければ失敗し、期限時は子孫を停止・回収します。probe の欠落、重複、FAIL は許容しません。default VFS の version/install も必須で、mounted fixture の 4 操作で置き換えません。

検証済み：Linux native fixture の package.json 3 ファイルは 0644 です（run `38009146869` / job `114084839291` の `native-stat.json`）。承認された C10 API `with_file_mode` は初期ファイルの mode を指定します。既存 `with_file` の 0755 を維持し、不正な mode/path、存在しないファイル、正規化後の重複指定を拒否します。通常の chmod/fchmod syscall は今回追加していません。

検証済み：ローカル runtime 単体テスト 53 件、Python 検証 37 件、runtime/harness の clippy と変更 Rust ファイルの fmt が成功しました。同実装 head の Linux coverage ジョブ 114086489426 は workspace 10152/10944 lines（92.76%）、U1 9928/10694（92.84%）、U9 LCOV 4613/5342（86.35%）、U3 LCOV 2246/2758（81.44%）で既存80% floorを満たしました。U3 の人向け report は2246/2990（75.12%）で、実ゲートのLCOVと分母が異なります。分母差の具体的な内訳は未検証です。異なる集計範囲の値を同じ分母の割合として扱いません。

ライセンス監査は root `deny.toml` を変更せず、probe と aube で advisories/bans/licenses/sources の全チェックを維持します。ユーザー承認済みの例外は guest の `webpki-root-certs@1.0.9` の `CDLA-Permissive-2.0` だけです。実際のライセンス全文、hash、派生監査設定、固定ソースの前後 hash を build receipt に添付します。[ソース調査](source-review.md) と [static PIE の判定](static-pie-checker.md) も参照してください。

`#1645` の再現条件は frozen の stderr と list の stdout の両方で、filedep と linked が 0.0.0 と報告されることです。upstream の不具合を修正する検証ではなく、固定版の観測を一致させる検証です。

Linux 以外の最終差分、全入力での動作保証、通常 chmod/fchmod の対応は未検証です。[計測の範囲](timings.md) を参照してください。
