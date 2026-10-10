"""Approved Step20 machine-artifact preservation, exclusive and lossless."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value,message):
    if not value:raise ValueError(message)


def regular(path):
    need(path.is_file() and not any(p.is_symlink() for p in (path,*path.parents)),'missing/linked input')
    return path.read_bytes()


def preserve(module,run,output):
    receipt_path=Path(str(module)+'.receipt.json')
    receipt_bytes=regular(receipt_path);receipt=json.loads(receipt_bytes)
    module_bytes=regular(module)
    need(digest(module_bytes)==receipt['module_sha256'],'module does not match receipt')
    files={'module.wasm':module_bytes,'build-receipt.json':receipt_bytes}
    physical={module:module_bytes,receipt_path:receipt_bytes}
    for name,expected in receipt['source_files'].items():
        need(name and not Path(name).is_absolute() and '\\' not in name and all(p not in ('','.','..') for p in name.split('/')),'unsafe source name')
        raw=regular(ROOT/name);need(digest(raw)==expected,'source changed: '+name)
        files['source/'+name]=raw;physical[ROOT/name]=raw
    for path in sorted(run.rglob('*')):
        need(not path.is_symlink(),'linked raw run')
        if path.is_file():
            raw=regular(path);files['run/'+path.relative_to(run).as_posix()]=raw;physical[path]=raw
    report=json.loads(files['run/observations.json'])
    need(report['module_sha256']==receipt['module_sha256'] and report['source_digest']==receipt['source_digest'],'run/source/module substitution')
    sidecar=Path(str(output)+'.receipt.json')
    need(not output.exists() and not sidecar.exists(),'archive output already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    manifest={n:dict(sha256=digest(b),bytes=len(b)) for n,b in sorted(files.items())}
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for name,raw in files.items():archive.writestr(name,raw)
        archive.writestr('archive-manifest.json',json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(output) as archive:
        need(set(archive.namelist())==set(files)|{'archive-manifest.json'},'archive inventory differs')
        need(all(archive.read(n)==raw for n,raw in files.items()),'archive bytes differ')
    need(all(regular(p)==raw for p,raw in physical.items()),'source/artifact changed during archive')
    result=dict(schema=1,path=str(output),sha256=digest(output.read_bytes()),bytes=output.stat().st_size,
                files=len(files)+1,source_files=len(receipt['source_files']),source_digest=receipt['source_digest'],
                module_sha256=receipt['module_sha256'],all_extracted_bytes_match=True)
    with sidecar.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('module','run','output'):p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();print(json.dumps(preserve(a.module,a.run,a.output)))
