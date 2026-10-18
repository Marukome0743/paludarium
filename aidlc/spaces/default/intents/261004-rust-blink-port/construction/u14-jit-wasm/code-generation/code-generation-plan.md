# U14 wasm JIT：コード生成計画

## Summary

- Builds: Step47。残しているMinor 3件（再レビュー review-11 の R-14・R-15・R-16）を記録で直す。U14の記録は、もう正式な確認コマンドの入口（binding-07）に固定されていない（2026-10-18から正式な確認コマンドはU15の `entry-e3c29d1d/entry-c.py`）ので、traceability.json と code-summary.md を直せる。製品・workflow・入口・bindingは変えず、CI・性能測定・pushもしない。
- Touches: U14の traceability.json（FR8.2・FR6.3・FR7.2 と NFR2・NFR3・NFR8 の行の説明文だけ）、code-summary.md（先頭に「現在の状態」の1節）、計画と手順書。
- Tests: 新しい試験はない。正式sensor 2件と、今の正式な確認コマンド（entry-c.py）でのcheckpointがexit 0になることで確かめる。

## Step47（残しているMinor R-14・R-15・R-16を記録で直す）

2026-10-18 JST。人の指示：「先に修正しましょう。提案通りお願いします。」（Safariの直し・CIの整理・残しているMinorをまとめて直す。U1・U14はそれぞれの記録のMinorだけを直す）。

- [x] Step 47 — **R-14・R-15・R-16を記録で直す**。(1) R-14：traceability.json の FR8.2・FR6.3・FR7.2 の「現行」の文に、根拠の U13 quality 39028305765 と U14 quality 39030957672 が attempt 2 で成功したこと（attempt 1 の失敗は code-summary.md 参照）を一言足す。(2) R-15：NFR2・NFR3・NFR8 の「現行」の文の参照先「FR8.2 の行」を「FR8.1 の行（7 run）」に直す。(3) R-16：code-summary.md の先頭に「現在の状態（2026-10-18 JST、Step47）」節を足し、Steps45〜46 と入口 v2（binding-07）は README.md の Step46 節を参照すること、正式な確認コマンドは2026-10-18からU15の `entry-e3c29d1d/entry-c.py` で、U14の入口（u14_candidate.py・u14_candidate_v2.py）は履歴として中身を変えずに残すこと、U14のcheckpointは entry-c.py で確かめることを書く（入口のhashは書かない。既存の節は履歴として残し、見出しに「履歴：」を付ける）。traceability.json の status と target は変えない。

## 前回のSummary（Steps45〜46）

- Builds: Steps45〜46。Steps42〜44の再レビューの指摘を直す：traceability.jsonの親FR8の行（Major）とNFR1・2・3・8、FR6.3・7.2の行（Minor）に、現行と履歴（208fd965）の区別を付け、手順書の古い「今回…」の見出しを履歴に変える（Step45）。それを許す新しい入口 `u14_candidate_v2.py`（binding-07、U11 v2をそのまま呼ぶ）を作り、確かめ、再レビューのあと採用を人に提示する（Step46）。Step42の計画との違い（source-manifestは変えない、NFR7は足さない）を記録する。製品・workflowは変えず、新しいCI・性能測定・pushは行わない。
- Touches: U14のtraceability.json・手順書の見出し・計画、必要ならcode-summary.mdの冒頭の節に1項目、`verification/loopback1-next/` の新しいファイル（入口・binding-07・回帰）とREADMEの節。
- Tests: 新しい入口の回帰（拒否と正の対照、Step43の履歴の固定）を書いて実行する。仮採用のコマンドが想定どおり止まることと、新しい入口がexit 0になることを確かめる。正式sensor、独立再レビュー、人の採用のあとの正式checkpoint。

## 前回のSummary（Steps42〜44）

- Builds: Steps42〜44（Loop-back 1の残り）。U14の記録（code-summary.md・traceability.json・source-manifest.json）を、整数SSEのJIT・正式性能（run 39030957672、FR8.3）・Safariの修正・npmのpinに合わせて更新し（Step42）、それを許す新しい確認の入口 `u14_candidate.py`（binding-06、U11 v2をそのまま呼ぶ）を作り、約束したMinor（U11のR-10：`--logical-child` のhash検査）も直す（Step43）。回帰・sensor・独立再レビューのあと、新しい入口の採用を人に提示する（Step44）。製品・workflowは変えず、新しいCI・性能測定・pushは行わない。
- Touches: U14の記録3ファイルと計画・手順書、新しい `construction/u14-jit-wasm/code-generation/verification/loopback1-next/`（入口・binding-06・回帰・README）だけ。
- Tests: 新しい入口の回帰（拒否と正の対照）を書いて実行する。今の正式確認コマンドが想定どおり止まることと、新しい入口がexit 0になることを確かめる。正式sensor、独立再レビュー、人の採用のあとの正式checkpoint。

## 前回のSummary（Steps31〜41）

- Builds: Loop-back 1の第2段階（Steps31〜41）。Step31で手元の費用を測り（済み）、見積りで速くなるのは整数SSE群だけだったため、人の選択で今回は整数SSE群（wasmのSIMD、JITの状態にXMMを足してrollbackを400 byteに）だけをJITに足す。GPRのregister形式（Step35）とbyte比較群（Step36）は今回は行わず、正式性能の結果を見てから別の計画にする。CIで品質を確かめた後、正式な性能測定を1回だけ行う。Safariの待ち時間はU11を開き直して直す。mise.tomlにnpm 12.2.0を書き（今はグローバル設定に記載済み）、それを許す新しい正式確認コマンドを作って人の承認を受ける。
- Touches: Step31は製品を変えない（`verification/loopback1-cost/` だけ）。その後：`tests/guests/u14/{native.c,validation.py,test_validation.py}`、`crates/paludarium-harness/tests/diff_u14.rs`、`crates/paludarium-jit/src/{block.rs,emit.rs,bridge.rs,lib.rs,cache.rs}`、`crates/paludarium-cpu`（XMM状態の受け渡しに必要な分だけ）、`crates/paludarium-wasm/src/abi.rs`、`packages/paludarium-wasm/jit-support.mjs`、JITのfuzz対象、`mise.toml`、U14の記録3ファイル、新しい `verification/loopback1-next/`。pushは2回（native先行、改善後）で、どちらも先にdiffを示して承認を受ける。
- Tests: Step31は既存の実Worker microbenchで測った（済み）。実装の前に整数SSE群のfresh x86-64 Linuxの差分ケース（形式ごとの境界を含む）を用意し、interpreterで一致を確かめる。実装の後に各部品7件以上・JS境界8件以上の単体テストを書く。CIで4環境の各28比較、3OS、依存の検査、各集合の行カバレッジ80%以上、fuzz各600秒を確かめ、正式な性能測定（20標本、片側p<0.05）を1回だけ行う。

## 入力と現状

Unit定義U14、要件FR8/FR8.1〜FR8.3、NFR1/2/3/6/8、契約C9/C10/C12、components.mdのJitを対象とする。既存NoopCodeCacheとnativeのインタプリタを保持する。下のSteps1〜7とlock overlayは初回構築の計画を保持したもの。現在は署名済みb79d30d5でJIT・4環境比較・overlayの証拠があるが、初回性能は平均JIT14.671968449秒／interpreter5.4624920141秒、全10ペアでJITが遅く片側p=1で未達。JE専用native差分と親FR8分類が不足している。今回実行する追加修復はSteps8〜14であり、旧成功を変更後の新実行へ読み替えない。

## 実装方針

Rust側でDecodedInstructionから制御フロー終端までの基本ブロックとwasmバイト列を生成し、既存Worker内のJSがWebAssembly.Module/Instanceを生成・管理する。独立Workerを追加せず、各guest Workerの共有メモリと既存状態ABIへ接続する。C9の同期呼び出しで実行できる接続を先に小さく確認する。状態・例外・syscall・kill・予算をインタプリタと揃える。対応命令はnative差分で先に固定し、未対応命令は状態を破壊せずフォールバックする。

メモリ読書きと命令fetchはMMUの権限・範囲・部分fault意味論を維持する。生成コードは生のhostポインタへ無検査アクセスしない。ページ世代・mapping世代を共有し、write/protect/unmap/remap/execの変更を他Workerでも実行前に検査する。コード取得から公開までの競合、複数ページ、実行中変更を含む原子性を設計し、古い世代の生成コードを実行しない。fallbackだけの成功をJIT成功と数えない。

## 手順

