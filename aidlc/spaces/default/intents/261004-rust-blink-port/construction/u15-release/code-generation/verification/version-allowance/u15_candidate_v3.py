"""U15 formal verification entry v3: the 15-file allowance at the signed head a54315f9 (not adopted).

Extension approved by the person on 2026-10-18 after the first v3 run refused
on .github/workflows/release-check.yml ("この 7 ファイルも a54315f9 のバイト列の
固定で許可に足し、もう一度実行してください。中身は U15 のレビューと試験で確かめる、
と明記してください。"): the 7 Step 14b files that the old chain's binding-v4
pins (EXTRA_FILES) get an exact-bytes allowance. Old bytes = the binding-v4
pin = the blobs at bb197e04, 57a8c96f, 1ceae86c and be45; current bytes = the
a54315f9 blob = the SHA-256 fixed in binding-10. Their old bytes are shown to
the old chain driver and its validator children only (v2 and the inner chain
do not read them). The allowed set is exactly 15 files (ALLOWED_PATHS_15):
v2's 8 plus these 7. For every exact-bytes file this command proves only that
the bytes are the signed-head a54315f9 bytes of U15's approved Steps 13-14b;
their content is checked by U15's review and tests (and the a54315f9 CI), not
by this command.

Same design and command-line contract as u15_candidate_v2.py (binding-09), the
adopted command, which is kept byte-unchanged as history (HISTORY_V2). This
entry executes u15_candidate_v2.py from its exact pinned bytes as a library and
calls its verify unchanged, so every v2 check runs: through v2 the binding-08
entry (signed head bb197e04, its stored CI and performance original, the
version-only proofs), the adopted U14 Step46 entry with binding-07, U11, U2,
U1 and the old-chain pins.

Layering (v2 hard-requires bb197e04 as its head):
  - v2 runs unchanged on its recorded bb197e04 evidence. bb197e04's records
    stay as the parent proof.
  - v3 adds the signed head a54315f9 (child of bb197e04, U15 Step 14b, 12
    files) and its stored CI (8 runs, attempt-1 job lists, each run's job set
    equal to the job set of the same workflow at bb197e04 in binding-08).
  - Of the 8 allowed files (unchanged set: Cargo.lock, fuzz/Cargo.lock,
    packages/paludarium-wasm/package.json, Cargo.toml, README.md,
    docs/release.md, tests/release/test_policy.py,
    tests/release/test_package.py), Step 14b changed only docs/release.md and
    tests/release/test_policy.py. For these two (MOVED), v3 proves the current
    bytes = the a54315f9 blob = the bound SHA-256, and the bb197e04 blob = the
    bytes v2 pins (binding-09). Only for these two, v3 shows v2 the bb197e04
    bytes through the unchanged historical_child.View, so v2's own checks run
    as recorded. For the other six (STAY), v3 proves the current bytes = the
    a54315f9 blob = the bb197e04 blob = the bound SHA-256.
  - v2 then shows all 8 files at their old bytes to the inner chain, and v3
    gives the same 8 old bytes to the old chain driver and its validators.
Nothing else is allowed. If the chain refuses on any other path (for example a
Step 14b file pinned by the old chain), the refusal stands.

Command line: `--entry-sha256 <hex> --binding-sha256 <hex>`, in this order.
Argument or pin mismatch: exit 2 before any check, nothing written. A refused
check: exit 1 and refusal.json; a pass: exit 0 and result.json, both in a fresh
run-<ns>-<pid>/ folder. `--logical-child` runs the same hash check first.

No guest, build, CI, measurement or publish is started, and no live GitHub
query is made.
"""
import copy,hashlib,json,os,re,runpy,subprocess,sys,time,traceback,types
from pathlib import Path

OWN=Path(__file__).resolve().parent
SELF=Path(__file__).resolve()
ROOT=next(p for p in OWN.parents if (p/'Cargo.toml').is_file())
INTENT='aidlc/spaces/default/intents/261004-rust-blink-port/'
LOOP=INTENT+'construction/u15-release/code-generation/verification/version-allowance/'
V2_ENTRY=LOOP+'u15_candidate_v2.py'
V2_ENTRY_SHA256='b78f867e4baf0a2ccae6f0b6daf4751383069db7913f58fc78a6375b63183ed5'
V2_BINDING='binding-09.json'
V2_BINDING_SHA256='687fee0c4a25147aab064ff101b742a8145d5cb46ea608295146745a524e3649'
# The adopted v2 command (entry, binding, regressions) stays byte-unchanged (history).
HISTORY_V2={V2_ENTRY:V2_ENTRY_SHA256,LOOP+V2_BINDING:V2_BINDING_SHA256,
    LOOP+'test_u15_candidate_v2.py':'57c0727fbfe71716fbd386227292f8d69171d7b5e7ac499f5e277c188fd53b7f'}
