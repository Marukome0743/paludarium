# U5 要件と検証の対応

（2026-10-19 Step34で追記）この表と次の行の「検証済み：source9aa14978」、NFR9の `nightly-2026-10-01` などのtoolchain・compiler・Nodeの値は、その時点（head 9aa14978）の観測である。今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`、今の状態は code-summary.md の先頭の「現在の状態」節。U5の製品のファイルが27d05de1まで変わっていないことは、U15の `construction/u15-release/code-generation/verification/ci-27d05de1/product-changes-e3c29d1d-27d05de1.txt`（e3c29d1d〜27d05de1の製品の変更の一覧）で確かめられる。

検証済み：source9aa149786015ad9f789e8527cc30d7f30f2f9482（Verified）。原本・hash・job IDはfinal-proof.json、コマンドとexit0出力はverification/final-verification.md。

| 要件 | 実装・証拠 |
| --- | --- |
| FR2.3 | clone/futex/timer待機・untimed SA_RESTART、native-first43件、同source43/43一致 |
| FR5.4 | Host real workers/Runtime join・exit・kill、3OS libと同期回帰 |
| FR9.1 | Kernel U5新2件を含む27test、417source leaf・先行証拠73件保持、候補checker43照合exit0 |
| NFR1 | 全43manifest/JSON/raw stdout/stderr/exit/timeout一致、先行U1/U2/U3/U4/U7/U9差分成功 |
| NFR2 | threads18531279/futex9935154runs、各601秒ASan/LSan、exit0/lock不変 |
| NFR3 | 固定13製品file 3256/3825=85.12%、floor80維持 |
| NFR7 | watchdog30秒、timeoutfalse、join/channel/Host entry同期、metadataと実中断の分離 |
| NFR8 | 3OS fmt/clippy/tests/deny、現wasm Node21/実Safari27.0.1 21成功 |
| NFR9 | nightly-2026-10-01、locked check/test/clippy、fuzz lock before/after/current一致 |

timer receiptは入口前通知でも期限を保ち、ownerだけがackし、別worker process drainでは消えない。masked/ignored signalとmetadataだけではEINTRにせず、実中断/group終了を保持する。native timed WAIT/BITSETはSA_RESTARTでもEINTR、untimedは再開しhandler値変更でEAGAIN。

初回coverageの未知Intel profile拒否原本を保持し、同sourceで一度再実行して成功した。U3 oracle/allowlistは変更していない。Node/実Safariは今回の現moduleで実測した。旧e8e23fbd proofは歴史として保持する。U8別プロセスclone、U11 guest Worker、probe全量と全入力保証は有限43結果から推測しない。独立レビューと人の完了確認は親へ渡す。