- [x] Step 1 — 現行ソース・両lock・最新ツール・契約を固定し、既存JIT限定テストrunnerを確認する。既存CIと共有状態ABI、MMUの全書込み経路を監査し、必要な限定変更を一覧化する。FR8.1、NFR8。
- [x] Step 2 — 実装前にU14命令/プログラム差分ケースとLinux native取得経路を用意する。整数・flags・分岐・メモリ・fault・未対応命令・自己書換えを含める。同じ固定probe/aube sourceと既存maskを使い、native原本を実機CIごとに取得する。承認済みの固定aube限定例外を専用設定・receipt検査へ実装し、crates.io unsafe-libyaml 0.2.11とlockを厳密照合してRUSTSEC-2024-0449だけを除外する。追加修復は下の「U14固定guest lock overlay修復」に従い、元aube source/tag/lockを保存してU14ビルドコピーのrustlsだけを0.23.46へ更新する。製品deny.tomlとprobe監査、workspace/fuzz両lock、他advisoryと依存4監査を維持し、ignoreを増やさない。内部helper/receipt境界を実装後に14件以上の拒否回帰と既存U10 policy/evidence回帰を書いて実行し、固定Python対象80%以上を確認する。更新binaryのLinux実機期待値を先に取得してから後続JIT差分へ進む。静的検査後、具体化した追加送信範囲を人へ提示しLinux CIを再実行する。初回失敗を保持する。FR8.2、NFR1/8。
- [x] Step 3 — 内部4部品（ブロック抽出、wasm生成、世代付きキャッシュ、実行ブリッジ）を層ごとに実装し、その層の単体テスト各7件以上を追加・実行する。生成wasmの検証失敗、境界、状態復帰、フォールバックを含める。C9、FR8.1、NFR2/3。
- [x] Step 4 — Runtime/MMU/wasm/JSを統合し、jit:false互換を維持してjit:trueを有効にする。接続境界10件以上（共有Worker invalidation、跨ページ、protect/unmap/remap、生成中write、fault、syscall、kill、trap、同時処理）と実wasm回帰を追加する。FR8.1/8.2、C10/C12。
- [x] Step 5 — 同一署名ソース・module・固定guestでNode/Chromium/Firefox/本物Safariを比較する。各環境で既存14ケース以上をJITあり/なし両方でfresh Linux期待値と照合し、probe全8項目、aube、元argv、既存C12/U11/U13回帰を維持する。実際のJITブロック実行も証明する。FR6.3/7.2/8.2。
- [x] Step 6 — 3OS品質と依存4検査、固定Rust JIT対象・変更JS・Python検証器各80%以上、既存workspace80%以上を確認する。新JIT生成器/キャッシュfuzzと依存変更のある既存対象を各600秒ASan/LSanで実行する（MMU最大4608バイト）。wasm専用ブリッジは実wasm境界で検査し、native sanitizerの代替と主張しない。Node Workerでprobe全体を各10回測定し、下記性能判定を行う。FR8.3、NFR2/3/6。
- [x] Step 7 — 全入力・両lock・署名head・CI全ジョブ・原本digest・生測定を固定し、source-manifest/summary/traceabilityを更新する。正式検査・独立レビュー後、新確認スクリプトは旧検査をその旧ソースへ保持し現行U14を別照合する。最終確認コマンドの人の承認と正式検証・完了承認へ進む。

## U14固定guest lock overlay修復

2026-10-15に人が追加を承認した修復範囲。Step 2の内部helper/証拠境界として先に実装し、検証成功後にStep 5〜7の新binary・native・全環境・品質証拠へ接続する。既存7手順の順序とTesting Contractを維持する。

- `tests/guests/u10/source-lock.json`：既存aube tag `v2.6.1`、revision `bd94e42f54d3b5e3dd102716b7197f316cb5f4ed`、元lock SHA256 `8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668` を保持し、別 `u14_aube_lock_overlay` 設定にpolicy ID・元/更新digest・単一package差分を固定する。
- 新 `tests/guests/u14/lock_overlay.py`：604 packageのrustls1件だけ、crates.io source不変でversion `0.23.45` → `0.23.46`、checksum `0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634` → `48e13bd8c0e9365c43cfa5c9e8f9ad49d3c8444926c9aac819e0e4dc503c8fdf` の2行のみを更新する。候補overlay SHA256 `b8d403f2c449da8eb104cca0cbd1c9f1f61ade8249615c246ae6cc8cd531db0e` を厳密照合し、依存一覧・他603 package・任意追加変更を拒否する。
- `tests/guests/u10/build.py`／`tests/guests/u10/evidence.py`：既存U14 policy選択時だけ、元downloaded sourceを保存してビルド用コピーへoverlayを適用する。元source/lockとbuild source/lockの前後snapshot・digest・receipt項目を分離し、コピー間の差分も上記Cargo.lockの2行だけと照合する。metadata・cargo-deny・cargo build --lockedは更新lockへ束縛する。旧receiptとU14以外の通常経路は元lockの検証を維持する。`source_unchanged` を元lock未変更と誤表示しない。
- 新 `tests/guests/u14/test_lock_overlay.py`、既存 `tests/guests/u14/test_guest_policy.py`／`tests/guests/u14/runner-tests/test_u14_runner.py`、`tests/guests/u10/runner-tests/test_evidence.py`／`test_policy.py`：正常更新に加え、元lock/source不一致・rustls重複/欠落・旧新版/registry/checksum違い・別package/依存一覧変更・overlay digest違い・通常経路への適用・receipt取り違え・元/build source改変・ignore追加・他advisory失敗伝播の14件以上を検査する。
- `.github/workflows/u14-quality.yml` のU14 Python coverage対象に新helperと変更build/evidenceを追加し、固定分母・80%下限を維持する。source-manifestには上記全source/test/config/CI変更を含める。変更workflowの具体diffと追加送信manifestを確定してから既存fork同branchへ署名jjで送信する。

Step 5〜7では、新aube binaryのhashを取得し、各CIで同binaryのfresh x86-64 Linux native14＋元argv14と命令11ケースを取得する。同じmodule・guest・引数・署名head・元/overlay両guest lock・workspace/fuzz両lockをNode/Chromium/Firefox/本物Safari各28比較とprobe各10回性能へ束縛する。Rust/JS/Python/workspace各80%、新JITと依存変更した既存対象各600秒ASan/LSanを維持する。旧binary/旧oracle/旧CIは履歴として保存し、新guestの成功へ流用しない。新ignore、製品/fuzz/probe lockの変更、元aube source変更は修復範囲外。

## 性能判定

FR8.3の対象は短いmicrobenchmarkではなくprobe全体。Node Workerの同じmodule/guest/引数を使用し、計測なしreleaseでJITなし/あり各10回、10ペアの順番を固定seedで均衡化して交互実行する。各回fresh Sessionを作り、guest実行開始から終了までを測りJITコンパイル時間を含める。module読込・準備時間も別記録する。計測前の共通warmupは測定10回へ含めず、数と条件を先に固定する。

片側の対応あり正確ランダム化検定を採用し、10ペアの全1024符号反転からp値を算出する。平均時間JITあり<なし、p<0.05、全20回のprobe全PASS・exit0・30秒以内・JIT実行証拠をすべて要求する。全標本・seed・順序・ツール版・速度差・p値・背景負荷を保存する。外れ値除外、成功するまで再測定、試験後の検定変更はしない。失敗は不足として報告し、性能をPR必須ゲートに変えない。

## 制限と変更管理

native JITと公開処理U15は対象外。旧native SIGSEGV・Windows race原因・ID競合の完全解消はこの計画で解決済みとしない。共有コード変更は影響Unitと証拠を監査し、旧証拠を現行へ無条件流用しない。snapshot上限、strict guard、guest30秒、既存比較mask、coverage分母を弱めない。C9同期接続で契約変更が必要と分かった場合は具体的差分を提示する。

## 性能・JE・親FR8の追加修復

2026-10-15の修正依頼に対応する。既存の比較mask、30秒guest上限、80%下限、各600秒ASan/LSan、元aube source/lockとU14限定overlayを保持する。Testing Contractは再renderした全文と現在のブロックが一致している。初回性能20標本とb79の後続失敗は別の履歴として保持する。

