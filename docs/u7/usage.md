# U7 ファイルシステムの利用

ドキュメント根拠：`Config`・`Mount`・`Session` の公開API、C6/C10/C11。検証済みのコマンド、テスト名、結果は `verification.md` と `inventory/` に記録する。

既定のセッションは独立したMemFsを持つ。`Config::with_file` は起動前にguest絶対パスへバイト列を配置する。ホストディレクトリを公開するには、利用側が明示的に `Config.mounts` へ `Mount { host: PathBuf, guest: Vec<u8> }` を追加し、`NativeHost` を渡す。

```rust,no_run
use std::{path::PathBuf, sync::Arc};
use paludarium::{Config, Mount, NativeHost, Session};

let config = Config::new("/program", vec![b"program".to_vec()])
    .with_file("/program", std::fs::read("program")?);
let mut config = config;
config.mounts.push(Mount {
    host: PathBuf::from("fixtures"),
    guest: b"/data".to_vec(),
});
let session = Session::new(config, Arc::new(NativeHost::new()))?;
let status = session.run()?;
# Ok::<(), Box<dyn std::error::Error>>(())
```

ホストrootのディレクトリ能力はSession作成時に開く。以後のHost操作はこの能力から相対的に行う。guest namespaceの絶対symlinkはguest rootから解決する。Hostに保存するリンクは能力内の相対targetを使い、guestが作成したtargetの表示値をinode単位で保持する。異なるマウント間のhard link・renameはEXDEVを返す。

preloadファイルは同じguestパスのホストファイルより優先する。root mountでもpreloadされたプログラムはMemFsに残る。guestの通常file操作はホストmount内では実際のホストファイルに作用するので、テストには独立したfixture rootを使う。

FDはopen-file descriptionへの参照で、dupはoffset・status flags・flock所有者を共有する。unlink後も開いているファイルは利用できる。flockはshared/exclusive/nonblocking、変換、最後のdescription closeによる解放を扱い、阻塞待機はHostのキャンセル/シグナル境界を通す。

検証対象はU7のMemFs、native host能力、Kernel file ABI、Runtime接続である。U10のprobe/aube全体、U11のブラウザ/wasm、U12/U13固有プラットフォーム合格はこのUnitの結果に含めない。platform別検証状況とABI比較の除外は `verification.md` に明記する。

コマンドでは次のように指定する。`--mount=<host>:<guest>`と繰り返し指定も使用できる。guest側は絶対パスにする。guest programの後の引数はguestへ渡すため、オプションはprogramの前に置く。

```text
paludarium --mount fixtures:/data ./program
```

検証済み：`cli::tests::u7_cli_mount_separate_argument`、`u7_cli_mount_equals_and_repeat`、`u7_cli_mount_windows_drive`、`u7_cli_mount_non_utf8`、`u7_cli_mount_after_program_is_guest_argument`、commandの`u7_cli_root_mount_keeps_private_program`と`u7_cli_mount_missing_root_is_emulator_error`が最終Linux測定で成功（`inventory/coverage-final.txt`）。
