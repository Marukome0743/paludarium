#!/usr/bin/env bash
# The Python builder records failures and leaves its isolated source intact.
set -euo pipefail
python3 tests/guests/u10/build.py "${1:-target/guests/u10}"