- [x] Step 8 — 現行source/module/guest/locksと使用ツールを固定し、既存U14 runnerの`--list`・Python loader・Node構文確認で実行準備を確かめる。ツール更新が必要なら区切りで設定とlockを整合し、性能測定中に版を変えない。性能初回の125,522ブロック／271,821命令／18,257,487 fallbackを診断の出発点として保存し、原因の寄与率は未計測とする。FR8.1/8.3、NFR8。
- [x] Step 9 — 製品の性能修復前にJEケースを準備する。`tests/guests/u14/native.c`へ`je-zf1-taken`（CMP入力7）と`je-zf0-not-taken`（入力8）をopcode0x74で追加する。既存opcode0x75は`jne-zf1-not-taken`／`jne-zf0-taken`へ正す。`validation.py`／`test_validation.py`／`crates/paludarium-harness/tests/diff_u14.rs`のcase対応を13ケースへ整合し、faultの固定配列indexをcase名参照へ変更する。同じbytesのfresh x86-64 Linux native原本を既存隔離CIで先に取得する。期待値を保存定数へ置き換えず、以後のCIも毎回原本を生成する。FR8.2、NFR1。
- [x] Step 10 — 受理用releaseと別のopt-in診断buildを用意する。JIT bridge/cache・CPU hook・Runtime workers・wasm ABIに診断用counterを接続し、`packages/paludarium-wasm/tests/u14-cost-profile-check.mjs`でprobe全体を各mode1回、各guest30秒・kill/reap/cleanup付きで実行する。fallback hit/miss、epoch失効、LRU更新、compile数/時間、JS遷移、実行block長、checkpoint数を収集する。時間計測は低頻度のcompile／集約箇所に限定し、高頻度pathはcounterを用いる。診断専用featureとbuild/outputを分離し、無効時にcounter/計測処理を受理moduleへ入れない。内部collectorは実装後に正常・無効・overflow・失敗・timeout・receipt取り違え等7件以上を検査する。診断値を受理20標本へ混入しない。FR8.3、NFR3/6。
- [x] Step 11 — 診断で確認した費用へ局所修復する。第一候補は`crates/paludarium-cpu/src/lib.rs`の既存decode情報による未対応命令の事前選別と、`crates/paludarium-jit/src/block.rs`／`bridge.rs`／`cache.rs`のnegative hit時のLRU更新削減。支持する命令・operand幅・prefix条件を一か所に寄せ、未対応命令は既存interpreterへ渡す。コード世代の検証前に古いpositive translationを実行しない。第二候補はwarm prepared-hitのRust/JS遷移を2回から1回へ減らす内部接続で、JS側cache miss時はcold prepareをMMU guard外で行い、実行前の世代・bytes照合、144-byte trap rollback、Worker-local cache、module ID非再利用を維持する。`crates/paludarium-jit/src/lib.rs`、Runtime workers、wasm ABIの利用側も同じ変更へ整合する。公開C10/C12は変更しない。各変更部品は実装後に7件以上、変更JS境界は8件以上の正常・境界・異常回帰を追加する。対応prefix/幅、未対応fallback、negative失効、eviction/clock exhaustion、cache miss、改変bytes、trap rollbackを含める。budget64の過課金は診断でcheckpoint増幅を確認した場合だけ、default互換helperで実行命令数を返す限定修復を行う。追加の対応命令やMMU共有generation/lockの省略には広げない。FR8.1/8.3、C9、NFR2/3/6。
- [x] Step 12 — JE2条件を`bridge.rs`の実Wasm試験でも直接実行する。CMP+JEだけの1ブロックでtarget/fallthrough RIP、flags、`executed_blocks=1`／`executed_instructions=2`を照合する。fresh Linux native・interpreter・実Wasm JITの三者結果を同じcase IDとbytesへ結合し、MOVだけJIT実行してJEをfallbackする偽陽性を拒否する。自己書換え、跨ページ、write-during-prepare、別Worker変更、protect/unmap/remap、eviction、trap rollback、syscall/fault/kill/budget境界とjit:false互換を再検証する。FR8.2、C9/C10/C12、NFR1/2。
- [x] Step 13 — 具体的な変更manifest/diffを確定し、既存`codex/u14-jit-wasm`へ署名付きjjで送信してVerified/headを照合する。JE native先行runと修復後runを区別する。同じ新head/module/guest・fresh原本でNode/Chromium/Firefox/本物Safari各28比較、probe8項目、aube/元argv、3OS品質・依存4監査、Rust/JS/Python/workspace固定集合各80%以上を確認する。診断を無効化したreleaseで初回と同じseed・warmup・10ペア順序・全1024符号反転・片側p<0.05・平均改善・全20回PASS/exit0/30秒以内を判定する。外れ値除外や同じbinaryの合格待ち再測定を行わない。失敗なら全標本を保存し、不足を提示して次の原因修復を具体化する。新JIT2対象と依存closureが変わった既存対象を各600秒ASan/LSan、MMU4608 bytesで逐次検査する。不変対象の再利用はsource/両lock/compiler/flags/suppression/binary/原本一致の範囲を明記し、成立しなければ再実行する。FR8.2/8.3、NFR1/2/3/6/8。
- [x] Step 14 — `traceability.json`の`upstream_ids`と`coverage`へ親`FR8`を追加する。FR8.1/8.2/8.3の集約である理由と各証拠をsummaryへ記し、FR8.3未達中は親FR8/FR8.3/NFR6をGAPにする。JEも実測完了までは未検証を明記する。全source/test/config/CIをmanifestへ含め、新headと原本digest、診断/受理の分離、全CI結果をsummaryへ結合する。旧checker・失敗原本・全旧検査を保持し、新sourceと新CIを別に厳密照合する確認候補と拒否回帰を作る。正式sensors・独立レビュー後、変更後の確認コマンドを正式承認・実行へ進める。u9専用coverageの未測定は別の不足として保持する。FR8、NFR1/3/6。

実行状況：Steps8〜12の実装・限定診断・JEのfresh native/interpreter/実Wasm三者確認は実施済み。a8e8332bの品質34/source-bound7/fuzz13と4環境各28比較は成功したが、正式性能20標本は全10ペア遅くp=1で未達原本を保持した。追加のdecode1lookup局所修復を署名head cd2de605へ送信済みで、現在の新CI・正式性能は結果待ち。Step13/14と正式確認・独立レビュー・完了承認は未完了。性能達成とunit全要件完了は主張しない。

## 追加性能原因診断（今回の追加範囲）

人の追加承認は診断段階だけを計画へ組み込むこと。以下の計画確認と内容確認が済むまでは実装しない。cd2de605の正式20標本はinterpreter平均5.581792195100001秒/JIT6.2825898274秒、全10ペア遅くp=1で未達。a8・b79・13753の失敗原本と分離して保存する。限定local診断のJIT命令190117/(190117+interpreterSteps16488376)=約1.14%、90324blocks/93340JS遷移は適用率・短block・境界回数の根拠であり、正式性能の時間寄与ではない。

- [x] Step 15 — 署名cd2de605、現在source/locks、旧88counter原本と正式失敗20標本を固定し、診断専用の観測定義と変更pathを確定する。観測するのは成功block後の次RIPの同epoch positive translation有無、同Worker prepared有無、実際にinterpreterを挟まず続いた既存blockの長さ分布、unsupported/negative/missing/epoch/budget/killの停止理由、観測lookup数/比較bytesである。推測上の次blockを実行・decodeして連鎖を作らず、現行1block制御の実イベントだけを使う。率/回数/bytesを時間費用や約0.70秒の残差へ換算しない。counterの意味・分母・重複分類・終了時flush・overflowを先に記録する。新ISA/guest期待値の追加はしない。FR8.3、NFR3/6。
- [x] Step 16 — `crates/paludarium-cpu/src/{lib.rs,jit_cost.rs,counted_hook_tests.rs}`、`crates/paludarium-jit/src/{lib.rs,cache.rs,bridge.rs}`の診断feature下に必要最小のno-touch peek/実イベントcollectorを実装し、実装後に変更部品各7件以上の回帰を行う。peek前後でcache entries・positive/negative LRU順・拒否hint・module ID・prepare/execute呼出数・CPU/RIP/flags・MMU世代が不変であることを確認する。missing/evicted/別space/別epoch/同slot衝突、decode fallback、interpreterを挟むchain終了、budget/kill/終了時flushを含める。peekでprepare/compile/実行/negative登録/世代更新を発生させない。private collectorによる並列独立とoverflow拒否を維持する。無効featureと既存C9 default利用側には観測処理を入れない。FR8.1/8.3、C9、NFR2/3。
- [x] Step 17 — `crates/paludarium-wasm/src/abi.rs`、`packages/paludarium-wasm/jit-support.mjs`、`tests/u14-cost-profile-check.mjs`／`tests/u14-cost-profile.test.mjs`（後二者は同package下）、`scripts/build-u14-cost-profile.py`と既存runner-testsを必要最小に整合する。既存88fieldsを保持して新fieldsを追加し、診断schema/versionを2へ上げ、新しい正確なfield一覧/分母を固定する。旧version1原本は履歴として保持し、新runnerが旧version/field欠落/重複/別source/module/receipt/overflowを受理しないことをJS8件以上とPython既存集約で検査する。Worker-local prepared観測もlookupだけとしLRU/prepare/executeを変えない。同sourceのdiagnostic/controlを別出力へbuildし、source digest/locks一致、診断exports有り、feature無効controlの診断exports0を実WebAssembly.Moduleで確認する。通常梱包closureに新static importを増やさず、既存配布import/実Wasm起動を維持する。FR8.3、C10/C12、NFR1/3。
- [x] Step 18 — 背景の重い処理を止めた後、現cd2のu11 acceptance probe/aube/oracle対応組を使い、新sourceの診断moduleを各mode新factoryで1回だけ実行する。guest30秒、外側180秒、8PASS/exit0/timeout=false、kill/reap/cleanup、interpreter modeへのJIT counter混入無しを必須にする。診断原本は旧ファイルと異なる新output directoryへ保存し、local:<sourceDigest>とbaseline signed headを区別する。観測率・chain分布・fallback密度・lookup/bytes・停止理由を集計し、測れない時間寄与は未検証とする。正式20標本・受理runnerは実行しない。同binaryの合格待ち測定をしない。FR8.3、NFR3/6。
- [x] Step 19 — 変更feature有効CPU/JIT/runtime・既存JE/prepare中write・JS/Python・fuzz cfgと配布境界を検証し、変更診断codeを含む固定Rust/JS/Python/workspace各80%と追加集合80%を維持する。既存native fixture/4環境各28比較、3OS/依存4監査、変更closure13fuzz各600秒/MMU4608の証拠要件は保持し、不変対象の再利用はsource/locks/compiler/flags/suppression/binary一致で限定する。新sourceの外部検証が必要な場合は具体manifest/diffを提示し、既存fork同branchへの署名jjとVerified/head/bytes確認を親が担当する。既存fullqualityの正式性能stepは起動せず、必要な診断専用workflow `.github/workflows/u14-cost-diagnostic.yml` に品質・finite診断だけを接続する。観測からbatchの償却候補/中止理由と残る不足を提示する。候補率が低い・探索費用が大きい・時間寄与や安全意味論の根拠が足りない場合はbatchを進めず、unsupported hotspots/適用率を次の調査候補にする。batch製品実装はbreak-even条件・安全意味論・具体差分を別の実装計画承認へ提示するまで行わない。命令追加も別承認。旧canonical/binding/失敗原本は変更せず、新証拠を別に作り、summary/traceability/manifestの更新と正式sensors/独立レビュー・次の確認command採用はその新証拠へ束縛して親が調整する。FR8/FR8.3/NFR6は未達として保持し、u9専用coverage不足も解消したとしない。

## Steps20〜27：JIT性能とU9専用coverageの追加修復（今回）

2026-10-16 JST。今回の実行範囲は以下の追加Steps20〜27とする。上のSteps1〜19・各時点の失敗／診断／未完了判定は履歴として本文を保持し、今回の成功や許可へ読み替えない。Step19の未完了項目はSteps25・27で新証拠へ結合するまで完了にしない。U1・U2・U5の共有変更後の再確認は人が承認済み。U5 R-05は質問ファイル構造の未解決Minorとして保持する。製品実装・新診断・U9再測定・正式性能再測定は、この追加計画の承認後に開始する。