PARENT='bb197e04db6387eb0c37222c25f60814524ab173'
JIT_HEAD='1ceae86ce303a1019e97ac7d162ce0efa9fadd50'
BRANCH='codex/build-and-test'
ALLOWED_PATHS=('Cargo.lock','Cargo.toml','README.md','docs/release.md','fuzz/Cargo.lock','packages/paludarium-wasm/package.json',
    'tests/release/test_package.py','tests/release/test_policy.py')
MOVED=('docs/release.md','tests/release/test_policy.py')
STAY=tuple(p for p in ALLOWED_PATHS if p not in MOVED)
# The 12 files of U15 Step 14b (a54315f9).
HEAD_FILES=('.github/workflows/release-check.yml','.github/workflows/release.yml','.github/workflows/u15-acceptance.yml','docs/release.md',
    'scripts/release/acceptance.py','scripts/release/check.py','scripts/release/policy.py','tests/release/test_acceptance.py','tests/release/test_api.py',
    'tests/release/test_check.py','tests/release/test_policy.py','tests/release/test_publish_adapter.py')
# The 7 Step 14b files pinned by the old chain (binding-v4), allowed at their a54315f9 bytes (approved extension).
EXTRA_FILES=('.github/workflows/release-check.yml','.github/workflows/release.yml','scripts/release/check.py','scripts/release/policy.py',
    'tests/release/test_api.py','tests/release/test_check.py','tests/release/test_publish_adapter.py')
ALLOWED_PATHS_15=tuple(sorted((*ALLOWED_PATHS,*EXTRA_FILES)))
# The Step 14b files outside every pin of the adopted chain (not byte-checked by this command).
OTHER_STEP14B=tuple(p for p in HEAD_FILES if p not in MOVED and p not in EXTRA_FILES)
OUTSIDE_PINS=('.github/workflows/u15-acceptance.yml','scripts/release/acceptance.py','tests/release/test_acceptance.py')
REQUIRED_RUNS=('CI','Release package checks','Release package checks','U1 U14 current-source evidence','U12 current full quality','U13 current full quality',
    'U14 current full quality','U14 fresh thirteen target ASan and LSan')
PERFORMANCE_RUN='U14 current full quality'
PERFORMANCE_PATH=INTENT+'construction/u15-release/code-generation/verification/ci-a54315f9/u14-quality-39096893624/u11-node/performance/observations.json'
BINDING='binding-10.json'
BINDING_SHA256='44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e'
SCHEMA=10
REPOSITORY='Marukome0743/paludarium'
USAGE='usage: u15_candidate_v3.py --entry-sha256 <64 hex> --binding-sha256 <64 hex>'
HEX40=re.compile(r'[0-9a-f]{40}');HEX64=re.compile(r'[0-9a-f]{64}')
sha=lambda b:hashlib.sha256(b).hexdigest()
_V2=None

def need(value,message):
    if not value:raise ValueError(message)

def check_pins(entry,binding):
    need(isinstance(entry,str) and HEX64.fullmatch(entry) is not None,'--entry-sha256 must be 64 lowercase hex digits')
    need(isinstance(binding,str) and HEX64.fullmatch(binding) is not None,'--binding-sha256 must be 64 lowercase hex digits')
    need(entry==sha(SELF.read_bytes()),'--entry-sha256 differs from the SHA-256 of this entry file')
    need(binding==sha((OWN/BINDING).read_bytes()),'--binding-sha256 differs from the SHA-256 of '+BINDING)
    need(binding==BINDING_SHA256,'--binding-sha256 differs from the binding pinned by this entry')
    return entry,binding

def command_line_pins(argv):
    need(len(argv)==5 and argv[1]=='--entry-sha256' and argv[3]=='--binding-sha256',USAGE)
    return check_pins(argv[2],argv[4])

def v2():
    """The adopted v2 entry module, executed from its exact pinned bytes."""
    global _V2
    if _V2 is None:
        path=ROOT/V2_ENTRY;need(not path.is_symlink(),'symlinked v2 entry')
        raw=path.read_bytes();need(sha(raw)==V2_ENTRY_SHA256,'v2 entry bytes differ from the pinned SHA-256')
        module=types.ModuleType('u15_candidate_v2');module.__file__=str(path)
        exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
        need(module.BINDING==V2_BINDING and module.BINDING_SHA256==V2_BINDING_SHA256 and module.ALLOWED_PATHS==ALLOWED_PATHS,'v2 entry pins differ')
        _V2=module
    return _V2

