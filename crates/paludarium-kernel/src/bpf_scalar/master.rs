//! A scalar as Linux master's verifier follows it: the bits it knows, one
//! circular range of its 64-bit values and one of its low 32 bits
//! (`r64` and `r32` of `struct bpf_reg_state`), and the line its signed
//! values lie on (`base` more than a multiple of `step`), with the
//! operations of master's `kernel/bpf/verifier.c` that change them.
//!
//! [`super::Scalar`] follows a scalar with this beside 7.0's model, and
//! the verifier refuses where the two decide differently.

use super::cnum::{Cnum32, Cnum64};
use super::{Tnum, fls64, jmp, op};

/// What master knows of a scalar, but its ID (which [`super::Scalar`]
/// holds for both).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct Master {
    pub(crate) var: Tnum,
    pub(crate) r64: Cnum64,
    pub(crate) r32: Cnum32,
    pub(crate) base: u16,
    pub(crate) step: u16,
}

/// `check_add_overflow` of two `i64`.
fn add_overflows(a: i64, b: i64) -> bool {
    a.checked_add(b).is_none()
}

/// `check_mul_overflow` of two `i64`.
fn mul_overflows(a: i64, b: i64) -> bool {
    a.checked_mul(b).is_none()
}

/// `imod`: the remainder of `v` by `step` that is not negative.
fn imod(v: i64, step: u16) -> u16 {
    v.rem_euclid(i64::from(step)) as u16
}

/// `cnum32_from_tnum`.
fn cnum32_of(t: Tnum) -> Cnum32 {
    let t = t.subreg();
    let (value, mask) = (t.value as u32, t.mask as u32);
    const SIGN: u32 = 1 << 31;
    if (mask | value) & SIGN != 0 {
        Cnum32::srange(
            (value | (mask & SIGN)) as i32,
            (value | (mask & !SIGN)) as i32,
        )
    } else {
        Cnum32::urange(value, value | mask)
    }
}

/// `cnum64_from_tnum`.
fn cnum64_of(t: Tnum) -> Cnum64 {
    const SIGN: u64 = 1 << 63;
    if (t.mask | t.value) & SIGN != 0 {
        Cnum64::srange(
            (t.value | (t.mask & SIGN)) as i64,
            (t.value | (t.mask & !SIGN)) as i64,
        )
    } else {
        Cnum64::urange(t.value, t.value | t.mask)
    }
}

impl Master {
    /// `bpf_mark_reg_unknown_imprecise`.
    pub(crate) const UNKNOWN: Master = Master {
        var: Tnum::UNKNOWN,
        r64: Cnum64::UNBOUNDED,
        r32: Cnum32::UNBOUNDED,
        base: 0,
        step: 1,
    };

    /// `__mark_reg_known`.
    pub(crate) fn known(value: u64) -> Master {
        let mut m = Master::UNKNOWN;
        m.set_known(value);
        m
    }

    /// `___mark_reg_known`.
    fn set_known(&mut self, value: u64) {
        self.var = Tnum::known(value);
        self.r64 = Cnum64::urange(value, value);
        self.r32 = Cnum32::urange(value as u32, value as u32);
        self.step_reset();
    }

    /// `__mark_reg32_known`.
    fn mark_known32(&mut self, value: u32) {
        self.var = self.var.const_subreg(value);
        self.r32 = Cnum32::urange(value, value);
    }

    /// `reg_step_reset`.
    fn step_reset(&mut self) {
        self.base = 0;
        self.step = 1;
    }

    pub(crate) fn umin(&self) -> u64 {
        self.r64.umin()
    }

    pub(crate) fn umax(&self) -> u64 {
        self.r64.umax()
    }

    pub(crate) fn smin(&self) -> i64 {
        self.r64.smin()
    }

    pub(crate) fn smax(&self) -> i64 {
        self.r64.smax()
    }

    pub(crate) fn u32_min(&self) -> u32 {
        self.r32.umin()
    }

    pub(crate) fn u32_max(&self) -> u32 {
        self.r32.umax()
    }

    pub(crate) fn s32_min(&self) -> i32 {
        self.r32.smin()
    }

    pub(crate) fn s32_max(&self) -> i32 {
        self.r32.smax()
    }

    fn set_urange64(&mut self, min: u64, max: u64) {
        self.r64 = Cnum64::urange(min, max);
    }

    fn set_srange64(&mut self, min: i64, max: i64) {
        self.r64 = Cnum64::srange(min, max);
    }

    fn set_urange32(&mut self, min: u32, max: u32) {
        self.r32 = Cnum32::urange(min, max);
    }

    fn set_srange32(&mut self, min: i32, max: i32) {
        self.r32 = Cnum32::srange(min, max);
    }

    /// The value, where every bit is known.
    pub(crate) fn value(&self) -> Option<u64> {
        self.var.is_const().then_some(self.var.value)
    }

