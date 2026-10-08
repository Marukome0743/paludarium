//! madvise(MADV_DONTNEED) on private anonymous memory.
//!
//! Linux guarantees that after MADV_DONTNEED, private anonymous pages read
//! back as zero on the next access. Allocators rely on this to hand out
//! purged memory as already zeroed, so an emulator that ignores the advice
//! returns stale data.
const PAGES: usize = 64;

fn check_range(base: *mut u8, len: usize, what: &str) -> Result<(), String> {
    for off in (0..len).step_by(512) {
        let v = unsafe { base.add(off).read_volatile() };
        if v != 0 {
            return Err(format!("{what}: offset {off:#x} reads {v:#x} after MADV_DONTNEED, want 0"));
        }
    }
    Ok(())
}

pub fn check() -> Result<(), String> {
    let len = PAGES * 4096;
    let base = unsafe {
        libc::mmap(std::ptr::null_mut(), len, libc::PROT_READ | libc::PROT_WRITE,
            libc::MAP_PRIVATE | libc::MAP_ANONYMOUS, -1, 0)
    } as *mut u8;
    if base as *mut libc::c_void == libc::MAP_FAILED {
        return Err(format!("mmap failed: {}", std::io::Error::last_os_error()));
    }
    unsafe { std::ptr::write_bytes(base, 0xa5, len) };

    // the whole range
    if unsafe { libc::madvise(base as *mut libc::c_void, len, libc::MADV_DONTNEED) } != 0 {
        return Err(format!("madvise failed: {}", std::io::Error::last_os_error()));
    }
    check_range(base, len, "whole range")?;

    // the memory stays usable afterwards
    unsafe { std::ptr::write_bytes(base, 0x5a, len) };
    let v = unsafe { base.add(len - 1).read_volatile() };
    if v != 0x5a {
        return Err(format!("write after MADV_DONTNEED reads {v:#x}, want 0x5a"));
    }

    // only the advised pages are cleared: pages 8..16 of the 64
    let (start, count) = (8 * 4096, 8 * 4096);
    if unsafe { libc::madvise(base.add(start) as *mut libc::c_void, count, libc::MADV_DONTNEED) } != 0 {
        return Err(format!("partial madvise failed: {}", std::io::Error::last_os_error()));
    }
    check_range(unsafe { base.add(start) }, count, "advised pages")?;
    for off in [0, start - 1, start + count, len - 1] {
        let v = unsafe { base.add(off).read_volatile() };
        if v != 0x5a {
            return Err(format!("offset {off:#x} outside the advised pages reads {v:#x}, want 0x5a"));
        }
    }

    unsafe { libc::munmap(base as *mut libc::c_void, len) };
    Ok(())
}
