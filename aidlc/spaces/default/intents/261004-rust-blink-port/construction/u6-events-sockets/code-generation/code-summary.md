# U6 イベントとソケット

## 現在の状態（2026-10-19 JST、Step20）

本節はStep20の記録である。U15のStep22〜28で製品のファイルが変わってfork `codex/build-and-test` へ送られた（head 27d05de1、e3c29d1d→8b415a7c→8360be2e→27d05de1、4つともVerified）ので、U6を確かめ直した（`reviews/review-06.md`、NOT-READY、Major 4・Minor 2）。checkpointで人がRequest Changesを選んだので、U6の記録で直せるR-04〜R-10を直した。U6の製品のコード・CI・workflow・ほかのUnitの記録は変えていない。traceability.jsonは、NFR8・NFR9のtargetと、各行のnotesの先頭の注記だけを変えた（statusとidは変えていない）。

- **今の正式な確認コマンド（R-07）**：`aidlc/spaces/default/intents/261004-rust-blink-port/verification-command.txt` の U15 `construction/u15-release/code-generation/verification/entry-e3c29d1d/entry-f.py`・`binding-e06f.json`（head 27d05de1、人が2026-10-19に採用、command SHA-256 `00f5c8832e04f7d27b30c6b445fdc30e0e5d233dfa5452e02c2c99368a08a159`）。今のtoolchainは `rust-toolchain.toml` の `nightly-2026-10-11`。下の節の `u2_candidate.py`・`verify-current-…` の候補、head 11c033c7、compiler 32dba69d6／LLVM 23.1.3、Safari 26.6.2、「未検証」「承認前は実行しない」は、それぞれの時点の記述である。U6のcheckpointはentry-fで確かめる。entry-fは作業コピーのbytesを `aidlc/` の外だけで比べるので、U6の記録の変更はその結果に影響しない想定である（結果はcheckpointの記録が持つ）。
- **U6に関わる製品の変更**：U6の製品のファイルは変わっていない。U6のsource-manifestにあった `u6-current-verification.yml`・`u6-native-diagnostic.yml`・`u6-quality.yml` は消えた（U15のCIの整理、`construction/ci-pipeline/ci-config.md` の「消す」）。source-manifest.jsonのwritesから3本を外した（33件→30件、R-06）。
- **U6の受け入れが今どこで動くか**（review-06の確かめた点）：events・socketsの600秒のASan/LSanのfuzzは、`ci.yml` が呼ぶ `u11-fuzz.yml` と、夜間の `u14-fuzz.yml`。3OSのテスト（`paludarium-kernel`、`u6_tests` を含む）は `ci.yml` と `u14-quality.yml`。`diff_u6` は差分テストのjobの `--test` 一覧になく、`ci.yml` のcoverageのjobの `cargo llvm-cov --workspace`（`PALUDARIUM_U6_EMULATOR` を設定）の中で動く（R-10）。27d05de1のCI 8 runはすべて成功した（U12は人が認めた1 jobの再実行。記録はU15の `verification/ci-27d05de1/`）。
- **U6だけの測定は今は測られていない（R-08）**：U6の固定9ファイルのcoverage（前回85.83%）、production wasmのNode/本物Safariの102件（共有20件とU6の82件）、`u6_tests::` の49件・ignored 0の件数は、27d05de1でU6のworkflowが消えてから、どのworkflowでも測られていない。残るのはworkspace全体・U11・U9の80%の下限と、U11の14ケースである。NFR3・NFR7・FR2.4〜FR2.7のOKの根拠は11c033c7時点の履歴で、traceability.jsonの該当行のnotesの先頭にもそう書いた。CIに戻すか受け入れるかは、残りのUnitを見てからまとめて決める（人の判断、2026-10-19）。
- **呼ばれていないU6の道具（R-09）**：`scripts/u6-coverage.py`・`scripts/u6-wasm-guests.py`・`scripts/u6-runner-test.py`・`packages/paludarium-wasm/tests/u6-check.mjs` は、残りのworkflowから呼ばれていない（手動用・CI未接続）。
- **traceability.json（R-05・R-07）**：NFR8のtargetを `.github/workflows/ci.yml`、NFR9のtargetを `rust-toolchain.toml` に替え、notesの先頭に理由を書いた。11c033c7の観測を書いた13行（FR2.4〜FR2.7、FR9.1、NFR1〜NFR5、NFR7〜NFR9）のnotesの先頭に「（履歴：11c033c7時点の観測。今の状態はcode-summary.mdの先頭の節）」を1回ずつ足し、NFR3・NFR7・FR2.4〜FR2.7にはU6だけの測定が今は測られていないことの注記を1回ずつ足した。最初の作業では同じ文の行が多かったため注記がFR2.4の行に重なって入ったので（review-07のNOT-READY）、27d05de1のtraceability.jsonから行ごとに作り直した。
- 「現行」「今回」で始まっていた見出しは「履歴：…（作成時の見出しは「…」）」にした。本文は変えていない。下の「履歴：Step19〜20」節の「今回Steps16〜18の現行実行」は、今の見出し「履歴：Steps16〜18の現行実行（2026-10-17のStep19〜20の前）」を指す（R-04）。
- 未検証：この作業ではentry-fを実行していない（checkpointで実行する）。独立再レビューはこの記録の後に行う。
- 下の節は、それぞれの時点の履歴として読む。