    /// `is_reg_const` and `reg_const_value`.
    pub(crate) fn constant(&self, subreg: bool) -> Option<u64> {
        let var = if subreg { self.var.subreg() } else { self.var };
        var.is_const().then_some(var.value)
    }

    /// `get_reg_width`.
    pub(crate) fn width(&self) -> u32 {
        fls64(self.umax())
    }

    /// `__update_reg32_bounds`.
    fn update_bounds32(&mut self) {
        self.r32 = self.r32.intersect(cnum32_of(self.var));
    }

    /// `__update_reg64_bounds`, which also finds the one value the range
    /// and the known bits may share.
    fn update_bounds64(&mut self) {
        self.r64 = self.r64.intersect(cnum64_of(self.var));
        let (umin, umax) = (self.umin(), self.umax());
        let next = self.var.step(umin);
        let umin_in = umin & !self.var.mask == self.var.value;
        let tmax = self.var.value | self.var.mask;
        if umin_in && next > umax {
            self.set_known(umin);
        } else if !umin_in && next == tmax {
            self.set_known(tmax);
        } else if !umin_in && next <= umax && self.var.step(next) > umax {
            self.set_known(next);
        }
    }

    /// `__update_reg_bounds`.
    fn update_bounds(&mut self) {
        self.update_bounds32();
        self.update_bounds64();
    }

    /// `__reg_deduce_bounds`.
    fn deduce(&mut self) {
        self.r32 = self.r32.intersect(Cnum32::from64(self.r64));
        self.r64 = self.r64.intersect32(self.r32);
    }

    /// `__reg_bound_offset`, which also takes the trailing zeros of the
    /// step.
    fn bound_offset(&mut self) {
        let var64 = self.var.intersect(Tnum::range(self.umin(), self.umax()));
        let var32 = var64.subreg().intersect(Tnum::range(
            u64::from(self.u32_min()),
            u64::from(self.u32_max()),
        ));
        self.var = var64.clear_subreg().or(var32);
        let zeros = if self.base == 0 {
            self.step.trailing_zeros()
        } else {
            self.base.trailing_zeros().min(self.step.trailing_zeros())
        };
        self.var = self.var.and(Tnum::known(!0u64 << zeros));
    }

    /// `range_bounds_violation`.
    fn violated(&self) -> bool {
        self.r32.is_empty() || self.r64.is_empty()
    }

    /// `reg_bounds_sync`.
    pub(crate) fn sync(&mut self) {
        if self.violated() {
            return;
        }
        self.update_bounds();
        self.deduce();
        self.deduce();
        self.bound_offset();
        self.update_bounds();
        // __update_bounds_from_step
        self.r64 = self.r64.intersect_linear(self.base, self.step);
        self.r32 = self.r32.intersect(Cnum32::from64(self.r64));
    }

    /// Whether `reg_bounds_sanity_check` passes.
    pub(crate) fn sane(&self) -> bool {
        if self.violated() {
            return false;
        }
        if self.var.is_const() && (!self.r64.is_const() || self.r64.base != self.var.value) {
            return false;
        }
        let sub = self.var.subreg();
        if sub.is_const() && (!self.r32.is_const() || u64::from(self.r32.base) != sub.value) {
            return false;
        }
        self.step != 0 && self.base < self.step
    }

    /// `reg_step_check_unsigned`.
    fn step_check_unsigned(&mut self, bits: u32) {
        if self.umax() >= 1u64 << bits {
            self.step_reset();
        }
    }

    /// `zext_32_to_64`.
    pub(crate) fn zext(&mut self) {
        self.step_check_unsigned(32);
        self.var = self.var.subreg();
        self.set_urange64(u64::from(self.u32_min()), u64::from(self.u32_max()));
    }

    /// `coerce_reg_to_size`.
    pub(crate) fn coerce(&mut self, size: u32) {
        let mask = (1u64 << (size * 8)) - 1;
        self.step_check_unsigned(size * 8);
        self.var = self.var.cast(size);
        let (umin, umax) = (self.umin(), self.umax());
        if umin & !mask == umax & !mask {
            self.set_urange64(umin & mask, umax & mask);
        } else {
            self.set_urange64(0, mask);
        }
        if size < 4 {
            self.r32 = Cnum32::UNBOUNDED;
        }
        self.sync();
    }

