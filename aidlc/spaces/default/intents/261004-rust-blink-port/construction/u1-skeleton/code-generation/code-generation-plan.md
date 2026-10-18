# コード生成の計画（u1-skeleton）

## Summary

- Builds: 今回の実行対象はStep74。U15のStep22〜28（push、head 27d05de1）でU1のmanifestにあるworkflowが変わり、正式な確認コマンドがentry-f・binding-e06fに替わったので、U1の確かめ直し（review-48、READY）の指摘のうちU1の記録で直せるもの（R-34のMajor、R-35、R-31〜R-33）を直す。人はcheckpointでRequest Changesを選んだ。
- Touches: U1の記録だけ（code-summary.md、unit-test-instructions.md、source-manifest.json、`verification/loopback1-next/README.md`）。製品・CI・workflow・ほかのUnitの記録・traceability.jsonのstatusとtargetは変えない。R-36（ルートの `README.md` の夜間の確認の説明）は製品のファイルで、直すと正式な確認コマンドがhead 27d05de1との違いで拒否するため、次の製品の変更のときにまとめて直す。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## Step74（確かめ直しの指摘を記録で直す）

2026-10-19 JST。人の指示：「ワークフローの順で進めてください。U1 の確かめ直しから始めて、ファイルが変わった Unit を順に確かめ直し、U15 のレビューと完了確認、U11 の確かめ直しまで進めてください。」。U1の確かめ直し（review-48、READY、Major 1・Minor 2）の後、checkpointで人がRequest Changesを選んだ（先にU1の記録を直す）。

- [x] Step 74 — **確かめ直しの指摘を記録で直す**。(1) R-34（Major）：code-summary.mdの先頭に「現在の状態（2026-10-19 JST、Step74）」節を足し、今の正式な確認コマンドは `verification-command.txt` の U15 `entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用）で、entry-cは2026-10-18〜19の間の正式なコマンド（履歴）であることを書く。U15のStep22〜28でU1のmanifestにある `ci.yml`・`nightly.yml`・`u14-quality.yml`・`u1-u14-source-bound.yml` が変わり、`native-diagnostic.yml`・`u1-frame-diagnostic.yml`・`u1-source-bound-verification.yml` が消えたこと、27d05de1のCI 8 runがすべて成功したこと（U12は人が認めた1 jobの再実行）、U1の製品のコードは変えていないことを書く。既存の「現在の状態（Step73）」節は見出しを「履歴：…（作成時の見出しは「…」）」にする（本文は変えない）。unit-test-instructions.mdの先頭に「今回のStep74」節を足し、checkpointはentry-f・binding-e06fで確かめることを書く。「今回のStep73」の見出しは「履歴：Step73（作成時の見出しは「今回のStep73：…」）」にし、15行目の期待（entry-cのexit 0）はその時点のものであることを注記する。(2) R-35：source-manifest.jsonのwritesから、27d05de1で消えた3つ（`.github/workflows/u1-frame-diagnostic.yml`・`native-diagnostic.yml`・`u1-source-bound-verification.yml`）を外し、外したことと理由（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）をcode-summary.mdの新しい節に書く。(3) R-31：`verification/loopback1-next/README.md` の冒頭に「2026-10-18から履歴。今の正式な確認コマンドはU15の `entry-e3c29d1d/entry-f.py`（binding-e06f）」と1行足す。(4) R-32：Step73の節の5行目の「計画・unit-test-instructions.md は変更していない」は、その時点の事実と食い違うので、新しい節に「Step73では計画と手順書にもStep73の節を足した」と訂正を書く（履歴の本文は変えない）。(5) R-33：手順書の新しい節で、checkpointの結果（exitと出力のフォルダ）はcheckpointの記録が持つことと、entry-fが `aidlc/` の中を比べない（README「binding-e06f」の節）ことを根拠として書く。(6) R-36はこのStepでは直さず、新しい節に「次の製品の変更で直す」と書く。traceability.jsonのstatusとtargetは変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR3、NFR8。

## 前回のSummary（Step73）

- Builds: Step73。残しているMinor 2件（独立再レビュー review-45 の R-27・R-28）を記録で閉じる。2件とも `verification/loopback1-next/new_candidate.py` についての指摘だが、正式な確認コマンドは2026-10-18にU15の新しい入口 `entry-e3c29d1d/entry-c.py` に替わり、new_candidate.py はもう実行されない履歴になった。そのためcheckerの中身は変えず、限界を記録に書いて閉じる。
- Touches: U1の記録の `verification/loopback1-next/README.md`（「この方法の限界」に1項目）とcode-summary.md（現在の状態の1節）。new_candidate.py・binding・回帰・製品・CI・ほかのUnitの記録は変えない。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-c.py）でのcheckpointがexit 0になることで確かめる。

## Step73（残しているMinor R-27・R-28を記録で閉じる）

2026-10-18 JST。人の指示：「先に修正しましょう。提案通りお願いします。」（Safariの直し・CIの整理・残しているMinorをまとめて直す。U1・U14はそれぞれの記録のMinorだけを直す）。

- [x] Step 73 — **R-27・R-28を記録で閉じる**。(1) `verification/loopback1-next/README.md` の「この方法の限界」に、次の2点を1項目として足す：R-27（Step72で足した verify_module_receipt と verify_ci_jobs の一部の検査〔receiptのjob ID、artifactのcreated_at、attempt 2で再実行されたjobの集合〕には拒否の回帰が無い）、R-28（result.jsonのclaim_scopeの performance_1ceae86c.scope には、artifactにsource digestが無くmetadataのheadで結び付けている限界が書かれていない）。あわせて、new_candidate.py は2026-10-18から正式な確認コマンドではなく（今はU15の `entry-e3c29d1d/entry-c.py`）、中身は変えずに履歴として残すことを書く。(2) code-summary.mdの先頭に「現在の状態（2026-10-18 JST、Step73）」節を足し、上と同じことと、U1のcheckpointは entry-c.py で確かめることを書く（既存の節は履歴として残し、見出しに「履歴：」を付ける）。traceability.jsonのstatusとtargetは変えない。

## 前回のSummary（Step72）

- Builds: 今回の実行対象はStep72。人が採用した新しい正式確認コマンド（Step71）について、再レビュー（iteration 4）のMinor 5件と、再レビュー（iteration 5）の指摘2件を直す。性能測定のmoduleを1ceae86cのbuildに結び付け、CIをjobの単位で確かめ、同じheadのattempt 1の失敗を記録し、拒否の回帰を9件足して29件にし、古い記録を直す。
- Touches: U1の記録の `verification/loopback1-next/`（checker・新しいbinding・証拠JSON・回帰・README.md）、U1のcode-summary.md・unit-test-instructions.md・traceability.json。コマンド行は変えない。製品・CI・lock・mise.toml・.gitignore・ほかのUnitの記録・旧verification原本は変えない。
- Tests: 新しいコマンドがexit 0、回帰29件がすべて期待どおり、正式sensor 2件、独立再レビュー。checkerの中身が変わるので、修正後のcheckerを人にもう一度採用してもらってから、U1のcheckpointを検証する。

## 前回のSummary（Step71）

前回の実行対象はStep71（2026-10-17、Build and TestのLoop-back 1）。U14のJITの改善（整数SSE、署名head 1ceae86c）とmise.tomlへのnpmの記載で、採用済みの正式確認コマンド `r05-r11-repair-01/final_candidate.py` がexit 1（compiled source changed）になった。このコマンドはU1の記録にあり、U1・U11・U14のcheckpointで使う。人はU1のcheckpointでRequest Changesを選び、新しい正式確認コマンドをU1のStep71として作ることを指定した（「U1 で作る（推奨）」）。

- Builds: 新しい正式確認コマンドの候補を `verification/loopback1-next/` に作る。旧コマンド・旧binding・旧失敗の原本は変えずに使い、違いは次だけにする：(a) 変わった14個のcompiled sourceを、署名head 1ceae86c のbytesと一致する新しいSHA-256で許す（ほかの209個は旧い固定のまま）、(b) mise.tomlは旧いbytesに `"npm:npm" = "12.2.0"` の1行を足したものだけを許す、(c) 1ceae86cのCI（PR・U12・U13・U14 quality・fuzz・source-bound）の成功と、正式な性能測定の原本（FR8.3合格）を束ねる。後でU11のSafariの2ファイル（U11 Step29）を、新しいbinding fileだけで足せる形にする。
- Touches: U1の記録の `verification/loopback1-next/`（新しいcheckerとbinding、拒否の回帰、README.md）、U1のcode-summary.md・traceability.json（今回の再レビューのMinor 2件への対応：今のsourceとの一致の記述の更新、`ExecutionBridge`・`JitState`・`STATE_BYTES` がC9の外のU14の内部であることの1文）。製品・CI・lock・mise.toml・ほかのUnitの記録・旧verification原本は変えない。U14の固定3ファイルは、今のbytesのまま束ねる（U14の記録の更新は、U14の順番で新しいbindingを足して行う）。
- Tests: 新しいコマンドがexit 0、旧コマンドがexit 1（理由を記録）。拒否の回帰（ほかのcompiled sourceの変更、許した14ファイルの別のbytes、ファイルの欠落、別のhead、CIの欠落・失敗、mise.tomlの別の変更、.gitignoreの別の変更、性能の原本のhash違い、produceの変更）がすべて拒否する。正式sensor 2件、独立再レビュー。そのあと、新しいコマンドの採用を人に提示し、承認を受けてからU1のcheckpointで実行する。

## 前回のSummary（Steps67〜70）

前回の実行対象はSteps67〜70（独立レビュー指摘R-05／R-11／R-13への記録対応と、その再レビュー指摘R-14／R-15への追記）。Steps1〜66の成果・旧検証・失敗原本は保持する。製品コード・CI・guestの変更と新しい性能測定・公開・tag送信は含まない。初回nativeクラッシュのcore欠落は歴史的限界として保持し、解消とは記載しない。

- Builds: U1記録4成果物のうちcode-summary.md／unit-test-instructions.md／traceability.jsonを、採用済み正式検証コマンド `r05-r11-repair-01/final_candidate.py`（binding-v4 SHA256 `1df65928…`）と現 sourceでのexit 0実行原本、R05の修復証拠、R11の現行設定の適用範囲へ整合させる。
- Touches: `construction/u1-skeleton/code-generation/` のcode-summary.md・unit-test-instructions.md・traceability.json（verification_context の追記）。アプリケーション source・source-manifest.json・旧 verification 原本は変更しない。
- Tests: 新規テストなし。採用済み正式コマンドの再実行（exit 0、`source_compatibility: PASS`／`U15_acceptance: GAP`）、required-sections／traceability sensor、独立再レビュー、checkpoint 再検証と人の完了承認。0件の手元 diff_u1 を Linux 証拠と呼ばない。

## 目的と範囲

U1 は、ネイティブの Linux で C と Rust の static-musl の hello world を最初から最後まで動かす細い一本です。合わせて、wasm のスレッドの確認を行います。

上流の成果物：
- `construction/u1-skeleton/functional-design/`（functional-spec.md・rules.md・entities.md）
- `construction/u1-skeleton/nfr-requirements/`（security-requirements.md・tech-stack-decisions.md）
- `inception/contract-design/contract-summary.md`（C1〜C11）
- `inception/units-generation/unit-of-work.md`（U1）

アプリケーションのコードはワークスペースの直下（`crates/` など）に置きます。記録のディレクトリには置きません。

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

## 手順

今回の変更要求「原因調査と修正をお願いします。」は、再レビュー要求と現在の計画承認が一致せず停止したことへの対応である。以前のチェック済み手順は履歴として保持する。今回の追加実行はStep 44に限定し、未解決の製品課題を修復済みと扱わない。

### Step 44：差し戻し後の承認と再レビューの整合

### Step 45：全Unitやり直し後のU1再確認（今回の実行）

- [x] 新しいstage attemptで既存回答を読み、U1の範囲と未検証項目を内容確認する。既存製品を照合し、必要がなければ再実装しない。旧レビューと旧承認を今回の証拠へ転用しない。
- [x] 今回の内容確認後に計画・検査手順・code-summary・traceabilityを保存し、source-manifestの担当と現行bytesを確認する。以前の検証結果は履歴として区別し、既存の承認済み検証コマンドで現在値との対応を確認する。
- [x] 正式レビュー要求、reviewer起動・結果記録、checkpoint検証・人の承認、次のUnitへの遷移を順に確認し、生出力と終了コードを残す。停止が再発すれば失敗箇所を明示する。U1経路成功を並行セッションのID競合の完全解消と呼ばない。guard strictと品質下限を維持する。

Step 44は前attemptの停止検証計画であり、今回の実行入口はStep 45。2026-10-10に標準jump reopenがstate_updated=true/audit_appended=trueを返し、全11対象UnitのCode Generationを正式に再開した。

追加の変更要求：「停止原因の完全解消は未検証　ここを検証して下さい。」。承認の質問が表示されたことだけでは合格にしない。

- [x] doctorとその診断が指定するhooks-healthを確認し、日時・版・実行コマンド・終了コード・拒否出力を今回の検証記録へ保存する。2026-10-10のdoctorはexit 0、0 problems/3 warnings、runtime 2.11.0であり、過去の停止記録が残っている。この結果だけでは停止原因の解消を示さない。
- [x] 新しい計画承認後、標準CLIのbrief、現在のsource/artifactに結び付くreview要求、正式なreviewer起動・結果記録、次のcheckpointへの遷移を同じセッションで順に実行する。各段階の出力を保存し、ID不一致・承認失効による拒否・同じ指示への無進行ループを失敗とする。拒否を隠す環境変数、guard無効化、runtimeファイルの手編集は行わない。
- [x] 再開後にも同じ承認の質問が不必要に再表示されず、次の作業へ進むことを確認する。今回の1経路成功は「今回の復旧を検証済み」とし、並行チャットや別Unitの再現条件を実行していない場合は「完全解消は未検証」と残す。失敗時は再現条件と限定修正案を提示し、製品テストの成功で停止問題の合格を代用しない。

- [x] 現在の計画・検査手順・Testing Contractへの新しい計画承認を取得し、標準CLIのbriefが成功することを確認する。guardはstrictを維持し、承認記録やreceiptを手編集しない。
- [x] 既存の承認済み検証コマンドと現行source・署名CIの対応を確認する。過去の成功を今回の実行結果と区別し、不一致があればファイルと差分を報告して限定修正を計画する。U1の既存製品と後続Unitを再実装しない。
- [x] 全記録を確定して現在のartifact/sourceに結び付く独立レビューを取得する。再レビュー要求とplan approval guardの食い違いは観測済み、失効の具体的原因は未特定と記録する。標準経路で再度拒否された場合はその出力を保存し、設定を緩めて通過させない。

各手順の括弧内は、対応する要件・ルールです。

### Step 1：ワークスペースの土台

- [x] ルートの `Cargo.toml` に Cargo のワークスペースを作り、次のクレートを `crates/` の下に置く：`paludarium-types`、`paludarium-decoder`、`paludarium-mmu`、`paludarium-cpu`、`paludarium-loader`、`paludarium-vfs`、`paludarium-kernel`、`paludarium-host`、`paludarium-jit`、`paludarium-runtime`、`paludarium`（まとめ役とコマンド）、`paludarium-harness`（公開しない）（tech-stack-decisions）
- [x] `rust-toolchain.toml` で nightly を日付まで固定し、rustfmt・clippy・llvm-tools と、x86_64-unknown-linux-musl・wasm32-unknown-unknown を入れる（NFR9.1）
- [x] `[workspace.lints]` に clippy の設定を置く：`unwrap_used`・`expect_used`・`panic`・`undocumented_unsafe_blocks` を deny、`unsafe_op_in_unsafe_fn` を deny。各クレートは `[lints] workspace = true`。Host 以外のクレートに `#![forbid(unsafe_code)]`（NFR2.3、NFR3.1、NFR3.2）
- [x] `deny.toml`：ライセンスの許可の一覧、取得元は crates.io だけ、RustSec、禁止の一覧（webix・portabox・lanmower/blink の系列）（NFR8.1、NFR8.4）
- [x] `Cargo.lock` をコミットする前提で `.gitignore` を整える（NFR8.3）

