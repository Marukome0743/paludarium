# U6 テスト手順

## 今回：確かめ直しの指摘を記録で直す（2026-10-19）

記録だけを直すので、新しい試験はない。project rootで正式sensor 2件を実行する。

```sh
aidlc engine sensor-required-sections --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u6-events-sockets/code-generation/code-summary.md
aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u6-events-sockets/code-generation/traceability.json
```

期待する結果：required-sectionsはpass、traceabilityはpass・findings 0（NFR8・NFR9のtargetを今のファイルに替えた後）。checkpointでは今の正式な確認コマンド（`verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`、人が2026-10-19に採用）を実行する。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べる（`entry-f.py` の `verify_working_copy`）ので、exit 0になる想定で、結果はcheckpointの記録が持つ。

今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`。下の節のコマンド・toolchain・compiler・「現在の承認済み最終確認」は、それぞれの時点のもの（head 11c033c7 以前）である。下の節にあるU6だけの測定（`scripts/u6-coverage.py` の固定9ファイルのcoverage、`u6-check.mjs`・`scripts/u6-wasm-guests.py` のproduction wasmのNode/Safari 102件、`u6_tests::` の49件・ignored 0の件数）は、27d05de1でU6のworkflowが消えてから、どのworkflowでも測られていない。

## 履歴：追加検証（Steps16〜18）（作成時の見出しは「承認された追加検証（Steps16〜18）」）

u6-check.mjsの旧総数assert一行を103→102に整合し、現行共有20件とU6の82件をID集合で確認する。ケース・期待値・比較条件を削除しない。新専用診断CI/helperとこの一行変更を含む全入力、両lock、実使用compiler・ツール版・flagsのbefore/after/current一致を保存する。製品Rustとguest fixtureは変更しない。

同じ署名済み現行ソースのLinuxでfresh native84件＋Tokio10反復を比較し、既存9製品ファイルのcoverage分母規則と80%下限を維持する。3OSで `cargo test --locked -p paludarium-kernel --lib u6_tests::` の49件・ignored0、fmt、Clippy警告エラー、依存4検査の実exitを保存する。kernel_events_u6とkernel_sockets_u6は現行実使用nightlyで各600秒以上ASan/LSanを実行し、instrumentation・runtime・flags・依存閉包・lock・原本を保存する。古いcompilerでの成功を代替にしない。

同CI生成production wasmをNodeと本物Safariで実行し、共有20＋非threaded U6 82の全102ケースを同じfresh native結果へ照合する。module hash、ID集合、COOP/COEP、sharedMemory、停止・cleanup、実exitと生ログを記録する。C66/Tokioのwasm guest WorkerはU11境界と区別する。30秒watchdog・kill/reap・比較mask・測定分母を維持し、失敗・0件・skipを合格扱いしない。正式検査と独立レビュー後、新最終確認コマンドは変更承認を得て実行する。

## 履歴：再確認（Steps13〜15）（作成時の見出しは「今回の再確認（Steps13〜15）」）

下記Steps1〜12の手順は実装時の履歴として保持する。今回製品・fixture・CIを変更せず、現行ソース・両lock・実使用compiler・設定を旧e33cfbb4の439入力と31担当leafへ照合する。有限U6内部テストは `cargo test --locked -p paludarium-kernel --lib u6_tests::` を実行し、旧49件との差、ignored、実exitとログを保存する。0件やskipを合格にしない。

Linux fresh native84差分とTokio10反復、固定9製品ファイルcoverage80%、3OS、kernel_events_u6/kernel_sockets_u6各600秒ASan/LSan、本番Node/本物Safari各103件は依存ソース・両lock・実使用compiler・設定・対象範囲が一致する証拠のみ再利用する。以前の21共有ケースと非threaded U6 82件を区別し、C66やTokioのwasmゲストWorkerはU11境界と明記する。必要な追加検証は具体的実行案として提示し、その範囲の承認後に実行する。固定分母・比較mask・30秒watchdog・kill/reap・80%下限を維持する。

正式検査では要件原本と独立した担当割当を照合し、他Unitと集約要件をDeferred/N/Aに分類する。実装済みでない要件をOKにしない。現在の承認済み最終確認は `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3-u5.py`。新U6証拠のためコマンド変更が必要な場合は候補を準備し、新しい承認後に実行する。

## Runner and ordering

（この節以下のtoolchainの版とコマンドはその時点のもの。今は `rust-toolchain.toml` の `nightly-2026-10-11`。先頭の「今回」の節を参照。）

Testing Contractはcustom。runner readiness→guest/syscall finite native観測→製品実装→内部単体test-afterを守る。最初の実行testより前にbuild/script/harness filterを準備して次のunit-scopedコマンドを実行可能にする。以下の新規ファイル/targetはStep2/10で作成する予定であり、現時点で実行済みとは主張しない。

```text
bash tests/guests/u6/build.sh target/guests/u6
python3 scripts/u6-runner-test.py
python3 scripts/u6-native-observe.py --out target/u6-native-first
cargo test --locked -p paludarium-kernel --lib u6_tests::
cargo test --locked -p paludarium-harness --test diff_u6 -- --nocapture
```

0test成功は合格にしない。static-musl U6 tokio/UnixStream guestはbuild.shで固定依存Cargo.lockから生成し、同じdiff_u6に含める。製品変更前のfixture-only Linux CI全native観測と親のgoが必須。追加APIが必要になった場合もそのケースを先に観測する。親がSCM/pushと外部CI収集を担当する。

## Finite cases and test data

native48ケース以上をStep3で一覧化しCOMPARISON.mdへ固定する。対象はeventfd通常/semaphore counter、ABI長/値/overflow、blocking/NONBLOCK、epoll LT/ET/ONESHOT rearm、ADD/MOD/DEL/invalid fd/self/nestingの必要範囲、data64/maxevents/公平性、OFD dup/close/reuse/最後の参照、socketpair双方向/partial IO/EOF/shutdown/EPIPE/flags、signal mask/handler/timeout/killと通知競合。network EAFNOSUPPORTは承認済みpolicy例外としてnative成功との差分を混ぜず別の拒否assertionを持つ。その他の対応外型/flagsは明示表とテストを持つ。

毎CIでx86-64 Linuxからfresh期待を生成し、保存oracleで代用しない。raw stdout/stderr/exit/timeout、guest binary hash、manifest/JSONを保存する。fd/TID/pid/時刻/アドレスは関係・区間boolへ正規化し、順不同イベント集合は順序非依存で比較する。未定義値は比較対象から除外して理由を表にする。全process30秒watchdog、process-group kill/reap、case単位有限timeoutを保持する。

## Internal unit and boundary integration

Kernel events/eventfd、socket endpoints、epoll、fd/readiness lifetimeの4境界に各8test以上、同期統合8test以上。制御可能なRecordingHost/WaitTokenとchannel/barrierを使い、登録前通知、Host entry後変更、owner ack直後通知、process drain、mask/実signal/group終了/metadata-only、timeout/wake競合を確定する。wall-clock sleepだけで順序を推定しない。MMU/fd/event lockを保持したHost待機がないことと、bad guest pointers/length/flagsでpanicしないことを検査する。通常file/stdio/U5待機の回帰を保持する。

```text
cargo test --locked -p paludarium-kernel --lib u6_tests::
cargo test --locked -p paludarium-harness --test diff_u6 -- --nocapture
```

共有sourceの先行Unit回帰と3OS品質は親がU6 CI gateとして収集する。上記unit testコマンドをbare workspace testへ置き換えず、Build and TestでUnitごとの全workspace反復を避ける。

## Coverage and fuzz

Step1でU6変更製品file一覧を固定しscripts/u6-coverage.pyが分母とfloor80を検査する。native Linuxでinstrumented U6 test/diffと対象guestを実行したLCOVから測定する。test-only/guest/CIファイルを製品分母へ混ぜず、未実行行を削って閾値を通さない。

```text
cargo llvm-cov --locked -p paludarium-kernel --lib --lcov --output-path target/u6-coverage.lcov -- u6_tests::
python3 scripts/u6-coverage.py --lcov target/u6-coverage.lcov --out target/u6-coverage.json
cargo check --locked --manifest-path fuzz/Cargo.toml --bin kernel_events_u6 --bin kernel_sockets_u6
cargo fuzz run kernel_events_u6 --sanitizer address -- -max_total_time=600
cargo fuzz run kernel_sockets_u6 --sanitizer address -- -max_total_time=600
```

fuzzはfuzz/ディレクトリをworkdirにして固定nightly/Linuxで実行し、LSanを有効にする。cargo-fuzzが--locked非対応でも先行check --lockedとCargo.lock before/after/current hash、exit/raw/toolchain/start/endをartifactへ保存する。各600秒以上、exit0、ASan/LSan/panic/tracer異常なしを原本で確認する。失敗したら原因を修正し対象・時間・下限を緩めない。

## Production module and evidence

製品Launcherの限定U6回帰をpackages/paludarium-wasm/tests/u6-check.mjsへ追加し、Nodeと実Safariで同じcase集合を実行する。各環境の具体driver起動パラメータはStep11で現artifactに合わせて記録し、実行前に確定する。WebKit代替を実Safariと呼ばない。U11 guest Worker未接続境界と非threaded U6回帰を明示する。

```text
node packages/paludarium-wasm/tests/u6-check.mjs --wasm target/u6-production/paludarium.wasm --native target/u6-production/native-results.json
python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u6-events-sockets.py
```

read-only checkerはStep12で作成する予定。same-head signed commit、run/job原本、全case raw、固定分母80%、両600秒sanitizer/lock、現module Node/Safari report、source-manifestの全leafと先行証拠保存を照合する。全traceability notes/Markdownが同じ実測値を指すことも検査する。原本未取得時はpass=false。3OS fmt/clippy warnings-as-errors/tests、crates.io/license/vulnerability、SHA-pinned ActionsをU6 CI gate原本で確認する。成功済み未変更の重い検証を理由なく繰り返さない。
