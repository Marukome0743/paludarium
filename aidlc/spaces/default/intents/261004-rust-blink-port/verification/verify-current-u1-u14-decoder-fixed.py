"""Retain historical predicates and bind the separately authorized decoder fix."""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
path = Path(__file__).with_name('verify-current-u1-u14-source-bound.py')
spec = importlib.util.spec_from_file_location('u1_u14_decoder_current', path)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def main():
    original.historical()
    original.current(
        binding_name='u14-decoder-u1-execution-binding.json',
        manifest_name='u14-decoder-originals-manifest.json',
        sanitizer_binding_name='u14-decoder-sanitizer-binding.json',
        sanitizer_folder_name='u14-decoder-sanitizer-originals-38319817478',
        sanitizer_options={
            'head': 'b45158d3f2b941fd6aa1c685089af893780e1059',
            'run': 38319817478,
            'workflow': '.github/workflows/u14-fuzz.yml',
            'job_prefix': '',
        },
    )


if __name__ == '__main__':
    main()
