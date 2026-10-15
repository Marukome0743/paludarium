import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('u9_producer',ROOT/'scripts/u9-coverage-evidence.py')
P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)


class Evidence(unittest.TestCase):
    def capture(self):
        tmp=tempfile.TemporaryDirectory(dir=ROOT/'target',prefix='u9-capture-');self.addCleanup(tmp.cleanup)
        return P.Capture(Path(tmp.name)/'fresh')

    def test_diff_counts(self):
        self.assertEqual(P.diff_counts(' Running tests/diff_u9.rs (target/x)\ntest result: ok. 7 passed; 0 failed; 0 ignored;'),(7,0))

    def test_zero_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(' Running tests/diff_u9.rs (x)\ntest result: ok. 0 passed; 0 failed; 0 ignored;')

    def test_ignored_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(' Running tests/diff_u9.rs (x)\ntest result: ok. 7 passed; 0 failed; 1 ignored;')

    def test_other_suite_not_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(' Running unittests lib.rs (x)\ntest result: ok. 70 passed; 0 failed; 0 ignored;')

    def test_exact_success_bytes(self):
        c=self.capture()
        with patch.object(P.subprocess,'run',return_value=subprocess.CompletedProcess(['tool'],0,b'\x00out',b'err')):
            out,err,row=c.run('success',['tool'])
        self.assertEqual(out,b'\x00out');self.assertEqual(err,b'err')
        self.assertEqual((c.output/'success.stdout').read_bytes(),out)
        self.assertEqual(row['exit'],0)

    def test_failure_keeps_raw(self):
        c=self.capture()
        with patch.object(P.subprocess,'run',return_value=subprocess.CompletedProcess(['tool'],3,b'out',b'full stderr')):
            with self.assertRaises(ValueError):c.run('failure',['tool'])
        self.assertEqual((c.output/'failure.stderr').read_bytes(),b'full stderr')
        self.assertEqual(c.commands[0]['exit'],3)

    def test_timeout_keeps_raw_and_rethrows(self):
        c=self.capture()
        error=subprocess.TimeoutExpired(['tool'],1,output=b'out',stderr=b'partial err')
        with patch.object(P.subprocess,'run',side_effect=error):
            with self.assertRaises(subprocess.TimeoutExpired):c.run('timeout',['tool'],1)
        self.assertEqual((c.output/'timeout.stderr').read_bytes(),b'partial err')
        self.assertTrue(c.commands[0]['timed_out'])

    def test_reuse_directory_rejected(self):
        c=self.capture()
        with self.assertRaises(FileExistsError):P.Capture(c.output)

    def test_raw_overwrite_rejected(self):
        c=self.capture();c.save('x',b'old')
        with self.assertRaises(FileExistsError):c.save('x',b'new')
        self.assertEqual((c.output/'x').read_bytes(),b'old')


if __name__=='__main__':unittest.main()
