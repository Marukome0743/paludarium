# U2 コード生成の現在source確認

## 現行Step71（Loop-back 1）：共有のabi.rsの再確認とbinding-03

2026-10-17、計画のStep71（Build and TestのLoop-back 1）の記録。下の「現行Step71：採用済み正式検証コマンド…」節は、2026-10-16のレビュー指摘R-05への別の記録であり、この節とは別物である（その節は変更していない）。製品のsource・CI・lock・mise.toml・.gitignore・U1とほかのUnitの記録・旧verification原本は変更していない。

### abi.rsの変更（読取確認）

`crates/paludarium-wasm/src/abi.rs` は e4f84768 → 12d6a2f6 では変わらず、1ceae86c で SHA-256 `f5fd27da40ee25d095084d9bb6c9e21d4dcaeef99fd9667b920e23464267f52a` → `8619137da7f8df65207a8e22e86055db7ea62624340de72b2f73dbceea69d81f` に変わった（作業コピーは1ceae86cのblobと一致）。変わったのは `WorkerJit`（`paludarium_jit::ExecutionBridge` の実装）の `execute_ready` と `execute` の2か所だけである：

- 状態の型が `&mut [u64; 18]` から `&mut paludarium_jit::JitState`（`[u64; STATE_WORDS]`、`STATE_WORDS` = 50）になった。
- host importの `jit_execute` に渡す状態の長さが定数 `144` から `paludarium_jit::STATE_BYTES`（= 50 × 8 = 400。GPR0〜15・RFLAGS・RIPの18語と、XMM0〜15の32語）になった。
- 2か所の `// SAFETY:` のコメントに「scratchはちょうどSTATE_BYTES」と足した。

export（`buffer_new` の64 MiBの上限など）、`unsafe extern "C"` のimportの宣言（`jit_prepare`／`jit_execute` の引数）、モジュール先頭の説明は変わっていない。JS側の `packages/paludarium-wasm/jit-support.mjs`（U14担当）は `JIT_STATE_BYTES = 400` で、長さが400でなければ -1 を返し、失敗時はちょうど400 bytesを元に戻す。

### U2の記録の主張の確認

- **C12の境界**（production-wasm-notes.md「ABI は検査済み scalar/handle と 64 MiB 以下の buffer を通じたコピーを用いる。guest pointer は host pointer として dereference しない」、本ファイルの履歴Step42〜48）：exportについては今のsourceでも正しい。JITのimportの経路は、Rustが持つcode bytesとRustが持つ400 bytesのscratchのpointerと長さを同期のhost import `jit_execute` に渡すもので、guestのpointerではない。この経路は「bufferを通じたコピー」ではなく、共有のlinear memory上のRustの領域をJSが同期の間だけ読み書きするものであり、U14の担当である。
- **`unsafe` とSAFETYの説明**（production-wasm-notes.md「unsafe は Host import 呼出し、wasm export 属性、整列 AtomicU32 に対する bounded wait/notify bridge に限定し、各 bridge に SAFETY コメントを付ける」）：今のsourceでも正しい。`jit_prepare`／`jit_execute` は import module `paludarium` のhost importで、呼出しごとにSAFETYのコメントがある。更新後のコメントは実装と一致する：`state.as_mut_ptr()` は `[u64; 50]`（400 bytes）の先頭を指し、渡す長さは `STATE_BYTES` = 400 である（変更前も `[u64; 18]` = 144 bytesと144が一致していた）。CPU・decoder・MMU・loaderの `unsafe` 禁止は変わらない。
- **production wasmの状態の受け渡し**：production-wasm-notes.mdの「TTY/JIT は typed unimplemented」のうち **JITの部分は今のsourceでは正しくない**。これはStep42〜48当時（署名head 178da99e、当時のabi.rsにJITの経路はなかった）の記述で、今のsourceでは `config_jit` exportでJITを有効にでき、`WorkerJit` がCPUの状態をRustのscratch（400 bytes：GPR・RFLAGS・RIP・XMM0〜15）にして `jit_execute` に渡し、成功したときだけCPUへ戻す（`paludarium_jit::bridge` の `scratch_from`／`commit`）。この不正確さはe4f84768の時点で既にあり、1ceae86cの変更で生じたものではない。TTYの部分は今回確認していない。production-wasm-notes.mdはStep42〜48の履歴として変更せず、この節で直す。JITの意味論と検証はU14の担当で、U2の記録の「JIT 未検証」はU2がJITを検証していないという意味で今も正しい。
- **traceability.json**：abi.rsの状態の大きさ・JITについての主張はなく、分類とtargetは今のsourceでも正しい。変更していない（旧い封印の値 `4579d9b6…` のまま）。
- **source-manifest.json**：abi.rsはpathだけの主張で、今も存在し、U2の所有の説明も変わらない。変更していない（封印の値 `a3b68721…` のまま）。
- `reviewed-source-*.tsv`（例：`reviewed-source-dfcc467739c6.tsv` の abi.rs `f5fd27da…`）は当時のsnapshotの履歴であり、今のabi.rs `8619137d…` と一致するとは主張しない。

### 正式確認のbinding（binding-03）

U1の正式確認コマンド（`construction/u1-skeleton/code-generation/verification/loopback1-next/new_candidate.py`、checker `a7836f9b…`、binding-02 `6315b735…`）は、再利用する旧い封印（`final-verifier-208fd965/consumer-v3/history-seal.json`）でこの計画（封印の値 `d6fe6500…`）とunit-test-instructions.md（`b3ec56ae…`）のbytesを固定しているため、これらの更新後はコード上exit 1になる（今回、U1のcheckerは実行していない）。U1のchecker・binding・旧い封印は変えず、U2の記録の `verification/loopback1-next/` に、U1のcheckerの関数をそのまま呼ぶ新しい入口 `u2_candidate.py` と `binding-03.json`、回帰 `test_u2_candidate.py`、`README.md` を作った。binding-02から増やす許可は、この計画（checkboxの状態だけを無視した形で固定）、unit-test-instructions.md、このcode-summary.md（封印には入っていないので新しいbytesを固定するだけ）の3ファイルで、旧いbytesは封印の値、新しいbytesはSHA-256で固定する。traceability.jsonは変えていないので許可に入れていない。コマンド行、SHA-256、回帰の一覧と件数、実行結果はそのREADME.mdに書く。新しい入口は、人が採用してからU2のcheckpointで実行する。U1のcheckerでの成功は履歴であり、新しい入口の成功と読み替えない。

