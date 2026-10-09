#![cfg_attr(target_arch = "wasm32", feature(stdarch_wasm_atomic_wait))]
#[cfg(target_arch = "wasm32")]
mod abi;
