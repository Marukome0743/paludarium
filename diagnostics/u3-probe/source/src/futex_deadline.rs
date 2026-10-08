//! Independent observation of absolute futex deadlines and bitset wakeups.
use std::sync::atomic::AtomicU32;
use std::sync::Arc;
use std::time::{Duration, Instant};

fn wait(word: &AtomicU32, mask: u32, duration: Duration) -> (i64, i32, Duration) {
    let (rc, error, elapsed, _, _) = wait_traced(word, mask, duration);
    (rc, error, elapsed)
}

fn realtime_ns() -> i128 {
    let mut now = libc::timespec { tv_sec: 0, tv_nsec: 0 };
    unsafe { libc::clock_gettime(libc::CLOCK_REALTIME, &mut now); }
    now.tv_sec as i128 * 1_000_000_000 + now.tv_nsec as i128
}

/// Also returns the monotonic gap between reading the deadline base and starting
/// the elapsed clock, and how far CLOCK_REALTIME is past the deadline on return.
fn wait_traced(word: &AtomicU32, mask: u32, duration: Duration)
    -> (i64, i32, Duration, Duration, i128) {
    let before = Instant::now();
    let mut deadline = libc::timespec { tv_sec: 0, tv_nsec: 0 };
    unsafe { libc::clock_gettime(libc::CLOCK_REALTIME, &mut deadline); }
    deadline.tv_sec += duration.as_secs() as i64;
    deadline.tv_nsec += duration.subsec_nanos() as libc::c_long;
    if deadline.tv_nsec >= 1_000_000_000 {
        deadline.tv_sec += 1;
        deadline.tv_nsec -= 1_000_000_000;
    }
    let started = Instant::now();
    let rc = unsafe {
        libc::syscall(libc::SYS_futex, word.as_ptr(),
            libc::FUTEX_WAIT_BITSET | libc::FUTEX_CLOCK_REALTIME,
            0u32, &deadline, std::ptr::null::<u32>(), mask)
    };
    let error = std::io::Error::last_os_error().raw_os_error().unwrap_or(0);
    let elapsed = started.elapsed();
    let past = realtime_ns() - (deadline.tv_sec as i128 * 1_000_000_000 + deadline.tv_nsec as i128);
    (rc, error, elapsed, started - before, past)
}

fn wake(word: &AtomicU32, mask: u32) -> i64 {
    unsafe { libc::syscall(libc::SYS_futex, word.as_ptr(), libc::FUTEX_WAKE_BITSET,
        1u32, std::ptr::null::<libc::timespec>(), std::ptr::null::<u32>(), mask) }
}

pub fn check() -> Result<(), String> {
    let word = Arc::new(AtomicU32::new(0));
    let waiter_word = word.clone();
    let waiter = std::thread::spawn(move || wait(&waiter_word, 1, Duration::from_secs(2)));
    std::thread::sleep(Duration::from_millis(30));
    let mut broadcasts = 0;
    for round in 0..45 {
        let other_word = word.clone();
        let spawned = Instant::now();
        let other = std::thread::spawn(move || {
            let entered = spawned.elapsed();
            let (rc, error, elapsed) = wait(&other_word, 2, Duration::from_secs(2));
            (rc, error, elapsed, entered)
        });
        // Thread start-up can take hundreds of milliseconds in a browser, so keep
        // waking until the waiter is woken or its own deadline ends it.
        let mut woke = false;
        let mut tries = 0;
        while !other.is_finished() {
            tries += 1;
            if wake(&word, 2) == 1 { woke = true; broadcasts += 1; break; }
            std::thread::sleep(Duration::from_millis(1));
        }
        let woke_at = spawned.elapsed();
        let (rc, error, elapsed, entered) = other.join().map_err(|_| "other waiter panicked")?;
        if !woke || rc != 0 {
            return Err(format!(
                "matching wake failed: round={round} woke={woke} tries={tries} wake_loop_ms={} \
                 waiter_started_ms={} rc={rc} errno={error} waiter_elapsed_ms={}",
                woke_at.as_millis(), entered.as_millis(), elapsed.as_millis()));
        }
    }
    let (rc, error, elapsed) = waiter.join().map_err(|_| "deadline waiter panicked")?;
    eprintln!("futex mismatch broadcasts={broadcasts} rc={rc} errno={error} elapsed_ms={}", elapsed.as_millis());
    if rc != -1 || error != libc::ETIMEDOUT || elapsed < Duration::from_millis(1900) {
        return Err(format!("absolute deadline shortened: rc={rc} errno={error} elapsed={elapsed:?}"));
    }
    let (rc, error, elapsed, gap, past) = wait_traced(&word, 1, Duration::from_millis(100));
    eprintln!("futex no-wake rc={rc} errno={error} elapsed_ms={} start_gap_us={} realtime_past_deadline_us={}",
        elapsed.as_millis(), gap.as_micros(), past / 1000);
    if rc != -1 || error != libc::ETIMEDOUT || elapsed < Duration::from_millis(95) {
        return Err(format!("no-wake deadline failed: rc={rc} errno={error} elapsed={elapsed:?}"));
    }
    Ok(())
}
