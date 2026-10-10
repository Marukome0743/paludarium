#![no_main]
use libfuzzer_sys::fuzz_target;
fuzz_target!(|data: &[u8]| {
    if let Some(header) = data.get(..8) {
        let mut word = [0; 8];
        word.copy_from_slice(header);
        if let Some(wasm) = paludarium_jit::fuzzing::translate(&data[8..], u64::from_le_bytes(word))
        {
            assert!(wasm.starts_with(b"\0asm\x01\0\0\0"));
            assert!(wasm.len() <= 65536);
        }
    }
});
