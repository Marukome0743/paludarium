# 根拠の記録：practices-discovery

> Step 5（リードの統合）の時点の記録です。リードの下書き、3 つの支援エージェントの独立レビュー、
> 人との面談（`practices-discovery-questions.md`）をまとめました。**人の回答がすべての下書き・提案より優先します。**
> 根拠の種類は **検証済み / ドキュメント根拠 / 推測** で示します。

## 調べたもの

### リード（aidlc-pipeline-deploy-agent）

| 対象 | 見たこと | 種類 |
|------|----------|------|
| リポジトリ直下（`ls -a`） | `README.md`、`LICENSE`、`.gitignore`、`aidlc/`、`.claude/`、`.git`、`.jj` だけ。コード、`Cargo.toml`、`.github/`、`mise.toml` はない | 検証済み |
| `git log --oneline`／`git rev-parse --short HEAD` | コミットは 1 件、`6546cf4` | 検証済み |
| `git remote -v` | 出力なし。GitHub のリモートはまだない | 検証済み |
| `.claude/scopes/aidlc-rust-blink-port.md` | `skeleton:` の指定がない（`grep skeleton` の結果が空） | 検証済み |
| `aidlc-state.md` | Greenfield、Scope `rust-blink-port`、Test Strategy Standard、Construction Checkpoints enabled、Operation はスキップ | 検証済み |
| `memory/org.md`・`team.md`・`project.md` | org.md の 5 節を既定値として読んだ。team.md は空。project.md の `## Corrections` に Ideation の訂正 4 件 | ドキュメント根拠 |
| Ideation の成果物 | 制約の一覧（C-T1〜C-T11、C-R1・C-R2、C-O1〜C-O3）、決定の記録（D3・D10・D14・D16・D21・D22 など）、範囲の文書 | ドキュメント根拠 |
| 背景資料 `knowledge/documents/research/cheerpx-oss.md` | webix・portabox の節にある `lanmower/blink` フォークとマルウェアの記述 | ドキュメント根拠 |
| `~/AppData/Local/mise/installs/` | rust、cargo-nextest、cargo-insta、cargo-semver-checks、cargo-machete、biome、actionlint、lefthook、node、pnpm などがある（存在のみ） | 検証済み |

### quality（`contributions/aidlc-quality-agent.md`）

- 見たもの：リードの下書き、stage 定義、`.claude/tools/aidlc-testing-posture.ts`（`custom` が正当な値であることをコードで読んだ。実行はしていない）、Ideation の RAID・制約、mise の一覧（cargo-llvm-cov・cargo-mutants・Playwright は手元に無い）。
- 推したこと：Ordering を層で分けた一文、差分テストの 3 つの粒度（命令・プログラム・JIT とインタプリタ）、未定義のフラグを比べないこと、実行ごとに変わる値をそろえること、「差分テストのある命令の割合」の記録、3 段の CI ゲート、揺れるテストの扱い、段階 5 の「速い」を数値にすること、Safari の確かめ方を決めること。

### developer（`contributions/aidlc-developer-agent.md`）

- 見たもの：リードの下書き、制約の一覧、範囲の文書、意図書の要約。コードはまだ無い。
- 推したこと：層の分け方と一方向の依存、host 層の trait、`GuestAddr` の newtype、3 種類のエラーの分け方、`#![forbid(unsafe_code)]` と `// SAFETY:` の必須化、`unwrap` などの禁止、`sys_`／`op_` の命名、ワークスペースの 2 案、nightly が要るかもしれない点、製品に入るつなぎの部品（`libc`・`windows-sys`・`wasm-bindgen`）を面談で問うこと。

### devsecops（`contributions/aidlc-devsecops-agent.md`）

- 見たもの：リポジトリ直下、mise の一覧（cargo-deny・cargo-audit・gitleaks・zizmor・cargo-fuzz は手元に無い）。
- 推したこと：cargo-deny（ライセンス・取得元・既知の脆弱性）、`Cargo.lock` と `--locked`、Actions の SHA 固定と最小権限、Trusted Publishing と人の承認つきの公開、来歴、ファジング、STRIDE の観点でのゲストの安全性（syscall の素通し禁止、ディレクトリの外へ出さない、環境変数・ネットワーク・プロセス・資源の上限）、`SECURITY.md`。

## 面談で決まったこと

