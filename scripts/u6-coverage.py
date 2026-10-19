"""Check the fixed U6 production-file denominator in a native Linux LCOV report."""
import argparse
import json
from pathlib import Path

FILES = {
    'crates/paludarium-host/src/fs.rs',
    'crates/paludarium-kernel/src/lib.rs', 'crates/paludarium-kernel/src/files.rs',
    'crates/paludarium-kernel/src/syscalls.rs', 'crates/paludarium-kernel/src/inbox.rs',
    'crates/paludarium-kernel/src/threads.rs', 'crates/paludarium-kernel/src/events.rs',
    'crates/paludarium-kernel/src/sockets.rs', 'crates/paludarium-kernel/src/epoll.rs',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lcov', type=Path, nargs='?')
    parser.add_argument('--lcov', type=Path, dest='lcov_option')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.lcov is not None and args.lcov_option is not None:
        parser.error('Pass either positional LCOV or --lcov, not both')
    args.lcov = args.lcov_option or args.lcov
    if args.lcov is None:
        parser.error('LCOV path is required')
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
    print(f'U6 coverage: {hit}/{total} = {percent:.2f}% (floor 80%)')
    if percent < 80:
        raise RuntimeError('U6 production coverage is below the unchanged 80% floor')


if __name__ == '__main__':
    main()

