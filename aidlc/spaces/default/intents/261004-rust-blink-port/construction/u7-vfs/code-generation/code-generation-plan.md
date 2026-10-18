# U7 ファイルシステム：実装計画

## Summary

- Builds: Step48。U14の整数SSEのJIT（署名head 1ceae86c）で変わった、U7が担当する `crates/paludarium-wasm/src/abi.rs`（JITの状態144 byte→`STATE_BYTES`の400 byte、SAFETYのコメント）を再確認する。U7の記録の主張が今のsourceでも正しいかを確かめ、正しくない記述があればcode-summary.mdに訂正の節を足す。製品は変えない。
- Touches: U7の計画・手順書・code-summary.md（必要な場合だけ）。製品・既存試験・旧証拠・ほかのUnitの記録は変えない。
- Tests: 新しいテストの実行はない。正式sensor 2件、独立再レビュー、今の正式確認コマンド（U2の `u2_candidate.py`）でのcheckpoint。

## 今回の計画：Step48（Build and TestのLoop-back 1：共有のabi.rsの再確認）

2026-10-17。U14の整数SSEのJIT（署名12d6a2f6・1ceae86c、CIはすべて成功、FR8.3の正式な性能測定は合格）で、U7のsource-manifestにある `crates/paludarium-wasm/src/abi.rs` が変わった。変わったのは `execute_ready`／`execute` の状態の型（`[u64;18]`→`JitState`）、長さ（144→`STATE_BYTES`＝400）、`// SAFETY:` のコメントだけである（U2 Step71の確認）。正式確認コマンドは、人の承認でU2の `verification/loopback1-next/u2_candidate.py` になっている。U7の計画・手順書は旧い封印に入っていないので、この記入でコマンドは壊れない。

- [x] Step 48 — abi.rsの変更を読み、U7の記録（code-summary.md・traceability.json）がabi.rsやJITの状態について述べていることが、今のsourceでも正しいかを確かめる。正しくない記述があれば、code-summary.mdに「現行Step48」節を足して直す（旧い記述は履歴として残す）。traceability.jsonの分類・targetは変えない。正式sensor 2件を実行し、書き込みを止めて独立再レビューに進む。そのあと今の正式確認コマンドでcheckpointを検証し、人の承認を受ける。新しい重い試験・CIは行わない（C12、NFR3、NFR8）。

## 前回のSummary（Steps45〜47）

- Builds: U7のTesting Contractと承認記録を現在の規則へ整合し、独立再レビューと最終確認を経てU11へ戻る。
- Touches: U7の計画・検査手順・照合記録だけ。製品・既存試験・旧証拠を保持する。
- Tests: 既存証拠の適用範囲を照合し、正式sensor・独立レビュー・承認済み最終確認を更新する。新しい重い試験は追加せず、strict guard、80%下限、30秒制限を維持する。

## 今回の計画：Steps45〜47（Testing Contractと承認記録の更新）

- [ ] Step 45 — 公式renderのTesting Contract全体を計画へ反映し、既存U7限定手順と新しい承認済み確認コマンドの準備を確認する。製品・既存試験を変更せず、旧原本と現行参照を区別し、現行担当ソース・依存・両lock・compiler・設定を保存証拠へ照合する（FR3.3/9.1/9.3、NFR1/2/3/7/8）。
- [ ] Step 46 — 照合した適用範囲と未検証をU7記録へ反映し、正式sensorを実行する。保存済みWindows隔離・Linux差分・coverage・ASan/LSanは条件一致範囲だけ再利用し、新規実行と区別する。不一致を閾値やmask変更で隠さず、必要な追加対応は具体化して人へ返す（全割当FR/BR/NFR）。
- [ ] Step 47 — 記録を固定して独立再レビュー、承認済み確認コマンド `python3 aidlc/spaces/default/intents/261004-rust-blink-port/verification/verify-current-u2-u11-revalidated.py` の正式checkpoint、人の完了承認へ進む。U11への遷移はengineの正式経路で確認する。ID競合の完全解消、新しいU7重検証、U11同時dispose修正完了は主張しない（NFR2/3/8/9）。

