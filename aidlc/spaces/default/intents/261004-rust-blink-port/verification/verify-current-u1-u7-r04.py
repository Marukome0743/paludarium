#!/usr/bin/env python3
"""Candidate intent checkpoint: current U1 integration plus signed U7 R04 evidence."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "Cargo.toml").is_file())
CHECK = HERE.parent / "construction/u1-skeleton/code-generation/verification/verify-current-u1-with-r04.py"

if __name__ == "__main__":
    raise SystemExit(subprocess.run([sys.executable, str(CHECK)], cwd=ROOT, check=False).returncode)
