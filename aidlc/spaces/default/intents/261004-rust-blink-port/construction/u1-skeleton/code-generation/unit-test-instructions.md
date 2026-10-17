# 単体テストの手順（u1-skeleton）

## 新attempt Step29〜31の記録確認

今回の内容確認後に本書を保存し、既存CI証拠の再照合として実行範囲を確定した。製品変更・新テスト実行なし。実際の4produces（計画・本書・code-summary・traceability）に加えてsource-manifestを保存し、未検証項目と既存exact commandsを維持する。

今回の対象は3手順。承認と別の内容確認後に103claims/108filesの現在snapshotと4d52CIを照合し、同じ製品への重い再試験は追加しない。下記commandsは不足回収用。新Summary Confirmation後に本書を含む4producesを全て保存し、旧fuzz/wasm/Safari未検証を保持する。親diaryを依頼前に出力専用追記し、reviewrequestからterminalまでsource/成果物書込とjj snapshot操作を停止する。

## テストの道具と設定

- 単体テストは Rust の組み込みのテスト（`cargo test`）で書く。各クレートの `src/` に `#[cfg(test)] mod tests` を置き、クレートをまたぐものは `tests/` に置く。
- ツールチェーンは `rust-toolchain.toml` の固定の nightly を使う。
- カバレッジは cargo-llvm-cov で、Linux のネイティブ（ubuntu のランナーか、手元の Linux のコンテナ）で測る。

## U1 のテストの実行（U1 のクレートだけに絞ったコマンド）

U1 はワークスペースの各クレートの最初の版を作るので、U1 のクレートを名前で列挙して実行する。

単体テスト（どの OS でも動く）：

```bash
cargo test --locked -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-loader -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-jit -p paludarium-runtime -p paludarium
```

差分テスト（x86-64 Linux だけで動く。手元の Windows では Linux のコンテナの中で動かす）：

```bash
cargo test --locked -p paludarium-harness --test diff_u1
```

カバレッジ（x86-64 Linux で、80% 未満なら失敗）：

```bash
cargo llvm-cov --locked -p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-loader -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-jit -p paludarium-runtime -p paludarium --fail-under-lines 80
```

最初のテストより前に、Step 2 で各クレートに空のテストを置き、上の単体テストのコマンドが通ることを確かめる。

## テストの量（Standard）

- 部品ごとに 5〜8 件の単体テストを書く。Vfs・Host は U1 の範囲が小さいので 5 件とする。
- 結合は差分テスト（`diff_u1`）で確かめる：C と Rust の hello world、命令ごとの差分テストのゲスト。
- 各部品で、正常な場合と、少なくとも 2 つの誤り・境界の場合を確かめる（phases/construction.md）。

## 期待するカバレッジ

- 行カバレッジ 80% 以上（U1 のクレート全体）。下限は下げない。
- 「U1 の命令の一覧のうち、差分テストが 1 件以上ある命令の割合」を記録する（100% を目指す）。

## モックと差し替え

- Host は trait なので、Kernel・Runtime のテストでは、標準出力を記録し、乱数を固定する Host のテスト用の実装を使う。
- Mmu・Cpu は外部に依存しないので、そのまま使う。
- ネイティブとの比べ合わせは、差分テストだけで行う（単体テストでネイティブを呼ばない）。

## テストのデータ

- ゲストのプログラムは `tests/guests/` にソースで置き、テストのときにビルドする。ビルドした ELF はリポジトリに入れない。
- 細工した ELF や命令のバイト列は、テストのコードの中で組み立てる。ファジングで見つかった入力は `fuzz/` の回帰のデータとして置く。
- 実行ごとに変わる値（AT_RANDOM など）は、比べる前にそろえるか、比べる対象から外す。

## 現在のsourceでのU1再確認

上記11packages commandはU1初期版を検証した時点の手順。現在は共有crateにU2 testsも存在するため、このcommandの全通過件数をU1専用件数とは呼ばない。`docs/u2/repairs/r01-workspace-coverage.txt` の197 parent tests/94.00%は過去の証拠であり、現在の合格証拠ではない。今回の失敗ログはverification/に保存し、修復後に関係テストと品質gateを実行する。

