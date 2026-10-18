# U3 SSE系命令のコード生成計画

## Summary

- Builds: 今回の計画（Build and TestのLoop-back 1）。製品は変えない。計画の古くなったTesting Contractを今の内容（`sha256:7ff27a24…`、方針は同じでproject層の学びが足されただけ）に置き換え、今の正式確認コマンドでU3を確かめ直す。
- Touches: この計画のTesting Contractと「今回の計画」の節だけ。製品・テスト・ほかの記録は変えない。
- Tests: 新しいテストの実行はない。独立再レビューと、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpoint。前回までの結果は履歴として保持する。

## 今回の計画：Testing Contractの更新と再確認（Build and TestのLoop-back 1）

2026-10-17。U14の整数SSEのJIT（署名head 1ceae86c）とU1・U2の正式確認の更新の途中で、記録の誤り（Code Generationの段階全体へのRequest Changes）のため、各Unitを順に確かめ直している。U3の担当のsource-manifestには、今回変わったファイル（U14のJIT・wasm・テスト、`crates/paludarium-wasm/src/abi.rs`、`mise.toml`）は含まれない。この計画の「## Testing Contract」は、memory（project.mdの学び）の更新で古くなっていたため、`aidlc engine testing-posture render` の出力に置き換えた。テストの方針（Methodology custom、Ordering、Standard、80%下限など）は変わらない。

- [ ] 製品・テスト・記録は変えない。今の正式確認コマンドでU3のcheckpointを確かめる。独立再レビューで、U3の記録が今のsourceと合っていることを確かめる。前回までの結果は履歴として保持し、今回の新しい実行とは数えない（NFR3、NFR9）。

## 前回のSummary

- Builds: 既存SSE実装を保持し、共有mtime変更とRust版統一後のU3ソース・命令対応・検証証拠を再確認する。
- Touches: U3の計画・検査手順・summary・traceability・manifest・検証記録。製品不一致は具体的な最小修正案として提示する。
- Tests: 独立U3 native matrixと共有CPU/Decoder coverage80%、差分・3OS・wasm/本物Safari・ASanの保存証拠を対象別に照合し、不足を未検証として報告する。

## 今回の再確認：Steps25〜27

## 承認された追加検証：Steps28〜30

- [ ] Step 28: 製品を変更せず同一現行ソース・両lock・最新公式確認版を固定した隔離署名CIで、Linux native正常23576/fault1162/CPUID12を毎回生成する。各30秒process-group kill/reap・欠落/unknown profile拒否を維持する。fresh入力を供給した独立U3 matrix CPU40/Decoder12（ignored0）とLinux diff_u3、同入力を使う3OSのU3限定テストを実行し、全入力before/after/current・raw実exit・署名Verifiedを保存する。（FR1.2/1.4/1.6/9.1、NFR1/7〜9）
- [ ] Step 29: 独立matrixと別に空profilesから同CPU/Decoder9ファイルの共有library coverage80%以上を測定し、LF/LH・JSON・LCOV・consoleを照合する。cpu_u2/mmu_u2/decodeだけをASan/LSan各600秒以上、seed1・timeout30・rss2048・detect_leaks1・既存suppressionで実行する。U9新ASan4対象とNode/本物Safari20内のU3関連7ケースは、依存ソース・両lock・実compiler・設定が一致する範囲だけ再利用し、新規実行と称さない。閾値・測定対象・比較maskを維持し失敗を成功へ読み替えない。（NFR1〜3/7〜9）
- [ ] Step 30: 新実測と旧失敗・旧時点の証拠を区別し、4成果物・命令対応・manifestを更新する。正式検査と独立レビュー前に全書込みを停止する。U3新証拠を検査する最終確認候補を具体化し、人の別承認前に実行しない。strict guardを維持し、未検証の端末動作・全入力・セッションID競合の完全解消を主張しない。（全割当FR/NFR）

## 先に承認された照合手順

