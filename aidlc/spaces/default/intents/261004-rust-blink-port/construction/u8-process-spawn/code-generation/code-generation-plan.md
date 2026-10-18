# U8 別のプログラムの起動 — コード生成計画

## Summary

- Builds: Step19。Step18の再レビュー（review-08）のMinor R-14を直す：traceability.jsonのNFR8のnotesの後半（692264fa時点の差分テスト・3OSの結果）が、供給網の検査の結果ではないことを明記する。
- Touches: U8のtraceability.json（NFR8のnotesの1行）とcode-summary.md（1文）だけ。製品・CI・workflow・ほかのUnitの記録・source-manifest.json・unit-test-instructions.mdは変えない。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## 前回のSummary（Step18）

- Builds: Step18。Step17の再レビュー（review-07）のMinor 2件を直す：NFR8のtargetを `ci.yml` にした理由を、要件書の定義（供給網）に合う `cargo deny` とactionのSHA固定に直す。code-summary.mdの冒頭の一文を、R-09・R-11が保留であることが分かる形に直す。
- Touches: U8のtraceability.json（NFR8のnotesの1行）とcode-summary.mdだけ。製品・CI・workflow・ほかのUnitの記録・source-manifest.json・unit-test-instructions.mdは変えない。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## 前回のSummary（Step17）

- Builds: Step17。U8の確かめ直し（review-06、NOT-READY、Critical 1・Major 3・Minor 4）のR-04〜R-11をU8の記録で直す：traceability.jsonの消えたtargetと逆引きの行、manifestの消えたworkflow、古い状態を今のものとして書いた箇所、今は測られていないU8の測定の明記。製品・CIは変えない。
- Touches: U8の記録だけ（code-summary.md、unit-test-instructions.md、traceability.json、source-manifest.json）。製品・CI・workflow・ほかのUnitの記録は変えない。呼び元が消え、実行すると失敗する `.github/scripts/u8-current-diagnostic.py`（R-09）を消すかどうかと、測られていない測定をCIに戻すか（R-11）は、製品の変更なので、残りのUnitを見てからまとめて決める。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-f.py・binding-e06f.json）でのcheckpointがexit 0になることで確かめる。

## 今回の計画：Step19（Step18の再レビューのMinor R-14を直す）

2026-10-19 JST。Step18の再レビュー（review-08、READY、新しいMinor 1件）の後、checkpointで人がRequest Changesを選んだ（先にR-14を直す）。

- [x] Step 19 — **R-14を記録で直す**。traceability.jsonのNFR8のnotesの「以下はその時点の記録。」を「以下は692264fa時点の記録で、NFR8（供給網）の検査の結果ではなく、当時の `u8-native-diagnostic.yml` が動かした差分テスト・3OSのテストの結果である（今の供給網の検査は上のとおり `ci.yml` の `cargo deny` とactionのSHA固定）。」に直す。JSONとして行ごとに直し、変わったのがNFR8の1行だけであることを直す前の版と比べて確かめる（target・status・idは変えない）。code-summary.mdの「現在の状態（Step17）」節のtraceability.jsonの箇条に、Step19でこの区別を足したことを1文で書く。unit-test-instructions.md・製品・CI・workflow・ほかのUnitの記録・source-manifest.jsonは変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR8。

## 前回の計画：Step18（Step17の再レビューのMinor R-12・R-13を直す）

2026-10-19 JST。Step17の再レビュー（review-07、READY、新しいMinor 2件）の後、checkpointで人がRequest Changesを選んだ（先にR-12とR-13を直す）。

