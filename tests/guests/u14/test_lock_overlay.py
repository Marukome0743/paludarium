"""Synthetic boundary fixtures; real pinned lock/audit is checked by guest build."""
import copy
import importlib.util
import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'u10'))
import lock_overlay as overlay
import evidence

spec = importlib.util.spec_from_file_location('u14_overlay_build_tests', HERE.parent / 'u10/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def fixture_lock():
    rows = ['version = 4\n']
    for index in range(602):
        rows.append(f'[[package]]\nname = "fixture-{index}"\nversion = "1.0.0"\n')
    rows.append('[[package]]\nname = "unsafe-libyaml"\nversion = "0.2.11"\n'
                f'source = "{overlay.REGISTRY}"\n')
    rows.append('[[package]]\nname = "rustls"\nversion = "0.23.45"\n'
                f'source = "{overlay.REGISTRY}"\nchecksum = "{overlay.OLD_CHECKSUM}"\n'
                'dependencies = ["fixture-1"]\n')
    return '\n'.join(rows).encode()


def elf():
    data = bytearray(512)
    data[:7] = b'\x7fELF\x02\x01\x01'
    struct.pack_into('<HH', data, 16, 2, 62)
    struct.pack_into('<Q', data, 32, 64)
    struct.pack_into('<HH', data, 54, 56, 1)
    struct.pack_into('<IIQQQQQQ', data, 64, 1, 5, 0, 0, 0, 512, 512, 4096)
    return data


class OverlayFixture:
    def setUp(self):
        self.original = fixture_lock()
        self.updated = self.original.replace(b'"0.23.45"', b'"0.23.46"').replace(
            overlay.OLD_CHECKSUM.encode(), overlay.NEW_CHECKSUM.encode())
        # Only synthetic digest bindings differ. Package/byte rejection logic,
        # approved policy and the real production constants are not weakened.
        self.enterContext(patch.object(overlay, 'ORIGINAL', overlay.sha(self.original)))
        self.enterContext(patch.object(overlay, 'UPDATED', overlay.sha(self.updated)))
        self.enterContext(patch.object(evidence, 'u14_overlay_module', return_value=overlay))
        self.temporary = self.enterContext(tempfile.TemporaryDirectory())
        self.directory = pathlib.Path(self.temporary)
        self.upstream = self.directory / 'source/aube'
        self.upstream.mkdir(parents=True)
        (self.upstream / 'Cargo.lock').write_bytes(self.original)
        (self.upstream / 'Cargo.toml').write_text('[package]\nname="fixture"\nversion="1.0.0"\n')
        (self.upstream / '.rules').write_text('fixed rules fixture')
        for name, target in overlay.SOURCE_LINKS.items():
            (self.upstream / name).symlink_to(target)
        self.destination = self.directory / 'build-source/aube'
        before = evidence.snapshot(self.upstream)
        self.enterContext(patch.object(overlay, 'SOURCE', overlay.snapshot_sha(before)))
        self.enterContext(patch.object(overlay, 'BUILD_SOURCE', overlay.snapshot_sha(
            dict(before, **{'Cargo.lock': overlay.UPDATED}))))

    def prepare(self):
        return overlay.prepare(self.upstream, self.destination, 'u14-fixed-aube',
                               overlay.POLICY, evidence.snapshot)

    def pair_rejected(self, original=None, updated=None):
        with self.assertRaises(ValueError):
            overlay.validate_pair(self.original if original is None else original,
                                  self.updated if updated is None else updated, overlay.POLICY)

class OverlayTests(OverlayFixture, unittest.TestCase):
    def test_config_is_exact_approved_policy(self):
        lock = evidence.json_source_lock()
        self.assertEqual(lock['u14_aube_lock_overlay'], overlay.POLICY)
        self.assertEqual(lock['aube']['lock_sha256'], overlay.POLICY['original_lock_sha256'])

    def test_copy_only_changes_lock_and_finishes(self):
        receipt = self.prepare()
        overlay.finish(self.upstream, self.destination, receipt, evidence.snapshot)
        overlay.verify(receipt)
        self.assertEqual((self.upstream / 'Cargo.lock').read_bytes(), self.original)
        self.assertEqual((self.destination / 'Cargo.lock').read_bytes(), self.updated)

    def test_original_digest_changed(self):
        self.pair_rejected(original=self.original + b'\n', updated=self.updated + b'\n')

    def test_updated_digest_changed(self):
        self.pair_rejected(updated=self.updated + b'\n')

    def test_duplicate_rustls(self):
        extra = self.original[self.original.index(b'[[package]]\nname = "rustls"'):]
        self.pair_rejected(original=self.original + extra)

    def test_missing_rustls(self):
        self.pair_rejected(original=self.original.replace(b'name = "rustls"', b'name = "other"'))

    def test_wrong_old_version(self):
        self.pair_rejected(original=self.original.replace(b'0.23.45', b'0.23.44'))

    def test_wrong_new_version(self):
        self.pair_rejected(updated=self.updated.replace(b'0.23.46', b'0.23.47'))

    def test_wrong_registry(self):
        self.pair_rejected(original=self.original.replace(overlay.REGISTRY.encode(), b'registry+other'))

    def test_wrong_old_checksum(self):
        self.pair_rejected(original=self.original.replace(overlay.OLD_CHECKSUM.encode(), b'0' * 64))

    def test_wrong_new_checksum(self):
        self.pair_rejected(updated=self.updated.replace(overlay.NEW_CHECKSUM.encode(), b'0' * 64))

    def test_another_package_changed(self):
        self.pair_rejected(updated=self.updated.replace(b'fixture-2"', b'fixture-X"'))

    def test_dependencies_changed(self):
        self.pair_rejected(updated=self.updated.replace(b'["fixture-1"]', b'[]'))

    def test_lock_metadata_changed(self):
        self.pair_rejected(updated=self.updated.replace(b'version = 4', b'version = 3'))

    def test_unapproved_policy(self):
        with self.assertRaises(ValueError):
            overlay.updated_lock(self.original, dict(overlay.POLICY, to_version='0.23.47'))

    def test_non_u14_application(self):
        with self.assertRaises(ValueError):
            overlay.prepare(self.upstream, self.destination, None, overlay.POLICY, evidence.snapshot)

    def test_existing_build_copy_rejected(self):
        self.prepare()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_source_symlink_rejected(self):
        (self.upstream / 'link').symlink_to(self.upstream / 'Cargo.toml')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_known_link_absolute_target_rejected(self):
        link = self.upstream / 'AGENTS.md'
        link.unlink()
        link.symlink_to(self.upstream / '.rules')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_known_link_parent_escape_rejected(self):
        link = self.upstream / 'AGENTS.md'
        link.unlink()
        link.symlink_to('../aube/.rules')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_known_link_other_internal_target_rejected(self):
        link = self.upstream / 'AGENTS.md'
        link.unlink()
        link.symlink_to('Cargo.toml')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_known_link_target_content_changed_rejected(self):
        (self.upstream / '.rules').write_text('changed')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_known_build_link_change_after_prepare_rejected(self):
        receipt = self.prepare()
        link = self.destination / 'GEMINI.md'
        link.unlink()
        link.symlink_to('Cargo.toml')
        with self.assertRaises(ValueError):
            overlay.finish(self.upstream, self.destination, receipt, evidence.snapshot)

    def test_source_edit_after_prepare(self):
        receipt = self.prepare()
        (self.upstream / 'Cargo.toml').write_text('changed')
        with self.assertRaises(ValueError):
            overlay.finish(self.upstream, self.destination, receipt, evidence.snapshot)

    def test_source_edit_before_prepare(self):
        (self.upstream / 'Cargo.toml').write_text('already modified')
        with self.assertRaisesRegex(ValueError, 'original source digest'):
            self.prepare()

    def test_build_edit_after_prepare(self):
        receipt = self.prepare()
        (self.destination / 'Cargo.toml').write_text('changed')
        with self.assertRaises(ValueError):
            overlay.finish(self.upstream, self.destination, receipt, evidence.snapshot)

    def test_snapshot_rejects_other_file_and_lock_swap(self):
        receipt = self.prepare()
        for changed in (dict(receipt['build_source_before'], extra='0' * 64), receipt['source_before']):
            with self.assertRaises(ValueError):
                overlay.verify_snapshots(receipt['source_before'], changed)


class BuildIntegration(OverlayFixture, unittest.TestCase):
    """Fake external tools only; exercise real copy, receipt, policy and ELF gates."""
    def run_build(self, policy='u14-fixed-aube', failure=None, mutate=None):
        lock = evidence.json_source_lock()
        lock['aube']['lock_sha256'] = overlay.ORIGINAL
        license_path = self.directory / 'registry/LICENSE'
        license_path.parent.mkdir()
        license_path.write_text('Community Data License Agreement full fixture 2.1.')
        metadata = {'packages': [{'name': 'webpki-root-certs', 'version': '1.0.9',
            'license': 'CDLA-Permissive-2.0', 'source': overlay.REGISTRY,
            'manifest_path': str(license_path.with_name('Cargo.toml'))}]}
        commands = []

        def command(args, cwd, log, env=None):
            commands.append(args)
            if failure and failure in str(log):
                raise subprocess.CalledProcessError(1, args)
            if 'build' in args:
                name = 'aube' if 'aube' in args else 'probe'
                binary = self.directory / 'targets' / name / lock['target'] / 'release' / (
                    'aube' if name == 'aube' else 'paludarium-probe-u10')
                binary.parent.mkdir(parents=True)
                binary.write_bytes(elf())
                if mutate and name == 'aube':
                    (self.destination / 'Cargo.toml').write_text('changed')

        # Avoid recursively patching json.loads used by source_lock().
        with patch.object(builder, 'command', side_effect=command), \
             patch.object(builder.json, 'loads', side_effect=lambda data: metadata if 'packages' in data else lock), \
             patch.object(builder.subprocess, 'check_output', side_effect=lambda args, **kw:
                          json.dumps(metadata) if 'metadata' in args else 'fixture tool'), \
             patch.object(builder.subprocess, 'run'):
            builder.build(self.directory, policy)
        receipt = json.loads((self.directory / 'build-receipt.json').read_text())
        return receipt, commands

    def test_successful_overlay_build_receipt(self):
        receipt, commands = self.run_build()
        self.assertEqual(receipt['exit'], 0)
        with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(),
                          aube=receipt['aube'])):
            evidence.validate(self.directory, receipt)
        self.assertEqual(receipt['binaries']['aube']['lock_sha256'], overlay.UPDATED)
        aube_commands = [args for args in commands if str(self.destination / 'Cargo.toml') in args]
        self.assertEqual(len(aube_commands), 2)
        self.assertTrue(all('--locked' in args for args in aube_commands))

    def test_normal_build_keeps_original_and_no_overlay(self):
        receipt, _ = self.run_build(None)
        self.assertNotIn('lock_overlay', receipt)
        self.assertFalse(self.destination.exists())
        self.assertEqual(receipt['binaries']['aube']['lock_sha256'], overlay.ORIGINAL)

    def test_audit_failure_propagates_with_both_snapshots(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_build(failure='aube-dependencies')
        receipt = json.loads((self.directory / 'build-receipt.json').read_text())
        self.assertEqual(receipt['exit'], 1)
        overlay.verify(receipt['lock_overlay'])
        self.assertNotIn('aube', receipt['audits'])

    def test_source_mutation_invalidates_success(self):
        with self.assertRaises(ValueError):
            self.run_build(mutate=True)
        receipt = json.loads((self.directory / 'build-receipt.json').read_text())
        self.assertEqual(receipt['exit'], 1)
        self.assertFalse(receipt['source_unchanged'])

    def test_receipt_lock_swaps_and_metadata_mismatch_rejected(self):
        receipt, _ = self.run_build()
        root = (ROOT / 'deny.toml').read_bytes()
        for key in ('advisory_lock', 'metadata_lock_sha256'):
            changed = copy.deepcopy(receipt)
            changed[key] = self.original.decode() if key == 'advisory_lock' else overlay.ORIGINAL
            with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(), aube=receipt['aube'])):
                with self.assertRaises(ValueError):
                    evidence.policy_receipt_valid(self.directory, changed, root)

    def test_original_lock_binary_receipt_rejected(self):
        receipt, _ = self.run_build()
        receipt['binaries']['aube']['lock_sha256'] = overlay.ORIGINAL
        with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(), aube=receipt['aube'])):
            with self.assertRaisesRegex(ValueError, 'binary uses original lock'):
                evidence.validate(self.directory, receipt)

    def test_overlay_without_advisory_policy_rejected(self):
        receipt, _ = self.run_build()
        del receipt['advisory_policy']
        with self.assertRaisesRegex(ValueError, 'requires U14'):
            evidence.validate(self.directory, receipt)

    def test_metadata_edit_after_receipt_rejected(self):
        receipt, _ = self.run_build()
        (self.directory / 'aube-metadata.json').write_text('{}')
        with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(), aube=receipt['aube'])):
            with self.assertRaisesRegex(ValueError, 'metadata hash mismatch'):
                evidence.validate(self.directory, receipt)

    def test_source_edit_after_receipt_rejected(self):
        receipt, _ = self.run_build()
        (self.destination / 'Cargo.toml').write_text('changed after receipt')
        with self.assertRaisesRegex(ValueError, 'changed after receipt'):
            evidence.validate(self.directory, receipt)

    def test_overlay_advisory_failure_invalidates_receipt(self):
        receipt, _ = self.run_build()
        receipt['audits']['aube'] = 1
        with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(), aube=receipt['aube'])):
            with self.assertRaisesRegex(ValueError, 'dependency audits did not pass'):
                evidence.validate(self.directory, receipt)

    def test_extra_ignore_and_other_advisory_audit_rejected(self):
        receipt, _ = self.run_build()
        config = self.directory / 'aube-deny.toml'
        config.write_bytes(config.read_bytes().replace(b'"RUSTSEC-2024-0449"',
                           b'"RUSTSEC-2024-0449", "RUSTSEC-2026-0346"'))
        with patch.object(evidence, 'json_source_lock', return_value=dict(evidence.json_source_lock(), aube=receipt['aube'])):
            with self.assertRaisesRegex(ValueError, 'receipt/config'):
                evidence.policy_receipt_valid(self.directory, receipt, (ROOT / 'deny.toml').read_bytes())


if __name__ == '__main__':
    unittest.main()