- [ ] Step 25: 既存U3実装、136担当行と568対応変種・補助9変種、固定probe/aubeと比較契約を確認する。現行ソース・両lock・実使用Rustと保存CI/coverage/native matrix/production wasm/ASanを対象ごとの依存範囲で照合する。mtime変更とRust版統一の不一致を分類し、旧成功を現行実行として扱わない。旧Steps1〜24の実装や重い検証を反復しない。（FR1.2/1.4/1.6/9.1、NFR1〜3/7〜9）
- [ ] Step 26: U3限定内部・Decoder境界・native差分入口とケース数を確認し、保存済み同source実測を再利用できる範囲を記録する。native入力欠落・0件・skipを成功扱いしない。共有CPU/Decoder9ファイルcoverage80%と独立U3 matrixを区別し、不足するLinux差分・coverage・wasm/本物Safari・ASanは具体的な追加検証案として提示する。最新ツールを区切りで確認し、strict guard、30秒制限、比較mask、測定対象を維持する。（FR9.1、NFR1〜3/7〜9）
- [ ] Step 27: 旧履歴と今回の結果を区別して4成果物・命令対応・manifestを整合し、正式検査と独立レビューへ渡す前に全書込みを停止する。承認済み最終確認コマンドがU3を十分検査しない場合は補足候補を具体化し、新コマンドは人の別承認前に実行しない。完了承認と次Unitへの遷移を確認し、ID競合の完全解消は未観測範囲へ一般化しない。（全割当FR/NFR）

## Sources
- FR1.2/FR1.4/FR1.6、FR9.1、NFR1〜3/7〜9: inception/requirements-analysis/requirements.md。
- U3: inception/units-generation/unit-of-work.md。probeとaubeが使うSSE系、AVX/AVX-512は対象外。
- C3/C5、公開型と層の境界: inception/contract-design/contract-summary.md。
- Cpu/Decoder/Harness: inception/domain-design/components.md。
- 検証済みの現状: CpuStateはXMM16本/MXCSRを持つ。既存SSEはmovaps/movups/movdqa/movdqu/movq/punpcklqdq/pxor/xorpsに限定。scalar movsdは文字列命令との識別が必要。

## Scope and completion
U3はSSE命令のデコードと意味論をCpu/Decoderへ追加する。probe/aubeの全機能合格はU10以降の担当だが、対象バイナリのSSE使用命令は棚卸ししU3の実装・差分テストへ対応付ける。静的出現と動的実行観測を区別する。対象バイナリが入手/ビルドできない、観測が他Unitの未実装機能で止まる場合、FR1.4全量達成を主張せず不足を明示し、人へ範囲判断を戻す。既存8命令だけで完了と扱わない。
整数SSE（packed加減算/飽和/比較/論理/shift/pack/unpack/shuffle/mask/extract/insert）、移動、scalar/packed浮動小数点演算・比較・変換・MXCSR操作を棚卸しの対象とする。命令形式、メモリ幅、alignment、upper lane、immediate、RFLAGS/MXCSR、fault時の状態更新をケースごとに扱う。浮動小数点をホストのf32/f64計算だけで近似して合格扱いしない。丸め4方式、NaN/Inf/±0/subnormal、DAZ/FTZ、例外mask/statusをネイティブと照合し、必要なsoftware演算を安全なRustで実装する。非mask例外は既存typed fault/signal境界へ整合させる。
公開API・U1/U2/U4/U7/U9の意味論を維持する。新依存は原則不要、必要ならcrates.io・Apache-2.0互換を確認し計画変更の承認を得る。JIT/AVX/後続syscallを実装しない。
人の追加scope選択に基づきSHA256RNDS2/MSG1/MSG2、AESENC/AESENCLAST、PCLMULQDQ selector00/11とCPUIDの仮想CPU契約を含む。詳細はverification/u3-cpuid-crypto-contract.md。host CPUIDを転送せず、未実装familyを広告しない。暗号7形式の実装だけでAES/SHA/PCLMUL feature全体の広告条件を満たしたとは扱わない。familyを完成させる追加命令が必要なら具体範囲判断を返す。