### Step 2：テストの実行の準備

- [x] 各クレートに空のテストを 1 つ置き、`unit-test-instructions.md` の U1 のコマンドが通ることを確かめる
- [x] ネイティブの x86-64 Linux の実行環境を用意する。手元（Windows）では Linux のコンテナ（wslc。だめなら Docker Desktop）を使い、CI では ubuntu のランナーを使う。コンテナには musl-tools・binutils（objdump）・strace を入れる

### Step 3：差分テストの仕組みとゲスト（期待結果を先に用意する）

- [x] `paludarium-harness` に差分テストの仕組みを作る：x86-64 Linux でゲストを直接動かして標準出力・標準エラー・終了状態を記録し、エミュレータでの結果とバイト単位で比べる。1 件あたり 30 秒の時間切れを付ける（BR7.1、NFR1.1、NFR7.1）
- [x] ゲストを置く：`tests/guests/hello-c/hello.c`（write と exit だけ）と `tests/guests/hello-rs/`（`println!`）。CI と手元のコンテナで、musl と x86_64-unknown-linux-musl でビルドするスクリプトを置く（BR7.2）
- [x] 2 つのゲストの ELF の種類（ET_EXEC か ET_DYN）を確かめて記録する（BR1.4）
- [x] 2 つのゲストを strace で動かし、呼ばれる syscall の一覧を確かめる。BR3.3 の一覧と違えば、違いを `code-summary.md` に記録し、実装する一覧を直す（BR3.3）
- [x] 2 つのゲストを逆アセンブルし、実行される命令の一覧（SSE 系を含む）を作る（BR4.4、W7）
- [x] 命令ごとの差分テスト：命令をインラインアセンブリで実行してレジスタとフラグを出力する小さなゲスト（C）を、命令の一覧の分だけ用意する。未定義のフラグは出力から外し、外したものを表で持つ（NFR1.2）

### Step 4：共通の型（paludarium-types）

- [x] GuestAddr（ホストの整数との変換は検査付き）、Errno、ExitReason（syscall・page-fault・invalid-opcode・halt・budget-exhausted）、ExitStatus、Error を作る（C1、BR2.1）
- [x] 単体テスト（5〜8 件）

### Step 5：デコーダ（paludarium-decoder）

- [x] iced-x86 と yaxpeax-x86 の両方で包みを試作し、Step 3 の命令の一覧がデコードでき、wasm32 でビルドできるかを比べて 1 つを選ぶ。結果と理由を `code-summary.md` に記録する（tech-stack-decisions の Q1）
- [x] 選んだ crate を包む `decode(bytes, rip)` を作り、crate の型は外に出さない。範囲外の命令は Unsupported を返す（C3、ADR-006）
- [x] 単体テスト（5〜8 件）

### Step 6：Mmu（paludarium-mmu）

- [x] 4 KiB ページの 2 段のページテーブル（上は疎な表、下は 512 ページ分）で AddressSpace を作る。read・write・fetch・map・unmap・protect・set_break（C4、BR2.1〜BR2.3）
- [x] 範囲外・権限違反はフォールトを返し、panic しない（BR2.2、NFR2.1、NFR4.4）
- [x] 単体テスト（5〜8 件）

### Step 7：Cpu（paludarium-cpu）

- [x] CpuState（汎用レジスタ・rip・rflags・fs/gs のベース・xmm0〜15・mxcsr）と `run(state, mem, budget)` を作る（C5、entities.md の CpuState）
- [x] Step 3 の命令の一覧の命令を実装する。syscall 命令は rcx・r11 を設定して止まる。一覧にない命令は invalid-opcode（BR4.1、BR4.2、BR4.4）
- [x] 予算を使い切ったら budget-exhausted で止まる（BR4.3）
- [x] Step 3 の命令ごとの差分テストが通ることを確かめる。内部の部品の単体テスト（5〜8 件）を書く

