//! Synchronous C9 bridge. Compilation runs outside the MMU epoch guard;
//! register-only execution runs inside it and cannot reenter guest memory.
use crate::{CodeCache, block, cache::EpochCache, emit};
use paludarium_cpu::CpuState;
#[cfg(feature = "u14-cost-profile")]
use paludarium_cpu::jit_cost::{self, Counter};
use paludarium_mmu::AddressSpace;
use paludarium_types::{ExitReason, GuestAddr};
use std::sync::{
    Arc,
    atomic::{AtomicU32, AtomicU64, Ordering},
};

/// One Worker-local synchronous wasm compiler/executor. State is trusted Rust
/// scratch storage: GPR0..15, rflags, RIP. Failure must never commit guest state.
pub trait ExecutionBridge: Send + Sync {
    /// Feature-only no-touch observation. None means unsupported observation,
    /// not a missing prepared entry, and never requests preparation.
    #[cfg(feature = "u14-cost-profile")]
    fn diagnostic_prepared(&self, _module_id: u32, _wasm: &[u8]) -> Option<bool> {
        None
    }
    /// Executes an already prepared Worker-local entry. `None` requests cold
    /// preparation outside the MMU guard; failures must roll back scratch.
    fn execute_ready(&self, _module_id: u32, _wasm: &[u8], _state: &mut [u64; 18]) -> Option<bool> {
        None
    }
    /// Compiles outside the MMU epoch guard. No guest state may change here.
    fn prepare(&self, _module_id: u32, _wasm: &[u8]) -> bool {
        true
    }
    fn execute(&self, module_id: u32, wasm: &[u8], state: &mut [u64; 18]) -> bool;
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct JitStatistics {
    pub translated_blocks: u64,
    pub executed_blocks: u64,
    pub executed_instructions: u64,
    pub fallbacks: u64,
}

struct Translation {
    id: u32,
    code: Vec<u8>,
    instruction_count: usize,
}
static NEXT_MODULE: AtomicU32 = AtomicU32::new(1);

/// A minimal register-only wasm cache. Unsupported instructions, memory,
/// syscall and fault handling remain entirely in the existing interpreter.
pub struct WasmCodeCache {
    bridge: Arc<dyn ExecutionBridge>,
    cache: EpochCache<Option<Arc<Translation>>>,
    translated: AtomicU64,
    executed: AtomicU64,
    instructions: AtomicU64,
    fallbacks: AtomicU64,
    minimum_block: usize,
}

impl WasmCodeCache {
    #[must_use]
    pub fn new(bridge: Arc<dyn ExecutionBridge>) -> Self {
        Self {
            bridge,
            cache: EpochCache::new(),
            translated: AtomicU64::new(0),
            executed: AtomicU64::new(0),
            instructions: AtomicU64::new(0),
            fallbacks: AtomicU64::new(0),
            minimum_block: 1,
        }
    }
    /// A compilation selection heuristic, never a guest execution limit.
    /// Shorter supported sequences continue through the ordinary interpreter.
    #[must_use]
    pub fn with_minimum_block(mut self, minimum: usize) -> Self {
        self.minimum_block = minimum.clamp(1, 64);
        self
    }
    #[must_use]
    pub fn statistics(&self) -> JitStatistics {
        JitStatistics {
            translated_blocks: self.translated.load(Ordering::Relaxed),
            executed_blocks: self.executed.load(Ordering::Relaxed),
            executed_instructions: self.instructions.load(Ordering::Relaxed),
            fallbacks: self.fallbacks.load(Ordering::Relaxed),
        }
    }
    #[cfg(feature = "u14-cost-profile")]
    fn observe_next(&self, memory: &AddressSpace, space: u64, generation: u64, rip: u64) {
        use crate::cache::Peek;
        jit_cost::add(Counter::ObservationLookups, 1);
        let observed = memory.with_code_epoch(space, generation, || {
            match self.cache.peek(space, rip, generation) {
                Peek::Missing => jit_cost::add(Counter::NextMissing, 1),
                Peek::Stale => jit_cost::add(Counter::NextEpoch, 1),
                Peek::Present(None) => jit_cost::add(Counter::NextNegative, 1),
                Peek::Present(Some(next)) => {
                    jit_cost::add(Counter::NextPositive, 1);
                    let field = match self.bridge.diagnostic_prepared(next.id, &next.code) {
                        Some(true) => Counter::NextPrepared,
                        Some(false) => Counter::NextUnprepared,
                        None => Counter::NextUnavailable,
                    };
                    jit_cost::add(field, 1);
                }
            }
        });
        if observed.is_none() {
            jit_cost::add(Counter::NextEpoch, 1);
        }
    }
    fn run(
        &self,
        state: &mut CpuState,
        memory: &AddressSpace,
        deterministic_rejection: &mut bool,
    ) -> Option<(ExitReason, u64)> {
        if state.repeat_continuation.is_some() {
            return None;
        }
        let (space, generation) = memory.code_epoch();
        let (translation, space, generation) =
            match self
                .cache
                .get_selected(space, state.rip.0, generation, Option::is_some)
            {
                Some(translation) => {
                    *deterministic_rejection = translation.is_none();
                    #[cfg(feature = "u14-cost-profile")]
                    if translation.is_none() {
                        jit_cost::add(Counter::NegativeHits, 1);
                    }
                    (translation?, space, generation)
                }
                None => {
                    #[cfg(feature = "u14-cost-profile")]
                    jit_cost::add(Counter::CacheMisses, 1);
                    let snapshot = memory.code_snapshot(state.rip, 960).ok()?;
                    #[cfg(feature = "u14-cost-profile")]
                    jit_cost::add(Counter::SnapshotBytes, snapshot.bytes.len() as u64);
                    let Some(block) = block::extract(&snapshot.bytes, state.rip.0) else {
                        *deterministic_rejection = true;
                        // Cache a deterministic unsupported first instruction too.
                        // Any executable mutation changes its epoch before reuse.
                        self.cache.insert(
                            snapshot.address_space,
                            state.rip.0,
                            snapshot.generation,
                            snapshot.bytes.len(),
                            None,
                        );
                        return None;
                    };
                    if block.operations.len() < self.minimum_block {
                        *deterministic_rejection = true;
                        self.cache.insert(
                            snapshot.address_space,
                            state.rip.0,
                            snapshot.generation,
                            snapshot.bytes.len(),
                            None,
                        );
                        return None;
                    }
                    let code = emit::emit(&block)?;
                    // Never reuse an ID, even on exhaustion: Worker-local JS caches
                    // must not mistake a different module for a previous one.
                    let id = NEXT_MODULE
                        .try_update(Ordering::Relaxed, Ordering::Relaxed, |id| id.checked_add(1))
                        .ok()?;
                    let translation = Arc::new(Translation {
                        id,
                        code,
                        instruction_count: block.operations.len(),
                    });
                    if !self.cache.insert(
                        snapshot.address_space,
                        state.rip.0,
                        snapshot.generation,
                        usize::try_from(block.end.checked_sub(block.entry)?).ok()?,
                        Some(translation.clone()),
                    ) {
                        return None;
                    }
                    self.translated.fetch_add(1, Ordering::Relaxed);
                    #[cfg(feature = "u14-cost-profile")]
                    jit_cost::add(Counter::TranslatedBlocks, 1);
                    (translation, snapshot.address_space, snapshot.generation)
                }
            };
        let mut scratch = [0; 18];
        scratch[..16].copy_from_slice(&state.gpr);
        scratch[16] = state.rflags;
        scratch[17] = state.rip.0;
        let ready = memory.with_code_epoch(space, generation, || {
            self.bridge
                .execute_ready(translation.id, &translation.code, &mut scratch)
        });
        #[cfg(feature = "u14-cost-profile")]
        if ready.is_none() {
            jit_cost::add(Counter::EpochInvalidations, 1);
        }
        let ready = ready?;
        let success = if let Some(success) = ready {
            Some(success)
        } else {
            #[cfg(feature = "u14-cost-profile")]
            jit_cost::add(Counter::PrepareCalls, 1);
            if !self.bridge.prepare(translation.id, &translation.code) {
                #[cfg(feature = "u14-cost-profile")]
                jit_cost::add(Counter::PrepareRejections, 1);
                return None;
            }
            memory.with_code_epoch(space, generation, || {
                #[cfg(feature = "u14-cost-profile")]
                jit_cost::add(Counter::ExecuteCalls, 1);
                self.bridge
                    .execute(translation.id, &translation.code, &mut scratch)
            })
        };
        #[cfg(feature = "u14-cost-profile")]
        if success.is_none() {
            jit_cost::add(Counter::EpochInvalidations, 1);
        }
        let success = success?;
        if !success {
            #[cfg(feature = "u14-cost-profile")]
            jit_cost::add(Counter::ExecuteRejections, 1);
            return None;
        }
        state.gpr.copy_from_slice(&scratch[..16]);
        state.rflags = scratch[16];
        state.rip = GuestAddr(scratch[17]);
        self.executed.fetch_add(1, Ordering::Relaxed);
        self.instructions
            .fetch_add(translation.instruction_count as u64, Ordering::Relaxed);
        #[cfg(feature = "u14-cost-profile")]
        {
            jit_cost::add(Counter::ExecutedBlocks, 1);
            jit_cost::add(
                Counter::ExecutedInstructions,
                translation.instruction_count as u64,
            );
            jit_cost::block_length(translation.instruction_count);
            self.observe_next(memory, space, generation, state.rip.0);
        }
        Some((
            ExitReason::BudgetExhausted { rip: state.rip },
            translation.instruction_count as u64,
        ))
    }
}
impl CodeCache for WasmCodeCache {
    fn cache_rejections(&self) -> bool {
        true
    }
    fn eligible(&self, instruction: &paludarium_decoder::Instruction) -> bool {
        crate::eligible_instruction(instruction)
    }
    fn try_run(&self, state: &mut CpuState, memory: &AddressSpace) -> Option<ExitReason> {
        self.try_run_counted(state, memory)
            .map(|(reason, _)| reason)
    }
    fn try_run_counted(
        &self,
        state: &mut CpuState,
        memory: &AddressSpace,
    ) -> Option<(ExitReason, u64)> {
        self.try_run_with_hint(state, memory).0
    }
    fn try_run_with_hint(
        &self,
        state: &mut CpuState,
        memory: &AddressSpace,
    ) -> (Option<(ExitReason, u64)>, bool) {
        let mut deterministic_rejection = false;
        let result = self.run(state, memory, &mut deterministic_rejection);
        if result.is_none() {
            self.fallbacks.fetch_add(1, Ordering::Relaxed);
            #[cfg(feature = "u14-cost-profile")]
            jit_cost::add(Counter::Fallbacks, 1);
        }
        (result, deterministic_rejection)
    }
    fn invalidate(&self, page: GuestAddr) {
        self.cache.invalidate(page.0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use paludarium_mmu::{MappingKind, Prot};
    use std::{
        io::Write,
        process::{Command, Stdio},
    };

    struct NodeBridge;
    #[cfg(feature = "u14-cost-profile")]
    #[derive(Default)]
    struct ObservingBridge {
        queries: AtomicU32,
        prepares: AtomicU32,
        executes: AtomicU32,
    }
    #[cfg(feature = "u14-cost-profile")]
    impl ExecutionBridge for ObservingBridge {
        fn diagnostic_prepared(&self, id: u32, _: &[u8]) -> Option<bool> {
            self.queries.fetch_add(1, Ordering::Relaxed);
            Some(id == 17)
        }
        fn prepare(&self, _: u32, _: &[u8]) -> bool {
            self.prepares.fetch_add(1, Ordering::Relaxed);
            false
        }
        fn execute(&self, _: u32, _: &[u8], _: &mut [u64; 18]) -> bool {
            self.executes.fetch_add(1, Ordering::Relaxed);
            false
        }
    }
    #[cfg(feature = "u14-cost-profile")]
    fn observation_case(kind: u32, expected_queries: u32) {
        let (state, memory) = machine(&[0xb8, 42, 0, 0, 0], 0);
        let before = state.clone();
        let epoch = memory.code_epoch();
        let bridge = Arc::new(ObservingBridge::default());
        let cache = WasmCodeCache::new(bridge.clone());
        let entry = Some(Arc::new(Translation {
            id: if kind == 2 { 18 } else { 17 },
            code: vec![0],
            instruction_count: 1,
        }));
        match kind {
            0 => {}
            3 => {
                cache.cache.insert(epoch.0, 4096, epoch.1, 1, None);
            }
            4 => {
                cache
                    .cache
                    .insert(epoch.0, 4096, epoch.1.wrapping_add(1), 1, entry);
            }
            5 => {
                cache
                    .cache
                    .insert(epoch.0.wrapping_add(1), 4096, epoch.1, 1, entry);
            }
            _ => {
                cache.cache.insert(epoch.0, 4096, epoch.1, 1, entry);
            }
        }
        if kind == 6 {
            cache.cache.invalidate(4096);
        }
        let statistics = cache.statistics();
        for _ in 0..3 {
            cache.observe_next(&memory, epoch.0, epoch.1, 4096);
        }
        assert_eq!(bridge.queries.load(Ordering::Relaxed), expected_queries);
        assert_eq!(bridge.prepares.load(Ordering::Relaxed), 0);
        assert_eq!(bridge.executes.load(Ordering::Relaxed), 0);
        assert_eq!(cache.statistics(), statistics);
        assert_eq!(state, before);
        assert_eq!(memory.code_epoch(), epoch);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_missing_never_prepares() {
        observation_case(0, 0);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_positive_only_queries_worker() {
        observation_case(1, 3);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_unprepared_never_compiles() {
        observation_case(2, 3);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_negative_never_queries_worker() {
        observation_case(3, 0);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_stale_never_queries_worker() {
        observation_case(4, 0);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_other_space_never_queries_worker() {
        observation_case(5, 0);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_invalidated_never_recreates_entry() {
        observation_case(6, 0);
    }
    #[cfg(feature = "u14-cost-profile")]
    #[test]
    fn u14_observe_default_bridge_reports_unavailable_without_prepare() {
        let bridge = WarmBridge::default();
        assert_eq!(bridge.diagnostic_prepared(17, &[]), None);
        assert_eq!(bridge.prepares.load(Ordering::Relaxed), 0);
        assert_eq!(bridge.executes.load(Ordering::Relaxed), 0);
    }
    #[derive(Default)]
    struct WarmBridge {
        prepared: AtomicU32,
        prepares: AtomicU32,
        executes: AtomicU32,
        fail: bool,
    }
    impl ExecutionBridge for WarmBridge {
        fn execute_ready(&self, id: u32, _: &[u8], scratch: &mut [u64; 18]) -> Option<bool> {
            if self.prepared.load(Ordering::Relaxed) != id {
                return None;
            }
            scratch[0] = 42;
            Some(!self.fail)
        }
        fn prepare(&self, id: u32, _: &[u8]) -> bool {
            self.prepares.fetch_add(1, Ordering::Relaxed);
            self.prepared.store(id, Ordering::Relaxed);
            true
        }
        fn execute(&self, _: u32, _: &[u8], scratch: &mut [u64; 18]) -> bool {
            self.executes.fetch_add(1, Ordering::Relaxed);
            scratch[0] = 42;
            !self.fail
        }
    }
    #[test]
    fn u14_warm_bridge_reuses_prepared_entry_without_second_prepare() {
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 0);
        let bridge = Arc::new(WarmBridge::default());
        let cache = WasmCodeCache::new(bridge.clone());
        assert!(cache.try_run(&mut state, &memory).is_some());
        assert!(cache.try_run(&mut state, &memory).is_some());
        assert_eq!(bridge.prepares.load(Ordering::Relaxed), 1);
        assert_eq!(bridge.executes.load(Ordering::Relaxed), 1);
        assert_eq!(cache.statistics().executed_blocks, 2);
    }
    #[test]
    fn u14_warm_bridge_failure_rolls_back_cpu_and_does_not_hint() {
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 17);
        let bridge = Arc::new(WarmBridge::default());
        let cache = WasmCodeCache::new(bridge.clone());
        assert!(cache.try_run(&mut state, &memory).is_some());
        let failing = WarmBridge {
            prepared: AtomicU32::new(bridge.prepared.load(Ordering::Relaxed)),
            fail: true,
            ..WarmBridge::default()
        };
        let mut scratch = [17; 18];
        assert_eq!(
            failing.execute_ready(bridge.prepared.load(Ordering::Relaxed), &[], &mut scratch),
            Some(false)
        );
        // Cache must never commit scratch returned by a failed ready execution.
        let failing = Arc::new(WarmBridge {
            fail: true,
            ..WarmBridge::default()
        });
        let cache = WasmCodeCache::new(failing);
        let before = state.clone();
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, false));
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, false));
        assert_eq!(state, before);
    }
    #[test]
    fn u14_warm_bridge_epoch_change_requires_new_module_preparation() {
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 0);
        let bridge = Arc::new(WarmBridge::default());
        let cache = WasmCodeCache::new(bridge.clone());
        cache.try_run(&mut state, &memory).unwrap();
        let previous = bridge.prepared.load(Ordering::Relaxed);
        memory.write(GuestAddr(4097), &[17]).unwrap();
        state.rip = GuestAddr(4096);
        cache.try_run(&mut state, &memory).unwrap();
        assert_ne!(previous, bridge.prepared.load(Ordering::Relaxed));
        assert_eq!(bridge.prepares.load(Ordering::Relaxed), 2);
    }
    #[test]
    fn u14_warm_bridge_separate_workers_prepare_independently() {
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 0);
        let left = Arc::new(WarmBridge::default());
        let right = Arc::new(WarmBridge::default());
        WasmCodeCache::new(left.clone())
            .try_run(&mut state, &memory)
            .unwrap();
        WasmCodeCache::new(right.clone())
            .try_run(&mut state, &memory)
            .unwrap();
        assert_eq!(left.prepares.load(Ordering::Relaxed), 1);
        assert_eq!(right.prepares.load(Ordering::Relaxed), 1);
    }
    #[test]
    fn u14_bridge_prepare_failure_never_executes_or_changes_state() {
        struct Reject;
        impl ExecutionBridge for Reject {
            fn prepare(&self, _: u32, _: &[u8]) -> bool {
                false
            }
            fn execute(&self, _: u32, _: &[u8], _: &mut [u64; 18]) -> bool {
                panic!("unprepared execution");
            }
        }
        let mut memory = AddressSpace::new();
        memory
            .map(
                Some(GuestAddr(4096)),
                4096,
                Prot::READ_EXEC,
                MappingKind::ElfSegment,
            )
            .unwrap();
        memory
            .write_initial(GuestAddr(4096), &[0xb8, 42, 0, 0, 0, 0xc3])
            .unwrap();
        let cache = WasmCodeCache::new(Arc::new(Reject));
        let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
        let before = state.clone();
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, false));
        assert_eq!(state, before);
        assert_eq!(cache.statistics().executed_blocks, 0);
    }