| 質問 | 回答 | 反映先 |
|------|------|--------|
| Q1 | **X（置き換え）**：基本的には外部のものを使ってよい。著作権やライセンスの問題に関わるものは自作する。既存のものに不具合や上手くいかないところがあれば、その部分は自作する。当初の回答 C（道具も含めてすべて自作）を、ユーザーのチャットでの発言で置き換えた | team-practices（Way of Working）、discovered-rules（Mandated 1・2） |
| Q2 | A：短命なブランチから PR、CI が通ってから `main` に squash | Way of Working |
| Q3 | A：細い一本を作る。段階 1 の hello world で、ネイティブとエミュレータの出力・終了コードの一致をコマンドで示し、人が確かめる | Walking Skeleton |
| Q4 | A：custom。命令・syscall・プログラムは期待結果を先に、内部の部品は実装の後に単体テスト | Testing Posture（Methodology・Ordering） |
| Q5 | A：行カバレッジ 80%（Linux のネイティブで測る）＋差分テストのある命令の割合を記録 | Testing Posture |
| Q6 | B：期待結果は毎回 CI の x86-64 Linux で作って比べる | Testing Posture |
| Q7 | A：変更のたびに 3 つの OS の単体テスト・lint・依存の検査、段階ごとに probe と aube、夜間にブラウザ・速さ・ファジング | Testing Posture |
| Q8 | A：タグで CI から公開、公開前に人の承認、Trusted Publishing を優先、段階ごとに 0.x 版 | Deployment |
| Q9 | A：rustfmt、clippy の警告はエラー、`unsafe` はホスト接続部と JIT だけ、理由のコメント必須、`unwrap` なども禁止 | Code Style |
| Q10 | B：最初から nightly | Code Style |
| Q11 | A・B・C・D（4 つとも）：未実装の syscall は ENOSYS、指定ディレクトリの外へ出さない、panic・未定義動作にしない（ファジング）、Actions の SHA 固定と crates.io からだけの依存 | discovered-rules |
| Q12 | A：macOS の CI で本物の Safari | Testing Posture |
| Q13 | **X（置き換え）**：Q1 の置き換えにより、道具の境目は「著作権・ライセンスに問題がなく、不具合がなければ外部のものを使ってよい」になった | Way of Working |
| Q14 | A：iced-x86 などの既存のデコーダを使い、合わないところは自作する。**実現性の工程の決定 D10（デコーダも自作）と制約 C-T2（外部の部品を使わずにすべて自作）を変更する** | Way of Working、discovered-rules から旧規則を削除 |
| まとめの確認 | Looks correct | ― |

### 方針の変更で消したもの・変えたもの

- 下書きの `ALWAYS デコーダを含め、製品のコードは外部の部品を使わずにすべて自作する` を削除し、Q1 の方針（ライセンス・著作権に関わるもの、不具合のあるものだけ自作）の 2 つの ALWAYS に置き換えた。
- 下書きの `NEVER 既存の x86 エミュレータやデコーダの実装（iced-x86 など）を依存として取り込まない` を削除した（Q14）。
- 「コードを写さない」と Blink のフォークの系列の禁止は、そのまま残した（ライセンス・著作権と安全のため。Q1 の方針とも合う）。
- 下書きにあった `ALWAYS Rust で実装する`（C-T1）、`ALWAYS Apache-2.0 で公開する`（C-R1）、`ALWAYS 既定は仮想ファイルシステム`（C-T8）、`ALWAYS 差分テストで確かめる` は、今回の固い規則の対象（Q1・Q11・コードを写さない・Blink の系列）から外した。前の 3 つは Ideation の制約の一覧に決定として残っており、差分テストは `team-practices.md` の Testing Posture に進め方として置いた。

### 統合のときの解釈（承認の場で確かめてほしい点）

- **Q7 の「依存の検査」**：回答には「外部の crate が入っていないことの確認」と書かれているが、これは Q1 を置き換える前の方針によるもの。新しい方針に合わせ、「ライセンスが Apache-2.0 と両立すること、取得元が crates.io だけであること（Q11 D）、既知の脆弱性」の検査と読み替えた（推測。人の確認が要る）。
- **Q4 と Q6 の組み合わせ**：期待結果はリポジトリに保存せず毎回 CI で作るので、Ordering の「期待結果を先に」は、「差分テストのケースを実装の前に用意し、その期待結果はネイティブの x86-64 Linux で作る」という意味で書いた。
- **差分テストを PR ごとに回すこと**：Q6 の「毎回」を、PR ごとに x86-64 Linux のランナーで差分テストを回す意味と読んだ。
- 支援エージェントの提案のうち、人が反対していないもの（層の境界、host 層の trait、`GuestAddr`、エラーの 3 分類、`sys_`／`op_` の命名、未定義のフラグを比べない、実行ごとに変わる値をそろえる、JIT とインタプリタの差分、揺れるテストの扱い、`Cargo.lock` と `--locked`、Actions の最小権限、来歴、yank と deprecate）は、固い規則ではなく進め方として `team-practices.md` に入れた。

