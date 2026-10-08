//! Concurrent first-touch faults on fresh anonymous pages.
//!
//! Every thread writes its own slot in every page of a newly mapped region, in
//! the same order and starting together, so several threads fault the same
//! not-yet-committed page at once. Afterwards each slot must still hold the
//! value its owner wrote: two guest pages sharing one host page, or a page
//! backed by memory the emulator also uses, shows up as a wrong value or a
//! crash. The region is unmapped and mapped again each round so that pages
//! returned to the emulator's pool are reused.
use std::sync::{Arc, Barrier};

const THREADS: usize = 8;
const PAGES: usize = 4096; // 16 MiB per round
const ROUNDS: usize = 6;

fn value(round: usize, page: usize, thread: usize) -> u64 {
    ((round as u64) << 48) | ((page as u64) << 8) | thread as u64 | 0x8000_0000_0000_0000
}

pub fn check() -> Result<(), String> {
    for round in 0..ROUNDS {
        let len = PAGES * 4096;
        let base = unsafe {
            libc::mmap(std::ptr::null_mut(), len, libc::PROT_READ | libc::PROT_WRITE,
                libc::MAP_PRIVATE | libc::MAP_ANONYMOUS, -1, 0)
        };
        if base == libc::MAP_FAILED {
            return Err(format!("round={round} mmap failed: {}", std::io::Error::last_os_error()));
        }
        let addr = base as usize;
        let barrier = Arc::new(Barrier::new(THREADS));
        let workers: Vec<_> = (0..THREADS).map(|thread| {
            let barrier = barrier.clone();
            std::thread::spawn(move || {
                barrier.wait();
                for page in 0..PAGES {
                    let slot = (addr + page * 4096 + thread * 8) as *mut u64;
                    unsafe { slot.write_volatile(value(round, page, thread)); }
                }
            })
        }).collect();
        for worker in workers {
            worker.join().map_err(|_| format!("round={round} writer panicked"))?;
        }
        let mut bad = 0usize;
        let mut first = String::new();
        for page in 0..PAGES {
            for thread in 0..THREADS {
                let slot = (addr + page * 4096 + thread * 8) as *const u64;
                let got = unsafe { slot.read_volatile() };
                let want = value(round, page, thread);
                if got != want {
                    if bad == 0 {
                        first = format!("page={page} thread={thread} got={got:#x} want={want:#x}");
                    }
                    bad += 1;
                }
            }
            // the rest of the page was never written and must still be zero
            let tail = (addr + page * 4096 + THREADS * 8) as *const u64;
            let got = unsafe { tail.read_volatile() };
            if got != 0 {
                if bad == 0 { first = format!("page={page} tail got={got:#x} want=0"); }
                bad += 1;
            }
        }
        if bad != 0 {
            return Err(format!("round={round} corrupted slots={bad} first: {first}"));
        }
        if unsafe { libc::munmap(base, len) } != 0 {
            return Err(format!("round={round} munmap failed: {}", std::io::Error::last_os_error()));
        }
    }
    Ok(())
}
