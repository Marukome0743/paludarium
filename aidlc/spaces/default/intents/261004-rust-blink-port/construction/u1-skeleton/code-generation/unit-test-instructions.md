# 単体テストの手順（u1-skeleton）

## 今回のStep72：再レビューのMinor 5件の修正

project rootで、採用済みのコマンド（コマンド行は同じ）と回帰テストを実行し、sensorを実行する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/loopback1-next/new_candidate.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/loopback1-next/test_new_candidate.py
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/code-summary.md
```

期待する結果：コマンドはexit 0。回帰テストはexit 0で、Step71の20件に、Step72で足した拒否9件（`new_sha256` と作業コピーの同時の偽、`run_old_chain` のguardのargv・cwd・timeoutの各不一致の3件、論理viewの範囲外、`run_attempt` の不一致、性能の行の対の崩れ、module hashの不一致、jobの欠落・失敗）が加わり、合計29件がすべて期待どおり。sensor 2件はpass。修正後のcheckerは、人がもう一度採用してからcheckpointで実行する。

実行結果（2026-10-17）：コマンドはexit 0（`verification/loopback1-next/run-1792243084087620000-92303/`、checker SHA-256 `a7836f9b880aed05b18d1f283f1cee4dadf79a420b8d8aaa6b3587a6652fc339`、binding-02 SHA-256 `6315b735647c310e5b9ac82291a56652830ff406ee98c43a0a31b2f7db70ecbb`）。回帰テストは29件（test_00〜test_19のStep71の20件、test_20〜test_28のStep72の9件）がすべて期待どおりでexit 0。1回目はtest_24が回帰テスト自身の誤り（比較用の物理bytesを論理viewの中で読んだ）で失敗し、test_24だけを直して再実行した。回帰の一覧は `verification/loopback1-next/README.md` にある。この成功は修正後のcheckerを人が採用する前の実行であり、checkpointでの検証ではない。

## 前回のStep71：新しい正式確認コマンド

製品のテストは追加しない。project rootで、新しいコマンドと旧コマンドを実行し、拒否の回帰を実行する。

```sh
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/loopback1-next/new_candidate.py
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/code-summary.md
```

（新しいcheckerのファイル名は作るときに決め、決めた名前とSHA-256をREADME.mdとcode-summary.mdに書く。拒否の回帰のコマンドも同じREADME.mdに書く。）

期待する結果：新しいコマンドはexit 0。旧コマンドはexit 1で、理由は `compiled source changed`（または mise.toml の違い）。拒否の回帰20件（正の対照1件と拒否19件。計画の拒否の9種類をすべて含む）はすべて期待どおり。sensor 2件はpass。（Step72で訂正：以前は「回帰9種」と書いていたが、9は種類の数で、実際の件数は20件だった。）

## 前回のStep38〜40：FR5.4担当説明の修正

U1の今回の変更はFR5.4のnotesにU5を追加する文書修正のみ。Deferredと他の対応項目を保持する。次の限定検査を実行し、exitと結果を今回のverificationログへ保存する。

```bash
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/traceability.json
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/code-summary.md
```

承認済みcanonical完了検査はUnit checkpointで別途実行する。新しい製品テスト実行ではなく、現行sourceと署名済みCI・実Safariの保存証拠の対応検査である。既存テスト設定と80%下限を維持する。U4/U9の修正と限定コマンドはそれぞれのUnit計画で確定し、ここで検証済みとはしない。

## 今回のStep35〜37：指摘修正と実Safari

CIログ名を修正し、traceabilityの追加60 FR/NFR IDsを要件とUnit割当からOK/Deferred/N/Aで正しく分類して不足0を確認する。既存47項目を保持する。本物のSafariは既存の共有wasmメモリのwait/notify確認を使う。以下のコマンドはU1の対応表とwasmスレッド確認だけを対象とする。

```bash
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/traceability.json
bash spikes/wasm-threads/build.sh
node spikes/wasm-threads/browser-check.mjs safari
```

固定nightlyとmise管理Node実体を使用する。Safariの版、生JSON、crossOriginIsolated、wait/notifyの結果と値42を保存し、5秒以内を合格条件とする。safaridriverのRemote Automationが無効なら有効化を依頼して保留する。WebKitで代替しない。エミュレータ全体のSafari実行、入れ子Worker、共有stdヒープ、fuzzは未検証を保持する。製品変更がなければ既存native CIのbytes一致を再確認し、重い試験を反復しない。

## 現行Step32〜34の記録確認

検証済み：2026-10-08、今回Summary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に現行af9b739d742a9552f44fc1515646c862b19e5de2と103claims/108filesを再照合した。107files一致、既知の非ビルド.gitignore例外のみ。intent直下verification/verify-native-ci.pyはexit0、CI37713953347の7jobsとnative37713953340の4jobs成功・署名済みcommit・全162 application filesを確認した。新しい製品テスト実行はなく、下記exact commandsは不足回収用。全体92.68%とU1対象packages83.04%は保存済みCIの値で、両80%gateを保持する。

未検証：U1各fuzz targetの現行600秒ASan、wasm、実Safari。30秒watchdog、nightly-2026-10-01、各600秒、比較mask、Docker VMM、2フックを維持する。今回の限定sensor結果はverification/step34-sensors.json。47IDs対応は維持し、全requirements fallback60IDs不足という未解決sensor結果をPASSへ読み替えない。

## 履歴：Step29〜31の記録確認（4d52時点）

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

## Step35〜37の追加確認

Summary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、共有要件60IDsを追加分類し107IDs/107対応へ更新した。既存47BR/詳細NFRの意味を保持する。traceability検査の実結果はverification/step35-traceability.jsonおよびstep37-sensors.json。Safari単独spikeはverification/safari-local-20261008-pass.jsonの実Safari27.0.1でexit0、値42、total216ms。他ブラウザ・fuzzの過去結果は今回の新実行に数えない。

canonical verify-native-ci.pyはSafari報告更新でexit1。全162 application filesの補助byte proofは160一致、差分は既知.gitignoreと報告docs/reports/wasm-threads.mdのみ。source/test/build/CIは不変だが、正式検証・完了確認は未完了。80%/30秒/nightly/各600秒を保持し、検証器の例外を独断で増やさない。

検証済み：人が選択した完了検査 `python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。元のverify-native-ci.pyは保持し、署名済みCIと異なるSafari文書・実測証拠の厳密hash対応だけを新検査で確認した。CI7jobs/native4jobs成功、全162 tracked application filesをaf9bへ照合し、既知.gitignoreと承認済みSafari報告以外の差分を認めない。実行ログはverification/step37-approved-native-ci.log。元の検査exit1は履歴であり、今回選択済み検査の成功と区別する。独立レビュー・Unit完了確認は引き続き未完了。

