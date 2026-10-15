"""Diagnostic builder input and receipt boundaries."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('cost_builder', ROOT / 'scripts/build-u14-cost-profile.py')
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class CostBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'target')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in BUILD.LOCKS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixed')
        for name in ['crates', 'packages/paludarium-wasm', 'scripts', 'tests/guests/u14']:
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.enterContext(patch.object(BUILD, 'ROOT', self.root))

    def test_all_fixed_locks_are_in_population(self):
        self.assertEqual(set(BUILD.source_snapshot()), set(BUILD.LOCKS))

    def test_source_change_changes_digest(self):
        before = BUILD.source_snapshot()
        (self.root / 'crates/code.rs').write_text('source')
        self.assertNotEqual(before, BUILD.source_snapshot())

    def test_linked_source_rejected(self):
        (self.root / 'scripts/code.py').symlink_to(self.root / 'Cargo.lock')
        with self.assertRaisesRegex(ValueError, 'linked source'):
            BUILD.source_snapshot()

    def test_generated_target_is_excluded(self):
        (self.root / 'crates/target').mkdir()
        (self.root / 'crates/target/code.rs').write_text('generated')
        self.assertEqual(set(BUILD.source_snapshot()), set(BUILD.LOCKS))

    def test_installed_dependency_is_excluded(self):
        (self.root / 'packages/paludarium-wasm/node_modules').mkdir()
        (self.root / 'packages/paludarium-wasm/node_modules/data.json').write_text('{}')
        self.assertEqual(set(BUILD.source_snapshot()), set(BUILD.LOCKS))

    def test_digest_is_sha256(self):
        self.assertEqual(BUILD.digest(b''), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')

    def test_fixed_lock_edit_changes_population(self):
        before = BUILD.source_snapshot()
        (self.root / 'Cargo.lock').write_bytes(b'changed')
        self.assertNotEqual(before['Cargo.lock'], BUILD.source_snapshot()['Cargo.lock'])