## 履歴：Step19〜20（Build and TestのLoop-back 1）：Testing Contractの更新と証拠の時点（作成時の見出しは「現行Step19〜20（Build and TestのLoop-back 1）：Testing Contractの更新と証拠の時点」）

2026-10-17。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c）と正式確認コマンドの更新（今はU2の `verification/loopback1-next/u2_candidate.py`）の途中で、Code Generationの段階全体の作り直しのため、U6を確かめ直した。
- (a) 計画の「## Testing Contract」を、memoryの更新で古くなっていたため、今の内容（contract `sha256:7ff27a24…`）に置き換えた。テストの方針（custom、Ordering、Standard、80%下限）は変わらない。
- (b) U6の担当source（source-manifest）は、12d6a2f6・1ceae86cで変わったファイル（U14のJIT・wasm・テスト、`crates/paludarium-wasm/src/abi.rs`、`mise.toml`）を含まない。製品・テストは変えていない。
- (c) 下の「今回Steps16〜18の現行実行」にあるNode・本物Safariの全102ケースの証拠は、U14の変更より前のproduction wasm module（`4482b157…`、head 11c033c7）に対するものである。1ceae86cから作るmoduleは、JITの状態の受け渡し（144→400 byte）が変わったため別物になる。1ceae86cのmoduleでの4環境（Node・Chromium・Firefox・本物Safari）の比較はU14 quality run 39030957672で行ったが、U6の102ケースは今のmoduleでは測り直していない。
- (d) 「U6の記録が今のsourceと合っている」は、独立再レビューで記録とsource-manifestを照らした範囲の確認であり、新しい実行ではない。
- 下の「今回Steps16〜18」の節は、その時点の履歴として読む。

## 履歴：Steps16〜18の現行実行（2026-10-17のStep19〜20の前）

検証済み：署名Verifiedのhead11c033c7d58166fb9292f5b822f9a92b008c779c、run38086676529でfresh Linux差分84件とTokio10反復、3OS各Kernel49件・ignored0とfmt/Clippy警告エラー/依存4検査が成功した。固定9製品ファイルの現行LCOVは2726/3176行＝85.8312%（下限80%）。旧分母2785と今回はソース行集合が異なるが、選択9ファイルと測定規則を減らしていない。原本はverification/step18-final-raw/。

検証済み：同production module4482b1574987ff62cc8f9f872e42e5dbe6f4fc91273103da6abc0dd8ffd18fe3と同fresh native JSONを用いたNode/本物Safari26.6.2は、共有20＋U6非threaded82＝全102件が成功し実exit0。SafariはcrossOriginIsolated/sharedMemory、13,489ms、driver_reaped/server_closedを確認した。前後と現在の322入力は厳密path/hashで一致し、生成82guestはsourceから区別してbinary SHAへ結合する。

検証済み：この最終runのevents2465471回・sockets2781965回は各601秒ASan/LSanを完走し、実exit0。actual compiler32dba69d6/LLVM23.1.3、instrumentation、runtime設定、flags、suppression、依存閉包、binary hash、前後/current全322入力と両lockを保存した。8ジョブすべて成功し、1144原本hashをverification/step18-current-proof.jsonへ結合した。旧run成功ジョブを今回の新実行へ読み替えていない。準備時のactual cargoへの旧+toolchain引数、native musl target不足、Tokio反復集計path不足は診断側の不備として失敗原本を保持した（step17-attempts.jsonおよび失敗説明）。製品Rustとfixtureは変更せず、u6-check.mjsの総数assert一行103→102と新診断2ファイルに限定した。

ドキュメント根拠：先行Unit証拠の旧320入力は今回の全入力一致とは呼ばず、319一致＋明示したassert一行の旧/新SHAで限定的に結合する（verification/step18-baseline-binding.md）。新確認候補verify-current-u1-u7-u9-u3-u5-u6.pyは構文確認のみで、実行には新しいコマンド承認が必要。C66/Tokioのwasm guest WorkerはU11境界、セッションID競合の完全解消は未検証。