## 追加Step41〜43：SHA共有CPU前提修復の限定検証

以下は追加範囲の実行手順であり、元の履歴を現在の合格へ変更しない。命令のnative期待結果を毎CIで実装前に取得し、その後共有CPUを修復する。decoder接続等内部layerのテストは実装後というTesting Contractを保持する。計画/内容確認後に実行する。現在未作成の新契約ケースは検証済みと扱わない。

### native観測と関係テスト

native x86-64 Linuxで固定nightlyを使用し、observer全行と実CPU profile/CPUIDを保存する。native-only入口は収集だけでemulator合格を示さない。

```bash
cargo +nightly-2026-10-01 test --locked -p paludarium-harness --test diff_u3 u3_native_observation -- --ignored --exact --nocapture
```

修復後のMac単体とLinux差分は既存の実入口を使う。追加するSHA契約ケースの予定filterは`u3_tests::sha_memory_contract_`、3命令×2非整列条件の最低6ケースで0件は失敗。profile情報は毎CIのraw CPUID/CPU情報と対応させ、観測済みAMD差異6行以外の不一致を除外しない。

```bash
/Users/mutoakio/.cargo/bin/cargo +nightly-2026-10-01 test --locked -p paludarium-cpu --lib u3_tests:: -- --nocapture
/Users/mutoakio/.cargo/bin/cargo +nightly-2026-10-01 test --locked -p paludarium-decoder --lib u3_tests:: -- --nocapture
cargo +nightly-2026-10-01 test --locked -p paludarium-harness --test diff_u3 u3_fresh_native_differential -- --exact --nocapture
cargo +nightly-2026-10-01 test --locked -p paludarium-harness --test diff_u1 --test diff_u2 --test parallel_u2 --test diff_u4 --test diff_u9 --test diff_u3 -- --nocapture
```