## 履歴：Steps40〜44（R-04の負mtime修正）

- [ ] Step 40 — FileStat、NativeFsのpath/open-file metadata、VFS、Kernel stat codec、wasm filesystem/ABIと利用側を限定確認する。Linux nativeでepoch直前・負の小数秒・epoch・正時刻のpath stat/fstatを取得し、現行EIOとの差分Redを記録する。範囲外時刻と丸め・overflowの扱いも固定し、既存runnerと30秒境界を使う（FR3.3/9.1、NFR1/2/7）。
- [ ] Step 41 — 負値と従来の正値範囲を保持できるmtime表現へ最小修正する。HostのSystemTime変換で負値をEIOにせず、VFS・Kernel・wasmの全利用側を同一変更で整合させる。Linux statは負時刻をfloor秒と0以上10億未満のnanosecondsへ正規化し、境界のchecked変換を行う。wasmの既存ABI/JS decoderへの影響を確認して変更が必要なら版・利用側も整合し、負値のunsigned wrapや既存正時刻の破壊を許さない。独立したclock syscallや無関係な機能は変更しない（FR3.3、NFR2/4/9）。
- [ ] Step 42 — 内部変換・stat codec・VFS/wasm境界の単体回帰を実装後に追加し、先行nativeケースとのpath stat/fstat差分をGreenにする。epoch前後、-1ns、負整数秒、正値の既存範囲、overflow、Linuxsec/nsecの正規化とbyte符号を確認する。最新ツールを公式確認して診断環境へ固定し、既存のmtime/U11回帰と変更利用側の回帰を実行する。実コマンド・件数・raw/exitを保存する（FR9.1、NFR1/2/3/9）。
- [ ] Step 43 — 修正後の全入力・両lock・suppressionを固定し、署名済みfork診断CIでWindows隔離、fresh Linux diff_u7、同scope U7coverage80%、影響するvfs_paths/syscall_args/mmu_ops各600秒ASan/LSanを再確認する。既存30秒・seed1/rss2048/suppression/detect_leaks1/masksを保持する。mtimeを利用するwasm ABI回帰も行い、現行ソースとのbefore/after一致と全rawを保存する。新しいcanonicalコマンドが必要なら具体化して人へ選択を求め、旧固定検査を無断変更しない。署名Verified/head確認、PR/mergeなし（FR9.1/9.3、NFR1/2/3/4/7/8）。
- [ ] Step 44 — R-04の修正と新実測を成果物・manifest・共有境界の説明へ反映し、U11への先送り表記を取り除く。正式sensorを実行して書き込みを止め、新しい独立レビュー・承認された最終確認・人の完了承認へ進む。過去の成功を修正後の証拠として流用せず、strict guard、80%/30秒/600秒、Testing Contractを維持する（全割当FR/BR/NFR）。

## 履歴：Steps36〜39（不足4項目の現行再検証）