- [x] Step 18 — **review-07のMinor 2件を記録で直す**。(1) R-12：NFR8は要件書（`inception/requirements-analysis/requirements.md` のNFR8）で供給網（依存はcrates.ioだけ、ライセンスがApache-2.0と両立、GitHub ActionsのSHA固定）と決められている。traceability.jsonのNFR8のnotesの先頭の理由を「`ci.yml` の `dependencies` のjobの `cargo deny`（取得元・ライセンス・既知の脆弱性）と、actionのSHA固定・読み取りだけの既定の権限が、NFR8の供給網の検査を担う」に直す（JSONとして行ごとに直し、変わったのがNFR8の1行だけであることを直す前の版と比べて確かめる。targetは `ci.yml` のまま、statusとidは変えない）。code-summary.mdの「現在の状態（Step17）」節のtraceability.jsonの箇条の同じ理由も直す。(2) R-13：同じ節の冒頭の「R-04〜R-11を直した」を「R-04〜R-08とR-10を直し、R-09とR-11は記録して人の判断を待つ」に直す。unit-test-instructions.mdは変えない（Step17の節と期待結果は同じ）。製品・CI・workflow・ほかのUnitの記録・source-manifest.jsonは変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR8。

## 前回の計画：Step17（確かめ直しの指摘を記録で直す）

2026-10-19 JST。U15のStep22〜28（push、head 27d05de1）で、U8のmanifestにある `ci.yml` が変わり、`u8-current-verification.yml`・`u8-native-diagnostic.yml` が消え、正式な確認コマンドがU15の `entry-e3c29d1d/entry-f.py`・`binding-e06f.json` に替わった。U8の確かめ直し（review-06、NOT-READY）の後、checkpointで人がRequest Changesを選んだ（U8の記録のR-04〜R-11を直す。測られていない測定をCIに戻すかは、まとめて決める）。人の指示：「ワークフローの順で進めてください。U1 の確かめ直しから始めて、ファイルが変わった Unit を順に確かめ直し、U15 のレビューと完了確認、U11 の確かめ直しまで進めてください。」

- [x] Step 17 — **確かめ直しの指摘を記録で直す**。traceability.jsonは文字列の置き換えではなく、行（idまたはpath）ごとにJSONとして直し、直す前の版（27d05de1）と比べて変わった行を確かめる。(1) R-04：traceability.jsonのcoverageのNFR8のtargetを `.github/workflows/ci.yml`（差分テストのjobが `diff_u8` を動かす）に替え、notesの先頭に「2026-10-19：27d05de1で `u8-native-diagnostic.yml` が消えたため、targetを替えた。以下はその時点の記録。」を足す。reverseから、消えた `.github/workflows/u8-native-diagnostic.yml` と `.github/workflows/u8-current-verification.yml` の2行を外す（statusとidは、ほかの行では変えない）。(2) R-05：source-manifest.jsonのwritesから、消えた2本を外す（manifestはpathだけを持ち、hashは持たない）。(3) R-06：code-summary.mdの先頭に「現在の状態（2026-10-19 JST、Step17）」節を足し、今の正式な確認コマンド（entry-f・binding-e06f、command SHA-256 `00f5c883…a159`）、今のtoolchain（`nightly-2026-10-11`）、U8に関わる製品の変更、27d05de1のCI 8 runの成功を書く。「現行」「今回」で始まる見出しは「履歴：…（作成時の見出しは「…」）」にする（本文は変えない）。(4) R-07：traceability.jsonのNFR9・NFR3のnotesの先頭に「（履歴：692264fa時点の旧pin・旧run。今のtoolchainは `rust-toolchain.toml` の nightly-2026-10-11、27d05de1のCIはU15の `verification/ci-27d05de1/ci-27d05de1.json`）」を足す。(5) R-08：unit-test-instructions.mdの古い見出しと「現在の承認済みコマンド」「計画時点では未実行」「今は計画のため全U8テストは未検証」に、その時点の記述であることの注記を付ける（計画のときに書いた）。(6) R-09：`.github/scripts/u8-current-diagnostic.py` は呼び元が無く、消えたworkflowを読むので実行すると失敗する（履歴・実行不可）ことを新しい節に書く。traceability.jsonのreverseのその行とmanifestのその行は、ファイルが残っているので残す。(7) R-10：code-summary.mdの各節の「先頭の『現行Step16〜18』節を参照」の案内は、新しい先頭の節を指すことを新しい節に書き、候補コマンド `verify-current-u1-u7-u9-u3-u5-u6-u8.py` は不採用・履歴であることを書く。(8) R-11：U8の受け入れが今どこで動くか（`diff_u8` は `ci.yml` の差分テスト、3OSのテストは `ci.yml` の `test` のjob、workspaceの80%、fmt・clippy・deny、ASanは `u11-fuzz.yml`・`u14-fuzz.yml`）と、**今は測られていないもの（U8専用のnative診断のrunの個別のログ、`u8_` の56件を名前で個別に記録する検査、324入力の前後のハッシュの照合）**、もともと未検証のもの（U8のfork/exec/waitのNode/Safari）を書く。製品・CI・workflow・ほかのUnitの記録は変えない。そのあと正式sensor 2件、独立再レビュー、checkpointの検証、人の承認に進む。NFR3、NFR8、NFR9。

