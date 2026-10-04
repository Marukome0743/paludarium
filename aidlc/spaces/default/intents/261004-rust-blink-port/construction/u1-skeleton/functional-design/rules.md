# ルール（u1-skeleton）

上流の成果物：
- `inception/requirements-analysis/requirements.md`
- `inception/contract-design/contract-summary.md`
- `inception/practices-discovery/team-practices.md`

根拠は `functional-design-questions.md`（Q1〜Q4）と `aidlc/spaces/default/memory/project.md` の Mandated です。

```yaml
rules:
  - id: BR1.1
    statement: 読み込めるのは、x86-64・リトルエンディアン・64 bit の ELF で、種類が ET_EXEC か ET_DYN（static-pie）で、動的リンカ（PT_INTERP）を持たないものだけ
    category: validation
    applies_to: Loader
    trigger: プログラムの読み込み
    logic: IF ELF の識別子・クラス・機械・種類・PT_INTERP のどれかが条件に合わない THEN 読み込まない
    violation: エミュレータのエラー（invalid-program）として返す。panic しない
    source: FR1.1
  - id: BR1.2
    statement: PT_LOAD のセグメントは、フラグどおりの権限で 4096 バイト境界に置き、ファイルにない部分（bss）は 0 で埋める
    category: constraint
    applies_to: Loader, Mmu
    trigger: セグメントの配置
    logic: IF セグメントが重なる、またはアドレス空間の範囲外 THEN 読み込まない
    violation: エミュレータのエラー（invalid-program）
    source: FR1.1
  - id: BR1.3
    statement: 最初のスタックには argc・argv・envp・補助ベクタを Linux と同じ並びで積み、16 バイト境界にそろえる。補助ベクタは AT_PHDR・AT_PHENT・AT_PHNUM・AT_PAGESZ（4096）・AT_BASE（0）・AT_FLAGS（0）・AT_ENTRY・AT_UID・AT_EUID・AT_GID・AT_EGID（どれも 1000）・AT_SECURE（0）・AT_CLKTCK（100）・AT_HWCAP（0）・AT_RANDOM・AT_EXECFN・AT_NULL
    category: constraint
    applies_to: Loader
    trigger: 起動の準備
    logic: スタックは 8 MiB をアドレス空間の上の方に取り、上から順に積む。AT_RANDOM の 16 バイトは Host の乱数から取る（取り決め C2 に乱数を取る口を足す。持ち主は U1 で、壊さない追加）。AT_PHDR と AT_ENTRY には読み込みの基準アドレス（BR1.4）を足した値を入れる
    violation: 入りきらなければエミュレータのエラー
    source: FR1.1
  - id: BR1.4
    statement: ET_DYN（static-pie）は、決まった基準アドレス 0x555555554000 に置く。ET_EXEC は ELF に書かれたアドレスにそのまま置く。static-pie の再配置はゲスト自身（musl の起動処理）が行うので、Loader は再配置しない
    category: calculation
    applies_to: Loader
    trigger: セグメントの配置
    logic: 配置アドレス = 基準アドレス + p_vaddr。どちらの種類になるかは、CI でビルドした C と Rust の hello world の ELF の種類を確かめ、両方を差分テストで通す
    violation: 基準アドレスに置けなければエミュレータのエラー
    source: FR1.1
  - id: BR2.1
    statement: ゲストのメモリは 4096 バイトのページ単位で、2 段のページテーブル（上は疎な表、下は 512 ページ分の表）で管理する。wasm32 でも同じ作りにする
    category: constraint
    applies_to: Mmu
    trigger: 常に
    logic: ゲストのアドレスとホストの整数は型で分け、変換は検査付きで行う
    violation: 変換できないアドレスはフォールトとして扱う
    source: FR1.5
  - id: BR2.2
    statement: 対応のないページへのアクセスや、権限のないアクセスはフォールトとして返し、panic しない
    category: validation
    applies_to: Mmu
    trigger: 読み書き・命令の取り出し
    logic: IF ページがない、または権限がない THEN フォールト（アドレスと読み書きの別）を返す
    violation: Cpu は page-fault で止まり、Kernel がゲストに SIGSEGV を送る（U1 ではハンドラがないので終了）
    source: FR1.5, NFR2
  - id: BR2.3
    statement: brk は、最初の break（最後の PT_LOAD の終わりをページ境界に上げた所）より下には下げない。上げるときは 0 で埋めたページを足す
    category: calculation
    applies_to: Mmu, Kernel
    trigger: brk の syscall
    logic: IF 要求が最初の break より小さい、または他の領域と重なる THEN 変えずに現在の break を返す ELSE 新しい break を返す
    violation: なし（Linux と同じく現在の値を返す）
    source: FR2.1
  - id: BR3.1
    statement: syscall は rax の番号で振り分け、引数は rdi・rsi・rdx・r10・r8・r9、戻り値は rax。失敗は -errno で返す
    category: policy
    applies_to: Kernel
    trigger: Cpu が syscall で止まった
    logic: 番号の表を引いて実装を呼ぶ
    violation: なし
    source: FR2.1
  - id: BR3.2
    statement: 表にない syscall には -ENOSYS を返し、番号のままホストに渡さない
    category: policy
    applies_to: Kernel
    trigger: 未実装の番号
    logic: IF 番号が表にない THEN -ENOSYS
    violation: なし
    source: FR2.1
  - id: BR3.3
    statement: U1 で実装する syscall は、C と Rust の hello world に要るもの。write・exit・exit_group・brk・arch_prctl（ARCH_SET_FS）・set_tid_address・mmap と munmap（無名・private のみ）・rt_sigaction と rt_sigprocmask（登録のみで配送はしない）・sigaltstack・poll（記述子 0〜2）・ioctl（TIOCGWINSZ は -ENOTTY）
    category: constraint
    applies_to: Kernel
    trigger: 該当の syscall
    logic: Rust の hello world がネイティブで呼ぶ syscall を strace で確かめ、この一覧と違えば、一覧を直してから実装する
    violation: 一覧にない呼び出しは BR3.2 で -ENOSYS
    source: FR2.1, FR1.1
  - id: BR3.4
    statement: write は記述子 1 と 2 だけをホストの標準出力・標準エラーにつなぐ。それ以外の記述子には -EBADF を返す
    category: validation
    applies_to: Kernel
    trigger: write
    logic: IF 記述子が 1 か 2 THEN 書いたバイト数を返す ELSE -EBADF
    violation: なし
    source: FR2.1
  - id: BR4.1
    statement: Cpu は命令を 1 つずつ取り出してデコーダの包みで解釈し、U1 で実装した命令だけを実行する。それ以外は invalid-opcode で止まる
    category: policy
    applies_to: Cpu, Decoder
    trigger: 実行
    logic: IF デコードできない、または未実装 THEN invalid-opcode（命令のバイト列を添える）
    violation: Kernel がゲストに SIGILL を送る（U1 ではハンドラがないので終了）
    source: FR1.2, FR1.6
  - id: BR4.2
    statement: syscall 命令では、命令ポインタを次の命令に進めてから syscall で止まる
    category: policy
    applies_to: Cpu
    trigger: syscall 命令
    logic: rcx と r11 には Linux と同じく戻り先とフラグを入れる
    violation: なし
    source: FR2.1
  - id: BR4.3
    statement: Cpu は決めた命令数（予算）を実行したら budget-exhausted で止まり、実行ループに戻る
    category: policy
    applies_to: Cpu, Runtime
    trigger: 予算の使い切り
    logic: 実行ループは止める要求（kill）を確かめてから再開する。kill の要求があれば、プロセスを SIGKILL で終わらせる
    violation: なし
    source: FR9.1
  - id: BR4.4
    statement: U1 で実装する命令は、CI でビルドした C と Rust の hello world を逆アセンブルし、実際に実行される命令から決める。そこに出てくる SSE 系の命令も U1 で実装する（残りの SSE 系は U3）
    category: constraint
    applies_to: Cpu
    trigger: U1 の実装の計画
    logic: 命令の一覧はコード生成の計画に書き、命令ごとに差分テストを持つ。一覧にない命令は BR4.1 で invalid-opcode
    violation: 一覧の命令が足りなければ、差分テストが invalid-opcode で落ちる
    source: FR1.2, FR1.3
  - id: BR4.5
    statement: U1 ではシグナルの登録（rt_sigaction など）を記録するだけで、配送はしない。フォールトや未対応の命令では、登録の有無にかかわらず、プロセスを該当のシグナルで終わらせる
    category: policy
    applies_to: Kernel
    trigger: フォールト・未対応の命令
    logic: 配送は U4 で実装する。それまではハンドラを持つゲストでもネイティブと結果が違いうる（hello world ではフォールトは起きない）
    violation: なし
    source: FR2.9
  - id: BR5.1
    statement: exit_group と exit（U1 では 1 スレッドなので同じ）の終了コードは、下位 8 bit を ExitStatus の exited にする
    category: calculation
    applies_to: Kernel
    trigger: exit_group・exit
    logic: code & 0xff
    violation: なし
    source: FR1.1
  - id: BR5.2
    statement: コマンドの終了コードは、ゲストが終わればその終了コード、シグナルで終われば 128 + シグナル番号、エミュレータ自身のエラーなら 70
    category: policy
    applies_to: Cli
    trigger: 実行の終わり
    logic: エラーのときは、種類・命令のアドレス・バイト列・syscall の番号を標準エラーに出す
    violation: なし
    source: FR1.1
  - id: BR5.3
    statement: コマンドの引数の誤り（知らないオプション、プログラムの指定がない、U1 では未実装の --mount）では、使い方を標準エラーに出して終了コード 2 で終わる。--env KEY=VALUE は U1 から受け付ける
    category: validation
    applies_to: Cli
    trigger: 引数の解釈
    logic: IF 引数が正しくない THEN 2 で終わる
    violation: なし
    source: FR1.1
  - id: BR5.4
    statement: コマンドで指定した <program> はホストのファイルとして読み、ゲストの中の /<ファイル名> に置いて実行する。argv[0] には指定した文字列をそのまま入れる
    category: policy
    applies_to: Cli
    trigger: 実行の準備
    logic: IF ホストのファイルが読めない THEN 使い方の誤りとして 2 で終わる
    violation: なし
    source: FR1.1
  - id: BR6.1
    statement: ホストの機能（標準入出力など）は、すべて Host の trait を通して使う。U1 で作る実装はネイティブの Linux 用だけ
    category: constraint
    applies_to: Host, Kernel, Runtime
    trigger: 常に
    logic: Host 以外のクレートでは unsafe を禁止し、std::fs・std::thread・std::time を直接呼ばない
    violation: lint（forbid(unsafe_code)）と依存の検査で CI が落ちる
    source: FR5.1
  - id: BR7.1
    statement: 差分テストでは、CI の x86-64 Linux で同じゲストをネイティブに直接動かした結果と、エミュレータの結果を比べる。比べるのは標準出力・標準エラーのバイト列と終了状態
    category: validation
    applies_to: Harness
    trigger: CI の実行
    logic: IF どれかが一致しない THEN テストは失敗
    violation: CI が落ちる
    source: FR9.1
  - id: BR7.2
    statement: 差分テストのゲスト（C の hello world と Rust の hello world）は、CI の中でソースからビルドする（Q1）
    category: policy
    applies_to: Harness
    trigger: CI の実行
    logic: C は musl でビルドし、Rust は x86_64-unknown-linux-musl でビルドする
    violation: ビルドできなければ CI が落ちる
    source: FR9.1
  - id: BR8.1
    statement: wasm のスレッドの確認では、SharedArrayBuffer を共有した 2 つの Worker の片方が値を待ち、もう片方が書いて起こす。5 秒以内に正しい値で起きれば合格とする。Node.js・Chromium 系・Firefox・Safari で確かめる（Q3）
    category: validation
    applies_to: Harness
    trigger: U1 の完了の前
    logic: 環境ごとに WasmThreadReport を 1 件作る。確認用のプログラムは Host の trait を通さない単独のもので、Host の wasm 用の設計の材料にする。ブラウザでは COOP/COEP の見出しを付けて配る小さな配信の仕組みを使う
    violation: 不合格の環境があっても U1 は報告をもって完了できる。ただし U4・U5 に入る前に設計を見直す（Delivery Planning の Q7）
    source: FR5.2
  - id: BR8.2
    statement: wasm のスレッドの確認の報告には、Worker を作るのが Host の wasm 用の実装と起動用 JS のどちらが妥当か、その理由と、必要なツールチェーンの設定を含める
    category: policy
    applies_to: Harness
    trigger: 報告の作成
    logic: 取り決めの未決の点（C2・C12）に答える
    violation: 報告がなければ U1 は完了にしない
    source: FR5.2
  - id: BR9.1
    statement: デコーダの包みと ELF の読み込みにファジングの入口を作る。どんな入力でも panic や未定義動作にならないことを夜間に確かめる
    category: validation
    applies_to: Harness, Decoder, Loader
    trigger: 夜間の CI
    logic: IF panic・未定義動作が見つかる THEN Issue にして直す
    violation: 夜間の CI が失敗として記録する
    source: FR9.3, NFR2
```