def nc():return v2().nc()
def view_class():return v2().view_class()

def load_binding(pin):
    need(HEX64.fullmatch(pin) is not None,'binding SHA-256 required')
    need(pin==BINDING_SHA256,'binding SHA-256 differs from the binding pinned by this entry')
    raw=nc().read(LOOP+BINDING);need(sha(raw)==pin,'binding bytes differ from the pinned SHA-256')
    return json.loads(raw)

def verify_base(b):
    """binding-10 names the unchanged v2 entry and binding-09; returns (binding-09, binding-08, binding-07, binding-02)."""
    need(b['schema']==SCHEMA and b['repository']==REPOSITORY,'binding schema/repository differs')
    need(set(b)=={'schema','purpose','repository','v2','approval','head','parent','head_chain','ci','ci_jobs','performance','moved_files','stay_files','old_chain_extra','history_v2'},'binding-10 key set differs')
    need(OTHER_STEP14B==OUTSIDE_PINS and len(ALLOWED_PATHS_15)==15,'allowed path constants differ')
    need(b['v2']=={'entry':{'path':V2_ENTRY,'sha256':V2_ENTRY_SHA256},'binding':{'name':V2_BINDING,'sha256':V2_BINDING_SHA256}},'v2 entry/binding differs')
    V=v2();b9=V.load_binding(V2_BINDING_SHA256);b8,b7,b2=V.verify_base(b9)
    return b9,b8,b7,b2

def verify_history_v2(b):
    need(b.get('history_v2')==HISTORY_V2,'v2 history pin set differs')
    m=nc()
    for rel,pin in sorted(HISTORY_V2.items()):need(not (ROOT/rel).is_symlink() and sha(m.read(rel))==pin,'v2 history file changed: '+rel)
    return dict(sorted(HISTORY_V2.items()))

def git_blob_id(commit,rel):return nc().git('rev-parse','--verify',commit+':'+rel).decode().strip()

def verify_head(b,b8):
    """Signed head a54315f9: Verified, child of bb197e04, the 12 Step 14b files, stored CI completed/success at the head."""
    m=nc();head=b['head']
    need(isinstance(head,str) and HEX40.fullmatch(head) is not None and head!=PARENT and head!=b8['parent'],'signed head differs')
    need(b['parent']==PARENT==b8['head'],'parent differs from the binding-08 signed head')
    chain=[PARENT,head];need(b['head_chain']==chain,'signed chain differs from bb197e04 -> head')
    # Expected job sets: the job set of the same workflow at bb197e04 (binding-08), not a copy of the new records.
    parent_jobs={b8['ci']['runs'][rid]['name']:names for rid,names in b8['ci_jobs']['expected'].items()}
    runs_entry=b['ci']['runs'];need(isinstance(runs_entry,dict) and runs_entry,'CI run binding missing')
    need(all(e['name'] in parent_jobs for e in runs_entry.values()),'CI run has no workflow at the parent head')
    jobs_entry={'path':b['ci_jobs']['path'],'sha256':b['ci_jobs']['sha256'],'expected':{rid:parent_jobs[e['name']] for rid,e in runs_entry.items()},'allowed_skipped':{},'attempt_1_failures':{}}
    sub={'ci':b['ci'],'head_chain':chain,'ci_jobs':jobs_entry}
    runs=m.verify_ci(sub,head);jobs=m.verify_ci_jobs(sub,head,runs)
    need(sorted(r['name'] for r in runs.values())==sorted(REQUIRED_RUNS),'CI run set differs from the required runs')
    need(all(r['run_attempt']==1 for r in runs.values()),'CI run is not a first attempt')
    ci=json.loads(m.read(b['ci']['path']))
    need(ci['branch']=={'name':BRANCH,'head':head},'CI branch head differs')
    files=ci['commits'][-1].get('files')
    need(isinstance(files,list) and sorted(files)==sorted(HEAD_FILES) and len(files)==len(HEAD_FILES),'signed commit file list differs')
    need(v2().v1().u14().u11().changed_paths(PARENT,head)==sorted(HEAD_FILES),'local git changes of the signed commit differ')
    c=ci['compare']
    need(c['base']==PARENT and c['head']==head and c['merge_base']==PARENT and c['status']=='ahead' and c['ahead_by']==1 and c['behind_by']==0 and c['total_commits']==1 and c['commits']==[head],'compare differs from bb197e04...head')
    need(len(c['files'])==len(HEAD_FILES) and sorted(f['filename'] for f in c['files'])==sorted(HEAD_FILES),'compare file list differs')
    for f in c['files']:need(f['sha']==git_blob_id(head,f['filename']),'compare blob differs from local git: '+f['filename'])
    listed=ci['runs_listed_for_head']
    need(listed['total_count']==len(listed['ids'])==len(runs) and sorted(str(i) for i in listed['ids'])==sorted(runs),'CI run listing for the head differs')
    d=json.loads(m.read(b['ci_jobs']['path']))
    need(all(r['total_count']==len(r['jobs']) for r in d['runs']),'CI job count differs from the API total')
    perf=b['performance'];need(perf['path']==PERFORMANCE_PATH,'performance original path differs')
    need(runs.get(str(perf['run_id']),{}).get('name')==PERFORMANCE_RUN,'performance run is not the U14 full-quality run')
    performance,_=m.verify_performance({'performance':perf},head,runs)
    return dict(head=head,parent=PARENT,head_chain=chain,changed_paths=sorted(HEAD_FILES),
        runs={rid:dict(name=r['name'],run_attempt=r['run_attempt']) for rid,r in sorted(runs.items())},jobs={rid:len(r['jobs']) for rid,r in sorted(jobs.items())},
        job_sets='equal to the same workflow at bb197e04 (binding-08)',ci_sha256=b['ci']['sha256'],ci_jobs_sha256=b['ci_jobs']['sha256'],
        performance_a54315f9=dict(run_id=perf['run_id'],**performance))

