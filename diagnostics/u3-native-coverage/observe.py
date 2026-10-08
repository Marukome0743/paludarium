"""DynamoRIO native DBI block observation; not a hardware trace/state oracle."""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import time

out = Path('target/u3-native-coverage').resolve()
binary = out / 'input/aube'
tool = next(out.glob('DynamoRIO-Linux-*/bin64/drrun'))
fixture = out / 'fixture'
(fixture / 'app/filedep').mkdir(parents=True)
(fixture / 'outside/linked').mkdir(parents=True)
(fixture / 'app/package.json').write_text(json.dumps(dict(name='app', version='1.0.0', dependencies=dict(filedep='file:./filedep', linked='link:../outside/linked'))))
for name, version in [('app/filedep', '1.0.0'), ('outside/linked', '2.0.0')]:
    (fixture / name / 'package.json').write_text(json.dumps(dict(name=name.split('/')[-1], version=version)))
results = {}
def normalize_elapsed(data):
    return re.sub(rb'(?<= in \x1b\[2m)[0-9]+(?:\.[0-9]+)?(?:ms|s)(?=\x1b\[0m)', b'<elapsed>', data)
initial = out / 'fixture-initial'
shutil.copytree(fixture, initial)
native = out / 'paired-native'
native.mkdir()
native_results = {}
for name, args in [('version', ['--version']), ('install', ['install']), ('frozen', ['install', '--frozen-lockfile']), ('list', ['list'])]:
    if name == 'frozen':
        shutil.rmtree(fixture / 'app/node_modules', ignore_errors=True)
    started = time.monotonic()
    with (native / (name+'.stdout')).open('wb') as stdout, (native / (name+'.stderr')).open('wb') as stderr:
        child = subprocess.Popen([str(binary), *args], cwd=fixture / 'app', env=dict(os.environ, AUBE_NO_UPDATE_CHECK='1', AUBE_NO_TELEMETRY='1'), stdout=stdout, stderr=stderr, start_new_session=True)
        timed_out = False
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
    native_results[name] = dict(exit=child.returncode, timeout=timed_out, reaped=True, elapsed_seconds=time.monotonic()-started)
shutil.rmtree(fixture)
shutil.copytree(initial, fixture)
for name, args in [('version', ['--version']), ('install', ['install']), ('frozen', ['install', '--frozen-lockfile']), ('list', ['list'])]:
    if name == 'frozen':
        shutil.rmtree(fixture / 'app/node_modules', ignore_errors=True)
    logs = out / name
    logs.mkdir()
    # Shell redirects only application stderr; DynamoRIO diagnostics stay separate.
    command = [str(tool), '-t', 'drcov', '-dump_text', '-logdir', str(logs), '--', '/bin/sh', '-c', 'exec "$@" 2>"$APP_STDERR"', 'u3-observation', str(binary), *args]
    env = dict(os.environ, AUBE_NO_UPDATE_CHECK='1', AUBE_NO_TELEMETRY='1')
    env['APP_STDERR'] = str(logs / 'application.stderr')
    started = time.monotonic()
    with (logs / 'stdout').open('wb') as stdout, (logs / 'stderr').open('wb') as stderr:
        child = subprocess.Popen(command, cwd=fixture / 'app', env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        timeout = False
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
    reference = (native / (name + '.stdout')).read_bytes()
    # Only the known fixture-root path differs between these two archived runs.
    # Preserve both raw outputs and report the exact normalization separately.
    old_root = b'/home/runner/work/paludarium/paludarium/target/u3-inventory/fixture/app'
    normalized_reference = reference.replace(old_root, str(fixture / 'app').encode())
    results[name] = dict(command=command, exit=child.returncode, timeout=timeout, reaped=True, elapsed_seconds=time.monotonic()-started, watchdog_seconds=30, stdout_matches_uninstrumented=reference == (logs / 'stdout').read_bytes(), application_stderr_matches_uninstrumented=(native / (name+'.stderr')).read_bytes() == (logs / 'application.stderr').read_bytes(), application_stderr_matches_duration_only_normalization=normalize_elapsed((native / (name+'.stderr')).read_bytes()) == normalize_elapsed((logs / 'application.stderr').read_bytes()), stdout_matches_after_exact_fixture_path_substitution=normalized_reference == (logs / 'stdout').read_bytes(), fixture_path_substitution=dict(before=old_root.decode(), after=str(fixture / 'app')), coverage_files=[p.name for p in logs.glob('drcov*')])
(out / 'results.json').write_text(json.dumps(dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), mode='native dynamic binary instrumentation basic-block coverage; not hardware PT or architectural state oracle', native_results=native_results, results=results), indent=2)+'\n')
if any(r['exit'] != 0 or r['timeout'] for r in native_results.values()) or any(r['exit'] != 0 or r['timeout'] or not r['stdout_matches_uninstrumented'] or not r['application_stderr_matches_duration_only_normalization'] or not r['coverage_files'] for r in results.values()):
    raise SystemExit('DBI workload or coverage validation failed; preserve raw evidence')