    /// `coerce_reg_to_size_sx`.
    pub(crate) fn coerce_sx(&mut self, size: u32) {
        let bits = size * 8;
        let limit = 1i64 << (bits - 1);
        if self.smin() >= -limit && self.smax() < limit {
            return;
        }
        self.step_reset();
        let sext = |v: u64| -> i64 {
            match size {
                1 => i64::from(v as i8),
                2 => i64::from(v as i16),
                _ => i64::from(v as i32),
            }
        };
        if self.var.is_const() {
            let v = sext(self.var.value) as u64;
            self.var = Tnum::known(v);
            self.r64 = Cnum64::urange(v, v);
            self.r32 = Cnum32::urange(v as u32, v as u32);
            return;
        }
        let top = |v: i64| (v as u64 >> bits) << bits;
        if top(self.smax()) == top(self.smin()) {
            let (a, b) = (sext(self.smax() as u64), sext(self.smin() as u64));
            let (max, min) = (a.max(b), a.min(b));
            if (max >= 0) == (min >= 0) {
                self.set_srange64(min, max);
                self.set_srange32(min as i32, max as i32);
                self.var = Tnum::range(min as u64, max as u64);
                return;
            }
        }
        // set_sext64_default_val
        let (min, max) = match size {
            1 => (i64::from(i8::MIN), i64::from(i8::MAX)),
            2 => (i64::from(i16::MIN), i64::from(i16::MAX)),
            _ => (i64::from(i32::MIN), i64::from(i32::MAX)),
        };
        self.set_srange64(min, max);
        self.set_srange32(min as i32, max as i32);
        self.var = Tnum::UNKNOWN;
    }

    /// `coerce_subreg_to_size_sx`.
    pub(crate) fn coerce_subreg_sx(&mut self, size: u32) {
        let bits = size * 8;
        if self.umax() < 1u64 << (bits - 1) {
            return;
        }
        self.step_reset();
        let sext = |v: u32| -> i32 {
            if size == 1 {
                i32::from(v as i8)
            } else {
                i32::from(v as i16)
            }
        };
        if self.var.is_const() {
            let v = sext(self.var.value as u32);
            self.var = Tnum::known(v as i64 as u64);
            self.set_srange32(v, v);
            return;
        }
        let top = |v: i32| (v as u32 >> bits) << bits;
        if top(self.s32_max()) == top(self.s32_min()) {
            let (a, b) = (sext(self.s32_max() as u32), sext(self.s32_min() as u32));
            let (max, min) = (a.max(b), a.min(b));
            if (min >= 0) == (max >= 0) {
                self.set_srange32(min, max);
                self.var = Tnum::range(min as i64 as u64, max as i64 as u64).subreg();
                return;
            }
        }
        // set_sext32_default_val
        if size == 1 {
            self.set_srange32(i32::from(i8::MIN), i32::from(i8::MAX));
        } else {
            self.set_srange32(i32::from(i16::MIN), i32::from(i16::MAX));
        }
        self.var = Tnum::UNKNOWN.subreg();
    }

    /// `bpf_get_smp_processor_id`'s result in `do_refine_retval_range`:
    /// 0 to `last`.
    pub(crate) fn below(last: u32) -> Master {
        let mut m = Master::UNKNOWN;
        m.set_urange64(0, u64::from(last));
        m.set_urange32(0, last);
        m.sync();
        m
    }

    /// The two sides of `maybe_fork_scalars`, as [`super::Scalar::forked`].
    pub(crate) fn forked(&self, alu32: bool) -> (Master, Master) {
        let (mut zero, mut ones) = (*self, *self);
        if alu32 {
            zero.mark_known32(0);
            ones.mark_known32(u32::MAX);
        } else {
            zero = Master::known(0);
            ones = Master::known(u64::MAX);
        }
        (zero, ones)
    }
}

/// `is_safe_to_compute_dst_reg_range`.
fn safe_range(op: u8, alu32: bool, src: &Master) -> bool {
    let constant = if alu32 {
        src.var.subreg().is_const()
            && src.s32_min() == src.s32_max()
            && src.u32_min() == src.u32_max()
    } else {
        src.var.is_const() && src.smin() == src.smax() && src.umin() == src.umax()
    };
    match op {
        op::ADD | op::SUB | op::NEG | op::AND | op::XOR | op::OR | op::MUL | op::END => true,
        op::DIV | op::MOD => constant,
        op::LSH | op::RSH | op::ARSH => constant && src.umax() < if alu32 { 32 } else { 64 },
        _ => false,
    }
}

/// Whether `maybe_fork_scalars` splits the walk, as [`super::forks`].
pub(crate) fn forks(op: u8, dst: &Master, src: &Master) -> Option<bool> {
    if !matches!(op, op::AND | op::OR) || !src.var.is_const() {
        return None;
    }
    if dst.smin() == -1 && dst.smax() == 0 {
        Some(false)
    } else if dst.s32_min() == -1 && dst.s32_max() == 0 {
        Some(true)
    } else {
        None
    }
}

impl Master {
    /// `scalar_step_add` of `self` and `src` into `self`.
    fn step_add(&mut self, src: &Master) {
        let (reg, amount) = if let Some(v) = src.value() {
            (*self, v as i64)
        } else if let Some(v) = self.value() {
            (*src, v as i64)
        } else {
            return self.step_reset();
        };
        if add_overflows(reg.smin(), amount) || add_overflows(reg.smax(), amount) {
            return self.step_reset();
        }
        self.base = ((u32::from(reg.base) + u32::from(imod(amount, reg.step)))
            % u32::from(reg.step)) as u16;
        self.step = reg.step;
    }

