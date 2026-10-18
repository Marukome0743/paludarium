"""Strict additive, read-only U3 evidence verification; human selection required.

Historical 11195 evidence stays intact. Only three exact, audited test/config
changes may be reconciled when evaluating that historical compiled-source proof.
This is finite validation, not all-input or whole-SSE-family certification.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[4]
E = R / "verification/u3-current-sha-reuse"
HEAD = "91ca0c4e3a090f49c6ac1ffb1e5e2e1d8d0a183d"
PROOF_SHA = "037484ebd8fc8a527719d7ab9fff8fd9a6da2038b63dccb4787df06228b04829"
OLD_CHECKER_SHA = "41c98e3ba346774dbdeba0d17739d39fbd051b81180735bee12bd39d00a8c3b1"
DELTAS = {
    ".github/workflows/ci.yml": ("5e7e7a6503fa11251b30d1b27b05c90b2d1287c0696fde4b83e0d09dccae8b31", "fbeea2cd3f6ffa88eebbc612f4834f1ea045f40db53b2f24aaf3e5b4f1ce1818"),
    "crates/paludarium-cpu/src/u3_tests.rs": ("bb9a27d85c0f9a38c3b4e52d5c55e299fcf34c770ab9729ec504374087ecf6f0", "35505434e4fc21f8f1294071122f68863f2152f35b2f285dcf00400865dcc548"),
    "crates/paludarium-decoder/src/u3_tests.rs": ("7f2e5242701f467e36fff1f660e883f3c7e13f282d3cf4df86074ad1a5df5634", "ba13c0d645fb7dd31846bff33b0d8166bab5f9dfc90b854de47534e7d4df06f5"),
}

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    need(path.is_file() and not path.is_symlink(), f"Missing/linked: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def validate():
    need(sha(E / "step22-completion-proof.json") == PROOF_SHA, "Exact final proof changed")
    proof = load(E / "step22-completion-proof.json")
    need(proof["head"] == HEAD and proof["pass"], "Final completion proof missing")
    r02_path = E / "r02-document-update-proof.json"
    need(sha(r02_path) == "8f03d2c8f4e9a07e3fac3d8ce4a84d64f06e5a932891708cd3b4ab25e17df1f2", "Exact R02 document proof changed")
    r02 = load(r02_path)
    changed = {x["path"]: x for x in r02["changed_documents"]}
    need(set(changed) == {"verification/u3-current-sha-reuse/inventory-case-audit.json", "construction/u3-sse/code-generation/code-summary.md", "construction/u3-sse/code-generation/code-generation-plan.md"}, "R02 document scope changed")
    for path, digest in proof["evidence_hashes"].items():
        if path in changed:
            row = changed[path]
            need(digest == row["old_sha256"] and sha(R / row["old_snapshot"]) == digest and sha(R / path) == row["new_sha256"], f"Exact R02 old/new document binding changed: {path}")
        else:
            need(sha(R / path) == digest, f"Evidence changed: {path}")
    need(sha(E / "r02-original-records/verify-current-u3-native-shared.py") == r02["historical_checker_sha256"], "Historical U3 checker changed")
    need(sha(R / r02["partition_proof_path"]) == r02["partition_proof_sha256"], "R02 partition evidence changed")
    need(len(r02["claims35"]) == 35 and all(sha(ROOT / x["path"]) == x["sha256"] for x in r02["claims35"]), "U3 source claims changed")
    for path, (_, current) in DELTAS.items():
        need(sha(ROOT / path) == current, f"Exact approved delta changed: {path}")
    source = load(E / "step22-current-source.json")
    need(len(source) == len({x["path"] for x in source}) == 211, "211 paths required")
    for row in source:
        need(sha(ROOT / row["path"]) == row["sha256"], f"Current source changed: {row['path']}")
    need(proof["unchanged_paths"] == 208 and proof["delta_paths"] == sorted(DELTAS), "Source delta scope changed")
    for crate in ["cpu", "decoder"]:
        text = (ROOT / f"crates/paludarium-{crate}/src/lib.rs").read_text()
        need(re.search(r"#\[cfg\(test\)\]\s*mod u3_tests;", text), "Test-only module boundary changed")
    old = R / "verification/verify-current-u1-sha-prerequisite.py"
    need(sha(old) == OLD_CHECKER_SHA, "Historical verifier changed")
    historical = R / "verification/u1-sha-prerequisite"
    old_proof = load(historical / "completion-evidence.json")
    need(sha(historical / "completion-evidence.json") == "1e8b3f71096461ad958496066afeb3b25b23124a196f64fd28d090f83b54b668", "Historical proof changed")
    for path, expected in old_proof["evidence_hashes"].items():
        need(sha(R / path) == expected, f"Historical evidence changed: {path}")
    old_source = load(historical / "current-source-proof.json")
    need(len(old_source["rows"]) == 211, "Historical inventory missing")
    for row in old_source["rows"]:
        expected = DELTAS[row["path"]][1] if row["path"] in DELTAS else row["sha256"]
        need(sha(ROOT / row["path"]) == expected, f"Historical/current exact delta mismatch: {row['path']}")
        if row["path"] in DELTAS:
            need(row["sha256"] == DELTAS[row["path"]][0], "Wrong historical delta baseline")
    preserved = load(historical / "preceding-artifact-preservation.json")
    need(preserved["unchanged"] == 23 and preserved["original_prefix_preserved"] == 2, "Preservation scope changed")
    for row in preserved["rows"]:
        need(sha(ROOT / row["path"]) == row["sha256"], "Prior artifact changed")
        if row["status"] == "original_prefix_preserved":
            original = R / "verification/u1-sha-prerequisite-plan-baseline" / Path(row["path"]).name
            need((ROOT / row["path"]).read_bytes().startswith(original.read_bytes()), "Original prefix changed")
    need(sha(R / "construction/u3-sse/code-generation/verification/preceding-unit-artifact-baseline.json") == "084b7ceefa4f2dfaac387fdc6b518a47f0d1eed58fe1d80291f957ac6d66a27e", "Original baseline changed")
    targets = load(historical / "final-sanitizer-proof.json")["targets"]
    need(set(targets) == {"cpu_u2", "mmu_u2", "decode", "load_elf", "syscall_args", "vfs_paths", "mmu_ops"}, "Seven sanitizer targets required")
    for target, item in targets.items():
        artifact = historical / item["artifact"]
        before = {name.strip(): value for value, name in [line.split(None, 1) for line in (artifact / "source-before.sha256").read_text().splitlines()]}
        after = {name.strip(): value for value, name in [line.split(None, 1) for line in (artifact / "source-after.sha256").read_text().splitlines()]}
        need(len(before) == 179 and before == after, "Sanitizer source inventory changed")
        for name, expected in before.items():
            if name in DELTAS:
                need(expected == DELTAS[name][0] and sha(ROOT / name) == DELTAS[name][1], "Exact non-production delta changed")
            else:
                need(sha(ROOT / name) == expected, "Compiled sanitizer source changed")
        for name in ["exit.txt", "source-compare-exit.txt", "minimal-1-exit.txt", "minimal-2-exit.txt"]:
            need((artifact / name).read_text().strip() == "0", "Sanitizer exit failed")
        log = (artifact / f"{target}.log").read_text()
        count, seconds = map(int, re.findall(r"Done (\d+) runs in (\d+) second", log)[-1])
        need(count == item["runs"] and seconds == item["seconds"] and seconds >= 600, "Sanitizer duration missing")
        need(all(x in log for x in ["-seed=1", "-max_total_time=600", "-timeout=30", "-rss_limit_mb=2048"]), "Sanitizer limits changed")
        need(not re.search(r"ERROR: AddressSanitizer|LeakSanitizer:|runtime error:|panicked at|Failed spawning tracer", log), "Sanitizer diagnostic failed")
        need("nightly-2026-10-01" in (artifact / "environment.log").read_text() and "__asan_init" in (artifact / "binary-symbols.txt").read_text(), "Sanitizer runtime missing")
        need(all(x in (artifact / "settings.txt").read_text() for x in ["seed=1", "sanitizer=address", "detect_leaks=1", "suppressions=/work/fuzz/lsan.supp"]), "Sanitizer settings changed")
        need(sha(artifact / "corpus-after.tar") == item["corpus_after_sha256"] and not item["crash_files"], "Corpus/crash evidence changed")
    node = load(historical / "final-production-wasm/target/production-wasm-evidence/node-report.json")
    safari = load(historical / "final-safari/stdout.json")
    invocation = load(historical / "final-safari/invocation.json")
    for report in [node, safari]:
        need(report["pass"] and report["caseCount"] == len(report["results"]) == 21 and all(x["pass"] for x in report["results"]) and report["sharedMemory"], "Production 21 cases missing")
    need(safari["browserVersion"] == "27.0.1" and safari["crossOriginIsolated"] and all(safari["cleanup"].values()), "Safari isolation/cleanup missing")
    need(invocation["exit"] == 0 and not invocation["whole_process_timeout"] and invocation["elapsed_seconds"] < 30 and invocation["outer_watchdog_seconds"] == 30 and invocation["runner_operation_deadline_seconds"] == 28, "Safari deadlines changed")
    need(sha(historical / "final-production-wasm/packages/paludarium-wasm/paludarium.wasm") == "ef8bfcc85dbe47d17866314dff8ad94b4b943ff1ecf0c61a7e02c8138ef74ac5", "Historical production module changed")
    current_wasm = E / "step22-production-wasm"
    need(sha(current_wasm / "packages/paludarium-wasm/paludarium.wasm") == "ef8bfcc85dbe47d17866314dff8ad94b4b943ff1ecf0c61a7e02c8138ef74ac5", "Current production module differs from Safari module")
    current_node = load(current_wasm / "target/production-wasm-evidence/node-report.json")
    need(current_node["pass"] and current_node["caseCount"] == len(current_node["results"]) == 21 and all(x["pass"] for x in current_node["results"]), "Current Node cases missing")
    for native, browser in zip(current_node["results"], safari["results"]):
        need(native["case"] == browser["case"] and all(native.get(key) == browser.get(key) for key in ["stdout", "stderr", "status", "errorKind"]), "Current Node/Safari results differ")
    windows = (historical / "final-windows.log").read_text()
    need(all(x in windows for x in ["U7_WINDOWS_SYMLINK_PERMISSION=true", "iterations=1000 exchanges=53 outside_unchanged=true cleanup=true", "U7_WINDOWS_SHARING_CONFLICTS=421", "elapsed_ms=786 child_exit=exit code: 0"]), "Historical finite Windows fixture missing")
    metadata = load(E / "step22-final-metadata.json")
    need(metadata["commit"]["sha"] == HEAD and metadata["commit"]["commit"]["verification"]["verified"], "Verified commit missing")
    names = {"unit tests (ubuntu-latest)", "unit tests (macos-latest)", "unit tests (windows-latest)", "lint", "dependencies", "differential tests (x86-64 Linux)", "line coverage >= 80%", "production wasm (shared Rust heap, nested Workers)"}
    jobs = metadata["ci"]["jobs"]
    need(metadata["ci"]["headSha"] == HEAD and metadata["ci"]["conclusion"] == "success" and {x["name"] for x in jobs} == names and all(x["conclusion"] == "success" for x in jobs), "Eight final CI gates required")
    need(metadata["diagnostic"]["headSha"] == HEAD and metadata["diagnostic"]["conclusion"] == "success", "Same-head diagnostic required")
    a = E / "step22-shared-artifacts/u3-listed-filter-coverage"
    need(load(a / "source-before.json") == load(a / "source-after.json"), "Diagnostic source changed")
    inventory = load(a / "source-before.json")
    need(len(inventory) == 211, "Diagnostic inventory incomplete")
    for row in inventory:
        actual = sha(ROOT / row["path"])
        if row["path"] == "docs/reports/wasm-threads.md":
            need(actual == "6aa691863688818e68a9a2c8cb323ad2c81cb44b21ca9640344efd70812eed39" and row["sha256"] == "0a06a9c381c0b8e32fd9d8761e92d95f37ee8f7e9a32037ad21cec5dc32b5cdf", "Exact documentary exception changed")
        else:
            need(actual == row["sha256"], "Diagnostic/current source mismatch")
    for name in ["matrix-exit.txt", "measurement-exit.txt", "lcov-report-exit.txt", "json-report-exit.txt"]:
        need((a / name).read_text().strip() == "0", f"Gate failed: {name}")
    need((a / "command.txt").read_text().strip() == "cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --fail-under-lines 80", "Shared command changed")
    need((a / "matrix-command.txt").read_text().strip() == "cargo llvm-cov --locked -p paludarium-cpu -p paludarium-decoder --lib --no-report -- u3_tests::", "Matrix command changed")
    matrix = (a / "matrix.log").read_text()
    need("40 passed; 0 failed; 0 ignored" in matrix and "12 passed; 0 failed; 0 ignored" in matrix, "U3 matrix skipped/missing")
    receipt = load(a / "native/receipt.json")
    need({x["name"] for x in receipt} == {"observe", "fault-observe", "cpuid-observe"}, "Native inputs missing")
    for row in receipt:
        file = a / "native" / (row["name"] + ".native")
        count = {"observe":23576, "fault-observe":1162, "cpuid-observe":12}[row["name"]]
        need(row["exit"] == 0 and row["rows"] == count and len(file.read_bytes().splitlines()) == count and sha(file) == row["output_sha256"] and not (a / "native" / (row["name"] + ".stderr")).read_bytes(), "Fresh native input invalid")
    coverage = load(E / "step22-shared-coverage-proof.json")
    need(coverage["scoped_LF"] == 2758 and coverage["scoped_LH"] == 2246 and coverage["lcov_json_match"] and len(coverage["scoped_files"]) == 9, "Exact nine-file coverage missing")
    json_lines = {"crates/" + x["filename"].split("/crates/", 1)[1]: x["summary"]["lines"] for x in load(a / "coverage.json")["data"][0]["files"]}
    scoped = []
    for record in (a / "coverage.lcov").read_text().split("end_of_record"):
        lines = record.splitlines()
        name = next((x[3:] for x in lines if x.startswith("SF:")), None)
        if not name:
            continue
        path = "crates/" + name.split("/crates/", 1)[1]
        lf = int(next(x[3:] for x in lines if x.startswith("LF:")))
        lh = int(next(x[3:] for x in lines if x.startswith("LH:")))
        need((lf, lh) == (json_lines[path]["count"], json_lines[path]["covered"]), "LCOV/JSON summaries differ")
        if path.startswith(("crates/paludarium-cpu/", "crates/paludarium-decoder/")):
            scoped.append((path, lf, lh))
    expected_paths = {x["path"] for x in coverage["scoped_files"]}
    need(len(scoped) == 9 and {x[0] for x in scoped} == expected_paths and sum(x[1] for x in scoped) == 2758 and sum(x[2] for x in scoped) == 2246, "Raw nine-file coverage changed")
    need(re.search(r"TOTAL\s+.*\s2758\s+512\s+81\.44%", (a / "measurement.log").read_text()), "Console measurement missing")
    need(2246 * 100 >= 2758 * 80, "80-percent floor failed")
    audit = load(E / "inventory-case-audit.json")
    need(audit["mapped_rows"] == len(audit["rows"]) == 136 and audit["assigned_legacy_rows"] == 129 and audit["assigned_crypto_rows"] == 7 and all(x["cases"] and x["implementation_paths"] for x in audit["rows"]), "Assigned instruction mapping incomplete")
    from collections import Counter
    normal = Counter(x.split("|")[0] for x in (a / "native/observe.native").read_text().splitlines())
    faults = Counter(x.split("|")[0] for x in (a / "native/fault-observe.native").read_text().splitlines())
    mapped = {x["case"] for row in audit["rows"] for x in row["cases"]}
    auxiliary = set(normal) - mapped
    expected_auxiliary = {"stmxcsr"} | {"pclmulqdq_" + imm + suffix for imm in ["80", "ee"] for suffix in ["", "_high", "_alias", "_memory"]}
    need(set(normal) == set(faults) and not mapped - set(normal) and auxiliary == expected_auxiliary, "R02 variant sets differ")
    need((len(mapped), len(auxiliary), len(normal), sum(normal[x] for x in mapped), sum(faults[x] for x in mapped), sum(normal[x] for x in auxiliary), sum(faults[x] for x in auxiliary)) == (568, 9, 577, 23384, 1141, 192, 21), "R02 partition counts differ")
    need(audit["mapped_case_variants"] == 568 and audit["auxiliary_case_variants"] == 9 and audit["mapped_normal_rows"] == 23384 and audit["mapped_fault_rows"] == 1141, "Corrected audit count claims differ")
    sensors = load(E / "step22-sensors.json")
    need(len(sensors) == 2 and all(x["exit"] == 0 and json.loads(x["stdout"])["pass"] for x in sensors), "Limited sensors failed")
    print("Verified finite U3: exact three test/config deltas, signed eight CI gates, fresh native matrix, nine-file shared coverage >=80%, preserved historical seven ASan600/Node/Safari21 evidence and prior artifacts. Old filter47 failure and Windows errno5 history remain; no all-input/full-family guarantee.")

if __name__ == "__main__":
    try:
        validate()
    except (RuntimeError, OSError, ValueError, KeyError, IndexError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
