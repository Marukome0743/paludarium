use super::*;
use paludarium_host::{ClockId, WaitOutcome, WaitToken};
use paludarium_mmu::{MappingKind, Prot};
use paludarium_types::{Errno, GuestAddr};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Mutex, PoisonError};
const DATA: u64 = 0x600000;
type Action = Box<dyn FnOnce() + Send>;
#[derive(Default)]
struct TestHost {
    now: AtomicU64,
    action: Mutex<Option<Action>>,
}
impl Host for TestHost {
    fn read_stdin(&self, _: &mut [u8]) -> Result<usize, Errno> {
        Ok(0)
    }
    fn write_stdout(&self, b: &[u8]) -> Result<usize, Errno> {
        Ok(b.len())
    }
    fn write_stderr(&self, b: &[u8]) -> Result<usize, Errno> {
        Ok(b.len())
    }
    fn random_bytes(&self, b: &mut [u8]) -> Result<(), paludarium_types::Error> {
        b.fill(0);
        Ok(())
    }
    fn clock(&self, _: ClockId) -> Result<u64, Errno> {
        Ok(self.now.load(Ordering::SeqCst))
    }
    fn wait_on(
        &self,
        token: &WaitToken,
        expected: u32,
        deadline: Option<(ClockId, u64)>,
        cancel: &AtomicBool,
    ) -> Result<WaitOutcome, Errno> {
        let action = self
            .action
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .take();
        if let Some(action) = action {
            action();
        }
        if token.value() != expected {
            return Ok(WaitOutcome::Complete);
        }
        if cancel.load(Ordering::SeqCst) {
            return Ok(WaitOutcome::Interrupted);
        }
        self.now
            .store(deadline.expect("bounded kernel wait").1, Ordering::SeqCst);
        Ok(WaitOutcome::Complete)
    }
}
struct Fixture {
    host: Arc<TestHost>,
    kernel: Kernel,
    thread: Thread,
    mem: AddressSpace,
}
impl Fixture {
    fn new() -> Self {
        let host = Arc::new(TestHost::default());
        let mut mem = AddressSpace::new();
        mem.map(
            Some(GuestAddr(DATA)),
            0x4000,
            Prot::READ_WRITE,
            MappingKind::Anonymous,
        )
        .unwrap();
        Self {
            host: Arc::clone(&host),
            kernel: Kernel::new(host),
            thread: Thread::new(1, Default::default()),
            mem,
        }
    }
    fn ret(&mut self, n: u64, args: [u64; 6]) -> u64 {
        self.thread.cpu.gpr[reg::RAX] = n;
        for (r, v) in [reg::RDI, reg::RSI, reg::RDX, reg::R10, reg::R8, reg::R9]
            .into_iter()
            .zip(args)
        {
            self.thread.cpu.gpr[r] = v;
        }
        let next = self.kernel.handle(
            &mut self.thread,
            &self.mem,
            ExitReason::Syscall {
                rip: GuestAddr(DATA + 0x3000),
            },
        );
        assert_eq!(next, Next::Resume);
        self.thread.cpu.gpr[reg::RAX]
    }
    fn event(&mut self, value: u32) -> u64 {
        self.ret(290, [value as u64, 0x800, 0, 0, 0, 0])
    }
    fn epoll(&mut self) -> u64 {
        self.ret(291, [0; 6])
    }
    fn add(&mut self, e: u64, fd: u64, mask: u32, data: u64) -> u64 {
        let mut bytes = mask.to_le_bytes().to_vec();
        bytes.extend_from_slice(&data.to_le_bytes());
        self.mem.write(GuestAddr(DATA), &bytes).unwrap();
        self.ret(233, [e, 1, fd, DATA, 0, 0])
    }
    fn put(&mut self, fd: u64, value: u64) -> u64 {
        self.mem.write_u64(GuestAddr(DATA + 32), value).unwrap();
        self.ret(1, [fd, DATA + 32, 8, 0, 0, 0])
    }
    fn poll(&mut self, e: u64, timeout: i32) -> u64 {
        self.ret(232, [e, DATA + 64, 4, timeout as u64, 0, 0])
    }
    fn data(&self) -> u64 {
        self.mem.read_u64(GuestAddr(DATA + 68)).unwrap()
    }
}

