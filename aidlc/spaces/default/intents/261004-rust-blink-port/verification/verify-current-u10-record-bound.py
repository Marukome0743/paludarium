"""Preserve U5's entire checker chain and bind historical/current U10 records."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
sys.path.insert(0, str(RECORD / 'construction/u10-probe-aube-native/code-generation/verification'))
from record_reference_binding import run


def main():
    run(RECORD, ROOT)


if __name__ == '__main__':
    main()
