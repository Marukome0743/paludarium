"""Explicit approved exception for the immutable U14 aube guest only."""
import hashlib
import tomllib

ROOT_SHA256 = '48881b3279292f43cbd1687636bce894185d35f5163c915a2799aff9f4d9b4e6'
LICENSE_SUFFIX = b'\n[[licenses.exceptions]]\ncrate = "webpki-root-certs@1.0.9"\nallow = ["CDLA-Permissive-2.0"]\n'
EXCEPTION = {'id': 'RUSTSEC-2024-0449', 'package': 'unsafe-libyaml',
             'version': '0.2.11', 'source': 'registry+https://github.com/rust-lang/crates.io-index',
             'approved_date': '2026-10-12',
             'rationale': 'Human-approved fixed aube 2.6.1 guest only; unmaintained advisory, no safe upgrade. Product and probe policy unchanged.'}


def generate(root_bytes, license_policy, lock_bytes, exception=EXCEPTION):
    if exception != EXCEPTION:
        raise ValueError('unapproved advisory exception')
    if hashlib.sha256(root_bytes).hexdigest() != ROOT_SHA256:
        raise ValueError('root policy changed')
    if license_policy != root_bytes + LICENSE_SUFFIX:
        raise ValueError('inherited certificate policy changed')
    packages = tomllib.loads(lock_bytes.decode())['package']
    selected = [p for p in packages if p['name'] == EXCEPTION['package']]
    if len(selected) != 1 or any(selected[0].get(k) != EXCEPTION[k] for k in ('version', 'source')):
        raise ValueError('fixed advisory package identity mismatch')
    if root_bytes.count(b'ignore = []') != 1:
        raise ValueError('root advisory ignore is not empty')
    config = license_policy.replace(b'ignore = []', b'ignore = ["RUSTSEC-2024-0449"]', 1)
    # Parsed confirmation prevents textual replacement affecting a different section.
    if tomllib.loads(config.decode())['advisories']['ignore'] != [EXCEPTION['id']]:
        raise ValueError('advisory exception section mismatch')
    return config, {'exception': dict(EXCEPTION), 'root_sha256': ROOT_SHA256,
                    'lock_sha256': hashlib.sha256(lock_bytes).hexdigest(),
                    'config_sha256': hashlib.sha256(config).hexdigest()}


def verify(root_bytes, license_policy, lock_bytes, config, receipt):
    expected, expected_receipt = generate(root_bytes, license_policy, lock_bytes, receipt['exception'])
    if config != expected or receipt != expected_receipt:
        raise ValueError('guest advisory receipt/config mismatch')


def generate_zip(root_bytes, license_policy, lock_bytes):
    # New source-copy policy changes no audit exception or category.
    if hashlib.sha256(lock_bytes).hexdigest() != 'b08d900a0b72764922da18bb0aec4b6598a8de58050babd9a6d59b6baefe7b89':
        raise ValueError('zip advisory lock mismatch')
    return generate(root_bytes, license_policy, lock_bytes)