- [ ] Step 36 — 現行製品・テスト・fuzz・設定・両lock・suppressionを固定し、既存隔離jjリポジトリの適切な診断workspaceへバイト一致で配置する。診断workflowだけを変更し、公式情報で最新ツールを確認して具体版を固定する。製品設定・lockは変更せず、環境版・取得根拠・全入力hashを保存する。署名付きjj pushとVerified・CI headを確認する。PR/mergeは作成しない（NFR1/3/8/9）。
- [ ] Step 37 — 同一現行ソースでnative Windowsの既存u7_native_windows_symlink_rename_raceをexact実行し、fixture内symlink生成・1000以上victim反復・成功交換1以上・outside不変・cleanup・whole-child30秒を確認する。native x86-64 Linuxでは既存U7限定coverageコマンドを同じscope/除外/80%下限で実行し、同runのdiff_u7をfresh native期待値と比較する。独立jobでvfs_pathsを600秒ASan/LSan、seed1/timeout30/rss2048/既定max_len/detect_leaks1/既存suppressionのまま実行する。最小ASan終了診断と全raw/exit/実測/coverageJSON/source before-after/両lock/binaryhash/symbols/corpus/crashを常時保存する。0件・skip・権限不成立・短縮・失敗は合格としない（FR3.2/9.1/9.3、NFR1/2/3/4/7）。
- [ ] Step 38 — CI成果物を現行全入力との一致で独立確認し、成功した実測範囲のみ7要件のGAPを更新する。製品不具合や80%未達は再現根拠と最小修正案を提示し、条件を緩めない。1970年以前のmtimeの既知課題は承認済みU11対応として未修正を明記する。4成果物・manifest・証拠を保存し正式sensorを再実行する（全割当FR/BR/NFR）。
- [ ] Step 39 — 書き込みを停止して新しい独立レビューを取得し、既存承認済みcanonical checkpointを実行する。人の完了承認後に次Unitへ進む。今回の有限CI成功を任意入力・全OSやID競合の完全解消へ拡張しない。strict guard、80%/30秒/600秒、Testing Contractを維持する（NFR3/7/9）。

## 履歴：Steps33〜35（全Unitやり直し後）

- [ ] Step 33 — 新しい計画承認と内容確認後、U7 source-manifestの担当範囲と共有契約を確認し、現行bytesを署名済み7eb1819f52acede33e83775374dd4ee93edf643bと照合する。Windows隔離回帰、Linux差分、VFS coverage、vfs_paths ASanの保存証拠を依存ソース・lock・設定の一致範囲で分類し、再利用できない範囲は未検証として具体的な確認手順を示す。今回のU4 syscall_args検証も依存一致を条件に適用範囲を明記する。旧成功を新実行と呼ばない（FR3.1–3.4/2.10/9.1/9.3、NFR1–9）。
- [ ] Step 34 — 現行照合結果に基づいて4成果物・厳密なsource-manifest・証拠を保存し、正式traceabilityとrequired-sectionsを実行する。既存要件の割当と後続UnitのDeferredを保持する。1970年以前のmtimeなど既知の未修正項目を現行ソースで確認し、承認済みU11対応と区別する。製品不一致は最小修正案を提示し、未検証を成功へ読み替えない（全割当FR/BR/NFR）。
- [ ] Step 35 — 全書き込みを止めて新しい独立レビューを取得し、承認済みcanonical checkpointを実行する。人の完了承認後に次Unitへの遷移を確認する。strict guard、80%下限、30秒watchdog、各600秒fuzz、比較mask、Testing Contractを維持する。並行セッションID競合の完全解消は今回の遷移成功だけでは証明しない（NFR3/7/9）。

## 履歴：Steps28〜32

ユーザーのRequest Changesにより、残るWindows NativeFs並行隔離をユーザー所有forkのwindows-latest CIで検証する。今回はPART1 planningのみで、テスト生成・本体実行・CI pushは新Plan ApprovalとConsolidated Summary Confirmation後に行う。対象はCIが作る一時fixtureのrootとoutside sentinelのみ。実ユーザーファイル・外部システム・OS設定変更は対象外。既存Linux実測は保持し、現在bytesとの適用範囲を再照合する。製品意味論の修正とU9は含めない。

