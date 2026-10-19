#!/usr/bin/env python3
"""U1/U7/U9 baseline plus fresh U3 evidence. Execute only after human command approval."""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/"Cargo.toml").is_file())
RECORD=ROOT/"aidlc/spaces/default/intents/261004-rust-blink-port"
BASE=RECORD/"construction/u3-sse/code-generation/verification"
RAW=BASE/"step28-final-raw"
ASAN=BASE/"step29-first-asan-raw"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())
def hashes(path):
    rows=[l.split("  ",1) for l in path.read_text(encoding="utf-8-sig").splitlines()]
    assert len(rows)==len({r[1] for r in rows}), "duplicate source"
    return {p:h for h,p in rows}
def exits(directory):
    found={p.relative_to(directory).as_posix():p.read_text().strip() for p in directory.rglob("*exit.txt")}
    assert found and all(v=="0" for v in found.values()), found
    return found
def validate():
    baseline=RECORD/"verification/verify-current-u1-u7-u9-aligned.py"
    assert subprocess.run([sys.executable,str(baseline)],cwd=ROOT,check=False).returncode==0
    proof=load(BASE/"step30-current-proof.json")
    expected=hashes(RAW/"native/source-before.sha256")
    assert len(expected)==318
    assert all(sha(ROOT/p)==h for p,h in expected.items())
    for name in ["native","scoped-ubuntu","scoped-macos","scoped-windows"]:
        d=RAW/name
        assert hashes(d/"source-before.sha256")==expected
        assert hashes(d/"source-after.sha256")==expected
        exits(d)
    sig=load(BASE/"step28-final-signature.json")
    assert sig["sha"]==proof["head"] and sig["commit"]["verification"]["verified"]
    assert proof["ci_run"]["headSha"]==sig["sha"] and proof["ci_run"]["conclusion"]=="success"
    assert len(proof["ci_run"]["jobs"])==4 and all(j["conclusion"]=="success" for j in proof["ci_run"]["jobs"])
    n=RAW/"native"
    receipts=load(n/"native/receipt.json")
    assert len(receipts)==3
    for name,count in [("observe",23576),("fault-observe",1162),("cpuid-observe",12)]:
        r=next(x for x in receipts if x["binary"]==name)
        p=n/"native"/(name+".native")
        assert r["exit"]==0 and not r["timeout"] and r["reaped"] and r["elapsed_seconds"]<30
        assert r["rows"]==r["expected_rows"]==count and sha(p)==r["sha256"]
        assert len(p.read_text().splitlines())==count and not (n/"native"/(name+".stderr")).read_bytes()
    matrix=(n/"matrix.log").read_text()
    assert "40 passed; 0 failed; 0 ignored" in matrix and "12 passed; 0 failed; 0 ignored" in matrix
    diff=(n/"diff-u3.log").read_text()
    assert "test u3_fresh_native_differential ... ok" in diff and "11 passed; 0 failed; 2 ignored" in diff
    extra=(n/"diff-explicit-ignored.log").read_text()
    assert "2 passed; 0 failed; 0 ignored" in extra
    for test in ["u3_saved_observation_replay","u3_native_observation"]: assert "test "+test+" ... ok" in extra
    for platform in ["ubuntu","macos","windows"]:
        d=RAW/("scoped-"+platform)
        assert "40 passed; 0 failed; 0 ignored" in (d/"cpu.log").read_text()
        assert "12 passed; 0 failed; 0 ignored" in (d/"decoder.log").read_text()
    allowed={"paludarium-cpu/src/"+x+".rs" for x in ["alu","cpuid","crypto","exec","lib","softfloat","sse","state"]}|{"paludarium-decoder/src/lib.rs"}
    files=load(n/"coverage.json")["data"][0]["files"]
    chosen={f["filename"].split("/crates/",1)[1]:f["summary"]["lines"] for f in files if "/crates/" in f["filename"] and f["filename"].split("/crates/",1)[1] in allowed}
    assert set(chosen)==allowed
    assert {f["filename"].split("/crates/",1)[1] for f in files}==allowed
    lf=sum(v["count"] for v in chosen.values());lh=sum(v["covered"] for v in chosen.values())
    assert lf>0 and lh/lf>=0.8 and proof["coverage"]["LF"]==lf and proof["coverage"]["LH"]==lh
    totals=next(line.split() for line in (n/"coverage.log").read_text().splitlines() if line.startswith("TOTAL "))
    assert int(totals[7])==lf and int(totals[8])==lf-lh and abs(float(totals[9].rstrip("%"))-100*lh/lf)<0.01
    lcov={}
    for block in (n/"coverage.lcov").read_text().split("end_of_record"):
        sf=next((l[3:] for l in block.splitlines() if l.startswith("SF:")),None)
        if not sf: continue
        key=sf.split("/crates/",1)[1]
        assert key in allowed
        lcov[key]={k:int(next(l[3:] for l in block.splitlines() if l.startswith(k+":"))) for k in ["LF","LH"]}
    assert set(lcov)==allowed
    assert all(lcov[k]["LF"]==chosen[k]["count"] and lcov[k]["LH"]==chosen[k]["covered"] for k in allowed)
    for rootdir,evidence in [("step28-final-raw",proof["fresh_evidence_hashes"]),("step29-first-asan-raw",proof["asan_evidence_hashes"])]:
        for path,h in evidence.items(): assert sha(BASE/rootdir/path)==h,path
    initial=load(BASE/"step28-signature.json")
    assert initial["commit"]["verification"]["verified"] and initial["sha"]==proof["asan_ci_run"]["headSha"]
    assert proof["asan_ci_run"]["conclusion"]=="failure", "first overall run must remain failed history"
    completed={j["name"]:j for j in proof["asan_ci_run"]["jobs"]}
    original_sha=sha(BASE/"step28-first-workflow.yml")
    for target in ["cpu_u2","mmu_u2","decode"]:
        d=ASAN/target
        assert completed["asan ("+target+")"]["conclusion"]=="success"
        prior=hashes(d/"source-before.sha256")
        assert hashes(d/"source-after.sha256")==prior and len(prior)==318
        delta={p for p in expected if expected[p]!=prior[p]}
        assert delta=={".github/workflows/u3-current-verification.yml",".github/scripts/u3-current-diagnostic.py"}
        assert prior[".github/workflows/u3-current-verification.yml"]==original_sha
        assert prior[".github/scripts/u3-current-diagnostic.py"]==sha(BASE/"step28-first-helper.py")
        exits(d)
        settings=(d/"settings.txt").read_text()
        for value in ["seed=1","sanitizer=address","LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp","ASAN_OPTIONS=detect_leaks=1"]:assert value in settings
        env=(d/"environment.log").read_text()
        for value in ["32dba69d69c5b10ea89a4042de8d0619f7756203","LLVM version: 23.1.3","cargo-fuzz 0.13.2"]:assert value in env
        log=(d/(target+".log")).read_text()
        match=re.search(r"Done (\d+) runs in (\d+) second",log)
        assert match and int(match[1])>0 and int(match[2])>=600
        for value in ["-seed=1","-max_total_time=600","-timeout=30","-rss_limit_mb=2048"]:assert value in log
        symbols=(d/"binary-symbols.txt").read_text()
        assert "__asan" in symbols and "__lsan" in symbols
    reuse=load(BASE/"step29-reuse-binding.json")
    assert sha(BASE/"step29-reuse-binding.json")==proof["reused_u9_proof_sha256"]
    for p,h in reuse["sanitizer_binding"]["production_closure"].items():assert expected[p]==h
    assert reuse["sanitizer_binding"]["actual_compiler"]["rustc_commit"]=="32dba69d69c5b10ea89a4042de8d0619f7756203"
    binding=reuse["instruction_binding"]
    audit=load(ROOT/binding["audit_path"])
    assert sha(ROOT/binding["audit_path"])==binding["audit_sha256"]
    assert len(audit["rows"])==136
    normal=collections.Counter(l.split("|",1)[0] for l in (n/"native/observe.native").read_text().splitlines())
    encodings=collections.defaultdict(set)
    for line in (n/"native/observe.native").read_text().splitlines():
        parts=line.split("|")
        encodings[parts[0]].add(parts[3])
    fault=collections.Counter(l.split("|",1)[0] for l in (n/"native/fault-observe.native").read_text().splitlines())
    mapped={}
    for row in audit["rows"]:
        assert row["implementation_paths"] and row["cases"] and row["comparison_mask"]
        for case in row["cases"]:
            if case["case"] in mapped:assert mapped[case["case"]]==case
            mapped[case["case"]]=case
            assert normal[case["case"]]==case["normal_rows"] and fault[case["case"]]==case["fault_rows"]
            assert encodings[case["case"]]==set(case["encodings"])
    assert len(mapped)==568
    fixed=load(BASE/"step25-fixed-binary-proof.json")
    assert fixed["current_binary_bytes_verified"] and len(fixed["binary_hashes"])==3
    for path,digest in fixed["binary_hashes"].items(): assert sha(ROOT/path)==digest
    extra_cases={x["case"]:x for x in audit["auxiliary_cases"]}
    assert len(extra_cases)==9 and not set(extra_cases).intersection(mapped)
    assert set(normal)==set(mapped)|set(extra_cases) and set(fault)==set(normal)
    for case in extra_cases.values():assert normal[case["case"]]==case["normal_rows"] and fault[case["case"]]==case["fault_rows"]
    for p,h in binding["mapping_source_hashes"].items():assert expected[p]==h
    print("Verified fresh U3 native23576/fault1162/CPUID12, matrix40/12, explicit replay/collection2, 3OS, same9-file coverage>=80%, signed separate-run ASan3>=600s; bounded U9 production/four-ASan reuse. Finite evidence only.")
if __name__=="__main__":validate()