## 採らなかった意見（反対意見の記録）

| 出どころ | 意見 | 採らなかった理由 |
|----------|------|------------------|
| quality | 差分テストの期待結果はリポジトリに保存し、どの OS でも保存した結果と比べる。作り直しは別のジョブ | Q6 で人が B（毎回 CI の Linux で作る）を選んだ |
| quality | 細い一本の確認は、ネイティブで動かした結果ではなく保存した基準と比べるべき | Q3 で人がネイティブとエミュレータの比較を選んだ。Q6 とも合う |
| quality | Safari は WebKit のテスト用ブラウザで代える選択肢 | Q12 で人が本物の Safari を選んだ |
| quality | 「NEVER jart/blink などのテスト用プログラムや期待値の表をそのまま写さない」を規則にする | 人が述べた制約ではない。ただし「コードを写さない」の禁止が素材にも及ぶ形で守れる |
| developer | 起動用 JS の実行時の npm 依存をゼロにする（C-T2 による） | C-T2 は Q1 で変わったので、根拠がなくなった。Construction で改めて決める |
| developer | C-T2 の範囲次第で `thiserror` なども使わず手で書く | Q1 で外部のクレートを使ってよくなった |
| developer | ワークスペースの 2 案（層ごとのクレート／少数のクレート） | 面談で決めていない。Construction の設計で決める（未決として残す） |
| devsecops | cargo-deny の `bans` で iced-x86 などのデコーダを名前で禁止する | Q14 で既存のデコーダを使うことにした |
| devsecops | 長く有効な公開トークンを使わない、`unsafe` の `// SAFETY:` を固い規則にする | 人は Q11 で A〜D だけを選んだ。Trusted Publishing と `// SAFETY:` は進め方として入れた |
| devsecops | ネットワーク・環境変数・ホストのプロセス・資源の上限の既定、`SECURITY.md`、secret scanning、pre-commit の秘密情報の検査 | 面談で決めていない。設計（Construction）で決める（未決として残す） |

## 残る不確かさ

- **nightly 専用のクレートと crates.io の公開**：Q10 で最初から nightly にした。公開するライブラリが nightly でしか作れないと、利用者が限られる。公開の前に stable で使えるかを見直す必要がある（推測）。
- **Windows の開発機で差分テストを回せない**：Q6 で期待結果を毎回 CI の x86-64 Linux で作るので、Windows の手元では差分テストを直接は回せない。WSL で回せるかは未検証。細い一本の確認コマンドも、Linux（CI または WSL）で動かす前提になる。
- **Trusted Publishing の対応**：crates.io と npm が GitHub Actions からの Trusted Publishing に対応しているかは、記憶による情報で未検証。導入前に公式の文書で確かめる。
- **macOS の CI での本物の Safari**：GitHub の macOS ランナーで Safari を自動操作できるか（safaridriver など）は未検証。
- **iced-x86**：MIT ライセンスで Apache-2.0 と両立する（面談 Q14 の説明。ドキュメント根拠）。wasm32 でのビルド、範囲（SSE 系まで）の対応、速さは未検証。
- **スコープの `skeleton:`**：`rust-blink-port` のスコープには `skeleton:` の指定がない（検証済み）。Q3 で細い一本を行うと決めたので、org.md の規則に従って細い一本の確認を行うには、スコープ側の扱いをオーケストレーターが確かめる必要がある。
- **jj と git worktree の共存**：Construction の worktree は AI-DLC の `aidlc engine worktree`（git ベース）が作る。jj の作業コピーとどう共存させるかは未決。
- **GitHub のリモート**：まだ無い。`main` の保護（必須のチェック）と、公開用の environment の設定は、リモートを作るときに行う。
- 道具の動作（cargo-llvm-cov の Windows 対応、GitHub の macOS ランナーの CPU、Miri とスレッドの相性など）は、どれも手元で確かめていない（未検証）。