### Step 8：Loader（paludarium-loader）

- [x] ELF の検査（x86-64・64 bit・リトルエンディアン・ET_EXEC か ET_DYN・PT_INTERP なし）、セグメントの配置、bss の 0 埋め、static-pie の基準アドレス 0x555555554000（BR1.1、BR1.2、BR1.4）
- [x] PT_LOAD の合計の大きさが 4 GiB を超える ELF は invalid-program にする（非機能要件のレビュー R-01 への対策。細工した ELF でホストのメモリを使い切らないため）
- [x] 最初のスタックと補助ベクタ（BR1.3）。AT_RANDOM は Host の乱数から取る
- [x] 単体テスト（5〜8 件）

### Step 9：Vfs（paludarium-vfs）

- [x] U1 の最小限：起動前にファイルを置き、パスで読めるようにする（C6、FR3.4 の先行）
- [x] 単体テスト（5 件）

### Step 10：Kernel（paludarium-kernel）

- [x] syscall の振り分け表と、表にない番号の -ENOSYS（BR3.1、BR3.2、NFR4.1）
- [x] Step 3 で確かめた一覧の syscall を実装する（BR3.3、BR3.4、BR2.3、BR5.1）。シグナルは登録だけで配送しない（BR4.5）
- [x] Cpu の止まった理由への応答：page-fault は SIGSEGV、invalid-opcode は SIGILL、halt は SIGSEGV で終わらせる
- [x] 単体テスト（5〜8 件）

### Step 11：Host（paludarium-host）

- [x] Host の trait（C2 の U1 の範囲と、乱数の口）と、std を使うネイティブの実装（標準入出力、乱数）。3 つの OS でビルドとテストが通る形にする（BR6.1）
- [x] 単体テスト（5 件）

### Step 12：Jit の口、Runtime、コマンド

- [x] `paludarium-jit`：何もしない CodeCache（C9）
- [x] `paludarium-runtime`：Session と、スレッドの実行ループ（W3）。kill の要求を予算の区切りで確かめる（BR4.3）
- [x] `paludarium`：公開 API の再公開と、コマンド `paludarium [options] <program> [args...]`。`--env` を受け付け、`--no-jit` は受け付けて何もしない（ネイティブには JIT がない）。`--mount` と知らないオプションは終了コード 2。プログラムはゲストの `/<ファイル名>` に置き、argv[0] は指定した文字列。終了コードはゲストの値、128 + シグナル、エミュレータのエラーは 70（BR5.2〜BR5.4、C11）
- [x] 単体テスト（各 5〜8 件）

### Step 13：結合（細い一本の確認）

- [x] Step 3 の差分テストで、C と Rust の hello world がネイティブと一致することを確かめる（NFR1.1）
- [x] 実行時間を記録する（NFR6.1）

### Step 14：ファジング

- [x] `fuzz/` に cargo-fuzz の対象を作る：デコーダの包み、ELF の読み込み、Mmu の操作の並び、syscall の引数（非機能要件のレビュー R-02 への対策）（NFR2.2）
- [x] 手元のコンテナで、各対象を短く動かして panic がないことを確かめる

### Step 15：CI

- [x] `.github/workflows/ci.yml`：3 つの OS でビルドと単体テスト、fmt、clippy（`-D warnings`）、cargo-deny、ubuntu で差分テストと cargo-llvm-cov（行カバレッジ 80% 未満で失敗）。action は SHA で固定し、既定の権限は読み取りだけ（NFR3.3、NFR8.1〜NFR8.3、team.md の Testing Posture）
- [x] `.github/workflows/nightly.yml`：ファジング（対象ごとに 10 分）と wasm のスレッドの確認（NFR2.2、BR8.1）

### Step 16：wasm のスレッドの確認

- [x] `spikes/wasm-threads/`：2 つの Worker が SharedArrayBuffer を共有し、片方が待ち、もう片方が書いて起こす確認用のプログラム（Rust の wasm32 に atomics などを付けたビルド）と、JS（BR8.1）
- [x] Node.js での確認スクリプト、COOP/COEP の見出しを付けて配る小さな配信のスクリプト、ブラウザの自動操作（Chromium 系・Firefox は自動操作の道具、Safari は safaridriver）
- [x] 結果の報告 `docs/reports/wasm-threads.md`：環境ごとの合否と版、Worker を作るのは Host の wasm 用の実装と起動用 JS のどちらが妥当か、その理由、必要なツールチェーンの設定（BR8.2）。手元で動かせない環境（Safari など）は nightly の CI の結果で埋める

### Step 17：文書と対応表

- [x] README に、ビルドと実行の手順、差分テストの動かし方、U1 の状態を書く
- [x] `code-summary.md`、`source-manifest.json`、`traceability.json` を作る

## 申し送り（前の工程のレビューの残り）

- 機能設計のレビュー R-09（C1・C2 への追加を contract-summary.md に反映していない）：コードでは追加を実装し、`code-summary.md` に、取り決めへの追加として記録する
- 機能設計のレビュー R-10（`--no-jit` を U1 で受け付けるか）：受け付けて何もしない（Step 12）
- 非機能要件のレビュー R-01・R-02：Step 8 と Step 14 で扱う


## 現在の共有sourceに対するU1確認

新attemptのPlan Approval・内容確認後、Step29〜31（3手順）の確認と成果物保存を完了し独立レビュー待ち。Step1〜28（24a〜24cを含む）は履歴。製品変更なし。過去の承認やレビューを新しい確認の代用にしない。

Step1〜17の[x]は先行実装の履歴であり、今回の承認や最新sourceの検証完了を示さない。今回の対象は既存U1実装とU1が所有するshared sourceの再確認・文書整合である。後続U2の独立source/test/docは作り直さず、そのsourceをU1 manifestへ追加しない。記録済み機能回答・Testing Contract・80%下限・30秒watchdog・nightly pinを維持する。

### Step 18：既存実装・回答・証拠の現在値を照合する

- [x] U1の既存source-manifest claims、C1〜C11利用側、writeのゼロ/部分結果回帰と既存命令census66件の対応を確認する。U2で共有sourceに加えられたArithmeticFault、typed atomics/common MMU synchronization、FS/GS linear addressを現在の共通sourceとして説明し、U1追加実装の成果とは数えない（BR3.4、BR4.1〜BR4.4、NFR1.1〜1.2）。
- [x] 最新sourceの保存済み検証（docs/u2/repairs/r01-workspace-coverage.txt、同fuzzとcargo-deny）からU1 diff16・Kernel write回帰・全workspace197件/94.00%を照合する。先行102件/87.11%と最新の分母を区別する。production変更がなければ同じ検証を反復しない（NFR3.3、NFR8.1）。

### Step 19：不足するU1確認のみ回収する

- [x] 証拠が不足または新規source修正が必要な場合だけunit-test-instructionsのexact U1 testsを実行する。命令/syscall修正はnative expectationまたは有限mockのRed先行→修正→Green、内部layerテストは実装後のcustom順序を保持する。未検証wasm環境、U1 fuzz各target、decoder候補比較の歴史的記録は不足を明記し、合格を推定しない（BR8.1〜8.2、BR9.1、NFR2.2）。

### Step 20：現在値と履歴を区別して成果物を確定する

- [x] U1 code-summary/traceability/source-manifestと必要なU1説明文だけを整合させる。build/cacheを除き、shell/scaffolding/generatorが書いたU1 application-sourceを全て列挙する。独立reviewへ渡し、記録済み回答から今回の承認を捏造しない（全BR/詳細NFR）。

### Step 21：修復用runnerと現在の失敗を固定する

- [x] Docker VMMと固定nightlyを維持し、scripts/linux-dev.shのstack無制限設定によるcompiler起動・image構築の修復を確認する。forkのUbuntu/Bookworm実機CIと手元Dockerのログを区別し、CPU・musl・ゲスト命令列を記録する。古い197件/94.00%を現在の合格証拠として引用しない（NFR1.1、NFR3.3）。

### Step 22：hello-cに必要なSSE命令を修復する

- [x] MOVQ/PUNPCKLQDQの非対称64bit値、上位64bitの扱い、自己参照をnative差分ゲストに追加し、実機期待結果と現実装の失敗を先に確認する。デコーダとCPUに必要なlegacy XMM形式を実装し、その後内部単体テストを追加する。hello-cでさらに不足が判明した場合も、命令censusとnative期待結果を先に確定して必要最小限の命令だけ扱う（BR4.4、NFR1.2）。

### Step 23：REPとゲストビルドの失敗を修復する

- [x] 実機でも失敗したREP4ケースについて、初期flags、ページ準備、fault/restart、CPU差を観測し、公式仕様と照合する。期待結果を先に確定し、原因が観測コードならゲスト、CPU意味論なら共有CPUだけを修正する。定義済みflagsのmaskを外して合格させない（NFR1.1〜1.2）。
- [x] tests/guests/u4/build.shとu7/build.shの混在CRLFをLFへ修正し、native Linuxで構文検査・ゲスト生成と関係する差分テストを確認する。他unitの機能追加や再実装は行わない。

### Step 24：修復後の検証

- [x] unit-test-instructionsの関係する限定コマンドをDocker VMMと実機Linuxで実行する。ENTER/ALUのDocker固有差は実機結果と区別し、30秒watchdogは維持する。更新したfork CIで既存suiteを確認し、fmt/clippy・依存検査・native行coverage80%以上を確認する。未通過項目は未検証または失敗として残し、nightlyを変更しない。

### Step 24a：3 OS検証で判明したHostの限定修復（追加承認対象）

