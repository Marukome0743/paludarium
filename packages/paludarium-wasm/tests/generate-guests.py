"""Deterministic freestanding x86-64 Linux ELF fixtures; no assembler dependency."""
import argparse
import pathlib
import struct

CODES = {
    "hello": "b801000000bf0100000048be0020400000000000ba060000000f05b83c00000031ff0f05",
    "integer": "b80700000083c02389c7b83c0000000f05",
    "atomic": "48b90020400000000000b801000000f0480fc1014883c02a4889c7b83c0000000f05",
    "divide_fault": "31d231c931c0f7f1",
    "stdin": "31c031ff48be0020400000000000ba060000000f054889c2b801000000bf010000000f05b83c00000031ff0f05",
    "infinite": "ebfe",
}


def guest(name):
    code = bytes.fromhex(CODES[name])
    data = bytes(64) if name in ("stdin", "infinite") else b"hello\n"
    ident = b"\x7fELF\x02\x01\x01" + bytes(9)
    header = ident + struct.pack("<HHIQQQIHHHHHH", 2, 62, 1, 0x401000, 64, 0, 0, 64, 56, 2, 0, 0, 0)
    code_segment = struct.pack("<IIQQQQQQ", 1, 5, 4096, 0x401000, 0x401000, len(code), len(code), 4096)
    data_segment = struct.pack("<IIQQQQQQ", 1, 6, 8192, 0x402000, 0x402000, len(data), len(data), 4096)
    image = bytearray(8192 + len(data))
    image[:176] = header + code_segment + data_segment
    image[4096:4096 + len(code)] = code
    image[8192:] = data
    return bytes(image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    directory = pathlib.Path(__file__).parent / "guests"
    directory.mkdir(exist_ok=True)
    for name in CODES:
        path = directory / name
        image = guest(name)
        if args.check:
            if path.read_bytes() != image:
                raise SystemExit(f"Fixture differs: {name}")
        else:
            path.write_bytes(image)
            path.chmod(0o755)
    print("All six deterministic ELF fixtures match" if args.check else "Generated six ELF fixtures")