## 現行Step71：採用済み正式検証コマンドとU2 checkpointの実行結果

本節は再確認レビュー指摘R-05への記録対応であり、計画のStep68〜70には属さない。計画（code-generation-plan.md）とunit-test-instructions.mdは採用済みコマンドの履歴sealでbytesが固定されており変更できないため、本節はcode-summary.mdにのみ置く。unit-test-instructions.mdのStep61〜67にある「別途のコマンド承認後に `verify-current-u2-u11-revalidated.py` を正式な完了確認として実行する」旨の記述は履歴であり、採用済みコマンド（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`、2026-10-16T12:32:15Z採用）に置き換えられている。

人が2026-10-16T12:32:15ZにApproveで採用したConstruction Verification Command（SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`）は、U1所有の入口 `r05-r11-repair-01/final_candidate.py` で、全Unitのcheckpointに共通して使う：

```text
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/final_candidate.py
```

U2 checkpointでの実行結果：verify `d74e4b1a-d52b-4630-9984-dc9996e1b764`、2026-10-16T19:35:06Z〜19:35:42Z、exit 0、stdout `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、`evidence_unchanged: true`、出力先 `verification/r05-r11-repair-01/formal-candidate-1792179306224747000-895/`（proof `.aidlc-construction-checkpoints/u2-integer-isa/unit.json`）。

U2 checkpoint 実行履歴（古い順。以後の実行は成否を問わず末尾に追記する）：

- `d74e4b1a-d52b-4630-9984-dc9996e1b764`：2026-10-16T19:35:06Z〜19:35:42Z、exit 0、`source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、`evidence_unchanged: true`、出力先 `formal-candidate-1792179306224747000-895/`。
- `ea535c9b-095c-411d-8ad8-2cad152a69f6`：2026-10-16T19:53:11Z〜19:53:22Z、exit 1、stdout 0 bytes、stderr に `ValueError: semantic validator failed or emitted unexpected stderr`（子 old_predicates.py が `runtime-discovered input changed` で停止）。原因：採用済みコマンドの履歴seal（`consumer-v3/history-seal.json` の observed_immutable）がU2の code-generation-plan.md（SHA-256 `d6fe6500dcb0321f11b135c735bb1996f54809da807808f288c4809a97d15a4f`）と unit-test-instructions.md（`b3ec56ae1ef32d47f279c322bed9a220500d6bcd011938f880571f14345c1e42`）のbytesを固定しており、R-05対応で両ファイルに加えた「Step71」追記がそれを変えたため。失敗原本は `formal-candidate-1792180391484406000-10580/refusal.json`。
- `9327800b-eb5d-4b1a-8737-0ec0d4a45857`：両ファイルをseal時点のbytesに復元した後、2026-10-16T20:04:03Z〜20:04:39Z、exit 0、`source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、`evidence_unchanged: true`、出力先 `formal-candidate-1792181043679104000-16798/`。

成功の主張はこの履歴に存在する実行（d74e4b1a と 9327800b）にのみ結びつける。以後のcheckpoint実行は成功・失敗を問わずここに追記する。proofファイル `.aidlc-construction-checkpoints/u2-integer-isa/unit.json` は最新の1回分しか保持しない。

この実行は保存済み証拠の純粋再解析であり、U2の全経路・新Linux差分・coverage測定の成功の証拠ではなく、U15別配布Wasm受理の証拠でもない。以下の `verify-current-u2-u11-revalidated.py`（診断）と `verify-current-u10-probe-aube-native.py`（履歴）の記述はそのまま保持する。

## 現行Step68〜70：時間項目の明示指定

内容確認e1c2c013eca5827a4ea44cb5c3dd2670cc97a61632ea889907858de92696d839後、successfulの時間項目引数を既定wall_secondsとして追加し、U11の4環境rowsだけsecondsを明示指定した。U10とU11 nativeはwall_secondsを保持する。fallbackを使わず、数値型/bool拒否/有限/0<=t<=30/exit0/timed_out falseの全条件を維持した。製品・他Unit原本・歴史trace原本の期待hash・現行traceの検査・旧canonical全検査は保持する。

検証済み：Python3.15.0の構文4ファイル、readiness22件、旧inventory8＋trace6＋時間8が各30秒外側timeout内で全件exit0、skipなし（verification/step69-local-results.json）。時間回帰は両正常schemaと0／30の境界、欠落／fallback拒否、誤型/bool、NaN/Infinity、負値、超過、exit／timeout異常を確認した。先行step66-whole-checker-diagnostic.jsonのwall_seconds KeyError/exit1を保持する。今回の全経路診断結果と正式完了検査は別原本とし、診断成功だけで人完了承認やU11未修正機能の完了を主張しない。

検証済み：レビュー前の全checker読取診断は05:03:31.583105〜05:04:43.716114Z、72.13秒、exit0、timeoutなし、stderr空。歴史U10、現行U10、有限U2/U11結合の3成功行をverification/step69-whole-checker-diagnostic.jsonへ全原本保存した。checker SHA d46d14b8ac6ce0475b27bf529394f41c4b57bcac674b45299cdecaeb9f623ec4。独立レビュー・正式checkpoint検査・人のU2完了承認・U11復帰は未完了。

## 現行Step64〜67：歴史trace原本と現行traceの分離

内容確認eeec80372acb01185755a679ac60d1d2af0719e9520338e56486a893a82fb9ac後に実施。検証済み：versioned revision969ecaac390da4a7e50ea1527bae74859ef7450bのU10 verification/step13-historical-traceability.jsonを読取回収し、U2 verification/step64-historical-u10-traceability.jsonへ生bytesで保存した。SHA2164fbd9af6bf6478c06ecf10ef3e3bc7d5dd3bb1a3be845e8855a5a13857764、source5b319／CI38010586387／歴史37が完全一致。歴史proof hashと論理pathを保持し、両関数のtrace/current_binding/preserved/historical_hashes/終了時hashの物理参照を原本copyへ統一した。有限参照監査はverification/step64-original-reference-audit.json。

現行U10 traceは別にSHA0bde9d5eae3205020fe85e0d3e434cfe9c63ba5d7238612e5bb4859e338ad87c、sourcecb979／CI38095031011、全要求60・reverse42・unit/stateとsource digestで厳密検査する。歴史37／現行42、EXTRA2、全旧canonical検査と品質下限を保持する。検証済み：構文3ファイル、readiness14件、旧inventory8＋新trace6は各30秒外側timeout内でexit0、skipなし（verification/step65-local-results.json）。正式失敗c2481414のHistorical trace/proof binding differsは保持する。レビュー前診断の結果と正式完了検査は分離し、U2完了承認／U11同時dispose修正は未完了。製品・他Unit原本は変更していない。

## 現行Step61〜63：歴史37／現行42の限定修正

内容確認1b39b8ba10ce51bd8a0387d1f47e4e78474f34249ad510bab777e94a1979bde1後に共通checkerだけを修正した。歴史37の固定順序・歴史trace/proof・当時署名source digestと、現行42のmanifest全順序・重複なし・現在／署名2b387／保存CI source2c690 digestを分離し、既存全検査・EXTRA2件・有限差分を保持した。検証済み：読み取り限定source照合42件に不一致なし（verification/step61-current42-digest-audit.json）。保存build receiptのupstream guest source inventoryを製品42件のinventoryと混同しない。

検証済み：Python3.15.0のast.parseで2ファイル構文正常、unittest readiness8件、外側timeout30秒の局所回帰8件は0.002秒・exit0・skipなし。正常2件とmissing/extra/duplicate/reordered/digest/歴史現行取り違えの拒否を確認した（verification/step62-syntax-readiness.json、step62-local-results.json）。製品・他Unit成果物は変更していない。前回の正式checkerのManifest inventory differs失敗は保持し、修正後の正式checkerは未承認・未実行。独立レビュー、新command承認と実行、人のU2完了承認、U11同時dispose修正への復帰は未完了。MMU4608原本とCPU/decode32dba当時条件の限定適用を維持し、新CIを反復していない。

## 現行Step58〜60：MMU4608と最終確認候補

内容確認4e28bdfab40ec819ef95b30d3d55b5f5bc8bc2fd5ba200cd6446bfa96d5ef53c後に実施。検証済み：署名fa21cbaff2c5fbd8c87456422c5ca64814c57e1b（connector Verified/valid）のLinux CI38109584503/job114382184327はMMU一対象のみ、raw command max_len4608/max_total_time600/timeout30/rss2048/seed1、ASan/LSan既存suppressionで2852233 runs/601秒/exit0。全774 signed入力before/after一致、現行application329入力と両Cargo.lock一致、compiler fullhash6f5da406b56c2db6607202b63daee73aa8c61297、実binary fc44562820911d2c4198bc694de005d63c76c00526b58a8119ad3dd502146a2d、原ZIP88f1aad8a85cb58da7912fcaaf9caab603f8771689e0cae65956dce4daa30f01を照合した。証拠はverification/step58-mmu-proof.jsonとstep58-mmu-artifact原本。compileを含む03:49:51〜04:00:22の壁時計と、fuzz終了行601秒を区別する。

製品pin nightly-2026-10-10は変更せず、診断だけ公式latest10-11へoverrideした。保存CPU/decode・既存7品質対象はcompiler32dba当時の入力/設定一致への限定適用で、新MMUcompilerとの同一を主張しない。保存旧MMU4096 bytesの601秒exit0は履歴であり、4608成功へ転用しない。初回CI38109485105はfuzz開始前のgit inventory dubious ownership/exit128で停止、step58-first-ci-job.logに保持。診断workflowのread-only ownership指定のみ修正して再runした。

検証済み：既存CI38102192489のU10成功3jobsからnative-first/differential/native-metadataの原ZIPを読取回収し、digest一致、source1365beforeafter、compiler32dba、native14/emulator16/originalargv/native-stat/license原本を確認した。U10担当39は観測2c690から現在2b387まで全bytes一致、共有差はworkflow2とU11 testJSだけ。全体runの旧syscall_args失敗は保持する。U10 aube890deaとU11 aube0667dcは別build、各receipt/native/emulatorと独立に結合し、同binaryと呼ばない。原本はverification/step59-u10-artifacts、限定proofはstep59-current-u10-proof.jsonとstep59-u10-source-binding.json。

検証済み：新verification/verify-current-u2-u11-revalidated.pyはPython3.15.0実体のast.parseによる構文確認のみexit0。旧canonical全検査をhistory/current/shared三関数へ明示分離し、39入力3diff、共有有限5diff、329/U2担当124/trace92/sensors、7ASan、4環境14、JS449、今回MMU原本を結合する。詳細はverification/step59-checker-design.md、他Unit読取の有限84fileはstep59-integration-files.json。未検証：候補の正式実行は独立レビューと新command承認前につき行っていない。構文成功をverification成功と扱わない。

製品・他Unit成果物・engine状態は変更していない。manifest124とtrace既存92担当/status/targetsを保持し、今回実測を追加した。Step58/59完了、Step60は正式レビュー・command承認実行・人U2完了承認・U11復帰が未完了。U9再承認と承認済みU11同時dispose修正は後続であり完了を主張しない。80%/30秒/strict guard/custom順序/比較maskを維持する。

## 現行Step55：共有変更後の有限証拠照合

今回の内容確認 `3a6bdc9a242ab7d36cf26c1ab5ceaf91a4aa94862821083be64915315c4f69ab` 後に実施。検証済み：`python3 .../u2-integer-isa/code-generation/verification/step55-audit.py` 最終exit0。実体jjの `--ignore-working-copy file show -r 2b3874eabda6fe6f1d1334202421db733445fd21 <path>` とSHA256で329 application入力、U2担当124/124を照合し不一致0。currentと4環境観測b263との差は品質workflow `.github/workflows/u11-fuzz.yml` のみ。全path/両hash/証拠hashはverification/step55-current-source-proof.json。manifestと既存traceability92 IDs/status/target、製品実装は変更していない。

検証済み：保存quality38104676911の7targetsは各601秒/exit0、binary原本・raw・compiler32dba69d・Cargo.lockとfuzz/Cargo.lockのbefore/after/current・既存LSan抑制設定が一致。production wasm同module/oracle/guest hashesでNode26.11.1・Chromium156.0.8078.4・Firefox157.0・本物Safari26.6.2各14cases/全row pass/exit0、JS定義5file420/449（93.54%）の原本hashを照合。今回の読取確認であり、新CI・fuzz・Safari実行ではない。旧syscall_args失敗と診断の観測を消していない。

検証済み：U3保存38066034107のcpu_u2=2145400、mmu_u2=3032340、decode=128740995各601秒/exit0。core33inputs、両locks、toolchain、targets、sourcebefore/after、compiler32dba69d、raw7hashと当時binaryhash記録が一致（verification/step55-core-sanitizer-binding.json）。全crategraph差はnative_fs.rsの `#[cfg(test)]` 内2testsとfuzzcrate非依存のwasm abi/filesystem。native_fs差分の位置は同source387行のcfg(test)、core targetsのimportはCPU/MMU/decoder/typesだけ。限定された依存・設定の再利用根拠であり、3targetの当時fuzz実binary原本は保存rawにないため現在再buildbinary同一は未検証。