- [x] macOS/Windowsのnative_fs::u7_testsを実装前に実行し、lock競合のOS errno35/33とLinux guest EAGAIN11の不一致、Windows hardlink links1対2、fixture終了時OS error32を保存する。OS番号をguestへ直接流す経路を修正し、同じguestエラーを返す回帰を確認する。無関係なHost APIの改善は加えない。
- [x] WindowsのFileStatリンク数を実際のmetadataから取得する。test fixtureは保持したNativeFs/関連handleを解放してから一時ディレクトリを削除し、cleanupのpanicで実際のテスト結果を隠さない。cleanup失敗を無視して合格させず、root外アクセス防止と既存lock/link/I/Oテストを保持する。
- [x] native_fs.rsと必要最小限のHostテスト・metadata/error変換だけを追加修復範囲とする。内部layerの順序はTesting Contractのtest-afterとし、既存失敗の再現ログを先に記録する。3OS Host回帰、3OS既存suite、Intel/AMD native差分、lint/依存、全体とU1限定coverage80%以上を確認し、manifest/traceabilityを追加した実ファイルへ更新する。

### Step 24b：Windows Runtimeマウントテストのcleanup（追加承認対象）

- [x] crates/paludarium-runtime/src/tests.rsのu7_runtime_mountだけで、remove_dir_allの直前にdrop(fs)とdrop(s)を追加する。両方が保持するmount root handleを解放してから削除し、cleanup失敗は引き続きunwrapで失敗させる。production Runtimeやmount機能は変更しない。Windows CIのOS error32ログを修正前の根拠として保持する。
- [x] Runtimeの当該テストとlibテスト、fmt/clippy、3OS既存suite、実機Linux差分、全体/U1 coverage80%以上を確認する。関連テストファイルは既存manifest claim内。30秒watchdog、nightly固定版、比較mask、2フックを保持する。

### Step 24c：Windows VFS共通fixtureの同種cleanup修復

- [x] crates/paludarium-vfs/src/mount.rsのtest専用Fixtureだけで、保持するMountedFsを空のMountedFsへreplaceしてdropし、root handleを解放してから既存remove_dir_allを実行する。production、mount意味論、assertion、cleanup errorのunwrapを保持する。WindowsのRuntime25件通過後に共通Drop:366で16件がOS error32になったログを修正前の証拠として残す。
- [x] mount回帰16件、VFS lib全件、fmt/clippy、3OS既存suite、実機Linux差分、全体/U1 coverage80%以上を確認する。source-manifestへ関連testのowning fileを追加する。これは同じ復旧で見つかった同種cleanupの限定修復で、以前の承認対象を変更済み内容へ読み替えない。

### Step 25：成果物と復旧の確定

- [x] code-summary、traceability、source-manifestと現在sourceのsnapshotを更新し、関連修復ファイルとunit所有を明記する。独立レビューへ渡す。plan-approval-guard/continue-workflowの2フックの登録と回復テストを確認し、rejected reportが必要な場合はその前に両フックを復元・検証する。過去のレビューや承認を今回へ転用しない。

### Step 26：現在ソースと既存の検証結果を照合する

- [x] U1の既存source-manifest、型・契約・テスト構成を読み、署名済み4d52be0aの実機CI（7+4ジョブ）と現在bytesを照合する。U1差分16件、hello world、3OS、全体/U1 coverage80% gateの証拠を現在値へ対応させる。旧失敗・旧fuzz・wasm/Safari未検証を区別する。新規ソース変更や証拠不足がなければ重いテストを重ねない（BR1.1、NFR1.1、NFR3.3）。

### Step 27：レビュー用記録を整合させる

- [x] code-summary/traceability/source-manifestと必要なsnapshotを現在値へ更新する。今回の作業は記録修復に限定し、製品不具合が見つかった場合のみrootへ返す。native-firstと内部test-after、30秒watchdog、各600秒fuzz、固定nightly、両coverage80%を保持する（全BR/詳細NFR）。

### Step 28：現在状態を固定して独立レビューを受ける

- [x] 日記・必要記録をレビュー依頼前に確定する。レビュー依頼から結果の正式記録までは成果物・sourceを固定し、jjのsnapshot/commit操作も挟まずに独立レビューを記録する。正式検証後に完了確認を受ける。U4の既存成果を保持し、後続の再レビューへ引き継ぐ。2フックを有効なまま維持する。

### Step 29：旧attemptのsourceと証拠を再確認する（履歴）

- [x] U1 manifest103claims/展開108filesと現在snapshot、署名済み4d52be0aの保存CI7+native4jobsを再照合する。別作業.gitignore差異を製品CI証拠と分け、hello world/U1差分16、3OS、全体/U1coverageを一致範囲で再利用する。新実行とは数えず、不足だけ既存exact commandsで回収する（BR1.1、NFR1.1/3.3）。

### Step 30：新しい内容確認後に4成果物を保存する

- [x] 今回のSummary Confirmation後にcode-summary.md、unit-test-instructions.md、source-manifest.json、traceability.jsonの全4producesを保存し、新attemptの確認との対応を明記する。意味論が正しいmanifest/traceabilityのclaimsとschemaは維持して保存する。必要snapshot/evidenceも整合し、旧fuzz/wasm/Safari未検証と80%/30秒/nightly/各600秒/masksを保持する。新製品不具合はrootへ返し、自動修正しない（全BR/NFR）。

### Step 31：日記と全書込を終えてレビューへ渡す

- [x] 親construction/code-generation/memory.mdへ読取なしheading anchored追記を依頼前に完了する。全source/成果物書込を終え、reviewrequestからterminal記録まで全workerとjj snapshot/commit操作を停止する。前回不整合原因を断定せず、rootの正式独立レビューへ渡す。2フックを有効のまま保持する（NFR3/9）。

## 工程差し戻し後の記録再確認（今回の実行対象）

Step32〜34は前回の実行履歴として保持する。今回の修正対象は末尾のStep35〜37。製品の意味論・既存テスト・CI設定・品質下限は維持する。

### Step 32：現行ソースと署名済みCIを照合する

- [x] U1 claimsとaf9b739d742a9552f44fc1515646c862b19e5de2のbytesを照合する。CI37713953347/native37713953340のhello world・U1差分・3OS・coverage証拠との対応を確認し、旧4d52照合と区別する。verify-native-ci.pyで現行byte proofを確認する（BR7.1、NFR1.1/3.3）。

### Step 33：証拠の時点表示と成果物を更新する

- [x] 新Summary Confirmation後、code-summary/evidence-currentの旧snapshot一致を歴史的記録と明記する。unit-test-instructions、source-manifest、traceabilityを現行確認に対応させて保存する。claims/schema・47IDs・未検証GAPを維持し、新製品不具合は報告する（全BR/詳細NFR）。

### Step 34：限定検査と独立レビュー

- [x] required-sections/traceabilityと現行CIのbyte proofを確認する。日記を依頼前に確定し、依頼から正式結果記録まで成果物・source・jj操作を固定する。2フック、Docker VMM、80%下限、30秒watchdog、固定nightly、各600秒fuzz設定を保持し、未実行fuzz/wasm/Safariを合格としない（NFR3/9）。

## 指摘修正と実Safariの検証（今回の実行対象）

### Step 35：CI証拠の参照名と要件の担当を修正する

- [x] evidence-current.mdのCI証拠2ファイル名を実在するci-jobs-37713953347.jsonとci-jobs-37713953340.jsonへ修正する。traceability.jsonの既存47項目を保持し、検査が要求する追加60 FR/NFR IDsを共有要件・Unit割当と照合する。U1が実装する範囲は実在する実装/テストへOKで対応させ、後続Unitの範囲はDeferredと担当Unitの根拠、集約見出しやU1非該当部分は理由付きN/Aで明示する。検査を無効化したり、後続機能をU1で実装済みとしない。既存traceability検査を再実行し不足0を確認する（FR/NFR全量と既存BR/詳細NFR）。

### Step 36：本物のSafariでwasmスレッドを検証する

- [x] このMacのmise管理Node.jsと固定nightlyを確認し、既存spikes/wasm-threads/build.shで共有メモリwasmを生成する。既存browser-check.mjs safariをAppleのsafaridriverと本物のSafariで実行し、Safari/macOS/Nodeの版、crossOriginIsolated、wait/notifyの結果、値42、5秒上限をログに記録する。safaridriverのRemote Automation有効化が必要なら具体的な設定を提示して待ち、WebKitの代替結果を使わない（BR8.1、NFR7.1）。
- [x] docs/reports/wasm-threads.mdのSafari行と判断を実測結果へ更新する。不合格・権限不足は未検証または失敗として原因を残す。U1 source-manifestの当該報告claimとBR8.1/BR8.2の対応を維持する。fuzzや他ブラウザの過去結果を今回の新検証と数えない（BR8.2）。

### Step 37：限定検査と新しい独立レビューで確定する

- [x] 更新した対応表とrequired-sectionsを検査し、追加IDsの担当・ステータス・実在targetを確認する。製品ソース不変と保存済みnative CIの対応を再確認し、Safari報告の変更をnative製品bytesとの差と区別する。成果物・日記を確定後に独立レビューを受け、今回の完了確認を行う。品質下限・両フック・既存未検証項目を維持する。

検証済み（今回Step32〜34）：Summary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後、103claims/108filesと現行af9bを再照合。限定sensorの結果を保存し、製品変更・新規重いテストなし。Step34の独立レビューは親担当へ引き渡して実施するため、そのチェックは未完了のまま。

Step35の分類検査とStep36の実Safari測定は完了。Step37のレビュー準備と補助byte比較は完了したが、canonical検証はSafari報告の差分でexit1。正式検証・独立レビュー・完了確認は未完了のまま、親担当に引き渡す。

Step37の正式検証コマンドは人が選択したverify-native-ci-with-safari-report.pyでexit0。対応表/required-sectionsとレビュー準備は完了。Step37チェックは独立レビュー・完了確認が残るため未完了のまま。旧canonicalの文書差分拒否は履歴として保持する。

## 今回の差し戻し：担当説明と後続Unitの指摘

ユーザー回答「3の両方です。」に従い、U1 R-03、U4 R-01、U9 R-01を修正対象とする。unit-major/serialの順序に従い、今回のU1ではStep38〜40のみを実行し、後続U4・U9はそれぞれの計画承認と独立レビューで修正する。従前の成果物維持指示は、今回指定された指摘箇所について更新する。その他の既存成果・履歴・Testing Contractを保持する。

### Step 38：FR5.4の担当説明を共有Unit定義へ合わせる

