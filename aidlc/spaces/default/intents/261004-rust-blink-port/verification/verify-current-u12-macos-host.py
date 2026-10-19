"""U12 candidate. Formal execution requires human command approval.

Historical U11 checks remain unchanged and run against their exact signed
baseline. Fresh U12 evidence is checked separately; no old execution is reused.
"""
import hashlib
import importlib.util
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
V = RECORD / 'construction/u12-macos-host/code-generation/verification'
sys.path.insert(0, str(V))
from step10_bridge import BASE, historical_check, need, safe_path, source_binding, validate_snapshot
from step10_retry import artifact_binding, selected_jobs

HEAD = 'a275bd3d6f08bf48c1a58dead339240b5364af4c'
RUN = 38125760476
CI = V / 'step10-final-ci'
REPO = 'Marukome0743/paludarium'
GH = next(p for p in sorted(Path.home().glob('.local/share/mise/installs/gh/*/gh_*/bin/gh'), reverse=True) if p.is_file())
JJ = next(p for p in sorted(Path.home().glob('.local/share/mise/installs/jj/*/jj'), reverse=True) if p.is_file())
TARGETS = ['cpu_u2', 'mmu_u2', 'decode', 'load_elf', 'mmu_ops', 'syscall_args', 'vfs_paths', 'kernel_threads_u5', 'kernel_futex_u5', 'kernel_events_u6', 'kernel_sockets_u6']
CHAIN = [BASE, '643ac23369ec39d38ee7ae80b60721cb2e6eaabf', '0e76a1783d1247f52badb79eeb0f8d8abac416b3', '3cfd58233c898367d7b16608b205af9075eb8244', '010871f67a9362ecca3180f859db2daf42c0dce0', 'ddf7c742092d3a87ee08f6eafdc249c0e5b38ec9', HEAD]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text())


def api(path):
    return json.loads(subprocess.check_output([str(GH), 'api', 'repos/' + REPO + '/' + path], cwd=ROOT, timeout=60))


def signed(path, revision=HEAD):
    return subprocess.check_output([str(JJ), '--ignore-working-copy', 'file', 'show', '-r', revision, path], cwd=ROOT, timeout=60)


def bounded(row, time_key='wall_seconds'):
    duration = row.get(time_key)
    need(type(duration) in (int, float) and math.isfinite(duration) and 0 <= duration <= 30,
         'Invalid guest duration')
    need(type(row.get('exit')) is int and row['exit'] == 0 and row.get('timed_out') is False, 'Guest failure or timeout')


def sources():
    binding = load(RECORD / 'construction/u11-wasm-launcher/code-generation/verification/step21-dispose-results/signed-source-binding.json')
    baseline = {path: row['current_sha256'] for path, row in binding['inputs'].items()}
    manifest = load(V.parent / 'source-manifest.json')
    need(manifest['stage'] == 'code-generation' and manifest['unit'] == 'u12-macos-host' and manifest['version'] == 1, 'Manifest scope differs')
    changed = [row['path'] for row in manifest['writes']]
    need(len(baseline) == 329 and len(changed) == 24 and changed == sorted(changed), 'Source inventory differs')
    current = {}
    for path in sorted(set(baseline) | set(changed)):
        safe_path(path)
        local = ROOT / path
        need(local.is_file() and not local.is_symlink(), 'Missing/linked current input: ' + path)
        current[path] = sha(local.read_bytes())
        need(local.read_bytes() == signed(path), 'Current/signed bytes differ: ' + path)
    need(len(current) == 342, 'Current input population differs')
    source_binding(baseline, current, changed)
    for index, revision in enumerate(CHAIN[1:]):
        commit = api('commits/' + revision)
        verification = commit['commit']['verification']
        need(verification['verified'] is True and verification['reason'] == 'valid', 'Signature invalid')
        need([p['sha'] for p in commit['parents']] == [CHAIN[index]], 'Signed parent differs')
        need(len(commit['files']) == [10, 15, 2, 1, 1, 8][index], 'Signed delta count differs')
        need(set(f['filename'] for f in commit['files']) <= set(changed), 'Published file outside approved inventory')
    comparison = api('compare/' + BASE + '...' + HEAD)
    need(sorted(f['filename'] for f in comparison['files']) == changed, 'Cumulative signed delta differs')
    manifest = load(V / 'step10-signed-baseline-manifest.json')
    need(manifest['source_sha'] == BASE and len(manifest['rows']) == 399, 'Historical baseline manifest differs')
    validate_snapshot(V / 'step10-signed-baseline', {row['path']: row['sha256'] for row in manifest['rows']})
    historical_check(RECORD, V / 'step10-signed-baseline', ROOT)