### coverageとCI品質

`U1_PACKAGES`はtypes/decoder/mmu/cpu/loader/vfs/kernel/host/jit/runtime/paludariumの既存11packagesを列挙する。Harnessはfresh native差分を測定に含めるための実行依存であり、そのtest crateだけを分母から外す。元のU1 production filesと80% floorは維持する。workspace・U1・U3測定のcommandと各分母/実値を別々に記録し、失敗を上書きしない。

```bash
U1_PACKAGES='-p paludarium-types -p paludarium-decoder -p paludarium-mmu -p paludarium-cpu -p paludarium-loader -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-jit -p paludarium-runtime -p paludarium'
RUST_TEST_THREADS=1 cargo +nightly-2026-10-01 llvm-cov --locked --workspace --fail-under-lines 80
RUST_TEST_THREADS=1 cargo +nightly-2026-10-01 llvm-cov --locked $U1_PACKAGES -p paludarium-harness --ignore-filename-regex 'paludarium-harness/' --fail-under-lines 80
RUST_TEST_THREADS=1 cargo +nightly-2026-10-01 llvm-cov --locked -p paludarium-cpu -p paludarium-decoder -p paludarium-harness --lib --test diff_u3 --ignore-filename-regex 'paludarium-(types|mmu|host|kernel|loader|vfs|jit|runtime|harness)/' --fail-under-lines 80 --lcov --output-path target/u3-coverage.lcov
cargo +nightly-2026-10-01 fmt --all --check
cargo +nightly-2026-10-01 fmt --check --manifest-path fuzz/Cargo.toml
cargo +nightly-2026-10-01 clippy --locked --workspace --all-targets -- -D warnings
cargo deny --locked check
```

3OSは既存CIの11packages単体とHarness lib、Windows既存NativeFs回帰を実行する。action SHA固定・read-only token・署名jj push/connector Verifiedを維持する。isolated workspaceの承認範囲だけを同期し、user dirty mainを一括commitしない。pushはhost権限から行う。新しい完了checker commandは別途人の選択後だけ実行する。

### 現行closureのASan/LSan

既存isolated `.github/workflows/u2-production-sanitizers.yml` の4targetsと `u3-shared-sanitizers.yml` の3targetsを同じ最終製品bytesで実行する。container `/work`、fixed nightly、cargo-fuzz0.13.2、最小C2回exit0、seed/corpus・raw exit・source前後・binary/symbolsを維持する。各matrix targetに対する実commandは以下。

```bash
export LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp
export ASAN_OPTIONS=detect_leaks=1
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address cpu_u2 -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048 -max_len=4096
cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address mmu_u2 -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048 -max_len=4608
for target in decode load_elf syscall_args vfs_paths mmu_ops; do
  cargo +nightly-2026-10-01 fuzz run --fuzz-dir fuzz --sanitizer address "$target" -- -seed=1 -max_total_time=600 -timeout=30 -rss_limit_mb=2048
done
```

各targetは独立matrix jobでもよい。途中同期・競合buildをせず、失敗しても他targetの実測を保存する。上記loopは各targetのexact argsを示し、既存30分jobへ5対象50分をまとめない。旧601秒証拠は旧bytesの履歴として保持する。

### 本番wasm・Node・実Safari

最終署名CIの既存production jobで以下を実行し、同module/native JSONをartifactへ保存する。build-wasm.shは固定nightly/std共有heap設定を含む既存scriptである。

```bash
python3 packages/paludarium-wasm/tests/generate-guests.py --check
python3 scripts/wasm-native-guests.py > target/production-wasm-evidence/native-results.json
bash scripts/build-wasm.sh
node --test packages/paludarium-wasm/tests/import-check.mjs
node packages/paludarium-wasm/tests/node-check.mjs packages/paludarium-wasm/paludarium.wasm target/production-wasm-evidence/native-results.json
```