#[test]
fn u6_ofd_dup_keeps_interest() {
    let mut f = Fixture::new();
    let fd = f.event(0);
    let dup = f.ret(32, [fd, 0, 0, 0, 0, 0]);
    let e = f.epoll();
    assert_eq!(f.add(e, fd, 1, 11), 0);
    f.ret(3, [fd, 0, 0, 0, 0, 0]);
    f.put(dup, 1);
    assert_eq!(f.poll(e, 0), 1);
    assert_eq!(f.data(), 11);
}
#[test]
fn u6_ofd_last_close_removes_interest() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let e = f.epoll();
    f.add(e, fd, 1, 11);
    f.ret(3, [fd, 0, 0, 0, 0, 0]);
    assert_eq!(f.poll(e, 0), 0);
}
#[test]
fn u6_ofd_reuse_is_new_description() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let e = f.epoll();
    f.add(e, fd, 1, 11);
    f.ret(3, [fd, 0, 0, 0, 0, 0]);
    let other = f.event(1);
    assert_eq!(other, fd);
    assert_eq!(f.poll(e, 0), 0);
    assert_eq!(f.add(e, other, 1, 22), 0);
    assert_eq!(f.poll(e, 0), 1);
    assert_eq!(f.data(), 22);
}
#[test]
fn u6_ofd_duplicates_register_separately() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let dup = f.ret(32, [fd, 0, 0, 0, 0, 0]);
    let e = f.epoll();
    f.add(e, fd, 1, 11);
    f.add(e, dup, 1, 22);
    assert_eq!(f.poll(e, 0), 2);
}
#[test]
fn u6_ofd_status_flags_are_shared() {
    let mut f = Fixture::new();
    let fd = f.event(0);
    let dup = f.ret(32, [fd, 0, 0, 0, 0, 0]);
    f.ret(72, [dup, 4, 0, 0, 0, 0]);
    assert_eq!(f.ret(72, [fd, 3, 0, 0, 0, 0]), 2);
}
#[test]
fn u6_ofd_cloexec_is_per_descriptor() {
    let mut f = Fixture::new();
    let fd = f.ret(290, [0, 0x80800, 0, 0, 0, 0]);
    let dup = f.ret(32, [fd, 0, 0, 0, 0, 0]);
    assert_eq!(f.ret(72, [fd, 1, 0, 0, 0, 0]), 1);
    assert_eq!(f.ret(72, [dup, 1, 0, 0, 0, 0]), 0);
}
#[test]
fn u6_ofd_clone_shared_table() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let child = f.kernel.files.for_clone(true, false);
    assert!(Arc::ptr_eq(
        &f.kernel.files.descriptor(fd).unwrap().file,
        &child.descriptor(fd).unwrap().file
    ));
    f.ret(3, [fd, 0, 0, 0, 0, 0]);
    assert!(child.descriptor(fd).is_err());
}
#[test]
fn u6_ofd_clone_copied_table_keeps_description() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let child = f.kernel.files.for_clone(false, false);
    f.ret(3, [fd, 0, 0, 0, 0, 0]);
    let mut bytes = [0; 8];
    assert_eq!(child.descriptor(fd).unwrap().file.read(&mut bytes), Ok(8));
    assert_eq!(u64::from_le_bytes(bytes), 1);
}

