//! x86-64 interpreter for paludarium (contract C5).
//!
//! [`run`] executes instructions on a [`CpuState`] until a system call, a
//! guest exception or the instruction budget stops it, and reports why as an
//! [`ExitReason`] (ADR-004). The CPU knows nothing about the kernel.
//! Instructions outside the implemented set stop with `InvalidOpcode`
//! (BR4.1). The implemented set is the one the U1 guests execute (BR4.4).
#![forbid(unsafe_code)]

mod alu;
mod exec;
mod state;
#[cfg(test)]
mod u2_tests;

use paludarium_decoder::{DecodeError, Instruction, decode};
use paludarium_mmu::AddressSpace;
use paludarium_types::{ExitReason, GuestAddr, InstructionBytes, MAX_INSTRUCTION_LEN};

pub use alu::{condition, sign_extend, size_mask};
pub use state::{CpuState, INITIAL_MXCSR, INITIAL_RFLAGS, RepeatContinuation, flag, reg};

use exec::Stop;

/// Number of entries of a [`DecodeCache`].
const CACHE_ENTRIES: usize = 4096;

/// Decoded instructions by address. An entry is used only while the
/// address space's [`AddressSpace::code_generation`] is unchanged, so
/// writes to executable memory and mapping changes (self-modifying code,
/// `mprotect`, `munmap`) are always seen.
pub struct DecodeCache {
    entries: Vec<Option<(u64, u64, Instruction)>>,
}

impl Default for DecodeCache {
    fn default() -> Self {
        DecodeCache {
            entries: vec![None; CACHE_ENTRIES],
        }
    }
}

impl DecodeCache {
    /// An empty cache.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    fn slot(rip: u64) -> usize {
        // CACHE_ENTRIES is a power of two; the mask keeps the index in range.
        usize::try_from((rip ^ (rip >> 12)) & (CACHE_ENTRIES as u64 - 1)).unwrap_or(0)
    }

    fn get(&self, rip: u64, generation: u64) -> Option<Instruction> {
        match self.entries.get(Self::slot(rip)) {
            Some(Some((r, g, insn))) if *r == rip && *g == generation => Some(*insn),
            _ => None,
        }
    }

    fn put(&mut self, rip: u64, generation: u64, insn: Instruction) {
        if let Some(entry) = self.entries.get_mut(Self::slot(rip)) {
            *entry = Some((rip, generation, insn));
        }
    }
}

fn fetch_and_decode(state: &CpuState, mem: &AddressSpace) -> Result<Instruction, ExitReason> {
    let rip = state.rip;
    let mut bytes = [0u8; MAX_INSTRUCTION_LEN];
    let available = mem
        .fetch_partial(rip, &mut bytes)
        .map_err(|f| ExitReason::PageFault {
            rip,
            addr: f.addr,
            write: false,
            fetch: true,
            mapped: f.mapped,
            present: f.present,
        })?;
    let fetched = &bytes[..available];
    match decode(fetched, rip) {
        Ok(insn) => Ok(insn),
        Err(DecodeError::NeedMoreBytes) if available < MAX_INSTRUCTION_LEN => {
            // The instruction runs into a page that cannot be executed.
            let addr = u64::try_from(available)
                .ok()
                .and_then(|n| rip.checked_add(n))
                .unwrap_or(rip);
            let fault = mem.fetch(addr, &mut [0]).err();
            Err(ExitReason::PageFault {
                rip,
                addr,
                write: false,
                fetch: true,
                mapped: fault.is_some_and(|f| f.mapped),
                present: fault.is_some_and(|f| f.present),
            })
        }
        Err(_) => Err(ExitReason::InvalidOpcode {
            rip,
            bytes: InstructionBytes::new(fetched),
        }),
    }
}

fn instruction_bytes(mem: &AddressSpace, rip: GuestAddr, len: u8) -> InstructionBytes {
    let mut bytes = [0u8; MAX_INSTRUCTION_LEN];
    let n = usize::from(len).min(MAX_INSTRUCTION_LEN);
    let got = mem.fetch_partial(rip, &mut bytes[..n]).unwrap_or(0);
    InstructionBytes::new(&bytes[..got])
}

