//! Internal scalar/handle ABI used by the Worker launcher.
//!
//! Guest data is copied through bounded buffers; it is never dereferenced as a
//! host pointer. JS stack/TLS regions are trusted launcher resources and must
//! stay owned until their Worker is terminated.
use paludarium_host::WasmHost;
use paludarium_runtime::{Config, Session};
use paludarium_types::{Error, ErrorKind, ExitStatus};
use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};
use std::sync::{
    Arc, Mutex, OnceLock, PoisonError,
    atomic::{AtomicU32, Ordering},
};

type Table<T> = OnceLock<Mutex<BTreeMap<u32, T>>>;
static NEXT: AtomicU32 = AtomicU32::new(1);
static BUFFERS: Table<Vec<u8>> = OnceLock::new();
static CONFIGS: Table<Config> = OnceLock::new();
static RUNS: Table<Arc<Run>> = OnceLock::new();
static REGIONS: Table<Box<[u128]>> = OnceLock::new();
struct Run {
    session: Option<Arc<Session>>,
    host: Arc<WasmHost>,
    error: Mutex<Option<Error>>,
}
fn table<T>(t: &Table<T>) -> &Mutex<BTreeMap<u32, T>> {
    t.get_or_init(Default::default)
}
fn insert<T>(t: &Table<T>, value: T) -> u32 {
    let Ok(id) = NEXT.try_update(Ordering::SeqCst, Ordering::SeqCst, |v| v.checked_add(1)) else {
        return 0;
    };
    table(t)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .insert(id, value);
    id
}
fn bytes(id: u32) -> Option<Vec<u8>> {
    table(&BUFFERS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .cloned()
}
fn run(id: u32) -> Option<Arc<Run>> {
    table(&RUNS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .cloned()
}

// SAFETY: exported entrypoints take scalars and validated handles only. They
// neither dereference caller-provided pointers nor export guest syscall numbers.
#[unsafe(no_mangle)]
pub extern "C" fn buffer_new(len: u32) -> u32 {
    if len > 64 * 1024 * 1024 {
        return 0;
    }
    insert(&BUFFERS, vec![0; len as usize])
}
#[unsafe(no_mangle)]
pub extern "C" fn buffer_set(id: u32, index: u32, value: u32) -> i32 {
    let mut b = table(&BUFFERS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner);
    if value > 255 {
        return -1;
    }
    if let Some(v) = b.get_mut(&id).and_then(|b| b.get_mut(index as usize)) {
        *v = value as u8;
        0
    } else {
        -1
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn buffer_len(id: u32) -> i32 {
    table(&BUFFERS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .map_or(-1, |b| b.len() as i32)
}
#[unsafe(no_mangle)]
pub extern "C" fn buffer_get(id: u32, index: u32) -> i32 {
    table(&BUFFERS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .and_then(|b| b.get(index as usize))
        .map_or(-1, |b| i32::from(*b))
}
#[unsafe(no_mangle)]
pub extern "C" fn buffer_drop(id: u32) {
    table(&BUFFERS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .remove(&id);
}
#[unsafe(no_mangle)]
pub extern "C" fn config_new(program: u32) -> u32 {
    let Some(program) = bytes(program) else {
        return 0;
    };
    insert(&CONFIGS, Config::new(program, Vec::new()))
}
#[unsafe(no_mangle)]
pub extern "C" fn config_arg(id: u32, arg: u32) -> i32 {
    let Some(arg) = bytes(arg) else { return -1 };
    let mut t = table(&CONFIGS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner);
    let Some(c) = t.get_mut(&id) else { return -1 };
    c.args.push(arg);
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn config_env(id: u32, key: u32, value: u32) -> i32 {
    let (Some(key), Some(value)) = (bytes(key), bytes(value)) else {
        return -1;
    };
    let mut t = table(&CONFIGS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner);
    let Some(c) = t.get_mut(&id) else { return -1 };
    c.env.push((key, value));
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn config_file(id: u32, path: u32, content: u32) -> i32 {
    let (Some(path), Some(content)) = (bytes(path), bytes(content)) else {
        return -1;
    };
    let mut t = table(&CONFIGS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner);
    let Some(c) = t.get_mut(&id) else { return -1 };
    c.files.push((path, content));
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn config_drop(id: u32) {
    table(&CONFIGS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .remove(&id);
}
#[unsafe(no_mangle)]
pub extern "C" fn session_from_config(id: u32, stdin: u32) -> u32 {
    let Some(config) = table(&CONFIGS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .cloned()
    else {
        return 0;
    };
    let host = Arc::new(WasmHost::streaming(bytes(stdin).unwrap_or_default()));
    let (session, error) = match Session::new(config, host.clone()) {
        Ok(s) => (Some(Arc::new(s)), None),
        Err(e) => (None, Some(e)),
    };
    insert(
        &RUNS,
        Arc::new(Run {
            session,
            host,
            error: Mutex::new(error),
        }),
    )
}
#[unsafe(no_mangle)]
pub extern "C" fn session_run(id: u32) -> i32 {
    let Some(r) = run(id) else { return -1 };
    let Some(s) = &r.session else { return -2 };
    match s.run() {
        Ok(ExitStatus::Exited(code)) => code,
        Ok(ExitStatus::Signaled(signal)) => 256 + signal,
        Err(e) => {
            *r.error.lock().unwrap_or_else(PoisonError::into_inner) = Some(e);
            -2
        }
        Ok(_) => {
            *r.error.lock().unwrap_or_else(PoisonError::into_inner) =
                Some(Error::new(ErrorKind::Internal, "unknown guest status"));
            -2
        }
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn session_kill(id: u32) -> i32 {
    let Some(r) = run(id) else { return -1 };
    r.host.close_stdin();
    if let Some(s) = &r.session {
        s.kill();
    }
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn session_stdin_write(id: u32, buffer: u32) -> i32 {
    let (Some(r), Some(b)) = (run(id), bytes(buffer)) else {
        return -1;
    };
    r.host.append_stdin(&b).map_or(-1, |()| 0)
}
#[unsafe(no_mangle)]
pub extern "C" fn session_stdin_close(id: u32) -> i32 {
    let Some(r) = run(id) else { return -1 };
    r.host.close_stdin();
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn session_output(id: u32, stream: u32) -> u32 {
    let Some(r) = run(id) else { return 0 };
    let data = match stream {
        1 => r.host.stdout(),
        2 => r.host.stderr(),
        _ => return 0,
    };
    insert(&BUFFERS, data)
}
#[unsafe(no_mangle)]
pub extern "C" fn session_error_kind(id: u32) -> i32 {
    let Some(r) = run(id) else { return -1 };
    r.error
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .as_ref()
        .map_or(0, |e| match e.kind {
            ErrorKind::Unimplemented => 1,
            ErrorKind::Internal => 2,
            ErrorKind::InvalidProgram => 3,
            ErrorKind::Host => 4,
            _ => 2,
        })
}
#[unsafe(no_mangle)]
pub extern "C" fn session_error_message(id: u32) -> u32 {
    let Some(r) = run(id) else { return 0 };
    let message = r
        .error
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .as_ref()
        .map_or_else(String::new, ToString::to_string);
    insert(&BUFFERS, message.into_bytes())
}
#[unsafe(no_mangle)]
pub extern "C" fn session_drop(id: u32) {
    table(&RUNS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .remove(&id);
}

#[unsafe(no_mangle)]
pub extern "C" fn region_new(len: u32) -> u32 {
    if !(4096..=16 * 1024 * 1024).contains(&len) {
        return 0;
    }
    insert(
        &REGIONS,
        vec![0u128; (len as usize).div_ceil(16)].into_boxed_slice(),
    )
}
#[unsafe(no_mangle)]
pub extern "C" fn region_pointer(id: u32) -> u32 {
    table(&REGIONS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .map_or(0, |b| b.as_ptr() as usize as u32)
}
#[unsafe(no_mangle)]
pub extern "C" fn region_drop(id: u32) {
    table(&REGIONS)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .remove(&id);
}
#[unsafe(no_mangle)]
pub extern "C" fn thread_token() -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    std::thread::current().id().hash(&mut h);
    h.finish()
}

struct SharedSpace {
    memory: paludarium_mmu::AddressSpace,
    wake: AtomicU32,
}
static SPACES: Table<Arc<SharedSpace>> = OnceLock::new();
fn space(id: u32) -> Option<Arc<SharedSpace>> {
    table(&SPACES)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .get(&id)
        .cloned()
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_space_new() -> u32 {
    let memory = paludarium_mmu::AddressSpace::new();
    if memory
        .map_shared(
            Some(paludarium_types::GuestAddr(0x1000)),
            4096,
            paludarium_mmu::Prot::READ_WRITE,
            paludarium_mmu::MappingKind::Anonymous,
        )
        .is_err()
    {
        return 0;
    }
    insert(
        &SPACES,
        Arc::new(SharedSpace {
            memory,
            wake: AtomicU32::new(0),
        }),
    )
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_space_add(id: u32, iterations: u32) -> i32 {
    let Some(s) = space(id) else { return -1 };
    if iterations > 1_000_000 {
        return -1;
    }
    for _ in 0..iterations {
        if s.memory
            .atomic(
                paludarium_types::GuestAddr(0x1000),
                paludarium_mmu::AtomicWidth::W64,
                paludarium_mmu::AtomicOp::Add(1),
            )
            .is_err()
        {
            return -1;
        }
    }
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_space_value(id: u32) -> i64 {
    space(id)
        .and_then(|s| s.memory.read_u64(paludarium_types::GuestAddr(0x1000)).ok())
        .map_or(-1, |v| v as i64)
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_space_drop(id: u32) {
    table(&SPACES)
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .remove(&id);
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_wait_word(id: u32, value: u32) -> i32 {
    let Some(s) = space(id) else { return -1 };
    s.wake.store(value, Ordering::SeqCst);
    0
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_wait(id: u32, expected: u32, timeout_ms: u32) -> i32 {
    let Some(s) = space(id) else { return -1 };
    if timeout_ms > 30_000 {
        return -1;
    }
    // SAFETY: retained Arc owns an aligned AtomicU32 for the whole bounded wait;
    // no Rust lock is held. Only atomics access this memory, in Workers.
    unsafe {
        core::arch::wasm32::memory_atomic_wait32(
            s.wake.as_ptr().cast(),
            expected as i32,
            i64::from(timeout_ms) * 1_000_000,
        )
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn shared_notify(id: u32, count: u32) -> i32 {
    let Some(s) = space(id) else { return -1 };
    // SAFETY: Arc pins the aligned AtomicU32; notify cannot outlive this call.
    unsafe { core::arch::wasm32::memory_atomic_notify(s.wake.as_ptr().cast(), count) as i32 }
}
