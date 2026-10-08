#!/bin/bash
set -uo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
out="${1:?evidence directory}"
mkdir -p "$out"
{ uname -a; id; cc --version; sha256sum "$src/clone-probe.c"; cat /proc/self/status; } > "$out/environment.log" 2>&1
cc -Wall -Wextra -Werror -O1 "$src/clone-probe.c" -o "$out/clone-probe" || exit 1
for signal in 17 0; do
 for mask in $(seq 0 15); do
  timeout 30 "$out/clone-probe" "$mask" "$signal" > "$out/clone-$mask-signal-$signal.log" 2>&1
  printf '%s\n' "$?" > "$out/clone-$mask-signal-$signal.exit"
 done
done
timeout 30 "$out/clone-probe" ptrace > "$out/ptrace.log" 2>&1
printf '%s\n' "$?" > "$out/ptrace.exit"
printf 'int main(void) { return 0; }\n' > "$out/minimal.c"
cc -fsanitize=address -g -O1 "$out/minimal.c" -o "$out/minimal-asan"
for attempt in 1 2; do
 ASAN_OPTIONS=detect_leaks=1 LSAN_OPTIONS=verbosity=1 timeout 30 "$out/minimal-asan" > "$out/lsan-$attempt.log" 2>&1
 printf '%s\n' "$?" > "$out/lsan-$attempt.exit"
done
sha256sum "$src/clone-probe.c" "$src/run.sh" > "$out/source.sha256"
