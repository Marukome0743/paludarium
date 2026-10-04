/* lock cmpxchg (32/64-bit, success and failure), lock or (immediate and
 * register), xchg with memory. Single-threaded: checks the values and flags. */
#include "insn.h"

int test_main(void) {
    for (u64 i = 0; i < NVEC; i++)
        for (u64 j = 0; j < NVEC; j += 2) {
            u64 m = vectors[i], expect = vectors[j], f;
            u64 rax = expect, src = 0x0f0f0f0f0f0f0f0fUL;
            __asm__ volatile("lock cmpxchg %[s], %[m]\n\tpushfq\n\tpop %[f]"
                             : [m] "+m"(m), "+a"(rax), [f] "=&r"(f)
                             : [s] "r"(src)
                             : "cc", "memory");
            report("cmpxchg64", vectors[i], expect, rax, m, f, F_ARITH);

            u64 m32 = vectors[i];
            rax = expect;
            __asm__ volatile("lock cmpxchg %k[s], %k[m]\n\tpushfq\n\tpop %[f]"
                             : [m] "+m"(m32), "+a"(rax), [f] "=&r"(f)
                             : [s] "r"(src)
                             : "cc", "memory");
            report("cmpxchg32", vectors[i], expect, rax, m32, f, F_ARITH);
        }
    /* Equal values take the success path. */
    for (u64 i = 0; i < NVEC; i++) {
        u64 m = vectors[i], rax = vectors[i], f;
        __asm__ volatile("lock cmpxchg %[s], %[m]\n\tpushfq\n\tpop %[f]"
                         : [m] "+m"(m), "+a"(rax), [f] "=&r"(f)
                         : [s] "r"(0x1234UL)
                         : "cc", "memory");
        report("cmpxchg64eq", vectors[i], 0, rax, m, f, F_ARITH);
    }
    for (u64 i = 0; i < NVEC; i++) {
        u64 m = vectors[i], f;
        __asm__ volatile("lock orl $0x80000001, %k[m]\n\tpushfq\n\tpop %[f]"
                         : [m] "+m"(m), [f] "=&r"(f)
                         :
                         : "cc", "memory");
        report("lockor32mi", vectors[i], 0, 0, m, f, F_LOGIC);
        m = vectors[i];
        __asm__ volatile("lock or %[s], %[m]\n\tpushfq\n\tpop %[f]"
                         : [m] "+m"(m), [f] "=&r"(f)
                         : [s] "r"(vectors[NVEC - 1 - i])
                         : "cc", "memory");
        report("lockor64mr", vectors[i], vectors[NVEC - 1 - i], 0, m, f, F_LOGIC);
    }
    flush_out();
    return 0;
}
