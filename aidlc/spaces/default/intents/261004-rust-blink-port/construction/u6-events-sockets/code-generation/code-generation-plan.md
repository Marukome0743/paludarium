# U6 イベントとソケットのコード生成計画

## Summary

- Builds: Step19。製品は変えない。計画の古くなったTesting Contractを今の内容（`sha256:7ff27a24…`、方針は同じでproject層の学びが足されただけ）に置き換え、今の正式確認コマンドでU6を確かめ直す。
- Touches: この計画のTesting ContractとStep19の節だけ。製品・テスト・ほかの記録は変えない。
- Tests: 新しいテストの実行はない。独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpoint。Steps16〜18の結果は履歴として保持する。

## 今回の計画：Step19（Build and TestのLoop-back 1：Testing Contractの更新と再確認）

2026-10-17。U14の整数SSEのJIT（署名head 1ceae86c）とU1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。U6の担当のsource-manifestには、今回変わったファイル（U14のJIT・wasm・テスト、`crates/paludarium-wasm/src/abi.rs`、`mise.toml`）は含まれない。この計画の「## Testing Contract」は、memory（project.mdの学び）の更新で古くなっていたため、`aidlc engine testing-posture render` の出力に置き換えた。テストの方針（Methodology custom、Ordering、Standard、80%下限など）は変わらない。

- [ ] Step 19 — 製品・テスト・記録は変えない。今の正式確認コマンドでU6のcheckpointを確かめる。独立再レビューで、U6の記録が今のsourceと合っていることを確かめる。Steps16〜18の結果は履歴として保持し、今回の新しい実行とは数えない（NFR3、NFR9）。
- [ ] Step 20 — 再レビュー（iteration 2）のMinorへの対応（人のRequest Changes「Minor を直す」）。code-summary.mdの先頭に「現行Step19〜20（Loop-back 1）」節を足し、次を書く：(a) Testing Contractを今の内容に置き換えたこと、(b) U6の担当source（source-manifest）は12d6a2f6・1ceae86cの変更に含まれないこと、(c) Steps16〜18のNode・本物Safariの全102ケースの証拠は、U14の変更より前のmodule（`4482b157…`、head 11c033c7）に対するもので、1ceae86cから作るmoduleとは別物であること。1ceae86cのmoduleでの4環境の比較はU14 quality run 39030957672で行ったが、U6の102ケースは今のmoduleでは測り直していないこと、(d) 「記録が今のsourceと合っている」はレビューで記録とsource-manifestを照らした範囲であり、新しい実行ではないこと。traceability.jsonの分類・targetは変えない。正式sensor 2件を実行し、独立再レビューと今の正式確認コマンドでのcheckpointに進む。

## 前回のSummary（Steps16〜18）

- Builds: 承認されたU6追加検証をSteps16〜18で実行し、旧ブラウザ総数assertを現行ケース集合へ整合する。
- Touches: U6文書・検証記録、新しい専用診断CI/helper、u6-check.mjsの総数assert一行（103→102）。既存製品Rustとguest fixtureは保持する。
- Tests: 同一現行ソースのfresh Linux差分84件＋Tokio10反復、固定9ファイルcoverage80%以上、3OSのU6限定49件と品質検査、events/sockets各600秒ASan/LSan、同production wasmのNode/本物Safari全102ケース。strict guardと30秒制限を維持する。

## 承認された追加検証（Steps16〜18）

- [ ] Step 16: U6の82ケースと共有20ケースをケースIDで照合し、削除済み旧unsupported-tty拒否に由来するu6-check.mjsの総数assert一行だけを103から102へ整合する。U6ケース・期待値・比較条件を削除しない。専用診断CI/helperを準備し、現行入力集合と両lock、実使用compiler・ツール版・設定のbefore/after/currentを保存する。診断ファイルとassert修正も入力へ明示する。旧439入力の42変更・担当31中9変更・旧compiler相違を歴史として保持する。最新ツールの公式確認で追加設定変更が必要なら最小案を提示する。
- [ ] Step 17: 同一現行ソースの署名済みCIでfresh x86-64 Linux native差分84件とTokio10反復、既存9製品ファイルの同分母規則coverage80%以上、3OSのKernel u6_tests49件・ignored0とfmt/Clippy/依存4検査を実行する。kernel_events_u6/kernel_sockets_u6を各600秒以上ASan/LSanで検証し、instrumentation、sanitizer runtime・flags、実使用compiler、依存閉包、全入力・両lock、生ログ・実exitを保存する。入力30秒watchdog、kill/reap、既存mask・比較規則・測定分母を維持する。失敗やskipを合格にしない。
- [ ] Step 18: 同CI生成のproduction wasmとfresh native結果を用い、Nodeと本物Safariで共有20＋非threaded U6 82の全102ケースを実行する。module hash・ケースID・COOP/COEP/sharedMemory・停止と清掃・実exitと原本を結合する。Tokio/C66のwasm guest WorkerはU11境界として保持する。新CIの全入力・両lockと署名head/job/raw hashを結合して4成果物・strict source-manifestを更新し、正式検査・独立レビューへ渡す。新最終確認候補は構文確認までとし、変更承認後に実行する。先行Unitの保存証拠は一致範囲だけ再利用し、変更の影響があれば具体的追加案を示す。strict guard、80%下限、30秒制限を維持する。

