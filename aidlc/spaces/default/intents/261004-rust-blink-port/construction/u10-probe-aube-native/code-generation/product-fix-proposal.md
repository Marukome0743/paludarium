# U10 install 差分の原因と次の検証案

## 現在の結論

検証済み: Linux CI 38007549010 の差分成果物では probe 8項目・全体実行・node不在・default-version が一致し、default-install は native exit 0 / emulator exit 1。CPU例外ではなく `Ok(Exited(1))` で終了し、stderr は `failed to link node_modules` / `Function not implemented (os error 38)` / `/node_modules/.aube/filedep@file+444ac87ade2c3106/node_modules/filedep/package.json` を示す。成果物は `verification/differential-failed/`。

検証済み: 同じ固定 guest を macOS の C10 ハーネスで読み取りデバッガ診断したところ、kernel の未実装分岐で syscall 90 (`chmod`) が2回観測された。引数 mode は 493 (0755) と 33261 (0100755)。syscall 94 (`fchmod`) は条件付き breakpoint に一度も到達せず、同じ install error / exit 1 に至った。当初の fchmod 原因仮説はこの観測では支持されない。macOS上の診断はLinux全体の合格証拠にはしない。

文書根拠: kernel `files.rs` の `NUMBERS` に90/94はなく、`lib.rs:431–433` は未登録番号を ENOSYS にする。一方、fixture の host package.json は0644だが、`Config.files` は `(path, bytes)` のみで、runtime は `GuestFile::new()` を使い、VFS `DEFAULT_MODE` は0755。したがって追加した default-install 比較には入力metadata不一致がある。chmod欠落が存在していても、このケースだけを根拠に製品修正を即承認するのは適切でない。

## 呼び出しの根拠

固定aube revision `bd94e42f54d3b5e3dd102716b7197f316cb5f4ed` の `crates/aube-linker/src/materialize.rs:666–677` は `stored.executable` のとき `xx::file::make_executable(&target)` を呼ぶ。固定lockの xx は2.6.2。ローカルcrate `xx-2.6.2/src/file.rs:392` の同関数はmetadataのmodeに0111を加え、同ファイルのchmod helper経由で `std::fs::set_permissions` を呼ぶ。エラー対象のpathは83bytesで、最後のchmod観測で保持された周辺値83とも整合するが、guest pathのメモリ内容はデバッガで直接取得しておらず、この関連付け自体は推測。

公式固定ソース: https://github.com/aubepkg/aube/blob/bd94e42f54d3b5e3dd102716b7197f316cb5f4ed/crates/aube-linker/src/materialize.rs#L666 。sourceは公式tarをメモリ内で読み取り検索し、製品へコピーしていない。

## 最初に行う harness の整合検証

1. native fixture のfile modeを記録し、C10 Config.filesが既定0755になることを明示する。現在APIではprivate VFSへの0644指定ができないため、API変更や未実装chmodをbootstrapとして利用する案は採らない。
2. 承認済みの限定mounted fixture (`app` → `/`, `outside` → `/outside`) はhostの0644を保持できる。まずこの経路でaube4コマンドを同一mode・同一bytes・同一状態遷移で比較する。default-installの成功条件を維持し、metadata不一致の失敗を取り消さない。比較順序だけmounted4操作を先にすることは、前の失敗で未実行だった条件の切り分けに使える。
3. この整合後もchmod等で失敗した場合、当該syscallとmode/path/fdを再取得し、製品修正の範囲を確定する。mounted成功はdefault-install合格の代用にはせず、private VFSのmetadata指定を整合する最小API追加を人の承認へ返す。

この変更はharnessの比較入力整合が目的であり、native exit/出力、#1645の両依存0.0.0、30秒、network/node不在、12必須プログラム項目を弱めない。default-installの不一致記録を成功へ書き換えない。

## 最小の製品修正計画（人の承認前・未実装）

U9/C10 Configとruntime初期ファイル配置の境界へ戻す。対象は `crates/paludarium-runtime/src/lib.rs` と同crateの単体テスト、U10の `support/u10.rs` とfixture検査。既存 `Config.files: Vec<(path, bytes)>` と `with_file` を変更せず、optional `file_modes: Vec<(path, mode)>` および `with_file_mode(path, bytes, mode)` を追加する。runtimeは `GuestFile::new` で作った既存ファイルへcreation時にoverride modeを設定してMemFsへ追加する。既存指定なしは0755を維持する。U10はfixtureファイルの0644を指定する。プログラム自身の0755、temporary領域の既存初期化は維持する。chmod syscallをbootstrapで呼ぶ方式ではない。

invalid overrideはSession::newで拒否する: permission bits以外を含むmode (`mode & !0o7777 != 0`)、空/非absolute/不正path、対応するConfig.filesがないpath、重複override。mode0は有効なpermission設定として扱い、既存VFSのpermission enforcement全体を新たに保証したとは主張しない。native oracleでstatの型bits+0644/0755を先に観測し、その後C10配置実装と内部テストを行う。最低7内部境界: 既存with_file0755維持、明示0644、mode0、typed filemode bits保持、invalidmode拒否、missingfile/invalidpath拒否、duplicate override拒否。guest filemode差分でcontents/linksが変わらないことも確認する。

U10 harnessでは、native fixtureとprivate VFS fixtureのmodeを証拠へ記録し一致を検査する。限定rootmountはtemporary `app/tmp` と `app/home/u10` を事前作成してnativeのruntime directory条件を揃える。rootmount下のchild `/tmp/fslock` はprivate `/tmp` directoryだけでは保護されずhost側へrouteするため、これを省くとENOSYS以前にENOENTとなる。runtime directory準備はU10 harness内だけで行う。

