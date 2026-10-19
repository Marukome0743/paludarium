#!/usr/bin/env python3
"""Candidate combined checkpoint. Do not execute before human command approval."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "Cargo.toml").is_file())

if __name__ == "__main__":
    for check in [HERE / "verify-current-u1-u7-r04.py", HERE.parent / "construction/u9-terminal-io/code-generation/verification/verify-current-u9-r04.py"]:
        result = subprocess.run([sys.executable, str(check)], cwd=ROOT, check=False)
        if result.returncode:
            raise SystemExit(result.returncode)
