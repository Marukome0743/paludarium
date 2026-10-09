//! Linux system-call layer for paludarium (contract C8).
//!
//! The kernel owns the process and thread state (ADR-002). It receives the
//! CPU's [`ExitReason`] and decides what happens next: system calls are
//! dispatched by number through an explicit table and unknown numbers return
//! `-ENOSYS`; nothing is ever passed through to the host by number
//! (BR3.1, BR3.2, NFR4.1). Guest exceptions end the process with the
//! matching signal; U1 records signal registrations but never delivers
//! signals (BR4.5).
#![forbid(unsafe_code)]

mod inbox;
mod signals;
pub use inbox::SignalInbox;
mod files;
mod futex;
mod syscalls;
mod threads;
pub use threads::ThreadGroup;

use std::collections::BTreeMap;
use std::sync::Arc;
use std::sync::atomic::AtomicBool;

use paludarium_cpu::{CpuState, reg};
use paludarium_host::Host;
use paludarium_loader::LoadedImage;
use paludarium_mmu::AddressSpace;
use paludarium_types::{ExitReason, ExitStatus, signal};

pub use syscalls::{SyscallTable, nr};

/// What the execution loop does after the kernel handled a stop.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[non_exhaustive]
pub enum Next {
    /// Continue running the thread.
    Resume,
    /// Job-control stop: retain CPU state until SIGCONT or SIGKILL.
    Stopped,
    /// The process has ended.
    Exit(ExitStatus),
}

/// A guest thread: its id and registers (entities.md CpuState).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Thread {
    pub tid: u32,
    pub cpu: CpuState,
}

/// A registered signal action (`struct k_sigaction` on x86-64). Recorded
/// only; U1 does not deliver signals (BR4.5).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct SignalAction {
    pub handler: u64,
    pub flags: u64,
    pub restorer: u64,
    pub mask: u64,
}

/// The alternate signal stack (`stack_t`).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct AltStack {
    pub sp: u64,
    pub flags: u32,
    pub size: u64,
}

/// `SS_DISABLE`.
pub const SS_DISABLE: u32 = 2;

impl Default for AltStack {
    fn default() -> Self {
        AltStack {
            sp: 0,
            flags: SS_DISABLE,
            size: 0,
        }
    }
}

/// The guest process (entities.md Process). U1 has exactly one.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Process {
    pub pid: u32,
    pub signal_actions: BTreeMap<i32, SignalAction>,
    pub signal_mask: u64,
    pub alt_stack: AltStack,
    pub clear_child_tid: u64,
    pub exit_status: Option<ExitStatus>,
    pub(crate) pending: Vec<signals::PendingSignal>,
    pub(crate) frames: Vec<signals::SavedFrame>,
    pub(crate) timer: signals::RealTimer,
    pub stopped: bool,
}

/// The emulated Linux kernel for one process.
pub struct Kernel {
    host: Arc<dyn Host>,
    process: Process,
    table: SyscallTable,
    files: files::Files,
    cancellation: Arc<AtomicBool>,
    inbox: Arc<SignalInbox>,
    group: Arc<ThreadGroup>,
    pending_child: Option<(Box<Kernel>, Thread)>,
}

impl Kernel {
    /// Creates a kernel that performs host I/O through `host` (BR6.1).
    pub fn new(host: Arc<dyn Host>) -> Self {
        let files = files::Files::with_host(Arc::clone(&host));
        Kernel {
            host,
            process: Process {
                pid: 1,
                ..Process::default()
            },
            table: SyscallTable::u1(),
            files,
            cancellation: Arc::new(AtomicBool::new(false)),
            inbox: Arc::new(SignalInbox::default()),
            group: Arc::new(ThreadGroup::default()),
            pending_child: None,
        }
    }

    /// Explicit virtual terminal dimensions override Host dimensions on stdio.
    #[must_use]
    pub fn with_terminal_size(mut self, columns: u16, rows: u16) -> Self {
        self.files.terminal_size = Some((columns, rows));
        self
    }

    /// Connects the filesystem shared with the loader.
    pub fn with_file_system(mut self, fs: Arc<dyn paludarium_vfs::FileSystem>) -> Self {
        self.files.fs = fs;
        self
    }

    /// Connects the session's bounded-wait cancellation token.
    pub fn with_cancellation(mut self, cancellation: Arc<AtomicBool>) -> Self {
        self.cancellation = cancellation;
        self
    }

