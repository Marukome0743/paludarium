# 取り決めの一覧：Rust 版 blink（paludarium）

## 出どころ

上流の成果物：
- `inception/units-generation/unit-of-work.md`
- `inception/units-generation/unit-of-work-dependency.md`
- `inception/domain-design/components.md`
- `inception/requirements-analysis/requirements.md`

根拠は `contract-design-questions.md` の回答（Q1〜Q5）です。

## 方針

- 内部の取り決めは Rust の trait と型で表し、提供する側のクレートが持ちます（Q1）。
- 複数のクレートで使う小さな型は、`paludarium-types` にまとめます（Q1）。
- 同じプロセスの中の呼び出しなので、通信の仕組み（HTTP など）はありません。そのため、spec は Rust と TypeScript の型の宣言で書きます。
- ここに書くのは取り決めの形です。関数の細かい引数や、エラーの種類の全量は、各 Unit の Functional Design で詰めます。

## 取り決めの一覧

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---------------|----------|-----------|-------|
| C1 | U1（`paludarium-types`） | すべてのクレート | 共通の Rust の型 | U1 |
| C2 | U1（`paludarium-host`。U5・U9・U11・U12・U13 が足す） | Kernel・Vfs・Runtime | Rust の trait | U1 |
| C3 | U1（`paludarium-decoder`） | Cpu・Jit | Rust の関数と型 | U1 |
| C4 | U1（`paludarium-mmu`。U4 が足す） | Cpu・Loader・Kernel・Jit | Rust の関数と型 | U1 |
| C5 | U1（`paludarium-cpu`。U2・U3 が足す） | Runtime | Rust の関数と型（ExitReason を返す） | U1 |
| C6 | U1（`paludarium-vfs`。U7 が足す） | Loader・Kernel | Rust の trait と型 | U1 |
| C7 | U1（`paludarium-loader`） | Kernel・Runtime | Rust の関数と型 | U1 |
| C8 | U1（`paludarium-kernel`。U4〜U9 が足す） | Runtime | Rust の関数と型（syscall の振り分け） | U1 |
| C9 | U14（`paludarium-jit`。U1 が口だけ作る） | Runtime | Rust の trait | U1（口）・U14（実装） |
| C10 | U1（`paludarium`、Runtime の公開 API） | External: crates.io の利用者、Cli、Harness | Rust の公開 API | U1 |
| C11 | U1（`paludarium` のコマンド） | External: ネイティブ環境の利用者、Harness | コマンドライン | U1 |
| C12 | U11（npm のパッケージ、起動用 JS） | External: formicarium、npm の利用者、Harness | ES モジュールの JS API（Web Streams） | U11 |

## C1 共通の型（`paludarium-types`）

```rust
/// ゲストのアドレス。ホストの usize と混ぜない（team-practices の Code Style）
pub struct GuestAddr(pub u64);

/// Linux の errno（ゲストへの戻り値）
pub struct Errno(pub i32); // 例：ENOSYS、EFAULT、ENOENT

/// Cpu・Jit が止まった理由（ADR-004）
pub enum ExitReason {
    Syscall,                                   // syscall 命令
    PageFault { addr: GuestAddr, write: bool }, // ゲストへの SIGSEGV になる
    InvalidOpcode { rip: GuestAddr },           // ゲストへの SIGILL になる
    Halt,
}

/// ゲストの終了状態（Q4）
pub enum ExitStatus {
    Exited(i32),      // 終了コード
    Signaled(i32),    // シグナルで終わった
}

/// エミュレータ自身の問題（Q4）。ゲストの終了とは別の型にする
pub struct Error {
    pub kind: ErrorKind,             // Unimplemented / Internal / InvalidProgram / Host
    pub rip: Option<GuestAddr>,      // 命令のアドレス
    pub bytes: Option<Vec<u8>>,      // 命令のバイト列
    pub syscall: Option<u64>,        // syscall の番号
    pub message: String,
}
```

