# 非機能要件（u1-skeleton）：質問

チームの進め方（`team-practices.md`）と要件書の NFR1〜NFR9 で、大半は決まっています。ここでは、U1 で道具や数値を決める必要がある点だけを聞きます。

## Q1. 命令デコーダの crate はどれにしますか？

開発の進め方で「iced-x86 などの既存のデコーダを使う」と決めました。

A. iced-x86（MIT。全命令に対応、命令が読み書きするフラグの情報あり）
B. yaxpeax-x86（0BSD。小さく、wasm のサイズで有利）
C. U1 で両方を試し、hello world の命令がデコードでき、wasm32 でビルドできる方を選ぶ
D. Not yet defined
X. Other (please specify)

[Answer]: C. U1 で両方を試し、hello world の命令がデコードでき、wasm32 でビルドできる方を選ぶ **Mode:** guided

## Q2. ファジングの合格条件はどうしますか？

要件分析のレビューで、ファジングの実行量と合格条件が決まっていないと指摘されました（R-04）。

A. 道具は cargo-fuzz（libFuzzer。nightly と Linux で動く）。夜間の CI で対象ごとに 10 分ずつ回し、panic・未定義動作の検出（AddressSanitizer）が 0 件なら合格。見つかった入力は回帰テストに加える
B. A と同じで、1 対象あたり 30 分回す
C. Not yet defined
X. Other (please specify)

[Answer]: A. cargo-fuzz で、夜間の CI で対象ごとに 10 分ずつ回し、panic・未定義動作の検出が 0 件なら合格。見つかった入力は回帰テストに加える **Mode:** guided

## Q3. 依存の検査の道具はどうしますか？

チームの進め方では、ライセンス・取得元・既知の脆弱性を CI で検査すると決めました。

A. cargo-deny を使う。ライセンスは Apache-2.0 と両立するもの（MIT・Apache-2.0・BSD・ISC・0BSD・Unicode など）だけを許し、取得元は crates.io だけ、既知の脆弱性（RustSec）があれば失敗させる
B. cargo-audit（脆弱性だけ）と、ライセンスの手作業での確認
C. Not yet defined
X. Other (please specify)

[Answer]: A. cargo-deny。Apache-2.0 と両立するライセンスだけを許し、取得元は crates.io だけ、既知の脆弱性があれば失敗させる **Mode:** guided

## Q4. 行カバレッジ 80% の下限は、いつから CI で強制しますか？

U1 は最初の一本なので、テストの網羅が育つ前に下限で止まる可能性があります。

A. U1 から強制する（cargo-llvm-cov で測る）
B. U1 では測って記録するだけにし、U2 から強制する
C. Not yet defined
X. Other (please specify)

[Answer]: A. U1 から強制する（cargo-llvm-cov で測る） **Mode:** guided

## Consolidated Summary Confirmation

- Q1：デコーダは U1 で iced-x86 と yaxpeax-x86 の両方を試し、hello world の命令がデコードでき、wasm32 でビルドできる方を選ぶ
- Q2：ファジングは cargo-fuzz で、夜間の CI で対象ごとに 10 分ずつ回す。panic・未定義動作の検出が 0 件なら合格。見つかった入力は回帰テストに加える
- Q3：依存の検査は cargo-deny。Apache-2.0 と両立するライセンスだけを許し、取得元は crates.io だけ、既知の脆弱性があれば失敗させる
- Q4：行カバレッジ 80% の下限は U1 から強制する（cargo-llvm-cov で測る）

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