Safariは既存phase runner `construction/u9-terminal-io/code-generation/verification/step11-safari-diagnostic.mjs` を使用する。Safariを完全終了して手動再起動せずdriverにautomation起動させる。`SAFARI_STATIC_ROOT`はrepo、`SAFARI_ENTRY_PATH`は既存 `/packages/paludarium-wasm/tests/index.html?wasm=<最終CI artifactのrepo内URL>&native=<同artifact native JSON URL>`、`SAFARI_REPORT_KEY=__paludariumProductionReport`、`SAFARI_DRIVER_ARGS=["--diagnose","--port","{port}"]`。artifact URLは取得後に確定するため旧headのURLを固定しない。

```bash
/Users/mutoakio/.local/share/mise/installs/node/24.21.0/bin/node aidlc/spaces/default/intents/261004-rust-blink-port/construction/u9-terminal-io/code-generation/verification/step11-safari-diagnostic.mjs
```

runnerの28秒AbortController/cleanup2秒、外側30秒process-group kill/reapを保持する。全21cases、browser version、crossOriginIsolated/sharedMemory/cleanup、最終module/native/source SHAを確認し、以前のSafari成功を修正後moduleへ再ラベルしない。mise node実体のversion/pathは実行時にも確認する。
## 今回の承認復旧と停止原因の検証（Step 44）

この節は以前の承認復旧の履歴。今回の実行は以下「旧確認スクリプトの分離修復」に従う。

## 旧確認スクリプトの分離修復（Steps44〜47の履歴）

旧U12 checkerを変更しない。旧342入力を署名a275bd3dへ結び付ける414snapshotと支援由来を検査し、旧mainの全predicateをその歴史的viewで実行する。現在workspaceの検査とは明確に分離する。旧sourceの復元、hashの任意例外、未完成U13成功の主張を禁止する。

現行U1は同一署名sourceで必要Linux job/stepが成功した原本だけを採用する。CI run全体が失敗していても、必要jobの実command・exit・skipなし件数・入力closure・compiler・guest/binary・分母の完全一致が必須。現時点で適用可能性は未検証。共有HostとRuntime変更後の動作をhashだけから推定しない。完全適用できない場合、必要なU1観測をfresh Linuxで再実行する。以下はその実在入口（新CIの追加/publicationは限定差分を先にrootへ提示）。

```sh
cargo test --locked -p paludarium-harness --test diff_u1 -- --nocapture
```

diff_u1はhello_c、hello_rs、hello_rs_with_argumentsと13命令ケースの計16。Harnessは毎実行fresh nativeとemulatorのstdout/stderr/exitを比較する。guestごと30秒watchdogと比較maskを保持する。実際のtests/guests/build.sh、hello-rs toolchain/lock、Harness supportと現在の11package closureを監査してから測定する。

coverageは既存 `U1_PACKAGES` のtypes/decoder/mmu/cpu/loader/vfs/kernel/host/jit/runtime/paludarium、Harness差分実行依存、既存Harnessだけの分母除外を維持する。`.github/workflows/u13-quality.yml` の `U1 package line coverage >= 80%` のcommand・profile・fresh U3 replay入力をそのまま監査する。分母縮小やmissing fileのignore追加は禁止。現在必要な全sourceのsigned bindingを取り、実測と現在bytesが一致しない場合は旧値を使用しない。

回帰は計18件：正常2系統と、snapshot改変/欠落/余分/symlink、checker改変、現行改変、署名不一致、CI head相違、failed/skip/0件、guest相違、compiler相違、coverage分母欠落、80%未達、30秒超過、旧証拠の現行誤用、artifact digest相違を拒否する16境界。前者のfailed/skip/0件は一つのパラメータ化境界で各variantを実行する。原本/各exitを保存し、全checker診断をレビュー前に完走させる。

新command候補は `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-source-bound.py`。正式実行はrootによる人のcommand承認後。独立レビュー前にsource/produces/証拠書込を終了し、required-sections/traceabilityを成功確認する。U13の32件実guest／独立16件coverage・全29ジョブは後続の未完了条件として保持する。

