import copy
import json
import unittest

from validation import CASES, HEX_FIELDS, validate


def observations():
    rows = []
    for name in CASES:
        row = {'name': name, 'signal': 0, 'child_exit': 0}
        if name in ('unmapped-data-fault', 'division-fault'):
            row['signal'] = 11 if name == 'unmapped-data-fault' else 8
            row['child_exit'] = None
        else:
            row.update(dict.fromkeys(HEX_FIELDS, '0000000000000000'))
        rows.append(row)
    return rows


def check(rows, **kwargs):
    return validate('\n'.join(json.dumps(row) for row in rows),
                    seconds=kwargs.get('seconds', 1), exit_code=kwargs.get('exit_code', 0))


class NativeValidation(unittest.TestCase):
    def test_complete_inventory_and_fault_rows(self):
        self.assertEqual(len(CASES), 13)
        self.assertEqual(check(observations()), observations())

    def test_each_je_condition_is_required(self):
        for name in ('je-zf1-taken', 'je-zf0-not-taken'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                check([row for row in observations() if row['name'] != name])

    def test_ambiguous_legacy_jne_labels_rejected(self):
        for name, old in (('jne-zf1-not-taken', 'branch-taken'),
                          ('jne-zf0-taken', 'branch-not-taken')):
            rows = observations()
            rows[CASES.index(name)]['name'] = old
            with self.subTest(name=name), self.assertRaises(ValueError):
                check(rows)

    def test_missing_case(self):
        with self.assertRaises(ValueError):
            check(observations()[:-1])

    def test_duplicate_case(self):
        rows = observations()
        rows[-1] = copy.deepcopy(rows[0])
        with self.assertRaises(ValueError):
            check(rows)

    def test_reordered_inventory(self):
        with self.assertRaises(ValueError):
            check(list(reversed(observations())))

    def test_extra_field(self):
        rows = observations()
        rows[0]['ignored'] = 1
        with self.assertRaises(ValueError):
            check(rows)

    def test_numeric_register_rejected(self):
        rows = observations()
        rows[0]['rax'] = 0
        with self.assertRaises(ValueError):
            check(rows)

    def test_unexpected_signal(self):
        rows = observations()
        rows[0] = {'name': CASES[0], 'signal': 11, 'child_exit': None}
        with self.assertRaises(ValueError):
            check(rows)

    def test_fault_success_rejected(self):
        rows = observations()
        index = CASES.index('unmapped-data-fault')
        rows[index] = dict(rows[0], name=CASES[index])
        with self.assertRaises(ValueError):
            check(rows)

    def test_nonzero_exit(self):
        with self.assertRaises(ValueError):
            check(observations(), exit_code=115)

    def test_wrong_fault_signal(self):
        rows = observations()
        rows[CASES.index('unmapped-data-fault')]['signal'] = 4
        with self.assertRaises(ValueError):
            check(rows)

    def test_signal_and_exit_are_distinct(self):
        rows = observations()
        rows[CASES.index('unmapped-data-fault')]['child_exit'] = 0
        with self.assertRaises(ValueError):
            check(rows)

    def test_child_failure(self):
        rows = observations()
        rows[0]['child_exit'] = 1
        with self.assertRaises(ValueError):
            check(rows)

    def test_deadline_and_nonfinite_duration(self):
        for seconds in (-1, 30.01, float('nan'), float('inf'), True):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                check(observations(), seconds=seconds)


if __name__ == '__main__':
    unittest.main()
