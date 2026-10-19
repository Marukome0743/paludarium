"""Candidate formal U11 verifier. Do not execute before human command approval.

Checks signed current inputs, bounded source rebinding, fresh actual guests,
defined coverage, preserved ASan/LSan binaries, and package originals.
"""
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[6]
U = pathlib.Path(__file__).resolve().parent.parent / 'construction/u11-wasm-launcher/code-generation'
V = U / 'verification'
HEAD = '2b3874eabda6fe6f1d1334202421db733445fd21'
OBS_HEAD = 'b263121214981a549ad8bfb7ddb975de03226f58'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())

def gh(*args):
    return json.loads(subprocess.check_output(['gh', *args], text=True))

for source in [HEAD, OBS_HEAD]:
    commit = gh('api', f'repos/Marukome0743/paludarium/commits/{source}')
    assert commit['sha'] == source and commit['commit']['verification']['verified']
    assert commit['commit']['verification']['reason'] == 'valid'
for run, source in [(38104676911, HEAD), (38103577222, OBS_HEAD)]:
    status = gh('run','view',str(run),'--repo','Marukome0743/paludarium',
                '--json','status,conclusion,headSha,jobs')
    assert status['headSha'] == source and status['status'] == 'completed'
    assert status['conclusion'] == 'success'
    assert all(job['conclusion'] == 'success' for job in status['jobs'])

sources = read(V/'source-hashes.json')
manifest = read(U/'source-manifest.json')
assert set(manifest) == {'stage','unit','version','writes'}
assert sources['source_sha'] == HEAD and len(sources['inputs']) == 329
assert {row['path'] for row in manifest['writes']} == set(sources['inputs'])
for path, expected in {**sources['inputs'], **sources['ci_record_helpers']}.items():
    actual = ROOT/path
    assert digest(actual) == expected, path
    signed = subprocess.check_output(['jj','--ignore-working-copy','file','show','-r',HEAD,path],cwd=ROOT)
    assert signed == actual.read_bytes(), path
binding = read(V/'current-quality-source-binding.json')
assert binding['source_sha'] == HEAD and binding['observation_source_sha'] == OBS_HEAD
assert binding['changed'] == ['.github/workflows/u11-fuzz.yml'] and binding['identical_inputs'] == 328
changes = subprocess.check_output(['jj','--ignore-working-copy','diff','--from',OBS_HEAD,'--to',HEAD,'--name-only'],cwd=ROOT,text=True).splitlines()
assert changes == binding['changed'], changes

CI = V/'final-current-ci'
module = CI/'inputs/packages/paludarium-wasm/paludarium.wasm'
oracle_path = CI/'inputs/target/u11/native/observations.json'
oracle = read(oracle_path)
assert oracle['native_complete'] and len(oracle['rows']) == 14
assert all(row['exit'] == 0 and not row['timed_out'] for row in oracle['rows'].values())
for environment in ['node','chromium','firefox','safari']:
    output = CI/environment/environment
    observation = read(output/'observations.json')
    assert observation['complete'] and len(observation['rows']) == 14
    assert all(row['pass'] and row['exit'] == 0 and not row['timed_out'] for row in observation['rows'].values())
    assert observation['module_sha256'] == digest(module)
    assert observation['oracle_sha256'] == digest(oracle_path)
    assert observation['guest_hashes'] == oracle['binary_hashes']
    supervisor = read(output/'suite-supervisor.json')
    assert supervisor['exit'] == 0 and not supervisor['timed_out'] and supervisor['process_group_cleaned']
    sequence = read(V/'sequential-current'/environment/'observations.json')
    assert sequence['complete'] and len(sequence['rows']) == 14
    assert sequence['module_sha256'] == digest(module) and sequence['oracle_sha256'] == digest(oracle_path)
    assert all(row['pass'] for row in sequence['rows'].values())
coverage = read(CI/'node/node/js-coverage.json')
assert len(coverage['files']) == 5 and all(row['raw_scripts'] > 0 for row in coverage['files'])
assert coverage['total']['lines'] == 449 and coverage['total']['hit'] >= 0.8*449
for path in [V/'current-ci/coverage-u11/u11-coverage.lcov',V/'current-quality/u3-coverage-lcov/u3-coverage.lcov',V/'current-quality/u9-coverage-lcov/u9-coverage.lcov']:
    lines = path.read_text().splitlines()
    total = sum(int(row[3:]) for row in lines if row.startswith('LF:'))
    hit = sum(int(row[3:]) for row in lines if row.startswith('LH:'))
    assert total > 0 and hit >= 0.8*total
old_quality = gh('run','view','38102192489','--repo','Marukome0743/paludarium','--json','headSha,conclusion,jobs')
assert old_quality['headSha'] == '2c690e123ec2e8f28ccc672c2b0d79d7f5aa90f8' and old_quality['conclusion'] == 'failure'
quality_delta = subprocess.check_output(['jj','--ignore-working-copy','diff','--from',old_quality['headSha'],'--to',HEAD,'--name-only'],cwd=ROOT,text=True).splitlines()
assert quality_delta == ['.github/workflows/u11-current-verification.yml','.github/workflows/u11-fuzz.yml','packages/paludarium-wasm/tests/u11-api-check.mjs'], quality_delta
for name in ['unit tests (windows-latest)','unit tests (macos-latest)','unit tests (ubuntu-latest)','lint','dependencies','differential tests (x86-64 Linux)','line coverage >= 80%']:
    assert any(row['name'] == name and row['conclusion'] == 'success' for row in old_quality['jobs'])
diff = (CI/'inputs/target/u11-shared-regressions/differential.log').read_text()
assert '43 passed; 0 failed' in diff and '84 passed; 0 failed' in diff

proof = read(V/'current-quality-proof.json')
assert proof['source_sha'] == HEAD and proof['ci_run'] == 38104676911 and len(proof['targets']) == 7
for target, result in proof['targets'].items():
    assert result['exit'] == 0 and result['seconds'] >= 600
    assert digest(V/result['binary']) == result['binary_sha256']
    assert digest(V/result['raw']) == result['raw_sha256']
    raw = V/result['raw']
    directory = raw.parent
    assert (directory/'exit.txt').read_text().strip() == '0'
    assert (directory/'locks-before.sha256').read_bytes() == (directory/'locks-after.sha256').read_bytes()
    for line in (directory/'locks-after.sha256').read_text().splitlines():
        expected,path = line.split(maxsplit=1)
        assert digest(ROOT/path.strip()) == expected
    assert 'commit-hash: 32dba69d69c5b10ea89a4042de8d0619f7756203' in (directory/'toolchain.txt').read_text()
    assert result['settings'] == (directory/'settings.txt').read_text()
    assert re.search(r'Done \d+ runs in 60[01] second\(s\)',raw.read_text())
assert digest(ROOT/'fuzz/lsan.supp') == proof['suppression_sha256'] and not proof['suppression_added']
pack = read(V/'current-pack-proof.json')
assert pack['exit'] == 0 and pack['npm'] == '12.2.0' and not pack['published']
assert len(pack['files']) == 10 and pack['files'].count('paludarium.wasm') == 1
assert digest(ROOT/'packages/paludarium-wasm/paludarium.wasm') == digest(module)
trace = read(U/'traceability.json')
assert trace['source_sha'] == HEAD and not trace['draft']
assert read(V/'current-sensor-trace.json')['pass'] and read(V/'current-sensor-summary.json')['pass']
print(json.dumps({'status':'verified','source_sha':HEAD,'application_inputs':329,
                  'actual_environments':4,'cases_each':14,'asan_targets':7,
                  'old_failed_execution_preserved':True}))
