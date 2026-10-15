//! Diagnostic-only aggregate for one fresh shared heap and its guest Workers.
//! No clocks or timers occur in these high-frequency paths. Overflow is sticky
//! and makes the diagnostic report invalid rather than wrapping a counter.
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

#[derive(Clone, Copy)]
#[repr(usize)]
pub enum Counter {
    HookAttempts,
    Checkpoints,
    CacheHits,
    NegativeHits,
    CacheMisses,
    EpochInvalidations,
    LruUpdates,
    SnapshotBytes,
    TranslatedBlocks,
    ExecutedBlocks,
    ExecutedInstructions,
    Fallbacks,
    PrepareCalls,
    ExecuteCalls,
    CompileCount,
    CompileNanoseconds,
    JsTransitions,
    CodeBytesCompared,
    CodeBytesCopied,
    StateBytesCopied,
    PrepareRejections,
    ExecuteRejections,
    InterpreterSteps,
    BudgetCharged,
}

pub const BASE_FIELDS: usize = 24;
pub const FIELD_COUNT: usize = BASE_FIELDS + 64;

struct Collector {
    values: [AtomicU64; FIELD_COUNT],
    overflow: AtomicBool,
}

impl Collector {
    const fn new() -> Self {
        Self {
            values: [const { AtomicU64::new(0) }; FIELD_COUNT],
            overflow: AtomicBool::new(false),
        }
    }

    fn add(&self, field: usize, value: u64) -> bool {
        let Some(counter) = self.values.get(field) else {
            return false;
        };
        if counter
            .try_update(Ordering::Relaxed, Ordering::Relaxed, |old| {
                old.checked_add(value)
            })
            .is_err()
        {
            self.overflow.store(true, Ordering::Relaxed);
            return false;
        }
        true
    }

    fn get(&self, field: usize) -> Option<u64> {
        self.values.get(field).map(|v| v.load(Ordering::Relaxed))
    }

    fn reset(&self) {
        for value in &self.values {
            value.store(0, Ordering::Relaxed);
        }
        self.overflow.store(false, Ordering::Relaxed);
    }

    fn block_length(&self, length: usize) -> bool {
        if (1..=64).contains(&length) {
            self.add(BASE_FIELDS + length - 1, 1)
        } else {
            self.overflow.store(true, Ordering::Relaxed);
            false
        }
    }
}

static COST: Collector = Collector::new();

pub fn add(counter: Counter, value: u64) {
    let _ = COST.add(counter as usize, value);
}

/// Called only by the trusted diagnostic JS import, never by guest code.
pub fn add_field(field: usize, value: u64) -> bool {
    COST.add(field, value)
}

#[must_use]
pub fn get(field: usize) -> Option<u64> {
    COST.get(field)
}

#[must_use]
pub fn overflowed() -> bool {
    COST.overflow.load(Ordering::Relaxed)
}

/// Only the coordinator calls this, before spawning any guest Worker.
pub fn reset() {
    COST.reset();
}

pub fn block_length(length: usize) {
    let _ = COST.block_length(length);
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;

    #[test]
    fn u14_cost_fresh_collector_has_complete_zero_population() {
        let c = Collector::new();
        assert_eq!(Counter::BudgetCharged as usize + 1, BASE_FIELDS);
        assert_eq!(FIELD_COUNT, 88);
        assert!((0..FIELD_COUNT).all(|field| c.get(field) == Some(0)));
        assert!(!c.overflow.load(Ordering::Relaxed));
    }

    #[test]
    fn u14_cost_accumulates_exact_values() {
        let c = Collector::new();
        assert!(c.add(Counter::CacheMisses as usize, 4));
        assert!(c.add(Counter::CacheMisses as usize, 7));
        assert_eq!(c.get(Counter::CacheMisses as usize), Some(11));
    }

    #[test]
    fn u14_cost_invalid_field_is_rejected_without_mutation() {
        let c = Collector::new();
        assert!(!c.add(FIELD_COUNT, 1));
        assert_eq!(c.get(FIELD_COUNT), None);
        assert_eq!(c.get(0), Some(0));
    }

    #[test]
    fn u14_cost_overflow_never_wraps_and_is_sticky() {
        let c = Collector::new();
        assert!(c.add(0, u64::MAX));
        assert!(!c.add(0, 1));
        assert_eq!(c.get(0), Some(u64::MAX));
        assert!(c.overflow.load(Ordering::Relaxed));
        assert!(c.add(1, 1));
        assert!(c.overflow.load(Ordering::Relaxed));
    }

    #[test]
    fn u14_cost_exclusive_reset_clears_values_and_overflow() {
        let c = Collector::new();
        c.add(0, u64::MAX);
        c.add(0, 1);
        c.reset();
        assert_eq!(c.get(0), Some(0));
        assert!(!c.overflow.load(Ordering::Relaxed));
    }

    #[test]
    fn u14_cost_block_histogram_separates_one_two_and_sixty_four() {
        let c = Collector::new();
        for length in [1, 2, 2, 64] {
            assert!(c.block_length(length));
        }
        assert_eq!(c.get(BASE_FIELDS), Some(1));
        assert_eq!(c.get(BASE_FIELDS + 1), Some(2));
        assert_eq!(c.get(FIELD_COUNT - 1), Some(1));
    }

    #[test]
    fn u14_cost_invalid_block_lengths_fail_closed() {
        for length in [0, 65, usize::MAX] {
            let c = Collector::new();
            assert!(!c.block_length(length));
            assert!(c.overflow.load(Ordering::Relaxed));
            assert_eq!(c.get(BASE_FIELDS), Some(0));
        }
    }

    #[test]
    fn u14_cost_shared_workers_accumulate_without_lost_updates() {
        let c = std::sync::Arc::new(Collector::new());
        let workers = (0..4)
            .map(|_| {
                let c = c.clone();
                std::thread::spawn(move || {
                    for _ in 0..1000 {
                        assert!(c.add(0, 1));
                    }
                })
            })
            .collect::<Vec<_>>();
        for worker in workers {
            worker.join().unwrap();
        }
        assert_eq!(c.get(0), Some(4000));
    }
}
