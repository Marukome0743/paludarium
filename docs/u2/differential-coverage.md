# U2 差分テスト対応表

検証済み：差分実行ごとに Linux native の期待出力を再生成する。`diff_u2` は35件、`parallel_u2` は外側の時間上限付き10件を実行した。追加で棚卸しした15整数命令群（当初の12候補と LEAVE/PUSHF/POPF の word 形式）はすべて native ケースに対応する。15/15 は命令群の対応数であり、全フォーム・全経路の割合ではない。U1 の既存66/66対応も harness coverage::tests で保持する。

| 命令・検証する条件 | 実行した guest・テストの対応 |
|---|---|
| ADD/ADC/SUB/SBB/AND/OR/XOR/CMP/TEST;8/16/32/64,carry/borrow/overflow | u2_alu/u2_cmptest and native insn/alu.c,cmptest.c |
| INC/DEC/NEG/NOT;partial registerとCF保持 | u2_incdec,insn/incdec.c;LOCK forms u2_control_forms |
| MOV/MOVSX/MOVSXD/MOVZX/LEA/XCHG;high8/REX/RIP/FS/GS | u2_move,insn/mov.c;internal decoder addressing cases |
| MUL/IMUL/DIV/IDIV;暗黙registerと商の境界 | u2_muldiv;u2_div_zero/u2_div_overflow/u2_idiv_zero/u2_idiv_overflow signal contexts |
| SHL/SHR/SAR/ROL/ROR/RCL/RCR;8/16/32/64,count0/1/boundaries/large masks | u2_shift,u2_integer_forms;insn/shift.c,u2-integer.c |
| SHLD/SHRD;16/32/64,countごとに定義されたflags | u2_control_forms,insn/u2-control.c |
| BT/BTS/BTR/BTC/BSF/BSR/BSWAP/TZCNT/LZCNT/POPCNT | u2_bt,u2_integer_forms;zero入力の未定義値は比較maskから除外 |
| Jcc/CMOVcc/SETcc 全16 condition code | u2_branch/u2_cmov/u2_set,macro展開したnative insn/cond-*.c |
| CBW/CWDE/CDQE/CWD/CDQ/CQO,CLC/STC/CMC,CLD/STD,LAHF/SAHF,LOOP/LOOPE/LOOPNE/J*CXZ,PAUSE | u2_control_forms and existing mov/string guests |
| PUSH/POP/CALL/RET/LEAVE/ENTER,word/quad stack | u2_move,u2_frame_forms;u2_pop_fault_preserves_stack_and_flags;ENTER chain/allocation/word fault cases |
| REP MOVS/STOS/LODS/CMPS/SCAS;全幅、DF、count、条件終了 | u2_string_forms,insn/u2-string.c;u2_string existing guest |
| REPE CMPS/REPNE SCAS fault start/partial/budget | 6件のu2_{cmps,scas}_fault_* signal-context。raw flags/maskはevidence |
| XADD/CMPXCHG/XCHG/LOCK arithmetic;比較失敗のwrite権限、16B alignment、cross page | u2_atomic/u2_atomic_pairs/u2_integer_forms/u2_control_forms;3件のatomic fault context |
| ADCX/ADOX/ANDN/BZHI/MOVBE/MULX/PEXT/RORX/SHLX/SHRX | u2_bmi_forms,insn/u2-bmi.c (幅/maskはinventory.md) |
| XLAT;AL256 values,address32,FS/GS | u2_frame_forms,insn/u2-frame.c |
| Native old value/成功数、normal/atomic overlap、128bit tearing、mapping race | parallel_u2 10件、外側watchdog30秒でchildをkill/reap |

実装後の内部テストで、decoder の prefix・暗黙の幅・未対応 SIMD、MMU の typed operation・permission preflight・失敗時の非変更、CPU の REP 継続 identity・fetch fault・code invalidation・address32・比較失敗、Types/Kernel の arithmetic-fault 利用箇所を補完した。通過件数は実行したケースの証拠であり、任意入力についての証明ではない。

未検証：probe/aube の全実行経路、任意の memory alias と flags 入力、原配布 binary の完全な再現性。環境依存・未対応命令と SIMD/x87 はこの整数対応表の検証対象外。sample に現れないことだけで到達不能とは判断しない。行カバレッジは独立した workspace 全体80%以上の判定であり、この対応数とは区別する。

検証済み：静的棚卸しで確認した memory-source を `insn/u2-bmi.c` に追加した。ADCX は offset0/+8、ADOX は-8、MULX は0/+8、SHLX は0/+8/-8、SHRX は64-bit offset0および32-bit offset0/-4を比較する。`cargo test --locked -p paludarium-harness --test diff_u2 u2_bmi_forms -- --exact --nocapture` は1 passed/0 failed、native/emu の全出力一致。既存 production の read-path で通過し、production 変更は追加していない。

| FS/GS atomic全経路、addr32後base加算、mapped decoy、final permission/alignment | u2_segment_atomic_forms、u2_atomic_gs_ 2件、CPU u2_segment_ 5件。修正前後と全体197件/94.00%は docs/u2/repairs/ |