    /// Connects the runtime's single-process signal queue and wait wake token.
    pub fn with_signal_inbox(mut self, inbox: Arc<SignalInbox>) -> Self {
        self.group.set_process_inbox(Arc::clone(&inbox));
        self.cancellation = inbox.wake_token();
        self.inbox = inbox;
        self
    }

    /// The process state.
    #[must_use]
    pub fn process(&self) -> &Process {
        &self.process
    }

    /// Creates the initial thread for a loaded image: rip at the entry
    /// point, rsp at the initial stack, everything else zero.
    #[must_use]
    pub fn spawn_initial(&self, image: &LoadedImage) -> Thread {
        self.group
            .register(self.process.pid, Arc::clone(&self.inbox));
        Thread {
            tid: self.process.pid,
            cpu: CpuState::new(image.entry_point, image.initial_stack_pointer),
        }
    }

    fn terminate(&mut self, signal: i32) -> Next {
        let status = ExitStatus::Signaled(signal);
        self.process.exit_status = Some(status);
        self.group.stop(status);
        Next::Exit(status)
    }

    /// Queues a standard signal for the process's current thread.
    pub fn queue_signal(&mut self, number: i32) -> Result<(), paludarium_types::Errno> {
        if number == 18 {
            self.group.job_continue();
        }
        if !(1..=64).contains(&number) {
            return Err(paludarium_types::Errno::EINVAL);
        }
        signals::queue(&mut self.process, signals::PendingSignal::user(number, 0));
        Ok(())
    }

    /// Delivers an unblocked pending signal at a CPU/Kernel boundary.
    pub fn checkpoint(&mut self, thread: &mut Thread, mem: &AddressSpace) -> Next {
        if let Some(status) = self.group.status() {
            return Next::Exit(status);
        }
        self.sync_actions();
        self.group.drain_process(&mut self.process);
        self.inbox.drain(&mut self.process);
        if self.process.pending.iter().any(|s| s.number == 18) {
            self.group.job_continue();
        }
        if let Ok(now) = self.host.clock(paludarium_host::ClockId::Monotonic) {
            signals::expire_timer(&mut self.process, now);
        }
        while let Some(index) = signals::next_pending(&self.process, false) {
            let signal = self.process.pending.remove(index);
            let action = self
                .process
                .signal_actions
                .get(&signal.number)
                .copied()
                .unwrap_or_default();
            if signal.synchronous
                && (action.handler <= 1
                    || self.process.signal_mask & (1u64 << (signal.number - 1)) != 0)
            {
                return self.terminate(signal.number);
            }
            if action.handler == 1
                || action.handler == 0 && matches!(signal.number, 17 | 18 | 23 | 28)
            {
                continue;
            }
            if signal.number == 19 || action.handler == 0 && matches!(signal.number, 20..=22) {
                self.process.stopped = true;
                self.group.job_stop();
                return Next::Stopped;
            }
            if action.handler == 0 || signal.number == 9 {
                return self.terminate(signal.number);
            }
            if signals::install(&mut self.process, &mut thread.cpu, mem, signal, action).is_err() {
                return self.terminate(signal::SIGSEGV);
            }
            if action.flags & signals::SA_RESETHAND != 0 {
                self.group
                    .set_action(signal.number, SignalAction::default());
            }
            return Next::Resume;
        }
        if self.process.stopped {
            Next::Stopped
        } else {
            Next::Resume
        }
    }

