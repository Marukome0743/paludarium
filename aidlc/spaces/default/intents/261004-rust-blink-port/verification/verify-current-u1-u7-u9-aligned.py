#!/usr/bin/env python3
"""Candidate command for U1/U7 production reuse and fresh U9. Await explicit command approval."""
import subprocess
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/"Cargo.toml").is_file())
CHECK=HERE.parent/"construction/u9-terminal-io/code-generation/verification/verify-current-u1-u7-u9-aligned.py"
if __name__=="__main__":
    raise SystemExit(subprocess.run([sys.executable,str(CHECK)],cwd=ROOT,check=False).returncode)

