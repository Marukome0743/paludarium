"""U15 formal verification entry v4: the signed head e3c29d1d (U15 Step 17) on top of the adopted v3 (not adopted).

Approved plan Step 18: update the verification entry for the new head and, at
the same time, fix the four Minor findings left on entry v3
(pending-minor-fixes.md); after regressions and an independent review, the
person is asked whether to adopt it as the verification command.

Same design and command-line contract as u15_candidate_v3.py (binding-10), the
adopted command, which is kept byte-unchanged as history (HISTORY_V3). This
entry executes u15_candidate_v3.py from its exact pinned bytes as a library and
calls its verify unchanged, so every v3 check runs: the a54315f9 signed head and
its 8 stored runs, the 15-file allowance at the a54315f9 bytes, and through v3
the adopted v2 (bb197e04), v1, the U14 Step46 entry, U11, U2, U1 and the old
chain's pins.

Layering (v3 hard-requires a54315f9 as its head):
  - v3 runs unchanged on its recorded a54315f9 evidence. a54315f9's records
    stay as the parent proof.
  - v4 adds the signed head e3c29d1d (child of a54315f9, U15 Step 17, exactly
    the 7 files of HEAD_FILES, Verified) and its stored CI: 7 runs, each run's
    job set equal to the job set of the same workflow at a54315f9 (binding-10's
    ci-jobs-a54315f9.json), not a copy of the new records. Exactly one run, U12
    current full quality 39114110570, is allowed at attempt 2: in attempt 1
    exactly one job failed (RERUN_FAILED_JOB, name and id), attempt 2 re-ran
    only that job, every attempt-2 job succeeded and the attempt-2 job set is
    the parent's. Every other run must be attempt 1.
  - The allowed set stays exactly v3's 15 files; no path is added. All 7
    changed files are inside it (docs/release.md and
    tests/release/test_policy.py are v3's MOVED files, the other 5 are v3's
    EXTRA_FILES). For these 7, v4 proves current bytes = the e3c29d1d blob =
    the SHA-256 bound in binding-11, and the a54315f9 blob = v3's binding-10
    pin; only these 7 are shown to v3 at their a54315f9 bytes through the
    unchanged historical_child.View. For the other 8, v4 proves current bytes =
    the e3c29d1d blob = the a54315f9 blob = binding-10's pin = binding-11's
    pin.
  - v3 then shows its own old bytes to v2, the inner chain and the old chain,
    as recorded. v4's old chain driver and its validator children are given
    the same 15 old bytes, and the children re-run this entry (SELF = v4).
For every exact-bytes file this command proves only that the bytes are the
signed-head e3c29d1d bytes of U15's approved Steps 13-17; their content is
checked by U15's review and tests (and the e3c29d1d CI), not by this command.
Nothing else is allowed. If the chain refuses on any other path, the refusal
stands.

Command line: `--entry-sha256 <hex> --binding-sha256 <hex>`, in this order.
Argument or pin mismatch: exit 2 before any check, nothing written. A refused
check: exit 1 and refusal.json; a pass: exit 0 and result.json, both in a fresh
run-<ns>-<pid>/ folder. `--logical-child` runs the same hash check first.

No guest, build, CI, measurement or publish is started, and no live GitHub
query is made.
"""
import copy,hashlib,io,json,os,re,runpy,subprocess,sys,time,traceback,types,zipfile
from pathlib import Path

OWN=Path(__file__).resolve().parent
SELF=Path(__file__).resolve()
ROOT=next(p for p in OWN.parents if (p/'Cargo.toml').is_file())
INTENT='aidlc/spaces/default/intents/261004-rust-blink-port/'
LOOP=INTENT+'construction/u15-release/code-generation/verification/version-allowance/'
V3_ENTRY=LOOP+'u15_candidate_v3.py'
V3_ENTRY_SHA256='ebb6789417b48d7e8e8ef3c5ae8919483a85eda0ea85ecda5fbf001d74c2e798'
V3_BINDING='binding-10.json'
V3_BINDING_SHA256='44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e'
# The adopted v3 command (entry, binding, regressions) stays byte-unchanged (history).
HISTORY_V3={V3_ENTRY:V3_ENTRY_SHA256,LOOP+V3_BINDING:V3_BINDING_SHA256,
    LOOP+'test_u15_candidate_v3.py':'148960fa85fcc8074bc833e4c9d9aa086431b993b6990781cdb5b60fe970b068'}
PARENT='a54315f9493d6e9fb8d4792ffcefd12203540311'
GRANDPARENT='bb197e04db6387eb0c37222c25f60814524ab173'
BRANCH='codex/build-and-test'
# v3's allowed set (15 files), unchanged: no path is added.
ALLOWED_PATHS_15=('.github/workflows/release-check.yml','.github/workflows/release.yml','Cargo.lock','Cargo.toml','README.md','docs/release.md','fuzz/Cargo.lock',
    'packages/paludarium-wasm/package.json','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_package.py','tests/release/test_policy.py','tests/release/test_publish_adapter.py')
VERSION_ONLY=('Cargo.lock','Cargo.toml','fuzz/Cargo.lock','packages/paludarium-wasm/package.json')
# The 7 files of U15 Step 17 (e3c29d1d), all inside the 15.
HEAD_FILES=('docs/release.md','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_policy.py','tests/release/test_publish_adapter.py')
V3_MOVED=('docs/release.md','tests/release/test_policy.py')
V3_EXTRA_CHANGED=('scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py','tests/release/test_publish_adapter.py')
UNCHANGED_FILES=tuple(p for p in ALLOWED_PATHS_15 if p not in HEAD_FILES)
EXACT_FILES_ALL=tuple(p for p in ALLOWED_PATHS_15 if p not in VERSION_ONLY)
REQUIRED_RUNS=('CI','Release package checks','U1 U14 current-source evidence','U12 current full quality','U13 current full quality',
    'U14 current full quality','U14 fresh thirteen target ASan and LSan')
