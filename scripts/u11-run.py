#!/usr/bin/env python3
"""U11 bounded test entry point; native oracle is generated afresh on Linux."""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tests/guests/u11'))
sys.path.insert(1, str(ROOT / 'tests/guests/u10'))


def main():
    from settings import configuration
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--guest-dir', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path)
    parser.add_argument('--browser', choices=('chromium', 'firefox', 'safari'))
    parser.add_argument('--wasm', type=pathlib.Path)
    parser.add_argument('--native', type=pathlib.Path)
    args = parser.parse_args()
    config = configuration(ROOT)
    if args.self_test:
        from runner import run
        row = run([sys.executable, '-c', 'pass'], cwd=ROOT, env={})
        if row['exit'] != 0 or row['timed_out']:
            raise RuntimeError('bounded test runner failed readiness')
        print('U11 runner ready: fresh native fourteen cases, 30-second external deadline')
        return
    if args.native_only:
        if args.guest_dir is None or args.output is None or args.browser:
            parser.error('native-only requires --guest-dir --output and no --browser')
        from native import observe
        from evidence import digest
        output = args.output.resolve()
        observe(args.guest_dir.resolve(), output, config)
        receipt = {'unit': 'u11-wasm-launcher', 'native_oracle_sha256': digest(output / 'observations.json'),
                   'cases_sha256': digest(ROOT / 'tests/guests/u10/cases.json'),
                   'source_lock_sha256': digest(ROOT / 'tests/guests/u10/source-lock.json'),
                   'production_source_sha256': {path: digest(ROOT / path) for path in (
                       'crates/paludarium-runtime/src/lib.rs', 'crates/paludarium-runtime/src/workers.rs',
                       'crates/paludarium-host/src/wasm.rs', 'crates/paludarium-wasm/src/abi.rs',
                       'packages/paludarium-wasm/index.mjs', 'packages/paludarium-wasm/coordinator.mjs',
                       'packages/paludarium-wasm/execution.mjs', 'packages/paludarium-wasm/worker-support.mjs')}}
        (output / 'u11-oracle-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        return
    parser.error('browser runner is not implemented yet; no browser result is claimed')


if __name__ == '__main__':
    main()
