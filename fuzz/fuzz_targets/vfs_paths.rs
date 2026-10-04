//! Finite operation sequences exercise filesystem paths without product quotas.
#![no_main]
use libfuzzer_sys::fuzz_target;
use paludarium_vfs::{HostFs, MemFs};
fuzz_target!(|data: &[u8]| {
    let fs = MemFs::new();
    let _ = fs.mkdir(b"/d", 0o755);
    for chunk in data.chunks(32).take(64) {
        if chunk.is_empty() {
            continue;
        }
        let mut p = b"/d/".to_vec();
        p.extend_from_slice(&chunk[1..]);
        match chunk[0] % 9 {
            0 => {
                if let Ok(f) = fs.open(&p, 66, 0o600) {
                    let _ = f.write(chunk);
                    let _ = f.seek(0, 0);
                    let mut b = [0; 32];
                    let _ = f.read(&mut b);
                }
            }
            1 => {
                let _ = fs.mkdir(&p, 0o700);
            }
            2 => {
                let _ = fs.unlink(&p, false);
            }
            3 => {
                let _ = fs.symlink(&p, b"/s");
                let _ = fs.metadata(b"/s", true);
            }
            4 => {
                let _ = fs.link(&p, b"/l");
            }
            5 => {
                let _ = fs.rename(&p, b"/r");
            }
            6 => {
                let _ = fs.read_dir(&p);
            }
            7 => {
                let _ = fs.metadata(&p, false);
            }
            _ => {
                let _ = fs.readlink(&p);
            }
        }
    }
});
