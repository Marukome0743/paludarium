import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('u9_producer',ROOT/'scripts/u9-coverage-evidence.py')
P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)

def result(passed,ignored=0,filtered=0):
    return f'test result: ok. {passed} passed; 0 failed; {ignored} ignored; 0 measured; {filtered} filtered out; finished in 0.01s\n'

def suite(passed,ignored=0):
    return f' Running tests/diff_u9.rs (target/x)\nrunning {passed+ignored} tests\n'+result(passed,ignored)


class Evidence(unittest.TestCase):
    def capture(self):
        tmp=tempfile.TemporaryDirectory(dir=ROOT/'target',prefix='u9-capture-');self.addCleanup(tmp.cleanup)
        return P.Capture(Path(tmp.name)/'fresh')

    def test_diff_counts(self):
        self.assertEqual(P.diff_counts(suite(7)),(7,0))

    def test_zero_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(suite(0))

    def test_ignored_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(suite(7,1))

    def test_other_suite_not_diff(self):
        with self.assertRaises(ValueError):P.diff_counts(' Running unittests lib.rs (x)\ntest result: ok. 70 passed; 0 failed; 0 ignored;')

    def test_separate_stream_concatenation_reproduces_missing_result(self):
        stdout=b'test result: ok. 70 passed; 0 failed; 0 ignored;\ntest result: ok. 7 passed; 0 failed; 0 ignored;\n'
        stderr=b' Running unittests lib.rs (x)\n Running tests/diff_u9.rs (x)\n'
        with self.assertRaisesRegex(ValueError,'diff_u9 result absent/ambiguous'):
            P.diff_counts((stdout+stderr).decode())

    def test_merged_stream_preserves_suite_identity(self):
        merged=(' Running unittests lib.rs (x)\nrunning 70 tests\n'+result(70)+suite(7)+' Running tests/command.rs (x)\nrunning 8 tests\n'+result(8)).encode()
        c=self.capture()
        with patch.object(P.subprocess,'run',return_value=subprocess.CompletedProcess(['tool'],0,merged,None)) as run:
            out,err,row=c.run('merged',['tool'],merge=True)
        self.assertEqual(run.call_args.kwargs['stdout'],subprocess.PIPE)
        self.assertEqual(run.call_args.kwargs['stderr'],subprocess.STDOUT)
        self.assertNotIn('capture_output',run.call_args.kwargs)
        self.assertEqual(err,b'')
        self.assertEqual(P.diff_counts(out.decode()),(7,0))
        self.assertEqual(row['stream_mode'],'stderr-merged-into-stdout')
        self.assertEqual((c.output/'merged.stdout').read_bytes(),merged)

    def test_duplicate_diff_suite_remains_ambiguous(self):
        section=suite(7)
        with self.assertRaises(ValueError):P.diff_counts(section+section)

    def test_actual_child_merged_stream_has_original_order(self):
        import sys
        stdout=('running 7 tests\n'+result(7)).encode()
        code='import os;os.write(2,b" Running tests/diff_u9.rs (x)\\n");os.write(1,'+repr(stdout)+')'
        out,err,row=self.capture().run('actual-merged',[sys.executable,'-c',code],merge=True)
        self.assertEqual(P.diff_counts(out.decode()),(7,0));self.assertEqual(err,b'')

    def test_merged_failure_keeps_raw(self):
        c=self.capture()
        with patch.object(P.subprocess,'run',return_value=subprocess.CompletedProcess(['tool'],7,b'ordered failure',None)):
            with self.assertRaises(ValueError):c.run('merged-failure',['tool'],merge=True)
        self.assertEqual((c.output/'merged-failure.stdout').read_bytes(),b'ordered failure')
        self.assertEqual(c.commands[0]['exit'],7)

    def test_merged_timeout_keeps_raw(self):
        c=self.capture()
        with patch.object(P.subprocess,'run',side_effect=subprocess.TimeoutExpired(['tool'],1,output=b'partial merged')):
            with self.assertRaises(subprocess.TimeoutExpired):c.run('merged-timeout',['tool'],1,merge=True)
        self.assertEqual((c.output/'merged-timeout.stdout').read_bytes(),b'partial merged')
        self.assertEqual(c.commands[0]['stream_mode'],'stderr-merged-into-stdout')

    def test_nested_14_children_and_host84_keep_only_diff_outer(self):
        child='running 1 test\ntest u9_case ... ok\n'+result(1,filtered=13)+'ok\n'
        diff=' Running tests/diff_u9.rs (target/diff_u9)\nrunning 14 tests\n'+child*14+result(14)
        host=' Running unittests src/lib.rs (target/paludarium_host)\nrunning 84 tests\nrunning 1 test\n'+result(1,filtered=83)+result(84)
        self.assertEqual(P.diff_counts(diff+host),(14,0))

    def test_nested_child_without_outer_summary_rejected(self):
        text=' Running tests/diff_u9.rs (x)\nrunning 14 tests\nrunning 1 test\n'+result(1,filtered=13)
        with self.assertRaises(ValueError):P.diff_counts(text)

    def test_outer_filtered_rejected(self):
        text=' Running tests/diff_u9.rs (x)\nrunning 1 test\n'+result(1,filtered=13)
        with self.assertRaises(ValueError):P.diff_counts(text)

    def test_outer_declared_population_mismatch_rejected(self):
        text=' Running tests/diff_u9.rs (x)\nrunning 14 tests\n'+result(1)
        with self.assertRaises(ValueError):P.diff_counts(text)

    def test_duplicate_outer_in_same_executable_rejected(self):
        text=suite(14)+'running 14 tests\n'+result(14)
        with self.assertRaises(ValueError):P.diff_counts(text)

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