## 今回の再確認（Steps13〜15）

- [ ] Step 13: FR2.4〜FR2.7/FR9.1、横断NFRと共有契約を確認し、現行担当ソース・両lock・実使用compiler・設定を保存する。旧e33cfbb4の439入力と31担当leaf、84native差分、Tokio10反復、9製品ファイルcoverage2352/2785、2ASan各601秒、Node/本物Safari各103件の証拠を個別に照合する。旧aeb7や修正前75pass/9failは歴史として保持し、現在の成功へ読み替えない。最新ツールは作業の区切りで公式情報を確認し、更新が必要なら具体的最小案を提示する。
- [ ] Step 14: 現行U6限定Kernel内部テストを `cargo test --locked -p paludarium-kernel --lib u6_tests::` で実行し、実件数・ignored・exitと原本を保存する。Linux fresh84差分・Tokio10反復、固定9ファイルcoverage80%、3OS品質、kernel_events_u6/kernel_sockets_u6各600秒ASan/LSan、本番Node/本物Safariの証拠について依存ソース・両lock・実使用compiler・設定・測定対象の一致範囲を確定する。U5の成功はU6全品質の代替にしない。不足は具体的な追加実行案として人へ提示し、重い追加CIや製品修正はこの段階では実施しない。
- [ ] Step 15: 実測結果と未検証をcode-summary・traceability・source-manifestへ反映する。要件原本と独立した担当割当を根拠に全要件をOK/Deferred/N/Aへ分類し、他Unit要件をU6実装済みと偽らない。正式検査・独立レビュー・承認済み最終確認へ渡す。既存確認コマンドが新U6証拠を検証できない場合は候補を具体化し、新承認後に実行する。strict guard、80%下限、30秒入力制限、比較maskと固定分母を維持する。Tokio・C66のwasm guest WorkerはU11境界であり、共有launcher成功と混同しない。ID競合の完全解消は実測範囲を超えて主張しない。

## Testing Contract