    /// Handles a stop of `thread` (W3, W4).
    pub fn handle(&mut self, thread: &mut Thread, mem: &AddressSpace, reason: ExitReason) -> Next {
        let fault = match reason {
            ExitReason::PageFault {
                rip,
                addr,
                write,
                fetch,
                mapped,
                present,
            } => {
                thread.cpu.rip = rip;
                Some(signals::PendingSignal {
                    target: signals::PendingTarget::Thread,
                    number: signal::SIGSEGV,
                    code: if mapped { 2 } else { 1 },
                    addr: addr.0,
                    trap: 14,
                    error: 4
                        | (u64::from(write) * 2)
                        | u64::from(present)
                        | (u64::from(fetch) * 16),
                    synchronous: true,
                })
            }
            ExitReason::InvalidOpcode { rip, .. } => {
                thread.cpu.rip = rip;
                Some(signals::PendingSignal {
                    target: signals::PendingTarget::Thread,
                    number: signal::SIGILL,
                    code: 2,
                    addr: rip.0,
                    trap: 6,
                    error: 0,
                    synchronous: true,
                })
            }
            ExitReason::ArithmeticFault { rip } => {
                thread.cpu.rip = rip;
                Some(signals::PendingSignal {
                    target: signals::PendingTarget::Thread,
                    number: signal::SIGFPE,
                    code: 1,
                    addr: rip.0,
                    trap: 0,
                    error: 0,
                    synchronous: true,
                })
            }
            ExitReason::FloatingPointFault { rip, code } => {
                thread.cpu.rip = rip;
                Some(signals::PendingSignal {
                    target: signals::PendingTarget::Thread,
                    number: signal::SIGFPE,
                    code: i32::from(code),
                    addr: rip.0,
                    trap: 19,
                    error: 0,
                    synchronous: true,
                })
            }
            ExitReason::GeneralProtection { rip } | ExitReason::Halt { rip } => {
                thread.cpu.rip = rip;
                Some(signals::PendingSignal {
                    target: signals::PendingTarget::Thread,
                    number: signal::SIGSEGV,
                    code: 128,
                    addr: 0,
                    trap: 13,
                    error: 0,
                    synchronous: true,
                })
            }
            _ => None,
        };
        if let Some(fault) = fault {
            signals::queue(&mut self.process, fault);
            return self.checkpoint(thread, mem);
        }
        match reason {
            ExitReason::Syscall { .. } => self.syscall(thread, mem),
            ExitReason::PageFault { .. }
            | ExitReason::GeneralProtection { .. }
            | ExitReason::Halt { .. } => self.terminate(signal::SIGSEGV),
            ExitReason::InvalidOpcode { .. } => self.terminate(signal::SIGILL),
            ExitReason::ArithmeticFault { .. } | ExitReason::FloatingPointFault { .. } => {
                self.terminate(signal::SIGFPE)
            }
            ExitReason::BudgetExhausted { .. } => self.checkpoint(thread, mem),
            // Later units add stop reasons; until then they end the process.
            _ => self.terminate(signal::SIGSEGV),
        }
    }

    fn syscall(&mut self, thread: &mut Thread, mem: &AddressSpace) -> Next {
        self.sync_actions();
        let number = thread.cpu.gpr[reg::RAX];
        let args = [
            thread.cpu.gpr[reg::RDI],
            thread.cpu.gpr[reg::RSI],
            thread.cpu.gpr[reg::RDX],
            thread.cpu.gpr[reg::R10],
            thread.cpu.gpr[reg::R8],
            thread.cpu.gpr[reg::R9],
        ];
        if let Some(next) = self.thread_syscall(thread, mem, number, args) {
            return next;
        }
        let Some(handler) = self.table.get(number) else {
            thread.cpu.gpr[reg::RAX] = paludarium_types::Errno::ENOSYS.to_syscall_return();
            return Next::Resume;
        };
        let mut ctx = syscalls::Context {
            host: &*self.host,
            files: &mut self.files,
            process: &mut self.process,
            cpu: &mut thread.cpu,
            mem,
            cancellation: &self.cancellation,
            inbox: &self.inbox,
        };
        let outcome = handler(&mut ctx, args);
        if number == syscalls::nr::RT_SIGACTION
            && args[1] != 0
            && let Some(action) = self.process.signal_actions.get(&(args[0] as i32))
        {
            self.group.set_action(args[0] as i32, *action);
        }
        self.inbox.drain(&mut self.process);
        match outcome {
            syscalls::Outcome::Return(value) => {
                thread.cpu.gpr[reg::RAX] = value;
                // Linux exposes the rewound syscall in a SA_RESTART handler's
                // context only when write was interrupted before any transfer.
                if number == syscalls::nr::WRITE
                    && value == paludarium_types::Errno(4).to_syscall_return()
                {
                    let action = signals::next_pending(&self.process, true)
                        .and_then(|index| {
                            self.process
                                .signal_actions
                                .get(&self.process.pending[index].number)
                        })
                        .filter(|action| action.handler > 1);
                    if action.is_some_and(|a| a.flags & 0x1000_0000 != 0)
                        && let Some(rip) = thread.cpu.rip.0.checked_sub(2)
                    {
                        thread.cpu.rip = paludarium_types::GuestAddr(rip);
                        thread.cpu.gpr[reg::RAX] = number;
                    }
                }
                self.checkpoint(thread, mem)
            }
            syscalls::Outcome::Restored => self.checkpoint(thread, mem),
            syscalls::Outcome::BadFrame => self.terminate(signal::SIGSEGV),
            syscalls::Outcome::Exit(code) => {
                let status = ExitStatus::Exited(code & 0xff);
                self.process.exit_status = Some(status);
                Next::Exit(status)
            }
        }
    }
}

#[cfg(test)]
mod tests;

#[cfg(test)]
mod u9_tests;

#[cfg(test)]
mod u5_tests;