## 履歴：Steps13〜15の確認と未検証（作成時の見出しは「今回Steps13〜15の確認と未検証」）

この節は追加検証前の初回判定である。下記の不足は上のSteps16〜18で現行原本を取得して解消した。

検証済み：現行実compiler32dba69d6／LLVM23.1.3を明示したKernel u6_testsは49 passed・0 failed・0 ignored・exit0でした（verification/step14-local-u6.raw.log）。旧e33cfbb4の439入力は397一致・42変更・欠落0、担当31leafは22一致・9変更です（verification/step13-current-audit.json）。共有mtime対応とRust統一後の現行成功を旧snapshotから推定しません。

未検証：現行U6のfresh84差分・Tokio10反復・同9file coverage80%・3OS品質・events/sockets各600秒・production Node/本物SafariのU6 82件。旧compiler21b707e3f／LLVM23.1.1と依存ソース・root lockが異なるため、旧品質を現行へ再利用できません。U9現行共有20ケースはU6の82件を含まず代替になりません。追加案はverification/step14-additional-verification-proposal.mdに保存し、承認前には重い追加CIや製品・fixture・既存CIの変更を行いません。

ドキュメント根拠：現行checks.mjsは共有20件、U6非threaded82件を追加すると計102件です。旧u6-check.mjsの103固定assertのみの整合が必要です。C66とTokioのwasm guest WorkerはU11境界を維持します。新U6証拠を既存最終確認コマンドは検査しないため、新候補の実行は別途exact command承認が必要です。セッションID競合の完全解消は未検証です。

## 歴史snapshot e33cfbb4の実装と検証

以下の「現module」「現head」は当時のsnapshotを指します。今回の現行ソースに対する成功ではありません。

検証済み：signed head `e33cfbb4bf1daefea2efa00d8c6a1f5f35848ef6` の439 source leafが一致し、Linux fresh native84差分とTokio10反復が成功した。3OS fmt/clippy/denyと先行Unit回帰、固定9file coverage2352/2785=84.45%（floor80）、両ASan/LSan fuzz要求600秒・実測601秒（events2739611runs、sockets2533386runs）が成功した。[final-proof](verification/final-proof.json)で原本head/job/stream/hashを結合する。

R-01は成功writeごとの入力callback、eventfd readとsocket write segment完全消費時のOUT callbackを修正した。socket部分readではsegment残量を保持し、既存full→space backpressure境界も維持する。R-02はepoll_pwait一時maskでhandlerを配送し、handlerのaction/self blockとsignal frame/sigreturnの旧mask復帰を保持する。同期内部テストはmasked/ignored/metadata-onlyも確認する。局所Kernel149/U6 49/Host40と実行コマンドは[repair-product-local.md](verification/repair-product-local.md)。Linux container RustのQEMU SIGSEGVとcase56 native差異は同文書に残し、signed Linux期待値を維持した。局所cross-build Tokio10回とCI fresh10回は別の証跡。

現module SHA256 `91c0f246b9043c996e40ba2fc80308dfae85d3f42ed99d0ea078e236a34d364e` のNodeと実Safari27.0.1は各103件成功した。Safariはnative UIから[JSON原本](verification/revision-final-safari-raw-report.json)を保存し、[補足receipt](verification/revision-final-safari-report.json)でisolation/sharedMemoryとtest tab/server清掃を記録する。WebDriver成功は主張しない。対象は既存21件＋非threaded U6 82件。C0〜81のC66を除きUnixStreamを含む。Tokio timerとC66のWasm guest WorkerはU11境界で、Linuxでは両方を含む84件を検証した。

AF_INET/AF_INET6は承認済み隔離ポリシーでEAFNOSUPPORTを返す。cases52〜54はその拒否を比較し、case60はnative SIGKILL -9とCLI137を正規化する。queue容量や部分write量は固定期待値にせず、EAGAIN・部分成功・OUT遷移・peer drainの関係を比較する。timerfdは対象native traceで使われず追加していない。

[source-manifest](source-manifest.json)の31 leafとprior417のunion439、凍結U5文書を含む歴史78を保持した。旧aeb7の69差分/88browser品質は[歴史proof](verification/historical-aeb7-proof.json)へ保存し、修正前native84/diff75pass9failも保持する。生成ELFはsource claimへ混ぜずbinary hashへ結合する。先行U1/U2/U3/U4/U5/U7/U9は現head native差分と3OS library/CLI testsで回帰確認した。有限入力から全入力、U10 probe全量、U11 guest Worker達成を主張しない。独立レビューと完了checkpointは親が担当する。