```json
{
  "version": 1,
  "methodology": "custom",
  "source": "team",
  "ordering": "命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
  "scope": "rust-blink-port",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "私たちはテストを各 Bolt の成果物の一部として扱います。エミュレータの正しさは「ネイティブの x86-64 Linux と同じ結果になるか」で決まるので、差分テストを中心に置きます。\n\n- **Methodology**: custom\n- **Ordering**: 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。\n\n補足：\n\n- **カバレッジ**（Q5）：行カバレッジ 80% を下限にします。測るのはネイティブの Linux です。あわせて「範囲内の命令のうち、差分テストが 1 件以上ある命令の割合」を記録します。決めた下限は Build and Test で下げません。\n- **差分テストの期待結果**（Q6）：期待結果は、**CI を実行するたびに x86-64 Linux のランナーで作り**、エミュレータの結果と比べます。期待結果をリポジトリに保存する方式は取りません。\n  - 比べるもの：命令の単位ではレジスタ・フラグ・メモリ、プログラムの単位では標準出力・標準エラー・終了コード。\n  - x86 で結果が未定義のフラグや値は比べません。命令ごとに「比べないもの」を表で持ちます。\n  - pid・時刻・乱数・アドレスなど、実行ごとに変わる値は、比べる前にそろえるか、比べる対象から外します。\n  - 段階 5 では、JIT ありと JIT なし（インタプリタ）の結果も同じ差分テストで比べます。JIT だけの意味論は持ちません。\n- **単体テスト**：層ごとに `cargo test` で書きます。テストやビルドの道具は外部のものを使ってよいです（Q1）。\n- **CI のゲート**（Q7）：\n  - 変更のたび（PR）：Linux・macOS・Windows の単体テスト、lint（`cargo fmt --check`、clippy の警告はエラー）、依存の検査（ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること、既知の脆弱性）、x86-64 Linux での差分テスト。通らなければマージしません。\n  - 段階ごと：その段階に入ったら、その段階の probe と aube の合格を必須にします。\n  - 夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）。失敗したら Issue にして直します。\n- **Safari**（Q12）：Safari での合格は、macOS の CI で本物の Safari を動かして確かめます。WebKit を使う別のテスト用ブラウザでは代えません。\n- **wasm**：paludarium が用意する起動用 JS とテストハーネスで、Node.js の Worker とブラウザ（Chromium 系・Firefox・Safari）で同じテストを動かします。テスト用のページには COOP/COEP の見出しを付けます。\n- **揺れるテスト**：スレッドを使うテストには時間切れの上限を付けます。揺れたテストは記録して直します。\n- 段階 5 の「JIT なしより速い」は、回数・統計量・差の大きさを要件分析で数値にしてから測ります。速さの測定は PR のゲートにしません。\n- Test Strategy は Standard です。量と種類はこの設定に従い、上の補足はそれに足すだけです。"
    },
    {
      "layer": "project",
      "text": "- 2026-10-08: U9公開型のconstructor移行後、外部6回帰・3compile_fail、既存Host7/Kernel8/Runtime8、署名head7069538fの3OS/差分/lint/依存/production wasm成功を取得。実Safari初回はsandboxからWebDriverへの接続が未成立、画面取得は674秒無応答で中断。期限を維持してhost権限でSafari27.0.1の14ケース16861ms成功、driver/server cleanupを確認。依存変更したsyscall_args/vfs_paths/load_elfは各601秒exit0、新155sourcepaths before/after一致、U9coverage82.66%。旧失敗と旧証拠を維持し、新commandは実行前に人の承認へ提示する。 (learned 2026-10-11) \n\n- 2026-10-08: U9の今回Steps8〜12の計画・要約を人が承認。公開型non_exhaustiveと外部生成APIの不一致修正、利用側の移行、外部crate回帰と変更後ソースのCI/production wasm/実Safari検証を実施する。旧Steps1〜7と既存Unit成果物は保持し、保存成功の新ソースへの読み替えを禁止する。canonical変更は具体化後に人の承認を取得する。 (learned 2026-10-11) \n\n- 2026-10-08: U7の承認済み計画・要約に基づき、成果物を保持して再確認した。4成果物とmanifestのハッシュ一致、sensor2件の成功、canonical検証exit0をredo-step32証拠へ保存。Windows/Linuxの保存済み有限観測を維持し、新規CIやSafariの再実行とは区別する。独立レビュー前に書き込みを停止した。 (learned 2026-10-11) \n\n- U4の既存成果物とLinuxのファジング・品質証拠を維持し、Windows追加テスト後の現在sourceを新しい承認済みcanonicalで照合する。限定sensor・同bytes再保存・5ファイルhash一致を新記録へ保存し、過去の実測を新規実行としない。 (learned 2026-10-11) \n\n- U2では実装と4成果物・manifestの内容を維持し、Windows追加テスト後の証拠照合だけを更新する。限定sensorと承認済みcanonicalの結果・同bytes再保存のハッシュ一致を新記録へ保存し、旧実行と区別して独立レビューへ渡す。 (learned 2026-10-11) \n\n- 人が指定したcode-generation redo後もU1成果物維持の指示を引き継ぐ。新しい計画承認と内容確認を記録し、4成果物を同bytesで保存して現行の限定検査と独立レビューを更新する。保存済み証拠の再照合を新CI・Safari実行と数えない。 (learned 2026-10-11) \n\n- ユーザー指示「U1の成果物は維持し、共有ソース変更後の完了確認を更新」に従い、U1の4成果物・manifest・製品コードの内容を維持して限定照合と独立レビューのみ行う。新しい検査コマンドは人の選択で正式登録済み。既存の実装・CI・Safari実行を繰り返さず、保存証拠の再確認を新試験と数えない。 (learned 2026-10-11) \n\n- Step39〜41（2026-10-08）：cloneの4flags全16組をSIGCHLDとsignal0の双方で同一C sourceで比較。local QEMUはmask0/SIGCHLDだけ成功、native実機Linuxは全32case成功、childexit42。QEMU10.2.3公開sourceのthread必須flags、fork許可flags、termination signal制限と一致する。LSanの直接停止はclone EINVALであり、独立ptrace ENOSYSを直接停止原因と混同しない。 (learned 2026-10-11) \n\n- Step40：production Sessionのwasm32はhostの無条件native依存によるerrno unsupportedで阻害。実CPU/MMU/decoder/typesの限定wrapperをNodeWorkerと実Safariで検証し、runtime/hello/本番launcher完成の根拠にしない。共有memoryなしと共有stdheap/入れ子Worker未実装を証拠の境界として保持する。 (learned 2026-10-11) \n\n- U2 Step36〜38: approved native Linux fork CI ran four unchanged targets at signed head77663b7982857cba841c91d4b23b44287bb8e29b (run37736496982) CPU2104569/MMU4900201/decode86019257/load_elf16609257 each601seconds and exit0 with ASan/LSan enabled. Artifact verifier proved127source paths identical before/after/baseline/current host; independent95claims check also matched. This is bounded U2 fuzz evidence, not arbitrary-input/wasm/other-unit assurance. (learned 2026-10-11) \n\n- U2 Step33〜35検証済み：同一同期snapshotでCPU636751/MMU910789各601秒ASan実行、両LSan終了fatal/exit1。最小C ASanも同runner2回exit1、製品非依存の終了検査問題を再現した。source before/after cmp0、host127実ファイル一致、32AppleDouble metadataはraw記録に保持。QEMU制約は原因候補の推測。品質設定を弱めず4GAP保持、証拠はU2 verification/step35-current-asan-proof.jsonとraw logs。required-sections pass、traceabilityは4GAP fail。U1/source/CI変更なし。 (learned 2026-10-11) \n\n- U2承認済みStep30〜32をSummary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3後に実施。95claims全て署名済みaf9b bytes一致、旧95snapshot2差異/127snapshot9差異は履歴化。保存CI7+native4jobs、差分38/並行10、source名とCPU14/decoder9/MMU9/types1/kernel1の実行証拠を独立照合し、新実行としない。既存44traceのstatus/target保持、fallback48追加で92IDs。FR5.4はU5 native/U11 wasm担当。製品/CI/U1成果物変更なし。 (learned 2026-10-11) \n\n- 人が選択したU1完了検査verify-native-ci-with-safari-report.pyはexit0。元のverifierを保持し、承認済みSafari文書と実測証拠を厳密hashで照合する限定検査。CI7jobs/native4jobs成功、162 application filesを署名af9bに照合。traceability PASS/findings0、required-sections PASS/H2=9。旧canonical exit1は履歴と区別し、新検査の実ログを保存。独立レビューとUnit完了確認は未完了。全記録書込を終了して固定する。 (learned 2026-10-11) \n\n- U1 Step35〜37のSummary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRを保持し追加60FR/NFRをOK9/Deferred40/N/A11へ分類、107IDs/107対応。traceabilityとrequired-sectionsはpass true。CI2参照名を実在名へ修正。本物Safari27.0.1/macOS27.0.1の単独wasm spikeはexit0、値42、wait201ms/total216msで5秒以内。全体エミュレータ/入れ子Worker/共有stdヒープとU1現行600秒fuzzは未検証。 (learned 2026-10-11) \n\n- U1 Step32〜34は今回のPlan ApprovalとSummary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後に記録を再確認。af9b739dの保存CI11jobsと現行162 application filesをverifier exit0で照合し、U1 103claims/108filesは107一致・既知非ビルド.gitignore例外のみ。旧4d52/source-bytes-currentは履歴であり現行一致を意味しない。製品変更・新規重い試験なし。 (learned 2026-10-11) \n\n- 工程全体の差し戻し後はU1のStep32〜34だけを実行する。ユーザーの製品コード維持の指定を守り、旧4d52証拠の時点表示と現行af9bの照合記録を更新する。計画承認と内容確認を新attemptで記録済み。 (learned 2026-10-11) \n\n- U9は直接FR4/FR4.1/FR4.2に対応する7手順で計画した。Unit固有設計がないため既存C2/C8/C10境界を使い、U7承認を維持する。Linux実機の期待結果を実装前に取得し、coverage・fuzz・各OS実機端末結果を過去のCI成功から推定しない。 (learned 2026-10-11) \n\n- U4 redo Steps22〜24は107claims/snapshotと4d52CI、内部76/差分44/15traceの再確認に限定した。新内容確認後に実4producesとmanifestを保存し、FR9.3/NFR2/NFR3の現在600秒ASan GAPとwasm未検証を保持した。製品変更・新testなし。レビュー依頼前に全書込を終了し、引渡し後はsource/成果物/SCM snapshotを固定する。不整合原因は未確定。 (learned 2026-10-11) \n\n- U2 redo Step27〜29は現在95claims/95snapshot/CI対象127paths一致、44traceと11jobs成功の再確認に限定した。新内容確認後に実4producesとmanifestを全保存し、現在600秒ASanの4GAPとwasm未検証を保持した。製品変更・新testなし。レビュー前に全書込を完了し、引渡し後はsource/成果物/SCM snapshotを固定する。 (learned 2026-10-11) \n\n- U1 jump redo Step29〜31は103claims/108filesの現在snapshot一致、CI4d52一致107filesと別作業.gitignore例外を再確認した。新Summary Confirmation後に実4produces plan/instructions/summary/traceabilityとmanifestを全て保存し、旧fuzz/wasm/Safari未検証を保持した。製品変更・新testなし。レビュー前に日記を含む全書込を終え、以後source/成果物とSCM snapshot操作を固定する。前回不整合原因は未確定。 (learned 2026-10-11) \n\n- U4新attempt Steps19〜21は107claims/snapshotの4d52一致、保存CI11jobsと内部76/差分44の再確認に限定した。FR9.3/NFR2/NFR3の現在600秒ASan GAPを保持し旧完走を現在passへ流用しない。製品変更・新testなし、レビュー前に日記を含む全書込を終了し引渡し後はsource/成果物/SCM snapshotを固定する。前回reviewterminal拒否の原因は未確定。 (learned 2026-10-11) \n\n- U2新attempt Step24〜26は95claimsと保存snapshotのbytes一致、4d52 CI7+4jobs成功と差分38/並行10の証拠再照合に限定した。旧600秒ASanを現在passへ流用せず既存4品質GAPを保持し、製品変更・新testなしとした。日記と必要記録をレビュー依頼前に確定し、引渡し後は全書込みとSCM snapshot操作を停止する。 (learned 2026-10-11) \n\n- U1新attempt Step26〜28は製品再実装ではなく記録再確認に限定した。103claims/108filesのsnapshot一致、4d52 CIとの107files一致を確認し、別作業.gitignore相違だけを明示した。保存済みU1差分16・coverage92.57%/82.71%を再利用し、新実行や未検証wasm/Safari・600秒ASanの合格へ読み替えず、レビュー依頼前に全記録を固定する。 (learned 2026-10-11) \n\n- U4の現在CI証拠は107 source claimsのbytesが署名済み4d52be0aと一致する範囲で再利用した。旧37paths中15pathsが相違し、syscall_args targetとmmu_ops依存sourceが変わっているため、旧各600秒ASan完走を現在passへ流用せずFR9.3/NFR2/NFR3をGAPとして保持した。 (learned 2026-10-11) \n\n- Windows初回fixture交換は共有違反32でchild101。fixtureハーネスだけに有限retryを加え、30秒・1000反復・交換>0・outside不変条件は維持した。中間成功はCRLF差異を発見して履歴に限定し、checkoutのみLFへ固定した最終run37765054790/head8cba60d9で1000反復/55交換/473共有違反/881ms/child0/strictcleanup、154paths厳密一致を確認。旧canonicalはnative_fs.rsのテスト差異でexit1を保持。旧全検査を維持しexact Windows test-only差異と最終CI証拠を追加する新checker案は手動exit0、正式command選択は独立reviewとユーザーの保護された承認で扱う。 (learned 2026-10-11) \n\n- Windows未検証のU7 checkpointをユーザーがRequest Changesで拒否し、所有fork CIでの実測を指定。新Steps28〜32をPlan Approval/Looks correctで承認し開始した。Windows-only test blockと一時fixtureに対象を限定、親テストの30秒whole-child kill/reapとstrict cleanupを要求する。既存Linux実行コードと意味論は保持し、保存ASan/coverage証拠は差分分類・hash再照合で再利用する。新test bytesでcanonicalが拒否すれば記録して正本commandの保護された承認へ返す。 (learned 2026-10-11) \n\n- Windows fixture内の隔離回帰を担当へ依頼したところ、安全性チェックで2回実行前停止した。Windows作業の再試行を止め、実行できなかった理由を保持し、影響しないLinux既存vfs_paths600秒ASan/LSan・U7限定80%coverage/diff_u7のみ実測する指示へ限定した。main source変更なし、署名Verified eafa5ac6の診断CI37760390069を起動。Windowsを検証済みに変更しない。 (learned 2026-10-11) \n\n- ユーザーはU7のWindows race本体・現行vfs_paths ASan/LSan・U7限定coverageもできる限り実測するよう訂正した。変更後Steps21〜27のPlan ApprovalとLooks correctを記録して開始。Windows test-only回帰とisolated署名診断CIを使用し、1000反復/attack交換1回以上/30秒、ASan600秒、coverage80%を保持する。権限不足・実行失敗は成功へ読み替えず、製品不具合は再現証拠と別計画へ返す。U9公開型修正は後続として保持。 (learned 2026-10-11) \n\n- U4の対応表検査は初回48 findingsで、ASan未検証3項目と共有要件45項目の分類不足を示した。以前のユーザーの後続Unitを含む対応表不一致修正依頼と現在Steps26の全割当FR/NFR整合に従い、共有要件とUnit定義を根拠にOK/Deferred/N/Aへ分類する。製品機能や検査設定を変更せず、ASan実測の適用範囲を守って再検査する。 (learned 2026-10-11) \n\n- ユーザーはU4の未検証ASan項目を保持する方針に変更を要求し、syscall_args/mmu_ops各600秒の実機検証を選んだ。承認済みSteps25〜30ではfork診断CIでASan/LSanを実行し、現在source一致・生ログ・実行時間・exitを確認した対象だけGAPを更新する。製品・U1/U2成果物と品質下限は保持し、U9の指摘は後続Unitで継続する。 (learned 2026-10-11) \n\n- U2の現在attemptは承認済みStep49〜51の証拠照合と記録更新に限定する。署名済み178da99eと現在source、保存済みCI・4対象ASan/LSan・production wasm Node/実Safariの実測範囲を確認し、新実行と区別する。U4/U9の修正依頼は後続Unitへ維持する。 (learned 2026-10-11) \n\n- ユーザーの「3の両方です。」に従いU1担当説明と後続U4/U9の指摘を修正対象とした。承認済みStep38〜40ではU1のFR5.4にU5を追加しDeferredを保持する。unit-major serialの順序で後続U4/U9は各Unitの計画・検証で扱い、U1の完了確認で解消済みへ読み替えない。 (learned 2026-10-11) \n\n- U1はユーザー指示に従いKeepとし、redo後の新Plan Approval/内容確認から4成果物を同一bytesで再保存した。plan/instructions/summary/traceabilityのbefore-after SHA256一致、source-manifest不変。共有ソース変更に対する再レビューと承認済み完了確認だけを更新し、既存製品や旧証拠は変更しない。 (learned 2026-10-11) \n\n- U2 Step42〜48で実 production Session wasm と C12 launcher を実装した。共有 Rust allocator/Arc/Mutex/独立stackTLSを nested Worker で実測し、trap時はlockを残す可能性があるためfactory全体を破棄する。Nodeと本物Safari各14件、CI生成同一moduleのSafari、3OS/80%品質gate、4target各601秒ASan+LSan終了0を確認し、任意guest/guestclone-futex全意味論/JIT/他browserは未検証として境界を残す。 (learned 2026-10-11) \n\n- U9の実装前期待結果はfork実機CIで取得し、Docker VMMの結果は診断と区別した。現行CIは11ジョブ成功し署名済みaf9b739dと162ソースが一致。U9対象クレート82.55%と追加実行可能行122/130（93.85%）を別の分母で記録し、現行ASan・非Linux実機端末は未検証を保持した。 (learned 2026-10-11) \n\n- ユーザーの希望に従いDocker VMMを維持し、実機Linuxを差分期待結果の根拠にする。QEMU固有のENTER faultと速度差は実機不具合と分けて記録する。 (learned 2026-10-11) \n\n- REP faultのnative期待値にはCPU差があった。Intel実機の初期flags復元とAMD実機の成功反復flags保持を観測し、明示モデルとnative差分fixtureで扱った。productionにhost検出は加えない。 (learned 2026-10-11) \n\n- 2026-10-08：承認済みHost追加修復後、Windows Host25件・macOS既存suite・実機Linux全workspaceが通過。Windows Runtime mountテストのcleanupだけがOS error32で残った。MountedFsとSessionの双方がcapability Arcを保持するため、削除前に両方dropする2行を追加計画24bとして承認・内容確認済み。全体/U1 coverageは直前sourceで92.57%/82.70%。最終sourceのCIで再確認し、古い結果を最終sourceへ転用しない。 (learned 2026-10-11) \n\n- User chose 追加調査 for U3 inventory. Resume Step2 fixed-binary comparison, encoding classification and bounded native-completion investigation in signed fork Linux CI before product implementation preserve approval contract and existing Unit artifacts. (learned 2026-10-11)"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "custom",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Custom ordering - 命令・syscall・ゲストのプログラムの単位では、実装の前に差分テストのケースを用意してネイティブの x86-64 Linux で得る期待結果を先に決めてから実装し、デコーダとの接続・MMU・ELF の読み込み・仮想ファイルシステムなどの内部の部品は、実装の後にその層の単体テストを書いて実行する。",
      "Implementation and tests - preserve that exact ordering; do not convert it to layer-local TDD.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cc8e6bbb985d32c580aff1d457ccafb5f05a4b442140eb6cb6303d51ca2ba418",
  "contract_sha256": "sha256:7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5"
}
```