全Unitやり直し後の今回の実行は計画Step 45。内容確認と新しい計画承認を取得してから、既存Unit限定検査とsource/CI照合を行い、標準のレビューとcheckpointで次のUnitへ進めるか検証する。旧attemptの承認・レビューを今回のものと扱わない。新たな検査コマンドの選択が必要なら実行前に提示する。

合格条件は質問表示だけではなく、同一セッションで現在の計画承認→brief成功→正式レビュー要求成功→reviewer結果記録→次checkpointへの遷移が完了し、再開でも不必要な承認再要求や無進行ループが起きないこと。各標準CLI呼出しの生出力・終了コード・runtime版・日時をverification記録へ保存する。失敗した段階を明示する。並行チャットのID競合と他Unitの承認失効は今回の成功だけで解消したと判断しない。

読み取り診断は `aidlc doctor --verbose` とdoctorが指定するhooks-healthの確認。承認後の入口は `aidlc engine testing-posture brief --unit u1-skeleton`。レビュー要求・記録・checkpointは次の標準指示が返すUnitとiterationに従い、値を推測して記録しない。guard strictを維持し、失敗を隠す修正をしない。

既存の検査手順・品質下限を保持する。計画承認前に製品変更を開始しない。承認後、標準CLIの `aidlc engine testing-posture brief --unit u1-skeleton` が現在の計画へ結び付くことを確認する。これは承認経路の確認であり、製品テストの合格証拠ではない。

## 消失した旧JS測定フォルダーの修復（今回Steps48〜50）

旧U12検査の `step10_current_validation.py:185` は `/private/tmp/paludarium-u2-mmu-4608` を参照する。旧binding342入力とV8原本83JSONのURLに結び付くため、単なるROOT変更や生JSON書換えを行わない。この計画が指定する一時先だけを、hash完全一致する保存済みsnapshotから検証時に再構成する。既存先は非symlink・全inventory・全bytes一致の場合だけ利用し、上書き・競合・未確認sourceの混入を拒否する。保存原本と製品を変更しない。

既存33回帰は次のU1専用入口で保持する。

```sh
python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification -p test_source_bound_validation.py
```

新helperの8境界は次の専用入口で実行する。テストfixtureは同verification配下へ隔離し、実測用の旧一時先や利用者のファイルをfixtureとして破壊しない。

```sh
python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification -p test_historical_js_workspace.py
```

旧Node binary・collector・原本hashを維持し、V8原本83JSONの再集計が旧reportに完全一致することを全スクリプト診断で確認する。旧全predicateと現行362入力・hello実終了・CI原本検査を省略しない。再集計を新しい実guest実行・新coverage測定としない。正式検査・独立レビュー後の最終commandは、既に承認された `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-source-bound.py` を使用し、実行結果がexit0かつ証拠不変の場合だけU1完了承認へ進む。初回native SIGSEGVの原因と並行セッションID競合の完全解消は未検証のまま明記する。

現行sourceと既存の署名済みCIを照合し、製品検査は既存の承認済みコマンドを使用する。新しい確認コマンドが必要な場合は実行前に提示する。再レビューとplan approval guardが再度食い違う場合は拒否出力を保存する。過去のテスト件数を今回の実行件数へ読み替えず、後続Unitの未検証項目を合格と扱わない。

## U14共有変更後の確認更新（今回Steps51〜54）

今回の変更はU1の確認補助・回帰と記録だけ。旧確認スクリプトを保持し、旧362／361入力に結び付いた全検査を各旧署名viewで実行する。新確認スクリプトは旧全検査と現行署名headの必須U1実測を両方検査する。承認済み39ファイルと後続の書式2ファイルは別manifestで監査し、現行input inventoryを依存closureから確定する。

実closureは署名CIの入力receiptから製品・guest・test・build・config・lockを列挙し、実行したU1 workflowから参照されるlocal reusable workflowを再帰で加える。過去の非参照workflowを今回の実行依存と推定しない。これらの差分は削除せず、signed／local SHAと非参照根拠を監査へ保存する。reusable workflowの欠落・循環・範囲外・改変・未結合外部参照を拒否する補助6回帰を、既存18境界へ追加した。新入口の実テスト数は24、従来33＋8と合わせ65件。Testing Contractと原本検査の下限を変更しない。

