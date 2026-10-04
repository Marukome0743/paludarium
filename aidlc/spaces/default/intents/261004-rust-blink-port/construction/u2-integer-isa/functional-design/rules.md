# U2：整数命令の規則

## Sources

要件 FR1.3・FR1.6・FR9.1、NFR1〜NFR3、および `functional-design-questions.md` Q1 の確認済み回答に基づく。以下は実装が満たすべき設計上の規則であり、動作は未検証。

## Business Rules

```yaml
rules:
  - id: BR1.1
    statement: 対応範囲は命令名だけでなく形式・幅・prefix・暗黙オペランドで管理する
    category: policy
    applies_to: Instruction
    trigger: 対応表の追加と命令実行
    logic: IF probe・aube または既存 U1 の対象形式なら THEN 意味論と差分ケースを対応させる
    violation: 未実装を対応済みに数えず SIGILL と未対応一覧に残す
    source: FR1.3
  - id: BR1.2
    statement: 部分レジスタの読書きは親のレジスタと一貫する
    category: calculation
    applies_to: CpuState
    trigger: レジスタオペランドへの書き込み
    logic: IF 32-bit 書き込みなら THEN 上位 32-bit をゼロ化し、8/16-bit なら対象外のビットを保持する。高位 byte と REX の形式を区別する
    violation: 差分テスト不一致で完了を拒否
    source: FR1.3
  - id: BR1.3
    statement: フラグは定義・保持・未定義を入力条件別に分類する
    category: calculation
    applies_to: FlagPolicy
    trigger: 算術・論理・shift・rotate・比較の実行と検証
    logic: IF フラグが定義済みなら THEN ネイティブと比較し、保持なら入力との一致も検査し、未定義だけ比較対象から外す。shift/rotate の有効 count がゼロの条件も別行にする
    violation: 根拠のない除外・全フラグ無視を許さない
    source: FR1.3, NFR1
  - id: BR1.4
    statement: アドレス式とメモリアクセスの権限を区別する
    category: validation
    applies_to: Operand
    trigger: 実効アドレスの計算と read/write/fetch
    logic: IF メモリへアクセスするなら THEN Mmu で全範囲と権限を検査する。lea は計算だけ行い読み取りをしない。RIP-relative・アドレス幅・fs/gs 基底を考慮する
    violation: フォールトを返しホストメモリへ直接アクセスしない
    source: FR1.3, FR1.5, NFR2
  - id: BR1.5
    statement: 単一命令の失敗で未完了のレジスタ・フラグ結果を公開しない
    category: constraint
    applies_to: CpuState, Operand
    trigger: メモリ検査・除算・命令検査の失敗
    logic: IF 非反復の命令が失敗するなら THEN faulting RIP と実行前の可視状態を保つ。複数範囲を書き込む場合は全範囲を検査してから確定する
    violation: 差分テスト不一致で完了を拒否
    source: FR1.3, NFR2
  - id: BR1.6
    statement: 反復命令は完了した反復だけを確定し再開位置を残す
    category: policy
    applies_to: CpuState
    trigger: rep/repne の各反復と実行予算切れ
    logic: IF 一反復が成功するなら THEN カウントと index を更新し、継続中の RIP は同じ命令を指す。MOVS/STOS 等は完了分を保持する。REPE/REPNE CMPS/SCAS の fault では完了分の count/index と faulting RIP を保持し、rflags は命令開始前へ復元する。内部予算切れは fault と区別し、その時点の flags と開始時 flags を保持して同じ反復命令を再開する
    violation: 無限ループや未完了反復の状態更新を許さない
    source: FR1.3, NFR2
  - id: BR1.7
    statement: 除算のゼロ除数と商の範囲外はゲストの除算例外になる
    category: validation
    applies_to: Instruction, CpuState
    trigger: div/idiv
    logic: IF ゼロ除数または商が出力幅に収まらないなら THEN Cpu は除算例外を返し Runtime が Kernel に渡す。通常の商・剰余は確定しない
    violation: ホストの panic や整数除算の trap を漏らさず既定の SIGFPE 終了に変換する
    source: FR1.3, NFR2
  - id: BR2.1
    statement: 原子的な命令の意味論は Cpu、不可分なメモリ更新は Mmu が担当する
    category: policy
    applies_to: Instruction, Operand
    trigger: 有効な lock 接頭辞または暗黙に原子的なメモリ xchg
    logic: IF 原子的な更新なら THEN Cpu は一回の Mmu 更新契約を呼び、読み取り・計算・書き込みをその不可分な区間に含める。Cpu が read と write を別々に呼ばない
    violation: ホスト並行テストの更新欠落・途中状態観測で完了を拒否
    source: FR1.3, Q1
  - id: BR2.2
    statement: 原子操作は通常のメモリアクセスと共通の排他・順序モデルを使う
    category: constraint
    applies_to: Mmu.AddressSpace
    trigger: 原子操作と重なる read/write または mapping の変更
    logic: IF 操作が重なりうるなら THEN 全 read/write/fetch と map/unmap/protect を共通の同期規約へ参加させ、原子更新の途中を見せない。初期版はアドレス空間単位で直列化できる
    violation: 原子操作だけをロックする設計を許さない
    source: FR1.3, FR1.5, Q1
  - id: BR2.3
    statement: 原子操作は全バイトの検査後に一回だけ確定する
    category: validation
    applies_to: Mmu.AddressSpace
    trigger: ページをまたぐ・権限違反・比較失敗を含む原子的な更新
    logic: IF 範囲か権限が不正なら THEN 書き込みなしで fault を返す。有効な非整列・ページ跨ぎは更新を分割せず処理する。命令固有の整列条件も Cpu で検査する
    violation: 部分的な書き込みやホスト例外を許さない
    source: FR1.3, NFR2, Q1
  - id: BR2.4
    statement: cmpxchg の比較成功と失敗を区別し、必要な write 権限を検査する
    category: calculation
    applies_to: CpuState, Mmu.AddressSpace
    trigger: cmpxchg 系
    logic: IF 比較成功なら THEN 新値を確定し、失敗なら accumulator とフラグを命令形式どおり更新する。失敗側でもメモリ宛て命令の write 権限を省略しない
    violation: 成功側だけのテストで対応済みにしない
    source: FR1.3, Q1
  - id: BR2.5
    statement: U2 はホスト並行テスト、U5 はゲストスレッドの統合テストを担当する
    category: policy
    applies_to: TestCase
    trigger: 原子操作の完了判定
    logic: IF U2 を完了するなら THEN 複数ホストスレッドで同じ AddressSpace を更新し不可分性を検査する。clone・futex の統合は U5 に引き継ぐ
    violation: 単一スレッドの差分一致だけで原子性を主張しない
    source: FR1.3, Q1, NFR7
  - id: BR3.1
    statement: 不正・範囲外・未実装の命令は Cpu の停止理由からゲスト SIGILL に変換する
    category: validation
    applies_to: Instruction, CpuState
    trigger: decode または実行可否判定
    logic: IF デコード不能・未対応形式・不正 lock 使用なら THEN faulting RIP と取得済み bytes を伴う InvalidOpcode を返し、Runtime が Kernel に渡す
    violation: エミュレータ自身の Error や panic と混ぜない
    source: FR1.6, NFR2
  - id: BR3.2
    statement: 命令 fetch のアクセス違反と不正命令を区別する
    category: validation
    applies_to: Instruction
    trigger: 命令がページ境界にある場合
    logic: IF 命令の判定に必要な次の bytes が実行不可なら THEN PageFault を返す。取得済み bytes だけで不正と判定できるなら InvalidOpcode を返す。不要な先読みで正常命令を拒否しない
    violation: 誤った SIGILL または SIGSEGV を返さない
    source: FR1.6, FR1.5
  - id: BR4.1
    statement: 差分テストは毎回のネイティブ観測から期待値を得る
    category: policy
    applies_to: TestCase, Observation
    trigger: 差分テスト実行
    logic: IF native-linux-x86_64 が使えるなら THEN 同一入力の正常値とシグナルを実行ごとに観測する。使えない環境では明示的に未実行と記録する
    violation: 固定 baseline や skip を native 一致の証拠にしない
    source: FR9.1, NFR1
  - id: BR4.2
    statement: 命令名の網羅率と意味論の網羅を区別する
    category: policy
    applies_to: TestCase
    trigger: 命令対応率の報告
    logic: IF 命令の割合を報告するなら THEN 対象版・命令形式の分母・対応ケースを併記し、幅・境界入力・flags・fault・原子性を別の検証軸として報告する
    violation: ケース名やソースの文字列対応だけで正しさを主張しない
    source: FR1.3, FR9.1, NFR1
```

## Rules Summary

| 規則 | 対象 |
|---|---|
| BR1.1〜BR1.7 | 命令形式、部分レジスタ、フラグ、アドレス、fault、反復、除算 |
| BR2.1〜BR2.5 | Cpu/Mmu の責任、通常アクセスとの同期、全範囲の検査、比較交換、並行検証 |
| BR3.1〜BR3.2 | SIGILL と命令 fetch の fault |
| BR4.1〜BR4.2 | 毎回のネイティブ観測と網羅の報告 |

## Assumptions & Open Questions

- 原子操作の共有モデルはネイティブ U2 の設計。wasm Worker の共有 heap への具体的な接続は U11 で検証する。原子性の契約自体は維持する。
