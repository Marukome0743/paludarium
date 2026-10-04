# 要件分析：質問

意図書、範囲の文書、チームの進め方（`team-practices.md`）を読み、要件にするにはまだ決まっていないところを質問にしました。前の工程のレビューやフェーズ境界の確認で持ち越した点も含めています。

## Q1. JIT の「JIT なしより速い」を、どう数値で判定しますか？

意図書の成功条件は「JIT を有効にしても probe が全項目通り、Node.js の Worker で JIT なしより速い」です。レビューで、差の大きさと測り方が決まっていないと指摘されました。

A. Node.js の Worker で probe 全体を JIT あり・なしで各 10 回実行し、実行時間の中央値で JIT ありが 20% 以上短い
B. 同じ測り方で、JIT ありが 2 倍以上速い（中央値が半分以下）
C. 同じ測り方で、少しでも速く、統計的に意味のある差がある（有意水準 5%）
D. Not yet defined
X. Other (please specify)

[Answer]: C. 同じ測り方で、少しでも速く、統計的に意味のある差がある（有意水準 5%） **Mode:** guided

## Q2. 合格判定に使う probe は、どこのものを使いますか？

probe は、tokio・rayon・ファイル操作などが動くかを項目ごとに PASS/FAIL で出す小さな Rust のプログラムです。formicarium の PoC で作ることになっています。

A. formicarium の probe のソースを正とし、同じものを paludarium でもビルドして使う
B. paludarium に同じ項目の probe を持つ（formicarium と内容をそろえる）
C. Not yet defined
X. Other (please specify)

[Answer]: B. paludarium に同じ項目の probe を持つ（formicarium と内容をそろえる） **Mode:** guided

## Q3. aube の「動く」は、何ができたら合格ですか？

A. 4 つのコマンド（`--version`、初回 `install`、frozen install、`list`）が、ネイティブの x86-64 Linux で直接動かしたときと同じ標準出力と終了コードになる
B. A に加えて、aube の不具合 #1645 の再現（frozen install と `aube list` が `0.0.0` を表示する）がネイティブと同じに起きる
C. `aube --version` が動けばよい
D. Not yet defined
X. Other (please specify)

[Answer]: B. A に加えて、aube の不具合 #1645 の再現（frozen install と aube list が 0.0.0 を表示する）がネイティブと同じに起きる **Mode:** guided

## Q4. static-musl 版の aube は、どう用意しますか？

aube を static-musl の x86-64 向けにビルドできるかは、まだ確かめていません（背景資料で確かめたのは i586 の glibc 版だけ）。

A. paludarium の CI で、版を固定した aube のソースから static-musl 版をビルドする。ビルドできなければ、そこで扱いを決め直す
B. formicarium が用意する static-musl 版の aube を使う
C. Not yet defined
X. Other (please specify)

[Answer]: A. paludarium の CI で、版を固定した aube のソースから static-musl 版をビルドする。ビルドできなければ、そこで扱いを決め直す **Mode:** guided

## Q5. JIT なしでの速さに、目標を置きますか？

A. 目標は置かず、測って記録するだけにする（背景資料にある CheerpX 上の値と並べる）
B. 目標を置く（たとえば「Node.js の Worker で `aube --version` が 2 秒以内」。値は Other に書いてください）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 目標は置かず、測って記録するだけにする（背景資料にある CheerpX 上の値と並べる） **Mode:** guided

## Q6. ゲストが使える資源に上限を設けますか？

信頼できないバイナリを動かす場面があるので、セキュリティの担当から上限を設ける案が出ていました。

A. 上限を設け、既定値は変えられるようにする（例：メモリ 2 GiB、スレッド 64、開いているファイル 1024）
B. 最初は上限を設けない
C. Not yet defined
X. Other (please specify)

[Answer]: B. 最初は上限を設けない **Mode:** guided

## Q7. 「安全性と保守性を上げる」は、何で測りますか？

レビューで、意図書の理由（安全性と保守性）に測れる指標がないと指摘されました。