def ci_originals():
    run = load(CI / 'run.json')
    live = api('actions/runs/' + str(RUN))
    need(run['id'] == live['id'] == RUN and run['head_sha'] == live['head_sha'] == HEAD
         and run['status'] == live['status'] == 'completed' and run['conclusion'] == live['conclusion'] == 'success'
         and run['run_attempt'] == live['run_attempt'] == 2, 'Final CI head/attempt/status differs')
    jobs = load(CI / 'jobs.json')['jobs']
    live_jobs = api('actions/runs/' + str(RUN) + '/jobs?per_page=100')['jobs']
    need(len(jobs) == len(live_jobs) == 29 and {j['id'] for j in jobs} == {j['id'] for j in live_jobs}, 'CI jobs differ')
    names = {'unit tests (' + p + ')' for p in ['ubuntu-latest', 'windows-latest', 'macos-latest']}
    names |= {'dependencies', 'lint', 'line coverage >= 80%', 'differential tests (x86-64 Linux)', 'production wasm (shared Rust heap, nested Workers)', 'macos-host', 'u12-oracle / native-first', 'u11-programs / build-oracle'}
    names |= {'u12-fuzz / fuzz (' + t + ')' for t in TARGETS}
    names |= {'u11-programs / differential (' + p + ', ' + e + ')' for p, e in [('ubuntu-latest', 'node'), ('ubuntu-latest', 'chromium'), ('ubuntu-latest', 'firefox'), ('macos-latest', 'safari')]}
    names |= {'U10 fixed guests and fresh native differential / ' + n for n in ['native-first', 'fixture-metadata-oracle', 'differential']}
    need({j['name'] for j in jobs} == names, 'Required CI job population differs')
    old = load(V / 'step10-failed-ci-attempt1/jobs.json')['jobs']
    live_old = api('actions/runs/' + str(RUN) + '/attempts/1/jobs?per_page=100')['jobs']
    need(len(live_old) == len(old) == 29 and {j['id'] for j in live_old} == {j['id'] for j in old}, 'Historical job provenance differs')
    for previous in old:
        actual = next(j for j in live_old if j['id'] == previous['id'])
        need(all(actual[field] == previous[field] for field in ('name', 'head_sha', 'run_id', 'run_attempt', 'started_at', 'completed_at', 'steps', 'status', 'conclusion')), 'Historical job execution differs')
    selected_jobs(old, jobs, names, HEAD, RUN, 2)
    origins = load(CI / 'log-origins.json')
    need(len(origins) == 29 and {o['job'] for o in origins} == {j['id'] for j in jobs}, 'Log provenance inventory differs')
    for job in jobs + live_jobs:
        need(job['head_sha'] == HEAD and job['run_id'] == RUN and job['run_attempt'] == 2
             and job['status'] == 'completed' and job['conclusion'] == 'success', 'Job failed or source differs')
        need((CI / ('job-' + str(job['id']) + '.log')).stat().st_size > 0, 'Job log missing')
        previous = next(j for j in old if j['name'] == job['name'])
        origin = next(o for o in origins if o['job'] == job['id'])
        need(origin['sha256'] == sha((CI / ('job-' + str(job['id']) + '.log')).read_bytes()), 'Log provenance hash differs')
        if previous['conclusion'] == 'success':
            need(origin['mode'] == 'carryover-identical-execution' and origin['original_job'] == previous['id']
                 and origin['started_at'] == job['started_at'] and origin['completed_at'] == job['completed_at']
                 and origin['steps_sha256'] == sha(json.dumps(job['steps'], sort_keys=True).encode()), 'Carryover origin differs')
            need((CI / ('job-' + str(job['id']) + '.log')).read_bytes() == (V / 'step10-failed-ci-attempt1' / ('job-' + str(previous['id']) + '.log')).read_bytes(), 'Carryover raw log differs')
            if origin['github_alias_sha256'] is not None:
                need(origin['github_alias_sha256'] == sha((CI / ('job-' + str(job['id']) + '.gh-alias.log')).read_bytes()), 'Preserved GitHub alias representation differs')
        else:
            need(origin['mode'] == 'new-execution' and origin['original_job'] == job['id'], 'Old failed log reused as fresh execution')
    artifacts = load(CI / 'artifacts.json')['artifacts']
    live_artifacts = api('actions/runs/' + str(RUN) + '/artifacts?per_page=100')['artifacts']
    selected = {}
    for artifact in live_artifacts:
        previous = selected.get(artifact['name'])
        if previous is None or artifact['id'] > previous['id']:
            selected[artifact['name']] = artifact
    need(len(artifacts) == len(selected) and {a['id'] for a in artifacts} == {a['id'] for a in selected.values()}, 'Artifact inventory changed')
    old_artifacts = load(V / 'step10-failed-ci-attempt1/artifacts.json')['artifacts']
    artifact_binding(old_artifacts, artifacts, jobs)
    for artifact in artifacts:
        current = next(a for a in live_artifacts if a['id'] == artifact['id'])
        archive = CI / (artifact['name'] + '.zip')
        need(current['expired'] is False and artifact['workflow_run']['head_sha'] == HEAD
             and artifact['workflow_run']['id'] == RUN
             and artifact['digest'] == current['digest'] == 'sha256:' + sha(archive.read_bytes()), 'Archive provenance differs')
        folder = CI / artifact['name']
        with zipfile.ZipFile(archive) as bundle:
            paths = [item.filename for item in bundle.infolist() if not item.is_dir()]
            need(len(paths) == len(set(paths)), 'Duplicate archive paths')
            need({str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()} == set(paths), 'Extracted inventory differs')
            for path in paths:
                need((folder / path).read_bytes() == bundle.read(path), 'Extracted bytes differ')


def main():
    print('Checking 342 signed current inputs and unchanged historical predicates.', flush=True)
    sources()
    print('Signed inputs/historical checks passed; checking retry provenance and immutable CI artifacts.', flush=True)
    ci_originals()
    print('CI provenance/artifacts passed; checking macOS, coverage, wasm environments and sanitizer observations.', flush=True)
    spec = importlib.util.spec_from_file_location('u12_current_validation', V / 'step10_current_validation.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    validator.validate(CI, ROOT, HEAD, signed)
    print('Verified finite U12: 342 signed inputs, complete fresh CI, macOS Host and original arguments, four wasm environments, fixed coverage scopes and eleven fresh ASan/LSan observations. No arbitrary-input or session-ID assurance.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print('U12 verification failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
