"""DynamoRIO native DBI block observation; not a hardware trace/state oracle."""
import hashlib
import json
import os
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
for name, args in [('version', ['--version']), ('install', ['install']), ('frozen', ['install', '--frozen-lockfile']), ('list', ['list'])]:
    if name == 'frozen':
        shutil.rmtree(fixture / 'app/node_modules', ignore_errors=True)
    logs = out / name
    logs.mkdir()
    command = [str(tool), '-t', 'drcov', '-dump_text', '-logdir', str(logs), '--', str(binary), *args]
    env = dict(os.environ, AUBE_NO_UPDATE_CHECK='1', AUBE_NO_TELEMETRY='1')
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
    reference = (out / ('input/' + name + '.stdout')).read_bytes()
    results[name] = dict(command=command, exit=child.returncode, timeout=timeout, reaped=True, elapsed_seconds=time.monotonic()-started, watchdog_seconds=30, stdout_matches_uninstrumented=reference == (logs / 'stdout').read_bytes(), coverage_files=[p.name for p in logs.glob('drcov*')])
(out / 'results.json').write_text(json.dumps(dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), mode='native dynamic binary instrumentation basic-block coverage; not hardware PT or architectural state oracle', results=results), indent=2)+'\n')
if any(r['exit'] != 0 or r['timeout'] or not r['stdout_matches_uninstrumented'] or not r['coverage_files'] for r in results.values()):
    raise SystemExit('DBI workload or coverage validation failed; preserve raw evidence')
