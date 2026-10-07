# U2 現在sourceとCI証拠の照合

## 実行と承認の境界

今回の対象は承認済みStep20〜23。tool-produced `verification/u2-approved-brief.txt` を読取、Testing Contract hash `99564cda628189cabe9281965610721eca6225a7082fe19e37954bf0dffa1616` を維持した。conductorが現在attemptのPlan ApprovalとSummary Confirmation、UNIT_STARTEDを記録した後に照合した。新しい製品変更・テスト実行・再build・fuzz・SCM書込・lifecycle操作は行っていない。Steps1〜19のチェックは履歴。

## 現在sourceのbyte照合

検証済み：Python hashlib.sha256でworking filesを読み、read-only `git show 4d52be0a6f3b11d6c11a62f96196985c9c280fdc:<path>` のraw bytesと比較した。manifest95claimsは95/95 MATCH、欠落0。`reviewed-source-4d52be0a-current.tsv` に各path/SHA256を保存。crates/tests/fuzz/scripts/workflowsとCargo.toml/Cargo.lock/rust-toolchain.toml/deny.tomlを `git ls-tree -r --name-only` で列挙し127/127 MATCHを確認、`verification/workspace-ci-source-match.tsv` に保存した。SCMの変更はない。

- exec.rs SHA256: `e660a4c0cc569a679e3c6dcf3511e782415196bc59786bc29eb16fc77ef1015e`
- u2_tests.rs SHA256: `dc80918a12a451e743f9bb0eabd8120fb4849019db698faa6a70494607d67827`

旧exec.rsのe5f052…との一致主張は現在には適用しない。旧95claimsとschemaを保持し、既にclaimされたCPU lib/exec/state/u2_tests・diff_u2/observe.cをREPmodelの現在確認対象として扱う。U1のSSE追加、Host/VFS cleanupはU2の新規実装成果とは数えない。

## 現在のnative/3OS品質証拠

検証済み：miseインストール実体のgh2.102.0で次のread-only操作を実行しexit0。JSONのheadShaは双方4d52be0a…、status completed、conclusion success。

```bash
gh run view 37695518838 --repo Marukome0743/paludarium --json headSha,status,conclusion,jobs
gh run view 37695518927 --repo Marukome0743/paludarium --json headSha,status,conclusion,jobs
```

実出力は `verification/ci-37695518838.json` と `verification/native-37695518927.json`。7jobs（3OS単体、差分、lint、dependencies、coverage）と4jobs（workspace、bookworm、期待観測2runner）が全success。CI実行コマンドはコピーしたraw jobログに保持する。

| 証拠 | 確認結果 |
| --- | --- |
| verification/final-bookworm-4d52be0a.log | AuthenticAMD、CPU全39、U2diff38、parallel10、U1diff16 passed |
| verification/final-ubuntu-4d52be0a.log | 実機Linux whole-workspace成功 |
| verification/final-mac-4d52be0a.log | macOS existing suite成功 |
| verification/final-windows-4d52be0a.log | Windows existing suite成功 |
| verification/final-coverage-4d52be0a.log:2187 | whole-workspace lines7030/missed522、92.57% |
| 同ログ:2617 | U1対象packages lines6780/missed1172、82.71% |

両行coverageは下限80%で実行。件数はchildの重複summaryを加算しない。静的sourceのu2_ test関数名とBookwormの `test ... ok` を照合：CPU14/decoder9/MMU9/types1/kernel1が全存在・実行済み。これは新しいfilter実行ではない。Runtimeには不存在のu2_filterを要求せず既存suite証拠を使う。

## REP modelと設計の対応

ドキュメント根拠：U2 functional-spec/rules BR1.6・NFR1.2の開始flags復元はIntel SDMを根拠とする。現在の既定 `RepFaultFlags::RestoreInitial` がこの契約を維持する。追加 `PreserveCompleted` はAMD EPYCのnative観測を反映する明示modelであり、全AMD製品を保証する一般仕様と主張しない。CPUからHost/Kernelを呼ばず、CPUIDによるmodel選択はnative diff fixture内だけにある。

検証済み：`u2_tests::u2_repeat_data_fault_applies_explicit_flags_model` はCMPS/SCAS、完了0/17/4096と内部budget再開について両policyを確認。`u2_tests::u2_repeat_fetch_fault_applies_explicit_flags_model_and_clears_context` はfetchfaultと継続context破棄を両policyで確認。Bookwormログで両test ok。

native6casesは `u2_cmps_fault_start/partial/budget`、`u2_scas_fault_start/partial/budget`。現在ログ:628/638/648/789/799/809にAuthenticAMDが報告され、38suite全件通過。mask0xcd5を維持。observerのvendor欠落/未知値はassertionで失敗し、flags出力からpolicyを逆算しない。

Intel実機成功は `verification/native-final-bookworm-e0818962.log`（job112975354218）の履歴：GenuineIntel、両内部test ok、native6casesと38suite通過。read-only git showでe0818962と現在のCPU lib/exec/state/u2_tests、decoder lib、diff_u2.rs、observe.cの7filesがbytes一致した。現在runをIntelで再実行したとは表現しない。Docker VMM/QEMUのENTER/ALU差を実機native結果と混ぜない。

## 固定inventory・契約・traceability

全U2 functional-design/NFR requirements、shared components/contracts/requirements/units/story-mapを読取。U2 nfr-design/infrastructure-design directoryは存在せず、内容を捏造しない。story-mapはストーリー工程を飛ばしFRを割当している。C1 ArithmeticFault consumer、C3 decoder forms、C4共通同期typed atomic、C5 CPU/continuationのsourceを照合し、U5/U10/U11/U14の境界を保持する。

`docs/u2/inventory/rebuild/build-receipt.json` を読み、固定aube revision bd94e42f54d3b5e3dd102716b7197f316cb5f4ed、lock8960ea…、binaryff54cffe…、probe binary15e90407…と原artifact一致を確認。隔離builderとdirtysource receiptは履歴。form-classification再集計aube4658=3136整数+190system+1332U3、probe865=696整数+3system+166U3。全native_case tokensの存在と幅/prefix/implicit operand対応は固定inventoryの対応表であり、全静的bytesのnative実行を意味しない。complete_runtime_inventory:falseと原artifact歴史上のbuilder未確定を保持する。

traceability44coverageの実file targets欠落0、詳細NFR16件欠落0。NFR2.2とfuzzを含むNFR2/NFR3/NFR3.4をGAPとし、旧notes/metricsは historical-traceability.json に保存した。旧summary/evidence-currentも historical-* に保存、evidence.md/旧reviewは保持。

## 残る品質GAPと確認方法

未検証：現在sourceのCPU/MMU各600秒ASan。旧r01 fuzzの1276258/1706799 runs・各601秒はREP変更前sourceの証拠であり現在の合格に転用しない。既存nightly target/ASan予算を保持し、Build and Testで現在sourceと紐付けた各600秒runが必要。CPUはmax_len4096、MMU4608、timeout30、rss_limit_mb2048の既存commandを用い、linux-dev.sh同期との並行を禁止する。

未検証：wasm Worker/Safari、guest clone/futex、probe/aube emulator全program、全任意入力/全vendor、JIT。新製品不具合は今回見つからず、CIとbyte照合で未解決の単体/差分懸念がないため追加Docker/QEMU全体検証は実行しなかった。30秒watchdog/nightly-2026-10-01/600秒ASan/80%/mask/custom orderingを変更せず、性能測定・別projectbackground停止も行っていない。
