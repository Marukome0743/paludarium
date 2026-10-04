# 作る順番の計画：質問

Unit の依存関係（`unit-of-work-dependency.md`）の中で、どの順番で作るかを決めます。ここでは、1 つの Unit（または関連する数個の Unit）を設計からコードまで通して作り、動くものを出すひと区切りを **Bolt** と呼びます。

前提：
- 最初の Bolt は、細い一本の U1（u1-skeleton）です（team-practices の Walking Skeleton）。
- これまでの 3 回のレビューで、同じ指摘が繰り返し出ています。U1 で行う wasm のスレッドの確認の結果によっては、Mmu・Host の trait・取り決め C2・C4 の形が変わりうる、というものです。

## Q1. U1 の後は、何を優先して並べますか？

A. リスクの大きいものを先に：スレッドと futex（U5）、epoll（U6）を早めに作り、ホストの中では差の大きい Windows（U13）を macOS（U12）より先にする
B. 価値の大きいものを先に：probe と aube がネイティブの Linux で動く（U10）までの最短の道を先に通す
C. Unit の番号の順に作る
D. Not yet defined
X. Other (please specify)

[Answer]: A. リスクの大きいものを先に：U5・U6 を早めに、Windows（U13）を macOS（U12）より先にする **Mode:** guided

## Q2. 順番を、点数で決める方法（価値・急ぎ・リスクの大きさを作業量で割って並べる WSJF）を使いますか？

A. 使わない。Q1 の方針と依存関係で決め、理由を文章で残す
B. 使う。各 Bolt に点数を付けて並べる
C. Not yet defined
X. Other (please specify)

[Answer]: B. 使う。各 Bolt に点数を付けて並べる **Mode:** guided

## Q3. 1 つの Bolt の大きさはどうしますか？

A. 1 つの Unit を 1 つの Bolt にする
B. 関連する Unit をまとめる（例：U4 と U5、U12 と U13）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 1 つの Unit を 1 つの Bolt にする **Mode:** guided

## Q4. 作る段階（Construction）の進め方はどうしますか？

A. 1 つずつ：1 つの Unit の設計からコードまでを終えてから次へ進む。各 Unit の完了時に、あなたが結果を確かめる（AI-DLC の既定）
B. 並行：同じ工程（設計、コードなど）を、依存のない複数の Unit でまとめて進める
C. Not yet defined
X. Other (please specify)

[Answer]: A. 1 つずつ：1 つの Unit の設計からコードまでを終えてから次へ。各 Unit の完了時にあなたが確かめる **Mode:** guided

## Q5. 外からの事情で待つことになりそうなものは、次のもので合っていますか？

- aube のソースと版（aube のリポジトリ）
- formicarium の probe の項目の一覧
- GitHub Actions の macOS の実行環境で、本物の Safari を動かせること
- crates.io と npm の Trusted Publishing

A. 合っている。この 4 つを記録する
B. ほかにもある（Other に書いてください）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 合っている。この 4 つを記録する **Mode:** guided

## Q6. この開発で一番心配なことは何ですか？（早めに手を打ちます）

A. wasm でマルチスレッドが作れるか
B. Windows のホストで Linux の syscall を再現できるか
C. 命令の意味の誤りが気づかれずに残ること
D. 範囲が大きすぎて、一人では長期化して止まること
E. Not yet defined
X. Other (please specify)

[Answer]: A, C. wasm でマルチスレッドが作れるか、命令の意味の誤りが気づかれずに残ること **Mode:** guided

## Q7. U1 での wasm のスレッドの確認の結果は、いつ見て、どう扱いますか？

A. U1 の完了条件に確認の結果の報告を含める。結果が悪ければ、U4・U5 に入る前に、Mmu・Host の trait・取り決め C2・C4 の形を見直す
B. 確認の結果は記録するだけにし、見直しは U11（wasm）で行う
C. Not yet defined
X. Other (please specify)

[Answer]: A. U1 の完了条件に確認の結果の報告を含める。結果が悪ければ、U4・U5 に入る前に Mmu・Host の trait・取り決め C2・C4 の形を見直す **Mode:** guided

## Q8. 作る段階は、誰が進めますか？

A. このセッションで、あなたと AI で進める（一人での開発）
B. チームごとに Unit を受け持ち、それぞれが承認する
C. Not yet defined
X. Other (please specify)

[Answer]: A. このセッションで、あなたと AI で進める（一人での開発） **Mode:** guided

## Q9. 各 Unit の完了時に結果を確かめるコマンドは、いつ決めますか？

まだコードがないので、実際に動くコマンドはありません。

A. 今は決めず、最初の確認（U1 の完了時）で決める
B. 今決める（`cargo test --workspace` と差分テストのスクリプトを想定。Other に具体的に書いてください）
C. Not yet defined
X. Other (please specify)

[Answer]: A. 今は決めず、最初の確認（U1 の完了時）で決める **Mode:** guided

## Consolidated Summary Confirmation

- Q1：U1 の後はリスクの大きいものを先に。U5（スレッドと futex）・U6（epoll）を早めに、Windows（U13）を macOS（U12）より先にする
- Q2：WSJF（価値・急ぎ・リスクの大きさを作業量で割った点数）で各 Bolt を並べる
- Q3：1 つの Unit を 1 つの Bolt にする
- Q4：1 つずつ進める。1 つの Unit の設計からコードまでを終えてから次へ。各 Unit の完了時にあなたが確かめる
- Q5：外からの待ちは、aube のソースと版、formicarium の probe の項目、GitHub の macOS で本物の Safari、crates.io と npm の Trusted Publishing の 4 つ
- Q6：一番の心配は、wasm でマルチスレッドが作れるかと、命令の意味の誤りが気づかれずに残ること
- Q7：U1 の完了条件に wasm のスレッドの確認結果の報告を含める。結果が悪ければ、U4・U5 の前に Mmu・Host の trait・C2・C4 を見直す
- Q8：このセッションで、あなたと AI で進める
- Q9：確認コマンドは今は決めず、U1 の完了時に決める

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