ドキュメント根拠：U2 functional-spec/rules/entitiesと共有requirements/units/C1/C3/C4/C5の責任を保持。manifest担当124filesの整数意味論・REP両policy・FS/GS最終address・MMU共通同期の既存対応を維持する。ソース中の差分test関数19・並行10・CPU内部14は現在の静的対応数でありparameter展開後の実行数ではない。旧差分38/並行10、固定inventory分母と15family対応は旧当時の証拠として扱い、全static encodingや全入力の合格へ広げない。

未検証/残件：旧U10正式checkerは7eb1819fに固定した39pathsのうちsource-lock.json・ci.yml・u10-native-diagnostic.ymlが現在3不一致。今回はcheckerを実行していないため現在exit1の実測とは呼ばず、sourcecheck拒否はコード根拠の予測。既存検査の下限を保持して新guest/compilerと有限変更を厳密結合する新commandが必要。未承認U11候補は実行していない。U9の直接claim品質workflow変更の再承認と今回U11 index.mjs同時dispose修正は未完了。独立レビュー、command新承認、標準確認、人のU2完了承認、U11復帰は親担当の残件。全入力/全環境/JIT/ID競合完全解消は未検証。80%・30秒・strict guard・custom順序と比較maskを保持する。

## 履歴Step52〜54：全Unitやり直し後のU2照合

