//! Session and execution loop for paludarium (contract C10 internals).
//!
//! A [`Session`] places the configured files in the virtual file system,
//! loads the program, and runs the thread loop (W2, W3): the CPU runs for a
//! budget of instructions, the kernel handles each stop, and between budget
//! slices the loop checks whether [`Session::kill`] was requested (BR4.3).
#![forbid(unsafe_code)]

use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, PoisonError};

use paludarium_cpu::{DecodeCache, run_cached};
use paludarium_host::Host;
use paludarium_jit::{CodeCache, NoopCodeCache};
use paludarium_kernel::{Kernel, Next, SignalInbox};
use paludarium_loader::{StartInfo, load};
use paludarium_mmu::AddressSpace;
use paludarium_types::{Error, ErrorKind, ExitReason, ExitStatus, signal};
use paludarium_vfs::{GuestFile, HostFs, MemFs, MountedFs};

/// Instructions run between two checks of the kill request (BR4.3,
/// entities.md SessionConfig: internal, default 100000).
pub const DEFAULT_BUDGET: u64 = 100_000;

/// A host directory shown to the guest (`--mount`). Implemented in U7; U1
/// accepts only an empty list.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Mount {
    pub host: PathBuf,
    pub guest: Vec<u8>,
}

/// Terminal size given to the guest. Used from U9.
/// ```compile_fail
/// use paludarium_runtime::TerminalInfo;
/// let _ = TerminalInfo { columns: 80, rows: 24 };
/// ```
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[non_exhaustive]
pub struct TerminalInfo {
    pub columns: u16,
    pub rows: u16,
}
impl TerminalInfo {
    /// Creates the explicit guest terminal size, including zero dimensions.
    #[must_use]
    pub const fn new(columns: u16, rows: u16) -> Self {
        Self { columns, rows }
    }
}

/// Configuration of one run (C10 `Config`, entities.md SessionConfig).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
#[non_exhaustive]
pub struct Config {
    /// Absolute guest path of the program.
    pub program: Vec<u8>,
    /// argv, including argv[0].
    pub args: Vec<Vec<u8>>,
    pub env: Vec<(Vec<u8>, Vec<u8>)>,
    /// Files placed in the virtual file system before start: (path, content).
    pub files: Vec<(Vec<u8>, Vec<u8>)>,
    pub mounts: Vec<Mount>,
    pub tty: Option<TerminalInfo>,
    /// Only meaningful in wasm; the native build has no JIT.
    pub jit: bool,
}

impl Config {
    /// A configuration running `program` with `args` (argv[0] included).
    #[must_use]
    pub fn new(program: impl Into<Vec<u8>>, args: Vec<Vec<u8>>) -> Self {
        Config {
            program: program.into(),
            args,
            ..Config::default()
        }
    }

    /// Adds an environment variable.
    #[must_use]
    pub fn with_env(mut self, key: impl Into<Vec<u8>>, value: impl Into<Vec<u8>>) -> Self {
        self.env.push((key.into(), value.into()));
        self
    }

    /// Adds a file to place before start.
    #[must_use]
    pub fn with_file(mut self, path: impl Into<Vec<u8>>, content: impl Into<Vec<u8>>) -> Self {
        self.files.push((path.into(), content.into()));
        self
    }
}

/// One guest run.
pub struct Session {
    config: Config,
    mounts: Vec<(Vec<u8>, Arc<dyn HostFs>)>,
    host: Arc<dyn Host>,
    code_cache: Box<dyn CodeCache>,
    budget: u64,
    kill_requested: Arc<AtomicBool>,
    signal_inbox: Arc<SignalInbox>,
    stopped: AtomicBool,
    last_stop: Mutex<Option<ExitReason>>,
}

impl Session {
    /// Validates the configuration. Mounts are not implemented in U1.
    pub fn new(config: Config, host: Arc<dyn Host>) -> Result<Self, Error> {
        if config.program.is_empty() {
            return Err(Error::new(ErrorKind::InvalidProgram, "no program given"));
        }
        let mut mounts = Vec::new();
        let mut validate = MountedFs::new(MemFs::new());
        for mount in &config.mounts {
            let capability = host
                .mount_fs(&mount.host)
                .map_err(|_| Error::new(ErrorKind::Host, "cannot acquire mount root"))?;
            validate
                .mount(mount.guest.clone(), Arc::clone(&capability))
                .map_err(|_| Error::new(ErrorKind::InvalidProgram, "invalid guest mount"))?;
            mounts.push((mount.guest.clone(), capability));
        }
        Ok(Session {
            mounts,
            config,
            host,
            code_cache: Box::new(NoopCodeCache),
            budget: DEFAULT_BUDGET,
            kill_requested: Arc::new(AtomicBool::new(false)),
            signal_inbox: Arc::new(SignalInbox::default()),
            stopped: AtomicBool::new(false),
            last_stop: Mutex::new(None),
        })
    }

