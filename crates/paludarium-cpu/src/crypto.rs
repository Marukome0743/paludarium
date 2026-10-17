//! Portable implementations of the explicitly assigned legacy crypto forms.
use paludarium_decoder::Mnemonic as M;

fn multiply(mut a: u8, mut b: u8) -> u8 {
    let mut out = 0;
    for _ in 0..8 {
        if b & 1 != 0 {
            out ^= a;
        }
        a = (a << 1) ^ if a & 128 != 0 { 0x1b } else { 0 };
        b >>= 1;
    }
    out
}
fn substitute(value: u8) -> u8 {
    let mut inverse = 1;
    let mut base = value;
    let mut exponent = 254;
    while exponent != 0 {
        if exponent & 1 != 0 {
            inverse = multiply(inverse, base);
        }
        base = multiply(base, base);
        exponent >>= 1;
    }
    inverse
        ^ inverse.rotate_left(1)
        ^ inverse.rotate_left(2)
        ^ inverse.rotate_left(3)
        ^ inverse.rotate_left(4)
        ^ 0x63
}
fn words(value: u128) -> [u32; 4] {
    core::array::from_fn(|n| (value >> (n * 32)) as u32)
}
fn join(value: [u32; 4]) -> u128 {
    value
        .into_iter()
        .enumerate()
        .fold(0, |out, (n, word)| out | (u128::from(word) << (n * 32)))
}
fn sigma0(x: u32) -> u32 {
    x.rotate_right(7) ^ x.rotate_right(18) ^ (x >> 3)
}
fn sigma1(x: u32) -> u32 {
    x.rotate_right(17) ^ x.rotate_right(19) ^ (x >> 10)
}

pub(crate) fn execute(m: M, a: u128, b: u128, implicit: u128, selector: u8) -> Option<u128> {
    Some(match m {
        M::Aesenc | M::Aesenclast => {
            let input = a.to_le_bytes();
            let mut state = [0; 16];
            for column in 0..4 {
                for row in 0..4 {
                    state[column * 4 + row] = substitute(input[((column + row) % 4) * 4 + row]);
                }
            }
            if m == M::Aesenc {
                for column in state.as_chunks_mut::<4>().0 {
                    let [x, y, z, w] = [column[0], column[1], column[2], column[3]];
                    column[0] = multiply(x, 2) ^ multiply(y, 3) ^ z ^ w;
                    column[1] = x ^ multiply(y, 2) ^ multiply(z, 3) ^ w;
                    column[2] = x ^ y ^ multiply(z, 2) ^ multiply(w, 3);
                    column[3] = multiply(x, 3) ^ y ^ z ^ multiply(w, 2);
                }
            }
            u128::from_le_bytes(state) ^ b
        }
        M::Pclmulqdq => {
            if !matches!(selector & 0x11, 0 | 0x11) {
                return None;
            }
            let left = (a >> (u32::from(selector & 1) * 64)) as u64;
            let right = (b >> (u32::from((selector >> 4) & 1) * 64)) as u64;
            let mut product = 0;
            for bit in 0..64 {
                if right & (1u64 << bit) != 0 {
                    product ^= u128::from(left) << bit;
                }
            }
            product
        }
        M::Sha256msg1 => {
            let x = words(a);
            let y = words(b);
            join([
                x[0].wrapping_add(sigma0(x[1])),
                x[1].wrapping_add(sigma0(x[2])),
                x[2].wrapping_add(sigma0(x[3])),
                x[3].wrapping_add(sigma0(y[0])),
            ])
        }
        M::Sha256msg2 => {
            let x = words(a);
            let y = words(b);
            let mut out = [0; 4];
            out[0] = x[0].wrapping_add(sigma1(y[2]));
            out[1] = x[1].wrapping_add(sigma1(y[3]));
            out[2] = x[2].wrapping_add(sigma1(out[0]));
            out[3] = x[3].wrapping_add(sigma1(out[1]));
            join(out)
        }
        M::Sha256rnds2 => {
            let x = words(a);
            let y = words(b);
            let wk = words(implicit);
            let [mut h, mut g, mut d, mut c] = x;
            let [mut f, mut e, mut bb, mut aa] = y;
            for round in wk.iter().take(2) {
                let t1 = h
                    .wrapping_add(e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25))
                    .wrapping_add((e & f) ^ ((!e) & g))
                    .wrapping_add(*round);
                let t2 = (aa.rotate_right(2) ^ aa.rotate_right(13) ^ aa.rotate_right(22))
                    .wrapping_add((aa & bb) ^ (aa & c) ^ (bb & c));
                h = g;
                g = f;
                f = e;
                e = d.wrapping_add(t1);
                d = c;
                c = bb;
                bb = aa;
                aa = t1.wrapping_add(t2);
            }
            join([f, e, bb, aa])
        }
        _ => return None,
    })
}