- [ ] Step 28 — 既存35claims/88filesとLinux証拠（署名eafa5ac6、run37760390069、vfs_paths3132329 runs/601秒、U7 coverage90.4652%、diff_u7親63）を保持し、現在hostと178da99e baselineの154関連paths、lock/suppression/toolchainを再照合する。U4 syscall_args1296522 runs/601秒も保存証拠の154paths一致により再利用する。必要なWindows test-only差分は正確に分類し、製品意味論bytes不変を示す。FR9.1/9.3、NFR1/2/3/8/9。
- [ ] Step 29 — 承認後にNativeFs/cap-std境界と既存Windows CI環境を限定読取し、windows-latestの一時fixture内で実directory symlink作成権限を確認する。権限不成立は明示FAIL/未検証としてrawに残し、silent skipやOS設定変更はしない。test-only u7_native_windows_symlink_rename_raceを追加し、root内pivotとoutsideを指すfixture symlinkの並行交換、1000回以上のvictim反復、成功交換1回以上、outside sentinel bytes/一覧不変を検証する。NativeFsのopen/write/create/stat/read_dir/link/rename/unlinkを対象に、barrier/stop/join、handles解放、30秒whole-child kill/reap、strict fixture cleanupを備える。fixture外を参照せず、Unix既存テストと製品意味論を維持する。FR3.2、NFR4/7。
- [ ] Step 30 — isolated jj診断workspaceにtest-only変更とWindows専用最小workflowを用意し、必要なmain test-only差分との同一hashを記録する。既存main CIとDocker設定を変えず、ユーザー所有forkの診断bookmarkへSSH署名付きjj pushをhost権限で実行しconnector Verifiedを確認する。windows-latest/fixed nightlyで新test本体をexact実行し、raw/stdout/stderr/exit/actual反復・交換数/timeout/cleanup/OS・tool・権限/source-before-after/binary SHAをalways artifactへ保存する。該当targetが0件・skip・交換0・timeout・cleanup不成立なら合格としない。製品不具合は保存した再現情報を親へ返し修正は別計画とする。FR3.2、NFR4/7/8/9。
- [ ] Step 31 — 同じ署名CI headの実Windows結果を独立照合し、fixtureに限定した隔離成功/失敗の観測範囲をsummary/evidence/traceabilityへ反映する。Linux証拠は再利用した範囲とtest-only差分の影響を区別し、hash不一致または影響がある場合はGAPと再測定手順を明記する。canonical178da99e固定検査がmain test-only bytesを拒否した場合はcommand/exit/差分を保存して親のprotected command選択へ返し、検査器を変更しない。35claimsには実際のtest-only変更を申告し、isolated workflowをmain claimへ混入しない。FR3.2/9.3、NFR2/3/4。
- [ ] Step 32 — 4produces/manifestとraw証拠を確定し、traceability/required-sectionsと承認済みcanonical結果を保存して全書込を停止する。既存60 IDs/旧R-01・R-02 Resolved、custom exact ordering、80%/30秒/nightly-2026-10-01/600秒を維持。Windows未検証・失敗を合格にせず、有限fixture観測を全OS/任意入力/全wasm保証に広げない。独立review/diary/checkpoint/完了承認は親担当。全割当FR/NFR。

## 履歴：Steps21〜27（Linux達成・Windows未実行）

このattemptではLinux診断CIのみ実行し、vfs_paths3132329 runs/601秒、coverage90.4652%、diff_u7親63を確認した。Windowsは安全性チェックで停止したとの親報告と中止指示により未実行。Step23とWindowsを含む22/24/25は未完、旧記述の「新承認待ち」「未実行」は当時の記録である。

ユーザーの追加指示により、現行sourceの証拠照合に加え、Windows race本体・vfs_paths各600秒ASan/LSan・U7限定coverage80%をできる限り実測する。Steps1〜20は履歴。現段階はPART1のみで、本体は新Plan Approvalと内容確認後に開始する。初期変更は必要なWindows回帰テストとisolated診断workflowに限定し、製品意味論・既存品質条件・他Unit成果物を変更しない。U9 non_exhaustiveは後続Unit。観測した製品不具合の修正は具体的証拠を親へ返し、別の計画で扱う。

