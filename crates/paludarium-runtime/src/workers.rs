//! Each real Host worker owns CPU/decoder/thread context and shares only process resources.
use paludarium_cpu::{DecodeCache, reg, run_cached};
use paludarium_host::{ClockId, Host, ThreadHandle};
use paludarium_jit::CodeCache;
use paludarium_kernel::{Kernel, Next, SignalInbox, Thread, ThreadGroup};
use paludarium_mmu::AddressSpace;
use paludarium_types::{Error, ErrorKind, ExitReason, ExitStatus, signal};
use std::sync::{
    Arc, Mutex, PoisonError,
    atomic::{AtomicBool, Ordering},
};

pub(crate) struct Execution {
    host: Arc<dyn Host>,
    mem: Arc<AddressSpace>,
    group: Arc<ThreadGroup>,
    kill: Arc<AtomicBool>,
    inbox: Arc<SignalInbox>,
    stopped: Arc<AtomicBool>,
    last_stop: Arc<Mutex<Option<ExitReason>>>,
    cache: Arc<dyn CodeCache>,
    budget: u64,
    handles: Mutex<Vec<Box<dyn ThreadHandle>>>,
    results: Mutex<Vec<Result<ExitStatus, Error>>>,
}
impl Execution {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        host: Arc<dyn Host>,
        mem: Arc<AddressSpace>,
        group: Arc<ThreadGroup>,
        kill: Arc<AtomicBool>,
        inbox: Arc<SignalInbox>,
        stopped: Arc<AtomicBool>,
        last_stop: Arc<Mutex<Option<ExitReason>>>,
        cache: Arc<dyn CodeCache>,
        budget: u64,
    ) -> Self {
        Self {
            host,
            mem,
            group,
            kill,
            inbox,
            stopped,
            last_stop,
            cache,
            budget,
            handles: Mutex::new(Vec::new()),
            results: Mutex::new(Vec::new()),
        }
    }
    pub fn execute(self: &Arc<Self>, mut kernel: Kernel, mut thread: Thread) {
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            self.run(&mut kernel, &mut thread)
        }))
        .unwrap_or_else(|_| Err(Error::new(ErrorKind::Host, "execution worker panicked")));
        if result.is_err() {
            self.group.stop(ExitStatus::Signaled(signal::SIGKILL));
        }
        kernel.finish_thread(&thread, &self.mem);
        self.results
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .push(result);
    }
    fn run(
        self: &Arc<Self>,
        kernel: &mut Kernel,
        thread: &mut Thread,
    ) -> Result<ExitStatus, Error> {
        let mut decode = DecodeCache::new();
        loop {
            if self.kill.load(Ordering::SeqCst) {
                self.group.stop(ExitStatus::Signaled(signal::SIGKILL));
            }
            match kernel.checkpoint(thread, &self.mem) {
                Next::Exit(status) => return Ok(status),
                Next::Stopped => {
                    self.stopped.store(true, Ordering::SeqCst);
                    self.pause()?;
                    continue;
                }
                _ => self.stopped.store(false, Ordering::SeqCst),
            }
            let reason = self
                .cache
                .try_run(&mut thread.cpu, &self.mem)
                .unwrap_or_else(|| {
                    run_cached(&mut thread.cpu, &self.mem, self.budget, &mut decode)
                });
            let next = kernel.handle(thread, &self.mem, reason);
            if let Some((child, child_thread)) = kernel.take_child() {
                let tid = child_thread.tid;
                let execution = self.clone();
                match self
                    .host
                    .spawn_thread(Box::new(move || execution.execute(*child, child_thread)))
                {
                    Ok(handle) => self
                        .handles
                        .lock()
                        .unwrap_or_else(PoisonError::into_inner)
                        .push(handle),
                    Err(error) => {
                        kernel.abandon_thread(tid);
                        thread.cpu.gpr[reg::RAX] = error.to_syscall_return();
                    }
                }
            }
            match next {
                Next::Resume | Next::Stopped => {}
                Next::Exit(status) => {
                    if !matches!(reason, ExitReason::Syscall { .. }) {
                        *self
                            .last_stop
                            .lock()
                            .unwrap_or_else(PoisonError::into_inner) = Some(reason);
                    }
                    return Ok(status);
                }
                _ => {
                    return Err(
                        Error::new(ErrorKind::Internal, "unexpected kernel decision")
                            .with_rip(thread.cpu.rip),
                    );
                }
            }
        }
    }
    fn pause(&self) -> Result<(), Error> {
        let clock = ClockId::Monotonic;
        let now = self
            .host
            .clock(clock)
            .map_err(|_| Error::new(ErrorKind::Host, "worker clock"))?;
        self.host
            .wait_until(
                clock,
                now.saturating_add(10_000_000),
                &self.inbox.wake_token(),
            )
            .map_err(|_| Error::new(ErrorKind::Host, "worker wait"))?;
        Ok(())
    }
    pub fn finish(&self) -> Result<ExitStatus, Error> {
        while self.group.active_threads() != 0 {
            if self.kill.load(Ordering::SeqCst) {
                self.group.stop(ExitStatus::Signaled(signal::SIGKILL));
            }
            if let Err(error) = self.pause() {
                self.group.stop(ExitStatus::Signaled(signal::SIGKILL));
                return Err(error);
            }
        }
        let handles =
            std::mem::take(&mut *self.handles.lock().unwrap_or_else(PoisonError::into_inner));
        for handle in handles {
            handle
                .join()
                .map_err(|_| Error::new(ErrorKind::Host, "worker join"))?;
        }
        self.stopped.store(false, Ordering::SeqCst);
        let mut results = self.results.lock().unwrap_or_else(PoisonError::into_inner);
        if let Some(index) = results.iter().position(Result::is_err) {
            return results.remove(index);
        }
        if let Some(status) = self.group.status() {
            return Ok(status);
        }
        results
            .pop()
            .unwrap_or_else(|| Err(Error::new(ErrorKind::Internal, "missing worker result")))
    }
}
