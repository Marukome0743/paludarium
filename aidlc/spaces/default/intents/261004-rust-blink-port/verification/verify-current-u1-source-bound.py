"""Preserve historical U12 checks and require independent current U1 CI.

Formal invocation requires the person's verification-command approval.
The completed U13 workflow is deliberately not a prerequisite or a claim.
"""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / 'construction/u1-skeleton/code-generation/verification'
U13 = RECORD / 'construction/u13-windows-host/code-generation/verification'
sys.path.insert(0, str(V))
from source_bound_validation import PACKAGES, TESTS, attempt_jobs, current_binding, hello, inventory, need, observation, sha
from historical_js_workspace import historical_workspace

HEAD = 'e2d3f316206974ef098fd9bdc85d94a8376a51f8'
RUN = 38171135965
PARENT = '17231f7a0cdfe9da8659497d963979690db1c2b3'
REPO = 'Marukome0743/paludarium'
GH = next(Path.home().glob('.local/share/mise/installs/gh/*/gh_*/bin/gh'))
JJ = next(Path.home().glob('.local/share/mise/installs/jj/*/jj'))
JOBS = {'unit tests (' + name + ')' for name in ('ubuntu-latest', 'macos-latest', 'windows-latest')}
JOBS |= {'lint', 'dependencies', 'differential tests (x86-64 Linux)', 'line coverage >= 80%'}


def load(path):
    return json.loads(path.read_text())


def api(path):
    return json.loads(subprocess.check_output([str(GH), 'api', 'repos/' + REPO + '/' + path], cwd=ROOT, timeout=60))


def signed(path, revision=HEAD):
    return subprocess.check_output([str(JJ), '--ignore-working-copy', 'file', 'show', '-r', revision, path], cwd=ROOT, timeout=60)