今回Summary Confirmation `3a887c7b37a8bb5d996fe43b58eab51c90b4991490d66f7ab7d45b45fdbad231`後に実施。検証済み：read-only `jj --ignore-working-copy file show -r 7eb1819f52acede33e83775374dd4ee93edf643b <manifest writes[].path>`でmanifestの124ファイルを署名済み検証対象7eb1819fのraw bytesへ照合し、124/124一致・不一致0・欠落0。SHA256両値と各jj終了コードはverification/step52-source-claims-proof.json。manifestの担当/schemaと既存製品を維持し、U11承認済み作業・他Unitの成果物は変更していない。

ドキュメント根拠：U2 functional-spec/rules/entitiesと共有requirements、unit-of-work、C1/C3/C4/C5を読取確認。整数命令・例外・REP・MMU原子操作の担当、U5のguest clone/futex、U11のWorker、U14のJITの境界を保持する。既存traceability92 IDsのstatus/targetは変更しない。旧178da99e以前のCI・Safari・各601秒ASan/LSanとそのsource一致は各履歴当時の観測であり、7eb1819f全sourceの新実行成功へ転用しない。

今回の製品テスト再実行はなし。現在の署名/CI/coverageとの対応は共有verification/u10-current-proof.jsonの7eb1819f/CI38021278452を入力とし、承認済み `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u10-probe-aube-native.py` を親の標準checkpointで確認する（この記録時点では未実行）。124claim一致から全workspace・全入力・全環境の一致や安全性を推定しない。現source全体の新ASan/LSan、今回のNode/Chromium/Firefox/本物Safari実行、並行セッションID競合の完全解消は未検証。strict guard、80%下限、30秒watchdog、各600秒fuzz、固定nightly、native先行/内部test-afterと比較maskは維持。

正式required-sections/traceabilityの実結果はverification/step53-sensors.jsonへ保存する。4producesとsource-manifestを今回内容確認のもとで保存し、Step54の独立レビュー・canonical checkpoint・人の完了承認・次Unit遷移は親へ引き渡す。

## 履歴Step49〜51：保存証拠と対応表の確認

今回Summary Confirmation `b81c718d0776da2c51eb806cbdcb70e4f4d44ba3c008d5655931b140a30de232`後に実施した記録確認である。検証済み：source-manifestの124claimsは、read-only `jj --ignore-working-copy file show -r 178da99e88d1aea242c5141207887767a69fa670 <path>`とのSHA256比較で124/124一致、claim内の文書例外0。manifest SHA256 a3b68721fb3659100c1644729ed689235d5862a80cefb4ffa2847d9c07dc3ebaと全paths/両hashはverification/step49-source-claims-proof.jsonへ保存した。製品・U1・他Unitに変更はない。

