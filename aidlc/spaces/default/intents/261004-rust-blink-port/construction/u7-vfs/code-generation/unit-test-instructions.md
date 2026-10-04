# U7 単位限定テスト手順

## 前提とrunner

`rust-toolchain.toml`のnightly、既存Cargo runner、Git Bashの`C:\Program Files\Git\bin\bash.exe`、既存Linux開発containerを使用する。テスト以外のVFS/Kernel/Runtimeは`#![forbid(unsafe_code)]`。ホストOS差はHost内に閉じ込める。依存はcrates.ioのみ、Cargo.lockとApache-2.0互換性を確認する。

実装前の既存runner確認（現在存在するVFSの5単体テストのみ）：

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib
```

これは最初の実行可能なU7所属クレート限定コマンドである。Part 2 Step 2で終了コード・実行件数を保存し、runner不備をゲスト意味論のRedと混同しない。既存workspace正式baselineは親が直前に確認したcheckpoint証拠を参照し、改変後のworkspace正式検証は親のcheckpointに委ねる。本ファイルの実行コマンドはU7だけに限定する。

## custom順序と差分

まず`tests/guests/u7/build.sh`・Linux native guest・`crates/paludarium-harness/tests/diff_u7.rs`を追加する。ゲストsyscall/プログラムのネイティブ結果を実装前に作り、現実装の失敗の生ログを保存する。期待値を固定ファイルとしてコミットせず、各実行で作る。VFS・FD・パス・Host adapterなど内部部品の単体テストは実装後に書いて実行する。差分先行を内部層TDDに置き換えない。

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1 --nocapture
```

各native/emulated guestに30秒の子プロセス上限を置く。ハングを親の無期限joinで隠さない。NULL stat、無効guestアドレス、flags/dirfd、create/read/write/seek/close、mkdir/unlink/rmdir、hard link、symlink/readlink、rename置換、getdents64、stat/fstat/lstat/newfstatat、flock shared/exclusive/nonblocking/close/dup所有者を含む。stdout/stderr/終了状態、file bytes、種別、link count、errnoを比較する。native inode番号・pid・実時間などの非決定値は対応表で正規化し、意味を持つ値を一括除外しない。

## 単体と隔離・並行

製品内部各部品5–8件以上、happy pathと少なくとも2件のerror/edge、VFS→Kernel→Runtime/Hostのintegrationを用意する。追加するunit-test関数/モジュール名には`u7_`を付ける。

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo test --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium u7_ -- --test-threads=1 --nocapture
```

MemFsは独立したfixtureを各テストに作る。inode寿命・hard link共有・rename原子性・directory判定・offset/append/truncate/seek・非UTF-8・NUL・relative cwd・symlink loopと上限・末尾slash・`..`を検査する。HostFsはHost側の個別temporary root/outside sentinelで、読取だけでなくcreate/write/link/rename/unlink/stat/read_dirでも外への効果がないことを観測する。root能力の相対操作とsymlink/rename差替え競合を検証する。単純なcanonicalize後openを安全性の根拠にしない。並行/ロックケースにも30秒上限、キャンセルとシグナル、close解放を検査する。guest cloneは追加しない。RecordingHost/fake HostFsはerrno/短いIO/キャンセルを再現するために使い、native隔離の証拠をmockだけで代替しない。

## coverage・lint・供給網

U7による変更部品についてLinux行80%以上を測定する。production quotaや閾値を新設/緩和しない。単位限定測定例：

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium --fail-under-lines 80 u7_ -- --test-threads=1
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo fmt -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium -p paludarium-harness --check
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh cargo clippy --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium -p paludarium-harness --all-targets -- -D warnings
```

filterだけでは未変更層の既存テストをcoverageから外すため、必要ならU7が変更するクレートの既存テストを同じ単位測定に含める。無関係なCPU等を足して数値を水増ししない。報告は測定対象/コマンド/covered/totalを明記する。供給網はU7が追加/変更した依存のlicense/source/advisoryを既存cargo-deny設定で確認し、取得エラーを成功に数えない。CIの既存OS単体test/lint/licenseゲートとaction SHAを維持する。

## ファジングと証拠

U7のパス・操作列target `vfs_paths`を作り、既存`syscall_args`にfile syscallを加える。nightly matrixにU7targetを追加し、各600秒、単一入力30秒、ASanと既存LSAN suppressionを保持する。手元では重い処理を順次実行する。

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O vfs_paths -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O syscall_args -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'
```

入力列の予算はharness内に置き製品のファイル数制限と分ける。panic/ASan異常は再現入力を保存し、unit regressionにする。`docs/u7/`とU7 recordに実コマンド、exit code、test名、native比較結果、coverage、fuzz run数/時間、ソースhashを保存する。U7の成功をprobe全体/aube全体/Windows・macOS固有mount/wasm合格と表示しない。