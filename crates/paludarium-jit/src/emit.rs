//! Small deterministic wasm encoder; guest memory is never imported as pointers.
use crate::block::{Arithmetic, Block, Operation};

fn unsigned(output: &mut Vec<u8>, mut value: usize) {
    loop {
        let byte = (value & 127) as u8;
        value >>= 7;
        output.push(byte | if value == 0 { 0 } else { 128 });
        if value == 0 {
            break;
        }
    }
}
fn constant(output: &mut Vec<u8>, value: u64) {
    output.push(0x42);
    let mut value = value as i64;
    loop {
        let byte = (value & 127) as u8;
        value >>= 7;
        let last = (value == 0 && byte & 64 == 0) || (value == -1 && byte & 64 != 0);
        output.push(byte | if last { 0 } else { 128 });
        if last {
            break;
        }
    }
}
fn section(output: &mut Vec<u8>, id: u8, bytes: &[u8]) {
    output.push(id);
    unsigned(output, bytes.len());
    output.extend(bytes);
}
fn get(output: &mut Vec<u8>, local: u8) {
    output.extend([0x20, local]);
}
fn set(output: &mut Vec<u8>, local: u8) {
    output.extend([0x21, local]);
}
fn load(output: &mut Vec<u8>, index: u8) {
    get(output, 0);
    output.extend([0x29, 3]);
    unsigned(output, usize::from(index) * 8);
}
fn store(output: &mut Vec<u8>, index: u8) {
    output.extend([0x37, 3]);
    unsigned(output, usize::from(index) * 8);
}
fn flag(output: &mut Vec<u8>, bit: u8, expression: impl FnOnce(&mut Vec<u8>)) {
    get(output, 4);
    expression(output);
    output.push(0xad); // i64.extend_i32_u
    constant(output, u64::from(bit));
    output.extend([0x86, 0x84]); // shl, or
    set(output, 4);
}
fn arithmetic(output: &mut Vec<u8>, kind: Arithmetic, register: u8, value: u64) {
    load(output, register);
    set(output, 1);
    constant(output, value);
    set(output, 2);
    get(output, 1);
    get(output, 2);
    output.push(if kind == Arithmetic::Add { 0x7c } else { 0x7d });
    set(output, 3);
    load(output, 16);
    constant(output, !0x8d5);
    output.push(0x83);
    set(output, 4);
    flag(output, 0, |out| {
        if kind == Arithmetic::Add {
            get(out, 3);
            get(out, 1);
        } else {
            get(out, 1);
            get(out, 2);
        }
        out.push(0x54);
    });
    flag(output, 2, |out| {
        get(out, 3);
        constant(out, 255);
        out.extend([0x83, 0x7b]);
        constant(out, 1);
        out.extend([0x83, 0x50]);
    });
    flag(output, 4, |out| {
        get(out, 1);
        get(out, 2);
        out.push(0x85);
        get(out, 3);
        out.push(0x85);
        constant(out, 16);
        out.extend([0x83, 0x50, 0x45]);
    });
    flag(output, 6, |out| {
        get(out, 3);
        out.push(0x50);
    });
    flag(output, 7, |out| {
        get(out, 3);
        constant(out, 0);
        out.push(0x53);
    });
    flag(output, 11, |out| {
        get(out, 1);
        get(out, 2);
        out.push(0x85);
        if kind == Arithmetic::Add {
            constant(out, u64::MAX);
            out.push(0x85);
        }
        get(out, 1);
        get(out, 3);
        out.extend([0x85, 0x83]);
        constant(out, 0);
        out.push(0x53);
    });
    get(output, 0);
    get(output, 4);
    store(output, 16);
    if kind != Arithmetic::Compare {
        get(output, 0);
        get(output, 3);
        store(output, register);
    }
}

