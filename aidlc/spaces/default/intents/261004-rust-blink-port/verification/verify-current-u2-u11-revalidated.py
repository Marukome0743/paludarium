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
U2 = RECORD / 'construction/u2-integer-isa/code-generation'
U11 = RECORD / 'construction/u11-wasm-launcher/code-generation/verification'
HEAD = '2b3874eabda6fe6f1d1334202421db733445fd21'
OBS_HEAD = 'b263121214981a549ad8bfb7ddb975de03226f58'
JJ = next(p for p in sorted(Path.home().glob('.local/share/mise/installs/jj/*/jj')) if p.is_file())
BASELINE_REBINDINGS = {
    "tests/guests/u10/source-lock.json": {
        "old_sha256": "81c29d81e22de9ea213f95f5e5312b4f3f7891dbcaf73b51de01f5743b6d3434",
        "current_sha256": "48bd3cfa32b4cac538dab481f6e07515294884504d7971ea54e8dc902cc92be2"
    },
    ".github/workflows/ci.yml": {
        "old_sha256": "eb048be295d1acde5cad190b16743c9d6cc6fb706e79e59162df0f684df4c5ba",
        "current_sha256": "08800ba029690d0804bd626f9dd79b3f5e5cb50787593d53e3cf9cc3200e2c70"
    },
    ".github/workflows/u10-native-diagnostic.yml": {
        "old_sha256": "ea4a4919ccd22d8a9eb825456e8f9401202bb09dddb55c701367ef4eb3f459f7",
        "current_sha256": "4ca9080f7efa9934ebaddf2737b54debfec1b65fba376a4ff1df32e411cce913"
    }
}

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
CURRENT_ADDITIONS = ['.github/scripts/u10-current-diagnostic.py',
                     '.github/workflows/u10-current-verification.yml',
                     'crates/paludarium-host/src/native_fs.rs'] + EXTRA
CURRENT_EXPECTED = CURRENT_ADDITIONS + EXPECTED
HISTORICAL_TRACE = U2 / 'verification/step64-historical-u10-traceability.json'
HISTORICAL_TRACE_SHA = '2164fbd9af6bf6478c06ecf10ef3e3bc7d5dd3bb1a3be845e8855a5a13857764'
CURRENT_TRACE_SHA = '0bde9d5eae3205020fe85e0d3e434cfe9c63ba5d7238612e5bb4859e338ad87c'


def validate_trace(raw, expected_digest, source, run_id, expected_paths):
    need(sha(raw) == expected_digest, 'Trace original digest differs')
    trace = json.loads(raw)
    need(trace['source_sha'] == source and trace['ci_run'] == run_id,
         'Trace source/CI binding differs')
    need(trace['stage'] == 'code-generation' and trace['unit'] == 'u10-probe-aube-native'
         and trace.get('draft', False) is False and trace['ci_status'] == 'success',
         'Trace state differs')
    paths = [row['path'] for row in trace['reverse']]
    need(paths == expected_paths and len(set(paths)) == len(paths), 'Trace inventory differs')
    ids = trace['upstream_ids']
    need(len(set(ids)) == len(ids) and len(trace['coverage']) == len(ids)
         and {row['id'] for row in trace['coverage']} == set(ids), 'Trace requirement inventory differs')
    need(all(row['id'] == row['path'] and row['status'] == 'OK'
             and row['upstream_ids'] and set(row['upstream_ids']) <= set(ids)
             for row in trace['reverse']), 'Trace reverse mapping differs')
    return trace


def historical_originals():
    # Preserve logical historical keys while reading the exact saved original.
    physical = {UNIT / 'verification/final-proof.json': UNIT / 'verification/final-proof.json',
                UNIT / 'traceability.json': HISTORICAL_TRACE}
    preserved = {actual: sha(actual.read_bytes()) for actual in physical.values()}
    logical_hashes = {str(logical.relative_to(RECORD)): preserved[actual]
                     for logical, actual in physical.items()}
    trace = validate_trace(HISTORICAL_TRACE.read_bytes(), HISTORICAL_TRACE_SHA,
                          '5b319a7072e698d8e7c2f94e4821bf584ec381fb', 38010586387, EXPECTED)
    return preserved, logical_hashes, trace


