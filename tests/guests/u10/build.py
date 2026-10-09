"""Isolated fixed-revision guest build; no Git repository mutation."""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import urllib.request

from evidence import digest, snapshot, static_elf

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent


def command(args, cwd, log, env=None):
    with log.open('ab') as out:
        out.write(('COMMAND ' + repr(args) + '\n').encode())
        subprocess.run(args, cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT, check=True)


def build(directory):
    directory.mkdir(parents=True, exist_ok=True)
    lock = json.loads((HERE / 'source-lock.json').read_text())
    receipt = {'schema': 1, 'exit': None, 'toolchain': lock['toolchain'],
               'target': lock['target'], 'aube': lock['aube'], 'binaries': {}}
    receipt_file = directory / 'build-receipt.json'
    source = directory / 'source'
    source.mkdir(exist_ok=True)
    upstream = source / 'aube'
    try:
        # cargo-deny 0.20.2 graph/config arguments are top-level options,
        # before `check`. Validate parsing before downloading/building guests.
        command(['cargo', 'deny', '--manifest-path', str(HERE / 'probe/Cargo.toml'),
                 '--config', str(ROOT / 'deny.toml'), '--locked', 'check', '--help'],
                ROOT, directory / 'cli-dependencies.log')
        if not upstream.exists():
            archive = directory / 'aube-source.tar.gz'
            revision = lock['aube']['revision']
            urllib.request.urlretrieve(f'https://codeload.github.com/aubepkg/aube/tar.gz/{revision}', archive)
            with tarfile.open(archive) as tar:
                tar.extractall(source, filter='data')
            (source / f'aube-{revision}').rename(upstream)
        if digest(upstream / 'Cargo.lock') != lock['aube']['lock_sha256']:
            raise ValueError('fixed aube Cargo.lock mismatch')
        before = snapshot(upstream)
        receipt['source_before'] = before
        primer = directory / 'empty-primer.rkyv.zst'
        primer.write_bytes(b'')
        cargo = ['cargo', '+' + lock['toolchain']]
        subprocess.run(cargo + ['--version'], check=True)
        receipt['rustc'] = subprocess.check_output(['rustc', '+' + lock['toolchain'], '--version'], text=True).strip()
        receipt['cargo'] = subprocess.check_output(cargo + ['--version'], text=True).strip()
        for name, manifest, extra in [
            ('probe', HERE / 'probe/Cargo.toml', []),
            ('aube', upstream / 'Cargo.toml', ['-p', 'aube', '--bin', 'aube']),
        ]:
            args = cargo + ['build', '--release', '--locked', '--target', lock['target'],
                            '--manifest-path', str(manifest), '--target-dir', str(directory / 'targets' / name)] + extra
            env = dict(os.environ, AUBE_PRIMER_PATH=str(primer))
            command(args, ROOT, directory / f'{name}-build.log', env)
            binary_name = 'paludarium-probe-u10' if name == 'probe' else 'aube'
            shutil.copy2(directory / 'targets' / name / lock['target'] / 'release' / binary_name, directory / name)
            static_elf((directory / name).read_bytes())
            receipt['binaries'][name] = {'sha256': digest(directory / name), 'static_elf': True,
                                         'lock_sha256': digest(manifest.parent / 'Cargo.lock'), 'command': args}
            command(['cargo', 'deny', '--manifest-path', str(manifest), '--config', str(ROOT / 'deny.toml'), '--locked', 'check'], ROOT, directory / f'{name}-dependencies.log')
        receipt['source_after'] = snapshot(upstream)
        receipt['source_unchanged'] = receipt['source_after'] == before
        if not receipt['source_unchanged']:
            raise ValueError('upstream source changed during build')
        receipt['exit'] = 0
    except Exception as error:
        receipt['exit'] = 1
        receipt['error'] = str(error)
        raise
    finally:
        receipt_file.write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    build(pathlib.Path(sys.argv[1]).resolve())
