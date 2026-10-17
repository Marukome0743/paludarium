"""U6 dedicated diagnostic input and finite-case audit."""
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("u5",ROOT/".github/scripts/u5-current-diagnostic.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def snapshot(output,compare):
    base=audit.listing(audit.audit.audit.snapshot())
    generated={f"packages/paludarium-wasm/tests/guests/u6-{n}" for n in range(82) if n!=66}|{"packages/paludarium-wasm/tests/guests/u6-unix"}
    value="".join(h+"  "+name+"\n" for name,h in base.items() if name not in generated)
    for name in [".github/scripts/u3-current-diagnostic.py",".github/workflows/u3-current-verification.yml",".github/scripts/u5-current-diagnostic.py",".github/workflows/u5-current-verification.yml",".github/scripts/u6-current-diagnostic.py",".github/workflows/u6-current-verification.yml"]:
        value+=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()+"  "+name+"\n"
    rows=audit.listing(value)
    assert len(rows)==322
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(value)
    if compare: assert audit.listing(Path(compare).read_text(encoding="utf-8-sig"))==rows
    print("Audited 322 strict input paths")
def lib(path):
    assert re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;",path.read_text())==[("49","0","0")]
def observations(directory,cases,nested=True):
    rows=[]
    for case in cases:
        case_dir=directory/str(case) if nested else directory
        data=json.loads((case_dir/"manifest.json").read_text());assert len(data)==1 and data[0]["case"]==case
        row=data[0];n,e=dict(row["native"]),dict(row["emulated"])
        assert not n["timeout"] and not e["timeout"]
        if case in (52,53,54):
            import struct
            assert e["stdout"]==struct.pack("<qqqq",-97,0,0,0).hex() and e["exit"]==0 and e["stderr"]==""
        else:
            if case==60: assert n["exit"]==-9 and e["exit"]==137;n["exit"]=137
            assert n==e
        for mode in ["native","emulated"]:
            for stream in ["stdout","stderr"]:
                assert (case_dir/f"{mode}-{case}.{stream}").read_bytes().hex()==row[mode][stream]
        rows.append(row)
    return rows
def diff(path):
    assert "84 passed; 0 failed; 0 ignored" in path.read_text()
    rows=observations(ROOT/"target/u6-diff",[*range(82),"timer","unix"])
    for attempt in range(1,11):
        rows+=observations(ROOT/f"target/u6-repeat/{attempt}",["timer"],nested=False)
    (path.parent/"differential-manifest.json").write_text(json.dumps(rows,indent=2)+"\n")
def browser(path):
    x=json.loads(path.read_text());assert x["pass"] and x["sharedMemory"] and x["productionLauncher"]
    assert x["caseCount"]==len(x["results"])==102 and all(r["pass"] for r in x["results"])
    ids=[r["case"] for r in x["results"]];assert len(set(ids))==102
    assert {n for n in ids if n.startswith("u6-")}=={f"u6-{n}" for n in range(82) if n!=66}|{"u6-unix"}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["snapshot","lib","diff","browser"]);p.add_argument("output",type=Path);p.add_argument("--compare");a=p.parse_args()
    if a.mode=="snapshot":snapshot(a.output,a.compare)
    else:globals()[a.mode](a.output)


