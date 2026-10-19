"""Diagnostic/current U1 verifier retaining both complete historical canonicals.

Current execution binding is produced only after the approved diagnostic CI.
Missing observations remain failures, even when a different CI's jobs passed.
"""
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / 'construction/u1-skeleton/code-generation/verification'
sys.path.insert(0, str(V))
from source_bound_validation import current_binding, need, observation, sha
from u14_historical_views import load, validate as historical
from u14_current_originals import closure, collect, sanitizer_originals
from u14_source_bound_validation import immutable_checker
from u14_publication_audit import validate as publications


def current(*, binding_name='u14-current-u1-execution-binding.json',
            manifest_name='u14-current-originals-manifest.json',
            sanitizer_binding_name='u14-current-sanitizer-binding.json',
            sanitizer_folder_name='u14-current-sanitizer-originals-38290361104',
            sanitizer_options=None):
    binding_path = V / binding_name
    need(binding_path.is_file() and not binding_path.is_symlink(),
         'current U1 execution binding unavailable: fresh hello/coverage/source receipt CI required')
    binding = json.loads(binding_path.read_bytes())
    head, run = binding['head'], binding['run']
    need(type(head) is str and len(head) == 40 and type(run) is int and run > 0,
         'current execution identity malformed')
    publications(head)
    folder = V / ('u14-current-originals-' + str(run))
    raw_manifest = json.loads((V / manifest_name).read_bytes())
    need(raw_manifest['head'] == head and raw_manifest['run'] == run,
         'current raw manifest identity differs')
    raw_rows = raw_manifest['files']
    need(len(raw_rows) == 21 and len({r['path'] for r in raw_rows}) == 21,
         'current original inventory differs')
    raw_folder = folder / 'current-u1-ci'
    need({p.name for p in raw_folder.iterdir()} == {r['path'] for r in raw_rows},
         'extra or missing current original')
    for row in raw_rows:
        path = raw_folder / row['path']
        need(path.parent == raw_folder and path.is_file() and not path.is_symlink()
             and sha(path.read_bytes()) == row['sha256'] and path.stat().st_size == row['size'],
             'current original changed')
    commit, jobs, files = collect(folder / 'current-u1-ci', head, run)
    need([p['sha'] for p in commit['parents']] == [binding['parent']], 'current signed parent differs')
    expected = closure(files, lambda name: subprocess.check_output(
        ['jj', '--ignore-working-copy', 'file', 'show', '-r', head, name], cwd=ROOT, timeout=60))
    need(expected == binding['inputs'], 'declared dependency closure differs from actual receipt')
    signed, local = {}, {}
    for name in expected:
        path = ROOT / name
        need(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)),
             'current dependency missing or linked: ' + name)
        local[name] = sha(path.read_bytes())
        signed[name] = sha(subprocess.check_output(['jj', '--ignore-working-copy', 'file', 'show', '-r', head, name],
                                                 cwd=ROOT, timeout=60))
    current_binding(local, signed, expected)
    checker = RECORD / 'verification/verify-current-u1-source-bound.py'
    immutable_checker(checker, 'bb199f298178ba1311308c7646c912317115f50d03c48efc8829b437279d763c')
    original = load('u14_current_u1_execution_predicates', checker)
    # Retain every original execution predicate; only current source/CI routes
    # change. Historical main ran separately without these bindings.
    original.HEAD, original.RUN, original.V = head, run, folder
    measured = original.executions(jobs, files, expected)
    observation(measured, binding['observation'])
    need(measured == binding['observation'], 'current observation binding differs')
    sanitizer_binding = json.loads((V / sanitizer_binding_name).read_bytes())
    actual_sanitizers = sanitizer_originals(V / sanitizer_folder_name, ROOT, head,
                                          **(sanitizer_options or {}))
    need(actual_sanitizers == sanitizer_binding, 'current sanitizer observation binding differs')
    unresolved = json.loads((V / 'u14-known-unresolved-jit-panic.json').read_bytes())
    need(unresolved['status'] == 'unresolved-product-panic; not a successful sanitizer observation'
         and unresolved['run'] == 38290360670 and unresolved['target_exit'] == 77
         and unresolved['wrapper_exit'] == 1, 'known failure improperly reclassified')
    for name, digest in unresolved['originals'].items():
        path = V / name
        need(path.parent == V and path.is_file() and not path.is_symlink()
             and sha(path.read_bytes()) == digest, 'known failure original changed')
    print('Current U1 source/hello/differential/fixed coverage predicates passed.', flush=True)
    print('Thirteen current-source sanitizer originals passed; browser failures and U14 performance remain unresolved.', flush=True)
    print('UNRESOLVED: same-binary standalone jit_compile panic retained; successful finite observations do not resolve it.', flush=True)


def main():
    historical()
    current()


if __name__ == '__main__':
    main()
