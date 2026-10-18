"""Read-only, exact-evidence completion check after the U9 terminal API change.

This checks finite observations, not arbitrary guests, all UB, clone/futex or JIT.
The earlier Safari/Windows checker and its reviewed evidence remain unchanged.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

record = Path(__file__).resolve().parents[1]
root = record.parents[4]
unit = record / 'construction/u9-terminal-io/code-generation'
evidence = unit / 'verification'
HEAD = '7069538f1bdadb62e275f0c8c4f580ac3b70e9b5'
VFS_HEAD = '0dc8ca8b240587e4897e025da6c730b1d1500e2b'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    require(path.is_file() and not path.is_symlink(), f'Missing/linked file: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((evidence / name).read_text())


def inventory(path):
    rows = [line.split(None, 1) for line in path.read_text().splitlines()]
    result = {name.strip(): value for value, name in rows}
    require(len(result) == len(rows) == 155, f'Incomplete inventory: {path}')
    return result


try:
    proof_file = evidence / 'step12-completion-evidence.json'
    require(digest(proof_file) == '872b6f41ec31caf53fc54b00d34fa44a84513666846073f8729a37f2d4ebdd2f',
            'Exact reviewed evidence bundle changed')
    proof = json.loads(proof_file.read_text())
    for name, expected in proof['evidence_hashes'].items():
        require(digest(record / name) == expected, f'Evidence changed: {name}')
    for name, expected in proof['produces_hashes'].items():
        require(digest(unit / name) == expected, f'U9 record changed: {name}')
    for name, expected in proof['manifest_claims'].items():
        require(digest(root / name) == expected, f'Manifest source changed: {name}')
    require(len(proof['manifest_claims']) == 19, 'U9 claim inventory changed')

    source = read('step11-source-proof.json')
    require(source['pass'] and source['head'] == HEAD and source['paths'] == 187,
            'Whole application/build inventory missing')
    require(len({row['path'] for row in source['rows']}) == 187, 'Source rows duplicated')
    for row in source['rows']:
        require(digest(root / row['path']) == row['sha256'], f'Current source changed: {row["path"]}')
        if row['sha256'] != row['ci_sha256']:
            require(row['path'] in ('.gitignore', 'docs/reports/wasm-threads.md') and row['exception'],
                    f'Unexpected CI byte difference: {row["path"]}')
    require(digest(root / 'crates/paludarium-host/src/native_fs.rs') ==
            '1888c7aeccc4c10fbb6ba75bf3a57045a5ad7e44f0ea8d3e816fe893b99a9fc1',
            'Reviewed Windows-only fixture bytes changed')

    metadata = read('step11-metadata.json')
    for key, head in [('commit', HEAD), ('vfs_commit', VFS_HEAD)]:
        require(metadata[key]['sha'] == head and metadata[key]['commit']['verification']['verified'],
                f'Signature missing: {key}')
    expected_jobs = {
        '37773320167': {'unit tests (ubuntu-latest)', 'unit tests (macos-latest)',
                       'unit tests (windows-latest)', 'lint', 'dependencies',
                       'differential tests (x86-64 Linux)', 'line coverage >= 80%',
                       'production wasm (shared Rust heap, nested Workers)'},
        '37773320171': {'windows-fixture'},
        '37773320203': {'clone', 'guests'},
        '37773320297': {'ASan syscall_args (10 min)'},
        '37773320346': {f'ASan {t} (10 min)' for t in ['cpu_u2', 'mmu_u2', 'decode', 'load_elf']},
        '37773925007': {'ASan vfs_paths (10 min)'},
    }
    for run_id, names in expected_jobs.items():
        run = metadata[run_id]['run']
        jobs = metadata[run_id]['jobs']['jobs']
        require(run['head_sha'] == (VFS_HEAD if run_id == '37773925007' else HEAD)
                and run['head_branch'] == 'codex/u2-asan-diagnostic'
                and run['status'] == 'completed' and run['conclusion'] == 'success',
                f'CI run incomplete: {run_id}')
        require({job['name'] for job in jobs} == names and all(
            job['status'] == 'completed' and job['conclusion'] == 'success' for job in jobs),
            f'CI jobs incomplete: {run_id}')
    coverage = next(j for j in metadata['37773320167']['jobs']['jobs'] if j['name'] == 'line coverage >= 80%')
    gates = {s['name']: s['conclusion'] for s in coverage['steps']}
    require(all(gates.get(name) == 'success' for name in [
        'Run cargo llvm-cov --locked --workspace --fail-under-lines 80',
        'U1 package line coverage >= 80%', 'U9 target crates line coverage >= 80%']), '80% gate missing')
    require((evidence / 'step11-vfs-only-diff.log').read_text().strip() ==
            'A .github/workflows/u9-vfs-sanitizer.yml', 'VFS head differs outside its diagnostic workflow')

    targets = read('step11-sanitizer-proof.json')['targets']
    require(set(targets) == {'cpu_u2', 'mmu_u2', 'decode', 'load_elf', 'syscall_args', 'vfs_paths'},
            'Sanitizer target set changed')
    for target, item in targets.items():
        path = evidence / item['artifact']
        before = inventory(path / 'source-before.sha256')
        require(before == inventory(path / 'source-after.sha256'), 'Fuzz source changed')
        for name, expected in before.items():
            require(digest(root / name) == expected, f'Fuzz/current source mismatch: {name}')
        for name in ['exit.txt', 'source-compare-exit.txt', 'minimal-1-exit.txt', 'minimal-2-exit.txt']:
            require(int((path / name).read_text()) == 0, f'Sanitizer failure: {target}/{name}')
        log = (path / (target + '.log')).read_text()
        require(all(s in log for s in ['-seed=1', '-max_total_time=600', '-timeout=30', '-rss_limit_mb=2048']),
                f'Fuzz command limits missing: {target}')
        require('nightly-2026-10-01' in (path / 'environment.log').read_text(),
                f'Fixed toolchain evidence missing: {target}')
        count, seconds = map(int, re.findall(r'Done (\d+) runs in (\d+) second', log)[-1])
        require(count == item['runs'] and seconds == item['seconds'] and seconds >= 600,
                f'Fuzz duration/runs missing: {target}')
        require(not re.search(r'ERROR: AddressSanitizer|LeakSanitizer:|runtime error:|panicked at|Failed spawning tracer', log),
                f'Sanitizer diagnostic: {target}')
        settings = (path / 'settings.txt').read_text()
        require(all(s in settings for s in ['seed=1', 'sanitizer=address', 'detect_leaks=1',
                                            'suppressions=/work/fuzz/lsan.supp']), 'Sanitizer settings changed')
        require('__asan_init' in (path / 'binary-symbols.txt').read_text(), 'ASan symbols missing')
        require(digest(path / 'corpus-after.tar') == item['corpus_after_sha256'] and not item['crash_files'],
                'Corpus/crash evidence changed')
    reuse = read('step11-mmu-ops-reuse.json')
    require(reuse['pass'] and reuse['runs'] == 3682821 and reuse['seconds'] == 601,
            'mmu_ops finite prior observation missing')
    require(digest(root / reuse['proof_path']) == reuse['proof_sha256'], 'mmu_ops prior proof changed')
    for name, expected in reuse['closure'].items():
        require(digest(root / name) == expected, f'mmu_ops dependency changed: {name}')

    windows = evidence / 'step11-windows'
    before = inventory(windows / 'source-before.sha256')
    require(before == inventory(windows / 'source-after.sha256'), 'Windows source changed')
    for name, expected in before.items():
        require(digest(root / name) == expected, f'Windows/current source mismatch: {name}')
    for name in ['build-exit.txt', 'exit.txt', 'source-compare-exit.txt']:
        require(int((windows / name).read_text()) == 0, f'Windows failure: {name}')
    raw = (evidence / 'step11-run-37773320171.log').read_text()
    require(all(s in raw for s in ['U7_WINDOWS_SYMLINK_PERMISSION=true',
        'U7_WINDOWS_RACE iterations=1000 exchanges=34 outside_unchanged=true cleanup=true',
        'U7_WINDOWS_SHARING_CONFLICTS=311', 'U7_WINDOWS_WATCHDOG elapsed_ms=597 child_exit=exit code: 0']),
        'Actual Windows fixture observation missing')
    require('u7_native_windows_symlink_rename_race: test' in (windows / 'tests.txt').read_text()
            and re.search(r'[A-F0-9]{64}', (windows / 'binary-sha256.txt').read_text()), 'Windows binary evidence missing')

    for name in ['step11-safari-third.json', 'step11-production-wasm/target/production-wasm-evidence/node-report.json']:
        report = read(name)
        require(report['pass'] and report['caseCount'] == 14 and report['sharedMemory'], 'Production wasm observation missing')
    safari = read('step11-safari-third.json')
    require(safari['crossOriginIsolated'] and safari['elapsed_ms'] < 30000 and all(safari['cleanup'].values()),
            'Real Safari/watchdog/cleanup failed')
    sensors = read('step12-sensors.json')
    require(len(sensors) == 2 and all(s['exit'] == 0 and json.loads(s['stdout'])['pass'] for s in sensors),
            'U9 narrow sensors failed')
    print('Verified U9 exact 187-path signed CI source, 3OS/80% gates, 6 current 600-second ASan+LSan observations, scoped mmu_ops reuse, current Windows fixture and Node/real Safari 14 cases. Historical evidence retained; arbitrary guests/clone/futex/JIT are not inferred.')
except (RuntimeError, OSError, ValueError, KeyError, IndexError) as error:
    print(f'Verification failed: {error}', file=sys.stderr)
    raise SystemExit(1)
