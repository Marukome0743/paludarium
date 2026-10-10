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


def build(directory, advisory_policy=None):
    if advisory_policy not in (None, 'u14-fixed-aube', 'u15-fixed-aube-zip9', 'u15-fixed-aube-zip9-name'):
        raise ValueError('unapproved guest advisory policy')
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
        build_source = upstream
        if advisory_policy:
            from evidence import u14_overlay_module
            build_source = directory / 'build-source/aube'
            receipt['lock_overlay'] = u14_overlay_module().prepare(
                upstream, build_source, advisory_policy,
                lock[{'u15-fixed-aube-zip9':'u15_aube_zip_overlay', 'u15-fixed-aube-zip9-name':'u15_aube_zip_name_overlay'}.get(advisory_policy, 'u14_aube_lock_overlay')], snapshot)
        root_policy = (ROOT / 'deny.toml').read_bytes()
        guest_config = directory / 'aube-deny.toml'
        config_bytes = guest_policy(root_policy, lock['guest_license_exception'])
        if advisory_policy:
            from evidence import u14_policy_module
            generator = u14_policy_module().generate_zip if advisory_policy in ('u15-fixed-aube-zip9', 'u15-fixed-aube-zip9-name') else u14_policy_module().generate
            config_bytes, advisory_receipt = generator(
                root_policy, config_bytes, (build_source / 'Cargo.lock').read_bytes())
            receipt['advisory_policy'] = advisory_receipt
            receipt['advisory_lock'] = (build_source / 'Cargo.lock').read_text()
        guest_config.write_bytes(config_bytes)
        # Metadata fetches crates.io sources but does not compile or mutate
        # the upstream project. Retain the crate's actual full license text.
        metadata_text = subprocess.check_output([
            'cargo', '+' + lock['toolchain'], 'metadata', '--locked', '--all-features',
            '--manifest-path', str(build_source / 'Cargo.toml'), '--format-version', '1'], text=True)
        metadata = json.loads(metadata_text)
        if advisory_policy:
            receipt['metadata_lock_sha256'] = digest(build_source / 'Cargo.lock')
            metadata_file = directory / 'aube-metadata.json'
            metadata_file.write_text(metadata_text)
            receipt['metadata_sha256'] = digest(metadata_file)
            receipt['metadata_json'] = metadata_text
            receipt['ci_head'] = os.environ.get('GITHUB_SHA')
            if advisory_policy in ('u15-fixed-aube-zip9', 'u15-fixed-aube-zip9-name'):
                receipt['metadata_manifest_sha256'] = digest(build_source / 'Cargo.toml')
            if advisory_policy == 'u15-fixed-aube-zip9-name':
                receipt['metadata_build_source_sha256'] = u14_overlay_module().snapshot_sha(snapshot(build_source))
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
        if advisory_policy:
            # Audit the repaired guest before any cross-compilation can fail
            # on the host linker; every advisory category remains mandatory.
            command(['cargo', 'deny', '--manifest-path', str(build_source / 'Cargo.toml'),
                     '--config', str(guest_config), '--locked', 'check'],
                    ROOT, directory / 'aube-dependencies.log')
            receipt['audits']['aube'] = 0
        for name, manifest, extra in [
            ('probe', HERE / 'probe/Cargo.toml', []),
            ('aube', build_source / 'Cargo.toml', ['-p', 'aube', '--bin', 'aube']),
        ]:
            config = ROOT / 'deny.toml' if name == 'probe' else guest_config
            if name not in receipt['audits']:
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
            if name == 'aube' and advisory_policy in ('u15-fixed-aube-zip9', 'u15-fixed-aube-zip9-name'):
                receipt['binaries'][name]['manifest_sha256'] = digest(manifest)
            if name == 'aube' and advisory_policy == 'u15-fixed-aube-zip9-name':
                receipt['binaries'][name]['source_sha256'] = u14_overlay_module().snapshot_sha(snapshot(build_source))
        receipt['exit'] = 0
    except Exception as error:
        receipt['exit'] = 1
        receipt['error'] = str(error)
        raise
    finally:
        try:
            record_source_after(upstream, receipt)
            if 'lock_overlay' in receipt:
                u14_overlay_module().finish(upstream, build_source, receipt['lock_overlay'], snapshot)
        except Exception as error:
            receipt['exit'] = 1
            receipt['source_unchanged'] = False
            receipt['source_error'] = str(error)
        if 'license_policy' in receipt and digest(ROOT / 'deny.toml') != receipt['license_policy']['root_config_sha256']:
            receipt['exit'] = 1
            receipt['error'] = 'root license policy changed during build'
        if 'lock_overlay' in receipt:
            from evidence import overlay_payload_digest
            receipt['artifact_payload_sha256'] = overlay_payload_digest(receipt)
        receipt_file.write_text(json.dumps(receipt, indent=2) + '\n')
    if receipt['exit'] != 0:
        raise ValueError(receipt.get('source_error', 'guest build failed'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--advisory-policy', choices=['u14-fixed-aube', 'u15-fixed-aube-zip9', 'u15-fixed-aube-zip9-name'])
    arguments = parser.parse_args()
    build(pathlib.Path(arguments.directory).resolve(), arguments.advisory_policy)
