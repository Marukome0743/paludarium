# 意図の整理：質問

## Sources

- [desc] Initial description: "jart/blink（C 製の x86-64 Linux ユーザーモードエミュレータ、ISC）と同等のものを Rust で再実装する。将来は formicarium のエミュレータコア（wasm モジュール 1 つ＋起動用 JS という境界）を置き換える。まずは blink と同等の既存 Rust 実装がないかを調べ、使えるものがなければ自分で作る。背景資料は formicarium の knowledge にある documents/research/cheerpx-oss.md。"
- [scope] Workflow-selected scope: `rust-blink-port`.

## Q1. Rust で作り直す一番の理由は何ですか？

formicarium の要件分析では「blink は更新が止まっているので使わない」という発言がありました。背景資料には、wasm 上では blink が高速なメモリ方式を使えないこと、blink の JIT は wasm では成り立たないことも書かれています。何を一番の理由とするかで、設計で何を優先するかが変わります。

A. upstream の blink の更新が止まっていて、自分たちで保守できるコードが要る
B. 最初から wasm で動かすことを前提に設計したい（blink の作りは wasm 向きでない）
C. Rust で書くことで、安全性と保守性を上げたい
D. A〜C のすべて
E. Not yet defined
X. Other (please specify)

[Answer]: C. Rust で書くことで、安全性と保守性を上げたい **Mode:** guided

## Q2. このエミュレータを使うのは誰ですか？（select all that apply）

A. formicarium（ブラウザ側と統合を担う。最初の利用者）
B. vivarium（formicarium を通して、CLI のバグ再現に使う）
C. 一般の利用者（ユーザーモード x86-64 Linux エミュレータの OSS として）
D. ネイティブ環境（wasm ではない Linux / macOS / Windows）で使う人
E. Not yet defined
X. Other (please specify)

[Answer]: A, B, C, D. formicarium、vivarium、一般の利用者、ネイティブ環境で使う人 **Mode:** guided

## Q3. このワークフローの「成功」は、どこまでできた状態ですか？

このワークフローには、調査・設計・実装・テスト・CI まで入っています。最初の到達点をどこに置くかを決めます。

A. 既存の Rust 実装を調べ、採用するか自作するかを決めて記録する（ここまで）
B. 自作または採用したエミュレータで、static-musl の x86-64「hello world」がネイティブ環境で動く
C. formicarium の合格判定用 probe（tokio・rayon・ファイル操作）がネイティブ環境で全項目通る
D. C に加えて、wasm モジュール 1 つ＋起動用 JS として、formicarium の Node.js Worker とブラウザで probe が通る
E. Not yet defined
X. Other (please specify)

[Answer]: D. C に加えて、wasm モジュール 1 つ＋起動用 JS として、formicarium の Node.js Worker とブラウザで probe が通る **Mode:** guided

## Q4. 「blink と同等」とは、どこまでを指しますか？

背景資料によると、blink は命令デコーダ、ALU と SSE の意味論、ソフトウェア MMU、178 個のシステムコールを持っています。最初から全部をそろえるか、必要なものから広げるかを決めます。

A. 最初から blink の機能をすべてそろえる（178 個のシステムコールを含む）
B. まずは probe と aube が必要とする範囲を作り、そこから広げる
C. blink の機能に加えて、blink に欠けているもの（eventfd、FUTEX_WAIT_BITSET、ホストに頼らない edge-triggered epoll）も最初から入れる
D. B と C の両方（必要な範囲から始め、その中で blink に欠けている部分も作る）
E. Not yet defined
X. Other (please specify)

[Answer]: D. B と C の両方（必要な範囲から始め、その中で blink に欠けている部分も作る） **Mode:** guided

## Q5. なぜ今始めるのですか？期限はありますか？

formicarium の PoC は既存の blink で進めていて、Rust 版はそれと並行して作ることになっています。

A. 期限はない。formicarium の PoC と並行して進める
B. formicarium の PoC が終わるころには、置き換えの見通しを立てたい
C. 特定の時期までに置き換えたい（時期を Other に書いてください）
D. Not yet defined
X. Other (please specify)

[Answer]: A. 期限はない。formicarium の PoC と並行して進める **Mode:** guided

## Q6. 関係者は誰ですか？（select all that apply）

成果を受け取る人や、意見を聞く必要がある人を挙げます。

