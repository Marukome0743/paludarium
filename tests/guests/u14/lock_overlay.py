"""One approved U14 build-copy overlay; immutable upstream remains evidence."""
import hashlib
import json
import shutil
import tomllib

ORIGINAL = '8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668'
UPDATED = 'b8d403f2c449da8eb104cca0cbd1c9f1f61ade8249615c246ae6cc8cd531db0e'
REGISTRY = 'registry+https://github.com/rust-lang/crates.io-index'
OLD_CHECKSUM = '0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634'
NEW_CHECKSUM = '48e13bd8c0e9365c43cfa5c9e8f9ad49d3c8444926c9aac819e0e4dc503c8fdf'
SOURCE = '54952fbb7982b5a046b74aa8323e6ccb8ff87326ba09149e0ce53b06cdef764e'
BUILD_SOURCE = 'a5eab8fb7e01a82825e6f44547a41968bc1c8bf2860be284ffec599ccecce352'
SOURCE_LINKS = {'AGENTS.md': '.rules', 'CLAUDE.md': '.rules', 'GEMINI.md': '.rules'}
POLICY = {'schema': 1, 'policy': 'u14-fixed-aube', 'package': 'rustls',
          'source': REGISTRY, 'from_version': '0.23.45', 'to_version': '0.23.46',
          'from_checksum': OLD_CHECKSUM, 'to_checksum': NEW_CHECKSUM,
          'original_lock_sha256': ORIGINAL, 'build_lock_sha256': UPDATED,
          'package_count': 604, 'original_source_sha256': SOURCE,
          'build_source_sha256': BUILD_SOURCE}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot_sha(files):
    return sha(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())


def verify_links(directory):
    links = {str(p.relative_to(directory)): str(p.readlink())
             for p in directory.rglob('*') if p.is_symlink()}
    if directory.is_symlink() or links != SOURCE_LINKS:
        raise ValueError('overlay source symlink identity mismatch')


def validate_pair(original, updated, policy):
    if policy != POLICY:
        raise ValueError('unapproved U14 lock overlay policy')
    before = tomllib.loads(original.decode())
    after = tomllib.loads(updated.decode())
    old, new = before['package'], after['package']
    selected = [i for i, p in enumerate(old) if p['name'] == 'rustls']
    if len(selected) != 1 or len(old) != 604 or len(new) != 604:
        raise ValueError('overlay package count or rustls identity mismatch')
    index = selected[0]
    expected = dict(old[index], version='0.23.46', checksum=NEW_CHECKSUM)
    if (old[index].get('version') != '0.23.45'
            or old[index].get('checksum') != OLD_CHECKSUM
            or old[index].get('source') != REGISTRY or new[index] != expected):
        raise ValueError('overlay rustls version/checksum/source/dependencies mismatch')
    if dict(after, package=new[:index] + [old[index]] + new[index + 1:]) != before:
        raise ValueError('overlay changed another package or lock metadata')
    marker = b'name = "rustls"\nversion = "0.23.45"'
    if original.count(marker) != 1 or original.count(OLD_CHECKSUM.encode()) != 1:
        raise ValueError('overlay original text boundary mismatch')
    exact = original.replace(marker, b'name = "rustls"\nversion = "0.23.46"', 1)
    exact = exact.replace(OLD_CHECKSUM.encode(), NEW_CHECKSUM.encode(), 1)
    if updated != exact or sha(original) != ORIGINAL or sha(updated) != UPDATED:
        raise ValueError('overlay lock digest or exact two-line difference mismatch')


def updated_lock(original, policy):
    updated = original.replace(b'name = "rustls"\nversion = "0.23.45"',
                               b'name = "rustls"\nversion = "0.23.46"', 1)
    updated = updated.replace(OLD_CHECKSUM.encode(), NEW_CHECKSUM.encode(), 1)
    validate_pair(original, updated, policy)
    return updated


