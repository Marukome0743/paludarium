"""U3 diagnostic capture; no production semantics or expected states."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("u9audit", ROOT / ".github/scripts/u9-source-audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def snapshot(output, compare=None):
    value = audit.snapshot()
    for name in [".github/scripts/u3-current-diagnostic.py", ".github/workflows/u3-current-verification.yml"]:
        value += hashlib.sha256((ROOT / name).read_bytes()).hexdigest() + "  " + name + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(value)
    if compare:
        def listing(text):
            rows = [line.split("  ", 1) for line in text.splitlines()]
            assert len(rows) == len({path for _, path in rows}), "Duplicate input path"
            return {path: digest for digest, path in rows}
        assert listing(Path(compare).read_text(encoding="utf-8-sig")) == listing(value), "Input path/hash mismatch"
    print("Audited", len(value.splitlines()), "inputs and both locks")

def native(output):
    output.mkdir(parents=True, exist_ok=True)
    receipts = []
    for binary, count in [("observe", 23576), ("fault-observe", 1162), ("cpuid-observe", 12)]:
        started = time.monotonic()
        p = subprocess.Popen([str(ROOT / "target/u3-guests" / binary)], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(p.pid, signal.SIGKILL)
            stdout, stderr = p.communicate()
        (output / (binary + ".native")).write_bytes(stdout)
        (output / (binary + ".stderr")).write_bytes(stderr)
        receipt = dict(binary=binary, rows=len(stdout.splitlines()), expected_rows=count,
                       exit=p.returncode, timeout=timed_out, reaped=p.poll() is not None,
                       elapsed_seconds=time.monotonic()-started,
                       sha256=hashlib.sha256(stdout).hexdigest())
        receipts.append(receipt)
        (output / "receipt.json").write_text(json.dumps(receipts, indent=2)+"\n")
        assert p.returncode == 0 and not timed_out and not stderr and receipt["rows"] == count, receipt
    print(json.dumps(receipts))

def bind(native_dir):
    names = {"PALUDARIUM_U3_NATIVE_OBSERVATIONS":"observe",
             "PALUDARIUM_U3_NATIVE_FAULTS":"fault-observe",
             "PALUDARIUM_U3_NATIVE_CPUID":"cpuid-observe"}
    receipt = json.loads((native_dir / "receipt.json").read_text())
    assert len(receipt) == 3
    for key, binary in names.items():
        path = (native_dir / (binary+".native")).resolve()
        r = next(r for r in receipt if r["binary"] == binary)
        assert r["exit"] == 0 and r["reaped"] and not r["timeout"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r["sha256"]
        assert len(path.read_bytes().splitlines()) == r["expected_rows"]
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as f:
            f.write(key+"="+path.as_posix()+"\n")
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as f:
        f.write("PALUDARIUM_U3_FULL_REPLAY=1\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["snapshot","native","bind"])
    p.add_argument("output", type=Path)
    p.add_argument("--compare")
    a = p.parse_args()
    if a.mode == "snapshot": snapshot(a.output, a.compare)
    elif a.mode == "native": native(a.output)
    else: bind(a.output)
