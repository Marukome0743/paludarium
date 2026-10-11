use paludarium::{Config, ExitStatus, Mount, Session};
use paludarium_host::{
    ClockId, DirectoryEntry, FileHandle, FileStat, Host, HostFs, NativeHost, StreamId,
    TerminalInfo, ThreadHandle, WaitOutcome, WaitToken, testing::RecordingHost,
};
use paludarium_types::Errno;
use std::collections::VecDeque;
use std::path::{Path, PathBuf};
use std::sync::{
    Arc, Mutex,
    atomic::{AtomicBool, Ordering},
};
use std::time::{Duration, Instant};

type DiagnosticCalls = Option<Arc<Mutex<VecDeque<String>>>>;
struct CaptureHost(RecordingHost, Arc<Mutex<Vec<String>>>, DiagnosticCalls);

fn record_call(calls: &DiagnosticCalls, event: impl FnOnce() -> String) {
    if let Some(calls) = calls {
        let mut calls = calls.lock().unwrap();
        if calls.len() == 64 {
            calls.pop_front();
        }
        calls.push_back(format!("{:?} {}", std::thread::current().id(), event()));
    }
}

struct TraceFs {
    inner: Arc<dyn HostFs>,
    root: PathBuf,
    trace: Arc<Mutex<Vec<String>>>,
}
impl TraceFs {
    fn record(&self, event: String) {
        self.trace
            .lock()
            .unwrap()
            .push(format!("{} {event}", self.root.display()));
    }
}
impl HostFs for TraceFs {
    fn open(&self, path: &[u8], flags: u32, mode: u32) -> Result<Arc<dyn FileHandle>, Errno> {
        let result = self.inner.open(path, flags, mode);
        if path.ends_with(b"package.json") {
            self.record(format!(
                "open {:?} flags={flags} => {:?}",
                String::from_utf8_lossy(path),
                result.as_ref().map(|_| ())
            ));
            return result.map(|inner| {
                Arc::new(TraceFile {
                    inner,
                    path: path.to_vec(),
                    trace: self.trace.clone(),
                }) as Arc<dyn FileHandle>
            });
        }
        result
    }
    fn metadata(&self, path: &[u8], follow: bool) -> Result<FileStat, Errno> {
        let result = self.inner.metadata(path, follow);
        if path.starts_with(b"node_modules") || path.ends_with(b"package.json") {
            self.record(format!(
                "metadata {:?} follow={follow} => {result:?}",
                String::from_utf8_lossy(path)
            ));
        }
        result
    }
    fn mkdir(&self, path: &[u8], mode: u32) -> Result<(), Errno> {
        self.inner.mkdir(path, mode)
    }
    fn unlink(&self, path: &[u8], directory: bool) -> Result<(), Errno> {
        self.inner.unlink(path, directory)
    }
    fn link(&self, old: &[u8], new: &[u8]) -> Result<(), Errno> {
        self.inner.link(old, new)
    }
    fn symlink(&self, target: &[u8], path: &[u8]) -> Result<(), Errno> {
        let result = self.inner.symlink(target, path);
        self.record(format!(
            "symlink {:?} target={:?} => {result:?}",
            String::from_utf8_lossy(path),
            String::from_utf8_lossy(target)
        ));
        result
    }
    fn readlink(&self, path: &[u8]) -> Result<Vec<u8>, Errno> {
        let result = self.inner.readlink(path);
        self.record(format!(
            "readlink {:?} => {:?}",
            String::from_utf8_lossy(path),
            result.as_ref().map(|bytes| String::from_utf8_lossy(bytes))
        ));
        result
    }
    fn rename(&self, old: &[u8], new: &[u8]) -> Result<(), Errno> {
        self.inner.rename(old, new)
    }
    fn read_dir(&self, path: &[u8]) -> Result<Vec<DirectoryEntry>, Errno> {
        self.inner.read_dir(path)
    }
}
struct TraceFile {
    inner: Arc<dyn FileHandle>,
    path: Vec<u8>,
    trace: Arc<Mutex<Vec<String>>>,
}
impl FileHandle for TraceFile {
    fn readiness(&self) -> Result<(u32, u64, u64), Errno> {
        self.inner.readiness()
    }
    fn as_any(&self) -> Option<&dyn std::any::Any> {
        self.inner.as_any()
    }
    fn stdio_channel(&self) -> Option<u32> {
        self.inner.stdio_channel()
    }
    fn guest_path_hint(&self) -> Option<Vec<u8>> {
        self.inner.guest_path_hint()
    }
    fn read(&self, bytes: &mut [u8]) -> Result<usize, Errno> {
        let result = self.inner.read(bytes);
        self.trace.lock().unwrap().push(format!(
            "read {:?} => {:?}",
            String::from_utf8_lossy(&self.path),
            result
                .as_ref()
                .map(|count| String::from_utf8_lossy(&bytes[..*count]))
        ));
        result
    }
    fn write(&self, bytes: &[u8]) -> Result<usize, Errno> {
        self.inner.write(bytes)
    }
    fn seek(&self, offset: i64, whence: u32) -> Result<u64, Errno> {
        self.inner.seek(offset, whence)
    }
    fn stat(&self) -> Result<FileStat, Errno> {
        self.inner.stat()
    }
    fn truncate(&self, size: u64) -> Result<(), Errno> {
        self.inner.truncate(size)
    }
    fn flock(&self, op: u32) -> Result<(), Errno> {
        self.inner.flock(op)
    }
    fn flags(&self) -> u32 {
        self.inner.flags()
    }
    fn set_flags(&self, flags: u32) -> Result<(), Errno> {
        self.inner.set_flags(flags)
    }
}
impl Host for CaptureHost {
    fn spawn_thread(&self, task: Box<dyn FnOnce() + Send>) -> Result<Box<dyn ThreadHandle>, Errno> {
        let calls = self.2.clone();
        NativeHost::new().spawn_thread(Box::new(move || {
            record_call(&calls, || "worker start".to_owned());
            task();
            record_call(&calls, || "worker return".to_owned());
        }))
    }
    fn wait_on(
        &self,
        token: &WaitToken,
        expected: u32,
        deadline: Option<(ClockId, u64)>,
        cancel: &AtomicBool,
    ) -> Result<WaitOutcome, Errno> {
        record_call(&self.2, || {
            format!("wait_on {token:p} expected={expected} deadline={deadline:?} start")
        });
        let result = NativeHost::new().wait_on(token, expected, deadline, cancel);
        record_call(&self.2, || format!("wait_on {token:p} => {result:?}"));
        result
    }
    fn wake(&self, token: &WaitToken) {
        record_call(&self.2, || format!("wake {token:p}"));
        NativeHost::new().wake(token);
    }
    fn terminal_info(&self, stream: StreamId) -> Result<Option<TerminalInfo>, Errno> {
        // CaptureHost previously used Host's non-terminal default unchanged.
        record_call(&self.2, || format!("terminal_info {stream:?} => Ok(None)"));
        Ok(None)
    }
    fn read_stdin(&self, bytes: &mut [u8]) -> Result<usize, paludarium_types::Errno> {
        self.0.read_stdin(bytes)
    }
    fn write_stdout(&self, bytes: &[u8]) -> Result<usize, paludarium_types::Errno> {
        self.0.write_stdout(bytes)
    }
    fn write_stderr(&self, bytes: &[u8]) -> Result<usize, paludarium_types::Errno> {
        self.0.write_stderr(bytes)
    }
    fn random_bytes(&self, bytes: &mut [u8]) -> Result<(), paludarium_types::Error> {
        NativeHost::new().random_bytes(bytes)
    }
    fn clock(&self, clock: ClockId) -> Result<u64, paludarium_types::Errno> {
        let result = NativeHost::new().clock(clock);
        record_call(&self.2, || format!("clock {clock:?} => {result:?}"));
        result
    }
    fn wait_until(
        &self,
        clock: ClockId,
        deadline: u64,
        aborted: &AtomicBool,
    ) -> Result<WaitOutcome, paludarium_types::Errno> {
        record_call(&self.2, || {
            format!("wait_until {clock:?} deadline={deadline} start")
        });
        let result = NativeHost::new().wait_until(clock, deadline, aborted);
        record_call(&self.2, || {
            format!("wait_until {clock:?} deadline={deadline} => {result:?}")
        });
        result
    }
    fn mount_fs(
        &self,
        root: &Path,
    ) -> Result<Arc<dyn paludarium_host::HostFs>, paludarium_types::Errno> {
        NativeHost::new().mount_fs(root).map(|inner| {
            Arc::new(TraceFs {
                inner,
                root: root.to_path_buf(),
                trace: self.1.clone(),
            }) as Arc<dyn HostFs>
        })
    }
}