# The one allowed rerun: U12 current full quality, attempt 2 after exactly this failed job in attempt 1.
RERUN_RUN='39114110570'
RERUN_NAME='U12 current full quality'
RERUN_FAILED_JOB=('u11-programs / differential (macos-latest, safari)',117638480843)
ATTEMPT_1_FAILURES={RERUN_RUN:[RERUN_FAILED_JOB[1]]}
PERFORMANCE_RUN='U14 current full quality'
PERFORMANCE_PATH=INTENT+'construction/u15-release/code-generation/verification/ci-e3c29d1d/u14-quality-39114108809/u11-node/performance/observations.json'
PERFORMANCE_ZIP=INTENT+'construction/u15-release/code-generation/verification/ci-e3c29d1d/u14-quality-39114108809/artifact-zip/u11-node-12131882922.zip'
PERFORMANCE_ARTIFACT=dict(id=12131882922,name='u11-node',zip_path=PERFORMANCE_ZIP,member='performance/observations.json')
BINDING='binding-11.json'
BINDING_SHA256='fb466da7e8f7dadff7efb3645ee5e4f4a95c0eb867207be875387879cf6caca4'
SCHEMA=11
REPOSITORY='Marukome0743/paludarium'
USAGE='usage: u15_candidate_v4.py --entry-sha256 <64 hex> --binding-sha256 <64 hex>'
HEX40=re.compile(r'[0-9a-f]{40}');HEX64=re.compile(r'[0-9a-f]{64}')
sha=lambda b:hashlib.sha256(b).hexdigest()
_V3=None

def need(value,message):
    if not value:raise ValueError(message)

def rel(key):return str(Path(key).relative_to(ROOT))

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

def v3():
    """The adopted v3 entry module, executed from its exact pinned bytes."""
    global _V3
    if _V3 is None:
        path=ROOT/V3_ENTRY;need(not path.is_symlink(),'symlinked v3 entry')
        raw=path.read_bytes();need(sha(raw)==V3_ENTRY_SHA256,'v3 entry bytes differ from the pinned SHA-256')
        module=types.ModuleType('u15_candidate_v3');module.__file__=str(path)
        exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
        need(module.BINDING==V3_BINDING and module.BINDING_SHA256==V3_BINDING_SHA256 and module.ALLOWED_PATHS_15==ALLOWED_PATHS_15,'v3 entry pins differ')
        _V3=module
    return _V3

def nc():return v3().nc()
def view_class():return v3().view_class()

def load_binding(pin):
    need(HEX64.fullmatch(pin) is not None,'binding SHA-256 required')
    need(pin==BINDING_SHA256,'binding SHA-256 differs from the binding pinned by this entry')
    raw=nc().read(LOOP+BINDING);need(sha(raw)==pin,'binding bytes differ from the pinned SHA-256')
    return json.loads(raw)

def verify_constants():
    V=v3()
    need(len(ALLOWED_PATHS_15)==15 and tuple(sorted(ALLOWED_PATHS_15))==ALLOWED_PATHS_15==V.ALLOWED_PATHS_15,'allowed path set differs from v3')
    need(set(HEAD_FILES)<=set(ALLOWED_PATHS_15) and len(set(HEAD_FILES))==len(HEAD_FILES)==7,'changed files are not inside the 15 allowed paths')
    need(V3_MOVED==V.MOVED and set(V3_EXTRA_CHANGED)<=set(V.EXTRA_FILES) and set(HEAD_FILES)==set(V3_MOVED)|set(V3_EXTRA_CHANGED),'changed files differ from v3 MOVED and EXTRA_FILES')
    need(set(VERSION_ONLY)<=set(V.ALLOWED_PATHS) and not set(VERSION_ONLY)&set(HEAD_FILES),'version-only files differ')
    need(not set(V.OUTSIDE_PINS)&set(HEAD_FILES),'a file outside every pin changed')

def verify_base(b):
    """binding-11 names the unchanged v3 entry and binding-10; returns (binding-10, binding-09, binding-08, binding-07, binding-02)."""
    need(b['schema']==SCHEMA and b['repository']==REPOSITORY,'binding schema/repository differs')
    need(set(b)=={'schema','purpose','repository','v3','approval','head','parent','head_chain','ci','ci_jobs','attempt_1_failures','performance','changed_files','unchanged_files','history_v3'},'binding-11 key set differs')
    verify_constants()
    need(b['v3']=={'entry':{'path':V3_ENTRY,'sha256':V3_ENTRY_SHA256},'binding':{'name':V3_BINDING,'sha256':V3_BINDING_SHA256}},'v3 entry/binding differs')
    V=v3();b10=V.load_binding(V3_BINDING_SHA256);b9,b8,b7,b2=V.verify_base(b10)
    return b10,b9,b8,b7,b2

def verify_history_v3(b):
    need(b.get('history_v3')==HISTORY_V3,'v3 history pin set differs')
    m=nc()
    for r,pin in sorted(HISTORY_V3.items()):need(not (ROOT/r).is_symlink() and sha(m.read(r))==pin,'v3 history file changed: '+r)
    return dict(sorted(HISTORY_V3.items()))

