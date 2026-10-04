## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-04T08:36:31Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C2 Host の trait（spawn_thread、wait_on、Send + Sync） | C2 の spawn_thread は Box<dyn FnOnce() + Send> を受け取るが、wasm の Worker ではクロージャを渡せない。渡せるのは共有メモリとメッセージだけである。wait_on が取る &AtomicU32 も、ゲストの futex アドレスが AddressSpace（C4）の中にあるのに、C4 にそれを取り出す口が無く、つながらない。Open Questions の R-01・R-02 は未解決のままだが、C2 は U1 で凍結され、U5・U11・U12・U13 がすべてこれに乗る（unit-of-work-dependency.md の「つなぎ目」表）。形が wasm で成り立たないと、U11 で C1〜C9 を壊す変更が出て、全利用側を直すことになる。 | U1 の wasm スレッドの確認結果を待たずに、wasm で成り立つ形（スレッドはエントリの識別子と共有状態のハンドルで起動する、待機の対象はゲストのアドレスと AddressSpace 上の原子操作、など）に C2 を直す。または C2 を U1 の確認後に確定する暫定の契約と明記し、確定までに Unit が依存してよい範囲を書く。 | New |
| R-02 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C4 Mmu、C5 Cpu（run の mem 引数） | C4 は read と write（バイトのコピー）と、可変参照を取る map・unmap・protect しか持たない。(a) lock 接頭辞付き命令、xchg、cmpxchg のための原子的な読み書きが無く、futex の値の比較にも使えない（U2 の注意点にある担当未決の問題）。(b) run は不変参照の AddressSpace を取るが、他のスレッドが走る間に可変参照の map を呼ぶ共有の仕方（RwLock、ページ単位の内部可変性など）が書かれていない。(c) Jit の invalidate を、書き込みが起きたとき誰が呼ぶのか（Mmu が通知するのか）が決まっていない。実装者が推測で決めるしかなく、ドメイン設計のレビュー R-02 と同じ穴が契約にそのまま残っている。 | C4 に原子操作（例：atomic_cmpxchg、atomic_load）と、複数スレッドから使うときの共有と排他のモデルを追加し、実行可能ページへの書き込みを Jit に伝える向き（Mmu 側のコールバックなど。Mmu が Jit に依存しない形）を決める。 | New |
| R-03 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > 取り決めの一覧（C1〜C12）と C12 | unit-of-work-dependency.md の「つなぎ目」表は「Launcher（JS）と wasm モジュールの境界（u11 が作り、u14 が使う）」を挙げているが、契約の一覧に対応する行が無い。C12 は npm 利用者向けの公開 API だけで、Launcher と wasm モジュールの間（wasm の export と import、Worker の起動と共有メモリの受け渡し、Jit が作った wasm の instantiate、標準入出力をつなぐ口）は、どの契約にも無い。U14 は U11 のこの境界に依存するので、内部の契約として最も壊れやすい箇所が空白になっている。 | C13 として Launcher と wasm モジュールの境界の行と spec（import と export の一覧、Worker の起動の責任、instantiate の担当）を追加する。確認前なら、Open Questions を「確認後に C13 を確定する」という形で C13 に紐づける。 | New |
| R-04 | Major | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C10 Session::new の host 引数と Open Questions 最終行 | C10 の署名はすでに Host を公開 API に出している（利用者が Arc<dyn Host> を渡す）。一方、Open Questions は「Host を差し替えられるようにするか（公開 API に trait を出すか）」を未決としている。矛盾したまま U15 で公開されると、0.x でも Host（C2）が公開契約になり、R-01 の不安定な形が C10 経由で外に漏れる。 | 決めてから署名を書く。差し替えを許さないなら Session::new(config) にして、Host の選択は paludarium クレートの中（cfg）で行う。許すなら C2 を C10 と同じ版の扱い（Q3）にそろえる。 | New |
| R-05 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C2〜C8 の型名 | StreamId、TerminalInfo、HostFs、Prot、Backing、InodeRef、OpenFile、Stat、LoadedImage、ThreadHandle、Mount、DirEntry が、定義もなく使われている。細部は各 Unit の Functional Design という方針（方針の節）はあるが、どのクレートが持つか（C1 に入るか）も書かれていない。 | 少なくとも各型の所有クレートを表にする（C1 に置く型と各クレートの型）。 | New |
| R-06 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C1 ExitReason と components.md の ExitReason | components.md の ExitReason は属性 kind、guestRip、faultAddress、syscallNumber を持つが、C1 では Syscall に番号が無く（rax から読む前提か不明）、Halt は components.md に無い種類である。JS の PaludariumError.syscall（number）は Rust の u64 を欠損なく表せない。 | syscall 番号を CpuState のどこから読むかを明記するか、Syscall に持たせる。Halt の起源を追記する。JS 側は bigint にそろえるか、範囲を明記する。 | New |
| R-07 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C8 Kernel（Next::Blocked）と components.md の Kernel の依存 | Blocked のとき、Runtime が何を待ってどう再開するか（Host の wait_on を Kernel が呼ぶのか、Runtime か）が書かれていない。また Kernel は handle で CpuState（paludarium-cpu）を使うが、components.md の Kernel の依存に Cpu が無い。契約の表（C5 の Consumer は Runtime のみ）とも合わない。 | Blocked の再開の手順を 1 行で書き、C5 の Consumer に Kernel を足すか、CpuState を paludarium-types に移す。 | New |
| R-08 | Minor | aidlc/spaces/default/intents/261004-rust-blink-port/inception/contract-design/contract-summary.md > C11 exit_code（emulator_error）と C12 PaludariumError | エミュレータ自身のエラーの終了コードが U1 で決める未決のままで、ゲストの終了コードと区別できる範囲かどうかの保証が無い。C2〜C9 の境界での失敗の表し方（Errno と Error のどちらを返すか、LoadError から Error への変換）も、一覧では揃っていない。時間切れと再試行は無いという方針自体は明記されていて妥当。 | 終了コードは、U1 で決めるまで暫定値（ゲストと区別できる範囲）を書く。境界ごとに Errno と Error の使い分けの規則を 1 つ書く。 | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| なし（stage に宣言された検証ツールは無い） | 目視で確認 | C1〜C12 の ID は一意で、Owner は U1・U11・U14 の実在する Unit を指す。クレート名と Unit の担当（U4〜U9 が追加）は unit-of-work.md の配置と一致。依存の循環は契約の範囲では無し。ただし、unit-of-work-dependency.md の「つなぎ目」にある Launcher と wasm モジュールの境界が契約に無い（R-03）。 |

### Summary

公開の契約（C10〜C12）と、Result と ExitStatus の分け方は整っている。一方、wasm と複数スレッドで成り立たない C2・C4 の形、Launcher と wasm モジュールの境界の欠落、C10 の Host の出し方の矛盾が残り、Major が 4 件ある。ドメイン設計の R-01・R-02 が契約に持ち越されたままなので、承認の前に、この 4 件の扱い（直す、または暫定と明記する）を決めてほしい。