検証済み：署名02375d54の保存診断は100388blocks、次prepared16、連続最大2でbatchを中止。最新正式cd2性能はinterpreter平均5.581792195100001秒／JIT6.2825898274秒、約12.555%遅くp=1、現023はNOT_REMEASURED。FR8・FR8.3・NFR3・NFR6はGAPのまま。U9既存LCOVは23ファイル、LF/LH予備集計では旧13が2766/3292・追加10が2174/2415だが、16ファイルでDA集計との差があり原因未特定。これを測定不足解消の証拠にしない。

検証済み：元U1失敗proof c9f79b0bはexit1・証拠不変で、内側stderrを元実行時に保持していないため直接原因未特定。別の限定診断ではNode実体未指定・shim解決時102件中1失敗、実体明示時102件成功を再現したが、元失敗との同一性は未証明。後続の同じ正式起動proof79edf727、U2 proof66e9ba9b、U5 proofc91d4f7aはexit0・証拠不変。これらで元失敗を置換しない。

計画・手順の変更前bytesは `verification/jit-u9-next/historical-before-plan-revision/`（intent直下）へ保存した。現canonical/binding、旧canonical・旧失敗、生測定、元guest source/lockとU14 build-copy overlayは変更しない。新検証候補は別入口 `verification/jit-u9-next/`（U14 code-generation配下）に作り、新コマンドの正式採用には人の確認を受ける。受理条件を弱めない。

- [x] Step 20 — **基準固定と起動準備**。署名head、全変更path、source closure、workspace/fuzz両lock、Rust/compiler/LLVM、Node/V8、Python、coverage集計器を固定する。最新情報とproject pinを作業の区切りで照合し、測定中は更新しない。旧検証proof79d569f4のexit0とevidence_unchanged=trueは過去の実行として保持する。

- [x] Step 21 — **U9集計仕様と拒否回帰**。旧13ファイル集合を初期LCOVから固定し、追加10集合を別に固定する。新規 `scripts/u9-coverage-check.py` と `tests/guests/u9/test_coverage_check.py` を作る。まず保存済み02375d54原本の独立監査を行い、公式artifactのhead/run/job/digest、全source before/after、compiler/locks、diff_u9の実行件数と実exit、測定コマンド、LCOVの各SF/DA、欠落・重複・非整数・負count・LF/LH整合を確認する。13集合と10集合を各80%以上で別判定し、分子分母・全ファイル別結果・未実行行を出力する。総合23集合だけで片側の不足を隠さない。元130追加行の旧専用指標も歴史として保持し、現在の行番号へ機械的に流用しない。

- [x] Step 22 — **U9不足取得と限定修復**。Step21の全条件が保存済み原本で成立すれば、現行headについて証拠接続を修復し、新規測定とは呼ばない。最終JIT修復でU9測定closureが変わる場合、または必要な実行条件が原本に無ければ、最終署名headで既存専用測定を再実行する。80%未達なら未実行行のU9意味論に対応するテストを追加する。対象はHost/Kernel/Runtime/CLIの端末API、stdin短read/EOF、stdout/stderr、isatty/ioctl、bad fd/pointer/request、dup、PTY cleanup、公開constructor/compile_fail。閾値引下げ・ファイル除外・0件/skip成功は行わない。製品不具合が無ければcoverageのためだけに製品を変えない。

- [x] Step 23 — **JIT費用の有限診断**。既存feature専用診断に、already-decoded boundaryの分類、negative-hintの再利用/衝突、cold snapshot/extract/emit、prepare、warm executeの件数を追加する。siteキーはaddress-space/epoch/RIP/分類、固定容量16384、overflowを別計数する。ランキングは保持した集合に限定し、overflow時は全体の頻出順位と断定しない。既存CPU/MMU/flags、LRU、module ID、prepare/execute回数を観測のために変更しない。未対応命令の追加実装や新たなmemory readを診断へ混ぜない。時刻取得は命令ごとに入れず、別の限定microbenchmarkで各段階を1024回のchunk単位で測る。fixtureはcold/negative/warm、短block/既存最大block、epoch変更を固定し、時計費用と観測有無の対照を保存する。nativeの速度をWasmの時間寄与と呼ばず、実Worker/Wasm経路を測る。probeは診断各mode1回、guest30秒・外側180秒・全8PASS/exit0・cleanupを維持する。

- [x] Step 24 — **既存ISA内の最小性能修復**。第一候補はcold/短blockのcompile・prepareを償却できない問題への一般的なhotness admission、第二候補はnegative hint/DecodeCache衝突による反復探索の削減。`N × (interpreter費用 − warm実行費用 − epoch等の必要費用) > cold生成・prepare費用` を満たせるか、Step23の実測で候補を選ぶ。数値・閾値・bounded cache容量・失効条件を実装前に記録する。hotness待ちはdeterministic unsupportedと区別し、後からJITへ昇格できるようにする。address-space/epoch変更、eviction、counter overflow、別Workerで状態を混用しない。probe/ELF名や既知RIPの特別扱い、jit:trueを常時interpreterにする回避は行わない。既定CodeCache利用側の契約、実命令数budget、kill/syscall/fault境界、144byte rollbackと共有lockを維持する。

   この段階で十分な改善の根拠が得られなければ、修復を済んだことにしない。頻出unsupported命令の追加が必要なら、具体的なopcode/operand幅/flags/例外/memory意味論、native差分fixtureと変更pathを別計画にして承認へ戻す。今回の提案は未特定ISA追加とbatch実装の包括承認を求めない。

- [x] Step 25 — **正しさと品質**。変更部品ごと7件以上、JS変更時8件以上、U9検証器は欠落/重複/別head/別source/coverage不足等の拒否回帰を用意する。JE taken/not-taken、prepare中write、epoch/map/protect/unmap、自己書換え、同slot衝突、budget0/1/63/64/不足、kill、syscall、fault、bridge例外を確認する。実WasmをNode実体へ必ず結び付け、skipを成功にしない。fresh Linux native13、4環境各28比較＋filesystem32、3OS、依存4監査、固定Rust/JS/Python/workspace/U9各80%を維持する。変更依存closureのfuzzは各600秒ASan/LSan、MMU4608byte上限を維持する。不変対象を再利用する場合はsource/lock/compiler/flags/suppression/binary一致を示し、成立しない対象だけ再実行する。

- [x] Step 26 — **固定20標本の正式性能**。Step25成功後、同一の診断無効release module・fresh native oracle・固定probeを使い、既存runnerでwarmup各1、各mode10回＝全20標本を1回だけ取得する。固定seed/順序/1024符号反転、全probe成功、実JIT実行、30秒制限、平均改善かつ片側p<0.05を維持する。先に背景負荷を止め、同一module/head/guest/locksと版・負荷の記録を保存する。同binaryで合格待ち再試行はしない。失敗・欠測・timeoutはそのまま保存して原因と次の差分計画へ戻し、初回や中間失敗を置換しない。

- [x] Step 27 — **証拠結合と正式確認**。旧canonical/bindingと旧失敗を全て保持した別の新検証候補を作る。U9二集合、最終source-bound実行、正式性能原標本、rollback/JE、各品質と過去全predicateを新候補へ結合する。FR8/FR8.3/NFR6は新性能の全受理条件を満たした場合だけ、NFR3はU9を含む必要な全品質条件を満たした場合だけ更新する。sensor・独立レビュー後、新しい正式コマンド採用と完了確認を人に提示する。検証器exit0と全要件達成を区別する。


### 追加変更pathと契約境界

| 対象path | 変更目的 | 変更しない境界 |
|---|---|---|
| `crates/paludarium-cpu/src/lib.rs` / `jit_cost.rs` | 拒否hint/衝突とfeature専用site観測、選択した最小hot path修復 | Noop/既定CodeCache、命令意味論、budget/kill/syscall/fault |
| `crates/paludarium-jit/src/lib.rs` / `cache.rs` / `bridge.rs` | cold admissionと必要なlookup費用の削減、feature対照fixture | epoch/space検査、lock、144byte rollback、既存ISA |
| `crates/paludarium-runtime/src/workers.rs` | 上記policyの接続とWorker局所性 | checkpoint、killとprocess状態 |
| `crates/paludarium-wasm/src/abi.rs` / `packages/paludarium-wasm/jit-support.mjs` | 診断専用payloadと測定境界 | 通常moduleの診断exports0、配布import closure |
| `scripts/build-u14-cost-profile.py` / cost-profile runner/tests | schema3/receipt/source収集の整合 | 元schema2原本、旧109fieldsと失敗記録 |
| 新 `packages/paludarium-wasm/tests/u14-cost-microbench.mjs` と回帰 | 実Worker/Wasmのchunk計時、固定fixture・対照 | 正式性能runner、固定20標本の受理条件 |
| 新 `scripts/u9-coverage-check.py` / `tests/guests/u9/coverage-scope.json` / `test_coverage_check.py` | 二集合・来歴・計測定義を固定した独立判定 | 既存13集合、80%下限、旧LCOV/JSON |
| 必要な `.github/workflows/u14-cost-diagnostic.yml` / `u14-wasm-acceptance.yml` / `u1-u14-source-bound.yml` 接続 | 新検証器の組込み、最終source計測、原本保持 | 必須job/監査を減らさない。正式性能は品質成功後の1回だけ |
| 新record配下 `verification/jit-u9-next/` | Node明示readiness・stdout/stderr/exit保持、新bindingと旧023読取view | 現行/旧canonical全てのbytesと既存predicate |

新coverage計測を行う場合は、JSON/LCOV/reportに加えてprofdata・対象instrumented binaryの識別子とSHA、compiler/LLVM・全flagsを保存し、必要な再現用原本も新成果物へ束縛する。診断ログには開始前readinessと終了後exit/timeout/cleanupを記録し、子の失敗を一般的なCalledProcessErrorだけへ縮約しない。元c9で欠けたログを後から生成して埋め戻すことはしない。

