/* shl, shr, sar by immediate and by cl, 8/16/32/64-bit. */
#include "insn.h"

/* Flags defined after a shift by the masked count `c` of a `w`-bit operand:
 * count 0 changes nothing; AF is undefined; OF is defined only for count 1;
 * CF is undefined when the count reaches the operand width. */
static u64 shift_mask(u64 c, u64 w) {
    if (c == 0) {
        return F_ARITH;
    }
    u64 m = F_CF | F_PF | F_ZF | F_SF;
    if (c == 1) {
        m |= F_OF;
    }
    if (c >= w) {
        m &= ~F_CF;
    }
    return m;
}

static const u64 counts[] = {0, 1, 2, 7, 8, 15, 16, 31, 32, 33, 63, 64, 65};
#define NCOUNT (sizeof counts / sizeof counts[0])

#define SHIFT_CL(label, op, sz, w, cmask)                                     \
    for (u64 i = 0; i < NVEC; i++)                                            \
        for (u64 j = 0; j < NCOUNT; j++)                                      \
            for (u64 k = 0; k < NFIN; k++) {                                  \
                u64 a = vectors[i], c = counts[j], f, fi = flag_inputs[k];    \
                __asm__ volatile("push %[fi]\n\tpopfq\n\t" op " %%cl, %" sz   \
                                 "[a]\n\tpushfq\n\tpop %[f]"                  \
                                 : [a] "+r"(a), [f] "=&r"(f)                  \
                                 : "c"(c), [fi] "r"(fi)                       \
                                 : "cc", "memory");                          \
                report(label, vectors[i], c, fi, a, f,                        \
                       shift_mask(c & (cmask), w));                           \
            }

#define SHIFT_I(label, op, sz, cnt, w, cmask)                                 \
    for (u64 i = 0; i < NVEC; i++)                                            \
        for (u64 k = 0; k < NFIN; k++) {                                      \
            u64 a = vectors[i], f, fi = flag_inputs[k];                       \
            __asm__ volatile("push %[fi]\n\tpopfq\n\t" op " $" #cnt ", %" sz  \
                             "[a]\n\tpushfq\n\tpop %[f]"                      \
                             : [a] "+r"(a), [f] "=&r"(f)                      \
                             : [fi] "r"(fi)                                   \
                             : "cc", "memory");                              \
            report(label, vectors[i], cnt, fi, a, f,                          \
                   shift_mask((cnt) & (cmask), w));                           \
        }

int test_main(void) {
    SHIFT_CL("shl64cl", "shl", "q", 64, 63)
    SHIFT_CL("shl32cl", "shl", "k", 32, 31)
    SHIFT_CL("shr64cl", "shr", "q", 64, 63)
    SHIFT_CL("sar64cl", "sar", "q", 64, 63)
    SHIFT_CL("shr32cl", "shr", "k", 32, 31)
    SHIFT_I("shl32i1", "shl", "k", 1, 32, 31)
    SHIFT_I("shl32i4", "shl", "k", 4, 32, 31)
    SHIFT_I("shl64i12", "shl", "q", 12, 64, 63)
    SHIFT_I("shr64i1", "shr", "q", 1, 64, 63)
    SHIFT_I("shr64i63", "shr", "q", 63, 64, 63)
    SHIFT_I("shr32i3", "shr", "k", 3, 32, 31)
    SHIFT_I("shr16i1", "shr", "w", 1, 16, 31)
    SHIFT_I("shr16i9", "shr", "w", 9, 16, 31)
    SHIFT_I("shr8i1", "shr", "b", 1, 8, 31)
    SHIFT_I("shr8i5", "shr", "b", 5, 8, 31)
    SHIFT_I("sar32i1", "sar", "k", 1, 32, 31)
    SHIFT_I("sar32i31", "sar", "k", 31, 32, 31)
    SHIFT_I("sar64i3", "sar", "q", 3, 64, 63)
    flush_out();
    return 0;
}