    /// `scalar_step_scale`.
    fn step_scale(&mut self, amount: u64) {
        let step = u64::from(self.step)
            .checked_mul(amount)
            .filter(|&s| s <= u64::from(u16::MAX));
        let Some(step) = step else {
            return self.step_reset();
        };
        if amount == 0
            || mul_overflows(self.smin(), amount as i64)
            || mul_overflows(self.smax(), amount as i64)
        {
            return self.step_reset();
        }
        self.base = (u64::from(self.base) * amount) as u16;
        self.step = step as u16;
    }

    fn mul32(&mut self, src: &Master) {
        let (mut umin, mut umax) = (self.u32_min(), self.u32_max());
        match (
            umax.checked_mul(src.u32_max()),
            umin.checked_mul(src.u32_min()),
        ) {
            (Some(max), Some(min)) => (umin, umax) = (min, max),
            _ => (umin, umax) = (0, u32::MAX),
        }
        let (smin, smax) = (self.s32_min(), self.s32_max());
        let products = [
            smin.checked_mul(src.s32_min()),
            smin.checked_mul(src.s32_max()),
            smax.checked_mul(src.s32_min()),
            smax.checked_mul(src.s32_max()),
        ];
        let (smin, smax) = match products {
            [Some(a), Some(b), Some(c), Some(d)] => {
                (a.min(b).min(c).min(d), a.max(b).max(c).max(d))
            }
            _ => (i32::MIN, i32::MAX),
        };
        self.r32 = Cnum32::urange(umin, umax).intersect(Cnum32::srange(smin, smax));
    }

    fn mul64(&mut self, src: &Master) {
        let (mut umin, mut umax) = (self.umin(), self.umax());
        match (umax.checked_mul(src.umax()), umin.checked_mul(src.umin())) {
            (Some(max), Some(min)) => (umin, umax) = (min, max),
            _ => (umin, umax) = (0, u64::MAX),
        }
        let (smin, smax) = (self.smin(), self.smax());
        let products = [
            smin.checked_mul(src.smin()),
            smin.checked_mul(src.smax()),
            smax.checked_mul(src.smin()),
            smax.checked_mul(src.smax()),
        ];
        let (smin, smax) = match products {
            [Some(a), Some(b), Some(c), Some(d)] => {
                (a.min(b).min(c).min(d), a.max(b).max(c).max(d))
            }
            _ => (i64::MIN, i64::MAX),
        };
        self.r64 = Cnum64::urange(umin, umax).intersect(Cnum64::srange(smin, smax));
    }

    /// `reset_reg64_and_tnum`.
    fn reset64_and_var(&mut self) {
        self.r64 = Cnum64::UNBOUNDED;
        self.var = Tnum::UNKNOWN;
    }

    /// `reset_reg32_and_tnum`.
    fn reset32_and_var(&mut self) {
        self.r32 = Cnum32::UNBOUNDED;
        self.var = Tnum::UNKNOWN;
    }

    fn udiv32(&mut self, src: &Master) {
        let v = src.u32_min();
        self.set_urange32(self.u32_min() / v, self.u32_max() / v);
        self.reset64_and_var();
    }

    fn udiv64(&mut self, src: &Master) {
        let v = src.umin();
        self.set_urange64(self.umin() / v, self.umax() / v);
        self.reset32_and_var();
    }

    fn sdiv32(&mut self, src: &Master) {
        let (mut smin, mut smax) = (self.s32_min(), self.s32_max());
        let v = src.s32_min();
        if smin == i32::MIN && v == -1 {
            if smax != i32::MIN {
                (smin, smax) = (i32::MIN, i32::MAX);
            }
        } else {
            let (a, b) = (smin / v, smax / v);
            (smin, smax) = (a.min(b), a.max(b));
        }
        self.set_srange32(smin, smax);
        self.reset64_and_var();
    }

    fn sdiv64(&mut self, src: &Master) {
        let (mut smin, mut smax) = (self.smin(), self.smax());
        let v = src.smin();
        if smin == i64::MIN && v == -1 {
            if smax != i64::MIN {
                (smin, smax) = (i64::MIN, i64::MAX);
            }
        } else {
            let (a, b) = (smin / v, smax / v);
            (smin, smax) = (a.min(b), a.max(b));
        }
        self.set_srange64(smin, smax);
        self.reset32_and_var();
    }

    fn umod32(&mut self, src: &Master) {
        let max = src.u32_min() - 1;
        if self.u32_max() <= max {
            return;
        }
        self.set_urange32(0, self.u32_max().min(max));
        self.reset64_and_var();
    }