fn execute_decoded(
    state: &mut CpuState,
    mem: &AddressSpace,
    insn: &Instruction,
) -> Result<(), ExitReason> {
    let rip = state.rip;
    let repeating =
        insn.rep != paludarium_decoder::RepPrefix::None && exec::is_string(insn.mnemonic);
    let comparison = repeating && exec::is_comparison_string(insn.mnemonic);
    let bytes = instruction_bytes(mem, rip, insn.len);
    if !comparison
        || state
            .repeat_continuation
            .is_some_and(|c| c.instruction != *insn || c.bytes != bytes)
    {
        state.repeat_continuation = None;
    }
    if comparison && state.repeat_continuation.is_none() {
        state.repeat_continuation = Some(RepeatContinuation {
            instruction: *insn,
            bytes,
            initial_flags: state.rflags,
        });
    }
    let snapshot = state.clone();
    let result = exec::execute(state, mem, insn);
    if result.is_ok() {
        if state.rip != rip {
            state.repeat_continuation = None;
        }
    } else if let Err(stop) = result {
        if matches!(stop, Stop::Fault(_)) && repeating {
            if let Some(c) = state.repeat_continuation {
                state.rflags = c.initial_flags;
            }
        } else if stop != Stop::Syscall {
            *state = snapshot;
        }
        state.repeat_continuation = None;
    }
    result.map_err(|stop| match stop {
        Stop::Fault(f) => ExitReason::PageFault {
            rip,
            addr: f.addr,
            write: f.write,
            fetch: f.fetch,
            mapped: f.mapped,
            present: f.present,
        },
        Stop::Invalid => ExitReason::InvalidOpcode {
            rip,
            bytes: instruction_bytes(mem, rip, insn.len),
        },
        Stop::Halt => ExitReason::Halt { rip },
        Stop::GeneralProtection => ExitReason::GeneralProtection { rip },
        Stop::ArithmeticFault => ExitReason::ArithmeticFault { rip },
        Stop::Syscall => ExitReason::Syscall { rip: state.rip },
    })
}

/// Executes one instruction. `Ok(())` means the guest can continue.
pub fn step(state: &mut CpuState, mem: &AddressSpace) -> Result<(), ExitReason> {
    let insn = fetch_for_state(state, mem)?;
    execute_decoded(state, mem, &insn)
}

/// Executes one instruction, reusing decoded instructions from `cache`.
pub fn step_cached(
    state: &mut CpuState,
    mem: &AddressSpace,
    cache: &mut DecodeCache,
) -> Result<(), ExitReason> {
    let generation = mem.code_generation();
    let insn = match cache.get(state.rip.0, generation) {
        Some(insn) => insn,
        None => {
            let insn = fetch_for_state(state, mem)?;
            cache.put(state.rip.0, generation, insn);
            insn
        }
    };
    execute_decoded(state, mem, &insn)
}

fn fetch_for_state(state: &mut CpuState, mem: &AddressSpace) -> Result<Instruction, ExitReason> {
    match fetch_and_decode(state, mem) {
        Ok(insn) => Ok(insn),
        Err(error) => {
            if let Some(continuation) = state.repeat_continuation.take()
                && continuation.instruction.rip == state.rip
            {
                state.rflags = continuation.initial_flags;
            }
            Err(error)
        }
    }
}

/// Runs at most `budget` instructions (BR4.3). Returns why execution stopped;
/// `BudgetExhausted` when the budget ran out.
pub fn run(state: &mut CpuState, mem: &AddressSpace, budget: u64) -> ExitReason {
    run_cached(state, mem, budget, &mut DecodeCache::new())
}

/// [`run`] with a decode cache that the caller keeps between calls (one per
/// guest thread).
pub fn run_cached(
    state: &mut CpuState,
    mem: &AddressSpace,
    budget: u64,
    cache: &mut DecodeCache,
) -> ExitReason {
    for _ in 0..budget {
        if let Err(reason) = step_cached(state, mem, cache) {
            return reason;
        }
    }
    ExitReason::BudgetExhausted { rip: state.rip }
}

/// Address of the instruction a state would execute next.
#[must_use]
pub fn current_rip(state: &CpuState) -> GuestAddr {
    state.rip
}

#[cfg(test)]
mod tests {
    use super::*;
    use paludarium_mmu::{MappingKind, Prot};

    const CODE: u64 = 0x40_0000;
    const STACK_TOP: u64 = 0x80_0000;

    fn machine(code: &[u8]) -> (CpuState, AddressSpace) {
        let mut mem = AddressSpace::new();
        mem.map(
            Some(GuestAddr(CODE)),
            0x1000,
            Prot::READ_EXEC,
            MappingKind::ElfSegment,
        )
        .unwrap();
        mem.map(
            Some(GuestAddr(STACK_TOP - 0x2000)),
            0x2000,
            Prot::READ_WRITE,
            MappingKind::Stack,
        )
        .unwrap();
        mem.write_initial(GuestAddr(CODE), code).unwrap();
        (CpuState::new(GuestAddr(CODE), GuestAddr(STACK_TOP)), mem)
    }

