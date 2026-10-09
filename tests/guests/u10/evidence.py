"""Build receipt checks shared by observations and unit tests."""
import hashlib
import pathlib
import struct

LICENSE_EXCEPTION = {'crate': 'webpki-root-certs@1.0.9', 'allow': ['CDLA-Permissive-2.0']}
LICENSE_SUFFIX = b'\n[[licenses.exceptions]]\ncrate = "webpki-root-certs@1.0.9"\nallow = ["CDLA-Permissive-2.0"]\n'


def guest_policy(root_bytes, exception):
    if exception != LICENSE_EXCEPTION:
        raise ValueError('unapproved guest license exception')
    return root_bytes + LICENSE_SUFFIX


def policy_receipt_valid(directory, receipt, root_bytes):
    policy = receipt['license_policy']
    if policy['exception'] != LICENSE_EXCEPTION:
        raise ValueError('unapproved guest license exception')
    if hashlib.sha256(root_bytes).hexdigest() != policy['root_config_sha256']:
        raise ValueError('root policy changed')
    config = directory / 'aube-deny.toml'
    if config.read_bytes() != guest_policy(root_bytes, policy['exception']):
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