- [ ] Step 21 — strict manifest35 claims（directory claimは実ファイルへ展開）を現在hostと署名済み178da99eの全hashへ照合する。旧88files snapshot/4d52 CIは当時の履歴へ限定し、af9bの中間証拠と現行178da99eを分ける。現行保存CIのdiff_u7親case、u7_内部テスト、CLI専用2case、Linux/macOS/Windows、lint/依存/coverageのraw名・件数・cfg条件を再確認し、旧63/81/80を現在件数と推定しない。read-only jj --ignore-working-copyで照合し、新実行と保存証拠再利用を区別する。FR2.10/3.1–3.4/9.1、NFR1/4/7/8/9。
- [ ] Step 22 — 承認後、NativeFs/cap-std4.0.3/cap-fs-ext4.0.3のWindows相対操作と既存Unix race、Windows runnerのsymlink権限/Developer Modeまたはjunction能力を限定確認する。Windows専用runner/testの30秒whole-child kill/reapとraw/exit/iterationsの保存を先に用意する。Linuxは既存isolated jj workspaceの178da99e基準でnative x86-64、固定nightly、llvm-tools/coverage、ASan/LSan最小C終了診断2回を確認する。製品API/OS設定を緩めず、準備不能は理由を保存しPASSにしない。FR3.2、NFR4/7/8/9。
- [ ] Step 23 — crates/paludarium-host/src/native_fs.rsのtest-only領域へWindows専用u7_native_windows_symlink_rename_raceを追加する。std::os::windows::fs::symlink_dirでroot内pivotをoutsideへのdirectory symlinkと交換する攻撃スレッド、outside sentinel、NativeFs経由のopen/write/create/stat/read_dir/link/rename/unlinkを実行する。利用可能性によりjunctionを使う場合も実際のreparse-point生成成功を先に記録し、外部一般pathは使わずfixture内だけを変更する。少なくとも1000 victim反復と成功したattack交換1回以上を要求し、outside内容・一覧が不変であることを確認する。共有開始barrier、終了flag、join、handle解放、30秒whole-child watchdogを保持し、権限なし/交換0/timeout/cleanup失敗は明示FAILまたは未検証（silent skip禁止）。Unix既存本体は保持する。FR3.2、NFR4/7。
- [ ] Step 24 — 承認後、isolated jj workspaceの診断bookmarkへ必要最小workflowと上記test-only変更を追加し、署名付きjj pushをhost権限で実行、connectorでVerifiedを確認する。native windows-latestでWindows新race本体、native x86-64 Linuxでvfs_pathsのASan+LSan各600秒（seed1/timeout30/rss2048/既定max_len/既存suppression/detect_leaks1）、既存scopeそのままのU7限定llvm-cov --fail-under-lines80を実行する。Linux coverageは既存diff_u7も実行して同runのnative期待値を作り、最新通常CIがdiff_u7を含まない点を補う。jobは独立・fail-fast:false、全結果のraw/exit/environment/source before-after/coverageJSON/binarysymbols/hash/corpus/crashをalways保存。既存main workflow・Docker設定を変えず、不要な旧targetの新規重複起動だけを親指示で扱う。FR9.1/9.3、NFR1/2/3/8/9。
- [ ] Step 25 — 同じ署名診断headから各成果物を回収し、178da99eと製品意味論bytes一致（差分は承認済みtest-only/workflowだけ）、現在host/CI source before-after・lock・suppression・targetのhash一致を確認する。Windows実attack回数/victim回数/30秒/外部sentinel/exit、vfs_pathsの非ゼロruns/600秒以上/ASan+LSan exit0、U7 scopeのcovered/total/80%gate/JSONを独立照合する。U4 syscall_args証拠は全意味論依存hash一致が証明できれば再利用し、test-only差分の非該当範囲を明記する。不一致なら再利用せずGAPと必要対応を提示する。実機失敗は再現証拠を保存し閾値・suppression・権限条件を弱めない。FR9.3、NFR2/3/4/7。
- [ ] Step 26 — code-summary/evidence-current/traceabilityを実測へ更新し、旧4d52/89.79%/旧fuzzと現行178da99e/診断headを分離する。既存17担当IDsと旧R-01/R-02 Resolvedを保持、共有fallbackを理由付きで分類し、成功した対象scopeのGAPだけ更新する。Windows本体を観測できなければ未検証を維持する。4producesとmanifestには実際のtest-only変更も申告、診断workflowはisolated証拠として分離する。限定sensorsを保存し、canonicalが178da99e固定で新test bytesを拒否する場合は拒否を記録して親のprotected verification-command承認へ返す（検査器を無断で変更しない）。全任意入力/全UB/全OS/全wasmへ一般化しない。全割当FR/NFR。
- [ ] Step 27 — 全記録・証拠を確定して書込を停止し独立レビューへ渡す。正式review/diary/checkpoint/完了承認は親担当。製品不具合や準備不能は実測根拠と具体的次手を提示し、別の製品修正や未承認CIへ広げない。NFR1/2/3/4/7/9。

