//! Compare/register and wake share a queue lock; MMU is always acquired second.
use paludarium_host::WaitToken;
use paludarium_mmu::AddressSpace;
use paludarium_types::{Errno, GuestAddr};
use std::{
    collections::BTreeMap,
    sync::{
        Arc, Mutex, PoisonError,
        atomic::{AtomicU32, Ordering},
    },
};
type Key = (u64, u64, bool);
pub(crate) struct Waiter {
    pub token: WaitToken,
    pub state: AtomicU32,
    mask: u32,
}
#[derive(Default)]
pub(crate) struct Futexes {
    queues: Mutex<BTreeMap<Key, Vec<Arc<Waiter>>>>,
}
impl Futexes {
    pub fn register(
        &self,
        mem: &AddressSpace,
        addr: u64,
        private: bool,
        value: u32,
        mask: u32,
    ) -> Result<Arc<Waiter>, Errno> {
        if addr & 3 != 0 || mask == 0 {
            return Err(Errno::EINVAL);
        }
        let mut queues = self.queues.lock().unwrap_or_else(PoisonError::into_inner);
        let mut bytes = [0; 4];
        mem.read(GuestAddr(addr), &mut bytes)
            .map_err(|_| Errno::EFAULT)?;
        if u32::from_le_bytes(bytes) != value {
            return Err(Errno::EAGAIN);
        }
        let waiter = Arc::new(Waiter {
            token: WaitToken::default(),
            state: AtomicU32::new(0),
            mask,
        });
        queues
            .entry((mem.id(), addr, private))
            .or_default()
            .push(waiter.clone());
        Ok(waiter)
    }
    pub fn finish(
        &self,
        mem: &AddressSpace,
        addr: u64,
        private: bool,
        waiter: &Arc<Waiter>,
        result: u32,
    ) -> u32 {
        let mut queues = self.queues.lock().unwrap_or_else(PoisonError::into_inner);
        if waiter.state.load(Ordering::SeqCst) == 0 {
            waiter.state.store(result, Ordering::SeqCst);
            let key = (mem.id(), addr, private);
            if let Some(queue) = queues.get_mut(&key) {
                queue.retain(|w| !Arc::ptr_eq(w, waiter));
                if queue.is_empty() {
                    queues.remove(&key);
                }
            }
        }
        waiter.state.load(Ordering::SeqCst)
    }
    pub fn wake(
        &self,
        mem: &AddressSpace,
        addr: u64,
        private: bool,
        count: u32,
        mask: u32,
    ) -> Result<u64, Errno> {
        if addr & 3 != 0 || mask == 0 {
            return Err(Errno::EINVAL);
        }
        let mut queues = self.queues.lock().unwrap_or_else(PoisonError::into_inner);
        // Validate before consulting queues, including when no waiter exists.
        mem.check_read(GuestAddr(addr), 4)
            .map_err(|_| Errno::EFAULT)?;
        let key = (mem.id(), addr, private);
        let mut woke = 0;
        if let Some(queue) = queues.get_mut(&key) {
            queue.retain(|waiter| {
                if woke < count && waiter.mask & mask != 0 {
                    waiter.state.store(1, Ordering::SeqCst);
                    waiter.token.notify();
                    woke += 1;
                    false
                } else {
                    true
                }
            });
            if queue.is_empty() {
                queues.remove(&key);
            }
        }
        Ok(u64::from(woke))
    }
}
