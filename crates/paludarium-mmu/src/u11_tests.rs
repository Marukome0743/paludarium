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

fn shared_space() -> AddressSpace {
    let m = AddressSpace::new();
    m.map_shared(
        Some(DATA),
        PAGE_SIZE * 2,
        Prot::READ_WRITE.union(Prot::EXEC),
        MappingKind::Anonymous,
    )
    .unwrap();
    m.write(DATA, &[0; 16]).unwrap();
    m
}
#[test]
fn u11_public_reads_share_outer_guards() {
    let m = shared_space();
    std::thread::scope(|scope| {
        let guard = m.read_locked();
        let (tx, rx) = std::sync::mpsc::channel();
        let memory = &m;
        let worker = scope.spawn(move || tx.send(memory.read_u64(DATA)).unwrap());
        let outcome = rx.recv_timeout(std::time::Duration::from_secs(1));
        drop(guard);
        worker.join().unwrap();
        assert_eq!(outcome.unwrap(), Ok(0));
    });
}
#[test]
fn u11_fork_shared_write_excludes_parent_read_guard() {
    let m = shared_space();
    m.mark_shared(DATA, PAGE_SIZE * 2).unwrap();
    let child = m.fork();
    std::thread::scope(|scope| {
        let guard = m.read_locked();
        let (started, ready) = std::sync::mpsc::channel();
        let (done, completion) = std::sync::mpsc::channel();
        let worker = scope.spawn(move || {
            started.send(()).unwrap();
            done.send(child.write_u64(DATA, 7)).unwrap();
        });
        ready
            .recv_timeout(std::time::Duration::from_secs(1))
            .unwrap();
        let blocked = completion.recv_timeout(std::time::Duration::from_millis(20));
        drop(guard);
        assert!(matches!(
            blocked,
            Err(std::sync::mpsc::RecvTimeoutError::Timeout)
        ));
        assert_eq!(
            completion
                .recv_timeout(std::time::Duration::from_secs(1))
                .unwrap(),
            Ok(())
        );
        worker.join().unwrap();
    });
    assert_eq!(m.read_u64(DATA), Ok(7));
}
#[test]
fn u11_shared_atomic_updates_cannot_tear_normal_reads() {
    let m = shared_space();
    m.mark_shared(DATA, PAGE_SIZE * 2).unwrap();
    let child = m.fork();
    let a = u128::from_le_bytes([7; 16]);
    let b = u128::from_le_bytes([9; 16]);
    std::thread::scope(|scope| {
        scope.spawn(|| {
            for _ in 0..1000 {
                child
                    .atomic(DATA, AtomicWidth::W128, AtomicOp::Exchange(a))
                    .unwrap();
                child
                    .atomic(DATA, AtomicWidth::W128, AtomicOp::Exchange(b))
                    .unwrap();
            }
        });
        for _ in 0..1000 {
            let mut bytes = [0; 16];
            m.read(DATA, &mut bytes).unwrap();
            assert!(bytes == [0; 16] || bytes == [7; 16] || bytes == [9; 16]);
        }
    });
}
#[test]
fn u11_mapping_race_returns_bytes_or_precise_fault() {
    let m = shared_space();
    std::thread::scope(|scope| {
        scope.spawn(|| {
            for _ in 0..100 {
                m.unmap_shared(DATA, PAGE_SIZE).unwrap();
                m.map_shared(
                    Some(DATA),
                    PAGE_SIZE,
                    Prot::READ_WRITE,
                    MappingKind::Anonymous,
                )
                .unwrap();
            }
        });
        for _ in 0..1000 {
            let mut byte = [9];
            match m.read(DATA, &mut byte) {
                Ok(()) => assert_eq!(byte, [0]),
                Err(fault) => {
                    assert_eq!(fault.addr, DATA);
                    assert!(!fault.mapped && !fault.present);
                    assert_eq!(byte, [9]);
                }
            }
        }
    });
}
#[test]
fn u11_private_fork_snapshot_excludes_concurrent_writes() {
    let m = shared_space();
    let a = u64::from_le_bytes([7; 8]);
    let b = u64::from_le_bytes([9; 8]);
    std::thread::scope(|scope| {
        scope.spawn(|| {
            for _ in 0..1000 {
                m.write_u64(DATA, a).unwrap();
                m.write_u64(DATA, b).unwrap();
            }
        });
        for _ in 0..100 {
            let child = m.fork();
            let value = child.read_u64(DATA).unwrap();
            assert!(value == 0 || value == a || value == b);
        }
    });
}
#[test]
fn u11_fork_concurrent_lazy_shared_read_keeps_atomic_backing() {
    let m = shared_space();
    m.mark_shared(DATA, PAGE_SIZE * 2).unwrap();
    let child = m.fork();
    let lazy = GuestAddr(DATA.0 + PAGE_SIZE);
    std::thread::scope(|scope| {
        for space in [&m, &child] {
            scope.spawn(move || {
                for _ in 0..1000 {
                    let _ = space.read_u64(lazy).unwrap();
                    space
                        .atomic(lazy, AtomicWidth::W64, AtomicOp::Add(1))
                        .unwrap();
                }
            });
        }
    });
    assert_eq!(m.read_u64(lazy), Ok(2000));
    assert_eq!(child.read_u64(lazy), Ok(2000));
}
#[test]
fn u11_readonly_metadata_and_fetch_share_guards() {
    let m = shared_space();
    std::thread::scope(|scope| {
        let guard = m.read_locked();
        let (tx, rx) = std::sync::mpsc::channel();
        let memory = &m;
        let worker = scope.spawn(move || {
            assert_ne!(memory.id(), 0);
            let _ = memory.code_generation();
            assert_eq!(memory.mappings().count(), 1);
            assert_eq!(memory.check_read(DATA, 1), Ok(()));
            assert_eq!(memory.check_write(DATA, 1), Ok(()));
            assert_eq!(memory.fetch(DATA, &mut [9]), Ok(()));
            assert_eq!(memory.fetch_partial(DATA, &mut [9]), Ok(1));
            tx.send(()).unwrap();
        });
        let outcome = rx.recv_timeout(std::time::Duration::from_secs(1));
        drop(guard);
        worker.join().unwrap();
        outcome.unwrap();
    });
}