def validate_inventory(rows, expected_paths, signed_digests):
    """Check a distinct ordered inventory against independent source digests."""
    paths = [row['path'] for row in rows]
    need(paths == expected_paths and len(set(paths)) == len(expected_paths),
         'Manifest inventory differs')
    need(set(signed_digests) == set(expected_paths), 'Digest inventory differs')
    for row in rows:
        value = row['sha256']
        need(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
             and value == signed_digests[row['path']],
             f'Source digest differs: {row["path"]}')


def validate_current_inventory(manifest, revision):
    need(manifest['unit'] == 'u10-probe-aube-native', 'Manifest unit differs')
    paths = [row['path'] for row in manifest['writes']]
    need(paths == CURRENT_EXPECTED and len(set(paths)) == 42, 'Manifest inventory differs')
    rows, signed = [], {}
    for path in paths:
        local = ROOT / path
        need(local.is_file() and not local.is_symlink(), f'Missing/linked source: {path}')
        rows.append({'path': path, 'sha256': sha(local.read_bytes())})
        signed[path] = sha(command(['jj', '--ignore-working-copy', 'file', 'show', '-r', HEAD, path]))
        observed = sha(command(['jj', '--ignore-working-copy', 'file', 'show', '-r', revision, path]))
        need(observed == signed[path], f'Current/owning CI source digest differs: {path}')
    validate_inventory(rows, CURRENT_EXPECTED, signed)


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
    args = [str(JJ) if value == 'jj' and index == 0 else value for index, value in enumerate(args)]
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


def successful(row, time_field='wall_seconds'):
    need(row['exit'] == 0 and row['timed_out'] is False, 'Guest exit/timeout failed')
    seconds = row[time_field]
    need(isinstance(seconds, (float, int)) and not isinstance(seconds, bool)
         and math.isfinite(seconds) and 0 <= seconds <= 30, 'Guest deadline invalid')


def validate_u10_baseline():
    """Validate historical U10 originals; explicit three-path supersession is separate from historical guest success."""
    preserved, logical_hashes, trace = historical_originals()
    historical = json.loads((UNIT / 'verification/final-proof.json').read_text())
    proof = json.loads((RECORD / 'verification/u10-current-proof.json').read_text())
    need(proof['status'] == 'complete', 'Final proof pending/incomplete')
    revision, run_id = proof['source_sha'], proof['ci_run']
    need(re.fullmatch(r'[0-9a-f]{40}', revision) and isinstance(run_id, int), 'Invalid source/run binding')
    manifest = json.loads((UNIT / 'source-manifest.json').read_text())
    # The live manifest is current42; history37 comes from the preserved
    # canonical list and original trace, never a projection of this manifest.
    need(manifest['unit'] == 'u10-probe-aube-native'
         and [row['path'] for row in manifest['writes']] == CURRENT_EXPECTED,
         'Manifest inventory differs')
    paths = EXPECTED
    current_binding(historical, trace, proof)
    need(logical_hashes == proof['historical_hashes'], 'Historical evidence bytes changed')
    ancestry = command(['jj', '--ignore-working-copy', 'log', '--no-graph', '-r',
        f'{historical["source_sha"]} & ancestors({revision})', '-T', 'commit_id']).decode().strip()
    need(ancestry == historical['source_sha'], 'Current source is not descendant of baseline')
    need(trace['unit'] == 'u10-probe-aube-native' and trace.get('draft') is False
         and trace['source_sha'] == historical['source_sha'] and trace['ci_run'] == historical['ci_run'],
         'Historical traceability not final')
    need({row['path'] for row in trace['reverse']} == set(paths)
         and len(trace['reverse']) == 37, 'Traceability inventory differs')
    historical_rows = []
    for path in paths + EXTRA:
        local = ROOT / path
        need(local.is_file() and not local.is_symlink(), f'Missing/linked source: {path}')
        signed = command(['jj', '--ignore-working-copy', 'file', 'show', '-r', revision, path])
        if path in paths:
            historical_rows.append({'path': path, 'sha256': sha(signed)})
        expected = BASELINE_REBINDINGS.get(path)
        if expected is None:
            need(local.read_bytes() == signed, f'Current source differs: {path}')
        else:
            need(sha(signed) == expected['old_sha256'] and sha(local.read_bytes()) == expected['current_sha256'],
                 f'Explicit baseline/current binding differs: {path}')
    binding = json.loads((U2 / 'verification/step59-u10-source-binding.json').read_text())
    need(binding['old_source_sha'] == revision, 'Historical inventory source differs')
    original_digests = {row['path']: row['old_sha256'] for row in binding['rows']
                        if row['path'] in EXPECTED}
    validate_inventory(historical_rows, EXPECTED, original_digests)
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