    #[test]
    fn runs_until_syscall_with_linux_register_convention() {
        // mov eax, 60; mov edi, 7; syscall
        let code = [0xb8, 60, 0, 0, 0, 0xbf, 7, 0, 0, 0, 0x0f, 0x05];
        let (mut s, mem) = machine(&code);
        let reason = run(&mut s, &mem, 100);
        assert_eq!(
            reason,
            ExitReason::Syscall {
                rip: GuestAddr(CODE + 12)
            }
        );
        assert_eq!(s.gpr[reg::RAX], 60);
        assert_eq!(s.gpr[reg::RDI], 7);
        assert_eq!(s.gpr[reg::RCX], CODE + 12);
        assert_eq!(s.gpr[reg::R11], s.rflags);
    }

    #[test]
    fn budget_exhaustion_stops_an_infinite_loop() {
        // jmp $ (eb fe)
        let (mut s, mem) = machine(&[0xeb, 0xfe]);
        assert_eq!(
            run(&mut s, &mem, 1000),
            ExitReason::BudgetExhausted {
                rip: GuestAddr(CODE)
            }
        );
    }

    #[test]
    fn unsupported_and_invalid_bytes_are_invalid_opcode() {
        // ud2 (0f 0b)
        let (mut s, mem) = machine(&[0x0f, 0x0b]);
        match run(&mut s, &mem, 10) {
            ExitReason::InvalidOpcode { rip, bytes } => {
                assert_eq!(rip, GuestAddr(CODE));
                assert_eq!(&bytes.as_slice()[..2], &[0x0f, 0x0b]);
            }
            other => panic!("unexpected {other:?}"),
        }
        // cpuid is valid x86 but not implemented.
        let (mut s, mem) = machine(&[0x0f, 0xa2]);
        assert!(matches!(
            run(&mut s, &mem, 10),
            ExitReason::InvalidOpcode { .. }
        ));
    }

    #[test]
    fn memory_faults_report_address_and_direction() {
        // mov [0x1000], eax  (89 04 25 00 10 00 00)
        let (mut s, mem) = machine(&[0x89, 0x04, 0x25, 0x00, 0x10, 0, 0]);
        assert_eq!(
            run(&mut s, &mem, 10),
            ExitReason::PageFault {
                rip: GuestAddr(CODE),
                addr: GuestAddr(0x1000),
                write: true,
                fetch: false,
                mapped: false,
                present: false
            }
        );
        // Jumping to unmapped memory faults on the fetch.
        let (mut s, mem) = machine(&[0xff, 0xe0]); // jmp rax (rax = 0)
        assert_eq!(
            run(&mut s, &mem, 10),
            ExitReason::PageFault {
                rip: GuestAddr(0),
                addr: GuestAddr(0),
                write: false,
                fetch: true,
                mapped: false,
                present: false
            }
        );
    }

    #[test]
    fn call_ret_push_pop_use_the_stack() {
        // call +1; hlt; (target:) push 5; pop rbx; ret
        let code = [0xe8, 0x01, 0, 0, 0, 0xf4, 0x6a, 0x05, 0x5b, 0xc3];
        let (mut s, mem) = machine(&code);
        assert_eq!(
            run(&mut s, &mem, 100),
            ExitReason::Halt {
                rip: GuestAddr(CODE + 5)
            }
        );
        assert_eq!(s.gpr[reg::RBX], 5);
        assert_eq!(s.gpr[reg::RSP], STACK_TOP);
    }

    #[test]
    fn writes_to_32_bit_registers_zero_extend() {
        // mov rax, -1; mov eax, 1; mov rbx, -1; mov bl, 0
        let code = [
            0x48, 0xc7, 0xc0, 0xff, 0xff, 0xff, 0xff, 0xb8, 1, 0, 0, 0, 0x48, 0xc7, 0xc3, 0xff,
            0xff, 0xff, 0xff, 0xb3, 0x00, 0xf4,
        ];
        let (mut s, mem) = machine(&code);
        assert!(matches!(run(&mut s, &mem, 100), ExitReason::Halt { .. }));
        assert_eq!(s.gpr[reg::RAX], 1);
        assert_eq!(s.gpr[reg::RBX], 0xffff_ffff_ffff_ff00);
    }

