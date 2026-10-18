"""Read-only checkpoint check: current source must match successful native CI."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys

record = Path(__file__).resolve().parents[1]
root = record.parents[4]
repository = "Marukome0743/paludarium"
branch = "codex/u2-asan-diagnostic"


def executable(tool):
    installs = Path.home() / ".local/share/mise/installs" / tool
    candidates = set(installs.glob(f"*/{tool}"))
    candidates.update(installs.glob(f"*/bin/{tool}"))
    candidates.update(installs.glob(f"*/*/bin/{tool}"))
    candidates = [p for p in candidates if p.is_file() and os.access(p, os.X_OK)]
    if not candidates:
        raise RuntimeError(f"mise-managed {tool} executable is missing")
    return str(max(candidates, key=lambda p: p.stat().st_mtime_ns))


jj = executable("jj")
metadata_path = record / "construction/u2-integer-isa/code-generation/verification/step47-ci-metadata.json"
metadata = json.loads(metadata_path.read_text())



def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def workflow(file, expected_names):
    run = metadata["runs"][file]
    require(run["head_branch"] == branch, f"Unexpected {file} branch")
    require(run["status"] == "completed" and run["conclusion"] == "success", f"{file} is not successful")
    jobs = metadata["jobs"][str(run["id"])]["jobs"]
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
        "production wasm (shared Rust heap, nested Workers)",
    })
    sanitizer_sha = workflow("u2-production-sanitizers.yml", {
        "ASan cpu_u2 (10 min)", "ASan mmu_u2 (10 min)",
        "ASan decode (10 min)", "ASan load_elf (10 min)",
    })
    native_sha = workflow("u2-asan-diagnostic.yml", {"clone", "guests"})
    require(sha == native_sha == sanitizer_sha, "The workflows tested different commits")
    commit = metadata["commit"]
    require(commit["sha"] == sha, "Signed commit differs from CI source")
    require(commit["commit"]["verification"]["verified"], "CI commit signature is not verified")
    # Check the whole tracked application/build tree, including later Units.
    tracked = subprocess.run(
        [jj, "--ignore-working-copy", "file", "list"], cwd=root,
        check=True, capture_output=True, text=True, timeout=30,
    ).stdout.splitlines()
    prefixes = ("crates/", "tests/", "fuzz/", "spikes/", "scripts/", "packages/", "ci/",
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
        elif relative == "docs/reports/wasm-threads.md" and tested != current:
            require(hashlib.sha256(current).hexdigest() == "6aa691863688818e68a9a2c8cb323ad2c81cb44b21ca9640344efd70812eed39",
                    "Safari report differs from the reviewed documentary update")
            print("Reviewed documentary difference: docs/reports/wasm-threads.md retains the exact previously checked report bytes")

        else:
            require(tested == current, f"Current source differs from tested commit: {relative}")
    print(f"Verified application tree: {len(paths)} tracked files checked against signed CI commit {sha}")
    verification = record / "construction/u2-integer-isa/code-generation/verification"
    proof = json.loads((verification / "step47-proof.json").read_text())
    require(proof["pass"] and proof["head_sha"] == sha, "Current source quality proof is incomplete")
    for name, expected in proof["evidence_hashes"].items():
        require(hashlib.sha256((verification / name).read_bytes()).hexdigest() == expected,
                f"Evidence changed: {name}")
    safari = json.loads((verification / "step45-production-wasm/ci-safari-report.json").read_text())
    require(safari["pass"] and safari["caseCount"] == 14 and safari["crossOriginIsolated"]
            and safari["cleanup"]["driver_reaped"] and safari["cleanup"]["server_closed"],
            "Actual CI production module Safari observation failed")
    print("Verified production wasm Node/real Safari 14 cases, shared Rust heap/nested Workers, fixed 4-target sanitizer evidence and native 3OS/80% gates. Guest clone/futex, arbitrary guests and JIT remain outside this observation.")

except (RuntimeError, subprocess.SubprocessError, OSError, ValueError, KeyError) as error:
    print(f"Verification failed: {error}", file=sys.stderr)
    raise SystemExit(1)