## C2 Host の trait（`paludarium-host`）

ADR-003 と ADR-007 に従い、Host が用意するのは最小限の道具だけです。

```rust
pub trait Host: Send + Sync {
    // スレッド（U5）
    fn spawn_thread(&self, entry: Box<dyn FnOnce() + Send>) -> Result<(), Error>;
    // 待機と起床（U5）。futex・epoll・eventfd は Kernel が作る
    fn wait_on(&self, addr: &core::sync::atomic::AtomicU32, expected: u32, timeout: Option<core::time::Duration>) -> WaitResult;
    fn wake(&self, addr: &core::sync::atomic::AtomicU32, count: u32) -> u32;
    // 時刻（U4）
    fn now_monotonic(&self) -> core::time::Duration;
    fn now_realtime(&self) -> core::time::Duration;
    // 標準入出力と端末（U1・U9）
    fn read_stdin(&self, buf: &mut [u8]) -> Result<usize, Errno>;
    fn write_stdout(&self, buf: &[u8]) -> Result<usize, Errno>;
    fn write_stderr(&self, buf: &[u8]) -> Result<usize, Errno>;
    fn terminal_info(&self, stream: StreamId) -> TerminalInfo; // isTerminal, columns, rows
    // ホストのファイル（U7。ホストのディレクトリを見せる方式のとき）
    fn host_fs(&self) -> Option<&dyn HostFs>;
}
pub enum WaitResult { Woken, TimedOut, ValueMismatch }
```

- 実装は 4 つです：ネイティブ用（Linux・macOS・Windows）と wasm 用。
- `unsafe` を使ってよいのは、このクレートの中だけです（Jit を除く）。

## C3 Decoder（`paludarium-decoder`）

```rust
pub fn decode(bytes: &[u8], rip: GuestAddr) -> Result<DecodedInstruction, DecodeError>;
pub enum DecodeError { Invalid, Unsupported, NeedMoreBytes }
```

- 既存の crate（iced-x86 など）の型は外に見せません（ADR-006）。
- 範囲外の命令（AVX・AVX-512）には `Unsupported` を返します。

## C4 Mmu（`paludarium-mmu`）

```rust
pub struct AddressSpace { /* ... */ }
impl AddressSpace {
    pub fn read(&self, addr: GuestAddr, buf: &mut [u8]) -> Result<(), Fault>;
    pub fn write(&self, addr: GuestAddr, buf: &[u8]) -> Result<(), Fault>;
    pub fn fetch(&self, addr: GuestAddr, buf: &mut [u8]) -> Result<(), Fault>; // 実行権限の検査付き
    pub fn map(&mut self, addr: Option<GuestAddr>, len: u64, prot: Prot, backing: Backing) -> Result<GuestAddr, Errno>;
    pub fn unmap(&mut self, addr: GuestAddr, len: u64) -> Result<(), Errno>;
    pub fn protect(&mut self, addr: GuestAddr, len: u64, prot: Prot) -> Result<(), Errno>;
    pub fn set_break(&mut self, addr: GuestAddr) -> GuestAddr;
}
pub struct Fault { pub addr: GuestAddr, pub write: bool }
```

- 範囲外や権限違反のアクセスでは `Fault` を返し、panic しません（NFR2）。
- ゲストのアドレスの変換は、検査付きで行います（`try_from`）。

## C5 Cpu（`paludarium-cpu`）

```rust
pub struct CpuState { /* 汎用レジスタ・rip・rflags・SSE レジスタ・fs/gs ベース */ }
pub fn run(state: &mut CpuState, mem: &AddressSpace, budget: u64) -> ExitReason;
```

- `CpuState` の持ち主は Kernel の Thread です（ADR-002）。
- Cpu は、Kernel のことを知りません（ADR-004）。

## C6 Vfs（`paludarium-vfs`）

