"""Keep all older canonical predicates and require complete current quality CI."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / "construction/u1-skeleton/code-generation/verification"
sys.path.insert(0, str(V))
from quality_source_binding import historical_frame, validate_current


def main():
    historical_frame(V, ROOT)
    validate_current(V, ROOT)


if __name__ == "__main__":
    main()
