"""Build receipt checks shared by observations and unit tests."""
import hashlib
import pathlib
import struct


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def static_elf(data):
    if len(data) < 64 or data[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('not ELF64 little endian')
    if struct.unpack_from('<H', data, 18)[0] != 62:
        raise ValueError('not x86-64')
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    if size < 56 or count == 0 or offset + size * count > len(data):
        raise ValueError('invalid program headers')
    types = [struct.unpack_from('<I', data, offset + i * size)[0] for i in range(count)]
    if 2 in types or 3 in types or 1 not in types:
        raise ValueError('dynamic/interpreted or missing load segment')
    return True


def validate(directory, receipt):
    if receipt['exit'] != 0 or not receipt['source_unchanged']:
        raise ValueError('build failure or modified upstream source')
    for name in ('probe', 'aube'):
        binary = directory / name
        if digest(binary) != receipt['binaries'][name]['sha256']:
            raise ValueError('binary hash differs')
        static_elf(binary.read_bytes())


def snapshot(directory):
    return {str(p.relative_to(directory)): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file()}