```rust
pub trait FileSystem: Send + Sync {
    fn resolve(&self, cwd: &Path, path: &[u8], follow: bool) -> Result<InodeRef, Errno>; // 指定ディレクトリの外へ出さない
    fn open(&self, inode: InodeRef, flags: OpenFlags) -> Result<OpenFile, Errno>;
    fn link(&self, old: InodeRef, new_parent: InodeRef, name: &[u8]) -> Result<(), Errno>;
    fn symlink(&self, target: &[u8], parent: InodeRef, name: &[u8]) -> Result<(), Errno>;
    fn rename(&self, from: (InodeRef, &[u8]), to: (InodeRef, &[u8])) -> Result<(), Errno>;
    fn read_dir(&self, dir: InodeRef) -> Result<Vec<DirEntry>, Errno>;
    fn stat(&self, inode: InodeRef) -> Result<Stat, Errno>;
    fn flock(&self, inode: InodeRef, op: FlockOp, owner: u64) -> Result<(), Errno>;
}
```

- 実装は 2 種類です：仮想ファイルシステム（既定）と、ホストのディレクトリを見せる方式。
- パスに NULL が渡された場合は、Kernel が EFAULT を返します。Vfs は NULL を受け取りません（FR2.10）。

## C7 Loader（`paludarium-loader`）

```rust
pub fn load(fs: &dyn FileSystem, path: &[u8], argv: &[Vec<u8>], envp: &[Vec<u8>], mem: &mut AddressSpace) -> Result<LoadedImage, LoadError>;
pub enum LoadError { NotFound, NotStaticMusl, Malformed, Errno(Errno) }
```

- 動的リンクのバイナリには `NotStaticMusl` を返します（成功条件の外）。

## C8 Kernel（`paludarium-kernel`）

```rust
pub struct Kernel { /* プロセス・スレッド・fd の表・futex・epoll など */ }
impl Kernel {
    pub fn new(host: Arc<dyn Host>, fs: Arc<dyn FileSystem>) -> Self;
    pub fn spawn_initial(&self, image: LoadedImage) -> ThreadHandle;
    /// syscall や fault を受け取り、ゲストの状態を更新する。
    /// 未実装の syscall には ENOSYS を返し、番号のままホストに渡さない（FR2.1）
    pub fn handle(&self, thread: &ThreadHandle, reason: ExitReason) -> Next;
}
pub enum Next { Resume, Exit(ExitStatus), Blocked }
```

## C9 Jit の口（`paludarium-jit`）

```rust
pub trait CodeCache: Send + Sync {
    /// 変換済みのものがあれば実行し、止まった理由を返す。なければ None（Cpu で実行する）
    fn try_run(&self, state: &mut CpuState, mem: &AddressSpace) -> Option<ExitReason>;
    /// 書き換えられたページの変換結果を捨てる
    fn invalidate(&self, page: GuestAddr);
}
```

- U1 では、何もしない実装（常に `None`）だけを用意します。
- U14 が wasm 向けの実装を作ります（ADR-005）。

## C10 Runtime の公開 API（`paludarium`、crates.io）

```rust
pub struct Config {
    pub program: Vec<u8>,            // ゲストの中のパス
    pub args: Vec<Vec<u8>>,
    pub env: Vec<(Vec<u8>, Vec<u8>)>,
    pub files: Vec<(Vec<u8>, Vec<u8>)>, // 起動前に仮想ファイルシステムへ置くファイル
    pub mounts: Vec<Mount>,          // ホストのディレクトリを見せる（既定は空）
    pub tty: Option<TerminalInfo>,
    pub jit: bool,                   // wasm のときだけ意味がある
}
pub struct Session { /* ... */ }
impl Session {
    pub fn new(config: Config, host: Arc<dyn Host>) -> Result<Self, Error>;
    pub fn run(&self) -> Result<ExitStatus, Error>;   // Q4
    pub fn kill(&self);                                // 途中で止める
}
```

## C11 コマンド（`paludarium`）

