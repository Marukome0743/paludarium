## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T09:17:55Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR5.1 と NFR2.1 と 脅威表の先頭行 | NFR2.1 は「どんな ELF でも panic せず、失敗はシグナル・errno・終了コード 70 のどれかになる」と保証し、脅威表も「細工した ELF による DoS」を 起こりやすさ 高 として対策済みにしている。一方 NFR5.1 は資源の上限を一切置かず、使い切りの経路は brk・mmap だけと記している。しかし rules.md の BR1.2 は PT_LOAD の p_memsz を超える部分を 0 で埋め、BR1.3 は 8 MiB のスタックを取る。細工した ELF が巨大な p_memsz を持てば、読み込みの時点でホストが OOM（abort）になりうる。これは NFR2.1 の失敗の 3 分類のどれにも入らない。NFR2.2 の cargo-fuzz も、既定の RSS 上限（libFuzzer の 2 GB。未検証の推測）で OOM として報告し、「0 件」の合格条件を満たせなくなるおそれがある。NFR5.1 の記録は「ゲストが使える資源」の話であり、読み込み時の入力検証とは別の要件である。 | 入力検証としての上限を NFR に加える（例：ELF 全体で map するバイト数の上限、または 0 埋めのページを遅延確保にして、確保失敗を invalid-program か ENOMEM にする）。NFR5.1 と NFR2.1 の関係を明記し、脅威表の DoS 行の対策欄にその要件 ID を足す。上限を置かないと決めるなら、その残余リスクを Accepted risk として書き、NFR2.2 の合否からメモリ枯渇を除く条件を明示する。 | New |
| R-02 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR2.2、NFR4.4、NFR2.1 の合否欄 | 検証の手段が主張に届いていない。NFR4.4 の合否は「Mmu の単体テストとファジング」だが、NFR2.2 のファジング対象はデコーダの包みと ELF の読み込みの 2 つだけで、Mmu 単独の対象はない。NFR2.1 は「どんな ELF・命令のバイト列・syscall の引数でも」と言うが、実行（Cpu の命令の実行）と syscall の引数の検査にはファジングの対象がなく、合否は単体テストに頼る。単体テストで「どんな入力でも」は確かめられない。上流の要件書 FR9.3 と NFR3 は syscall の引数もファジングの対象に挙げているため、U1 での範囲がどこまでかも読み取れない。 | NFR2.2 の対象を、NFR4.4 と NFR2.1 の合否と一致させる。選択肢は 2 つ。(a) Mmu・Cpu の実行・syscall の引数を対象に加える。(b) 対象外にし、NFR2.1 と NFR4.4 の合否欄から「ファジング」を外して、U1 では何を確かめないかを明記する（U2 以降への繰り延べ先を書く）。 | New |
| R-03 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR2.3 | panic の主な原因である添字アクセスと整数の算術（`clippy::indexing_slicing`、`clippy::arithmetic_side_effects` など）が lint の対象に入っていない。team.md の Code Style は unwrap・expect・panic だけを deny にしており、エミュレータではメモリや命令のデコードの添字計算が panic の最大の源になる。NFR2.3 の合否（clippy が通る）では NFR2.1 を守れない。 | 添字アクセスと算術の lint を NFR2.3 に加えるか、その代わりにファジングのビルドで overflow-checks と debug-assertions を有効にすることを NFR2.2 に書く。 | New |
| R-04 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR3.1、および tech-stack-decisions.md > ワークスペースのクレート（paludarium-harness） | NFR3.1 は「Host のクレート以外には forbid(unsafe_code)」としているが、公開しない paludarium-harness はファジングの入口（cargo-fuzz の fuzz_target! マクロ）を持つ。マクロの展開が unsafe や no_mangle を含むため、forbid と衝突する可能性が高い（未検証の推測）。また team.md は JIT も unsafe 可とするが、NFR3.1 は触れていない。 | harness と fuzz 用のクレートの扱いを NFR3.1 に明記する（例外にするか、fuzz 用を別の枠にする）。jit が U1 で unsafe を持たないことも一文で書く。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR3.3 | 行カバレッジ 80% を U1 から CI で強制すると決めたが、分母が定義されていない。harness・jit（何もしない実装）・host（unsafe）・fuzz 用のクレート・main を含めるか否かで合否が変わる。さらに BR8.1 の wasm のスレッドの確認用の単独のプログラムが対象か否かも不明。上流の要件書の NFR3 の 4 項目のうち「ファジングで panic が出ない」は NFR2.2 が担うが、traceability.json の NFR3 の target に NFR2.2 が含まれず、対応が読み取れない。 | 測る対象のクレートと除外を NFR3.3 に書く。traceability.json の NFR3 の target に NFR2.2 を足すか、NFR3 のどこにファジングが入るかを本文に書く。 | New |
| R-06 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > 信頼の境界 B2 と 要件（乱数） | B2 は乱数（AT_RANDOM）をホストとの入口と認めているが、要件がない。rules.md の BR1.3 は Host の乱数と書くだけで、OS の暗号論的な乱数であることは要求していない。musl のスタックカナリアとポインタの保護は AT_RANDOM に依存するため、予測できる値だと、ゲスト内の防御が弱くなる。さらに 差分テストでは実行ごとに変わる値を比べない扱いのため、乱数を固定値にする誘惑も生じる。 | 乱数の取得元を OS の暗号論的な乱数に限る要件（または、テスト用に固定してよい条件と、その経路が製品のビルドに入らないこと）を加える。 | New |
| R-07 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/tech-stack-decisions.md > 言語とツールチェーン、および wasm のスレッドの確認 > ビルド、CI > PR ごと | (a) コンポーネントに rust-src がない。wasm32-unknown-unknown でスレッドに要る atomics を使うには、nightly の build-std（rust-src が必要）が通常は要る（ドキュメント根拠の記憶による。未検証）。(b) PR ごとに 3 つの OS で単体テストとあるが、U1 の Host はネイティブの Linux 用だけで、macOS・Windows でホストの実装がないクレートのビルドの方針（cfg で分ける、スタブにするなど）が NFR にない。 | (a) rust-src と build-std を明記するか、「設定は記録する」の実施の担当と時期を決める。(b) 3 つの OS でのビルドの合否が U1 で何を意味するかを、NFR9.1 か tech-stack に書く。 | New |
| R-08 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/tech-stack-decisions.md > 外部の crate と道具 > 命令デコーダ、および security-requirements.md > NFR8 | デコーダの選定が「両方を試して、デコードできて wasm32 でビルドできる方」で、両方が条件を満たしたときの決め方がない。選ぶのが U1 のコード生成の中なので、決める人と記録先が不確定になる。また NFR8 の供給網は crate と action だけを対象にしており、wasm のスレッドの確認で使う npm の道具（Playwright など）とブラウザの取得、safaridriver は対象外で、版の固定とロックファイルの要件がない。 | 同点のときの決め方（例：wasm のサイズ、保守の状況、命令が読み書きするフラグの情報の有無）と記録先を決める。npm の依存にもロックファイルのコミットと版の固定を求める、または U1 の確認用の道具は製品の依存ではないと明記する。 | New |
| R-09 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/construction/u1-skeleton/nfr-requirements/security-requirements.md > NFR2.4 と 信頼の境界 B3 | NFR2.4 は「ホストのパスや環境変数を出さない」としているが、BR5.4 の「ホストのファイルが読めない」場合の使い方の誤り（終了コード 2）の表示がこの範囲に入るかが曖昧。利用者が指定したパスを自分に返すのは問題ないはずで、NFR2.4 の適用範囲（エミュレータのエラーだけか、Cli の誤りも含むか）を決めないと単体テストを書けない。 | NFR2.4 の適用範囲を、エミュレータ自身のエラー（終了コード 70）に限ると明記するか、Cli の誤りの表示に許すものを書く。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| traceability sensor（既に通過、依頼で提示） | PASS | NFR1〜NFR9 のすべてが traceability.json で NFRx.y に対応している。ただし R-05 のとおり、NFR3 と NFR2.2 の対応の注記は不足 |
| 手作業の相互参照（NFR ID と BR の参照） | 実施 | security-requirements.md の NFR ID は一意で、脅威表の参照はすべて存在する。BR3.2・BR5.2・BR5.3・BR7.1・BR9.1 との整合も確認した。矛盾は R-01・R-02 の 2 点 |

### Summary

Critical はなく、Major は 2 件（READY の基準内）。読み込み時の資源の上限がないまま、NFR2.1 が「どんな ELF でも失敗は 3 分類のどれか」と保証している点と、NFR2.1・NFR4.4 の合否がファジングの対象に届いていない点は、Construction の前に直すのが望ましい。それ以外は、細部の指定を詰める Minor の指摘である。
