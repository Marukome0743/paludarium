# コード生成の結果（u1-skeleton）

## 現行Step72：正式確認コマンドの修正（2026-10-17、再レビューiteration 4・5のMinor）

本節はStep72の記録である。人はStep71の新しい正式確認コマンド（command SHA-256 `f6c6d3216bbfbe4c483427a985e0ebd8d59732910e6cfb208dbffc84e2fc038b`）を採用し、再レビュー（iteration 4）のMinor 5件（R-20〜R-24）と、再レビュー（iteration 5）の指摘2件も直すよう求めた。コマンド行は変えず、checker・binding・回帰・記録を直した。製品source・CI・lock・mise.toml・.gitignore・ほかのUnitの記録・旧verification原本・source-manifest.json・binding-01.json・Step71の実行原本は変更していない。

検証済み（新しいchecker・binding）：`verification/loopback1-next/new_candidate.py` の今のSHA-256は `a7836f9b880aed05b18d1f283f1cee4dadf79a420b8d8aaa6b3587a6652fc339`、既定のbinding `binding-02.json`（schema 2）のSHA-256は `6315b735647c310e5b9ac82291a56652830ff406ee98c43a0a31b2f7db70ecbb`、回帰 `test_new_candidate.py` は `dce37d4f104e2b9a2638af89a39662b357f2bf47fd1e09d6ba85c4547d0c6209`。同じコマンド行でexit 0だった（`verification/loopback1-next/run-1792243084087620000-92303/result.json`、再利用した旧chainは `r05-r11-repair-01/formal-candidate-1792243084680309000-92303/` で `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、子4件exit 0・stderr空）。

検証済み（R-20：性能のmoduleの束縛）：u14-quality run 39030957672のartifactを読み取り専用で取得し（`gh api` のartifact metadataと、`gh run download` で `target/u1-step72-dl-*` の新しい空のフォルダーへ。中身は実行していない）、`verification/loopback1-next/module-receipt-39030957672.json`（SHA-256 `db2adee52abf71bfb083dbdc10a46430599dc1bcdee28f96c292bd707f9a8e63`）に束ねた。attempt 1の `u11-programs / build-oracle`（job 117391130739、`bash scripts/build-wasm.sh`）が上げた `u11-acceptance-inputs`（digest `sha256:5c589aad…`、`workflow_run.head_sha` 1ceae86c）の `paludarium.wasm` は `d892ea2879dd160aa3e81f0afafef56b73d826bcfa88995b310a60e49d51faad` で、性能の原本の `moduleSha256` と一致する。probe・oracleも一致し、性能の原本そのものは同じrunの `u11-node`（job 117392269851）の `performance/observations.json` と同じbytesである。checkerはこれらを確かめる。artifactの中にmoduleのsource digestやbuild receiptはなく、headへの結び付きはGitHubのartifactのmetadata・build jobのhead・runのheadによる。旧 `current_semantics` の「保存済みの標準module（fb2fdb…）を再利用」という主張は、旧い内容（be45、論理viewの旧bytes）に対する主張で、1ceae86cのmoduleではない。checkerは `result.json` の `claim_scope` で、この旧い主張（`old_current_semantics`）と1ceae86cの性能の束縛（`performance_1ceae86c`）を分けて書く。

検証済み（R-21：CIをjobの単位で）：`verification/loopback1-next/ci-jobs-1ceae86c.json`（SHA-256 `982989cf7f91da788341c7591013df5800045fe4a12fb7bb1799209b3688d506`）に、7 runの最新attemptのjob名・job ID・結論・開始時刻を束ねた。checkerは、bindingに固定した期待するjobの集合（CI 23・Release 1・U12 29・U13 29・U14 fuzz 13・source-bound 7・U14 quality 34）と名前・数が完全に一致し、すべてsuccessであることを確かめる。skippedはbindingに書いたものだけを許す（今回は空で、skippedのjobはない）。checkerは保存したhash固定のJSONを読み、checkpointの時点でliveの `gh api` は呼ばない（作成時に一度、7 run・attempt 1を含めてliveのAPIと照合し、すべて一致した）。

検証済み（R-22：同じheadのattempt 1の失敗）：U13 quality run 39028305765のattempt 1は、job 117383570126 `differential tests (x86-64 Linux)` のstep 6で `diff_u3` の `u3_fresh_native_differential` が `unobserved native SHA profile: "GenuineIntel" signature 000606a6`（`tests/guests/u3/native-contract.rs:25`）で止まった（未観測のIntel CPU signatureで止まる作り）。U14 quality run 39030957672のattempt 1は、job 117392444723 `windows-host` のstep 14（coverage付きのprobe）で、case `probe-all` が30秒の上限に達した（`timed_out: true`）。同じheadのU13 qualityでは同じ名前のjob（117385157902）が成功している。遅くなった原因は確定していない。どちらもattempt 2は失敗したjobだけの再実行で、正式な性能測定はattempt 1の1回だけ（job 117392269851）である。これをCIの証拠JSONとREADME.mdに書き、checkerは失敗したjobの一覧と、attempt 2で再実行されたjobが失敗したjobだけであることを確かめる。

検証済み（R-23・iteration 5の指摘2：回帰）：拒否の回帰を9件足し、Step71の20件と合わせて29件がすべて期待どおり（exit 0）。足したのは、`new_sha256` と作業コピーの同時の偽、`run_old_chain` のguardのargv・cwd・timeoutの各不一致（3件）、論理viewの範囲外のpath、`run_attempt` の不一致、性能の行の対の崩れ（JITあり・なしの数の違い、pairの重複。checkerはpair 0〜9ごとに1対を要求するようにした）、module hashの不一致、jobの欠落・失敗である。実ファイルは変えていない。1回目の実行ではtest_24が回帰テスト自身の誤り（比較用の物理bytesを論理viewの中で読んだ）で失敗し、test_24だけを直して再実行した。一覧は `verification/loopback1-next/README.md` にある。

検証済み（R-24：記録）：計画のStep71の「14個」「209個」は、正しくは13個・210個である（計画のStep72項目5の注記）。この記録の古い「現行」見出し（Steps67〜69・Steps63〜66・Steps48〜50）と「今回Steps51〜54」の見出しを、各時点の「履歴」に直した。unit-test-instructions.mdのStep71節の「回帰9種」は実際の件数（20件）に直した。

未検証（iteration 5の指摘1）：checkerの中身が変わったので、コマンド行が同じでも、修正後のchecker（SHA-256 `a7836f9b…`、binding-02 `6315b735…`）は人がもう一度採用（Construction Verification Commandの決定・回答・設定）してから、U1のcheckpointで検証する。この作業では採用していない。Step71のchecker（`09ec238a…`）での成功は、2026-10-17T13:01Zのcheckpoint検証（exit 0、`run-1792242039966644000-88257/`）を含めて履歴であり、修正後のcheckerの成功とは読み替えない。初回crashのcore欠落、U15別配布Wasmの受理（GAP）、歴史jit_compile panic、セッションID保証は解決していない。独立再レビューはこの記録の後に行う。

## 前回Step71：新しい正式確認コマンドの候補（2026-10-17、Build and TestのLoop-back 1）

本節はStep71の記録である。製品source・CI・lock・mise.toml・.gitignore・ほかのUnitの記録・旧verification原本・source-manifest.jsonは変更していない。下の「R05／R11…（Steps67〜69）」節は、その時点（署名be45）の記録として保持する。

検証済み（変化の事実）：U14のLoop-back 1で整数SSEのJIT（署名head 12d6a2f63c205b672d30e8bcb104dc0ee75932ac・1ceae86ce303a1019e97ac7d162ce0efa9fadd50）が入った。1ceae86cのCIは、PR CI 39028285747、Release package checks 39028285755、U12 quality 39028303336、U13 quality 39028305765（attempt 2）、U14 fuzz 39028307842、source-bound 39028309948、U14 quality 39030957672（attempt 2）がすべてhead 1ceae86c・successである。3つのcommitはGitHubで `verified: true`／`valid`、親子はe4f84768 → 12d6a2f6 → 1ceae86cである（`gh api` で読み取り、`verification/loopback1-next/ci-1ceae86c.json` に保存し、保存後に再取得して全項目の一致を確かめた）。正式な性能測定（FR8.3）の原本 `u14-jit-wasm/code-generation/verification/loopback1-next/perf-39030957672-observations.json`（SHA-256 `b827a5e1c1ece977be6acab4988d5c1d9dc8a1d54cd5877451eb6d241e402b7c`）は、JITなし平均4.5277秒・JITあり平均3.6349秒、p = 1/1024、20回すべてPASSである。

検証済み（旧コマンドの失敗）：採用済みの正式確認コマンド `r05-r11-repair-01/final_candidate.py` は、今のsourceでexit 1になる（`verification/r05-r11-repair-01/formal-candidate-1792240234682266000-82058/refusal.json`）。内側の理由は、子0（old_predicates.py）の `compatibility.py` が出す `configuration differs beyond three authorized entries`（mise.toml の `"npm:npm" = "12.2.0"` の1行）で、その次の理由は `compiled source changed`（変わった13個のcompiled source）である。npm行の追加前の同日の拒否（`…31476`・`…31491`）は `compiled source changed` だった。旧コマンド・旧binding・旧失敗の原本は変えていない。

検証済み（新しいコマンドの候補）：`verification/loopback1-next/new_candidate.py`（SHA-256 `09ec238a5ee83a566027b4ae871c03a4ab1a08f991d22a01689156817c521a3f`）と `binding-01.json`（SHA-256 `c10d19ebb80ba40f0881aa97930496117c19e64b34b81dcc7bdbf0fb5539a4a3`）を作った。コマンドは次のとおりで、exit 0だった（`verification/loopback1-next/run-1792240798166668000-84752/result.json`、再利用した旧chainは `r05-r11-repair-01/formal-candidate-1792240798811311000-84752/` で `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`）。

```text
/Users/mutoakio/.local/share/mise/installs/python/3.15.0/bin/python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/code-generation/verification/loopback1-next/new_candidate.py
```

旧い検査は写さずにそのまま呼び出し、違いは3点だけにした：(a) 223個のcompiled sourceのうち変わった13個だけを、署名head 1ceae86cの `git cat-file` のblob・作業コピー・bindingの新SHA-256が一致する場合に許し、ほかの210個はbe45と1ceae86cの両方のblobと一致することを要求する（計画は「14個」と書くが列挙は13個で、14個目の変更である新規 `packages/paludarium-wasm/tests/u14-single.mjs` は223個に含まれない）、(b) mise.tomlは署名headのbytes（旧 `physical_config` を通過）に `"npm:npm" = "12.2.0"` の1行だけを足したものを許す、(c) 上の7 runとcommitの署名・親子、性能の原本を束ねる。U14の固定3ファイル（code-summary.md・traceability.json・source-manifest.json）は今のbytesのまま束ねる。旧い検査には、`compatibility.py` が旧consumer-v3へ旧miseを見せたのと同じ方法で、変わった13個（be45のblob）とmise.toml（署名headのblob）だけを読取専用の旧bytesとして見せ、それ以外は物理的に読ませる。拒否の回帰20件（正の対照1件・拒否19件）はすべて期待どおりで、実ファイルは変えていない。詳細と、U11のSafari 2ファイル・U14の記録の更新をbinding fileだけで足す方法は `verification/loopback1-next/README.md` にある。

検証済み（今のsourceとの一致の記述）：この記録の過去の節にある「署名af9b739d・4d52be0aとの一致」「103 claims／108 files」などの照合は、それぞれの時点の履歴であり、今のsourceとの一致を意味しない。たとえばU1のmanifestにある `crates/paludarium-jit/src/lib.rs` は1ceae86cで変わった（`STATE_WORDS`・`STATE_BYTES`・`JitState` の再エクスポートとテストの差し替え、今のSHA-256 `4aedefa3a2ba53b10e180b1184cc2a935c6de34852e27d784f1c7db32a643414`）。今のsourceとの一致は、新しいコマンド（採用後）で確かめる。

検証済み（C9の境界）：`ExecutionBridge`・`JitState`・`STATE_BYTES` は、契約C9の口（`CodeCache::try_run`・`invalidate`）の外にあるU14所有の内部APIであり、その変更はU14の記録で扱う。U1の契約は変わらない。

未検証：新しいコマンドは候補であり、人による採用（Construction Verification Commandの変更）と採用後のcheckpointでの実行はまだである。旧い性能の再利用の検査（runtime JSが保存済み性能のmoduleと同じこと）は論理的な旧bytesに対して通るものであり、1ceae86cの速さは上の性能の原本で別に束ねている。初回crashのcore欠落、U15別配布Wasmの受理（GAP）、歴史jit_compile panic、セッションID保証は解決していない。独立再レビューはこの記録の後に行う。

## 履歴（be45時点）：R05／R11の現在証拠と正式検証コマンドの実行原本（Steps67〜69）

本節は署名be45の時点の記録である。本節の「現source」「現行」はbe45の時点を指し、今のsourceでは `final_candidate.py` はexit 1になる。今のsourceの照合は `verification/loopback1-next/new_candidate.py` が行う（上のStep71・Step72）。

本節は独立レビュー指摘R-05／R-11／R-13を契機とする記録の追記であり、製品source・fixture・CI・guest・source-manifest.jsonは変更していない。旧検証と失敗原本はすべて保持する。

検証済み（R05の工学的原因と修復）：旧記録の「最初のframe crashの原因不明」は、初回job 114563806344のcore／RIP／レジスタが保存されていない歴史的限界として保持する。別途、保存されている同一の旧ELFを独立にGDBで再現し、`leavew`（opcode 66c9）でのSIGSEGVと、16bit BPの+65536 wrapを観測した。修復済みの64KiB整列scratch window（mapped window）と、全7 caller境界×7 forms（nest31を含む）をsourceの exact bytes と算術で検査した。署名be45b36ce9d7a65719ba1f86cf6a0b018070741bのsourceによるfresh native／emulated 200比較と、coverageに収録された実2 ELFは一致した。これは初回coreを回収したという主張ではなく、初回事象のfaultを直接証明したものでもない。工学的原因の説明と修復（R05 engineering defect）と、レビューによる指摘closureは区別し、後者はレビュアーに委ねる。

検証済み（R11の現source照合の範囲）：現sourceの照合は `verification/r05-r11-repair-01/final_candidate.py` が行う。旧strict consumer-v3・canonical・binding・実695.780秒chainの原本は不変のまま保存し、旧rawの純粋再解析と、現source／CIの照合を分離した。拘束した入力は、現owned40・compiled223・署名888／7入力、公式U1 7jobs／11ZIP、現全品質34jobs／32ZIP、versioned guest 3receipt、実11crate／npm tar 7境界である。旧208標準Wasmと現標準Wasmは全bytes fb2fdb…で一致し、U11性能probe f09911…・runtime JS・compiler／build script／flags・製品locksを再照合した。mise設定は署名208fd965のpreview13からpreview15へ変わっている。`compatibility.py` は旧consumer-v3へ歴史的なmise bytesの読取専用viewを与えて旧predicateを再照合するため、`source_compatibility: PASS` は現行preview15設定でのconsumer-v3正式実行を示さず、その実行は未検証のまま保持する。新しい性能測定は実行していない。私有CARGO_HOMEの別U15 moduleへ旧性能を移していない。

検証済み（正式検証コマンドの実行原本、R-13）：人が2026-10-16T12:32:15ZにApproveで採用したConstruction Verification Command（`python3 -B .../r05-r11-repair-01/final_candidate.py`、SHA-256 `d799bbb919f5927304fbb5c5a57e4b3686a52436eaac70cd325ffe981afa9b3e`、固定binding `binding-v4.json` SHA256 `1df659288e5dc8ed7962b6c43dae6df3fbf32779562f34f3caf0e2734891f7d7`）の実行原本は3件である。

- checkpoint verify 43ea67bc-2049-4886-8246-b4167fecfdde（2026-10-16T12:41:42Z、exit 0）：`verification/r05-r11-repair-01/formal-candidate-1792154502657025000-40216/`。`.gitignore` の追加が許容2行（`aidlc/active-memory/`・`aidlc/.aidlc-request-text/`）だけの状態。子4件はすべてexit 0・stderr空。
- Claude Code harness追加で `.gitignore` に3行目 `.claude/settings.local.json` が入った状態（exit 1）：`verification/r05-r11-repair-01/formal-candidate-1792157037871198000-68539/refusal.json`。子0（old_predicates.py）がexit 1、stderrは `compatibility.py` の `ignore has other changes` で停止し、`formal_command_adopted: false`／`new_measurement: false`。失敗原本として保持する。
- 冗長な3行目を削除し許容2行に戻した後（2026-10-16T13:33Z、exit 0）：`verification/r05-r11-repair-01/formal-candidate-1792157659313715000-72179/`。子4件はすべてexit 0・stderr空で、各stdout SHA256は40216と同一。

いずれの `result.json` もstdoutは `source_compatibility: PASS`／`U15_acceptance: GAP`／`unit_completed: false`、`head` はbe45b36ce9d7a65719ba1f86cf6a0b018070741b、`new_measurement: false` である。これらはUnit完了・U15別配布Wasm受理の証拠ではない。

未検証：初回crashのcore欠落は解消していない。現行preview15設定でのconsumer-v3正式実行、U15別配布Wasmの受理、非必須のU14性能、歴史jit_compile panic、セッションID保証はこの記録時点で未解決のまま保持する。独立再レビュー・checkpoint再検証・人の完了承認はこの記録の後に行う。

## 履歴（署名62611f25時点）：必須品質検証の修復（Steps63〜66）

検証済み：HTTP fixtureはファイル読み取り完了後にヘッダーを送信し、読み取り失敗・並行要求・切断の7回帰を追加した。Windowsの親ディレクトリrenameは子handle保持中にerror5、close後に成功することを実機で確認した。この限定条件のfixture競合だけを期限付きで再試行し、永続拒否・非renameのerror5・他エラーを返す境界を保持した。製品の権限エラー変換は変更していない。実機の10必須反復・各1000操作・交換成功・sentinel不変・cleanup・30秒watchdogを維持する。

検証済み：署名62611f2556c4caf1470a7eb4471269d92611db6eのU1 CI38392056273は7ジョブ成功。現行362入力とhello6・差分16・frame200 native/emulator比較、fixed11package11302/12122をstep66-quality-binding.jsonへ結合した。quality CI38392057138は34必須ジョブ成功、追加workflow依存を含む367入力を照合した。ASan38392056163は13対象各601秒・345sourceを照合した。確認補助の全116回帰は成功した。旧107分類・targetは保持し、旧context3件を全文履歴化した。

検証済み：保存済み5ZIPの4環境原本は同一module／guest／fresh native oracleに一致し、各2mode×14caseの出力とfilesystemを既存比較述語で再計算して成功した。Node性能原本はcomplete:true／passed:false、平均interpreter5.48059秒／JIT14.53658秒、p=1である。これは承認済み非必須の性能診断であり、必須guest成功と区別して不合格を保持する。

検証済み：quality初回は33成功・jit_cacheのLLVM鍵取得curl7失敗だった。attempt2のjit_cache新実行115289746913が成功し、成功33jobは実行時刻／steps／原ログbytesを保持してGitHub複製ID対応も明示検査した。旧全canonical単独診断59453はexit0。初回失敗のrun/jobs/logを保持して成功だけに履歴を書き換えていない。

検証済み：正式traceability／required-sections sensorは各exit0／pass:true／findings0（107分類、H2=20）。結果はverification/step66-sensors.json、完全stdoutはtool transcriptに保持した。

検証済み：新全checkerのレビュー前診断85478はexit0で完走し、旧全canonicalと新34必須quality／13sanitizer／原本binding一致を検査した。最終出力は `All thirty-four mandatory quality jobs and unchanged historical predicates passed.`。これは正式な完了確認ではない。

未検証：独立レビュー・新コマンド承認／正式実行・完了承認はこの記録時点で未完了。初回crashの直接core欠落、歴史jit_compile panic、セッションID競合の完全解消は今回の有限合格へ読み替えない。

## 履歴：frame fixture限定修正と証拠分離（Steps55〜62）

検証済み：保存初回ELFをLinuxで独立再実行し、CI38344587478の `step56-linux-gdb-capture/debugger-019.stdout` でRIP4012e0のleavewにSIGSEGV、RBPと正しいframe addressの差65536 bytesを観測した。16bit ENTERがBPだけを更新し、fixtureの旧RBP=RSP+512が64KiB境界を越えたことと整合する。W=2 FRAMEのみ64KiB整列scratch stack中央へ移し、最大N31のchainとLEAVEを同mapped windowへ置いた。元caller RSP／RBP／return addressを復元し、W=8と既存17 FRAME・prefix・XLAT／flags、全比較maskを維持した。製品emulator・AI-DLC本体は変更していない。原因算術と原本hashはverification/step57-frame-cause-proposal.md。

検証済み：署名b623c7ca41ac7296826b171ee0ccc28b3a529ce9、CI38380449349の必要7ジョブ成功。元frameと新7caller境界guestの各100 native／emulator、計200比較が全stdout／stderr／実exit0・各30秒以内で一致。旧GDB startup失敗と旧native SIGSEGVは保持した。固定11package11226/12041=93.231459%、workspace11698/12542=93.270611%、hello6実終了0・diff_u1全16件・関連U2・3OS品質を同じ署名ソースに結合した。verification/step62-execution-binding.jsonの360入力と22原本、5署名commitの親／scope／bytesを監査した。ASan／LSan run38380449276の13対象各601秒と343source・両lock・実compiler／settings／binaryを新規検査し、verification/step62-sanitizer-binding.jsonへ結合した。

検証済み：traceabilityの107分類・targetをcanonical hashで保持し、旧b4ccとb451contextを全文履歴化した。現行b623／CI／binding・sanitizer参照を7回帰で検査。追加publication8拒否回帰も成功。新確認候補 `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-frame-fixed.py` は旧decoder canonical全mainを旧b451 signed viewで実行し、現行には同じ旧executionsを11原本中の明示10artifact投影へ適用、追加frame原本を別厳密検査する。正式実行は独立レビューと別のコマンド承認後であり、診断の実exitを以下に記録する。

検証済み：上記新確認候補のレビュー前全診断は終了コード0（tool session 47012）。旧canonical全検査と現行execution／13 sanitizer検査を完走した。97回帰は成功し、正式required-sections（H2 19件）とtraceability sensorは親担当の実行で双方exit0／PASS／指摘0件。source-manifestは112件・重複0。結果はverification/step62-diagnostic-result.jsonに記録する。独立レビュー・新コマンドの正式承認と実行・完了承認は未完了であり、診断を代用しない。

未検証／未解消：初回クラッシュにはcore／RIPの直接証明がなく、独立再現との関連を初回fault位置の確定へ読み替えない。U14全品質run38380449837のFirefox／SafariはERR_HTTP_HEADERS_SENT、Windowsは既知VFS symlink rename raceで失敗し、原ログをverification/step62-quality-originalsへ保持。U1専用3OS成功をそれらの解消へ代用しない。U14性能、セッションID競合の完全解消は未検証。

## 履歴（2026-10-12時点）：旧JS測定先の再構成（Steps48〜50）

検証済み：正式確認が失敗した直接原因は、旧U12 validatorの固定測定先 `/private/tmp/paludarium-u2-mmu-4608` の消失だった。旧342入力を保存済み署名snapshotと完全hash照合し、検査中だけ同じbytesを同じURL位置に再構成する専用helperを追加した。旧checker・validator・collector・binding・V8原本83 JSON・414snapshotのhashは実行前後で不変。製品・AI-DLC本体・既存CI・閾値・比較条件は変更していない。

検証済み：既存33回帰と新8境界の計41件が成功。新規作成物だけをinode／bytes照合付きで非再帰cleanupし、既存先は完全一致の場合だけ上書きせず利用する。余分・欠落・重複・異なるbytes・symlinkと祖先symlink・排他markerによる同時利用・検査中のsource変更を拒否した。協調する検証間の排他と前後監査であり、任意の悪意ある別processがsystem call間に祖先を交換する競合への完全保証は主張しない。

検証済み：承認済みcommand `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u1-source-bound.py` のレビュー前全診断はexit0。旧Node／collectorと83原本の再集計が旧reportに完全一致し、旧U12全predicateと現行U1の362入力・署名・CI7必要job・hello実終了・coverage検査まで完走した。終了後に再構成先が消去されたことを確認した。command・実exit・捕捉出力・全不変hashはverification/step50-diagnostic-result.jsonとstep50-full-diagnostic.log、説明はstep50-historical-js-reconstruction.md。旧原本の再集計であり、新しいLinux guest実行・新しいcoverage測定とは呼ばない。

未検証：独立review-25のR-05（初回native SIGSEGVの原因）は未確定のまま。R-06のMac上Linux専用diff0件・旧canonical exit1は履歴として保持し、合格へ読み替えていない。今回の正式sensor／独立再レビュー／checkpoint／人の完了承認は親が進める。U13全体と並行session-ID競合の完全解消は未検証。計画・手順・質問ファイルと他Unit成果物を保持し、重い製品試験を追加していない。

## 履歴：R-04実終了証拠修正（2026-10-12、Steps44〜47）

独立review-24のCritical R-04に従い、diff_u1の状態同値性から実exit0を生成する誤りを修正した。旧診断のhello実exit0主張は成立していなかったため、旧原本・旧checker結果をpre-r04-originals/へ保持し、新原本に置き換えた。製品Rust、承認済みplan/instructions/questions、coverage分母・80%・30秒を変更していない。

検証済み：署名e2d3f316206974ef098fd9bdc85d94a8376a51f8はGitHub Verified、親17231f7a…、新差分workflow1pathだけ。現行362入力を同署名へ結合。run38171135965はattempt2 success、API全14job recordを保存した。成功6はattempt1実行のsteps／開始終了／statusを同一のattempt2 carry recordへ結合し、新規再実行と数えない。coverageだけattempt1 failure114563806344→attempt2 success114564941865で再実行。全12 ZIP digestを検査し、採用10種類は対応success jobのhead／時刻／入力／compiler／内容へ結合、非採用2ZIPは合格根拠へ混ぜない。

検証済み：同job fresh CLI/guestのhello3×native/emulator6操作は実returncode0・signalなし・timeoutなし、stdout/stderr原bytes一致、最大0.008367425秒。16差分の32時間は最大4.438712208秒だが、終了状態は同値性のみで、他13件の具体的exit値は主張しない。固定11package／42files coverageは10193/10974行=92.8832%、workspaceは10668/11475行=92.9673%。実compiler6f5da406b／LLVM23.1.3を同原本から照合。既存18＋R-04拒否7＋attempt結合8の33回帰が成功（0.026秒）。詳細と原本はverification/r04-exit-evidence-repair.md、current-source-bound-results.md、current-u1-originals-manifest.json、current-u1-observation-binding.json。

検証済み：R-04修正後の全checker診断は歴史全predicateから現行362入力・実hello6・API14record・全12 ZIPまで最後まで成功しexit0。完全stdout／command／exitはverification/current-u1-full-diagnostic.{json,log}、33回帰rawはcurrent-r04-regressions.log。record内4コードの最終hashとレビュー対象一覧はreview-record-files.md。source-manifest104claims／traceability107IDの意味論を保持して成果物を確定した。

未解消：coverage初回のu2_frame_forms native SIGSEGVは原本を保持した。同じELF/hash/compilerと同EPYC9V74/family25で再試行は成功したが、fault位置と不定性の原因は未確定。skip/mask/分母変更で隠していない。正式再sensor／独立再レビュー／最終確認・完了承認は親が進める。U13全体、現行本番wasm4環境／ASan新規実行、ID競合の完全解消は未検証。

## 履歴：R-04修正前の分離診断（hello実exit0主張は反証済み）

検証済み：旧U12の342署名入力と現行Host2ファイルが一致しない原因を確定し、旧342＋支援72の歴史snapshotと現行U1実測を分離するcheckerを作成した。旧checker／全predicate／製品コードは変更していない。現行362入力（旧U13の361＋新workflow1）は最終署名HEAD `17231f7a0cdfe9da8659497d963979690db1c2b3` と全件一致する。GitHub Verified、親3817231637d289f670884f0df50ea98caf56c287、最終差分workflow1path、fc44からの累積差分は承認済み3pathである。

検証済み：CI38169414877の7必須ジョブ成功、Linux hello3＋diff_u1全16件（ignored/failed/filtered各0）、全32 native/emulator時間は30秒以内（最大4.069583253秒）。固定11package／42filesのcoverageは10196/10974行=92.9105%、workspaceは10668/11475行=92.9673%。実compiler6f5da406b／LLVM23.1.3。source receipts7・coverage・U3 observationsの計9原ZIPはAPI digest完全一致、展開inventory／bytesも原本と照合した。18不正証拠拒否回帰はexit0（0.015秒）。実コマンド・観測binding・測定分母・原本は verification/current-source-bound-results.md と current-u1-{ci,ci-artifacts,originals-manifest.json,observation-binding.json} に保存した。

初回CI38169187513のWindows checkout CRLF不一致と中間CI38169390895は履歴として保存し、合格へ流用しない。checkoutだけをcore.autocrlf=falseへ修正し、最終HEAD／最終runで全7ジョブを再検証した。正式sensor／独立レビュー／正式最終確認／完了承認はこの文書だけでは未完了。U13全体の完成、現行本番wasm4環境／ASanの新規実行、ID競合の完全解消も今回の有限U1検証からは主張しない。

## 履歴：Testing Contract復旧後の限定確認（2026-10-11）

今回の内容確認は `current-contract-recovery-questions.md`、確認識別子は `fcb92ab1e0227f810293c39d1ffba06cd1a5b1db07ff10b80587364641428142`。公式briefのContract `7ff27a240f8283092b490270c3b4f352c35a5c72585e09c8b98a2db75be446d5` に従い、承認済み計画・検査手順と製品ソースを保持した。親が正式sensor・独立レビュー・checkpointを担当する。

検証済み：署名済みU10 head `cb9797138313046b3cf9bbbfcab0515910b81215`／CI38095031011の保存証拠に対し、現在326入力は326/326一致・欠落0・差分0。17manifest・1674rawの全SHA256と実ファイル集合も一致、監査exit0。spikeのpackage/lockはこの326集合に含まれないため別に確認した。U1の103claimsを108filesへ展開した旧7ebとの比較は100一致・8差分であり、旧Step45の108一致を現在の主張としない。全行と現在hashは `verification/current-contract-recovery-audit.json`。

検証済み（限定再利用）：U1 native hello3件・diff_u1の16件・U1対象42filesの10206/10972行=93.0186%は署名head4a27bc2644f5／CI38056188441の保存実測。実compilerは現在と同じrustc32dba69d／LLVM23.1.3である。変更済みtest/configは既存承認済みcanonicalの限定bindingで扱い、旧294入力が現在全部一致したとは呼ばない。現在326入力とU10の有限品質実測を照合したが、この監査でLinux hello・coverageを新規実行したものではない。80%下限・30秒・既存maskを保持する。

検証済み（今回新規spike実行）：Playwright1.64.0のpackage/lockはバージョン・resolved・integrityと対応する依存版のみの変更で、他のJSON意味とpackage集合を保持した。実インストールも1.64.0。現行nightly10-10の実cargo/rustc/rustdocで既存build.shはexit0、新spike module SHA256は `a6a02f2d1190c597eb9288da022d44e1d1975af6530b611516f59fd048330e8c`。Node26.11.1と本物Safari27.0.1は同moduleで各exit0、値42、wait201ms、全処理213/241ms、crossOriginIsolated=true。Safari外側4.371秒、driver残存0、4444/8787閉鎖を確認した。rawは `verification/current-contract-recovery-raw.md`。standalone wait/notifyの有限観測であり、本番launcher・guest clone/futexの完成を意味しない。

未検証：更新後PlaywrightでのChromium/Firefox新実行、今回の正式レビュー・checkpoint・次Unit遷移と並行セッションID競合の完全解消。generated production wasm81571ee6…はU1 manifestの所有対象外であり、このspike結果をそのmoduleへ転用しない。既存canonicalは変更せず、developerは実行していない。

## 履歴：Step45のソース照合（2026-10-10）

今回の内容確認は専用の `code-generation-summary-questions.md` に記録した。確認の識別子は `647ce2ac0a418262174cc3322a192b4051ac5938fa2dc1cb2eec562aa4411aa4`。承認済みの計画・Testing Contract・検査手順を保持し、製品ソースを変更していない。

検証済み：U1 source-manifestの103claimsを108filesへ展開し、各ファイルの現在bytesを署名済みCIの基準 `7eb1819f52acede33e83775374dd4ee93edf643b` の `git show <SHA>:<path>` 出力と比較した。108/108一致、不一致0、比較コマンドexit 0。比較結果の詳細は `verification/step45-current-reconciliation.json`。これは保存済み製品と現在bytesの照合であり、新しい製品テストの実行ではない。後続Unitの独立ファイルや未検証動作へ一致の主張を広げない。

検証済み（親のCLI観測）：専用内容確認への `log answer` と `testing-posture brief --unit u1-skeleton` はexit 0。今回の経路では計画承認の再要求はまだ観測していない。`aidlc doctor --verbose` はruntime 2.11.0、0 problems/3 warnings、exit 0。以前のhooks失敗記録が残っており、この診断の成功だけで停止原因の解消とは判断しない。

未検証：正式レビュー結果の記録、checkpoint検証・人の完了承認・次Unitへの遷移、および並行セッションでのID競合の完全解消。これらの停止検証は親が標準CLIで継続する。80%のカバレッジ下限、30秒制限、strict guard、既存の比較対象を維持する。既存の成功・失敗・未検証記録は下記の履歴として保持し、今回の新実行へ読み替えない。

## 履歴：Step38〜40の担当説明修正（178da99e）

今回Summary Confirmation `01e6d98e3147d0b715a7b5f4045ee7fce1deb952f9cba824b09f6f8f9bf89228`後、FR5.4のDeferredを保持し、notesの担当へU5を追加した。共有unit-of-work.mdのU5はゲストのnative thread割当、U11はwasm Host/LauncherのWorker割当、U12/U13はmacOS/Windows backendである。C2の共有Host traitとBR6.1を維持する。107 coverage行中、他106行とupstream_idsは同一であり、verification/step38-traceability-preservation.jsonにbefore/after hashと検査を保存した。製品ソースは変更していない。

検証済み：承認済みcanonical `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。署名済み178da99e88d1aea242c5141207887767a69fa670と現行186 tracked application filesのbytesを照合し、厳密hashで確認したSafari報告の文書例外だけを区別した。CI37745425190の8jobs、sanitizer37745425204の4jobs、native37745425183の2jobsを同じSHAとして確認した。stdout/stderr/exitはverification/step39-native-ci.jsonとstep39-native-ci.logに保存した。保存済みCI証拠の再確認であり、この文書修正で製品テストを再実行したものではない。

