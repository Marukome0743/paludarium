use super::*;
use paludarium_mmu::{MappingKind, Prot};
use paludarium_types::{Errno, GuestAddr};
use std::sync::atomic::Ordering;
const DATA: u64 = 0x600000;
fn memory() -> AddressSpace {
    let mem = AddressSpace::new();
    mem.map_shared(
        Some(GuestAddr(DATA)),
        4096,
        Prot::READ_WRITE,
        MappingKind::Anonymous,
    )
    .unwrap();
    mem
}
fn kernel() -> Kernel {
    Kernel::new(Arc::new(paludarium_host::NativeHost))
}
fn thread() -> Thread {
    Thread {
        tid: 1,
        state: ThreadState {
            pid: 1,
            ..ThreadState::default()
        },
        cpu: CpuState::default(),
    }
}
fn clone(k: &mut Kernel, t: &mut Thread, m: &AddressSpace, flags: u64) -> u64 {
    k.thread_syscall(t, m, 56, [flags, DATA + 4096, DATA, DATA + 4, DATA + 8, 0]);
    t.cpu.gpr[reg::RAX]
}
#[test]
fn clone_registers_and_tls() {
    let mut k = kernel();
    let mut t = thread();
    t.cpu.rip = GuestAddr(0x400123);
    let m = memory();
    let tid = clone(&mut k, &mut t, &m, 0x1390900);
    assert_eq!(tid, 2);
    let (_c, ct) = k.take_child().unwrap();
    assert_eq!(ct.cpu.gpr[reg::RAX], 0);
    assert_eq!(ct.cpu.gpr[reg::RSP], DATA + 4096);
    assert_eq!(ct.cpu.fs_base, DATA + 8);
    assert_eq!(ct.cpu.rip, t.cpu.rip);
    assert_eq!(ct.state.clear_child_tid, DATA + 4);
}
#[test]
fn clone_parent_child_tid() {
    let mut k = kernel();
    let mut t = thread();
    let m = memory();
    let tid = clone(&mut k, &mut t, &m, 0x1310900);
    let mut b = [0; 8];
    m.read(GuestAddr(DATA), &mut b).unwrap();
    assert_eq!(u32::from_le_bytes(b[..4].try_into().unwrap()) as u64, tid);
    assert_eq!(u32::from_le_bytes(b[4..].try_into().unwrap()) as u64, tid);
}
#[test]
fn clone_invalid_dependencies() {
    assert_eq!(
        clone(&mut kernel(), &mut thread(), &memory(), 0x10100),
        Errno::EINVAL.to_syscall_return()
    );
}
#[test]
fn clone_process_is_u8() {
    assert_eq!(
        clone(&mut kernel(), &mut thread(), &memory(), 0),
        Errno::ENOSYS.to_syscall_return()
    );
}
#[test]
fn clone_unknown_flags() {
    assert_eq!(
        clone(
            &mut kernel(),
            &mut thread(),
            &memory(),
            0x10900 | 0x20000000
        ),
        Errno::EINVAL.to_syscall_return()
    );
}
#[test]
fn clear_child_tid_on_finish() {
    let mut k = kernel();
    let mut t = thread();
    let m = memory();
    clone(&mut k, &mut t, &m, 0x1310900);
    let (mut child, ct) = k.take_child().unwrap();
    child.finish_thread(&ct, &m);
    let mut b = [0; 4];
    m.read(GuestAddr(DATA + 4), &mut b).unwrap();
    assert_eq!(b, [0; 4]);
    assert_eq!(k.group.active_threads(), 1);
}
#[test]
fn individual_exit_does_not_stop_group() {
    let mut k = kernel();
    let mut t = thread();
    assert_eq!(
        k.thread_syscall(&mut t, &memory(), 60, [7, 0, 0, 0, 0, 0]),
        Some(Next::Exit(ExitStatus::Exited(7)))
    );
    assert_eq!(k.group.status(), None);
}
#[test]
fn exit_group_stops_all() {
    let mut k = kernel();
    let mut t = thread();
    k.thread_syscall(&mut t, &memory(), 231, [17, 0, 0, 0, 0, 0]);
    assert_eq!(k.group.status(), Some(ExitStatus::Exited(17)));
}
#[test]
fn futex_mismatch() {
    assert!(matches!(
        futex::Futexes::default().register(&memory(), DATA, false, 1, 1),
        Err(Errno::EAGAIN)
    ));
}
#[test]
fn futex_fault() {
    assert!(matches!(
        futex::Futexes::default().register(&memory(), 0, false, 0, 1),
        Err(Errno::EFAULT)
    ));
}
#[test]
fn futex_alignment() {
    assert!(matches!(
        futex::Futexes::default().register(&memory(), DATA + 1, false, 0, 1),
        Err(Errno::EINVAL)
    ));
}
#[test]
fn futex_empty_mask() {
    assert!(matches!(
        futex::Futexes::default().register(&memory(), DATA, false, 0, 0),
        Err(Errno::EINVAL)
    ));
}
#[test]
fn futex_bitset_selects_waiter() {
    let m = memory();
    let f = futex::Futexes::default();
    let a = f.register(&m, DATA, true, 0, 1).unwrap();
    let b = f.register(&m, DATA, true, 0, 2).unwrap();
    assert_eq!(f.wake(&m, DATA, true, 1, 2), Ok(1));
    assert_eq!(a.state.load(Ordering::SeqCst), 0);
    assert_eq!(b.state.load(Ordering::SeqCst), 1);
    assert_eq!(f.wake(&m, DATA, true, 1, 1), Ok(1));
}
#[test]
fn futex_private_shared_keys() {
    let m = memory();
    let f = futex::Futexes::default();
    let a = f.register(&m, DATA, true, 0, 1).unwrap();
    assert_eq!(f.wake(&m, DATA, false, 1, 1), Ok(0));
    assert_eq!(a.state.load(Ordering::SeqCst), 0);
    assert_eq!(f.wake(&m, DATA, true, 1, 1), Ok(1));
}
#[test]
fn futex_wake_before_host_wait_retained() {
    let m = memory();
    let f = futex::Futexes::default();
    let a = f.register(&m, DATA, true, 0, 1).unwrap();
    f.wake(&m, DATA, true, 1, 1).unwrap();
    assert_eq!(a.token.value(), 1);
    assert_eq!(f.finish(&m, DATA, true, &a, 2), 1);
}
#[test]
fn futex_timeout_wins_once() {
    let m = memory();
    let f = futex::Futexes::default();
    let a = f.register(&m, DATA, true, 0, 1).unwrap();
    assert_eq!(f.finish(&m, DATA, true, &a, 2), 2);
    assert_eq!(f.wake(&m, DATA, true, 1, 1), Ok(0));
    assert_eq!(f.finish(&m, DATA, true, &a, 3), 2);
}