def verify_files(b,b9,head):
    """MOVED: current = a54315f9 blob, bb197e04 blob = v2's pin; STAY: current = a54315f9 blob = bb197e04 blob. Returns (summary, bb197e04 mapping)."""
    m=nc();moved=b['moved_files'];stay=b['stay_files']
    need(isinstance(moved,dict) and set(moved)==set(MOVED) and len(moved)==len(MOVED),'moved allowance differs from the authorized path set')
    need(isinstance(stay,dict) and set(stay)==set(STAY) and len(stay)==len(STAY),'unchanged allowance differs from the authorized path set')
    need(tuple(sorted({*moved,*stay}))==ALLOWED_PATHS,'allowed path set differs')
    names=list(ALLOWED_PATHS);new=m.git_blobs(head,names);par=m.git_blobs(PARENT,names)
    v2pins={p:e['new_sha256'] for p,e in b9['old_chain_files'].items()}
    mapping={};summary={}
    for p in MOVED:
        e=moved[p];need(isinstance(e,dict) and set(e)=={'bb197e04_sha256','new_sha256'},'moved entry differs: '+p)
        need(e['bb197e04_sha256']==v2pins.get(p)==sha(par[p]),'moved file bb197e04 pin differs: '+p)
        current=m.read(p)
        need(sha(current)==e['new_sha256']==sha(new[p]),'moved file differs from binding/signed head: '+p)
        need(e['new_sha256']!=e['bb197e04_sha256'],'moved allowance is not a change: '+p)
        mapping[str(ROOT/p)]=par[p];summary[p]=dict(kind='exact-bytes',bb197e04_sha256=e['bb197e04_sha256'],a54315f9_sha256=e['new_sha256'],shown_to_v2='bb197e04 bytes')
    for p in STAY:
        pin=stay[p];current=m.read(p)
        need(isinstance(pin,str) and sha(current)==pin==sha(new[p])==sha(par[p]),'allowed file differs from the signed head: '+p)
        summary[p]=dict(a54315f9_sha256=pin,equals_bb197e04=True)
    return summary,mapping

def verify_extra(b,head):
    """The 7 old-chain-pinned Step 14b files: old = binding-v4 pin = bb197e04/57a8c96f/1ceae86c/be45 blobs; current = a54315f9 blob = bound SHA-256."""
    m=nc();V=v2();extra=b['old_chain_extra'];pins=V.old_chain_pins()
    need(isinstance(extra,dict) and set(extra)==set(EXTRA_FILES) and len(extra)==len(EXTRA_FILES),'old-chain extra allowance differs from the authorized path set')
    need(not set(EXTRA_FILES)&set(ALLOWED_PATHS),'old-chain extra allowance overlaps the v2 allowance')
    names=list(EXTRA_FILES);new=m.git_blobs(head,names);par=m.git_blobs(PARENT,names)
    prior=m.git_blobs(V.v1().PRIOR_HEAD,names);base=m.git_blobs(JIT_HEAD,names);logical=m.git_blobs(m.LOGICAL_HEAD,names)
    mapping={};summary={}
    for p in names:
        e=extra[p];need(isinstance(e,dict) and set(e)=={'old_sha256','new_sha256'},'old-chain extra entry differs: '+p)
        need(e['old_sha256']==pins.get(p)==sha(par[p])==sha(prior[p])==sha(base[p])==sha(logical[p]),'old-chain extra old pin differs: '+p)
        current=m.read(p)
        need(sha(current)==e['new_sha256']==sha(new[p]),'old-chain extra file differs from binding/signed head: '+p)
        need(e['new_sha256']!=e['old_sha256'],'old-chain extra allowance is not a change: '+p)
        mapping[str(ROOT/p)]=par[p];summary[p]=dict(kind='exact-bytes',old_sha256=e['old_sha256'],a54315f9_sha256=e['new_sha256'],shown_to='old chain driver and validators (bb197e04 bytes)',scope=EXACT_SCOPE_V3)
    return summary,mapping