既存33回帰と8再構成境界は上記2つのU1専用入口で保持する。新18境界の入口は次のとおり。

```sh
python3 -B -m unittest discover -s aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification -p test_u14_source_bound_validation.py
```

runnerは既存Python unittestを使い、最初に既存入口を確認する。fixtureはU1 verification配下に隔離し、署名source・証拠原本・利用者の一時先へ書き込まない。正常2系統と16拒否境界を計画Step53に対応させ、欠落や改変を無視するmockを使わない。

現行U1の必須実測は、同じ署名headのfresh Linux hello3件のstdout／stderr／実終了0、diff_u1全16件、固定11packageとworkspaceのcoverage各80%以上、3OS品質。CIのguest、両lock、実compiler、全入力と原本digestを照合し、failed／skip／0件を合格扱いしない。共有wasm4環境各28件と13対象各600秒ASan／LSanは依存closureが一致する範囲を記録し、MMU最大4608バイトとguest30秒を保持する。未完了の性能測定やU14完成をU1合格へ混ぜない。

`python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u14-source-bound.py` は作成予定の新確認入口であり、現時点では正式コマンド承認を受けていない。レビュー前の全診断は計画Step54の診断として記録し、独立レビュー後に別途正式コマンド承認を取得する。旧検査・初回失敗原本・既存native SIGSEGV指摘を保持する。U1完了承認後は正式手順でU14へ戻る。（上記はSteps51〜54時点の記述であり、歴史検証手順として残す。現在の正式コマンドは末尾「今回Steps67〜69：現在のsourceでの正式検証コマンド」節を参照。）

## 今回Steps55〜58：証拠参照とnative SIGSEGVの追加修正

既存Python74回帰とdecoder31／JIT39件の成功・旧原本を保持する。traceabilityの現行参照訂正では107要件の分類とtargetを完全比較し、旧文脈の保存、署名head／CI run／実行bindingとsanitizer bindingの一致を正常・拒否7境界で検査する。実装後のテスト入口と実コマンドは成果物へ記録する。

native原因調査では保存された失敗ELFを優先し、ELF hash・compiler・失敗CI条件と今回条件の差を先に列挙する。Linux実機で1実行30秒・最大100反復、native実終了・signal・fault RIP／レジスタ／stackと逆アセンブルを保存する。初回coverage相当と単独起動、通常ASLRと補助配置比較を区別する。ELF欠落・再現なし・診断ツール失敗は未検証として記録し、失敗原本を上書きしない。失敗に対応する最小回帰を修正前に失敗・修正後に成功として確認する。製品／fixture修正が必要なら具体的差分の承認を先に得る。

変更後の実行依存を監査し、必要範囲のU1 hello実終了・全16差分・U2境界・固定coverage80%以上・3OS品質を再実行する。13 ASan/LSanは実compiler・全依存・設定一致の場合のみ保存済み601秒証拠を再利用し、不一致対象は各600秒実行する。MMU最大4608バイト、比較mask、guest30秒、測定分母は維持する。現行承認済みcheckerはverify-current-u1-u14-decoder-fixed.pyであり、文書更新後の正式再検証の適用可否を調べる。変更する場合は新コマンドの正式承認後に実行する。単なる有限再成功をSIGSEGV原因解消の証明へ代用しない。

## 今回Steps63〜66：全品質CIを成功させる検査

Windowsのsymlink交換とブラウザHTTP二重応答を原ログ・同一署名ソースで再現し、原因を製品／fixture／サーバー／設定へ分類する。修正前失敗と修正後成功を対応する回帰で確認する。Windows実機で範囲外sentinel不変・交換発生・30秒・有限反復・cleanupを維持し、HTTPは正常／切断／同時要求／エラー経路の終端応答を確認する。失敗のskip・黙殺・閾値低下は行わない。

