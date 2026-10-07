//! Execution of one decoded instruction.

use paludarium_decoder::{
    Instruction, MemoryOperand, Mnemonic, Operand, Register, RepPrefix, Segment,
};
use paludarium_mmu::{AddressSpace, AtomicOp, AtomicWidth, Fault};
use paludarium_types::GuestAddr;

use crate::alu::{self, ShiftKind, sign_extend, size_mask};
use crate::state::{CpuState, flag, reg};

/// Why executing an instruction did not simply continue.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Stop {
    Fault(Fault),
    /// Not implemented / not valid in this form (SIGILL).
    Invalid,
    Halt,
    GeneralProtection,
    ArithmeticFault,
    /// `syscall` executed; the state already points past it.
    Syscall,
}

impl From<Fault> for Stop {
    fn from(f: Fault) -> Self {
        Stop::Fault(f)
    }
}

type Result<T> = core::result::Result<T, Stop>;

fn atomic_width(size: u8) -> Result<AtomicWidth> {
    match size {
        1 => Ok(AtomicWidth::W8),
        2 => Ok(AtomicWidth::W16),
        4 => Ok(AtomicWidth::W32),
        8 => Ok(AtomicWidth::W64),
        16 => Ok(AtomicWidth::W128),
        _ => Err(Stop::Invalid),
    }
}

/// Upper bound of `rep` iterations per step, so that a huge `rcx` cannot
/// keep one step running forever (the instruction is resumed next step, as
/// on hardware where `rep` is interruptible).
const REP_CHUNK: u64 = 4096;

pub(crate) fn is_comparison_string(m: Mnemonic) -> bool {
    matches!(
        m,
        Mnemonic::Cmpsb
            | Mnemonic::Cmpsw
            | Mnemonic::Cmpsd
            | Mnemonic::Cmpsq
            | Mnemonic::Scasb
            | Mnemonic::Scasw
            | Mnemonic::Scasd
            | Mnemonic::Scasq
    )
}
pub(crate) fn is_string(m: Mnemonic) -> bool {
    is_comparison_string(m)
        || matches!(
            m,
            Mnemonic::Movsb
                | Mnemonic::Movsw
                | Mnemonic::Movsd
                | Mnemonic::Movsq
                | Mnemonic::Stosb
                | Mnemonic::Stosw
                | Mnemonic::Stosd
                | Mnemonic::Stosq
                | Mnemonic::Lodsb
                | Mnemonic::Lodsw
                | Mnemonic::Lodsd
                | Mnemonic::Lodsq
        )
}

struct Exec<'a> {
    s: &'a mut CpuState,
    mem: &'a AddressSpace,
    i: &'a Instruction,
}

fn op(i: &Instruction, n: usize) -> Result<Operand> {
    i.operand(n).ok_or(Stop::Invalid)
}

