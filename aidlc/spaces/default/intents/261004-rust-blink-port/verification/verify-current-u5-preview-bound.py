"""Preserve every quality canonical check and audit the exact AI-DLC preview delta."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / "construction/u5-threads-futex/code-generation/verification"
sys.path.insert(0, str(V))
from preview_source_binding import run


def main():
    run(RECORD, ROOT)


if __name__ == "__main__":
    main()