既存test files/config（diff_u7.rs、support/u7.rs、tests/guests/u7、各crate u7_、vfs_paths/syscall_args、Cargo/CI設定）は保持し、欠落や実在性をStep21で確認する。Standard各部品5–8、happy path/error/edge、80%・30秒・固定nightly-2026-10-01・各600秒・custom native-before/internal-test-afterの完全Testing Contractを変更しない。今回の保存証拠照合は過去のRedを作り直したという主張ではない。

## 範囲と根拠

ドキュメント根拠：`inception/units-generation/unit-of-work.md` のU7、`unit-of-work-story-map.md`、`inception/requirements-analysis/requirements.md` のFR3.1–FR3.4、FR2.10、NFR1–NFR9、`inception/contract-design/contract-summary.md` のC2/C6/C8/C10/C11。ストーリー工程は省略されているため、FRを手順に直接対応させる。U7固有のfunctional/NFR/infrastructure設計は存在しない。

既定のMemFs、明示指定されたホストディレクトリのマウント、作成・読み書き・hard link・symlink・flock・rename・read_dir・stat、起動前配置を完成させる。ゲストstat系のNULLパスにはEFAULTを返す。既存のhello world、整数命令、メモリ・シグナルの挙動を維持する。スレッド作成・プロセス起動・ソケット・端末・SSE・wasm・JITはそれぞれの担当Unitに残す。

## 変更面と設計

- `crates/paludarium-vfs/src/`：inode、ディレクトリ、パス解決、OpenFile、リンク、メタデータ、ロック、マウント合成。`FileSystem::read_file/stat`の現利用側との互換を保ち、必要な内部型変更は利用側も同時に更新する。
- `crates/paludarium-host/src/`：型付きHostFs能力とネイティブのディレクトリ能力。OSファイル操作はここに閉じ込める。VFSからstd::fsを呼ばず、依存循環を作らない。
- `crates/paludarium-kernel/src/`：FD表・共有open-file description・cwd、明示的syscall追加、checked guest bufferとLinux x86-64 ABIの変換。
- `crates/paludarium-runtime/src/`、必要な`loader/src/`・公開API/CLI：preloadとマウントを接続し、既定はホスト非公開。
- `crates/paludarium-harness/tests/diff_u7.rs`、`tests/guests/u7/`、各クレートの`u7_`テスト、`fuzz/fuzz_targets/vfs_paths.rs`・既存syscall_args、CI/nightly、必要なCargo manifests/lock、`docs/u7/`。

影響はVFS/Host/Kernel/Runtime境界にまたがる。CPU・decoder・MMUの命令やフォールト意味論の変更は計画しない。Loaderや既存APIの追従はC6利用側に限定する。

パス解決はinodeから逐次行い、symlink展開と`..`を単なる事前lexical normalizationで済ませない。rootを越える参照、symlink loop、NUL/長さ、非UTF-8、末尾slash、relative cwd、follow/nofollowを型付きerrnoで扱う。ホストはrootの開いたディレクトリ能力から相対操作する。`canonicalize`で検査後に絶対パスを再openする方式は採用しない。安全なRust APIを持つcrates.io依存を評価し、ライセンス・逃走防止・symlink/rename競合を実測してから導入する。依存選定・安全性は現時点で未検証で、確認を実装手順に含める。