def historical():
    manifest = load(U13 / 'step7-u12-signed-baseline-manifest.json')
    path = U13 / 'step7_bridge.py'
    need(sha(path.read_bytes()) == 'af4a237b05b53eca67f5b84ac38ae5304bbc9639eccf6235c767eaeb40945a4e', 'historical bridge modified')
    need(sha((U13 / 'step7-u12-signed-baseline-manifest.json').read_bytes()) == 'fd071e87ed15fedeca1ccba5be5f84e79ebbf971a5d3b6368383bbec3fcbb4db', 'historical manifest modified')
    spec = importlib.util.spec_from_file_location('preserved_u12_source_view', path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    bridge.validate_snapshot(U13 / 'step7-u12-signed-baseline', manifest)
    binding_path = RECORD / 'construction/u12-macos-host/code-generation/verification/step10-js-results/binding.json'
    binding = load(binding_path)
    need(binding['source_sha'] == bridge.BASE and binding['inputs_before'] == binding['inputs_after'],
         'historical JS input binding differs')
    rows = [{'path': path, 'sha256': value} for path, value in binding['inputs_before'].items()]
    with historical_workspace(U13 / 'step7-u12-signed-baseline', rows):
        bridge.historical_check(RECORD, U13 / 'step7-u12-signed-baseline', ROOT,
                                '352022ad96ccf421fdb8df3d98f551bed38ddb02635154bb3b1f55ced073ae46')


def current_sources():
    need(sha((V / 'current-source-bound-inputs.json').read_bytes()) == '7dae384ee72751b5ab682b30213100064dc57a9138f9432e01f5befb8f620052', 'current input binding modified')
    binding = load(V / 'current-source-bound-inputs.json')
    need(binding['head'] == HEAD and len(binding['rows']) == 362, 'signed input binding differs')
    expected = inventory(binding['rows'])
    local, committed = {}, {}
    for path in expected:
        file = ROOT / path
        need(file.is_file() and not file.is_symlink(), 'missing/linked current input')
        local[path], committed[path] = sha(file.read_bytes()), sha(signed(path))
    current_binding(local, committed, expected)
    rust_sources = {str(p.relative_to(ROOT)) for p in (ROOT / 'crates').rglob('*.rs')
                    if 'target' not in p.relative_to(ROOT).parts}
    need(rust_sources <= set(expected), 'unbound current Rust source added')
    commit = api('commits/' + HEAD)
    need(commit['commit']['verification']['verified'] is True
         and commit['commit']['verification']['reason'] == 'valid', 'signature invalid')
    need([p['sha'] for p in commit['parents']] == [PARENT], 'signed parent differs')
    need([f['filename'] for f in commit['files']] == [
        '.github/workflows/u1-source-bound-verification.yml'], 'publication scope differs')
    previous = api('commits/' + PARENT)
    need(previous['commit']['verification']['verified'] is True
         and [p['sha'] for p in previous['parents']] == ['3817231637d289f670884f0df50ea98caf56c287']
         and [f['filename'] for f in previous['files']] == ['.github/workflows/u1-source-bound-verification.yml'], 'previous signature/scope differs')
    initial = api('commits/3817231637d289f670884f0df50ea98caf56c287')
    need(initial['commit']['verification']['verified'] is True
         and [p['sha'] for p in initial['parents']] == ['fc44cece63f118fb9b39ca2bec4b569594a8f2fb']
         and sorted(f['filename'] for f in initial['files']) == [
             '.github/workflows/u1-source-bound-verification.yml', '.github/workflows/u13-quality.yml',
             'crates/paludarium-harness/tests/support/u13.rs'], 'initial signature/scope differs')
    return expected


def originals():
    folder = V / 'current-u1-ci'
    frozen = V / 'current-u1-originals-manifest.json'
    need(sha(frozen.read_bytes()) == '21b31f4fd5eae74ab99dbc1b7cc81bc7a7409bbb620d78be6c5dff3041c9a0fe', 'reviewed original inventory modified')
    frozen_rows = inventory(load(frozen)['rows'])
    actual_originals = {'current-u1-ci/' + p.name for p in folder.iterdir() if p.is_file()}
    need(set(frozen_rows) == actual_originals | {'current-u1-observation-binding.json'}, 'original inventory differs')
    need(all(not (V / p).is_symlink() and sha((V / p).read_bytes()) == digest for p, digest in frozen_rows.items()), 'original bytes modified')
    saved = load(folder / 'run.json')
    actual = api('actions/runs/' + str(RUN))
    need(saved == actual and actual['id'] == RUN and actual['head_sha'] == HEAD
         and actual['conclusion'] == 'success', 'CI run failed/differs')
    all_jobs = load(folder / 'jobs.json')['jobs']
    live = api('actions/runs/' + str(RUN) + '/jobs?per_page=100&filter=all')['jobs']
    need(all_jobs == live and len(all_jobs) == 14, 'attempt job inventory differs')
    jobs = attempt_jobs(all_jobs, HEAD, RUN, JOBS)
    chosen = {j['name']:j for j in jobs}
    need(len(jobs) == 7 and set(chosen) == JOBS, 'required jobs differ')
    need(actual['run_attempt'] == 2 and all(j['run_attempt'] == 2 for j in jobs), 'attempt binding differs')
    failed = [j for j in all_jobs if j['conclusion'] == 'failure']
    need(len(failed) == 1 and failed[0]['name'] == 'line coverage >= 80%' and failed[0]['run_attempt'] == 1
         and failed[0]['id'] == 114563806344 and failed[0]['head_sha'] == HEAD and failed[0]['conclusion'] == 'failure', 'original coverage failure not retained')
    need(all(j['head_sha'] == HEAD and j['conclusion'] == 'success'
             and all(s['conclusion'] == 'success' for s in j['steps'] if s['name'] not in ('Post Run actions/checkout', 'Complete job'))
             for j in jobs), 'failed/skipped required step')
    files = {}
    artifacts = load(folder / 'artifacts.json')['artifacts']
    live_artifacts = api('actions/runs/' + str(RUN) + '/artifacts?per_page=100')['artifacts']
    need({a['id'] for a in artifacts} == {a['id'] for a in live_artifacts}, 'artifact inventory differs')
    need(len(artifacts) == 12, 'original artifact population differs')
    latest = {}
    for artifact in sorted(artifacts, key=lambda a:(a['created_at'],a['id'])):
        latest[artifact['name']] = artifact
    artifact_jobs = {
        'u1-source-bound-inputs-test-Linux':'unit tests (ubuntu-latest)',
        'u1-source-bound-inputs-test-macOS':'unit tests (macos-latest)',
        'u1-source-bound-inputs-test-Windows':'unit tests (windows-latest)',
        'u1-source-bound-inputs-lint-Linux':'lint',
        'u1-source-bound-inputs-dependencies-Linux':'dependencies',
        'u1-source-bound-inputs-differential-Linux':'differential tests (x86-64 Linux)',
        'u3-differential-observations':'differential tests (x86-64 Linux)',
        'u1-hello-exit-receipts':'differential tests (x86-64 Linux)',
        'u1-source-bound-inputs-coverage-Linux':'line coverage >= 80%',
        'u1-source-bound-coverage':'line coverage >= 80%'}
    need(set(latest) == set(artifact_jobs), 'artifact job population differs')
    for artifact in artifacts:
        raw = (folder / (str(artifact['id']) + '.zip')).read_bytes()
        live_artifact = next(a for a in live_artifacts if a['id'] == artifact['id'])
        need(artifact['digest'] == 'sha256:' + sha(raw)
             and live_artifact['digest'] == artifact['digest'] and live_artifact['expired'] is False
             and artifact['workflow_run']['head_sha'] == HEAD, 'artifact digest/head differs')
        with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
            names = [r.filename for r in bundle.infolist() if not r.is_dir()]
            need(len(names) == len(set(names)) and all(not p.startswith('/') and '..' not in Path(p).parts for p in names), 'duplicate/unsafe archive path')
            content = {name: bundle.read(name) for name in names}
            extracted = V / 'current-u1-ci-artifacts' / artifact['name']
            if artifact == latest[artifact['name']]:
                files[artifact['name']] = content
                need(sorted(str(p.relative_to(extracted)) for p in extracted.rglob('*') if p.is_file()) == sorted(names), 'extracted artifact inventory differs')
                need(all(not (extracted / p).is_symlink() and (extracted / p).read_bytes() == content[p] for p in names), 'extracted artifact bytes differ')
                issuing_job = chosen[artifact_jobs[artifact['name']]]
                need(issuing_job['started_at'] <= artifact['created_at'] <= issuing_job['completed_at'], 'artifact belongs to a different execution attempt')
    return jobs, files


def seconds(value):
    match = re.fullmatch(r'(\d+(?:\.\d+)?)(s|ms|µs|ns)', value)
    need(match is not None, 'unknown Rust Duration representation')
    return float(match[1]) * {'s': 1, 'ms': .001, 'µs': .000001, 'ns': .000000001}[match[2]]


def executions(jobs, files, expected):
    names = {'u1-source-bound-inputs-' + job + '-' + platform for job, platform in
             [('test', 'Linux'), ('test', 'macOS'), ('test', 'Windows'),
              ('lint', 'Linux'), ('dependencies', 'Linux'), ('differential', 'Linux'), ('coverage', 'Linux')]}
    need(set(files) == names | {'u1-source-bound-coverage', 'u3-differential-observations', 'u1-hello-exit-receipts'}, 'execution receipt population differs')
    compilers = {}
    for name in names:
        receipt = json.loads(files[name]['inputs.json'])
        need(receipt['head'] == HEAD, 'execution source head differs')
        rows = inventory(receipt['rows'])
        need(all(rows.get(p) == value for p, value in expected.items()), 'execution inputs differ')
        compiler = files[name]['compiler.txt'].decode()
        need('rustc 1.101.0-nightly' in compiler and 'commit-date: 2026-10-10' in compiler,
             'actual compiler differs')
        compilers[name] = compiler
    need(compilers['u1-source-bound-inputs-coverage-Linux'] == compilers['u1-source-bound-inputs-differential-Linux'],
         'differential/coverage compiler mismatch')
    job = next(j for j in jobs if j['name'] == 'differential tests (x86-64 Linux)')
    raw = (V / 'current-u1-ci' / ('job-' + str(job['id']) + '.log')).read_text()
    clean = re.sub(r'\x1b\[[0-9;]*m', '', raw)
    need('--test diff_u1' in clean and '16 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out' in clean,
         'differential command/count differs')
    tests = re.findall(r'test (hello_c|hello_rs|hello_rs_with_arguments|insn_[a-z_]+) \.\.\. ok', clean)
    need(len(tests) == 16 and set(tests) == TESTS, 'differential actual tests differ')
    timing = re.findall(r'timing ([^:]+): native ([^, ]+), emulated ([^\s\x1b]+)', clean)
    timing = [r for r in timing if r[0] in {'hello-c', 'hello-rs', 'hello-rs-args'} or r[0].startswith('insn-')]
    need(len(timing) == 16 and len({r[0] for r in timing}) == 16, 'timing population differs')
    # Successful differential tests establish equal status, not a particular status.
    timings = [{'seconds': seconds(value), 'timed_out': False}
               for _, native, emulator in timing for value in (native, emulator)]
    bundle = files['u1-source-bound-coverage']
    package_path = next(p for p in bundle if p.endswith('u1-package-coverage.json'))
    workspace_path = next(p for p in bundle if p.endswith('u1-workspace-coverage.json'))
    report = json.loads(bundle[package_path])
    workspace = json.loads(bundle[workspace_path])
    for output in (report, workspace):
        total = output['data'][0]['totals']['lines']
        need(total['count'] > 0 and total['covered'] / total['count'] >= .8, 'coverage floor failed')
    paths = sorted(row['filename'].split('/crates/', 1)[1]
                   for row in report['data'][0]['files'] if '/crates/' in row['filename'])
    need(paths and len(paths) == len(set(paths)) and not any(p.startswith('paludarium-harness/') for p in paths),
         'coverage duplicate/excluded package differs')
    represented = {p.split('/', 1)[0].removeprefix('paludarium-') for p in paths}
    need(represented == set(PACKAGES), 'fixed eleven-package scope differs')
    # Verify every reported production input against the independently signed source map.
    need(all('crates/' + p in expected for p in paths), 'unbound measured source')
    guests = {p: sha(bundle[p]) for p in ('guests/hello-c', 'guests/hello-rs') if p in bundle}
    need(len(guests) == 2, 'fresh hello binaries missing')
    actual = files['u1-hello-exit-receipts']
    receipt = json.loads(actual['receipt.json'])
    need(receipt['schemaVersion'] == 1 and receipt['head'] == HEAD
         and receipt['compiler'] == compilers['u1-source-bound-inputs-differential-Linux'], 'hello provenance differs')
    rows = receipt['rows']
    hello(rows)
    need(set(actual) == {'receipt.json', 'paludarium', 'hello-c', 'hello-rs'} |
         {name + '-' + mode + '.' + stream for name in ('hello-c', 'hello-rs', 'hello-rs-args')
          for mode in ('native', 'emulated') for stream in ('stdout', 'stderr')}, 'hello raw inventory differs')
    for row in rows:
        binary = 'hello-c' if row['name'] == 'hello-c' else 'hello-rs'
        need(row['argv0'] == binary and row['arguments'] == (['--flag', 'two words'] if row['name'] == 'hello-rs-args' else [])
             and row['guest_sha256'] == sha(actual[binary]) == guests['guests/' + binary]
             and row['cli_sha256'] == sha(actual['paludarium']), 'hello binary/argv binding differs')
        for stream in ('stdout', 'stderr'):
            raw_name = row['name'] + '-' + row['mode'] + '.' + stream
            need(row[stream + '_sha256'] == sha(actual[raw_name]), 'hello raw output digest differs')
    for name in ('hello-c', 'hello-rs', 'hello-rs-args'):
        need(all(actual[name + '-native.' + stream] == actual[name + '-emulated.' + stream]
                 for stream in ('stdout', 'stderr')), 'hello raw output mismatch')
    total = report['data'][0]['totals']['lines']
    obs = {'origin': 'current-u1-execution', 'signature_verified': True, 'head': HEAD,
           'compiler': compilers['u1-source-bound-inputs-coverage-Linux'], 'guests': guests,
           'artifact_digest': sha(b'\n'.join(bundle[p] for p in sorted(bundle))),
           'jobs': jobs, 'tests': tests, 'timings': timings, 'hello': rows,
           'differential_status_claim': 'equal only; no exit code inferred from timing', 'coverage_paths': paths,
           'coverage_packages': sorted(represented), 'lines': total['count'], 'covered': total['covered']}
    return obs


def main():
    print('Checking immutable historical U12 predicates; this is historical evidence.', flush=True)
    historical()
    print('Checking independently signed current U1 inputs and seven required CI jobs.', flush=True)
    expected = current_sources()
    jobs, files = originals()
    observed = executions(jobs, files, expected)
    evidence = load(V / 'current-u1-observation-binding.json')
    need(observed == evidence['observed'], 'derived observation differs from reviewed binding')
    observation(observed, evidence['expected'])
    print('Verified current finite U1 and preserved historical U12. U13 full validation and session-ID assurance remain unverified.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print('U1 source-bound verification failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
