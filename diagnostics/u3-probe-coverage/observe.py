"""Eight-check native DBI observation; no emulator product dependency."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

out=Path('target/u3-probe-coverage').resolve()
binary=out/'input/probe'
tool=next(out.glob('DynamoRIO-Linux-*/bin64/drrun'))
results={}
for name in ['native','observed']:
    logs=out/name
    logs.mkdir()
    command=[str(binary)] if name=='native' else [str(tool),'-t','drcov','-dump_text','-logdir',str(logs),'--','/bin/sh','-c','exec "$@" 2>"$APP_STDERR"','u3-probe',str(binary)]
    started=time.monotonic()
    with (logs/'stdout').open('wb') as stdout,(logs/'stderr').open('wb') as stderr:
        child=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=dict(os.environ,APP_STDERR=str(logs/'application.stderr')),start_new_session=True)
        timeout=False
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            timeout=True
            os.killpg(child.pid,signal.SIGKILL)
            child.wait()
    results[name]=dict(command=command,exit=child.returncode,timeout=timeout,reaped=True,elapsed_seconds=time.monotonic()-started,watchdog_seconds=30)
stdout_equal=(out/'native/stdout').read_bytes()==(out/'observed/stdout').read_bytes()
stderr_equal=(out/'native/stderr').read_bytes()==(out/'observed/application.stderr').read_bytes()
checks=(out/'observed/stdout').read_text().splitlines()
proof=dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),results=results,stdout_matches=stdout_equal,application_stderr_matches=stderr_equal,checks=checks,coverage_files=[p.name for p in (out/'observed').glob('drcov.probe.*.log')],boundary='finite eight-check native DBI basic block coverage, not architectural state oracle')
(out/'results.json').write_text(json.dumps(proof,indent=2)+'\n')
assert all(r['exit']==0 and not r['timeout'] for r in results.values())
assert stdout_equal and stderr_equal and len(checks)==8 and all(c.startswith('PASS ') for c in checks)
assert proof['coverage_files']