impl Exec<'_> {
    fn read_reg(&self, r: Register) -> u64 {
        match r {
            Register::Gpr { index, size } => self.s.gpr[usize::from(index & 15)] & size_mask(size),
            Register::GprHigh8 { index } => (self.s.gpr[usize::from(index & 3)] >> 8) & 0xff,
            Register::Xmm(n) => self.s.xmm[usize::from(n & 15)] as u64,
        }
    }

    fn write_reg(&mut self, r: Register, value: u64) {
        match r {
            Register::Gpr { index, size } => {
                let slot = &mut self.s.gpr[usize::from(index & 15)];
                *slot = match size {
                    8 => value,
                    // 32-bit writes zero the upper half.
                    4 => value & 0xffff_ffff,
                    _ => (*slot & !size_mask(size)) | (value & size_mask(size)),
                };
            }
            Register::GprHigh8 { index } => {
                let slot = &mut self.s.gpr[usize::from(index & 3)];
                *slot = (*slot & !0xff00) | ((value & 0xff) << 8);
            }
            Register::Xmm(n) => self.s.xmm[usize::from(n & 15)] = u128::from(value),
        }
    }

    fn address(&self, m: &MemoryOperand) -> GuestAddr {
        let reg_value = |r: Register| match r {
            Register::Gpr { index, size } => self.s.gpr[usize::from(index & 15)] & size_mask(size),
            _ => 0,
        };
        let mut ea = m.displacement;
        if let Some(b) = m.base {
            ea = ea.wrapping_add(reg_value(b));
        }
        if let Some(x) = m.index {
            ea = ea.wrapping_add(reg_value(x).wrapping_mul(u64::from(m.scale)));
        }
        if m.address_size_32 {
            ea &= 0xffff_ffff;
        }
        GuestAddr(ea)
    }

    fn linear(&self, m: &MemoryOperand) -> GuestAddr {
        let ea = self.address(m);
        match m.segment {
            Segment::Fs => ea.wrapping_add(self.s.fs_base),
            Segment::Gs => ea.wrapping_add(self.s.gs_base),
            Segment::None => ea,
        }
    }

    fn load(&self, addr: GuestAddr, size: u8) -> Result<u64> {
        let mut b = [0u8; 8];
        let n = usize::from(size.min(8));
        self.mem.read(addr, &mut b[..n])?;
        Ok(u64::from_le_bytes(b))
    }

    fn store(&self, addr: GuestAddr, size: u8, value: u64) -> Result<()> {
        let n = usize::from(size.min(8));
        self.mem.write(addr, &value.to_le_bytes()[..n])?;
        Ok(())
    }

    /// Size of an operand in bytes (immediates take the size of `other`).
    fn size_of(o: Operand, other: Option<Operand>) -> u8 {
        match o {
            Operand::Register(r) => r.size(),
            Operand::Memory(m) => m.size,
            Operand::Immediate(_) | Operand::Branch(_) => match other {
                Some(x) => Self::size_of(x, None),
                None => 8,
            },
        }
    }

    fn read(&self, o: Operand, size: u8) -> Result<u64> {
        match o {
            Operand::Register(r) => Ok(self.read_reg(r) & size_mask(size)),
            Operand::Immediate(v) => Ok(v & size_mask(size)),
            Operand::Memory(m) => self.load(self.linear(&m), size),
            Operand::Branch(t) => Ok(t.0),
        }
    }

    fn write(&mut self, o: Operand, size: u8, value: u64) -> Result<()> {
        match o {
            Operand::Register(r) => {
                self.write_reg(r, value & size_mask(size));
                Ok(())
            }
            Operand::Memory(m) => self.store(self.linear(&m), size, value),
            Operand::Immediate(_) | Operand::Branch(_) => Err(Stop::Invalid),
        }
    }

    fn set_status(&mut self, update: u64, value: u64) {
        self.s.rflags = (self.s.rflags & !update) | (value & update);
    }

    fn push(&mut self, value: u64, size: u8) -> Result<()> {
        let rsp = self.s.gpr[reg::RSP].wrapping_sub(u64::from(size));
        self.store(GuestAddr(rsp), size, value)?;
        self.s.gpr[reg::RSP] = rsp;
        Ok(())
    }

    fn pop(&mut self, size: u8) -> Result<u64> {
        let rsp = self.s.gpr[reg::RSP];
        let value = self.load(GuestAddr(rsp), size)?;
        self.s.gpr[reg::RSP] = rsp.wrapping_add(u64::from(size));
        Ok(value)
    }

    fn enter(&mut self) -> Result<()> {
        let size = self.i.implicit_size;
        let allocation = self.read(op(self.i, 0)?, 2)?;
        let nesting = self.read(op(self.i, 1)?, 1)? & 31;
        let old_bp = self.s.gpr[reg::RBP];
        self.push(old_bp, size)?;
        let frame = self.s.gpr[reg::RSP];
        let mut cursor = old_bp;
        if nesting != 0 {
            for _ in 1..nesting {
                cursor = cursor.wrapping_sub(u64::from(size));
                // Native ENTERW retains the full chain address even when
                // decrementing crosses the low 16-bit boundary.
                let value = self.load(GuestAddr(cursor), size)?;
                self.push(value, size)?;
            }
            self.push(frame, size)?;
        }
        self.s.gpr[reg::RBP] = if size == 2 {
            (old_bp & !0xffff) | (frame & 0xffff)
        } else {
            frame
        };
        let stack = self.s.gpr[reg::RSP].wrapping_sub(allocation);
        self.mem.check_write(GuestAddr(stack), 1)?;
        self.s.gpr[reg::RSP] = stack;
        Ok(())
    }

    fn binary(&self) -> Result<(Operand, Operand, u8)> {
        let dst = op(self.i, 0)?;
        let src = op(self.i, 1)?;
        Ok((dst, src, Self::size_of(dst, None)))
    }

    fn alu(&mut self, m: Mnemonic) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let b = self.read(src, size)?;
        let cf = self.s.flag(flag::CF);
        let locked = self.i.lock && matches!(dst, Operand::Memory(_));
        let a = if locked {
            let Operand::Memory(mem) = dst else {
                return Err(Stop::Invalid);
            };
            let operation = match m {
                Mnemonic::Add => AtomicOp::Add(u128::from(b)),
                Mnemonic::Adc => AtomicOp::Add(u128::from(b) + u128::from(cf)),
                Mnemonic::Sub => AtomicOp::Sub(u128::from(b)),
                Mnemonic::Sbb => AtomicOp::Sub(u128::from(b) + u128::from(cf)),
                Mnemonic::And => AtomicOp::And(u128::from(b)),
                Mnemonic::Or => AtomicOp::Or(u128::from(b)),
                Mnemonic::Xor => AtomicOp::Xor(u128::from(b)),
                _ => return Err(Stop::Invalid),
            };
            self.mem
                .atomic(self.linear(&mem), atomic_width(size)?, operation)?
                .old as u64
        } else {
            self.read(dst, size)?
        };
        let ((r, f), writes) = match m {
            Mnemonic::Add => (alu::add(a, b, false, size), true),
            Mnemonic::Adc => (alu::add(a, b, cf, size), true),
            Mnemonic::Sub => (alu::sub(a, b, false, size), true),
            Mnemonic::Sbb => (alu::sub(a, b, cf, size), true),
            Mnemonic::Cmp => (alu::sub(a, b, false, size), false),
            Mnemonic::And => ((a & b, alu::logic(a & b, size)), true),
            Mnemonic::Or => ((a | b, alu::logic(a | b, size)), true),
            Mnemonic::Xor => ((a ^ b, alu::logic(a ^ b, size)), true),
            Mnemonic::Test => ((a & b, alu::logic(a & b, size)), false),
            _ => return Err(Stop::Invalid),
        };
        if writes && !locked {
            self.write(dst, size, r)?;
        }
        self.set_status(flag::STATUS, f);
        Ok(())
    }

    fn unary(&mut self, m: Mnemonic) -> Result<()> {
        let dst = op(self.i, 0)?;
        let size = Self::size_of(dst, None);
        let locked = self.i.lock && matches!(dst, Operand::Memory(_));
        let a = if locked {
            let Operand::Memory(mem) = dst else {
                return Err(Stop::Invalid);
            };
            let operation = match m {
                Mnemonic::Inc => AtomicOp::Add(1),
                Mnemonic::Dec => AtomicOp::Sub(1),
                Mnemonic::Neg => AtomicOp::Neg,
                Mnemonic::Not => AtomicOp::Not,
                _ => return Err(Stop::Invalid),
            };
            self.mem
                .atomic(self.linear(&mem), atomic_width(size)?, operation)?
                .old as u64
        } else {
            self.read(dst, size)?
        };
        match m {
            Mnemonic::Inc | Mnemonic::Dec => {
                let (r, f) = if m == Mnemonic::Inc {
                    alu::add(a, 1, false, size)
                } else {
                    alu::sub(a, 1, false, size)
                };
                if !locked {
                    self.write(dst, size, r)?;
                }
                self.set_status(flag::STATUS & !flag::CF, f);
            }
            Mnemonic::Neg => {
                let (r, f) = alu::sub(0, a, false, size);
                if !locked {
                    self.write(dst, size, r)?;
                }
                self.set_status(flag::STATUS, f);
            }
            Mnemonic::Not => {
                if !locked {
                    self.write(dst, size, !a)?;
                }
            }
            _ => return Err(Stop::Invalid),
        }
        Ok(())
    }

    fn shift(&mut self, kind: ShiftKind) -> Result<()> {
        let dst = op(self.i, 0)?;
        let size = Self::size_of(dst, None);
        let count = match self.i.operand(1) {
            Some(o) => self.read(o, 1)?,
            None => 1,
        };
        let a = self.read(dst, size)?;
        match alu::shift(kind, a, count, size) {
            Some((r, f)) => {
                self.write(dst, size, r)?;
                self.set_status(flag::STATUS, f);
            }
            // A zero count leaves the flags alone, but the destination is
            // still written: a 32-bit register is zero-extended.
            None => self.write(dst, size, a)?,
        }
        Ok(())
    }

    fn imul(&mut self) -> Result<()> {
        match self.i.operand_count() {
            1 => {
                let src = op(self.i, 0)?;
                let size = Self::size_of(src, None);
                let b = self.read(src, size)?;
                let a = self.s.gpr[reg::RAX] & size_mask(size);
                let full = i128::from(sign_extend(a, size) as i64)
                    * i128::from(sign_extend(b, size) as i64);
                self.write_wide(size, full as u128)?;
                let (_, overflow) = alu::imul(a, b, size);
                self.set_status(
                    flag::CF | flag::OF,
                    if overflow { flag::CF | flag::OF } else { 0 },
                );
                Ok(())
            }
            n => {
                let dst = op(self.i, 0)?;
                let size = Self::size_of(dst, None);
                let (a, b) = if n == 2 {
                    (self.read(dst, size)?, self.read(op(self.i, 1)?, size)?)
                } else {
                    (
                        self.read(op(self.i, 1)?, size)?,
                        self.read(op(self.i, 2)?, size)?,
                    )
                };
                let (r, overflow) = alu::imul(a, b, size);
                self.write(dst, size, r)?;
                self.set_status(
                    flag::CF | flag::OF,
                    if overflow { flag::CF | flag::OF } else { 0 },
                );
                Ok(())
            }
        }
    }

    /// Writes a double-width result to rdx:rax (ax for 8-bit operands).
    fn write_wide(&mut self, size: u8, value: u128) -> Result<()> {
        let bits = alu::bits(size);
        let low = value as u64 & size_mask(size);
        let high = (value >> bits) as u64 & size_mask(size);
        let rax = Register::Gpr { index: 0, size };
        if size == 1 {
            self.write_reg(Register::Gpr { index: 0, size: 2 }, (high << 8) | low);
        } else {
            self.write_reg(rax, low);
            self.write_reg(Register::Gpr { index: 2, size }, high);
        }
        Ok(())
    }

    fn mul(&mut self) -> Result<()> {
        let src = op(self.i, 0)?;
        let size = Self::size_of(src, None);
        let b = self.read(src, size)?;
        let a = self.s.gpr[reg::RAX] & size_mask(size);
        let full = u128::from(a) * u128::from(b);
        self.write_wide(size, full)?;
        let overflow = full >> alu::bits(size) != 0;
        self.set_status(
            flag::CF | flag::OF,
            if overflow { flag::CF | flag::OF } else { 0 },
        );
        Ok(())
    }

    fn divide(&mut self, signed: bool) -> Result<()> {
        let src = op(self.i, 0)?;
        let size = Self::size_of(src, None);
        let divisor = self.read(src, size)?;
        if divisor == 0 {
            return Err(Stop::ArithmeticFault);
        }
        let bits = alu::bits(size);
        let (high, low) = if size == 1 {
            let ax = self.s.gpr[reg::RAX] & 0xffff;
            (ax >> 8, ax & 0xff)
        } else {
            (
                self.s.gpr[reg::RDX] & size_mask(size),
                self.s.gpr[reg::RAX] & size_mask(size),
            )
        };
        let dividend = (u128::from(high) << bits) | u128::from(low);
        let (q, r) = if signed {
            let shift = 128 - 2 * bits;
            let n = ((dividend << shift) as i128) >> shift;
            let d = i128::from(sign_extend(divisor, size) as i64);
            let q = n.checked_div(d).ok_or(Stop::ArithmeticFault)?;
            let r = n.checked_rem(d).ok_or(Stop::ArithmeticFault)?;
            let lo = -(1i128 << (bits - 1));
            let hi = (1i128 << (bits - 1)) - 1;
            if q < lo || q > hi {
                return Err(Stop::ArithmeticFault);
            }
            (q as u64 & size_mask(size), r as u64 & size_mask(size))
        } else {
            let q = dividend / u128::from(divisor);
            if q > u128::from(size_mask(size)) {
                return Err(Stop::ArithmeticFault);
            }
            (q as u64, (dividend % u128::from(divisor)) as u64)
        };
        if size == 1 {
            self.write_reg(Register::Gpr { index: 0, size: 2 }, (r << 8) | q);
        } else {
            self.write_reg(Register::Gpr { index: 0, size }, q);
            self.write_reg(Register::Gpr { index: 2, size }, r);
        }
        Ok(())
    }

    fn bit(&mut self, mnemonic: Mnemonic) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let offset = self.read(src, size)?;
        let (dst, bit) = match (dst, src) {
            (Operand::Memory(m), Operand::Register(_)) => {
                let signed = sign_extend(offset, size) as i64;
                let width = i64::from(alu::bits(size));
                let mut adjusted = m;
                adjusted.displacement = adjusted
                    .displacement
                    .wrapping_add(signed.div_euclid(width).wrapping_mul(i64::from(size)) as u64);
                (Operand::Memory(adjusted), signed.rem_euclid(width) as u64)
            }
            _ => (dst, offset % u64::from(alu::bits(size))),
        };
        let mask = 1u64 << bit;
        let old = if self.i.lock {
            let Operand::Memory(memory) = dst else {
                return Err(Stop::Invalid);
            };
            let operation = match mnemonic {
                Mnemonic::Bts => AtomicOp::Or(u128::from(mask)),
                Mnemonic::Btr => AtomicOp::And(u128::from(!mask)),
                Mnemonic::Btc => AtomicOp::Xor(u128::from(mask)),
                _ => return Err(Stop::Invalid),
            };
            self.mem
                .atomic(self.linear(&memory), atomic_width(size)?, operation)?
                .old as u64
        } else {
            let old = self.read(dst, size)?;
            let updated = match mnemonic {
                Mnemonic::Bts => Some(old | mask),
                Mnemonic::Btr => Some(old & !mask),
                Mnemonic::Btc => Some(old ^ mask),
                _ => None,
            };
            if let Some(value) = updated {
                self.write(dst, size, value)?;
            }
            old
        };
        self.set_status(flag::CF, if old & mask != 0 { flag::CF } else { 0 });
        Ok(())
    }

    fn rotate(&mut self, mnemonic: Mnemonic) -> Result<()> {
        let dst = op(self.i, 0)?;
        let size = Self::size_of(dst, None);
        let masked =
            self.i.operand(1).map_or(Ok(1), |o| self.read(o, 1))? & if size == 8 { 63 } else { 31 };
        let width = alu::bits(size);
        let through = matches!(mnemonic, Mnemonic::Rcl | Mnemonic::Rcr);
        let period = width + u32::from(through);
        let count = u32::try_from(masked).map_err(|_| Stop::Invalid)? % period;
        let value = self.read(dst, size)?;
        if masked == 0 || (through && count == 0) {
            return self.write(dst, size, value);
        }
        let wide = u128::from(value)
            | if through {
                u128::from(self.s.flag(flag::CF)) << width
            } else {
                0
            };
        let mask = (1u128 << period) - 1;
        let left = matches!(mnemonic, Mnemonic::Rol | Mnemonic::Rcl);
        let rotated = if count == 0 {
            wide
        } else if left {
            ((wide << count) | (wide >> (period - count))) & mask
        } else {
            ((wide >> count) | (wide << (period - count))) & mask
        };
        let result = rotated as u64 & size_mask(size);
        let cf = if through {
            rotated & (1u128 << width) != 0
        } else if left {
            result & 1 != 0
        } else {
            result & (1u64 << (width - 1)) != 0
        };
        let overflow = if left {
            (result & (1u64 << (width - 1)) != 0) != cf
        } else {
            ((result >> (width - 1)) ^ (result >> (width - 2))) & 1 != 0
        };
        self.write(dst, size, result)?;
        let flag_mask = flag::CF | if masked == 1 { flag::OF } else { 0 };
        self.set_status(
            flag_mask,
            if cf { flag::CF } else { 0 } | if overflow { flag::OF } else { 0 },
        );
        Ok(())
    }

    fn scan(&mut self, reverse: bool) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let value = self.read(src, size)?;
        if value != 0 {
            let index = if reverse {
                63 - value.leading_zeros()
            } else {
                value.trailing_zeros()
            };
            self.write(dst, size, u64::from(index))?;
        }
        self.set_status(flag::ZF, if value == 0 { flag::ZF } else { 0 });
        Ok(())
    }

    fn extend(&mut self, signed: bool) -> Result<()> {
        let (dst, src, _) = self.binary()?;
        let src_size = Self::size_of(src, None);
        let dst_size = Self::size_of(dst, None);
        let v = self.read(src, src_size)?;
        let v = if signed { sign_extend(v, src_size) } else { v };
        self.write(dst, dst_size, v)
    }

    fn double_shift(&mut self, right: bool) -> Result<()> {
        let dst = op(self.i, 0)?;
        let size = Self::size_of(dst, None);
        let width = u32::from(size) * 8;
        let a = self.read(dst, size)?;
        let b = self.read(op(self.i, 1)?, size)?;
        let count = self.read(op(self.i, 2)?, 1)? as u32 & if size == 8 { 63 } else { 31 };
        if count == 0 {
            return self.write(dst, size, a);
        }
        // Results/flags above the operand width are architecturally undefined.
        let n = count.min(width);
        let joined = if right {
            u128::from(a) | (u128::from(b) << width)
        } else {
            (u128::from(a) << width) | u128::from(b)
        };
        let result = if right {
            (joined >> n) as u64
        } else {
            ((joined << n) >> width) as u64
        } & size_mask(size);
        let cf = if right {
            (a >> (n - 1)) & 1
        } else {
            (a >> (width - n)) & 1
        };
        let mut flags = alu::zf_sf_pf(result, size) | cf;
        if count == 1 && (a ^ result) & (1u64 << (width - 1)) != 0 {
            flags |= flag::OF;
        }
        self.write(dst, size, result)?;
        self.set_status(
            flag::CF | flag::ZF | flag::SF | flag::PF | if count == 1 { flag::OF } else { 0 },
            flags,
        );
        Ok(())
    }

    fn adx(&mut self, overflow_chain: bool) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let a = self.read(dst, size)?;
        let b = self.read(src, size)?;
        let bit = if overflow_chain { flag::OF } else { flag::CF };
        let (value, flags) = alu::add(a, b, self.s.flag(bit), size);
        self.write(dst, size, value)?;
        self.s.set_flag(bit, flags & flag::CF != 0);
        Ok(())
    }

    fn bmi(&mut self, mnemonic: Mnemonic) -> Result<()> {
        let dst = op(self.i, 0)?;
        let size = Self::size_of(dst, None);
        let width = u32::from(size) * 8;
        let a = self.read(op(self.i, 1)?, size)?;
        let b = self.read(op(self.i, 2)?, size)?;
        let count = b as u32 & (width - 1);
        let value = match mnemonic {
            Mnemonic::Andn => !a & b,
            Mnemonic::Bzhi => {
                let n = b & 0xff;
                if n >= u64::from(width) {
                    a
                } else if n == 0 {
                    0
                } else {
                    a & ((1u64 << n) - 1)
                }
            }
            Mnemonic::Shlx => a.wrapping_shl(count),
            Mnemonic::Shrx => a >> count,
            Mnemonic::Rorx => {
                if size == 4 {
                    u64::from((a as u32).rotate_right(count))
                } else {
                    a.rotate_right(count)
                }
            }
            Mnemonic::Pext => {
                let mut mask = b;
                let mut result = 0u64;
                let mut out = 1u64;
                while mask != 0 {
                    let bit = 1u64 << mask.trailing_zeros();
                    if a & bit != 0 {
                        result |= out;
                    }
                    mask &= mask - 1;
                    out = out.wrapping_shl(1);
                }
                result
            }
            _ => return Err(Stop::Invalid),
        } & size_mask(size);
        self.write(dst, size, value)?;
        if matches!(mnemonic, Mnemonic::Andn | Mnemonic::Bzhi) {
            let flags = alu::zf_sf_pf(value, size) & (flag::ZF | flag::SF)
                | if mnemonic == Mnemonic::Bzhi && b & 0xff >= u64::from(width) {
                    flag::CF
                } else {
                    0
                };
            self.set_status(flag::CF | flag::OF | flag::ZF | flag::SF, flags);
        }
        Ok(())
    }

    fn mulx(&mut self) -> Result<()> {
        let high = op(self.i, 0)?;
        let low = op(self.i, 1)?;
        let size = Self::size_of(high, None);
        let a = self.s.gpr[reg::RDX] & size_mask(size);
        let b = self.read(op(self.i, 2)?, size)?;
        let product = u128::from(a) * u128::from(b);
        self.write(low, size, product as u64)?;
        self.write(high, size, (product >> (u32::from(size) * 8)) as u64)
    }

    fn movbe(&mut self) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        if !matches!(dst, Operand::Memory(_)) && !matches!(src, Operand::Memory(_)) {
            return Err(Stop::Invalid);
        }
        let value = self.read(src, size)?;
        let swapped = match size {
            2 => u64::from((value as u16).swap_bytes()),
            4 => u64::from((value as u32).swap_bytes()),
            8 => value.swap_bytes(),
            _ => return Err(Stop::Invalid),
        };
        self.write(dst, size, swapped)
    }

    fn count_bits(&mut self, mnemonic: Mnemonic) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let value = self.read(src, size)? & size_mask(size);
        let width = u32::from(size) * 8;
        let count = match mnemonic {
            Mnemonic::Tzcnt => {
                if value == 0 {
                    width
                } else {
                    value.trailing_zeros()
                }
            }
            Mnemonic::Lzcnt => value.leading_zeros() - (64 - width),
            Mnemonic::Popcnt => value.count_ones(),
            _ => return Err(Stop::Invalid),
        };
        self.write(dst, size, u64::from(count))?;
        if mnemonic == Mnemonic::Popcnt {
            self.set_status(flag::STATUS, if value == 0 { flag::ZF } else { 0 });
        } else {
            self.set_status(
                flag::CF | flag::ZF,
                if value == 0 { flag::CF } else { 0 } | if count == 0 { flag::ZF } else { 0 },
            );
        }
        Ok(())
    }

    fn cmpxchg(&mut self) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let acc = Register::Gpr { index: 0, size };
        let expected = self.read_reg(acc);
        let new = self.read(src, size)?;
        let current = if let Operand::Memory(mem) = dst {
            self.mem
                .atomic(
                    self.linear(&mem),
                    atomic_width(size)?,
                    AtomicOp::CompareExchange {
                        expected: u128::from(expected),
                        replacement: u128::from(new),
                    },
                )?
                .old as u64
        } else {
            self.read(dst, size)?
        };
        let (_, f) = alu::sub(expected, current, false, size);
        if expected == current {
            if !matches!(dst, Operand::Memory(_)) {
                self.write(dst, size, new)?;
            }
        } else {
            self.write_reg(acc, current);
        }
        self.set_status(flag::STATUS, f);
        Ok(())
    }

    fn xchg(&mut self) -> Result<()> {
        let (a, b, size) = self.binary()?;
        if let Operand::Memory(mem) = a {
            let value = self.read(b, size)?;
            let old = self
                .mem
                .atomic(
                    self.linear(&mem),
                    atomic_width(size)?,
                    AtomicOp::Exchange(u128::from(value)),
                )?
                .old;
            return self.write(b, size, old as u64);
        }
        if let Operand::Memory(mem) = b {
            let value = self.read(a, size)?;
            let old = self
                .mem
                .atomic(
                    self.linear(&mem),
                    atomic_width(size)?,
                    AtomicOp::Exchange(u128::from(value)),
                )?
                .old;
            return self.write(a, size, old as u64);
        }
        let va = self.read(a, size)?;
        let vb = self.read(b, size)?;
        // Write memory first so a fault leaves the registers untouched.
        if matches!(a, Operand::Memory(_)) {
            self.write(a, size, vb)?;
            self.write(b, size, va)
        } else {
            self.write(b, size, va)?;
            self.write(a, size, vb)
        }
    }

    fn xadd(&mut self) -> Result<()> {
        let (dst, src, size) = self.binary()?;
        let b = self.read(src, size)?;
        let a = if let Operand::Memory(mem) = dst {
            self.mem
                .atomic(
                    self.linear(&mem),
                    atomic_width(size)?,
                    AtomicOp::Add(u128::from(b)),
                )?
                .old as u64
        } else {
            self.read(dst, size)?
        };
        let (sum, flags) = alu::add(a, b, false, size);
        self.write(src, size, a)?;
        if !matches!(dst, Operand::Memory(_)) {
            self.write(dst, size, sum)?;
        }
        self.set_status(flag::STATUS, flags);
        Ok(())
    }

    fn cmpxchg_pair(&mut self, wide: bool) -> Result<()> {
        let Operand::Memory(mem) = op(self.i, 0)? else {
            return Err(Stop::Invalid);
        };
        let address = self.linear(&mem);
        if wide && address.0 & 15 != 0 {
            return Err(Stop::GeneralProtection);
        }
        let bits = if wide { 64 } else { 32 };
        let mask = if wide { u64::MAX } else { 0xffff_ffff };
        let expected = u128::from(self.s.gpr[reg::RAX] & mask)
            | (u128::from(self.s.gpr[reg::RDX] & mask) << bits);
        let replacement = u128::from(self.s.gpr[reg::RBX] & mask)
            | (u128::from(self.s.gpr[reg::RCX] & mask) << bits);
        let result = self.mem.atomic(
            address,
            if wide {
                AtomicWidth::W128
            } else {
                AtomicWidth::W64
            },
            AtomicOp::CompareExchange {
                expected,
                replacement,
            },
        )?;
        if !result.exchanged {
            self.s.gpr[reg::RAX] = result.old as u64 & mask;
            self.s.gpr[reg::RDX] = (result.old >> bits) as u64 & mask;
        }
        self.s.set_flag(flag::ZF, result.exchanged);
        Ok(())
    }

    fn string(&mut self, m: Mnemonic) -> Result<bool> {
        let size = self.i.implicit_size;
        let step = if self.s.flag(flag::DF) {
            0u64.wrapping_sub(u64::from(size))
        } else {
            u64::from(size)
        };
        let repeat = self.i.rep != RepPrefix::None;
        let address_mask = if self.i.string_address_size_32 {
            0xffff_ffff
        } else {
            u64::MAX
        };
        let mut budget = REP_CHUNK;
        loop {
            if repeat {
                if self.s.gpr[reg::RCX] & address_mask == 0 {
                    return Ok(true);
                }
                if budget == 0 {
                    return Ok(false);
                }
                budget -= 1;
            }
            let rdi = GuestAddr(self.s.gpr[reg::RDI] & address_mask);
            let source_index = self.s.gpr[reg::RSI] & address_mask;
            let source_base = match self.i.string_segment {
                Segment::Fs => self.s.fs_base,
                Segment::Gs => self.s.gs_base,
                Segment::None => 0,
            };
            let source = GuestAddr(source_index.wrapping_add(source_base));
            let uses_source = matches!(
                m,
                Mnemonic::Movsb
                    | Mnemonic::Movsw
                    | Mnemonic::Movsd
                    | Mnemonic::Movsq
                    | Mnemonic::Lodsb
                    | Mnemonic::Lodsw
                    | Mnemonic::Lodsd
                    | Mnemonic::Lodsq
                    | Mnemonic::Cmpsb
                    | Mnemonic::Cmpsw
                    | Mnemonic::Cmpsd
                    | Mnemonic::Cmpsq
            );
            let uses_destination = !matches!(
                m,
                Mnemonic::Lodsb | Mnemonic::Lodsw | Mnemonic::Lodsd | Mnemonic::Lodsq
            );
            match m {
                Mnemonic::Movsb | Mnemonic::Movsw | Mnemonic::Movsd | Mnemonic::Movsq => {
                    let v = self.load(source, size)?;
                    self.store(rdi, size, v)?;
                }
                Mnemonic::Stosb | Mnemonic::Stosw | Mnemonic::Stosd | Mnemonic::Stosq => {
                    let v = self.s.gpr[reg::RAX] & size_mask(size);
                    self.store(rdi, size, v)?;
                }
                Mnemonic::Lodsb | Mnemonic::Lodsw | Mnemonic::Lodsd | Mnemonic::Lodsq => {
                    let value = self.load(source, size)?;
                    self.write_reg(Register::Gpr { index: 0, size }, value);
                }
                _ => {
                    let a = if uses_source {
                        self.load(source, size)?
                    } else {
                        self.s.gpr[reg::RAX] & size_mask(size)
                    };
                    let b = self.load(rdi, size)?;
                    let (_, flags) = alu::sub(a, b, false, size);
                    self.set_status(flag::STATUS, flags);
                }
            }
            if uses_source {
                self.s.gpr[reg::RSI] = (source_index.wrapping_add(step)) & address_mask;
            }
            if uses_destination {
                self.s.gpr[reg::RDI] = (rdi.0.wrapping_add(step)) & address_mask;
            }
            if !repeat {
                return Ok(true);
            }
            self.s.gpr[reg::RCX] = self.s.gpr[reg::RCX].wrapping_sub(1) & address_mask;
            if is_comparison_string(m)
                && ((self.i.rep == RepPrefix::Rep && !self.s.flag(flag::ZF))
                    || (self.i.rep == RepPrefix::Repne && self.s.flag(flag::ZF)))
            {
                return Ok(true);
            }
        }
    }

    fn read128(&self, o: Operand, aligned: bool) -> Result<u128> {
        match o {
            Operand::Register(Register::Xmm(n)) => Ok(self.s.xmm[usize::from(n & 15)]),
            Operand::Memory(m) => {
                let addr = self.linear(&m);
                if aligned && !addr.0.is_multiple_of(16) {
                    return Err(Stop::GeneralProtection);
                }
                let mut b = [0u8; 16];
                self.mem.read(addr, &mut b)?;
                Ok(u128::from_le_bytes(b))
            }
            _ => Err(Stop::Invalid),
        }
    }

    fn write128(&mut self, o: Operand, value: u128, aligned: bool) -> Result<()> {
        match o {
            Operand::Register(Register::Xmm(n)) => {
                self.s.xmm[usize::from(n & 15)] = value;
                Ok(())
            }
            Operand::Memory(m) => {
                let addr = self.linear(&m);
                if aligned && !addr.0.is_multiple_of(16) {
                    return Err(Stop::GeneralProtection);
                }
                self.mem.write(addr, &value.to_le_bytes())?;
                Ok(())
            }
            _ => Err(Stop::Invalid),
        }
    }

    fn sse_move(&mut self, aligned: bool) -> Result<()> {
        let dst = op(self.i, 0)?;
        let v = self.read128(op(self.i, 1)?, aligned)?;
        self.write128(dst, v, aligned)
    }

    fn sse_xor(&mut self) -> Result<()> {
        let dst = op(self.i, 0)?;
        // Legacy-SSE memory operands must be 16-byte aligned.
        let v = self.read128(dst, true)? ^ self.read128(op(self.i, 1)?, true)?;
        self.write128(dst, v, true)
    }

    fn sse_movq(&mut self) -> Result<()> {
        let dst = op(self.i, 0)?;
        let src = op(self.i, 1)?;
        let value = self.read(src, 8)?;
        // Legacy MOVQ writes only a qword to GPR/memory, but clears the
        // upper qword when its destination is an XMM register.
        self.write(dst, 8, value)
    }

    fn sse_unpack_low_qwords(&mut self) -> Result<()> {
        let dst = op(self.i, 0)?;
        let low = self.read128(dst, true)? as u64;
        let high = self.read128(op(self.i, 1)?, true)? as u64;
        self.write128(dst, u128::from(low) | (u128::from(high) << 64), true)
    }

    fn branch_target(&self) -> Result<u64> {
        let o = op(self.i, 0)?;
        self.read(o, 8)
    }
}