def validate_current_u10():
    """Validate successful U10 jobs on2c690; preserve that whole run failure and require independent bounded repair."""
    preserved, logical_hashes, trace = historical_originals()
    historical = json.loads((UNIT / 'verification/final-proof.json').read_text())
    proof = json.loads((U2 / 'verification/step59-current-u10-proof.json').read_text())
    need(proof['status'] == 'complete', 'Final proof pending/incomplete')
    revision, run_id = proof['source_sha'], proof['ci_run']
    need(re.fullmatch(r'[0-9a-f]{40}', revision) and isinstance(run_id, int), 'Invalid source/run binding')
    manifest = json.loads((UNIT / 'source-manifest.json').read_text())
    validate_current_inventory(manifest, revision)
    current_trace = validate_trace((UNIT / 'traceability.json').read_bytes(), CURRENT_TRACE_SHA,
        'cb9797138313046b3cf9bbbfcab0515910b81215', 38095031011, CURRENT_EXPECTED)
    need(len(current_trace['upstream_ids']) == 60, 'Current trace requirement count differs')
    validate_current_inventory(manifest, current_trace['source_sha'])
    paths = EXPECTED  # Original trace37 and old executable checks remain history.
    current_binding(historical, trace, proof)
    need(logical_hashes == proof['historical_hashes'], 'Historical evidence bytes changed')
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
         and run['conclusion'] == 'failure', 'Preserved partly failed CI binding differs')
    jobs = api(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
    need(len(jobs) < 100 and all(j['status'] == 'completed' for j in jobs), 'CI pagination/incomplete')
    failed = [j for j in jobs if j['conclusion'] != 'success']
    need([(j['id'], j['name'], j['conclusion']) for j in failed] ==
         [(114360236133, 'u11-fuzz / fuzz (syscall_args)', 'failure')], 'Preserved failure set differs')
    repaired = api('actions/runs/38104676911')
    need(repaired['head_sha'] == HEAD and repaired['status'] == 'completed' and repaired['conclusion'] == 'success',
         'Bounded quality repair CI not successful')
    repaired_jobs = api('actions/runs/38104676911/jobs?per_page=100')['jobs']
    need(len(repaired_jobs) == 7 and all(j['conclusion'] == 'success' for j in repaired_jobs), 'Seven repair jobs differ')
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
    need(receipt['toolchain'] == 'nightly-2026-10-10' and receipt['rustc'] == 'rustc 1.101.0-nightly (32dba69d6 2026-10-09)'
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


REV = HEAD

def digest(data):
    return hashlib.sha256(data).hexdigest()


def doc(path):
    return json.loads(path.read_text())


def show(revision, path):
    result = subprocess.run([str(JJ), '--ignore-working-copy', 'file', 'show', '-r', revision, path], cwd=ROOT, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError(f'jj read failed {revision} {path}: {result.stderr.decode()[:500]}')
    return result.stdout


def u2_saved_evidence_audit():
    source = doc(U11 / 'source-hashes.json')
    binding = doc(U11 / 'current-quality-source-binding.json')
    quality = doc(U11 / 'current-quality-proof.json')
    observed = doc(U11 / 'current-unaffected-proof.json')
    manifest = doc(U2 / 'source-manifest.json')
    claims = [r['path'] for r in manifest['writes']]
    rows = []
    for path, expected in source['inputs'].items():
        current = (ROOT / path).read_bytes()
        signed = show(REV, path)
        rows.append({'path': path, 'current': digest(current), 'signed': digest(signed), 'recorded': expected, 'match': digest(current) == digest(signed) == expected})
    need(len(rows) == 329 and all(r['match'] for r in rows), 'Saved U2 evidence condition differs')
    claim_rows = [{'path': p, 'current': digest((ROOT / p).read_bytes()), 'signed': digest(show(REV, p))} for p in claims]
    need(len(claim_rows) == 124 and all(r['current'] == r['signed'] for r in claim_rows), 'Saved U2 evidence condition differs')
    changed = [r['path'] for r in rows if show(binding['observation_source_sha'], r['path']) != (ROOT / r['path']).read_bytes()]
    need(changed == binding['changed'] == ['.github/workflows/u11-fuzz.yml'], 'Saved U2 evidence condition differs')
    locks = {p: digest((ROOT / p).read_bytes()) for p in ('Cargo.lock', 'fuzz/Cargo.lock')}
    targets = {}
    for name, entry in quality['targets'].items():
        raw_path = U11 / entry['raw']
        raw = raw_path.read_bytes()
        folder = raw_path.parent
        need(digest(raw) == entry['raw_sha256'], 'Saved U2 evidence condition differs')
        need(digest((U11 / entry['binary']).read_bytes()) == entry['binary_sha256'], 'Saved U2 evidence condition differs')
        compiler = (folder / 'toolchain.txt').read_bytes()
        need(digest(compiler) == entry['compiler_sha256'], 'Saved U2 evidence condition differs')
        need('32dba69d69c5b10ea89a4042de8d0619f7756203' in compiler.decode(), 'Saved U2 evidence condition differs')
        for phase in ('before', 'after'):
            listed = dict((line.split()[1], line.split()[0]) for line in (folder / f'locks-{phase}.sha256').read_text().splitlines())
            need(listed == locks, 'Saved U2 evidence condition differs')
        need((folder / 'settings.txt').read_text() == entry['settings'], 'Saved U2 evidence condition differs')
        need('detect_leaks=1' in entry['settings'] and 'suppressions=/work/fuzz/lsan.supp' in entry['settings'], 'Saved U2 evidence condition differs')
        need(int((folder / 'exit.txt').read_text()) == entry['exit'] == 0, 'Saved U2 evidence condition differs')
        need(re.search(rf'Done {entry["runs"]} runs in 601 second', raw.decode()), 'Saved U2 evidence condition differs')
        need(entry['seconds'] == 601, 'Saved U2 evidence condition differs')
        targets[name] = {'runs': entry['runs'], 'seconds': 601, 'exit': 0, 'raw_sha256': entry['raw_sha256'], 'binary_sha256': entry['binary_sha256'], 'compiler_sha256': entry['compiler_sha256']}
    need(len(targets) == 7, 'Saved U2 evidence condition differs')
    environments = {}
    for name, entry in observed['environments'].items():
        original = (U11 / entry['raw']).read_bytes()
        need(digest(original) == entry['sha256'], 'Saved U2 evidence condition differs')
        data = json.loads(original)
        passed = data['slice_passed'] if name == 'node' else data['passed']
        need(data['complete'] is True and passed is True and len(data['rows']) == 14, 'Saved U2 evidence condition differs')
        need(all(row['pass'] is True and row['exit'] == 0 and row['timed_out'] is False for row in data['rows'].values()), 'Saved U2 evidence condition differs')
        need(data['version'] == entry['version'] and data['module_sha256'] == observed['module_sha256'], 'Saved U2 evidence condition differs')
        need(data['oracle_sha256'] == observed['oracle_sha256'] and data['guest_hashes'] == entry['guest_hashes'], 'Saved U2 evidence condition differs')
        environments[name] = {'version': entry['version'], 'cases': len(data['rows']), 'complete': data['complete'], 'passed': passed, 'raw_sha256': digest(original), 'module_sha256': data['module_sha256'], 'oracle_sha256': data['oracle_sha256']}
    coverage_path = U11 / observed['javascript_coverage']['raw']
    need(digest(coverage_path.read_bytes()) == observed['javascript_coverage']['sha256'], 'Saved U2 evidence condition differs')
    coverage = doc(coverage_path)
    need(coverage['passed'] is True and len(coverage['population']) == 5 and len(coverage['files']) == 5, 'Saved U2 evidence condition differs')
    need(all(row['raw_scripts'] > 0 for row in coverage['files']), 'Saved U2 evidence condition differs')
    need(coverage['total'] == {'lines': 449, 'hit': 420}, 'Saved U2 evidence condition differs')
    coverage = {'total': coverage['total'], 'population': coverage['population'], 'passed': coverage['passed'], 'sha256': digest(coverage_path.read_bytes())}
    old = doc(RECORD / 'verification/u10-current-proof.json')
    old_checker_paths = ['crates/paludarium-runtime/src/lib.rs', 'README.md']
    old_mismatch = [p for p in old_checker_paths if (ROOT / p).read_bytes() != show(old['source_sha'], p)]
    matrix = {}
    for path in ('crates/paludarium-harness/tests/diff_u2.rs', 'crates/paludarium-harness/tests/parallel_u2.rs', 'crates/paludarium-cpu/src/u2_tests.rs', 'docs/u2/differential-coverage.md', 'docs/u2/flag-masks.md'):
        text = (ROOT / path).read_text()
        matrix[path] = {'sha256': digest(text.encode()), 'test_names': re.findall(r'fn (u2_\w+)\(', text)}
    return {'kind': 'saved-evidence-read-only-audit-not-fresh-test', 'source_sha': REV, 'jj_binary': str(JJ), 'source_rows': rows, 'claim_rows': claim_rows, 'application_count': len(rows), 'claim_count': len(claim_rows), 'observation_changed': changed, 'locks': locks, 'quality_ci': quality['ci_run'], 'targets': targets, 'environments': environments, 'javascript_coverage': coverage, 'old_checker_source_sha': old['source_sha'], 'old_checker_mismatch': old_mismatch, 'matrix': matrix, 'preserved_hashes': {p: digest((U2 / p).read_bytes()) for p in ('code-generation-plan.md', 'unit-test-instructions.md', 'traceability.json', 'source-manifest.json')}, 'shared_proof_hashes': {p: digest((U11 / p).read_bytes()) for p in ('source-hashes.json', 'current-quality-source-binding.json', 'current-quality-proof.json', 'current-unaffected-proof.json')}}


def validate_shared_and_mmu():
    source = doc(U11 / 'source-hashes.json')
    need(source['baseline_source_sha'] == 'cb9797138313046b3cf9bbbfcab0515910b81215', 'U11 baseline differs')
    added = ['.github/workflows/u11-current-verification.yml', 'spikes/wasm-threads/package-lock.json', 'spikes/wasm-threads/package.json']
    changed = ['.github/workflows/u11-fuzz.yml', 'crates/paludarium-wasm/src/abi.rs', 'crates/paludarium-wasm/src/filesystem.rs', 'packages/paludarium-wasm/coordinator.mjs', 'packages/paludarium-wasm/tests/u11-api-check.mjs']
    need(source['baseline_added'] == added and source['baseline_changed'] == changed, 'Finite baseline diff inventory differs')
    actual = [p for p in source['inputs'] if p not in added and show(source['baseline_source_sha'], p) != (ROOT / p).read_bytes()]
    need(sorted(actual) == changed and len(source['inputs']) - len(added) == 326, 'Finite five changes differ')
    current_delta = command(['jj', '--ignore-working-copy', 'diff', '--from', '2c690e123ec2e8f28ccc672c2b0d79d7f5aa90f8', '--to', HEAD, '--name-only']).decode().splitlines()
    need(current_delta == ['.github/workflows/u11-current-verification.yml', '.github/workflows/u11-fuzz.yml', 'packages/paludarium-wasm/tests/u11-api-check.mjs'], 'U10 observation to current finite diff differs')
    result = u2_saved_evidence_audit()
    for path, expected in source['ci_record_helpers'].items():
        need(digest((ROOT/path).read_bytes()) == expected and show(HEAD,path) == (ROOT/path).read_bytes(), 'Signed CI helper differs: '+path)
    need(result['claim_count'] == 124 and result['application_count'] == 329, 'U2 inventory differs')
    for revision, run_id in [(HEAD,38104676911),(OBS_HEAD,38103577222)]:
        signature = api(f'commits/{revision}')['commit']['verification']
        need(signature['verified'] is True and signature['reason'] == 'valid', 'Shared signature invalid')
        run = api(f'actions/runs/{run_id}')
        need(run['head_sha'] == revision and run['status'] == 'completed' and run['conclusion'] == 'success', 'Shared finite CI binding differs')
        jobs = api(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
        need(len(jobs) < 100 and all(j['status'] == 'completed' and j['conclusion'] == 'success' for j in jobs), 'Shared finite CI jobs incomplete')
    module = U11 / 'final-current-ci/inputs/packages/paludarium-wasm/paludarium.wasm'
    oracle_path = U11 / 'final-current-ci/inputs/target/u11/native/observations.json'
    oracle = doc(oracle_path)
    need(oracle['native_complete'] is True and len(oracle['rows']) == 14, 'U11 fresh native inventory differs')
    for row in oracle['rows'].values():
        successful(row)
    for environment in ['node','chromium','firefox','safari']:
        folder = U11 / 'final-current-ci' / environment / environment
        observation = doc(folder / 'observations.json')
        need(observation['module_sha256'] == digest(module.read_bytes()) and observation['oracle_sha256'] == digest(oracle_path.read_bytes())
             and observation['guest_hashes'] == oracle['binary_hashes'], 'U11 module/oracle/guest binding differs')
        for row in observation['rows'].values():
            successful(row, time_field='seconds')
        supervisor = doc(folder / 'suite-supervisor.json')
        need(supervisor['exit'] == 0 and supervisor['timed_out'] is False and supervisor['process_group_cleaned'] is True, 'U11 suite watchdog/cleanup differs')
    trace = doc(U2 / 'traceability.json')
    need(trace['unit'] == 'u2-integer-isa' and len(trace['coverage']) == len(trace['upstream_ids']) == 92, 'U2 claims differ')
    sensors = doc(U2 / 'verification/step60-formal-sensors.json')
    for entry in sensors.values():
        need(entry['exit_code'] == 0 and json.loads(entry['output'])['pass'] is True and json.loads(entry['output'])['findings_count'] == 0, 'Formal U2 sensor failed')
    core = doc(U2 / 'verification/step55-core-sanitizer-binding.json')
    u3 = RECORD / 'construction/u3-sse/code-generation/verification'
    historical = doc(u3 / 'step30-current-proof.json')
    for target in ['cpu_u2','decode']:
        entry = core[target]
        need(len(entry['selected']) == 33 and not entry['mismatches'], 'Saved core inventory differs')
        for path, expected in entry['selected'].items():
            need(digest((ROOT / path).read_bytes()) == expected, 'Saved core input differs: ' + path)
        for name in ['environment.log','source-before.sha256','source-after.sha256','binary.sha256',target+'.log','exit.txt','settings.txt']:
            need(digest((u3 / 'step29-first-asan-raw' / target / name).read_bytes()) == historical['asan_evidence_hashes'][target+'/'+name], 'Saved core raw differs')
        directory = u3 / 'step29-first-asan-raw' / target
        settings = (directory/'settings.txt').read_text().splitlines()
        need(all(value in settings for value in ['seed=1','sanitizer=address','LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp','ASAN_OPTIONS=detect_leaks=1','CI_HEAD=97a642fd94b47abbd3612b7fa03fff1a741439a5']), 'Saved core sanitizer/settings differ')
        need('32dba69d69c5b10ea89a4042de8d0619f7756203' in (directory/'environment.log').read_text()
             and (directory/'source-before.sha256').read_bytes() == (directory/'source-after.sha256').read_bytes(), 'Saved core compiler/input binding differs')
        need(int((directory/'exit.txt').read_text()) == 0 and re.search(r'Done \d+ runs in 601 second', (directory/(target+'.log')).read_text()), 'Saved core bounded observation failed')
    # Old MMU4096 evidence stays historical. Only the new proof may satisfy4608.
    mmu = doc(U2 / 'verification/step58-mmu-proof.json')
    need(mmu['status'] == 'complete' and mmu['max_len'] == 4608 and mmu['max_total_time'] == 600
         and mmu['seed'] == 1 and mmu['timeout'] == 30 and mmu['rss_limit_mb'] == 2048 and mmu['exit'] == 0, 'MMU4608 condition incomplete')
    directory = U2 / 'verification/step58-mmu-artifact'
    for path, expected in mmu['raw_hashes'].items():
        need(digest((directory/path).read_bytes()) == expected, 'MMU original artifact differs: ' + path)
    raw = (directory/'target/u2-mmu-4608/raw.log').read_text()
    need(re.search(r'Done \d+ runs in 601 second',raw) and 'Seed: 1' in raw, 'MMU budget/seed observation differs')
    need(all(option in raw for option in ['-max_len=4608','-max_total_time=600','-timeout=30','-rss_limit_mb=2048','-seed=1']), 'MMU actual target command differs')
    need('6f5da406b56c2db6607202b63daee73aa8c61297' in (directory/'target/u2-mmu-4608/toolchain.txt').read_text(), 'MMU diagnostic compiler differs')
    before = (directory/'target/u2-mmu-4608/source-before.sha256').read_bytes()
    need(before == (directory/'target/u2-mmu-4608/source-after.sha256').read_bytes(), 'MMU source mutated')
    listed = {line.split(maxsplit=1)[1].strip():line.split(maxsplit=1)[0] for line in before.decode().splitlines()}
    for path, expected in listed.items():
        need(digest(show(mmu['source_sha'],path)) == expected, 'MMU signed input differs: '+path)
    need(all(listed[p] == digest((ROOT/p).read_bytes()) for p in source['inputs']), 'MMU current329 input differs')
    need(listed['rust-toolchain.toml'] == digest((ROOT/'rust-toolchain.toml').read_bytes()), 'Product pin mutated')
    for phase in ['before','after']:
        locks = (directory/('target/u2-mmu-4608/locks-'+phase+'.sha256')).read_text().splitlines()
        need(len(locks) == 2 and all(digest((ROOT/line.split()[1]).read_bytes()) == line.split()[0] for line in locks), 'MMU locks differ')
    need(digest((ROOT/'fuzz/lsan.supp').read_bytes()) == mmu['suppression_sha256'], 'MMU suppression changed')
    binary_path = directory / 'fuzz/target/x86_64-unknown-linux-gnu/release/mmu_u2'
    need(digest(binary_path.read_bytes()) == mmu['binary_sha256'] and (directory/'target/u2-mmu-4608/binary.sha256').read_text().split()[0] == mmu['binary_sha256'], 'MMU binary differs')
    need(b'__asan_init' in binary_path.read_bytes(), 'MMU binary not ASan instrumented')
    settings = (directory/'target/u2-mmu-4608/settings.txt').read_text()
    need(all(value in settings.splitlines() for value in ['ASAN_OPTIONS=detect_leaks=1','LSAN_OPTIONS=suppressions=/work/fuzz/lsan.supp','seed=1','max_len=4608','max_total_time=600','timeout=30','rss_limit_mb=2048','sanitizer=address']), 'MMU ASan/LSan settings differ')
    signature = api(f'commits/{mmu["source_sha"]}')['commit']['verification']
    need(signature['verified'] is True and signature['reason'] == 'valid', 'MMU signature invalid')
    run = api(f'actions/runs/{mmu["ci_run"]}')
    need(run['head_sha'] == mmu['source_sha'] and run['status'] == 'completed' and run['conclusion'] == 'success', 'MMU CI incomplete')
    jobs = api(f'actions/runs/{mmu["ci_run"]}/jobs?per_page=100')['jobs']
    need(len(jobs) == 1 and jobs[0]['id'] == mmu['job_id'] and jobs[0]['conclusion'] == 'success', 'MMU owning job differs')
    artifacts = api(f'actions/runs/{mmu["ci_run"]}/artifacts?per_page=100')['artifacts']
    artifact = select_artifact(artifacts,'u2-mmu-4608',mmu['source_sha'],mmu['ci_run'],jobs[0],mmu['artifact_id'])
    need(artifact['digest'] == 'sha256:'+digest((directory/'u2-mmu-4608.zip').read_bytes()) == 'sha256:'+mmu['zip_sha256'], 'MMU artifact ZIP digest differs')
    delta = command(['jj','--ignore-working-copy','diff','--from',HEAD,'--to',mmu['source_sha'],'--name-only']).decode().splitlines()
    need(delta == ['.github/workflows/u2-mmu-4608-revalidation.yml'], 'Diagnostic source delta exceeds workflow')
    print('Verified finite current U2/U11 binding, preserving U10 full checks and old CI failure; no all-input or Unit completion claim.')


if __name__ == '__main__':
    try:
        validate_u10_baseline()
        validate_current_u10()
        validate_shared_and_mmu()
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as error:
        print(f'U2/U11 verification failed: {error}', file=sys.stderr)
        raise SystemExit(1)