def git_blob_id(commit,r):return nc().git('rev-parse','--verify',commit+':'+r).decode().strip()

def v3_pins(b10):
    """The a54315f9 SHA-256 that binding-10 fixes for each of the 15 files."""
    pins={**b10['stay_files'],**{p:e['new_sha256'] for p,e in b10['moved_files'].items()},**{p:e['new_sha256'] for p,e in b10['old_chain_extra'].items()}}
    need(tuple(sorted(pins))==ALLOWED_PATHS_15,'binding-10 pins do not cover the 15 allowed paths')
    return pins

def parent_job_sets(b10):
    """Job set of each workflow at a54315f9, from binding-10's stored job lists (not from the new records)."""
    m=nc();entry=b10['ci_jobs'];raw=m.read(entry['path']);need(sha(raw)==entry['sha256'],'parent CI job evidence bytes differ')
    d=json.loads(raw);need(d['repository']==REPOSITORY and d['head']==PARENT==b10['head'],'parent CI job evidence head differs')
    names={rid:e['name'] for rid,e in b10['ci']['runs'].items()};sets={}
    for r in d['runs']:
        need(str(r['id']) in names and r['name']==names[str(r['id'])] and r['run_attempt']==1 and 'attempt_1' not in r,'parent CI job run differs: '+str(r['id']))
        s=sorted(j[0] for j in r['jobs']);need(sets.setdefault(r['name'],s)==s,'parent job sets differ within a workflow: '+r['name'])
    need(set(sets)==set(names.values()),'parent CI job runs differ from binding-10')
    return sets

def verify_rerun(jobs,parent_jobs):
    """The one allowed attempt-2 run: exactly the recorded failed job in attempt 1, only it re-ran, all attempt-2 jobs success."""
    r=jobs[RERUN_RUN];a=r.get('attempt_1');need(r['name']==RERUN_NAME and r['run_attempt']==2 and isinstance(a,dict),'rerun run differs from the allowance')
    failed=[j for j in a['jobs'] if j[2]!='success']
    need(len(failed)==1 and failed[0][0]==RERUN_FAILED_JOB[0] and failed[0][1]==RERUN_FAILED_JOB[1] and failed[0][2]=='failure','attempt-1 failed job differs from the allowance')
    need(len(a['failures'])==1 and a['failures'][0]['job_id']==RERUN_FAILED_JOB[1] and a['failures'][0]['name']==RERUN_FAILED_JOB[0],'attempt-1 failure record differs from the allowance')
    need(a.get('total_count')==len(a['jobs']),'CI attempt 1 job count differs from the API total')
    need(all(j[2]=='success' for j in r['jobs']),'attempt-2 job not successful')
    need(sorted(j[0] for j in r['jobs'])==parent_jobs[RERUN_NAME]==sorted(j[0] for j in a['jobs']),'attempt-2 job set differs from the parent')
    rerun=[j for j in r['jobs'] if j[3]>=r['run_started_at']]
    need(len(rerun)==1 and rerun[0][0]==RERUN_FAILED_JOB[0],'attempt 2 re-ran other jobs')
    return dict(run_id=int(RERUN_RUN),name=RERUN_NAME,attempt_1_failed_job=dict(name=failed[0][0],id=failed[0][1]),attempt_2_rerun_job=dict(name=rerun[0][0],id=rerun[0][1]),
        attempt_2_jobs=len(r['jobs']),attempt_2_all_success=True,attempt_2_job_set='equal to the same workflow at a54315f9 (binding-10)',statement=RERUN_STATEMENT,statement_en=RERUN_STATEMENT_EN)

def verify_artifact(perf):
    """The performance original equals the member of the u11-node artifact ZIP whose SHA-256 is the API digest."""
    m=nc();a=perf['artifact']
    need(isinstance(a,dict) and set(a)=={'id','name','zip_path','digest','size_in_bytes','member'} and {k:a[k] for k in PERFORMANCE_ARTIFACT}==PERFORMANCE_ARTIFACT,'performance artifact entry differs')
    raw=m.read(a['zip_path']);need('sha256:'+sha(raw)==a['digest'] and len(raw)==a['size_in_bytes'],'performance artifact ZIP differs from the API digest')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:member=z.read(a['member'])
    except (zipfile.BadZipFile,KeyError) as error:raise ValueError('performance artifact ZIP member missing') from error
    need(member==m.read(perf['path']),'performance original differs from the artifact ZIP member')
    return dict(id=a['id'],name=a['name'],digest=a['digest'],size_in_bytes=a['size_in_bytes'],member=a['member'])

