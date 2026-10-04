# 開発の進め方：質問

リリースエンジニアの下書き（`team-practices.md`、`discovered-rules.md`、`evidence.md`）と、品質・開発・セキュリティの各担当のレビュー（`contributions/`）をもとに作りました。各質問の A が、下書きとレビューで多かった提案です。

## Q1. 「外部の部品を使わない」は、どこまでを指しますか？

Ideation で「デコーダも含めてすべて自作し、外部の部品は使わない」と決めました。ただし、次の 2 種類のものを外部の部品に含めるかは決まっていません。開発とセキュリティの担当から、wasm と Windows の工数を大きく左右すると指摘がありました。

- ビルド・テスト・CI の道具（テストの補助、カバレッジ計測、依存の検査、ブラウザのテスト）
- 製品に入る、OS やブラウザとつなぐための薄い部品（`libc`、`windows-sys`、`wasm-bindgen`）

A. エミュレータの中身（デコーダ・CPU・MMU・syscall・ファイルシステム・JIT）は自作する。道具は外部のものを使ってよい。OS やブラウザとつなぐ薄い部品も使ってよい
B. 道具は外部のものを使ってよい。製品に入るものは、OS やブラウザとつなぐ部品も含めてすべて自作する
C. 道具も含めて、すべて自作する
D. Not yet defined
X. Other (please specify)

[Answer]: X. Other — 基本的には外部のものを使ってよい。著作権やライセンスの問題に関わるものは自作する。既存のものに不具合や上手くいかないところがあれば、その部分は自作する（ユーザー発言：「使う使わないの技術選定ですが、基本的には他のものを使ってもいいです。ただ、著作権的な問題とかライセンス問題とかそういった所に関わるものは自作にして下さい。また、既存のものがあってもそれに不具合というか上手くいかないところがあれば、そこは自作しましょう。」。当初の回答 C を置き換え） **Mode:** chat

## Q2. 変更を main に入れる方法はどうしますか？

A. 短命なブランチから Pull Request を作り、CI が通ってから main に squash で入れる
B. 一人なので main に直接 push する。CI は push のたびに回す
C. Not yet defined
X. Other (please specify)

[Answer]: A. 短命なブランチから Pull Request を作り、CI が通ってから main に squash で入れる **Mode:** guided

## Q3. 細い一本を先に作りますか？

walking skeleton（細い一本）とは、全体を端から端まで通す最小の版を最初に作ることです。部品がつながることを確かめてから、本格的な機能を足します。

A. はい。段階 1 の hello world をその一本にする。ネイティブの Linux で直接動かした結果とエミュレータの結果（出力と終了コード）が一致することをコマンドで示し、あなたが確かめてから先へ進む
B. いいえ。最初から段階ごとに普通に作る
C. Not yet defined
X. Other (please specify)

[Answer]: A. はい。段階 1 の hello world をその一本にする。ネイティブの Linux で直接動かした結果とエミュレータの結果（出力と終了コード）が一致することをコマンドで示し、あなたが確かめてから先へ進む **Mode:** guided

## Q4. テストはどの順番で書きますか？

A. 混合（custom）：命令・syscall・プログラムの単位では、ネイティブの x86-64 Linux で得た期待結果を先に用意してから実装する。内部の部品は、実装の後に単体テストを書く
B. TDD：すべての部品で、テストを先に書いてから実装する
C. test-after：実装してから、その層のテストを書く（AI-DLC の既定）
D. Not yet defined
X. Other (please specify)

[Answer]: A. 混合（custom）：命令・syscall・プログラムの単位では、ネイティブの x86-64 Linux で得た期待結果を先に用意してから実装する。内部の部品は、実装の後に単体テストを書く **Mode:** guided

## Q5. カバレッジ（テストが通ったコードの割合）の下限はどうしますか？

A. 行カバレッジ 80% を下限にする（Linux のネイティブで測る）。あわせて「差分テストのある命令の割合」も記録する
B. 行カバレッジの下限は設けず、「差分テストのある命令の割合」だけを記録する
C. 行カバレッジ 80% だけにする
D. Not yet defined
X. Other (please specify)

[Answer]: A. 行カバレッジ 80% を下限にする（Linux のネイティブで測る）。あわせて「差分テストのある命令の割合」も記録する **Mode:** guided