具体的送信差分の承認後、同一署名headの全品質CIを実行し、Windows・Firefox・本物Safariを含む全必須ジョブの成功と原本を照合する。既存guest全ケース・固定coverage80%・比較条件・strict guardを維持する。変更依存のU1比較／coverage／ASanは一致範囲のみ再利用し、不一致対象は契約どおり実行する。旧全checkerを保持した確認更新には失敗／skip／head違い／原本改変の拒否回帰を追加し、正式検査・独立レビュー・承認済み最終コマンドの検証を経る。初回core欠落・U14性能と既知panic・ID保証は別の未解決事項として保持する。

## 追加Steps59〜62：16bit FRAMEのscratch stackとnative境界

順序は失敗原本／算術境界の確認、修正前の境界失敗、fixture限定修正、同じ境界の成功、fresh native／emulator全比較、既存回帰／品質、証拠binding、正式検査／独立レビュー／最終確認とする。今回の具体化は既存Step57の「変更範囲の承認後に修正する」に対応し、ユーザーのfixture限定修正承認を保持する。正式エンジンの進行指示に従って実装へ移る。

W=2だけ64KiB整列scratch stack中央を使い、ENTER直前low16 RSP=0x7c00／旧RBP=0x7e00／frame temp=0x7bfeとする。最大N31のchain読取とpush／local領域が同mapped window内にあることを検査する。W=8の元stack、既存17 FRAME、全prefix／XLAT／flags、比較maskを維持する。RBP=RSP−2だけの修正はN31のBP wrapが残るため採用しない。

新境界guestは元stack low16の0x0000／0x0001／0x0002／0x01ff／0xfdff／0xfe00／0xffffの7配置から全16bit N=0／1／2／31、LEAVE、prefixを実行する。独立wrapperの上下mapping・caller RSP／RBP／return address復元を検査し、同じframe実装を再利用する。nativeとemulatorで全stdout／stderr／exitを比較する。修正前の誤windowは算術で検出し、旧LEAVEによるrunnerの無条件クラッシュを回帰成功条件にしない。

Linux実機の同一署名ソースで修正後guestをfresh buildし、通常ASLRのnative最大100回・各30秒以内、関連diff_u2、新guest、既存diff_u1全16件とhello6実終了0を検査する。固定11package／workspace coverage各80%以上、3OS品質を確認する。既存74＋参照7＋診断回帰を保持し、fixture修正に対応した境界を追加する。source／ELF hash、両lock、実compiler、実exit、原stdout／stderrを保存する。

共有wasm／13 ASan／LSanはcompiler・全依存・設定一致を監査し、一致範囲だけ再利用する。不一致対象は各600秒、MMU最大4608 bytesで再実行する。測定対象・80%下限・比較mask・strict guardを維持する。旧全checker検査を残して新旧入力・publication・bindingを厳密に分離し、必要な新コマンドは独立レビューと別承認後に正式実行する。初回faultの直接core証明欠落と今回の独立再現を区別し、U14未完了をU1修正成功で合格扱いしない。

## 今回Steps67〜69：現在のsourceでの正式検証コマンド

人が2026-10-16T12:32:15ZにApproveで採用したConstruction Verification Command（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）：

```text
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py
```

引数なしでプロジェクト直下から実行し、排他的な `verification/r05-r11-repair-01/formal-candidate-<time_ns>-<pid>/` に子4件（old_predicates.py／current_semantics.py／package_semantics.py／old_predicates.py）のargv・exit・timeout・stdout/stderr原bytesとSHAを保存する。`binding-v4.json` のSHA256 `1df659288e5dc8ed7962b6c43dae6df3fbf32779562f34f3caf0e2734891f7d7` をプログラム内の固定値と一致要求し、保存済み証拠の純粋再解析だけを行う。guest・旧695秒chain・性能測定・CI・公開処理は起動しない。互換検証器（`verification/preview-20261015-update/compatibility.py`）は `.gitignore` の追加を `aidlc/active-memory/`・`aidlc/.aidlc-request-text/` の2行に限定し、それ以外の差分では `ignore has other changes` で拒否する。

実行原本（いずれもstdoutは `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`。Unit完了・U15別配布Wasm受理の証拠ではない）：

