"""Read-only checkpoint check: current source must match successful native CI."""
import json
import os
from pathlib import Path
import subprocess
import sys

record = Path(__file__).resolve().parents[1]
root = record.parents[4]
repository = "Marukome0743/paludarium"
branch = "codex/native-x86-diagnostic"


def executable(tool):
    installs = Path.home() / ".local/share/mise/installs" / tool
    candidates = set(installs.glob(f"*/{tool}"))
    candidates.update(installs.glob(f"*/bin/{tool}"))
    candidates.update(installs.glob(f"*/*/bin/{tool}"))
    candidates = [p for p in candidates if p.is_file() and os.access(p, os.X_OK)]
    if not candidates:
        raise RuntimeError(f"mise-managed {tool} executable is missing")
    return str(max(candidates, key=lambda p: p.stat().st_mtime_ns))


gh = executable("gh")
jj = executable("jj")


def api(endpoint):
    result = subprocess.run(
        [gh, "api", f"repos/{repository}/{endpoint}"],
        cwd=root, check=True, capture_output=True, text=True, timeout=60,
    )
    return json.loads(result.stdout)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def workflow(file, expected_names):
    runs = api(f"actions/workflows/{file}/runs?branch={branch}&per_page=1")["workflow_runs"]
    require(len(runs) == 1, f"No current {file} run")
    run = runs[0]
    require(run["status"] == "completed" and run["conclusion"] == "success", f"{file} is not successful")
    jobs = api(f"actions/runs/{run['id']}/jobs?per_page=100")["jobs"]
    require({j["name"] for j in jobs} == expected_names, f"{file} job set changed")
    require(all(j["status"] == "completed" and j["conclusion"] == "success" for j in jobs), f"{file} has a non-successful job")
    if file == "ci.yml":
        coverage = next(j for j in jobs if j["name"] == "line coverage >= 80%")
        steps = {s["name"]: s for s in coverage["steps"]}
        for name in ("Run cargo llvm-cov --locked --workspace --fail-under-lines 80",
                     "U1 package line coverage >= 80%"):
            require(name in steps and steps[name]["conclusion"] == "success",
                    f"Coverage gate did not pass: {name}")
    print(f"Verified {file}: {len(jobs)} successful jobs, {run['html_url']}")
    return run["head_sha"]


try:
    sha = workflow("ci.yml", {
        "unit tests (ubuntu-latest)", "unit tests (macos-latest)",
        "unit tests (windows-latest)", "lint", "dependencies",
        "differential tests (x86-64 Linux)", "line coverage >= 80%",
    })
    native_sha = workflow("native-diagnostic.yml", {
        "workspace", "bookworm", "expectations (ubuntu-latest)", "expectations (ubuntu-22.04)",
    })
    require(sha == native_sha, "The two workflows tested different commits")
    commit = api(f"commits/{sha}")
    require(commit["commit"]["verification"]["verified"], "CI commit signature is not verified")
    # Check the whole tracked application/build tree, including later Units.
    tracked = subprocess.run(
        [jj, "--ignore-working-copy", "file", "list"], cwd=root,
        check=True, capture_output=True, text=True, timeout=30,
    ).stdout.splitlines()
    prefixes = ("crates/", "tests/", "fuzz/", "spikes/", "scripts/", "ci/",
                ".github/workflows/", "tools/insn-trace/", "docs/u1/census/", "docs/reports/")
    top_level = {"Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "clippy.toml",
                 "deny.toml", ".gitignore", "README.md"}
    paths = {root / p for p in tracked if p in top_level or p.startswith(prefixes)}
    require(bool(paths), "Empty application source tree")
    for path in sorted(paths):
        relative = str(path.relative_to(root))
        require(not path.is_symlink(), f"Unexpected source symlink: {relative}")
        tested = subprocess.run(
            [jj, "--ignore-working-copy", "file", "show", "-r", sha, relative],
            cwd=root, check=True, capture_output=True, timeout=30,
        ).stdout
        current = path.read_bytes()
        if relative == ".gitignore" and tested != current:
            # This already reviewed local-only ignore entry does not change a build.
            require(tested.count(b".claude/settings.local.json\n") == 1, "Unexpected ignore-file drift")
            require(tested.replace(b".claude/settings.local.json\n", b"") == current, "Unexpected ignore-file drift")
            print("Reviewed non-build difference: .gitignore removes .claude/settings.local.json")
        else:
            require(tested == current, f"Current source differs from tested commit: {relative}")
    print(f"Verified application tree: {len(paths)} tracked files match signed CI commit {sha}")
    print("Native end-to-end/workspace and 3OS/quality checks passed; Docker QEMU, wasm/Safari and fuzz results are not inferred.")
except (RuntimeError, subprocess.SubprocessError, OSError, ValueError, KeyError) as error:
    print(f"Verification failed: {error}", file=sys.stderr)
    raise SystemExit(1)