def verify(b,reuse_compat=True):
    """binding-10 checks, then the adopted v2 entry's verify (with only the two Step 14b files at their bb197e04 bytes)."""
    b9,b8,_,_=verify_base(b)
    history=verify_history_v2(b)
    head=verify_head(b,b8)
    files,bb_map=verify_files(b,b9,head['head'])
    extra,extra_map=verify_extra(b,head['head'])
    with view_class()(bb_map) as view:inner,mapping=v2().verify(b9,reuse_compat)
    read={c['path'] for c in view.calls};need(set(bb_map)<=read,'v2 checks did not read the moved files through the bb197e04 view')
    mapping8={k:v for k,v in mapping.items() if k in {str(ROOT/p) for p in ALLOWED_PATHS}}
    need(sorted(str(Path(k).relative_to(ROOT)) for k in mapping8)==list(ALLOWED_PATHS),'v2 logical view does not cover the 8 allowed paths')
    need(not set(mapping)&set(extra_map),'v2 and v3 extra logical views overlap')
    full={**mapping,**extra_map}
    shown=sorted(str(Path(k).relative_to(ROOT)) for k in full if str(Path(k).relative_to(ROOT)) in set(ALLOWED_PATHS_15))
    need(shown==list(ALLOWED_PATHS_15),'logical view does not cover exactly the 15 allowed paths')
    summary=dict(v2=inner,u15_a54315f9=dict(head=head,files=files,old_chain_extra=extra,history_v2=history,allowed_paths=list(ALLOWED_PATHS_15),layering=LAYERING))
    return summary,full

def logical_child(argv):
    need(len(argv)==7,'internal child argv differs')
    entry,pin,outdir,validator,result_file=argv[2:]
    check_pins(entry,pin)
    m=nc();_,mapping=verify(load_binding(pin),reuse_compat=False)
    v=Path(validator);need(v.parent==m.OLD and v.name in m.VALIDATORS,'validator outside the reused old set')
    out=Path(outdir);need(out.parent==OWN and out.name.startswith('run-') and out.is_dir(),'child receipt folder differs')
    View=view_class()
    sys.argv=[str(v),result_file];sys.path[0]=str(v.parent)
    with View(mapping) as view:runpy.run_path(str(v),run_name='__main__')
    calls={}
    for c in view.calls:key=str(Path(c['path']).relative_to(ROOT));calls[key]=calls.get(key,0)+1
    with (out/(v.name+'-'+str(time.time_ns())+'.view-calls.json')).open('x') as f:json.dump(dict(validator=v.name,logical_reads=calls,code_loads=view.code_loads),f,indent=2)

def guarded_run(entry,pin,out,receipts,real):
    """subprocess.run replacement for the reused old chain: only the old child argv/options are accepted."""
    m=nc()
    def run(argv,**kw):
        need(kw==dict(cwd=ROOT,capture_output=True,timeout=900),'unexpected child options')
        need(len(argv)==4 and argv[0]==sys.executable and argv[1]=='-B' and Path(argv[2]).parent==m.OLD and Path(argv[2]).name in m.VALIDATORS,'unexpected old child argv')
        actual=[sys.executable,'-B',str(SELF),'--logical-child',entry,pin,str(out),argv[2],argv[3]]
        start=time.monotonic();row=dict(old_argv=argv,actual_argv=actual)
        try:r=real(actual,**kw)
        except subprocess.TimeoutExpired:
            row.update(timeout=True,seconds=time.monotonic()-start);receipts.append(row);raise
        row.update(timeout=False,exit=r.returncode,seconds=time.monotonic()-start,stdout_sha256=sha(r.stdout),stderr_sha256=sha(r.stderr),stderr_tail=r.stderr[-2000:].decode('utf-8','replace'))
        receipts.append(row);return r
    return run

