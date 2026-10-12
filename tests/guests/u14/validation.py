"""Strict inventory/schema checks; numeric guest expectations come from Linux."""
import json
import math

CASES = ('move64', 'add64-carry', 'sub64-overflow', 'branch-taken',
         'branch-not-taken', 'memory-read-write', 'unsupported-sse-fallback',
         'unmapped-data-fault', 'division-fault', 'self-modifying-code',
         'cross-page-instruction')
HEX_FIELDS = ('rax', 'first_rax', 'flags', 'flag_mask', 'memory')


def validate(stdout, *, seconds, exit_code):
    if (type(seconds) not in (int, float) or not math.isfinite(seconds)
            or not 0 <= seconds <= 30 or type(exit_code) is not int or exit_code != 0):
        raise ValueError('native process failed or exceeded thirty seconds')
    rows = [json.loads(line) for line in stdout.splitlines()]
    if tuple(row.get('name') for row in rows) != CASES:
        raise ValueError('missing, duplicate, reordered or extra native cases')
    for row in rows:
        if type(row.get('signal')) is not int or not 0 <= row['signal'] < 65:
            raise ValueError('invalid Linux signal')
        fields = {'name', 'signal', 'child_exit'} if row['signal'] else {'name', 'signal', 'child_exit', *HEX_FIELDS}
        if set(row) != fields:
            raise ValueError('native row schema changed')
        if row['signal']:
            if row['child_exit'] is not None:
                raise ValueError('signaled child cannot have an exit code')
        elif type(row['child_exit']) is not int or row['child_exit'] != 0:
            raise ValueError('native child did not exit successfully')
        for name in fields - {'name', 'signal', 'child_exit'}:
            value = row[name]
            if (type(value) is not str or len(value) != 16
                    or any(char not in '0123456789abcdef' for char in value)):
                raise ValueError('native register must be a sixteen-digit hex string')
        fault = row['name'] in ('unmapped-data-fault', 'division-fault')
        if bool(row['signal']) != fault:
            raise ValueError('unexpected native success or signal')
        if fault and row['signal'] != (11 if row['name'] == 'unmapped-data-fault' else 8):
            raise ValueError('wrong native fault signal')
    return rows