## Ordered implementation steps
- [ ] Step 1: U3のrunner/configを準備する。CPU u3_tests、Decoder u3_tests、Harness diff_u3、tests/guests/u3/build.shの実行入口を作り、単位別コマンドが実行可能なことを確認する（FR9.1/NFR9）。製品意味論をまだ追加しない。
- [ ] Step 2: probe/aubeの固定対象と既存static-muslゲストを棚卸し、SSE/追加暗号7形式/CPUID契約・encoding・operand形・未定義/実装依存の比較除外表を作る。probeは人が選択した8source/29916d90 targetを保持する。aubeは固定1,362source/lock/元builder、build date2026-10-05、空primer mtime1791158400で同条件の独立double buildを行いexact binary SHA一致とsource前後不変を要求する。binary・mtime・wrapper実呼出・compiler・全環境をimmutable receipt/artifactへ保存し旧ff54/5a/781fを履歴保持。有限DBI block観測と保守的静的候補を対応付け、全入力保証やchild Node coverageへ拡張しない（FR1.4/NFR1）。網羅性/追加family広告が確定しない場合は実装前に人へ具体判断を戻す。
- [ ] Step 3: 各対象命令と追加暗号7形式/CPUIDの差分C/assemblyケースを先に作成し、fork CIのx86-64 LinuxでネイティブのXMM/GPR/定義済みRFLAGS/MXCSR/メモリ/終了結果を毎CI生成・保存する。nativeが対象feature非対応なら未検証で停止しskip合格にしない。CPUIDはhost依存identity/feature値を比較mask根拠表で区別し、仮想CPU出力は独立した契約定数へassertする。expected値をリポジトリへ固定しない。初回はnative観測だけ、未対応emulator結果を別記録する（FR1.4/FR9.1/NFR1）。
- [ ] Step 4: DecoderのSSE/追加暗号/CPUID mnemonicとoperand情報を拡張し、scalar MOVSDとstring MOVSDを区別する。legacy形式検査を保持しVEX SIMD/EVEXはUnsupportedにする。暗号prefix/opcode/ModRM/REX/selectorとCPUID0f a2を識別する。接続後に5〜8件以上の境界・不正・切断encoding単体ケースを実行する（FR1.2/FR1.6/NFR2）。
- [ ] Step 5: 移動・整数packed処理、暗号7形式、明示CPUID契約をCpuの安全なRustモジュールで実装する。暗号はportable整数/byte演算で新production依存を追加しない。CPUIDはvendor/maxleaf/subleaf/reserved bitsとfeature family gatingを固定し、未実装AVX/EVEX/x87/MMX/XSAVE/OSXSAVEを広告しない。XGETBVはUnsupportedを維持し隠れたAVX stateを実装しない。命令ごとにStep 3のnative結果へ一致させ、XMM8〜15、implicitXMM0/alias、即値境界、飽和、shift大値、unaligned/跨ページ/権限faultを単体・差分テストで確認する（FR1.4/NFR1〜3）。
- [ ] Step 6: 対象の浮動小数点・比較・変換・MXCSRを実装し、全rounding modeとNaN/Inf/zero/subnormal/DAZ/FTZ/例外をnative差分で確認する。fault/例外でpartial state更新しない。CPU各処理群5〜8件以上の単体ケースを追加する（FR1.4/NFR1〜3）。
- [ ] Step 7: Harnessでnative結果とemulatorを毎CI比較する。正常・alignment fault・ページfault・無効MXCSR・unsupported AVXを含め、signal/RIP/比較maskの根拠を記録する。命令inventoryの全assigned行に実装と差分ケースを対応付ける（FR1.6/FR9.1/NFR1）。
- [ ] Step 8: 既存CIへdiff_u3とU3測定を組込み、3OS単体、fmt/clippy警告0、依存検査、native差分、Linux行coverage80%以上を通す。CPU/Decoder変更のwasm32 buildと本番wasmをCI artifactからNode/実Safariで確認する。CPU/decode fuzzを現行sourceでASan+LSan各600秒以上実行し、source前後hashを保存する。時間切れを緩和しない（NFR2〜3/7〜9）。
- [ ] Step 9: README/API説明、比較除外/支持命令表、unit-test-instructions、code-summary、source-manifest、全assigned要件traceを更新する。後続Unit依存はDeferred/N/A/未検証理由を区別し、他Unitの成果物は維持する（FR1.4/NFR1）。
- [ ] Step 10: 限定sensorと独立レビューを実行し、現行署名付きCI source・artifact・全ログの整合性を確認する。共有source変更による先行Unitの完了確認は成果物を維持して更新する。新しい完了確認コマンドが必要なら内容を用意して人の承認を得る。正式検証とU3完了承認まで完了扱いしない。

