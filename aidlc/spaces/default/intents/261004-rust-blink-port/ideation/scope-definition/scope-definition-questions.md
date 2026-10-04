# 範囲の定義：質問

## 前提

実現性の評価（`ideation/feasibility/feasibility-assessment.md`）では、作業を次の 5 段階に分けて見積もりました。合計の目安は 10〜21 か月で、判断による見積もりです。

- 段階 1：デコーダ・整数命令・MMU・最小の syscall。ネイティブの Linux で static-musl の hello world が動く（2〜4 か月）
- 段階 2：スレッド・futex・eventfd・epoll・ソケット・ファイル操作。ネイティブの Linux で probe が全項目通る（3〜6 か月）
- 段階 3：wasm ビルド・起動用 JS・テストハーネス。Node.js の Worker とブラウザで probe が通る（2〜4 か月）
- 段階 4：macOS と Windows のホスト（2〜5 か月）
- 段階 5：wasm 向け JIT の最小版（1〜2 か月以上）

意図書の成功条件は、段階 1〜5 のすべてを含みます。期限はありません。

## Q1. 段階をどの順番で進めますか？

順番によって、大きな不確実性（wasm のマルチスレッド、Windows ホスト）に早く気づけるかどうかが変わります。

A. 上の番号の順（1 → 2 → 3 → 4 → 5）。土台から積み上げる
B. リスクを先に：最初に wasm のマルチスレッドの小さな試作をしてから、1 → 2 → 3 → 4 → 5
C. wasm を早めに：1 の直後に、hello world を wasm でも動かす。その後 2 → 3 → 4 → 5
D. B と C の両方（試作を先にし、段階 1 から wasm でも動かす）
E. Not yet defined
X. Other (please specify)

[Answer]: A. 上の番号の順（1 → 2 → 3 → 4 → 5）。土台から積み上げる **Mode:** guided

## Q2. 最初の区切り（最小限の動くもの）をどこに置きますか？

最初の区切りまでできたら、設計の進め方が正しいかを見直します。

A. ネイティブの Linux で static-musl の hello world が動く
B. ネイティブの Linux と Node.js の Worker（wasm）の両方で hello world が動く
C. ネイティブの Linux で probe が全項目通る
D. Not yet defined
X. Other (please specify)

[Answer]: A. ネイティブの Linux で static-musl の hello world が動く **Mode:** guided

## Q3. aube を動かすことは、どの優先度にしますか？

aube は、vivarium で再現したい CLI の最初の例です。意図書では「blink と同等」の範囲を probe と aube の必要な範囲から始めることになっていますが、成功条件には probe しか入っていません。

A. Must：probe と同じく、ネイティブ・Node.js の Worker・ブラウザで aube も動くことを成功条件に加える
B. Should：probe が通ったあとに、aube も動かして時間を測る。成功条件には加えない
C. Could：このワークフローでは扱わず、後で扱う
D. Not yet defined
X. Other (please specify)

[Answer]: A. Must：probe と同じく、ネイティブ・Node.js の Worker・ブラウザで aube も動くことを成功条件に加える **Mode:** guided

## Q4. ブラウザでの合格条件に、どのブラウザを含めますか？

意図書では「ブラウザ」としか決まっていません。formicarium の PoC では、Chromium 系・Firefox・Safari のすべてを対象にしています。

A. Chromium 系だけ
B. Chromium 系と Firefox
C. Chromium 系・Firefox・Safari のすべて
D. Not yet defined
X. Other (please specify)

[Answer]: C. Chromium 系・Firefox・Safari のすべて **Mode:** guided

## Q5. 明示的に範囲外（Won't）にするものはどれですか？（select all that apply）

範囲外と決めておくと、作業が広がりすぎるのを防げます。どれも後で範囲に戻せます。

A. ネイティブ向けの JIT（意図書では「後で考える」としている）
B. 動的リンクのバイナリ（glibc の共有ライブラリを読み込むもの）。static-musl だけを対象にする
C. 32-bit x86 のゲスト
D. AVX・AVX-512 の命令（SSE 系までにする）
E. None
X. Other (please specify)

[Answer]: C, D. 32-bit x86 のゲスト、AVX・AVX-512 の命令（SSE 系までにする） **Mode:** guided

## Q6. 成果物の公開（crates.io や npm へのパッケージ公開）は、このワークフローに含めますか？

利用者には一般の OSS 利用者も含まれています。ただし、formicarium への組み込みは formicarium 側で行います。

A. 含めない。リポジトリで公開するだけにする
B. 含める。成功条件を満たしたら公開する
C. Not yet defined
X. Other (please specify)

[Answer]: B. 含める。成功条件を満たしたら公開する **Mode:** guided

## Consolidated Summary Confirmation

- Q1：段階は番号の順（1 → 2 → 3 → 4 → 5）で、土台から積み上げる
- Q2：最初の区切りは、ネイティブの Linux で static-musl の hello world が動くこと
- Q3：aube も Must とし、ネイティブ・Node.js の Worker・ブラウザで aube が動くことを成功条件に加える
- Q4：ブラウザの合格条件は Chromium 系・Firefox・Safari のすべて
- Q5：範囲外（Won't）にするのは、32-bit x86 のゲストと、AVX・AVX-512 の命令（SSE 系まで）
- Q6：成功条件を満たしたら、crates.io や npm へのパッケージ公開も行う

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