#[test]
fn u6_integration_nested_epoll() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    let child = f.epoll();
    let parent = f.epoll();
    f.add(child, fd, 1, 11);
    f.add(parent, child, 1, 32);
    assert_eq!(f.poll(parent, 0), 1);
    assert_eq!(f.data(), 32);
}
#[test]
fn u6_integration_guest_pointer_errors() {
    let mut f = Fixture::new();
    let fd = f.event(1);
    assert_eq!(
        f.ret(0, [fd, 1, 8, 0, 0, 0]),
        Errno::EFAULT.to_syscall_return()
    );
    assert_eq!(
        f.ret(1, [fd, 1, 8, 0, 0, 0]),
        Errno::EFAULT.to_syscall_return()
    );
    assert_eq!(
        f.ret(53, [1, 1, 0, 1, 0, 0]),
        Errno::EFAULT.to_syscall_return()
    );
}
#[test]
fn u6_integration_epoll_timeout() {
    let mut f = Fixture::new();
    let e = f.epoll();
    assert_eq!(f.poll(e, 20), 0);
    assert_eq!(f.host.now.load(Ordering::SeqCst), 20_000_000);
}
#[test]
fn u6_integration_timer_metadata_before_wait() {
    let mut f = Fixture::new();
    let inbox = Arc::new(SignalInbox::default());
    f.kernel = f.kernel.with_signal_inbox(Arc::clone(&inbox));
    let e = f.epoll();
    inbox.timer_changed();
    assert_eq!(f.poll(e, 20), 0);
    assert_eq!(f.host.now.load(Ordering::SeqCst), 20_000_000);
}
#[test]
fn u6_integration_metadata_during_wait() {
    let mut f = Fixture::new();
    let inbox = Arc::new(SignalInbox::default());
    f.kernel = f.kernel.with_signal_inbox(Arc::clone(&inbox));
    let e = f.epoll();
    *f.host.action.lock().unwrap() = Some(Box::new(move || inbox.timer_changed()));
    assert_eq!(f.poll(e, 20), 0);
    assert_eq!(f.host.now.load(Ordering::SeqCst), 20_000_000);
}
#[test]
fn u6_integration_ready_before_host_registration() {
    let mut f = Fixture::new();
    let fd = f.event(0);
    let e = f.epoll();
    f.add(e, fd, 1, 12);
    let file = f.kernel.files.descriptor(fd).unwrap().file;
    *f.host.action.lock().unwrap() = Some(Box::new(move || {
        file.write(&1u64.to_le_bytes()).unwrap();
    }));
    assert_eq!(f.poll(e, 20), 1);
    assert_eq!(f.host.now.load(Ordering::SeqCst), 0);
    assert_eq!(f.data(), 12);
}
#[test]
fn u6_integration_timer_signal_interrupts_wait() {
    let mut f = Fixture::new();
    let e = f.epoll();
    f.thread.cpu.gpr[reg::RSP] = DATA + 0x4000;
    f.thread.state.signal_actions.insert(
        14,
        SignalAction {
            handler: DATA + 0x1000,
            flags: 0x4000000,
            restorer: DATA + 0x1010,
            mask: 0,
        },
    );
    f.kernel.group.set_timer(signals::RealTimer {
        deadline: Some(5_000_000),
        interval: 0,
    });
    assert_eq!(f.poll(e, 20), Errno(4).to_syscall_return());
    assert_eq!(f.host.now.load(Ordering::SeqCst), 5_000_000);
}
#[test]
fn u6_integration_policy_and_socket_transfer() {
    let mut f = Fixture::new();
    for domain in [2, 10] {
        assert_eq!(
            f.ret(41, [domain, 1, 0, 0, 0, 0]),
            Errno(97).to_syscall_return()
        );
    }
    assert_eq!(f.ret(53, [1, 0x80801, 0, DATA, 0, 0]), 0);
    let mut bytes = [0; 8];
    f.mem.read(GuestAddr(DATA), &mut bytes).unwrap();
    let a = u32::from_le_bytes(bytes[..4].try_into().unwrap()) as u64;
    let b = u32::from_le_bytes(bytes[4..].try_into().unwrap()) as u64;
    f.mem.write(GuestAddr(DATA + 32), b"hi").unwrap();
    assert_eq!(f.ret(44, [a, DATA + 32, 2, 0x4000, 0, 0]), 2);
    assert_eq!(f.ret(45, [b, DATA + 64, 2, 0, 0, 0]), 2);
    let mut received = [0; 2];
    f.mem.read(GuestAddr(DATA + 64), &mut received).unwrap();
    assert_eq!(&received, b"hi");
}