検証済み：共有ソースの最新証拠はU2 verification/step47-proof.jsonとstep47-ci-metadata.jsonである。native3OS、lint/依存、全体92.68%・U1対象packages83.04%の両80%gateを保持する。U2が取得したproduction wasm Node/実Safari14ケース、共有Rust heap・nested Workers、およびCPU/MMU/decode/load_elf各601秒ASan+LSanは、その限定観測として参照しU1新規実装とは数えない。guest clone/futex全体、任意guest・任意入力の完全保証、JIT、Chromium/Firefox今回再検証、U1 mmu_ops/syscall_argsの現在600秒ASanは未検証。夜間scheduled run実行とは呼ばない。30秒watchdog・nightly-2026-10-01・各600秒・比較mask・両フックを保持する。

検証済み：限定sensorの実コマンド・stdout/stderr・exit・passはverification/step39-sensors.jsonへ保存した。traceabilityとrequired-sectionsは両方exit0/pass:true/findings0（107対応、H2=11）である。Step40の独立レビューと正式完了確認は親担当であり、この記録で完了済みとはしない。U4/U9の指摘もそれぞれのUnitで扱う。

## 履歴：以下はStep1〜37当時の記録

以下の旧「現在」「今回」「未完了」「未検証」は各記録時点の観測であり、178da99eの現在bytesへの主張ではない。4d52/af9bのCI件数・source比較・旧Safari未検証状態を現行結果へ転用しない。今回の現在値は上のStep38〜40とstep39証拠で確認する。

