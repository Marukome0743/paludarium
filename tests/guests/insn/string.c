/* rep movsq and rep stosq with DF=0, including zero counts. */
#include "insn.h"

static u64 src[40];
static u64 dst[40];

static void dump(const char *name, u64 count, u64 rdi, u64 rsi, u64 rcx) {
    report(name, count, rdi, rsi, rcx, 0, 0);
    for (u64 i = 0; i < 40; i++) {
        report_value("  ", dst[i]);
    }
}

int test_main(void) {
    static const u64 counts[] = {0, 1, 2, 7, 32};
    for (u64 c = 0; c < 5; c++) {
        for (u64 i = 0; i < 40; i++) {
            src[i] = vectors[i % NVEC] ^ i;
            dst[i] = 0xdddddddddddddddd;
        }
        u64 n = counts[c], *d = dst + 4, *s = src + 1;
        __asm__ volatile("rep movsq" : "+D"(d), "+S"(s), "+c"(n) : : "memory");
        dump("repmovsq", counts[c], (u64)(d - dst), (u64)(s - src), n);

        for (u64 i = 0; i < 40; i++) {
            dst[i] = 0xdddddddddddddddd;
        }
        n = counts[c];
        d = dst + 2;
        __asm__ volatile("rep stosq" : "+D"(d), "+c"(n) : "a"(vectors[c + 9]) : "memory");
        dump("repstosq", counts[c], (u64)(d - dst), 0, n);
    }
    flush_out();
    return 0;
}
