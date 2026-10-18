# Step42〜48 production wasm 実装・検証

## 実装の契約

ドキュメント根拠：C12 の createPaludarium/run/RunningGuest を packages/paludarium-wasm/index.mjs に実装する。Config/Session は paludarium-runtime の既存 API を利用する。実 ELF loader、Vfs、kernel、CPU、MMU、decoder を新 cdylib paludarium-wasm にリンクし、命令・syscall 意味論は変更しない。native Host の cap-std/cap-fs-ext/fs2/getrandom を wasm から target gating し、WasmHost が stdio、暗号学的乱数、時計、wait/cancel を供給する。TTY/JIT は typed unimplemented、mount は Host の既存 ENOSYS として明示する。native CLI 自体をブラウザ向け executable とする変更ではない。

固定 nightly-2026-10-01 の build-std=std,panic_abort と atomics/bulk-memory/mutable-globals、import-memory/shared-memory を使用する。Rust allocator が同期して memory growth を扱い、JS は memory.grow を呼ばない。最大 1 GiB、初期 8 MiB。同一 WebAssembly.Module と shared WebAssembly.Memory を coordinator Worker から nested execution Worker へ渡す。linker の共有初期化は一度だけ。child は Rust entrypoint の前に独立 stack と __wasm_init_tls を設定する。実 stack/TLS region は親の Rust Box<[u128]> が所有し、Rust return と child Worker termination 後に解放する。

ABI は検査済み scalar/handle と 64 MiB 以下の buffer を通じたコピーを用いる。guest pointer は host pointer として dereference しない。Arc/Mutex/OnceLock は Rust std、共有 AddressSpace は既存 MMU 実装。unsafe は Host import 呼出し、wasm export 属性、整列 AtomicU32 に対する bounded wait/notify bridge に限定し、各 bridge に SAFETY コメントを付ける。CPU/decoder/MMU/loader の unsafe 禁止は維持する。

trap/硬い Worker timeout は Rust lock を置き去りにする可能性があるため、全 nested Worker と factory を破棄し、その heap に以後 Rust ABI を呼ばない。正常な typed guest error は Rust return 後に join/free できる。dispose は pending Promise・streams・timer を settle して coordinator cleanup を待ち、1秒で Worker terminate する。再利用は拒否する。

## 検証済みの範囲

native は run37743977030/head ac0825816ef369964fb405642c323438acdd6c5c、署名 Verified=true。新 wasm 実装を比較する前に実機 x86-64 Linux で6個の同一 ELF SHA を取得した。hello stdout=hello\n/exit0、integer42、atomic146、divide_fault SIGFPE8、stdin input\n/exit0、infinite SIGKILL9。期待結果は production CI ごとにも scripts/wasm-native-guests.py で取得し、wasm 側に固定成功値を埋め込まない。

Node v24.21.0 と実 Safari27.0.1/macOS は同じ製品 module と launcher で各14ケース PASS。Safari は COOP/COEP と crossOriginIsolated=true、1880ms、driver_reaped/server_closed=true。全結果は verification/step45-production-wasm/{node-report.json,safari-report.json}。実 Kernel の SIGFPE8 を確認し、旧診断の ArithmeticFault136 と区別する。

共有 probe は2つの nested Worker の Rust std allocator alloc/free を各128回、同じ Arc<AddressSpace> の atomic add を各1000回（最終2000）、Rust共有 AtomicU32 の wait result0/notify1 を実行した。4同時 Session は全42、各 stack/TLS/thread token が別。新 factory の再初期化、stdin待ち Session の dispose で exited/stdout/stderr が有限時間に settle することも確認した。全任意 ELF、guest clone/futex の全意味論、JIT、mount/network、Chromium/Firefox は今回未検証。

Safari の初回 production 実行は shared-memory view に対する WebCrypto 実装差で host error となった。通常 ArrayBuffer に getRandomValues して共有メモリへコピーする修正後に実 Safari で解決を確認した。import-check の2件は ordinary view、65536-byte分割、範囲外/entropy失敗の -1 を検証する。

R03 は全 WebDriver fetch/response body/poll sleep に28秒 operation deadline、cleanup は別500ms budget、独立最外 process-group watchdog は30秒。応答しない driver fixture は28400.43msで非ゼロ終了し driver残留なし、cleanup成功。verification/step43-watchdog/unresponsive-proof.json が実測。旧 Step40 ファイルは旧 hash のまま履歴として保持する。

## 実行コマンドと品質検査

製品 build は scripts/build-wasm.sh。ローカルは /Users/mutoakio/.cargo/bin/cargo +nightly-2026-10-01、Node は /Users/mutoakio/.local/share/mise/installs/node/24.21.0/bin/node を実行した。native workspace test、native clippy --locked --workspace --all-targets -- -D warnings、wasm clippy --locked -Z build-std=std,panic_abort --release --target wasm32-unknown-unknown -p paludarium-wasm -- -D warnings、cargo fmt --all --check は exit0。ログは verification/step45-production-wasm/ に保存する。

Node command: node packages/paludarium-wasm/tests/node-check.mjs packages/paludarium-wasm/paludarium.wasm <fresh-native-results.json>。境界検査: node --test packages/paludarium-wasm/tests/import-check.mjs。fixture生成元: python3 packages/paludarium-wasm/tests/generate-guests.py --check（6件 bytes一致）。

実 Safari command は SAFARI_STATIC_ROOT=/private/tmp/paludarium-production-safari SAFARI_ENTRY_PATH=/tests/index.html SAFARI_REPORT_KEY=__paludariumProductionReport node <verification>/step43-watchdog/safari-check.mjs。static root に製品 package と fresh native-results.json を配置した。head/source と CI 成果物の照合、3OS/80%/固定4target ASan+LSan の最終判定は別の Step47 proof に記録する。検証済み：最終 head178da99e…の CI37745425190 8jobs と sanitizer37745425204 4jobs が全success。各 target601秒、ASan/LSan exit0、154 source hashes before/after/host一致。実測回数と全証拠hashは verification/step47-proof.json。native coverageはwasm-only ABIをinstrumentしていないため、bridge全行coverageとは主張しない。CI生成moduleはローカルmoduleとbytes異なるが、CIの同一binaryをNode/実Safari14ケースで検証した。
