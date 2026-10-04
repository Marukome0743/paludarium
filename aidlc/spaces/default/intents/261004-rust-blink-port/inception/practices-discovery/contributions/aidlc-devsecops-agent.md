**Collaborator:** aidlc-devsecops-agent

## Contribution

> 担当：lint・整形、SAST／動的検査、秘密情報と依存の検査、サプライチェーン（GitHub Actions の固定、crates.io・npm の公開トークン、来歴）、信頼できないゲストを動かすときの安全性。
> 根拠の種類は各項目に「検証済み／ドキュメント根拠／推測」で付けています。ここにある規則案はすべて **提案** で、人が述べた制約ではありません。`discovered-rules.md` に入れるかは面談で決めてください。

### 1. 前提として確かめたこと

- リポジトリ直下は `.claude`、`.git`、`.gitignore`、`.jj`、`aidlc`、`LICENSE`、`README.md` だけで、`.github/`、`Cargo.toml`、`deny.toml` などはまだない（`ls -a` の結果。検証済み）。
- 手元の mise には `actionlint`、`lefthook`、`hk`、`cargo-machete`、`cargo-semver-checks`、`shellcheck` がある。一方で `cargo-deny`、`cargo-audit`、`gitleaks`、`zizmor`、`cargo-fuzz` は入っていない（`ls ~/AppData/Local/mise/installs/` の結果。検証済み）。下の提案で使う道具の一部は、新たに入れる必要がある。
- 製品のコードは外部の部品を使わない（C-T2）ので、実行時の依存はほぼゼロになる見込み。ただし前提 A1 がどちらに決まっても、**開発用の依存（テスト・ビルドの道具、JS の道具、GitHub Actions）は残る**。サプライチェーンの対策はそちらが主な対象になる（推測）。

### 2. Code Style に足す案（lint・整形）

リードの下書き（rustfmt・clippy、警告はエラー）に賛成し、次を足すことを提案します。

- CI では `cargo fmt --check` と `cargo clippy --all-targets --all-features --locked -- -D warnings` を実行する。
- `Cargo.toml` の `[workspace.lints]` で、`unsafe` に関する次の lint を有効にする：
  - `rust.unsafe_op_in_unsafe_fn = "deny"`
  - `clippy.undocumented_unsafe_blocks = "deny"`（`unsafe` ブロックごとに `// SAFETY:` の理由を必須にする）
  - `clippy.missing_safety_doc = "deny"`
- `unsafe` を使ってよいクレート（例：ホストとの境界、MMU の高速経路、JIT）を決め、それ以外のクレートでは `#![forbid(unsafe_code)]` を付ける。デコーダと命令の意味論は `forbid` の対象にするのが自然です（推測。デコーダは安全な Rust だけで書ける見込み）。
- `unsafe` を含むモジュールは、`cargo miri test` で一部のテストを動かすことを検討する（nightly が要るので、毎回か定期かは面談で決める）。
- GitHub Actions のワークフローは `actionlint` で検査する（手元にあることは検証済み）。`zizmor`（Actions の危険な書き方の検査）も候補（未導入。推測）。
- JS（起動用 JS とテストハーネス）は量が少ないので、整形と lint は 1 つの道具にまとめる案（例：Biome。手元にあることは検証済み）。A1 の決め方次第です。

### 3. 静的解析と動的検査

- **SAST**：Rust では clippy が主な静的検査になる。追加の SAST（CodeQL の Rust 対応、Semgrep など）は、一人の開発では効果が小さいので、**必須にしない** ことを提案します。CodeQL の Rust 対応は公開リポジトリなら無料で使える見込みですが、未検証です（推測）。
- **DAST**：Web サービスではないので、Web 向けの DAST は当てはまりません。代わりに、**信頼できない入力を受け取る部分へのファジング** を動的検査として置くことを提案します。
  - 対象：デコーダ（任意のバイト列）、ELF の読み込み（壊れた ELF）、syscall の引数の解釈、仮想ファイルシステムのパス解決。
  - 合格条件：どんな入力でも、ホスト側が panic・無限ループ・未定義動作にならない。ゲストの誤りはゲストへのシグナル（SIGSEGV、SIGILL など）か、決められた終了に変える。
  - デコーダは、ネイティブとの差分テスト（R1 の対策）と同じ基準を使い、「デコード結果の長さが 1〜15 バイトに収まる」などの性質も確かめられる（推測）。
  - 毎回の PR ではなく、短時間の実行を CI で、長時間の実行を定期または手元で行う案。`cargo-fuzz` は nightly と libFuzzer が要るので、A1 の扱いを面談で確かめる。

### 4. 秘密情報の検査

- GitHub に公開リポジトリを作るときに、**secret scanning と push protection を有効にする**（公開リポジトリでは無料で使える見込み。ドキュメント根拠、未検証）。
- 手元では、すでにある `lefthook` か `hk` の pre-commit に、秘密情報の検査（例：gitleaks。未導入）を入れる案。一人の開発なので任意でよいと考えます。
- 下の 5 の方式（トークンを持たない公開）を取れば、リポジトリに置く秘密情報はほぼなくなります。

