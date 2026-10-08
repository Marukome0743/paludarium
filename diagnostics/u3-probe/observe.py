"""Approved probe repin source proof and bounded native observations."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

out = Path('target/u3-probe')
out.mkdir(parents=True, exist_ok=True)
source = Path('diagnostics/u3-probe/source')
rows = json.loads(Path('diagnostics/u3-probe/source-manifest.json').read_text())['rows']
observed = [dict(r, observed=hashlib.sha256((source/r['path']).read_bytes()).hexdigest()) for r in rows]
assert len(observed) == 8 and all(r['sha256'] == r['observed'] for r in observed)
mode = sys.argv[1]
if mode in ['before', 'after']:
    (out/('source-'+mode+'.json')).write_text(json.dumps(observed, indent=2)+'\n')
    if mode == 'after':
        assert json.loads((out/'source-before.json').read_text()) == observed
else:
    binary = (out/'probe').resolve()
    (out/'binary.json').write_text(json.dumps(dict(sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), target='human-approved current eight-source snapshot; historical probe retained separately'), indent=2)+'\n')
    results = {}
    for name, command in [('native',[str(binary)]), ('elf',['readelf','-W','-l','-S',str(binary)]), ('disassembly',['objdump','-d','-Mintel','--insn-width=16',str(binary)])]:
        started=time.monotonic()
        with (out/(name+'.stdout')).open('wb') as stdout, (out/(name+'.stderr')).open('wb') as stderr:
            child=subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
            timeout=False
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                timeout=True
                os.killpg(child.pid,signal.SIGKILL)
                child.wait()
        results[name]=dict(command=command,exit=child.returncode,timeout=timeout,reaped=True,elapsed_seconds=time.monotonic()-started,watchdog_seconds=30)
    text=(out/'native.stdout').read_text()
    results['native']['stdout']=text
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(r['exit']==0 and not r['timeout'] for r in results.values())
    assert 'PASS' in text and 'FAIL' not in text, 'inspect actual eight check output before inventory acceptance'
