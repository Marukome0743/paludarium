"""U5 current diagnostic evidence; production and comparison rules remain unchanged."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("u3audit", ROOT / ".github/scripts/u3-current-diagnostic.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def listing(text):
    rows = [line.split("  ", 1) for line in text.splitlines()]
    assert len(rows) == len({p for _, p in rows}), "Duplicate input path"
    return {p: d for d, p in rows}

def snapshot(output, compare):
    value = audit.audit.snapshot()
    for name in [".github/scripts/u3-current-diagnostic.py", ".github/workflows/u3-current-verification.yml",
                 ".github/scripts/u5-current-diagnostic.py", ".github/workflows/u5-current-verification.yml"]:
        value += hashlib.sha256((ROOT / name).read_bytes()).hexdigest() + "  " + name + "\n"
    assert len(listing(value)) == 320, "Unexpected input inventory"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(value, encoding="utf-8")
    if compare:
        assert listing(Path(compare).read_text(encoding="utf-8-sig")) == listing(value), "Input path/hash mismatch"
    print("Audited", len(listing(value)), "inputs and both locks")

def validate_lib(path):
    rows = re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;", path.read_text())
    assert sorted(rows) == sorted([("7","0","0"),("27","0","0"),("6","0","0"),("6","0","0")]), rows
    print("U5 46 passed, 0 failed, 0 ignored across four crates")

def validate_diff(path):
    text = path.read_text()
    assert "43 passed; 0 failed; 0 ignored" in text
    rows = []
    for i in range(43):
        p = ROOT / f"target/u5-diff/{i}/manifest.json"
        data = json.loads(p.read_text())
        assert len(data) == 1 and data[0]["case"] == i
        row = data[0]
        assert row["native"] == row["emulated"]
        assert not row["native"]["timeout"] and not row["native"]["stderr"]
        assert row["native"]["exit"] == (17 if i == 16 else 0)
        rows.append(row)
    (path.parent / "differential-manifest.json").write_text(json.dumps(rows, indent=2)+"\n")
    print("Fresh native and emulator: 43 complete cases")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["snapshot", "lib", "diff"])
    p.add_argument("output", type=Path)
    p.add_argument("--compare")
    a = p.parse_args()
    if a.mode == "snapshot": snapshot(a.output, a.compare)
    elif a.mode == "lib": validate_lib(a.output)
    else: validate_diff(a.output)