## 前回のSummary（Step16）

- Builds: Step16。製品は変えない。計画の古くなったTesting Contractを今の内容（`sha256:7ff27a24…`、方針は同じでproject層の学びが足されただけ）に置き換え、今の正式確認コマンドでU8を確かめ直す。
- Touches: この計画のTesting ContractとStep16の節だけ。製品・テスト・ほかの記録は変えない。
- Tests: 新しいテストの実行はない。独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpoint。Steps13〜15の結果は履歴として保持する。

## 前回の計画：Step16（Build and TestのLoop-back 1：Testing Contractの更新と再確認）

2026-10-17。U14の整数SSEのJIT（署名head 1ceae86c）とU1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。U8の担当のsource-manifestには、今回変わったファイル（U14のJIT・wasm・テスト、`crates/paludarium-wasm/src/abi.rs`、`mise.toml`）は含まれない。この計画の「## Testing Contract」は、memory（project.mdの学び）の更新で古くなっていたため、`aidlc engine testing-posture render` の出力に置き換えた。テストの方針（Methodology custom、Ordering、Standard、80%下限など）は変わらない。

- [x] Step 16 — 製品・テスト・記録は変えない。今の正式確認コマンドでU8のcheckpointを確かめる。独立再レビューで、U8の記録が今のsourceと合っていることを確かめる。Steps13〜15の結果は履歴として保持し、今回の新しい実行とは数えない（NFR3、NFR9）。
- [x] Step 17 — 再レビュー（iteration 2）のMajor・Minorへの対応（人のRequest Changes）。製品は変えない。code-summary.mdを次のように直す：(a) 見出し「## 現在の検証済み結果」を「## 履歴：署名head 692264faの検証結果」に変え、その節の数値（workspace全体coverage 93.06%／11427行、3OSのClippy・deny、CI run）は692264faの時点のもので、U14の変更（12d6a2f6・1ceae86cで `paludarium-jit` と `crates/paludarium-wasm/src/abi.rs` が変わった）の後のsourceについての数値ではないと明記する。(b) 「## 正式検査・最終確認の境界」の節の旧い未実行の候補 `verify-current-u1-u7-u9-u3-u5-u6-u8.py` を履歴とし、今の正式確認コマンドが `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u2-integer-isa/code-generation/verification/loopback1-next/u2_candidate.py` であること、2026-10-17のU8 checkpointの検証がexit 0（`source_compatibility: PASS`、`u2_candidate: PASS`、`U15_acceptance: GAP`）だったことを書く。(c) 先頭に「現行Step16〜17（Loop-back 1）」節を足し、Testing Contractの置き換え、担当sourceが今回の変更に含まれないこと、上の (a)(b) をまとめる。traceability.jsonの分類・targetは変えない。正式sensor 2件を実行し、独立再レビューと今の正式確認コマンドでのcheckpointに進む。
- [x] Step 18 — 再レビュー（Step17のiteration 1、READY）のMinorへの対応（人のRequest Changes「この Minor も直す」）。製品は変えない。code-summary.mdの「履歴：署名head 692264faの検証結果」より後ろの4つの節（「実コマンド・入力と責務」「ASanの限定再利用と未検証」「失敗と歴史的証拠」「正式検査・最終確認の境界」）の見出しの直後に、それぞれ「（履歴：署名head 692264faの時点の記述。この節の「現行」「今回」はその時点を指す。今の状態は先頭の「現行Step16〜18」節を参照。）」の一行を足し、先頭節の見出しを「現行Step16〜18」に直す。本文は変えない。正式sensor 2件を実行し、独立再レビューと今の正式確認コマンドでのcheckpointに進む。

