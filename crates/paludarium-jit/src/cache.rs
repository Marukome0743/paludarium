//! Bounded immutable translations keyed by address space, RIP and MMU epoch.
use std::collections::BTreeMap;
use std::sync::{Mutex, PoisonError};

struct Entry<T> {
    generation: u64,
    end: u64,
    translation: T,
    access: u64,
}

struct State<T> {
    entries: BTreeMap<(u64, u64), Entry<T>>,
    accesses: BTreeMap<u64, (u64, u64)>,
    clock: u64,
}
impl<T> State<T> {
    fn tick(&mut self) -> u64 {
        if self.clock == u64::MAX {
            // Evicting all entries on counter exhaustion is a safe fallback.
            self.entries.clear();
            self.accesses.clear();
            self.clock = 0;
        }
        self.clock += 1;
        self.clock
    }
    fn remove(&mut self, key: &(u64, u64)) {
        if let Some(entry) = self.entries.remove(key) {
            self.accesses.remove(&entry.access);
        }
    }
}

pub(crate) struct EpochCache<T> {
    state: Mutex<State<T>>,
}

impl<T: Clone> EpochCache<T> {
    pub(crate) fn new() -> Self {
        Self {
            state: Mutex::new(State {
                entries: BTreeMap::new(),
                accesses: BTreeMap::new(),
                clock: 0,
            }),
        }
    }

    pub(crate) fn get(&self, space: u64, rip: u64, generation: u64) -> Option<T> {
        let mut state = self.state.lock().unwrap_or_else(PoisonError::into_inner);
        let key = (space, rip);
        if state.entries.get(&key)?.generation != generation {
            state.remove(&key);
            return None;
        }
        let access = state.tick();
        let entry = state.entries.get_mut(&key)?;
        let old_access = entry.access;
        entry.access = access;
        let translation = entry.translation.clone();
        state.accesses.remove(&old_access);
        state.accesses.insert(access, key);
        Some(translation)
    }

    pub(crate) fn insert(
        &self,
        space: u64,
        rip: u64,
        generation: u64,
        length: usize,
        translation: T,
    ) -> bool {
        if length == 0 || length > 960 {
            return false;
        }
        let Some(end) = rip.checked_add(length as u64) else {
            return false;
        };
        let mut state = self.state.lock().unwrap_or_else(PoisonError::into_inner);
        let access = state.tick();
        let key = (space, rip);
        state.remove(&key);
        if state.entries.len() >= 1024
            && let Some((_, oldest)) = state.accesses.first_key_value() {
                let oldest = *oldest;
                state.remove(&oldest);
        }
        state.entries.insert(
            key,
            Entry {
                generation,
                end,
                translation,
                access,
            },
        );
        state.accesses.insert(access, key);
        true
    }

    pub(crate) fn invalidate(&self, address: u64) {
        let page = address & !4095;
        let end = page.checked_add(4096);
        let mut state = self.state.lock().unwrap_or_else(PoisonError::into_inner);
        let removed = state
            .entries
            .iter()
            .filter_map(|(&key @ (_, start), entry)| {
                (!(entry.end <= page || end.is_some_and(|end| start >= end))).then_some(key)
            })
            .collect::<Vec<_>>();
        for key in removed {
            state.remove(&key);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn u14_cache_lru_preserves_hot_low_rip_and_evicts_oldest() {
        let cache = EpochCache::new();
        for rip in 0..1024 {
            cache.insert(1, rip * 4096, 1, 1, rip);
        }
        assert_eq!(cache.get(1, 0, 1), Some(0));
        cache.insert(1, 1024 * 4096, 1, 1, 1024);
        assert_eq!(cache.get(1, 0, 1), Some(0));
        assert_eq!(cache.get(1, 4096, 1), None);
        assert_eq!(cache.get(1, 1024 * 4096, 1), Some(1024));
    }

    #[test]
    fn u14_cache_lru_epoch_removal_and_invalidation_remove_recency() {
        let cache = EpochCache::new();
        cache.insert(1, 4096, 1, 1, 42);
        assert_eq!(cache.get(1, 4096, 2), None);
        assert!(cache.state.lock().unwrap().accesses.is_empty());
        cache.insert(1, 4096, 2, 1, 43);
        cache.invalidate(4096);
        assert!(cache.state.lock().unwrap().accesses.is_empty());
    }

    #[test]
    fn u14_cache_lru_recency_exhaustion_discards_safely() {
        let cache = EpochCache::new();
        cache.insert(1, 4096, 1, 1, 42);
        cache.state.lock().unwrap().clock = u64::MAX;
        assert_eq!(cache.get(1, 4096, 1), None);
        assert!(cache.state.lock().unwrap().accesses.is_empty());
        assert!(cache.insert(1, 8192, 1, 1, 43));
        assert_eq!(cache.get(1, 8192, 1), Some(43));
    }

    #[test]
    fn u14_cache_returns_only_matching_epoch() {
        let cache = EpochCache::new();
        assert!(cache.insert(1, 4096, 2, 10, 42));
        assert_eq!(cache.get(1, 4096, 2), Some(42));
        assert_eq!(cache.get(1, 4096, 3), None);
        assert_eq!(cache.get(1, 4096, 2), None);
    }

    #[test]
    fn u14_cache_separates_address_spaces() {
        let cache = EpochCache::new();
        cache.insert(1, 4096, 2, 10, 42);
        cache.insert(2, 4096, 2, 10, 17);
        assert_eq!(cache.get(1, 4096, 2), Some(42));
        assert_eq!(cache.get(2, 4096, 2), Some(17));
    }

    #[test]
    fn u14_cache_cross_page_invalidation_covers_entire_block() {
        let cache = EpochCache::new();
        cache.insert(1, 8191, 2, 10, 42);
        cache.invalidate(8192);
        assert_eq!(cache.get(1, 8191, 2), None);
    }

    #[test]
    fn u14_cache_unrelated_page_is_preserved() {
        let cache = EpochCache::new();
        cache.insert(1, 4096, 2, 10, 42);
        cache.invalidate(8192);
        assert_eq!(cache.get(1, 4096, 2), Some(42));
    }

    #[test]
    fn u14_cache_rejects_overflow_and_unbounded_blocks() {
        let cache = EpochCache::new();
        assert!(!cache.insert(1, u64::MAX, 2, 1, 42));
        assert!(!cache.insert(1, 0, 2, 961, 42));
        assert!(!cache.insert(1, 0, 2, 0, 42));
    }

    #[test]
    fn u14_cache_evicts_safely_at_capacity() {
        let cache = EpochCache::new();
        for index in 0..1025 {
            assert!(cache.insert(1, index, 2, 1, index));
        }
        assert_eq!(cache.get(1, 0, 2), None);
        assert_eq!(cache.get(1, 1024, 2), Some(1024));
    }

    #[test]
    fn u14_cache_serializes_shared_worker_invalidation() {
        let cache = std::sync::Arc::new(EpochCache::new());
        cache.insert(1, 4096, 2, 10, 42);
        let other = cache.clone();
        std::thread::spawn(move || other.invalidate(4096))
            .join()
            .unwrap();
        assert_eq!(cache.get(1, 4096, 2), None);
    }
}
