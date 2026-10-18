# U11 dispose concurrency plan change

## Question 1

公開FS APIの同時disposeを修正する限定計画変更を承認しますか？

実wasmでPromise.allSettled([fs.dispose(), fs.dispose()])を実行すると、片方が内部エラーになることを独立レビューで再現しました。

packages/paludarium-wasm/index.mjsで処理中の破棄Promiseを共有し、成功後の冪等性と失敗後の再試行を維持します。同時呼び出し・大規模FS・実行中の拒否と再試行の境界回帰を追加し、同一入力で4環境・C12・既存回帰・JS coverage80%以上を確認します。Rust、guest、lock、ASan設定は保持し、一致する今回の検査証拠のみ再利用します。U9の品質CI変更の正式再確認、独立再レビュー、新しい最終確認コマンドの承認も実施します。strict guardと30秒制限を維持します。

[Answer]: 限定修正を承認
