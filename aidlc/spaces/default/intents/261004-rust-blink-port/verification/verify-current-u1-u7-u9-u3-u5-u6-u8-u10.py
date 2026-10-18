"""U10 additional current proof candidate. Execution needs separate human approval."""
import contextlib, hashlib, importlib.util, io, json, math, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
RECORD=Path(__file__).resolve().parents[1]
ROOT=RECORD.parents[4]
UNIT=RECORD/"construction/u10-probe-aube-native/code-generation"
PRIOR=RECORD/"verification/verify-current-u1-u7-u9-u3-u5-u6-u8.py"
PRIOR_SHA="9132f82282911af49a45451a07559d6cbe9fcbffdc9764a2bade8ea242160d34"
MTIME="crates/paludarium-host/src/native_fs.rs"
MTIME_OLD="cb6280537bf2df354444670522bacb492c2bb27d798812bdfdc6d3996bbaa684"
MTIME_NEW="d187196317af221cd79eb1f630366379167ecdb8f0806b41585368a93659d039"
GH="/Users/mutoakio/.local/share/mise/installs/gh/2.102.0/gh_2.102.0_macOS_arm64/bin/gh"
PROOF_SHA="255c162925b28239cb6b2cf7c9f70f30b96ced74ba2a7ca33a2e96eacce467d2"
def need(ok,message):
    if not ok: raise ValueError(message)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def doc(p): return json.loads(p.read_text())
def api(route):
    q=subprocess.run([GH,"api","repos/Marukome0743/paludarium/"+route],capture_output=True,text=True,timeout=60)
    need(q.returncode==0,"GitHub read failed")
    return json.loads(q.stdout)
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/("tests/guests/u10/"+name+".py"))
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def successful(row):
    seconds=row["wall_seconds"]
    need(row["exit"]==0 and row["timed_out"] is False and type(seconds) in (int,float) and math.isfinite(seconds) and 0<=seconds<=30,"guest exit/deadline")
def listing(p):
    rows={}
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        h,name=line.split("  ",1)
        need(name not in rows and re.fullmatch("[0-9a-f]{64}",h),"duplicate/malformed input")
        rows[name]=h
    return rows
def exact_test_delta():
    actual=(ROOT/MTIME).read_bytes()
    need(hashlib.sha256(actual).hexdigest()==MTIME_NEW,"actual mtime test delta changed")
    replacements=[
        (b"for ns in [1, 99, 100, 101, 500_000_000, 1_000_000_000]",b"for ns in [1, 500_000_000, 1_000_000_000]",1),
        (b"for ns in [0, 1, 99, 100, 101, 1_500_000_000, u64::MAX]",b"for ns in [0, 1, 1_500_000_000, u64::MAX]",1),
        (b"            let represented_ns = if cfg!(windows) { ns / 100 * 100 } else { ns };\n",b"",2),
        (b"Ok(-i128::from(represented_ns))",b"Ok(-i128::from(ns))",1),
        (b"Ok(i128::from(represented_ns))",b"Ok(i128::from(ns))",1)]
    old=actual
    for new,previous,count in replacements:
        need(old.count(new)==count,"mtime exact replacement count")
        old=old.replace(new,previous)
    need(hashlib.sha256(old).hexdigest()==MTIME_OLD,"reverse patch changes more than two tests")
    need(actual.split(b"#[cfg(test)]\nmod u7_tests")[0]==old.split(b"#[cfg(test)]\nmod u7_tests")[0],"production prefix changed")
def bind_mtime(rows):
    need(rows[MTIME]==MTIME_OLD,"historical mtime binding")
    for name,digest in rows.items():
        need(sha(ROOT/name)==(MTIME_NEW if name==MTIME else digest),"historical production mismatch:"+name)
def replace_once(text,old,new):
    need(text.count(old)==1,"fixed checker structure changed")
    return text.replace(old,new)
