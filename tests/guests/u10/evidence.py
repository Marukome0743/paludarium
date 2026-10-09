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


def snapshot(directory):
    return {str(p.relative_to(directory)): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file()}
