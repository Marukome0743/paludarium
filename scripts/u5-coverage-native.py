"""Regenerate preceding U3 native replay inputs before U5 coverage, with watchdogs."""
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess

out = Path('target/u3-guests')
rows = []
for name, expected_rows in [('observe', 23576), ('fault-observe', 1162), ('cpuid-observe', 12)]:
    binary = out / name
    with (out / (name + '.native')).open('wb') as stdout, (out / (name + '.stderr')).open('wb') as stderr:
        child = subprocess.Popen([str(binary.resolve())], stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            raise
    data = (out / (name + '.native')).read_bytes()
    rows.append(dict(name=name, exit=code, rows=len(data.splitlines()),
                     binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                     output_sha256=hashlib.sha256(data).hexdigest()))
    (out / 'native-input-receipt.json').write_text(json.dumps(rows, indent=2) + '\n')
    if code != 0 or len(data.splitlines()) != expected_rows or (out / (name + '.stderr')).read_bytes():
        raise RuntimeError(f'U3 native input generation failed: {rows[-1]}')
