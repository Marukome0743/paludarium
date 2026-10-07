# U4 現在sourceと保存済み実機CIの照合

## 承認と作業範囲

tool-produced `verification/u4-approved-brief.txt` を全文読取した。Testing Contract hash99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616のcustom順序と品質下限を維持。conductorの現在Plan Approval/Summary Confirmation/UNIT_STARTED後、Step15〜18だけを実行した。製品source、テスト、U1/U2記録、frameworkstate、SCM、review/lifecycleを書き換えていない。

共有requirements FR2.2/FR2.9・NFR1〜9、C1/C2/C4/C8の提供側所有とconsumer一括更新、components/units/story-mapは保持済みの入力。U4 functional-design/nfr-requirements/nfr-design/infrastructure-designはすべて不存在。計画の未実装Host/配送しないというSourcesは旧baselineであり、現在は時刻・待機・signal配送を実装済み。

## source bytesとCIの対応

検証済み：Python hashlib.sha256とread-only `git show 4d52be0a6f3b11d6c11a62f96196985c9c280fdc:<path>` でmanifest107pathsを比較し107 MATCH/0差異/0欠落。各SHA256と照合結果は reviewed-source-4d52be0a-current.tsv、現在snapshotは source-hashes-current.json。CI JSON headShaも同revisionで、conclusion success。

strict source-manifestはversion1/writes、従来107claimsを保持。共有CPU u2_tests/diff_u2は先行C1/C4変更のconsumer修正として既存claimを保持し、今回の新規U4実装とはしない。tests/guests/u4/build.shはU1復旧でLF修復済みのbytesを確認した。

旧source-hashes-current.jsonの37pathsは historical-source-hashes-current.jsonへ保存。15paths相違を validation-current.json に列挙した。旧snapshotを現在不変と称さない。

## native差分・内部6層の非ゼロ結果

検証済み：verification/final-bookworm-4d52be0a.logは実機AuthenticAMDの全workspace success、diff_u4 44passed。構成はmemory10/time8/signal23/live3。差分期待は実行ごとnativeで作り、固定goldensを使わない。

CargoのRunning unittests sectionからpackageを識別し、`test ...u4_tests::... ok` の一意名を集計した。verification/current-counts.jsonに全名を保存：MMU10、Host8、Kernel37、Runtime11、Cpu5、Types5、計76。Host/Typesは関数名のu4_接頭辞ではなくu4_tests moduleでfilterされるので、関数名だけの0件をPASSとして扱っていない。すべて現在sourceのtest名と一致した。新しいscoped commandを実行したとは記録しない。

実行コマンドはrawに保持。現在不足がなく新テストを必要としなかったため、承認済み限定commands/重いDocker QEMU workspaceを追加実行していない。QEMUのtrapno/ENTER/ALU観測差を実機native証拠へ転用しない。

## CI・3OS・品質

独立レビュー用に必要なログをU4 verificationへコピーし、U1/U2成果物を読まずに確認できるようにした。

| 証拠 | 結果 |
| --- | --- |
| verification/ci-37695518838.json | 3OS単体、differential、lint、dependencies、coverageの7jobs success |
| verification/native-37695518927.json | workspace/Bookworm/2expectation jobsの4jobs success |
| verification/final-bookworm-4d52be0a.log | U4差分44、内部76の個別test ok |
| verification/final-ubuntu-4d52be0a.log | 実機Linux whole-workspace success |
| verification/final-mac-4d52be0a.log | macOS existing suite success |
| verification/final-windows-4d52be0a.log | Windows existing suite success |
| verification/final-coverage-4d52be0a.log:2187 | 全体7030行/未実行522、92.57% |
| 同ログ:2617 | U1対象packages6780行/未実行1172、82.71% |

このCIは新しいU4-only test実行ではない。両coverage80%gateを保持し、unit subsetで全体gateを代替しない。nightly固定版と依存lock/Actions pinを維持。support/u4.rsは全ケース外側30秒watchdogでkill/reapする。sourceのC2 clock/wait、C4共通Mutex、C8明示dispatch、C1fault metadataを読取し、CPU crate dependenciesはtypes/decoder/mmuだけでHost/Kernelへの逆依存なしを確認した。

## ABI/inventoryと履歴

docs/u4/syscall-matrix.md、signal-abi.md、validation.mdを読取。固定probe/aube receiptsは履歴として維持。static syscall位置109/258は到達経路・syscall番号数ではない。有限native traceにclock/sleepがないことを対応不要の証拠にせず、専用time fixture8件のnative結果を用いる。siginfo/ucontext offset、mask0xcd5、pending target順、REP budget returnの各内部/native回帰が現在CIで通る。

docs/u4/validation.mdの317passed/93.70%と旧ASan完走は先行sourceの記録であり、このreconciliationの現在結果ではない。旧summary/validation/traceability/hashをhistorical-*へ保存、evidence.mdとRed/Green失敗履歴は保持した。

## 未検証・handoff

現在sourceのsyscall_args/mmu_ops各600秒ASanは未検証。syscall_args.rs自身が旧hashと異なり、mmu_ops.rsは同じでも共有MMU/CPU/Kernel/Host/Runtime依存が異なる。旧1136975/1564316runs各601秒を転用しない。FR9.3/NFR2/NFR3をtraceability GAPにした。夜間targetと各600秒ASan/timeout30を維持し、Build and Testで現在sourceに結び付ける。その他15割当FR/NFRは既存implementation/test/config targetの欠落0を確認した。

未検証：任意入力・全runtime経路・probe/aube emulator全program/U10、guest clone/futex/U5、file-backed mmap関連統合、wasm/Safari/U11、JIT/U14、handler内FS/GS変更の追加native比較。これらへ現在CIを一般化しない。新製品defectは今回見つからず、追加のproduction修正を行わない。