def prepare(upstream, destination, policy_name, policy, snapshot):
    if policy_name == ZIP_POLICY['policy']:
        return prepare_zip(upstream, destination, policy, snapshot)
    if policy_name != POLICY['policy']:
        raise ValueError('overlay is U14 only')
    original = (upstream / 'Cargo.lock').read_bytes()
    updated = updated_lock(original, policy)
    if destination.exists():
        raise ValueError('overlay copy exists')
    verify_links(upstream)
    before = snapshot(upstream)
    if snapshot_sha(before) != SOURCE:
        raise ValueError('overlay original source digest mismatch')
    shutil.copytree(upstream, destination, symlinks=True)
    (destination / 'Cargo.lock').write_bytes(updated)
    build_before = snapshot(destination)
    verify_snapshots(before, build_before)
    return {'policy': dict(POLICY), 'original_lock': original.decode(),
            'build_lock': updated.decode(), 'source_before': before,
            'build_source_before': build_before}


def verify_snapshots(original, build):
    if original.get('Cargo.lock') != ORIGINAL or build.get('Cargo.lock') != UPDATED:
        raise ValueError('overlay snapshot lock identity mismatch')
    if dict(build, **{'Cargo.lock': ORIGINAL}) != original:
        raise ValueError('overlay changed source outside Cargo.lock')
    if snapshot_sha(original) != SOURCE or snapshot_sha(build) != BUILD_SOURCE:
        raise ValueError('overlay source snapshot digest mismatch')


def finish(upstream, destination, overlay, snapshot):
    verify_links(upstream)
    verify_links(destination)
    overlay['source_after'] = snapshot(upstream)
    overlay['build_source_after'] = snapshot(destination)
    verify(overlay)


def verify(overlay):
    if overlay['policy'].get('policy') == ZIP_POLICY['policy']:
        return verify_zip(overlay)
    validate_pair(overlay['original_lock'].encode(), overlay['build_lock'].encode(), overlay['policy'])
    verify_snapshots(overlay['source_before'], overlay['build_source_before'])
    if (overlay['source_before'] != overlay['source_after']
            or overlay['build_source_before'] != overlay['build_source_after']):
        raise ValueError('overlay original or build source changed during audit/build')


# A separately approved source-copy policy; the original U14 policy is immutable.
ZIP_OLD_CHECKSUM = '2d04a6b5381502aa6087c94c669499eb1602eb9c5e8198e534de571f7154809b'
ZIP_NEW_CHECKSUM = 'a954114b47a54df49f83d2722814e86b23d4bb1b54a1b90fb7d92b41619ddc22'
ZIP_LOCK = 'b08d900a0b72764922da18bb0aec4b6598a8de58050babd9a6d59b6baefe7b89'
ZIP_MANIFEST_ORIGINAL = 'c3c9d286af517fa85ef8b2aa2286ef503e5bb09b11242bf1eac00f40ab1d3850'
ZIP_MANIFEST = 'f776a219b6844f32527045492511290cd611e351709212eb8c867717b349817c'
ZIP_SOURCE = 'd4375aa7b8b4049b0d14ca49eaa718ed4402f3d82247b9c80d8cbc93ca76f57a'
ZIP_POLICY = dict(POLICY, schema=2, policy='u15-fixed-aube-zip9',
                  build_lock_sha256=ZIP_LOCK, build_source_sha256=ZIP_SOURCE,
                  original_manifest_sha256=ZIP_MANIFEST_ORIGINAL,
                  build_manifest_sha256=ZIP_MANIFEST,
                  zip_from_version='8.6.0', zip_to_version='9.0.4',
                  zip_from_checksum=ZIP_OLD_CHECKSUM, zip_to_checksum=ZIP_NEW_CHECKSUM)


