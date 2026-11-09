//! Instruction forms worked out when they are decoded.
//!
//! [`Fast::of`] picks the operation of the most frequent register, memory and
//! branch forms once, so that running them needs neither the mnemonic `match`
//! of [`super::execute`] nor the generic operand handling. Each form means
//! exactly what [`super::execute`] does with it. A form changes the state only
//! after the last thing that can fail: when it fails, nothing has changed, and
//! the instruction runs again in [`super::execute`], which gives the fault.

use paludarium_decoder::{
    Condition, Instruction, MemoryOperand, Mnemonic, Operand, Register, RepPrefix,
};
use paludarium_mmu::AddressSpace;
use paludarium_types::GuestAddr;

use super::{Exec, Result};
use crate::alu::{self, size_mask};
use crate::state::{CpuState, flag};

/// An arithmetic or logic operation of [`Fast`].
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Alu {
    Add,
    Sub,
    And,
    Or,
    Xor,
    Cmp,
    Test,
}

impl Alu {
    fn of(m: Mnemonic) -> Option<Self> {
        Some(match m {
            Mnemonic::Add => Self::Add,
            Mnemonic::Sub => Self::Sub,
            Mnemonic::And => Self::And,
            Mnemonic::Or => Self::Or,
            Mnemonic::Xor => Self::Xor,
            Mnemonic::Cmp => Self::Cmp,
            Mnemonic::Test => Self::Test,
            _ => return None,
        })
    }

    fn writes(self) -> bool {
        !matches!(self, Self::Cmp | Self::Test)
    }

    /// The result and the status flags, as [`Exec::alu`] has them.
    #[inline]
    fn apply(self, a: u64, b: u64, size: u8) -> (u64, u64) {
        match self {
            Self::Add => alu::add(a, b, false, size),
            Self::Sub | Self::Cmp => alu::sub(a, b, false, size),
            Self::And | Self::Test => (a & b, alu::logic(a & b, size)),
            Self::Or => (a | b, alu::logic(a | b, size)),
            Self::Xor => (a ^ b, alu::logic(a ^ b, size)),
        }
    }
}

/// A second operand of [`Fast`]: a register or an immediate.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Source {
    Register(Register),
    Immediate(u64),
}

/// The operation of a decoded instruction, if it has one of these forms.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Fast {
    /// Every other form, run by [`super::execute`].
    None,
    Nop,
    /// `mov r, r/imm`.
    Move {
        dst: Register,
        src: Source,
    },
    /// `mov r, [m]`.
    Load {
        dst: Register,
        mem: MemoryOperand,
    },
    /// `mov [m], r/imm`.
    Store {
        mem: MemoryOperand,
        src: Source,
    },
    /// `movzx r, [m]`.
    LoadZeroExtended {
        dst: Register,
        mem: MemoryOperand,
    },
    /// `lea r64, [m]`.
    Lea {
        dst: u8,
        mem: MemoryOperand,
    },
    /// `push r64`.
    Push(u8),
    /// `pop r64`.
    Pop(u8),
    Jcc {
        condition: Condition,
        target: u64,
    },
    Jmp(u64),
    Call(u64),
    /// `ret` without an immediate.
    Ret,
    /// `op r, r/imm`.
    Alu {
        op: Alu,
        dst: Register,
        src: Source,
    },
    /// `cmp`/`test [m], r/imm`.
    Compare {
        op: Alu,
        mem: MemoryOperand,
        src: Source,
    },
}

/// A general-purpose register that is not one of the high bytes.
fn gpr(o: Option<Operand>) -> Option<Register> {
    match o {
        Some(Operand::Register(r @ Register::Gpr { .. })) => Some(r),
        _ => None,
    }
}

fn gpr64(o: Option<Operand>) -> Option<u8> {
    match o {
        Some(Operand::Register(Register::Gpr { index, size: 8 })) => Some(index & 15),
        _ => None,
    }
}

/// A register of `size` bytes, or an immediate.
fn source(o: Option<Operand>, size: u8) -> Option<Source> {
    match o {
        Some(Operand::Register(r @ Register::Gpr { size: s, .. })) if s == size => {
            Some(Source::Register(r))
        }
        Some(Operand::Immediate(v)) => Some(Source::Immediate(v)),
        _ => None,
    }
}

fn memory(o: Option<Operand>) -> Option<MemoryOperand> {
    match o {
        Some(Operand::Memory(m)) => Some(m),
        _ => None,
    }
}

fn branch(o: Option<Operand>) -> Option<u64> {
    match o {
        Some(Operand::Branch(t)) => Some(t.0),
        _ => None,
    }
}

impl Fast {
    /// The form of `i`, or [`Fast::None`].
    pub(crate) fn of(i: &Instruction) -> Self {
        if i.lock || i.rep != RepPrefix::None {
            return Self::None;
        }
        Self::form(i).unwrap_or(Self::None)
    }

