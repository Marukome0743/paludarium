//! Builds tiny static ELF executables in memory, for tests and fuzzing of
//! the crates above the loader (test data is built in code, never stored).

/// Address of the code segment of [`tiny_exec`].
pub const CODE_ADDR: u64 = 0x40_1000;
/// Address of the data segment of [`tiny_exec`].
pub const DATA_ADDR: u64 = 0x40_2000;

/// An `ET_EXEC` image with `code` (R+X) at [`CODE_ADDR`], entry at its
/// start, and `data` (R+W) at [`DATA_ADDR`].
#[must_use]
pub fn tiny_exec(code: &[u8], data: &[u8]) -> Vec<u8> {
    const PAGE: usize = 0x1000;
    let segments: [(u32, u64, &[u8]); 2] = [(5, CODE_ADDR, code), (6, DATA_ADDR, data)];
    let mut out = vec![0u8; 64];
    out[..4].copy_from_slice(b"\x7fELF");
    out[4] = 2;
    out[5] = 1;
    out[6] = 1;
    out[16..18].copy_from_slice(&2u16.to_le_bytes());
    out[18..20].copy_from_slice(&62u16.to_le_bytes());
    out[20..24].copy_from_slice(&1u32.to_le_bytes());
    out[24..32].copy_from_slice(&CODE_ADDR.to_le_bytes());
    out[32..40].copy_from_slice(&64u64.to_le_bytes());
    out[52..54].copy_from_slice(&64u16.to_le_bytes());
    out[54..56].copy_from_slice(&56u16.to_le_bytes());
    out[56..58].copy_from_slice(&2u16.to_le_bytes());
    let mut offset = PAGE;
    let mut placed = Vec::new();
    for (flags, vaddr, bytes) in segments {
        let size = bytes.len() as u64;
        let mut ph = [0u8; 56];
        ph[0..4].copy_from_slice(&1u32.to_le_bytes());
        ph[4..8].copy_from_slice(&flags.to_le_bytes());
        ph[8..16].copy_from_slice(&(offset as u64).to_le_bytes());
        ph[16..24].copy_from_slice(&vaddr.to_le_bytes());
        ph[24..32].copy_from_slice(&vaddr.to_le_bytes());
        ph[32..40].copy_from_slice(&size.to_le_bytes());
        ph[40..48].copy_from_slice(&size.max(1).to_le_bytes());
        ph[48..56].copy_from_slice(&(PAGE as u64).to_le_bytes());
        out.extend_from_slice(&ph);
        placed.push((offset, bytes));
        offset += bytes.len().div_ceil(PAGE).max(1) * PAGE;
    }
    for (at, bytes) in placed {
        out.resize(at, 0);
        out.extend_from_slice(bytes);
    }
    out
}
