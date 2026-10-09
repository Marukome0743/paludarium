# Static PIE build evidence correction

## Observed failure

検証済み: native-first CI38002964866, job114065152928 failed after successful probe compilation at evidence.py static_elf. Downloaded probe SHA256 545e5dad54fc53fc481d30cc5cfe69326996492c4d8a14df44d85418f094f6f1: ELF64 little-endian x86-64, ET_DYN=3; program types 1,1,1,1,2,4,7,1685382480,1685382481,1685382482. PT_INTERP absent. PT_DYNAMIC tags contain relocation entries and no DT_NEEDED. Binary evidence lives in code-generation/verification/native-first-failed/guests/u10/probe. Python struct unpacking of its ELF header, program headers and complete dynamic table established these observations.

## Correction and regression

The U10 checker incorrectly rejected every PT_DYNAMIC segment, including self-relocating static PIE. The existing loader explicitly accepts ET_EXEC and ET_DYN static PIE (crates/paludarium-loader/src/lib.rs lines3–6). The corrected checker continues to reject PT_INTERP and DT_NEEDED external libraries, and validates dynamic-table bounds and termination. No guest build flags, production loader or static-musl acceptance requirement changed.

ドキュメント根拠: [GCC Link Options](https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html) describes static PIE as loading at any address without a dynamic linker. Seven build-evidence unit tests include static EXEC/static PIE acceptance, interpreter/library rejection, architecture/table corruption and hash tampering. The test data is synthetic internal checker input, never native/emulator acceptance evidence.