    fn umod64(&mut self, src: &Master) {
        let max = src.umin() - 1;
        if self.umax() <= max {
            return;
        }
        self.set_urange64(0, self.umax().min(max));
        self.reset32_and_var();
    }

    fn smod32(&mut self, src: &Master) {
        let v = src.s32_min();
        let abs = if v > 0 {
            v as u32
        } else {
            (v as u32).wrapping_neg()
        };
        let max = abs.wrapping_sub(1) as i32;
        let (smin, smax) = (self.s32_min(), self.s32_max());
        if smin >= -max && smax <= max {
            return;
        }
        if smin >= 0 {
            self.set_srange32(0, smax.min(max));
        } else if smax <= 0 {
            self.set_srange32(smin.max(-max), 0);
        } else {
            self.set_srange32(-max, max);
        }
        self.reset64_and_var();
    }

    fn smod64(&mut self, src: &Master) {
        let v = src.smin();
        let abs = if v > 0 {
            v as u64
        } else {
            (v as u64).wrapping_neg()
        };
        let max = abs.wrapping_sub(1) as i64;
        let (smin, smax) = (self.smin(), self.smax());
        if smin >= -max && smax <= max {
            return;
        }
        if smin >= 0 {
            self.set_srange64(0, smax.min(max));
        } else if smax <= 0 {
            self.set_srange64(smin.max(-max), 0);
        } else {
            self.set_srange64(-max, max);
        }
        self.reset32_and_var();
    }

    fn and32(&mut self, src: &Master) {
        let var32 = self.var.subreg();
        if src.var.subreg().is_const() && var32.is_const() {
            return self.mark_known32(var32.value as u32);
        }
        self.set_urange32(var32.value as u32, self.u32_max().min(src.u32_max()));
    }

    fn and64(&mut self, src: &Master) {
        if src.var.is_const() && self.var.is_const() {
            return self.set_known(self.var.value);
        }
        self.set_urange64(self.var.value, self.umax().min(src.umax()));
        self.update_bounds();
    }

    fn or32(&mut self, src: &Master) {
        let var32 = self.var.subreg();
        if src.var.subreg().is_const() && var32.is_const() {
            return self.mark_known32(var32.value as u32);
        }
        self.set_urange32(
            self.u32_min().max(src.u32_min()),
            (var32.value | var32.mask) as u32,
        );
    }

    fn or64(&mut self, src: &Master) {
        if src.var.is_const() && self.var.is_const() {
            return self.set_known(self.var.value);
        }
        self.set_urange64(self.umin().max(src.umin()), self.var.value | self.var.mask);
        self.update_bounds();
    }

    fn xor32(&mut self, src: &Master) {
        let var32 = self.var.subreg();
        if src.var.subreg().is_const() && var32.is_const() {
            return self.mark_known32(var32.value as u32);
        }
        self.set_urange32(var32.value as u32, (var32.value | var32.mask) as u32);
    }

    fn xor64(&mut self, src: &Master) {
        if src.var.is_const() && self.var.is_const() {
            return self.set_known(self.var.value);
        }
        self.set_urange64(self.var.value, self.var.value | self.var.mask);
    }

    /// `__scalar32_min_max_lsh`.
    fn lsh32_bounds(&mut self, umin: u64, umax: u64) {
        if umax > 31 || u64::from(self.u32_max()) > 1u64 << (31 - umax) {
            self.set_urange32(0, u32::MAX);
        } else {
            self.set_urange32(self.u32_min() << umin, self.u32_max() << umax);
        }
    }

    fn lsh32(&mut self, src: &Master) {
        let (umin, umax) = (u64::from(src.u32_min()), u64::from(src.u32_max()));
        let subreg = self.var.subreg();
        self.lsh32_bounds(umin, umax);
        self.var = subreg.lshift(umin as u32).subreg();
        self.r64 = Cnum64::UNBOUNDED;
        self.update_bounds32();
    }

    fn lsh64(&mut self, src: &Master) {
        let (umin, umax) = (src.umin(), src.umax());
        let s = if umin == 32 && umax == 32 {
            Cnum64::srange(
                i64::from(self.s32_min()) << 32,
                i64::from(self.s32_max()) << 32,
            )
        } else {
            Cnum64::UNBOUNDED
        };
        let u = if self.umax() > 1u64 << (63 - umax) {
            Cnum64::UNBOUNDED
        } else {
            Cnum64::urange(self.umin() << umin, self.umax() << umax)
        };
        self.r64 = u.intersect(s);
        self.lsh32_bounds(umin, umax);
        self.var = self.var.lshift(umin as u32);
        self.update_bounds();
    }

    fn rsh32(&mut self, src: &Master) {
        let (umin, umax) = (src.u32_min(), src.u32_max());
        self.var = self.var.subreg().rshift(umin);
        self.set_urange32(self.u32_min() >> umax, self.u32_max() >> umin);
        self.r64 = Cnum64::UNBOUNDED;
        self.update_bounds32();
    }