FD番号とopen-file descriptionを分離し、offsetとflock所有者を共有する。unlink後のopen inode寿命、hard linkのlink count、rename置換、cross-mount EXDEV、同一inode操作、append・truncate・seekを扱う。flockはshared/exclusive/nonblocking・変換・close解放と、阻塞時のキャンセル/シグナルを既存Host待機境界で実装する。ゲストファイル数・サイズに独自quotaは追加しない（NFR5）。symlinkのLinux規定やファジング一入力の有限予算は製品quotaと分ける。

## 順序付き実装手順

以下のSteps1〜20と設計・変更面は保存済みの当時の計画と実行履歴である。今回実行するのは冒頭のSteps21〜27だけで、以下の当時の「現在」「今回」は現行sourceのbyte proofを意味しない。

- [ ] Step 1 — U7変更面とC6/C2境界を確定し、既存互換を記録する。FR3.1–3.4、FR2.10、NFR3/4/9。
- [ ] Step 2 — 既存Rust runnerと単位限定コマンドを確認する。まず既存VFS 5テストを実行し、`u7_`名前空間/専用diffターゲットと30秒境界を用意する。NFR1/7/9。
- [ ] Step 3 — 実装前にLinuxでsyscall/ゲストのケースを作る。open/openat/create/read/write/close/lseek、mkdir/unlink/rmdir、link/linkat、symlink/readlink、rename/renameat、getdents64、stat/fstat/lstat/newfstatat、flockを対象とし、必要なdup/fcntl FD操作も最小限含める。NULL・不正buffer・flags・dirfd・エラー・リンク/rename/lockを含め、ネイティブ期待結果と現実装の失敗を生ログで残す。FR3.3/2.10、NFR1。
- [ ] Step 4 — inode/ディレクトリ・パス・OpenFileの内部型と解決を実装し、その後に5–8件以上の単体テストを各部品へ追加して実行する。FR3.1/3.3、NFR2/4/5。
- [ ] Step 5 — MemFsの作成・読み書き・リンク・unlink・rename・read_dir・stat・preloadを実装し、その後に内容/offset/寿命/エラー単体テストを追加して実行する。FR3.1/3.3/3.4。
- [ ] Step 6 — FD表とfile syscallのguest-memory/ABI境界を実装し、Step 3の差分をgreenにする。実装後にKernelの5–8件以上の単体テストを追加して実行する。NULL statはguest EFAULTで継続する。FR3.3/2.10、NFR1/2/4。
- [ ] Step 7 — flock所有権・競合・変換・阻塞/キャンセルを実装し、ネイティブと差分比較する。実装後にロック内部状態の単体テストを追加して実行する。guest cloneを新設せず、複数FD/共有descriptionとHost側の有限並行ケースで検証する。FR3.3、NFR7。
- [ ] Step 8 — ホストのrootディレクトリ能力、型付きHostFs、crates.io依存の出所/ライセンスを検証して実装する。実装後に許可root内操作とroot外参照・symlink/rename競合・hard link・cross-mountの5–8件以上の単体/隔離テストを追加して実行する。FR3.2、NFR4/8。
- [ ] Step 9 — Mount合成・Session/Loader/preload・CLIに接続する。先にネイティブと比較するゲストケースを用意してから実装し、内部Runtime接続テストは実装後に追加する。未指定時のホスト非公開と起動前配置を確認する。FR3.1/3.2/3.4。
- [ ] Step 10 — file probeに相当する作成/hard link/symlink/flockをU7のゲスト差分で検証する。probe全体・aube全体の合格は担当U10と混同しない。標準出力・標準エラー・終了状態・ファイルの内容/種別/link countなどを比較し、pid/inode番号/時刻の除外を記録する。FR3.3/9.1、NFR1。
- [ ] Step 11 — VFSパス/操作列fuzzとU7 syscall_args入力を追加する。nightlyに各600秒、各ケース30秒を維持し、順次実行してpanic/ASan違反・再現入力を保存する。FR9.3、NFR2/3/7。
- [ ] Step 12 — U7単位限定coverageでLinux行80%以上、fmt/clippy警告ゼロ、cargo-deny、CI action SHA、依存lockを検証する。既存workspaceの正式検証は承認済みcheckpointコマンドで確認する。NFR3/8/9。
- [ ] Step 13 — U7 raw evidence・native比較除外一覧・変更API/使用法・source manifest・FR/NFR traceability・code-summaryを完成させる。測定した件数だけ記録し、未検証を合格にしない。NFR1–9。
- [ ] Step 14 — independent review用にソースと成果物を固定し、指摘の必要修正だけを行って再検証する。checkpointの承認と次Unit選択は親担当へ返す。
- [ ] Step 15 — 保存済みsource manifestとソースsnapshotを現在のソースおよび署名付きCIコミットに照合する。ネイティブdiff_u7 63件、U7内部/並行テスト、CLI接続と3OSのログを件数・名前・実行条件まで再確認する。FR2.10、FR3.1–3.4、FR9.1、NFR1/4/7/8/9。
- [ ] Step 16 — 現在のソースへの証拠の適用範囲を明記して4成果物とstrict v1 manifestを保存する。U7担当17IDに限定したtraceabilityと既存targetを整合させ、600秒ASan fuzzやU7限定coverageが古い依存に対する測定ならGAPを保持する。全体CIの80%成功をU7限定80%へ読み替えない。FR9.3、NFR2/3/5/6。
- [ ] Step 17 — 観測記録を更新した後に成果物・manifest・claimed sourceを固定し、独立レビューへ渡す。正式なレビュー記録の登録、承認済みcheckpointコマンドによる検証、完了承認は親担当が実施する。レビュー依頼から正式な結果登録まで製品・成果物・SCMを変更しない。
- [ ] Step 18 — evidence-current.mdの並行root逃走テストの実行範囲をLinux/macOSに限定し、Windowsの同名テストではUnix専用本体が実行されないこととWindowsの並行root逃走検証が未検証であることを明記する。内部テスト件数と本体の実行範囲を区別する。FR3.2、NFR4/7。
- [ ] Step 19 — code-summary.mdを実装・証拠、品質GAP・制限などのH2見出し最低2件で構成する。literal改行や文字escapingを検査し、required-sectionsセンサーのPASSを確認する。製品ソースと検証結果の値は変更しない。NFR3。
- [ ] Step 20 — 4成果物とmanifestを今回の確認後に保存し、17IDs/88ソース一致とGAP維持を確認する。観測記録を更新した後に固定して独立再レビューへ渡し、親が正式レビュー記録と承認済みcheckpoint検証を実施する。SCM操作を行わない。NFR1/2/3/4。

## 検証の合否

custom orderingをそのまま適用し、ゲストsyscallはネイティブケースを先に、VFSなど内部部品は実装後に単体テストを実行する。Standardの各部品5–8テスト、happy pathと少なくとも2つのerror/edge、重要境界のintegrationを満たす。Linux行80%以上・30秒diff/並行・各10分fuzz・unsafe禁止・依存検査を下げない。ホスト隔離はチェック後openの競合ケースまで観測する。U12/U13の固有ホスト実装やU11ブラウザ合格を本Unitで主張しない。

## 承認と未確定点

履歴：旧承認・summary確認後、Steps18〜20のWindows race実行範囲修正、必須見出し検証と成果物保存を完了した。Steps15〜17も当時の証拠。新Steps21〜27は未実行で新承認待ち。ドキュメント根拠：Windows現行race本体はcfg(unix)、NativeFsはretained cap_std::fs::Dirから相対操作する。Windows runnerのdirectory symlink/junction権限とrace実行可能性は未検証でStep22で確定する。失敗時は証拠付きで報告する。
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
