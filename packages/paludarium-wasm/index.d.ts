export type ExitStatus = { kind: "exited"; code: number } | { kind: "signaled"; signal: number };
export class PaludariumError extends Error {
  kind: "unimplemented" | "internal" | "invalid-program" | "host";
  rip?: bigint;
  bytes?: Uint8Array;
  syscall?: number;
}
export interface FileSystemOptions {
  files?: Record<string, Uint8Array>;
  fileModes?: Record<string, number>;
}
export interface FileSystemEntry {
  path: string;
  mode: number;
  inode: bigint;
  links: bigint;
  mtimeNs: bigint;
  /** Regular file bytes or symlink target bytes; empty for directories. */
  content: Uint8Array;
}
export interface PrivateFileSystem {
  dispose(): Promise<void>;
  snapshot(): Promise<FileSystemEntry[]>;
  remove(path: string, options?: { recursive?: boolean }): Promise<void>;
}
export interface RunOptions extends FileSystemOptions {
  program: string;
  cwd?: string;
  args?: string[];
  env?: Record<string, string>;
  tty?: { columns: number; rows: number } | null;
  jit?: boolean;
  filesystem?: PrivateFileSystem;
}
export interface Guest {
  stdin: WritableStream<Uint8Array>;
  stdout: ReadableStream<Uint8Array>;
  stderr: ReadableStream<Uint8Array>;
  exited: Promise<ExitStatus>;
  kill(): void;
}
export interface Launcher {
  createFileSystem(options?: FileSystemOptions): Promise<PrivateFileSystem>;
  run(options: RunOptions): Guest;
  diagnostics(): Promise<unknown>;
  dispose(): Promise<void>;
}
export interface PaludariumOptions { wasmUrl: string | URL; }
export type RunningGuest = Guest;
export type Paludarium = Launcher;
export function createPaludarium(options: PaludariumOptions): Promise<Paludarium>;
