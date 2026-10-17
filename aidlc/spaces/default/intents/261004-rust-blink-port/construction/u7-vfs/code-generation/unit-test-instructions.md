# U7 単位限定テスト手順

## 前提と現在の検証方針

ドキュメント根拠：Testing Contractのcustom ordering、Standard、Linux行80%以上、各guest/並行ケース30秒、各ASan fuzz target 600秒を維持する。rust-toolchain.tomlのnightlyを使う。MacではDocker DesktopのDocker VMMを維持し、Linuxコンテナ用scripts/linux-dev.shを使用する。Windows用PowerShell/Git Bashの呼出しは現在の実行手順に含めない。

保存済み実装について今回のSteps 15–17は署名付きネイティブx86-64 CIのソースとログを再照合する。Docker VMM内のamd64 QEMUの差を実機Linuxの意味論として扱わない。製品ソースは変更せず、過去のRed/Green/coverage/fuzzは測定時ソースと一致する範囲だけ証拠として使う。今回未実行のコマンドは未検証であり、下記は必要時に再現するためのU7限定コマンドである。

## runnerとネイティブ差分

最初のrunner確認はU7所属VFSクレートに限定する。

```sh
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib
bash scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1 --nocapture
```

ゲストsyscallはケースとLinux native期待結果を先に用意し、内部VFS/Host/Kernelの単体テストは実装後に作る。既存実装の過去の順序証拠はdocs/u7/inventory/diff-red.txt等を参照し、今回の再検証で過去の実装前Redを作り直したと主張しない。

各native/emulated guestには30秒の子プロセスwatchdogを維持する。diff_u7は63親caseを数え、childを二重加算しない。NULL stat、不正buffer/flags/dirfd、作成・read/write/seek/close、mkdir/unlink/rmdir、hard link、symlink/readlink、rename、getdents64、stat系、flockとdup所有権を確認する。stdout/stderr/終了状態、file bytes/種別/link count/errnoを比較し、非決定的なinode番号・pid・時刻の除外はdocs/u7/native-comparison.mdの限定範囲を使う。

## 単体・隔離・CLI接続

```sh
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium u7_ -- --test-threads=1 --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium --test command -- --test-threads=1 --nocapture
```

各部品5–8件以上、happy pathと少なくとも2つのerror/edge、重要境界のintegrationを確認する。MemFsのinode寿命、hard link共有、rename、offset/append/truncate/seek、relative cwd、非UTF-8/NUL、symlink loop、末尾slashと..を扱う。HostFsは各テスト独立のtemporary rootとoutside sentinelを使い、root外のread/create/write/link/rename/unlink/stat/read_dirへの効果がないことを観測する。mockだけでnative隔離を証明しない。flock並行・キャンセル・シグナル・close解放は30秒を維持する。Windowsでは開いたfixtureを閉じてからstrict removeする。guest cloneをU7で追加しない。

## coverage・lint・供給網

過去のU7限定測定89.79%（4203/4681）は測定時ソースの結果である。現在の依存が変更されていれば現在のU7限定coverageの証拠として使わず、NFR3のGAPを明記する。現在のCI全体/骨格coverageが80%を超えていてもU7限定測定へ読み替えない。

```sh
bash scripts/linux-dev.sh cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1
bash scripts/linux-dev.sh cargo fmt -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --check
bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --all-targets -- -D warnings
```

U7変更クレートの既存lib・専用diff・CLI integrationを測定し、未変更CPU等やharness基盤のreport行を除外する。covered/total・対象・コマンド・ソースhashを記録する。依存検査は既存cargo-deny CIのlicense/source/advisory結果とU7依存を照合する。閾値やwarning設定、action SHA pin、Cargo.lockを変更しない。全workspaceの正式な完了検証は親が既に承認されたcheckpointコマンドで実行する。

## ASanファジングと適用範囲

```sh
bash scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O vfs_paths -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
bash scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O syscall_args -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
```

各target 600秒、単一入力30秒、ASanと既存LSAN suppressionを保持する。重い処理は順次実行する。保存済みvfs_paths 859022 runs / 601秒、syscall_args 469436 runs / 601秒は過去の結果であり、targetと全依存のbytesが現在と一致するまで現在の合格とはしない。不一致ならFR9.3/NFR2/NFR3にGAPを残す。製品のquotaは追加しない。panic/ASan異常は再現入力とregressionへつなぐ。

証拠の再照合結果はU7 recordへ保存し、実コマンド・exit・テスト名・除外・hashを記す。U7の結果でprobe/aube全体、wasm/Safari/JIT、ホストマウントの全OS挙動を証明しない。