## 履歴af9b：Step32〜34の記録確認

検証済み：現在sourceを署名済みaf9b739d742a9552f44fc1515646c862b19e5de2とread-only `git show <SHA>:<path>`で全bytes比較した。103claims/108files中107一致、別作業の非ビルド設定.gitignoreのみ既知例外。source-bytes-af9b739d-current.jsonが今回snapshotであり、source-bytes-current.jsonは4d52時点の履歴である。47上流/47対応、OK target欠落0、claims/schema変更なし。

検証済み：CI37713953347の7jobsとnative37713953340の4jobsは成功。canonical intent直下verification/verify-native-ci.pyはexit0、全162 application filesと署名済みCIを照合した。verification/ci-native-bookworm.log:525〜527のhello_c/hello_rs/引数付きhello_rs、542行のU1差分16passを確認。verification/ci-coverage.log:2340の全体7155行/未実行524=92.68%、2802行のU1対象11packages6905行/未実行1171=83.04%で両80%gate成功。共有crate内の後続実装を含む分母でありU1初期実装だけのcoverageではない。rawログは同af9bのU9採取ログをrootがU1 verificationへコピーしたもの。CI再利用であり今回新テスト実行とは数えない。

今回Summary Confirmation fab469c065d27f9eb3044809b71af14d9a69fc11740b1148c7016f4936f3b13e後（2026-10-08T02:35:31Z以降）に4producesとmanifestを保存した。テスト手順のStep29〜31と旧4d52確認説明を履歴として明記し、今回Step32〜34の再照合を追記した。製品・CI変更なし。wasm/Safari、U1各targetの現在600秒ASanは未検証のまま。80%/30秒/nightly2026-10-01/600秒/masks/Docker VMM/2フックを保持し、rootの日記完了後、独立レビュー依頼からterminalまで全書込を固定する。

