//! Master's circular ranges (`struct cnum32` and `struct cnum64`,
//! `include/linux/cnum.h`, `kernel/bpf/cnum.c` and `cnum_defs.h`): an arc
//! on the circle of the values of a width, from `base` clockwise over
//! `size` more values, which holds a value's unsigned and signed ranges in
//! one.

macro_rules! cnum {
    ($name:ident, $u:ty, $s:ty) => {
        /// An arc of `size` values after `base`; `size` all ones but `base`
        /// too is the empty one.
        #[derive(Clone, Copy, Debug, PartialEq, Eq)]
        pub(crate) struct $name {
            pub(crate) base: $u,
            pub(crate) size: $u,
        }

        impl $name {
            /// Every value (`CNUM*_UNBOUNDED`).
            pub(crate) const UNBOUNDED: $name = $name {
                base: 0,
                size: <$u>::MAX,
            };
            /// No value (`CNUM*_EMPTY`).
            pub(crate) const EMPTY: $name = $name {
                base: <$u>::MAX,
                size: <$u>::MAX,
            };

            /// `cnum*_from_urange`.
            pub(crate) fn urange(min: $u, max: $u) -> $name {
                $name {
                    base: min,
                    size: max.wrapping_sub(min),
                }
            }

            /// `cnum*_from_srange`.
            pub(crate) fn srange(min: $s, max: $s) -> $name {
                let size = (max as $u).wrapping_sub(min as $u);
                let base = if size == <$u>::MAX { 0 } else { min as $u };
                $name { base, size }
            }

            /// `cnum*_is_empty`.
            pub(crate) fn is_empty(self) -> bool {
                self == $name::EMPTY
            }

            /// `cnum*_is_const`.
            pub(crate) fn is_const(self) -> bool {
                self.size == 0
            }

            /// `cnum*_contains`.
            pub(crate) fn contains(self, v: $u) -> bool {
                !self.is_empty() && v.wrapping_sub(self.base) <= self.size
            }

            /// `cnum*_urange_overflow`: the arc crosses from the largest
            /// unsigned value to 0.
            pub(crate) fn urange_overflow(self) -> bool {
                self.size > <$u>::MAX - self.base
            }

            /// `cnum*_srange_overflow`: the arc crosses from the largest
            /// signed value to the smallest.
            pub(crate) fn srange_overflow(self) -> bool {
                self.contains(<$s>::MAX as $u) && self.contains(<$s>::MIN as $u)
            }

            /// `cnum*_umin`.
            pub(crate) fn umin(self) -> $u {
                if self.urange_overflow() { 0 } else { self.base }
            }

            /// `cnum*_umax`.
            pub(crate) fn umax(self) -> $u {
                if self.urange_overflow() {
                    <$u>::MAX
                } else {
                    self.base + self.size
                }
            }

            /// `cnum*_smin`.
            pub(crate) fn smin(self) -> $s {
                if self.srange_overflow() {
                    <$s>::MIN
                } else {
                    self.base as $s
                }
            }

            /// `cnum*_smax`.
            pub(crate) fn smax(self) -> $s {
                if self.srange_overflow() {
                    <$s>::MAX
                } else {
                    self.base.wrapping_add(self.size) as $s
                }
            }

            /// `cnum*_intersect`: where the two arcs meet in two, the
            /// smaller arc.
            pub(crate) fn intersect(self, b: $name) -> $name {
                let (mut a, mut b) = (self, b);
                if a.is_empty() || b.is_empty() {
                    return $name::EMPTY;
                }
                if a.base > b.base {
                    core::mem::swap(&mut a, &mut b);
                }
                let dbase = b.base - a.base;
                let b1 = $name {
                    base: dbase,
                    size: b.size,
                };
                if b1.urange_overflow() {
                    if b1.base <= a.size {
                        if a.size <= b.size { a } else { b }
                    } else {
                        $name {
                            base: a.base,
                            size: a.size.min(b1.base.wrapping_add(b1.size)),
                        }
                    }
                } else if a.size >= b1.base {
                    $name {
                        base: b.base,
                        size: (a.size - dbase).min(b.size),
                    }
                } else {
                    $name::EMPTY
                }
            }

            /// `cnum*_intersect_with_urange`.
            pub(crate) fn intersect_urange(self, min: $u, max: $u) -> $name {
                self.intersect($name::urange(min, max))
            }

            /// `cnum*_intersect_with_srange`.
            pub(crate) fn intersect_srange(self, min: $s, max: $s) -> $name {
                self.intersect($name::srange(min, max))
            }

            /// `cnum*_normalize`: the whole circle starts at 0.
            fn normalize(mut self) -> $name {
                if self.size == <$u>::MAX {
                    self.base = 0;
                }
                self
            }

            /// `cnum*_union`: the smallest arc holding both, of the smaller
            /// base where two are as small.
            #[cfg_attr(not(test), allow(dead_code))]
            pub(crate) fn union(self, b: $name) -> $name {
                let a = self;
                if a.is_empty() {
                    return b;
                }
                if b.is_empty() {
                    return a;
                }
                let b1 = $name {
                    base: b.base.wrapping_sub(a.base),
                    size: b.size,
                }
                .normalize();
                let end = a.size.max(b1.base.wrapping_add(b1.size));
                if b1.urange_overflow() {
                    if b1.base <= a.size {
                        return $name::UNBOUNDED;
                    }
                    return $name {
                        base: b.base,
                        size: end.wrapping_sub(b1.base),
                    }
                    .normalize();
                }
                let mut ab = $name {
                    base: a.base,
                    size: end,
                };
                if b1.base <= a.size {
                    return ab.normalize();
                }
                let ba = $name {
                    base: b.base,
                    size: a.size.wrapping_sub(b1.base),
                };
                if ba.size < ab.size || (ba.size == ab.size && ba.base < ab.base) {
                    ab = ba;
                }
                ab.normalize()
            }

            /// `cnum*_add`.
            pub(crate) fn add(self, b: $name) -> $name {
                if self.is_empty() || b.is_empty() {
                    return $name::EMPTY;
                }
                if self.size > <$u>::MAX - b.size {
                    $name::UNBOUNDED
                } else {
                    $name {
                        base: self.base.wrapping_add(b.base),
                        size: self.size + b.size,
                    }
                    .normalize()
                }
            }

            /// `cnum*_negate`.
            pub(crate) fn negate(self) -> $name {
                if self.is_empty() {
                    return $name::EMPTY;
                }
                $name {
                    base: self.base.wrapping_add(self.size).wrapping_neg(),
                    size: self.size,
                }
                .normalize()
            }
        }
    };
}