新診断は旧schema2/109fields原本と混同しない新version・新outputへ保存し、制限付きsite表は別payloadとする。通常feature無効moduleの診断exportsは0のまま、配布static importを追加しない。新しいU9集計器・固定scope・回帰ファイルをsource収集へ明示追加し、収集漏れ・別compiler・別head・欠落payloadを拒否する。

予定対象はCPU `lib.rs`/`jit_cost.rs`、JIT `lib.rs`/`cache.rs`/`bridge.rs`、Runtime `workers.rs`、feature専用Wasm ABI/JS・診断builder/runner/tests、および新U9集計器/testsと必要な専用CI接続。実変更前に差分manifestを固定する。U9製品への変更はStep22で再現した不足に限り、その場合は対象test・理由を追加する。ゲスト元source/lock、通常依存、監査例外、性能runnerの受理条件は変更しない。


外部実行が必要な段階で具体diff/manifestを提示し、既存fork `codex/u14-jit-wasm` へ署名付きjj送信、Verified/head/bytesを確認する。正式性能stepを診断だけのCIへ無条件追加せず、品質成功後の明示した1回に限定する。計画承認と新canonicalの正式採用は別の確認とする。


各Stepの要件対応：20はFR8.1/NFR8、21〜22はFR3/NFR3（人が指定したU9不足の修復）、23〜24はFR8.1/FR8.3/C9/NFR2/3/6、25はFR8.2/C10/C12/NFR1/2/3/8、26はFR8.3/NFR6、27は親FR8/NFR3/6。今回の上流には独立したUser Story IDがないため、Unit U14と実在するFR/NFRおよび人の修正依頼へ結び付け、架空のUS IDは作らない。

## 今回の指摘対応：Step28（R-04・R-05）

