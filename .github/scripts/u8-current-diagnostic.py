"""U8 current finite diagnostic; no product or fixture changes."""
import argparse, hashlib, importlib.util, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("u6",ROOT/".github/scripts/u6-current-diagnostic.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def snapshot(output,compare):
    # U6 snapshot already excludes only known generated guest binaries.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"base"
        audit.snapshot(p,None)
        value=p.read_text()
    for name in [".github/scripts/u8-current-diagnostic.py",".github/workflows/u8-current-verification.yml"]:
        value+=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()+"  "+name+"\n"
    rows=audit.audit.listing(value)
    assert len(rows)==324
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(value)
    if compare:assert audit.audit.listing(Path(compare).read_text(encoding="utf-8-sig"))==rows
    print("Audited 324 strict path/hash inputs, including both locks")
def lib(path,unit):
    expected={"u8":[("42","0","0"),("7","0","0"),("7","0","0")],"u5":[("27","0","0"),("6","0","0")],"u6":[("49","0","0")]}
    rows=re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;",path.read_text())
    assert sorted(rows)==sorted(expected[unit]),rows
def diff(path):
    text=path.read_text()
    assert "30 passed; 0 failed; 0 ignored" in text
    expected=re.findall(r'u8_(\w+) => \("([^"]+)"', (ROOT/"crates/paludarium-harness/tests/diff_u8.rs").read_text())
    assert len(expected)==29
    for name,mode in expected:
        assert f"test linux::u8_{name} ... ok" in text
        assert f"{mode}: native " in text
    assert "test u8_runner_ready ... ok" in text
    print("Fresh 29 native/emulated cases and runner passed; comparison masks unchanged")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["snapshot","lib","diff"]);p.add_argument("output",type=Path);p.add_argument("--compare");p.add_argument("--unit");a=p.parse_args()
    if a.mode=="snapshot":snapshot(a.output,a.compare)
    elif a.mode=="lib":lib(a.output,a.unit)
    else:diff(a.output)