    fn form(i: &Instruction) -> Option<Self> {
        let (a, b) = (i.operand(0), i.operand(1));
        if i.operand(2).is_some() {
            return None;
        }
        Some(match i.mnemonic {
            Mnemonic::Nop | Mnemonic::Endbr64 => Self::Nop,
            Mnemonic::Mov => {
                if let Some(dst) = gpr(a) {
                    match memory(b) {
                        Some(mem) if mem.size == dst.size() => Self::Load { dst, mem },
                        Some(_) => return None,
                        None => Self::Move {
                            dst,
                            src: source(b, dst.size())?,
                        },
                    }
                } else {
                    let mem = memory(a)?;
                    Self::Store {
                        mem,
                        src: source(b, mem.size)?,
                    }
                }
            }
            Mnemonic::Movzx => {
                let dst = gpr(a)?;
                let mem = memory(b)?;
                if !matches!(mem.size, 1 | 2) || dst.size() <= mem.size {
                    return None;
                }
                Self::LoadZeroExtended { dst, mem }
            }
            Mnemonic::Lea => Self::Lea {
                dst: gpr64(a)?,
                mem: memory(b)?,
            },
            Mnemonic::Push if i.implicit_size == 8 && b.is_none() => Self::Push(gpr64(a)?),
            Mnemonic::Pop if i.implicit_size == 8 && b.is_none() => Self::Pop(gpr64(a)?),
            Mnemonic::Jcc(condition) => Self::Jcc {
                condition,
                target: branch(a)?,
            },
            Mnemonic::Jmp => Self::Jmp(branch(a)?),
            Mnemonic::Call => Self::Call(branch(a)?),
            Mnemonic::Ret if a.is_none() => Self::Ret,
            m => {
                let op = Alu::of(m)?;
                if let Some(dst) = gpr(a) {
                    Self::Alu {
                        op,
                        dst,
                        src: source(b, dst.size())?,
                    }
                } else if op.writes() {
                    return None;
                } else {
                    let mem = memory(a)?;
                    Self::Compare {
                        op,
                        mem,
                        src: source(b, mem.size)?,
                    }
                }
            }
        })
    }
}

impl Exec<'_> {
    #[inline]
    fn source(&self, src: Source, size: u8) -> u64 {
        match src {
            Source::Register(r) => self.read_reg(r) & size_mask(size),
            Source::Immediate(v) => v & size_mask(size),
        }
    }
}

/// Runs `f`, the form of `i`, which is not [`Fast::None`]. When it fails, the
/// state is as it was.
#[inline]
pub(crate) fn execute(
    s: &mut CpuState,
    mem: &AddressSpace,
    i: &Instruction,
    f: &Fast,
) -> Result<()> {
    let next = i.next_rip().0;
    let mut x = Exec { s, mem, i };
    let target = match *f {
        Fast::None | Fast::Nop => next,
        Fast::Move { dst, src } => {
            let v = x.source(src, dst.size());
            x.write_reg(dst, v);
            next
        }
        Fast::Load { dst, mem } => {
            let v = x.load(x.linear(&mem), mem.size)?;
            x.write_reg(dst, v & size_mask(dst.size()));
            next
        }
        Fast::Store { mem, src } => {
            let v = x.source(src, mem.size);
            x.store(x.linear(&mem), mem.size, v)?;
            next
        }
        Fast::LoadZeroExtended { dst, mem } => {
            let v = x.load(x.linear(&mem), mem.size)?;
            x.write_reg(dst, v & size_mask(dst.size()));
            next
        }
        Fast::Lea { dst, mem } => {
            x.s.gpr[usize::from(dst)] = x.address(&mem).0;
            next
        }
        Fast::Push(r) => {
            let v = x.s.gpr[usize::from(r)];
            x.push(v, 8)?;
            next
        }
        Fast::Pop(r) => {
            let v = x.pop(8)?;
            x.s.gpr[usize::from(r)] = v;
            next
        }
        Fast::Jcc { condition, target } => {
            if alu::condition(x.s.rflags, condition) {
                target
            } else {
                next
            }
        }
        Fast::Jmp(target) => target,
        Fast::Call(target) => {
            x.push(next, 8)?;
            target
        }
        Fast::Ret => x.pop(8)?,
        Fast::Alu { op, dst, src } => {
            let size = dst.size();
            let b = x.source(src, size);
            let a = x.read_reg(dst) & size_mask(size);
            let (r, flags) = op.apply(a, b, size);
            if op.writes() {
                x.write_reg(dst, r & size_mask(size));
            }
            x.set_status(flag::STATUS, flags);
            next
        }
        Fast::Compare { op, mem, src } => {
            let size = mem.size;
            let b = x.source(src, size);
            let a = x.load(x.linear(&mem), size)?;
            let (_, flags) = op.apply(a, b, size);
            x.set_status(flag::STATUS, flags);
            next
        }
    };
    x.s.rip = GuestAddr(target);
    Ok(())
}
