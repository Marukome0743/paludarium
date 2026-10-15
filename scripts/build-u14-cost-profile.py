#!/usr/bin/env python3
"""Build separate diagnostic/control modules, retaining exact local source identity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
FLAGS = '-C target-feature=+atomics,+bulk-memory,+mutable-globals -C link-arg=--import-memory -C link-arg=--shared-memory -C link-arg=--max-memory=1073741824 -C link-arg=--export=__stack_pointer -C link-arg=--export=__wasm_init_tls -C link-arg=--export=__tls_size -C link-arg=--export=__tls_align -C link-arg=--export=__tls_base'
LOCKS = ('Cargo.lock', 'fuzz/Cargo.lock', 'tests/guests/u10/source-lock.json',
         'tests/guests/u10/probe/Cargo.lock', 'rust-toolchain.toml', 'deny.toml')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_snapshot():
    paths = {ROOT / name for name in LOCKS}
    for directory, extensions in [('crates', ('.rs', '.toml')),
                                  ('packages/paludarium-wasm', ('.mjs', '.json')),
                                  ('scripts', ('.py', '.sh')),
                                  ('tests/guests/u14', ('.py', '.c'))]:
        for path in (ROOT / directory).rglob('*'):
            relative = path.relative_to(ROOT)
            if (path.is_file() and path.suffix in extensions
                    and not {'target', 'node_modules', '__pycache__'} & set(relative.parts)):
                if path.is_symlink():
                    raise ValueError('linked source input')
                paths.add(path)
    return {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('diagnostic', 'acceptance-control'), required=True)
    parser.add_argument('--baseline-head', required=True)
    args = parser.parse_args()
    if len(args.baseline_head) != 40 or any(c not in '0123456789abcdef' for c in args.baseline_head):
        parser.error('baseline head must be exact signed SHA')
    source = source_snapshot()
    source_digest = digest(json.dumps(source, sort_keys=True, separators=(',', ':')).encode())
    pin = tomllib.loads((ROOT / 'rust-toolchain.toml').read_text())['toolchain']['channel']
    candidates = list((Path.home() / '.rustup/toolchains').glob(pin + '-*/bin/cargo'))
    if len(candidates) != 1:
        raise ValueError('one actual project-pinned Rust toolchain is required')
    cargo = candidates[0]
    rustc = cargo.with_name('rustc')
    directory = ROOT / 'target/u14-cost-profile'
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / (args.kind + '.wasm')
    env = dict(os.environ, RUSTC=str(rustc), RUSTC_WRAPPER='', RUSTFLAGS=FLAGS)
    env['PATH'] = str(cargo.parent) + os.pathsep + env.get('PATH', '')
    command = [str(cargo), 'build', '--locked', '-Z', 'build-std=std,panic_abort',
               '--release', '--target', 'wasm32-unknown-unknown', '-p', 'paludarium-wasm',
               '--target-dir', str(directory / 'build')]
    features = ['u14-cost-profile'] if args.kind == 'diagnostic' else []
    if features:
        command += ['--features', ','.join(features)]
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if source_snapshot() != source:
        raise ValueError('source changed during build')
    if result.returncode:
        raise RuntimeError(f'diagnostic/control build failed: {result.returncode}')
    shutil.copyfile(directory / 'build/wasm32-unknown-unknown/release/paludarium_wasm.wasm', output)
    head = os.environ.get('GITHUB_SHA')
    if head is not None and (len(head) != 40 or any(c not in '0123456789abcdef' for c in head)):
        raise ValueError('invalid CI head')
    receipt = {'schema': 1, 'purpose': 'u14-cost-profile' if features else 'u14-acceptance-control',
               'head': head or 'local:' + source_digest, 'local_snapshot': head is None,
               'baseline_signed_head': args.baseline_head, 'source_digest': source_digest,
               'source_files': source, 'module_sha256': digest(output.read_bytes()),
               'features': features, 'rustflags': FLAGS, 'command': command,
               'locks': {name: source[name] for name in LOCKS},
               'rustc': subprocess.check_output([str(rustc), '-Vv'], text=True).strip(),
               'cargo': subprocess.check_output([str(cargo), '--version'], text=True).strip()}
    receipt_path = output.with_suffix('.wasm.receipt.json')
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'module': str(output), 'receipt': str(receipt_path),
                      'purpose': receipt['purpose'], 'head': receipt['head'],
                      'module_sha256': receipt['module_sha256'], 'source_digest': source_digest}))


if __name__ == '__main__':
    main()
