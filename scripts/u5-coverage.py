"""Check the fixed U5 production-file denominator in a native Linux LCOV report."""
import argparse
import json
from pathlib import Path

FILES = {
    'crates/paludarium-host/src/lib.rs', 'crates/paludarium-host/src/threads.rs',
    'crates/paludarium-host/src/native_fs.rs',
    'crates/paludarium-kernel/src/lib.rs', 'crates/paludarium-kernel/src/files.rs',
    'crates/paludarium-kernel/src/syscalls.rs', 'crates/paludarium-kernel/src/inbox.rs',
    'crates/paludarium-kernel/src/threads.rs', 'crates/paludarium-kernel/src/futex.rs',
    'crates/paludarium-kernel/src/signals.rs',
    'crates/paludarium-mmu/src/lib.rs', 'crates/paludarium-runtime/src/lib.rs',
    'crates/paludarium-runtime/src/workers.rs',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lcov', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = {}
    for record in args.lcov.read_text().split('end_of_record'):
        fields = record.strip().splitlines()
        source = next((line[3:].replace('\\', '/') for line in fields if line.startswith('SF:')), None)
        if source is None:
            continue
        path = next((name for name in FILES if source.endswith('/'+name) or source == name), None)
        if path is None:
            continue
        lines = [line[3:].split(',') for line in fields if line.startswith('DA:')]
        rows[path] = dict(lines=len(lines), hit=sum(int(count)>0 for _,count,*_ in lines))
    missing = FILES-rows.keys()
    if missing:
        raise RuntimeError(f'Coverage denominator missing files: {sorted(missing)}')
    total = sum(row['lines'] for row in rows.values())
    hit = sum(row['hit'] for row in rows.values())
    percent = 100*hit/total if total else 0
    args.out.write_text(json.dumps(dict(files=rows, lines=total, hit=hit, percent=percent, floor=80), indent=2)+'\n')
    print(f'U5 coverage: {hit}/{total} = {percent:.2f}% (floor 80%)')
    if percent < 80:
        raise RuntimeError('U5 production coverage is below the unchanged 80% floor')


if __name__ == '__main__':
    main()
