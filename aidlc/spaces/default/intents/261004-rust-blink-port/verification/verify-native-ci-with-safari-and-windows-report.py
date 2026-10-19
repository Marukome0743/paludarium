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



def verify_windows():
    import re
    verification = record / "construction/u7-vfs/code-generation/verification"
    proof_path = verification / "step31-windows-proof.json"
    require(hashlib.sha256(proof_path.read_bytes()).hexdigest() ==
            "877c0cfda5a71b211e8389950c9fc0f9bc162941968a007e5f2212b3e7f591ff",
            "Windows proof differs from the reviewed exact evidence")
    proof = json.loads(proof_path.read_text())
    final_head = "8cba60d9a3d33da53c0040732f90b737b10d0476"
    require(proof["pass"] and proof["head"] == final_head
            and proof["run_id"] == 37765054790, "Unexpected Windows source/run")
    for name, expected in proof["evidence_hashes"].items():
        require(hashlib.sha256((verification / name).read_bytes()).hexdigest() == expected,
                f"U7 evidence changed: {name}")
    commit = json.loads((verification / "step30-lf-commit.json").read_text())
    run = json.loads((verification / "step30-lf-run.json").read_text())
    jobs = json.loads((verification / "step30-lf-jobs.json").read_text())["jobs"]
    require(commit["sha"] == final_head and commit["commit"]["verification"]["verified"],
            "Windows diagnostic signature is not verified")
    require(run["head_sha"] == final_head and run["head_branch"] == branch
            and run["status"] == "completed" and run["conclusion"] == "success",
            "Final Windows CI did not succeed")
    require(len(jobs) == 1 and jobs[0]["id"] == 113270545801
            and jobs[0]["status"] == "completed" and jobs[0]["conclusion"] == "success"
            and all(s["conclusion"] == "success" for s in jobs[0]["steps"]),
            "Windows job/steps incomplete")
    artifact = verification / "step30-lf-ci-artifacts/u7-windows-fixture"
    for name in ("build-exit.txt", "exit.txt", "source-compare-exit.txt"):
        require(int((artifact / name).read_text()) == 0, f"Windows failure: {name}")
    log = (artifact / "test.log").read_text()
    require("U7_WINDOWS_SYMLINK_PERMISSION=true" in log
            and "U7_WINDOWS_RACE iterations=1000 exchanges=55 outside_unchanged=true cleanup=true" in log
            and "U7_WINDOWS_SHARING_CONFLICTS=473" in log
            and "U7_WINDOWS_WATCHDOG elapsed_ms=881 child_exit=exit code: 0" in log
            and "test result: ok. 1 passed; 0 failed; 0 ignored;" in log
            and "panicked at" not in log, "Real Windows fixture observation missing")
    require(proof["iterations"] == 1000 and proof["exchanges"] == 55
            and proof["child_elapsed_ms"] == 881 and proof["child_elapsed_ms"] < 30000,
            "Windows iteration/watchdog conditions changed")
    require("native_fs::u7_tests::u7_native_windows_symlink_rename_race: test" in
            (artifact / "tests.txt").read_text(), "Windows test was not registered")
    require("8ADC0B46D152AEFE3DE75BC3E08E19E24D03F679952BD1B052D4CAA658153E41" in
            (artifact / "binary-sha256.txt").read_text(), "Test executable hash changed")

    def source_hashes(name):
        lines = (artifact / name).read_text().splitlines()
        rows = [line.split(None, 1) for line in lines]
        require(len(rows) == 154 and len({r[1].strip() for r in rows}) == 154,
                "Windows source inventory is incomplete or duplicated")
        return {r[1].strip(): r[0] for r in rows}

    before = source_hashes("source-before.sha256")
    require(before == source_hashes("source-after.sha256"), "Windows source changed during execution")
    baseline = json.loads((verification / "step24-source-baseline.json").read_text())
    require(baseline["source_paths"] == 154, "U7 baseline inventory changed")
    expected = {r["path"]: r["sha256"] for r in baseline["rows"]}
    native_file = "crates/paludarium-host/src/native_fs.rs"
    require(expected[native_file] ==
            "c88d9d93f55e800f77418e6c32333cfeeced3a0a19fbbcf49a70a3c039751342",
            "NativeFs baseline hash changed")
    expected[native_file] = "1888c7aeccc4c10fbb6ba75bf3a57045a5ad7e44f0ea8d3e816fe893b99a9fc1"
    require(before == expected, "Windows source is not the exact baseline plus reviewed test")
    for name, digest in before.items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest,
                f"Windows/current host bytes differ: {name}")
        tested = subprocess.run([jj, "--ignore-working-copy", "file", "show", "-r", final_head, name],
                                cwd=root, check=True, capture_output=True, timeout=30).stdout
        require(hashlib.sha256(tested).hexdigest() == digest, f"Signed Windows head differs: {name}")
    fuzz = json.loads((verification / "step25-fuzz-proof.json").read_text())
    coverage = json.loads((verification / "step25-coverage-proof.json").read_text())
    reuse = json.loads((verification / "step25-syscall-reuse-proof.json").read_text())
    require(fuzz["pass"] and fuzz["runs"] == 3132329 and fuzz["fuzz_seconds"] == 601
            and fuzz["exit_code"] == 0 and fuzz["minimal_asan_exit_codes"] == [0, 0]
            and fuzz["baseline_host_ci_before_after_match"] and fuzz["source_paths"] == 154,
            "Existing exact Linux vfs_paths evidence failed")
    require(coverage["pass"] and coverage["line_coverage"]["percent"] >= 80
            and coverage["line_coverage"]["covered"] == 4317
            and coverage["line_coverage"]["count"] == 4772
            and coverage["diff_u7_63_passed"], "U7 coverage/native differential evidence failed")
    require(reuse["pass"] and reuse["runs"] == 1296522 and reuse["seconds"] == 601
            and reuse["u4_ci_before_after_current_host_baseline_match"],
            "syscall_args evidence reuse failed")
    require(hashlib.sha256((root / reuse["proof_path"]).read_bytes()).hexdigest() ==
            reuse["proof_sha256"], "Reused U4 evidence changed")
    print("Verified U7 Windows temporary fixture: 1000 iterations, 55 exchanges, 473 sharing retries, 881 ms, strict cleanup; 154 exact source paths and existing Linux 600-second/80% observations. Whole-OS/arbitrary-input guarantees are not inferred.")


try:
    verify_windows()
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

        elif relative == "crates/paludarium-host/src/native_fs.rs":
            require(hashlib.sha256(tested).hexdigest() ==
                    "c88d9d93f55e800f77418e6c32333cfeeced3a0a19fbbcf49a70a3c039751342",
                    "NativeFs baseline differs from the reviewed signed commit")
            require(hashlib.sha256(current).hexdigest() ==
                    "1888c7aeccc4c10fbb6ba75bf3a57045a5ad7e44f0ea8d3e816fe893b99a9fc1",
                    "NativeFs differs from the exact final Windows test bytes")
            marker = b"\n    #[cfg(windows)]\n    #[test]\n    fn u7_native_windows_symlink_rename_race()"
            require(current.count(marker) == 1, "Expected Windows-only test block missing")
            start = current.index(marker)
            require(current[:start].rstrip(b"\n") + b"\n}\n" == tested,
                    "NativeFs changed outside the Windows-only test block")
            print("Reviewed exact NativeFs Windows-only test addition; production and Linux code bytes retained")

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

