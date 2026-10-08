"""Inventory diagnostic only. No emulator semantics; uncertain rows stay uncertain."""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

out = Path('target/u3-inventory')
out.mkdir(parents=True, exist_ok=True)
source = Path('target/u3-aube-source')


def save(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + '\n')


def source_hashes():
    expected = Path('docs/u2/inventory/rebuild/aube-source-files.before.sorted.sha256')
    rows = []
    for line in expected.read_text().splitlines():
        wanted, name = line.split(None, 1)
        relative = name.removeprefix('/src/aube/')
        path = source / relative
        got = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        rows.append(dict(path=relative, expected=wanted, observed=got, match=wanted == got))
    return rows


def run(name, command, cwd=None):
    started = time.monotonic()
    env = os.environ.copy()
    env.update(AUBE_NO_UPDATE_CHECK='1', AUBE_NO_TELEMETRY='1')
    with (out / (name + '.stdout')).open('wb') as stdout, (out / (name + '.stderr')).open('wb') as stderr:
        child = subprocess.Popen(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                                 start_new_session=True)
        timed_out = False
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
    result = dict(command=command, exit=child.returncode, timeout=timed_out,
                  elapsed_seconds=time.monotonic() - started, reaped=True,
                  process_watchdog_seconds=30)
    save(name + '.json', result)
    return result


mode = os.sys.argv[1]
if mode.startswith('source'):
    rows = source_hashes()
    save(mode + '.json', dict(rows=rows, all_match=all(r['match'] for r in rows)))
    if not all(r['match'] for r in rows):
        raise SystemExit('pinned source hash mismatch; reproduction rejected')
    if mode == 'source-after':
        before = json.loads((out / 'source.json').read_text())['rows']
        save('source-before-after.json', dict(unchanged=before == rows))
        if before != rows:
            raise SystemExit('source changed during build')
else:
    binary = (out / 'aube').resolve()
    observed = hashlib.sha256(binary.read_bytes()).hexdigest()
    save('binary-comparison.json', dict(expected='ff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a',
         observed=observed, matches=observed == 'ff54cffe389cc2cc589d2a737c3499e1b7be4589e9a2fe3bf37c6e7c205cca4a'))
    fixture = (out / 'fixture').resolve()
    (fixture / 'app/filedep').mkdir(parents=True)
    (fixture / 'outside/linked').mkdir(parents=True)
    (fixture / 'app/package.json').write_text(json.dumps(dict(name='app', version='1.0.0',
        dependencies=dict(filedep='file:./filedep', linked='link:../outside/linked'))))
    for name, version in [('app/filedep', '1.0.0'), ('outside/linked', '2.0.0')]:
        (fixture / name / 'package.json').write_text(json.dumps(dict(name=name.split('/')[-1], version=version)))
    observations = {}
    for name, args in [('version', ['--version']), ('install', ['install']),
                       ('frozen', ['install', '--frozen-lockfile']), ('list', ['list'])]:
        if name == 'frozen':
            shutil.rmtree(fixture / 'app/node_modules', ignore_errors=True)
        observations[name] = run(name, [str(binary), *args], fixture / 'app')
    save('native-workloads.json', observations)
    for name, args in [('elf', ['readelf', '-W', '-l', '-S', str(binary)]),
                       ('disassembly', ['objdump', '-d', '-Mintel', '--insn-width=16', str(binary)])]:
        run(name, args)
    # -d limits decoding to executable sections, but embedded data can remain.
    # Encodings and boundaries are preserved; no FDE/non-hit row is excluded.
    rows = []
    for line in (out / 'disassembly.stdout').read_text().splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*(.+)', line)
        if not match:
            continue
        address, raw, asm = match.groups()
        tokens = asm.split()
        while tokens and tokens[0] in {'data16', 'addr32', 'rep', 'repz', 'repnz', 'lock', 'cs', 'ds', 'fs', 'gs', 'ss', 'es'}:
            tokens.pop(0)
        mnemonic = tokens[0] if tokens else ''
        category = None
        if '{evex}' in asm or re.search(r'\bzmm\d+', asm):
            category = 'evex-out-of-scope'
        elif mnemonic.startswith('v') and re.search(r'\b[xyz]mm\d+', asm):
            category = 'vex-simd-out-of-scope'
        elif mnemonic.startswith(('aes', 'sha', 'pclmul')):
            category = 'crypto-scope-question'
        elif mnemonic.startswith('f') and mnemonic not in {'fs', 'fwait'}:
            category = 'x87-scope-question'
        elif re.search(r'\bxmm\d+', asm) or mnemonic in {'ldmxcsr', 'stmxcsr'}:
            category = 'legacy-sse-candidate'
        elif re.search(r'\bmm[0-7]\b', asm):
            category = 'mmx-scope-question'
        elif '(bad)' in asm or mnemonic == '.byte':
            category = 'undecodable-unresolved'
        if category:
            rows.append(dict(address=address, encoding=raw.split(), assembly=asm,
                mnemonic=mnemonic, category=category, dynamic_execution_verified=False,
                embedded_data_or_reachability_unresolved=True))
    save('static-candidates.json', dict(boundary='objdump -d executable sections; readelf PT_LOAD/SHF_EXECINSTR retained',
        complete_runtime_inventory=False, rows=rows, counts=dict(collections.Counter(r['category'] for r in rows))))
    # Hardware-native trace capability is probed without changing perf/OS settings.
    # Failure is preserved; no software/QEMU trace is called native observation.
    run('gdb-btrace-version', ['gdb', '--batch', '-ex', 'set pagination off',
        '-ex', 'starti', '-ex', 'record btrace pt', '-ex', 'continue',
        '-ex', 'info record', '--args', str(binary), '--version'], fixture / 'app')
