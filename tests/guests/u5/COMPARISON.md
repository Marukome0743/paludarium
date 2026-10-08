# U5 native-first comparison

The oracle is generated on each native x86-64 Linux CI run. `threads.c` has no
libc dependency and writes only little-endian signed 64-bit observations.
stdout, stderr, exit status and every emitted defined memory value compare
exactly. Numeric TIDs never appear in the output: clone return, parent TID,
child TID and gettid are reduced to their equality relationships. No address,
time or scheduler-order observation is compared. WAKE loops until the waiter
actually registered; no sleeps are used to guess registration order.

| Cases | Behavior |
| --- | --- |
| 0–5 | mismatch, unmapped/unaligned address, empty WAIT/WAKE bitset, invalid timespec |
| 6–8 | relative WAIT and expired absolute monotonic/realtime BITSET deadlines |
| 9–11 | no waiters, invalid timespec pointer, unsupported realtime WAIT |
| 12–14 | clone TLS, child TID before execution, individual exit and clear_child_tid |
| 15–16 | parent individual exit retains child; exit_group terminates the process |
| 17–20 | private wake, bitset selection, shared bitset wake, valid tgkill lookup |
| 21–23 | signal interrupts WAIT, invalid flag dependency, parent TID invalid pointer |
| 24–26 | simultaneous locked increments, 100 mutex/condvar-style handoffs, shared wake |

`scripts/u5-native-observe.py --out target/u5-native-first` runs all cases with
30-second independent process-group watchdogs, kill/reap and raw logs. Add
`--emulator target/debug/paludarium` for native-then-emulator comparison. Case 16
must exit with 17; all other cases exit with 0. Native mismatch/error observations
are recorded as data, not assumed from an errno table.

Case 23 deliberately observes Linux's actual handling of an invalid
CLONE_PARENT_SETTID pointer and normalizes successful clone to 1. It does not
assume that clone fails when Linux ignores a failed parent-TID write.

The raw guests cover the synchronization primitives required by Rust Mutex,
Condvar and Rayon without requiring their later-unit instruction/library
dependencies. Full probe completion remains a separate requirement. Additional
REQUEUE/CMP_REQUEUE/WAKE_OP support requires an observed usage requirement.
