//! Deterministic virtual CPU identity; never forwards host CPUID.
pub(crate) fn values(leaf: u32, _subleaf: u32) -> [u32; 4] {
    match leaf {
        0 => [
            7,
            u32::from_le_bytes(*b"Palu"),
            u32::from_le_bytes(*b"umVM"),
            u32::from_le_bytes(*b"dari"),
        ],
        0x8000_0000 => [0x8000_0001, 0, 0, 0],
        0x8000_0001 => [0, 0, 0, 1 << 29],
        // Partial target subsets never advertise a complete feature family.
        _ => [0; 4],
    }
}
