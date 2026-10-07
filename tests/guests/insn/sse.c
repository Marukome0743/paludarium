/* The SSE instructions executed by the hello-world guests: movaps, movups
 * (load and store, aligned and unaligned memory), pxor, xorps, movq,
 * punpcklqdq. */
#include "insn.h"

static u8 buffer[80] __attribute__((aligned(16)));

static void dump(const char *name) {
    for (u64 i = 0; i < 80; i += 8) {
        u64 v = 0;
        for (u64 b = 0; b < 8; b++) {
            v |= (u64)buffer[i + b] << (8 * b);
        }
        report_value(name, v);
    }
}

int test_main(void) {
    for (u64 i = 0; i < 80; i++) {
        buffer[i] = (u8)(i * 37 + 11);
    }
    /* movups unaligned load, movaps aligned store. */
    __asm__ volatile("movups 3(%[b]), %%xmm0\n\tmovaps %%xmm0, 32(%[b])"
                     : : [b] "r"(buffer) : "xmm0", "memory");
    dump("movups-movaps");
    /* movaps aligned load, movups unaligned store. */
    __asm__ volatile("movaps 16(%[b]), %%xmm1\n\tmovups %%xmm1, 49(%[b])"
                     : : [b] "r"(buffer) : "xmm1", "memory");
    dump("movaps-movups");
    /* pxor and xorps of two registers, and zeroing idioms. */
    __asm__ volatile("movups 0(%[b]), %%xmm2\n\t"
                     "movups 7(%[b]), %%xmm3\n\t"
                     "pxor %%xmm3, %%xmm2\n\t"
                     "movups %%xmm2, 0(%[b])\n\t"
                     "movups 20(%[b]), %%xmm4\n\t"
                     "xorps %%xmm2, %%xmm4\n\t"
                     "movups %%xmm4, 20(%[b])\n\t"
                     "pxor %%xmm5, %%xmm5\n\t"
                     "movups %%xmm5, 64(%[b])\n\t"
                     "xorps %%xmm6, %%xmm6\n\t"
                     "movups %%xmm6, 40(%[b])"
                     : : [b] "r"(buffer) : "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "memory");
    dump("pxor-xorps");
    /* MOVQ clears the high qword; PUNPCKLQDQ interleaves only low qwords.
     * Distinct inputs and prefilled XMM registers expose stale high halves. */
    u64 low = 0x0123456789abcdefUL, other = 0xfedcba9876543210UL;
    __asm__ volatile("movups 0(%[b]), %%xmm0\n\t"
                     "movq %[low], %%xmm0\n\t"
                     "movups %%xmm0, 0(%[b])\n\t"
                     "movq %[other], %%xmm1\n\t"
                     "punpcklqdq %%xmm1, %%xmm0\n\t"
                     "movups %%xmm0, 16(%[b])\n\t"
                     "punpcklqdq %%xmm0, %%xmm0\n\t"
                     "movups %%xmm0, 32(%[b])"
                     : : [b] "r"(buffer), [low] "r"(low), [other] "r"(other)
                     : "xmm0", "xmm1", "memory");
    dump("movq-punpcklqdq");
    flush_out();
    return 0;
}