## Q6. 差分テストの期待結果は、どう用意しますか？

差分テストでは、同じゲストをネイティブの x86-64 Linux で直接動かした結果と、エミュレータの結果を比べます。開発機は Windows で、macOS の CI は arm64 の可能性があるため、どこでもネイティブで実行できるわけではありません。

A. 期待結果はネイティブの x86-64 Linux で作り、リポジトリに保存する。どの OS でも、保存した結果と比べる。作り直しは別のジョブで行う
B. 毎回、CI の x86-64 Linux で期待結果を作って比べる
C. Not yet defined
X. Other (please specify)

[Answer]: B. 毎回、CI の x86-64 Linux で期待結果を作って比べる **Mode:** guided

## Q7. CI で何をいつ確かめますか？

A. 変更のたびに：3 つの OS の単体テスト、lint、依存の検査。段階ごと：その段階に入ったら probe と aube の合否を必須にする。夜間：ブラウザのテスト、速さの測定、ファジング（でたらめな入力で壊れないかを試す）
B. 変更のたびには Linux だけを確かめ、それ以外は夜間に回す
C. Not yet defined
X. Other (please specify)

[Answer]: A. 変更のたびに：3 つの OS の単体テスト、lint、依存の検査（外部の crate が入っていないことの確認）。段階ごと：その段階に入ったら probe と aube の合否を必須にする。夜間：ブラウザのテスト、速さの測定、ファジング **Mode:** guided

## Q8. パッケージの公開はどうしますか？

A. タグを打つと CI から公開する。公開の前にあなたの承認を挟む。トークンを保存しない方式（Trusted Publishing）を優先する。段階ごとに 0.x 版を出してよい
B. 公開は成功条件を満たした最後に一度だけ、手元から行う
C. Not yet defined
X. Other (please specify)

[Answer]: A. タグを打つと CI から公開する。公開の前にあなたの承認を挟む。トークンを保存しない方式（Trusted Publishing）を優先する。段階ごとに 0.x 版を出してよい **Mode:** guided

## Q9. Rust のコードの書き方の決まりはどうしますか？

`unsafe` は、Rust の安全性の検査を外して書くコードです。

A. rustfmt で整形し、clippy の警告はエラーにする。デコーダや CPU などの層では `unsafe` を禁止し、ホストとの接続部と JIT だけで許す。`unsafe` には理由のコメントを必須にする。ゲストからの入力でエミュレータが panic しないよう、`unwrap` なども禁止する
B. rustfmt と clippy は使うが、警告はエラーにしない。`unsafe` は必要なところで自由に使う
C. Not yet defined
X. Other (please specify)

[Answer]: A. rustfmt で整形し、clippy の警告はエラーにする。デコーダや CPU などの層では unsafe を禁止し、ホストとの接続部と JIT だけで許す。unsafe には理由のコメントを必須にする。unwrap なども禁止する **Mode:** guided

## Q10. Rust のツールチェーンはどうしますか？

wasm でスレッドを使うには、nightly（開発版）の Rust が要るかもしれません（ドキュメント上の情報で、未検証）。

A. stable に固定する。wasm のスレッドで nightly が要るとわかったら、wasm のビルドだけ nightly にする
B. 最初から nightly にする
C. Not yet defined
X. Other (please specify)

[Answer]: B. 最初から nightly にする **Mode:** guided

## Q11. 次の安全のための決まりのうち、必ず守る規則（ALWAYS / NEVER）にするものはどれですか？（select all that apply）

A. ゲストの syscall を番号のままホストに渡さない。実装していないものは ENOSYS（未実装）を返す
B. ホストのファイルを見せる方式でも、`..` やシンボリックリンクで指定したディレクトリの外へ出られないようにする
C. ゲストからどんな入力が来ても、エミュレータが panic せず、未定義動作にもならないようにする（ファジングで確かめる）
D. GitHub Actions はコミットの SHA で固定し、依存は crates.io からだけ取る
E. None
X. Other (please specify)

[Answer]: A, B, C, D. 未実装の syscall は ENOSYS、指定ディレクトリの外へ出さない、panic・未定義動作にしない（ファジング）、Actions の SHA 固定と crates.io からだけの依存 **Mode:** guided

