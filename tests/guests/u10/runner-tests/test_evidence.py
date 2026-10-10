import pathlib
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from evidence import digest, static_elf, validate
import evidence
import copy


def elf(*, pie=False, interpreter=False, needed=False):
    image = bytearray(512)
    image[:7] = b'\x7fELF\x02\x01\x01'
    struct.pack_into('<HH', image, 16, 3 if pie else 2, 62)
    struct.pack_into('<Q', image, 32, 64)
    count = 1 + int(pie) + int(interpreter)
    struct.pack_into('<HH', image, 54, 56, count)
    struct.pack_into('<IIQQQQQQ', image, 64, 1, 5, 0, 0, 0, 512, 512, 4096)
    if pie:
        struct.pack_into('<IIQQQQQQ', image, 120, 2, 6, 400, 400, 0, 32, 32, 8)
        struct.pack_into('<qQ', image, 400, 1 if needed else 7, 0)
        struct.pack_into('<qQ', image, 416, 0, 0)
    if interpreter:
        struct.pack_into('<IIQQQQQQ', image, 64 + (count - 1) * 56, 3, 4, 450, 450, 0, 16, 16, 1)
    return image


class BuildEvidence(unittest.TestCase):
    def test_name_metadata_source_exact(self):
        helper=evidence.u14_overlay_module()
        evidence.verify_name_metadata(dict(metadata_build_source_sha256=helper.NAME_SOURCE,binaries={'aube':{'source_sha256':helper.NAME_SOURCE}}),helper)

    def test_name_metadata_or_binary_source_tamper(self):
        for field in ('metadata','binary'):
            helper=evidence.u14_overlay_module()
            receipt=dict(metadata_build_source_sha256=helper.NAME_SOURCE,binaries={'aube':{'source_sha256':helper.NAME_SOURCE}})
            if field=='metadata':receipt['metadata_build_source_sha256']=helper.ZIP_SOURCE
            else:receipt['binaries']['aube']['source_sha256']=helper.ZIP_SOURCE
            with self.assertRaises(ValueError):evidence.verify_name_metadata(receipt,helper)

    def zip_metadata(self):
        helper=evidence.u14_overlay_module()
        dependency=dict(name='zip',req='=9.0.4',source=helper.REGISTRY,uses_default_features=False,features=['deflate'])
        packages=[dict(name='zip',version='9.0.4',source=helper.REGISTRY)]+[
            dict(name=n,dependencies=[dict(dependency)]) for n in ('aube-registry','aube-runtime')]
        receipt=dict(metadata_manifest_sha256=helper.ZIP_MANIFEST,binaries={'aube':{'manifest_sha256':helper.ZIP_MANIFEST}})
        return helper,packages,receipt

    def test_zip_metadata_exact(self):
        helper,packages,receipt=self.zip_metadata()
        evidence.verify_zip_metadata(receipt,packages,helper)

    def test_zip_metadata_duplicate_or_wrong_version(self):
        for kind in ('duplicate','version','source'):
            helper,packages,receipt=self.zip_metadata()
            if kind=='duplicate':packages.append(copy.deepcopy(packages[0]))
            else:packages[0][kind]='wrong'
            with self.assertRaises(ValueError):evidence.verify_zip_metadata(receipt,packages,helper)

    def test_zip_metadata_dependency_constraints(self):
        for field,value in [('req','^8'),('uses_default_features',True),('features',[]),('source','other')]:
            helper,packages,receipt=self.zip_metadata();packages[1]['dependencies'][0][field]=value
            with self.assertRaises(ValueError):evidence.verify_zip_metadata(receipt,packages,helper)

    def test_zip_metadata_manifest_missing_or_original(self):
        for target in ('metadata','binary'):
            helper,packages,receipt=self.zip_metadata()
            if target=='metadata':del receipt['metadata_manifest_sha256']
            else:receipt['binaries']['aube']['manifest_sha256']='0'*64
            with self.assertRaises(ValueError):evidence.verify_zip_metadata(receipt,packages,helper)

    def test_push_never_runs_diagnostic_or_formal_measurement(self):
        root=pathlib.Path(__file__).resolve().parents[4]
        diagnostic=(root/'.github/workflows/u14-cost-diagnostic.yml').read_text()
        self.assertIn("  diagnostic-v2:\n    if: github.event_name == 'workflow_dispatch'\n",diagnostic)
        acceptance=(root/'.github/workflows/u14-wasm-acceptance.yml').read_text()
        self.assertIn("- name: Frozen paired full-probe performance\n        if: matrix.environment == 'node' && github.event_name == 'workflow_dispatch'",acceptance)

    def test_accepts_static_exec(self):
        self.assertTrue(static_elf(elf()))

    def test_accepts_self_relocating_static_pie(self):
        self.assertTrue(static_elf(elf(pie=True)))

    def test_rejects_external_interpreter(self):
        with self.assertRaisesRegex(ValueError, 'interpreter'):
            static_elf(elf(pie=True, interpreter=True))

    def test_rejects_needed_library_without_interpreter(self):
        with self.assertRaisesRegex(ValueError, 'DT_NEEDED'):
            static_elf(elf(pie=True, needed=True))

    def test_rejects_wrong_architecture(self):
        data = elf()
        struct.pack_into('<H', data, 18, 183)
        with self.assertRaisesRegex(ValueError, 'x86-64'):
            static_elf(data)

    def test_rejects_truncated_dynamic_table(self):
        data = elf(pie=True)
        struct.pack_into('<Q', data, 120 + 32, 31)
        with self.assertRaisesRegex(ValueError, 'dynamic table'):
            static_elf(data)

    def test_rejects_tampered_binary_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for name in ('probe', 'aube'):
                (root / name).write_bytes(elf())
            receipt = {'exit': 0, 'source_unchanged': True, 'binaries': {n: {'sha256': digest(root / n)} for n in ('probe', 'aube')}}
            (root / 'aube').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'hash differs'):
                validate(root, receipt)