    fn rsh64(&mut self, src: &Master) {
        let (umin, umax) = (src.umin(), src.umax());
        self.var = self.var.rshift(umin as u32);
        self.set_urange64(self.umin() >> umax, self.umax() >> umin);
        self.r32 = Cnum32::UNBOUNDED;
        self.update_bounds();
    }

    fn arsh32(&mut self, src: &Master) {
        let v = src.u32_min();
        self.set_srange32(self.s32_min() >> v, self.s32_max() >> v);
        self.var = self.var.subreg().arshift(v, 32);
        self.r64 = Cnum64::UNBOUNDED;
        self.update_bounds32();
    }

    fn arsh64(&mut self, src: &Master) {
        let v = src.umin() as u32;
        self.set_srange64(self.smin() >> v, self.smax() >> v);
        self.var = self.var.arshift(v, 64);
        self.r32 = Cnum32::UNBOUNDED;
        self.update_bounds();
    }

    /// `scalar_byte_swap`, as [`super::Scalar`]'s.
    fn byte_swap(&mut self, swap: bool, bits: u32) {
        if swap {
            let Tnum { value, mask } = self.var;
            self.var = match bits {
                16 => Tnum::new(
                    u64::from((value as u16).swap_bytes()),
                    u64::from((mask as u16).swap_bytes()),
                ),
                32 => Tnum::new(
                    u64::from((value as u32).swap_bytes()),
                    u64::from((mask as u32).swap_bytes()),
                ),
                _ => Tnum::new(value.swap_bytes(), mask.swap_bytes()),
            };
            self.r64 = Cnum64::UNBOUNDED;
            self.r32 = Cnum32::UNBOUNDED;
            self.step_reset();
        }
        if bits == 16 || bits == 32 {
            self.coerce(bits / 8);
        }
    }

    /// `adjust_scalar_min_max_vals`, as [`super::Scalar::alu`].
    pub(crate) fn alu(
        &mut self,
        op: u8,
        alu32: bool,
        signed: bool,
        src: &Master,
        end: (bool, u32),
    ) {
        if !safe_range(op, alu32, src) {
            *self = Master::UNKNOWN;
            return;
        }
        match op {
            op::ADD => {
                self.step_add(src);
                self.r32 = self.r32.add(src.r32);
                self.r64 = self.r64.add(src.r64);
                self.var = self.var.add(src.var);
            }
            op::SUB => {
                self.r32 = self.r32.add(src.r32.negate());
                self.r64 = self.r64.add(src.r64.negate());
                self.var = self.var.sub(src.var);
                self.step_reset();
            }
            op::NEG => {
                let old = *self;
                *self = Master::known(0);
                self.r32 = self.r32.add(old.r32.negate());
                self.r64 = self.r64.add(old.r64.negate());
                self.var = old.var.neg();
                self.step_reset();
            }
            op::MUL => {
                match src.value() {
                    Some(v) => self.step_scale(v),
                    None => self.step_reset(),
                }
                self.var = self.var.mul(src.var);
                self.mul32(src);
                self.mul64(src);
            }
            op::DIV => {
                let zero = if alu32 {
                    src.u32_min() == 0
                } else {
                    src.umin() == 0
                };
                if zero {
                    self.set_known(0);
                } else {
                    match (alu32, signed) {
                        (true, true) => self.sdiv32(src),
                        (true, false) => self.udiv32(src),
                        (false, true) => self.sdiv64(src),
                        (false, false) => self.udiv64(src),
                    }
                    self.step_reset();
                }
            }
            op::MOD => {
                let zero = if alu32 {
                    src.u32_min() == 0
                } else {
                    src.umin() == 0
                };
                if !zero {
                    match (alu32, signed) {
                        (true, true) => self.smod32(src),
                        (true, false) => self.umod32(src),
                        (false, true) => self.smod64(src),
                        (false, false) => self.umod64(src),
                    }
                    self.step_reset();
                }
            }
            op::AND => {
                self.var = self.var.and(src.var);
                self.and32(src);
                self.and64(src);
                self.step_reset();
            }
            op::OR => {
                self.var = self.var.or(src.var);
                self.or32(src);
                self.or64(src);
                self.step_reset();
            }
            op::XOR => {
                self.var = self.var.xor(src.var);
                self.xor32(src);
                self.xor64(src);
                self.step_reset();
            }
            op::LSH => {
                match src.value() {
                    Some(v) if v < 64 => self.step_scale(1 << v),
                    _ => self.step_reset(),
                }
                if alu32 {
                    self.lsh32(src);
                } else {
                    self.lsh64(src);
                }
            }
            op::RSH => {
                if alu32 {
                    self.rsh32(src);
                } else {
                    self.rsh64(src);
                }
                self.step_reset();
            }
            op::ARSH => {
                if alu32 {
                    self.arsh32(src);
                } else {
                    self.arsh64(src);
                }
                self.step_reset();
            }
            op::END => {
                self.byte_swap(end.0, end.1);
                self.step_reset();
            }
            _ => {}
        }
        if alu32 && op != op::END {
            self.zext();
        }
        self.sync();
    }

