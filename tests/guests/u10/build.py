"""Isolated fixed-revision guest build; no Git repository mutation."""
import json
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import urllib.request

from evidence import digest, snapshot, static_elf, guest_policy, record_source_after

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
               'target': lock['target'], 'aube': lock['aube'], 'binaries': {}, 'audits': {}}
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
        root_policy = (ROOT / 'deny.toml').read_bytes()
        guest_config = directory / 'aube-deny.toml'
        guest_config.write_bytes(guest_policy(root_policy, lock['guest_license_exception']))
        # Metadata fetches crates.io sources but does not compile or mutate
        # the upstream project. Retain the crate's actual full license text.
        metadata = json.loads(subprocess.check_output([
            'cargo', '+' + lock['toolchain'], 'metadata', '--locked', '--all-features',
            '--manifest-path', str(upstream / 'Cargo.toml'), '--format-version', '1'], text=True))
        packages = [p for p in metadata['packages'] if p['name'] == 'webpki-root-certs' and p['version'] == '1.0.9']
        if len(packages) != 1 or packages[0]['license'] != 'CDLA-Permissive-2.0':
            raise ValueError('fixed certificate crate identity/license mismatch')
        package = packages[0]
        if package['source'] != 'registry+https://github.com/rust-lang/crates.io-index':
            raise ValueError('certificate crate not sourced from crates.io')
        original_license = pathlib.Path(package['manifest_path']).parent / 'LICENSE'
        license_text = original_license.read_bytes()
        if b'Community Data License Agreement' not in license_text or b'2.1.' not in license_text:
            raise ValueError('full certificate data license missing')
        licenses = directory / 'licenses'
        licenses.mkdir(exist_ok=True)
        license_file = licenses / 'webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt'
        license_file.write_bytes(license_text)
        receipt['license_policy'] = {
            'exception': lock['guest_license_exception'], 'crate_source': package['source'],
            'root_config_sha256': hashlib.sha256(root_policy).hexdigest(),
            'guest_config_sha256': digest(guest_config), 'license_sha256': digest(license_file)}
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
            config = ROOT / 'deny.toml' if name == 'probe' else guest_config
            command(['cargo', 'deny', '--manifest-path', str(manifest), '--config', str(config),
                     '--locked', 'check'], ROOT, directory / f'{name}-dependencies.log')
            receipt['audits'][name] = 0
            args = cargo + ['build', '--release', '--locked', '--target', lock['target'],
                            '--manifest-path', str(manifest), '--target-dir', str(directory / 'targets' / name)] + extra
            env = dict(os.environ, AUBE_PRIMER_PATH=str(primer))
            command(args, ROOT, directory / f'{name}-build.log', env)
            binary_name = 'paludarium-probe-u10' if name == 'probe' else 'aube'
            shutil.copy2(directory / 'targets' / name / lock['target'] / 'release' / binary_name, directory / name)
            static_elf((directory / name).read_bytes())
            receipt['binaries'][name] = {'sha256': digest(directory / name), 'static_elf': True,
                                         'lock_sha256': digest(manifest.parent / 'Cargo.lock'), 'command': args}
        receipt['exit'] = 0
    except Exception as error:
        receipt['exit'] = 1
        receipt['error'] = str(error)
        raise
    finally:
        try:
            record_source_after(upstream, receipt)
        except Exception as error:
            receipt['exit'] = 1
            receipt['source_unchanged'] = False
            receipt['source_error'] = str(error)
        if 'license_policy' in receipt and digest(ROOT / 'deny.toml') != receipt['license_policy']['root_config_sha256']:
            receipt['exit'] = 1
            receipt['error'] = 'root license policy changed during build'
        receipt_file.write_text(json.dumps(receipt, indent=2) + '\n')
    if receipt['exit'] != 0:
        raise ValueError(receipt.get('source_error', 'guest build failed'))


if __name__ == '__main__':
    build(pathlib.Path(sys.argv[1]).resolve())
