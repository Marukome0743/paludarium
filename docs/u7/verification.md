# U7 検証記録（実装作業中）

このファイルは作業中の観測であり、U7完了またはreview合格を意味しない。raw evidenceは `inventory/` にある。Testing Contractは `sha256:99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616`。Linux行80%、各ケース30秒、nightly fuzz各600秒を維持する。

## 検証済みの中間結果

全LinuxコマンドのprefixはPowerShellの `& 'C:\Program Files\Git\bin\bash.exe' scripts/linux-dev.sh`。

|raw log|suffix / 結果|観測|
|---|---|---|
|runner-baseline.txt|`cargo test --locked -p paludarium-vfs --lib` / exit0|実装前の既存VFS5件成功。|
|diff-red.txt|`cargo test --locked -p paludarium-harness --test diff_u7 -- --test-threads=1 --nocapture` / exit101|初期20件はnative期待取得後、emulator ENOSYS等で全失敗。|
|diff-third-green.txt|同diff command / exit0|当時20件成功。|
|host-tests-first.txt|Host限定 / exit0|8単体ケース成功。|
|host-race.txt|Host symlink/rename競合限定 / exit0|1親ケース成功。childの成功を件数へ重複加算しない。|
|owned-full-second.txt|owned crate full tests / exit0|188親unit/integration＋1doctest成功。当時のsourceの証拠。|
|diff-fd-red.txt|diff command / exit101|31件中28成功、closed/redirect/dup stdio3件失敗。|
|diff-fd-green.txt|同diff command / exit0|FD共有description修正後31件成功。|
|diff-host-red.txt|同diff command / exit101|61件中56成功、Host symlink/readonly create関連5件失敗。|
|diff-host-green.txt|同diff command / exit0|guest namespaceと安全なread-only create修正後61件成功（MemFs32＋Host29）。|
|mount-namespace.txt|`cargo test --locked -p paludarium-vfs u7_mount -- --test-threads=1 --nocapture` / exit0|mount内部16件成功。|
|coverage-first.txt|初回測定 / exit1|line69.74%、4973 total/1505 missed。失敗の証拠を保持する。|
|coverage-second.txt|測定 / exit101|前ジョブ終了前のwrapper同期でsourceが消えたrunner失敗。guest意味論の失敗・coverage合格と扱わない。|
|coverage-third.txt|下記scoped測定 / exit101|Runtime cross-mount fixtureが相対HostFs契約に合わず期待EXDEV18に対しENOENT2。数値未生成。|
|coverage-fourth.txt|下記scoped測定 / exit0|line4099 covered /4569 total＝89.71%、missed470。fixtureをNativeFsへ直し期待EXDEVとroot無変更を維持。CLI追加前の中間source。|
|diff-trailing-red.txt|限定case32 / exit101|未完成CLI初稿がwrapper同期されE0608 compile failure。native semantic Redと扱わない。|
|diff-trailing-semantic-red.txt|`cargo test --locked -p paludarium-harness --test diff_u7 trailing_operations -- --test-threads=1 --nocapture` / exit101|2親ケース失敗。nativeはsymlink_to_dirの末尾slash rmdir/rename/unlinkでENOTDIR、O_CREAT\|O_DIRECTORYでEINVAL/no file。emulatorはtarget directoryを削除し、拒否後fileを残した。未修正の不具合として保持。|

coverage-fourthの正確なsuffix：

```text
cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1
```

測定対象はU7変更クレートの全lib（既存共有挙動も含む）とnative U7差分。新MMU `check_read` を含むMMU libは831 total/68 missed＝91.82%。除外は未変更CPU/decoder/JIT/typesとharness infrastructureのreport行であり、whole-workspace coverageとは表示しない。U7のproduction変更ファイルを除外して閾値へ合わせない。CLI変更後の最終sourceはこの中間測定で合格扱いにせず再測定する。

## 未完了・未検証

