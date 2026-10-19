"""Read-only verification of the finite, current U1 shared-SHA repair evidence.

The historical checkers remain unchanged. This does not certify all SSE,
arbitrary guests, all browser engines, or the unfinished U3 lifecycle.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
EVIDENCE = RECORD / "verification/u1-sha-prerequisite"
HEAD = "11195ad000415af6b320b8e0e4b64a46265fdb61"
PROOF_SHA256 = "1e8b3f71096461ad958496066afeb3b25b23124a196f64fd28d090f83b54b668"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    require(path.is_file() and not path.is_symlink(), f"Missing/linked file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def inventory(path):
    rows = [line.split(None, 1) for line in path.read_text().splitlines()]
    result = {name.strip(): value for value, name in rows}
    require(len(rows) == len(result) == 179, f"Incomplete source inventory: {path}")
    return result


def validate():
    proof_path = EVIDENCE / "completion-evidence.json"
    require(digest(proof_path) == PROOF_SHA256, "Exact reviewed evidence changed")
    proof = read("completion-evidence.json")
    require(proof["head"] == HEAD, "Wrong final head")
    for path, expected in proof["evidence_hashes"].items():
        require(digest(RECORD / path) == expected, f"Evidence changed: {path}")
    source = read("current-source-proof.json")
    require(source["head"] == HEAD and source["paths"] == len(source["rows"]) == 211,
            "Whole application/build inventory missing")
    require(len({row["path"] for row in source["rows"]}) == 211, "Duplicate source rows")
    differences = []
    for row in source["rows"]:
        require(digest(ROOT / row["path"]) == row["sha256"], f"Current source changed: {row['path']}")
        if row["sha256"] != row["ci_sha256"]:
            differences.append(row["path"])
            require(row["path"] == "docs/reports/wasm-threads.md" and
                    row["sha256"] == "6aa691863688818e68a9a2c8cb323ad2c81cb44b21ca9640344efd70812eed39" and
                    row["ci_sha256"] == "0a06a9c381c0b8e32fd9d8761e92d95f37ee8f7e9a32037ad21cec5dc32b5cdf",
                    "Unexpected documentary exception")
    require(differences == ["docs/reports/wasm-threads.md"], "Documentary difference changed")

    preservation = read("preceding-artifact-preservation.json")
    require(preservation["unchanged"] == 23 and preservation["original_prefix_preserved"] == 2,
            "Prior Unit preservation scope changed")
    for row in preservation["rows"]:
        require(digest(ROOT / row["path"]) == row["sha256"], "Preserved artifact changed")
        if row["status"] == "original_prefix_preserved":
            original = RECORD / "verification/u1-sha-prerequisite-plan-baseline" / Path(row["path"]).name
            require((ROOT / row["path"]).read_bytes().startswith(original.read_bytes()),
                    "Original plan/instructions prefix changed")
    baseline = RECORD / "construction/u3-sse/code-generation/verification/preceding-unit-artifact-baseline.json"
    require(digest(baseline) == "084b7ceefa4f2dfaac387fdc6b518a47f0d1eed58fe1d80291f957ac6d66a27e",
            "Original 25-artifact baseline changed")

    metadata = read("final-metadata.json")
    require(metadata["commit"]["sha"] == HEAD and metadata["commit"]["commit"]["verification"]["verified"],
            "Signed final commit missing")
    ci_names = {"unit tests (ubuntu-latest)", "unit tests (macos-latest)",
                "unit tests (windows-latest)", "lint", "dependencies",
                "differential tests (x86-64 Linux)", "line coverage >= 80%",
                "production wasm (shared Rust heap, nested Workers)"}
    runs = {37858171955: ci_names,
            37858171926: {f"ASan {target} (10 min)" for target in ["cpu_u2", "mmu_u2", "decode", "load_elf"]},
            37858171928: {f"ASan {target} (10 min)" for target in ["syscall_args", "vfs_paths", "mmu_ops"]}}
    for run_id, names in runs.items():
        run = metadata[str(run_id)]["run"]
        jobs = metadata[str(run_id)]["jobs"]
        require(run["head_sha"] == HEAD and run["status"] == "completed" and run["conclusion"] == "success",
                f"Incomplete final run: {run_id}")
        require({job["name"] for job in jobs} == names and all(
            job["status"] == "completed" and job["conclusion"] == "success" for job in jobs),
            f"Incomplete final jobs: {run_id}")

    coverage = read("coverage-proof.json")
    require(coverage["floor"] == 80 and coverage["head"] == HEAD, "Coverage policy changed")
    for key in ["workspace", "u1"]:
        item = coverage[key]
        require((item["lines"] - item["uncovered"]) * 100 >= item["lines"] * 80, f"Coverage below 80: {key}")
    records = []
    for record in (EVIDENCE / "final-u3-lcov/u3-coverage.lcov").read_text().split("end_of_record"):
        lines = record.splitlines()
        name = next((line[3:] for line in lines if line.startswith("SF:")), None)
        if name:
            path = "crates/" + name.split("/crates/", 1)[1]
            require(path.startswith(("crates/paludarium-cpu/src/", "crates/paludarium-decoder/src/")),
                    "U3 LCOV includes a different production denominator")
            data = [line.split(",") for line in lines if line.startswith("DA:")]
            require(len({line[0] for line in data}) == len(data), "Duplicate line entries")
            records.append((path, len(data), sum(int(line[1]) > 0 for line in data)))
    require(len(records) == 9 and sum(row[1] for row in records) == 2737 and
            sum(row[2] for row in records) == 2225, "Exact U3 LCOV denominator changed")
    require(sum(row[2] for row in records) * 100 >= sum(row[1] for row in records) * 80, "U3 below 80%")

    targets = read("final-sanitizer-proof.json")["targets"]
    require(set(targets) == {"cpu_u2", "mmu_u2", "decode", "load_elf", "syscall_args", "vfs_paths", "mmu_ops"},
            "Seven current sanitizer targets missing")
    for target, item in targets.items():
        artifact = EVIDENCE / item["artifact"]
        before = inventory(artifact / "source-before.sha256")
        require(before == inventory(artifact / "source-after.sha256"), "Sanitizer source changed")
        for name, expected in before.items():
            require(digest(ROOT / name) == expected, f"Sanitizer/current source mismatch: {name}")
        for name in ["exit.txt", "source-compare-exit.txt", "minimal-1-exit.txt", "minimal-2-exit.txt"]:
            require(int((artifact / name).read_text()) == 0, f"Sanitizer failure: {target}/{name}")
        log = (artifact / f"{target}.log").read_text()
        require(all(value in log for value in ["-seed=1", "-max_total_time=600", "-timeout=30", "-rss_limit_mb=2048"]),
                "Sanitizer execution limits changed")
        if target in {"cpu_u2", "mmu_u2"}:
            require(f"-max_len={4096 if target == 'cpu_u2' else 4608}" in log,
                    "Target input limit changed")
        count, seconds = map(int, re.findall(r"Done (\d+) runs in (\d+) second", log)[-1])
        require(count == item["runs"] and seconds == item["seconds"] and seconds >= 600,
                "Actual sanitizer duration missing")
        require(not re.search(r"ERROR: AddressSanitizer|LeakSanitizer:|runtime error:|panicked at|Failed spawning tracer", log),
                "Sanitizer diagnostic failure")
        require("nightly-2026-10-01" in (artifact / "environment.log").read_text(), "Toolchain changed")
        settings = (artifact / "settings.txt").read_text()
        require(all(value in settings for value in ["seed=1", "sanitizer=address", "detect_leaks=1",
                                                    "suppressions=/work/fuzz/lsan.supp"]), "Sanitizer settings changed")
        require("__asan_init" in (artifact / "binary-symbols.txt").read_text(), "ASan symbols missing")
        require(digest(artifact / "corpus-after.tar") == item["corpus_after_sha256"] and not item["crash_files"],
                "Corpus/crash evidence changed")

    windows = (EVIDENCE / "final-windows.log").read_text()
    require(all(value in windows for value in ["U7_WINDOWS_SYMLINK_PERMISSION=true",
            "U7_WINDOWS_RACE iterations=1000 exchanges=53 outside_unchanged=true cleanup=true",
            "U7_WINDOWS_SHARING_CONFLICTS=421", "U7_WINDOWS_WATCHDOG elapsed_ms=786 child_exit=exit code: 0"]),
            "Current Windows fixture observation missing")
    node = read("final-production-wasm/target/production-wasm-evidence/node-report.json")
    safari = read("final-safari/stdout.json")
    invocation = read("final-safari/invocation.json")
    for report in [node, safari]:
        require(report["pass"] and report["caseCount"] == 21 and len(report["results"]) == 21 and
                all(row["pass"] for row in report["results"]) and report["sharedMemory"], "Production cases missing")
    require([row["case"] for row in node["results"]] == [row["case"] for row in safari["results"]],
            "Node/Safari case identities differ")
    for native_row, browser_row in zip(node["results"], safari["results"]):
        for field in ["stdout", "stderr", "status", "errorKind"]:
            require(native_row.get(field) == browser_row.get(field), "Node/Safari observable result differs")
    require(safari["browserVersion"] == "27.0.1" and safari["crossOriginIsolated"] and all(safari["cleanup"].values()),
            "Real Safari isolation/cleanup missing")
    require(invocation["exit"] == 0 and not invocation["whole_process_timeout"] and
            invocation["elapsed_seconds"] < 30 and invocation["outer_watchdog_seconds"] == 30 and
            invocation["runner_operation_deadline_seconds"] == 28, "Safari deadline changed")
    require(digest(EVIDENCE / "final-production-wasm/packages/paludarium-wasm/paludarium.wasm") ==
            "ef8bfcc85dbe47d17866314dff8ad94b4b943ff1ecf0c61a7e02c8138ef74ac5", "Final module changed")
    sensors = read("sensors.json")
    require(len(sensors) == 2 and all(row["exit"] == 0 and json.loads(row["stdout"])["pass"] for row in sensors),
            "U1 limited sensors failed")
    print("Verified finite current U1 SHA repair: signed 211-path source, preserved 23 artifacts/original 2 prefixes, "
          "3OS/native/80% gates, seven current 600-second ASan+LSan targets, Node/real Safari 21 cases. "
          "Prior Windows errno5 failure remains recorded; all-input/all-SSE/U3 lifecycle completion is not inferred.")


if __name__ == "__main__":
    try:
        validate()
    except (RuntimeError, OSError, ValueError, KeyError, IndexError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