    /// The addition of `sync_linked_regs` of a register whose constant is
    /// `delta` more than the known one's: `known` plus `delta`, and its
    /// zero extension for a 32-bit link.
    pub(crate) fn plus(known: &Master, delta: i64, zext: bool) -> Master {
        let fake = Master::known(delta as u64);
        let mut m = *known;
        m.step_add(&fake);
        m.r32 = m.r32.add(fake.r32);
        m.r64 = m.r64.add(fake.r64);
        m.var = m.var.add(fake.var);
        if zext {
            m.zext();
        }
        m.sync();
        m
    }
}

/// `is_scalar_branch_taken`, with `simulate_both_branches_taken` where
/// the bounds alone do not decide.
pub(crate) fn taken(a: &Master, b: &Master, op: u8, jmp32: bool, same: bool) -> Option<bool> {
    let (t1, t2) = if jmp32 {
        (a.var.subreg(), b.var.subreg())
    } else {
        (a.var, b.var)
    };
    let bounds = |s: &Master| {
        if jmp32 {
            (
                u64::from(s.u32_min()),
                u64::from(s.u32_max()),
                i64::from(s.s32_min()),
                i64::from(s.s32_max()),
            )
        } else {
            (s.umin(), s.umax(), s.smin(), s.smax())
        }
    };
    let (umin1, umax1, smin1, smax1) = bounds(a);
    let (umin2, umax2, smin2, smax2) = bounds(b);
    if same {
        return match op {
            jmp::JGE | jmp::JLE | jmp::JSGE | jmp::JSLE | jmp::JEQ => Some(true),
            jmp::JGT | jmp::JLT | jmp::JSGT | jmp::JSLT | jmp::JNE => Some(false),
            jmp::JSET if t1.is_const() => Some(t1.value != 0),
            jmp::JSET => (smin1 > 0 || smax1 < 0).then_some(true),
            _ => None,
        };
    }
    let apart = || {
        !t1.overlap(t2)
            || umin1 > umax2
            || umax1 < umin2
            || smin1 > smax2
            || smax1 < smin2
            || (!jmp32
                && (a.u32_min() > b.u32_max()
                    || a.u32_max() < b.u32_min()
                    || a.s32_min() > b.s32_max()
                    || a.s32_max() < b.s32_min()))
    };
    let decided = match op {
        jmp::JEQ if t1.is_const() && t2.is_const() => Some(t1.value == t2.value),
        jmp::JEQ => apart().then_some(false),
        jmp::JNE if t1.is_const() && t2.is_const() => Some(t1.value != t2.value),
        jmp::JNE => apart().then_some(true),
        jmp::JSET => {
            let (t1, t2) = if b.constant(jmp32).is_none() {
                (t2, t1)
            } else {
                (t1, t2)
            };
            if a.constant(jmp32).is_none() && b.constant(jmp32).is_none() {
                return None;
            }
            if (!t1.mask & t1.value) & t2.value != 0 {
                Some(true)
            } else if (t1.mask | t1.value) & t2.value == 0 {
                Some(false)
            } else {
                None
            }
        }
        jmp::JGT => order(umin1 > umax2, umax1 <= umin2),
        jmp::JSGT => order(smin1 > smax2, smax1 <= smin2),
        jmp::JLT => order(umax1 < umin2, umin1 >= umax2),
        jmp::JSLT => order(smax1 < smin2, smin1 >= smax2),
        jmp::JGE => order(umin1 >= umax2, umax1 < umin2),
        jmp::JSGE => order(smin1 >= smax2, smax1 < smin2),
        jmp::JLE => order(umax1 <= umin2, umin1 > umax2),
        jmp::JSLE => order(smax1 <= smin2, smin1 > smax2),
        _ => None,
    };
    if decided.is_some() {
        return decided;
    }
    // simulate_both_branches_taken: a side whose bounds come out empty
    // is never taken.
    let (mut fa, mut fb) = (*a, *b);
    refine_cond(&mut fa, &mut fb, super::reverse(op), jmp32);
    fa.sync();
    fb.sync();
    if fa.violated() || fb.violated() {
        return Some(true);
    }
    let (mut ta, mut tb) = (*a, *b);
    refine_cond(&mut ta, &mut tb, op, jmp32);
    ta.sync();
    tb.sync();
    if ta.violated() || tb.violated() {
        return Some(false);
    }
    None
}

fn order(yes: bool, no: bool) -> Option<bool> {
    if yes {
        Some(true)
    } else if no {
        Some(false)
    } else {
        None
    }
}