```yaml
command: paludarium [options] <program> [args...]
options:
  - name: --mount <host>:<guest>
    meaning: ホストのディレクトリを、ゲストの guest に見せる（指定がなければ仮想ファイルシステムだけ）
  - name: --env KEY=VALUE
    meaning: ゲストの環境変数（何度でも指定できる）
  - name: --no-jit
    meaning: JIT を使わない（ネイティブでは JIT はない）
exit_code:
  guest_exited: ゲストの終了コード
  guest_signaled: 128 + シグナル番号
  emulator_error: エミュレータ自身のエラーは、ゲストと区別できるよう標準エラーに詳細を出し、決めた終了コードで終わる（値は U1 で決める）
```

## C12 起動用 JS の API（npm）

formicarium との境界です（制約 C-T5）。

```ts
export interface PaludariumOptions {
  wasmUrl: string | URL;
}
export interface RunOptions {
  program: string;
  args?: string[];
  env?: Record<string, string>;
  files?: Record<string, Uint8Array>;          // 起動前に仮想ファイルシステムへ置く
  tty?: { columns: number; rows: number } | null;
  jit?: boolean;
}
export type ExitStatus =
  | { kind: "exited"; code: number }
  | { kind: "signaled"; signal: number };
export interface RunningGuest {
  stdin: WritableStream<Uint8Array>;
  stdout: ReadableStream<Uint8Array>;
  stderr: ReadableStream<Uint8Array>;
  exited: Promise<ExitStatus>;   // エミュレータのエラーでは reject する（PaludariumError）
  kill(): void;
}
export interface Paludarium {
  run(options: RunOptions): RunningGuest;
}
export declare function createPaludarium(options: PaludariumOptions): Promise<Paludarium>;
export declare class PaludariumError extends Error {
  kind: "unimplemented" | "internal" | "invalid-program" | "host";
  rip?: bigint;
  bytes?: Uint8Array;
  syscall?: number;
}
```

- **動く環境**：Node.js の Worker と、COOP/COEP 付きのページのブラウザ（Chromium 系・Firefox・Safari）（FR5.3）。
- **標準入出力**：Web Streams でつなぎます（Q2）。

## 取り決めの持ち方と変更の決まり

- **持ち主**：各取り決めは、上の表の Owner の Unit が持ちます。後の Unit がクレートに機能を足すときは、取り決めを壊さない追加にします。
- **版**（Q3）：公開する取り決め（C10・C11・C12）は、セマンティック バージョニングに従います。
  - 0.x の間は、minor を上げて壊す変更をしてよいことにします。
  - 壊す変更は、変更履歴に書きます。
  - C12 を壊すときは、事前に formicarium 側と合わせます。
- **内部の取り決めを壊す変更**（C1〜C9）：同じワークスペースの中なので、すべての利用側を同じ Pull Request で直します。
- **追加の変更**：フィールドの追加は、利用側が知らない値を無視できる形にします。Rust の公開の型には `#[non_exhaustive]` を付けます。
- **失敗**（Q4）：エミュレータ自身の問題（`Error`）と、ゲストの終了（`ExitStatus`）を混ぜません。
- **時間切れと再試行**：境界には時間切れも再試行もありません。止めたいときは、呼び出し側が `kill()` を呼びます。

## Open Questions

| Contract | Question | Blocks |
|----------|----------|--------|
| C2・C12 | wasm で Worker を作るのは Host の wasm 用の実装か、起動用 JS か。Jit が作った wasm の instantiate をどちらが担うか（ドメイン設計のレビュー指摘 R-01） | U1（確認）、U11、U14 |
| C2・C4 | Worker の間で共有する状態（アドレス空間、Kernel の状態）の置き方（ドメイン設計のレビュー指摘 R-02） | U1（確認）、U5、U11 |
| C11 | エミュレータ自身のエラーのときの終了コードの値 | U1 |
| C12 | npm のパッケージ名 | U11、U15 |
| C10 | `Host` をライブラリの利用者が差し替えられるようにするか（公開 API に trait を出すか） | U1、U15 |
