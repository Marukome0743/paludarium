use super::*;
use paludarium_mmu::{MappingKind, Prot};

fn hint_attempt(
    state: &mut CpuState,
    memory: &AddressSpace,
    cache: &mut DecodeCache,
    deterministic: bool,
    enabled: bool,
) -> usize {
    state.rip = GuestAddr(4096);
    let mut calls = 0;
    run_cached_with_counted_hook(
        state,
        memory,
        64,
        cache,
        AccelerationPolicy {
            maximum_block: 64,
            cache_rejections: enabled,
        },
        |_, _, rejected| {
            calls += 1;
            *rejected = deterministic;
            None
        },
    );
    calls
}

#[test]
fn u14_counted_negative_hint_skips_only_same_epoch_boundary() {
    let (mut state, memory) = machine();
    let mut cache = DecodeCache::new();
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 1);
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 0);
    memory.write_initial(GuestAddr(4096), &[0x90]).unwrap();
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 1);
}
#[test]
fn u14_counted_transient_rejection_remains_retryable() {
    let (mut state, memory) = machine();
    let mut cache = DecodeCache::new();
    assert_eq!(
        hint_attempt(&mut state, &memory, &mut cache, false, true),
        1
    );
    assert_eq!(
        hint_attempt(&mut state, &memory, &mut cache, false, true),
        1
    );
}
#[test]
fn u14_counted_default_opt_out_does_not_cache_rejections() {
    let (mut state, memory) = machine();
    let mut cache = DecodeCache::new();
    assert_eq!(
        hint_attempt(&mut state, &memory, &mut cache, true, false),
        1
    );
    assert_eq!(
        hint_attempt(&mut state, &memory, &mut cache, true, false),
        1
    );
}
#[test]
fn u14_counted_negative_hint_protect_change_invalidates() {
    let (mut state, mut memory) = machine();
    let mut cache = DecodeCache::new();
    hint_attempt(&mut state, &memory, &mut cache, true, true);
    memory
        .protect(GuestAddr(4096), 4096, Prot::from_bits(7).unwrap())
        .unwrap();
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 1);
}
#[test]
fn u14_counted_negative_hint_unmap_preserves_fetch_fault() {
    let (mut state, mut memory) = machine();
    let mut cache = DecodeCache::new();
    hint_attempt(&mut state, &memory, &mut cache, true, true);
    memory.unmap(GuestAddr(4096), 4096).unwrap();
    state.rip = GuestAddr(4096);
    assert!(matches!(
        run_cached_with_counted_hook(&mut state, &memory, 64, &mut cache, 64, |_, _, _| panic!(
            "unmapped"
        )),
        ExitReason::PageFault { .. }
    ));
}
#[test]
fn u14_counted_negative_hint_remap_invalidates() {
    let (mut state, mut memory) = machine();
    let mut cache = DecodeCache::new();
    hint_attempt(&mut state, &memory, &mut cache, true, true);
    memory.unmap(GuestAddr(4096), 4096).unwrap();
    memory
        .map(
            Some(GuestAddr(4096)),
            4096,
            Prot::READ_EXEC,
            MappingKind::ElfSegment,
        )
        .unwrap();
    memory.write_initial(GuestAddr(4096), &[0x90; 128]).unwrap();
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 1);
}
#[test]
fn u14_counted_negative_hint_other_worker_write_invalidates() {
    let (mut state, memory) = machine();
    let memory = std::sync::Arc::new(memory);
    let mut cache = DecodeCache::new();
    hint_attempt(&mut state, &memory, &mut cache, true, true);
    let other = memory.clone();
    std::thread::spawn(move || other.write_initial(GuestAddr(4096), &[0x90]).unwrap())
        .join()
        .unwrap();
    assert_eq!(hint_attempt(&mut state, &memory, &mut cache, true, true), 1);
}

fn machine() -> (CpuState, AddressSpace) {
    let mut memory = AddressSpace::new();
    memory
        .map(
            Some(GuestAddr(4096)),
            4096,
            Prot::READ_EXEC,
            MappingKind::ElfSegment,
        )
        .unwrap();
    memory.write_initial(GuestAddr(4096), &[0x90; 128]).unwrap();
    (CpuState::new(GuestAddr(4096), GuestAddr(8192)), memory)
}

