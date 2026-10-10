"""U10 diagnostic only: exact input audit, exits, and full Python populations."""
import argparse, hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("u8", ROOT/".github/scripts/u8-current-diagnostic.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
CORE = ["evidence.py", "comparison.py", "runner.py"]
EXTRA = ["build.py", "native.py", "differential.py", "metadata.py", "comparison_args.py"]
def snapshot(output, compare):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)/"base"
        audit.snapshot(p, None)
        value = p.read_text()
    for name in [".github/scripts/u10-current-diagnostic.py", ".github/workflows/u10-current-verification.yml"]:
        value += hashlib.sha256((ROOT/name).read_bytes()).hexdigest()+"  "+name+"\n"
    rows = audit.audit.audit.listing(value)
    assert len(rows) == 326
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(value)
    if compare:
        assert audit.audit.audit.listing(Path(compare).read_text(encoding="utf-8-sig")) == rows
    print("Audited326 strict path/hash inputs including both locks")
def setup(directory):
    # Diagnostic runtime configuration only; all executable module lines counted.
    import site, shutil
    directory.mkdir(parents=True, exist_ok=True)
    config = directory/"coverage.ini"
    config.write_text("[run]\nparallel = true\nsource = "+str(ROOT/"tests/guests/u10")+"\ndata_file = "+str(directory/".coverage")+"\n[report]\nexclude_lines =\n")
    Path(site.getsitepackages()[0], "u10_diagnostic_coverage.pth").write_text("import coverage; coverage.process_startup()\n")
    cargo = shutil.which("cargo")
    assert cargo and "nightly-2026-10-10" in cargo, cargo
    tool = directory/"tools"
    tool.mkdir(exist_ok=True)
    wrapper = tool/"cargo"
    wrapper.write_text('#!/usr/bin/env bash\nset -euo pipefail\nif [[ "${1:-}" == +nightly-2026-10-10 ]]; then shift; fi\nexec "'+cargo+'" "$@"\n')
    wrapper.chmod(0o755)
    print(config)
def coverage_gate(path):
    data = json.loads(path.read_text())
    rows = {}
    for name in CORE+EXTRA:
        matches = [v for p,v in data["files"].items() if p.replace("\\","/").endswith("tests/guests/u10/"+name)]
        assert len(matches) == 1, name
        row = matches[0]
        assert row["excluded_lines"] == [], name
        lines = sorted(set(row["executed_lines"]+row["missing_lines"]))
        assert lines
        rows[name] = {"lines":lines, "covered":row["executed_lines"], "missing":row["missing_lines"]}
    core_total = sum(len(rows[n]["lines"]) for n in CORE)
    core_hit = sum(len(rows[n]["covered"]) for n in CORE)
    result = {"core_files":CORE,"additional_files":EXTRA,"files":rows,"core_lines":core_total,"core_hit":core_hit,"core_percent":100*core_hit/core_total}
    path.with_name("python-populations.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="files"}))
    assert core_hit*100 >= core_total*80
if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode", choices=["snapshot","setup","coverage"])
    p.add_argument("output",type=Path)
    p.add_argument("--compare")
    a=p.parse_args()
    if a.mode=="snapshot": snapshot(a.output,a.compare)
    elif a.mode=="setup": setup(a.output.resolve())
    else: coverage_gate(a.output)
