//! Each real Host worker owns CPU/decoder/thread context and shares only process resources.
use paludarium_cpu::{DecodeCache, reg, run_cached};
use paludarium_host::{ClockId, Host, ThreadHandle};
use paludarium_jit::CodeCache;
use paludarium_kernel::{Kernel, Next, Processes, SignalInbox, Thread, ThreadGroup};
use paludarium_mmu::AddressSpace;
use paludarium_types::{Error, ErrorKind, ExitReason, ExitStatus, signal};
use std::sync::{
    Arc, Mutex, PoisonError,
    atomic::{AtomicBool, Ordering},
};

// Temporary U13 observation: independent Host-side state, never a guest operation.
#[derive(Clone, Copy, Debug)]
struct U13Snapshot {
    host: std::thread::ThreadId,
    pid: u32,
    tid: u32,
    phase: &'static str,
    rip: u64,
    registers: [u64; 7],
    clear_child_tid: u64,
    stopped: bool,
    exit: Option<ExitStatus>,
    reason: Option<ExitReason>,
    next: Option<Next>,
}
impl U13Snapshot {
    fn text(self) -> String {
        format!(
            "host={:?} pid={} tid={} phase={} rip={:#x} rax={:#x} args={:x?} clear_child_tid={:#x} stopped={} exit={:?} reason={:?} next={:?}",
            self.host,
            self.pid,
            self.tid,
            self.phase,
            self.rip,
            self.registers[0],
            &self.registers[1..],
            self.clear_child_tid,
            self.stopped,
            self.exit,
            self.reason,
            self.next
        )
    }
}
struct U13Diagnostic {
    rows: Mutex<std::collections::BTreeMap<u32, std::collections::VecDeque<U13Snapshot>>>,
    finished: AtomicBool,
}
impl U13Diagnostic {
    fn start() -> Option<Arc<Self>> {
        if std::env::var("PALUDARIUM_U13_DIAGNOSTIC").ok().as_deref() != Some("1") {
            return None;
        }
        let directory = std::env::var_os("PALUDARIUM_U13_OPERATION")?;
        let observation = Arc::new(Self {
            rows: Mutex::new(std::collections::BTreeMap::new()),
            finished: AtomicBool::new(false),
        });
        let copy = observation.clone();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_secs(25));
            if copy.finished.load(Ordering::Acquire) {
                return;
            }
            // No Kernel/Process/Session lock is acquired by the observer.
            let rows = copy.rows.lock().unwrap_or_else(PoisonError::into_inner);
            let snapshots = rows
                .values()
                .flat_map(|rows| rows.iter())
                .copied()
                .collect::<Vec<_>>();
            drop(rows);
            let text = snapshots
                .into_iter()
                .map(U13Snapshot::text)
                .collect::<Vec<_>>()
                .join("\n");
            let _ = std::fs::write(
                std::path::PathBuf::from(directory).join("diagnostic-runtime.log"),
                text + "\n",
            );
        });
        Some(observation)
    }
    fn record(
        &self,
        kernel: &Kernel,
        thread: &Thread,
        phase: &'static str,
        reason: Option<ExitReason>,
        next: Option<Next>,
    ) {
        let registers = &thread.cpu.gpr;
        let snapshot = U13Snapshot {
            host: std::thread::current().id(),
            pid: kernel.process().pid,
            tid: thread.tid,
            phase,
            rip: thread.cpu.rip.0,
            registers: [
                registers[reg::RAX],
                registers[reg::RDI],
                registers[reg::RSI],
                registers[reg::RDX],
                registers[reg::R10],
                registers[reg::R8],
                registers[reg::R9],
            ],
            clear_child_tid: thread.state.clear_child_tid,
            stopped: thread.state.stopped,
            exit: thread.state.exit_status,
            reason,
            next,
        };
        let mut rows = self.rows.lock().unwrap_or_else(PoisonError::into_inner);
        let row = rows.entry(thread.tid).or_default();
        if row.len() == 8 {
            row.pop_front();
        }
        row.push_back(snapshot);
    }
}

