/* setcc for all 16 conditions, after cmp on vector pairs. */
#include "insn.h"

#define SETCC(cc)                                                             \
    for (u64 i = 0; i < NVEC; i++)                                            \
        for (u64 j = 0; j < NVEC; j++) {                                      \
            u64 a = vectors[i], b = vectors[j], r = 0xaaUL;                   \
            __asm__ volatile("cmp %[b], %[a]\n\tset" #cc " %b[r]"             \
                             : [r] "+r"(r)                                    \
                             : [a] "r"(a), [b] "r"(b)                         \
                             : "cc");                                        \
            report("set" #cc, a, b, 0, r, 0, 0);                              \
        }

#define CMOVCC(cc)                                                            \
    for (u64 i = 0; i < NVEC; i++)                                            \
        for (u64 j = 0; j < NVEC; j++) {                                      \
            u64 a = vectors[i], b = vectors[j];                               \
            u64 r64 = 0x1111111111111111UL, r32 = 0x2222222222222222UL;       \
            u64 rm = 0x3333333333333333UL, src = 0x4444444444444444UL;         \
            __asm__ volatile("cmp %[b], %[a]\n\t"                             \
                             "cmov" #cc " %[src], %[r64]\n\t"                 \
                             "cmov" #cc " %k[src], %k[r32]\n\t"               \
                             "cmov" #cc " %[m], %[rm]"                        \
                             : [r64] "+r"(r64), [r32] "+r"(r32), [rm] "+r"(rm) \
                             : [a] "r"(a), [b] "r"(b), [src] "r"(src),         \
                               [m] "m"(src)                                   \
                             : "cc");                                        \
            report("cmov" #cc, a, b, r64, r32, rm, ~0UL);                     \
        }

#define JCC(cc)                                                               \
    for (u64 i = 0; i < NVEC; i++)                                            \
        for (u64 j = 0; j < NVEC; j++) {                                      \
            u64 a = vectors[i], b = vectors[j], r;                            \
            __asm__ volatile("cmp %[b], %[a]\n\t"                             \
                             "mov $1, %[r]\n\t"                               \
                             "j" #cc " 1f\n\t"                                \
                             "mov $0, %[r]\n"                                 \
                             "1:"                                             \
                             : [r] "=&r"(r)                                   \
                             : [a] "r"(a), [b] "r"(b)                         \
                             : "cc");                                        \
            report("j" #cc, a, b, 0, r, 0, 0);                                \
        }

int test_main(void) {
    SETCC(o) SETCC(no) SETCC(b) SETCC(ae) SETCC(e) SETCC(ne) SETCC(be) SETCC(a) SETCC(s) SETCC(ns) SETCC(p) SETCC(np) SETCC(l) SETCC(ge) SETCC(le) SETCC(g)
    flush_out();
    return 0;
}