- checkpoint verify 43ea67bc-2049-4886-8246-b4167fecfdde（2026-10-16T12:41:42Z〜12:42:17Z、exit 0）：`formal-candidate-1792154502657025000-40216/`
- Claude Code harness追加で `.gitignore` に3行目 `.claude/settings.local.json` が入った状態（exit 1、`ignore has other changes`）：`formal-candidate-1792157037871198000-68539/refusal.json`。失敗原本として保持する。
- 冗長な3行目を削除し許容2行だけに戻した後（2026-10-16T13:33Z、exit 0）：`formal-candidate-1792157659313715000-72179/`

保存される子4件の原本（`formal-candidate-1792157659313715000-72179/<n>.receipt.json` から引用。argvは `python3 -B <script> <出力先>/<n>-<script>.result.json` の形で、python3実体は上の正式コマンドと同じmise 3.15.0のもの。stderr SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` は空bytesを示す）：

| n | script | exit | timeout | stdout SHA256 | stderr SHA256 |
|---|---|---|---|---|---|
| 0 | `old_predicates.py` | 0 | false | `759e640f6253426a44ecb8b7beac30f77ba4ff44e3e3b8e416c537aab3a0d4cb` | 空 |
| 1 | `current_semantics.py` | 0 | false | `89d4566e5d89f52ed66f4d7c27d20ace2ce232f36686f4b4cef0efb5b0794be4` | 空 |
| 2 | `package_semantics.py` | 0 | false | `b638fc309c218c20e418f406448bfe5c6ba07fb1d2841cee86519642f3ac5272` | 空 |
| 3 | `old_predicates.py` | 0 | false | `759e640f6253426a44ecb8b7beac30f77ba4ff44e3e3b8e416c537aab3a0d4cb` | 空 |

`formal-candidate-1792154502657025000-40216/` の子4件も同じexit 0・timeout false・同一のstdout／stderr SHA256である。拒否原本 `formal-candidate-1792157037871198000-68539/0.receipt.json` は子0（old_predicates.py）がexit 1、stdout空、stderr SHA256 `8425610ff9cf44c50c583e30e869f45b3ab74e7df7dd87aa8a51f89ee59f9707`（`compatibility.py` の `ignore has other changes`）で、子1〜3は起動されていない。

旧コマンド（`verification/preview-20261015-update/verify-compatibility.py` によるcheckpoint verify 894ff252、2026-10-16T10:14Z、exit 0。および `verify-current-u1-u14-source-bound.py` 等の各時点の確認入口）は歴史検証手順として上の各節に残す。上の「作成予定であり、現時点では正式コマンド承認を受けていない」という記述はその時点（Steps51〜54）の記録であり、現在の正式コマンドは本節のものである。

mise設定は署名208fd965のpreview13からpreview15へ変わっている。本コマンドは旧consumer-v3へ旧mise bytesの読取専用viewを与えて旧predicateを再照合するため、`source_compatibility: PASS` は現行preview15設定でのconsumer-v3正式実行を示さない。その実行は未検証のまま保持する。手元macOSの `cargo test --locked -p paludarium-harness --test diff_u1` は0件・exit 0であり、Linuxの16件の証拠とは呼ばない。

標準経路での再実行（Step70、R-15対応）：Steps67〜69の記録修正後、checkpoint verify `d97dcbec-3dfe-4b71-8871-361aceb6a419` として本コマンドを再実行し、2026-10-16T18:28:37Z〜18:29:13Zにexit 0、stdout `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、出力先 `formal-candidate-1792175317098659000-58394/` を得た（proofは `.aidlc-construction-checkpoints/u1-skeleton/skeleton.json`、`CHECKPOINT_VERIFICATION_RECORDED` を監査に記録）。traceability.jsonは `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -I` によるJSON parseがexit 0で、`coverage` 107件・`verification_context_history` 4件を確認した。独立レビュー（iteration 1、2026-10-16T18:21:33Z）は同じ3コマンドをhookの拒否で実行できず保存原本の直接読取で判定したため、この再実行を標準経路の結果として区別して記録する。手元macOSで観測した `diff_u1` 0件はLinux証拠と呼ばない。これらもUnit完了・U15別配布Wasm受理の証拠ではない。

