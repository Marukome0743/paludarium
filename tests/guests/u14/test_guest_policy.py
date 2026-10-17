import copy
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from guest_policy import EXCEPTION, generate, verify

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('u10_evidence_for_u14', ROOT / 'tests/guests/u10/evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class GuestPolicy(unittest.TestCase):
    def test_zip_policy_does_not_add_exception(self):
        from guest_policy import generate_zip
        from unittest.mock import patch
        import hashlib
        from types import SimpleNamespace
        actual = hashlib.sha256
        def selected(raw):
            return SimpleNamespace(hexdigest=lambda:'b08d900a0b72764922da18bb0aec4b6598a8de58050babd9a6d59b6baefe7b89') if raw == self.lock else actual(raw)
        with patch('guest_policy.hashlib.sha256', side_effect=selected):
            config, receipt = generate_zip(self.root, self.inherited, self.lock)
        self.assertEqual(config, generate(self.root,self.inherited,self.lock)[0])
        self.assertEqual(receipt['exception'], EXCEPTION)

    def test_zip_policy_wrong_lock_rejected(self):
        from guest_policy import generate_zip
        with self.assertRaisesRegex(ValueError, 'zip advisory lock'):
            generate_zip(self.root, self.inherited, self.lock)

    def setUp(self):
        self.root = (ROOT / 'deny.toml').read_bytes()
        self.inherited = evidence.guest_policy(self.root, evidence.LICENSE_EXCEPTION)
        self.lock = ('[[package]]\nname="unsafe-libyaml"\nversion="0.2.11"\n'
                     'source="registry+https://github.com/rust-lang/crates.io-index"\n').encode()

    def test_exact_exception_and_receipt(self):
        config, receipt = generate(self.root, self.inherited, self.lock)
        verify(self.root, self.inherited, self.lock, config, receipt)
        self.assertIn(evidence.LICENSE_SUFFIX, config)
        self.assertEqual(config.replace(b'["RUSTSEC-2024-0449"]', b'[]'), self.inherited)

    def test_other_id(self):
        exception = dict(EXCEPTION, id='RUSTSEC-2026-0001')
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited, self.lock, exception)

    def test_other_version(self):
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited, self.lock.replace(b'0.2.11', b'0.2.12'))

    def test_other_package(self):
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited, self.lock.replace(b'unsafe-libyaml', b'other'))

    def test_other_source(self):
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited, self.lock.replace(b'crates.io-index', b'other-index'))

    def test_duplicate_lock_package(self):
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited, self.lock + self.lock)

    def test_root_changed(self):
        with self.assertRaises(ValueError):
            generate(self.root + b'\n', self.inherited, self.lock)

    def test_root_existing_ignore(self):
        with self.assertRaises(ValueError):
            generate(self.root.replace(b'ignore = []', b'ignore = ["another"]'), self.inherited, self.lock)

    def test_inherited_policy_changed(self):
        with self.assertRaises(ValueError):
            generate(self.root, self.inherited + b'\n', self.lock)

    def test_config_tampered(self):
        config, receipt = generate(self.root, self.inherited, self.lock)
        with self.assertRaises(ValueError):
            verify(self.root, self.inherited, self.lock, config + b'\n', receipt)

    def test_receipt_hash_tampered(self):
        config, receipt = generate(self.root, self.inherited, self.lock)
        receipt['config_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            verify(self.root, self.inherited, self.lock, config, receipt)

    def test_approval_rationale_tampered(self):
        config, receipt = generate(self.root, self.inherited, self.lock)
        receipt = copy.deepcopy(receipt)
        receipt['exception']['approved_date'] = '2025-01-01'
        with self.assertRaises(ValueError):
            verify(self.root, self.inherited, self.lock, config, receipt)

    def test_other_audit_failure_propagates(self):
        build_spec = importlib.util.spec_from_file_location('u10_build_for_u14', ROOT / 'tests/guests/u10/build.py')
        sys.path.insert(0, str(ROOT / 'tests/guests/u10'))
        module = importlib.util.module_from_spec(build_spec)
        build_spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            with self.assertRaises(subprocess.CalledProcessError):
                module.command([sys.executable, '-c', 'raise SystemExit(1)'], ROOT,
                               pathlib.Path(temporary) / 'audit.log')


if __name__ == '__main__':
    unittest.main()
