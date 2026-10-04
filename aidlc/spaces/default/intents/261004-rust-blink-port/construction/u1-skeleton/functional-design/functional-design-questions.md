# 機能設計（u1-skeleton）：質問

U1 は、ネイティブの Linux で hello world を最初から最後まで動かす細い一本です。設計の大半は、これまでの工程（部品の一覧、取り決め、チームの進め方）で決まっています。ここでは、まだ決まっていない点だけを聞きます。

## Q1. 細い一本で動かす hello world は、どのプログラムにしますか？

ゲストのプログラムによって、U1 で作る命令と syscall の量が変わります。

A. Rust の static-musl の hello world（`println!`。後の probe と同じ作り方。std の起動処理のため、syscall と命令が多めに要る）
B. C を musl でビルドした最小の hello world（`write` と `exit` だけで済む。命令と syscall が最小）
C. 両方。まず B を通し、U1 の中で A まで通す
D. Not yet defined
X. Other (please specify)

[Answer]: C. 両方。まず C の最小の hello world を通し、U1 の中で Rust の static-musl の hello world まで通す **Mode:** guided

## Q2. U1 での Mmu（ゲストのメモリ）の作りはどうしますか？

A. 最初から本番と同じ形：4 KiB ページのソフトウェアのページテーブル（2 段の表）で、wasm32 でも同じに動く形にする
B. U1 だけの簡略版：連続した 1 つの領域にし、U4 でページテーブルに置き換える
C. Not yet defined
X. Other (please specify)

[Answer]: A. 最初から本番と同じ形：4 KiB ページのソフトウェアのページテーブル（2 段の表）で、wasm32 でも同じに動く形にする **Mode:** guided

## Q3. U1 での wasm のスレッドの確認は、どこまで行いますか？

これまでの決定で、U1 の完了条件に確認結果の報告を含めることになっています（Delivery Planning の Q7）。

A. 小さな確認用のプログラムで、SharedArrayBuffer を共有した 2 つの Worker が、アドレスで待つ・起こす（Atomics の wait・notify）を使えることを Node.js で確かめる。ブラウザは Chromium 系だけ。Worker を誰が作るのが妥当かも報告する
B. A に加えて、Firefox と Safari でも確かめる
C. Not yet defined
X. Other (please specify)

[Answer]: B. 2 つの Worker の wait・notify を Node.js と Chromium 系に加えて、Firefox と Safari でも確かめる。Worker を誰が作るのが妥当かも報告する **Mode:** guided

## Q4. エミュレータ自身のエラーのとき、コマンドはどの終了コードで終わりますか？

ゲストの終了コード（0〜255）と重なることは避けられません。そのため、エラーの詳細は標準エラーに必ず出します（取り決め C11）。

A. 70（BSD の EX_SOFTWARE。内部のエラーを表す慣例の値）
B. 125（ほかのコマンドを実行するツールで、ツール自身の失敗を表すことが多い値）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 70（EX_SOFTWARE） **Mode:** guided

## Consolidated Summary Confirmation

- Q1：hello world は両方。まず C の最小の hello world（write と exit だけ）を通し、U1 の中で Rust の static-musl の hello world（println!）まで通す
- Q2：Mmu は最初から本番の形。4 KiB ページのソフトウェアのページテーブル（2 段の表）で、wasm32 でも同じに動く
- Q3：wasm のスレッドの確認は、2 つの Worker の wait・notify を Node.js・Chromium 系・Firefox・Safari で確かめ、Worker を誰が作るのが妥当かも報告する
- Q4：エミュレータ自身のエラーのときの終了コードは 70（EX_SOFTWARE）。詳細は標準エラーに出す

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
