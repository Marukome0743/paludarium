/* bt r, r: CF is the selected bit; ZF unaffected; OF SF AF PF undefined. */
#include "insn.h"

int test_main(void) {
    BIN_RR("bt32", "bt", "k", F_CF | F_ZF)
    BIN_RR("bt64", "bt", "q", F_CF | F_ZF)
    flush_out();
    return 0;
}