def verify_head(b,b10):
    """Signed head e3c29d1d: Verified, child of a54315f9, the 7 Step 17 files, stored CI completed/success at the head."""
    m=nc();head=b['head']
    need(isinstance(head,str) and HEX40.fullmatch(head) is not None and head not in (PARENT,GRANDPARENT),'signed head differs')
    need(b['parent']==PARENT==b10['head'],'parent differs from the binding-10 signed head')
    chain=[PARENT,head];need(b['head_chain']==chain,'signed chain differs from a54315f9 -> head')
    parent_jobs=parent_job_sets(b10)
    runs_entry=b['ci']['runs'];need(isinstance(runs_entry,dict) and runs_entry,'CI run binding missing')
    need(all(isinstance(e,dict) and e.get('name') in parent_jobs for e in runs_entry.values()),'CI run has no workflow at the parent head')
    need(b['attempt_1_failures']==ATTEMPT_1_FAILURES,'attempt-1 failure allowance differs from the one recorded rerun')
    need(runs_entry.get(RERUN_RUN,{}).get('name')==RERUN_NAME,'rerun run differs from the allowance')
    for rid,e in runs_entry.items():need(e.get('run_attempt')==(2 if rid==RERUN_RUN else 1),'CI run attempt differs from the allowance: '+rid)
    jobs_entry={'path':b['ci_jobs']['path'],'sha256':b['ci_jobs']['sha256'],'expected':{rid:parent_jobs[e['name']] for rid,e in runs_entry.items()},
        'allowed_skipped':{},'attempt_1_failures':copy.deepcopy(ATTEMPT_1_FAILURES)}
    sub={'ci':b['ci'],'head_chain':chain,'ci_jobs':jobs_entry}
    runs=m.verify_ci(sub,head);jobs=m.verify_ci_jobs(sub,head,runs)
    need(sorted(r['name'] for r in runs.values())==sorted(REQUIRED_RUNS),'CI run set differs from the required runs')
    for rid,r in runs.items():need(r['run_attempt']==(2 if rid==RERUN_RUN else 1),'CI run attempt differs from the allowance: '+rid)
    rerun=verify_rerun(jobs,parent_jobs)
    ci=json.loads(m.read(b['ci']['path']))
    need(ci['branch']=={'name':BRANCH,'head':head},'CI branch head differs')
    files=ci['commits'][-1].get('files')
    need(isinstance(files,list) and sorted(files)==sorted(HEAD_FILES) and len(files)==len(HEAD_FILES),'signed commit file list differs')
    need(v3().v2().v1().u14().u11().changed_paths(PARENT,head)==sorted(HEAD_FILES),'local git changes of the signed commit differ')
    c=ci['compare']
    need(c['base']==PARENT and c['head']==head and c['merge_base']==PARENT and c['status']=='ahead' and c['ahead_by']==1 and c['behind_by']==0 and c['total_commits']==1 and c['commits']==[head],'compare differs from a54315f9...head')
    need(len(c['files'])==len(HEAD_FILES) and sorted(f['filename'] for f in c['files'])==sorted(HEAD_FILES),'compare file list differs')
    for f in c['files']:need(f['sha']==git_blob_id(head,f['filename']),'compare blob differs from local git: '+f['filename'])
    listed=ci['runs_listed_for_head']
    need(listed['total_count']==len(listed['ids'])==len(runs) and sorted(str(i) for i in listed['ids'])==sorted(runs),'CI run listing for the head differs')
    d=json.loads(m.read(b['ci_jobs']['path']))
    need(all(r['total_count']==len(r['jobs']) for r in d['runs']),'CI job count differs from the API total')
    perf=b['performance'];need(perf['path']==PERFORMANCE_PATH,'performance original path differs')
    need(runs.get(str(perf['run_id']),{}).get('name')==PERFORMANCE_RUN and runs[str(perf['run_id'])]['run_attempt']==1,'performance run is not the U14 full-quality run')
    performance,_=m.verify_performance({'performance':{k:perf[k] for k in ('path','sha256','run_id','p','rows')}},head,runs)
    artifact=verify_artifact(perf)
    return dict(head=head,parent=PARENT,head_chain=chain,changed_paths=sorted(HEAD_FILES),
        runs={rid:dict(name=r['name'],run_attempt=r['run_attempt']) for rid,r in sorted(runs.items())},jobs={rid:len(r['jobs']) for rid,r in sorted(jobs.items())},
        job_sets='equal to the same workflow at a54315f9 (binding-10)',rerun=rerun,ci_sha256=b['ci']['sha256'],ci_jobs_sha256=b['ci_jobs']['sha256'],
        performance_e3c29d1d=dict(run_id=perf['run_id'],artifact=artifact,**performance))

def verify_files(b,b10,head):
    """Changed 7: current = e3c29d1d blob, a54315f9 blob = v3's pin; other 8: current = e3c29d1d blob = a54315f9 blob = v3's pin. Returns (summary, a54315f9 mapping)."""
    m=nc();changed=b['changed_files'];unchanged=b['unchanged_files']
    need(isinstance(changed,dict) and set(changed)==set(HEAD_FILES) and len(changed)==len(HEAD_FILES),'changed allowance differs from the authorized path set')
    need(isinstance(unchanged,dict) and set(unchanged)==set(UNCHANGED_FILES) and len(unchanged)==len(UNCHANGED_FILES),'unchanged allowance differs from the authorized path set')
    need(tuple(sorted({*changed,*unchanged}))==ALLOWED_PATHS_15,'allowed path set differs')
    pins=v3_pins(b10);names=list(ALLOWED_PATHS_15);new=m.git_blobs(head,names);par=m.git_blobs(PARENT,names)
    mapping={};summary={}
    for p in HEAD_FILES:
        e=changed[p];need(isinstance(e,dict) and set(e)=={'a54315f9_sha256','e3c29d1d_sha256'},'changed entry differs: '+p)
        need(e['a54315f9_sha256']==pins[p]==sha(par[p]),'changed file a54315f9 pin differs: '+p)
        current=m.read(p)
        need(sha(current)==e['e3c29d1d_sha256']==sha(new[p]),'changed file differs from binding/signed head: '+p)
        need(e['e3c29d1d_sha256']!=e['a54315f9_sha256'],'changed allowance is not a change: '+p)
        mapping[str(ROOT/p)]=par[p]
        summary[p]=dict(kind='exact-bytes',a54315f9_sha256=e['a54315f9_sha256'],e3c29d1d_sha256=e['e3c29d1d_sha256'],shown_to_v3='a54315f9 bytes (binding-10)',
            time_points=dict(a54315f9_sha256='a54315f9のblob（binding-10の固定。v4がv3にviewで見せたbytes）',e3c29d1d_sha256='e3c29d1dのblob（binding-11の固定）＝今の作業ツリーのbytes'),
            scope=EXACT_SCOPE_V4)
    for p in UNCHANGED_FILES:
        pin=unchanged[p];current=m.read(p)
        need(isinstance(pin,str) and sha(current)==pin==sha(new[p])==sha(par[p])==pins[p],'allowed file differs from the signed head: '+p)
        row=dict(kind='version-only' if p in VERSION_ONLY else 'exact-bytes',e3c29d1d_sha256=pin,equals_a54315f9=True,
            time_points=dict(e3c29d1d_sha256='e3c29d1dのblob＝a54315f9のblob（binding-10の固定）＝今の作業ツリーのbytes'))
        if p not in VERSION_ONLY:row['scope']=EXACT_SCOPE_V4
        summary[p]=row
    return summary,mapping

