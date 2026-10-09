"""Fresh native oracle and identical guest bytes executed through C10."""
import json
import os
import pathlib
import shutil
import sys
import tempfile

from comparison import compare, probe_pass, reproduced
from evidence import snapshot
from native import observe
from runner import run

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def operation(executable, binary, args, directory, environment, fixture=None, mounted=False):
    directory.mkdir(parents=True)
    (directory / 'args').write_text('\n'.join(args) + ('\n' if args else ''))
    (directory / 'environment').write_text(''.join(k + '=' + v + '\n' for k, v in environment.items()))
    env = dict(os.environ, PALUDARIUM_U10_OPERATION=str(directory), PALUDARIUM_U10_BINARY=str(binary))
    env.pop('PALUDARIUM_U10_FIXTURE', None)
    env.pop('PALUDARIUM_U10_MOUNTED', None)
    if fixture is not None:
        env['PALUDARIUM_U10_FIXTURE'] = str(fixture)
    if mounted:
        env['PALUDARIUM_U10_MOUNTED'] = '1'
    child = run([str(executable), '--exact', 'u10_guest_operation', '--nocapture'], cwd=ROOT, env=env)
    (directory / 'runner.json').write_text(json.dumps(child, indent=2) + '\n')
    if child['timed_out'] or child['exit'] != 0:
        raise ValueError('emulator operation failed/timed out: ' + str(directory))
    row = {'stdout': (directory / 'stdout').read_text(), 'stderr': (directory / 'stderr').read_text(),
           'exit': int((directory / 'exit').read_text()), 'timed_out': False,
           'wall_seconds': float((directory / 'seconds').read_text()), 'stop': (directory / 'stop').read_text()}
    if fixture is not None:
        row['filesystem'] = snapshot(fixture)
    return row


def differential(executable):
    config = json.loads((HERE / 'cases.json').read_text())
    guests = pathlib.Path(os.environ.get('PALUDARIUM_U10_GUEST_DIR', ROOT / 'target/guests/u10')).resolve()
    output = ROOT / 'target/u10/differential'
    output.mkdir(parents=True, exist_ok=True)
    observe(guests, output / 'native', config)
    native = json.loads((output / 'native/observations.json').read_text())
    observations = {'schema': 1, 'binary_hashes': native['binary_hashes'], 'rows': {},
                    'native_complete': native['native_complete'],
                    'mount_scope': 'temporary fixture/app and fixture/outside only'}
    operations = pathlib.Path(tempfile.mkdtemp(prefix='operations-', dir=output))
    observations['operation_records'] = str(operations)

    def store(name, row):
        observations['rows'][name] = row
        (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')

    with tempfile.TemporaryDirectory(prefix='paludarium-u10-emulated-') as temporary:
        scratch = pathlib.Path(temporary)
        for name in config['probe'] + ['all', 'environment']:
            args = [] if name == 'all' else [name]
            row = operation(executable, guests / 'probe', args, operations / ('probe-' + name), config['environment'])
            store('probe-' + name, row)
            compare(native['rows']['probe-' + name], row, native['fixture_root'], '/')
            if name != 'environment':
                probe_pass(row, config['probe'] if name == 'all' else [name])
        fixture = scratch / 'fixture'
        shutil.copytree(HERE / 'fixtures', fixture)
        for case in config['aube'][:2]:
            name = 'default-' + case['name']
            row = operation(executable, guests / 'aube', case['args'], operations / name,
                            config['environment'], fixture)
            store(name, row)
            compare(native['rows'][case['name']], row, str(pathlib.Path(native['fixture_root']) / 'fixture/app'), '/')
        rows = {}
        for case in config['aube']:
            if case.get('before') == 'remove-node-modules':
                shutil.rmtree(fixture / 'app/node_modules')
            row = operation(executable, guests / 'aube', case['args'], operations / case['name'],
                            config['environment'], fixture, mounted=True)
            store(case['name'], row)
            rows[case['name']] = row
            compare(native['rows'][case['name']], row, str(pathlib.Path(native['fixture_root']) / 'fixture/app'), '/')
        reproduced(rows)
        observations['differential_complete'] = True
        (output / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
    print('U10 differential: eight probe items and four aube commands passed')


if __name__ == '__main__':
    differential(pathlib.Path(sys.argv[1]).resolve())
