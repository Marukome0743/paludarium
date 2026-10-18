# U5 テスト手順

## 今回Step33：変更がないことの再確認

新しいテスト・CIの実行はない。project rootで、U5のsource-manifestの全ファイルがe4f84768と同じであることを確かめる（読み取りだけ）。

```sh
git diff --quiet e4f847686c8dccb1bc899de88c63a4b3b2a8dd1d -- $(python3 -I -c "import json;print(' '.join(w['path'] for w in json.load(open('aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/source-manifest.json'))['writes']))")
```

期待する結果：exit 0（差なし）。checkpointでは今の正式確認コマンド `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` がexit 0になる。

## 前回の限定修正（Steps29〜32）

旧署名head62611f2556c4caf1470a7eb4471269d92611db6eの入力viewで旧checkerの全検査を保持し、現workspaceは別に厳密照合する。mise.tomlのAI-DLC version 2.11.0→2.11.1-preview.20261012.1だけを許す。bun、取得元、asset指定、他設定、製品source、両lock、compilerは変更を拒否する。実workspace・旧checker・旧原本・AI-DLC本体・guardを変更しない。

正常2件と想定外version・他tool・asset・source・lock変更、欠落、余分な入力、symlink、旧現行混同、digest改変を含む12境界以上を新helperの回帰で検査する。既存回帰と全スクリプト診断後に正式sensorと独立レビューへ進む。全mise.toml除外や旧原本のhash再基準化は禁止する。診断を正式完了証拠へ代用せず、新最終確認コマンドを別途承認後に実行する。新しい重い試験と外部送信は追加せず、coverage80%・guest30秒・strictを維持する。

## 今回の記録更新（Steps26〜28）

Testing Contractを正式renderで更新し、製品・既存試験を保持する。現行共有ソースと署名済みCI原本を照合し、旧U5専用のLinux43差分・固定13ファイルcoverage・threads/futexの記録を現行の新規実行へ読み替えない。既存の命令・固定対象・80%下限・30秒制限を維持する。正式検査と独立再レビュー後、現在承認済みの最終確認コマンドで原本を検査する。新しい重い試験や外部送信は追加しない。

## 承認された追加検証（Steps23〜25）

製品・fixtureを変更せず、U5専用診断CI/helperで現行入力と両lockのbefore/after/current一致を保存する。署名済みcommit、各job、実使用compiler・ツール版・flags、全生ログ・実exitへ結合する。新診断ファイルも入力監査に含める。

Linuxは既存diff_u5の全43ケースを毎回生成するfresh native期待結果と比較する。比較mask、TID・時刻の既存正規化、30秒process-group watchdogとkill/reapを維持する。coverageは旧U5の既存13製品ファイルと同じ分母規則を使い、80%以上を要求する。3OSは `cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests::` でHost7/Kernel27/MMU6/Runtime6の46件・ignored 0を個別に確認し、fmt、Clippy警告エラー、既存依存4検査も実行する。正確なCIコマンドと版を原本ログへ保存する。

kernel_threads_u5／kernel_futex_u5は現行実使用nightlyで各600秒以上ASan/LSanを実行する。instrumentation、sanitizer runtime、flags、依存閉包、両lock、実exitを保存し、旧nightly-2026-10-01の成功で代替しない。入力30秒上限と600秒のfuzz実行時間を区別する。

Node/本物SafariはU9証拠の共有機能についてケース単位の一致条件を記録して限定再利用する。guest clone/futexの43 native差分やnative Hostへの実スレッド割当とは別の証拠であり、wasmゲストWorker接続のU11完了を主張しない。失敗・不足は具体的に記録し、閾値・比較条件を弱めない。正式検査・独立レビュー後、新最終確認コマンドは変更承認を得て実行する。

## 今回の現行ソース再確認（Steps20〜22）

以下のStep19以前の手順・版・結果は履歴であり、今回そのまま再実施する指示ではない。sensor本体の移行・配布対応は別チャットで継続する。

現行ソース、両Cargo.lock、実使用Rust/compiler、共有依存と設定を保存し、旧7eb1819の46件・36担当パスと旧9aa1497の43差分・417入力を個別に照合する。U5限定内部テストは `cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests::` を用い、各crateの実件数・ignored・exitと生ログを保存する。0件やskipを成功証拠にしない。

