/* add, sub, and, or, xor: register, immediate and memory forms. */
#include "insn.h"

int test_main(void) {
    BIN_RR("add64", "add", "q", F_ARITH)
    BIN_RR("add32", "add", "k", F_ARITH)
    BIN_RR("add16", "add", "w", F_ARITH)
    BIN_RR("add8", "add", "b", F_ARITH)
    BIN_RI("add64i8", "addq", "q", "8", F_ARITH)
    BIN_RI("add64i32", "addq", "q", "0x12345678", F_ARITH)
    BIN_RI("add64in", "addq", "q", "-0x80000000", F_ARITH)
    BIN_RI("add32i", "addl", "k", "0x7f", F_ARITH)
    BIN_MR("add64mr", "addq", "q", F_ARITH)
    BIN_RM("add64rm", "addq", "q", F_ARITH)
    BIN_MI("add32mi", "addl", "0x80", F_ARITH)

    BIN_RR("sub64", "sub", "q", F_ARITH)
    BIN_RR("sub32", "sub", "k", F_ARITH)
    BIN_RI("sub64i", "subq", "q", "0x10", F_ARITH)
    BIN_RI("sub32i", "subl", "k", "-1", F_ARITH)
    BIN_MR("sub64mr", "subq", "q", F_ARITH)
    BIN_RM("sub64rm", "subq", "q", F_ARITH)
    BIN_MI("sub64mi", "subq", "0x7fffffff", F_ARITH)

    BIN_RR("and64", "and", "q", F_LOGIC)
    BIN_RR("and32", "and", "k", F_LOGIC)
    BIN_RI("and64i", "andq", "q", "-16", F_LOGIC)
    BIN_RI("and32i", "andl", "k", "0xff00", F_LOGIC)
    BIN_RI("and16i", "andw", "w", "0x7ff0", F_LOGIC)

    BIN_RR("or64", "or", "q", F_LOGIC)
    BIN_RR("or32", "or", "k", F_LOGIC)
    BIN_RI("or32i", "orl", "k", "0x80000000", F_LOGIC)

    BIN_RR("xor64", "xor", "q", F_LOGIC)
    BIN_RR("xor32", "xor", "k", F_LOGIC)
    flush_out();
    return 0;
}