cnum!(Cnum32, u32, i32);
cnum!(Cnum64, u64, i64);

impl Cnum32 {
    /// `cnum32_from_cnum64`: the low 32 bits of the values.
    pub(crate) fn from64(c: Cnum64) -> Cnum32 {
        if c.is_empty() {
            Cnum32::EMPTY
        } else if c.size >= u64::from(u32::MAX) {
            Cnum32::UNBOUNDED
        } else {
            Cnum32 {
                base: c.base as u32,
                size: c.size as u32,
            }
        }
    }
}

impl Cnum64 {
    /// `cnum64_cnum32_intersect`: the values of `self` whose low 32 bits
    /// are in `b`, as one arc.
    pub(crate) fn intersect32(self, b: Cnum32) -> Cnum64 {
        let a = self;
        if a.is_empty() || b.is_empty() {
            return Cnum64::EMPTY;
        }
        let b1 = Cnum32 {
            base: b.base.wrapping_sub(a.base as u32),
            size: b.size,
        };
        let mut t = a;
        let low = a.size as u32;
        if b1.urange_overflow() {
            let b1_max = b1.base.wrapping_add(b1.size);
            if low > b1_max && low < b1.base {
                t.size -= u64::from(low - b1_max);
            }
        } else {
            if t.size < u64::from(b1.base) {
                return Cnum64::EMPTY;
            }
            t.base = t.base.wrapping_add(u64::from(b1.base));
            t.size -= u64::from(b1.base);
            let b1_max = u64::from(b1.base) + u64::from(b1.size);
            let d = if low < b1.base {
                u64::from(low) + ((1u64 << 32) - b1_max)
            } else if u64::from(low) >= b1_max {
                u64::from(low) - b1_max
            } else {
                0
            };
            if t.size < d {
                return Cnum64::EMPTY;
            }
            t.size -= d;
        }
        t
    }