pub(crate) struct Execution {
    host: Arc<dyn Host>,
    mem: Arc<AddressSpace>,
    group: Arc<ThreadGroup>,
    processes: Arc<Processes>,
    kill: Arc<AtomicBool>,
    inbox: Arc<SignalInbox>,
    stopped: Arc<AtomicBool>,
    last_stop: Arc<Mutex<Option<ExitReason>>>,
    cache: Arc<dyn CodeCache>,
    budget: u64,
    handles: Mutex<Vec<Box<dyn ThreadHandle>>>,
    results: Mutex<Vec<Result<ExitStatus, Error>>>,
    diagnostic: Option<Arc<U13Diagnostic>>,
}
impl Execution {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        host: Arc<dyn Host>,
        mem: Arc<AddressSpace>,
        group: Arc<ThreadGroup>,
        processes: Arc<Processes>,
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
            processes,
            kill,
            inbox,
            stopped,
            last_stop,
            cache,
            budget,
            handles: Mutex::new(Vec::new()),
            results: Mutex::new(Vec::new()),
            diagnostic: U13Diagnostic::start(),
        }
    }
    pub fn execute(self: &Arc<Self>, mut kernel: Kernel, mut thread: Thread) {
        let memory = self.mem.clone();
        self.execute_memory(&mut kernel, &mut thread, memory);
    }
    fn execute_memory(
        self: &Arc<Self>,
        kernel: &mut Kernel,
        thread: &mut Thread,
        mut memory: Arc<AddressSpace>,
    ) {
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            self.run(kernel, thread, &mut memory)
        }))
        .unwrap_or_else(|_| Err(Error::new(ErrorKind::Host, "execution worker panicked")));
        if result.is_err() {
            self.processes
                .stop_all(ExitStatus::Signaled(signal::SIGKILL));
        }
        self.observe(kernel, thread, "before-finish-thread", None, None);
        kernel.finish_thread(thread, &memory);
        self.observe(kernel, thread, "after-finish-thread", None, None);
        kernel.complete_process(
            result
                .as_ref()
                .copied()
                .unwrap_or(ExitStatus::Signaled(signal::SIGKILL)),
        );
        self.observe(kernel, thread, "after-complete-process", None, None);
        if kernel.process().pid == 1 || result.is_err() {
            self.results
                .lock()
                .unwrap_or_else(PoisonError::into_inner)
                .push(result);
        }
    }
    fn run(
        self: &Arc<Self>,
        kernel: &mut Kernel,
        thread: &mut Thread,
        memory: &mut Arc<AddressSpace>,
    ) -> Result<ExitStatus, Error> {
        let mut decode = DecodeCache::new();
        loop {
            self.observe(kernel, thread, "before-checkpoint", None, None);
            if self.kill.load(Ordering::SeqCst) {
                self.processes
                    .stop_all(ExitStatus::Signaled(signal::SIGKILL));
            }
            match kernel.checkpoint(thread, memory) {
                Next::Exit(status) => return Ok(status),
                Next::Stopped => {
                    self.stopped.store(true, Ordering::SeqCst);
                    self.pause()?;
                    continue;
                }
                _ => self.stopped.store(false, Ordering::SeqCst),
            }
            self.observe(kernel, thread, "before-cpu", None, None);
            let reason = self
                .cache
                .try_run(&mut thread.cpu, memory)
                .unwrap_or_else(|| run_cached(&mut thread.cpu, memory, self.budget, &mut decode));
            self.observe(kernel, thread, "before-handle", Some(reason), None);
            let next = kernel.handle(thread, memory, reason);
            self.observe(kernel, thread, "after-handle", Some(reason), Some(next));
            if let Some(replacement) = kernel.take_exec_memory() {
                *memory = replacement;
                decode = DecodeCache::new();
            }
            if let Some((mut child, mut child_thread)) = kernel.take_child() {
                let tid = child_thread.tid;
                let pid = child.process().pid;
                let child_memory = child.take_spawn_memory().unwrap_or_else(|| memory.clone());
                let execution = self.clone();
                match self.host.spawn_thread(Box::new(move || {
                    execution.execute_memory(&mut child, &mut child_thread, child_memory)
                })) {
                    Ok(handle) => self
                        .handles
                        .lock()
                        .unwrap_or_else(PoisonError::into_inner)
                        .push(handle),
                    Err(error) => {
                        kernel.abandon_child(pid, tid);
                        thread.cpu.gpr[reg::RAX] = error.to_syscall_return();
                    }
                }
                if let Err(error) = kernel.wait_vfork(&self.kill) {
                    thread.cpu.gpr[reg::RAX] = error.to_syscall_return();
                }
            }
            match next {
                Next::Resume | Next::Stopped => {}
                Next::Exit(status) => {
                    if !matches!(reason, ExitReason::Syscall { .. }) && kernel.process().pid == 1 {
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
    fn observe(
        &self,
        kernel: &Kernel,
        thread: &Thread,
        phase: &'static str,
        reason: Option<ExitReason>,
        next: Option<Next>,
    ) {
        if let Some(diagnostic) = &self.diagnostic {
            diagnostic.record(kernel, thread, phase, reason, next);
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
        let mut host_error = None;
        while self.processes.active_threads() != 0 {
            if self.kill.load(Ordering::SeqCst) {
                self.processes
                    .stop_all(ExitStatus::Signaled(signal::SIGKILL));
            }
            if let Err(error) = self.pause() {
                self.processes
                    .stop_all(ExitStatus::Signaled(signal::SIGKILL));
                host_error.get_or_insert(error);
            }
        }
        let handles =
            std::mem::take(&mut *self.handles.lock().unwrap_or_else(PoisonError::into_inner));
        for handle in handles {
            if handle.join().is_err() {
                host_error.get_or_insert_with(|| Error::new(ErrorKind::Host, "worker join"));
            }
        }
        self.stopped.store(false, Ordering::SeqCst);
        if let Some(diagnostic) = &self.diagnostic {
            diagnostic.finished.store(true, Ordering::Release);
        }
        if let Some(error) = host_error {
            return Err(error);
        }
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