def run_old_chain(entry,pin,out,mapping8,trace):
    """The reused old chain driver; its parent process is shown the 8 allowed files at their old bytes only."""
    m=nc();fc=m.load('reused_final_candidate',m.OLD/'final_candidate.py');receipts=[]
    fc.subprocess=types.SimpleNamespace(run=guarded_run(entry,pin,out,receipts,subprocess.run),TimeoutExpired=subprocess.TimeoutExpired)
    before={p.name for p in m.OLD.glob('formal-candidate-*')};saved=sys.argv;calls=[]
    try:
        sys.argv=[str(m.OLD/'final_candidate.py')]
        with view_class()(mapping8) as view:
            try:fc.main()
            finally:calls=view.calls
    finally:
        sys.argv=saved
        created=sorted(m.OLD/n for n in {p.name for p in m.OLD.glob('formal-candidate-*')}-before)
        trace['old_chain_outputs']=[str(p.relative_to(ROOT)) for p in created]
        trace['old_chain_parent_logical_reads']=sorted({str(Path(c['path']).relative_to(ROOT)) for c in calls})
        with (out/'children.json').open('x') as f:json.dump(receipts,f,indent=2)
    need(len(created)==1,'old chain output folder ambiguous')
    result=json.loads((created[0]/'result.json').read_bytes())
    need(result['source_compatibility']=='PASS' and result['unit_completed'] is False,'old chain did not pass')
    need(len(receipts)==4 and all(r.get('exit')==0 for r in receipts),'old chain children incomplete')
    pinned=set(v2().old_chain_pins())&set(ALLOWED_PATHS_15);need(pinned<=set(trace['old_chain_parent_logical_reads']),'old chain did not read its pinned allowed files through the logical view')
    return dict(output=str(created[0].relative_to(ROOT)),result=result,children=len(receipts),parent_logical_reads=trace['old_chain_parent_logical_reads']),created[0]

LAYERING=('v2（採用済み、binding-09）は変えずに、記録済みのbb197e04の証拠（署名head・CI・性能の原本）の上で実行する。bb197e04の記録は親の証明として残す。'
    'v3は署名head a54315f9（親bb197e04、U15 Step 14bの12ファイル）とそのCI（8 run）を足す。8ファイルのうちStep 14bで変わったのはdocs/release.mdとtests/release/test_policy.pyだけで、'
    'v3はこの2つの今のbytesがa54315f9のblobであることを確かめ、v2にはこの2つだけをbb197e04のbytes（binding-09の固定）としてviewで見せる。ほかの6つは今のbytes・a54315f9・bb197e04が同じ。'
    'v2は8ファイルを古いbytesとして中のchainに見せ、v3は同じ古いbytesを旧chainの親とvalidatorに見せる。'
    'さらにv3は、旧chainのbinding-v4が固定するStep 14bの7ファイルの今のbytesがa54315f9のblobであることを確かめ、その古いbytes（bb197e04のblob）を旧chainの親とvalidatorだけに見せる（v2と中のchainはこの7つを読まない）。'
    '許可の集合は15ファイルである。')
EXACT_FILES_ALL=('README.md','docs/release.md','tests/release/test_package.py','tests/release/test_policy.py',*EXTRA_FILES)
ALLOWANCE_V3=('許すのは15ファイルだけである。版の行（0.0.0 → 0.1.0）だけの証明が4つ（Cargo.lock・fuzz/Cargo.lock・packages/paludarium-wasm/package.json・Cargo.toml）、'
    '署名済みhead a54315f9のbytesへの固定が11（'+'・'.join(EXACT_FILES_ALL)+'。README.md・tests/release/test_package.pyのbytesはbb197e04とa54315f9で同じ）。'
    '署名headはa54315f9（親bb197e04）、CIの記録はa54315f9の8 runである。FR10.1・U15の受け入れはGAPのまま。')
ALLOWANCE_V3_EN=('Exactly 15 files are allowed: 4 version-only proofs (0.0.0 -> 0.1.0: Cargo.lock, fuzz/Cargo.lock, packages/paludarium-wasm/package.json, Cargo.toml) and 11 exact-bytes pins to the signed head a54315f9 ('
    +', '.join(EXACT_FILES_ALL)+'). Signed head a54315f9 (parent bb197e04); CI records are the 8 runs at a54315f9. FR10.1 and U15 acceptance remain GAP.')