Linux差分43件、既存13ファイルのcoverage80%以上、3OS、kernel_threads_u5/kernel_futex_u5各600秒ASan/LSan、本番wasmのNode/本物Safariはソース・lock・実使用compiler・設定・対象範囲一致を確認する。U9/U3で得た共有証拠もU5全体の検証と同一視しない。再利用できない対象は未検証と具体的追加実行案を記録し、その範囲の承認後に実行する。製品修正が必要な場合も具体的不一致と最小変更を先に提示する。strict guard、30秒制限、比較maskとcoverage分母を維持する。

今回の承認済み最終確認コマンドは `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-u7-u9-u3.py`。新U5証拠の検証を追加するためにコマンドを変更する場合は、新しい承認を得てから実行する。正式sensor・required-sections検査は公開された正式経路で実行し、exitとpass/findingsを保存する。旧51件FAILを今回の実測と混同しない。

## 過去の文書検査修正（Steps17〜19）

追加Step19ではsensor本体と回帰テストを修正する。既存frameworkの公式テスト配置・実行方法を確認し、隔離コピーで担当要件欠落、共通要件欠落、他Unit要件の除外、未知Unit、欠落・矛盾した割当、既存AC経路、Unitなし全体経路、詳細NFR/BR、target/status/path異常を検証する。正式適用後は `aidlc engine sensor-traceability --stage code-generation --output-path aidlc/spaces/default/intents/261004-rust-blink-port/construction/u5-threads-futex/code-generation/traceability.json` を実行し、exit値とJSONのpass/findingsを両方記録する。expected集合は独立した上流割当から取得し、U5の自己申告表をoracleにしない。回帰テストの正確な実行コマンドは既存runnerを確認後に確定する。

Step 18は文書だけを対象にする。code-summary.mdのH2見出しを検査し、共有要件・Unit定義からU5に割り当てられた9要件とtraceability.jsonの全対応先の実在を照合する。51 ID欠落の出力が全体要件の入力によるものか、Unit割当漏れによるものかを確定し、Unit限定の正式sensorのコマンドと出力を保存する。対象を誤った検査を成功扱いにせず、他Unitの要件をU5のOK行に追加しない。検査用の正確な引数はsensorの公開helpで確認し、未実行の検査をPASSと記載しない。

現在の承認済み確認コマンドは `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py`。修正後の独立レビューを経て親が同じコマンドを再実行する。下記の旧U5コマンドと9aa1497向け数値は過去の検証手順として保持し、7eb1819の今回の結果と混同しない。製品コードの変更がない場合は重いCIを再実行せず、現在のソースへの成功済み証拠の結合を確認する。

## Runner and configuration

固定rust-toolchain.toml、Cargo.lock、既存Cargo runnerを使用する。Step2でKernel/Host/Runtime/MMUのU5専用filterを整備し、初回差分ケースより先にrunnerが実行可能なことを確認する。

`cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests::`

現時点ではU5テスト未実装であり、0件成功を検証成功としない。実装後は各対象部品5〜8件以上と統合ケースを要求する。

## Native differential

U5専用guestをtests/guests/u5へ置き、専用比較scriptでnative生成→emulator実行→stdout/stderr/exit/定義済みメモリ値の比較を行う。各プロセス30秒watchdog、kill/reap、rawログを保持。TIDは関係と一致性を比較し数値自体は正規化する。時刻・scheduler順序を同一と仮定しない。具体コマンドをStep2で固定してから実装前native生成を行う。

## Coverage and safety

Linuxのllvm-covでU5の製品変更ファイルを明示し、同じ分母と80%下限を維持する。対象ファイルと専用reportコマンドはStep1〜2で確定し手順へ追記する。古いUnit filterを改名してU5の測定としない。fuzz専用U5対象は固定nightly、各600秒ASan/LSan、kill/reap付きで検証する。

## Cases and test data

clone flags/TLS/TID/exit、futex mismatch/wake/bitset/timeout/割込み/異常アドレス、clear_child_tid、lost wake、killと回収を含む。単体では制御可能なHostを使い、統合では実Hostスレッドを使う。期待結果は毎CI生成しfixtureを保存済native期待値で代替しない。旧結果と新結果を分けて保存する。

## 追加手順: 待機開始前のtimer制御通知

上記は初期bootstrap時点の手順として保持する。既存の内部44件・finite38件と証拠は存在するが、入口前通知の追加検証は未完了である。この計画改訂段階では製品・fixtureを変更しない。Plan Approvalと必要summary確認後、Step10〜16を順に実施する。