Step32〜34時点（履歴）のrequired-sectionsはPASS/H2=7。traceability sensorはFAIL：既存47IDsのtarget/entry不正0、全requirements fallbackに対するFR/NFR60IDs不足を報告。承認済み47IDsを自動拡張せず未解決結果として引き渡す。実コマンドとJSONはverification/step34-sensors.json。sensor exit0はPASSの意味ではない。

旧source-bytes-current.jsonは4d52時点の履歴であり、現行sourceに対して8claimed filesが異なるという先行レビュー指摘を保持する。現行一致の根拠は今回更新したsource-bytes-af9b739d-current.jsonで、旧snapshotの一致は現在の合格根拠としない。

## 履歴：Jump redo後のStep29〜31確認（4d52時点）

検証済み：verification/u1-redo-brief.txt全文、新Summary Confirmation/UNIT_STARTED後に103claims/108filesを現在snapshotと照合し差異0。read-only git show4d52be0a比較は107files一致、別作業.gitignoreのみ例外。manifest SHA256=33595e7b79804895bc9b311c346b6427d0ed958a278c8ce3643727a3bd363f71、47上流/47対応・OK target欠落0。保存CI11jobs、hello world/U1差分16、全体92.57%/U1対象82.71%は同じ製品bytesの既存証拠を再利用し、新実行と数えない。