検証済み：承認済みcanonical `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。全186 tracked application filesを同じ署名済み178da99eへ照合し、docs/reports/wasm-threads.mdの厳密hashによる既存文書例外だけを区別した。CI37745425190の8jobs、sanitizer37745425204の4jobs、native37745425183の2jobsは同一SHAで成功。実コマンド・stdout/stderr/exitはverification/step49-native-ci.jsonとstep49-native-ci.log。保存済み証拠の再確認であり、新しい製品テスト実行とは数えない。

検証済み：既存step47-proof/CI metadata/step45実Safari証拠の内容とhashを照合しverification/step49-evidence-reuse.jsonに集約した。Node/実Safari14ケース、production CI wasm SHA cb37fa85a9818f96b821785e3d1a8538ec0cb078ca5e79223ee3839053ba3e78、shared Rust heap/nested Workers、CPU2155757/MMU3189042/decode142758823/load_elf23166884 runs・各601秒ASan+LSan exit0・source154before/after/host一致を保持する。全体92.68%・U1対象83.04%・U9対象82.55%の80%gateは同runの証拠。固定nightly-2026-10-01、seed1、timeout30、rss2048、CPUmax_len4096/MMU4608、既存suppression・比較mask・native先行/内部test-afterを変更しない。診断push CIの観測でありscheduled nightly実行とは呼ばない。

未検証：任意guest/任意入力の完全保証・全UB不在、guest clone/futex全意味論、JIT、Chromium/Firefox今回実行、mount/network、probe/aube全統合。共有C1/C3/C4/C5・Host境界を維持し、U5/U11/U14等の全機能完了へ広げない。U4証拠表記修正とU9公開型修正は後続対応として未完了。Step51の独立レビュー・正式Unit完了確認は親担当である。

検証済み：限定sensorの実コマンド・stdout/stderr・exit・passはverification/step50-sensors.jsonに保存した。traceability/required-sectionsは両方exit0/pass:true/findings0、H2=13。今回4producesとmanifestは上記内容確認後に保存し、124claimsと既存traceability分類を保持する。

## 履歴：以下はStep1〜48当時の記録

以下の「現行」「今回」「未検証」「未実装」「GAP」は各先行記録時点の状態であり、Step49〜51の現在sourceに対する主張へ転用しない。旧4d52/af9b、local LSan失敗、診断wrapper、旧CIと最新178da99e production観測を区別する。現在値は上記確認とstep49/50証拠を参照する。

## 履歴Step42〜48：実 production wasm と R03 修正

検証済み：新 paludarium-wasm cdylib と C12 JS launcher が既存 Config/Session→loader/Vfs/kernel/CPU/MMU を実行する。WasmHost を target gating し、native semantics は変更しない。共有 build-std/atomics の Rust allocator/Arc/Mutex/OnceLock、独立 stack/TLS、coordinator→nested Worker、正常 return 後の解放、trap 時の全 heap 破棄を実装した。manifest124 claims が実ファイルを列挙する。詳細は production-wasm-notes.md。

検証済み：実機 native6 ELF の先行期待値と SHA を照合し、Node/本物Safari 各14ケース PASS。hello出力/exit0、integer42、atomic146、Kernel SIGFPE8、stdin input\n、kill9、4同時Session、shared Rust allocator256操作、同一 AddressSpace atomic2000、wait0/notify1、factory再初期化、active stdin待ちdisposeを確認した。旧CPU wrapper136を製品signalと読み替えない。

検証済み：最終 fork CI head178da99e88d1aea242c5141207887767a69fa670、署名Verified=true、CI37745425190の8jobs全success。Linux/macOS/Windows、fmt/clippy/dependencies、native差分、production Node14件、lines全workspace92.68%/U1対象83.04%/U9対象82.55%（各80%以上）。CI生成wasm SHA cb37fa85a9818f96b821785e3d1a8538ec0cb078ca5e79223ee3839053ba3e78 を実Safari27.0.1で14件PASS、1871ms、COOP/COEP/crossOriginIsolated/cleanup=true。ローカル生成module SHA5c76de…とはbytes異なるので同一binaryと表現しない。verification/step45-production-wasm/ci-safari-report.json、step47-production-ci-artifacts/、step47-coverage.log が実測。

検証済み：R03全fetch/poll/cleanupにdeadline、最外process-group watchdog30秒。応答しないdriverは28400.43msで非ゼロ終了、残留なし。旧Step40履歴は変更しない。verification/step43-watchdog/unresponsive-proof.json。

未検証：任意全guest/全UB不在、guest clone/futex全意味論、JIT、mount/network、Chromium/Firefox、probe/aube全統合。後続Unit全体の完了を推定しない。検証済み：最終sourceのCI37745425204でCPU2155757/MMU3189042/decode142758823/load_elf23166884 runs、各601秒、ASan+LSan終了exit0、source154件before/after/host一致。seed1・timeout30・rss2048・max_len4096/4608・既存suppression維持。verification/step47-proof.json を参照。nightly/80%/30秒/custom orderingを維持する。


## 履歴Step39〜41：clone切り分けと製品wasmの適用限界

検証済み：Step39の同一C source/hashで64caseのclone比較検査PASS（verification/step39-clone-proof.json、step39-clone-diagnosis.md）。local QEMU10.2.3はflagsなし/SIGCHLDだけ成功42、残るflags15組/SIGCHLDとsignal0全16組はEINVAL。native実機x86-64 Linuxは32組すべて成功42。ptraceはlocal ENOSYS/native成功、最小LSan local終了1/native2回0。VM経路ではSIGHAND/THREAD/SYSVSEMの必須flags不足、fork経路ではFS/FILES/UNTRACEDと非SIGCHLDが拒否され、単一flagだけを原因とはしない。同version公開QEMU sourceとの一致はドキュメント根拠で、配布binary内部branch/独自patchは未検証。LSan直接失敗点はclone EINVALによるtracer生成失敗。local customimageとnative CI imageは別image。native run37739732442/headb44049356ce2537720487310bd15b1fcf0217c88 Verified=true。

検証済み：Step40でactual production APIs/起動経路を読取確認。production Session/ConfigはRust APIだがwasm export/JS production launcherは存在せず、spikes/wasm-threadsは別module。固定nightly2026-10-01でcargo build --locked --release --target wasm32-unknown-unknown -p paludariumはexit101、isolated full Session wrapperもexit101。paludarium-hostの無条件cap-std/cap-fs-ext/fs2依存からerrno0.3.14がtargetOS unknown unsupportedのcompile_error。production-build.log/full-runtime-build.log、full-runtime-Cargo.toml/full-runtime-lib.rsに失敗と構成を保存。loader→Vfs→Host/kernel/runtimeもこのfull buildの阻害対象。製品修正や新本番launcher実装は行っていない。

検証済み：製品CPU/MMU/decoder/typesをリンクした独立診断cdylibはwasm32 release/locked build exit0。同一core.wasmをNode24.21.0 Workerと本物Safari27.0.1/macOS Workerで各3cases実行、外側30秒watchdog、Safari COOP/COEP・crossOriginIsolated=true、両exit0。整数exit syscall引数42、atomic exit syscall引数146、DIVのCPU ArithmeticFaultを診断encoding136として観測。実機nativeの同guest SHA（integer42/atomic146/divide_fault SIGFPE=-8）との限定比較PASS。ArithmeticFault136はwrapperの診断値で、Kernelのguest signal配送やstdout/exit全runtimeの成功ではない。native helloのstdout hello\n/exit0は取得済みだがwasm hello/runtime実行はbuild阻害で未検証。

具体証拠：verification/step40-wasm/{Cargo.toml,Cargo.lock,src/lib.rs,core.wasm,core-build.log,production-build.log,full-runtime-build.log,guest-hashes.json,node-check.mjs,node-report.json,safari-check.mjs,safari-report-host.json,proof.json}。native期待はverification/step39-ci-artifacts/u2-native-guests/results.json。Safari初回sandbox fetch失敗はsafari-report.jsonに保存しhost権限再実行で実Safari結果を取得。proofはwasm/source/全診断artifact hashes、nativeguest hash比較、3cases×2環境、限定passを記録。production127source baseline一致、95claims再照合はverification/step41-source-claims-proof.json。

未実装/未検証：core module memoryはshared=false、imports0。共有std heap、製品moduleを共有する入れ子Worker、production launcher/host/runtime/loaderのwasm実行は未検証。独立Workerがsingle-memory moduleを実行できることからthread共有を推定しない。共有inception/units-generation/unit-of-work.md:124〜131のU11 u11-wasm-launcherがwasmHost/起動JS/SABAtomicsとNode/Chromium/Firefox/Safariを担当。thread/futex kernel/Host/Runtime意味論はU5、JITはU14の責任を保持。Step37四target各601秒ASan+LSan成功、実Safari spike、af9b unit/diff/80%gateは別証拠。全入力/全UB/全vendorの合格を主張しない。nightly/80%/30秒/custom順序を維持。


## 履歴Step36〜38：fork実機x86-64 Linux診断CI

検証済み：[診断run37736496982](https://github.com/Marukome0743/paludarium/actions/runs/37736496982)、SSH署名済みhead77663b7982857cba841c91d4b23b44287bb8e29bで4jobs成功。af9b739d742a9552f44fc1515646c862b19e5de2基準のisolated jj workspaceへ診断workflowだけを追加した。製品source127pathsはbaseline/CI container before-after/現在hostで全hash一致（verification/step36-ci-source-baseline.json、step37-ci-artifacts-proof.json）。診断SHAと既存af9b CI37713953347/native37713953340のunit/differential/coverage証拠は別枠であり、診断を既存suiteの新実行とは数えない。main checkout/U1/製品sourceの変更なし。

検証済み：cpu_u2=2104569、mmu_u2=4900201、decode=86019257、load_elf=16609257 runs、すべて601秒・exit0/source-compare-exit0。各bundleの最小C ASan終了診断は2回ともexit0。native x86_64 Linux container、nightly-2026-10-01、cargo-fuzz0.13.2、ASan binary symbols、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、ASAN_OPTIONS=detect_leaks=1、seed1、timeout30、rss2048を確認。CPU max_len4096/MMU4608を維持。sanitizer異常・LSan fatalは観測0。これは診断用push CI実行でありscheduled nightly実行とは呼ばない。

具体証拠：verification/step37-ci-jobs.json、step37-ci-raw.log、step37-ci-artifacts-proof.json。4bundleはverification/step37-ci-artifacts/u2-asan-{cpu_u2,mmu_u2,decode,load_elf}/で、各target.log、exit.txt、start.txt/end.txt、source-before.sha256/source-after.sha256、source-compare-exit.txt、settings.txt、environment.log、binary-symbols.txt/binary.sha256、minimal-{1,2}-exit.txt、minimal-settings.txt、corpus-before.tar/corpus-after.tarを保存。proofに各archive SHA256と全artifactファイルhash、実測runs/秒数・全checksを記録。verify-step37-ci-artifacts.pyの検査PASSを根拠とする。

検証済み：先行Step33〜35のlocal失敗は保持。rootの追加診断verification/step36-local-diagnostic.md、step36-local-binfmt.txt、step36-local-ptrace.txt、step36-local-lsan-syscalls.logに、同image/権限のQEMU x86_64登録、ptrace ENOSYS、最小C LSanのclone(...CLONE_UNTRACED...) EINVAL、Failed spawning a tracer threadを保存。直接失敗点はLSan tracer thread生成。推測：QEMU user-mode制約との整合性が高いが拒否された個別clone flag/版固有原因は未検証。既存suppressionやLSanを弱めず実機CIで合格を回収した。

検証済み：connector保存step37-ci-run.json/step37-ci-artifacts.json、step38-source-claims-proof.jsonの95/95現在claims一致、step36-ci-workflow.ymlのexactcopyも参照。CI rust:1-bookwormのpull digestはsha256:114c7a4425406451c2866b6aafe69fe29b1b298832db1277d411ac73c82d04d6（step37-ci-raw.log:74/1822/5667/14299）。Docker config imageIDは未記録でdigestをimageIDとは呼ばない。local customimage6666753bとCI imageは異なるため完全同一image比較ではない。localのclone EINVAL/ptrace ENOSYSとCI成功を分け、個別clone flag/版固有原因は未検証とする。

対応範囲：NFR2/NFR2.2/NFR3/NFR3.4の不足した現行fuzz証拠を回収しU2責任範囲のOKへ更新。NFR3は既存unsafe禁止/lint/80%coverageと今回fuzzを組み合わせる。全体FR9.3は後続syscall_args/VFSを含むためDeferred維持。任意入力完全保証・全UB不在・native意味論一致・全vendor・production wasm・共有std heap・入れ子Worker・他Unitの合格へ推定しない。旧4d52 metrics/旧r01 fuzz/local失敗は履歴。以下の4GAP維持/新CI未検証/未実行という記述は各過去時点の観測で、現行状態は本節を参照。80%/30秒/nightly/各600秒/custom順序を保持する。


## 履歴Step33〜35：CPU/MMU各600秒ASan（失敗証拠）

検証済み：承認後に既存Docker image6666753bed3a753ce9f178d5a76bd91ff1de45cf6918a273fe9a43892eb51971を使い、単一同期snapshot/同containerでcpu_u2→mmu_u2を順次実行。固定nightly-2026-10-01、cargo-fuzz0.13.2、ASan、seed1、timeout30、rss2048、max_len4096/4608、既存LSan suppressionを維持した。cpu_u2は636751 runs/601秒、mmu_u2は910789 runs/601秒だが、両方終了時にLeakSanitizer fatalでexit1、総command exit1。ASan本体の入力処理中に異常は観測しなかったが、終了検査を含む合格ではない。raw cpu_u2.log/mmu_u2.logと各start/end/exit、corpus-before/after.tar、source-before/after.sha256はverification/に保存。

検証済み：source before/after cmp exit0。host127実ファイルは全一致、containerのみ32件はmacOS tar由来の._AppleDouble metadata（sourceではないがraw159件に保持）。hostとのSHA照合と実時刻はverification/step35-current-asan-proof.json。実process環境に-Zsanitizer=address、ASAN_OPTIONS=detect_odr_violation=0（cargo-fuzz設定）、LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp、固定nightlyを確認し、両binaryのASan symbolsをstep33-sanitizer-runtime.txtに保存。Docker実argsはCAP_SYS_PTRACE/seccomp=unconfined/stack=-1、uid0、LinuxKit7.0.14、aarch64Docker上amd64image。ptrace_scope pathは存在しない。step33-docker-inspect.json/step33-docker-info.txtが実構成。

検証済み：製品に依存しない最小C main{return0;}をcc12.2/ASan/同image・権限・LSanenvで2回確認し、両exit1・同LSan fatal（step35-minimal-asan.txt）。終了処理のrunner問題を再現した。推測：amd64エミュレーションとptrace制約が原因候補であり、実QEMUbinfmt未確認のため原因確定ではない。ドキュメント根拠：[QEMU user emulation](https://www.qemu.org/docs/master/user/main.html)のptrace制約、[LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html)の終了検査説明。LSan無効化・suppression追加・retryによる合格化は行わない。

GAP：NFR2/NFR3/NFR2.2/NFR3.4の4GAPを維持。decoder/ELF等の現行600秒、production wasm、共有std heap、入れ子Worker、任意入力安全性は未検証。実機native差分38/並行10と80%下限の保存af9b CIは別証拠として保持する。再開手順：LSan終了検査を実行できるx86-64 Linux runnerでunit-test-instructions.mdの同一snapshot/seed/予算/品質条件をそのまま実行し、両exit0とsource不変を回収する。今回source変更なし。


## 履歴Step30〜32：af9bの記録照合

検証済み：今回Summary Confirmation 699f316ed0dc6f786bd0ff8fc068f4dc6808b8af4653792fad4fdc171a9f38f3、UNIT_STARTED後、jj --ignore-working-copy file show -r af9b739d742a9552f44fc1515646c862b19e5de2 <path>とSHA256でU2 manifest95claimsを独立照合し、95/95一致・欠落0。verification/source-bytes-af9b739d-current.json/.tsvが今回のbyte proof。元のreviewed-source-4d52be0a-current.tsvは95files中2差異、verification/workspace-ci-source-match.tsvは127files中9差異で、旧snapshot一致を現在の根拠へ転用しない。既存95claims/schemaを保持し、製品・テスト・CI・U1成果物の変更はない。

検証済み：署名済みaf9bのCI37713953347（7jobs）/native37713953340（4jobs）成功をstep30-native-ci.logで再確認。ci-jobs-37713953347.json/ci-jobs-37713953340.jsonとci-native-bookworm.log/ci-coverage.logは同SHAのU1保存証拠をU2 verificationへコピーした。コピーは新テスト実行ではない。全162application filesの比較はU1で承認された厳密hash文書例外を含む共有検査で、U2 claims全一致は別に独立確認した。

検証済み：ci-native-bookworm.log:862はU2差分38pass/0fail、2003はホスト並行10pass/0fail。source名と保存rawログ対応はstep30-test-correspondence.json：CPU14/decoder9/MMU9/types1/kernel1のU2内部tests全存在・実行済み。CPU全39のsummaryには後続U4等を含み、U2専用件数として扱わない。u2_segment_内部5、u2_segment_atomic_forms差分1、u2_atomic_gs_差分2のexact名を保存ログで確認し、新filter実行とは数えない。REP両model内部tests（u2_repeat_data_fault_applies_explicit_flags_model／u2_repeat_fetch_fault_applies_explicit_flags_model_and_clears_context）もok。CMPS/SCAS start/partial/budget native6casesはAuthenticAMD観測で38suite内、Intelは先行証拠。mask0xcd5、外側30秒kill/reapを維持する。

検証済み：ci-coverage.log:2340は全体7155行/未実行524=92.68%、2802はU1対象packages6905/1171=83.04%。両80%gate成功、分母は後続共有実装を含みU2専用coverageではない。3OS/lint/依存の成功は同runのjobsで確認。4d52の92.57%/82.71%、旧197/94.00%、旧fuzz各601秒は履歴。

ドキュメント根拠/検証済み：C1 ArithmeticFault→Kernel SIGFPE、C3 forms、C4 typed atomicと全アクセス共通同期、C5 REP continuation/FS-GS最終addressの既存source対応を保持。inventory/rebuild receiptは固定取得・builder履歴。再集計aube4658=整数3136+system190+U31332、probe865=整数696+system3+U3166、native_case tokens欠落0（step30-inventory-correspondence.json）。全static encoding実行やcomplete runtime inventoryとは主張しない。15/15 family対応、U5 clone/futex・U10 program全体・U11 wasm・U14 JITの境界を維持する。

対応表：既存44行のstatus/targetを保持し、共有requirements fallback48IDsを担当分類で追加した（92IDs/92対応）。FR5.4はU5 native thread割当とU11 wasm Worker割当を明記。NFR4/NFR6既存OKはU2の詳細責任への対応であり全製品のmount/network/JIT合格ではない。検査の実結果はverification/step31-sensors.json。

履歴（Step30〜32時点）：当時は現行sourceの各600秒ASan証拠がなく、重いfuzz/全suite再実行なしで4GAPを保持した。現在はStep33〜35でCPU636751/MMU910789各601秒を実行済みだが両LSan終了fatal/exit1のためNFR2/NFR3/NFR2.2/NFR3.4の4GAPを維持する。新fork診断CI結果はまだ未検証。単独Safari spikeからU2 production wasm・共有std heap・入れ子Worker・任意入力安全性を推定しない。nightly-2026-10-01、各600秒、80%、30秒、比較mask、custom順序を維持する。

以下のStep1〜29・4d52観測はすべて当時の履歴。本文中の「現在」「今回」「差異0」はその時点に限り、現行af9bへの一致・今回新実行を意味しない。


## 履歴：Step27〜29（4d52時点）

検証済み：u2-redo-brief全文と新内容確認後、95claims/95snapshotとCI対象127pathsの現在bytes一致、44trace target欠落0、CI4d52の11jobs成功を再確認した。下記既存差分38/並行10・3OS品質証拠を再利用し、新実行と数えない。新Summary Confirmation後に実4produces plan/instructions/本summary/traceabilityとmanifestを全保存した。既存claims/schemaと4ASan GAP/wasm未検証を保持。製品変更・追加testsなし。親diaryをレビュー前に終え、引渡し後は全書込とSCM snapshot操作を停止する。

## 履歴：Step24〜26（4d52時点）の再確認

検証済み：tool-produced u2-rereview-brief全文と現在承認後、95claimsをread-only git show4d52be0aと比較し95一致/欠落0。保存snapshotと同じexec.rs=e660a4c0…、u2_tests.rs=dc80918a…を確認した。manifest SHA256=f63868dd93dda0e9138225540f9b4967915329441dfe1d6eb35d5ab0de12b0a7、strict version1の所有範囲は変更不要。

保存CI JSONは4d52be0aで7+4jobs success。Bookworm raw475/480行のREP両model内部test、861行の差分38、1884行の並行10passを確認した。traceability44件のtarget欠落0、既存NFR2/NFR3/NFR2.2/NFR3.4のGAPを保持する。現在600秒ASan/wasm未検証を合格へ転用しない。製品変更・追加テスト実行なし。Step1〜23は履歴で、今回の日記をレビュー前に確定し、rootの依頼以降はsource/成果物/SCM snapshot操作を固定する。

## 履歴：Step20〜23の結果（4d52時点）

検証済み：承認済みStep20〜23を実行し、U2の95source claimsとCI対象127pathsがproduction revision `4d52be0a6f3b11d6c11a62f96196985c9c280fdc` のbytesに一致した。今回はU2記録だけを更新し、製品・テスト・U1凍結成果物は変更していない。現在の実機CI証拠を照合して再利用し、テストを再実行したとは表現しない。

[CI37695518838](https://github.com/Marukome0743/paludarium/actions/runs/37695518838) の7jobsと [native37695518927](https://github.com/Marukome0743/paludarium/actions/runs/37695518927) の4jobsは成功。実機Linux U2差分38件・ホスト並行10件、3OS既存suite、fmt/clippy、依存検査、全体行coverage92.57%を確認。80%下限を維持した。詳細ログ・source snapshotは evidence-current.md と verification/ にまとめ、レビューにU1記録の読取を要求しない。

## 現在の実装と契約

C1 ArithmeticFaultはKernelでSIGFPEへ渡り、C3の幅/prefix/暗黙operandをC5が解釈する。C4のtyped atomicと通常アクセス/mappingは共通同期に参加する。FS/GS atomicの最終linear address、failed compareのwrite preflight、128-bit alignment、REP再開を現在sourceとnative回帰へ照合した。

REPfault flagsは明示的なCpuState policyで、既定 `RestoreInitial` はIntel設計の開始flags復元を維持する。`PreserveCompleted` は観測済みAMD EPYC modelで、productionがhost CPUを検出して変更することはない。native差分fixtureだけがobserverのCPUID vendorに応じて選択し、未知vendorを失敗にする。start/partial/budget/fetchの両model内部testsは通過。現在native runnerはAMD、Intel成功はe081時点の履歴で、関連7sourceのbytes一致を確認した。

固定inventoryはaube4658forms（整数3136/system190/U3 1332）、probe865forms（整数696/system3/U3 166）。分類分母とnative-case参照を保持する。追加15/15命令群の対応はfamilyの対応であり、全static bytesや任意入力の一致率ではない。probe/aube全program統合はU10、clone/futexはU5、wasmはU11、JITはU14へ残る。

## 更新した記録と所有境界

code-summary.md、evidence-current.md、traceability.json、source-manifest.jsonの現claim照合snapshot、およびplan Step20〜23のチェックを更新。先行summary/evidence-current/traceabilityは historical-* に保存し、evidence.mdと旧reviewsを保持した。manifestのstrict schemaと95 owning pathsを維持し、共有CPU/observerのREP修復は現在source確認対象として説明する。新しいapplication-sourceは作成・変更・削除していない。

## 品質の限界

履歴（Step30〜32時点）：当時はREP修復後sourceの各600秒ASan未実行だった。現在はStep33〜35でCPU636751/MMU910789各601秒実行済み、両LSan終了fatal/exit1（verification/step35-current-asan-proof.jsonとraw logs）。過去CPU/MMU成功は旧sourceの履歴で現在の合格へ転用せず、4GAPを維持する。新fork診断CI結果はまだ未検証。既存nightly各600秒、30秒watchdog、nightly-2026-10-01、比較mask、coverage80%を変更していない。

未検証：全vendor・任意入力/経路、完全runtime inventory、probe/aube emulator全program、wasm/Safari/JIT統合。今回のCI成功をこれらの証明に使わない。具体的な新製品不具合は今回の照合では見つからず、独立reviewと完了判定はconductorへ渡す。

検証済み：Step31 traceabilityはpass:false/findings4で実GAP NFR2/NFR2.2/NFR3/NFR3.4のみ。missing IDs/invalid entries/invalid targets/orphansは0。required-sectionsはpass:true/H2=7。exit0をPASSへ読み替えず、未実施ASanを保留としてBuild and Testへ渡す。全produces・manifest・証拠の書込を終了し、独立レビュー前に固定する。
