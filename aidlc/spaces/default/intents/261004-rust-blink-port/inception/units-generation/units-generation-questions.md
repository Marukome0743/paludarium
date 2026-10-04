# 作業単位への分割：質問

部品の一覧（`components.md`）の 12 部品と要件書の FR を、作る単位（Unit）に分けます。チームの進め方では「最初に端から端まで動く細い一本を作る」と決まっているので、最初の Unit は段階 1 の hello world が動く最小の一本にします。

## Q1. Unit はどう分けますか？

A. 混合：最初の Unit は、hello world を端から端まで動かす細い一本（Decoder・Mmu・Cpu の最小限・Loader・Kernel の最小限・ネイティブの Host・Runtime・Cli・差分テストの最小限）。その後の Unit は、機能ごとに分ける（SSE、スレッドと同期、イベントとソケット、ファイルシステム、別プログラムの起動、wasm と起動用 JS、macOS、Windows、JIT、公開など）
B. 部品ごと：1 部品を 1 Unit にする（Decoder、Mmu、Cpu…）。最初の Unit だけでは何も動かない
C. 段階ごと：段階 1〜5 をそれぞれ 1 Unit にする（Unit が大きくなる）
D. Not yet defined
X. Other (please specify)

[Answer]: A. 混合：最初の Unit は hello world を端から端まで動かす細い一本。その後の Unit は機能ごとに分ける **Mode:** guided

## Q2. Unit の大きさはどのくらいにしますか？

A. 細かめ（12〜16 個）。1 つの Unit は数週間で終わる大きさ
B. 粗め（6〜8 個）。1 つの Unit は 1〜2 か月
C. Not yet defined
X. Other (please specify)

[Answer]: A. 細かめ（12〜16 個）。1 つの Unit は数週間で終わる大きさ **Mode:** guided

## Q3. コードの置き方（Rust のクレートの分け方）はどうしますか？

A. Cargo のワークスペースで、部品ごとにクレートを分ける（`paludarium-decoder` など）。公開するのは、まとめ役のクレート `paludarium`、コマンド、npm のパッケージ
B. 1 つのクレートの中で、部品ごとにモジュールを分ける
C. Not yet defined
X. Other (please specify)

[Answer]: A. Cargo のワークスペースで部品ごとにクレートを分ける。公開するのはまとめ役の paludarium、コマンド、npm のパッケージ **Mode:** guided

## Q4. 依存のない Unit どうしを、並行して作ってよいですか？

開発者は一人ですが、AI が複数の Unit を並行して作ることはできます。

A. よい。並行して作れる組み合わせを記録しておき、実際の順番は次の Delivery Planning で決める
B. 並行させず、1 つずつ順番に作る
C. Not yet defined
X. Other (please specify)

[Answer]: A. よい。並行して作れる組み合わせを記録し、実際の順番は Delivery Planning で決める **Mode:** guided

## Plan Approval

分割の計画：15 Unit。最初の U1（u1-skeleton）は、ネイティブの Linux で hello world を端から端まで動かす細い一本。その後、機能ごとの Unit（整数命令、SSE、メモリとシグナル、スレッドと futex、イベントとソケット、仮想ファイルシステム、別プログラムの起動、入出力と端末、probe と aube、wasm と起動用 JS、macOS、Windows、JIT、公開）。並行できる組み合わせは、U1 の後の U2・U4・U7・U9 と、U10 の後の U11・U12・U13。

- Approve Plan
- Revise Plan

[Answer]: Approve Plan

## Consolidated Summary Confirmation

- Q1：最初の Unit は hello world を端から端まで動かす細い一本。その後の Unit は機能ごとに分ける
- Q2：細かめ（12〜16 個）。1 つの Unit は数週間で終わる大きさ
- Q3：Cargo のワークスペースで部品ごとにクレートを分ける。公開するのはまとめ役の paludarium、コマンド、npm のパッケージ
- Q4：依存のない Unit は並行して作ってよい。実際の順番は Delivery Planning で決める
- 計画：15 Unit（U1〜U15）で承認済み

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
