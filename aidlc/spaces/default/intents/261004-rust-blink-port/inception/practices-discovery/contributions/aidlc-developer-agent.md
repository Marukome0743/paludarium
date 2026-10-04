**Collaborator:** aidlc-developer-agent

## Contribution

開発者の立場からの独立レビューです。担当は、命名、層とモジュールの境界、エラー処理、`unsafe` の方針、ワークスペースの構成、Rust と起動用 JS の書き方です。リポジトリにはまだコードも `Cargo.toml` もありません（リードの `evidence.md` で確認済み）。そのため、以下はすべて面談で確かめるための「提案」です。根拠は、制約の一覧（C-T1〜C-T11、C-R2）、範囲の文書、意図書の要約です。下の「検証済み／ドキュメント根拠／推測」は根拠の種類を表します。

### 1. 層とモジュールの境界（Code Style または Way of Working に追記する提案）

製品の中身を次の層に分け、依存は一方向（上の層から下の層へ）に限ることを提案します。ネイティブと wasm の違いは、一番下の「ホスト」の層だけに閉じ込めます。こうしておけば、段階 3（wasm）と段階 4（macOS・Windows）は、ホストの層を足すだけで済みます（R2 の対策。範囲の文書「段階 1 の設計で、wasm への移しやすさを意識しておく」）。

| 層 | 役割 | ホストへの依存 |
|----|------|----------------|
| decoder | x86-64 の命令のバイト列を、命令の表現に変える。SSE 系まで | なし（純粋な関数） |
| cpu | レジスタ、フラグ、整数命令と SSE 系の命令の意味論 | なし。メモリは下の MMU の trait 経由 |
| mmu | ゲストの 64-bit アドレス空間をソフトウェアで扱う（C-T10） | なし |
| loader | static-musl の ELF を読み込み、スタックと auxv を作る（C-T4） | なし |
| linux | syscall の振り分け、fd の表、futex、epoll、eventfd、socketpair、シグナル | ホストの trait 経由のみ |
| vfs | 仮想ファイルシステム（既定、C-T8） | なし |
| host | スレッド、時計、乱数、標準入出力、ホストのファイルシステムを見せる方式（選んだときだけ） | ここだけがホストに触れる。native 版と wasm 版を持つ |
| jit-wasm | 段階 5 の wasm 向け JIT | cpu・mmu と同じ意味論に従う |

決まりの候補：

- ALWAYS ホストの機能（スレッド、時計、ファイル、標準入出力）は host 層の trait を通して使う。decoder・cpu・mmu・loader・linux・vfs から `std::thread`、`std::fs`、`std::time` を直接呼ばない。段階 1 の細い一本も、最初からこの trait を通す（後で wasm に移すときの書き直しを避けるため）。
- ALWAYS 「ゲストのアドレス」と「ホストのアドレス・`usize`」を型で分ける（例：`GuestAddr(u64)` のような newtype）。wasm32 では `usize` が 32 bit なので、混ぜると黙って切り詰められる。境界での変換は検査付き（`try_from`）にする。【推測：wasm32 の `usize` が 32 bit であることはドキュメント根拠、取り違えが実際に起きるかは推測】
- jit-wasm は、インタプリタ（cpu）と同じ差分テストに通す。JIT だけの意味論を持たない（範囲の文書の成功条件 3「JIT を有効にしても probe が全項目通る」）。

### 2. ワークスペースの構成（2 案）

| 案 | 内容 | 良い点 | 弱い点 |
|----|------|--------|--------|
| A：層ごとのクレート | `crates/paludarium-decoder`、`-cpu`、`-mmu`、`-loader`、`-linux`、`-vfs`、`-host`、`-jit-wasm`、まとめ役の `paludarium`、ネイティブの実行ファイル `paludarium-cli`、wasm の `paludarium-wasm`（cdylib）、補助の `xtask` | 依存の向きをコンパイラが強制する。層ごとに `#![forbid(unsafe_code)]` を付けられる。層ごとに `cargo test` を回せる | crates.io に公開するクレートが多くなり、一人での版の管理が重い |
| B：少数のクレート | `paludarium-core`（decoder〜vfs をモジュールとして持つ）、`paludarium-host-native`、`paludarium-wasm`、`paludarium-cli`、`xtask` | 公開と版の管理が軽い | モジュール間の依存の向きは規約とレビューでしか守れない |