## 前回のSummary（Steps13〜15）

- Builds: 既存fork/clone・vfork・execve・wait4を保持し、承認された現行ソースの追加検証をSteps13〜15で行う。
- Touches: U8文書・証拠、新しい専用診断CI/helper。製品とguest fixtureは変更しない。Steps1〜12と旧証拠は履歴として保持する。
- Tests: fresh Linux全29差分＋runner1、3OSのU8本体42件と既存U8回帰14件、U5内部33/U6内部49回帰、fmt/Clippy/依存4検査、既存workspace全体coverage80%以上。ASanは条件一致対象のみ限定再利用する。

今回の件数訂正：`u8_tests::` はKernel28/MMU7/Runtime7の本体42件。旧U8入口 `u8_` は既存 `sockets::u8_pipe_tests` 7件と `threads::u8_exec_thread_tests` 7件も含み、Kernel42/MMU7/Runtime7の合計56件となる。本体42件と既存回帰14件を別々に記録する。以前の「u8_tests::で56件」という報告は誤りで、旧原本を保持して訂正する。テスト・下限・品質条件は減らさず、診断filterを既存 `u8_` に整合する。

## 承認された現行ソース追加検証（Steps13〜15）

- [x] Step 13: 現行実装を保持し、U8専用診断CI/helperで全入力・両lock・実使用compiler・ツール版・設定を固定する。新診断ファイルも入力へ明示し、before/after/current SHAを保存する。旧06d58952の25担当path中6変更、現行322入力の旧commit投影207一致/34変更/81未存在、旧nightly10-01と現行compiler相違を歴史として記録する。最新ツールを公式確認し、追加製品設定変更が必要なら具体的最小案を示す。wait4のEFAULTでもreapするLinux動作と既存公開C10を維持する。
- [x] Step 14: 同一現行ソースの署名済みCIでfresh x86-64 Linux U8全29ケース＋runner1を実行する。Rust Command spawn/status/output/missing、wait-faultを含む既存ケースとmaskを保持し、stdout/stderr/exit/errnoと原本を保存する。3OSで既存 `u8_` filterによる本体42件＋既存pipe/exec回帰14件を個別確認し、関連U5 Kernel27/Runtime6の33件、U6 Kernel49件をignored0で確認する。fmt/Clippy警告エラー/依存4検査の実exitを保存する。既存workspace全体coverage経路でempty profileからfresh U3 nativeとinstrumented CLI・U8/U5/U6差分を含む測定を実行し、同じ対象規則・全体80%下限を維持する。U8専用coverageを全体と呼ばない。30秒入力制限・kill/reap・比較規則を維持し、失敗・0件・skipを合格にしない。
- [x] Step 15: 既存load_elf/syscall_args/mmu_ops等のASan保存証拠は対象ごとに現在依存閉包・両lock・実使用compiler・flags・設定・原本一致を証明できる範囲だけ再利用し、不一致は未検証と具体的追加案を示す。新CIの全入力・署名head/job・生ログ・実exit・coverage分母を結合して4成果物・strict source-manifestを更新し、独立した全要件割当による正式検査と独立レビューへ渡す。U8のNode/Safari fork/exec/wait成功を共有launcherの証拠で代替せず、U11境界として明記する。新最終確認候補は構文確認までとし、新承認後に実行する。strict guard、80%下限、30秒制限、先行Unitの証拠と成果物を維持する。ID競合の完全解消は未検証と区別する。

## Sources

