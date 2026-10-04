#!/usr/bin/env bash
# Builds the spike module into spikes/wasm-threads/pkg/threads.wasm.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"
cargo build --release --locked
mkdir -p pkg
cp target/wasm32-unknown-unknown/release/wasm_threads_spike.wasm pkg/threads.wasm
echo "built $here/pkg/threads.wasm" >&2