この節は中間状態の記録である。unit/diff/coverage、fmt/clippy、cargo-deny、各600秒fuzzの最終結果は後続の「最終ソースの再検証」を参照する。独立reviewと現在U7 checkpointは親担当で実行する。

Linux以外のnative Host mount、browser/wasm/JIT、probe全体/aube全体、stat未比較フィールド、Host側の外部rename後に既存dirfdが参照し続ける挙動は未検証。比較値と除外理由は `native-comparison.md` を参照する。

## 最終ソースの再検証

検証済み：`scripts/linux-dev.sh cargo llvm-cov --locked -p paludarium-vfs -p paludarium-kernel -p paludarium-host -p paludarium-runtime -p paludarium-loader -p paludarium-mmu -p paludarium -p paludarium-harness --lib --test diff_u7 --test command --ignore-filename-regex 'paludarium-(cpu|decoder|jit|types|harness)/' --fail-under-lines 80 -- --test-threads=1` はexit0。`coverage-final.txt` のTOTAL行は4681 total、478 missed、4203 covered＝89.79%。CLI追加後の最終ソースを測定した。差分63親case、CLI integration6件が成功。ネイティブ期待結果は各実行時に取得し、childの結果を親件数に加算しない。

検証済み：trailing関連修正後の正式workspace検証は `repair-workspace-verification-retry.json` のexit0、fmtとworkspace clippyは `repair-clippy.txt` 等のexit0証拠を保持する。今回の再開では製品ソースを変更せず、検証手順と成果物を完成させる。

この時点ではcargo-denyとファジング2本の結果待ちだった。後続の検証済み記録を参照する。独立reviewは親担当。`fuzz-vfs-final.txt` はcontainer login shellのcargo PATH不足によるexit127で、製品の異常とは扱わない。同じASan・600秒・30秒設定を `bash -c` で再実行し、元失敗logを保持する。

検証済み：`target/aidlc-tools/cargo-deny.exe --locked check` はexit0、`advisories ok, bans ok, licenses ok, sources ok`（`inventory/deny-final-locked.txt`）。依存の重複版について11グループの警告が出るが、既存`multiple-versions = "warn"`方針を変更していない。ライセンス・取得元・既知脆弱性を検証した。ツールはofficial prebuilt binaryをcargo-binstallで取得し、製品依存を足していない。

検証済み：VFS fuzzは`bash -c 'cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O vfs_paths -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048'`をLinux development containerで実行しexit0。859022 runs in601second(s)、ASan異常・panic報告なし（`inventory/fuzz-vfs-final-retry.txt`）。単一入力30秒、RSS2048MiB、既存LSAN suppressionを維持する。

検証済み：syscall_args fuzzは同じLinux開発volumeに対する`docker run --rm --platform linux/amd64 --cap-add SYS_PTRACE --security-opt seccomp=unconfined -v paludarium-cargo-registry:/usr/local/cargo/registry -v paludarium-work:/work -e CARGO_TERM_COLOR=never -w /work paludarium-dev bash -c "cd fuzz && LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp cargo fuzz run -O syscall_args -- -max_total_time=600 -timeout=30 -rss_limit_mb=2048"`がexit0。469436 runs in601second(s)、panic/ASan異常報告なし（`inventory/fuzz-syscall-final.txt`）。前targetのASan buildを再利用するためsource再同期を省き、同じソースとファジング生成lockを検証した。`fuzz/Cargo.lock`をvolumeから回収した。

検証済み：traceability sensorの初回ab3df804は共有要件全文の範囲外43FR未列挙を検出してfailed。U7のtarget不備は0。担当外要件を所有UnitへのDeferredで明示して再実行した31ec39e1はpassed。元センサー失敗を成功として扱わない。範囲・coverage80%・600秒・30秒・既存依存方針を変更していない。

現時点で独立reviewと現在U7 checkpointは親担当へ引き継ぐ。過去の正式workspace成功証拠は保持するが、現在U7承認の代わりにしない。