    /// Sets the number of instructions between kill checks (tests).
    #[must_use]
    pub fn with_budget(mut self, budget: u64) -> Self {
        self.budget = budget.max(1);
        self
    }

    /// Requests the guest to stop; it ends with SIGKILL at the next budget
    /// boundary (BR4.3).
    pub fn kill(&self) {
        self.kill_requested.store(true, Ordering::SeqCst);
        self.signal_inbox.interrupt();
    }

    /// Sends a Linux signal to the single guest process (U4).
    pub fn signal(&self, number: i32) -> Result<(), paludarium_types::Errno> {
        self.signal_inbox.send(number)
    }

    /// Whether the execution loop has observed a job-control stop.
    #[must_use]
    pub fn is_stopped(&self) -> bool {
        self.stopped.load(Ordering::SeqCst)
    }

    /// The CPU stop that ended the guest, if it ended by a guest exception
    /// (for diagnostics; not part of the guest-visible result).
    #[must_use]
    pub fn termination_detail(&self) -> Option<ExitReason> {
        *self
            .last_stop
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
    }

    fn file_system(&self) -> Result<MountedFs, Error> {
        let mut fs = MemFs::new();
        fs.mkdir(b"/tmp", 0o1777)
            .map_err(|_| Error::new(ErrorKind::Internal, "temporary directory"))?;
        for (path, content) in &self.config.files {
            fs.add_file(GuestFile::new(path.clone(), content.clone()))
                .map_err(|_| Error::new(ErrorKind::InvalidProgram, "invalid file placement"))?;
        }
        let mut mounted = MountedFs::new(fs);
        for (path, capability) in &self.mounts {
            mounted
                .mount(path.clone(), Arc::clone(capability))
                .map_err(|_| Error::new(ErrorKind::InvalidProgram, "invalid guest mount"))?;
        }
        Ok(mounted)
    }

    /// Runs the guest to completion (W2–W4).
    pub fn run(&self) -> Result<ExitStatus, Error> {
        let fs: Arc<dyn paludarium_vfs::FileSystem> = Arc::new(self.file_system()?);
        let mut random = [0u8; 16];
        self.host.random_bytes(&mut random)?;
        let envp: Vec<Vec<u8>> = self
            .config
            .env
            .iter()
            .map(|(k, v)| {
                let mut s = k.clone();
                s.push(b'=');
                s.extend_from_slice(v);
                s
            })
            .collect();
        let start = StartInfo {
            argv: &self.config.args,
            envp: &envp,
            execfn: &self.config.program,
            random,
        };
        let mut mem = AddressSpace::new();
        let image = load(&*fs, &self.config.program, &start, &mut mem)?;
        let mut kernel = Kernel::new(Arc::clone(&self.host))
            .with_file_system(fs)
            .with_signal_inbox(Arc::clone(&self.signal_inbox));
        if let Some(tty) = self.config.tty {
            kernel = kernel.with_terminal_size(tty.columns, tty.rows);
        }
        let mut thread = kernel.spawn_initial(&image);
        let mut decode_cache = DecodeCache::new();

        loop {
            if self.kill_requested.load(Ordering::SeqCst) {
                self.stopped.store(false, Ordering::SeqCst);
                return Ok(ExitStatus::Signaled(signal::SIGKILL));
            }
            match kernel.checkpoint(&mut thread, &mem) {
                Next::Stopped => {
                    self.stopped.store(true, Ordering::SeqCst);
                    let clock = paludarium_host::ClockId::Monotonic;
                    let now = self
                        .host
                        .clock(clock)
                        .map_err(|_| Error::new(ErrorKind::Host, "stopped process clock"))?;
                    self.host
                        .wait_until(
                            clock,
                            now.saturating_add(10_000_000),
                            &self.signal_inbox.wake_token(),
                        )
                        .map_err(|_| Error::new(ErrorKind::Host, "stopped process wait"))?;
                    continue;
                }
                Next::Exit(status) => {
                    self.stopped.store(false, Ordering::SeqCst);
                    return Ok(status);
                }
                _ => self.stopped.store(false, Ordering::SeqCst),
            }
            let reason = self
                .code_cache
                .try_run(&mut thread.cpu, &mem)
                .unwrap_or_else(|| {
                    run_cached(&mut thread.cpu, &mem, self.budget, &mut decode_cache)
                });
            match kernel.handle(&mut thread, &mut mem, reason) {
                Next::Resume => {}
                Next::Stopped => {}
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
}

#[cfg(test)]
mod tests;

#[cfg(test)]
mod u9_tests;