- [x] traceability.jsonのFR5.4 notesへU5を追加し、ゲストのnative thread割当とwasm Worker割当の担当を共有Unit定義に合わせる。Deferred状態、他106項目、実装済み範囲を保持する。BR6.1とFR5.4の説明修正であり、スレッド機能の実装は追加しない。

### Step 39：限定検査と証拠の更新

- [x] U1対応表sensor、required-sections、承認済みcanonical完了検査を実行し、件数・exit・現行署名済みCIとの対応を保存する。新しい製品変更がないため重い試験は反復しない。code-summary/evidence-currentへ今回の修正と検査を追記し、旧証拠を現行結果へ読み替えない。全BR/詳細NFRと80%・30秒・固定nightly・各600秒を保持する。

### Step 40：独立レビューと後続Unitへの引継ぎ

- [x] 全4成果物・manifestと必要記録を確定して独立レビューを受け、U1 R-03の解消を確認後に完了確認を更新する。レビュー中の書込・jj snapshotを停止する。後続U4では4d52時点と現行CIの証拠表記を修正する。後続U9では共有HostのTerminalAttributes/TerminalInfoをnon_exhaustiveとし、constructor等で他crateのliteral構築を置換し、既存terminal/ioctl挙動・3OS・production wasmを再検証する。後続指摘をU1の完了で解消済みとはしない。

## 共有CPUの前提修復と現行完了検査（追加範囲）

ユーザーの明示依頼に従い、U1の現行source検証を阻害するSHA非整列契約とcoverageを必要最小限で修復する。既存Step1〜40とTesting Contractは履歴を含めて変更せず保持する。元のplan/instructions bytesとhashはintent verification/u1-sha-prerequisite-plan-baseline/へ保存した。この2文書への末尾追記のみが今回の計画変更であり、他23先行成果物と旧25files基準は維持する。旧Step39のチェックを新source合格へ転用しない。

### Step 41：native観測を先に保存し、共有SHAメモリ契約を修復する

- [x] U3で人が選択し内容確認したIntel SDM Rev089 Table2-21のSHA256RNDS2/MSG1/MSG2契約を共有CPUの前提修復として適用する。新CIで既存native observerの全行、CPU vendor/family/model/stepping/feature、CPUID、encoding/input/source/binary hashを実装前に取得する。既存3 runner×3反復のIntel/AMD差異証拠を保持し、nativeだけの観測をemulator合格としない。
- [x] crates/paludarium-cpu/src/exec.rsのSHA3形式の非整列許容だけを除き、16-byte整列違反はメモリread前にGeneralProtectionとする。Cpuの安全なRustのみを変更し、他命令・decoder・公開型・kernel・CPUID広告・guest fixtureの意味論は変更しない。CPU u3_tests.rsに3命令×非整列accessible/跨PROT_NONEの6独立契約ケースを追加し、#GP、RIP・全GPR/XMM・MXCSR・定義済みflags・メモリ不変を検査する。整列accessible/PROT_NONEも境界として保持する。
- [x] Harness support/u3_oracle.rs、diff_u3.rsとCPU native replayを必要最小限で更新する。native全行は保存する。整列caseとIntel nativeは厳密比較を維持し、既に実測したAMD profileのSHA3形式×scenario2/3の6行だけは差異を明示してnative同値主張を外し、独立した仮想CPU全state不変assertを必須にする。profileはCIごとの実CPUID/CPU情報から検査し、未知profile・入力/encoding不一致・その他trap不一致は失敗とする。広域mask、case削除、期待値の固定保存を行わない。

### Step 42：最終共有sourceでnative品質と本番wasmを実測する

- [x] 固定nightly-2026-10-01で関係CPU/Decoder単体とfresh diff_u3、既存diff_u1/2/4/9、3OS単体、fmt/clippy警告0・依存検査を確認する。CIのworkspaceとU1 production file集合を対象とする行coverage80%以上を維持し、Harnessのfresh native差分を同測定で実行する。U3 CPU/Decoder対象80%も確認する。失敗command/分母を保持し、production files除外や閾値低下で通さず、必要な境界テストだけ追加する。
- [x] 変更closureを各targetの実hashで照合し、現行sourceのCPU/MMU/decode/load_elf/syscall_args/vfs_paths/mmu_opsをASan+LSan各600秒以上確認する。既存固定nightly/cargo-fuzz0.13.2/seed1/timeout30/rss2048/既存suppression/detect_leaks1/各max_lenを保持する。署名付きisolated fork CIを使用し、source前後、raw exit/runs/time、最小C2回、binary/symbols/corpus/crashを常時保存する。旧7対象成功を変更後の全source成功へ読み替えない。
- [x] 最終CIの本番wasm module・fresh native13fixtures・Node21ケースを確認し、同一module SHAで実Safari21ケースを既存28秒operation/30秒whole-process watchdogとCOOP/COEPで実行する。Safariは閉じた状態からdriverがautomation用に起動する。既存成功/失敗rawを保持し、今回結果・version・crossOriginIsolated・cleanup・前後source hashesを保存する。現行Windows既存回帰のsource closureとraw metricsを確認し、旧154paths証拠を現行全一致としない。

### Step 43：先行成果物を維持して現行証拠と独立レビューを確定する

- [x] U1のcode-summary/traceability/source-manifest、他Unitの既存成果物は変更せず、共有修復の実変更・担当・証拠をintent verificationに保存する。plan/instructionsは元bytesをprefixとして保持し、他23先行成果物のsize/SHA不変を確認する。新sourceと署名CI/artifact/raw/coverage/Safari/7ASanの対応を厳密に検査する別pathのread-only checkerを準備し、旧checkerは保持する。新commandはrootが人の承認を取得するまで実行しない。
- [x] U1限定sensor2件と必要な証拠を確定し、全書込とjj snapshotを停止して独立レビューへ渡す。rootが日記・正式検証・完了確認を担当する。未達品質、全入力/全SSE/後続Unit未検証は合格へ拡張しない。Step40の正式独立レビューはその後に実施する。

## 旧確認スクリプトと現行ソースの分離修復（今回Steps44〜47）

### Step 44：旧全入力と現行U1の証拠境界を確定する

- [x] 旧 `verification/verify-current-u12-macos-host.py` の342入力・署名a275bd3d6f08bf48c1a58dead339240b5364af4c・全predicateを保持する。承認後、jjの読取diffと342全pathのbytes照合で現行との差を列挙する。lib.rs/native_fs.rs/Runtimeを含む共有変更をcfgだけで無影響と断定しない。両lock・toolchain・guest生成・Harness・実行設定を含めU1の依存境界を実在ファイルから確定し、過去U1 claimと実build入力を別に記録する（BR6.1、BR7.1、NFR1.1）。
- [x] U13 step7_bridge.pyの414ファイルsnapshot（342署名入力＋72歴史支援）を厳密hash/全inventory/由来で検査する。旧checkerのhashとAPIの署名・CI・artifact証明を維持し、旧main全検査を歴史的source viewで実行する。旧sourceをworkspaceへ復元せず、歴史的合格を現行合格と表示しない。

### Step 45：現行U1の実測を結び付ける

- [x] U13の成功済みLinuxジョブから、同一署名sourceのhello_c/hello_rs/hello_rs_with_arguments、diff_u1全16件、既存11packageのU1 coverage80%以上、品質・3OS・U1 wasm観測の適用範囲を監査する。run全体の成功は要求も主張もしない。必要job/stepのsuccess、実command、skipなし件数、raw exit、入力・両lock・compiler・生成guest/binary・計測分母を厳密照合する。未完了Windows guest/coverageをU1合格の代用にしない。
- [x] 完全適用できない実測だけ、同じ現行署名sourceでfresh Linux native→emulatorのhelloとdiff_u1、固定U1分母coverage80%以上を再実行する。共有Runtime復元などで実行bytesが変われば該当実測を更新する。追加の診断CI/publicationが必要ならファイル・送信先・限定差分を具体化してrootへ返し、許可前に公開しない。U13全29完了を前提にしない。

### Step 46：二層checkerと不正証拠拒否の回帰

- [x] 新 `verification/verify-current-u1-source-bound.py` とU1 verification配下の補助module/testを作る。歴史全検査と現行U1検査の双方が成功した時だけexit0。現行入力に未承認差分/欠落/追加/重複/改変を許さず、U13作業中という境界を結果へ明記する。旧checker・threshold・mask・歴史原本・他Unitの既存成果物は保持する。
- [x] 正常2系統（U13全体未完了でも必要U1実測成立／必要実測のみ新規取得）と、旧snapshot改変・欠落・余分・symlink、checker改変、現行改変、署名不一致、異なるCI head、失敗/skip/0件、guest不一致、compiler不一致、coverage分母欠落、coverage80%未達、30秒超過、歴史証拠の現行への誤用、artifact digest不一致を含む計18回帰を実行する。拒否条件のassertを無効化しない。

### Step 47：全診断・正式検査・再レビュー・最終確認

- [x] レビュー前に全checker診断を最後まで実行し、生ログ/exitと実行時点の全入力を保存する。diagnosticを完了承認へ代用しない。required-sections/traceability、全producesとmanifestを修正範囲へ整合し、既存107対応の意味論を保持する。全書込を止め独立再レビューを受ける。新確認commandはrootが人の正式承認を記録した後に実行する。
- [x] U1完了承認後はengineの返す手順でU13へ戻り、既に承認された32件非計測比較／16件独立coverageと診断撤去を続ける。U13完成やセッションID競合の完全解消を今回のU1成功だけで主張しない。

## 消失した旧JS測定フォルダーの修復（今回Steps48〜50）

### Step 48：保存済み原本と旧測定先の安全な再構成

