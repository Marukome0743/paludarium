#!/usr/bin/env bash
# U3 guest runner bootstrap. Instruction fixtures follow native-oracle design.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="${1:?output directory required}"
mkdir -p "$out"
cc="${MUSL_CC:-musl-gcc}"
"$cc" -static -nostdlib -fno-pie -no-pie -o "$out/runner" "$here/runner.S"
