"""Read-only U10 checkpoint candidate. Formal execution requires human approval.

The preserved final-proof.json is the completed historical U10 baseline.
u10-current-proof.json explicitly supersedes it for current signed source/CI.
Both bindings and historical hashes are checked. No pending state, historical
oracle substitution, skipped source checks, or writes are accepted.
"""
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
import zipfile
from datetime import datetime

RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
UNIT = RECORD / 'construction/u10-probe-aube-native/code-generation'
REPO = 'Marukome0743/paludarium'
EXPECTED = ["tests/guests/u10/.gitignore","tests/guests/u10/probe/.gitignore","scripts/u10-run.py","scripts/u10-build-guests.sh","tests/guests/u10/runner.py","tests/guests/u10/evidence.py","tests/guests/u10/comparison.py","tests/guests/u10/build.py","tests/guests/u10/native.py","tests/guests/u10/cases.json","tests/guests/u10/source-lock.json","tests/guests/u10/probe/Cargo.toml","tests/guests/u10/probe/Cargo.lock","tests/guests/u10/probe/src/main.rs","tests/guests/u10/fixtures/app/package.json","tests/guests/u10/fixtures/app/filedep/package.json","tests/guests/u10/fixtures/outside/linked/package.json","tests/guests/u10/runner-tests/test_ready.py","tests/guests/u10/runner-tests/test_evidence.py","tests/guests/u10/runner-tests/test_policy.py","tests/guests/u10/runner-tests/test_comparison.py","tests/guests/u10/runner-tests/test_runner.py","tests/guests/u10/differential.py","tests/guests/u10/metadata.py","tests/guests/u10/runner-tests/test_metadata.py","crates/paludarium-harness/tests/diff_u10.rs","crates/paludarium-harness/tests/support/u10.rs","crates/paludarium-runtime/src/lib.rs","crates/paludarium-runtime/src/u10_tests.rs",".github/workflows/ci.yml","tests/guests/u10/COMPARISON.md","docs/u10/source-review.md","docs/u10/static-pie-checker.md",".github/workflows/u10-native-diagnostic.yml","README.md","docs/u10/README.md","docs/u10/timings.md"]
BASE_JOBS = {
    'dependencies', 'lint', 'line coverage >= 80%',
    'unit tests (windows-latest)', 'unit tests (macos-latest)',
    'unit tests (ubuntu-latest)', 'differential tests (x86-64 Linux)',
    'production wasm (shared Rust heap, nested Workers)',
}
MODES = {'/package.json': 420, '/filedep/package.json': 420,
         '/outside/linked/package.json': 420}
EXTRA = ['tests/guests/u10/comparison_args.py',
         'tests/guests/u10/runner-tests/test_comparison_args.py']


def current_binding(historical, trace, proof):
    need(historical['status'] == 'complete' and proof['status'] == 'complete', 'Proof incomplete')
    need(trace['source_sha'] == historical['source_sha'] and trace['ci_run'] == historical['ci_run'],
         'Historical trace/proof binding differs')
    need(proof['baseline_sha'] == historical['source_sha']
         and proof['baseline_run'] == historical['ci_run'], 'Supersession baseline differs')
    need(proof['extra_sources'] == EXTRA, 'Supplemental executable inventory differs')


def select_artifact(artifacts, name, revision, run_id, job, pinned_id):
    matches = [a for a in artifacts if a['name'] == name and a['expired'] is False]
    need(matches, f'Artifact missing/expired: {name}')
    item = max(matches, key=lambda a: (a['created_at'], a['id']))
    need(item['id'] == pinned_id and item['workflow_run']['head_sha'] == revision
         and item['workflow_run']['id'] == run_id, 'Artifact source/latest selection differs')
    stamp = lambda value: datetime.fromisoformat(value.replace('Z', '+00:00'))
    need(stamp(job['started_at']) <= stamp(item['created_at']) <= stamp(job['completed_at']),
         'Artifact outside successful owning job execution')
    return item


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=60)
    need(result.returncode == 0, f'Command failed: {args!r}: {result.stderr[:800]!r}')
    return result.stdout


def api(endpoint):
    return json.loads(command(['gh', 'api', f'repos/{REPO}/{endpoint}']))


def member(archive, suffix):
    names = [suffix] if suffix in archive.namelist() else [
        n for n in archive.namelist() if n.endswith('/' + suffix)]
    need(len(names) == 1, f'Artifact member missing/ambiguous: {suffix}')
    return archive.read(names[0])


def document(archive, suffix):
    return json.loads(member(archive, suffix))


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'tests/guests/u10/{name}.py')
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def successful(row):
    need(row['exit'] == 0 and row['timed_out'] is False, 'Guest exit/timeout failed')
    seconds = row['wall_seconds']
    need(isinstance(seconds, (float, int)) and not isinstance(seconds, bool)
         and math.isfinite(seconds) and 0 <= seconds <= 30, 'Guest deadline invalid')


