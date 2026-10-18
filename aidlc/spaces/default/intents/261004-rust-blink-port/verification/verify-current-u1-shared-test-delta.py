"""Candidate: preserve historical predicates; separately verify bounded current U1.

Current coverage failure and unresolved U14 guest audit are explicit limits.
This is not a claim that the latest full CI or U14 is complete.
"""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tomllib

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
OWN = RECORD / 'verification/u1-shared-delta'
BINDING_SHA = 'b6bd0df97b66b0800842de0cb4e5741f211aee7e1cfbd5fe87ea350d6fe48122'
BASE = '62611f2556c4caf1470a7eb4471269d92611db6e'
CURRENT_HEAD = '9b5e6215e180e6602fdbde6b416281aebea9d110'
PROJECT = {
    '.github/workflows/u14-quality.yml', 'Cargo.lock',
    'crates/paludarium-harness/Cargo.toml',
    'crates/paludarium-jit/src/block.rs', 'crates/paludarium-runtime/src/tests.rs',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root, name):
    need(type(name) is str and name and not Path(name).is_absolute()
         and '\\' not in name and all(p not in ('', '.', '..') for p in name.split('/')),
         'unsafe input path')
    path = root / name
    need(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)),
         'missing/linked input: ' + name)
    return path.read_bytes()


def signed(name):
    return subprocess.check_output(
        ['jj', '--ignore-working-copy', 'file', 'show', '-r', BASE, name],
        cwd=ROOT, timeout=60)


def current_evidence(binding):
    for name, digest in binding['evidence_pins'].items():
        need(sha(regular(OWN, name)) == digest, 'current evidence changed: ' + name)
    run = json.loads(regular(OWN, 'source-bound-run.json'))
    need(run['headSha'] == CURRENT_HEAD and run['status'] == 'completed'
         and run['conclusion'] == 'failure', 'current overall CI failure must remain explicit')
    jobs = {row['name']: row for row in run['jobs']}
    mandatory = ('unit tests (ubuntu-latest)', 'unit tests (macos-latest)',
                 'unit tests (windows-latest)', 'lint', 'dependencies',
                 'differential tests (x86-64 Linux)')
    for name in mandatory:
        need(jobs[name]['status'] == 'completed' and jobs[name]['conclusion'] == 'success',
             'current required bounded job failed: ' + name)
    coverage = jobs['line coverage >= 80%']
    need(coverage['databaseId'] == 116147613935 and coverage['conclusion'] == 'failure'
         and any(s['name'] == 'Workspace line coverage >= 80%' and s['conclusion'] == 'failure'
                 for s in coverage['steps']), 'current coverage failure was removed')
    log = regular(OWN, 'current-coverage-failure.log').decode()
    need('Os { code: 2, kind: NotFound' in log
         and 'packed_and_crypto_native_replay' in log
         and 'packed_crypto_movement_fault_replay' in log, 'coverage failure original differs')
    inputs = json.loads(regular(OWN, 'linux-inputs/inputs.json'))
    need(inputs['head'] == CURRENT_HEAD, 'fresh Linux source head differs')
    rows = inputs['rows']
    need(len({r['path'] for r in rows}) == len(rows), 'duplicate Linux input')
    return {r['path']: r['sha256'] for r in rows}, mandatory


def classify(binding, baseline):
    signed_bytes = {name: signed(name) for name in PROJECT}
    current = {name: regular(ROOT, name) for name in binding['source_pins']}
    for name, digest in binding['source_pins'].items():
        need(sha(current[name]) == digest, 'approved delta/new entry changed: ' + name)
    old_lock = tomllib.loads(signed_bytes['Cargo.lock'].decode())
    new_lock = tomllib.loads(current['Cargo.lock'].decode())
    expected_lock = json.loads(json.dumps(old_lock))
    harness = [p for p in expected_lock['package'] if p['name'] == 'paludarium-harness']
    need(len(harness) == 1 and 'paludarium-jit' not in harness[0]['dependencies'],
         'unexpected old harness dependency')
    harness[0]['dependencies'] = sorted(harness[0]['dependencies'] + ['paludarium-jit'])
    need(new_lock == expected_lock, 'root lock changes more than harness dev dependency')
    old_manifest = tomllib.loads(signed_bytes['crates/paludarium-harness/Cargo.toml'].decode())
    new_manifest = tomllib.loads(current['crates/paludarium-harness/Cargo.toml'].decode())
    old_manifest['dev-dependencies']['paludarium-jit'] = {'workspace': True}
    need(new_manifest == old_manifest, 'harness changes exceed one dev dependency')
    block = 'crates/paludarium-jit/src/block.rs'
    need(current[block].split(b'#[cfg(test)]', 1)[0] == signed_bytes[block].split(b'#[cfg(test)]', 1)[0],
         'JIT product section changed')
    start = current[block].index(b'\n    #[test]\n    fn u14_block_saved_jit_compile_crash_')
    need(current[block][:start] + b'}\n' == signed_bytes[block], 'JIT changes exceed appended test')
    tests = 'crates/paludarium-runtime/src/tests.rs'
    start = current[tests].index(b'#[test]\nfn u14_runtime_cache_fallback_')
    end = current[tests].index(b'#[test]\nfn guest_exceptions_become_signals', start)
    need(current[tests][:start] + current[tests][end:] == signed_bytes[tests],
         'Runtime changes exceed two added tests')
    workflow = '.github/workflows/u14-quality.yml'
    old = b'--test diff_u8 -- --nocapture'
    new = b'--test diff_u8 --test diff_u14 -- --nocapture'
    need(signed_bytes[workflow].count(old) == 1
         and current[workflow] == signed_bytes[workflow].replace(old, new),
         'workflow delta exceeds approved differential entry')
    for name, raw in signed_bytes.items():
        need(sha(raw) == baseline['quality_inputs'][name], 'signed baseline mismatch: ' + name)
    return signed_bytes, current


