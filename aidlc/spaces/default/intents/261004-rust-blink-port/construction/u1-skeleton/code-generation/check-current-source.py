"""Read-only U1 source/record reconciliation; this creates no lifecycle receipt."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

record = Path(__file__).resolve().parent
root = record.parents[7]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mismatches(snapshot):
    return [
        row["path"]
        for row in json.loads((root / snapshot).read_text())["files"]
        if not (root / row["path"]).is_file()
        or sha256(root / row["path"]) != row["sha256"]
    ]


manifest = json.loads((record / "source-manifest.json").read_text())
paths = set()
missing = []
for claim in manifest["writes"]:
    path = root / claim["path"]
    if path.is_dir():
        paths.update(p for p in path.rglob("*") if p.is_file())
    elif path.is_file():
        paths.add(path)
    else:
        missing.append(claim["path"])
tracked = set(
    subprocess.check_output(
        ["jj", "--ignore-working-copy", "file", "list"], cwd=root, text=True
    ).splitlines()
)
trace = json.loads((record / "traceability.json").read_text())
source = (root / "crates/paludarium-harness/src/coverage.rs").read_text()
entries = re.findall(r'\("([^"\n]+)", "([^"\n]+)", "((?:\\.|[^"\\])*)"\)', source)
uncovered = [
    instruction
    for instruction, file, fragment in entries
    if bytes(fragment, "utf8").decode("unicode_escape")
    not in (root / "tests/guests" / file).read_text()
]
result = {
    "purpose": "診断用の静的照合。テスト結果・review・lifecycle receiptではない。",
    "claim_count": len(manifest["writes"]),
    "expanded_files": len(paths),
    "missing": missing,
    "untracked": sorted(str(p.relative_to(root)) for p in paths if str(p.relative_to(root)) not in tracked),
    "u7_snapshot_mismatches": mismatches("docs/u7/inventory/source-bytes-final.json"),
    "u1_snapshot_mismatches": mismatches(str((record / "source-bytes-current.json").relative_to(root))),
    "traceability_upstream": len(trace["upstream_ids"]),
    "traceability_coverage": len(trace["coverage"]),
    "missing_OK_targets": [row["id"] for row in trace["coverage"] if row["status"] == "OK" and not (root / row["target"]).exists()],
    "census_entries": len(entries),
    "census_uncovered": uncovered,
    "current_cargo_lock_sha256": sha256(root / "Cargo.lock"),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
# The U7 snapshot records earlier source and stays historical after the
# explicitly approved related repair; only the current U1 snapshot is a gate.
if missing or result["untracked"] or result["u1_snapshot_mismatches"] or result["missing_OK_targets"] or uncovered:
    raise SystemExit(1)