    #[test]
    fn u14_bridge_write_during_prepare_invalidates_before_execution() {
        struct Mutate(Arc<AddressSpace>);
        impl ExecutionBridge for Mutate {
            fn prepare(&self, _: u32, _: &[u8]) -> bool {
                let memory = self.0.clone();
                let (send, receive) = std::sync::mpsc::channel();
                let worker = std::thread::spawn(move || {
                    memory.write(GuestAddr(4096), &[0xcc]).unwrap();
                    send.send(()).unwrap();
                });
                receive
                    .recv_timeout(std::time::Duration::from_secs(1))
                    .expect("compilation must not hold MMU guard");
                worker.join().unwrap();
                true
            }
            fn execute(&self, _: u32, _: &[u8], _: &mut [u64; 18]) -> bool {
                panic!("stale prepared execution");
            }
        }
        let mut memory = AddressSpace::new();
        memory
            .map(
                Some(GuestAddr(4096)),
                4096,
                Prot::from_bits(7).unwrap(),
                MappingKind::ElfSegment,
            )
            .unwrap();
        memory
            .write_initial(GuestAddr(4096), &[0xb8, 42, 0, 0, 0, 0xc3])
            .unwrap();
        let memory = Arc::new(memory);
        let cache = WasmCodeCache::new(Arc::new(Mutate(memory.clone())));
        let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
        let before = state.clone();
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, false));
        assert_eq!(state, before);
        assert_eq!(cache.statistics().executed_blocks, 0);
    }
    #[test]
    fn u14_bridge_short_selection_fallback_preserves_state_and_counts() {
        let mut memory = AddressSpace::new();
        memory
            .map(
                Some(GuestAddr(4096)),
                4096,
                Prot::READ_EXEC,
                MappingKind::ElfSegment,
            )
            .unwrap();
        memory
            .write_initial(GuestAddr(4096), &[0xb8, 42, 0, 0, 0, 0xc3])
            .unwrap();
        let cache = WasmCodeCache::new(Arc::new(NodeBridge)).with_minimum_block(2);
        let mut state = CpuState::new(GuestAddr(4096), GuestAddr(8192));
        let before = state.clone();
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, true));
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, true));
        assert_eq!(state, before);
        let statistics = cache.statistics();
        assert_eq!(statistics.translated_blocks, 0);
        assert_eq!(statistics.executed_blocks, 0);
        assert_eq!(statistics.fallbacks, 2);
        assert_eq!(cache.minimum_block, 2);
        assert_eq!(
            WasmCodeCache::new(Arc::new(NodeBridge))
                .with_minimum_block(0)
                .minimum_block,
            1
        );
        assert_eq!(
            WasmCodeCache::new(Arc::new(NodeBridge))
                .with_minimum_block(usize::MAX)
                .minimum_block,
            64
        );
    }
    impl ExecutionBridge for NodeBridge {
        fn execute(&self, _id: u32, wasm: &[u8], state: &mut [u64; 18]) -> bool {
            let Ok(node) = std::env::var("PALUDARIUM_TEST_NODE") else {
                panic!("PALUDARIUM_TEST_NODE must name actual current Node executable");
            };
            let script = "import{readFileSync}from'node:fs';const lines=readFileSync(0,'utf8').trim().split('\\n');const memory=new WebAssembly.Memory({initial:1,maximum:65536,shared:true});const state=new BigUint64Array(memory.buffer,64,18);state.set(lines[1].split(',').map(BigInt));const module=new WebAssembly.Module(Uint8Array.from(Buffer.from(lines[0],'hex')));const instance=new WebAssembly.Instance(module,{env:{memory}});if(instance.exports.run(64)!==0)process.exit(1);console.log(Array.from(state,String).join(','));";
            let mut child = Command::new(node)
                .args(["--input-type=module", "-e", script])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spawn()
                .unwrap();
            let hex: String = wasm.iter().map(|byte| format!("{byte:02x}")).collect();
            let values = state
                .iter()
                .map(u64::to_string)
                .collect::<Vec<_>>()
                .join(",");
            writeln!(child.stdin.take().unwrap(), "{hex}\n{values}").unwrap();
            let output = child.wait_with_output().unwrap();
            if !output.status.success() {
                return false;
            }
            let text = String::from_utf8(output.stdout).unwrap();
            let values = text
                .trim()
                .split(',')
                .map(|word| word.parse::<u64>().unwrap())
                .collect::<Vec<_>>();
            state.copy_from_slice(&values);
            true
        }
    }
    fn machine(code: &[u8], rax: u64) -> (CpuState, AddressSpace) {
        let mut memory = AddressSpace::new();
        memory
            .map(
                Some(GuestAddr(4096)),
                8192,
                Prot::from_bits(7).unwrap(),
                MappingKind::ElfSegment,
            )
            .unwrap();
        memory.write_initial(GuestAddr(4096), code).unwrap();
        let mut state = CpuState::new(GuestAddr(4096), GuestAddr(12288));
        state.gpr[0] = rax;
        (state, memory)
    }
    fn differential(code: &[u8], rax: u64, instructions: u64) {
        let (mut state, memory) = machine(code, rax);
        let mut expected = state.clone();
        paludarium_cpu::run(&mut expected, &memory, instructions);
        let cache = WasmCodeCache::new(Arc::new(NodeBridge));
        assert!(cache.try_run(&mut state, &memory).is_some());
        assert_eq!(state, expected);
        assert_eq!(cache.statistics().executed_instructions, instructions);
    }
    #[test]
    fn u14_bridge_real_wasm_mov_matches_interpreter() {
        differential(
            &[
                0x48, 0xb8, 0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 1, 0xc3,
            ],
            0,
            1,
        );
    }
    #[test]
    fn u14_bridge_real_wasm_add_carry_matches_interpreter() {
        differential(&[0x48, 0x83, 0xc0, 1, 0xc3], u64::MAX, 1);
    }
    #[test]
    fn u14_bridge_real_wasm_sub_overflow_matches_interpreter() {
        differential(&[0x48, 0x83, 0xe8, 1, 0xc3], 1 << 63, 1);
    }
    #[test]
    fn u14_bridge_real_wasm_compare_and_branch_matches_interpreter() {
        for rax in [7, 8] {
            differential(
                &[0x48, 0x83, 0xf8, 7, 0x75, 6, 0xb8, 42, 0, 0, 0, 0xc3],
                rax,
                2,
            );
        }
    }
    fn observed_je(rax: u64, next: u64, flags: u64) {
        let (mut state, memory) = machine(
            &[
                0x48, 0x83, 0xf8, 7, 0x74, 6, 0xb8, 42, 0, 0, 0, 0xc3, 0xb8, 9, 0, 0, 0, 0xc3,
            ],
            rax,
        );
        let mut expected = state.clone();
        paludarium_cpu::run(&mut expected, &memory, 2);
        let cache = WasmCodeCache::new(Arc::new(NodeBridge));
        let (_, count) = cache.try_run_counted(&mut state, &memory).unwrap();
        assert_eq!(count, 2);
        assert_eq!(state, expected);
        assert_eq!(state.rip, GuestAddr(4096 + next));
        assert_eq!(state.rflags & 0x8d5, flags);
        assert_eq!(cache.statistics().executed_blocks, 1);
        assert_eq!(cache.statistics().executed_instructions, 2);
        paludarium_cpu::run(&mut state, &memory, 1);
        assert_eq!(state.gpr[0], if rax == 7 { 9 } else { 42 });
    }
    #[test]
    fn u14_bridge_real_wasm_je_zf1_taken_matches_fresh_native() {
        // c3df1156 native13 oracle: input7 => RAX9, arithmetic flags0x44.
        observed_je(7, 12, 0x44);
    }
    #[test]
    fn u14_bridge_real_wasm_je_zf0_not_taken_matches_fresh_native() {
        // c3df1156 native13 oracle: input8 => RAX42, arithmetic flags0.
        observed_je(8, 6, 0);
    }
    #[test]
    fn u14_bridge_unsupported_fallback_leaves_all_state_untouched() {
        let (mut state, memory) = machine(&[0x66, 0x0f, 0xef, 0xc0], 17);
        let before = state.clone();
        let cache = WasmCodeCache::new(Arc::new(NodeBridge));
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, true));
        assert_eq!(state, before);
        assert_eq!(cache.statistics().executed_blocks, 0);
    }
    #[test]
    fn u14_bridge_failure_rolls_back_cpu_state() {
        struct Failing;
        impl ExecutionBridge for Failing {
            fn execute(&self, _: u32, _: &[u8], state: &mut [u64; 18]) -> bool {
                state.fill(u64::MAX);
                false
            }
        }
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 17);
        let before = state.clone();
        let cache = WasmCodeCache::new(Arc::new(Failing));
        assert_eq!(cache.try_run_with_hint(&mut state, &memory), (None, false));
        assert_eq!(state, before);
    }
    #[test]
    fn u14_bridge_real_wasm_self_modification_recompiles() {
        let (mut state, memory) = machine(&[0xb8, 42, 0, 0, 0], 17);
        let cache = WasmCodeCache::new(Arc::new(NodeBridge));
        assert!(cache.try_run(&mut state, &memory).is_some());
        assert_eq!(state.gpr[0], 42);
        memory.write(GuestAddr(4097), &[17]).unwrap();
        state.rip = GuestAddr(4096);
        assert!(cache.try_run(&mut state, &memory).is_some());
        assert_eq!(state.gpr[0], 17);
        assert_eq!(cache.statistics().translated_blocks, 2);
    }
}