EXACT_SCOPE_V3=('bytesの固定の11ファイル（'+'・'.join(EXACT_FILES_ALL)+'）について、このコマンドが証明するのは、今のbytesがU15の承認済みSteps 13〜14bの署名済みhead a54315f9のbytesであることだけである。'
    '中身はU15のレビューと試験（とa54315f9のCI）で確かめるものであり、このコマンドでは確かめていない。')
EXACT_SCOPE_V3_EN=("For all 11 exact-bytes files this command proves only that the bytes are the signed-head a54315f9 bytes of U15's approved Steps 13-14b; "
    "their content is checked by U15's review and tests (and the a54315f9 CI), not by this command.")
CLAIMED_V3=('a54315f9が署名済み（Verified）で親がbb197e04、変更はStep 14bの12ファイルだけであり（commit・compare・local git）、保存したCI 8 runがそのheadでattempt 1のまま全job成功であること。各runのjobの集合はbb197e04の同じworkflowと同じ',
    'docs/release.md・tests/release/test_policy.pyの今のbytesがa54315f9のblob（binding-10の固定）であり、そのbb197e04のbytesがv2の固定（binding-09）と同じであること。README.md・tests/release/test_package.pyと版の4ファイルは、今のbytes・a54315f9・bb197e04のblobが同じであること',
    '旧chainのbinding-v4が固定するStep 14bの7ファイル（'+'・'.join(EXTRA_FILES)+'）の今のbytesがa54315f9のblob（binding-10の固定）であり、古いbytesがbinding-v4の固定・bb197e04・57a8c96f・1ceae86c・be45のblobであること',
    'a54315f9で1回だけ測った性能（FR8.3）の原本を確かめて記録したこと（run 39096893624）')
NOT_CLAIMED_V3=('15ファイル以外の差を許すこと。この入口が許すのは、版の行だけの証明4つ（Cargo.lock・fuzz/Cargo.lock・packages/paludarium-wasm/package.json・Cargo.toml）と、署名済みhead a54315f9のbytesへの固定11（'+'・'.join(EXACT_FILES_ALL)+'）だけである',
    'bytesの固定の11ファイルの中身が正しいこと。'+EXACT_SCOPE_V3,
    'Step 14bのファイルのうち、採用済みのchainのどの固定にも入っていない3ファイル（'+'・'.join(OUTSIDE_PINS)+'）のbytes。このコマンドはこの3つのbytesを確かめない（commitとcompareのファイル一覧に入っていることだけを確かめる）。bytesと中身はU15のレビュー・試験とa54315f9のCIで確かめる',
    'FR10.1とU15の受け入れ（U15_acceptanceはGAPのまま）',
    'unitの完了・正式な確認コマンドとしての採用（人の承認が必要）',
    'a54315f9での性能（FR8.3）の正式な合格。原本は検査して記録するだけで、moduleのreceiptには束ねていない。内側の性能の根拠は今までどおり1ceae86c（binding-02）',
    '新しい測定・CI・build・publish')

def statements():
    V=v2();claimed,_=V.statements()
    # v2's own CLAIMED_V2[1] (the 4 exact files are bb197e04 bytes) is replaced by CLAIMED_V3[1].
    need(claimed[-1]==V.CLAIMED_V2[1],'v2 claimed list differs')
    return [*claimed[:-1],*CLAIMED_V3],list(NOT_CLAIMED_V3)

def u15_scope_v3(scope,u15_v2,u15_v3):
    out=v2().u15_scope_v2(scope,u15_v2);claimed,not_claimed=statements()
    version=dict(out['u15_version']);version.update(head=u15_v3['head']['head'],parent=PARENT,scope=ALLOWANCE_V3,claimed=claimed,not_claimed=not_claimed)
    old_chain=dict(out['u15_old_chain']);old_chain.update(claimed=list(CLAIMED_V3[1:3]),not_claimed=list(NOT_CLAIMED_V3[:3]),exact_bytes_scope=EXACT_SCOPE_V3,exact_bytes_scope_en=EXACT_SCOPE_V3_EN,
        allowed_paths=list(ALLOWED_PATHS_15),v2_allowed_paths=list(ALLOWED_PATHS),old_chain_files=sorted([*old_chain['old_chain_files'],*EXTRA_FILES]))
    note=dict(head=u15_v3['head']['head'],parent=PARENT,changed_paths=u15_v3['head']['changed_paths'],moved=list(MOVED),stay=list(STAY),old_chain_extra=list(EXTRA_FILES),
        outside_pins=list(OUTSIDE_PINS),allowed_paths=list(ALLOWED_PATHS_15),layering=LAYERING,
        approval=['人の承認（2026-10-18）：「この案で u15_candidate_v3.py と binding-10.json を作り、回帰と独立レビューの後に採用を伺ってください。」',
            '人の承認（2026-10-18）：「この 7 ファイルも a54315f9 のバイト列の固定で許可に足し、もう一度実行してください。中身は U15 のレビューと試験で確かめる、と明記してください。」'])
    return {**out,'u15_version':version,'u15_old_chain':old_chain,'u15_a54315f9':note}