開発者としては **A を基本にし、公開するのはまとめ役の `paludarium` と npm パッケージだけ（内部クレートは `publish = false` か、まとめて同じ版で出す）** を推します。依存の向きの決まり（1.）を道具で守れるからです。どちらにするかは面談で決めます。

そのほかの置き場所の提案：

- `js/`：起動用 JS（npm パッケージ）と、Node.js・ブラウザ用のテストハーネス（C-T6）。
- `tests/`：差分テストの入力（ゲストのバイナリまたはそのソース）と期待結果。基準の作り方は quality の担当に任せ、ここでは置き場所だけ決める。
- リポジトリ直下：`Cargo.toml`（`[workspace]`、`[workspace.lints]`）、`rust-toolchain.toml`、`rustfmt.toml`、JS の整形・lint の設定。

### 3. エラー処理（Code Style に追記する提案）

エミュレータでは「エラー」が 3 種類あり、混ぜると、ゲストに返すべきものでエミュレータが止まったり、逆にバグを隠したりします。

1. **ゲストに返すエラー**：syscall の errno。Rust のエラーではなく、`Errno` のような型で値としてゲストに返す。
2. **ゲストに起きる例外**：ページフォールト、未定義命令、ゼロ除算など。ゲストへのシグナル（SIGSEGV、SIGILL、SIGFPE）として扱う。`Fault` のような列挙型で表す。
3. **エミュレータ自身の問題**：未実装の命令・syscall、内部の矛盾。`Result` で呼び出し元まで返し、命令のアドレスやバイト列、syscall の番号を添えて止まる。

決まりの候補：

- NEVER ゲストが用意した入力（命令のバイト列、syscall の引数、ELF の中身）で、ホスト側が panic しない。製品のコード（テスト以外）では clippy の `unwrap_used`・`expect_used`・`panic` を deny にする。
- ALWAYS 未実装の命令は、黙って飛ばさずに「未実装」として、アドレスとバイト列を添えて止まる（または SIGILL をゲストに送る）。どちらにするかは設定で選べるようにし、テストでは止まる方にする。
- 未実装の syscall は、Linux と同じく `ENOSYS` を返しつつ、番号を記録する。テストでは記録があれば失敗にできるようにする。
- C-T2 の範囲次第では `thiserror` などのエラー用クレートも使えないので、`Display` と `std::error::Error` は手で実装する前提にする。

### 4. `unsafe` の方針（Code Style に追記する提案）

作り直しの一番の理由が安全性（決定 D3）なので、具体的な線を引くことを提案します。

- ALWAYS decoder・cpu・mmu・loader・linux・vfs の各クレートには `#![forbid(unsafe_code)]` を付ける。
- `unsafe` を許すのは host（ネイティブの OS 呼び出し、wasm のスレッドと共有メモリ）と jit-wasm だけにする。mmu の高速化で必要になったら、そのときに理由を書いて面談で例外を決める。
- ALWAYS `unsafe` のブロックには `// SAFETY:` のコメントで、守っている前提を書く。clippy の `undocumented_unsafe_blocks` を deny、rustc の `unsafe_op_in_unsafe_fn` を deny にして道具で守る。
- 差分テストとは別に、`unsafe` を含むクレートは Miri で回すかを面談で決める（Miri はスレッドや FFI に制限がある。【推測】）。

### 5. 命名（Code Style に追記する提案）

言語の標準（Rust は snake_case、型は UpperCamelCase、JS は camelCase）に従うのはリードの下書きどおりです。そのうえで、エミュレータに特有の点だけ決めておくことを提案します。

- syscall の処理は `sys_<Linux での名前>`（例：`sys_write`、`sys_futex`）。番号と errno の定数名は Linux のヘッダの名前に合わせる（`SYS_write`、`EINVAL`）。参照先の名前と一対一にすることで、Linux のドキュメントと照らし合わせやすくするため。
- 命令の処理は、Intel のマニュアルのニーモニックに合わせる（例：`op_add`、`op_movdqa`）。
- クレート名は `paludarium-` を頭に付ける。
- jart/blink の識別子をまねて名前を付けることは、C-T3（コードをコピーしない）と紛らわしくなるので避け、Intel のマニュアルと Linux の名前を基準にする。

### 6. Rust の道具の設定