fn fixture_files(config: &mut Config, directory: &Path, guest: &str) {
    for entry in std::fs::read_dir(directory).unwrap() {
        let entry = entry.unwrap();
        let path = format!("{guest}/{}", entry.file_name().to_str().unwrap());
        if entry.file_type().unwrap().is_dir() {
            fixture_files(config, &entry.path(), &path);
        } else {
            let mode = fixture_mode(&entry.path());
            assert_eq!(
                mode, 0o644,
                "U13 fixture permissions must match native 0644"
            );
            *config = std::mem::take(config).with_file_mode(
                path,
                std::fs::read(entry.path()).unwrap(),
                mode,
            );
        }
    }
}

#[cfg(unix)]
fn fixture_mode(path: &Path) -> u32 {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(path).unwrap().permissions().mode() & 0o7777
}

#[cfg(windows)]
fn fixture_mode(path: &Path) -> u32 {
    let metadata = std::fs::metadata(path).unwrap();
    assert!(metadata.is_file() && !metadata.permissions().readonly());
    // Observe the existing Windows Host's guest metadata, not Python's
    // synthesized Unix permission bits or a fabricated native chmod result.
    let fs = NativeHost::new().mount_fs(path.parent().unwrap()).unwrap();
    let name = path.file_name().unwrap().to_str().unwrap().as_bytes();
    fs.metadata(name, true).unwrap().mode & 0o7777
}

