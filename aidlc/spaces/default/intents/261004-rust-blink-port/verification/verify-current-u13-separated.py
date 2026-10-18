"""U13 candidate; formal execution requires separate human command approval.

The unchanged U12 checker runs against its exact 342 signed inputs and 72
historical support files. Fresh Windows/shared evidence is checked separately.
"""
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V = RECORD / 'construction/u13-windows-host/code-generation/verification'
sys.path.insert(0, str(V))
from step7_bridge import historical_check, need, validate_snapshot
from step7_ci_validation import load, originals
from step10_sources import sources
from step10_windows_validation import validate as windows_validate
from step10_separation import validate as separation_validate
import step10_shared_validation as shared

HEAD = '832abd0fb9c67f20af0fbb8b58119f019c1f9f4a'
RUN = 38236916982
CI = V / 'step10-retry-ci'
OLD_CHECKER_SHA256 = '352022ad96ccf421fdb8df3d98f551bed38ddb02635154bb3b1f55ced073ae46'
GH = next(p for p in sorted(Path.home().glob('.local/share/mise/installs/gh/*/gh_*/bin/gh'), reverse=True) if p.is_file())
JJ = next(p for p in sorted(Path.home().glob('.local/share/mise/installs/jj/*/jj'), reverse=True) if p.is_file())


def api(path):
    import json
    return json.loads(subprocess.check_output([str(GH), 'api', 'repos/Marukome0743/paludarium/' + path],
                                             cwd=ROOT, timeout=60))


def signed(path):
    return subprocess.check_output([str(JJ), '--ignore-working-copy', 'file', 'show', '-r', HEAD, path],
                                   cwd=ROOT, timeout=60)


def windows_tests():
    jobs = load(CI / 'jobs.json')['jobs']
    job = next(j for j in jobs if j['name'] == 'windows-host')
    raw = (CI / ('job-' + str(job['id']) + '.log')).read_text()
    expected = set()
    for path in ['crates/paludarium-host/src/windows.rs', 'crates/paludarium-host/src/u13_tests.rs']:
        expected |= set(re.findall(r'fn (u13_[a-z0-9_]+)\(', signed(path).decode()))
    need(len(expected) == 33, 'Windows independent test inventory differs')
    # Child console helpers appear repeatedly; only distinct named tests count.
    observed = set(re.findall(r'test [a-z0-9_:]*::(u13_[a-z0-9_]+) \.\.\. ok', raw))
    need(expected <= observed and 'Ran 35 tests' in raw, 'Windows Host/Python execution incomplete')


def linux_common_coverage():
    text = (CI / 'u11-coverage-lcov/u11-coverage.lcov').read_text()
    expected = {'lib.rs', 'clock.rs', 'threads.rs', 'native_fs.rs', 'fs.rs'}
    records = {}
    for record in text.split('end_of_record'):
        name = re.search(r'^SF:(.*)$', record, re.MULTILINE)
        if not name or '/paludarium-host/src/' not in name[1]:
            continue
        basename = Path(name[1]).name
        if basename not in expected:
            continue
        need(basename not in records, 'Duplicate common Host LCOV source')
        lines = [tuple(map(int, r)) for r in re.findall(r'^DA:(\d+),(\d+)', record, re.MULTILINE)]
        need(lines and len(lines) == len({r[0] for r in lines}), 'Empty/duplicate common Host LCOV lines')
        records[basename] = lines
    need(set(records) == expected, 'Linux common Host five-file denominator differs')
    lines = sum(len(rows) for rows in records.values())
    covered = sum(sum(hits > 0 for _, hits in rows) for rows in records.values())
    need(covered / lines >= .8, 'Linux common Host coverage below eighty percent')
    print('Fresh Linux common Host scope:', covered, '/', lines, 100 * covered / lines, flush=True)


def main():
    print('Checking 361 signed U13 inputs; historical U12 predicates remain unchanged.', flush=True)
    sources(RECORD, ROOT, HEAD, signed, api)
    validate_snapshot(V / 'step7-u12-signed-baseline', load(V / 'step7-u12-signed-baseline-manifest.json'))
    # Keep the complete approved U1/U12 validation chain unchanged, including its
    # owned historical JS reconstruction and original source/CI predicates.
    from step10_u1_historical import validate as preserved_u1
    preserved_u1()
    print('Historical checks passed; checking complete fresh U13 CI originals.', flush=True)
    originals(CI, HEAD, RUN, api)
    windows_tests()
    windows_validate(CI / 'u13-native-first', CI / 'u13-windows-host', ROOT, HEAD, signed)
    separation_validate(CI / 'u13-native-first', CI / 'u13-windows-host', ROOT, HEAD, signed)
    linux_common_coverage()
    shared.validate(CI, ROOT, HEAD, signed, V / 'step10-retry-js-results', V / 'step10-retry-signed-view')
    print('Verified finite U13: 361 signed inputs, complete fresh CI, Windows ordinary guest32 plus independent instrumented guest16, fixed coverage scopes, four wasm environments and eleven fresh sanitizer observations. Session-ID assurance remains unverified.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('U13 verification failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1)

