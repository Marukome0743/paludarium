"""Preserve the complete old canonical and separately inspect repaired fixtures."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / "construction/u1-skeleton/code-generation/verification"
sys.path.insert(0, str(V))
from frame_source_binding import historical_decoder, validate_current


def main():
    historical_decoder(V, ROOT)
    validate_current(V, ROOT)


if __name__ == "__main__":
    main()