def verify(b,reuse_compat=True):
    """binding-11 checks, then the adopted v3 entry's verify (with only the 7 Step 17 files at their a54315f9 bytes)."""
    b10,_,_,_,_=verify_base(b)
    history=verify_history_v3(b)
    head=verify_head(b,b10)
    files,a5_map=verify_files(b,b10,head['head'])
    with view_class()(a5_map) as view:inner,mapping=v3().verify(b10,reuse_compat)
    read={c['path'] for c in view.calls};need(set(a5_map)<=read,'v3 checks did not read the changed files through the a54315f9 view')
    shown=sorted(rel(k) for k in mapping if rel(k) in set(ALLOWED_PATHS_15))
    need(shown==list(ALLOWED_PATHS_15),'logical view does not cover exactly the 15 allowed paths')
    summary=dict(v3=inner,u15_e3c29d1d=dict(head=head,files=files,history_v3=history,allowed_paths=list(ALLOWED_PATHS_15),changed_paths=list(HEAD_FILES),
        unchanged_paths=list(UNCHANGED_FILES),layering=LAYERING_V4))
    return summary,mapping

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
    for c in view.calls:key=rel(c['path']);calls[key]=calls.get(key,0)+1
    with (out/(v.name+'-'+str(time.time_ns())+'.view-calls.json')).open('x') as f:json.dump(dict(validator=v.name,logical_reads=calls,code_loads=view.code_loads),f,indent=2)

def guarded_run(entry,pin,out,receipts,real):
    """subprocess.run replacement for the reused old chain: only the old child argv/options are accepted; the child re-runs this entry."""
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

def run_old_chain(entry,pin,out,mapping15,trace):
    """The reused old chain driver; its parent process is shown the 15 allowed files at their old bytes only."""
    m=nc();fc=m.load('reused_final_candidate',m.OLD/'final_candidate.py');receipts=[]
    fc.subprocess=types.SimpleNamespace(run=guarded_run(entry,pin,out,receipts,subprocess.run),TimeoutExpired=subprocess.TimeoutExpired)
    before={p.name for p in m.OLD.glob('formal-candidate-*')};saved=sys.argv;calls=[]
    try:
        sys.argv=[str(m.OLD/'final_candidate.py')]
        with view_class()(mapping15) as view:
            try:fc.main()
            finally:calls=view.calls
    finally:
        sys.argv=saved
        created=sorted(m.OLD/n for n in {p.name for p in m.OLD.glob('formal-candidate-*')}-before)
        trace['old_chain_outputs']=[rel(p) for p in created]
        trace['old_chain_parent_logical_reads']=sorted({rel(c['path']) for c in calls})
        with (out/'children.json').open('x') as f:json.dump(receipts,f,indent=2)
    need(len(created)==1,'old chain output folder ambiguous')
    result=json.loads((created[0]/'result.json').read_bytes())
    need(result['source_compatibility']=='PASS' and result['unit_completed'] is False,'old chain did not pass')
    need(len(receipts)==4 and all(r.get('exit')==0 for r in receipts),'old chain children incomplete')
    pinned=set(v3().v2().old_chain_pins())&set(ALLOWED_PATHS_15);need(pinned<=set(trace['old_chain_parent_logical_reads']),'old chain did not read its pinned allowed files through the logical view')
    return dict(output=rel(created[0]),result=result,children=len(receipts),parent_logical_reads=trace['old_chain_parent_logical_reads']),created[0]

J='・'.join
LAYERING_V4=('v3（採用済み、binding-10）は変えずに、記録済みのa54315f9の証拠（署名head・CI 8 run・性能の原本）の上で実行する。a54315f9の記録は親の証明として残す。'
    'v4は署名head e3c29d1d（親a54315f9、U15 Step 17の7ファイル）とそのCI（7 run）を足す。許可の15ファイルのうちe3c29d1dで変わったのは7つ（'+J(HEAD_FILES)+'）で、'
    'v4はこの7つの今のbytesがe3c29d1dのblob（binding-11の固定）であり、a54315f9のblobがv3の固定（binding-10）と同じことを確かめ、v3にはこの7つだけをa54315f9のbytesとしてviewで見せる。'
    'ほかの8つ（'+J(UNCHANGED_FILES)+'）は、今のbytes・e3c29d1d・a54315f9のblobが同じ。'
    'v3はその上で、記録どおりに、v2・中のchain・旧chainへそれぞれの古いbytesを見せる。v4の旧chainの親とvalidatorの子にも同じ15ファイルの古いbytesを見せ、子はv4を実行する。'
    '許可の集合は15ファイルのままで、pathは足していない。')