## Verification boundaries
上記Steps1〜10と未検証表記は初回実装時点の履歴を含む。今回の現在ソース確認は次のSteps11〜13だけを実行し、過去の実装や重い検証を反復しない。80%下限を下げない。性能保証や全SSE/全入力保証はしない。native-onlyのcase収集をemulator合格へ読み替えない。fork CIの書込みはjj/signingを使い、mainのユーザー変更をまとめてcommitしない。

## 現在ソースでの完了確認手順

Steps8〜10の品質・文書・レビュー義務は引き続き必須であり、Steps11〜13はそれらを現在ソース上で完成させる手順である。U3 filterだけのcoverage commandを81.293%で合格したと読み替えない。同値は既存CIのCPU/Decoder9製品file集計であり、正確な実行commandと分母を記録する。filter単独の80%証拠やassigned形式ごとの対応が欠ける場合は未達/GAPとして具体的に報告する。

- [ ] Step 11: 署名head11195ad000415af6b320b8e0e4b64a46265fdb61の211 source、既存U3実装・固定probe/aube binary・inventory・native oracle・比較契約を照合する。verification/u1-sha-prerequisite の現行CI、CPU/Decoder9製品fileの2737行中2225行（81.29338691998538%）、workspace93.13%、production Node/実Safari21、7ASan各601秒/179pathsをexact hash付きで再利用評価する。旧74.78%の別分母測定、SHA native profile差・初回Windows errno5未解明と失敗履歴を保持する。assigned inventory全行の実装/差分対応が不足すれば具体GAPを記録し完了を主張しない。（FR1.2/FR1.4/FR1.6/FR9.1、NFR1〜3/7〜9）
- [ ] Step 12: U3のcode-summary、source-manifest、traceabilityと支持命令/比較除外説明を現行証拠へ更新する。supplemental-change-inventoryのCPU u3_tests、Harness diff_u3/support/u3_oracle、新native-contract.rsを含む実際のU3関連変更を漏れなく列挙し、共有Kernel/CI/production fixture経路も所有と実変更根拠を明示する。後続UnitはDeferred/N/Aを理由付きで区別する。未実装familyのCPUID広告offとIntel16byte SHA整列契約、exact観測profileの6差異だけを認める比較・unknown profile FAILを維持する。23先行成果物と元2prefixを変更しない。製品変更が必要な不足は具体案を親へ報告し、この記録完了作業で黙って実装しない。（FR1.4、C3/C5、NFR1）
- [ ] Step 13: 承認済みread-only checkerを1回、U3限定traceability/required-sections sensorを各1回実行してraw/exitとcurrent source/成果物hashを保存する。限定CPU/Decoder/Harnessコマンドは既存CIの同source実測を根拠にし、追加実行は証拠の欠落を補う場合だけとする。checkerがU3 inventory/trace対応を検査しない境界は別の対応表検証で補い、必要な新正本commandは内容を用意して人の承認前に実行しない。全書込み停止後に独立レビューへ渡す。レビュー/正式checkpointは親担当であり、この手順の準備成功だけで正式U3完了としない。（FR9.1、NFR1〜3/7〜9）

## Step14：列挙した単独filter coverageのLinux実測

