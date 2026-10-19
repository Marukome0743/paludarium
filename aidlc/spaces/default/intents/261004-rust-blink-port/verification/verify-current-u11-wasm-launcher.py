"""Read-only U11 checkpoint candidate; formal execution requires human approval."""
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
UNIT = RECORD / 'construction/u11-wasm-launcher/code-generation'
REPO = 'Marukome0743/paludarium'
BASE = '5b319a7072e698d8e7c2f94e4821bf584ec381fb'
FUZZ = ('vfs_paths', 'load_elf', 'syscall_args', 'kernel_threads_u5',
        'kernel_futex_u5', 'kernel_events_u6', 'kernel_sockets_u6')
BASE_JOBS = {'dependencies', 'lint', 'line coverage >= 80%',
             'unit tests (windows-latest)', 'unit tests (macos-latest)',
             'unit tests (ubuntu-latest)', 'differential tests (x86-64 Linux)',
             'production wasm (shared Rust heap, nested Workers)'}
NODE_CANDIDATES = [path for path in (Path.home() / '.local/share/mise/installs/node').glob('*/bin/node')
                   if re.fullmatch(r'\d+\.\d+\.\d+', path.parents[1].name)]
NODE = str(max(NODE_CANDIDATES, key=lambda path: tuple(
    int(part) for part in path.parents[1].name.split('.')))) if NODE_CANDIDATES else None


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(args, *, data=None):
    result = subprocess.run(args, cwd=ROOT, input=data, capture_output=True, timeout=60)
    need(result.returncode == 0, f'Command failed: {args!r}: {result.stderr[:800]!r}')
    return result.stdout


def api(endpoint):
    return json.loads(command(['gh', 'api', f'repos/{REPO}/{endpoint}']))


def member(archive, suffix):
    names = [name for name in archive.namelist()
             if name == suffix or name.endswith('/' + suffix)]
    need(len(names) == 1, f'Missing/ambiguous artifact member: {suffix}')
    return archive.read(names[0])


def document(archive, suffix):
    return json.loads(member(archive, suffix))