## Scope and sources

requirements.mdのFR2.4〜FR2.7と横断FR9.1/NFR1〜4/7〜9、unit-of-work.mdのU6、components.mdのEpollInstance/EventCounter/SocketPairEnd、C2 Host/C4 MMU/C6 VFS/C8 Kernelを根拠とする。ユーザーストーリー工程は省略されたため各stepを直接FR/NFRへ対応させる。u6-scope-questions.mdの3回答とsummary確認を設計根拠とする。

既存Host clockとepoll期限でtokio timerを支える。timerfdは対象probeの実使用が確認された場合だけ、nativeケースを先に追加して実装する。AF_UNIX SOCK_STREAMとNONBLOCK/CLOEXECを対応する。DGRAM/SEQPACKETは今回必須対応型ではなく明示エラーと対応外表へ記録する。AF_INET/AF_INET6は全HostでEAFNOSUPPORT。通信可能nativeとの不一致は承認済み隔離ポリシー例外として拒否テストで確かめる。

Kernelがevent counter、epoll interest/ready状態とsocket endpoint/bufferを所有し、ホストepollへ転送しない。Hostはclock/wait/notifyのみ。U5のThread/futex/signal owner receipt、U7の共通fdとdup/close/fcntl、U9のstdioを保持する。別プロセスfork/execはU8、probe全量統合はU10、wasm guest Worker接続はU11。新Web/API/DB/公開deployはない。