- [ ] Step 14: 既存Steps11〜12の保存証拠とNFR3 GAPを保持したまま、署名11195ad000415af6b320b8e0e4b64a46265fdb61の製品bytesを基準に既存隔離jj workspaceで診断専用workflowを追加する。mainworkspace製品/test/CIの意味論は変更しない。固定nightly2026-10-01とlocked Cargo、空coverage profilesから `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib u3_tests:: --fail-under-lines 80` をnative x86-64 Linuxでそのまま実行する。全211 pathsを署名基準へbefore/after照合し、唯一の既知Safari文書差は主workspace/current証拠とCI基準を別hashで明示する。read-only permissions、SHA固定Actions、always artifactでcommand/raw/exit/LCOV/JSON/toolchain/source hashを成功・失敗とも保存する。既存bookmark codex/u2-asan-diagnosticへjj署名pushをhost権限で行いconnector Verifiedを確認、Actions run/job/log/artifactを取得する。PRは作成しない。このpushで新規起動した不要な旧sanitizerだけをsource不変照合後にキャンセルし既存成功や他者runを触らない。80未満ならFAIL/GAPを保持してmissing-line/file分析と意味のある追加test案を親へ返し、閾値・製品分母を変えない。既存81.293%を上書きせず、この列挙commandが成功したと称しない。成功時だけ該当command GAPを解消し限定sensor・記録を更新、全書込み停止して親の独立レビューへ渡す。承認前はworkflow草案の保存のみとし、テスト/CI/pushを実行しない。（NFR3、FR9.1）

## U3 filter 80% 達成の追加手順（Steps15〜18）

- [ ] Step 15: Step14の構文失敗と508/2758行18.419%を保持し、同じCPU/Decoder9製品ファイルを測定対象に固定する。tests/guests/u3/build.shの既存observe/fault-observe/cpuid-observeをnative x86-64 Linux CIで毎回先に実行し、正常・fault・CPUIDのfresh expected/raw/hashを生成する。既存CPU u3_testsのnative replay2件へ供給する入口を設計し、観測欠落やunknown profileはFAILとする。期待値の固定保存・skip合格は禁止。（FR1.4、FR9.1、NFR1〜3）
- [ ] Step 16: crates/paludarium-cpu/src/u3_tests.rsのreplay入口を同じu3_tests:: filterで通常実行できるよう移行し、正常/暗号/FP/faultのfresh native観測を実CPUへ比較する。必要な共有test utilityはtests/guests/u3/native-contract.rs、Harness supportの既存比較契約と整合させる。Decoder u3_tests.rsにはprefix/幅/切断/無効encodingの独立境界、CPUにはpacked saturation/shift/alias、FP丸め/例外/fault原子性、公開CPU実行のU3命令境界を追加する。native caseを先に用意・観測し、内部接続の単体ケースは接続後に追加する。実装を鏡写ししたexpected、無関係な整数分岐の件数埋めは禁止。製品不具合発見はraw再現を報告し別具体範囲判断へ戻す。（FR1.4、NFR1〜3）
- [ ] Step 17: 隔離fork診断workflow u3-filter-coverage.ymlをfresh native生成→同じfilter測定へ拡張し、固定nightly/locked/空profilesで `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80 -- u3_tests::` を実行する。package追加・production除外・閾値低下はしない。raw exit、CPU/Decoder9file LF/LHと別unscoped report、native入力、profiles、211基準＋実追加test pathsのsource前後hashをalways保存する。jjの同bookmark署名push/Verified、read-only permissionとSHA固定Actions、30秒native process watchdogを維持する。80未達なら未到達行とU3関連性を具体報告し黙って分母や範囲を変えない。native replayだけで80達成とは事前に保証しない。（NFR3、FR9.1）
- [ ] Step 18: 80%達成後にU3 summary/trace/manifestと全assigned inventoryを実証に更新する。変更がtest/configだけなら7ASan既存600秒証拠は各compiled dependency closureのbyte一致を証明した範囲で再利用、不一致の対象のみ再検証する。production wasm/Node/実Safariもmoduleとproduct closure一致を要求し不一致時は再実測する。先行23成果物と元2prefixは不変で完了確認だけ更新する。旧strict211 checkerを弱めず、新test/config exact inventory・fresh native・同filter80%を検査する補足正本commandを必要時別pathで作り、人のcommand承認前に実行しない。限定sensor/独立レビューと正式checkpointは親担当。未知profile・部分family広告off・SHA16byte契約と歴史失敗を保持する。（NFR1〜3/7〜9）

## 選択された品質測定契約（Steps19〜21）