#[test]
fn u14_counted_hook_charges_actual_instructions() {
    let (mut state, memory) = machine();
    let mut calls = 0;
    let result = run_cached_with_counted_hook(
        &mut state,
        &memory,
        65,
        &mut DecodeCache::new(),
        64,
        |state, _, _| {
            calls += 1;
            state.rip.0 += 2;
            Some((ExitReason::BudgetExhausted { rip: state.rip }, 2))
        },
    );
    assert_eq!(calls, 1);
    assert_eq!(state.rip, GuestAddr(4161));
    assert_eq!(result, ExitReason::BudgetExhausted { rip: state.rip });
}
#[test]
fn u14_counted_hook_small_budget_never_calls_hook() {
    let (mut state, memory) = machine();
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        63,
        &mut DecodeCache::new(),
        64,
        |_, _, _| panic!("small budget"),
    );
    assert_eq!(state.rip, GuestAddr(4159));
}
#[test]
fn u14_counted_hook_zero_budget_preserves_state() {
    let (mut state, memory) = machine();
    let before = state.clone();
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        0,
        &mut DecodeCache::new(),
        64,
        |_, _, _| panic!("zero budget"),
    );
    assert_eq!(state, before);
}
#[test]
fn u14_counted_hook_rejection_executes_decoded_instruction() {
    let (mut state, memory) = machine();
    let mut calls = 0;
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        64,
        &mut DecodeCache::new(),
        64,
        |_, instruction, _| {
            calls += 1;
            assert_eq!(instruction.mnemonic, paludarium_decoder::Mnemonic::Nop);
            None
        },
    );
    assert_eq!(calls, 1);
    assert_eq!(state.rip, GuestAddr(4160));
}
#[test]
fn u14_counted_hook_fetch_fault_does_not_call_hook() {
    let (mut state, _) = machine();
    assert!(matches!(
        run_cached_with_counted_hook(
            &mut state,
            &AddressSpace::new(),
            64,
            &mut DecodeCache::new(),
            64,
            |_, _, _| panic!("fault")
        ),
        ExitReason::PageFault { .. }
    ));
}

#[test]
fn u14_counted_hook_exact_maximum_exhausts_remaining_budget() {
    let (mut state, memory) = machine();
    let mut calls = 0;
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        64,
        &mut DecodeCache::new(),
        64,
        |state, _, _| {
            calls += 1;
            state.rip.0 += 64;
            Some((ExitReason::BudgetExhausted { rip: state.rip }, 64))
        },
    );
    assert_eq!(calls, 1);
    assert_eq!(state.rip, GuestAddr(4160));
}

#[test]
fn u14_counted_hook_syscall_after_short_block_returns_immediately() {
    let (mut state, memory) = machine();
    memory.write_initial(GuestAddr(4098), &[0x0f, 5]).unwrap();
    let reason = run_cached_with_counted_hook(
        &mut state,
        &memory,
        65,
        &mut DecodeCache::new(),
        64,
        |state, _, _| {
            state.rip.0 += 2;
            Some((ExitReason::BudgetExhausted { rip: state.rip }, 2))
        },
    );
    assert!(matches!(reason, ExitReason::Syscall { .. }));
    assert_eq!(state.rip, GuestAddr(4100));
}

#[test]
fn u14_counted_hook_fault_after_short_block_is_preserved() {
    let (mut state, memory) = machine();
    let reason = run_cached_with_counted_hook(
        &mut state,
        &memory,
        65,
        &mut DecodeCache::new(),
        64,
        |state, _, _| {
            state.rip = GuestAddr(8192);
            Some((ExitReason::BudgetExhausted { rip: state.rip }, 2))
        },
    );
    assert!(matches!(
        reason,
        ExitReason::PageFault {
            rip: GuestAddr(8192),
            fetch: true,
            ..
        }
    ));
}
#[test]
#[should_panic(expected = "invalid accelerator instruction count")]
fn u14_counted_hook_rejects_zero_count() {
    let (mut state, memory) = machine();
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        64,
        &mut DecodeCache::new(),
        64,
        |state, _, _| Some((ExitReason::BudgetExhausted { rip: state.rip }, 0)),
    );
}
#[test]
#[should_panic(expected = "invalid accelerator instruction count")]
fn u14_counted_hook_rejects_excessive_count() {
    let (mut state, memory) = machine();
    run_cached_with_counted_hook(
        &mut state,
        &memory,
        64,
        &mut DecodeCache::new(),
        64,
        |state, _, _| Some((ExitReason::BudgetExhausted { rip: state.rip }, 65)),
    );
}
