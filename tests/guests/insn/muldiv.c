/* imul (two- and three-operand) and div r64. */
#include "insn.h"

#define F_MUL (F_CF | F_OF) /* SF, ZF, AF, PF are undefined after imul */

#define IMUL3(label, sz, imm)                                                 \
    for (u64 i = 0; i < NVEC; i++) {                                          \
        u64 a = vectors[i], r = 0x5555555555555555UL, f, fi = 0;              \
        __asm__ volatile("push %[fi]\n\tpopfq\n\timul $" #imm ", %" sz        \
                         "[a], %" sz "[r]\n\tpushfq\n\tpop %[f]"              \
                         : [r] "+r"(r), [f] "=&r"(f)                          \
                         : [a] "r"(a), [fi] "r"(fi)                           \
                         : "cc", "memory");                                  \
        report(label, a, (u64)(imm), fi, r, f, F_MUL);                        \
    }

static const u64 dividend_high[] = {0, 1, 0x7f};

int test_main(void) {
    BIN_RR("imul64", "imul", "q", F_MUL)
    BIN_RR("imul32", "imul", "k", F_MUL)
    IMUL3("imul64i", "q", 10)
    IMUL3("imul64in", "q", -3)
    IMUL3("imul32i", "k", 1000)

    /* div r64: rdx:rax / src. Only non-faulting inputs (divisor above the
     * high half); all flags are undefined so none are compared. */
    for (u64 h = 0; h < 3; h++)
        for (u64 i = 0; i < NVEC; i++)
            for (u64 j = 0; j < NVEC; j++) {
                u64 d = vectors[j];
                if (d <= dividend_high[h]) {
                    continue;
                }
                u64 q = vectors[i], r = dividend_high[h];
                __asm__ volatile("div %[d]" : "+a"(q), "+d"(r) : [d] "r"(d) : "cc");
                report("div64", vectors[i], d, dividend_high[h], q, r, ~0UL);
            }
    flush_out();
    return 0;
}
