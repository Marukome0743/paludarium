"""Focused rejection tests for current evidence supersession; no network calls."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('checker', Path(__file__).with_name('verify-current-u10-probe-aube-native.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class EvidenceBindingTests(unittest.TestCase):
    def setUp(self):
        self.old = {'status': 'complete', 'source_sha': 'old', 'ci_run': 1}
        self.trace = {'source_sha': 'old', 'ci_run': 1}
        self.proof = {'status': 'complete', 'baseline_sha': 'old', 'baseline_run': 1,
                      'extra_sources': checker.EXTRA.copy()}
        self.job = {'started_at': '2026-10-10T03:38:36Z', 'completed_at': '2026-10-10T03:43:57Z'}
        self.artifact = {'name': 'native', 'expired': False, 'created_at': '2026-10-10T03:43:50Z',
                         'id': 2, 'workflow_run': {'head_sha': 'new', 'id': 3}}

    def test_preserved_baseline_and_extra_sources_accepted(self):
        checker.current_binding(self.old, self.trace, self.proof)

    def test_stale_supersession_baseline_rejected(self):
        self.proof['baseline_sha'] = 'other'
        with self.assertRaises(ValueError):
            checker.current_binding(self.old, self.trace, self.proof)

    def test_pending_current_proof_rejected(self):
        self.proof['status'] = 'pending'
        with self.assertRaises(ValueError):
            checker.current_binding(self.old, self.trace, self.proof)

    def test_skipped_new_comparison_source_rejected(self):
        self.proof['extra_sources'].pop()
        with self.assertRaises(ValueError):
            checker.current_binding(self.old, self.trace, self.proof)

    def test_latest_artifact_in_actual_job_window_accepted(self):
        old = copy.deepcopy(self.artifact)
        old.update(id=1, created_at='2026-10-10T03:40:00Z')
        self.assertEqual(checker.select_artifact([old, self.artifact], 'native', 'new', 3, self.job, 2)['id'], 2)

    def test_stale_artifact_id_rejected(self):
        with self.assertRaises(ValueError):
            checker.select_artifact([self.artifact], 'native', 'new', 3, self.job, 1)

    def test_artifact_outside_job_window_rejected(self):
        self.artifact['created_at'] = '2026-10-10T04:00:00Z'
        with self.assertRaises(ValueError):
            checker.select_artifact([self.artifact], 'native', 'new', 3, self.job, 2)

    def test_artifact_wrong_source_rejected(self):
        with self.assertRaises(ValueError):
            checker.select_artifact([self.artifact], 'native', 'old', 3, self.job, 2)

    def test_timeout_and_nonfinite_duration_rejected(self):
        for seconds, timeout in ((31, False), (float('nan'), False), (1, True)):
            with self.subTest(seconds=seconds, timeout=timeout), self.assertRaises(ValueError):
                checker.successful({'exit': 0, 'timed_out': timeout, 'wall_seconds': seconds})


if __name__ == '__main__':
    unittest.main()
