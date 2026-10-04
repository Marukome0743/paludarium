//! The `paludarium` command; see [`paludarium::cli`].
#![forbid(unsafe_code)]

use std::process::ExitCode;
use std::sync::Arc;

use paludarium::NativeHost;

fn main() -> ExitCode {
    let code = paludarium::cli::main_with(
        std::env::args_os().skip(1),
        Arc::new(NativeHost::new()),
        &mut std::io::stderr(),
    );
    // Exit codes are 0..=255 (guest code, 128 + signal, 2 or 70).
    ExitCode::from(u8::try_from(code).unwrap_or(u8::MAX))
}
