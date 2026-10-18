#!/usr/bin/env python3
"""U8 finite current verification plus unchanged prior U6 verification. Candidate only."""
import hashlib, json, re, runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/"Cargo.toml").is_file())
RECORD=HERE.parent
BASE=RECORD/"construction/u8-process-spawn/code-generation/verification"
RAW=BASE/"step14-final-raw"
PRIOR=HERE/"verify-current-u1-u7-u9-u3-u5-u6.py"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def listing(p):
    rows=[s.split("  ",1) for s in p.read_text(encoding="utf-8-sig").splitlines()]
    assert len(rows)==len({n for h,n in rows})
    return {n:h for h,n in rows}
def exits(d,names):
    assert all((d/n).read_text().strip()=="0" for n in names)
    assert all(p.read_text().strip()=="0" for p in d.glob("*exit.txt"))
def validate():
    assert sha(PRIOR)=="771b88a59e22652068099db99ff1d5ed8342a7444e9a84fe508a74901e3fdd57"
    runpy.run_path(str(PRIOR))["validate"]()
    proof=load(BASE/"step15-current-proof.json")
    signature=load(BASE/"step14-signature.json")
    assert signature["sha"]==proof["head"] and signature["verification"]["verified"]
    run=proof["ci_run"]
    assert run["headSha"]==proof["head"] and run["conclusion"]=="success"
    assert len(run["jobs"])==4 and {j["name"] for j in run["jobs"]}=={"native-coverage","platforms (ubuntu-latest)","platforms (macos-latest)","platforms (windows-latest)"}
    assert all(j["conclusion"]=="success" for j in run["jobs"])
    expected=proof["inputs"]
    assert len(expected)==324 and all(sha(ROOT/n)==h for n,h in expected.items())
    prior=load(RECORD/"construction/u6-events-sockets/code-generation/verification/step18-current-proof.json")["inputs"]
    assert len(prior)==322 and set(expected)-set(prior)=={".github/scripts/u8-current-diagnostic.py",".github/workflows/u8-current-verification.yml"}
    assert all(expected[n]==h for n,h in prior.items())
    for n,h in proof["evidence_hashes"].items():assert sha(RAW/n)==h,n
    directories={n:RAW/p for n,p in proof["directories"].items()}
    for name,d in directories.items():
        assert listing(d/"source-before.sha256")==listing(d/"source-after.sha256")==expected
        assert "32dba69d69c5b10ea89a4042de8d0619f7756203" in (d/"compiler.txt").read_text()
        assert "LLVM version: 23.1.3" in (d/"compiler.txt").read_text()
        exits(d,["source-compare-exit.txt"])
    for platform in ["ubuntu","macos","windows"]:
        d=directories[platform]
        exits(d,["lib-exit.txt","u5-lib-exit.txt","u6-lib-exit.txt","fmt-exit.txt","clippy-exit.txt","deny-advisories-exit.txt","deny-bans-exit.txt","deny-licenses-exit.txt","deny-sources-exit.txt"])
        rows=re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;",(d/"lib.log").read_text())
        assert sorted(rows)==sorted([("42","0","0"),("7","0","0"),("7","0","0")])
        names=re.findall(r"^test (.+) \.\.\. ok$",(d/"lib.log").read_text(),re.M)
        assert len(names)==len(set(names))==56
        assert sum(n.startswith("sockets::u8_pipe_tests::") for n in names)==7
        assert sum(n.startswith("threads::u8_exec_thread_tests::") for n in names)==7
        assert sorted(re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;",(d/"u5-lib.log").read_text()))==sorted([("27","0","0"),("6","0","0")])
        assert re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;",(d/"u6-lib.log").read_text())==[("49","0","0")]
    n=directories["native"]
    exits(n,["cli-build-exit.txt","diff-exit.txt","diff-validation-exit.txt","coverage-exit.txt","coverage-report-exit.txt"])
    text=(n/"diff.log").read_text()
    assert "30 passed; 0 failed; 0 ignored" in text and "test u8_runner_ready ... ok" in text
    cases=re.findall(r'u8_(\w+) => \("([^"]+)"',(ROOT/"crates/paludarium-harness/tests/diff_u8.rs").read_text())
    assert len(cases)==29
    for test,mode in cases:
        assert f"test linux::u8_{test} ... ok" in text and f"{mode}: native " in text
    for required in ["wait-fault","spawn","status","output","missing"]:assert required in {m for t,m in cases}
    native=load(n/"coverage-native-input-receipt.json")
    assert [(r["name"],r["rows"],r["exit"]) for r in native]==[("observe",23576,0),("fault-observe",1162,0),("cpuid-observe",12,0)]
    cov=load(n/"coverage.json")["data"][0]
    total=cov["totals"]["lines"]
    assert total==proof["coverage"] and total["count"]>0 and total["covered"]/total["count"]>=.8
    assert sum(f["summary"]["lines"]["count"] for f in cov["files"])==total["count"]
    coverage=(n/"coverage.log").read_text()
    for name,count in [("diff_u8",30),("diff_u5",43),("diff_u6",84)]:
        assert name in coverage and f"{count} passed; 0 failed; 0 ignored" in coverage
    reuse=load(BASE/"step15-sanitizer-reuse.json")
    assert len(reuse["production_dependencies"])==132
    assert all(expected[p]==h for p,h in reuse["production_dependencies"].items())
    for entry in reuse["proofs"].values():
        path=ROOT/entry["proof_path"];assert sha(path)==entry["proof_sha256"]
        old=load(path)
        assert all(old["inputs"][p]==h for p,h in reuse["production_dependencies"].items())
    assert reuse["actual_compiler"]=="32dba69d69c5b10ea89a4042de8d0619f7756203"
    for r in load(BASE/"step15-formal-sensors.json").values():
        assert r["exit_code"]==0 and json.loads(r["output"])["pass"]
    print("Verified current U8 fresh29+runner1, three OS base42+existing14 and U5/U6, unchanged workspace>=80%, signed324 inputs; prior sanitizer evidence reused for equal production dependencies/compiler/settings. U8 browser process execution remains unverified.")
if __name__=="__main__":validate()