人が選択したoption1により、CPU/Decoder共有library全単体suiteの80%品質測定と、U3 fresh native差分/境界matrixの必須成功を分離する。以前のfilter単独80%義務は今回の測定義務に置き換えるが、Step14/17の47.1356%など失敗を成功へ再ラベルしない。80%下限・同じ9sourceファイル・package集合は保持する。ファイル内inline cfg(test)も元の分母に含まれ、compiler/object集合でLFが変わる場合は実値と差を明示する。

- [ ] Step 19: 現在の2test-only変更と非test209path、先行23成果物・元2prefixを照合して保持する。隔離forkの既存u3-filter-coverage.ymlだけを、fresh正常/fault/CPUID生成→独立U3 matrix→空profilesで共有全library80%測定の順へ更新する。毎CIのnative前置、unknown profile/欠落FAIL、固定nightly/locked、30秒process-group watchdog、同bookmark署名jj push/Verified、SHA固定Actions/read-only/always raw artifactを保持する。製品/testの追加修正は行わず、具体不具合発見時は再現を報告する。（FR1.4、FR9.1、NFR1〜3）
- [ ] Step 20: fresh native inputsとFULL_REPLAYを供給して `cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --no-report -- u3_tests::` を独立matrixとして実行し、CPU40/Decoder12・ignored0、正常23576/fault1162/CPUID12の件数と比較成功をrawから要求する。次に `cargo llvm-cov clean --workspace` でprofilesを消去し、`cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80` を共有suite品質gateとして実行する。追加package・production除外・U2testのU3への改名は禁止。両gateを独立評価し、9sourceファイルLF/LH・console・LCOV/JSON・native/profile/source前後を保存する。80未達またはmatrix未達ならGAPを保持する。（FR9.1、NFR3）
- [ ] Step 21: 両gate成功時だけNFR3とU3記録を今回選択された義務に基づき更新し、旧filter47.1356%や既存81.293%を別履歴保持する。product compiled closure不変の根拠付きで7ASan各600秒とproduction Node/実Safari21を再利用し、新実行とは主張しない。旧strict211 checkerは保持する。2test-only exact deltaと新署名CI/native/matrix/shared80/raw hashを追加検査する新read-only正本commandが必要なら具体化し、人のcommand選択前に実行しない。限定sensorと独立レビュー、正式checkpointは親担当。全書込み停止後に渡す。（NFR1〜3/7〜9）

## Step22：既存CI coverageのnative入力接続修復

- [ ] Step 22: auto CI37907701758 coverage jobのnative env NotPresent回帰を、main .github/workflows/ci.ymlのLinux coverage jobだけで修復する。草案step22-ci.patch-draftに従い、既存musl buildから正常23576/fault1162/CPUID12を毎CI先に生成し各process-group30秒kill/reap、exit0/stderr空/行数/hashを要求する。3absolute native pathとFULL_REPLAYを全coverage commandへ供給する。test/製品意味論・skip条件・閾値80・package/除外・既存3OS/native/lint/deps/production wasm gateは変えない。選択済み独立matrixと共有80%は別証拠として保持。隔離forkにこのexact CI差分だけを同期し同bookmark署名jj push/Verifiedでfresh全CIを実測する。最終同headの全8jobs成功とraw/source/receipt、2test-only差分＋CI設定差分のexact inventoryを保存する。compiled product closure不変なら7ASan600/Node実Safari21は根拠付き再利用し、旧失敗履歴を残す。旧checkerを弱めず、新追加正本checkerは全CI成功を含む具体証拠固定後に準備し、人のcommand承認前は実行しない。限定sensor・独立レビュー・正式checkpointは親担当。承認前はdraftと計画だけでlive CIを変更しない。（FR9.1、NFR3/7〜9）

## R-02 文書修正計画

- [ ] Step 23: US3・NFR3の検証記録で、136行に対応する568変種（正常23384・fault1141）と全native577変種（正常23576・fault1162・CPUID12）を区別する。code-summary.mdとinventory-case-audit.jsonへ補助9変種（正常192・fault21）の内訳と役割を記録する。
- [ ] Step 24: 既存native rawから集合差と件数を再集計し、568+9=577と正常・fault件数の一致を検査する。正本verify-current-u3-native-shared.py、独立レビュー、完了確認を更新する。製品・テスト・CIソース、品質下限、先行Unit成果物、過去証拠を維持する。

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
