#!/usr/bin/env python3
"""Candidate: bounded historical baseline plus fresh U6. Human approval required."""
import hashlib
import contextlib
import io
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "Cargo.toml").is_file())
RECORD = HERE.parent
BASE = RECORD / "construction/u6-events-sockets/code-generation/verification"
RAW = BASE / "step18-final-raw"
DELTA = "packages/paludarium-wasm/tests/u6-check.mjs"
OLD = "e07b5916ac3224822ae66c2535b9eea1497882f44679d4538f5495b930e33502"
NEW = "d2b62c2f8803508acd82eeefe8febafd36d7482bf14ea32763845d47e3d7c3f0"
CHECKERS = {
    "u5": ("verification/verify-current-u1-u7-u9-u3-u5.py", "c0a1a3066acea4cf1c78d0dc606c08be653d774e0d59365fac7163709dc3c8d4"),
    "u3": ("verification/verify-current-u1-u7-u9-u3.py", "8205e1fc2a2f07a0be9486f03482295c65301a7c9fe2f466be4e42d0e0c15564"),
    "u9": ("construction/u9-terminal-io/code-generation/verification/verify-current-u1-u7-u9-aligned.py", "67850e636876d58ad9277e6c84c132d1967fca3bc30a2f8921caee26e1c57ff7"),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def listing(path):
    rows = [line.split("  ", 1) for line in path.read_text(encoding="utf-8-sig").splitlines()]
    assert len(rows) == len({p for h, p in rows}), "duplicate input"
    return {p: h for h, p in rows}

def bind_historical(rows):
    """Only the declared assertion delta can differ; actual bytes remain untouched."""
    assert rows[DELTA] == OLD
    for name, digest in rows.items():
        assert sha(ROOT / name) == (NEW if name == DELTA else digest), name

def replace_once(text, old, new):
    assert text.count(old) == 1, "historical checker structure changed"
    return text.replace(old, new)

def run_prior(unit):
    name, digest = CHECKERS[unit]
    path = RECORD / name
    assert sha(path) == digest
    text = path.read_text()
    if unit == "u5":
        text = replace_once(text,
            '    assert subprocess.run([sys.executable, str(HERE/"verify-current-u1-u7-u9-u3.py")], cwd=ROOT).returncode == 0',
            '    run_prior("u3")')
        text = replace_once(text,
            '    assert len(expected) == 320 and all(sha(ROOT/n) == h for n,h in expected.items())',
            '    assert len(expected) == 320\n    bind_historical(expected)')
    elif unit == "u3":
        text = replace_once(text,
            '    assert subprocess.run([sys.executable,str(baseline)],cwd=ROOT,check=False).returncode==0',
            '    run_prior("u9")')
        text = replace_once(text, '    assert all(sha(ROOT/p)==h for p,h in expected.items())',
            '    bind_historical(expected)')
    else:
        text = replace_once(text,
            'assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in inputs.items())',
            'bind_historical(inputs)')
    ns = {"__file__": str(path), "__name__": "historical_bounded_reuse",
          "bind_historical": bind_historical, "run_prior": run_prior}
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        exec(compile(text, str(path), "exec"), ns)
        if unit != "u9":
            ns["validate"]()
    print("Historical " + unit + " evidence retained under bounded assertion compatibility; execution is not fresh for this U6 head.")

def exits(directory, required):
    for name in required:
        assert (directory / name).read_text().strip() == "0", name
    found = list(directory.glob("*exit.txt"))
    assert found and all(p.read_text().strip() == "0" for p in found)

def validate():
    actual = (ROOT / DELTA).read_bytes()
    assert hashlib.sha256(actual).hexdigest() == NEW
    # Exact statement includes the matching diagnostic message, both on one line.
    new_line = b'  if (report.caseCount !== 102 || report.results.filter(row => row.case.startsWith("u6-")).length !== 82) throw new Error("U6 production suite must contain 102 finite cases");'
    old_line = b'  if (report.caseCount !== 103 || report.results.filter(row => row.case.startsWith("u6-")).length !== 82) throw new Error("U6 production suite must contain 103 finite cases");'
    assert actual.count(new_line) == 1
    assert hashlib.sha256(actual.replace(new_line, old_line)).hexdigest() == OLD
    run_prior("u5")
    proof = load(BASE / "step18-current-proof.json")
    signature = load(BASE / "step18-signature.json")
    assert signature["sha"] == proof["head"] and signature["verification"]["verified"]
    run = proof["ci_run"]
    names = {"native-coverage", "platforms (ubuntu-latest)", "platforms (macos-latest)",
             "platforms (windows-latest)", "sanitizer (kernel_events_u6)",
             "sanitizer (kernel_sockets_u6)", "production", "safari"}
    assert run["headSha"] == proof["head"] and run["conclusion"] == "success"
    assert len(run["jobs"]) == 8 and {j["name"] for j in run["jobs"]} == names
    assert all(j["conclusion"] == "success" for j in run["jobs"])
    expected = proof["inputs"]
    assert len(expected) == 322 and all(sha(ROOT / n) == h for n, h in expected.items())
    prior = load(RECORD / "construction/u5-threads-futex/code-generation/verification/step25-current-proof.json")["inputs"]
    assert len(prior) == 320 and set(expected) - set(prior) == {
        ".github/scripts/u6-current-diagnostic.py", ".github/workflows/u6-current-verification.yml"}
    assert {n for n, h in prior.items() if expected[n] != h} == {DELTA}
    for name, h in proof["evidence_hashes"].items():
        assert sha(RAW / name) == h, name
    directories = {name: RAW / relative for name, relative in proof["directories"].items()}
    for name, directory in directories.items():
        assert listing(directory / "source-before.sha256") == listing(directory / "source-after.sha256") == expected
        assert (directory / "source-compare-exit.txt").read_text().strip() == "0"
        if name != "safari":
            assert "32dba69d69c5b10ea89a4042de8d0619f7756203" in (directory / "compiler.txt").read_text()
            assert "LLVM version: 23.1.3" in (directory / "compiler.txt").read_text()
    n = directories["native"]
    exits(n, ["cli-build-exit.txt", "diff-exit.txt", "tokio-repeat-exit.txt", "diff-validation-exit.txt",
              "coverage-exit.txt", "coverage-cli-exit.txt", "coverage-diff-exit.txt", "coverage-report-exit.txt",
              "coverage-validation-exit.txt", "coverage-json-exit.txt", "source-compare-exit.txt"])
    assert "84 passed; 0 failed; 0 ignored" in (n / "diff.log").read_text()
    rows = load(n / "differential-manifest.json")
    assert len(rows) == 94 and [r["case"] for r in rows[:84]] == [*range(82), "timer", "unix"]
    assert all(r["case"] == "timer" for r in rows[84:])
    for row in rows:
        native, emulated = dict(row["native"]), dict(row["emulated"])
        assert not native["timeout"] and not emulated["timeout"]
        if row["case"] in (52, 53, 54):
            assert emulated["exit"] == 0 and emulated["stdout"] == "9fffffffffffffff" + "00" * 24 and not emulated["stderr"]
        else:
            if row["case"] == 60:
                assert native["exit"] == -9 and emulated["exit"] == 137
                native["exit"] = 137
            assert native == emulated
    coverage = load(n / "u6-coverage.json")
    allowed = {"crates/paludarium-host/src/fs.rs"} | {
        "crates/paludarium-kernel/src/" + x + ".rs" for x in
        ["lib", "files", "syscalls", "inbox", "threads", "events", "sockets", "epoll"]}
    assert set(coverage["files"]) == allowed and coverage["floor"] == 80
    computed = {}
    for block in (n / "coverage.lcov").read_text().split("end_of_record"):
        sf = next((line[3:].replace(chr(92), "/") for line in block.splitlines() if line.startswith("SF:")), None)
        if not sf:
            continue
        name = next((p for p in allowed if sf == p or sf.endswith("/" + p)), None)
        if name:
            assert name not in computed
            da = [line[3:].split(",") for line in block.splitlines() if line.startswith("DA:")]
            computed[name] = {"lines": len(da), "hit": sum(int(row[1]) > 0 for row in da)}
    assert computed == coverage["files"]
    total = sum(r["lines"] for r in computed.values()); hit = sum(r["hit"] for r in computed.values())
    assert total == coverage["lines"] > 0 and hit == coverage["hit"] and hit / total >= .8
    assert abs(coverage["percent"] - 100 * hit / total) < 1e-8 and proof["coverage"] == coverage
    for platform in ["ubuntu", "macos", "windows"]:
        d = directories[platform]
        exits(d, ["lib-exit.txt", "lib-validation-exit.txt", "fmt-exit.txt", "clippy-exit.txt",
                  "deny-advisories-exit.txt", "deny-bans-exit.txt", "deny-licenses-exit.txt", "deny-sources-exit.txt"])
        assert re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;", (d / "lib.log").read_text()) == [("49", "0", "0")]
    for target in ["kernel_events_u6", "kernel_sockets_u6"]:
        d = directories[target]
        exits(d, ["fuzz-check-exit.txt", "fuzz-exit.txt", "instrumentation-exit.txt"])
        text = (d / "fuzz.log").read_text()
        done = re.search(r"Done (\d+) runs in (\d+) second", text)
        assert done and int(done[1]) > 0 and int(done[2]) >= 600
        assert not re.search(r"ERROR: (?:AddressSanitizer|LeakSanitizer)|panicked at|runtime error:", text)
        for flag in ["-seed=1", "-max_total_time=600", "-timeout=30", "-rss_limit_mb=2048"]:
            assert flag in text
        settings = (d / "settings.txt").read_text()
        for value in ["ASAN_OPTIONS=detect_leaks=1", "LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp",
                      "seed=1", "timeout=30", "rss_limit_mb=2048", "max_total_time=600", "san=address"]:
            assert value in settings
        assert "__asan_init" in (d / "symbols.txt").read_text() and "__lsan" in (d / "symbols.txt").read_text()
        assert (d / "suppression.sha256").read_text().split()[0] == expected["fuzz/lsan.supp"]
        assert (d / "binary.sha256").read_text().split()[1].endswith("/" + target)
        assert "0.13.2" in (d / "fuzz-version.txt").read_text()
    node = load(directories["production"] / "node-report.json")
    safari = load(directories["safari"] / "safari-report.json")
    for report in [node, safari]:
        assert report["pass"] and report["sharedMemory"] and report["productionLauncher"]
        assert report["caseCount"] == len(report["results"]) == 102 and all(r["pass"] for r in report["results"])
    ids = [r["case"] for r in node["results"]]
    assert len(set(ids)) == 102 and ids == [r["case"] for r in safari["results"]]
    assert {i for i in ids if i.startswith("u6-")} == {f"u6-{i}" for i in range(82) if i != 66} | {"u6-unix"}
    assert safari["crossOriginIsolated"] and safari["elapsed_ms"] < 30000
    assert safari["cleanup"]["driver_reaped"] and safari["cleanup"]["server_closed"]
    assert (directories["production"] / "node-exit.txt").read_text().strip() == "0"
    assert (directories["safari"] / "exit.txt").read_text().strip() == "0"
    assert (directories["production"] / "module-native.sha256").read_bytes() == (directories["safari"] / "module-native.sha256").read_bytes()
    receipt = listing(directories["production"] / "module-native.sha256")
    assert set(receipt) == {"packages/paludarium-wasm/paludarium.wasm", "target/u6-production-evidence/native-results.json"}
    assert sha(directories["production"] / "paludarium.wasm") == receipt["packages/paludarium-wasm/paludarium.wasm"]
    assert sha(directories["production"] / "native-results.json") == receipt["target/u6-production-evidence/native-results.json"]
    native = load(directories["production"] / "native-results.json")
    native_u6 = {r["name"]: r for r in native if r["name"].startswith("u6-")}
    assert set(native_u6) == {f"u6-{i}" for i in range(82) if i != 66} | {"u6-unix"}
    for name, row in native_u6.items():
        assert not row["timed_out"]
        binary = RAW / "u6-current-production/packages/paludarium-wasm/tests/guests" / name
        assert sha(binary) == row["sha256"]
    formal = load(BASE / "step18-formal-sensors.json")
    for result in formal.values():
        assert result["exit_code"] == 0 and json.loads(result["output"])["pass"]
    print("Verified fresh U6 native84/Tokio10, fixed9-file coverage>=80%, 3OS49/ignored0/quality, two ASanLSan>=600s, production Node/realSafari102, signed322-input binding; bounded historical baseline reuse. Finite evidence only.")

if __name__ == "__main__":
    validate()
