"""Read-only candidate verification command; requires a separately assembled final proof.

Preserves historical evidence and checks fresh current-source evidence. Never
rewrites the recorded U3 command or treats its old-source sanitizer run as new.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
PROOF = RECORD / 'construction/u5-threads-futex/code-generation/verification/final-proof.json'


def need(value, message):
    if not value:
        raise RuntimeError(message)


def digest(path):
    need(path.is_file() and not path.is_symlink(), f'Missing/linked file: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def validate():
    proof = read(PROOF)
    need(proof['unit'] == 'u5-threads-futex' and proof['pass'], 'Final proof incomplete')
    need(re.fullmatch('[0-9a-f]{40}', proof['head']), 'Full current revision required')
    need(proof['verified_commit'] and proof['metadata']['sha'] == proof['head'], 'Signed Verified metadata missing')
    commit = read(RECORD / proof['metadata']['raw_receipt'])
    need(commit['sha'] == proof['head'] and commit['verification']['verified']
         and commit['verification']['reason'] == 'valid', 'Raw signed commit verification failed')
    source = proof['source']
    need(source and len(source) == len({row['path'] for row in source}), 'Unique current source inventory required')
    for row in source:
        need(digest(ROOT / row['path']) == row['sha256'], f"Current source changed: {row['path']}")
    manifests = [read(RECORD / f'construction/{unit}/code-generation/source-manifest.json')
                 for unit in ['u1-skeleton', 'u2-integer-isa', 'u3-sse', 'u4-memory-signals', 'u7-vfs', 'u9-terminal-io', 'u5-threads-futex']]
    needed = set()
    for manifest in manifests:
        for row in manifest['writes']:
            path = ROOT / row['path']
            if path.is_dir():
                needed.update(str(file.relative_to(ROOT)) for file in path.rglob('*') if file.is_file())
            else:
                needed.add(row['path'])
    need(needed <= {row['path'] for row in source}, 'Current inventory does not cover all preceding Unit and U5 claims')
    historical = proof['preserved_evidence']
    need(historical and any('verify-current-u3-native-shared.py' in row['path'] for row in historical), 'Historical checker preservation missing')
    for row in historical:
        need(digest(RECORD / row['path']) == row['sha256'], f"Historical evidence changed: {row['path']}")
    for path, expected in proof['evidence_hashes'].items():
        need(digest(RECORD / path) == expected, f'Evidence changed: {path}')
    gates = proof['gates']
    jobs = {}
    for binding in proof['ci_runs']:
        run = read(RECORD / binding['metadata_path'])
        need(run['id'] == binding['run_id'] and run['head_sha'] == proof['head'], 'CI run raw head binding failed')
        need(run['status'] == 'completed' and run['conclusion'] == 'success', 'CI run incomplete/failed')
        raw_jobs = read(RECORD / binding['jobs_path'])['jobs']
        for job in raw_jobs:
            need(job['run_id'] == run['id'], 'Job belongs to a different raw run')
            jobs[job['id']] = job
    required = {'linux', 'macos', 'windows', 'dependencies', 'native-diff', 'preceding-native-diff', 'coverage', 'production-wasm'}
    need(required <= gates.keys() and all(gates[name]['head'] == proof['head'] and gates[name]['conclusion'] == 'success' for name in required), 'Same-head current gates missing')
    for name in required:
        gate = gates[name]
        job = jobs[gate['job_id']]
        need(job['run_id'] == gate['run_id'] and job['status'] == 'completed' and job['conclusion'] == 'success', f'Gate/raw job mismatch: {name}')
    need(set(proof['preceding_units']) == {'u1-skeleton', 'u2-integer-isa', 'u3-sse', 'u4-memory-signals', 'u7-vfs', 'u9-terminal-io'}, 'Preceding Unit current verification missing')
    need(all(row['pass'] and row['source_head'] == proof['head'] for row in proof['preceding_units'].values()), 'Preceding Unit current source check failed')
    differential = proof['differential']
    need(differential['cases'] == 43 and differential['passed'] == 43 and differential['failed'] == 0 and differential['fresh_native'], 'All43 fresh native differential cases required')
    need(re.search(r'test result: ok\. 43 passed; 0 failed; 0 ignored', (RECORD / differential['log']).read_text()), 'Raw43-case result missing')
    observation_root = RECORD / differential['artifact_path']
    for case in range(43):
        directory = observation_root / str(case)
        manifest = read(directory / 'manifest.json')
        need(len(manifest) == 1 and manifest[0]['case'] == case, 'Differential case inventory mismatch')
        row = manifest[0]
        need(re.fullmatch('[0-9a-f]{64}', row['binary_sha256']), 'Native guest binary hash missing')
        for mode in ['native', 'emulated']:
            observation = read(directory / f'{mode}-{case}.json')
            need(observation == row[mode] and not observation['timeout'], 'Raw observation/manifest mismatch')
            for stream in ['stdout', 'stderr']:
                need((directory / f'{mode}-{case}.{stream}').read_bytes().hex() == observation[stream], 'Raw stream/observation mismatch')
        need(row['native'] == row['emulated'], 'Fresh native/emulated observation differs')
    coverage = read(RECORD / proof['coverage_path'])
    import runpy
    files = runpy.run_path(str(ROOT / 'scripts/u5-coverage.py'))['FILES']
    need(set(coverage['files']) == files and coverage['floor'] == 80, 'Fixed production denominator changed')
    need(coverage['hit'] * 100 >= coverage['lines'] * 80, 'Unchanged80-percent floor failed')
    targets = proof['sanitizers']
    need({'kernel_threads_u5', 'kernel_futex_u5'} <= targets.keys(), 'Both U5 sanitizer targets required')
    for target, row in targets.items():
        need(row['source_head'] == proof['head'] and row['seconds'] >= 600 and row['exit'] == 0 and row['asan'] and row['lsan'], f'Current sanitizer proof missing: {target}')
        job = jobs[row['job_id']]
        need(job['run_id'] == row['run_id'] and target in job['name']
             and job['status'] == 'completed' and job['conclusion'] == 'success', f'Sanitizer raw job mismatch: {target}')
        log = (RECORD / row['log']).read_text()
        count, seconds = map(int, re.findall(r'Done (\d+) runs in (\d+) second', log)[-1])
        need(count == row['runs'] and seconds == row['seconds'], f'Sanitizer raw duration mismatch: {target}')
        need(not re.search(r'ERROR: AddressSanitizer|LeakSanitizer:|runtime error:|panicked at|Failed spawning tracer', log), f'Sanitizer diagnostic failed: {target}')
        receipt = RECORD / row['artifact_path']
        before = (receipt / 'lock-before.sha256').read_text().split()[0]
        after = (receipt / 'lock-after.sha256').read_text().split()[0]
        need(before == after == digest(ROOT / 'fuzz/Cargo.lock'), f'Fuzz lockfile changed: {target}')
        need((receipt / 'exit.txt').read_text().strip() == '0', f'Fuzz artifact exit failed: {target}')
    node = read(RECORD / proof['node_report'])
    safari = read(RECORD / proof['safari_report'])
    for report in [node, safari]:
        need(report['pass'] and report['sharedMemory'] and report['caseCount'] == len(report['results']) and all(row['pass'] for row in report['results']), 'Production Node/Safari result incomplete')
    need(safari['crossOriginIsolated'] and safari['browserVersion'] and all(safari['cleanup'].values()), 'Actual Safari isolation/cleanup proof missing')
    need(proof['wasm_sha256'] == digest(RECORD / proof['wasm_path']), 'Safari/current production wasm binding missing')
    need([row['case'] for row in node['results']] == [row['case'] for row in safari['results']], 'Node/Safari case sets differ')
    print('Verified current U5 finite43 native differential, preserved preceding evidence, same-source gates, fixed coverage80%, sanitizer600s, production Node/actual Safari. No all-input guarantee.')


if __name__ == '__main__':
    try:
        validate()
    except (RuntimeError, OSError, ValueError, KeyError, IndexError) as error:
        print(f'Verification failed: {error}', file=sys.stderr)
        raise SystemExit(1)