## Q12. Safari での合格は、どう確かめますか？

A. macOS の CI で本物の Safari を動かして確かめる
B. Safari と同じエンジン（WebKit）を使うテスト用ブラウザで代わりにする
C. Not yet defined
X. Other (please specify)

[Answer]: A. macOS の CI で本物の Safari を動かして確かめる **Mode:** guided

## Q13. Q1 の「道具も含めてすべて自作」の境目を確かめます

Rust のツールチェーン（rustc・cargo・rustfmt・clippy・cargo test）や、実行環境（OS・Node.js・ブラウザ）まで自作するのは現実的ではありません。どこまでを「使ってよいもの」としますか？

A. Rust のツールチェーン（cargo test を含む）と、実行環境（OS・Node.js・ブラウザ）・GitHub Actions だけは使う。それ以外（テストの補助、カバレッジ計測、依存の検査、ブラウザの自動操作、wasm のつなぎなど）はすべて自作するか、使わない
B. A に加えて、mise で入れている CLI の道具（lint や整形など、製品に入らないもの）も使ってよい
C. A に加えて、Rust 公式の道具（rustup のコンポーネント、wasm 用の公式ターゲット）も使ってよい
D. Not yet defined
X. Other (please specify)

[Answer]: X. Other — Q1 の置き換えにより、道具の境目は「著作権・ライセンスに問題がなく、不具合がなければ外部のものを使ってよい」になった（当初の回答 C を置き換え） **Mode:** chat

## Q14. 新しい方針で、命令デコーダはどうしますか？

実現性の工程では「デコーダも自作する」と決めました（feasibility Q9）。Q1 の新しい方針では、ライセンスに問題がなく不具合がなければ、外部のものを使ってよいことになります。iced-x86 は MIT ライセンスで、Apache-2.0 の paludarium と両立します。

A. 新しい方針に従い、iced-x86 などの既存のデコーダを使う。不具合や合わないところがあれば、その部分を自作する
B. デコーダは引き続き自作する
C. Not yet defined
X. Other (please specify)

[Answer]: A. 新しい方針に従い、iced-x86 などの既存のデコーダを使う。不具合や合わないところがあれば、その部分を自作する **Mode:** guided

## Consolidated Summary Confirmation

- Q1・Q13（方針の変更）：基本的には外部のものを使ってよい。著作権やライセンスの問題に関わるものは自作する。既存のものに不具合や上手くいかないところがあれば、その部分を自作する
- Q14：命令デコーダは iced-x86 などの既存のものを使う。合わないところがあれば自作する（実現性の工程の「デコーダも自作」を変更）
- Q2：短命なブランチから Pull Request を作り、CI が通ってから main に squash で入れる
- Q3：細い一本を先に作る。段階 1 の hello world で、ネイティブとエミュレータの出力と終了コードが一致することをコマンドで示し、あなたが確かめてから先へ進む
- Q4：テストの順番は混合（custom）。命令・syscall・プログラムは期待結果を先に用意し、内部の部品は実装の後に単体テストを書く
- Q5：行カバレッジ 80% を下限にし（Linux のネイティブで測る）、差分テストのある命令の割合も記録する
- Q6：差分テストの期待結果は、毎回 CI の x86-64 Linux で作って比べる
- Q7：変更のたびに 3 つの OS の単体テスト・lint・依存の検査。段階ごとに probe と aube を必須に。夜間にブラウザ・速さ・ファジング
- Q8：タグで CI から公開し、公開前にあなたが承認する。Trusted Publishing を優先し、段階ごとに 0.x 版を出してよい
- Q9：rustfmt、clippy の警告はエラー。unsafe はホスト接続部と JIT だけに許し、理由のコメントを必須にする。unwrap なども禁止
- Q10：ツールチェーンは最初から nightly
- Q11：必ず守る規則にするのは 4 つ。未実装の syscall は ENOSYS を返す。ホストのファイルを見せても指定ディレクトリの外へ出さない。どんな入力でも panic や未定義動作にならない（ファジングで確かめる）。Actions は SHA で固定し、依存は crates.io からだけ取る
- Q12：Safari は macOS の CI で本物を動かして確かめる

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