今回の内容確認後に実際のproducesである計画・テスト手順・本summary・traceabilityを保存し、source-manifestも保存した。claims/schemaは保持。製品変更・追加testsなし。旧fuzz/wasm/Safari未検証、80%/30秒/nightly/各600秒/masksを保持する。親diaryを依頼前に完了し、引渡し後は全書込とSCM snapshotを停止する。レビュー不整合原因は未確定。

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

## 履歴：最終修復後の検証（4d52時点）

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

## 履歴：Step26〜28の記録再確認（4d52時点）

検証済み：新attemptのPlan Approval/内容確認後、103claimsを108filesへ展開しread-only `git show 4d52be0a:<path>`とSHA256で照合した。107files一致、`.gitignore`のみ別作業の保持済み設定変更として相違。現在snapshot108filesは全一致し、manifest所有範囲は追加していない。詳細はverification/rereview-source-4d52be0a.json。`.gitignore`変更の動作検証を旧CI成功とは呼ばない。

保存済みCI7+native4jobsと同じ製品bytesを再利用し、新規テスト実行として数えない。Bookworm raw524〜526行のhello_c/hello_rs/引数付きhello_rs、541行のU1差分16pass、coverage raw2187/2617行の92.57%/82.71%を確認した。上流47件/対応47件、OK target欠落0、source欠落0。新製品不具合・追加test必要性は見つからず製品修正なし。