/// Executes `i` on `s`. On success `s.rip` points at the next instruction to
/// run. On any [`Stop`] other than `Syscall`, `s.rip` is left at `i`.
pub(crate) fn execute(s: &mut CpuState, mem: &AddressSpace, i: &Instruction) -> Result<()> {
    let next = i.next_rip();
    let mut x = Exec { s, mem, i };
    let mut target: Option<u64> = None;
    match i.mnemonic {
        m @ (Mnemonic::Add
        | Mnemonic::Adc
        | Mnemonic::Sub
        | Mnemonic::Sbb
        | Mnemonic::And
        | Mnemonic::Or
        | Mnemonic::Xor
        | Mnemonic::Cmp
        | Mnemonic::Test) => x.alu(m)?,
        m @ (Mnemonic::Inc | Mnemonic::Dec | Mnemonic::Neg | Mnemonic::Not) => x.unary(m)?,
        Mnemonic::Shl => x.shift(ShiftKind::Shl)?,
        Mnemonic::Shr => x.shift(ShiftKind::Shr)?,
        Mnemonic::Sar => x.shift(ShiftKind::Sar)?,
        Mnemonic::Shld => x.double_shift(false)?,
        Mnemonic::Shrd => x.double_shift(true)?,
        Mnemonic::Imul => x.imul()?,
        Mnemonic::Mul => x.mul()?,
        Mnemonic::Div => x.divide(false)?,
        Mnemonic::Idiv => x.divide(true)?,
        m @ (Mnemonic::Bt | Mnemonic::Bts | Mnemonic::Btr | Mnemonic::Btc) => x.bit(m)?,
        m @ (Mnemonic::Rol | Mnemonic::Ror | Mnemonic::Rcl | Mnemonic::Rcr) => x.rotate(m)?,
        Mnemonic::Bsf => x.scan(false)?,
        Mnemonic::Bsr => x.scan(true)?,
        m @ (Mnemonic::Tzcnt | Mnemonic::Lzcnt | Mnemonic::Popcnt) => x.count_bits(m)?,
        Mnemonic::Adcx => x.adx(false)?,
        Mnemonic::Adox => x.adx(true)?,
        m @ (Mnemonic::Andn
        | Mnemonic::Bzhi
        | Mnemonic::Pext
        | Mnemonic::Rorx
        | Mnemonic::Shlx
        | Mnemonic::Shrx) => x.bmi(m)?,
        Mnemonic::Mulx => x.mulx()?,
        Mnemonic::Movbe => x.movbe()?,
        Mnemonic::Enter => x.enter()?,
        Mnemonic::Xlatb => {
            let value = x.read(op(i, 0)?, 1)?;
            x.s.gpr[reg::RAX] = (x.s.gpr[reg::RAX] & !0xff) | value;
        }
        Mnemonic::Bswap => {
            let dst = op(i, 0)?;
            let size = Exec::size_of(dst, None);
            let value = x.read(dst, size)?;
            let result = match size {
                8 => value.swap_bytes(),
                4 => u64::from((value as u32).swap_bytes()),
                _ => return Err(Stop::Invalid),
            };
            x.write(dst, size, result)?;
        }
        Mnemonic::Mov => {
            let (dst, src, size) = x.binary()?;
            let v = x.read(src, size)?;
            x.write(dst, size, v)?;
        }
        Mnemonic::Movsx | Mnemonic::Movsxd => x.extend(true)?,
        Mnemonic::Movzx => x.extend(false)?,
        Mnemonic::Cdqe => {
            x.s.gpr[reg::RAX] = sign_extend(x.s.gpr[reg::RAX] & 0xffff_ffff, 4);
        }
        Mnemonic::Cbw => {
            let value = sign_extend(x.s.gpr[reg::RAX] & 0xff, 1);
            x.write_reg(Register::Gpr { index: 0, size: 2 }, value);
        }
        Mnemonic::Cwde => {
            let value = sign_extend(x.s.gpr[reg::RAX] & 0xffff, 2);
            x.write_reg(Register::Gpr { index: 0, size: 4 }, value);
        }
        Mnemonic::Cwd => {
            let value = if x.s.gpr[reg::RAX] & 0x8000 != 0 {
                0xffff
            } else {
                0
            };
            x.write_reg(Register::Gpr { index: 2, size: 2 }, value);
        }
        Mnemonic::Clc => x.s.set_flag(flag::CF, false),
        Mnemonic::Stc => x.s.set_flag(flag::CF, true),
        Mnemonic::Cmc => x.s.set_flag(flag::CF, !x.s.flag(flag::CF)),
        Mnemonic::Lahf => {
            let value = (x.s.rflags & 0xd5) | 2;
            x.write_reg(Register::GprHigh8 { index: 0 }, value);
        }
        Mnemonic::Sahf => {
            let value = (x.s.gpr[reg::RAX] >> 8) & 0xd5;
            x.set_status(0xd5, value);
        }
        Mnemonic::Cdq => {
            let negative = x.s.gpr[reg::RAX] & 0x8000_0000 != 0;
            x.s.gpr[reg::RDX] = if negative { 0xffff_ffff } else { 0 };
        }
        Mnemonic::Cqo => {
            let negative = x.s.gpr[reg::RAX] & (1 << 63) != 0;
            x.s.gpr[reg::RDX] = if negative { u64::MAX } else { 0 };
        }
        Mnemonic::Lea => {
            let dst = op(i, 0)?;
            let Operand::Memory(m) = op(i, 1)? else {
                return Err(Stop::Invalid);
            };
            let size = Exec::size_of(dst, None);
            let ea = x.address(&m);
            x.write(dst, size, ea.0)?;
        }
        Mnemonic::Xchg => x.xchg()?,
        Mnemonic::Cmpxchg => x.cmpxchg()?,
        Mnemonic::Xadd => x.xadd()?,
        Mnemonic::Cmpxchg8b => x.cmpxchg_pair(false)?,
        Mnemonic::Cmpxchg16b => x.cmpxchg_pair(true)?,
        Mnemonic::Push => {
            let size = i.implicit_size;
            let v = x.read(op(i, 0)?, size)?;
            x.push(v, size)?;
        }
        Mnemonic::Pop => {
            let size = i.implicit_size;
            let v = x.pop(size)?;
            x.write(op(i, 0)?, size, v)?;
        }
        Mnemonic::Pushfq | Mnemonic::Pushf => {
            let v = x.s.rflags & !(flag::RF | flag::VM);
            x.push(v, i.implicit_size)?;
        }
        Mnemonic::Popfq | Mnemonic::Popf => {
            let v = x.pop(i.implicit_size)?;
            let writable = flag::USER_WRITABLE & size_mask(i.implicit_size);
            let keep = x.s.rflags & !writable;
            x.s.rflags = keep | (v & writable) | flag::RESERVED1;
        }
        Mnemonic::Call => {
            let t = x.branch_target()?;
            x.push(next.0, 8)?;
            target = Some(t);
        }
        Mnemonic::Ret => {
            let t = x.pop(8)?;
            if let Some(Operand::Immediate(extra)) = i.operand(0) {
                x.s.gpr[reg::RSP] = x.s.gpr[reg::RSP].wrapping_add(extra & 0xffff);
            }
            target = Some(t);
        }
        Mnemonic::Jmp => target = Some(x.branch_target()?),
        Mnemonic::Jrcxz | Mnemonic::Jecxz => {
            let count = x.s.gpr[reg::RCX]
                & if i.mnemonic == Mnemonic::Jecxz {
                    0xffff_ffff
                } else {
                    u64::MAX
                };
            if count == 0 {
                target = Some(x.branch_target()?);
            }
        }
        Mnemonic::Loop | Mnemonic::Loope | Mnemonic::Loopne => {
            let size = if i.string_address_size_32 { 4 } else { 8 };
            let count = x.s.gpr[reg::RCX].wrapping_sub(1) & size_mask(size);
            x.write_reg(Register::Gpr { index: 1, size }, count);
            let condition = match i.mnemonic {
                Mnemonic::Loope => x.s.flag(flag::ZF),
                Mnemonic::Loopne => !x.s.flag(flag::ZF),
                _ => true,
            };
            if count != 0 && condition {
                target = Some(x.branch_target()?);
            }
        }
        Mnemonic::Jcc(c) => {
            if alu::condition(x.s.rflags, c) {
                target = Some(x.branch_target()?);
            }
        }
        Mnemonic::Setcc(c) => {
            let v = u64::from(alu::condition(x.s.rflags, c));
            x.write(op(i, 0)?, 1, v)?;
        }
        Mnemonic::Cmovcc(c) => {
            let (dst, src, size) = x.binary()?;
            // The source is read (and may fault) whatever the condition.
            let v = x.read(src, size)?;
            let v = if alu::condition(x.s.rflags, c) {
                v
            } else {
                x.read(dst, size)?
            };
            // A 32-bit cmov zero-extends the destination even when false.
            x.write(dst, size, v)?;
        }
        Mnemonic::Leave => {
            x.s.gpr[reg::RSP] = x.s.gpr[reg::RBP];
            let v = x.pop(i.implicit_size)?;
            let mask = size_mask(i.implicit_size);
            x.s.gpr[reg::RBP] = (x.s.gpr[reg::RBP] & !mask) | (v & mask);
        }
        Mnemonic::Nop | Mnemonic::Endbr64 => {}
        Mnemonic::Syscall => {
            x.s.gpr[reg::RCX] = next.0;
            x.s.gpr[reg::R11] = x.s.rflags & !flag::RF;
            x.s.rip = next;
            return Err(Stop::Syscall);
        }
        Mnemonic::Hlt => return Err(Stop::Halt),
        Mnemonic::Cld => x.s.set_flag(flag::DF, false),
        Mnemonic::Std => x.s.set_flag(flag::DF, true),
        m @ (Mnemonic::Movsb
        | Mnemonic::Movsd
        | Mnemonic::Movsq
        | Mnemonic::Stosb
        | Mnemonic::Stosd
        | Mnemonic::Stosq) => {
            if !x.string(m)? {
                // Not finished: run the same instruction again next step.
                return Ok(());
            }
        }
        m if is_string(m) => {
            if !x.string(m)? {
                return Ok(());
            }
        }
        Mnemonic::Movaps | Mnemonic::Movdqa => x.sse_move(true)?,
        Mnemonic::Movups | Mnemonic::Movdqu => x.sse_move(false)?,
        Mnemonic::Pxor | Mnemonic::Xorps => x.sse_xor()?,
        Mnemonic::Movq => x.sse_movq()?,
        Mnemonic::Punpcklqdq => x.sse_unpack_low_qwords()?,
        _ => return Err(Stop::Invalid),
    }
    x.s.rip = GuestAddr(target.unwrap_or(next.0));
    Ok(())
}
