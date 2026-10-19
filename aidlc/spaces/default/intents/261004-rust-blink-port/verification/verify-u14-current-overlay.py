"""Candidate U14 evidence verifier; checker pass does not close open requirements."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
UNIT = RECORD / 'construction/u14-jit-wasm/code-generation'
V = UNIT / 'verification'
OWN = RECORD / 'verification/u14-current-overlay'
HEAD = 'b79d30d5cadcff7b83bc715b38b5fc3af5a47a0e'
OLD = '9b5e6215e180e6602fdbde6b416281aebea9d110'
BINDING_SHA = '6e58bae26130ff34c11c3ec626707b6f1e6cc6fb8dd28c46e0baa3ccd8c2fceb'
PROJECT = {
    '.github/workflows/u1-u14-source-bound.yml',
    '.github/workflows/u14-native-diagnostic.yml',
    '.github/workflows/u14-quality.yml',
    'tests/guests/u10/build.py', 'tests/guests/u10/evidence.py',
    'tests/guests/u10/source-lock.json',
    'tests/guests/u14/runner-tests/test_u14_runner.py',
}
TARGETS = {'cpu_u2', 'decode', 'jit_cache', 'jit_compile', 'kernel_events_u6',
           'kernel_futex_u5', 'kernel_sockets_u6', 'kernel_threads_u5',
           'load_elf', 'mmu_ops', 'mmu_u2', 'syscall_args', 'vfs_paths'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(root, name):
    path = root / name
    need(name and not Path(name).is_absolute() and '\\' not in name
         and all(p not in ('', '.', '..') for p in name.split('/')), 'unsafe path')
    need(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)), 'missing/linked input')
    return path.read_bytes()


def load(root, name):
    return json.loads(read(root, name))


def tree(root):
    paths = sorted(root.rglob('*'))
    need(not any(p.is_symlink() for p in paths), 'linked artifact')
    rows = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in paths if p.is_file()}
    return {'files': len(rows), 'digest': sha(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode())}


def pins(binding):
    for name, digest in binding['source_pins'].items():
        need(sha(read(ROOT, name)) == digest, 'current source changed: ' + name)
    for name, digest in binding['evidence_pins'].items():
        need(sha(read(RECORD, name)) == digest, 'evidence changed: ' + name)
    need(tree(V / 'overlay-ci/b79d30d5') == binding['artifact_tree'], 'current artifact inventory/bytes changed')


def current(binding):
    pins(binding)
    jobs = load(V, 'final-ci-jobs-b79d30d5.json')
    for key, count in [('quality', 34), ('source_bound', 7)]:
        run = jobs[key]
        need(run['head'] == HEAD and run['status'] == 'completed' and run['conclusion'] == 'success'
             and len(run['jobs']) == count and len({j['id'] for j in run['jobs']}) == count
             and all(j['status'] == 'completed' and j['conclusion'] == 'success' for j in run['jobs']),
             'current CI required jobs failed/mismatched')
    pub = load(V, 'head-forwarding-publication-proof-b79d30d5.json')
    need(pub['head'] == HEAD and pub['github_verified'] is True
         and len(pub['files']) == 1 and pub['files'][0]['filename'] == '.github/workflows/u14-native-diagnostic.yml',
         'signed publication differs')
    base = V / 'overlay-ci/b79d30d5'
    for p in (base / 'source-bound').glob('u1-source-bound-inputs-*/inputs.json'):
        inputs = json.loads(p.read_bytes())
        need(inputs['head'] == HEAD and len({r['path'] for r in inputs['rows']}) == len(inputs['rows']), 'CI source inventory')
        ci_rows = {r['path']: r['sha256'] for r in inputs['rows']}
        need(set(binding['source_pins']) <= set(ci_rows), 'required current closure absent from CI source manifest')
        for row in inputs['rows']:
            if row['path'] in binding['source_pins']:
                need(sha(read(ROOT, row['path'])) == row['sha256'], 'current source differs from CI: ' + row['path'])
    snapshot = load(V, 'source-snapshot-b79d30d5.json')
    need(snapshot['head'] == HEAD and len(snapshot['files']) == 62, 'current62 inventory')
    manifest = load(UNIT, 'source-manifest.json')
    need({x['path'] for x in manifest['writes']} == {x['path'] for x in snapshot['files']}, 'manifest inventory')
    for row in snapshot['files']:
        need(binding['source_pins'][row['path']] == row['sha256'], 'current source snapshot differs')
    for name in ['core-archive-integrity-b79d30d5.json', 'fuzz-archive-integrity-b79d30d5.json']:
        proof = load(V, name)
        need(proof['head'] == HEAD and len(proof['archives']) == proof['archives_count'], 'archive identity')
        need(all(a.get('official_digest_matched', a.get('downloaded_zip_sha256_matched')) is True
                 and a['files_matched'] > 0 for a in proof['archives']), 'archive digest check missing')
    sys.path.insert(0, str(ROOT / 'tests/guests/u10'))
    import evidence
    os.environ['GITHUB_SHA'] = HEAD
    for name in ['u10-native-first/guests/u10', 'u13-native-first/guests/u10',
                 'u11-acceptance-inputs/target/guests/u10']:
        directory = base / name
        receipt = json.loads((directory / 'build-receipt.json').read_bytes())
        evidence.validate(directory, receipt)
        need(receipt['ci_head'] == HEAD and receipt['source_unchanged'] is True
             and receipt['exit'] == 0 and all(v == 0 for v in receipt['audits'].values()), 'guest receipt failure')
    acceptance = base / 'u11-acceptance-inputs'
    module = sha((acceptance / 'packages/paludarium-wasm/paludarium.wasm').read_bytes())
    oracle_path = acceptance / 'target/u11/native/observations.json'
    oracle = json.loads(oracle_path.read_bytes())
    guests = {n: sha((acceptance / 'target/guests/u10' / n).read_bytes()) for n in ('probe', 'aube')}
    need(oracle['binary_hashes'] == guests and oracle['native_complete'] is True, 'fresh native oracle differs')
    for row in oracle['rows'].values():
        need(row['exit'] == 0 and not row['timed_out'] and math.isfinite(row['wall_seconds'])
             and 0 <= row['wall_seconds'] <= 30, 'native oracle deadline/failure')
    for environment in ('node', 'chromium', 'firefox', 'safari'):
        path = base / ('u11-' + environment)
        r = json.loads((path / 'observations.json').read_bytes())
        need(r['environment'] == environment and r['complete'] and r['passed'] and r['caseCount'] == 28
             and r['module_sha256'] == module and r['oracle_sha256'] == sha(oracle_path.read_bytes())
             and r['guest_hashes'] == guests, 'acceptance identity/inventory/failure')
        for mode in ('interpreter', 'jit'):
            need(set(r['rows'][mode]) == set(oracle['rows']), 'acceptance case inventory differs')
            for row in r['rows'][mode].values():
                need(row['pass'] and row['exit'] == 0 and not row['timed_out']
                     and math.isfinite(row['seconds']) and 0 <= row['seconds'] <= 30, 'acceptance deadline/failure')
                if mode == 'jit':
                    need(int(row['jit']['executedBlocks']) > 0 and int(row['jit']['executedInstructions']) > 0, 'missing real JIT proof')
        s = json.loads((path / 'suite-supervisor.json').read_bytes())
        need(s['exit'] == 0 and not s['timed_out'] and s['process_group_cleaned'], 'acceptance cleanup/deadline')
    native = load(V, 'native-guest-proof-b79d30d5.json')
    need(native['head'] == HEAD and len(native['builds']) == 3 and len(native['observations']) == 7, 'native proof inventory')
    for row in native['observations']:
        r = load(base, row['path'])
        need(sha(read(base, row['path'])) == row['sha256'] and len(r['rows']) == row['rows'], 'native raw proof differs')
        for observation in r['rows'].values():
            need(observation['exit'] == 0 and not observation['timed_out'] and math.isfinite(observation['wall_seconds'])
                 and 0 <= observation['wall_seconds'] <= 30, 'native row failure/deadline')
    coverage = base / 'source-bound/u1-source-bound-coverage'
    for name in ('u1-workspace-coverage.json', 'u1-package-coverage.json'):
        totals = load(coverage, name)['data'][0]['totals']['lines']
        need(totals['count'] > 0 and totals['covered'] / totals['count'] >= .8, 'workspace/U1 coverage below80')
    python = load(base, 'u14-python-coverage/python-coverage.json')
    need(set(python['files']) == {'scripts/u14-run.py', 'tests/guests/u14/guest_policy.py',
                                 'tests/guests/u14/lock_overlay.py', 'tests/guests/u10/build.py',
                                 'tests/guests/u10/evidence.py'}, 'fixed Python population changed')
    need(python['totals']['num_statements'] == 427 and python['totals']['covered_lines'] >= 342, 'Python below80')
    lcov = read(base, 'u14-jit-coverage/u14-jit.lcov').decode()
    sf = re.findall(r'^SF:(.+)$', lcov, re.M)
    need({Path(p).name for p in sf} == {'block.rs', 'bridge.rs', 'cache.rs', 'emit.rs', 'lib.rs'}, 'fixed Rust population changed')
    total = sum(map(int, re.findall(r'^LF:(\d+)$', lcov, re.M)))
    hit = sum(map(int, re.findall(r'^LH:(\d+)$', lcov, re.M)))
    need(total > 0 and hit / total >= .8, 'JIT coverage below80')
    js = load(base, 'u11-node/js-coverage.json')
    need(js['population'] == ['index.mjs', 'coordinator.mjs', 'execution.mjs', 'worker-support.mjs',
                              'filesystem-snapshot.mjs', 'jit-support.mjs']
         and js['passed'] is True and js['total']['lines'] > 0
         and js['total']['hit'] / js['total']['lines'] >= .8, 'fixed JS coverage failed')
    for row in js['files']:
        need(sha(read(ROOT, row['path'])) == row['source_sha256'] and row['raw_scripts'] > 0,
             'JS coverage source differs')
    for row in js['raw_files']:
        need(sha(read(base / 'u11-node/v8', row['name'])) == row['sha256'], 'JS V8 raw input differs')
    folders = list((base / 'fuzz').glob('u12-fuzz-*'))
    need({p.name.removeprefix('u12-fuzz-') for p in folders} == TARGETS, 'fuzz13 inventory differs')
    for p in folders:
        v = p / 'target/u12-fuzz'
        need(read(v, 'head.txt').decode().strip() == HEAD and read(v, 'exit.txt').strip() == b'0', 'fuzz head/exit')
        for before, after in [('source-before.sha256', 'source-after.sha256'), ('lock-before.sha256', 'lock-after.sha256'),
                              ('locks-before.sha256', 'locks-after.sha256')]:
            need(read(v, before) == read(v, after), 'fuzz source/lock mutation')
        for line in read(v, 'source-before.sha256').decode().splitlines():
            digest, name = line.split(None, 1)
            need(sha(read(ROOT, name)) == digest, 'fuzz source closure mismatch')
        digest, name = read(v, 'binary.sha256').decode().strip().split(None, 1)
        need(sha(read(p, name)) == digest, 'fuzz binary mismatch')
        raw = read(v, 'raw.log').decode()
        done = re.findall(r'Done (\d+) runs in (\d+) second', raw)
        need(done and int(done[-1][1]) >= 600 and 'ERROR: AddressSanitizer' not in raw, 'finite sanitizer observation failed')
        settings = read(v, 'settings.txt').decode()
        need(all(s in settings for s in ('ASAN_OPTIONS=detect_leaks=1', 'LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp',
                                        'seed=1', 'max_total_time=600', 'timeout=30', 'rss_limit_mb=2048')), 'fuzz setting changed')
        if p.name == 'u12-fuzz-mmu_u2':
            need('max_len=-max_len=4608' in settings, 'MMU bound changed')
    first = load(V, 'performance-first-result-13753b14.json')
    need(first['head'] == '13753b14ee3ff73227acb03630cd9d2c21b5ccb7'
         and first['complete'] is True and first['passed'] is False
         and first['result']['p'] == 1 and first['samples'] == 20, 'initial performance gap lost')
    initial_raw = load(V, 'overlay-ci/13753b14/u11-node/performance/observations.json')
    need(initial_raw['complete'] is True and initial_raw['passed'] is False
         and initial_raw['result'] == first['result'] and len(initial_raw['rows']) == 20,
         'initial raw performance was replaced')
    trace = load(UNIT, 'traceability.json')
    need({r['id'] for r in trace['coverage'] if r['status'] == 'GAP'} == {'FR8.3', 'NFR6'}, 'performance GAP lost')
    return {'currentCI': '34+7 success', 'currentNativeReceipts': 3, 'fourEnvironments': '28 each; actual JIT',
            'freshFuzzTargets': 13, 'finiteSecondsPerTarget': 600, 'coverageFloors': 80}


@contextmanager
def historical_projection(legacy, preview, originals):
    regular = legacy.regular
    safe = preview.safe_read
    def old_regular(root, name):
        raw = regular(root, name)
        return originals[name] if root == ROOT and name in PROJECT else raw
    def old_safe(root, name):
        raw = safe(root, name)
        return originals[name] if root == ROOT and name in PROJECT else raw
    legacy.regular = old_regular
    preview.safe_read = old_safe
    try:
        yield
    finally:
        legacy.regular = regular
        preview.safe_read = safe


def bound_inputs():
    binding_raw = read(OWN, 'binding.json')
    need(sha(binding_raw) == BINDING_SHA, 'candidate binding changed')
    binding = json.loads(binding_raw)
    os.environ['PATH'] = os.pathsep.join(binding['tool_directories']) + os.pathsep + os.environ.get('PATH', '')
    need(binding['head'] == HEAD and binding['historical_head'] == OLD, 'head binding')
    return binding


def fresh_current():
    # Legacy verifiers load historical helpers under shared Python module names.
    # A fresh interpreter isolates the complete current helper import closure.
    result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--current-only'],
                            cwd=ROOT, check=True, capture_output=True, text=True, timeout=180)
    return json.loads(result.stdout)


def main():
    binding = bound_inputs()
    result = fresh_current()
    originals = {}
    for name, pair in binding['historical_projection'].items():
        raw = subprocess.check_output(['jj', '--ignore-working-copy', 'file', 'show', '-r', OLD, name], cwd=ROOT, timeout=60)
        need(sha(raw) == pair['old'] and sha(read(ROOT, name)) == pair['current'], 'historical source binding')
        originals[name] = raw
    need(set(originals) == PROJECT, 'historical projection exceeds exact7paths')
    canonical = RECORD / 'verification/verify-current-u1-shared-test-delta.py'
    spec = importlib.util.spec_from_file_location('preserved_u1_shared_delta', canonical)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    sys.path.insert(0, str(RECORD / 'construction/u5-threads-futex/code-generation/verification'))
    import preview_source_binding as preview
    print(json.dumps({'historicalProjection': sorted(PROJECT), 'scope': 'all old predicates retained on matching signed9b5 historical view; old failures stay historical'}), flush=True)
    with historical_projection(legacy, preview, originals):
        legacy.main()
    subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s',
                    'tests/guests/u14/runner-tests', '-p', 'test_*.py'], cwd=ROOT, check=True, timeout=180)
    need(fresh_current() == result, 'current proof changed during verifier')
    pins(binding)
    print(json.dumps({'checker': 'PASS', **result, 'openGaps': ['FR8.3', 'NFR6', 'JE dedicated native execution unverified'],
                      'unitAllRequirementsComplete': False, 'performanceInitial': 'p=1 failed; not replaced',
                      'limits': 'finite sanitizer observation with existing LSan table suppression; no engine approval or lifecycle mutation'}), flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['--current-only']:
        print(json.dumps(current(bound_inputs()), sort_keys=True), flush=True)
    else:
        need(len(sys.argv) == 1, 'unexpected candidate arguments')
        main()
