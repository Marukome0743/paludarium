//! What the verifier decides of a corpus of generated programs, pinned in
//! `decisions.txt`: one line for each program, its number and either
//! `ok` and the instructions processed, or the errno and the log's line.
//!
//! The programs are made for the parts a scalar's bounds decide: values
//! the verifier knows, values of the context it does not, operations on
//! them, conditional jumps over a read through a scalar (which is
//! refused wherever a path reaches it), and a round trip through the
//! stack. A change of what the verifier knows shows in this file's diff,
//! program by program.
//!
//! `PALUDARIUM_BLESS=1 cargo test -p paludarium-kernel bpf_verifier::pins`
//! writes the file anew.
use super::*;

/// The number of programs.
const PROGRAMS: usize = 3000;

/// splitmix64, seeded with the program's number.
struct Rng(u64);

impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        z ^ (z >> 31)
    }
    fn below(&mut self, n: usize) -> usize {
        (self.next() % n as u64) as usize
    }
    fn pick<T: Copy>(&mut self, of: &[T]) -> T {
        of[self.below(of.len())]
    }
}

fn i(code: u8, dst: u8, src: u8, off: i16, imm: i32) -> Insn {
    Insn {
        code,
        dst,
        src,
        off,
        imm,
    }
}

/// Immediates at the edges of the bounds: of a byte, of a sign, of the
/// shifts' widths, of 32 bits.
const IMMS: [i32; 20] = [
    0,
    1,
    2,
    3,
    7,
    8,
    15,
    16,
    31,
    32,
    63,
    64,
    255,
    256,
    0xffff,
    -1,
    -8,
    -256,
    i32::MAX,
    i32::MIN,
];

/// The context's fields a program reads as scalars: `len`, `pkt_type`,
/// `mark`, `cb[0]`, `cb[1]`.
const CTX_FIELDS: [i16; 5] = [0, 4, 8, 48, 52];

/// The registers the body works on; R1 keeps the context.
const WORK: [u8; 4] = [2, 3, 4, 5];

/// Program `n`: `r0 = 0`, each working register set, a body, and `exit`.
fn program(n: usize) -> Vec<Insn> {
    let mut rng = Rng(n as u64);
    let mut p = vec![i(0xb7, 0, 0, 0, 0)];
    for r in WORK {
        p.push(match rng.below(3) {
            0 => i(0xb7, r, 0, 0, rng.pick(&IMMS)),
            1 => i(0xb4, r, 0, 0, rng.pick(&IMMS)),
            _ => i(0x61, r, 1, rng.pick(&CTX_FIELDS), 0),
        });
    }
    let body = 3 + rng.below(10);
    let start = p.len();
    for _ in 0..body {
        let dst = rng.pick(&WORK);
        let src = rng.pick(&WORK);
        let wide = rng.below(2) == 0;
        let x = rng.below(3) == 0;
        let imm = rng.pick(&IMMS);
        let insn = match rng.below(10) {
            // An operation.
            0..=3 => {
                let op = rng.pick(&alu::BINARY);
                let op = if rng.below(12) == 0 { alu::NEG } else { op };
                let class = if wide { class::ALU64 } else { class::ALU };
                // Shifts by an immediate in range, so that most programs
                // get past them.
                let imm = if matches!(op, alu::LSH | alu::RSH | alu::ARSH) {
                    imm & if wide { 63 } else { 31 }
                } else {
                    imm
                };
                match op {
                    alu::NEG => i(class | op, dst, 0, 0, 0),
                    _ if x => i(class | op | X, dst, src, 0, 0),
                    _ => i(class | op, dst, 0, 0, imm),
                }
            }
            // A conditional jump; its target is fixed below.
            4..=6 => {
                let op = rng.pick(&jmp::CONDITIONS);
                let class = if wide { class::JMP } else { class::JMP32 };
                if x {
                    i(class | op | X, dst, src, 0, 0)
                } else {
                    i(class | op, dst, 0, 0, imm)
                }
            }
            // A read through a scalar, refused where a path reaches it.
            7 => i(0x71, 0, dst, 0, 0),
            // A spill and a fill, whole or of the low 32 bits.
            8 => {
                p.push(i(0x7b, 10, src, -8, 0));
                if rng.below(2) == 0 {
                    i(0x79, dst, 10, -8, 0)
                } else {
                    i(0x61, dst, 10, -8, 0)
                }
            }
            // The return value.
            _ => i(0xbf, 0, src, 0, 0),
        };
        p.push(insn);
    }
    p.push(i(0x95, 0, 0, 0, 0));
    // Each jump goes 0 to 3 instructions forward, the exit at most.
    let last = p.len() - 1;
    for (at, insn) in p.iter_mut().enumerate().take(last).skip(start) {
        if matches!(insn.class(), class::JMP | class::JMP32) {
            let room = last - at - 1;
            insn.off = rng.below(room.min(3) + 1) as i16;
        }
    }
    p
}

/// What the verifier decides of `insns`, as `decisions.txt` has it.
fn decision(insns: &[Insn]) -> String {
    let mut no_maps = |_: i32| Err(Errno::EBADF);
    match check(insns, Options::default(), &mut no_maps) {
        Ok(v) => format!("ok {}", v.processed),
        Err(r) => format!("{} {}", r.errno.0, r.line),
    }
}

#[test]
fn the_corpus_is_decided_as_pinned() {
    let got: String = (0..PROGRAMS)
        .map(|n| format!("{n:04} {}\n", decision(&program(n))))
        .collect();
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/src/bpf_verifier/decisions.txt"
    );
    if std::env::var_os("PALUDARIUM_BLESS").is_some() {
        std::fs::write(path, &got).unwrap();
        return;
    }
    let pinned = include_str!("decisions.txt");
    for (n, (got, pinned)) in got.lines().zip(pinned.lines()).enumerate() {
        assert_eq!(got, pinned, "program {n}: {:?}", program(n));
    }
    assert_eq!(got.lines().count(), pinned.lines().count());
}
