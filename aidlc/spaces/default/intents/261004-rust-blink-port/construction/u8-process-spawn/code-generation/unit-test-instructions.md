# U8 テスト手順

## 承認された現行ソース追加検証（Steps13〜15）

既存製品・guest fixtureを保持し、新専用診断CI/helperを含む全入力・両lock・実使用compiler・設定のbefore/after/currentを保存する。旧証拠は履歴として区別する。

同じ署名済み現行ソースのLinuxで既存全29差分＋runner1をfresh nativeと比較し、Rust Commandとwait-faultを含む全ケースを保持する。3OSのU8入口は `cargo test --locked -p <MMU/Kernel/Runtime crate> --lib u8_` を使う。実在する本体42件（MMU7/Kernel28/Runtime7）と既存Kernel pipe7/exec-thread7の回帰14件を個別に記録し、合計MMU7/Kernel42/Runtime7＝56件、ignored0を確認する。旧 `u8_tests::` の実測は42件であり、56件という旧報告は訂正し原本を残す。関連U5 Kernel27/Runtime6＝33件、U6 Kernel49件、fmt/Clippy警告エラーと依存4検査の原本exitを保存する。全入力30秒watchdog、kill/reap、比較maskとLinuxのEFAULT時reap動作を維持する。

workspace全体coverageは既存対象規則でprofileを空にし、fresh U3 native、instrumented CLI、U8/U5/U6差分を含む既存測定経路を実行する。全体80%以上と分母を記録し、U8限定測定や古い全体92.75%で代替しない。正確な実コマンド・対象file・LCOV/JSON/consoleと実exitを保存する。閾値・対象を減らさない。

ASanは既存対象ごとの依存閉包・両lock・実使用compiler・flags・設定・原本一致を記録し、一致した保存結果のみ限定再利用する。U8 fork/exec/waitのNode/Safari成功は未検証と明記し、共有launcher成功を代替にしない。正式検査と独立レビュー後、新最終確認コマンドは変更承認を得て実行する。現在の承認済みコマンドは `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3-u5-u6.py`。

## Setup

既存 Cargo test と paludarium-harness を使う。rust-toolchain.toml の nightly を使い、Cargo.lock を維持する。native oracle は x86-64 Linux と musl-gcc、Rust の x86_64-unknown-linux-musl target を必要とする。Mac では単体のみ実行可能で、Linux 差分の cfg 除外による 0 件成功を合格にしない。

Step 1 で u8_runner_ready を作り、次のコマンドが 1 件を実行することを確認してからゲストの最初の native ケースに進む。ツールは環境の実体パスを解決し、以下 cargo はその実体を使う。C/Rust ゲストは tests/guests/u8/build.sh で target/guests/u8 に置く。

## Commands

すべて workspace root で実行する。各コマンドは U8 か関連する単一 Unit に限定する。

```sh
cargo test --locked -p paludarium-harness --test diff_u8 u8_runner_ready -- --exact
bash tests/guests/u8/build.sh target/guests/u8
python3 tests/guests/u8/observe.py --native-only --cases tests/guests/u8/cases.json --guest-dir target/guests/u8
cargo test --locked -p paludarium-mmu --lib u8_tests::
cargo test --locked -p paludarium-kernel --lib u8_tests::
cargo test --locked -p paludarium-runtime --lib u8_tests::
cargo test --locked -p paludarium-harness --test diff_u8 u8_ -- --nocapture
```

上記の U8 ファイル・テストは実装 Step 1〜8 で作成する予定で、計画時点では未実行。runner-ready は oracle を実行できる Linux 環境と timeout 機構を検査し、環境不足を失敗として示す。observe.py は native-only を syscall 実装前に実行し、各ケースを timeout で囲む。diff_u8 は毎回同じバイナリを native と emulated で動かす。

## Assertions and Volume

- MMU 7 件：私有複製、共有 mapping、親子書込み、protection、brk、unmap、fault。
- 親子管理 7 件：PID の一意性、親子登録、子だけの exit_group、zombie、全スレッド終了、二重 reap、待機の競合。
- exec 境界 7 件：argv/env、ENOENT、EFAULT、不正 ELF、CLOEXEC、失敗時旧状態、TLS／signal の reset。
- Runtime 7 件：fork resume、vfork exec 解除、vfork exit 解除、複数子、子 error、kill 起床、終了待機。
- 差分 16 件以上と Rust Command spawn/status/output／起動失敗。stdout・stderr・ExitStatus・errno を比較し、signal status を exit code に混ぜない。
- pid は親子関係の真偽、rusage は配置と非負性などの性質を比べる。時間・PID・アドレスは固定値で比較しない。非決定な出力順はゲスト同期で固定する。除外事項は cases.json に理由付きで記録する。
- ENOENT は VFS 内で発生させる。ホストの実行ファイルをゲスト起動に使用しない。

## Regression

U8 実装後、既存 test 名の正確な filter を確認して次を実行する。ここは U5／U6 への U8 接続変更に伴う回帰検証である。

```sh
cargo test --locked -p paludarium-kernel --lib u5_tests::
cargo test --locked -p paludarium-runtime --lib u5_tests::
cargo test --locked -p paludarium-kernel --lib u6_tests::
cargo test --locked -p paludarium-harness --test diff_u5 u5_ -- --nocapture
cargo test --locked -p paludarium-harness --test diff_u6 u6_ -- --nocapture
```

## Coverage and Quality

Linux の既存全体カバレッジ測定で行 80% 以上を維持する。U8 だけの実行結果を全体カバレッジと呼ばない。ここには Unit 外の全体コマンドを置かず、Build and Test の既存 CI 結果を根拠として記録する。fmt と clippy の変更クレート検査は計画 Step 11、全体 CI は既存ゲートで行う。数値が届かなければ対象ケースを追加し、閾値を下げない。

## Test Data and Doubles

Host は既存 RecordingHost を使い、親子の stdout/stderr と起床を観測する。ファイルは Session の Config.files で VFS に親子 ELF を配置する。プロセスの clone／exec／wait の成功を mock で代用せず、本物の Kernel と Runtime を接続する。native 専用のホストプロセス利用はテスト harness 内に限定する。各 native/emulated ケースに既存 bounded support を基に上限を設け、timeout を失敗として扱う。期待結果はチェックインしない。

## Evidence

native-only 実行を実装前、部品単体を各部品実装後に記録する。コマンド、実行環境、件数、stdout／stderr／status、未検証の理由を code-summary.md に残す。今は計画のため全 U8 テストは未検証。

