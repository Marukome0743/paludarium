use super::*;
const DATA: GuestAddr = GuestAddr(0x10000);
fn memory(prot: Prot) -> AddressSpaceData {
    let mut m = AddressSpaceData::new();
    m.map(Some(DATA), PAGE_SIZE * 2, prot, MappingKind::Anonymous)
        .unwrap();
    m
}
#[test]
fn u11_populated_read_works_under_shared_directory_guard() {
    let m = memory(Prot::READ_WRITE);
    m.write(DATA, b"populated").unwrap();
    // Another reader prevents an accidental exclusive read path. The worker
    // reports completion before the guard is released; a safety timeout drops
    // the guard before joining if an implementation regresses.
    std::thread::scope(|scope| {
        let guard = m.read_directory();
        let (done, result) = std::sync::mpsc::channel();
        let memory = &m;
        let task = scope.spawn(move || {
            let mut bytes = [0; 9];
            let outcome = memory.read(DATA, &mut bytes);
            done.send((outcome, bytes)).unwrap();
        });
        let outcome = result.recv_timeout(std::time::Duration::from_secs(1));
        drop(guard);
        task.join().unwrap();
        assert_eq!(outcome.unwrap(), (Ok(()), *b"populated"));
    });
}
#[test]
fn u11_populated_fetch_keeps_execute_permission() {
    let mut m = memory(Prot::READ_WRITE.union(Prot::EXEC));
    m.write(DATA, &[0x90]).unwrap();
    assert_eq!(m.fetch(DATA, &mut [0]), Ok(()));
    m.protect(DATA, PAGE_SIZE, Prot::READ).unwrap();
    let fault = m.fetch(DATA, &mut [0]).unwrap_err();
    assert!(fault.fetch && fault.mapped && fault.present);
}
#[test]
fn u11_lazy_zero_read_populates_logical_page_only() {
    let m = memory(Prot::READ);
    assert!(lookup(&m.read_directory(), DATA.0).is_none());
    let mut bytes = [9; 8];
    m.read(DATA, &mut bytes).unwrap();
    assert_eq!(bytes, [0; 8]);
    let guard = m.read_directory();
    assert!(lookup(&guard, DATA.0).unwrap().frame.get().is_none());
}
#[test]
fn u11_cross_page_read_revalidates_entire_range() {
    let mut m = memory(Prot::READ_WRITE);
    m.write(GuestAddr(DATA.0 + PAGE_SIZE - 2), &[1, 2, 3, 4])
        .unwrap();
    m.unmap(GuestAddr(DATA.0 + PAGE_SIZE), PAGE_SIZE).unwrap();
    let mut bytes = [9; 4];
    let fault = m
        .read(GuestAddr(DATA.0 + PAGE_SIZE - 2), &mut bytes)
        .unwrap_err();
    assert_eq!(fault.addr, GuestAddr(DATA.0 + PAGE_SIZE));
    assert!(!fault.mapped && !fault.present && !fault.write && !fault.fetch);
    assert_eq!(bytes, [9; 4]);
}
#[test]
fn u11_fork_read_preserves_private_bytes() {
    let m = memory(Prot::READ_WRITE);
    m.write(DATA, &[7]).unwrap();
    let child = m.fork();
    child.write(DATA, &[8]).unwrap();
    let mut parent = [0];
    m.read(DATA, &mut parent).unwrap();
    assert_eq!(parent, [7]);
    let mut changed = [0];
    child.read(DATA, &mut changed).unwrap();
    assert_eq!(changed, [8]);
}
#[test]
fn u11_concurrent_populated_reads_and_writes_are_atomic_bytes() {
    let m = memory(Prot::READ_WRITE);
    m.write(DATA, &[0; 64]).unwrap();
    std::thread::scope(|scope| {
        scope.spawn(|| {
            for _ in 0..1000 {
                m.write(DATA, &[7; 64]).unwrap();
                m.write(DATA, &[9; 64]).unwrap();
            }
        });
        for _ in 0..3 {
            scope.spawn(|| {
                for _ in 0..1000 {
                    let mut bytes = [0; 64];
                    m.read(DATA, &mut bytes).unwrap();
                    assert!(bytes.into_iter().all(|b| matches!(b, 0 | 7 | 9)));
                }
            });
        }
    });
}
#[test]
fn u11_concurrent_lazy_reads_install_one_zero_page() {
    let m = memory(Prot::READ);
    std::thread::scope(|scope| {
        for _ in 0..4 {
            scope.spawn(|| {
                let mut bytes = [9; 8];
                m.read(DATA, &mut bytes).unwrap();
                assert_eq!(bytes, [0; 8]);
            });
        }
    });
    let guard = m.read_directory();
    assert!(lookup(&guard, DATA.0).is_some());
    assert!(lookup(&guard, DATA.0).unwrap().frame.get().is_none());
}