pub(crate) fn emit(block: &Block) -> Option<Vec<u8>> {
    if block.operations.is_empty() || block.operations.len() > 64 {
        return None;
    }
    let mut output = vec![0, 97, 115, 109, 1, 0, 0, 0];
    section(&mut output, 1, &[1, 0x60, 1, 0x7f, 1, 0x7f]);
    // env.memory: shared memory, minimum 1 and maximum 65536 pages. The
    // production shared Rust memory must satisfy these limits.
    section(
        &mut output,
        2,
        &[
            1, 3, b'e', b'n', b'v', 6, b'm', b'e', b'm', b'o', b'r', b'y', 2, 3, 1, 0x80, 0x80, 4,
        ],
    );
    section(&mut output, 3, &[1, 0]);
    section(&mut output, 7, &[1, 3, b'r', b'u', b'n', 0, 0]);
    let mut body = vec![1, 4, 0x7e]; // Four i64 locals; local 0 is state pointer.
    for operation in &block.operations {
        match *operation {
            Operation::Move { register, value } => {
                if register >= 16 {
                    return None;
                }
                get(&mut body, 0);
                constant(&mut body, value);
                store(&mut body, register);
            }
            Operation::Arithmetic {
                kind,
                register,
                value,
            } => {
                if register >= 16 {
                    return None;
                }
                arithmetic(&mut body, kind, register, value);
            }
            Operation::Branch {
                equal,
                target,
                fallthrough,
            } => {
                get(&mut body, 0);
                constant(&mut body, target);
                constant(&mut body, fallthrough);
                load(&mut body, 16);
                constant(&mut body, 64);
                body.extend([0x83, 0x50]);
                if equal {
                    body.push(0x45);
                }
                body.push(0x1b);
                store(&mut body, 17);
            }
        }
    }
    if !matches!(block.operations.last(), Some(Operation::Branch { .. })) {
        get(&mut body, 0);
        constant(&mut body, block.end);
        store(&mut body, 17);
    }
    body.extend([0x41, 0, 0x0b]);
    let mut code = vec![1];
    unsigned(&mut code, body.len());
    code.extend(body);
    section(&mut output, 10, &code);
    Some(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn block(operation: Operation) -> Block {
        Block {
            entry: 4096,
            end: 4106,
            operations: vec![operation],
        }
    }
    #[test]
    fn u14_emit_mov_module_has_real_wasm_header() {
        assert_eq!(
            &emit(&block(Operation::Move {
                register: 0,
                value: 42
            }))
            .unwrap()[..8],
            b"\0asm\x01\0\0\0"
        );
    }
    #[test]
    fn u14_emit_signed_integer_extremes_are_bounded() {
        for value in [0, 63, 64, 127, 128, u64::MAX, 1 << 63] {
            let mut bytes = Vec::new();
            constant(&mut bytes, value);
            assert!(bytes.len() <= 11);
            assert_eq!(bytes.last().unwrap() & 128, 0);
        }
    }
    #[test]
    fn u14_emit_rejects_empty_and_unbounded_blocks() {
        let mut block = block(Operation::Move {
            register: 0,
            value: 42,
        });
        block.operations.clear();
        assert!(emit(&block).is_none());
        block.operations = vec![
            Operation::Move {
                register: 0,
                value: 42
            };
            65
        ];
        assert!(emit(&block).is_none());
    }
    #[test]
    fn u14_emit_rejects_invalid_register_scratch_offsets() {
        assert!(
            emit(&block(Operation::Move {
                register: 16,
                value: 42
            }))
            .is_none()
        );
    }
    #[test]
    fn u14_emit_add_and_sub_are_distinct_modules() {
        let add = emit(&block(Operation::Arithmetic {
            kind: Arithmetic::Add,
            register: 0,
            value: 1,
        }))
        .unwrap();
        let sub = emit(&block(Operation::Arithmetic {
            kind: Arithmetic::Sub,
            register: 0,
            value: 1,
        }))
        .unwrap();
        assert_ne!(add, sub);
    }
    #[test]
    fn u14_emit_conditional_branch_preserves_two_targets() {
        let equal = emit(&block(Operation::Branch {
            equal: true,
            target: 8192,
            fallthrough: 4098,
        }))
        .unwrap();
        let unequal = emit(&block(Operation::Branch {
            equal: false,
            target: 8192,
            fallthrough: 4098,
        }))
        .unwrap();
        assert_ne!(equal, unequal);
    }
    #[test]
    fn u14_emit_is_deterministic_for_worker_compilation() {
        let block = block(Operation::Move {
            register: 0,
            value: 42,
        });
        assert_eq!(emit(&block), emit(&block));
    }
}