def hello():
    receipt = json.loads(regular(OWN, 'native-hello/receipt.json'))
    need(receipt['head'] == CURRENT_HEAD and 'x86_64-unknown-linux-gnu' in receipt['compiler'],
         'fresh hello platform/head differs')
    expected = [(name, mode) for name in ('hello-c', 'hello-rs', 'hello-rs-args')
                for mode in ('native', 'emulated')]
    need([(r['name'], r['mode']) for r in receipt['rows']] == expected, 'hello row inventory differs')
    cli = regular(OWN, 'native-hello/paludarium')
    for row in receipt['rows']:
        need(row['returncode'] == 0 and type(row['returncode']) is int
             and row['signal'] is None and row['timed_out'] is False
             and type(row['seconds']) in (int, float) and math.isfinite(row['seconds'])
             and 0 <= row['seconds'] <= 30, 'hello failure/deadline')
        args = ['--flag', 'two words'] if row['name'] == 'hello-rs-args' else []
        need(row['arguments'] == args and row['argv0'] == ('hello-c' if row['name'] == 'hello-c' else 'hello-rs'),
             'hello argv differs')
        guest = regular(OWN, 'native-hello/' + row['argv0'])
        need(sha(guest) == row['guest_sha256'] and sha(cli) == row['cli_sha256'], 'hello binary differs')
        for stream in ('stdout', 'stderr'):
            output = regular(OWN, 'native-hello/' + row['name'] + '-' + row['mode'] + '.' + stream)
            need(sha(output) == row[stream + '_sha256'], 'hello output digest differs')
            other = 'emulated' if row['mode'] == 'native' else 'native'
            need(output == regular(OWN, 'native-hello/' + row['name'] + '-' + other + '.' + stream),
                 'hello native/emulated differs')
    return len(receipt['rows'])


@contextmanager
def historical_test_view(preview, originals):
    previous = preview.safe_read
    def read(root, name):
        raw = previous(root, name)
        return originals[name] if root == ROOT and name in PROJECT else raw
    preview.safe_read = read
    try:
        yield
    finally:
        preview.safe_read = previous


def main():
    need(sha(regular(OWN, 'binding.json')) == BINDING_SHA, 'candidate binding changed')
    binding = json.loads(regular(OWN, 'binding.json'))
    need(binding['head'] == CURRENT_HEAD and binding['baseline'] == BASE, 'candidate source identity')
    baseline = json.loads(regular(RECORD, 'construction/u1-skeleton/code-generation/verification/step66-quality-binding.json'))
    need(baseline['head'] == BASE and len(baseline['quality_inputs']) == 367, 'historical closure changed')
    linux, mandatory = current_evidence(binding)
    originals, before = classify(binding, baseline)
    for name in baseline['quality_inputs']:
        need(sha(regular(ROOT, name)) == linux[name], 'current source differs from new Linux checkout: ' + name)
    for name, raw in before.items():
        need(sha(raw) == linux[name], 'new entry differs from new Linux checkout: ' + name)
    hello_count = hello()
    canonical = RECORD / 'construction/u11-wasm-launcher/code-generation/verification/verify-packed-current.py'
    need(sha(canonical.read_bytes()) == binding['canonical_sha256'], 'official packed verifier changed')
    spec = importlib.util.spec_from_file_location('unchanged_official_packed_verifier', canonical)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    sys.path.insert(0, str(RECORD / 'construction/u5-threads-futex/code-generation/verification'))
    import preview_source_binding as preview
    print(json.dumps({'current_coverage': binding['coverage'], 'current_ci_overall': 'failure',
                      'current_u14_guest_audit': binding['u14_guest_audit'],
                      'old_coverage': 'historical signed-source audit only; no new coverage success'}, sort_keys=True), flush=True)
    with historical_test_view(preview, originals):
        legacy.main()  # ALL old predicates and fresh packed production wasm hello retained.
    need(classify(binding, baseline)[1] == before, 'current delta changed during verification')
    current_evidence(binding)
    print(json.dumps({'bounded_current_u1': 'passed', 'head': CURRENT_HEAD,
                      'current_ci_successful_jobs': mandatory, 'fresh_native_hello_rows': hello_count,
                      'historical_quality_predicates': 'all retained on matching signed old source',
                      'projected_test_dev_ci_paths': sorted(PROJECT),
                      'current_coverage': 'measurement failed, not passed',
                      'u14': 'not completed; aube overlay repair pending',
                      'future_source_change': 'refused; new explicit verification command approval required'}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
