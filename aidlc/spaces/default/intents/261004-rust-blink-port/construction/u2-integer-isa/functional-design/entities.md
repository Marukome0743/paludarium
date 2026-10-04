# U2：整数命令のデータモデル

## Sources

`inception/domain-design/components.md`、`inception/contract-design/contract-summary.md` の C1・C3・C4・C5、`functional-design-questions.md` Q1 と確認済み要約に基づく設計。動作の主張は未検証であり、実装と差分テストで確かめる。

## Entity Model

```yaml
entities:
  - name: CpuState
    description: Kernel の Thread が所有し、Cpu に貸し出す整数命令の実行状態
    attributes:
      - {name: threadId, type: identifier, required: true, unique: true, references: Kernel.Thread}
      - {name: registers, type: "16 unsigned 64-bit values", required: true, constraints: "部分レジスタは同じ値への窓。独立した複製を持たない"}
      - {name: rip, type: guest-address-64, required: true}
      - {name: rflags, type: bitset-64, required: true, constraints: "定義済み・保持・未定義を命令条件別に扱う"}
      - {name: segmentBases, type: "fs/gs guest-address-64", required: true}
      - {name: repeatContinuation, type: optional-repeat-context, required: false, constraints: "反復命令の開始 RIP・命令識別・開始時 rflags を保持する。内部 BudgetStop をまたいで保存し、同じ命令の再開で開始時値を取り直さない。完了・fault・別命令への移行で破棄する"}
    constraints: ["Cpu は Kernel を呼ばない", "成功した命令だけ通常の次 RIP を確定する"]
    relationships:
      - {target: Instruction, cardinality: "1:N", direction: executes}
  - name: Instruction
    description: Decoder が生成する一命令の値。実行可能かどうかは Cpu が判断する
    attributes:
      - {name: rip, type: guest-address-64, required: true, unique: false}
      - {name: bytes, type: byte-sequence, required: true, min: 1, max: 15}
      - {name: operation, type: instruction-identity, required: true}
      - {name: prefixes, type: prefix-set, required: true, constraints: "lock・反復・オペランド幅・アドレス幅を保持する"}
      - {name: operands, type: operand-sequence, required: true}
    constraints: ["外部デコーダ固有の型を契約の外に出さない", "命令名だけで対応判定しない"]
    relationships:
      - {target: Operand, cardinality: "1:N", direction: uses}
  - name: Operand
    description: レジスタの窓、即値、または検査付きメモリアクセスの指定
    attributes:
      - {name: kind, type: enum, required: true, allowed: [register, immediate, memory, implicit]}
      - {name: width, type: bits, required: true, allowed: [8, 16, 32, 64, 128], constraints: "128 は cmpxchg16b の対としてだけ。SSE は U3"}
      - {name: valueOrRegister, type: optional-value, required: false}
      - {name: addressExpression, type: optional-address-expression, required: false, constraints: "基底・index・scale・変位・次 RIP・fs/gs・アドレス幅を区別する"}
    constraints: ["guest address と host index を混ぜない", "メモリを参照しない命令はアクセス権検査のための読み取りもしない"]
    relationships: []
  - name: FlagPolicy
    description: 命令形式と入力条件から決まるフラグ比較の規則
    attributes:
      - {name: key, type: "operation + form + width + input-condition", required: true, unique: true}
      - {name: definedMask, type: bitset-64, required: true}
      - {name: preservedMask, type: bitset-64, required: true}
      - {name: undefinedMask, type: bitset-64, required: true}
      - {name: source, type: specification-reference, required: true}
    constraints: ["三つのマスクは互いに重ならない", "保持ビットは実行前の値との一致も検査する", "未定義ビットだけを比較から外す"]
    relationships: []
  - name: TestCase
    description: ネイティブとエミュレータに同じ入力を与える命令単位の検証契約
    attributes:
      - {name: caseId, type: identifier, required: true, unique: true}
      - {name: instructionBytes, type: byte-sequence, required: true}
      - {name: initialState, type: register-and-memory-image, required: true}
      - {name: memoryRegions, type: region-sequence, required: true, constraints: "アドレス・権限・初期値・比較範囲を指定する"}
      - {name: flagPolicy, type: reference, required: true, references: FlagPolicy.key}
      - {name: expectedStopKind, type: enum, required: true, allowed: [completed, SIGILL, SIGSEGV, SIGFPE]}
    constraints: ["ネイティブの期待値は実行ごとに作る", "観測のための命令が対象のフラグを壊さない", "ゲストアドレスを共通化するか比較前に意味を保って正規化する"]
    relationships:
      - {target: Observation, cardinality: "1:N", direction: compares}
      - {target: FlagPolicy, cardinality: "N:1", direction: selects}
  - name: Observation
    description: 一ケースの一環境の実行結果。未定義ビットを隠す前の値も保持する
    attributes:
      - {name: runId, type: identifier, required: true, unique: true}
      - {name: caseId, type: reference, required: true, references: TestCase.caseId}
      - {name: environment, type: enum, required: true, allowed: [native-linux-x86_64, interpreter]}
      - {name: registers, type: register-image, required: true}
      - {name: flags, type: bitset-64, required: true}
      - {name: memory, type: byte-sequence, required: true}
      - {name: termination, type: stop-record, required: true, constraints: "正常完了・シグナル・観測器自身の失敗を区別する"}
    constraints: ["観測器の失敗と比較不一致を成功にしない"]
    relationships: []
```

CpuState の所有者は既存契約どおり Kernel。Instruction と Operand は Decoder の値で、Cpu が意味論を実行する。FlagPolicy・TestCase・Observation は Harness の検証データで、製品の実行状態に混ぜない。

## Assumptions & Open Questions

- probe・aube の対象版から得た整数命令の完全な一覧は未取得。コード生成の計画で取得方法と証拠を確定し、未取得を「全量対応」と表現しない。
