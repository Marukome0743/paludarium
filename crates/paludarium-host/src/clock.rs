use paludarium_types::Errno;
use std::sync::{
    OnceLock,
    atomic::{AtomicBool, Ordering},
};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Clocks required by the guest ABI; values are not host syscall numbers.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ClockId {
    Realtime,
    Monotonic,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WaitOutcome {
    Complete,
    Interrupted,
}

pub(crate) fn native_clock(clock: ClockId) -> Result<u64, Errno> {
    static EPOCH: OnceLock<Instant> = OnceLock::new();
    let duration = match clock {
        ClockId::Realtime => SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|_| Errno::EIO)?,
        ClockId::Monotonic => EPOCH.get_or_init(Instant::now).elapsed(),
    };
    u64::try_from(duration.as_nanos()).map_err(|_| Errno::ERANGE)
}
pub(crate) fn native_wait(
    clock: ClockId,
    deadline: u64,
    cancel: &AtomicBool,
) -> Result<WaitOutcome, Errno> {
    loop {
        if cancel.load(Ordering::SeqCst) {
            return Ok(WaitOutcome::Interrupted);
        }
        let now = native_clock(clock)?;
        if now >= deadline {
            return Ok(WaitOutcome::Complete);
        }
        std::thread::sleep(Duration::from_nanos((deadline - now).min(10_000_000)));
    }
}
