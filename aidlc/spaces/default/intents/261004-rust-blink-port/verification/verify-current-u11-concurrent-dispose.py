"""Preserve historical checks and bind the approved two-file U11 fix to current CI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
import zipfile

RECORD = Path(__file__).resolve().parent.parent
ROOT = RECORD.parents[4]
V = RECORD / 'construction/u11-wasm-launcher/code-generation/verification'
HEAD = 'a19bea3549a77a0f665b20626d65049ecc6e2f6a'
BASE = '2b3874eabda6fe6f1d1334202421db733445fd21'
RUN = 38118128088
REPO = 'Marukome0743/paludarium'
OLD_SHA = 'd46d14b8ac6ce0475b27bf529394f41c4b57bcac674b45299cdecaeb9f623ec4'
CASES = ['probe-tokio-timer', 'probe-unix-stream-pair', 'probe-rayon', 'probe-mutex-condvar',
         'probe-fs-basic', 'probe-fs-hardlink', 'probe-fs-symlink', 'probe-fs-flock',
         'probe-all', 'probe-environment', 'version', 'install', 'frozen', 'list']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/' + path], timeout=60))


def signed(path, revision):
    return subprocess.check_output(['jj', '--ignore-working-copy', 'file', 'show', '-r', revision, path], cwd=ROOT, timeout=30)


def scm_at_repository(old, original):
    def wrapped(*args, **kwargs):
        snapshot_root = old.ROOT
        try:
            old.ROOT = ROOT
            return original(*args, **kwargs)
        finally:
            old.ROOT = snapshot_root
    return wrapped


def check_sources(predicates):
    baseline = load(V / 'source-hashes.json')
    binding = load(V / 'step21-dispose-results/signed-source-binding.json')
    need(baseline['source_sha'] == BASE and binding['source_sha'] == HEAD, 'Source heads differ')
    historical = baseline['inputs']
    current = {path: row['current_sha256'] for path, row in binding['inputs'].items()}
    predicates.validate_bridge(historical, current)
    snapshot = V / 'step22-historical-source'
    expected = {**historical, **baseline['ci_record_helpers']}
    manifest = load(V / 'step22-historical-source-manifest.json')
    claims = load(RECORD / 'construction/u2-integer-isa/code-generation/source-manifest.json')['writes']
    for row in claims:
        if row['path'] not in expected:
            expected[row['path']] = sha(signed(row['path'], BASE))
    need(manifest['source_sha'] == BASE and manifest['checker_sha256'] == OLD_SHA,
         'Historical snapshot binding differs')
    need(len(manifest['rows']) == len(expected)
         and {row['path']: row['sha256'] for row in manifest['rows']} == expected,
         'Historical snapshot manifest differs')
    need({str(path.relative_to(snapshot)) for path in snapshot.rglob('*') if path.is_file()} == set(expected),
         'Historical snapshot inventory differs')
    need(not snapshot.is_symlink() and not any(path.is_symlink() for path in snapshot.rglob('*')), 'Historical symlink not permitted')
    for path, digest in expected.items():
        saved = snapshot / path
        need(not saved.is_symlink() and sha(saved.read_bytes()) == digest == sha(signed(path, BASE)),
             'Historical signed source differs: ' + path)
    for path, digest in current.items():
        need(sha((ROOT / path).read_bytes()) == digest == sha(signed(path, HEAD)),
             'Current signed source differs: ' + path)
    for path, digest in baseline['ci_record_helpers'].items():
        need(sha((ROOT / path).read_bytes()) == digest == sha(signed(path, HEAD)), 'CI helper changed')
    commit = api('commits/' + HEAD)
    need(commit['commit']['verification']['verified'] is True
         and commit['commit']['verification']['reason'] == 'valid', 'Current signature invalid')
    need([row['filename'] for row in commit['files']] == predicates.CHANGED
         and [row['sha'] for row in commit['parents']] == [BASE], 'Current commit exceeds two files')
    return snapshot


def check_ci(predicates):
    directory = V / 'step21-dispose-ci-attempt2'
    run = load(directory / 'run.json')
    live = api(f'actions/runs/{RUN}')
    need(run['id'] == live['id'] == RUN and run['head_sha'] == live['head_sha'] == HEAD
         and run['status'] == live['status'] == 'completed'
         and run['conclusion'] == live['conclusion'] == 'success'
         and run['run_attempt'] == live['run_attempt'] == 2, 'Current CI attempt incomplete')
    jobs = load(directory / 'jobs.json')['jobs']
    need(len(jobs) == 5 and all(row['status'] == 'completed' and row['conclusion'] == 'success' for row in jobs),
         'CI jobs incomplete')
    oldjobs = load(V / 'step21-dispose-ci-attempt1-failed/jobs.json')['jobs']
    need(load(V / 'step21-dispose-ci-attempt1-failed/run.json')['conclusion'] == 'failure', 'Old failure lost')
    names = ['producer', *['consumer (' + platform + ', ' + environment + ')' for platform, environment in
             [('ubuntu-latest', 'node'), ('ubuntu-latest', 'chromium'), ('ubuntu-latest', 'firefox'), ('macos-latest', 'safari')]]]
    need(sorted(row['name'] for row in jobs) == sorted(names), 'CI job population differs')
    for job in jobs:
        need(job['head_sha'] == HEAD and job['run_id'] == RUN and job['run_attempt'] == 2, 'Job head/attempt differs')
        if job['name'] != names[-1]:
            old = next(row for row in oldjobs if row['name'] == job['name'])
            need(old['conclusion'] == 'success' and (old['started_at'], old['completed_at']) ==
                 (job['started_at'], job['completed_at']), 'Carried success job provenance differs')
        else:
            need(job['id'] == 114410379632 and job['started_at'] > '2026-10-11T06:48:00Z', 'Safari retry differs')
        need((directory / ('job-' + str(job['id']) + '.log')).is_file(), 'Job raw log missing')
    artifacts = load(directory / 'artifacts.json')['artifacts']
    need(sorted(row['name'] for row in artifacts) == sorted(['u11-current-inputs', *['u11-current-' + e for e in predicates.ENVIRONMENTS]]),
         'Artifact population differs')
    live_artifacts = api(f'actions/runs/{RUN}/artifacts?per_page=100')['artifacts']
    for artifact in artifacts:
        current = next(row for row in live_artifacts if row['id'] == artifact['id'])
        archive = directory / (artifact['name'] + '.zip')
        need(not current['expired'] and artifact['workflow_run']['head_sha'] == HEAD
             and artifact['workflow_run']['id'] == RUN and artifact['digest'] == current['digest'] == 'sha256:' + sha(archive.read_bytes()),
             'Artifact original differs')
        folder = directory / ('inputs' if artifact['name'] == 'u11-current-inputs' else artifact['name'].removeprefix('u11-current-'))
        with zipfile.ZipFile(archive) as bundle:
            for path in folder.rglob('*'):
                if path.is_file():
                    need(path.read_bytes() == bundle.read(str(path.relative_to(folder))), 'Extracted original differs')
    inputs = directory / 'inputs'
    oracle_path = inputs / 'target/u11/native/observations.json'
    oracle = load(oracle_path)
    need(list(oracle['rows']) == CASES, 'Fresh native case inventory differs')
    programs = ROOT / 'packages/paludarium-wasm/tests/u11-programs.mjs'
    node = next(path for path in sorted(Path.home().glob('.local/share/mise/installs/node/*/bin/node'), reverse=True) if path.is_file())
    sequence = json.loads(subprocess.check_output([str(node), '--input-type=module', '-e',
        'import {probeCases} from ' + json.dumps(programs.as_uri()) + '; console.log(JSON.stringify(probeCases().map(row=>row.name)));'], timeout=30))
    need(sequence + [row['name'] for row in oracle['case_config']['aube']] == CASES, 'Signed runner execution array differs')
    for row in oracle['rows'].values():
        need(type(row['exit']) is int and row['exit'] == 0 and row['timed_out'] is False
             and type(row['wall_seconds']) in (int, float), 'Native case failed')
        predicates.validate_row({'seconds': row['wall_seconds'], 'exit': row['exit'], 'pass': True, 'timed_out': row['timed_out']})
    module_sha = sha((inputs / 'packages/paludarium-wasm/paludarium.wasm').read_bytes())
    guests = {name: sha((inputs / ('target/guests/u10/' + name)).read_bytes()) for name in ['probe', 'aube']}
    need(guests == oracle['binary_hashes'], 'Fresh native guest hashes differ')
    receipt = load(inputs / 'target/u11/native/u11-oracle-receipt.json')
    need(receipt['native_oracle_sha256'] == sha(oracle_path.read_bytes()), 'Native receipt differs')
    for path, digest in receipt['production_source_sha256'].items():
        need(sha((ROOT / path).read_bytes()) == digest, 'Native producer source differs')
    reports = {environment: load(directory / environment / environment / 'observations.json') for environment in predicates.ENVIRONMENTS}
    predicates.validate_environments(reports, CASES, module_sha, sha(oracle_path.read_bytes()), guests)
    for environment in predicates.ENVIRONMENTS:
        result = load(directory / environment / environment / 'suite-supervisor.json')
        need(type(result['exit']) is int and result['exit'] == 0 and result['timed_out'] is False and result['process_group_cleaned'] is True
             and type(result['seconds']) in (int, float) and 0 <= result['seconds'] <= 600, 'Suite cleanup/deadline failed')
    nodejob = next(row for row in jobs if row['name'] == names[1])
    api_results = []
    for line in (directory / ('job-' + str(nodejob['id']) + '.log')).read_text().splitlines():
        if ' {"exit":' in line:
            try:
                row = json.loads(line[line.index('{'):])
                if row.get('stdout') == predicates.API_PASS:
                    api_results.append(row)
            except json.JSONDecodeError:
                pass
    need(len(api_results) == 1, 'C12 raw result missing/duplicate')
    predicates.validate_c12(api_results[0])
    coverage = load(directory / 'node/node/js-coverage.json')
    previous = load(V / 'step21-dispose-results/js-coverage.json')
    predicates.validate_coverage(coverage, {row['path']: row['lines'] for row in previous['files']})
    print('Verified current two-file U11 CI bridge: four environments x14, C12, complete JS coverage; attempt1 failure retained.')


def main():
    checker_path = RECORD / 'verification/verify-current-u2-u11-revalidated.py'
    need(sha(checker_path.read_bytes()) == OLD_SHA, 'Preserved checker changed')
    predicates = module('u11_dispose_validation', V / 'step22_dispose_validation.py')
    snapshot = check_sources(predicates)
    old = module('u11_preserved_checker', checker_path)
    old.validate_u10_baseline()
    old.validate_current_u10()
    prior_root = old.ROOT
    prior_show, prior_command = old.show, old.command
    try:
        old.show = scm_at_repository(old, prior_show)
        old.command = scm_at_repository(old, prior_command)
        old.ROOT = snapshot
        old.validate_shared_and_mmu()
    finally:
        old.ROOT = prior_root
        old.show, old.command = prior_show, prior_command
    print('Preserved historical checks against exact signed baseline snapshot; no fresh-current execution claim.')
    check_ci(predicates)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print('U11 concurrent disposal verification failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