def zip_bytes(original_lock, original_manifest, policy):
    if policy != ZIP_POLICY:
        raise ValueError('unapproved zip overlay policy')
    repaired = updated_lock(original_lock, POLICY)
    before = tomllib.loads(repaired.decode())
    selected = [p for p in before['package'] if p['name'] == 'zip']
    if (len(selected) != 1 or selected[0]['version'] != '8.6.0'
            or selected[0]['checksum'] != ZIP_OLD_CHECKSUM
            or selected[0]['source'] != REGISTRY
            or selected[0]['dependencies'] != ['crc32fast', 'flate2', 'indexmap 2.14.0', 'memchr', 'typed-path', 'zopfli']
            or not any(p['name'] == 'nix' and p['version'] == '0.31.3' for p in before['package'])):
        raise ValueError('zip original package/dependency identity mismatch')
    marker = b'name = "zip"\nversion = "8.6.0"'
    if repaired.count(marker) != 1 or repaired.count(ZIP_OLD_CHECKSUM.encode()) != 1:
        raise ValueError('zip text identity mismatch')
    repaired = repaired.replace(marker, b'name = "zip"\nversion = "9.0.4"', 1)
    repaired = repaired.replace(ZIP_OLD_CHECKSUM.encode(), ZIP_NEW_CHECKSUM.encode(), 1)
    position = repaired.index(b'name = "zip"\n')
    entry = repaired[position:]
    if entry.count(b' "memchr",\n') != 1:
        raise ValueError('zip dependency text boundary mismatch')
    repaired = repaired[:position] + entry.replace(b' "memchr",\n', b' "memchr",\n "nix 0.31.3",\n', 1)
    line = b'zip = { version = "8", default-features = false, features = ["deflate"] }'
    if sha(original_manifest) != ZIP_MANIFEST_ORIGINAL or original_manifest.count(line) != 1:
        raise ValueError('zip original manifest mismatch')
    manifest = original_manifest.replace(line, line.replace(b'"8"', b'"=9.0.4"'), 1)
    if sha(repaired) != ZIP_LOCK or sha(manifest) != ZIP_MANIFEST:
        raise ValueError('zip build lock/manifest digest mismatch')
    return repaired, manifest


def verify_zip_snapshots(original, build):
    if (original.get('Cargo.lock') != ORIGINAL or original.get('Cargo.toml') != ZIP_MANIFEST_ORIGINAL
            or build.get('Cargo.lock') != ZIP_LOCK or build.get('Cargo.toml') != ZIP_MANIFEST
            or dict(build, **{'Cargo.lock': ORIGINAL, 'Cargo.toml': ZIP_MANIFEST_ORIGINAL}) != original
            or snapshot_sha(original) != SOURCE or snapshot_sha(build) != ZIP_SOURCE):
        raise ValueError('zip original/build source snapshot mismatch')


def prepare_zip(upstream, destination, policy, snapshot):
    if destination.exists():
        raise ValueError('overlay copy exists')
    verify_links(upstream)
    original_lock = (upstream / 'Cargo.lock').read_bytes()
    original_manifest = (upstream / 'Cargo.toml').read_bytes()
    lock, manifest = zip_bytes(original_lock, original_manifest, policy)
    before = snapshot(upstream)
    if snapshot_sha(before) != SOURCE:
        raise ValueError('zip original source digest mismatch')
    shutil.copytree(upstream, destination, symlinks=True)
    (destination / 'Cargo.lock').write_bytes(lock)
    (destination / 'Cargo.toml').write_bytes(manifest)
    build = snapshot(destination)
    verify_links(destination)
    verify_zip_snapshots(before, build)
    return dict(policy=dict(ZIP_POLICY), original_lock=original_lock.decode(), build_lock=lock.decode(),
                original_manifest=original_manifest.decode(), build_manifest=manifest.decode(),
                source_before=before, build_source_before=build)


def verify_zip(overlay):
    lock, manifest = zip_bytes(overlay['original_lock'].encode(), overlay['original_manifest'].encode(), overlay['policy'])
    if overlay['build_lock'].encode() != lock or overlay['build_manifest'].encode() != manifest:
        raise ValueError('zip receipt lock/manifest bytes mismatch')
    verify_zip_snapshots(overlay['source_before'], overlay['build_source_before'])
    if (overlay['source_before'] != overlay['source_after']
            or overlay['build_source_before'] != overlay['build_source_after']):
        raise ValueError('zip source changed during audit/build')