### 5. 依存の検査とサプライチェーン

**Rust の依存**

- `cargo-deny` を CI で実行し、`deny.toml` に次を書く案（未導入。推測）：
  - `advisories`：RustSec の既知の脆弱性で失敗させる。
  - `licenses`：Apache-2.0 と両立するライセンスだけを許す（C-R1）。
  - `bans`：`iced-x86` などの x86 エミュレータ・デコーダのクレートを名前で禁止する。これで決定 D10 の禁止を機械的に確かめられる。
  - `sources`：取得元を crates.io だけに限り、git からの依存を許さない。`lanmower/blink` など C-R2 の系列が git 経由で入る道を塞ぐ。
- `Cargo.lock` をコミットし、CI では `--locked` を付ける。
- `rust-toolchain.toml` でツールチェーンの版を固定する（MSRV の決定とは別に、CI の再現性のため）。
- `cargo-machete`（手元にあることは検証済み）で使っていない依存を見つける。

**JS の依存**

- 起動用 JS は実行時の依存を持たない（C-T2）。テストハーネスの開発用の依存は、lockfile をコミットし、`pnpm install --frozen-lockfile` と `pnpm audit` を CI で実行する案。
- npm に公開するパッケージには `files` を明示して、意図しないファイルが入らないようにする。`postinstall` などのインストール時スクリプトは持たせない。

**GitHub Actions**

- サードパーティの action は **タグではなくコミットの SHA で固定** し、コメントに版を書く（例：`uses: owner/action@<40桁のSHA> # v4.2.0`）。
- ワークフローの既定の権限は `permissions: {}` か `contents: read` にし、必要なジョブだけに権限を足す。
- `actions/checkout` には `persist-credentials: false` を付ける。
- `pull_request_target` は使わない（外部の PR のコードを、書き込み権限つきで動かす危険があるため）。
- Dependabot は `github-actions` と `cargo`（と `npm`）に設定し、SHA の更新を PR で受け取る。

**公開（crates.io と npm）**

- 長く有効なトークンを GitHub の secrets に置く方式ではなく、**OIDC を使ったトークンなしの公開（Trusted Publishing）** を第一の候補にする。crates.io と npm の両方がこの方式に対応している見込みです（ドキュメント根拠ではなく記憶による。推測。導入前に公式の文書で確かめる）。
- 公開のジョブは GitHub の environment（例：`release`）に分け、**人の承認（必須のレビュアー＝自分）** と、タグの条件（`v*` だけ）を付ける。これがリードの「公開は手動承認とタグから」にそのまま当たる。
- やむを得ずトークンを使う場合は、crates.io は対象のクレートと `publish-update` だけに絞り、有効期限を付ける。npm は granular token で対象のパッケージと期限を絞る。
- crates.io・npm・GitHub のアカウントで 2 要素認証を有効にする。

**来歴（provenance）**

- npm は公開時に来歴（provenance）を付ける（Trusted Publishing では自動で付く見込み。推測）。
- wasm モジュールとネイティブのバイナリを GitHub Releases に置く場合は、GitHub の artifact attestations（`actions/attest-build-provenance`）で来歴を付ける案。
- SBOM は、実行時の依存がほぼないので優先度は低い。必要になったら `cargo-cyclonedx` などで作る（推測）。

### 6. 信頼できないゲストを動かすときの安全性

C-T8・決定 D14（既定は仮想ファイルシステム）と RAID の R6 に賛成し、STRIDE の観点で次を補います。ここは設計（Construction）で詳しく決めることで、ここでは「守るべき性質」の候補だけを挙げます。

| 脅威 | 守るべき性質（案） |
|------|----------------------|
| ゲストの入力でホストが壊れる（改ざん・権限昇格） | どんなゲストの命令・メモリ・syscall の引数でも、ホストで panic・未定義動作にならない。範囲外のアクセスはゲストへの SIGSEGV にする（3 のファジングで確かめる） |
| syscall がホストに素通しされる（権限昇格） | ゲストの syscall を番号のままホストへ渡さない。実装した syscall だけを明示的に対応付け、それ以外は `ENOSYS` を返す |
| ホストのファイルが見える（情報漏えい） | 既定は仮想ファイルシステム（C-T8）。ホストを見せる方式を選んだときも、指定したディレクトリの外へ `..` やシンボリックリンクで出られないようにする。Linux・macOS・Windows でパスの解決が違う（R3）ので、ルートの外に出ないことを OS ごとのテストで確かめる。読み取り専用の選択肢も検討する |
| ホストのプロセスが起動される（権限昇格） | ゲストの `execve`・`fork`・`clone` は、エミュレータの中でだけ扱い、ホストのプロセスを起動しない |
| ホストの環境変数・引数が漏れる（情報漏えい） | ホストの環境変数を既定ではゲストに渡さない。渡すものは利用者が明示する |
| ネットワークへの接続（情報漏えい・踏み台） | 範囲の文書では `socketpair` が出てくるが、ホストのネットワークへの接続を既定で許すかは決まっていない。面談で確かめる |
| 資源の使い尽くし（サービス妨害） | ゲストのメモリ量、スレッド数、開けるファイルの数に上限を設け、超えたらゲストにエラーを返す。上限の値は設計で決める |
| JIT の誤り（改ざん） | wasm 向けの JIT が作るコードは wasm のサンドボックスの中で動くので、ホストの安全は wasm エンジンが守る。ただし JIT がソフトウェア MMU の範囲チェックを省くと、ゲストの中の隔離が壊れるので、JIT ありとなしの差分テストで確かめる。ネイティブ向け JIT（後で考える）を作るときは、W^X などの対策を改めて検討する |