wasm/Safari・U1各targetの現在600秒ASanは未検証のまま。traceabilityのOKは実装・設定・報告の対応であり未測定項目の合格を意味しない。30秒watchdog・nightly2026-10-01・各600秒・両coverage80%を保持。2フックはrootが有効性を確認し、今回rejected reportの原因を特定したとは主張しない。日記をレビュー依頼前に確定し、以後はrootの独立レビュー記録までsource/成果物/SCM snapshot操作を停止する。

## 履歴（署名b4cc2381時点）：Steps51〜54：U14共有変更後の確認更新

検証済み：追加18境界＋workflow closure6回帰と既存33＋8回帰の計65件はPython3.15.0で成功。旧362入力のU1全mainと旧361入力のU13全mainは、それぞれ署名歴史viewで述語を保持して診断exit0となった。旧U13が参照するU11検査・分母原本・collectorの3支援記録を別SHAで固定し、旧collectorは元の測定bindingとも照合した。これは履歴の再確認であり、現行製品の新測定ではない。

検証済み：凍結39ファイルの署名922e、書式2ファイルのみの署名0ebを別manifestで監査した。2ファイルは非空白bytes不変。同じ製品の診断workflowだけを署名f518→796→b4ccで追加・整合し、各親・Verified・正確な1ファイル差分を確認した。初回dispatch404とNode前提不足による3OSの実wasm5テスト失敗原本を保持する。Node26.11.1と既存U14のactionSHAを同workflowへ揃え、製品・lockは変更していない。

