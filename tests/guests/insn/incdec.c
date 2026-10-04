/* inc, dec, neg, not: register and memory forms. */
#include "insn.h"

int test_main(void) {
    UN_R("inc64", "inc", "q", F_ARITH)
    UN_R("inc32", "inc", "k", F_ARITH)
    UN_M("inc64m", "incq", F_ARITH)
    UN_R("dec64", "dec", "q", F_ARITH)
    UN_M("dec32m", "decl", F_ARITH)
    UN_R("neg64", "neg", "q", F_ARITH)
    UN_R("neg32", "neg", "k", F_ARITH)
    UN_R("not64", "not", "q", F_ARITH)
    UN_R("not32", "not", "k", F_ARITH)
    flush_out();
    return 0;
}
