"""Expose diagnostic collector/runner rejection regressions in the U14 suite."""
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[3]


class CostProfileRegression(unittest.TestCase):
    def test_node_cost_collector_and_runner_boundaries(self):
        node = os.environ.get('PALUDARIUM_TEST_NODE') or shutil.which('node')
        if not node or '/shims/' in node:
            self.fail('actual Node executable required via PALUDARIUM_TEST_NODE')
        result = subprocess.run([node, '--test',
                                 'packages/paludarium-wasm/tests/u14-cost-profile.test.mjs'],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('tests 16', result.stdout)


if __name__ == '__main__':
    unittest.main()