検証済み：署名b4cc2381のCI38314464997は全7ジョブ成功。10 archive・7ログ・4 API JSONを原本として保存し、署名・head・必須step・時系列・digestを照合した。現行実dependency closureは355入力で、全signed／local hashが一致する。実行workflowのlocal reusable参照を再帰収集し、local actionは存在しない。非参照の旧workflow5件はsigned／local hashと理由をu14-current-source-audit.jsonへ保持し、歴史viewの検査から除外していない。

検証済み：旧executionsの全述語で新原本を検査し、hello3件×native／emulatorの6操作は実returncode0・signalなし・timeoutなし・stdout／stderr一致。diff_u1全16件、固定11packageは11209/12024行=93.22188955422487%、workspaceは11681/12525行=93.26147704590818%。実compiler・guest・両lock・分母を原本へ結合した。実測bindingはu14-current-u1-execution-binding.json、21原本のhashはu14-current-originals-manifest.jsonに保存した。原本manifest guardを含む旧全main＋新main診断もexit0、出力はu14-current-final-full-diagnostic.logに保存した。

検証済み（有限観測の結合）：全CI38290361104内の13 sanitizerジョブは成功し、各原ZIPのAPI digest・job／step／head／時系列、338 sourceの前後不変と0eb／b4cc／手元一致、両lock、実compiler6f5da406b、binary hash、ASan／LSan・seed1・timeout30・rss2048・各最大入力、非zero runsと各601秒を照合した。結果はu14-current-sanitizer-binding.json、13 ZIP原本はu14-current-sanitizer-originals-38290361104。旧11対象の歴史成功へ追加対象を推定していない。新sanitizer述語と既知失敗receiptを統合した最終全診断は実行中。正式コマンド承認・独立レビュー・完了承認は未完了。

U14の性能要件未達、Firefox／本物SafariのERR_HTTP_HEADERS_SENT失敗、初回native SIGSEGVの原因不明、Windows raceとセッションID競合の完全解消未検証を保持する。今回のU1確認をU14完成証明へ流用しない。