- ブラウザでの COOP/COEP（C-T11）は、ページを用意する formicarium 側の責任です（C-O3）。paludarium のテストハーネスのページでは、COOP/COEP を付けて動かす。
- このプロジェクトは「エミュレータ＝隔離の仕組み」と誤解されやすいので、README に **「paludarium はセキュリティの境界として保証しない」か「どこまでを保証するか」** を書くことを提案します。脆弱性の報告先として `SECURITY.md` を置き、GitHub の private vulnerability reporting を有効にする案も合わせて出します（推測。面談で決める）。

### 7. CI の安全のための関門（案）

| 時点 | 確認 | 失敗したとき |
|------|------|--------------|
| コミット（手元・任意） | 秘密情報の検査、`cargo fmt --check` | コミットを止める |
| PR | `clippy -D warnings`、`cargo-deny`、`actionlint`、テスト、差分テスト | マージを止める |
| PR（GitHub 側） | secret scanning の push protection | push を止める |
| 定期（例：週 1） | `cargo-deny` の advisories、長時間のファジング | Issue を作る |
| 公開 | environment の人の承認、タグの条件、Trusted Publishing、来歴の付与 | 公開しない |

- `main` の保護（必須のチェック）には、PR の行の確認を入れる案。一人でも PR を経由するなら、必須のチェックで自分の見落としを防げます。

### 8. 面談で決めること（追加分）

1. 次を固い規則（`discovered-rules.md`）として採るか、進め方（`team-practices.md`）に留めるか：
   - ゲストの入力でホストが panic・未定義動作にならない。
   - ゲストの syscall を番号のままホストへ渡さない。
   - サードパーティの GitHub Actions はコミットの SHA で固定する。
   - 長く有効な公開トークンを使わず、Trusted Publishing で公開する。
   - `unsafe` ブロックには `// SAFETY:` の理由を必ず書く。
2. サンドボックスの既定を、ファイルシステム以外（ネットワーク、環境変数、ホストのプロセス、資源の上限）にも広げるか。
3. 前提 A1 で、`cargo-deny`、`cargo-fuzz`、`miri`、Biome などの道具を「外部の部品」に含めないと決めてよいか。
4. ファジングを CI で毎回動かすか、定期や手元に限るか。
5. `SECURITY.md` と private vulnerability reporting を、公開前に用意するか。

## Positions

- AGREE: `discovered-rules.md` に人が述べた制約だけを載せ、提案の進め方を `team-practices.md` に分けたのは正しい。下の安全の規則案も、面談で確かめるまでは提案として扱うべき。
- AGREE: `lanmower/blink` を C-R2 と同じ扱いにするかを面談で確かめる方針に賛成する。採る場合は `cargo-deny` の `sources` で git 依存を塞げば機械的に守れる。
- AGREE: 公開を人の承認と `main` 上のタグから行い、取り消しは yank と deprecate で対応する読み替えに賛成する。
- OBJECT: Deployment の論点 2 が「CI から公開する場合、トークンは GitHub の secrets に置く」を前提にしている。漏えいの危険が小さい Trusted Publishing（OIDC）を第一の候補にし、トークンは期限と対象を絞った代替に留めるべき。
- OBJECT: Deployment の「マージ時の CI」がビルド、テスト、差分テスト、lint だけで、依存の検査（`cargo-deny`）、ワークフローの検査（`actionlint`）、Actions の SHA 固定と最小権限が入っていない。PR の必須チェックに加えるべき。
- OBJECT: 仮想ファイルシステムの既定（C-T8）だけでは、ゲストの安全の既定がファイルシステムにしか及ばない。syscall の素通し禁止、環境変数、ネットワーク、ホストのプロセス、資源の上限の既定を面談で確かめるべき。
- AGREE: Code Style で `unsafe` の扱いを面談に回したのは正しい。最低限の線として `undocumented_unsafe_blocks = "deny"` と、`unsafe` を使わないクレートでの `#![forbid(unsafe_code)]` を候補として示す。
- AGREE: 前提 A1 を面談で確かめる方針に賛成する。ただし A1 がどちらに決まっても、開発用の依存と GitHub Actions は残るので、それらの検査は A1 と切り離して必要になる。