/// Executed only as a child of the 30-second Python group watchdog.
pub fn operation() {
    let directory = PathBuf::from(std::env::var_os("PALUDARIUM_U13_OPERATION").unwrap());
    let binary = PathBuf::from(std::env::var_os("PALUDARIUM_U13_BINARY").unwrap());
    let mut args = vec![b"/program".to_vec()];
    args.extend(
        std::fs::read_to_string(directory.join("args"))
            .unwrap()
            .lines()
            .map(|s| s.as_bytes().to_vec()),
    );
    let mut config = Config::new("/program", args)
        .with_file("/program", std::fs::read(binary).unwrap())
        .with_file("/tmp/.u10", Vec::new())
        .with_file("/home/u10/.u10", Vec::new());
    for line in std::fs::read_to_string(directory.join("environment"))
        .unwrap()
        .lines()
    {
        let (key, value) = line.split_once('=').unwrap();
        config
            .env
            .push((key.as_bytes().to_vec(), value.as_bytes().to_vec()));
    }
    if let Some(fixture) = std::env::var_os("PALUDARIUM_U13_FIXTURE") {
        let fixture = PathBuf::from(fixture).canonicalize().unwrap();
        if std::env::var_os("PALUDARIUM_U13_MOUNTED").is_some() {
            config.mounts.push(Mount {
                host: fixture.join("app"),
                guest: b"/".to_vec(),
            });
            config.mounts.push(Mount {
                host: fixture.join("outside"),
                guest: b"/outside".to_vec(),
            });
        } else {
            fixture_files(&mut config, &fixture.join("app"), "");
            fixture_files(&mut config, &fixture.join("outside"), "/outside");
        }
    }
    let host = Arc::new(CaptureHost(
        RecordingHost::new(),
        Arc::new(Mutex::new(Vec::new())),
        std::env::var("PALUDARIUM_U13_DIAGNOSTIC")
            .ok()
            .filter(|s| s == "1")
            .map(|_| Arc::new(Mutex::new(VecDeque::new()))),
    ));
    let fixture_modes = if std::env::var_os("PALUDARIUM_U13_MOUNTED").is_some() {
        let fixture = PathBuf::from(std::env::var_os("PALUDARIUM_U13_FIXTURE").unwrap());
        [
            ("app/package.json", "/package.json"),
            ("app/filedep/package.json", "/filedep/package.json"),
            (
                "outside/linked/package.json",
                "/outside/linked/package.json",
            ),
        ]
        .iter()
        .map(|(source, guest)| format!("{guest}\t{}\n", fixture_mode(&fixture.join(source))))
        .collect::<String>()
    } else {
        config
            .file_modes
            .iter()
            .map(|(path, mode)| format!("{}\t{mode}\n", String::from_utf8_lossy(path)))
            .collect::<String>()
    };
    std::fs::write(directory.join("fixture-modes"), fixture_modes).unwrap();
    let session = Arc::new(Session::new(config, host.clone()).unwrap());
    let finished = Arc::new(AtomicBool::new(false));
    if host.2.is_some() {
        let host = host.clone();
        let directory = directory.clone();
        let session = session.clone();
        let finished = finished.clone();
        std::thread::spawn(move || {
            std::thread::sleep(Duration::from_secs(25));
            if finished.load(Ordering::Acquire) {
                return;
            }
            // Diagnostic-only host files; no guest FS call, kill, signal or stop.
            let calls = host
                .2
                .as_ref()
                .unwrap()
                .lock()
                .unwrap()
                .iter()
                .cloned()
                .collect::<Vec<_>>();
            std::fs::write(
                directory.join("diagnostic-calls.log"),
                calls.join("\n") + "\n",
            )
            .unwrap();
            std::fs::write(
                directory.join("diagnostic-fs.log"),
                host.1.lock().unwrap().join("\n") + "\n",
            )
            .unwrap();
            std::fs::write(directory.join("diagnostic-stdout"), host.0.stdout()).unwrap();
            std::fs::write(directory.join("diagnostic-stderr"), host.0.stderr()).unwrap();
            std::fs::write(
                directory.join("diagnostic-state"),
                format!(
                    "process={} elapsed=25s completed=false stopped={}\n",
                    std::process::id(),
                    session.is_stopped()
                ),
            )
            .unwrap();
        });
    }
    let started = Instant::now();
    let result = session.run();
    finished.store(true, Ordering::Release);
    std::fs::write(
        directory.join("host-fs-trace.log"),
        host.1.lock().unwrap().join("\n") + "\n",
    )
    .unwrap();
    std::fs::write(directory.join("stdout"), host.0.stdout()).unwrap();
    std::fs::write(directory.join("stderr"), host.0.stderr()).unwrap();
    std::fs::write(
        directory.join("stop"),
        format!("{:?}\n{result:?}", session.termination_detail()),
    )
    .unwrap();
    std::fs::write(
        directory.join("seconds"),
        started.elapsed().as_secs_f64().to_string(),
    )
    .unwrap();
    let status = match result {
        Ok(ExitStatus::Exited(code)) => code,
        Ok(ExitStatus::Signaled(signal)) => -signal,
        Err(_) | Ok(_) => -255,
    };
    std::fs::write(directory.join("exit"), status.to_string()).unwrap();
}
