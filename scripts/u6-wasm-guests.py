"""Package the freshly observed, nonthreaded U6 inputs for production Workers."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-native', type=Path, required=True)
    parser.add_argument('--observations', type=Path, required=True)
    parser.add_argument('--guests', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.observations / 'manifest.json').read_text())
    expected = {row['case']: row for row in manifest}
    assert set(expected) == {*range(82), 'timer', 'unix'} and len(manifest) == 84
    rows = json.loads(args.base_native.read_text())
    args.destination.mkdir(parents=True, exist_ok=True)
    for case in [*range(66), *range(67, 82), 'unix']:
        source = args.guests / (f'event-{case}' if isinstance(case, int) else 'u6-unix')
        binary = source.read_bytes()
        native = expected[case]['native']
        assert hashlib.sha256(binary).hexdigest() == expected[case]['binary_sha256']
        assert not native['timeout'] and native['stderr'] == ''
        assert native['exit'] == (-9 if case == 60 else 0)
        name = f'u6-{case}'
        (args.destination / name).write_bytes(binary)
        row = dict(name=name, sha256=expected[case]['binary_sha256'],
                   returncode=native['exit'], stdout=native['stdout'],
                   stderr=native['stderr'], timed_out=native['timeout'])
        if case in (52, 53, 54):
            row['policy_exception'] = 'AF_INET/AF_INET6 unavailable: EAFNOSUPPORT'
            row['policy_stdout'] = struct.pack('<qqqq', -97, 0, 0, 0).hex()
        rows.append(row)
    args.out.write_text(json.dumps(rows, indent=2)+'\n')
    print('Packaged 82 freshly observed U6 nonthreaded inputs; Tokio/backpressure guest threads remain U11 boundary')


if __name__ == '__main__':
    main()
