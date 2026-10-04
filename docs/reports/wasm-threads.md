# wasm のスレッドの確認（U1）

段階 1 の設計の中で、wasm でスレッドを使えるかを小さく確かめました（Ideation の決定 D22、BR8.1・BR8.2）。
確認用のプログラムは Host の trait を通さない単独のもので、Host の wasm 用の設計の材料にします。

- プログラム：`spikes/wasm-threads/`
- 確かめたこと：`SharedArrayBuffer` を共有した 2 つの Worker のうち、Worker A が共有メモリの番地で値の変化を待ち（`memory.atomic.wait32`）、Worker B が値 42 を書いて起こす（`memory.atomic.notify`）。A が 5 秒以内に値 42 で起きれば合格。

## 結果（WasmThreadReport）

| 環境 | 版 | crossOriginIsolated | 待つ・起こす | 確かめた場所 | メモ |
|------|----|---------------------|--------------|--------------|------|
| nodejs | v24.21.0 | true（Node.js には該当なし） | 合格 | 手元（Windows 11） | 待ちの結果 0（起こされた）、値 42、待ち 206 ms、起こしたのは 1 |
| chromium | 151.0.7922.34（Playwright 1.62.0 のヘッドレス版） | true | 合格 | 手元（Windows 11） | 待ちの結果 0、値 42、待ち 286 ms、起こしたのは 1 |
| firefox | 153.0（Playwright 1.62.0） | true | 合格 | 手元（Windows 11） | 待ちの結果 0、値 42、待ち 243 ms、起こしたのは 1 |
| safari | 未確認 | 未確認 | **未検証** | 夜間の CI（macOS、本物の Safari を safaridriver で操作） | 手元が Windows のため動かせない。`.github/workflows/nightly.yml` の `wasm-threads-safari` の結果でこの行を埋める |

再現の手順：

```bash
bash spikes/wasm-threads/build.sh
node spikes/wasm-threads/node-check.mjs
cd spikes/wasm-threads && npm ci && cd ../..
node spikes/wasm-threads/browser-check.mjs chromium firefox
node spikes/wasm-threads/browser-check.mjs safari   # macOS で。先に sudo safaridriver --enable
```

各コマンドは環境ごとに WasmThreadReport を 1 行の JSON で出し、どれかが不合格なら終了コード 1 で終わります。

## Worker を作るのはどちらか（取り決め C2・C12 の未決の点、R-01）

**提案：Worker を作るのは起動用 JS（C12）とし、Host の wasm 用の実装は、起動用 JS が渡す関数を呼ぶだけの薄い層にする。**

理由：

1. Worker を作る手段は JS の API（`new Worker(url, { type: "module" })`）だけで、wasm から直接は作れません。Host の wasm 用の実装が作るとしても、結局は起動用 JS が import として渡す関数を呼ぶことになります。作る処理そのものを JS に置けば、層が 1 つ減ります。
2. 新しい Worker には、コンパイル済みの `WebAssembly.Module` と共有の `WebAssembly.Memory` を `postMessage` で渡し、同じメモリで instantiate する必要があります（今回の確認もこの形で通りました）。この受け渡しと、Worker の終了・エラーの扱いは、JS の側で完結します。
3. ブラウザの主スレッドでは `memory.atomic.wait32` が使えません（待つと例外）。エミュレータは Worker の中で動かす必要があり、最初の Worker を作るのはどのみち起動用 JS です。ゲストのスレッドの Worker も同じ場所で管理すると、kill（C10・C12）のときにまとめて止められます。
4. Host の trait の `spawn_thread` は、wasm 用の実装では「起動用 JS に Worker の作成を頼む関数を呼ぶ」だけになります。ゲストの `clone` はスレッド ID をすぐに返し、新しいスレッドは Worker の準備ができてから動き出す形にします（Linux でも新しいスレッドがいつ動くかは決まっていないので、意味は変わりません）。

まだ確かめていないこと（U5・U11 の設計で確かめる）：

- Worker の中から、さらに Worker を作るか、主スレッドに頼むか。今回は主スレッドが 2 つの Worker を作る形だけを確かめました。入れ子の Worker の可否は、ブラウザごとに **未検証** です。
- 共有の状態の置き方（R-02）：今回の wasm は `no_std` で、スタックとスレッドローカル変数を使わない関数だけを公開したので、2 つの instance が同じメモリを使っても衝突しませんでした。エミュレータ本体（`std` を使い、Rust のヒープにアドレス空間や Kernel の状態を置く）を共有するには、`std` も atomics 付きでビルドし（`-Z build-std=std,panic_abort`）、instance ごとにスタックとスレッドローカル領域を分ける初期化が要ります。この初期化は **未検証** です。

## 必要なツールチェーンの設定（BR8.2）

| 項目 | 設定 | 場所 |
|------|------|------|
| ツールチェーン | nightly（`rust-toolchain.toml` の nightly-2026-10-01）と `rust-src` | リポジトリの `rust-toolchain.toml` |
| ターゲット | `wasm32-unknown-unknown` | `spikes/wasm-threads/.cargo/config.toml` |
| ターゲットの機能 | `-C target-feature=+atomics,+bulk-memory,+mutable-globals` | 同上 |
| 標準ライブラリの作り直し | `-Z build-std=core,panic_abort`（atomics を有効にした core が要る。本体では `std` も） | 同上 |
| リンカの引数 | `--shared-memory`、`--import-memory`、`--initial-memory=1179648`、`--max-memory=1179648`（共有メモリには最大値が必須） | 同上 |
| Rust の不安定機能 | `#![feature(stdarch_wasm_atomic_wait)]`（`memory_atomic_wait32` が不安定のため） | `spikes/wasm-threads/src/lib.rs` |
| JS 側のメモリ | `new WebAssembly.Memory({ initial: 18, maximum: 18, shared: true })`（モジュールの import と同じ大きさ） | `spikes/wasm-threads/js/check.mjs` |
| ページの見出し | `Cross-Origin-Opener-Policy: same-origin`、`Cross-Origin-Embedder-Policy: require-corp`（これがないと `crossOriginIsolated` が偽で、`SharedArrayBuffer` が使えない） | `spikes/wasm-threads/serve.mjs` |
| Worker | モジュールの Worker（`{ type: "module" }`）。Node.js は `worker_threads` | `spikes/wasm-threads/web/page.mjs`、`node-check.mjs` |

## 判断

- Node.js・Chromium 系・Firefox では、wasm の待つ・起こすが動くことを確かめました。BR8.1 により、U1 はこの報告をもって完了できます。
- Safari は夜間の CI の結果を待ちます。不合格なら、U4・U5 に入る前に設計を見直します（BR8.1）。
