# データの形（u1-skeleton）

上流の成果物：
- `inception/domain-design/components.md`
- `inception/contract-design/contract-summary.md`
- `inception/units-generation/unit-of-work.md`（U1）

根拠は `functional-design-questions.md`（Q1〜Q4）です。U1 で使う範囲だけを定めます。後の Unit で属性を足します。

```yaml
entities:
  - name: AddressSpace
    owner: Mmu
    description: 1 つのプロセスのゲストのアドレス空間
    attributes:
      - { name: addressSpaceId, type: identifier, required: true, unique: true }
      - { name: pageDirectory, type: map(directoryIndex -> PageTable), required: true, constraints: "疎。使う範囲だけ作る" }
      - { name: mappings, type: list(Mapping), required: true }
      - { name: initialBreak, type: GuestAddress, required: true }
      - { name: currentBreak, type: GuestAddress, required: true, constraints: ">= initialBreak" }
    constraints:
      - "ページの大きさは 4096 バイト（Q2）"
      - "ゲストのアドレスは 48 bit の範囲（0 から 2^47-1 までの下半分）"
    relationships:
      - { to: Mapping, cardinality: one-to-many }
      - { to: PageTable, cardinality: one-to-many }

  - name: PageTable
    owner: Mmu
    description: 2 段のページテーブルの下の段。連続した 512 ページ分の対応を持つ（Q2）
    attributes:
      - { name: directoryIndex, type: integer, required: true, unique: true, constraints: "AddressSpace の中で一意" }
      - { name: entries, type: list(PageEntry), required: true, constraints: "512 個" }
    relationships:
      - { to: AddressSpace, cardinality: many-to-one }

  - name: PageEntry
    owner: Mmu
    description: 1 ページ分の対応
    attributes:
      - { name: present, type: boolean, required: true, default: false }
      - { name: protection, type: set(read|write|execute), required: true }
      - { name: frame, type: reference(host memory block), required: false, constraints: "present のときだけ" }

  - name: Mapping
    owner: Mmu
    description: mmap や ELF のセグメントで作られた連続した領域
    attributes:
      - { name: addressSpaceId, type: identifier, required: true }
      - { name: start, type: GuestAddress, required: true, constraints: "4096 の倍数" }
      - { name: length, type: integer, required: true, min: 4096, constraints: "4096 の倍数" }
      - { name: protection, type: set(read|write|execute), required: true }
      - { name: kind, type: enum, required: true, allowed: [elf-segment, anonymous, stack, heap] }
    constraints:
      - "識別子は addressSpaceId と start の組"
      - "同じ AddressSpace の中で重ならない"

  - name: CpuState
    owner: Kernel
    description: スレッドのレジスタの状態（ADR-002）。Cpu は渡されたものを実行するだけ
    attributes:
      - { name: threadId, type: identifier, required: true, unique: true }
      - { name: generalRegisters, type: list(64-bit integer), required: true, constraints: "rax〜r15 の 16 個" }
      - { name: instructionPointer, type: GuestAddress, required: true }
      - { name: flags, type: 64-bit integer, required: true }
      - { name: fsBase, type: GuestAddress, required: true, default: 0 }
      - { name: gsBase, type: GuestAddress, required: true, default: 0 }
      - { name: sseRegisters, type: list(128-bit value), required: true, constraints: "xmm0〜xmm15 の 16 個（取り決め C5）" }
      - { name: mxcsr, type: 32-bit integer, required: true, default: 8064 }

  - name: ExitReason
    owner: Cpu
    description: Cpu が止まった理由（取り決め C1。C1 に budget-exhausted を足す。持ち主は U1 で、壊さない追加）
    attributes:
      - { name: kind, type: enum, required: true, allowed: [syscall, page-fault, invalid-opcode, halt, budget-exhausted] }
      - { name: guestRip, type: GuestAddress, required: true }
      - { name: faultAddress, type: GuestAddress, required: false, constraints: "page-fault のときだけ" }
      - { name: faultIsWrite, type: boolean, required: false }
      - { name: instructionBytes, type: bytes, required: false, constraints: "invalid-opcode のとき、最大 15 バイト" }
    constraints:
      - "syscall の番号は ExitReason に持たせず、CpuState の rax から読む"

  - name: LoadedImage
    owner: Loader
    description: 読み込んだ ELF の結果
    attributes:
      - { name: entryPoint, type: GuestAddress, required: true }
      - { name: programHeaderAddress, type: GuestAddress, required: true }
      - { name: programHeaderCount, type: integer, required: true }
      - { name: initialStackPointer, type: GuestAddress, required: true, constraints: "16 バイト境界" }
      - { name: initialBreak, type: GuestAddress, required: true }
      - { name: loadBase, type: GuestAddress, required: true, constraints: "ET_EXEC なら 0、ET_DYN（static-pie）なら BR1.4 の基準アドレス" }
    relationships:
      - { to: AddressSpace, cardinality: many-to-one, references: AddressSpace }

  - name: Process
    owner: Kernel
    description: ゲストのプロセス（U1 では 1 つだけ）
    attributes:
      - { name: processId, type: identifier, required: true, unique: true, default: 1 }
      - { name: addressSpaceId, type: identifier, required: true, references: AddressSpace }
      - { name: threadIds, type: list(identifier), required: true, constraints: "U1 では 1 つ" }
      - { name: exitStatus, type: ExitStatus, required: false }
      - { name: registeredSignalActions, type: map(signal number -> action), required: true, constraints: "U1 では登録を記録するだけで、配送しない（BR4.5）" }
    relationships:
      - { to: AddressSpace, cardinality: one-to-one }
      - { to: CpuState, cardinality: one-to-many }

  - name: StandardStream
    owner: Kernel
    description: U1 で扱うファイル記述子（0・1・2 だけ）
    attributes:
      - { name: descriptor, type: integer, required: true, allowed: [0, 1, 2] }
      - { name: hostStream, type: enum, required: true, allowed: [stdin, stdout, stderr] }

  - name: GuestFile
    owner: Vfs
    description: 起動前に仮想ファイルシステムへ置くファイル（U1 では ELF だけ）
    attributes:
      - { name: path, type: bytes, required: true, unique: true }
      - { name: content, type: bytes, required: true }
      - { name: mode, type: integer, required: true, default: 493 }

  - name: SessionConfig
    owner: Runtime
    description: 1 回の実行の設定（取り決め C10 の Config と同じ形）
    attributes:
      - { name: programPath, type: bytes, required: true, constraints: "ゲストの中の絶対パス" }
      - { name: arguments, type: list(bytes), required: true, constraints: "argv[0] を含む" }
      - { name: environment, type: list(pair(bytes, bytes)), required: true }
      - { name: files, type: list(GuestFile), required: true }
      - { name: mounts, type: list(pair(host path, guest path)), required: true, constraints: "U1 では空だけを受け付ける（U7 で実装）" }
      - { name: tty, type: optional(TerminalInfo), required: false, constraints: "U1 では使わない（U9 で実装）" }
      - { name: jit, type: boolean, required: true, default: false, constraints: "ネイティブでは常に false" }
    constraints:
      - "命令数の予算（BR4.3）は Runtime の内部の設定で、SessionConfig には入れない（既定 100000）"

  - name: DiffTestCase
    owner: Harness
    description: 差分テストの 1 件
    attributes:
      - { name: name, type: text, required: true, unique: true }
      - { name: guestSource, type: enum, required: true, allowed: [c-musl, rust-musl] }
      - { name: arguments, type: list(text), required: true }
      - { name: compared, type: set(stdout|stderr|exitStatus), required: true }

  - name: WasmThreadReport
    owner: Harness
    description: wasm のスレッドの確認の結果（Q3）
    attributes:
      - { name: environment, type: enum, required: true, allowed: [nodejs, chromium, firefox, safari] }
      - { name: version, type: text, required: true }
      - { name: crossOriginIsolated, type: boolean, required: true }
      - { name: waitNotifyPassed, type: boolean, required: true }
      - { name: notes, type: text, required: false }
```

## 概要

| データ | 持ち主 | 役割 |
|--------|--------|------|
| AddressSpace・PageTable・PageEntry・Mapping | Mmu | 4 KiB ページの 2 段のページテーブルで、ゲストのメモリを表す（Q2） |
| CpuState | Kernel | スレッドのレジスタの状態（ADR-002） |
| ExitReason | Cpu | Cpu が止まった理由。syscall の番号は rax から読む |
| LoadedImage | Loader | 読み込んだ ELF の入口・スタック・初期の break |
| Process・StandardStream | Kernel | U1 では 1 プロセス・1 スレッド、ファイル記述子は 0〜2 だけ |
| GuestFile | Vfs | 起動前に置く ELF |
| SessionConfig | Runtime | 1 回の実行の設定 |
| DiffTestCase・WasmThreadReport | Harness | 差分テストと、wasm のスレッドの確認の結果 |

## Assumptions & Open Questions

None.