RERUN_STATEMENT=('e3c29d1dのCI 7 runのうち、U12 current full quality（run 39114110570）だけはattempt 2である。attempt 1で失敗したのはjob「'+RERUN_FAILED_JOB[0]+'」（'+str(RERUN_FAILED_JOB[1])+'）の1つだけで'
    '（safaridriverのsession作成の時間切れ、runner側。原因は確かめていない）、人がそのjobだけの再実行を選んだ。attempt 2はそのjobだけを再実行し、attempt 2の29 jobはすべて成功し、'
    'jobの集合はa54315f9の同じworkflowと同じである。ほかの6 runはattempt 1のまま全job成功。この入口は、この1 runのこの1 jobのほかに、attempt 2や失敗したjobを許さない。')
RERUN_STATEMENT_EN=('Of the 7 CI runs at e3c29d1d, only U12 current full quality (run 39114110570) is attempt 2: in attempt 1 exactly one job failed, "'+RERUN_FAILED_JOB[0]+'" ('+str(RERUN_FAILED_JOB[1])+'; '
    'safaridriver session creation timed out on the runner, root cause not established), and the person chose to rerun that job only. Attempt 2 re-ran only that job, all 29 attempt-2 jobs succeeded and the job set equals the same workflow at a54315f9. '
    'The other 6 runs are attempt 1 with every job successful. No other attempt 2 or failed job is allowed.')
ALLOWANCE_V4=('許すのは15ファイルだけである。版の行（0.0.0 → 0.1.0）だけの証明が4つ（'+J(VERSION_ONLY)+'）、'
    '署名済みhead e3c29d1dのbytesへの固定が11（'+J(EXACT_FILES_ALL)+'）。このうちe3c29d1dで変わったのは7つ（'+J(HEAD_FILES)+'）で、'
    'ほかの4つ（'+J(p for p in EXACT_FILES_ALL if p not in HEAD_FILES)+'）のbytesはa54315f9とe3c29d1dで同じ。'
    '署名headはe3c29d1d（親a54315f9）、CIの記録はe3c29d1dの7 run（U12 current full qualityだけattempt 2）である。FR10.1・U15の受け入れはGAPのまま。')
ALLOWANCE_V4_EN=('Exactly 15 files are allowed: 4 version-only proofs (0.0.0 -> 0.1.0: '+', '.join(VERSION_ONLY)+') and 11 exact-bytes pins to the signed head e3c29d1d ('
    +', '.join(EXACT_FILES_ALL)+'), of which 7 changed at e3c29d1d ('+', '.join(HEAD_FILES)+'). Signed head e3c29d1d (parent a54315f9); CI records are the 7 runs at e3c29d1d '
    '(only U12 current full quality is attempt 2). FR10.1 and U15 acceptance remain GAP.')
EXACT_SCOPE_V4=('bytesの固定の11ファイル（'+J(EXACT_FILES_ALL)+'）について、このコマンドが証明するのは、今のbytesがU15の承認済みSteps 13〜17の署名済みhead e3c29d1dのbytesであることだけである。'
    '中身はU15のレビューと試験（とe3c29d1dのCI）で確かめるものであり、このコマンドでは確かめていない。')
EXACT_SCOPE_V4_EN=("For all 11 exact-bytes files this command proves only that the bytes are the signed-head e3c29d1d bytes of U15's approved Steps 13-17; "
    "their content is checked by U15's review and tests (and the e3c29d1d CI), not by this command.")
PERFORMANCE_SCOPE_V4=('inner FR8.3 binding unchanged (1ceae86c, binding-02); the performance originals measured once at bb197e04 (run 39089194062), a54315f9 (run 39096893624) '
    'and e3c29d1d (run 39114108809) were each checked and recorded only (the e3c29d1d original also against its u11-node artifact ZIP digest); none is bound to the module receipt')
PERFORMANCE_SCOPE_V4_JA=('中の性能（FR8.3）の根拠は今までどおり1ceae86c（binding-02）。bb197e04（run 39089194062）・a54315f9（run 39096893624）・e3c29d1d（run 39114108809）でそれぞれ1回だけ測った原本は、'
    'どれも確かめて記録しただけである（e3c29d1dの原本はu11-nodeのartifactのZIPのdigestとも照合した）。どれもmoduleのreceiptには束ねていない。')
V3_LAYER_TIME_POINT=('この層はv3（binding-10）の検査の記録である。v4は、e3c29d1dで変わった7ファイルをa54315f9のbytes（binding-10の固定）としてviewで見せてv3を実行したので、'
    'この層で「今のbytes」と書かれているものは、v4がviewで見せたa54315f9の時点のbytesを指す。今の作業ツリーのbytes（署名済みhead e3c29d1dのbytes）の主張は、u15_e3c29d1dとallowanceにある。')
V2_ROW_SCOPE=('このrowの値の時点：old_sha256は旧chainのbinding-v4の固定（57a8c96f・1ceae86c・be45のblob）、new_sha256はbb197e04のblob（binding-09の固定。v2がbb197e04の時点で確かめた値）である。'
    '今の作業ツリーのbytes（署名済みhead e3c29d1dのbytes）とその主張の範囲は、u15_e3c29d1d.filesとallowance.exact_bytes_scopeにある。')