def v2_summary_for_result(s):
    """v2's summary with its exact-bytes row text (bb197e04 bytes) restated for v3; data values unchanged."""
    s=copy.deepcopy(s)
    for p,row in s['u15']['old_chain_files'].items():
        if 'scope' in row:row['scope']=EXACT_SCOPE_V3;row['v2_layer']='v2はこのファイルをbb197e04のbytesとして確かめた（MOVEDの2つはv3がbb197e04のbytesをviewで見せた）'
    return s

def refuse_arguments(error):
    print('REFUSED: '+str(error),file=sys.stderr)
    return 2

def main(argv):
    if argv[1:2]==['--logical-child']:return logical_child(argv)
    try:entry,pin=command_line_pins(argv)
    except (ValueError,OSError) as error:return refuse_arguments(error)
    out=OWN/('run-'+str(time.time_ns())+'-'+str(os.getpid()));out.mkdir()
    trace=dict(stage='load binding')
    try:
        b=load_binding(pin)
        trace['stage']='verify (binding-10, then the adopted v2 entry with the two Step 14b files at their bb197e04 bytes)'
        before,mapping=verify(b)
        mapping15={k:v for k,v in mapping.items() if k in {str(ROOT/p) for p in ALLOWED_PATHS_15}}
        trace['stage']='old chain (final_candidate.main and its validators)'
        old,old_output=run_old_chain(entry,pin,out,mapping15,trace)
        trace['stage']='claim scope'
        _,_,_,b2=verify_base(b);s2=before['v2'];s14=s2['u14'];u11=v2().u14().u11()
        scope=u15_scope_v3(v2().u14().u14_scope(u11.head_scope(u11.u2().claim_scope(b2,old_output,s14['u11']['u2']['u1']['module_receipt']),s14['u11']['u11']['head']),s14['u14']),s2['u15'],before['u15_a54315f9'])
        trace['stage']='re-verify'
        after,_=verify(b);need(after==before,'inputs changed during validation')
        check_pins(entry,pin)
        claimed,not_claimed=statements()
        result=dict(u15_candidate_v3='PASS',command_line=dict(entry_sha256=entry,binding_sha256=pin),binding=BINDING,binding_sha256=pin,entry_sha256=entry,
            v2_entry=dict(path=V2_ENTRY,sha256=V2_ENTRY_SHA256,binding=V2_BINDING,binding_sha256=V2_BINDING_SHA256),
            v2_layer=v2_summary_for_result(s2),u15_a54315f9=before['u15_a54315f9'],old_chain=old,claim_scope=scope,
            allowed_paths=list(ALLOWED_PATHS_15),allowance_statement=ALLOWANCE_V3,allowance_statement_en=ALLOWANCE_V3_EN,layering=LAYERING,
            allowance=dict(version_only=['Cargo.lock','Cargo.toml','fuzz/Cargo.lock','packages/paludarium-wasm/package.json'],
                exact_bytes={**{p:'a54315f9 (= bb197e04)' for p in ('README.md','tests/release/test_package.py')},**{p:'a54315f9' for p in ('docs/release.md','tests/release/test_policy.py',*EXTRA_FILES)}},
                outside_pins_not_byte_checked=list(OUTSIDE_PINS),
                exact_bytes_scope=EXACT_SCOPE_V3,exact_bytes_scope_en=EXACT_SCOPE_V3_EN),
            claimed=claimed,not_claimed=not_claimed,
            ci_inputs='stored hash-bound JSON only; no live GitHub query at check time',
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False)
        with (out/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
        print(json.dumps(dict(output=str(out.relative_to(ROOT)),u15_candidate_v3='PASS',old_chain_source_compatibility=old['result']['source_compatibility'],FR10_1='GAP',U15_acceptance='GAP',unit_completed=False)))
        return 0
    except BaseException as error:
        with (out/'refusal.json').open('x',encoding='utf-8') as f:
            json.dump(dict(error=str(error),refused_at=trace,traceback=traceback.format_exc(),allowed_paths=list(ALLOWED_PATHS_15),allowance=ALLOWANCE_V3+' 許可は広げていない。',
                FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False),f,indent=2,ensure_ascii=False)
        print('REFUSED: '+str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main(sys.argv))