- inception/requirements-analysis/requirements.md：FR2.8、FR2.1、FR3.1、FR3.4、FR4.1、FR9.1、NFR1〜4・NFR7〜9。
- inception/units-generation/unit-of-work.md：U8。unit-of-work-story-map.md は FR2.8 を U8 に割り当てる。独立した U8 の AC／BR 文書は存在しないため、直接 FR／NFR を追跡する。
- inception/domain-design/components.md：Process、Thread、AddressSpace、FileDescription、Kernel→Loader、Runtime→Kernel。
- inception/contract-design/contract-summary.md：C4・C6・C7・C8・C10。
- planning-confirmation-questions.md：承認済みの U8 範囲。2026-10-09T19:39:35Z に SUMMARY_CONFIRMATION_RECORDED がある。
- U8 の個別 Functional／NFR／Infrastructure Design は未作成。既存の型と上記の契約を基に実装する。

## Design

Kernel に親子関係と終了状態を共有するプロセス管理を加える。既存の ThreadGroup は一つのプロセス内のスレッドを管理し、子プロセスごとに独立させる。PID/TID の割当は衝突しない共有元にまとめる。fork は呼出しスレッドの CPU とアドレス空間を複製する。私有メモリは隔離し、MAP_SHARED の共有を維持する。fd 表は複製するが、開いたファイルの offset／pipe／socket／eventfd の実体は共有する。

vfork 相当の clone は CLONE_VM と CLONE_VFORK を区別し、exec 成功または子の終了まで親を待機させる。既存 U5 の CLONE_THREAD 経路を維持する。clone3 を Rust Command が試す場合、未対応なら ENOSYS による既存 libc の fallback をネイティブ trace とゲストで確認する。必要な pipe2・dup・CLOEXEC とエラー通知経路を U6/U7 の実装に接続する。

execve はゲストの path／argv／envp を検査付きで読む。新しい AddressSpace に Loader で読み込み、成功時だけ CPU・メモリ・fd の CLOEXEC・シグナル disposition／TLS を切り替える。失敗時は旧プログラムを継続し、ENOENT／EFAULT／ENOEXEC 等をゲストに返す。ホストのプロセスを生成しない。

Runtime の実行コンテキストはプロセスごとのメモリと ThreadGroup を持ち、同じ Session の VFS・Host を利用する。子の終了と実行失敗を親待機側に通知する。Session の kill とエミュレータ自身のエラー時には全実行コンテキストを起床・終了させる。プロセス表・メモリ・fd のロックを Host 待機中に保持しない。

wait4 は特定 PID と -1、WNOHANG、終了 status の通常終了／シグナル終了を優先する。一度だけ reap し、結果書込みが EFAULT の場合も終了情報を回収済みにする（Linux native-first の wait-fault ケースで確認し、ユーザーが計画修正を承認）。ECHILD／EINVAL／EFAULT、割込みと SA_RESTART、rusage の書込みを扱う。停止／再開通知は対象プログラムが要求した場合に追加し、その前に native ケースを用意する。process group 対応の必要性も同じ証拠で決める。

## Implementation Steps