- `rustfmt` は既定の設定、`clippy` は `-D warnings`（リードの下書きに同意）。`[workspace.lints]` に上の deny をまとめて書き、各クレートで `[lints] workspace = true` にする。
- pedantic のグループは、最初は有効にしない。ただし `cast_possible_truncation`・`cast_sign_loss` は、mmu・host・loader で deny にする（ゲストの 64 bit とホストの 32 bit の取り違えを防ぐため）。
- **ツールチェーン（新しい論点）**：wasm でスレッドを使う方法によっては、nightly の Rust（標準ライブラリを atomics 付きで作り直す `-Z build-std`）が要る可能性があります。【ドキュメント根拠・未検証：この環境では試していない】決定 D22（段階 1 の設計で wasm のスレッドを小さく確かめる）の結果で、stable だけで済むか、`rust-toolchain.toml` で nightly を固定するかが決まります。リードの Code Style の面談項目「MSRV と edition」に、この点を加えることを提案します。

### 7. 起動用 JS とテストハーネス

- ALWAYS 起動用 JS は、実行時の npm 依存をゼロにする（C-T2 の製品のコードに当たるため）。ES モジュールだけで書き、ビルドの手順なしで Node.js とブラウザの両方で読み込めるようにする。
- Node.js とブラウザの違い（Worker の作り方、ファイルの読み方）は、小さな差し替え用のモジュールに閉じ込め、残りは共通にする。
- 型の確認は `// @ts-check` と JSDoc で行い、TypeScript のビルドは置かない案を推します（起動用 JS を小さく保つため）。
- 整形と lint は、手元にある Biome（1 つの道具で両方できる。リードの `evidence.md` で手元にあることを確認済み）を推します。開発用の道具なので、A1 の前提（道具は「外部の部品」に含めない）が通れば C-T2 とは衝突しません。
- ファイル名は kebab-case、関数と変数は camelCase。

### 8. 面談に加えてほしい質問

1. **製品側のつなぎの部品は C-T2 の「外部の部品」に当たるか**。前提 A1 はビルドやテストの道具だけを扱っていますが、wasm と JS をつなぐ `wasm-bindgen`・`js-sys`、ネイティブの OS 呼び出しの `libc`・`windows-sys` は製品の中に入ります。使わない場合は、wasm の import/export とネイティブの FFI を自作することになり、段階 3・4 の工数が増えます。
2. ワークスペースは案 A（層ごとのクレート）と案 B（少数のクレート）のどちらにするか。crates.io に出すのはどのクレートか。
3. `unsafe` を許すクレートを host と jit-wasm に限る案でよいか。
4. 未実装の命令は「止まる」と「SIGILL を送る」のどちらを既定にするか。
5. wasm のスレッドのために nightly を使うことを受け入れるか（D22 の結果しだい）。

## Positions

- AGREE: Code Style の rustfmt と clippy（警告をエラーにする）は、一人での開発でも品質を道具で守れるので妥当。
- AGREE: Walking Skeleton を段階 1 の hello world にする案は妥当。ただし細い一本も最初から host 層の trait を通すことを条件に加えたい（wasm への移しやすさのため）。
- AGREE: `discovered-rules.md` の禁止事項（コードのコピー禁止、`lanmower/blink` を含む Blink 系列の禁止）は制約の一覧と背景資料に合っている。
- OBJECT: Code Style の「プロジェクト独自の命名規則は設けません」は、ゲストとホストのアドレスの取り違え（wasm32 で黙って切り詰め）を防げないので、`GuestAddr` のような型の区別と `sys_`／`op_` の命名だけは決まりにすべき。
- OBJECT: `unsafe` を「面談で決める」とだけ書くのは弱い。D3（安全性が作り直しの理由）に合わせ、`#![forbid(unsafe_code)]` を付けるクレートと `// SAFETY:` の必須化を具体案として面談に出すべき。
- OBJECT: 面談の項目に、製品側のつなぎの部品（`wasm-bindgen`、`libc`、`windows-sys`）が C-T2 に当たるかの質問がない。A1 は道具だけを扱っており、段階 3・4 の工数を大きく左右するので加えるべき。
- OBJECT: 面談の項目「MSRV と edition」に、wasm のスレッドのために nightly が要るかもしれない点（D22 の確認しだい）が入っていない。ツールチェーンの固定方針に直結するので加えるべき。