V2_ROW_LAYER='v2はこのファイルをbb197e04のbytesとして確かめた（docs/release.md・tests/release/test_policy.pyは、v4がa54315f9のbytesを、その中でv3がbb197e04のbytesをviewで見せた）'
V3_ROW_SCOPE=('このrowの値の時点：old_sha256は旧chainのbinding-v4の固定（bb197e04・57a8c96f・1ceae86c・be45のblob）、a54315f9_sha256はa54315f9のblob（binding-10の固定。v3がa54315f9の時点で確かめた値）である。'
    '今の作業ツリーのbytes（署名済みhead e3c29d1dのbytes）とその主張の範囲は、u15_e3c29d1d.filesとallowance.exact_bytes_scopeにある。')
CLAIMED_V4=('e3c29d1dが署名済み（Verified）で親がa54315f9、変更はU15 Step 17の7ファイル（'+J(HEAD_FILES)+'）だけであり（commit・compare・local git）、保存したCI 7 runがそのheadで完了・全job成功であること。'
        '各runのjobの集合はa54315f9の同じworkflowと同じ。'+RERUN_STATEMENT,
    'e3c29d1dで変わった7ファイルの今のbytesがe3c29d1dのblob（binding-11の固定）であり、そのa54315f9のbytesがv3の固定（binding-10）と同じであること。'
        'ほかの8ファイル（'+J(UNCHANGED_FILES)+'）は、今のbytes・e3c29d1d・a54315f9のblobが同じであること。許可の集合はv3の15ファイルのままであること',
    'e3c29d1dで1回だけ測った性能（FR8.3）の原本を確かめて記録したこと（run 39114108809。artifact u11-nodeのZIPのSHA-256がAPIのdigestと一致し、原本はそのZIPの中のファイルと同じ）')
NOT_CLAIMED_V4=('15ファイル以外の差を許すこと。この入口が許すのは、版の行だけの証明4つ（'+J(VERSION_ONLY)+'）と、署名済みhead e3c29d1dのbytesへの固定11（'+J(EXACT_FILES_ALL)+'）だけである',
    'bytesの固定の11ファイルの中身が正しいこと。'+EXACT_SCOPE_V4,
    'Step 14bのファイルのうち、採用済みのchainのどの固定にも入っていない3ファイル（.github/workflows/u15-acceptance.yml・scripts/release/acceptance.py・tests/release/test_acceptance.py）のbytes。'
        'このコマンドはこの3つのbytesを確かめない（a54315f9のcommitとcompareのファイル一覧に入っていること、e3c29d1dの一覧に入っていないことだけを確かめる）。bytesと中身はU15のレビュー・試験とCIで確かめる',
    'FR10.1とU15の受け入れ（U15_acceptanceはGAPのまま）',
    'unitの完了・正式な確認コマンドとしての採用（人の承認が必要）',
    'e3c29d1dでの性能（FR8.3）の正式な合格。原本は検査して記録するだけで、moduleのreceiptには束ねていない。内側の性能の根拠は今までどおり1ceae86c（binding-02）',
    'U12 current full qualityのattempt 1で失敗したSafariのjobの原因。runner側のsafaridriverのsession作成の時間切れと記録しただけで、原因は確かめていない。attempt 2の成功を、同じ失敗が起きないことの証明とはしない',
    '新しい測定・CI・build・publish')

def statements():
    """(claimed, not_claimed) of v4: v3's claimed list without its two a54315f9-current-bytes statements, plus v4's."""
    V=v3();claimed,_=V.statements()
    need(claimed[-len(V.CLAIMED_V3):]==list(V.CLAIMED_V3),'v3 claimed list differs')
    kept=[s for s in claimed if s not in (V.CLAIMED_V3[1],V.CLAIMED_V3[2])]
    return [*kept,*CLAIMED_V4],list(NOT_CLAIMED_V4)

def u15_scope_v4(scope,u15_v4):
    """v3's claim scope with every current-bytes statement restated for e3c29d1d; v3's own note kept with its time point."""
    need(isinstance(scope.get('u15_version'),dict) and 'performance' in scope['u15_version'] and isinstance(scope.get('u15_old_chain'),dict) and isinstance(scope.get('u15_a54315f9'),dict),'v3 claim scope differs')
    claimed,not_claimed=statements()
    version=dict(scope['u15_version']);version.update(head=u15_v4['head']['head'],parent=PARENT,scope=ALLOWANCE_V4,claimed=claimed,not_claimed=not_claimed,
        performance=PERFORMANCE_SCOPE_V4,performance_ja=PERFORMANCE_SCOPE_V4_JA)
    old_chain=dict(scope['u15_old_chain']);old_chain.update(claimed=[CLAIMED_V4[1]],not_claimed=list(NOT_CLAIMED_V4[:3]),exact_bytes_scope=EXACT_SCOPE_V4,exact_bytes_scope_en=EXACT_SCOPE_V4_EN,
        allowed_paths=list(ALLOWED_PATHS_15))
    a5={'time_point':V3_LAYER_TIME_POINT,**scope['u15_a54315f9']}
    note=dict(head=u15_v4['head']['head'],parent=PARENT,changed_paths=list(HEAD_FILES),unchanged_paths=list(UNCHANGED_FILES),allowed_paths=list(ALLOWED_PATHS_15),
        layering=LAYERING_V4,ci_rerun=RERUN_STATEMENT,
        approval=['承認済みの計画 Step 18：「新しいheadに合わせて確認コマンドの入口を更新し、そのときに入口v3のMinor 4件（verification/version-allowance/pending-minor-fixes.md）も直す。回帰と独立レビューの後、検証コマンドとしての採用を人に伺う。」',
            'U12 current full quality（run 39114110570）のattempt 1で失敗した1 jobだけの再実行は、人が選んだ（coordinator経由）。'])
    return {**scope,'u15_version':version,'u15_old_chain':old_chain,'u15_a54315f9':a5,'u15_e3c29d1d':note}