1. 製品変更前に既存ケース0〜37を保持し、38disarm先行relative sleep、39後期限timer set先行relative sleep、40set/shorten/disarm反復先行relative sleep、41disarm先行absolute clock_nanosleep、42disarm先行timeout付きfutexを追加する。子がtimer syscall完了後にreadyをrelease storeし、親はacquire load後に待機syscallへ入る。全43ケースで同じstdout/stderr/exit/timeout/raw比較を行う。errno・handler回数・時間区間boolの期待はnative CI実測で確定する。
2. fixture-only native-firstの正確なコマンドは `bash tests/guests/u5/build.sh target/guests/u5`、`python3 scripts/u5-runner-test.py`、`python3 scripts/u5-native-observe.py --out target/u5-native-first`。rootが限定commit/pushとx86-64 Linux原本取得を担当する。全43raw manifest/JSON/streamを確認し、rootのgo前に製品修正しない。
3. 製品修正後の内部test-afterは `cargo test --locked -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-mmu --lib u5_tests::`。Host同期で入口前通知、Host entry後、再計算中のset/shorten/disarmと反復を確定させる。別worker process drainではowner通知を失わず、owner ack/send競合でも通知種別を保持すること、metadata-onlyはEINTRにしないこと、masked/ignored/実signal・group終了・外部停止との区別、futex/flock回帰を検査する。0件成功を合格にしない。Host待機と完了に既存の有限timeoutを付ける。
4. 現sourceで `cargo build --locked -p paludarium` 後、`cargo test --locked -p paludarium-harness --test diff_u5 -- --nocapture` を実行する。毎回fresh native43件を生成する。比較表、build loop、runner範囲、harnessテスト一覧、manifest inventory、候補checkerを全43件へ一致させ、既存38件の削除・緩和をしない。untimed SA_RESTART再開・handler値変更EAGAIN・timed EINTRは既測定nativeの回帰対象として保持する。
5. 最終sourceの3OS単体・fmt/clippy（警告エラー）・cargo deny、先行U1/U2/U3/U4/U7/U9差分、固定13製品file Linux coverage80%以上を再実行する。既存nightly-2026-10-01とlockedコマンドを維持する。kernel_threads_u5/kernel_futex_u5は各600秒ASan/LSan、exit0、kill/reap、raw artifact、fuzz/Cargo.lock before/after/current一致を検証する。cargo-fuzz非対応の--lockedを加えず、先行cargo check --lockedとlock hash監視を維持する。
6. 現production wasm moduleでNodeと本物のSafariを実行し、同一case集合・sharedMemory・crossOriginIsolated・cleanup・module hash・raw reportへ結合する。旧module報告やWebKit代替を現moduleの実測と扱わない。旧417source inventory/先行証拠73件を保持し、同sourceの全claimと原本run head/job/commit/stream/artifact/hashを更新する。全条件成立前はfinal-proofを未完了とし、旧成功は中間snapshotとして残す。
7. 最終候補checkerの内部件数を43へ更新するが、承認済みcanonical verificationのcommand stringは変更しない。実際の登録文字列を親が保持・確認し、独立レビュー後に同じ文字列で実行する。計画の完了checkboxは実測後だけtickし、source-manifestの未知fieldやreview bookkeepingを製品成果物へ加えない。

閾値・watchdog30秒・600秒fuzzの下限と対象を緩めない。ready同期は入口前順序、内部Host同期は実待機と通知ack順序をそれぞれ検証し、有限guestの時間区間boolだけを全入力保証へ拡張しない。

## 文書整合の追加確認

Plan Approval後、traceability.jsonの全7notesを読み取り専用で抽出し、現在のhead9aa149786015ad9f789e8527cc30d7f30f2f9482・43ケース・coverage3256/3825・threads18531279/futex9935154runs各601秒とpreentry-final原本参照へ一致することを確認する。旧e8e23fbd/38/3226/3797/旧fuzz値が現在結果として残らず、残す歴史には過去snapshotの表示があることを全notesで検査する。対応するMarkdownとfinal-proofの原本値も照合し、文書変更のhashを再結合する。417source不変を確認し、製品変更と重いCI再実行を行わず現headの成功原本を再利用する。

既存canonical `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u5-native-shared.py` を変更せず再実行してexit0を記録する。成果物freeze後、親による新しい独立レビューと同commandのcanonical確認を行う。保存証拠73件、全43raw比較、固定13file/floor80、両600秒sanitizer、現module Node/実Safari条件は維持する。
