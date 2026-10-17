"""The approved guest exception cannot widen the root license policy."""
import copy
import hashlib
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from evidence import (LICENSE_EXCEPTION, LICENSE_SUFFIX, digest, guest_policy,
                      policy_receipt_valid, record_source_after, snapshot)


class PolicyTests(unittest.TestCase):
    def test_exact_root_inheritance(self):
        root = b'[licenses]\nallow = ["Apache-2.0"]\nconfidence-threshold = 0.93\n'
        self.assertEqual(guest_policy(root, LICENSE_EXCEPTION), root + LICENSE_SUFFIX)

    def test_other_crate_rejected(self):
        exception = copy.deepcopy(LICENSE_EXCEPTION)
        exception['crate'] = 'other@1.0.9'
        with self.assertRaises(ValueError):
            guest_policy(b'', exception)

    def test_other_version_rejected(self):
        exception = copy.deepcopy(LICENSE_EXCEPTION)
        exception['crate'] = 'webpki-root-certs@1.0.10'
        with self.assertRaises(ValueError):
            guest_policy(b'', exception)

    def test_extra_license_rejected(self):
        exception = copy.deepcopy(LICENSE_EXCEPTION)
        exception['allow'].append('MIT')
        with self.assertRaises(ValueError):
            guest_policy(b'', exception)

    def test_receipt_detects_policy_license_and_audit_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            root = b'[licenses]\nallow = ["Apache-2.0"]\n'
            config = directory / 'aube-deny.toml'
            config.write_bytes(guest_policy(root, LICENSE_EXCEPTION))
            license_file = directory / 'licenses/webpki-root-certs-1.0.9-CDLA-Permissive-2.0.txt'
            license_file.parent.mkdir()
            license_file.write_bytes(b'complete test license fixture\n')
            receipt = {'audits': {'probe': 0, 'aube': 0}, 'license_policy': {
                'exception': copy.deepcopy(LICENSE_EXCEPTION),
                'crate_source': 'registry+https://github.com/rust-lang/crates.io-index',
                'root_config_sha256': hashlib.sha256(root).hexdigest(),
                'guest_config_sha256': digest(config), 'license_sha256': digest(license_file)}}
            policy_receipt_valid(directory, receipt, root)
            with self.assertRaises(ValueError):
                policy_receipt_valid(directory, receipt, root + b'changed')
            license_file.write_bytes(b'truncated')
            with self.assertRaises(ValueError):
                policy_receipt_valid(directory, receipt, root)
            license_file.write_bytes(b'complete test license fixture\n')
            receipt['audits']['aube'] = 4
            with self.assertRaises(ValueError):
                policy_receipt_valid(directory, receipt, root)

    def test_failure_still_records_source_after(self):
        with tempfile.TemporaryDirectory() as temporary:
            upstream = pathlib.Path(temporary)
            (upstream / 'Cargo.lock').write_bytes(b'fixed source')
            receipt = {'exit': 1, 'source_before': snapshot(upstream)}
            record_source_after(upstream, receipt)
            self.assertEqual(receipt['source_before'], receipt['source_after'])
            self.assertTrue(receipt['source_unchanged'])
            self.assertEqual(receipt['exit'], 1)

    def test_changed_source_invalidates_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            upstream = pathlib.Path(temporary)
            source = upstream / 'Cargo.lock'
            source.write_bytes(b'original')
            receipt = {'exit': 0, 'source_before': snapshot(upstream)}
            source.write_bytes(b'changed')
            record_source_after(upstream, receipt)
            self.assertFalse(receipt['source_unchanged'])
            self.assertEqual(receipt['exit'], 1)
            self.assertIn('source_error', receipt)


if __name__ == '__main__':
    unittest.main()