不足または関係source変更があった場合のunit-scoped commands：
```
cargo test --locked -p paludarium-harness --test diff_u1
cargo test --locked -p paludarium-harness --lib coverage::tests -- --nocapture
cargo test --locked -p paludarium-kernel --lib tests::write_returns_zero_without_retrying_host -- --exact
cargo test --locked -p paludarium-kernel --lib tests::write_returns_partial_count_without_filling_remainder -- --exact
```
期待件数は順に16、2、1、1（0件を合格と扱わない）。Linux差分はscripts/linux-dev.shから実行する。同scriptは/work/target以外を同期時に削除するため、実行中fuzzとの同時呼出しは禁止。coverageはU1 package gateと別の全体80% gateを維持し、既存の保存済み全体結果を照合する。新しい変更の必要があれば承認後に関係するexact testsと全体gateを回収する。

最新CPU/MMU600秒fuzzはU2追加targetの証拠であり、U1 decode/load_elf/mmu_ops/syscall_args各targetの実行済み証拠へ転用しない。既存nightly各600秒は維持する。macOS/Safari等の未実行環境も未検証と記録する。

## 今回の関連修復の実行

native x86-64 Linuxで実装前に新規命令ゲストとREP観測を実行し、失敗を保存する。修復後は同じコマンドで比較する。

```bash
cargo test --locked -p paludarium-decoder --lib
cargo test --locked -p paludarium-cpu --lib
cargo test --locked -p paludarium-harness --test diff_u1
cargo test --locked -p paludarium-harness --test diff_u2
bash -n tests/guests/u4/build.sh
bash -n tests/guests/u7/build.sh
cargo test --locked -p paludarium-harness --test diff_u4
cargo test --locked -p paludarium-harness --test diff_u7
```

手元Macでは各Linuxコマンドを `bash scripts/linux-dev.sh <command>` で実行し、同期処理は直列にする。QEMUでの結果をnative期待結果とは呼ばない。diff_u1は既存16件に追加回帰がある場合その分を記録する。他suiteも0件の成功は合格扱いにしない。構文検査だけでゲスト生成成功とは判定しない。既存suite全体の確認はfork CIで行い、上記U1 coverage80% gateと全体coverage gateをともに維持する。

## 3 OSのHost追加修復

既存失敗はverification/native-final-mac-e0818962.logとnative-final-windows-e0818962.logに保存。承認後に各OSで実行する限定コマンド：

```bash
cargo test --locked -p paludarium-host --lib native_fs::u7_tests -- --nocapture
cargo test --locked -p paludarium-host --lib
```

OS別のlock errno、Windows hardlink metadata、NativeFs root解放後のfixture削除を確認する。テストのcfg除外やエラー無視で通過させない。既存のroot外アクセス防止も確認する。Host内部layerの新規単体テストは修正後に追加・実行し、API/syscallの観測を修正する場合だけnative期待結果を先に確定する。最後に既存3OS suiteとnative Intel/AMD全体を実行し、全体coverage80%に加え、上記U1限定package coverage80%も測定する。

## Windows Runtimeマウントcleanupの追加検証

修復前の証拠はverification/windows-host-d238c8d1.logのu7_runtime_mount、tests.rs:164、OS error32。productionは変更せず、testのMountedFsとSessionをdropしてからstrict cleanupする。

```bash
bash scripts/linux-dev.sh cargo test --locked -p paludarium-runtime --lib tests::u7_runtime_mount -- --exact --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-runtime --lib
bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-runtime --all-targets -- -D warnings
bash scripts/linux-dev.sh cargo fmt --all -- --check
```

当該テスト1件とRuntime libの既存suiteを確認し、native Windowsで同一のcleanupを含む3OS既存CIを再実行する。実機Linux差分と全体/U1 coverage80%以上のチェックは保持する。

## Windows VFS共通fixtureのcleanup再検証

修正前証拠：verification/runtime-windows-2a8fe818.log。Runtime25件は成功し、VFS mount16件は共通fixture Drop:366でOS error32。productionは変えず、FixtureのMountedFsをdropしてからstrict cleanupする。

```bash
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib mount::u7_mount_tests -- --nocapture
bash scripts/linux-dev.sh cargo test --locked -p paludarium-vfs --lib
bash scripts/linux-dev.sh cargo clippy --locked -p paludarium-vfs --all-targets -- -D warnings
bash scripts/linux-dev.sh cargo fmt --all -- --check
```

mount16件と既存VFS全件、3OS native CIで後片付けまで確認する。削除エラーを無視せず、機能と境界assertionsを保持する。
