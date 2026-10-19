"""Read-only U8 checker candidate; formal checkpoint use requires human approval.

Checks finite current-source CI evidence, not historical U6 evidence replacement,
all-input correctness, actual Safari, or a new fuzz run. Never writes receipts.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
UNIT = RECORD / 'construction/u8-process-spawn/code-generation'
SHA = '06d58952a43c82e70c946924b23e11b475042840'
REPO = 'Marukome0743/paludarium'
EXPECTED = (
    '.github/workflows/ci.yml', '.github/workflows/u8-native-diagnostic.yml',
    'README.md', 'tests/guests/u8/build.sh', 'tests/guests/u8/process.c',
    'tests/guests/u8/command.rs', 'tests/guests/u8/cases.json',
    'tests/guests/u8/observe.py', 'crates/paludarium-harness/tests/diff_u8.rs',
    'crates/paludarium-harness/tests/support/u8.rs',
    'crates/paludarium-mmu/src/lib.rs', 'crates/paludarium-mmu/src/u8_tests.rs',
    'crates/paludarium-kernel/src/lib.rs', 'crates/paludarium-kernel/src/processes.rs',
    'crates/paludarium-kernel/src/threads.rs', 'crates/paludarium-kernel/src/files.rs',
    'crates/paludarium-kernel/src/syscalls.rs', 'crates/paludarium-kernel/src/sockets.rs',
    'crates/paludarium-kernel/src/u8_tests.rs', 'crates/paludarium-runtime/src/lib.rs',
    'crates/paludarium-runtime/src/workers.rs', 'crates/paludarium-runtime/src/u8_tests.rs',
    'fuzz/fuzz_targets/kernel_futex_u5.rs', 'fuzz/fuzz_targets/kernel_threads_u5.rs',
    'crates/paludarium-kernel/src/null.rs',
)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def command(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=60)
    need(result.returncode == 0,
         f'Command failed {args!r}: {result.stderr.decode(errors="replace")[:800]}')
    return result.stdout


def api(endpoint):
    return json.loads(command(['gh', 'api', f'repos/{REPO}/{endpoint}']))


def log(job):
    return command(['gh', 'api', '--allow-escape-sequences',
                    f'repos/{REPO}/actions/jobs/{job}/logs']).decode()


def digest(path):
    need(path.is_file() and not path.is_symlink(), f'Missing/linked file: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suite_results(text):
    """Bind result counts to the actual preceding cargo test executable."""
    current = None
    found = {}
    for line in text.splitlines():
        match = re.search(r'Running (?:unittests src/lib.rs|tests/(diff_u[568])\.rs) \(([^)]+)\)', line)
        if match:
            current = match[1] or next(
                (name for name in ('kernel', 'mmu', 'runtime')
                 if f'paludarium-{name}/' in match[2]), None)
        result = re.search(r'test result: ok\. (\d+) passed; 0 failed; 0 ignored; 0 measured; (\d+) filtered out;', line)
        if result and current:
            found.setdefault(current, []).append(tuple(map(int, result.groups())))
    return found


def validate():
    historical = [RECORD / 'verification/verify-current-u6-events-sockets.py',
                  RECORD / 'construction/u6-events-sockets/code-generation/verification/final-proof.json']
    preserved = {path: digest(path) for path in historical}
    manifest = json.loads((UNIT / 'source-manifest.json').read_text())
    need(manifest.get('unit') == 'u8-process-spawn', 'Wrong manifest unit')
    paths = [row['path'] for row in manifest['writes']]
    need(paths == list(EXPECTED) and len(set(paths)) == 25, 'Manifest differs from pinned 25-path inventory')
    for path in paths:
        local = ROOT / path
        digest(local)
        if path != 'README.md':
            published = command(['jj', '--ignore-working-copy', 'file', 'show', '-r', SHA, path])
            need(local.read_bytes() == published, f'Current source differs from signed CI revision: {path}')
    # Markdown documentation is explicitly excluded from executable provenance.
    need((ROOT / 'README.md').suffix == '.md' and 'U8' in (ROOT / 'README.md').read_text(),
         'U8 descriptive README missing')
    commit = api(f'commits/{SHA}')
    verification = commit['commit']['verification']
    need(commit['sha'] == SHA and verification.get('verified') is True
         and verification.get('reason') == 'valid', 'Commit signature is not Verified/valid')
    requirements = {
        37989041260: {
            'dependencies', 'lint', 'line coverage >= 80%',
            'unit tests (windows-latest)', 'unit tests (macos-latest)',
            'unit tests (ubuntu-latest)', 'differential tests (x86-64 Linux)',
            'production wasm (shared Rust heap, nested Workers)',
        },
        37989041283: {'native-first', 'differential'},
    }
    jobs_by_run = {}
    for run_id, required in requirements.items():
        run = api(f'actions/runs/{run_id}')
        need(run['head_sha'] == SHA and run['status'] == 'completed'
             and run['conclusion'] == 'success', f'Run {run_id} is not successful at pinned SHA')
        jobs = api(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
        need(required <= {job['name'] for job in jobs}, f'Required jobs missing in run {run_id}')
        need(all(job['status'] == 'completed' and job['conclusion'] == 'success' for job in jobs),
             f'Incomplete/failed job in run {run_id}')
        jobs_by_run[run_id] = {job['name']: job for job in jobs}
    results = suite_results(log(jobs_by_run[37989041283]['differential']['id']))
    for suite, count in [('diff_u8', 30), ('diff_u5', 43), ('diff_u6', 84)]:
        need((count, 0) in results.get(suite, []), f'Missing complete {suite} {count}-test result')
    for suite, count in [('kernel', 42), ('mmu', 7), ('runtime', 7)]:
        need(any(passed == count for passed, _ in results.get(suite, [])),
             f'Missing U8 {suite} {count}-test result')
    coverage_job = jobs_by_run[37989041260]['line coverage >= 80%']
    need(coverage_job['id'] == 114018218614, 'Unexpected coverage job binding')
    totals = re.findall(r'\bTOTAL\s+([^\n]+)', log(coverage_job['id']))
    need(totals, 'Workspace TOTAL missing')
    columns = totals[0].split()
    need(len(columns) >= 9, 'Malformed llvm-cov TOTAL')
    # llvm-cov columns: regions/missed/%, functions/missed/%, lines/missed/%.
    lines, missed, percent = int(columns[6]), int(columns[7]), float(columns[8].rstrip('%'))
    need(lines == 10899 and missed == 790, 'Workspace TOTAL denominator/hit differs from recorded evidence')
    need((lines - missed) * 100 >= lines * 80 and percent >= 80,
         f'Workspace 80% floor failed: {lines - missed}/{lines} ({percent}%)')
    lcov = UNIT / 'verification/final-u3-lcov/u3-coverage.lcov'
    if lcov.exists():
        text = lcov.read_text()
        files = re.findall(r'^SF:(.+)$', text, re.MULTILINE)
        lf = sum(map(int, re.findall(r'^LF:(\d+)$', text, re.MULTILINE)))
        lh = sum(map(int, re.findall(r'^LH:(\d+)$', text, re.MULTILINE)))
        need(len(files) == 9 and all('paludarium-cpu/' in p or 'paludarium-decoder/' in p for p in files)
             and (lf, lh) == (2758, 2246) and lh * 100 >= lf * 80,
             'Optional U3 LCOV corroboration differs')
    need(all(digest(path) == before for path, before in preserved.items()), 'Historical U6 evidence changed')
    print(f'Verified finite U8 internal56/native29 (30 tests including runner), U5 native43/U6 native84; '
          f'24 executable sources match signed {SHA}; both CIs/all required jobs successful; '
          f'workspace lines {lines - missed}/{lines}={percent:.2f}% >=80%. '
          'README is descriptive, unpublished documentation only. No Safari, new fuzz, or all-input guarantee.')


if __name__ == '__main__':
    try:
        validate()
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(f'U8 verification failed: {error}', file=sys.stderr)
        raise SystemExit(1)