def historical_u6():
    path=RECORD/"verification/verify-current-u1-u7-u9-u3-u5-u6.py"
    need(sha(path)=="771b88a59e22652068099db99ff1d5ed8342a7444e9a84fe508a74901e3fdd57","historical U6 checker changed")
    text=path.read_text()
    text=replace_once(text,
        '        assert sha(ROOT / name) == (NEW if name == DELTA else digest), name',
        '        assert sha(ROOT / name) == (MTIME_NEW if name == MTIME else NEW if name == DELTA else digest), name\n        if name == MTIME: assert digest == MTIME_OLD')
    text=replace_once(text,
        '    assert len(expected) == 322 and all(sha(ROOT / n) == h for n, h in expected.items())',
        '    assert len(expected) == 322\n    bind_mtime(expected)')
    ns={"__file__":str(path),"__name__":"historical_bounded_reuse","MTIME":MTIME,"MTIME_NEW":MTIME_NEW,"MTIME_OLD":MTIME_OLD,"bind_mtime":bind_mtime}
    exec(compile(text,str(path),"exec"),ns)
    ns["validate"]()
def historical_prior():
    need(sha(PRIOR)==PRIOR_SHA,"Prior approved checker changed")
    text=PRIOR.read_text()
    text=replace_once(text,'    runpy.run_path(str(PRIOR))["validate"]()','    historical_u6()')
    text=replace_once(text,'    assert len(expected)==324 and all(sha(ROOT/n)==h for n,h in expected.items())','    assert len(expected)==324\n    bind_mtime(expected)')
    ns={"__file__":str(PRIOR),"__name__":"historical_bounded_reuse","historical_u6":historical_u6,"bind_mtime":bind_mtime}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(text,str(PRIOR),"exec"),ns)
        ns["validate"]()
    print("Historical prior Units retained under exact two-test compatibility; those CI executions are not fresh for this U10 head.")
