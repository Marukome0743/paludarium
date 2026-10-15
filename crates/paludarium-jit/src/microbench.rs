//! Diagnostic-only bounded fixtures. Timing is done by the actual JS Worker at
//! chunk boundaries, never by a native clock or inside a guest instruction.
use crate::{CodeCache, ExecutionBridge, WasmCodeCache, block, emit};
use paludarium_cpu::{CpuState, DecodeCache};
use paludarium_mmu::{AddressSpace, MappingKind, Prot};
use paludarium_types::GuestAddr;
use std::sync::Arc;

pub struct DiagnosticBench {
    kind: u32,
    observe: bool,
    memory: AddressSpace,
    cache: WasmCodeCache,
    decode: DecodeCache,
    bridge: Arc<dyn ExecutionBridge>,
    bytes: Vec<u8>,
    extracted: block::Block,
    expected: u64,
    instructions: u64,
    operations: u64,
    checksum: u64,
    decoded: paludarium_decoder::Instruction,
    emitted: Vec<u8>,
}

impl DiagnosticBench {
    /// kinds0 loop,1 interpreter,2 cold,3 negative,4 warm,5 epoch,
    /// 6 snapshot,7 extract,8 emit,9 cold prepare. short/max are existing2/64 blocks.
    pub fn new(
        kind: u32,
        maximum: bool,
        observe: bool,
        bridge: Arc<dyn ExecutionBridge>,
    ) -> Option<Self> {
        if kind > 11 {
            return None;
        }
        let bytes = if matches!(kind, 10 | 11) {
            vec![0x90; 128]
        } else if maximum {
            [vec![0xb8, 1, 0, 0, 0].repeat(64), vec![0xc3]].concat()
        } else {
            vec![0xb8, 42, 0, 0, 0, 0x48, 0x83, 0xc0, 1, 0xc3]
        };
        let extracted = block::extract(
            if matches!(kind, 10 | 11) {
                &[0xb8, 42, 0, 0, 0, 0x48, 0x83, 0xc0, 1]
            } else {
                &bytes
            },
            4096,
        )?;
        let emitted = emit::emit(&extracted)?;
        let mut memory = AddressSpace::new();
        memory
            .map(
                Some(GuestAddr(4096)),
                4096,
                Prot::READ_EXEC,
                MappingKind::ElfSegment,
            )
            .ok()?;
        memory
            .write_initial(
                GuestAddr(4096),
                if kind == 3 { &[0x90, 0xc3] } else { &bytes },
            )
            .ok()?;
        let instructions = if maximum { 64 } else { 2 };
        let expected = if maximum { 1 } else { 43 };
        let cache = WasmCodeCache::new(bridge.clone()).with_minimum_block(2);
        let decoded = paludarium_decoder::decode(
            if kind == 3 { &[0x90, 0xc3] } else { &bytes },
            GuestAddr(4096),
        )
        .ok()?;
        let mut bench = Self {
            kind,
            observe,
            memory,
            cache,
            decode: DecodeCache::new(),
            bridge,
            bytes,
            extracted,
            expected,
            instructions,
            operations: 0,
            checksum: 0,
            decoded,
            emitted,
        };
        if kind == 10 {
            // Each fresh start has a full acceleration budget. One 64-step
            // warmup would reject only its first instruction: the remaining
            // steps have too little budget to enter the acceleration hook.
            for offset in 0..64 {
                let mut state = CpuState::new(GuestAddr(4096 + offset), GuestAddr(8192));
                let _ = paludarium_cpu::run_cached_with_counted_hook(
                    &mut state,
                    &bench.memory,
                    64,
                    &mut bench.decode,
                    paludarium_cpu::AccelerationPolicy {
                        maximum_block: 64,
                        cache_rejections: true,
                    },
                    |_, _, det| {
                        *det = true;
                        None
                    },
                );
                if state.rip.0 != 4160 + offset {
                    return None;
                }
            }
        }
        if matches!(kind, 3 | 4 | 5) {
            // Explicit untimed warmup. Negative is a real deterministic reject.
            let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
            let result = bench.cache.try_run_counted(&mut state, &bench.memory);
            if kind == 3 {
                if result.is_some() {
                    return None;
                }
            } else if result.is_none() || state.gpr[0] != expected {
                return None;
            }
        }
        Some(bench)
    }