A. あなた自身（一人で開発する）
B. formicarium（同じ持ち主の別リポジトリ。境界の契約を合わせる相手）
C. jart/blink の upstream（参考にする実装の作者。変更を還元するかもしれない相手）
D. 将来の OSS の利用者・貢献者
E. Not identified
X. Other (please specify)

[Answer]: A, D. あなた自身（一人で開発する）、将来の OSS の利用者・貢献者 **Mode:** guided

## Q7. 範囲や優先順位は誰が決め、進み具合はどう共有しますか？

A. すべてあなたが決める。進み具合は AI-DLC の記録と承認ゲートで足りる
B. すべてあなたが決める。加えて、節目ごとに README などに状況を書く
C. Not yet defined
X. Other (please specify)

[Answer]: A. すべてあなたが決める。進み具合は AI-DLC の記録と承認ゲートで足りる **Mode:** guided

## Q8. このワークフローの範囲は合っていますか？

このワークフローは `rust-blink-port` という計画で始めました。内容は、既存実装の調査と判断、要件と設計、エミュレータコアの実装・テスト・CI です。ブラウザ側（Worker・ページ・ファイルシステム）は formicarium の担当なので入っていません。JIT と、formicarium への組み込み作業も入っていません。

A. この範囲で合っている
B. もっと狭くする：今回は既存実装の調査と判断だけにする
C. もっと広くする：JIT も含める
D. 範囲が違う（どう違うかを Other に書いてください）
E. Not yet defined
X. Other (please specify)

[Answer]: C. もっと広くする：JIT も含める **Mode:** guided

## Q9. JIT は、どの実行環境向けに作りますか？

Q8 で、このワークフローに JIT も含めることになりました。背景資料によると、blink の JIT はネイティブの機械語をコピーする方式で、wasm では使えません。wasm 向けには、x86-64 の命令を wasm に変換する別の方式が要ります。

A. wasm 向けだけ（x86-64 → wasm）
B. wasm 向けとネイティブ向けの両方
C. まず wasm 向けを作り、ネイティブ向けは後で考える
D. Not yet defined
X. Other (please specify)

[Answer]: C. まず wasm 向けを作り、ネイティブ向けは後で考える **Mode:** guided

## Q10. JIT について、何ができたら成功としますか？

Q3 の成功条件（probe がネイティブ・Node.js の Worker・ブラウザで通る）は、JIT がなくても満たせます。JIT を含めるなら、その成功条件も決めておく必要があります。背景資料には、CheerpX 1.3.9 上で aube を動かしたときの計測値（`--version` 0.3–0.7 秒、初回 `install` 1.8–5.7 秒など）があります。

A. JIT を有効にすると、probe が全項目通ったまま、JIT なしより速くなる
B. aube の 4 コマンド（`--version`、初回 `install`、frozen install、`list`）の時間が、CheerpX 1.3.9 上の計測値と同じかそれより速い
C. 具体的な倍率や時間の目標を決める（Other に書いてください）
D. Not yet defined（調査と設計の段階で決める）
X. Other (please specify)

[Answer]: A. JIT を有効にすると、probe が全項目通ったまま、JIT なしより速くなる **Mode:** guided

## Consolidated Summary Confirmation

- Q1：Rust で作り直す一番の理由は、安全性と保守性を上げること
- Q2：利用者は formicarium、vivarium、一般の利用者（OSS）、ネイティブ環境で使う人
- Q3：成功条件は、formicarium の probe がネイティブ環境で全項目通り、さらに wasm モジュール 1 つ＋起動用 JS として Node.js の Worker とブラウザでも通ること
- Q4：「blink と同等」は、probe と aube が必要とする範囲から始めて広げ、その中で blink に欠けている eventfd・FUTEX_WAIT_BITSET・ホストに頼らない epoll も作る
- Q5：期限はなく、formicarium の PoC と並行して進める
- Q6：関係者は、あなた自身（一人で開発）と、将来の OSS の利用者・貢献者
- Q7：範囲と優先順位はすべてあなたが決め、共有は AI-DLC の記録と承認ゲートで足りる
- Q8：範囲を広げて JIT も含める
- Q9：JIT はまず wasm 向けを作り、ネイティブ向けは後で考える
- Q10：JIT の成功条件は、JIT を有効にしても probe が全項目通り、JIT なしより速くなること

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
