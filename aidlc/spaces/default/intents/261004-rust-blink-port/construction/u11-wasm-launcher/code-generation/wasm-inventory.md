# U11 実装前の棚卸し

読取確認（2026-10-10）。実guestでの再現は fresh Linux oracle 生成後に行う。

| 境界 | 現実装 | U11で必要な互換追加 |
|---|---|---|
| C2 worker | runtime/workers.rs が子Kernel/Threadを閉包に保持して Host::spawn_thread へ渡す。WasmHostはoverrideせず既定wasm ENOSYSを返す | wasm Hostに閉包のhandle tableと完了ticketを持ち、JSへscalar handleだけ通知。実Workerから閉包を一度だけ実行しjoinする |
| C2 futex ticket | threads.rsのwaitはwasmでENOSYS。notifyはticket値を更新するがwasm atomic notifyを呼ばない | host-owned AtomicU32のwait/notifyを追加。value mismatch、期限、signal/killを10ms以下で再確認し、guest pointerをJS/OSへ渡さない |
| C2 shared state | ExecutionのArcがMMU、process/thread group、kill、signal inbox、cacheを保持。子kernel/threadは個別所有 | 同じRust heapでArcを保持。各Workerへ個別stack/TLS regionを割り当て、終了後だけ親が解放 |
| 既存診断 | sharedProbeはAddressSpace追加とallocator/atomic waitを試験。execution.mjsは一つのsession_runだけ実行 | 診断成功をguest cloneの成功へ読み替えず、rayon/mutex-condvar/tokioで実guest照合 |
| C10 VFS | Session::runの入口でfile_systemを毎回作る。JS runごとにもSessionを新規生成 | 明示的なprivate filesystem handleを互換追加。既定runの状態分離は維持。再利用FSは実行中のmutationを拒否 |
| C12 initial mode | filesはUint8Arrayのみ、config_fileは0755既定。Runtime ConfigにはU10 file_modesがある | optional fileModesとconfig_file_mode。既定0755維持、fixtureのみ0644 |
| C12 terminal | validateはtty指定をunimplementedとする。Runtimeはterminal sizeを渡せる | tty dimensionのu16境界検証とconfig terminal接続。Host terminal state/attributesも接続 |
| C12 errors | kind/messageだけ転送。Rust Errorのrip/bytes/syscallは落ちる | scalar/bufferでoptional diagnosticsを転送しPaludariumErrorへ付与 |
| C12 streams | coordinatorが10msでhost出力全体を再コピー。stdinはbounded64MiB、closedはRustHostで拒否 | EOF/完了後writer/streamerrorの境界を確認。大guest転送はtrusted host bufferのbulkcopyを検討 |
| 停止 | indexとcoordinatorに製品guest30秒watchdogがある。killはSession::kill、disposeは全guest kill後待つ | guest自動期限を製品から外す。30秒は外部差分監督がkill/disposeしてWorker回収。初期化/異常cleanup期限は別管理 |

## Worker所有と解放

Coordinatorはmodule/shared memoryとすべてのWorker resourceを所有する。各execution Workerは初期化前に私有Rust stack/TLSをセットする。ゲストclone閉包が保持するArcは同じSession内のKernel/MMU/process stateだけを共有し、CPU/decodeとThreadは子閉包が所有する。親はWorkerが戻って停止するまでstack/TLSを解放しない。trap・強制終了でRust lockの所有が不明な場合はheap全体を廃棄し、資源を再利用しない。

ABIはwasm32のscalar u32 handleを検査し、CONFIGS/RUNS/BUFFERS/REGIONSはOnceLock/Mutexで同じ共有heapに置く。regionはu128 storageで16byte整列、TLSはmoduleの__tls_alignで追加整列し、2MiB stackを確保する。Rustへ入る前に__stack_pointerと__wasm_init_tlsをセットする。ゲストアドレスはRustのMMU内にとどめ、JSへ渡すregion pointerは信頼済みlauncherのhost memoryだけとする。

## VFS互換追加案

`createFileSystem({files, fileModes})` がprivate filesystem objectを作り、`run({..., filesystem})` が任意に借りる。省略時は従来通りrunごと独立。`filesystem.snapshot()` と `filesystem.remove(path, {recursive:true})` はguestが停止している時だけ許す。install、remove node_modules、frozen、listは同じobjectを使用する。明示objectの別launcher利用を拒否し、disposeで無効化する。Snapshotにはpath/type/mode/content/hashまたはsymlink targetを含め、nativeと比較できる形を採用する。実装前にMemFsの既存操作APIに合わせ最小化する。

## 検証順

1. runner readiness（Python7件、JS7件）
2. immutable guestのfresh Linux14ケースとhash/source receipt
3. 現wasm baselineの不一致を保存
4. Host/Worker/VFS/C12を順に実装し内部試験
5. fresh nativeと同一guest/moduleを4実環境へ照合

既存API型と共有契約のC12に破壊変更は加えない。具体的な新APIは実装結果と型宣言へ明記する。