未解消の新規不具合：同署名0ebのstandalone run38290360670はjit_compileが失敗した。保存原本はiced-x86 1.21.0 decoder.rs:1421の減算overflow panic、libFuzzer deadly signal、target exit77／wrapper exit1を示す。32byteのcrash-b2871010e28147fb3fc96a68c88219a2c1d6b08bを含む原ZIPとjob114948701092ログを保存した。再現入口は`cargo fuzz run jit_compile fuzz/artifacts/jit_compile/crash-b2871010e28147fb3fc96a68c88219a2c1d6b08b`。別の同head全CIの13対象成功は有限の別観測であり、この失敗の解消やR07全解消を意味しない。製品修正・再現実行は今回未実施。

## 承認済みデコーダ限定修正後のU1原本照合

検証済み：人が承認したdecoder lib.rs一ファイルの署名付き公開をeecb641cで実施し、再現入力の転記誤りを同ファイルのテストだけで訂正したb45158d3へ更新した。両公開はGitHub Verified/valid、親と一ファイル差分を照合済み。訂正コミットの製品部分は親とbytes完全一致。初回入力誤りとCIを履歴として保持する。製品修正は最大15バイトを16バイト整列バッファにコピーしてiced-x86へ渡す処理で、overflow検査を無効化していない。

検証済み：訂正後decoder31件・JIT39件、既存source-bound57件・historical JS8件・追加publication/checker9件が成功。`u14_publication_audit.validate`は実GitHub署名・親・path・bytes監査でexit0。

検証済み：修正後署名b45158d3のCI38319817485は全7ジョブ成功。`u14_current_originals.bind`で355実行依存入力のsigned/local一致と旧executions全述語を確認した。hello native/emulator6操作の実終了0・stdout/stderr一致、差分16件、固定11package11226/12041行=93.23145918113113%を確認。原本21件は別manifest `u14-decoder-originals-manifest.json`、bindingは `u14-decoder-u1-execution-binding.json`。旧原本・checker・閾値は保持する。

検証済み：署名b45158d3のstandalone CI38319817478の13対象はすべて成功。`sanitizer_originals`で13原ZIPのdigest・署名head・job時系列・338 sourceの実行前後と現行一致、両lock・compiler・binary hash・入力上限を照合し、全対象601秒・実終了0を確認した。MMU最大4608バイト、jit_compile最大968バイト、jit_cache最大2048バイト、timeout30とASan/LSanを維持。bindingは `u14-decoder-sanitizer-binding.json`。jit_compileは53905185 runs、decodeは111995295 runsの有限観測である。旧失敗原本を変更していない。

検証済み：新確認スクリプト `verification/verify-current-u1-u14-decoder-fixed.py` のレビュー前診断はexit0。旧U1/U13全検査と参照するU10/U11/U12検査を保持し、現行355入力・hello実終了・固定coverageと13 sanitizer原本の述語まで通過した。診断receiptは `u14-decoder-full-diagnostic.json`。正式文書検査のrequired-sectionsとtraceabilityも今回passed。診断を正式コマンド承認後の完了確認へ代用しない。

未検証：新コマンドの正式承認と独立した確認。ホストメモリを4GiB境界へ直接配置する再現と任意入力の完全保証は未検証。現行品質CI38319817919ではFirefoxと本物Safariのジョブが失敗し、U14性能要件も未達。Safariログはu14-check.mjs:56のERR_HTTP_HEADERS_SENTを示す。初回native SIGSEGV原因・ID競合の完全解消を今回のU1原本照合で解消済みとしない。

## Step35：共有要件の担当分類

今回Summary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、既存47BR/詳細NFRの行・status・targetを保持し、要件fallback60FR/NFRを追加して107IDs/107対応へ更新した。U1範囲は実在source/test/configへOK、後続完全機能と未検証fuzzはDeferred、集約見出しと資源上限非適用は理由付きN/A。後続Unit実装をU1成果へ転用しない。CIの証拠名を実在ci-jobs-37713953347.json/ci-jobs-37713953340.jsonへ修正した。検査結果はverification/step35-traceability.json。旧Step34のFAILは履歴として保持する。

## Step36〜37：実Safariと文書差分の確認

今回Summary Confirmation 5d6a234e978c037dea4f9350ef1c6939e48984d02f8f3b33939f34a2fcf845f5後、検証済み：本物のSafari 27.0.1/macOS 27.0.1 build26A434、固定nightly-2026-10-01で単独wasm spikeがexit0。crossOriginIsolated=true、waitNotifyPassed=true、wait result0、value42、waited201ms、notify woke1、total216ms（5秒以内）。verification/safari-local-20261008-pass.jsonが生結果。Remote Automationによる初回blockedログを保持し、夜間CIの実行結果と区別する。Node/Chromium/Firefoxは過去の結果で今回再実行ではない。U1各fuzz現行600秒ASan、共有stdヒープ、入れ子Worker、エミュレータ全体のSafari動作は未検証。

検証済み：verification/step37-application-bytes.jsonで署名済みaf9bと全162 application filesを再比較し160一致。差分は既知非ビルド.gitignoreと承認対象docs/reports/wasm-threads.mdのみ。runtime/source/test/build/CI bytesは不変。旧Step32の全一致はSafari報告更新前の履歴である。U1既存103claims・Safari報告claimを保持した。

未完了：canonical verification/verify-native-ci.pyはexit1、Current source differs from tested commit: docs/reports/wasm-threads.md。stdoutのCI7jobs/native4jobs成功と現在sourceの全一致を混同しない。verification/step37-native-ci.logへ保存。検証器・除外条件・CIを変更せず、Safari報告を戻さず、親担当へこの拒否を引き渡す。Step37の正式検証・独立レビュー・完了確認は未完了。

検証済み：人が選択した完了検査 `python3 -B aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-native-ci-with-safari-report.py` はexit0。元のverify-native-ci.pyは保持し、署名済みCIと異なるSafari文書・実測証拠の厳密hash対応だけを新検査で確認した。CI7jobs/native4jobs成功、全162 tracked application filesをaf9bへ照合し、既知.gitignoreと承認済みSafari報告以外の差分を認めない。実行ログはverification/step37-approved-native-ci.log。元の検査exit1は履歴であり、今回選択済み検査の成功と区別する。独立レビュー・Unit完了確認は引き続き未完了。