    pub fn chunk(&mut self, count: u32) -> Option<u64> {
        if count == 0 || count > 1024 {
            return None;
        }
        for _ in 0..count {
            let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
            let value = match self.kind {
                0 => std::hint::black_box(1),
                1 => {
                    let _ = paludarium_cpu::run_cached(
                        &mut state,
                        &self.memory,
                        self.instructions,
                        &mut self.decode,
                    );
                    if state.gpr[0] != self.expected || state.rip.0 != self.extracted.end {
                        return None;
                    }
                    state.gpr[0]
                }
                2 | 4 | 5 => {
                    if self.kind == 2 {
                        self.cache = WasmCodeCache::new(self.bridge.clone()).with_minimum_block(2);
                    }
                    if self.kind == 5 {
                        self.memory
                            .write_initial(GuestAddr(4096), &self.bytes)
                            .ok()?;
                    }
                    let (_, count) = self.cache.try_run_counted(&mut state, &self.memory)?;
                    if count != self.instructions
                        || state.gpr[0] != self.expected
                        || state.rip.0 != self.extracted.end
                    {
                        return None;
                    }
                    state.gpr[0]
                }
                3 => {
                    let before = state.clone();
                    if self
                        .cache
                        .try_run_counted(&mut state, &self.memory)
                        .is_some()
                        || state != before
                    {
                        return None;
                    }
                    1
                }
                6 => self
                    .memory
                    .code_snapshot(GuestAddr(4096), 960)
                    .ok()?
                    .bytes
                    .len() as u64,
                7 => block::extract(&self.bytes, 4096)?.operations.len() as u64,
                8 => emit::emit(&self.extracted)?.len() as u64,
                9 => {
                    let id = crate::bridge::next_module_id()?;
                    crate::jit_cost::add(crate::jit_cost::Counter::PrepareCalls, 1);
                    if !self.bridge.prepare(id, &self.emitted) {
                        return None;
                    }
                    1
                }
                10 | 11 => {
                    if self.kind == 10 {
                        let _ = paludarium_cpu::run_cached_with_counted_hook(
                            &mut state,
                            &self.memory,
                            64,
                            &mut self.decode,
                            paludarium_cpu::AccelerationPolicy {
                                maximum_block: 64,
                                cache_rejections: true,
                            },
                            |_, _, det| {
                                *det = true;
                                None
                            },
                        );
                    } else {
                        let _ = paludarium_cpu::run_cached(
                            &mut state,
                            &self.memory,
                            64,
                            &mut self.decode,
                        );
                    }
                    if state.rip.0 != 4160 || state.gpr[0] != 0 {
                        return None;
                    }
                    1
                }
                _ => return None,
            };
            if self.observe {
                let (space, epoch) = self.memory.code_epoch();
                crate::jit_cost::observe_site(space, epoch, 4096, 5, &self.decoded);
            }
            self.operations = self.operations.checked_add(1)?;
            self.checksum = self.checksum.checked_add(value)?;
        }
        Some(self.checksum)
    }
    pub fn operations(&self) -> u64 {
        self.operations
    }
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;
    struct Never;
    impl ExecutionBridge for Never {
        fn execute(&self, _: u32, _: &[u8], _: &mut [u64; 18]) -> bool {
            panic!("no execution in these fixtures")
        }
    }
    fn run(kind: u32, max: bool) -> DiagnosticBench {
        DiagnosticBench::new(kind, max, false, Arc::new(Never)).unwrap()
    }
    #[test]
    fn u14_micro_loop() {
        let mut b = run(0, false);
        assert_eq!(b.chunk(1024), Some(1024));
        assert_eq!(b.operations(), 1024);
    }
    #[test]
    fn u14_micro_interpreter_short() {
        assert_eq!(run(1, false).chunk(2), Some(86));
    }
    #[test]
    fn u14_micro_interpreter_max() {
        assert_eq!(run(1, true).chunk(2), Some(2));
    }
    #[test]
    fn u14_micro_negative_preserves_cpu() {
        assert_eq!(run(3, false).chunk(2), Some(2));
    }
    #[test]
    fn u14_micro_snapshot() {
        assert_eq!(run(6, false).chunk(1), Some(960));
    }
    #[test]
    fn u14_micro_extract_max() {
        assert_eq!(run(7, true).chunk(1), Some(64));
    }
    #[test]
    fn u14_micro_emit_actual_wasm() {
        assert!(run(8, false).chunk(1).unwrap() > 8);
    }
    #[test]
    fn u14_micro_invalid_bounds() {
        let mut b = run(0, false);
        assert_eq!(b.chunk(0), None);
        assert_eq!(b.chunk(1025), None);
        assert_eq!(b.operations(), 0);
    }
    #[test]
    fn u14_micro_hint_warmup_covers_every_measured_boundary() {
        let mut bench = run(10, false);
        assert_eq!(bench.operations(), 0);
        let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
        let _ = paludarium_cpu::run_cached_with_counted_hook(
            &mut state,
            &bench.memory,
            64,
            &mut bench.decode,
            paludarium_cpu::AccelerationPolicy {
                maximum_block: 64,
                cache_rejections: true,
            },
            |_, _, _| panic!("every measured boundary must already be rejected"),
        );
        assert_eq!(state.rip.0, 4160);
        assert_eq!(bench.chunk(2), Some(2));
        assert_eq!(bench.operations(), 2);
    }
}