2026-10-17 JST。ユーザーは、U14 checkpointの再確認（iteration 2、判定READY）でRequest Changesを選び、R-04とR-05への対応を指定した。再確認のきっかけは、2026-10-16のClaude Code harness追加で、ルート `.gitignore` のAI-DLCブロックに `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行が入ったことである。ルート `.gitignore` は、U14のsource-manifest（91パス）に含まれない。その後、人の承認でConstruction Verification Commandとして `/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py`（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）が採用された。U14のcheckpointでもこのコマンドが実行される。2026-10-17の再確認後の実行は、終了コード0（checkpointの検証記録 `.aidlc-construction-checkpoints/u14-jit-wasm/unit.json`）であった。判定は `formal-candidate-1792198889197428000-95617/result.json` にあり、`source_compatibility` が `PASS`、`head` が be45b36c、`U15_acceptance` は GAP である。Step27（証拠結合と正式確認）は未完了の履歴として残す。

- [x] Step 28 — code-summary.mdの記録更新（R-04・R-05）。code-summary.mdの末尾（「## 保存した失敗と残る確認」の後）に「## 現行Step28：正式検証コマンドとルート.gitignoreの位置づけ」節を加え、次を記録する。(a) R-04：checkpointで実行する正式コマンドは、採用済みの `final_candidate.py`（上のSHA-256）である。2026-10-17の再確認後の実行の終了コード0はcheckpointの検証記録に、判定は上の `result.json` にある。正式コマンドは実行のたびに `r05-r11-repair-01/` の下へ新しい `formal-candidate-<id>/` を作り、checkpointの最新の実行は `unit.json` の `verification.stdout_tail` に記録される。どの実行も、同じコマンドで同じ判定項目（source_compatibility、U15_acceptance）を出す。U14 Step27で予定していた「新しい検証候補」の正式採用は行っておらず、checkpointの正式検証はこの採用済みコマンドで行う。(b) R-05：ルート `.gitignore` はU14のビルド、テスト、JIT、wasmの入力ではない。manifest（91パス）に含めない、ビルド対象外の共有パスである。2026-10-16のharness追加で上の2行が入ったことが、再確認のきっかけになった。製品の除外（`/target/`、`paludarium.wasm`）は変わっていない。(c) 範囲：新しいCI・性能測定・Safari・ASan・U15の受理は主張しない。また、「## 保存した失敗と残る確認」節の最終段落（「新しい正式検証コマンドはまだ未採用である。」で始まる段落）の先頭に、「（履歴：final_candidate.py採用前の記述。現行は「現行Step28」節を参照）」を足す。その他の文と節は変えない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR3、NFR8）。

## 今回の対応：Step29（固定bytesへの復元と記録の移動）

2026-10-17 JST。Step28の後、独立再レビューはREADY（R-04・R-05はFixed）だった。しかし、採用済みの正式コマンドでのcheckpoint検証は終了コード1になった。失敗の原本は `construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/formal-candidate-1792199458129316000-434/` にある。その中の `refusal.json` には、外側の汎用メッセージ「semantic validator failed or emitted unexpected stderr」だけが記録されている。具体的な理由 `ValueError: bound input changed: aidlc/spaces/default/intents/261004-rust-blink-port/construction/u14-jit-wasm/code-generation/code-summary.md`（`final-verifier-208fd965/checks.py` の `verify_index`）は、内側の検証の標準エラー `0.stderr.bin` の末尾にある（R-06）。正式コマンドは、U14の `final-verifier-208fd965/binding-final-v3-01.json` の `produces` で、code-summary.md（sha256 `223488c21a911afdff961538442e4d6dfe1b8985fe91a7281a2c93c7a8a46edd`、6746 bytes）、traceability.json、source-manifest.jsonのbytesを固定している。この計画とunit-test-instructions.mdは固定されていない。人は「summaryを戻し、記録はplanへ」を選び、この作業に限りreview-freezeをオフにした。この失敗は原本として残し、成功へ読み替えない。

固定値の記録（R-09）：`binding-final-v3-01.json` の `produces` は次の3件を固定している。この値は、`consumer-v3/binding-final.json` の `current_binding` が指す `binding-final-v3-01.json` を読んで確かめた。
- `construction/u14-jit-wasm/code-generation/code-summary.md`：sha256 `223488c21a911afdff961538442e4d6dfe1b8985fe91a7281a2c93c7a8a46edd`、6746 bytes
- `construction/u14-jit-wasm/code-generation/traceability.json`：sha256 `23b4a0beeaeae3e021b26596a1c2c5cd6fb8b54722619f9527d5d89c3045e032`、4902 bytes
- `construction/u14-jit-wasm/code-generation/source-manifest.json`：sha256 `280df22ac7231c13d9473cdd8b0a04cea3213e53333cfc0507839315a772294c`、6401 bytes

復元後の `shasum -a 256` の結果は `223488c21a911afdff961538442e4d6dfe1b8985fe91a7281a2c93c7a8a46edd` で、固定値と一致した。復元後の正式検証（2026-10-17 01:19 UTC）は終了コード0、出力は `formal-candidate-1792199940961338000-5317/` だった。

R-04・R-05の記録（この計画に残すもの）：
- R-04・R-08：checkpointで実行する正式コマンドは、採用済みの `final_candidate.py`（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）である。code-summary.mdの最終段落の「新しい正式検証コマンドはまだ未採用である」は、U14 Step27で予定していた新しい検証候補についての記述で、`final_candidate.py` の採用より前に書かれた履歴である。code-summary.mdを読むときは、正式コマンドについてこの記録を合わせて見る。code-summary.mdは正式コマンドの固定対象なので書き換えない。U14 Step27で予定していた「新しい検証候補」は正式採用していない。正式コマンドは実行のたびに `r05-r11-repair-01/` の下へ新しい `formal-candidate-<id>/` を作る。checkpointの最新の実行（終了コードと出力先）は `.aidlc-construction-checkpoints/u14-jit-wasm/unit.json` の `verification` に記録される。
- R-05：ルート `.gitignore` は、U14のビルド、テスト、JIT、wasmの入力ではない。source-manifest（91パス）に含めない、ビルド対象外の共有パスである。2026-10-16のClaude Code harness追加で、AI-DLCブロックに `aidlc/active-memory/` と `aidlc/.aidlc-request-text/` の2行が入ったことが、再確認のきっかけになった。製品の除外（`/target/`、`/packages/paludarium-wasm/paludarium.wasm`）は変わっていない。

注記（R-07）：Step28とStep29の作業は実施済みである。Step28でcode-summary.mdに足した節と注記は、Step29で取り除いた。実施の証拠は、チェックボックスではなく、エンジンのunit記録（UNIT_COMPLETED。Step29の作業を最初に記録したのは2026-10-17 01:24:40 UTCで、以後もcheckpointのたびに再記録される）とcheckpoint検証（正式コマンドexit 0）にある（R-10）。このワークフローでは、unitの記録やレビューの後に計画のチェックボックスが `[ ]` へ戻されることがあるため、表示が `[ ]` でも未実施を意味しない。

- [x] Step 29 — code-summary.mdを固定bytesへ復元する。Step28で足した「## 現行Step28：…」節（直前の空行を含む）と、最終段落の先頭の注記「（履歴：final_candidate.py採用前の記述。現行は「現行Step28」節を参照）」を取り除く。復元後のファイルのSHA-256が `223488c21a911afdff961538442e4d6dfe1b8985fe91a7281a2c93c7a8a46edd`、大きさが6746 bytesであることを確かめる。一致しなければ、書き換えを止めて報告する。ほかのファイルは変更しない。正式sensorを実行した後は全書込を止め、独立再レビュー、採用済み正式コマンドでのcheckpoint再検証、人の完了承認に進む（NFR3、NFR8）。

## Loop-back 1：Step30（JITの効果が出ない原因の診断）

2026-10-17 JST。Build and Testで、FR8.3（JITありが有意に速い）が不合格になった。head bd247f1e、Node v26.12.0、AMD EPYC 7763で、JITなし平均5.4972秒・JITあり5.4987秒、p = 529/1024 = 0.5166（原本は `construction/build-and-test/verification/ci-bd247f1e/u14-quality-39009460781/u11-node/performance/observations.json`）。前回の合格（208fd965、改善2.74%、p = 0.0068）とほぼ同じ製品コードで差が出なかった。人はRetry with fixを選び、U14のCode Generationに戻した。この段階は診断だけで、製品は変えない。改善の中身は診断の結果で決め、別のPlan Approvalに出す。

これまでに分かっていること（保存済みの記録から）：
- 今のJITが受け付ける命令は、Mov GPR32/64←即値、Add/Sub/Cmp GPR64と即値、JE/JNEだけである（`verification/jit-u9-next/unsupported-candidates-208fd965-readonly.md`）。
- 以前の限定診断では、JITで実行した命令は全体の約1.14%（190117／(190117＋16488376)）だった（上の「追加性能原因診断」節）。
- 208fd965の診断で拒否された境界の集計は、16384個の保持枠に入ったevents（全体の約0.29%）だけで、全体の分布ではない。どの命令形式を足せばどれだけ効くかは、まだ分かっていない。

このため、JITの効果が小さいのは、対応する命令が少なくJITで実行される部分がごく一部だからだ、という仮説を、全数の実測で確かめる。

- [x] Step 30 — **実行された命令の形式の全数集計と、JITで扱える割合の見積り**。
  1. 入力を固定する：作業コピーのhead（e4f84768と同じ製品bytes）、`Cargo.lock`、`rust-toolchain.toml`（nightly-2026-10-11）、fixed probeと元argv。probeのbinaryは、Build and TestのCI run 39015770796（またはrun 39009460781）のartifact `u11-acceptance-inputs` から取得し、SHA-256を記録する。artifactは空の新しいフォルダ `target/u14-diagnosis/inputs/` に展開する。
  2. 数える仕組みを作業コピーの外に置く：`target/u14-diagnosis/` の下に、既存のcrateをpathで参照する診断用のcrateを作り、既存の公開API（CPUのstep・decode）でprobeをnative interpreterで実行しながら、実行した命令ごとに形式（mnemonic、operandの種類＝register/immediate/memory、幅、prefix）を数える。公開APIで足りなければ、`target/u14-diagnosis/` の下に別のjj workspaceを作り、そこにだけ一時的なcounterを入れる。どちらの場合も、作業コピーの製品ファイルと固定bytesは変更しない。
  3. 数え方を先に確かめる：既存のU14 native fixture（命令数が分かっている小さなguest）で、総命令数と形式ごとの数が期待どおりかを確かめてから、probeを数える。
  4. probeを1回実行する：全数のcounterで、上限なし（形式の種類は少ないので保持枠を使わない）。guestの30秒の上限は外す代わりに、外側を600秒で止める。probeの8項目の結果とexit 0を確かめる。
  5. 見積りを計算する：実行された命令を順に並べた列から、(a) 今のJIT対応形式で、JITのblock（今のadmissionの最小3命令以上で、未対応命令で終わる）に入る命令の割合、(b) 候補の形式（register間MOV、GPR64 LEA、GPR32/64の論理・算術、TEST/CMPとJcc全条件、memoryのMOV、PUSH/POPなど）を1つずつ足した場合と全部足した場合の同じ割合、(c) それぞれのblock長の分布、を出す。時間ではなく命令数で見積もり、速さの改善を断定しない。
  6. 記録する：結果を `verification/loopback1-diagnosis/`（`instruction-mix.json`・`coverage-estimate.json`・`README.md`、入力のSHA-256、使ったコマンドと出力）に保存する。
  7. 改善の案を作る：見積りから、足す命令形式の候補と順番、それぞれのnative差分fixture（実装の前にfresh x86-64 Linuxで期待結果を取る）、変更するpath、Safariのsession作成の待ち時間の修正（`packages/paludarium-wasm/tests/u11-browser-driver.mjs`、U11 Step27と同じ内容）、新しい正式確認コマンドの案（旧canonical・旧bindingを残し、変わったcompiled sourceだけを新しく照合する）を、Step31以降として計画に書き足し、Plan Approvalを受ける。見積りで改善が見込めない場合は、そのことを報告して、人に次の進め方を相談する。

  変えないもの：製品のsource・lock・CI、U14の固定3ファイル、旧証拠・旧canonical・旧binding、FR8.3の不合格の原本。診断の結果をFR8.3の合格の証拠にしない。正式な性能測定（20標本）はこの段階では行わない。診断の前後で採用済みの正式確認コマンドを実行し、exit 0のままであることを記録する。FR8.1、FR8.3、NFR6。

## Loop-back 1：Step30の結果

診断の記録は `verification/loopback1-diagnosis/`（README.md・instruction-mix.json・coverage-estimate.json）にある。probeを1回、native interpreter（macOS arm64）で実行し、17,704,550境界を全数で数えた。
- 今のJITが受け付ける形式は実行の25.30%あるが、3命令以上のblockに入るのは0.248%（43,929命令、平均3.001命令）だけだった。対応形式が未対応命令で細かく分断されているのが原因である。保存済みのCI（bd247f1e）の観測とも、平均block長と量の桁が合う。
- 実行の76.5%はmain threadで、2つのhot loopがある。整数SSEのregister loop（PSHUFD・PMULUDQ・MOVDQA・PUNPCKLDQ・PSUBD・PADDD・PSLLD・PSRLD・PACKUSWB）と、byte比較のloop（`MOVZX r32,m8[base+idx]`・`CMP r8,r8`・`CMP r64,r64`）である。
- 足した場合のblockの割合：計画の候補6種を全部足しても13.99%。整数SSE群だけを足すと30.58%（平均25.6命令）。byte比較群だけでも30.58%（平均4.9命令、guest memoryの読み出しが必要）。
- 限界：命令の数だけで、時間は測っていない。blockごとの固定費用はモデルに入っていない。wasmではなくnativeで1回だけ実行した。4群はこのprobeの結果を見て決めた。
- 正式確認コマンドは、診断の前と後でexit 0。記録を書いた後の3回目はexit 1で、原因はリポジトリの外のmise `npm:npm@12.2.0` が無くなっていたことだった（原本 `formal-candidate-1792229683178268000-69975`）。2026-10-17に `mise install npm:npm@12.2.0` で戻し、再実行はexit 0（`formal-candidate-1792229820292147000-70271`）。このnpmはmiseのどの設定ファイルにも書かれていなかったため、`mise prune` などで消えたと考えられる。人の選択で、2026-10-17にグローバルの `~/.config/mise/config.toml` へ `"npm:npm" = "12.2.0"` を足した（正式確認コマンドはこのファイルのpythonの固定だけを照合するので影響しない）。project の `mise.toml` への記載は、正式確認コマンドがbytesを照合しているため、新しい正式確認コマンドで扱う（最後のStep）。
- 製品の作業コピーとU14の固定3ファイルは変わっていない。

## Loop-back 1：Steps31〜41（改善：整数SSE・GPRのregister形式・byte比較をJITに足す）

2026-10-17 JST。最初の改善案（整数SSEだけ、Steps31〜37）に人がRequest Changesを選び、次を指定した：byte比較も足す、GPR形式も足す、実装の前に費用を測る、npmの扱いを変える（miseで入れてもよく、npmの代わりにbunなどを使うのもよい。とりあえずmise.tomlのtoolsに書いて `mise prune` で消えないようにする）。mise.tomlは正式確認コマンドがbytesを照合しているので、今はグローバルのmise設定に書き、mise.tomlへの記載は新しい正式確認コマンドと一緒に行う、を人が選んだ。

方針：まず費用を測り、効果が見込めることを確かめてから実装する。足す順番は、guest memoryに触らないもの（整数SSE群→GPRのregister形式）を先にし、guest memoryを読むbyte比較群を最後にする。byte比較群はC9の「register-only」の境界を変えるので、契約の具体的な差分を示して承認を受けてから実装する。guest memoryへの書き込み（memoryのMOV store、PUSH/POP、CALL/RET）は今回も足さない。

対象の形式：
- 整数SSE群（operandがすべてXMM register）：PSHUFD xmm,xmm,imm8、PMULUDQ、MOVDQA xmm←xmm、PUNPCKLDQ、PSUBD、PADDD、PSLLD xmm,imm8、PSRLD xmm,imm8、PACKUSWB、PXOR・POR・PAND。
- GPRのregister形式：ALUのreg-reg・reg-imm（ADD・SUB・CMP・AND・OR・XOR・TEST、32/64 bit。8 bitの `CMP r8,r8` を含む）、MOV reg-reg（32/64）、LEA r32/r64（memoryを読まないaddress計算だけ）、INC・DEC・NEG・NOT、SHL・SHR・SAR imm、MOVSXD、CMOVcc、NOP、Jccの全条件。
- byte比較群（guest memoryを読むだけ）：`MOVZX r32,m8[base+index*scale+disp]` と、診断で同じloopに出た読み出しの形式。
- どの群でも、VEX・lock・rep・segment prefix、memoryへの書き込み、未対応の組合せはfallbackにする。

- [x] Step 31 — **実装の前に費用を測る**。既存の診断用build（`scripts/build-u14-cost-profile.py` の diagnostic・acceptance-control）と、既存の実Worker microbench（`packages/paludarium-wasm/tests/u14-cost-microbench.mjs`・`u14-length-microbench.mjs`・`u14-cost-null-microbench.mjs`）を手元のNode 26.12.0で実行し、(a) blockごとの固定費用（JSとRustの往復、prepare済みblockの呼出し、状態の受け渡し）、(b) 命令1つあたりのinterpreterの費用、(c) 今のJIT形式での命令1つあたりの費用、(d) block長ごとの時間を測る。製品のsourceは変えない。測った値とStep30のblock長の分布から、群ごと（SSE、GPR、byte比較、全部）にprobe全体の時間がどれだけ変わるかを見積もる。SSE・GPR・byte比較の命令はまだ翻訳できないので、命令1つあたりのJIT費用は今の形式の値で仮定し、仮定であることを記録する。結果は `verification/loopback1-cost/`（README.md・cost.json・入力のSHA-256・コマンドと出力）に保存する。測定はmacOS arm64で、CIのAMD EPYCとは違うことも記録する。**判断点**：見積りで、全部足してもprobeが数%以上速くならない場合は、実装に進まず、結果を人に示して相談する。見積りで十分な改善が見込める場合は、群ごとの見込みを人に報告してからStep32へ進む。FR8.3、NFR6。
**Step31の結果と人の選択（2026-10-17）**：記録は `verification/loopback1-cost/`（README.md・cost.json）。Apple M1、Node 26.12.0で既存の実Worker microbenchを測った（背景の負荷あり）。主な費用は、interpreter 110.4 ns/命令、今のJIT 5.8 ns/命令、prepare済みblockの固定費用587 ns、損益分岐のblock長5.6命令。Step30のblock長の分布で見積もったprobe全体の時間の変化は、整数SSE群だけで約−13%〜−7%（どの仮定でも速くなる）、GPRのregister形式で約+2%〜+8%（平均3.4命令で固定費用を回収できず遅くなる）、byte比較群は測り方で向きが逆（−13%〜+24%）、全部では主な測り方でSSEだけより効果が小さい。新しい形式のJITの費用は今の形式と同じと仮定した。手元の診断用probeはJITあり4.726秒・interpreter 3.475秒でJITありが遅く、理由は分かっていない。この見積りはFR8.3の合格の証拠にしない。人は「SSEだけ先に」を選んだ。このため、今回はStep35（GPR）とStep36（byte比較）を行わず、Step32のケースも整数SSE群だけにする。GPRとbyte比較は、整数SSE群の正式性能の結果を見てから、別の計画として承認を受ける。

- [x] Step 32 — **native差分のケースを先に用意する**（Testing ContractのOrdering）。`tests/guests/u14/native.c` に、整数SSE群の形式ごとのケースを足す（GPRとbyte比較のケースは今回は足さない）。整数SSE：PSHUFDのimm 0x00/0x1b/0xb1/0xe4、PMULUDQ（上位laneを無視すること、最大値）、PADDD/PSUBD（桁あふれの巻き戻り）、PSLLD/PSRLD（シフト数0/1/31/32/255。32以上は0）、PACKUSWB（負は0、255超は255に飽和）、PUNPCKLDQ、MOVDQA、PXOR/POR/PAND。これらとJccを混ぜた短いloopも足す。比べるのはXMM0〜15全部・GPR・RIP・flags（SSE命令がflagsを変えないことも確かめる）。`validation.py`・`test_validation.py`・`crates/paludarium-harness/tests/diff_u14.rs` のcase対応をそろえる。期待結果は、CIのfresh x86-64 Linuxで毎回取る（保存した定数にしない）。push前に変更manifestとdiffを人に示し、承認を受けてから既存forkの `codex/build-and-test` へ署名付きで送り、JITを入れる前のinterpreterで全ケースがnativeと一致することを先に確かめる。FR8.2、NFR1。
- [x] Step 33 — **JITの状態にXMMを足す**。`crates/paludarium-jit` のscratch（今はu64×18）にXMM0〜15（u64×32）を足し、trap時のrollbackを144 byteから400 byteにする。CPUとのXMM状態の受け渡し（`crates/paludarium-cpu` の既存の状態APIを使う。公開APIを変える必要があれば、具体的な差分を示してから進める）、`bridge.rs`、`crates/paludarium-wasm/src/abi.rs`、`packages/paludarium-wasm/jit-support.mjs` を合わせる。wasmではSIMD（v128）を使う。Node・Chromium・Firefox・Safariの4環境がすべて対応しており、整数演算なので結果は決まる。実装の後に、状態の受け渡し・rollback・ABIの各部品で7件以上、JSの境界で8件以上の単体テストを書いて実行する（rollbackで400 byte全部が戻ること、XMMの上位と下位の取り違え、部分trap、Worker間の独立を含む）。C9、NFR2、NFR3。
- [x] Step 34 — **整数SSE群の翻訳を足す**。`crates/paludarium-jit/src/block.rs`（受け付ける形式の判定を1か所にまとめる）と `emit.rs`（v128の命令を出す）に整数SSE群を足す。未対応の形式・memory operand・VEX・prefixの組合せはfallbackにし、状態を壊さない。admission（3命令以上）、budget、kill、syscall、faultの境界、コード世代の検査、共有lockは今のまま保つ。実装の後に、形式ごとの境界（shift数32以上、飽和、imm8の全ビット）、fallback、自己書換え、epoch変更、evictionを含む単体テストを7件以上書いて実行する。FR8.1、C9、NFR2/3。
- Step 35（今回は行わない。人の選択「SSEだけ先に」、Step31の見積りで遅くなる見込み） — **GPRのregister形式の翻訳を足す**。同じ `block.rs`・`emit.rs` に、上のGPRの形式を足す。flagsは命令ごとに、定義されたbitだけを計算し、未定義のbitはStep32の表のとおりに扱う。8・16・32 bitの部分registerの書き込み（32 bitは上位を0、8・16 bitは残りを保つ）、CMOVccの条件不成立でも32 bitは上位を0にすること、シフト数のmask（32 bitは5 bit、64 bitは6 bit）とシフト数0でflagsを変えないことを、実装の後の単体テスト（7件以上）で確かめる。FR8.1、C9、NFR2/3。
- Step 36（今回は行わない。人の選択「SSEだけ先に」、Step31の見積りで効果の向きが決まらない） — **byte比較群（guest memoryの読み出し）を足す**。実装の前に、C9（JITとCPU/MMUの境界）の契約の具体的な差分を `inception/contract-design/` の契約に照らして作り、人に示して承認を受ける。差分の中身：translated codeはguest memoryを読むだけで書かない。読み出しは既存のMMUの権限・範囲・ページ世代の検査を通す（生のhostポインタに直接アクセスしない）。読み出しがfaultしたら、そのblockのそれまでの変更をrollbackし、blockの先頭からinterpreterで実行し直して、interpreterと同じfaultを起こす。読み出しの途中で別Workerがmappingを変えた場合は、世代の検査で古いtranslationを使わない。承認の後に、`block.rs`・`emit.rs`・`bridge.rs`・`crates/paludarium-wasm/src/abi.rs`・`jit-support.mjs` と、必要ならMMUの読み出し用の内部APIを変える。実装の後に、ページ境界、読めないページ、protect/unmap/remapの途中、自己書換え、別Workerの変更、faultの後の状態がinterpreterと同じこと、を含む単体テストを7件以上（JSの境界は8件以上）書いて実行する。契約の承認が得られなければ、この群は足さずに次へ進む。FR8.1、C9、C10、NFR2/3。
- [x] Step 37 — **手元で確かめる**。workspaceの単体テスト（`PALUDARIUM_TEST_NODE` を設定）、`cargo fmt --check`、`cargo clippy -D warnings`、wasm32のビルド、実WasmのJIT試験を通す。Step30の診断の仕組み（`target/u14-diagnosis/`）でprobeをもう一度数え、新しい形式で実際にblockに入る命令の割合を記録する（整数SSE群で約30.6%の見込み。時間の改善とは言わない）。手元の診断用probeでJITありが遅かった理由（4.726秒対3.475秒）も、診断用buildとacceptance-control buildを比べて切り分け、記録する。Step31の費用の測定を同じ条件でもう一度行い、見積りと比べる。FR8.1、NFR3。
- [x] Step 38 — **CIで確かめる**。変更manifestとdiffを人に示し、承認を受けてから `codex/build-and-test` へ署名付きで送り、Verifiedとheadを確かめる。PRのCI、全品質（`u14-quality.yml`）、U12・U13の品質、JITのfuzz（変わった対象を各600秒、ASan/LSan、MMU 4608 byte）、`u1-u14-source-bound.yml` を実行する。4環境の各28比較とprobe 8項目、JITあり・なしの一致、各集合の行カバレッジ80%以上を確かめる。全部通った後に、正式な性能測定（warmup各1、各mode10回、固定seed、1024通りの符号反転、片側p<0.05かつ平均が速い）を1回だけ行う。不合格でも測り直さず、全標本を残して人に相談する。FR8.2、FR8.3、NFR1/2/3/6/8。
- [x] Step 39 — **Safariのsession作成の待ち時間**。U11 Step27と同じ修正（`packages/paludarium-wasm/tests/u11-browser-driver.mjs` の `POST /session` を60秒にし、回帰テストを足す）は、U11のファイルなので、U14の作業の後にU11のCode Generationを開き直して行う。U11の計画承認・再レビュー・checkpointを通す。Step38のCIの前に入れられる場合は、同じpushに含める。NFR7。
- [x] Step 40 — **mise.tomlにnpmを書く**。project の `mise.toml` の `[tools]` に `"npm:npm" = "12.2.0"` を足し、`mise prune` で消えないようにする。今の正式確認コマンドは `mise.toml` のbytesを照合するので、この変更はStep41の新しい正式確認コマンドで許す1行として扱う。CIや性能測定の道具としてnpmの代わりにbunを使う案は、人がよいとしているが、正式確認コマンドとCIの両方を変えるので、この計画では行わず、道具の版の更新の別作業で人に相談する。NFR8、NFR9。
- [x] Step 41 — **新しい正式確認コマンドと記録**。U14のcompiled source（223個）と固定3ファイルが変わるので、今の `final_candidate.py` はexit 1になる。旧canonical・旧binding・`final_candidate.py` と失敗の原本は残し、変わったcompiled sourceと新しいfixture、新しい署名headのCI結果だけを別に照合する新しい確認コマンドを、`verification/loopback1-next/` に作る。`mise.toml` は、今のbytesに `"npm:npm" = "12.2.0"` の1行だけを足したものを許し、それ以外の違いは拒否する。拒否の回帰（別head・別source・欠落・hash違い・mise.tomlの別の変更）を付ける。code-summary.md・traceability.json・source-manifest.jsonを新しいsourceと証拠に合わせて更新する。C9の契約を変えた場合は、その記録も更新する。FR8・FR8.3・NFR6は、正式性能の受理条件をすべて満たした場合だけ更新する。正式sensor・独立レビューの後、新しい確認コマンドの採用を人に提示し、承認を受けてから正式checkpointで実行する。NFR3、NFR8。

変えないもの：既存の対応形式とその意味論、C10/C12の公開契約、jit:false互換、比較mask、guest30秒の上限、80%の下限、FR8.3の受理条件。旧証拠・旧失敗の原本は消さない。診断の数値をFR8.3の合格の証拠にしない。

## Loop-back 1：Steps42〜44（Step41の具体化：U14の記録と新しい確認の入口）

2026-10-18 JST。Steps38〜40は、次のとおり中身が済んでいる（チェックはUnitの完了の記録でengineが扱うため、ここでは状態を本文で書く）。

- Step38：人の承認のあと、12d6a2f6（native差分ケース）と1ceae86c（整数SSEのJIT、10ファイル）を署名付きで送った（Verified）。1ceae86cのCI（PR CI、u14-quality、U12・U13の品質、JITのfuzz）が成功し、u14-qualityの正式な性能測定（run 39030957672）を1回だけ行った。結果はJITありが約19.7%速く、片側p=1/1024（<0.05）で、平均も速い。原本は `verification/loopback1-next/perf-39030957672-observations.json`（`b827a5e1…`）。測り直しはしていない。
- Step39：U11を開き直して直した（U11 Steps29〜31。2b8723ab・57a8c96f。人の承認済み）。57a8c96fのPR CIとU12 qualityで本物のSafariのjobが成功した。
- Step40：`mise.toml` に `"npm:npm" = "12.2.0"` を足した。U1の入口（binding-02）がこの1行だけを許している（人が採用済み）。
- Step41のうち「新しい正式確認コマンド」は、U1→U2→U11の入口として作られ、今はU11の `u11_candidate_v2.py`（binding-05、hash付きのコマンド行）が人に採用されている。残っているのは、U14の記録の更新と、それを許す入口だけである。

- [x] Step 42 — **U14の記録を今に合わせる**。(1) `code-summary.md` の冒頭に「現行Steps30〜44（Build and TestのLoop-back 1）」節を足し、Step30の診断、Step31の費用、Steps32〜34の整数SSEのJIT、Step37の手元の確認、Step38のCIと正式性能（run 39030957672、−19.7%、p=1/1024、測定は1回）、Step39のSafariの修正（U11）、Step40の `mise.toml`、Steps35〜36を行わなかったこと（人の選択）、今の正式確認コマンド（全文）と、この入口（Step43）の採用はまだであることを書く。既存の「現行」で始まる見出しは「履歴：…（作成時の見出しは「…」）」に変え、「下の節の本文にある「現行」「未実施」「未検証」は、その節を書いた時点のものを指す」と書く（U12・U13と同じ扱い）。(2) `traceability.json` は、FR8.1・FR8.2・FR8.3・NFR6・NFR7のnotesに今回の証拠（commit・run・観測ファイルとそのSHA-256）を足す。FR8.3の状態は、正式性能の受理条件（warmup各1、各mode10回、固定seed、1024通りの符号反転、片側p<0.05かつ平均が速い）をすべて満たしたことを原本で確かめた場合だけ合格にする。分類とtargetはほかに変えない。(3) `source-manifest.json` に、12d6a2f6・1ceae86cで変えたU14のファイル（`git diff-tree` の結果と一致させる）とその署名headを足す。他Unitの記録・製品・workflowは変えない。FR8.1、FR8.2、FR8.3、NFR6、NFR7、NFR8。
- [x] Step 43 — **U14の記録を許す新しい入口**。`construction/u14-jit-wasm/code-generation/verification/loopback1-next/` に `u14_candidate.py` と `binding-06.json` と回帰 `test_u14_candidate.py` と README.md を作る。入口は、U11の `u11_candidate_v2.py`（`56870072…`）とbinding-05（`a3d81077…`）を1 byteも変えずにそのまま呼び、その全検査を弱めない。足す許可は、U14の記録（Step42で変えた `code-summary.md`・`traceability.json`・`source-manifest.json`、計画（checkboxを正規化した形）、手順書）の新しいbytesだけで、それ以外の違いは拒否する。旧い封印や `binding-final-v3-01` がU14の記録を固定している場合は、U2・U11と同じく旧い検査には固定時のbytesを読取専用のviewで見せ、新しいbytesはbinding-06で固定する。入口のコマンド行は `--entry-sha256 <hex> --binding-sha256 <hex>` を必須にする（U11 v2と同じ）。**約束したMinor（U11 review-12 の R-10）**：内部の `--logical-child` の分岐にも同じコマンド行のhash検査を通す（できない場合は、その理由をREADMEに書く）。拒否の回帰（記録の別のbytes・欠落、許可外のpath、ほかのcompiled sourceの変更、別のhead、入口とbindingのhashの違い・引数の欠落と順の違い、U11の入口とbinding-05の差し替え、`--logical-child` のhash検査）と正の対照を付ける。新しいCI・性能測定・pushは行わない（記録だけの変更で、署名headは57a8c96fのまま）。NFR3、NFR8。
- [x] Step 44 — **確認と採用の提示**。回帰を実行し、今の正式確認コマンド（U11 v2）がU14の記録の変更で止まること（想定どおりのexit 1）と、新しい入口がexit 0になることを確かめて記録する。正式sensor（traceability・required-sections）を実行した後は書込を止め、独立再レビューを受ける。そのあと、新しい入口のコマンド行（2つのhashを含む）の採用を人に提示し、承認を受けてから登録し、正式checkpointで実行する。採用の承認がなければ登録しない。NFR3、NFR8。

## Loop-back 1：Steps45〜46（再レビューの指摘への対応）

2026-10-18 JST。Steps42〜44の独立レビュー（iteration 1、READY）で、Major 1件とMinor 2件が出た。人は「仮に採用して直す」を選び、Step43の入口 `u14_candidate.py`（binding-06）を正式確認コマンドとして仮に採用した。checkpointの検証はexit 0（u14_candidate: PASS）で、そのあと人がRequest Changesを選んだ。Step42の計画との違い（source-manifest.jsonは変えない：14 pathはすでに `writes` にあり、engineの検証が `writes` 以外の項目を拒否するためheadはcode-summary.mdに書いた。traceability.jsonにNFR7は足さない：U14の担当外でU11の表にある）は、レビューも妥当とした。これを計画として記録する。

- [x] Step 45 — **traceabilityと手順書の履歴の表示**。(1) Major：`traceability.json` の親FR8の行の説明文の先頭に、現行の根拠（FR8.3の行と同じ：run 39030957672、約19.72%速い、片側p=1/1024）への参照を足し、既存の208fd965の数値（改善2.74%、p=7/1024）を「履歴（208fd965）：」と明示し、その後のbd247f1eでの不合格（p=529/1024、原本は `construction/build-and-test/verification/ci-bd247f1e/u14-quality-39009460781/u11-node/performance/observations.json`）にも触れる。(2) Minor：NFR1・NFR2・NFR3・NFR8・FR6.3・FR7.2の行で「検証済み：head208fd965」の記述に「履歴（208fd965）：」の印を付け、1ceae86cのCI（PR CI、u14-quality、U12・U13の品質、JITのfuzz）で今回確かめた範囲があれば「現行（2026-10-18 JST）：」として足す。確かめていない範囲は足さない。statusとtargetは変えない。(3) Minor：`unit-test-instructions.md` の「## 今回Step28：…」「## 今回Steps20〜27：…」「## 今回Steps15〜19：…」の見出しを「## 履歴：…（作成時の見出しは「今回…」）」に変える。本文は変えない。code-summary.mdは変えない（必要なら冒頭の節にStep45の1項目だけ足す）。
- [x] Step 46 — **新しい入口と確認**。`verification/loopback1-next/` に `u14_candidate_v2.py`・`binding-07.json`・`test_u14_candidate_v2.py` を作り、READMEに節を足す。入口はU11 v2（`56870072…`）とbinding-05（`a3d81077…`）を1 byteも変えずに呼び（Step43と同じ型）、許可はU14の記録（計画は正規化した形、手順書、code-summary.md、traceability.json、source-manifest.json）の新しいbytesだけにする。Step43の `u14_candidate.py`・binding-06・回帰・実行結果は履歴として変えず、その不変を検査する。コマンド行は `--entry-sha256 <hex> --binding-sha256 <hex>` 必須、`--logical-child` も同じhash検査を先に通す。回帰はStep43の範囲（記録の別のbytes・欠落、許可外のpath、ほかのcompiled source、別のhead、hashの違い・引数、U11の入口とbinding-05の差し替え、logical-child、正の対照）に、Step43の履歴の固定を足す。回帰・今の仮採用のコマンド（Step45の変更で想定どおりexit 1）・新しい入口（exit 0）・正式sensor 2件を実行し、READMEに結果を書く。そのあと書込を止め、独立再レビューを受け、新しい入口のコマンド行の採用を人に提示し、承認を受けてから登録し、正式checkpointで実行する。新しいCI・性能測定・pushは行わない。NFR3、NFR8。

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