A. 次の 4 つを指標にする。`unsafe` がホスト接続部と JIT の外にないこと、clippy の警告がゼロ、行カバレッジ 80% 以上、ファジングで panic や未定義動作が出ないこと
B. 指標は置かず、理由としてだけ扱う
C. Not yet defined
X. Other (please specify)

[Answer]: A. 次の 4 つを指標にする。unsafe がホスト接続部と JIT の外にないこと、clippy の警告がゼロ、行カバレッジ 80% 以上、ファジングで panic や未定義動作が出ないこと **Mode:** guided

## Q8. ゲストの入出力は、どこまで扱いますか？

formicarium ではブラウザの中の端末で CLI を動かします。端末らしい入出力（画面の幅や、色付き表示の判定）が要るかを決めます。

A. 標準入力・標準出力・標準エラー、引数、環境変数を扱う。端末の機能（tty の判定や画面の幅）も扱う
B. 標準入出力、引数、環境変数だけを扱う。tty ではないものとして動かす
C. Not yet defined
X. Other (please specify)

[Answer]: A. 標準入力・標準出力・標準エラー、引数、環境変数を扱う。端末の機能（tty の判定や画面の幅）も扱う **Mode:** guided

## Q9. ネットワークはどう扱いますか？

aube は、ローカルの依存だけでも registry の名前解決を試みます（背景資料）。

A. ネットワーク（AF_INET の通信や名前解決）は、どのホストでも使えないものとしてエラーを返す。AF_UNIX の socketpair だけを扱う
B. ネイティブではホストのネットワークを使えるようにし、wasm では使えないものとしてエラーを返す
C. Not yet defined
X. Other (please specify)

[Answer]: A. ネットワーク（AF_INET の通信や名前解決）は、どのホストでも使えないものとしてエラーを返す。AF_UNIX の socketpair だけを扱う **Mode:** guided

## Q10. ゲストが別のプログラムを起動する（fork・execve）場合はどうしますか？

aube の `install` は `node --version` を起動します（背景資料）。

A. 仮想ファイルシステムにある static-musl のバイナリなら、エミュレータの中で起動できるようにする。ないものは ENOENT を返す
B. 別のプログラムの起動は扱わず、エラーを返す
C. Not yet defined
X. Other (please specify)

[Answer]: A. 仮想ファイルシステムにある static-musl のバイナリなら、エミュレータの中で起動できるようにする。ないものは ENOENT を返す **Mode:** guided

## Consolidated Summary Confirmation

- Q1：JIT の合格は、Node.js の Worker で probe 全体を JIT あり・なしで各 10 回実行し、JIT ありが少しでも速く、統計的に意味のある差がある（有意水準 5%）こと
- Q2：probe は paludarium に同じ項目のものを持ち、formicarium と内容をそろえる
- Q3：aube の合格は、4 コマンドがネイティブの x86-64 Linux と同じ標準出力・終了コードになり、不具合 #1645 の再現もネイティブと同じに起きること
- Q4：static-musl 版の aube は、paludarium の CI で版を固定したソースからビルドする。できなければ扱いを決め直す
- Q5：JIT なしの速さに目標は置かず、測って記録する（CheerpX 上の値と並べる）
- Q6：ゲストが使える資源の上限は、最初は設けない
- Q7：安全性と保守性の指標は、unsafe がホスト接続部と JIT の外にないこと、clippy の警告ゼロ、行カバレッジ 80% 以上、ファジングで panic・未定義動作が出ないこと
- Q8：標準入出力・引数・環境変数に加えて、端末の機能（tty の判定や画面の幅）も扱う
- Q9：ネットワーク（AF_INET の通信や名前解決）はどのホストでも使えないものとしてエラーを返し、AF_UNIX の socketpair だけを扱う
- Q10：仮想ファイルシステムにある static-musl のバイナリなら、エミュレータの中で起動できるようにする。ないものは ENOENT を返す

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
