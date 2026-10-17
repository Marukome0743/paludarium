"""Build receipt checks shared by observations and unit tests."""
import hashlib
import pathlib
import struct
import importlib.util
import json
import os
import re

LICENSE_EXCEPTION = {'crate': 'webpki-root-certs@1.0.9', 'allow': ['CDLA-Permissive-2.0']}
LICENSE_SUFFIX = b'\n[[licenses.exceptions]]\ncrate = "webpki-root-certs@1.0.9"\nallow = ["CDLA-Permissive-2.0"]\n'


def guest_policy(root_bytes, exception):
    if exception != LICENSE_EXCEPTION:
        raise ValueError('unapproved guest license exception')
    return root_bytes + LICENSE_SUFFIX


def u14_policy_module():
    path = pathlib.Path(__file__).resolve().parents[1] / 'u14/guest_policy.py'
    spec = importlib.util.spec_from_file_location('u14_guest_policy', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u14_overlay_module():
    path = pathlib.Path(__file__).resolve().parents[1] / 'u14/lock_overlay.py'
    spec = importlib.util.spec_from_file_location('u14_lock_overlay', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def overlay_payload_digest(receipt):
    payload = {k: v for k, v in receipt.items() if k != 'artifact_payload_sha256'}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def policy_receipt_valid(directory, receipt, root_bytes):
    policy = receipt['license_policy']
    if policy['exception'] != LICENSE_EXCEPTION:
        raise ValueError('unapproved guest license exception')
    if hashlib.sha256(root_bytes).hexdigest() != policy['root_config_sha256']:
        raise ValueError('root policy changed')
    config = directory / 'aube-deny.toml'
    inherited = guest_policy(root_bytes, policy['exception'])
    if 'advisory_policy' in receipt:
        # Bind full pinned source lock, not merely the ignored package row.
        lock_bytes = receipt['advisory_lock'].encode()
        source_lock = json_source_lock()
        expected_lock = source_lock['aube']['lock_sha256']
        if 'lock_overlay' in receipt:
            overlay = receipt['lock_overlay']
            helper = u14_overlay_module()
            helper.verify(overlay)
            is_name = overlay['policy'].get('policy') == 'u15-fixed-aube-zip9-name'
            is_zip = is_name or overlay['policy'].get('policy') == 'u15-fixed-aube-zip9'
            if overlay['policy'] != source_lock['u15_aube_zip_name_overlay' if is_name else 'u15_aube_zip_overlay' if is_zip else 'u14_aube_lock_overlay']:
                raise ValueError('unapproved overlay receipt policy')
            if (overlay['source_before'] != receipt['source_before']
                    or overlay['source_after'] != receipt['source_after']
                    or overlay['original_lock'] == receipt['advisory_lock']
                    or overlay['build_lock'] != receipt['advisory_lock']):
                raise ValueError('overlay original/build receipt mismatch')
            expected_lock = helper.ZIP_LOCK if is_zip else helper.UPDATED
            if (receipt['metadata_lock_sha256'] != expected_lock
                    or receipt['binaries']['aube']['lock_sha256'] != expected_lock):
                raise ValueError('metadata or binary uses original lock')
            if hashlib.sha256(receipt['metadata_json'].encode()).hexdigest() != receipt['metadata_sha256']:
                raise ValueError('overlay metadata hash mismatch')
            packages = json.loads(receipt['metadata_json'])['packages']
            rustls = [p for p in packages if p['name'] == 'rustls']
            if len(rustls) != 1 or rustls[0]['version'] != '0.23.46' or rustls[0]['source'] != helper.REGISTRY:
                raise ValueError('overlay metadata rustls identity mismatch')
            if is_zip:
                verify_zip_metadata(receipt, packages, helper)
            if is_name:
                verify_name_metadata(receipt, helper)
            metadata_file = directory / 'aube-metadata.json'
            if metadata_file.exists() and digest(metadata_file) != receipt['metadata_sha256']:
                raise ValueError('overlay metadata hash mismatch')
        if receipt['aube'] != source_lock['aube'] or hashlib.sha256(lock_bytes).hexdigest() != expected_lock:
            raise ValueError('fixed aube Cargo.lock mismatch')
        u14_policy_module().verify(root_bytes, inherited, lock_bytes,
                                   config.read_bytes(), receipt['advisory_policy'])
    elif config.read_bytes() != inherited:
        raise ValueError('guest config does not inherit exact root policy')
    if digest(config) != policy['guest_config_sha256']:
        raise ValueError('guest config hash differs')
    license_file = directory / 'licenses/webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt'
    if digest(license_file) != policy['license_sha256']:
        raise ValueError('license text hash differs')
    if policy['crate_source'] != 'registry+https://github.com/rust-lang/crates.io-index':
        raise ValueError('certificate crate source is not crates.io')
    if receipt['audits'] != {'probe': 0, 'aube': 0}:
        raise ValueError('full guest dependency audits did not pass')


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def json_source_lock():
    import json
    return json.loads(pathlib.Path(__file__).with_name('source-lock.json').read_text())


def static_elf(data):
    if len(data) < 64 or data[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('not ELF64 little endian')
    if struct.unpack_from('<H', data, 18)[0] != 62:
        raise ValueError('not x86-64')
    if struct.unpack_from('<H', data, 16)[0] not in (2, 3):
        raise ValueError('not executable or static PIE')
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    if size < 56 or count == 0 or offset + size * count > len(data):
        raise ValueError('invalid program headers')
    headers = [struct.unpack_from('<IIQQQQQQ', data, offset + i * size) for i in range(count)]
    types = [header[0] for header in headers]
    if 3 in types or 1 not in types:
        raise ValueError('interpreter or missing load segment')
    # Rust/musl static PIE uses PT_DYNAMIC for its own relocations. It is
    # static iff no external interpreter or DT_NEEDED library is required.
    for header in headers:
        if header[2] + header[5] > len(data):
            raise ValueError('segment extends outside binary')
        if header[0] != 2:
            continue
        start, length = header[2], header[5]
        if length == 0 or length % 16:
            raise ValueError('malformed dynamic table')
        terminated = False
        for position in range(start, start + length, 16):
            tag, _ = struct.unpack_from('<qQ', data, position)
            if tag == 1:
                raise ValueError('DT_NEEDED external library')
            if tag == 0:
                terminated = True
                break
        if not terminated:
            raise ValueError('unterminated dynamic table')
    return True


def validate(directory, receipt):
    if receipt['exit'] != 0 or not receipt['source_unchanged']:
        raise ValueError('build failure or modified upstream source')
    if 'lock_overlay' in receipt:
        if 'advisory_policy' not in receipt:
            raise ValueError('overlay requires U14 advisory policy')
        overlay = receipt['lock_overlay']
        helper = u14_overlay_module()
        helper.verify(overlay)
        if receipt.get('artifact_payload_sha256') != overlay_payload_digest(receipt):
            raise ValueError('overlay artifact payload digest mismatch')
        original, built = directory / 'source/aube', directory / 'build-source/aube'
        if original.exists() or built.exists():
            helper.verify_links(original)
            helper.verify_links(built)
            if (snapshot(original) != overlay['source_after']
                    or snapshot(built) != overlay['build_source_after']):
                raise ValueError('overlay source changed after receipt')
        else:
            # Download-artifact verifies the CI archive digest externally. Bind
            # its receipt payload to this exact workflow head, never just a bool.
            head = receipt.get('ci_head')
            if not isinstance(head, str) or not re.fullmatch('[0-9a-f]{40}', head) or head != os.environ.get('GITHUB_SHA'):
                raise ValueError('overlay artifact CI head binding mismatch')
    for name in ('probe', 'aube'):
        binary = directory / name
        if digest(binary) != receipt['binaries'][name]['sha256']:
            raise ValueError('binary hash differs')
        static_elf(binary.read_bytes())
    root_bytes = (pathlib.Path(__file__).resolve().parents[3] / 'deny.toml').read_bytes()
    policy_receipt_valid(directory, receipt, root_bytes)


def record_source_after(upstream, receipt):
    if 'source_before' not in receipt:
        return
    receipt['source_after'] = snapshot(upstream)
    receipt['source_unchanged'] = receipt['source_after'] == receipt['source_before']
    if not receipt['source_unchanged']:
        receipt['exit'] = 1
        receipt['source_error'] = 'upstream source changed during build or audit'


def snapshot(directory):
    return {str(p.relative_to(directory)): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file()}


def verify_zip_metadata(receipt, packages, helper):
    """Bind metadata, manifest, and the built binary to the new policy."""
    selected = [p for p in packages if p['name'] == 'zip']
    if len(selected) != 1 or selected[0]['version'] != '9.0.4' or selected[0]['source'] != helper.REGISTRY:
        raise ValueError('overlay metadata zip identity mismatch')
    if (receipt.get('metadata_manifest_sha256') != helper.ZIP_MANIFEST
            or receipt['binaries']['aube'].get('manifest_sha256') != helper.ZIP_MANIFEST):
        raise ValueError('overlay metadata/binary manifest mismatch')
    for name in ('aube-registry', 'aube-runtime'):
        matches = [p for p in packages if p['name'] == name]
        if len(matches) != 1:
            raise ValueError('overlay metadata workspace package mismatch')
        dependencies = [d for d in matches[0]['dependencies'] if d['name'] == 'zip']
        if (len(dependencies) != 1 or dependencies[0]['req'] != '=9.0.4'
                or dependencies[0]['source'] != helper.REGISTRY
                or dependencies[0]['uses_default_features'] is not False
                or dependencies[0]['features'] != ['deflate']):
            raise ValueError('overlay metadata zip constraint mismatch')


def verify_name_metadata(receipt, helper):
    if (receipt.get('metadata_build_source_sha256') != helper.NAME_SOURCE
            or receipt['binaries']['aube'].get('source_sha256') != helper.NAME_SOURCE):
        raise ValueError('overlay metadata/binary compatibility source mismatch')