- [x] `verification/verify-current-u1-source-bound.py` の歴史検査だけに、U1 verification配下の `historical_js_workspace.py` を接続する。旧U12 validatorの固定参照 `/private/tmp/paludarium-u2-mmu-4608` とV8原本のURLを変更せず、旧bindingの全342入力を既存U13 `step7-u12-signed-baseline` と完全hash照合してから、この計画が明示する一時フォルダーへ同一bytesを再構成する（BR7.1、NFR1.1）。workspaceの製品を旧版へ戻さない。
- [x] manifest全inventory・安全な相対path・重複・symlink・hashを検査する。一時フォルダーが既に存在する場合は上書きせず、再利用条件を全342入力の完全一致と非symlinkへ限定する。別bytes・余分なファイル・同時再構成は拒否する。作成物は所有範囲を記録し、失敗時も利用者の既存ファイルを削除しない。再構成・利用中のsource変更を前後hashで拒否する。一時フォルダーは証拠原本として扱わず、毎回保存済み原本を検査する。

### Step 49：旧全検査を維持した回帰と再集計

- [x] Python unittestの既存U1専用33回帰を保持する。新 `test_historical_js_workspace.py` に8境界を追加する：一時先不存在からの成功／完全一致する既存先の再利用／保存原本hash不一致／欠落・余分・重複inventory／既存先の異なるbytes／symlink／同時利用の競合／検査中のsource変更。variantは個別subTestで確認する。テスト用一時先はU1 verification配下に隔離する（NFR1.1、NFR3）。
- [x] 保存済みV8原本83JSONを変更せず、旧Node binary・collector・342入力のhash確認と旧aggregateをそのまま実行し、旧js-coverage.jsonとの完全一致を要求する。旧checker・validator・collector・snapshot・原本manifestのhash不変を照合する。旧原本の再集計は新しいguest実行や新しいcoverage測定と表示しない。初回native SIGSEGVの原因未確定という独立レビュー指摘を保持する。

### Step 50：全診断・正式検査・独立レビューとU13への復帰

- [x] 同じ確認スクリプトの全診断を最後まで実行し、実exit・全入力・修復前失敗を記録する。正式required-sections／traceabilityを確認し、レビュー前に書込みを終える。独立レビュー後、承認済みcommandが正式に有効であることを確認してcheckpointを再検証する。command文字列を変更する場合だけ新しいcommand承認を取得する。
- [x] U1の実測・履歴・未検証を区別して完了承認へ進む。その後、正式手順でU13の承認済み32操作比較／16操作coverage分離と診断撤去へ戻る。他Unitをやり直さず、U13未完了・ID競合の完全解消未検証を保持する。

## U14共有変更後の確認更新（今回Steps51〜54）

### Step 51：旧全検査と現行入力の境界を確定する

- [x] 旧U1確認スクリプトと旧U13確認スクリプトを変更せず、旧362入力と署名e2d3f316の原本、旧361入力と署名832abd0fの原本をそれぞれ完全hash照合する。旧U12を含む全predicate・V8再集計・一時先再構成を旧署名ソースの読み取りviewで保持する。旧成功を現行成功に読み替えない（BR7.1、NFR1.1）。
- [x] 承認済み39ファイルの署名922e5371と書式2ファイル修正の署名0eb724b5を、親・GitHub署名・全path／bytesと別々のpublication manifestで監査する。旧39manifestと初回失敗原本を保持する。現行依存入力は実在する製品・guest生成・Harness・両lock・toolchain・CI設定から再列挙し、391件という暫定unionを固定値で合格にせず、全inventoryと変更closureを確定する。追加・欠落・未承認変更を例外で無視しない。

### Step 52：現行の署名ソースへU1実行証拠を結び付ける

- [x] 書式修正後の同一署名headによるCIから、fresh Linux nativeとemulatorのhello_c／hello_rs／hello_rs_with_arguments各stdout・stderr・実終了0、diff_u1全16件、固定11packageのU1 coverage80%以上とworkspace coverage80%以上、3OS品質の原本を保存・照合する。失敗・skip・0件・異なるhead／guest／compilerを拒否する（BR7.1〜7.2、FR9.1）。
- [x] 同CIの共有wasm4環境各28ケースとASan／LSan13対象各600秒原本は、U1に必要な変更closureと実compiler・設定が一致する範囲を明記して扱う。MMU最大4608バイト、guest30秒、固定coverage分母を保持する。CI全体未完了をU1の必須証拠不足へ代用しない。U14の速度改善は未達のまま保持し、U1の成功でU14完成や初回native SIGSEGV原因解消を主張しない。

### Step 53：旧／現行を分離する新確認スクリプトと拒否回帰

- [x] 新 `verification/verify-current-u1-u14-source-bound.py` とU1専用 `verification/u14_source_bound_validation.py` を実装する。旧全predicateが旧署名viewで成功し、現行U1の必須証拠が現行署名sourceに完全一致する場合だけexit0とする。旧checker・threshold・比較mask・原本を変更しない。新スクリプトの診断は正式完了証明と区別する。
- [x] 既存41回帰を保持し、新 `verification/test_u14_source_bound_validation.py` に18境界を追加する：正常な二層検査、正常な書式限定更新、旧snapshot改変、欠落、余分、重複、symlink、旧checker改変、現行改変、署名／親不一致、CI head不一致、失敗／skip／0件、guest不一致、compiler不一致、coverage分母欠落、80%未達、30秒超過、歴史証拠の現行流用。全変種を独立assertまたはsubTestで検査し、期待条件を緩めない。

### Step 54：全診断・正式検査・独立レビューとU14への復帰

- [x] 新確認スクリプトの全診断を最後まで実行し、実exit・全入力・raw manifestを保存する。required-sections／traceabilityと4成果物・source-manifestを今回の範囲へ整合し、既存107対応の意味論を保持する。書込を終えて独立レビューを受ける。新最終確認コマンドは完成した内容を人へ提示し、別の正式コマンド承認後だけcheckpointで実行する。
- [x] U1の正式検証と人の完了承認後、返された正式手順に従ってU14の既存JIT作業へ戻る。全Unitのやり直し、製品のついで修正、AI-DLC本体やguard変更を行わない。初回native SIGSEGV・並行セッションID競合の完全解消、U14性能要件は検証できた範囲だけを報告する。

## 完了承認後の追加修正（今回Steps55〜58）

ユーザーは「両方を調査・修正する」と指定した。U1だけを正式に再開し、R-08の旧証拠参照とR-05のnative SIGSEGV原因を対象とする。先行Unitの完了済み作業、署名b45158d3の成功と失敗原本、既存107要件の分類・target、AI-DLC本体とstrict guardを保持する。

### Step 55：旧参照を履歴として保持し、現行参照を整合する

- [x] traceability.jsonの旧b4cc2381／CI38314464997／bindingを履歴へ保存し、現行b45158d3／CI38319817485／355入力／u14-decoder-u1-execution-binding.json／CI38319817478の13対象bindingを明記する。既存107要件の分類・targetは変更しない。正常更新、旧履歴保持、107分類不変、head／run／binding取り違え、sanitizer参照欠落、成功主張の根拠欠落の7境界を回帰検査する。

### Step 56：初回失敗の実体とLinux条件を復元して観測する

- [x] job114563806344の3863〜3869行、失敗時の原ZIP、insn-u2-frame ELFとSHA、署名ソース、実compiler、CPU・kernel・stack／環境条件の保存有無を監査する。失敗ELFが保存されていなければ欠落と明記し、同一ソース再ビルドを同一失敗ELFと呼ばない。
- [x] Linux実機で保存ELFを優先して起動し、初回coverage相当と単独nativeの両条件を比較する。1実行30秒以内、有限反復最大100回、失敗時のRIP・レジスタ・stack・signal／終了コードとdisassembly、ELF／設定hashを保存する。通常ASLR条件を先に扱い、stack配置やASLRを変える比較は補助診断として区別する。ツールは最新を確認して版を記録する。専用CIの外部送信は具体的なファイル差分が完成してから別途承認を取得する。

### Step 57：反証可能な原因を示し、必要な最小修正だけを実装する

- [x] fixture・ABI／stack・compiler・環境とエミュレータ動作のどこに差があるか、失敗観測と独立した境界回帰で切り分ける。単なる再試行成功を原因解消としない。製品／fixture変更が必要なら、原因・対象ファイル・最小差分と影響するUnit境界を提示し、変更範囲の承認後に修正する。再現できない場合は未解明と条件・観測上限を残し、完了解消を宣言しない。

### Step 58：修正後証拠・正式検査・独立レビュー・確認を更新する

- [x] 既存74回帰を維持し、追加7境界と原因に対応する回帰を実行する。実行依存が変われば同一署名ソースでU1 hello6実終了0・diff_u1全16件・関連U2差分・固定11packageとworkspace coverage80%以上・3OS品質を再確認し、共有wasmと13 ASan/LSanはcompiler／依存／設定が一致する範囲だけ再利用する。不一致対象は各600秒、MMU最大4608バイトを維持する。
- [x] 旧全検査・失敗原本を保持して確認スクリプトと4成果物を整合し、全診断・required-sections／traceability・独立再レビューを実施する。新最終確認コマンドが必要なら具体化後に別承認を取得する。原因未解明やU14ブラウザ失敗・性能未達を残す場合は完了承認時に明記し、人の判断を待ってU14へ戻る。

## 全品質CIの3失敗の修正（今回Steps63〜66）

ユーザーは全品質CIを必ず成功させる方針へ変更した。初回nativeクラッシュの直接証拠不足は今回の対象外とし、既存の未解明記録を保持する。CIの誤りは再現と根拠で判断し、失敗の無視・skip・閾値低下で成功扱いしない。

### Step 63：3失敗の再現と責任境界を確認する

- [x] CI38380449837のWindows隔離symlink交換テストとFirefox／本物SafariのERR_HTTP_HEADERS_SENTの原ログ・署名ソースを照合する。Windows実機のファイルハンドル寿命・共有違反とAccessDeniedの条件、HTTP応答の二重送信経路を個別に再現し、製品・fixture・テストサーバー・CI設定のどこが原因か根拠を記録する。既存の成功31／失敗3と失敗原本を保持する。

### Step 64：原因に対応する最小修正と回帰を実装する

- [x] 特定した原因に限定して実装・テスト・CI設定を修正する。Windowsではcapability外のsentinel不変、交換発生、有限反復と30秒制限、cleanupを維持する。HTTPでは正常応答・切断・同時要求・エラー時の終端応答を検査し、二重headers送信の再現が修正後に成功することを確認する。既存guestケース・比較mask・coverage80%・strict guardを保持する。広い製品変更が必要なら具体的差分を先に提示する。

