//! Register-only subset, observed before implementation on real Linux.
use paludarium_decoder::{Condition, Mnemonic, Operand, Register, RepPrefix, decode};
use paludarium_types::GuestAddr;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Arithmetic {
    Add,
    Sub,
    Compare,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Operation {
    Move {
        register: u8,
        value: u64,
    },
    Arithmetic {
        kind: Arithmetic,
        register: u8,
        value: u64,
    },
    Branch {
        equal: bool,
        target: u64,
        fallthrough: u64,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Block {
    pub entry: u64,
    pub end: u64,
    pub operations: Vec<Operation>,
}

pub(crate) fn operation(instruction: &paludarium_decoder::Instruction) -> Option<Operation> {
    if instruction.lock || instruction.rep != RepPrefix::None {
        return None;
    }
    Some(
        match (
            instruction.mnemonic,
            instruction.operand(0),
            instruction.operand(1),
        ) {
            (
                Mnemonic::Mov,
                Some(Operand::Register(Register::Gpr { index, size: 4 | 8 })),
                Some(Operand::Immediate(value)),
            ) => {
                if index >= 16 {
                    return None;
                }
                Operation::Move {
                    register: index,
                    value: if instruction.operand(0).is_some_and(|o| {
                        matches!(o, Operand::Register(Register::Gpr { size: 4, .. }))
                    }) {
                        value & 0xffff_ffff
                    } else {
                        value
                    },
                }
            }
            (
                mnemonic @ (Mnemonic::Add | Mnemonic::Sub | Mnemonic::Cmp),
                Some(Operand::Register(Register::Gpr { index, size: 8 })),
                Some(Operand::Immediate(value)),
            ) => {
                if index >= 16 {
                    return None;
                }
                let kind = match mnemonic {
                    Mnemonic::Add => Arithmetic::Add,
                    Mnemonic::Sub => Arithmetic::Sub,
                    _ => Arithmetic::Compare,
                };
                Operation::Arithmetic {
                    kind,
                    register: index,
                    value,
                }
            }
            (
                Mnemonic::Jcc(condition @ (Condition::E | Condition::Ne)),
                Some(Operand::Branch(target)),
                None,
            ) => Operation::Branch {
                equal: condition == Condition::E,
                target: target.0,
                fallthrough: instruction.next_rip().0,
            },
            _ => return None,
        },
    )
}

pub(crate) fn extract(bytes: &[u8], entry: u64) -> Option<Block> {
    let mut block = Block {
        entry,
        end: entry,
        operations: Vec::new(),
    };
    let mut offset = 0;
    while offset < bytes.len() && block.operations.len() < 64 {
        let Ok(instruction) = decode(&bytes[offset..], GuestAddr(block.end)) else {
            break;
        };
        let Some(operation) = operation(&instruction) else {
            break;
        };
        offset += usize::from(instruction.len);
        block.end = block.end.checked_add(u64::from(instruction.len))?;
        block.operations.push(operation);
        if matches!(operation, Operation::Branch { .. }) {
            break;
        }
    }
    if block.operations.is_empty() {
        None
    } else {
        Some(block)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn u14_block_extracts_observed_mov64() {
        let block = extract(
            &[
                0x48, 0xb8, 0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 1, 0xc3,
            ],
            4096,
        )
        .unwrap();
        assert_eq!(
            block.operations,
            [Operation::Move {
                register: 0,
                value: 0x0123_4567_89ab_cdef
            }]
        );
        assert_eq!(block.end, 4106);
    }
    #[test]
    fn u14_block_stops_before_guest_memory() {
        assert!(extract(&[0x48, 0x8b, 7], 4096).is_none());
        let block = extract(&[0xb8, 42, 0, 0, 0, 0x48, 0x8b, 7], 4096).unwrap();
        assert_eq!(block.end, 4101);
    }
    #[test]
    fn u14_block_stops_before_syscall() {
        assert!(extract(&[0x0f, 5], 4096).is_none());
        assert_eq!(
            extract(&[0xb8, 42, 0, 0, 0, 0x0f, 5], 4096).unwrap().end,
            4101
        );
    }
    #[test]
    fn u14_block_rejects_partial_decode() {
        assert!(extract(&[0x48, 0xb8, 1], 4096).is_none());
    }
    #[test]
    fn u14_block_observed_arithmetic_and_branch_terminate_block() {
        let block = extract(&[0x48, 0x83, 0xf8, 7, 0x75, 6, 0xb8, 42, 0, 0, 0], 4096).unwrap();
        assert_eq!(block.operations.len(), 2);
        assert_eq!(
            block.operations[1],
            Operation::Branch {
                equal: false,
                target: 4108,
                fallthrough: 4102
            }
        );
    }
    #[test]
    fn u14_block_bounds_instruction_count() {
        let code = [0xb8, 42, 0, 0, 0].repeat(100);
        let block = extract(&code, 4096).unwrap();
        assert_eq!(block.operations.len(), 64);
        assert_eq!(block.end - block.entry, 320);
    }
    #[test]
    fn u14_block_unsupported_sse_is_clean_fallback() {
        assert!(extract(&[0x66, 0x0f, 0xef, 0xc0], 4096).is_none());
    }

    #[test]
    fn u14_block_saved_jit_compile_crash_translates_without_panic() {
        // Original jit_compile crash 4dabc170d4fa7cd3…: eight-byte RIP
        // header followed by decoder input. This finite regression checks
        // the saved input, not a replacement for the sanitizer campaign.
        let input = [
            0x00, 0xe1, 0x00, 0xe1, 0xe1, 0x4a, 0x4a, 0xe1, 0x4a, 0x48, 0x05, 0xff, 0x4a, 0x4a,
            0xe1, 0x4a, 0x48, 0x05, 0x6e, 0x3b, 0x27, 0x4a, 0x4a, 0x05, 0xff, 0x93, 0x3f, 0x93,
            0x93, 0x93, 0x93, 0x93,
        ];
        let rip = u64::from_le_bytes(input[..8].try_into().unwrap());
        for prefix in 0..16 {
            let mut bytes = vec![0; prefix];
            bytes.extend_from_slice(&input[8..]);
            let block = extract(&bytes[prefix..], rip).unwrap();
            let wasm = crate::emit::emit(&block).unwrap();
            assert!(wasm.starts_with(b"\0asm\x01\0\0\0"));
            assert!(wasm.len() <= 65536);
        }
    }
}
