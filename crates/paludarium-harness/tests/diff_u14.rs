//! Fresh x86-64 Linux instruction oracle against interpreter and real wasm JIT.
#![allow(clippy::unwrap_used, clippy::expect_used, clippy::panic)]
#![cfg(all(target_os = "linux", target_arch = "x86_64"))]

use paludarium_cpu::{CpuState, reg};
use paludarium_jit::{CodeCache, ExecutionBridge, WasmCodeCache};
use paludarium_mmu::{AddressSpace, MappingKind, Prot};
use paludarium_types::{ExitReason, GuestAddr};
use std::{
    io::Write,
    process::{Command, Stdio},
    sync::Arc,
};

struct NodeBridge;
impl ExecutionBridge for NodeBridge {
    fn execute(&self, _: u32, code: &[u8], state: &mut [u64; 18]) -> bool {
        let script = "import{readFileSync}from'node:fs';const [code,values]=readFileSync(0,'utf8').trim().split('\\n');const memory=new WebAssembly.Memory({initial:1,maximum:65536,shared:true});const state=new BigUint64Array(memory.buffer,64,18);state.set(values.split(',').map(BigInt));const instance=new WebAssembly.Instance(new WebAssembly.Module(Buffer.from(code,'hex')),{env:{memory}});if(instance.exports.run(64)!==0)process.exit(1);console.log(Array.from(state,String).join(','));";
        let mut child =
            Command::new(std::env::var("PALUDARIUM_TEST_NODE").expect("actual Node executable"))
                .args(["--input-type=module", "-e", script])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spawn()
                .unwrap();
        let hex: String = code.iter().map(|byte| format!("{byte:02x}")).collect();
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
        let values = String::from_utf8(output.stdout)
            .unwrap()
            .trim()
            .split(',')
            .map(|value| value.parse::<u64>().unwrap())
            .collect::<Vec<_>>();
        state.copy_from_slice(&values);
        true
    }
}

fn field<'a>(row: &'a str, key: &str) -> &'a str {
    let prefix = format!("\"{key}\":\"");
    row.split_once(&prefix)
        .unwrap()
        .1
        .split('"')
        .next()
        .unwrap()
}
fn number(row: &str, key: &str) -> u64 {
    u64::from_str_radix(field(row, key), 16).unwrap()
}

fn execute(
    code: &[u8],
    input: u64,
    address: u64,
    fault: bool,
    jit: bool,
) -> (CpuState, AddressSpace, i32, u64) {
    let mut memory = AddressSpace::new();
    memory
        .map(
            Some(GuestAddr(4096)),
            8192,
            Prot::from_bits(7).unwrap(),
            MappingKind::Anonymous,
        )
        .unwrap();
    memory.write_initial(GuestAddr(address), code).unwrap();
    if !fault {
        memory
            .map(
                Some(GuestAddr(0x10000)),
                4096,
                Prot::READ_WRITE,
                MappingKind::Anonymous,
            )
            .unwrap();
    }
    let mut state = CpuState::new(GuestAddr(address), GuestAddr(0));
    state.gpr[reg::RAX] = input;
    state.gpr[reg::RDI] = 0x10000;
    let cache = WasmCodeCache::new(Arc::new(NodeBridge));
    let mut signal = 0;
    // Stop before RET, matching native values immediately before its return.
    for _ in 0..64 {
        let mut byte = [0];
        memory.fetch(state.rip, &mut byte).unwrap();
        if byte[0] == 0xc3 {
            break;
        }
        let reason = if jit {
            cache
                .try_run(&mut state, &memory)
                .unwrap_or_else(|| paludarium_cpu::run(&mut state, &memory, 1))
        } else {
            paludarium_cpu::run(&mut state, &memory, 1)
        };
        match reason {
            ExitReason::BudgetExhausted { .. } => {}
            ExitReason::PageFault { .. } => {
                signal = 11;
                break;
            }
            ExitReason::ArithmeticFault { .. } => {
                signal = 8;
                break;
            }
            other => panic!("unexpected instruction exit: {other:?}"),
        }
    }
    (state, memory, signal, cache.statistics().executed_blocks)
}