/// The two sides of a jump `taken` does not decide: `regs_refine_cond_op`
/// and `reg_bounds_sync` of both, as `simulate_both_branches_taken` left
/// them; nothing where it did not run (a `BPF_JSET` of two registers
/// neither of which is a constant).
pub(crate) fn refine(a: &mut Master, b: &mut Master, op: u8, jmp32: bool) {
    if matches!(op, jmp::JSET | jmp::NOT_JSET)
        && a.constant(jmp32).is_none()
        && b.constant(jmp32).is_none()
    {
        return;
    }
    refine_cond(a, b, op, jmp32);
    a.sync();
    b.sync();
}

/// `regs_refine_cond_op`.
fn refine_cond(a: &mut Master, b: &mut Master, op: u8, jmp32: bool) {
    let (a, b, op) = match op {
        jmp::JGE | jmp::JGT | jmp::JSGE | jmp::JSGT => (b, a, super::flip(op)),
        _ => (a, b, op),
    };
    match op {
        jmp::JEQ => {
            if jmp32 {
                a.r32 = a.r32.intersect(b.r32);
                b.r32 = a.r32;
                let t = a.var.subreg().intersect(b.var.subreg());
                a.var = a.var.with_subreg(t);
                b.var = b.var.with_subreg(t);
            } else {
                a.r64 = a.r64.intersect(b.r64);
                b.r64 = a.r64;
                a.var = a.var.intersect(b.var);
                b.var = a.var;
            }
        }
        jmp::JNE => {
            let (a, b) = if b.constant(jmp32).is_none() {
                (b, a)
            } else {
                (a, b)
            };
            let Some(val) = b.constant(jmp32) else {
                return;
            };
            if jmp32 {
                a.r32 = a.r32.intersect(Cnum32 {
                    base: (val as u32).wrapping_add(1),
                    size: u32::MAX - 1,
                });
            } else {
                a.r64 = a.r64.intersect(Cnum64 {
                    base: val.wrapping_add(1),
                    size: u64::MAX - 1,
                });
            }
        }
        jmp::JSET => {
            let (a, b) = if b.constant(jmp32).is_none() {
                (b, a)
            } else {
                (a, b)
            };
            let Some(val) = b.constant(jmp32) else {
                return;
            };
            if !val.is_power_of_two() {
                return;
            }
            if jmp32 {
                let t = a.var.subreg().or(Tnum::known(val));
                a.var = a.var.with_subreg(t);
            } else {
                a.var = a.var.or(Tnum::known(val));
            }
        }
        jmp::NOT_JSET => {
            let (a, b) = if b.constant(jmp32).is_none() {
                (b, a)
            } else {
                (a, b)
            };
            let Some(val) = b.constant(jmp32) else {
                return;
            };
            a.r64 = Cnum64::UNBOUNDED;
            a.r32 = Cnum32::UNBOUNDED;
            a.step_reset();
            if jmp32 {
                let t = a.var.subreg().and(Tnum::known(!val));
                a.var = a.var.with_subreg(t);
            } else {
                a.var = a.var.and(Tnum::known(!val));
            }
        }
        jmp::JLE => {
            if jmp32 {
                a.r32 = a.r32.intersect_urange(0, b.u32_max());
                b.r32 = b.r32.intersect_urange(a.u32_min(), u32::MAX);
            } else {
                a.r64 = a.r64.intersect_urange(0, b.umax());
                b.r64 = b.r64.intersect_urange(a.umin(), u64::MAX);
            }
        }
        jmp::JLT => {
            if jmp32 {
                a.r32 = a.r32.intersect_urange(0, b.u32_max().wrapping_sub(1));
                b.r32 = b
                    .r32
                    .intersect_urange(a.u32_min().wrapping_add(1), u32::MAX);
            } else {
                a.r64 = a.r64.intersect_urange(0, b.umax().wrapping_sub(1));
                b.r64 = b.r64.intersect_urange(a.umin().wrapping_add(1), u64::MAX);
            }
        }
        jmp::JSLE => {
            if jmp32 {
                a.r32 = a.r32.intersect_srange(i32::MIN, b.s32_max());
                b.r32 = b.r32.intersect_srange(a.s32_min(), i32::MAX);
            } else {
                a.r64 = a.r64.intersect_srange(i64::MIN, b.smax());
                b.r64 = b.r64.intersect_srange(a.smin(), i64::MAX);
            }
        }
        jmp::JSLT => {
            if jmp32 {
                a.r32 = a
                    .r32
                    .intersect_srange(i32::MIN, b.s32_max().wrapping_sub(1));
                b.r32 = b
                    .r32
                    .intersect_srange(a.s32_min().wrapping_add(1), i32::MAX);
            } else {
                a.r64 = a.r64.intersect_srange(i64::MIN, b.smax().wrapping_sub(1));
                b.r64 = b.r64.intersect_srange(a.smin().wrapping_add(1), i64::MAX);
            }
        }
        _ => {}
    }
}
