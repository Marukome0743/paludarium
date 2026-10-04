/* cmp, test: register, immediate and memory forms. */
#include "insn.h"

int test_main(void) {
    BIN_RR("cmp64", "cmp", "q", F_ARITH)
    BIN_RR("cmp32", "cmp", "k", F_ARITH)
    BIN_RR("cmp16", "cmp", "w", F_ARITH)
    BIN_RR("cmp8", "cmp", "b", F_ARITH)
    BIN_RI("cmp64i", "cmpq", "q", "-1", F_ARITH)
    BIN_RI("cmp32i", "cmpl", "k", "0x80", F_ARITH)
    BIN_RI("cmp16i", "cmpw", "w", "0x7ff", F_ARITH)
    BIN_RI("cmp8i", "cmpb", "b", "0x7f", F_ARITH)
    BIN_MR("cmp64mr", "cmpq", "q", F_ARITH)
    BIN_RM("cmp64rm", "cmpq", "q", F_ARITH)
    BIN_MR("cmp8mr", "cmpb", "b", F_ARITH)
    BIN_MI("cmp64mi", "cmpq", "0x10", F_ARITH)
    BIN_MI("cmp8mi", "cmpb", "0x2f", F_ARITH)
    BIN_MI("cmp32mi", "cmpl", "-2", F_ARITH)
    BIN_RR("test64", "test", "q", F_LOGIC)
    BIN_RR("test32", "test", "k", F_LOGIC)
    BIN_RR("test16", "test", "w", F_LOGIC)
    BIN_RR("test8", "test", "b", F_LOGIC)
    BIN_RI("test64i", "testq", "q", "-0x80000000", F_LOGIC)
    BIN_RI("test32i", "testl", "k", "0x100", F_LOGIC)
    BIN_RI("test8i", "testb", "b", "0x81", F_LOGIC)
    BIN_MI("test8mi", "testb", "4", F_LOGIC)
    BIN_MI("test64mi", "testq", "-0x100", F_LOGIC)
    flush_out();
    return 0;
}