#[test]
fn u14_fresh_linux_instruction_differential() {
    if std::env::var_os("PALUDARIUM_U14_INSTRUCTION_CHILD").is_none() {
        assert!(
            Command::new("python3")
                .arg(
                    paludarium_harness::workspace_root()
                        .join("tests/guests/u14/instruction-supervisor.py")
                )
                .arg(std::env::current_exe().unwrap())
                .status()
                .unwrap()
                .success()
        );
        return;
    }
    {
        let root = paludarium_harness::workspace_root();
        let directory = paludarium_harness::guest_dir().join("u14-instructions");
        std::fs::create_dir_all(&directory).unwrap();
        let binary = directory.join("oracle");
        assert!(
            Command::new("cc")
                .args(["-O2", "-Wall", "-Wextra", "-Werror"])
                .arg(root.join("tests/guests/u14/native.c"))
                .arg("-o")
                .arg(&binary)
                .status()
                .unwrap()
                .success()
        );
        let report = directory.join("observations.json");
        assert!(
            Command::new("python3")
                .arg(root.join("scripts/u14-native-first.py"))
                .arg("--binary")
                .arg(&binary)
                .arg("--output")
                .arg(&report)
                .status()
                .unwrap()
                .success()
        );
        // Parse only the native generator's original stdout; Python checks the
        // complete ordered schema and hashes before this comparison.
        let output = Command::new("python3")
            .args([
                "-c",
                "import json,sys;print(json.load(open(sys.argv[1]))['stdout'],end='')",
            ])
            .arg(&report)
            .output()
            .unwrap();
        assert!(output.status.success());
        let native = String::from_utf8(output.stdout).unwrap();
        let move64 = [
            0x48, 0xb8, 0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 1, 0xc3,
        ];
        let branch = [
            0x48, 0x83, 0xf8, 7, 0x75, 6, 0xb8, 42, 0, 0, 0, 0xc3, 0xb8, 9, 0, 0, 0, 0xc3,
        ];
        let cases: [(&str, &[u8], u64, bool); 11] = [
            ("move64", &move64, 0, true),
            ("add64-carry", &[0x48, 0x83, 0xc0, 1, 0xc3], u64::MAX, true),
            (
                "sub64-overflow",
                &[0x48, 0x83, 0xe8, 1, 0xc3],
                1 << 63,
                true,
            ),
            ("branch-taken", &branch, 7, true),
            ("branch-not-taken", &branch, 8, true),
            (
                "memory-read-write",
                &[0x48, 0x89, 7, 0x48, 0x83, 7, 5, 0x48, 0x8b, 7, 0xc3],
                11,
                false,
            ),
            (
                "unsupported-sse-fallback",
                &[0x66, 0x0f, 0xef, 0xc0, 0x66, 0x48, 0x0f, 0x7e, 0xc0, 0xc3],
                17,
                false,
            ),
            ("unmapped-data-fault", &[0x48, 0x8b, 7, 0xc3], 0, false),
            (
                "division-fault",
                &[0x31, 0xd2, 0x31, 0xc9, 0x48, 0xf7, 0xf1, 0xc3],
                1,
                false,
            ),
            ("self-modifying-code", &move64, 0, true),
            ("cross-page-instruction", &move64, 0, true),
        ];
        assert_eq!(native.lines().count(), cases.len());
        for ((name, code, input, translated), row) in cases.into_iter().zip(native.lines()) {
            assert_eq!(field(row, "name"), name);
            let address = if name == "cross-page-instruction" {
                8189
            } else {
                4096
            };
            let interpreter = execute(code, input, address, name == "unmapped-data-fault", false);
            let actual = execute(code, input, address, name == "unmapped-data-fault", true);
            assert_eq!(actual.0, interpreter.0, "{name}: interpreter/JIT state");
            assert_eq!(actual.2, interpreter.2, "{name}: interpreter/JIT fault");
            if translated {
                assert!(actual.3 > 0, "{name}: real translation execution required");
            }
            if actual.2 != 0 {
                assert!(
                    row.contains(&format!("\"signal\":{}", actual.2)),
                    "{name}: native signal"
                );
            } else {
                assert_eq!(
                    actual.0.gpr[0],
                    number(row, "first_rax"),
                    "{name}: native first RAX"
                );
                assert_eq!(
                    actual.0.rflags & number(row, "flag_mask"),
                    number(row, "flags"),
                    "{name}: native flags"
                );
                assert_eq!(
                    actual.1.read_u64(GuestAddr(0x10000)).unwrap(),
                    number(row, "memory"),
                    "{name}: native memory"
                );
                if name == "self-modifying-code" {
                    let cache = WasmCodeCache::new(Arc::new(NodeBridge));
                    let mut state = actual.0;
                    state.rip = GuestAddr(address);
                    assert!(cache.try_run(&mut state, &actual.1).is_some());
                    actual
                        .1
                        .write(GuestAddr(address + 2), &[42, 0, 0, 0, 0, 0, 0, 0])
                        .unwrap();
                    state.rip = GuestAddr(address);
                    assert!(cache.try_run(&mut state, &actual.1).is_some());
                    assert_eq!(state.gpr[0], number(row, "rax"));
                    assert_eq!(cache.statistics().translated_blocks, 2);
                }
            }
            println!("{name}: native/interpreter/real-wasm match");
        }
    }
}