    #[test]
    fn rep_stosq_fills_memory_and_divide_by_zero_traps() {
        // lea rdi, [rsp-64]; mov ecx, 8; mov eax, 0x11; rep stosq; xor ecx, ecx; div rcx
        let code = [
            0x48, 0x8d, 0x7c, 0x24, 0xc0, 0xb9, 8, 0, 0, 0, 0xb8, 0x11, 0, 0, 0, 0xf3, 0x48, 0xab,
            0x31, 0xc9, 0x48, 0xf7, 0xf1,
        ];
        let (mut s, mem) = machine(&code);
        assert_eq!(
            run(&mut s, &mem, 100),
            ExitReason::ArithmeticFault {
                rip: GuestAddr(CODE + 20)
            }
        );
        assert_eq!(s.gpr[reg::RCX], 0);
        assert_eq!(mem.read_u64(GuestAddr(STACK_TOP - 64)).unwrap(), 0x11);
        assert_eq!(mem.read_u64(GuestAddr(STACK_TOP - 8)).unwrap(), 0x11);
    }

    #[test]
    fn misaligned_movaps_is_a_general_protection_fault() {
        // movaps [rsp-15], xmm0 (0f 29 44 24 f1)
        let (mut s, mem) = machine(&[0x0f, 0x29, 0x44, 0x24, 0xf1]);
        assert_eq!(
            run(&mut s, &mem, 10),
            ExitReason::GeneralProtection {
                rip: GuestAddr(CODE)
            }
        );
    }

    #[test]
    fn shift_by_zero_keeps_flags_but_zero_extends_32_bit_destination() {
        // Regression found by the insn-shift differential test.
        // mov rax, -1; xor ecx, ecx; stc; shl eax, cl; hlt
        let code = [
            0x48, 0xc7, 0xc0, 0xff, 0xff, 0xff, 0xff, 0x31, 0xc9, 0xf9, 0xd3, 0xe0, 0xf4,
        ];
        let (mut s, mem) = machine(&code);
        // stc is not in the U1 set; set CF directly and start after it.
        let reason = run(&mut s, &mem, 2);
        assert!(matches!(reason, ExitReason::BudgetExhausted { .. }));
        s.rflags |= flag::CF;
        s.rip = GuestAddr(CODE + 10);
        assert!(matches!(run(&mut s, &mem, 10), ExitReason::Halt { .. }));
        assert_eq!(s.gpr[reg::RAX], 0xffff_ffff);
        assert!(s.flag(flag::CF));
    }

    #[test]
    fn decode_cache_sees_self_modifying_code() {
        // An RWX page: execute `mov eax, 1; hlt`, patch the immediate, rerun.
        let mut mem = AddressSpace::new();
        mem.map(
            Some(GuestAddr(CODE)),
            0x1000,
            Prot::from_bits(7).unwrap(),
            MappingKind::Anonymous,
        )
        .unwrap();
        mem.write(GuestAddr(CODE), &[0xb8, 1, 0, 0, 0, 0xf4])
            .unwrap();
        let mut cache = DecodeCache::new();
        let mut s = CpuState::new(GuestAddr(CODE), GuestAddr(0));
        assert!(matches!(
            run_cached(&mut s, &mem, 10, &mut cache),
            ExitReason::Halt { .. }
        ));
        assert_eq!(s.gpr[reg::RAX], 1);
        mem.write(GuestAddr(CODE + 1), &[2]).unwrap();
        s.rip = GuestAddr(CODE);
        assert!(matches!(
            run_cached(&mut s, &mem, 10, &mut cache),
            ExitReason::Halt { .. }
        ));
        assert_eq!(s.gpr[reg::RAX], 2);
    }

    #[test]
    fn decode_cache_sees_unmapped_code() {
        let (mut s, mut mem) = machine(&[0x90, 0xeb, 0xfd]); // nop; jmp back
        let mut cache = DecodeCache::new();
        assert!(matches!(
            run_cached(&mut s, &mem, 50, &mut cache),
            ExitReason::BudgetExhausted { .. }
        ));
        mem.unmap(GuestAddr(CODE), 0x1000).unwrap();
        assert!(matches!(
            run_cached(&mut s, &mem, 50, &mut cache),
            ExitReason::PageFault { write: false, .. }
        ));
    }

    #[test]
    fn fs_relative_load_uses_fs_base() {
        // mov rax, fs:[8]; hlt
        let code = [0x64, 0x48, 0x8b, 0x04, 0x25, 0x08, 0, 0, 0, 0xf4];
        let (mut s, mem) = machine(&code);
        s.fs_base = STACK_TOP - 0x100;
        mem.write_u64(GuestAddr(STACK_TOP - 0xf8), 0xabcd).unwrap();
        assert!(matches!(run(&mut s, &mem, 10), ExitReason::Halt { .. }));
        assert_eq!(s.gpr[reg::RAX], 0xabcd);
    }
}
