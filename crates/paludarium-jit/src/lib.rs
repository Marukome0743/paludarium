//! JIT code-cache interface for paludarium (contract C9).
//!
//! The runtime asks the cache first and falls back to the interpreter when
//! it returns `None`. U1 ships only [`NoopCodeCache`], which never has
//! translated code; U14 provides the wasm implementation (ADR-005).
#![forbid(unsafe_code)]

use paludarium_cpu::CpuState;
use paludarium_mmu::AddressSpace;
use paludarium_types::{ExitReason, GuestAddr};

/// A cache of translated guest code.
pub trait CodeCache: Send + Sync {
    /// Runs translated code for `state.rip` if there is any and returns why it
    /// stopped; `None` means "not translated, use the interpreter".
    fn try_run(&self, state: &mut CpuState, mem: &AddressSpace) -> Option<ExitReason>;
    /// Discards translations of the page containing `page` (guest code was
    /// written).
    fn invalidate(&self, page: GuestAddr);
}

/// The code cache used when there is no JIT (always native in U1).
#[derive(Debug, Default, Clone, Copy)]
pub struct NoopCodeCache;

impl CodeCache for NoopCodeCache {
    fn try_run(&self, _state: &mut CpuState, _mem: &AddressSpace) -> Option<ExitReason> {
        None
    }

    fn invalidate(&self, _page: GuestAddr) {}
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn noop_cache_never_runs_code_and_leaves_state_alone() {
        let cache = NoopCodeCache;
        let mut state = CpuState::new(GuestAddr(0x401000), GuestAddr(0x7000));
        let before = state.clone();
        assert_eq!(cache.try_run(&mut state, &AddressSpace::new()), None);
        assert_eq!(state, before);
    }

    #[test]
    fn noop_cache_invalidate_is_harmless() {
        let cache = NoopCodeCache;
        cache.invalidate(GuestAddr(0));
        cache.invalidate(GuestAddr(u64::MAX));
        assert_eq!(
            cache.try_run(&mut CpuState::default(), &AddressSpace::new()),
            None
        );
    }

    #[test]
    fn usable_as_trait_object() {
        let cache: Box<dyn CodeCache> = Box::new(NoopCodeCache);
        assert!(
            cache
                .try_run(&mut CpuState::default(), &AddressSpace::new())
                .is_none()
        );
    }

    #[test]
    fn invalidation_and_fallback_preserve_guest_code() {
        use paludarium_mmu::{MappingKind, Prot};

        let cache = NoopCodeCache;
        let page = GuestAddr(0x401000);
        let mut mem = AddressSpace::new();
        assert!(
            mem.map(Some(page), 4096, Prot::READ_EXEC, MappingKind::ElfSegment)
                .is_ok()
        );
        assert!(mem.write_initial(page, &[0x0f, 0x05]).is_ok());
        let mut state = CpuState::new(page, GuestAddr(0x7000));
        let before = state.clone();
        cache.invalidate(page);
        assert_eq!(cache.try_run(&mut state, &mem), None);
        let mut code = [0; 2];
        assert!(mem.fetch(page, &mut code).is_ok());
        assert_eq!(code, [0x0f, 0x05]);
        assert_eq!(state, before);
    }

    #[test]
    fn shared_cache_supports_concurrent_fallback_and_invalidation() {
        let cache: std::sync::Arc<dyn CodeCache> = std::sync::Arc::new(NoopCodeCache);
        std::thread::scope(|scope| {
            let handles: Vec<_> = (0..4)
                .map(|index| {
                    let cache = std::sync::Arc::clone(&cache);
                    scope.spawn(move || {
                        let mut state =
                            CpuState::new(GuestAddr(0x401000 + index * 4096), GuestAddr(0x7000));
                        let before = state.clone();
                        let mem = AddressSpace::new();
                        for _ in 0..32 {
                            cache.invalidate(state.rip);
                            assert_eq!(cache.try_run(&mut state, &mem), None);
                            assert_eq!(state, before);
                        }
                    })
                })
                .collect();
            for handle in handles {
                assert!(handle.join().is_ok());
            }
        });
    }
}
