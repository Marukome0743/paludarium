# U2 flag comparison policy

Native fault observations print raw ucontext EFLAGS to stderr and the compared
value to stdout. REP CMPS/SCAS cases begin with `0x8d7` and compare `0xcd5`:
CF/PF/AF/ZF/SF/OF plus DF. The fault contract requires these initial flags to be
restored, including across a 4096-iteration internal budget stop. Count and
source/destination progress remain committed; fault RIP remains at the string instruction.

RF (exception delivery), IF (execution environment), reserved bits and other
noninteger flags are excluded from the comparison. The raw value is retained
so this exclusion does not hide an arithmetic/status mismatch. Initial status
bits are explicitly set rather than inferred from surrounding C instructions.

Existing integer guests define their input-sensitive masks in
`tests/guests/insn/UNDEFINED.md` and `insn.h`.

| Case | Compared flags and conditions |
|---|---|
| ROL/ROR/RCL/RCR 8/16/32/64 | Arithmetic status, retaining initial preserved bits; OF excluded when masked count >1. Counts 0/1/2/width-boundaries/63/64/65. |
| SHLD/SHRD 16/32/64 | Count0 preserves all status; nonzero excludes AF; count>1 excludes OF; count>operand width excludes result and all flags (architecturally undefined). |
| BSF/BSR | ZF only; zero-input destination is excluded. |
| TZCNT/LZCNT 16/32/64 | CF/ZF only; undefined OF/SF/AF/PF excluded. Zero input returns width; low/high output bits are compared. |
| POPCNT 16/32/64 | All status flags; only ZF is set for zero input. |
| BTS/BTR/BTC | CF only; other status bits are undefined. |
| BSWAP, sign extensions, LOOP/J*CXZ, PAUSE | All arithmetic status preserved. CLC/STC/CMC modify only CF; LAHF/SAHF compare the defined status effect. |
| LOCK ADD/ADC/SUB/SBB/INC/DEC/NEG | All defined status; INC/DEC preserve initial CF. Logical LOCK AND/OR/XOR excludes undefined AF; NOT preserves all status. |
| CMPXCHG8B/16B | ZF updated and other status flags preserved; compare full defined/preserved status. |
| MOVS/STOS/LODS/CMPS/SCAS | Arithmetic status plus DF; all widths and both DF directions. CMPS/SCAS termination and completed indices/count/memory also compared. |
| DIV/IDIV, POP, atomic faults | Native ucontext status/DF mask0xcd5, original registers and faulting RIP; successful DIV/IDIV flags follow U1 undefined policy. |

The REP fault mask is not applied to every instruction. Full target-program
forms/paths remain incompletely classified; see inventory.md and
differential-coverage.md. Sampled absence is not evidence of unreachability.

Additional candidate masks: ADCX updates CF only and ADOX OF only; other status bits retained. ANDN/BZHI compare CF/OF/ZF/SF (AF/PF undefined); BZHI indexes through low8 bits and reports out-of-width CF. MULX/PEXT/RORX/SHLX/SHRX/MOVBE/ENTER/LEAVE/XLAT preserve arithmetic status. PUSHFW/POPFW compare defined writable arithmetic bits and retain bits outside the operand width. ENTER signal contexts compare original RSP/RBP/RIP,0xcd5 flags,fault address and preceding committed stack bytes; the native observation requires partial memory effects even though registers roll back.

FS/GS atomicのsignal-context比較は raw flags=0x10ad7、mask=0xcd5 を使用する。RF/IFと配送時のreserved bitsは整数命令のstatus/DF差分に数えない。GS readonly failed CMPXCHGと最終linear addressのCMPXCHG16B alignment faultをnative observerで確認し、FSのpermission/alignmentは実装後CPU内部テストでも補完する。具体物はdocs/u2/repairs/r01-gs-fault-green.txt。
