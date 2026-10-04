# 見つかった必須・禁止の規則：paludarium

> 人が述べた固い制約だけを載せています。出どころは、面談の Q1（外部のものの使い方。Q13 も同じ方針に置き換え）、
> Q11 の A〜D（4 つとも選択）、実現性の工程の Q3（コードを写さない）、Ideation の制約 C-R2（Blink のフォークの系列）です。
> 進め方（trunk ベース、squash マージ、テストの順番など）は `team-practices.md` にあります。

## Mandated

- ALWAYS 外部のクレートや道具を使うときは、著作権・ライセンスに問題がないことを確かめ、著作権やライセンスの問題に関わるものは自作する（面談 Q1）。
- ALWAYS 既存のクレートや道具に不具合や上手くいかないところがあれば、その部分は自作する（面談 Q1・Q14）。
- ALWAYS ゲストが実装していない syscall を呼んだら `ENOSYS` を返す。実装した syscall だけを明示的に扱う（面談 Q11 A）。
- ALWAYS ゲストにホストのファイルを見せる方式でも、`..` やシンボリックリンクで、指定したディレクトリの外へ出られないようにする（面談 Q11 B）。
- ALWAYS ゲストからどんな入力（命令のバイト列、メモリ、syscall の引数、ELF の中身）が来ても、エミュレータが panic せず、未定義動作にもならないようにし、ファジングで確かめる（面談 Q11 C）。
- ALWAYS GitHub Actions の action はコミットの SHA で固定する（面談 Q11 D）。
- ALWAYS Rust のクレートの依存は crates.io からだけ取る。ワークスペースの中のクレートを除き、git などほかの取得元からの依存は入れない（面談 Q11 D）。

## Forbidden

- NEVER ゲストの syscall を番号のままホストに渡す（面談 Q11 A）。
- NEVER 他のプロジェクト（jart/blink、nixvm など）のコードを写す。動作と設計を参考にするだけにする（実現性の工程 Q3、制約 C-T3）。
- NEVER Blink ベースの webix・portabox の系列と、その元になった Blink のフォーク `lanmower/blink` を、参照・依存・取得・実行する（履歴にマルウェアがあった。制約 C-R2、背景資料 `knowledge/documents/research/cheerpx-oss.md`）。
