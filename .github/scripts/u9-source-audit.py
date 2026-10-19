"""Diagnostic source audit: application inputs, both locks, and executable configuration."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = [
    ".github/workflows/ci.yml",
    ".github/workflows/u5-native-diagnostic.yml",
    ".github/workflows/u11-native-first.yml",
    ".github/workflows/u11-fuzz.yml",
    ".github/workflows/u11-browser-readiness.yml",
    ".github/workflows/u11-native-metadata.yml",
    ".github/workflows/u5-quality.yml",
    ".github/workflows/u11-acceptance.yml",
    ".github/workflows/native-diagnostic.yml",
    ".github/workflows/u6-native-diagnostic.yml",
    ".github/workflows/u11-firefox-diagnostic.yml",
    ".github/workflows/nightly.yml",
    ".github/workflows/u10-native-diagnostic.yml",
    ".github/workflows/u8-native-diagnostic.yml",
    ".github/workflows/u2-production-sanitizers.yml",
    ".github/workflows/u6-quality.yml",
    "ci/linux-dev/Dockerfile",
    "deny.toml",
    "mise.toml",
    ".github/workflows/u9-current-verification.yml",
    ".github/scripts/u9-safari-diagnostic.mjs",
    ".github/scripts/u9-source-audit.py"
]
BASE = ["Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "fuzz/Cargo.toml", "fuzz/Cargo.lock", "fuzz/lsan.supp"]

def snapshot():
    paths = {p for folder in ["crates", "tests", "packages", "scripts", "fuzz/fuzz_targets"]
             for p in (ROOT / folder).rglob("*")
             if p.is_file() and not {"target", "__pycache__"}.intersection(p.parts) and p.suffix != ".wasm"}
    paths.update(ROOT / name for name in BASE + CONFIG)
    return "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.relative_to(ROOT).as_posix() + "\n"
                   for p in sorted(paths))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--compare")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    value = snapshot()
    output.write_text(value, encoding="utf-8")
    if args.compare:
        assert Path(args.compare).read_text(encoding="utf-8-sig") == value, "Source changed during diagnostic"
    print(f"Audited {len(value.splitlines())} inputs and both locks.")