## Steps

- [ ] Step 1: FR2.4〜2.7/NFR1。現Kernel Files/FileHandle/ThreadGroup/Host wait、poll/selectの既存範囲と対象tokio/UnixStream syscall実使用を限定調査し、U6変更path・syscall/flags/対応外表・guest ABIを記録する。open file description（OFD）identityとfd番号を区別する設計、lock順序と待機登録/再確認/通知の不可分境界を確定する。U6変更製品fileのLinux coverage分母をここで明示・固定し、以後減らさない。
- [ ] Step 2: FR9.1/NFR7。tests/guests/u6/build.sh、scripts/u6-native-observe.pyとu6-runner-test.py、harness/tests/diff_u6.rs、Kernel u6_tests filter、.github/workflows/u6-native-diagnostic.ymlの最小runnerを用意する。下記unit commandの実行可能性を先に確認し、0件成功を検証としない。全processの30秒watchdog/process-group kill/reap、stdout/stderr/exit/timeoutとmanifest/binary hashを保存する。
- [ ] Step 3: FR2.4〜2.7/NFR1。製品変更前に48件以上の有限guestケースとCOMPARISON.mdを用意する。eventfd counter/semaphore/8-byte ABI/overflow/EAGAIN、epoll LT/ET/ONESHOT/ADD-MOD-DEL/error/ready公平性、fd dup-close-reuse/OFD寿命、socketpair双方向/partial IO/EOF/shutdown/EPIPE/NONBLOCK/CLOEXEC、期限/signal/kill/masked signalとmetadata通知を含める。network拒否のpolicy例外を別に記録する。順序はchannel/guest handshakeで確定し、生fd/TID/時刻/順不同event集合を正規化する。各ケース名・件数・比較対象を固定する。
- [ ] Step 4: FR2.4〜2.6/FR9.1。fixture-only sourceを親へpush-readyとして渡して停止する。親がsigned Linux CIで全native期待を取得しraw整合を確認後、明示goを受けて製品へ進む。静的expected fixtureを実行oracleに使わない。追加syscall必要時も追加ケースnative先行の順序を守る。
- [ ] Step 5: FR2.4/NFR2。Kernel events部品とeventfd2を実装しread/write/flags/dup/status/closeへ接続する。counter上限・semaphore・blocking/NONBLOCK・EFAULT/errno・poll readinessをnative観測へ一致させる。実装後に単体8件以上を追加して実行する。待機中にMMU/fd table/event lockを保持しない。
- [ ] Step 6: FR2.6/NFR2/4。Kernel socketpair endpointsを実装しSOCK_STREAM/NONBLOCK/CLOEXEC、双方向buffer、partial IO、EOF、shutdown、peer close/EPIPEとsignal、read/writeおよび必要なsend/recv APIへ接続する。buffer方式とbackpressureのnative比較規則を明記しNFR5の任意ゲスト資源上限を新設しない。実装後にendpoint単体8件以上を実行する。AF_INET/AF_INET6をHostへ接続せずEAFNOSUPPORTで拒否する。
- [ ] Step 7: FR2.5/NFR1/2。自前epoll create/ctl/waitと対象で必要なpwait、readiness通知を実装する。LT/ET、ONESHOT rearm、ready→not-ready→ready、maxevents、公平性、data64、error/hangup、timeoutとsignal maskをnativeへ一致させる。通知登録前後の再確認でlost wakeを防ぎ、実signal/group終了/外部停止とtimer metadataを区別する。実装後にepoll単体8件以上を実行する。
- [ ] Step 8: FR2.4〜2.6/NFR7。OFD identityによるepoll登録、dup/fcntlでの同一description共有、closeと最後の参照、fd再利用、CLONE_FILES共有/非共有tableに接続する。lock順序・owner ack/send競合・通知先行・timeout勝者を検査する。実装後にfd/readiness境界単体8件以上と同期統合8件以上を実行し、既存U5/U7/U9回帰を保持する。
- [ ] Step 9: FR2.4〜2.6/FR9.1。static-muslのU6限定tokio multi-thread timer guestとUnixStream::pair guestを現sourceで通す。実使用syscallを記録し、timerfdが必要ならケース追加→fixture-only native観測→go→実装の順を守る。全有限ケースで毎CI fresh nativeとの差分を実行し、比較件数をrunner/build/harness/manifest/checkerへ一致させる。後続Unit依存によるprobe全量未達は具体的に分け、U6対象の失敗を後続依存へ隠さない。
- [ ] Step 10: NFR2/3/8/9。U6限定quality CIとcoverage/fuzz設定を作る。固定nightly/locked、3OS単体/fmt/clippy警告エラー/依存検査、固定U6製品file分母のLinux coverage80%以上を確認する。kernel_events_u6/kernel_sockets_u6各600秒ASan/LSan、exit0/lock before-after/current/raw artifactを確認する。失敗・未知CPU profile・未検証を記録し、閾値や対象を減らさない。
- [ ] Step 11: NFR1/7/FR9.1。親が安定sourceをsigned pushし同headの全差分/quality/coverage/fuzz原本を収集する。現production wasmにU6 guestを含む限定回帰を追加し、製品LauncherでNode Workerと実Safariの同case集合、module hash、COOP/COEP/sharedMemory/cleanupを検証する。U11未接続のguest threadingは明示境界として扱い、既存共有heap/launcher成功とU6 guest clone成功を混同しない。先行Unit sourceと歴史証拠を保持して共有変更後の現source回帰を確認する。
- [ ] Step 12: FR9.1/NFR1。code-summary、traceability.json、strict source-manifest（stage/unit/version/writes、repo/pathのみ）とread-only証拠checkerを作る。全notesとMarkdownを実際のhead/件数/coverage/fuzz/module/raw値へ照合し、現source inventory・歴史保存・commit/run/job/stream/hashを結合する。候補checker exit0後に成果物freezeを親へ渡す。親の新しい独立レビューとcanonical verification、人の完了確認を受ける。子はreviewやlifecycleを承認しない。

## Validation and boundaries

内部4境界に各8件以上、統合8件以上を最低計画量とし、必要な追加回帰は減らさない。48nativeケース以上の具体一覧はStep3で製品変更前に固定する。tokio/UnixStreamには別のE2Eケースを加える。new fd種別が通常VFS/stdioのread/write/fcntl/stat/pollへ与える影響と、SignalInbox通知種別を必ず検証する。

Hostネットワーク・epoll転送は禁止。未知flags/未対応操作は対応表へ明示する。Linuxのerrnoやrestart/timeoutを一般説明から推定せずnative実測を優先する。資源上限・速度目標・機能追加をついでに導入しない。測定前にcoverage分母を固定し、80%下限とfuzz600秒/30秒watchdogを変更しない。CI証拠未取得を成功にせず、製品エラーとguest errno/signalを区別する。