- [x] Step 1 — U8 の実行基盤を準備する。既存 diff_u7 の bounded 実行・VFS 配置方法を確認し、tests/guests/u8/build.sh、observe.py、cases.json と harness の support/u8.rs、diff_u8.rs を作る。最初の実行可能ケースの前に runner と unit-scoped コマンドを成立させる。差分比較の基準は FR2.8・FR9.1・NFR1・NFR7。
- [x] Step 2 — syscall 実装の前に C の fork/clone/vfork/exec/wait と Rust std::process::Command の static-musl ゲストを作り、x86-64 Linux で native-only 実行する。16 ケース以上の stdout／stderr／status／errno、必要な syscall と clone flags を記録する。PID／時刻／usage 値は真偽条件へ正規化し、順序は同期で固定する。期待結果は毎回 native 実行で作り保存しない。FR2.8・FR4.1・FR9.1。
- [x] Step 3 — crates/paludarium-mmu/src/lib.rs に fork 用のアドレス空間複製を加え、その後 src/u8_tests.rs の 7 件を実装・実行する。私有領域、共有領域、protection、brk、unmap、親子間書込み、エラーを検証する。FR2.8・NFR2・NFR3。
- [x] Step 4 — crates/paludarium-kernel/src/processes.rs を作り、lib.rs・threads.rs と接続する。親子関係、PID/TID、プロセス固有 ThreadGroup、zombie、起床を実装し、その後 u8_tests.rs のプロセス管理 7 件を実行する。終了状態は全スレッド終了まで公開せず、exit_group は子の group のみに作用させる。FR2.8・NFR2・NFR7。
- [x] Step 5 — Step 2 の oracle を先に確認したうえで、process clone／fork／vfork と fd 継承を threads.rs・processes.rs・files.rs に実装する。fork の戻り値、親子の独立性、共有 fd offset、VM/VFORK の待機解除、tid stores、無効 flags を差分比較する。既存 U5 clone を分岐で維持する。FR2.8・FR2.3・NFR4。
- [x] Step 6 — execve 引数読出しと切替えを processes.rs、Kernel、Runtime、必要な Loader 接続部に実装する。Step 2 の成功／ENOENT／EFAULT／不正 ELF／argv-env／CLOEXEC ケースを比較する。その後境界の単体テスト 7 件を実行する。成功時のみ状態を交換し、失敗時に待機解除や fd 破棄を行わない。FR2.8・FR3.1・FR3.4・FR4.1・NFR2・NFR4。
- [x] Step 7 — wait4 と子終了通知を processes.rs・threads.rs・syscalls.rs に接続する。特定 PID／任意の子／WNOHANG／終了 status／二重 reap／EFAULT／ECHILD／割込みの native oracle を先に確認してから実装・比較する。rusage の配置と正規化を記録する。FR2.8・NFR1・NFR2・NFR7。
- [x] Step 8 — crates/paludarium-runtime/src/lib.rs・workers.rs に子プロセスの実行、メモリ切替え、親の待機、全体 cancellation を接続する。その後 src/u8_tests.rs の 7 件を実行する。子の失敗を親の終了と混ぜず、待機中のロックと取りこぼしを検証する。FR2.8・NFR2・NFR7。
- [x] Step 9 — Rust Command の spawn/status/output、存在しない executable、pipe による起動エラー通知を Step 2 の trace と比較する。追加 syscall が必要な場合は U8 の起動に必要な分だけ oracle を先に加えて実装する。停止／再開通知を要求する証拠があれば、そのケースを先に加える。FR2.8・FR4.1・NFR4。
- [x] Step 10 — U8 全単体・差分テストを実行し、U5 スレッドと U6 fd/event/socket の回帰を実行する。Linux の全体 80% 行カバレッジを既存測定経路で確認する。ローカルで Linux を利用できなければ実行可能な CI 検証を要求し、未実行を PASS にしない。NFR1・NFR3・NFR7。
- [x] Step 11 — 変更した Rust を整形し、関係クレートの clippy を -D warnings で実行する。依存追加が必要なときだけ Cargo.toml／Cargo.lock とライセンス検査を更新する。既存 Linux 差分 CI に U8 を接続し、ホスト専用処理を Kernel に入れない。NFR3・NFR8・NFR9。
- [x] Step 12 — 実装判断・検証結果・未検証事項を code-summary.md に記録し、source-manifest.json と traceability.json に変更した全 source と FR／NFR の対応を書く。README.md は U8 の対応内容だけ追記する。実装後のレビューに進む。

## Test Inventory

4 部品で各 7 件、計 28 件を下限にする。部品は MMU 複製、Kernel の親子管理、exec 境界、Runtime の実行接続。差分ケースは fork 戻り値、私有メモリ、共有メモリ、fd offset、vfork exec、vfork exit、exec argv/env、exec ENOENT、exec EFAULT、不正 ELF、CLOEXEC、wait specific、wait any、WNOHANG、シグナル終了、二重 reap の 16 件を最低限とし、Rust Command と追加の境界ケースを足す。単体は各部品の正常系と 2 件以上の異常／境界を含む。全待機ケースに wall-clock timeout を付ける。

## Boundaries and Verification

既存公開 C10 を維持する。Kernel・Runtime 間の内部型を変更する場合は全利用側を同じ変更で更新する。現時点は計画のみでテスト未実行。実装順序と品質目標は下記 Testing Contract と unit-test-instructions.md に従う。上流フックの修正はこの実装計画に含めない。

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

