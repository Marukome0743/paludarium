# コード生成の結果（u1-skeleton）

## 修復した動作とファイル

Ubuntu muslのhello-cが未対応SSEで停止し、REP比較のfault時flagsが実機vendorにより異なっていた。U4/U7の混在CRLFとDocker VMM compiler起動も修復した。3OS検証で判明したHost errno・Windowsリンク数・test cleanupを追加修復した。

- decoder lib.rs、CPU exec.rs/lib.rs：legacy XMM MOVQ/PUNPCKLQDQ。64bit読取、MOVQ上位ゼロ、更新前の両低64bit結合、自己aliasを実装。MMX/AVXは追加しない。
- CPU state.rs/lib.rs/u2_tests.rsとharness diff_u2.rs・guest u2/observe.c：明示RepFaultFlagsモデル。既定RestoreInitialはIntelの初期flags復元、PreserveCompletedはAMD観測の成功済み反復flags保持。productionはhost vendorを検出しない。native observerのvendorで差分fixtureだけが選択し、未知vendorは失敗。mask0xcd5とstart/partial/budget/fetch fault比較を保持。
- guest insn/sse.c、harness coverage.rs、docs/u1/census/：非対称64bit、dirty上位、自己alias回帰。census68/68はソース根拠片の対応であり、全形式・flags入力の意味論網羅率ではない。
- guests u4/build.sh・u7/build.sh：CRLFからLFへ統一し、buildロジックを保持。
- scripts/linux-dev.sh：build/runのstack上限解除でDocker VMM compiler SIGSEGVを修復。VMMを維持し、voicevoxを復帰した。
- Host native_fs.rs/lib.rs：Linux raw errnoを保持し他OSをguest errnoへ変換、lock競合をEAGAIN11へ統一。Windows link metadataは実リンク数を取得し、値が無ければEIO。pinned nightlyのWindows限定featureを利用し、依存・toolchainを変更しない。root保持handleを解放してからfixtureを削除する。
- Runtime tests.rs：u7_runtime_mountの削除前にMountedFs/Sessionの両方をdropする2行のみ。
- VFS mount.rs：test共通FixtureのMountedFsをreplace/dropしてから削除。production mount機能・assertions・cleanup失敗のunwrapを保持。
- CI：fork診断ブランチで既存3OS・native差分・lint・依存・coverageを実行。native診断はUbuntu/BookwormとCPU/musl識別・期待結果を保持。全体80%とU1対象packages80%を別々に測定する。

後続U2/U4/U7の独立機能をU1の新成果とは数えない。関連修復のowning fileだけをmanifestへ追加した。C1〜C11の口は保持し、現在のsignal配送/mount拡張は後続共有変更である。初期U1の登録のみ/mount拒否仕様を現在の全挙動とは主張しない。

## 実装前の期待結果と失敗

検証済み：commit6229ff02のnative run37672366086でMOVQ上位ゼロ、非対称PUNPCKLQDQ、自己aliasの期待結果を取得し、Bookworm insn_sseのInvalidOpcode Red（66 48 0f 6e c0）をproduction変更より先に保存した。内部decoder/CPU/HostテストはTesting Contractのtest-afterに従った。

検証済み：AMD EPYC7763/9V74のREP start flags8d5、完了反復後CMPS44/SCAS0と、Intel Xeon8370Cの復元8d5を観測した。prefault準備とREP直前popfqを逆アセンブルで確認し、比較対象を減らして通過させていない。仕様根拠と実機観測の区別はverification/repair-implementation-results.md。

検証済み：先行e081のmacOS errno35、Windows lock33/links1対2/cleanup32を保存。Host修復後d238でHost25件が通過しRuntime cleanup32が残り、Runtime修復後2a8でRuntime25件が通過しVFS共通cleanup32の16件が残った。各failure logをverification/へ保持し、機能assertionそのものの不具合と断定していない。

## 最終修復後の検証

最終commit **4d52be0a6f3b11d6c11a62f96196985c9c280fdc** はGitHub verified:true/reason:valid。

| 検査 | 最終結果と証拠 |
| --- | --- |
| [CI37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838) | 検証済み：全7 jobs成功。Linux/macOS/Windows単体、native差分、fmt/clippy、依存、coverage |
| Windows Host/Runtime/VFS | 検証済み：25/25/45 passed、0failed。final-windows-4d52be0a.log。u7_runtime_mountと全mount fixtureのcleanupまで通過 |
| [Native37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927) | 検証済み：全4 jobs成功。Ubuntu/BookwormともAMD EPYC7763、各全workspace・U1差分16/U2 38/U4 44/U7 63 passed |
| 行coverage全体 | 検証済み：7030行/未実行522、92.57%。final-coverage-4d52be0a.log |
| 行coverage U1対象11packages | 検証済み：6780行/未実行1172、82.71%。同ログ。共有crate内の後続unit実装も含むため、U1初期実装だけの分母とは呼ばない |
| 手元Docker VMM | 検証済み：decoder18、CPU39、U1差分16、REP6、Host25、Runtime25、VFS45 passed。各限定clippy/fmt exit0。repair-implementation-results.mdとhost/runtime/vfs-cleanup reports |
| 静的対応 | 検証済み：103 claims/108 files、欠落・未追跡・現在snapshot不一致0。上流47/対応47、OK target欠落0、census68根拠欠落0 |
| 2フック | 検証済み：plan-approval-guard/continue-workflow登録済み、復旧9 tests/37 assertions成功。hooks-recovery-current.md |

Intel実機の成功はe081時点のjob112975354218で記録した。e081から最終commitまでCPU・decoder・REP observer/fixture・SSE guestはjj diffで差分0。最終runのrunnerはAMDであり、最終全workspaceをIntel実機で再実行したとは主張しない。過去197件/94.00%、102件/87.11%、89.79%を今回の成功へ転用しない。

## 計画との関係と制約

Step24a/24bは追加承認と別の内容確認後に実行した。VFS同種cleanupはStep24cとして同じ復旧に限定し、現在のplan-approval check off/execution_allowed trueに従い続行した。以前の人間回答を変更済み計画の承認へ読み替えず、Q&Aを保持する。

Docker VMM/QEMUのENTER allocation faultは元命令の後の_exit呼出しでfault（rip_delta=-61）し、実機Linuxと異なる。関連U4/U7にもQEMU oracleのsignal/errno差が残る。Docker全workspace成功とは扱わず、失敗ログを保持する。

今回のwasm/Safari、U1各fuzz再実行、decoder候補比較の歴史的ログは未検証。後続unitのfuzzを代用しない。nightly2026-10-01、各600秒、coverage80%下限、case30秒watchdogを保持する。これらの未測定項目はBuild and Testの入力であり、manifest/traceabilityのOKは測定合格ではない。

rejected reportが必要な場合、その直前にも2フックを再確認する。今回の修復中に人間のgate rejectionを捏造していない。
