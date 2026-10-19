<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-17T04:54:46Z — 人の指示で、Step 9 の実行前に U9〜U12 の code-generation を開き直し、workflow を直す。CI 38994430947 で、u12-native-first.yml・u11-acceptance.yml・u10-native-diagnostic.yml がゲストのビルドに `--advisory-policy u15-fixed-aube-zip9-name` を付けておらず aube の cargo deny が exit 1、u12-quality.yml に `PALUDARIUM_TEST_NODE` がなく JIT の実 Wasm 試験 9 件と diff_u14 が panic した。手元の Mac でも `PALUDARIUM_TEST_NODE` なしで同じ 9 件が失敗し、設定すると 57 件すべて通った。ci.yml の unit tests にも同じ環境変数がない。push と CI は承認を得てから行う。
- 2026-10-17T06:40:00Z — 道具の版（Q2：最新に上げる）は、固定が38ファイル・14 Unitにまたがり、U14のworkflowが正式な確認コマンドの封印対象と分かったため、人がQ5で「今の版で測り、更新は後の別作業」に見直した。
- 2026-10-17T06:45:00Z — push の範囲をソースとCI設定の207ファイルに絞った（`aidlc/` の記録、`target/`・`__pycache__`・`.profraw`、手元用の `tools/aidlc-recovery/` は除外）。fork `codex/build-and-test` の head bd247f1e（署名 Verified）。dispatch：u14-quality 39009460781、u1-u14-source-bound 39009462882、u12-quality 39009464565、u13-quality 39009466368、u14-fuzz 39009468398、release-check 39009470191。u14-wasm-acceptance は fork main に無く dispatch できないが u14-quality から呼ばれる。ci.yml は fork 内の draft PR #1 で動かす。
- 2026-10-17T06:45:00Z — u13-quality（run 39009466368）で windows 単体試験（PALUDARIUM_TEST_NODE なし）と u13-oracle（advisory policy なし）が失敗。U13 の code-generation を開き直し、u13-native-first・u13-wasm-acceptance・u13-quality を同じ形で直した（レビュー READY、正式コマンド exit 0、人が承認）。fork head 2cbef558（署名 Verified、3 ファイルだけの差分）に push し、u13-quality を再起動（run 39012180587）。ほかの dispatch 済み run は head bd247f1e のままで、差は U13 の workflow 3 ファイルだけ。
- 2026-10-17T08:05:00Z — U10 の差分 job が `overlay artifact CI head binding mismatch` で失敗（policy 付きビルドが ci_head=GITHUB_SHA を記録するが、差分の sudo が GITHUB_SHA を落とす）。U9 を開き直して Step 80 で `env GITHUB_SHA="$GITHUB_SHA"` を足した（READY、正式コマンド exit 0、承認）。head e4f84768（署名 Verified、1 ファイル）に push し、u12-quality 39015780495・u13-quality 39015782530 を再起動。外の要因の失敗：Safari の session 作成のタイムアウト（u14-quality 39009460781 の失敗 job だけ再実行）、`load_elf` のファジングで apt.llvm.org への接続失敗（PR ゲートの再実行で再試行）。
- 2026-10-17T09:05:00Z — Safari の session 作成のタイムアウト（WebDriver の要求の待ち時間が 10 秒固定）を U11 Step 27 で直したが、`u11-browser-driver.mjs` は正式な確認コマンドが固定する 223 個の compiled source の 1 つで、確認が `compiled source changed` で exit 1 になった。人の判断で Step 28 で取り消し（e4f84768 の版に戻し、正式な確認 exit 0、承認）。Safari の揺れは今回は再実行と記録で扱い、修正は道具の版の更新と一緒に後で行う。U3 の差分テストは未確認の Intel CPU（signature 000606a6）のランナーで止まる作りで、u13-quality 39015782530 は attempt 2 で成功。
- 2026-10-17T09:05:47Z — Loop-back 1：FR8.3（JIT の速さ）が p = 0.5166 で不合格、NFR7（Safari の揺れ）が未解決。人が Retry with fix を選んだ。U14 の code-generation を開き直し、JIT の効果の改善と Safari の待ち時間、新しい正式な確認コマンドを扱う。

- 2026-10-18T01:17:45Z — Loop-back 1 の後の Build and Test は、人の指示で Modify にした。手順書と前回の記録は残し、FR8.3（run 39030957672、head 1ceae86c）と NFR7（Safari の session 作成だけ 60 秒、2b8723ab・57a8c96f）を Met にした。ほかの目標の証拠も Loop-back 前の head（bd247f1e・e4f84768）から今の head（1ceae86c・57a8c96f）の run に結び直し、前回の結果は履歴として test-results.md に残した。
- 2026-10-18T01:27:17Z — Loop-back 2：FR10.1（公開）だけが Unverified。人が Q6 で公開まで進める、Q7 で 0.1.0、Q8 で U15 の Code Generation に戻って版を書き換えると決めた。版のファイルは 12 Unit の担当ソースのため、Build and Test の中では書き換えない。
- 2026-10-18T11:20:00Z — Loop-back 2 の後（head e3c29d1d）、Modify でまとめ直した。CI 7 run は最終的にすべて成功。U12 の Safari の 1 job が safaridriver 側の時間切れ（31 秒）で 1 回目に落ち、人の判断で失敗 job だけ再実行して成功した。人は Q9 で NFR7 を Not Met とし、直しを公開の前の製品の変更にまとめると決めた。FR8.3 は e3c29d1d でも合格（約 12.9%、p = 1/1024）。
- 2026-10-18T11:20:00Z — 手元の試験で `PALUDARIUM_TEST_NODE=node` を渡すと、mise の shim がこのフォルダで Node の版を決められず、JIT の bridge の 21 件が落ちた。Node 26.12.0 の実体のパスを渡して 809 成功・1 失敗（diff_u8）・4 無視になり、前回と同じ結果を得た。

## Tradeoffs
- 2026-10-18T01:17:45Z — FR8.3 の証拠は head 1ceae86c、今の head は 57a8c96f。差は Safari の道具の 2 ファイルだけで JIT は同じなので、57a8c96f で測り直さずに 1ceae86c の判定を Met に使った。速さは合格を待つ測り直しを禁じているため、追加の測定は避けた。公開（FR10.1）には同じ head の証拠が要ることを記録に残した。
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