製品側追加実装と回帰の承認後、default-installを含む全gateを再実行する。同一metadataでchmodがなお必須なら以下の別修正を再提案する。

## chmod の条件付き追加計画

整合した必須ケースで必要性が確認された場合のみ、U7のfilesystem/kernel担当へ戻す。chmod90を `files.rs` のdispatchへ追加し、VFS inodeのmodeを型bitsを維持して更新する境界を用意する。必要なら同じinodeを指すhardlinkと開いているfdのstatへ反映し、host mountでも既存capabilityを通す。戻り値0だけのstubは不可。fchmod94は今回実観測がないので自動的に追加しない。別の必須ケースで確認されたら、fd→inode境界とEBADFを含む別の具体範囲を提示する。

実装前のnative x86-64 Linux oracle: 小さい独立static-musl guestで `chmod(path,0600)`、`chmod(path,0755)`、hardlink経由stat、open済みfdのfstat、directory、symlink-follow、missingpath ENOENT、invalid pointer EFAULTを観測する。各操作30秒以内。kernel/VFS実装はその期待値を先に得てから行い、その後に内部単体テストを追加する。mode更新でcontents・offset・link countが変わらないことも確認する。

検証コマンド: `cargo test --locked -p paludarium-harness --test diff_u7 --test diff_u10 -- --nocapture`（Linuxの隔離namespace、明示CARGO_HOME、offline cacheで実行）、該当kernel/VFS unit tests、clippy/fmt、root依存監査、既存U8回帰、Linux行coverage80%以上。合格の主張は実測のhead/CI/分母へ限定する。

## ローカル読み取り診断の再現

保存先: `verification/local-install-diagnostic/` に args=`install` と environment、guest stdout/stderr/exit/stop/seconds がある。最後に完走したC10実行はinstall exit1。LLDBコマンド出力の抜粋を下記に保存する（LLDBのprocess exit0はtest wrapper終了を表し、guest成功ではない）。

build: 実nightly2026-10-01 cargo/rustcで `cargo test --locked --offline -p paludarium-harness --test diff_u10 --no-run`。

環境: `PALUDARIUM_U10_OPERATION=<record>/verification/local-install-diagnostic`, `PALUDARIUM_U10_BINARY=<record>/verification/native-first-success/guests/u10/aube`, `PALUDARIUM_U10_FIXTURE=<workspace>/tests/guests/u10/fixtures`。実行は Python `runner.run()` のprocess group / timeout30 / kill・reapを使い、LLDBへ次を渡した。製品sourceは変更していない。

```text
lldb --batch
  -o 'breakpoint set --file crates/paludarium-kernel/src/lib.rs --line 432'
  -o 'breakpoint modify -c "thread->cpu.gpr[0] == 90 || thread->cpu.gpr[0] == 94" -G true 1'
  -o 'breakpoint command add 1 -o "frame variable --raw thread->cpu.gpr thread->cpu.rip"'
  -o run -- <compiled diff_u10 test executable> --exact u10_guest_operation --nocapture

thread->cpu.gpr[0] = 90; thread->cpu.gpr[6] = 493
thread->cpu.gpr[0] = 90; thread->cpu.gpr[6] = 33261
thread->cpu.rip.__0 = 93825017888779 (both calls)
test u10_guest_operation ... ok
Process 81572 exited with status = 0
runner: exit 0, timed_out false, wall_seconds 3.914672
guest record: exit 1, stop None / Ok(Exited(1))
```

最初のsandbox内LLDBは `process exited with status -1 (no such process)`、host権限での同じ読み取り診断は成功。最適化で `number` 変数が取得不能だったため、型の実データ `thread->cpu.gpr[0]` を読んだ。RAX=0、RSI=6、RDI=7のindexはCPU state.rsに定義される。各診断操作は30秒未満で、現在実行中sessionはない。

## mounted の追加ローカル診断

検証済み: `verification/local-mounted-diagnostic/install/` は元のmount設定でexit1、stderr `failed to acquire project lock` / `/tmp/fslock` ENOENT。専用一時fixtureだけへ `app/tmp` と `app/home/u10` を作った `install-with-runtime-dirs/` はexit0、`filedep@1.0.0` / `linked@2.0.0`、stop `Ok(Exited(0))`、wall 3.517608292秒。metadata0644を保持するmounted経路では今回の致命的ENOSYSは出なかった。macOSでのguest診断であり、native Linux full CI合格は未検証。

検証済み: 同じ専用fixtureでversion→install→node_modules除去→frozen→listも完走した。保存先 `local-mounted-diagnostic/sequence-{version,install,frozen,list}/`。すべてexit0/stop `Ok(Exited(0))`。wall secondsは0.65003675、3.275868958、14.961398084、0.578781333。version stdoutは `2.6.1 linux-x64 (2026-10-09)`、install stdoutは空、frozen stderrは両依存 `0.0.0`、list stdoutも両依存 `0.0.0`。各操作30秒以内。これはローカル切り分けであり、同一headのLinux native/emulator CI比較は未検証。

再現は既存 `differential.operation` を使用し、公式成功artifactのaube bytes、現在のcompiled diff_u10 test executable、configのenvironment、専用コピーしたfixtureを渡し `mounted=True`。実行はrunnerが各操作30秒で停止/回収する。raw stdout/stderr/exit/stop/seconds/runner.jsonは上記directoryに保持する。

Step9は未完了。private default-install gateは維持し、まずcreation時modeを指定する最小C10追加を具体承認へ返す。製品sourceは変更していない。
