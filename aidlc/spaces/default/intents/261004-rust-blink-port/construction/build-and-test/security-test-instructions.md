# 安全性の試験手順（Build and Test）

## 対象（NFR2・NFR3・NFR4・NFR8、project.md の Mandated／Forbidden）

| ID | 内容 | 確かめ方 |
|---|---|---|
| NFR2 / FR9.3 | ゲストからどんな入力が来ても panic・未定義動作にならない | ファジング 13 対象を各 600 秒、ASan/LSan、終了コード 0 |
| NFR3.1 | `unsafe` はホスト接続部と JIT の外にない | 各層の `#![forbid(unsafe_code)]` と clippy（`undocumented_unsafe_blocks`、`unsafe_op_in_unsafe_fn` を deny） |
| NFR3.2 | clippy の警告ゼロ | `cargo clippy --locked --workspace --all-targets -- -D warnings` |
| NFR2.1 | 製品コードで `unwrap`・`expect`・`panic` を使わない | clippy の `unwrap_used`・`expect_used`・`panic` を deny |
| NFR4 / FR3.2 | ホストのファイルを見せても指定したディレクトリの外へ出られない | U7 の `..`・symlink の試験、Windows の symlink rename race（1000 反復、交換 1 回以上、outside 不変） |
| NFR4 / FR2.1 | syscall を番号のままホストに渡さない、未実装は ENOSYS | Kernel の単体テストと差分テスト |
| NFR8.1 | 依存は crates.io だけ、ライセンスが Apache-2.0 と両立、既知の脆弱性なし | `cargo deny --locked check`（`deny.toml`） |
| NFR8.2 | GitHub Actions はコミットの SHA で固定、既定の権限は読み取りだけ | actionlint と workflow の目視、`permissions: contents: read` |
| Forbidden | webix・portabox の系列と `lanmower/blink` を参照・依存・取得・実行しない | `deny.toml` の禁止と依存一覧の確認 |

## ファジング（Q3：今のソースで新しく実行）

CI の `.github/workflows/u14-fuzz.yml`（13 対象）で、push と起動の承認後に実行する。各対象の条件：

```sh
cargo fuzz run --fuzz-dir fuzz --sanitizer address <target> -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
```

`cpu_u2` は `-max_len=4096`、`mmu_u2` は `-max_len=4608`。`ASAN_OPTIONS=detect_leaks=1`、`LSAN_OPTIONS=suppressions=fuzz/lsan.supp`。対象：decode、load_elf、syscall_args、vfs_paths、mmu_ops、cpu_u2、mmu_u2、kernel_threads_u5、kernel_futex_u5、kernel_events_u6、kernel_sockets_u6、jit_compile ほか `u14-fuzz.yml` に並ぶもの。

注意：`nightly.yml`（main、2026-10-16 の run 38967100569）は musl target で ASan をビルドしようとして全対象が失敗している（`sanitizer is incompatible with statically linked libc`）。今回の正式な実行には `u14-fuzz.yml` を使い、`nightly.yml` の問題は既知の不具合として記録する。

## この Mac での補助確認

```sh
env PATH="$HOME/.cargo/bin:$PATH" cargo clippy --locked --workspace --all-targets -- -D warnings
env PATH="$HOME/.cargo/bin:$PATH" cargo fmt --all --check
```

`cargo deny` はこの Mac に入っていないため CI の `dependencies` job で確かめる。

## 合否

- ファジングは 13 対象すべてで 600 秒以上・終了コード 0。crash・leak が出たら、入力と原本を保存して失敗とする。
- 有限時間のファジングは、任意の入力に対する安全性の証明ではない（記録に書く）。