### Step 65：同一署名ソースで全品質CIを成功させる

- [x] 具体的差分と送信範囲を提示し、外部送信の承認後に既存fork／ブランチへ署名付きjjでpushする。同一headでWindows・Firefox・本物Safariを含む全品質CIの必須ジョブを再実行し、全成功・skipなしを確認する。依存が変わるU1比較・coverage・ASan／LSanは適用条件を監査して必要範囲だけ再実行し、異なるheadや過去の成功を現行成功へ流用しない。

### Step 66：確認更新・独立レビュー・正式検証

- [x] 旧全checker検査と失敗原本を保持して新しい全品質成功原本を厳密に結び付ける。拒否回帰・正式sensor・独立レビュー・全診断を実施する。新最終確認コマンドが必要なら具体化して別承認後に実行し、完了承認へ進む。U14性能・既知JIT panic・初回core欠落・ID競合はこのCI修正だけで解消と主張しない。

## 観測後のfixture限定修正（追加Steps59〜62）

ユーザーは「fixture限定修正と再検証を承認」と指定した。保存元ELFの独立再現で `leavew` のSIGSEGVとRBPの65536 bytes差を観測した。初回クラッシュのcore欠落と独立再現の原因を区別し、既存Steps55〜58・全失敗原本を保持する。対象はfixture・境界登録・必要な診断CI／確認bindingであり、emulator製品・AI-DLC本体の修正は含まない。

### Step 59：失敗に対応する境界を準備し、16bit fixtureのstackを限定修正する

- [x] `tests/guests/insn/u2-frame.c` のW=2 FRAMEだけ64KiB整列・64KiB scratch stackの中央32768 bytesへ切り替える。元RSPをR10へ保存して復元し、W=8は元stackを維持する。RBP=RSP+512、chain初期化、N=0／1／2／31、LEAVE、prefix、XLAT／flagsと全17 FRAME呼び出しを保持する。N31のBP decrementも同window内に入ることを算術とnative境界で検査する。
- [x] 新規 `tests/guests/insn/u2-frame-boundary.c` と `crates/paludarium-harness/tests/diff_u2.rs` 登録で、元stack low16の0x0000／0x0001／0x0002／0x01ff／0xfdff／0xfe00／0xffffの7配置を検査する。上下mapped領域を確保し、caller RSP／RBP／return address復元と全16bit nesting／prefixを検査する。修正前のwindow不一致を独立境界で検出し、修正後に同境界を通す。異常な旧LEAVEの実行でrunnerを無条件に落とさない。

### Step 60：同一署名ソースのLinux nativeとemulatorを再比較する

- [x] 固定build条件で新しいfixtureをビルドし、通常ASLRのnative最大100回・各30秒以内と、emulatorの全stdout／stderr／exitを比較する。新境界guestと関連diff_u2、既存diff_u1全16件・hello6実終了0を実行する。旧expectedや旧ELFを修正後guestの期待値へ代用せず、fresh native原本・ELF／source hash・compiler・CPU／kernel／stack条件を保存する。外部送信は具体的差分を完成させて別途承認後に行う。

### Step 61：既存品質・測定対象と証拠の適用条件を再確認する

- [x] 同一署名ソースで3OS品質と固定11package／workspace coverage各80%以上を確認し、測定対象・mask・guest30秒を維持する。共有wasmと13 ASan／LSanは全依存・実compiler・設定が一致する範囲だけ再利用し、不一致対象は各600秒、MMU最大4608バイトで再実行する。fixture依存が違う旧native証拠を現行合格へ流用しない。
- [x] 既存74回帰・参照7回帰・診断回帰を保持し、scratch領域／N31／caller復元の回帰を追加する。新旧入力差分と診断publicationを監査し、旧全checker検査を保持した確認binding更新を検査する。

### Step 62：正式検査・再レビュー・最終確認へ進む

- [x] traceabilityの107分類・targetを保持して現行署名ソース／CI／入力／bindingを整合し、code-summary等4成果物に原本・未検証を記録する。全checker診断、正式sensor、独立再レビューを実行し、新最終確認コマンドが必要なら具体化して別承認後に正式実行する。初回fault位置の直接証明欠落と、U14のブラウザ・性能・ID保証の未検証を明記し、完了承認後にU14へ戻る。

## 独立レビュー指摘R-05／R-11／R-13への記録対応（今回Steps67〜69）

ユーザーはskeleton checkpointでRequest Changesを選び、「R-05 R-11 R-13 の必要対応を反映する。produces-revision-proposal.md の文案を code-summary.md と unit-test-instructions.md に適用し、正式コマンド final_candidate.py と binding-v4 SHA、現 source での exit 0 実行 formal-candidate-1792157659313715000-72179 を記録し、traceability の R05 R11 参照を更新する。旧検証と失敗原本は保持する。」と指定した。正式検証コマンドは人がApproveで採用済み（verification-command.txt、SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）。対象は記録3ファイルだけで、製品source・fixture・CI・guest・AI-DLC本体・source-manifest.jsonは変更しない。

### Step 67：code-summary.mdへR05／R11の現在証拠と正式実行原本を追記する

- [x] `verification/r05-r11-repair-01/produces-revision-proposal.md` の「code-summary.md への追記」2段落を新しい現行節として追記する。R05は、保存同ELFの独立GDB再現（`leavew`／66c9のSIGSEGV、16bit BPの+65536 wrap）、修復済み64KiB整列scratch window、7 caller境界×7 forms（nest31を含む）、署名be45b36ce9d7a65719ba1f86cf6a0b018070741bのfresh native／emulated 200比較と実2 ELFの一致を根拠として記し、初回job114563806344のcore／RIP／レジスタ未保存を歴史的限界として保持する。工学的原因の説明と指摘closureを区別し、「初回事象のfaultを直接証明した」とは書かない（R-05）。
- [x] R11は、旧canonical／consumer-v3／binding／実695.780秒chainの原本不変、旧rawの純粋再解析と現 source／CIの照合の分離、現owned40・compiled223・署名888／7入力、公式U1 7jobs／11ZIP、全品質34jobs／32ZIP、versioned guest 3receipt、実11crate／npm tar 7境界の拘束範囲を記す。mise設定がpreview13（署名208fd965）から15へ変わったこと、compatibility.pyが旧consumer-v3へ旧mise bytesの読取専用viewを与えて照合していること、したがって「現行preview15設定でのconsumer-v3正式実行」は未検証のままであることを明記する（R-11）。新性能測定なし、私有CARGO_HOMEの別U15 moduleへ旧性能を移さない。
- [x] 正式コマンドの実行原本を3件記録する（R-13）：checkpoint verify 43ea67bc（2026-10-16T12:41:42Z、exit 0、`formal-candidate-1792154502657025000-40216`、.gitignore追加2行の状態）、Claude Code harness追加で.gitignoreに3行目 `.claude/settings.local.json` が入った状態のexit 1拒否（`formal-candidate-1792157037871198000-68539/refusal.json`、`ignore has other changes`）、3行目削除後のexit 0（`formal-candidate-1792157659313715000-72179`、2026-10-16T13:33Z）。いずれもstdoutは `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false` であり、Unit完了・U15受理の証拠ではないと書く。

### Step 68：unit-test-instructions.mdの正式コマンド欄と履歴を整合する

- [x] 「現在のsourceでの正式検証コマンド」節を追加し、exact noargs command `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py`、固定binding-v4 SHA256 `1df659288e5dc8ed7962b6c43dae6df3fbf32779562f34f3caf0e2734891f7d7`、exclusive出力先 `formal-candidate-<time_ns>-<pid>/`、保存される子4件（old_predicates／current_semantics／package_semantics／old_predicates）のargv・exit・stdout/stderr SHAを記す。guest・旧695秒chain・性能測定・CI・公開を起動しないことと、`.gitignore` の許容追加が `aidlc/active-memory/`・`aidlc/.aidlc-request-text/` の2行だけであることを記す。
- [x] 旧コマンド `verification/preview-20261015-update/verify-compatibility.py` と `verify-current-u1-u14-source-bound.py` 等は歴史検証手順として本文を残し、「作成予定／未承認」の記述は時点付きの履歴へ改める。「正式採用済み」は人のApprove記録（Construction Verification Command、2026-10-16T12:32:15Z）を根拠にだけ書く。Step 67と同じ3実行原本を列挙し、結果がUnit完了を宣言しないことを再掲する。手元macOSの `cargo test --locked -p paludarium-harness --test diff_u1` が0件であることをLinux 16件の証拠と呼ばない。

### Step 69：traceabilityの参照更新・sensor・独立再レビュー・checkpoint再検証

- [x] traceability.jsonの `verification_context` を `verification_context_history` へ退避し、新 `verification_context` に scope「U1 Steps67–69 R-05/R-11/R-13 record repair; existing 107 classifications unchanged」、current_head be45b36ce9d7a65719ba1f86cf6a0b018070741b、U1 run 38897611994、quality run 38897611874、native run 38897611887、distribution run 38897653085、binding `verification/r05-r11-repair-01/binding-v4.json` とそのSHA256、formal runs 3件のID、remaining（初回core欠落、現行mise設定でのconsumer-v3正式実行未検証、U15別配布Wasm受理GAP、U14性能・既知JIT panic・session ID保証）を記す。既存107件の id／status／target は変更しない。
- [x] source-manifest.jsonは変更しない（新しいapplication sourceを生成しないため）。required-sections／traceability sensorの実行、独立再レビュー（R-05／R-11／R-13の判定はレビュアーに委ね、文書内に指摘状態の表を書かない）、採用済み正式コマンドでのcheckpoint再検証（verify）を経て、人の完了承認へ進む。新コマンド採用・性能測定・registry公開・tag送信は行わない。

## 再レビュー指摘R-14／R-15への追記（今回Step70）