def validate():
    preserved = {p: sha(p.read_bytes()) for p in (
        UNIT / 'verification/final-proof.json', UNIT / 'traceability.json')}
    historical = json.loads((UNIT / 'verification/final-proof.json').read_text())
    proof = json.loads((RECORD / 'verification/u10-current-proof.json').read_text())
    need(proof['status'] == 'complete', 'Final proof pending/incomplete')
    revision, run_id = proof['source_sha'], proof['ci_run']
    need(re.fullmatch(r'[0-9a-f]{40}', revision) and isinstance(run_id, int), 'Invalid source/run binding')
    manifest = json.loads((UNIT / 'source-manifest.json').read_text())
    paths = [row['path'] for row in manifest['writes']]
    need(manifest['unit'] == 'u10-probe-aube-native' and paths == EXPECTED
         and len(set(paths)) == 37, 'Manifest inventory differs')
    trace = json.loads((UNIT / 'traceability.json').read_text())
    current_binding(historical, trace, proof)
    need({str(p.relative_to(RECORD)): value for p, value in preserved.items()}
         == proof['historical_hashes'], 'Historical evidence bytes changed')
    ancestry = command(['jj', '--ignore-working-copy', 'log', '--no-graph', '-r',
        f'{historical["source_sha"]} & ancestors({revision})', '-T', 'commit_id']).decode().strip()
    need(ancestry == historical['source_sha'], 'Current source is not descendant of baseline')
    need(trace['unit'] == 'u10-probe-aube-native' and trace.get('draft') is False
         and trace['source_sha'] == historical['source_sha'] and trace['ci_run'] == historical['ci_run'],
         'Historical traceability not final')
    need({row['path'] for row in trace['reverse']} == set(paths)
         and len(trace['reverse']) == 37, 'Traceability inventory differs')
    for path in paths + EXTRA:
        local = ROOT / path
        need(local.is_file() and not local.is_symlink(), f'Missing/linked source: {path}')
        need(local.read_bytes() == command(['jj', '--ignore-working-copy', 'file', 'show',
                                            '-r', revision, path]), f'Current source differs: {path}')
    root_policy = (ROOT / 'deny.toml').read_bytes()
    need(sha(root_policy) == '48881b3279292f43cbd1687636bce894185d35f5163c915a2799aff9f4d9b4e6',
         'Root policy differs from preserved baseline')
    need(root_policy == command(['jj', '--ignore-working-copy', 'file', 'show',
                                 '-r', revision, 'deny.toml']), 'Root policy differs from signed source')
    commit = api(f'commits/{revision}')
    signature = commit['commit']['verification']
    need(commit['sha'] == revision and signature['verified'] is True
         and signature['reason'] == 'valid', 'Signature not Verified/valid')
    run = api(f'actions/runs/{run_id}')
    need(run['head_sha'] == revision and run['status'] == 'completed'
         and run['conclusion'] == 'success', 'CI not successful at final source')
    jobs = api(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
    need(len(jobs) < 100 and all(j['status'] == 'completed' and j['conclusion'] == 'success'
                               for j in jobs), 'CI incomplete/failed/pagination unresolved')
    by_name = {j['name']: j for j in jobs}
    need(BASE_JOBS <= set(by_name), 'Existing mandatory job missing')
    u10_jobs = {}
    for suffix in ('fixture-metadata-oracle', 'native-first', 'differential'):
        matches = [j for j in jobs if j['name'].endswith('/ ' + suffix)]
        need(len(matches) == 1, f'Reusable U10 job missing/ambiguous: {suffix}')
        u10_jobs[suffix] = matches[0]
    artifacts = api(f'actions/runs/{run_id}/artifacts?per_page=100')['artifacts']
    need(len(artifacts) < 100, 'Artifact pagination unresolved')

    def archive(name):
        owner = {'u10-native-first': u10_jobs['native-first'],
                 'u10-differential': u10_jobs['differential'],
                 'u10-native-metadata': u10_jobs['fixture-metadata-oracle'],
                 'u3-coverage-lcov': by_name['line coverage >= 80%'],
                 'u9-coverage-lcov': by_name['line coverage >= 80%']}[name]
        item = select_artifact(artifacts, name, revision, run_id, owner, proof['artifacts'][name])
        return zipfile.ZipFile(io.BytesIO(command(['gh', 'api',
            f'repos/{REPO}/actions/artifacts/{item["id"]}/zip'])))

    built = archive('u10-native-first')
    diff = archive('u10-differential')
    metadata = archive('u10-native-metadata')
    receipt = document(built, 'guests/u10/build-receipt.json')
    need(receipt['exit'] == 0 and receipt['source_unchanged'] is True
         and receipt['source_before'] == receipt['source_after']
         and len(receipt['source_before']) == 1365, 'Build/source audit invalid')
    need(receipt['toolchain'] == 'nightly-2026-10-01'
         and receipt['target'] == 'x86_64-unknown-linux-musl'
         and receipt['aube']['revision'] == 'bd94e42f54d3b5e3dd102716b7197f316cb5f4ed'
         and receipt['aube']['lock_sha256'] == '8960ea5673ff7b7bf376d2b1570b2a79875c2bf397c9044f88b203d7375b2668',
         'Fixed build differs')
    evidence = module('evidence')
    comparison = module('comparison')
    args_comparison = module('comparison_args')
    hashes = {}
    for name in ('probe', 'aube'):
        data = member(built, 'guests/u10/' + name)
        evidence.static_elf(data)
        hashes[name] = sha(data)
        need(receipt['binaries'][name]['static_elf'] is True
             and receipt['binaries'][name]['sha256'] == hashes[name], 'ELF receipt mismatch')
    need(receipt['binaries']['probe']['lock_sha256']
         == sha((ROOT / 'tests/guests/u10/probe/Cargo.lock').read_bytes()), 'Probe lock differs')
    policy = receipt['license_policy']
    config = member(built, 'guests/u10/aube-deny.toml')
    license_text = member(built, 'guests/u10/licenses/webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt')
    need(policy['exception'] == evidence.LICENSE_EXCEPTION
         and config == evidence.guest_policy(root_policy, policy['exception'])
         and policy['root_config_sha256'] == sha(root_policy)
         and policy['guest_config_sha256'] == sha(config)
         and policy['license_sha256'] == sha(license_text)
         and policy['license_sha256'] == 'e271993808fec50ab29350b39539cdec611a9103f827e0aa26d61da70e2d33f8'
         and policy['crate_source'] == 'registry+https://github.com/rust-lang/crates.io-index'
         and receipt['audits'] == {'probe': 0, 'aube': 0}, 'License audit differs')
    native = document(diff, 'native/observations.json')
    emulated = document(diff, 'observations.json')
    first = document(built, 'u10/native/observations.json')
    need(all(n['native_complete'] is True and n['binary_hashes'] == hashes
             and 'Linux' in n['machine'] and 'x86_64' in n['machine']
             and n['network_namespace'].startswith('net:[') and n['route'] == ''
             and n['fixture_input_modes'] == MODES for n in (native, first)), 'Fresh native oracle invalid')
    need(emulated['native_complete'] is True and emulated['differential_complete'] is True
         and emulated['binary_hashes'] == hashes, 'Differential incomplete')
    cases = json.loads((ROOT / 'tests/guests/u10/cases.json').read_text())
    primary_cases = args_comparison.comparison_config(cases)
    need(primary_cases['aube'][1]['args'] == cases['aube'][1]['args'] + ['--reporter=append-only']
         and primary_cases['aube'][2]['args'] == cases['aube'][2]['args'] + ['--reporter=append-only'],
         'Primary comparison arguments differ')
    probe_names = ['probe-' + p for p in cases['probe'] + ['all', 'environment']]
    aube_names = ['version', 'install', 'frozen', 'list']
    need(set(native['rows']) == set(first['rows']) == set(probe_names + aube_names)
         and set(emulated['rows']) == set(probe_names + aube_names + ['default-version', 'default-install']),
         'Native14/emulator16 row inventory differs')
    for oracle in (native, first):
        for row in oracle['rows'].values():
            successful(row)
        comparison.reproduced({k: oracle['rows'][k] for k in aube_names})
    for name, row in emulated['rows'].items():
        successful(row)
        expected = native['rows'][name.removeprefix('default-')]
        expected_root = native['fixture_root'] if name.startswith('probe-') else native['fixture_root'] + '/fixture/app'
        comparison.compare(expected, row, expected_root, '/')
        if name.startswith('probe-') and name != 'probe-environment':
            items = cases['probe'] if name == 'probe-all' else [name.removeprefix('probe-')]
            comparison.probe_pass(expected, items)
            comparison.probe_pass(row, items)
        if not name.startswith('probe-'):
            need(row['fixture_input_modes'] == MODES, 'Emulator fixture mode differs')
        runners = [n for n in diff.namelist() if n.endswith('/' + name + '/runner.json')
                   and 'original-argv/' not in n]
        need(len(runners) == 1, 'Durable operation runner record missing')
        successful(json.loads(diff.read(runners[0])))
    comparison.reproduced({k: emulated['rows'][k] for k in aube_names})
    original_native = document(diff, 'original-argv/native/observations.json')
    original_emulated = document(diff, 'original-argv/observations.json')
    need(original_native['native_complete'] is True
         and original_emulated['differential_complete'] is True
         and original_native['binary_hashes'] == original_emulated['binary_hashes'] == hashes
         and original_native['fixture_input_modes'] == MODES
         and set(original_native['rows']) == set(probe_names + aube_names)
         and set(original_emulated['rows']) == set(emulated['rows']), 'Original argv evidence incomplete')
    for name, row in original_emulated['rows'].items():
        successful(row)
        expected = original_native['rows'][name.removeprefix('default-')]
        successful(expected)
        expected_root = original_native['fixture_root'] if name.startswith('probe-') else original_native['fixture_root'] + '/fixture/app'
        args_comparison.compare_original(expected, row, expected_root, '/')
        need(isinstance(row['stderr'], str) and isinstance(expected['stderr'], str), 'Original raw stderr missing')
        if not name.startswith('probe-'):
            need(row['fixture_input_modes'] == MODES, 'Original fixture modes differ')
        successful(document(diff, 'original-argv/' + Path(original_emulated['operation_records']).name + '/' + name + '/runner.json'))
    for observation in (original_native, original_emulated):
        comparison.reproduced({k: observation['rows'][k] for k in aube_names})
    stat = document(metadata, 'native-stat.json')
    successful(stat['result'])
    need(stat['result']['stderr'] == '' and json.loads(stat['result']['stdout']) == stat['native_stat']
         and stat['native_stat']['fixture_modes'] == {'app/package.json': 33188,
             'app/filedep/package.json': 33188, 'outside/linked/package.json': 33188}
         and stat['native_stat']['mode_boundaries'] == {'493': 33261, '420': 33188, '0': 32768},
         'Native metadata oracle differs')
    coverage_job = by_name['line coverage >= 80%']
    coverage_log = command(['gh', 'api', '--allow-escape-sequences',
        f'repos/{REPO}/actions/jobs/{coverage_job["id"]}/logs']).decode()
    totals = re.findall(r'\bTOTAL\s+([^\n]+)', coverage_log)
    expected_totals = proof['coverage']['totals']
    need(len(totals) == len(expected_totals) == 4, 'Coverage TOTAL inventory differs')
    for index, (text, expected) in enumerate(zip(totals, expected_totals)):
        cells = text.split()
        need(len(cells) >= 9, 'Malformed coverage TOTAL')
        denominator, missed = int(cells[6]), int(cells[7])
        need(expected == {'lines': denominator, 'hit': denominator - missed}
             and denominator > 0 and 0 <= missed <= denominator,
             'Coverage denominator differs')
        # workspace/U1 reports are their actual floors. U3's human report
        # has a different population; its authoritative gate is LCOV below.
        if index < 2:
            need((denominator - missed) * 100 >= denominator * 80
                 and float(cells[8].rstrip('%')) >= 80, 'Workspace/U1 floor failed')
    for name in ('u3', 'u9'):
        lcov = member(archive(name + '-coverage-lcov'), name + '-coverage.lcov').decode()
        lines = sum(map(int, re.findall(r'^LF:(\d+)$', lcov, re.MULTILINE)))
        hit = sum(map(int, re.findall(r'^LH:(\d+)$', lcov, re.MULTILINE)))
        need(proof['coverage'][name] == {'lines': lines, 'hit': hit}
             and lines > 0 and 0 <= hit <= lines and hit * 100 >= lines * 80,
             f'{name} coverage denominator/floor differs')
    native_log = command(['gh', 'api', '--allow-escape-sequences',
        f'repos/{REPO}/actions/jobs/{u10_jobs["native-first"]["id"]}/logs']).decode()
    diff_log = command(['gh', 'api', '--allow-escape-sequences',
        f'repos/{REPO}/actions/jobs/{u10_jobs["differential"]["id"]}/logs']).decode()
    need('Ran 44 tests' in native_log and re.search(r'\bOK\s*$', native_log, re.MULTILINE)
         and re.search(r'test u10_differential \.\.\. ok', diff_log), 'Required internal/differential tests missing')
    need(proof['timings'] == {name: {'native': native['rows'][name]['wall_seconds'],
                                    'emulator': emulated['rows'][name]['wall_seconds']}
                             for name in aube_names}, 'Timing rows differ')
    need(proof['measurement_scope'] == 'builds complete; guest operations sequential; OS background uncontrolled',
         'Measurement scope invalid')
    need(all(sha(p.read_bytes()) == value for p, value in preserved.items()), 'Historical evidence modified')
    print(f'Verified finite U10: signed {revision}, CI {run_id}, native14/emulator16, '
          'fixture0644, full guest audits, existing80% floors. No all-input/platform guarantee.')


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    try:
        validate()
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as error:
        print(f'U10 verification failed: {error}', file=sys.stderr)
        raise SystemExit(1)