## 概要

| ID | 内容 | 種類 |
|----|------|------|
| BR1.1〜BR1.4 | ELF の受け入れ条件（ET_EXEC・ET_DYN）、セグメントの配置、最初のスタックと補助ベクタ、static-pie の基準アドレス | 検証・制約・計算 |
| BR2.1〜BR2.3 | 4 KiB ページの 2 段のページテーブル、フォールト、brk | 制約・検証・計算 |
| BR3.1〜BR3.4 | syscall の振り分け、未実装は ENOSYS、U1 で作る syscall、write の範囲 | 方針・制約 |
| BR4.1〜BR4.5 | 命令の実行、syscall 命令、命令数の予算と kill、U1 の命令の決め方（SSE を含む）、シグナルは登録だけ | 方針・制約 |
| BR5.1〜BR5.4 | 終了コード（ゲストの値、128 + シグナル、エミュレータのエラーは 70、引数の誤りは 2）、<program> の置き場所 | 計算・方針・検証 |
| BR6.1 | ホストの機能は Host の trait だけを通す | 制約 |
| BR7.1〜BR7.2 | 差分テストの比べ方と、ゲストのビルド | 検証・方針 |
| BR8.1〜BR8.2 | wasm のスレッドの確認と報告 | 検証・方針 |
| BR9.1 | ファジングの入口 | 検証 |

## Assumptions & Open Questions

None.
