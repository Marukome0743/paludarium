"""Exercise runner success, binary logging, failure, timeout and group cleanup."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('u5_runner', Path(__file__).with_name('u5-native-observe.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.prefix = Path(self.directory.name)/'case'

    def tearDown(self):
        self.directory.cleanup()

    def test_binary_stdout_and_stderr(self):
        out = runner.run([sys.executable, '-c',
                          'import os;os.write(1,b"\\x00\\xff");os.write(2,b"error")'], self.prefix)
        self.assertEqual(out['stdout'], '00ff')
        self.assertEqual(out['stderr'], '6572726f72')
        self.assertEqual(out['exit'], 0)
        self.assertFalse(out['timeout'])
        self.assertEqual(self.prefix.with_suffix('.stdout').read_bytes(), b'\x00\xff')

    def test_exit_code_is_preserved(self):
        out = runner.run([sys.executable, '-c', 'raise SystemExit(17)'], self.prefix)
        self.assertEqual(out['exit'], 17)

    def test_timeout_kills_and_reaps_leader(self):
        with self.assertRaisesRegex(RuntimeError, 'watchdog expired'):
            runner.run([sys.executable, '-c', 'import time;time.sleep(60)'], self.prefix, .1)
        out = json.loads(self.prefix.with_suffix('.json').read_text())
        self.assertEqual(out['exit'], -9)
        self.assertTrue(out['timeout'])

    def test_timeout_kills_pipe_inheriting_descendant(self):
        with self.assertRaisesRegex(RuntimeError, 'watchdog expired'):
            runner.run([sys.executable, '-c',
                        'import subprocess,time;subprocess.Popen(["sleep","60"]);time.sleep(60)'],
                       self.prefix, .1)
        self.assertTrue(json.loads(self.prefix.with_suffix('.json').read_text())['timeout'])

    def test_exited_leader_with_live_descendant_is_bounded(self):
        with self.assertRaisesRegex(RuntimeError, 'watchdog expired'):
            runner.run([sys.executable, '-c',
                        'import subprocess;subprocess.Popen(["sleep","60"])'], self.prefix, .1)
        self.assertEqual(json.loads(self.prefix.with_suffix('.json').read_text())['exit'], 0)


if __name__ == '__main__':
    unittest.main()