Steps67〜69の独立再レビュー（READY、R-05／R-11／R-13はFixed）が新たに挙げたR-14（`verification/r05-r11-repair-01/README.md` が依然「正式採用前の候補」と書く）とR-15（レビュアーが標準経路の3コマンドを実行できなかった）に、ユーザーがskeleton checkpointのRequest Changesで対応を指定した。対象はREADME.mdとunit-test-instructions.mdの追記だけで、製品source・binding・実行原本・source-manifest.jsonは変更しない。

### Step 70：README.mdの採用済み注記とunit-test-instructions.mdの再実行記録

- [x] `verification/r05-r11-repair-01/README.md` の冒頭に、このコマンドが2026-10-16T12:32:15Zに人のApprove（Construction Verification Command、SHA-256 `d799bbb9…`）で採用済みであり、冒頭と末尾の「正式採用前の候補」「正式コマンド採用…は親担当の次 gate」はその採用前（2026-10-16T12:31Z時点）の記述として保持する旨を一行追記する。既存本文・原本・binding-v4.json・実行結果は変更しない（R-14）。
- [x] `unit-test-instructions.md` の「今回Steps67〜69：現在のsourceでの正式検証コマンド」節に、標準経路での再実行結果——checkpoint verify `d97dcbec-3dfe-4b71-8871-361aceb6a419`（2026-10-16T18:28:37Z〜18:29:13Z、exit 0、`formal-candidate-1792175317098659000-58394/`、stdout `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`）——と、traceability.jsonの件数確認（`coverage` 107件、`verification_context_history` 4件、`python3 -I` によるJSON parse exit 0）を追記する。手元macOSの `diff_u1` 0件はLinux証拠と呼ばない（R-15）。

## Step71：新しい正式確認コマンド（Build and TestのLoop-back 1、今回の実行対象）

2026-10-17。U14のLoop-back 1で、整数SSEのJIT（署名head 12d6a2f6・1ceae86c）を入れ、正式な性能測定（FR8.3）は合格した（run 39030957672、JITなし平均4.5277秒・JITあり平均3.6349秒、p = 1/1024、20回すべてPASS）。1ceae86cのCIは、PR CI 39028285747、Release package checks 39028285755、U12 quality 39028303336、U13 quality 39028305765（attempt 2）、U14 fuzz 39028307842、source-bound 39028309948、U14 quality 39030957672（attempt 2）がすべて成功した。このため変わった14個のcompiled sourceと、mise.tomlに足したnpmの1行で、採用済みの正式確認コマンドがexit 1になる。U1の再レビュー（iteration 3、READY）はMinor 2件を出した。

- [x] Step 71 — 新しい正式確認コマンドの候補と記録の更新（NFR3、NFR8）。
  1. `verification/loopback1-next/` に、新しいchecker（例：`new_candidate.py`）とbinding（JSON）を作る。旧コマンド `r05-r11-repair-01/final_candidate.py`、`preview-20261015-update/compatibility.py`、`consumer-v3/`、旧binding・旧canonical・旧失敗の原本は変えず、旧い検査をそのまま呼び出して使う（弱めた写しを作らない）。違いは次の3点だけにする。
     - (a) 変わった14個のcompiled source（`tests/guests/u14/{native.c,validation.py,test_validation.py}`、`crates/paludarium-harness/tests/diff_u14.rs`、`crates/paludarium-jit/src/{block.rs,bridge.rs,emit.rs,lib.rs,microbench.rs}`、`crates/paludarium-wasm/src/abi.rs`、`packages/paludarium-wasm/jit-support.mjs`、`packages/paludarium-wasm/tests/{u14-jit.test.mjs,u14-cost-profile.test.mjs}` のうち223個に含まれるもの）を、署名head 1ceae86c の `git cat-file blob` と作業コピーの両方に一致する新しいSHA-256で許す。ほかのcompiled sourceは旧い固定のまま。
     - (b) mise.tomlは、旧いbytesに `"npm:npm" = "12.2.0"` の1行（`bun = "latest"` の次）を足したものだけを許す。
     - (c) 上の1ceae86cのCIのrun ID・head・conclusion（`gh api` で読み取った小さなJSON）と、正式な性能測定の原本（U14の `verification/loopback1-next/perf-39030957672-observations.json`、sha256 `b827a5e1c1ece977be6acab4988d5c1d9dc8a1d54cd5877451eb6d241e402b7c`）を束ねる。
     U14の固定3ファイル（code-summary.md・traceability.json・source-manifest.json）は今のbytesのまま束ねる。後でU11のSafariの2ファイル（U11 Step29）とU14の記録の更新を、新しいbinding fileを足すだけで許せる形にする。
  2. 拒否の回帰を作って実行する：ほかのcompiled sourceの変更、許した14ファイルの別のbytes、ファイルの欠落、別のhead、CIの欠落・失敗、mise.tomlの別の変更、.gitignoreの別の変更、性能の原本のhash違い、produceの変更。すべて拒否すること。
  3. 新しいコマンドがexit 0、旧コマンドがexit 1（理由を記録）であることを確かめる。`verification/loopback1-next/README.md` に、新しいコマンドが確かめることと旧コマンドとの違いを日本語で書く。
  4. U1のcode-summary.mdに「現行Step71」節を足し、上の事実、今のsourceとの一致の記述（旧af9b・4d52の一致は履歴であり、今の一致は新しいコマンドで確かめること）、`ExecutionBridge`・`JitState`・`STATE_BYTES` がC9の外のU14の内部であることを書く（再レビューのMinor 2件）。traceability.jsonは分類・targetを変えず、verification_contextに新しいコマンドの候補を足す。
  5. 正式sensor 2件を実行し、独立再レビューに進む。新しいコマンドの採用（Construction Verification Commandの変更）は人に提示し、承認を受けてからcheckpointで実行する。製品・CI・lock・mise.toml・.gitignore・ほかのUnitの記録・旧verification原本は変えない。

## Step72：Step71の再レビュー（iteration 4、READY）のMinor 5件の修正

2026-10-17。人は新しい正式確認コマンド（`verification/loopback1-next/new_candidate.py`、command SHA-256 `f6c6d3216bbfbe4c483427a985e0ebd8d59732910e6cfb208dbffc84e2fc038b`）を採用した（Approve）。そのうえで、再レビューのMinor 5件も今回の計画で直すよう求めた（「U1 の計画に 5 件の修正を足して、承認します」）。この記入のため、人の選択でreview freezeの確認をこの作業の間だけ切った。コマンド行は変えず、checker・binding・回帰・記録を直す。Step71の実行の原本（`run-1792240798166668000-84752/` など）は履歴として残す。

- [x] Step 72 — Minor 5件の修正（NFR3、NFR8）。
  1. 性能の原本のmoduleを1ceae86cのbuildに結び付ける：u14-quality run 39030957672 のartifactから、性能測定に使ったmoduleのreceipt（`moduleSha256` とsource digest・head）を読み取り専用で取得し、性能の原本の `moduleSha256` と一致し、そのbuildのheadが1ceae86cであることをcheckerで確かめる。取得したreceiptは小さなJSONとして束ね、hashで固定する。旧 `current_semantics` の「保存済みのmodule（fb2fdb）を再利用」という主張は、`result.json` とREADME.mdで「旧い内容に対する主張で、1ceae86cの速さは新しい性能の原本で束ねる」と明記して区別する。
  2. CIをjobの単位で確かめる：7件のrunについて、各runの最新attemptのjob名と結論の一覧を束ね、期待するjobの集合（名前と数）がそろって成功していることをcheckerで確かめる。skippedは期待どおりのものだけを許す。
  3. 同じhead 1ceae86cでのattempt 1の失敗を記録する：U13 quality run 39028305765 attempt 1（`differential tests (x86-64 Linux)`、未観測のIntel CPU signature 000606a6で止まる作り）と、U14 quality run 39030957672 attempt 1（`windows-host` のcoverage付きprobeが30秒の上限。同じheadのU13 qualityでは同じjobが成功）を、理由とjob IDとともにCIの証拠JSONとREADME.mdに書く。性能測定はattempt 1の1回だけで、attempt 2は失敗したjobだけの再実行であることも書く。
  4. 回帰テストを足す：作業コピーとbindingの `new_sha256` を同時に偽にした場合、`run_old_chain` のguard（argv・cwd・timeoutの不一致）、論理viewの範囲外のpathを旧い内容として見せようとした場合、`run_attempt` の不一致、性能の行の対の崩れ（JITあり・なしの数の違い、pairの重複）、module hashの不一致、jobの欠落・失敗。すべて拒否すること。
  5. 記録を直す：この計画のStep71の「14個」「209個」は、正しくは13個（14個目の `u14-single.mjs` は223個の外）・210個である（この注記で直す）。code-summary.mdの古い「現行」見出しを「履歴」に直す。unit-test-instructions.mdの「回帰9種」を実際の件数に直す。
  6. binding・checkerを直したので、新しいbindingのSHA-256とcheckerのSHA-256を記録し直す。新しいコマンド（コマンド行は同じ）がexit 0、回帰がすべて期待どおりであることを確かめる。正式sensor 2件を実行し、独立再レビューに進む。
  7. 再レビュー（iteration 5、READY）の指摘2件への対応：(i) checkerの中身が変わるので、コマンド行が同じでも、修正後のchecker（新しいSHA-256）を人にもう一度提示し、採用の承認（Construction Verification Commandの決定・回答・設定）を受け直してから、U1のcheckpointを検証する。Step71のchecker（`09ec238a…`）での成功（2026-10-17T13:01Zのcheckpoint検証 exit 0を含む）は履歴とし、修正後のcheckerの成功と読み替えない。(ii) 足す回帰は次の9件とし、Step71の20件と合わせて29件にする：`new_sha256` と作業コピーの同時の偽、`run_old_chain` のguardのargv・cwd・timeoutの各不一致（3件）、論理viewの範囲外のpath、`run_attempt` の不一致、性能の行の対の崩れ、module hashの不一致、jobの欠落・失敗。件数と一覧をREADME.mdとunit-test-instructions.mdに書く。製品・CI・lock・mise.toml・.gitignore・ほかのUnitの記録・旧verification原本は変えない。
