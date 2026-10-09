//! Synchronized runtime-to-Kernel signal transport; it never holds an MMU lock.
use crate::{Process, signals};
use paludarium_types::Errno;
use std::sync::{
    Arc, Mutex, PoisonError,
    atomic::{AtomicBool, Ordering},
};

#[derive(Default)]
pub struct SignalInbox {
    queue: Mutex<Vec<signals::PendingSignal>>,
    wake: Arc<AtomicBool>,
}
impl SignalInbox {
    /// Queues a signal for the single guest process (U4).
    pub fn send(&self, number: i32) -> Result<(), Errno> {
        self.send_pending(signals::PendingSignal::user(number, 0))
    }
    pub(crate) fn send_thread(&self, number: i32) -> Result<(), Errno> {
        self.send_pending(signals::PendingSignal::thread(number, 0))
    }
    fn send_pending(&self, signal: signals::PendingSignal) -> Result<(), Errno> {
        let number = signal.number;
        if !(1..=64).contains(&number) {
            return Err(Errno::EINVAL);
        }
        let mut queue = self.queue.lock().unwrap_or_else(PoisonError::into_inner);
        if number < 32
            && queue
                .iter()
                .any(|s| s.number == number && s.target == signal.target)
        {
            return Ok(());
        }
        queue.push(signal);
        self.wake.store(true, Ordering::SeqCst);
        Ok(())
    }
    /// Interrupts a native wait without modifying CPU or guest memory.
    pub fn interrupt(&self) {
        self.wake.store(true, Ordering::SeqCst)
    }
    #[must_use]
    pub fn wake_token(&self) -> Arc<AtomicBool> {
        self.wake.clone()
    }
    pub(crate) fn drain(&self, process: &mut Process) -> bool {
        let mut queue = self.queue.lock().unwrap_or_else(PoisonError::into_inner);
        let received = !queue.is_empty();
        for signal in queue.drain(..) {
            signals::queue(process, signal);
        }
        // Sender stores while holding this same mutex, preventing a lost wake.
        self.wake.store(false, Ordering::SeqCst);
        received
    }
}

#[cfg(test)]
mod u4_tests {
    use super::*;
    #[test]
    fn u4_inbox_control_signal_survives_realtime_backlog() {
        let inbox = SignalInbox::default();
        for _ in 0..2048 {
            inbox.send(32).unwrap();
        }
        inbox.send(19).unwrap();
        inbox.send(18).unwrap();
        inbox.send(9).unwrap();
        let mut process = Process::default();
        inbox.drain(&mut process);
        assert!(process.pending.iter().any(|s| s.number == 9));
        assert!(!process.stopped);
        assert_eq!(
            process.pending.iter().filter(|s| s.number == 32).count(),
            2048
        );
    }
    #[test]
    fn u4_inbox_sender_drain_race_preserves_realtime_count() {
        let inbox = Arc::new(SignalInbox::default());
        let sender = inbox.clone();
        let runner = std::thread::spawn(move || {
            for _ in 0..1000 {
                sender.send(32).unwrap();
            }
        });
        let deadline = std::time::Instant::now() + std::time::Duration::from_secs(3);
        let mut process = Process::default();
        let mut count = 0;
        while count < 1000 {
            assert!(
                std::time::Instant::now() < deadline,
                "signal transport did not drain"
            );
            inbox.drain(&mut process);
            count += process.pending.len();
            process.pending.clear();
            std::thread::yield_now();
        }
        runner.join().unwrap();
        assert_eq!(count, 1000);
        assert!(!inbox.wake.load(Ordering::SeqCst));
    }
}