    /// `cnum64_intersect_linear`: the values of `self` that are `base`
    /// more than a multiple of `step`, as signed values.
    pub(crate) fn intersect_linear(self, base: u16, step: u16) -> Cnum64 {
        if step <= 1 || self.is_empty() || self.srange_overflow() {
            return self;
        }
        let (smin, smax) = (self.smin(), self.smax());
        let step64 = i64::from(step);
        // imod: the remainder that is not negative.
        let imod = |a: i64, b: i64| a.rem_euclid(b);
        let d = imod(i64::from(base) - imod(smin, step64), step64) as u16;
        if (smax as u64).wrapping_sub(smin as u64) < u64::from(d) {
            return Cnum64::EMPTY;
        }
        let lo = smin + i64::from(d);
        let d = imod(imod(smax, step64) - i64::from(base), step64) as u16;
        let hi = smax - i64::from(d);
        Cnum64::srange(lo, hi)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The values of a small arc, by brute force over 8-bit-like widths of
    /// a 32-bit cnum near the edges.
    fn members(c: Cnum32, of: &[u32]) -> Vec<u32> {
        of.iter().copied().filter(|&v| c.contains(v)).collect()
    }

    #[test]
    fn an_arc_s_bounds_are_its_ends_unless_it_crosses_them() {
        let c = Cnum32::urange(5, 9);
        assert_eq!((c.umin(), c.umax(), c.smin(), c.smax()), (5, 9, 5, 9));
        let c = Cnum32::srange(-1, 0);
        assert_eq!(
            c,
            Cnum32 {
                base: u32::MAX,
                size: 1
            }
        );
        assert_eq!(
            (c.umin(), c.umax(), c.smin(), c.smax()),
            (0, u32::MAX, -1, 0)
        );
        let c = Cnum32::urange(i32::MAX as u32, i32::MIN as u32);
        assert_eq!((c.smin(), c.smax()), (i32::MIN, i32::MAX));
        assert_eq!(Cnum32::srange(i32::MIN, i32::MAX), Cnum32::UNBOUNDED);
    }

    #[test]
    fn an_intersection_holds_every_value_of_both() {
        let edges: Vec<u32> = (0..8)
            .chain(u32::MAX - 7..=u32::MAX)
            .chain((i32::MAX as u32 - 3)..=(i32::MIN as u32 + 3))
            .collect();
        let arcs: Vec<Cnum32> = edges
            .iter()
            .flat_map(|&b| {
                [0, 1, 3, 6, u32::MAX - 2, u32::MAX].map(|s| Cnum32 { base: b, size: s })
            })
            .filter(|c| !c.is_empty())
            .collect();
        for &a in &arcs {
            for &b in &arcs {
                let i = a.intersect(b);
                let u = a.union(b);
                for v in members(a, &edges) {
                    assert!(u.contains(v), "{a:?} | {b:?} = {u:?} misses {v}");
                    if b.contains(v) {
                        assert!(i.contains(v), "{a:?} & {b:?} = {i:?} misses {v}");
                    }
                }
                for v in members(b, &edges) {
                    assert!(u.contains(v), "{a:?} | {b:?} = {u:?} misses {v}");
                }
                let s = a.add(b);
                for x in members(a, &edges) {
                    for y in members(b, &edges) {
                        assert!(s.contains(x.wrapping_add(y)), "{a:?} + {b:?} = {s:?}");
                    }
                    assert!(a.negate().contains(x.wrapping_neg()));
                }
            }
        }
    }

    #[test]
    fn the_64_bit_arc_keeps_the_values_whose_low_bits_are_in_the_32_bit_one() {
        let a = Cnum64::urange(0, 0x3_0000_0010);
        let b = Cnum32::urange(0x20, 0x30);
        let t = a.intersect32(b);
        assert_eq!((t.umin(), t.umax()), (0x20, 0x2_0000_0030));
        let t = Cnum64::urange(0x40, 0x50).intersect32(b);
        assert!(t.is_empty());
        let t = Cnum64::urange(0x1_0000_0000, 0x1_0000_0040).intersect32(b);
        assert_eq!((t.umin(), t.umax()), (0x1_0000_0020, 0x1_0000_0030));
    }

    #[test]
    fn a_linear_intersection_rounds_to_the_step() {
        let t = Cnum64::srange(-7, 21).intersect_linear(2, 4);
        assert_eq!((t.smin(), t.smax()), (-6, 18));
        assert!(Cnum64::srange(5, 6).intersect_linear(3, 4).is_empty());
        assert_eq!(Cnum64::UNBOUNDED.intersect_linear(1, 2), Cnum64::UNBOUNDED);
    }
}
