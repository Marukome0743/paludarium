"""10月13日版の設定を照合し、旧U10検証は10月12日版の設定投影で保持する。"""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
RECORD = Path(__file__).resolve().parents[1]
ROOT = RECORD.parents[4]
V5 = RECORD / 'construction/u5-threads-futex/code-generation/verification'
sys.path.insert(0, str(V5))
import preview_source_binding as preview

OLD = b' version = "2.11.0",'
PREVIOUS = b' version = "2.11.1-preview.20261012.1",'
CURRENT = b' version = "2.11.1-preview.20261013.1",'
WRAPPER_SHA = '34bd0c1cb858ff1ed07167b31cd7eeddf8ac0e69f03d15c2c1e8fada5f01e790'


def projected_configuration(signed, current):
    """許可する差分は一つのバージョン文字列のみ。その他の全bytesを保持する。"""
    preview.need(signed.count(OLD) == 1 and CURRENT not in signed,
                 'unexpected signed configuration')
    preview.need(current == signed.replace(OLD, CURRENT),
                 'configuration delta exceeds exact October 13 preview version')
    return signed.replace(OLD, PREVIOUS)


@contextmanager
def previous_configuration_view(repository, signed_configuration):
    """旧検証の入力だけを投影し、旧述語と実際の設定ファイルを変更しない。"""
    original = preview.safe_read
    def read(root, name):
        raw = original(root, name)
        if root == repository and name == 'mise.toml':
            return projected_configuration(signed_configuration, raw)
        return raw
    preview.safe_read = read
    try:
        yield
    finally:
        preview.safe_read = original


def main():
    binding = json.loads(preview.safe_read(
        RECORD, 'construction/u1-skeleton/code-generation/verification/step66-quality-binding.json'))
    preview.need(binding['head'] == preview.HEAD, 'signed baseline differs')
    signed = preview.subprocess.check_output(
        ['jj', '--ignore-working-copy', 'file', 'show', '-r', preview.HEAD, 'mise.toml'],
        cwd=ROOT, timeout=60)
    preview.need(preview.sha(signed) == binding['quality_inputs']['mise.toml'],
                 'signed configuration digest differs')
    actual = preview.safe_read(ROOT, 'mise.toml')
    projected_configuration(signed, actual)
    old = RECORD / 'verification/verify-current-u10-record-bound.py'
    before = old.read_bytes()
    # The old wrapper is additionally pinned by bytes before it is executed.
    preview.need(hashlib.sha256(before).hexdigest() == WRAPPER_SHA, 'old U10 wrapper changed')
    spec = importlib.util.spec_from_file_location('preserved_u10_preview12', old)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    with previous_configuration_view(ROOT, signed):
        legacy.main()
    preview.need(preview.safe_read(ROOT, 'mise.toml') == actual,
                 'actual configuration changed during verification')
    preview.need(old.read_bytes() == before, 'old U10 wrapper changed during verification')
    print(json.dumps({
        'current_configuration': 'exact signed 2.11.0 to 2.11.1-preview.20261013.1 delta',
        'legacy_configuration_view': '2.11.1-preview.20261012.1; predicates unchanged',
        'legacy_u10_checks': 'passed',
        'scope': 'saved evidence audit, not fresh guest execution',
    }, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