def validate():
    proof = json.loads((UNIT / 'verification/final-proof.json').read_text())
    revision, run_id = proof['source_sha'], proof['ci_run']
    need(proof['status'] == 'complete' and re.fullmatch(r'[0-9a-f]{40}', revision)
         and isinstance(run_id, int), 'Final proof incomplete')
    paths = command(['jj', '--ignore-working-copy', 'diff', '--from', BASE,
                     '--to', revision, '--name-only']).decode().splitlines()
    paths = [path for path in paths if not path.startswith('aidlc/')]
    need(paths and all(path.startswith(('crates/', 'packages/paludarium-wasm/',
         'tests/guests/', 'scripts/', '.github/workflows/', 'fuzz/'))
         or path in ('Cargo.lock', 'spikes/wasm-threads/package.json',
                     'spikes/wasm-threads/package-lock.json')
         for path in paths), 'Unexpected source inventory outside U11 boundaries')
    manifest = json.loads((UNIT / 'source-manifest.json').read_text())
    need(set(manifest) == {'stage', 'unit', 'version', 'writes'}
         and manifest['stage'] == 'code-generation' and manifest['version'] == 1
         and manifest['unit'] == 'u11-wasm-launcher'
         and sorted(row['path'] for row in manifest['writes']) == sorted(paths),
         'Manifest differs from signed differential inventory')
    trace = json.loads((UNIT / 'traceability.json').read_text())
    need(trace['unit'] == 'u11-wasm-launcher' and trace.get('draft') is False
         and trace['source_sha'] == revision and trace['ci_run'] == run_id
         and sorted(row['path'] for row in trace['reverse']) == sorted(paths),
         'Traceability incomplete or stale')
    for path in paths:
        local = ROOT / path
        need(local.is_file() and not local.is_symlink(), f'Missing/linked source: {path}')
        need(local.read_bytes() == command(['jj', '--ignore-working-copy', 'file',
             'show', '-r', revision, path]), f'Current source differs: {path}')
    policy = (ROOT / 'deny.toml').read_bytes()
    need(sha(policy) == '48881b3279292f43cbd1687636bce894185d35f5163c915a2799aff9f4d9b4e6',
         'Root dependency policy changed')
    signature = api(f'commits/{revision}')['commit']['verification']
    need(signature['verified'] and signature['reason'] == 'valid', 'Signature not Verified')
    run = api(f'actions/runs/{run_id}')
    need(run['head_sha'] == revision and run['status'] == 'completed'
         and run['conclusion'] == 'success', 'CI not successful at signed source')
    jobs = api(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
    need(len(jobs) < 100 and all(row['conclusion'] == 'success'
         and row['status'] == 'completed' for row in jobs), 'CI incomplete/failed')
    names = {row['name'] for row in jobs}
    need(BASE_JOBS <= names, 'Existing mandatory job missing')
    need(all(any(name.endswith('/ fuzz (' + target + ')') for name in names)
         for target in FUZZ), 'Affected fuzz job missing')
    artifacts = api(f'actions/runs/{run_id}/artifacts?per_page=100')['artifacts']
    need(len(artifacts) < 100, 'Artifact pagination unresolved')

    def archive(name):
        rows = [row for row in artifacts if row['name'] == name and not row['expired']]
        need(rows, f'Missing/expired artifact: {name}')
        rows.sort(key=lambda row: row['created_at'], reverse=True)
        need(len(rows) == 1 or rows[0]['created_at'] != rows[1]['created_at'],
             f'Ambiguous latest artifact: {name}')
        row = rows[0]
        if name in ('u11-node', 'u11-chromium', 'u11-firefox', 'u11-safari'):
            environment = name.removeprefix('u11-')
            matching = [job for job in jobs if '/ differential (' in job['name']
                        and job['name'].endswith(', ' + environment + ')')]
        elif name.startswith('u11-fuzz-'):
            target = name.removeprefix('u11-fuzz-')
            matching = [job for job in jobs if job['name'].endswith('/ fuzz (' + target + ')')]
        elif name.endswith('-coverage-lcov'):
            matching = [job for job in jobs if job['name'] == 'line coverage >= 80%']
        elif name == 'u11-acceptance-inputs':
            matching = [job for job in jobs if job['name'].endswith('/ build-oracle')]
        else:
            matching = []
        need(len(matching) == 1 and matching[0]['started_at'] <= row['created_at']
             <= matching[0]['completed_at'], 'Artifact not bound to latest successful job')
        need(row['workflow_run']['head_sha'] == revision
             and row['workflow_run']['id'] == run_id, 'Artifact source mismatch')
        return zipfile.ZipFile(io.BytesIO(command(['gh', 'api',
             f'repos/{REPO}/actions/artifacts/{row["id"]}/zip'])))

    inputs = archive('u11-acceptance-inputs')
    wasm = member(inputs, 'packages/paludarium-wasm/paludarium.wasm')
    receipt = document(inputs, 'target/guests/u10/build-receipt.json')
    need(receipt['exit'] == 0 and receipt['source_unchanged']
         and receipt['source_before'] == receipt['source_after']
         and receipt['audits'] == {'probe': 0, 'aube': 0}
         and receipt['aube']['revision'] == 'bd94e42f54d3b5e3dd102716b7197f316cb5f4ed',
         'Guest build/source/audits changed')
    spec = importlib.util.spec_from_file_location('u11_evidence', ROOT / 'tests/guests/u10/evidence.py')
    evidence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evidence)
    hashes = {}
    for name in ('probe', 'aube'):
        binary = member(inputs, 'target/guests/u10/' + name)
        evidence.static_elf(binary)
        hashes[name] = sha(binary)
        need(receipt['binaries'][name]['sha256'] == hashes[name], 'Guest hash mismatch')
    license_policy = receipt['license_policy']
    guest_policy = member(inputs, 'target/guests/u10/aube-deny.toml')
    license_text = member(inputs, 'target/guests/u10/licenses/webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt')
    need(license_policy['exception'] == evidence.LICENSE_EXCEPTION
         and guest_policy == evidence.guest_policy(policy, license_policy['exception'])
         and license_policy['root_config_sha256'] == sha(policy)
         and license_policy['guest_config_sha256'] == sha(guest_policy)
         and license_policy['license_sha256'] == sha(license_text)
         and sha(license_text) == 'e271993808fec50ab29350b39539cdec611a9103f827e0aa26d61da70e2d33f8',
         'Approved guest license exception differs')
    native_bytes = member(inputs, 'target/u11/native/observations.json')
    native = json.loads(native_bytes)
    need(native['native_complete'] and native['binary_hashes'] == hashes
         and len(native['rows']) == 14 and native['route'] == ''
         and 'Linux' in native['machine'] and 'x86_64' in native['machine'],
         'Fresh isolated native oracle invalid')
    for row in native['rows'].values():
        need(row['exit'] == 0 and not row['timed_out']
             and math.isfinite(row['wall_seconds']) and 0 <= row['wall_seconds'] <= 30,
             'Native guest deadline/exit failed')
    for row in native['rows'].values():
        for metadata in row.get('filesystem_metadata', {}).values():
            metadata['mtime_ns'] = str(metadata['mtime_ns'])
    checker = '''
import {compare} from './packages/paludarium-wasm/tests/u11-programs.mjs';
import {compareFilesystem} from './packages/paludarium-wasm/tests/u11-filesystem.mjs';
let input=''; for await(const chunk of process.stdin) input+=chunk;
const {native,report}=JSON.parse(input);
for(const [name,row] of Object.entries(report.rows)) {
  compare(native.rows[name],row,native.fixture_root,native.fixture_root);
  if(!name.startsWith('probe-')) await compareFilesystem(native.rows[name].filesystem_metadata,row.filesystem,native.fixture_root+'/fixture');
}
'''
    for environment in ('node', 'chromium', 'firefox', 'safari'):
        bundle = archive('u11-' + environment)
        report = document(bundle, 'observations.json')
        supervisor = document(bundle, 'suite-supervisor.json')
        need(supervisor['exit'] == 0 and not supervisor['timed_out']
             and supervisor['process_group_cleaned'], 'Suite cleanup/deadline failed')
        need(report['environment'] == environment and report['complete'] is True
             and report['module_sha256'] == sha(wasm)
             and report['oracle_sha256'] == sha(native_bytes)
             and report['guest_hashes'] == hashes
             and set(report['rows']) == set(native['rows']), 'Environment binding incomplete')
        for row in report['rows'].values():
            need(row['pass'] and row['exit'] == 0 and not row['timed_out']
                 and not row['errors'] and math.isfinite(row['seconds'])
                 and 0 <= row['seconds'] <= 30, 'Actual guest comparison failed')
        need(NODE is not None, 'Mise-managed Node binary unavailable')
        command([NODE, '--input-type=module', '-e', checker],
                data=json.dumps({'native': native, 'report': report}).encode())
    for name in ('u3', 'u9', 'u11'):
        lcov = member(archive(name + '-coverage-lcov'), name + '-coverage.lcov').decode()
        lines = sum(map(int, re.findall(r'^LF:(\d+)$', lcov, re.MULTILINE)))
        hit = sum(map(int, re.findall(r'^LH:(\d+)$', lcov, re.MULTILINE)))
        need(lines > 0 and 0 <= hit <= lines and hit * 100 >= lines * 80,
             f'{name} actual LCOV floor failed')
        need(proof['coverage'][name] == {'lines': lines, 'hit': hit}, 'Coverage evidence differs')
    coverage_job = next(row for row in jobs if row['name'] == 'line coverage >= 80%')
    log = command(['gh', 'api', '--allow-escape-sequences',
                  f'repos/{REPO}/actions/jobs/{coverage_job["id"]}/logs']).decode()
    totals = re.findall(r'\bTOTAL\s+([^\n]+)', log)
    need(totals, 'Workspace coverage totals missing')
    cells = totals[0].split()
    lines, missed = int(cells[6]), int(cells[7])
    need(lines > 0 and 0 <= missed <= lines and (lines - missed) * 100 >= lines * 80,
         'Workspace actual coverage floor failed')
    for target in FUZZ:
        bundle = archive('u11-fuzz-' + target)
        need(member(bundle, 'exit.txt').strip() == b'0'
             and member(bundle, 'lock-before.sha256') == member(bundle, 'lock-after.sha256'),
             'Fuzz exit/lock changed')
        log = member(bundle, 'raw.log').decode(errors='replace')
        durations = re.findall(r'Done \d+ runs in (\d+) second', log)
        need(durations and int(durations[-1]) >= 600, 'Fuzz 600-second observation missing')
    print(f'Verified finite U11: signed {revision}, CI {run_id}, fresh native14, '
          'Node/Chromium/Firefox/actual Safari fourteen cases each, metadata,80% floors,7 fuzz targets.')


if __name__ == '__main__':
    try:
        validate()
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as error:
        print(f'U11 verification failed: {error}', file=sys.stderr)
        raise SystemExit(1)
