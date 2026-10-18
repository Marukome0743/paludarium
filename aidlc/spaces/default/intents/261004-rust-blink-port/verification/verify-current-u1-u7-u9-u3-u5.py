#!/usr/bin/env python3
"""Approved baseline plus fresh U5 proof. Candidate: human approval required to execute."""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/"Cargo.toml").is_file())
RECORD = ROOT/"aidlc/spaces/default/intents/261004-rust-blink-port"
BASE = RECORD/"construction/u5-threads-futex/code-generation/verification"
RAW = BASE/"step24-final-raw"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def listing(p):
    rows = [x.split("  ", 1) for x in p.read_text(encoding="utf-8-sig").splitlines()]
    assert len(rows) == len({p for h,p in rows}), "Duplicate source path"
    return {p:h for h,p in rows}
def check_exits(d, required):
    for name in required:
        assert (d/(name+"-exit.txt")).read_text().strip() == "0", name
    found = list(d.glob("*exit.txt"))
    assert found and all(x.read_text().strip() == "0" for x in found)
def validate():
    assert subprocess.run([sys.executable, str(HERE/"verify-current-u1-u7-u9-u3.py")], cwd=ROOT).returncode == 0
    p = load(BASE/"step25-current-proof.json")
    formal = load(BASE/"step25-formal-sensors.json")
    assert formal["corrected"]["exit_code"] == 0
    assert json.loads(formal["corrected"]["output"])["pass"]
    assert formal["required_sections"]["exit_code"] == 0
    assert json.loads(formal["required_sections"]["output"])["pass"]
    sig = load(BASE/"step24-signature.json")
    assert sig["sha"] == p["head"] and sig["commit"]["verification"]["verified"]
    assert p["ci_run"]["headSha"] == p["head"] and p["ci_run"]["conclusion"] == "success"
    names = {"native-coverage", "platforms (ubuntu-latest)", "platforms (macos-latest)",
             "platforms (windows-latest)", "sanitizer (kernel_threads_u5)", "sanitizer (kernel_futex_u5)"}
    assert len(p["ci_run"]["jobs"]) == 6 and {j["name"] for j in p["ci_run"]["jobs"]} == names
    assert all(j["conclusion"] == "success" for j in p["ci_run"]["jobs"])
    expected = p["inputs"]
    assert len(expected) == 320 and all(sha(ROOT/n) == h for n,h in expected.items())
    for name in ["native","platform-ubuntu","platform-macos","platform-windows","kernel_threads_u5","kernel_futex_u5"]:
        d = RAW/name/"target/u5-current-evidence"
        assert listing(d/"source-before.sha256") == listing(d/"source-after.sha256") == expected
        assert "32dba69d69c5b10ea89a4042de8d0619f7756203" in (d/"compiler.txt").read_text()
        assert "LLVM version: 23.1.3" in (d/"compiler.txt").read_text()
        assert (d/"source-compare-exit.txt").read_text().strip() == "0"
    n = RAW/"native/target/u5-current-evidence"
    check_exits(n, ["cli-build", "diff", "diff-validation", "coverage", "coverage-validation", "coverage-json", "source-compare"])
    assert "43 passed; 0 failed; 0 ignored" in (n/"diff.log").read_text()
    differential = load(n/"differential-manifest.json")
    assert len(differential) == 43 and {x["case"] for x in differential} == set(range(43))
    for row in differential:
        assert row["native"] == row["emulated"] and not row["native"]["timeout"] and not row["native"]["stderr"]
        assert row["native"]["exit"] == (17 if row["case"] == 16 else 0)
        original = load(RAW/"native/target/u5-diff"/str(row["case"])/"manifest.json")
        assert original == [row]
    coverage = load(n/"u5-coverage.json")
    allowed = {"crates/paludarium-host/src/"+x+".rs" for x in ["lib","threads","native_fs"]}
    allowed |= {"crates/paludarium-kernel/src/"+x+".rs" for x in ["lib","files","syscalls","inbox","threads","futex","signals"]}
    allowed |= {"crates/paludarium-mmu/src/lib.rs", "crates/paludarium-runtime/src/lib.rs","crates/paludarium-runtime/src/workers.rs"}
    assert len(allowed) == 13 and set(coverage["files"]) == allowed and coverage["floor"] == 80
    rows = {}
    for block in (n/"coverage.lcov").read_text().split("end_of_record"):
        sf = next((l[3:].replace(chr(92),"/") for l in block.splitlines() if l.startswith("SF:")),None)
        if not sf: continue
        key = next((x for x in allowed if sf.endswith("/"+x) or sf == x),None)
        if key:
            assert key not in rows
            da = [l[3:].split(",") for l in block.splitlines() if l.startswith("DA:")]
            rows[key] = {"lines":len(da),"hit":sum(int(x[1]) > 0 for x in da)}
    assert rows == coverage["files"]
    lf = sum(x["lines"] for x in rows.values()); lh = sum(x["hit"] for x in rows.values())
    assert coverage["lines"] == lf > 0 and coverage["hit"] == lh and lh/lf >= .8
    assert abs(coverage["percent"]-100*lh/lf) < 1e-8 and p["coverage"] == coverage
    for platform in ["ubuntu","macos","windows"]:
        d = RAW/("platform-"+platform)/"target/u5-current-evidence"
        check_exits(d, ["lib","lib-validation","fmt","clippy","deny-advisories","deny-bans","deny-licenses","deny-sources","source-compare"])
        result = re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;", (d/"lib.log").read_text())
        assert collections.Counter(result) == collections.Counter([("7","0","0"),("27","0","0"),("6","0","0"),("6","0","0")])
        assert "0.20.2" in (d/"deny-version.txt").read_text()
    for target in ["kernel_threads_u5","kernel_futex_u5"]:
        d = RAW/target/"target/u5-current-evidence"
        check_exits(d, ["fuzz-check","fuzz","instrumentation","source-compare"])
        text = (d/"fuzz.log").read_text()
        done = re.search(r"Done (\d+) runs in (\d+) second",text)
        assert done and int(done[1]) > 0 and int(done[2]) >= 600
        for flag in ["-seed=1","-max_total_time=600","-timeout=30","-rss_limit_mb=2048"]: assert flag in text
        settings = (d/"settings.txt").read_text()
        for value in ["ASAN_OPTIONS=detect_leaks=1","LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp","seed=1","timeout=30","rss_limit_mb=2048","max_total_time=600","san=address"]: assert value in settings
        assert "0.13.2" in (d/"fuzz-version.txt").read_text()
        symbols = (d/"symbols.txt").read_text()
        assert "__asan_init" in symbols and "__lsan" in symbols
        assert (d/"suppression.sha256").read_text().split()[0] == expected["fuzz/lsan.supp"]
        assert (d/"binary.sha256").read_text().split()[1].endswith("/"+target)
    for name,h in p["evidence_hashes"].items(): assert sha(RAW/name) == h,name
    reuse = load(BASE/"step25-browser-reuse.json")
    assert sha(BASE/"step25-browser-reuse.json") == p["browser_reuse_sha256"]
    u9 = RECORD/"construction/u9-terminal-io/code-generation/verification/step20-fixed-proof.json"
    assert sha(u9) == reuse["proof_sha256"]
    assert all(expected[n] == h for n,h in reuse["proof_inputs"].items())
    assert reuse["compiler"]["rustc_commit"] == "32dba69d69c5b10ea89a4042de8d0619f7756203"
    for name,r in reuse["reports"].items():
        report = load(ROOT/name)
        assert sha(ROOT/name) == r["sha256"] and report["pass"] and report["caseCount"] == 20
        cases = {x["case"]:x for x in report["results"]}
        assert len(cases) == 20 and all(cases[x]["pass"] for x in reuse["reused_cases"])
    print("Verified fresh U5 native43, 3OS scoped46/ignored0 and quality, fixed13-file coverage>=80%, both ASanLSan>=600s, signed320-input binding; bounded U9 shared browser reuse. Finite evidence only.")
if __name__ == "__main__": validate()