def v3_summary_for_result(s):
    """v3's summary with each row's values labelled by their time point (Minor 2); data values unchanged."""
    s=copy.deepcopy(s)
    for p,row in s['v2']['u15']['old_chain_files'].items():
        row['time_points']=dict(old_sha256='旧chainのbinding-v4の固定（57a8c96f・1ceae86c・be45のblob）',new_sha256='bb197e04のblob（binding-09の固定）')
        if 'scope' in row:row['scope']=V2_ROW_SCOPE
        row['v2_layer']=V2_ROW_LAYER
    u=s['u15_a54315f9']
    for p,row in u['files'].items():
        row['time_points']={'a54315f9_sha256':'a54315f9のblob（binding-10の固定。v4がv3にviewで見せたbytes）'}
        if 'bb197e04_sha256' in row:row['time_points']['bb197e04_sha256']='bb197e04のblob（binding-09の固定。v3がv2にviewで見せたbytes）'
    for p,row in u['old_chain_extra'].items():
        row['time_points']=dict(old_sha256='旧chainのbinding-v4の固定（bb197e04・57a8c96f・1ceae86c・be45のblob）',a54315f9_sha256='a54315f9のblob（binding-10の固定。v4がv3にviewで見せたbytes）')
        row['scope']=V3_ROW_SCOPE
    return {'time_point':V3_LAYER_TIME_POINT,**s}

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
        trace['stage']='verify (binding-11, then the adopted v3 entry with the 7 Step 17 files at their a54315f9 bytes)'
        before,mapping=verify(b)
        mapping15={k:v for k,v in mapping.items() if k in {str(ROOT/p) for p in ALLOWED_PATHS_15}}
        trace['stage']='old chain (final_candidate.main and its validators)'
        old,old_output=run_old_chain(entry,pin,out,mapping15,trace)
        trace['stage']='claim scope'
        b10,_,_,_,b2=verify_base(b);s3=before['v3'];s2=s3['v2'];s14=s2['u14'];V=v3();u11=V.v2().u14().u11()
        _,a5_map=verify_files(b,b10,b['head'])
        with view_class()(a5_map):
            scope3=V.u15_scope_v3(V.v2().u14().u14_scope(u11.head_scope(u11.u2().claim_scope(b2,old_output,s14['u11']['u2']['u1']['module_receipt']),s14['u11']['u11']['head']),s14['u14']),s2['u15'],s3['u15_a54315f9'])
        scope=u15_scope_v4(scope3,before['u15_e3c29d1d'])
        trace['stage']='re-verify'
        after,_=verify(b);need(after==before,'inputs changed during validation')
        check_pins(entry,pin)
        claimed,not_claimed=statements()
        result=dict(u15_candidate_v4='PASS',command_line=dict(entry_sha256=entry,binding_sha256=pin),binding=BINDING,binding_sha256=pin,entry_sha256=entry,
            v3_entry=dict(path=V3_ENTRY,sha256=V3_ENTRY_SHA256,binding=V3_BINDING,binding_sha256=V3_BINDING_SHA256),
            v3_layer=v3_summary_for_result(s3),u15_e3c29d1d=before['u15_e3c29d1d'],old_chain=old,claim_scope=scope,
            allowed_paths=list(ALLOWED_PATHS_15),allowance_statement=ALLOWANCE_V4,allowance_statement_en=ALLOWANCE_V4_EN,layering=LAYERING_V4,
            ci_rerun=RERUN_STATEMENT,ci_rerun_en=RERUN_STATEMENT_EN,
            allowance=dict(version_only=list(VERSION_ONLY),
                exact_bytes={p:('e3c29d1d' if p in HEAD_FILES else 'e3c29d1d (= a54315f9)') for p in EXACT_FILES_ALL},
                changed_at_e3c29d1d=list(HEAD_FILES),outside_pins_not_byte_checked=list(V.OUTSIDE_PINS),
                exact_bytes_scope=EXACT_SCOPE_V4,exact_bytes_scope_en=EXACT_SCOPE_V4_EN),
            claimed=claimed,not_claimed=not_claimed,
            ci_inputs='stored hash-bound JSON only; no live GitHub query at check time',
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False)
        with (out/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
        print(json.dumps(dict(output=rel(out),u15_candidate_v4='PASS',old_chain_source_compatibility=old['result']['source_compatibility'],FR10_1='GAP',U15_acceptance='GAP',unit_completed=False)))
        return 0
    except BaseException as error:
        with (out/'refusal.json').open('x',encoding='utf-8') as f:
            json.dump(dict(error=str(error),refused_at=trace,traceback=traceback.format_exc(),allowed_paths=list(ALLOWED_PATHS_15),allowance=ALLOWANCE_V4+' 許可は広げていない。',
                FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False),f,indent=2,ensure_ascii=False)
        print('REFUSED: '+str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main(sys.argv))
