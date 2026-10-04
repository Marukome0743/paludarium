## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T08:24:41Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/units-generation/unit-of-work-dependency.md > yaml edge block（u5-threads-futex の depends_on）と unit-of-work.md > U2 注意点 | U2 の注意点に「原子的な命令（lock 接頭辞付き、xchg）の担当を決める」とあり、担当が未決のまま残っている。一方 U5 は depends_on が [u4-memory-signals] だけで、u2 への辺がない（u4 は u1 のみに依存）。clone と futex を使う musl のゲストは lock 接頭辞付きの命令を必ず使うので、U5 の差分テストは U2 より前の状態では動かせない。DAG が許す並べ方（u1, u4, u5 の順）では、U5 が必要とする命令がまだ無い。 | 原子的な命令の担当 Unit を U2 か U5 のどちらかに決め、U2 が担当なら u5-threads-futex に u2-integer-isa への辺を足す（edge block・mermaid 図・並行の記述も直す）。U5 が担当なら U5 の内容に明記し、FR1.3 との分担を story-map に書く。 | New |
| R-02 | Major | unit-of-work-dependency.md > 「つなぎ目」「並行して作れる組み合わせ」、unit-of-work.md > U1「wasm のスレッドの確認」と末尾の Assumptions | 決定 D22 と components.md の assumption（ゲストのメモリを SharedArrayBuffer に置き全 Worker で共有できる）は、U1 の確認結果によって Mmu・Kernel の futex の持ち方・Host trait の形を変えうる。しかし unit-of-work.md の影響範囲の記述は「U11 の内容と大きさが変わる」だけで、U4（Mmu のバックエンド）・U5（futex・Host trait の拡張）への影響が書かれていない。DAG 上も U1 の確認結果を待つ辺がなく、U4・U5 は確認結果の前に進められる。結果が悪い場合、U4・U5・U7 の作り直しが U11 まで気づかれない。確認に使う wasm 用の Host（Worker・Atomics）は U11 の持ち物だが、U1 はそれに依存しない扱いで、確認の範囲（どの Host 機能を試すか）も境界が曖昧。 | 確認結果が影響しうる Unit（少なくとも U4・U5・U11）と、結果を見る時点（U1 の完了条件に含めるか、U5 の着手前の判断点にするか）を unit-of-work.md の Assumptions に明記する。確認に使う最小の Host 機能を U1 の含めるものに挙げる。 | New |
| R-03 | Minor | unit-of-work.md > U1「含めるもの」、Unit の一覧、ADR-007・components.md Runtime の depends_on | Runtime は Jit に依存する（components.md）が、U1 の「最初の版」の一覧には Jit がなく、Jit は U14 まで現れない。U1 の Runtime が Jit なしで動くための差し込み口（JIT 無効の既定、または trait）が U1 の内容に書かれていない。また Harness の最小限は「差分テストの最小限」としてだけ触れられ、部品名の対応が追いにくい。 | U1 の内容に「Runtime が Jit を任意の部品として扱う口（既定は無効）」を明記し、Harness の最初の版が U1 に入ることを一覧に書く。 | New |
| R-04 | Minor | unit-of-work-dependency.md > 「つなぎ目」表（Host の trait の行） | Host の trait の拡張者として u5・u9・u11・u12・u13 を挙げているが、U7 の Vfs（ホストのディレクトリを見せる方式、FR3.2）は Host の「ホストのファイルの読み書き」を使う（components.md Vfs depends_on Host）。U1 の Host が持つファイル操作の範囲と、U7 が足す分の境界が書かれていない。 | Host の trait のうち、ホストのファイルの操作を U1 が持つのか U7 が足すのかを、つなぎ目の表と U7 の内容に明記する。 | New |
| R-05 | Minor | unit-of-work.md > Unit の一覧（大きさ列）と Q2 の回答 | Q2 は「1 つの Unit は数週間で終わる」を選んでいるが、U11 と U14 が XL、U1・U2・U5・U13 が L。U11 は wasm の Host・起動用 JS・Node.js と 3 種類のブラウザのハーネス・probe と aube の確認を 1 つに含む。U1 も 9 クレートの最初の版・CI・ファジングの入口・wasm の確認を含む。大きさは相対的な見積もりという assumption はあるが、Q2 の回答との食い違いが明示されていない。 | XL の 2 つは分割するか（例：U11 を wasm の Host と起動用 JS／ハーネスとブラウザの確認に分ける）、Q2 からの意図的な逸脱として理由を書く。U1 の実績で見直すことは Delivery Planning への申し送りに加える。 | New |
| R-06 | Minor | unit-of-work.md > Unit の一覧（Kind 列）と各 Unit の定義 | Kind の付け方が内容と合わない箇所がある。U1 は Cli（実行ファイル）と CI を含むが library。U11 は npm のパッケージ（起動用 JS）とハーネスを含むが library。kind は Construction でどの設計成果物を課すかを決めるので、U11 に packaging 相当の設計が落ちる可能性がある。 | U1・U11 の kind が内容に合うか見直す。library のままにするなら、起動用 JS やコマンドの扱いを implementation notes に書く。 | New |
| R-07 | Minor | unit-of-work.md 全体（Step 5 の要求項目） | 段階の定義は Unit ごとの「Deployment model（standalone・shared・embedded）」を求めているが、表の「配置」列はクレートの置き場所で、配備形態ではない。Unit 単位で、公開するか内部だけか（U15 で公開するクレート・コマンド・npm のどれに入るか）が読み取れない。 | 各 Unit に配備形態（embedded／shared／standalone）を一列足す。 | New |
| R-08 | Minor | unit-of-work.md > U1 と U4 の内容、story-map の FR2.1・FR2.2 | brk は U1（最小限の syscall）と U4（メモリの syscall、FR2.2）の両方に出る。ゲストのメモリの syscall の持ち主が 2 か所に分かれ、同じ syscall 振り分け表・Mmu の領域管理を U1 と U4 が触る。また U4・U7・U9 は並行できるとされるが、いずれも paludarium-kernel の振り分け表を足すので、同じファイルへの変更が衝突しやすい（squash マージの運用）。 | brk の持ち主を 1 つに決める（U1 は最小実装、U4 が完成させる、など）。並行する Unit が同じクレートを触る点を、Delivery Planning への注意として dependency 文書に書く。 | New |
| R-09 | Minor | unit-of-work-story-map.md > FR5・FR5.1、traceability.json > FR5.1 の target | FR5.1（Linux・macOS・Windows で動く）の主担当が U1（Linux だけ）で、macOS・Windows は U12・U13。U1 の完了で FR5.1 が満たされたように読めるため、トレーサビリティの根拠として弱い。また NFR1〜NFR9（例：NFR2 堅さ、NFR7 時間切れ、NFR8 供給網）はどの Unit にも割り当てられていない。ストーリー省略時は FR だけの列挙で足りるが、NFR の持ち主が見えない。 | FR5.1 は U12・U13 を含む複数 Unit の対応として明記する。NFR を、少なくとも U1（CI・ファジング）や U15 に紐づける補足表を足す。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| 検証ツール（この段階の定義にはなし） | 実行せず | 段階の定義は検証ツールを挙げていない。代わりに、edge block の 15 Unit の名前・depends_on を読んで確かめた（未検証の部分はない）。名前は重複なく、depends_on はすべて宣言済みの Unit を指し、自己依存・循環は見当たらない（u1→u2→u3→u10、u1→u4→u5→u6/u8→u10 など、辺をたどって確認）。kind はすべて許される値。traceability.json は FR1〜FR10 と子の FR の計 51 件を列挙し、story-map の表の Unit と照合して食い違いは見つからなかった。 |

### Summary

DAG は循環がなく、U1 は端から端まで動く最初の一本として成立している。要件の割り当ても漏れがない。ただし、原子的な命令の担当と U5 の依存辺の欠け（R-01）、wasm のスレッド確認の結果が U4・U5 に及ぶ影響の未記載（R-02）は、承認の前に人が判断するのが望ましい。残りは軽微な補足である。