def validate():
    exact_test_delta()
    historical_prior()
    proof_path=UNIT/"verification/step18-current-proof.json"
    need(sha(proof_path)==PROOF_SHA,"reviewed U10 proof changed")
    proof=doc(proof_path)
    need(proof["status"]=="complete","U10 proof incomplete")
    for name,digest in proof["record_hashes"].items():
        need(sha(UNIT/name)==digest,"reviewed record changed:"+name)
    head,run=proof["head"],proof["run"]
    commit=api("commits/"+head)
    need(commit["sha"]==head and commit["commit"]["verification"]["verified"] is True and commit["commit"]["verification"]["reason"]=="valid","head not Verified")
    ci=api("actions/runs/"+str(run))
    jobs=api("actions/runs/"+str(run)+"/jobs?per_page=100")["jobs"]
    expected_jobs={"native-coverage","sanitizer-binding","platforms (ubuntu-latest)","platforms (macos-latest)","platforms (windows-latest)"}
    need(ci["head_sha"]==head and ci["conclusion"]=="success" and len(jobs)==5 and {j["name"] for j in jobs}==expected_jobs and all(j["conclusion"]=="success" for j in jobs),"U10 CI/job binding")
    inputs=proof["inputs"]
    need(len(inputs)==326 and all(sha(ROOT/p)==h for p,h in inputs.items()),"current326 mismatch")
    old_inputs=doc(RECORD/"construction/u8-process-spawn/code-generation/verification/step15-current-proof.json")["inputs"]
    need(set(inputs)-set(old_inputs)=={".github/scripts/u10-current-diagnostic.py",".github/workflows/u10-current-verification.yml"},"unapproved input addition")
    need({p for p,h in old_inputs.items() if inputs[p]!=h}=={MTIME},"unapproved historical source change")
    need(old_inputs[MTIME]==MTIME_OLD and inputs[MTIME]==MTIME_NEW,"exact test-only source delta")
    base=UNIT/"verification/step18-final3-raw"
    raw_hashes={}
    for name,digest in proof["raw_manifests"].items():
        manifest=UNIT/"verification"/name
        need(sha(manifest)==digest,"raw manifest changed:"+name)
        rows=doc(manifest)
        need(not set(rows)&set(raw_hashes),"duplicate raw manifest entries")
        raw_hashes.update(rows)
    need({str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()}==set(raw_hashes),"raw file set changed")
    for p,h in raw_hashes.items(): need(sha(base/p)==h,"raw changed:"+p)
    for relative in proof["directories"].values():
        e=base/relative
        need(listing(e/"source-before.sha256")==listing(e/"source-after.sha256")==inputs,"before/after/current326 mismatch")
        need("32dba69d69c5b10ea89a4042de8d0619f7756203" in (e/"compiler.txt").read_text() and "LLVM version: 23.1.3" in (e/"compiler.txt").read_text(),"actual compiler")
        for p in e.glob("*-exit.txt"): need(p.read_text().strip()=="0","actual exit failed:"+str(p))
    e=base/proof["directories"]["native"]
    for name in ["wasm-build","native","coverage-env-preflight","source-compare","diff","coverage-report","coverage","guest-build","python-coverage","coverage-u10"]:
        need((e/(name+"-exit.txt")).read_text().strip()=="0","required native exit missing/failed:"+name)
    need((e/"python-version.txt").read_text().strip()=="Python 3.15.0","native Python latest diagnostic pin")
    for os in ("ubuntu-latest","macos-latest","windows-latest"):
        platform=base/proof["directories"][os]
        need((platform/"python-host-version.txt").read_text().strip()=="Python 3.15.0","platform Python latest diagnostic pin")
        for name in ["lib","harness-lib","u5-lib","u6-lib","fmt","clippy","deny-advisories","deny-bans","deny-licenses","deny-sources","source-compare"]:
            need((platform/(name+"-exit.txt")).read_text().strip()=="0","required platform exit missing/failed:"+name)
        for test in ("u7_mtime_system_time_before_epoch","u7_mtime_system_time_epoch_positive_range"):
            need(re.search(r"test .*"+test+r" \.\.\. ok",(platform/"lib.log").read_text()),"mtime boundary missing:"+os+test)
        need("27 passed; 0 failed; 0 ignored" in (platform/"u5-lib.log").read_text() and "6 passed; 0 failed; 0 ignored" in (platform/"u5-lib.log").read_text(),"U5 regressions missing")
        need("49 passed; 0 failed; 0 ignored" in (platform/"u6-lib.log").read_text(),"U6 regressions missing")
    need("Ran 44 tests" in (e/"python-tests.log").read_text() and "\nOK\n" in (e/"python-tests.log").read_text(),"Python44 missing")
    need("test u10_differential ... ok" in (e/"diff.log").read_text() and "test u10_differential ... ok" in (e/"coverage-u10.log").read_text(),"differential body not executed")
    receipt=doc(base/proof["guest_directory"]/"build-receipt.json")
    need(receipt["exit"]==0 and receipt["source_unchanged"] and receipt["source_before"]==receipt["source_after"] and len(receipt["source_before"])==1365 and receipt["toolchain"]=="nightly-2026-10-10","guest build provenance")
    evidence=module("evidence");comparison=module("comparison");args=module("comparison_args")
    guests=base/proof["guest_directory"]
    evidence.validate(guests,receipt)
    need(receipt["audits"]=={"probe":0,"aube":0},"guest audits")
    hashes={n:sha(guests/n) for n in ("probe","aube")}
    diff=base/proof["differential_directory"]
    cases=doc(ROOT/"tests/guests/u10/cases.json")
    names={"probe-"+n for n in cases["probe"]+["all","environment"]}|{"version","install","frozen","list"}
    for prefix,compare in [("",comparison.compare),("original-argv/",args.compare_original)]:
        native=doc(diff/prefix/"native/observations.json")
        emulated=doc(diff/prefix/"observations.json")
        need(native["native_complete"] and emulated["differential_complete"] and native["binary_hashes"]==emulated["binary_hashes"]==hashes,"fresh oracle/hash")
        need(set(native["rows"])==names and set(emulated["rows"])==names|{"default-version","default-install"},"native14/emulator16")
        need(native["network_namespace"].startswith("net:[") and "Linux" in native["machine"],"native isolation")
        need(native["rows"]["probe-environment"]["stdout"]=="PASS node-absent ENOENT\n","node absent")
        for name,row in emulated["rows"].items():
            successful(row);expected=native["rows"][name.removeprefix("default-")];successful(expected)
            fixture=native["fixture_root"]+("/fixture/app" if not name.startswith("probe-") else "")
            compare(expected,row,fixture,"/")
        for observed in (native,emulated):
            comparison.reproduced({n:observed["rows"][n] for n in ("version","install","frozen","list")})
    coverage=doc(e/"coverage.json")["data"][0]["totals"]["lines"]
    need(coverage["count"]>0 and coverage["covered"]*100>=coverage["count"]*80,"workspace80")
    python=doc(e/"python-coverage.json");hit=total=0
    for name in ["evidence.py","comparison.py","runner.py","build.py","native.py","differential.py","metadata.py","comparison_args.py"]:
        matches=[v for p,v in python["files"].items() if p.replace("\\","/").endswith("tests/guests/u10/"+name)]
        need(len(matches)==1 and matches[0]["excluded_lines"]==[],"Python full population")
        row=matches[0];need(row["executed_lines"] or row["missing_lines"],"empty Python population")
        if name in ("evidence.py","comparison.py","runner.py"):
            hit+=len(row["executed_lines"]);total+=len(set(row["executed_lines"]+row["missing_lines"]))
    need(hit*100>=total*80,"Python core80")
    need((e/"wasm-build-exit.txt").read_text().strip()=="0" and (e/"wasm.sha256").read_text(),"productionwasm missing")
    reuse=doc(UNIT/"verification/step18-sanitizer-reuse.json")
    need(len(reuse["production_dependencies"])==132 and all(sha(ROOT/p)==h for p,h in reuse["production_dependencies"].items()),"ASan closure")
    old_reuse_path=ROOT/reuse["historical_reuse_path"]
    need(sha(old_reuse_path)==reuse["historical_dependencies_sha256"],"old ASan proof changed")
    old_reuse=doc(old_reuse_path)
    need(set(old_reuse["production_dependencies"])==set(reuse["production_dependencies"]) and {p for p,h in old_reuse["production_dependencies"].items() if reuse["production_dependencies"][p]!=h}=={MTIME},"ASan dependency delta not test-only")
    binding=base/reuse["binding"]["raw_directory"]
    need(reuse["binding"]["head"]==head and reuse["binding"]["run"]==run and reuse["binding"]["input_count"]==326 and listing(binding/"source-before.sha256")==inputs and sha(binding/"source-before.sha256")==reuse["binding"]["source_before_sha256"],"fresh ASan build head/input binding")
    need(set(reuse["targets"])=={"load_elf","syscall_args","vfs_paths","mmu_ops","kernel_threads_u5","kernel_futex_u5","kernel_events_u6","kernel_sockets_u6"},"ASan target population")
    settings=(binding/"settings.txt").read_text()
    for line in ["ASAN_OPTIONS=detect_leaks=1","LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp","seed=1","timeout=30","rss_limit_mb=2048","max_total_time=600","san=address","build-only=true"]:
        need(line in settings.splitlines(),"ASan settings")
    need((binding/"suppression.sha256").read_text().split()[0]==inputs["fuzz/lsan.supp"],"LSan suppression changed")
    need("0.13.2" in (binding/"fuzz-version.txt").read_text(),"ASan tool version")
    for target,row in reuse["targets"].items():
        need((binding/(target+"-build-exit.txt")).read_text().strip()=="0","ASan build failed")
        digest=(binding/(target+"-binary.sha256")).read_text().split()[0]
        need(digest==row["binary_sha256"]==old_reuse["targets"][target]["binary_sha256"],"ASan instrumented binary mismatch:"+target)
        need("-Zsanitizer=address" in (binding/(target+"-build.log")).read_text(),"ASan instrumentation flags absent")
    formal=doc(UNIT/"verification/step18-formal-sensors.json")
    need(all(v["exit_code"]==0 and json.loads(v["output"])["pass"] for v in formal.values()),"formal sensors")
    print("Verified current U10326/native14/emulator16/44/Python80/workspace80/productionwasm; finite ASan reuse. U11 browser unverified.")
if __name__=="__main__":
    try: validate()
    except Exception as error:
        print("U10 verification failed:",error,file=sys.stderr);raise SystemExit(1)
