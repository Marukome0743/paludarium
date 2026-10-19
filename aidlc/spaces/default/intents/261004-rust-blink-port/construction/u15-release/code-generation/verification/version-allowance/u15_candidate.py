"""U15 formal verification entry: release version 0.0.0 -> 0.1.0 allowance (not adopted).

Spec: ../version-allowance-proposal.md (approved design, pinned by SHA-256 in
binding-08 `spec`). This entry wraps the adopted U14 Step46 entry
(u14_candidate_v2.py with binding-07) and, through it, the U11 Step31 entry
(binding-05), the U2 Step71 entry (binding-03) and the U1 Step72 checker
(binding-02), without changing any of them. The U14 entry is executed from its
exact bytes pinned by SHA-256 and its functions are called unchanged:
u14.verify (every binding-07 check and, through it, every binding-05,
binding-03 and binding-02 check), the reused old chain (final_candidate.main
with its unchanged validators, each validator child under the unchanged
historical_child.View) and the claim scopes of U2, U11 and U14.

The only new authorization (binding-08) is the release version change in
exactly three sealed compiled sources (VERSION_FILES, a fixed constant):
  (a) old bytes = git blob at 57a8c96f (binding-07's head) = blob at
      1ceae86c (binding-02's head) = blob at be45 (U1's logical head), and the
      binding-02 compiled-receipt pin = the blob at the receipt's build head
      208fd965. For the two lock files the receipt pin also equals the old
      bytes. For package.json it does not (repository/publishConfig were added
      between 208fd965 and be45; U1 seals it by the be45 and 1ceae86c blobs,
      never by the receipt pin); this fixed exception (RECEIPT_IS_OLD) is the
      one deviation from the proposal's wording and is stated in the result;
  (b) current bytes = git blob at the binding's signed head bb197e04 = the
      bound new SHA-256;
  (c) parsed (TOML / JSON) and line by line, the ONLY difference old -> new is:
      Cargo.lock and fuzz/Cargo.lock: the `version` of the packages whose name
      is in the fixed workspace crate set of that file changes from exactly
      "0.0.0" to exactly "0.1.0"; the package count and order, every other
      field of those packages and every other package (external crates,
      paludarium-fuzz) are identical; package.json: only the top-level
      "version" changes "0.0.0" -> "0.1.0", every other key/value and the key
      order are identical;
  (d) the signed head bb197e04 is Verified, its parent is 57a8c96f, local git
      and the stored compare list exactly the 11 known files, and the stored
      CI runs of bb197e04 (runs and attempt-1 job lists) are completed/success
      at that head, checked by U1's unchanged verify_ci / verify_ci_jobs; the
      FR8.3 performance original measured at bb197e04 (run 39089194062) is
      checked by U1's unchanged verify_performance and recorded only.
Then only these three paths are shown at their OLD bytes, through the unchanged
historical_child.View, to the inner chain (U14, U11, U2, U1, the old chain
driver and its validator children). Every other path is read physically. When
the inner chain refuses on any other path, the refusal stands: the allowance is
never widened here.

Command line (as the U14 entry): `--entry-sha256 <hex> --binding-sha256
<hex>`, in this order. The entry computes the SHA-256 of its own file and of
binding-08.json and refuses with exit 2, before any check and without writing
anything, when an argument is missing, malformed or different. A refused check
exits 1 and writes refusal.json; a pass exits 0 and writes result.json, both in
a fresh run-<ns>-<pid>/ folder. The internal `--logical-child` branch runs the
same hash check before anything else.

No guest, build, CI, measurement or publish is started, and no live GitHub
query is made: every CI input is the stored, hash-bound JSON in this folder.
"""
import hashlib,json,os,re,runpy,subprocess,sys,time,tomllib,traceback,types
from pathlib import Path

OWN=Path(__file__).resolve().parent
SELF=Path(__file__).resolve()
ROOT=next(p for p in OWN.parents if (p/'Cargo.toml').is_file())
INTENT='aidlc/spaces/default/intents/261004-rust-blink-port/'
U14_LOOP=INTENT+'construction/u14-jit-wasm/code-generation/verification/loopback1-next/'
U14_ENTRY=U14_LOOP+'u14_candidate_v2.py'
U14_ENTRY_SHA256='934f21bc9ca7f58d68a72dc9759df90ae1f28c63791600bb552039c3cfe0d23a'
U14_BINDING='binding-07.json'
U14_BINDING_SHA256='425ae3e7554a84de78062723954317f0bb2bba99c41567773bc1752c63ecdd7e'
U11_ENTRY=INTENT+'construction/u11-wasm-launcher/code-generation/verification/loopback1-next/u11_candidate_v2.py'
U11_ENTRY_SHA256='56870072810100fa97456ced54a0732e8696489dcb297fa38aa17c0a39978ca7'
U15_VER=INTENT+'construction/u15-release/code-generation/verification/'
LOOP=U15_VER+'version-allowance/'
SPEC=U15_VER+'version-allowance-proposal.md'
SPEC_SHA256='df38caab6d484c1cf9fa9945b66ee59eaab1c55900ef4d09fc66c81282e786b4'
# The adopted U14 entry, its binding, regressions and README stay byte-unchanged (history).
HISTORY={U14_ENTRY:U14_ENTRY_SHA256,U14_LOOP+U14_BINDING:U14_BINDING_SHA256,
         U14_LOOP+'test_u14_candidate_v2.py':'aab2a01a68c4afc23ef8a3d7c754e3971468e572347c70a1d59f204e8884bf80',
         U14_LOOP+'README.md':'dfad66355d890688b8ccb4963de11830527c0186e50cc66a442e8aa37361d9ed'}
# binding-07's signed head; the new signed head must be its only child.
PRIOR_HEAD='57a8c96f610d6e02234354e5e4fb5cac068d5036'
BRANCH='codex/build-and-test'
# The three sealed compiled sources the approved proposal names; a binding cannot authorize any other path.
CARGO_LOCK='Cargo.lock';FUZZ_LOCK='fuzz/Cargo.lock';PACKAGE_JSON='packages/paludarium-wasm/package.json'
VERSION_FILES=(CARGO_LOCK,FUZZ_LOCK,PACKAGE_JSON)
KINDS={CARGO_LOCK:'cargo-lock',FUZZ_LOCK:'cargo-lock',PACKAGE_JSON:'package-json'}
WORKSPACE_CRATES=frozenset({'paludarium','paludarium-cpu','paludarium-decoder','paludarium-harness','paludarium-host','paludarium-jit','paludarium-kernel',
    'paludarium-loader','paludarium-mmu','paludarium-runtime','paludarium-types','paludarium-vfs','paludarium-wasm'})
FUZZ_CRATES=frozenset({'paludarium-cpu','paludarium-decoder','paludarium-host','paludarium-jit','paludarium-kernel','paludarium-loader','paludarium-mmu',
    'paludarium-types','paludarium-vfs'})
LOCK_CRATES={CARGO_LOCK:WORKSPACE_CRATES,FUZZ_LOCK:FUZZ_CRATES}
OLD_VERSION='0.0.0';NEW_VERSION='0.1.0'
# The compiled receipt (binding-02) was built at 208fd965. Its pin equals the old bytes for the two lock files.
# packages/paludarium-wasm/package.json changed between 208fd965 and be45 (repository/publishConfig added), so
# its receipt pin is the 208fd965 blob, not the old bytes; U1 has always sealed it by the be45 and 1ceae86c blobs.
RECEIPT_HEAD='208fd9652528fbb9002a7bd25c0cb1f2105a5738'
RECEIPT_IS_OLD=frozenset({CARGO_LOCK,FUZZ_LOCK})
# The 11 files of the signed version commit (Step13/14/14b of U15).
HEAD_FILES=('.github/workflows/u15-acceptance.yml','Cargo.lock','Cargo.toml','README.md','docs/release.md','fuzz/Cargo.lock',
    'packages/paludarium-wasm/package.json','scripts/release/acceptance.py','tests/release/test_acceptance.py','tests/release/test_package.py','tests/release/test_policy.py')
REQUIRED_RUNS=frozenset({'CI','Release package checks','U14 current full quality','U12 current full quality','U13 current full quality',
    'U14 fresh thirteen target ASan and LSan','U1 U14 current-source evidence'})
PERFORMANCE_RUN='U14 current full quality'
PERFORMANCE_PATH=U15_VER+'ci-bb197e04/u14-quality-39089194062/u11-node/performance/observations.json'
BINDING='binding-08.json'
BINDING_SHA256='f20954e14dc761f4dc0172d775af3c2602f8f2887539c900fa2319ba33b30262'
SCHEMA=8
REPOSITORY='Marukome0743/paludarium'
USAGE='usage: u15_candidate.py --entry-sha256 <64 hex> --binding-sha256 <64 hex>'
HEX40=re.compile(r'[0-9a-f]{40}');HEX64=re.compile(r'[0-9a-f]{64}')
sha=lambda b:hashlib.sha256(b).hexdigest()
_U14=None

def need(value,message):
    if not value:raise ValueError(message)

def check_pins(entry,binding):
    """Both SHA-256 values must be well formed and equal the real files and the pinned binding."""
    need(isinstance(entry,str) and HEX64.fullmatch(entry) is not None,'--entry-sha256 must be 64 lowercase hex digits')
    need(isinstance(binding,str) and HEX64.fullmatch(binding) is not None,'--binding-sha256 must be 64 lowercase hex digits')
    need(entry==sha(SELF.read_bytes()),'--entry-sha256 differs from the SHA-256 of this entry file')
    need(binding==sha((OWN/BINDING).read_bytes()),'--binding-sha256 differs from the SHA-256 of '+BINDING)
    need(binding==BINDING_SHA256,'--binding-sha256 differs from the binding pinned by this entry')
    return entry,binding

def command_line_pins(argv):
    need(len(argv)==5 and argv[1]=='--entry-sha256' and argv[3]=='--binding-sha256',USAGE)
    return check_pins(argv[2],argv[4])

def u14():
    """The U14 entry module, executed from its exact pinned bytes (it loads the pinned U11, U2 entries and U1 checker)."""
    global _U14
    if _U14 is None:
        path=ROOT/U14_ENTRY;need(not path.is_symlink(),'symlinked U14 entry')
        raw=path.read_bytes();need(sha(raw)==U14_ENTRY_SHA256,'U14 entry bytes differ from the pinned SHA-256')
        module=types.ModuleType('u14_candidate_v2');module.__file__=str(path)
        exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
        need(module.BINDING==U14_BINDING and module.BINDING_SHA256==U14_BINDING_SHA256 and module.U11_ENTRY==U11_ENTRY and module.U11_ENTRY_SHA256==U11_ENTRY_SHA256,'U14 entry base pins differ')
        _U14=module
    return _U14

def nc():
    """The U1 checker module (pinned by the U2 entry, re-checked by the U11 entry)."""
    return u14().nc()

def view_class():
    return u14().view_class()

def load_binding(pin):
    need(HEX64.fullmatch(pin) is not None,'binding SHA-256 required')
    need(pin==BINDING_SHA256,'binding SHA-256 differs from the binding pinned by this entry')
    raw=nc().read(LOOP+BINDING);need(sha(raw)==pin,'binding bytes differ from the pinned SHA-256')
    return json.loads(raw)

def verify_base(b):
    """binding-08 must name the unchanged U14 entry and binding-07; returns (binding-07, binding-05, binding-02)."""
    need(b['schema']==SCHEMA and b['repository']==REPOSITORY,'binding schema/repository differs')
    need(b['base']=={'entry':{'path':U14_ENTRY,'sha256':U14_ENTRY_SHA256},'binding':{'name':U14_BINDING,'sha256':U14_BINDING_SHA256}},'base entry/binding differs')
    b7=u14().load_binding(U14_BINDING_SHA256)
    b5,b2=u14().verify_base(b7)
    return b7,b5,b2

def verify_history(b):
    """The adopted U14 entry, binding-07, its regressions and README keep their pinned bytes; the spec is pinned."""
    need(b.get('history')==HISTORY,'history pin set differs')
    m=nc()
    for rel,pin in sorted(HISTORY.items()):
        need(not (ROOT/rel).is_symlink(),'symlinked history file: '+rel)
        need(sha(m.read(rel))==pin,'history file changed: '+rel)
    need(b.get('spec')=={'path':SPEC,'sha256':SPEC_SHA256},'spec reference differs')
    need(sha(m.read(SPEC))==SPEC_SHA256,'spec differs from the approved proposal bytes')
    return dict(sorted(HISTORY.items()))

def git_blob_id(commit,rel):
    return nc().git('rev-parse','--verify',commit+':'+rel).decode().strip()

def verify_head(b,b7,b2):
    """(d) signed head bb197e04: Verified, child of 57a8c96f, 11 files, stored CI completed/success at the head."""
    m=nc();head=b['head']
    need(isinstance(head,str) and HEX40.fullmatch(head) is not None and head not in (PRIOR_HEAD,b2['head']),'signed head differs')
    need(b['parent']==PRIOR_HEAD==b7['head'],'parent differs from the binding-07 signed head')
    chain=[PRIOR_HEAD,head];need(b['head_chain']==chain,'signed chain differs from 57a8c96f -> head')
    sub={'ci':b['ci'],'head_chain':chain,'ci_jobs':b['ci_jobs']}
    runs=m.verify_ci(sub,head);jobs=m.verify_ci_jobs(sub,head,runs)
    need(len(runs)==len(REQUIRED_RUNS) and {r['name'] for r in runs.values()}==REQUIRED_RUNS,'CI run set differs from the required runs')
    need(all(r['run_attempt']==1 for r in runs.values()),'CI run is not a first attempt')
    ci=json.loads(m.read(b['ci']['path']))
    need(ci['branch']=={'name':BRANCH,'head':head},'CI branch head differs')
    files=ci['commits'][-1].get('files')
    need(isinstance(files,list) and sorted(files)==sorted(HEAD_FILES) and len(files)==len(HEAD_FILES),'signed commit file list differs')
    need(u14().u11().changed_paths(PRIOR_HEAD,head)==sorted(HEAD_FILES),'local git changes of the signed commit differ')
    c=ci['compare']
    need(c['base']==PRIOR_HEAD and c['head']==head and c['merge_base']==PRIOR_HEAD and c['status']=='ahead' and c['ahead_by']==1 and c['behind_by']==0 and c['total_commits']==1 and c['commits']==[head],'compare differs from 57a8c96f...head')
    need(len(c['files'])==len(HEAD_FILES) and sorted(f['filename'] for f in c['files'])==sorted(HEAD_FILES),'compare file list differs')
    for f in c['files']:
        if f['filename'] in VERSION_FILES:need(f['status']=='modified' and f['sha']==git_blob_id(head,f['filename']),'compare blob differs from local git: '+f['filename'])
    listed=ci['runs_listed_for_head']
    need(listed['total_count']==len(listed['ids'])==len(runs) and sorted(str(i) for i in listed['ids'])==sorted(runs),'CI run listing for the head differs')
    d=json.loads(m.read(b['ci_jobs']['path']))
    need(all(r['total_count']==len(r['jobs']) for r in d['runs']),'CI job count differs from the API total')
    perf_entry=b['performance'];need(perf_entry['path']==PERFORMANCE_PATH,'performance original path differs')
    need(runs.get(str(perf_entry['run_id']),{}).get('name')==PERFORMANCE_RUN,'performance run is not the U14 full-quality run')
    performance,_=m.verify_performance({'performance':perf_entry},head,runs)
    return dict(head=head,parent=PRIOR_HEAD,head_chain=chain,changed_paths=sorted(HEAD_FILES),
        runs={rid:dict(name=r['name'],run_attempt=r['run_attempt']) for rid,r in sorted(runs.items())},jobs={rid:len(r['jobs']) for rid,r in sorted(jobs.items())},
        ci_sha256=b['ci']['sha256'],ci_jobs_sha256=b['ci_jobs']['sha256'],performance_bb197e04=dict(run_id=perf_entry['run_id'],**performance))

def decode(raw,rel):
    try:return raw.decode('utf-8')
    except UnicodeDecodeError as error:raise ValueError('version file is not UTF-8: '+rel) from error

def lock_diff(rel,old,new):
    """Cargo.lock / fuzz/Cargo.lock: only the workspace crates' version 0.0.0 -> 0.1.0 (parsed and line by line)."""
    crates=LOCK_CRATES[rel]
    try:o=tomllib.loads(decode(old,rel));n=tomllib.loads(decode(new,rel))
    except tomllib.TOMLDecodeError as error:raise ValueError('lock file does not parse: '+rel) from error
    need(set(o)==set(n) and {k:v for k,v in o.items() if k!='package'}=={k:v for k,v in n.items() if k!='package'},'lock top-level differs: '+rel)
    op,np_=o.get('package'),n.get('package')
    need(isinstance(op,list) and isinstance(np_,list) and len(op)==len(np_),'lock package count differs: '+rel)
    need([p.get('name') for p in op]==[p.get('name') for p in np_],'lock package order differs: '+rel)
    changed=[]
    for a,c in zip(op,np_):
        name=a.get('name')
        if name in crates:
            need(a.get('version')==OLD_VERSION and c.get('version')==NEW_VERSION,'workspace crate version is not 0.0.0 -> 0.1.0: '+rel+': '+name)
            need({k:v for k,v in a.items() if k!='version'}=={k:v for k,v in c.items() if k!='version'},'workspace crate entry differs beyond its version: '+rel+': '+name)
            need('source' not in a and 'checksum' not in a,'workspace crate has a registry source: '+rel+': '+name)
            changed.append(name)
        else:
            need(a==c,'lock package differs outside the workspace version allowance: '+rel+': '+str(name))
    need(len(changed)==len(crates) and set(changed)==crates,'workspace crate set differs: '+rel)
    ol=old.split(b'\n');nl=new.split(b'\n');need(len(ol)==len(nl),'lock line count differs: '+rel)
    diff=[i for i in range(len(ol)) if ol[i]!=nl[i]];names={('name = "'+c+'"').encode() for c in crates}
    need(len(diff)==len(crates),'lock changed line count differs: '+rel)
    for i in diff:
        need(ol[i]==b'version = "0.0.0"' and nl[i]==b'version = "0.1.0"' and i>0 and ol[i-1] in names,'lock line differs beyond a workspace version line: '+rel+': line '+str(i+1))
    need({ol[i-1] for i in diff}==names,'lock changed lines do not cover the workspace crates: '+rel)
    return dict(packages=len(op),external_or_other_packages_identical=len(op)-len(changed),changed_crates=sorted(changed),changed_lines=len(diff),lines=len(ol))

def unique_pairs(pairs):
    keys=[k for k,_ in pairs];need(len(set(keys))==len(keys),'package.json has a duplicate key')
    return dict(pairs)

def package_json_diff(rel,old,new):
    """package.json: only the top-level "version" 0.0.0 -> 0.1.0; every other key/value and the key order identical."""
    try:o=json.loads(decode(old,rel),object_pairs_hook=unique_pairs);n=json.loads(decode(new,rel),object_pairs_hook=unique_pairs)
    except json.JSONDecodeError as error:raise ValueError('package.json does not parse: '+rel) from error
    need(isinstance(o,dict) and isinstance(n,dict),'package.json is not an object: '+rel)
    need(list(o)==list(n),'package.json keys/order differ: '+rel)
    need(o.get('version')==OLD_VERSION and n.get('version')==NEW_VERSION,'package.json version is not 0.0.0 -> 0.1.0: '+rel)
    for k in o:
        if k!='version':need(o[k]==n[k],'package.json key differs: '+rel+': '+k)
    token_old=b'"version":"0.0.0"';token_new=b'"version":"0.1.0"'
    need(old.count(token_old)==1 and new==old.replace(token_old,token_new),'package.json bytes differ beyond the version value: '+rel)
    return dict(keys=len(o),other_keys_identical=len(o)-1,changed_key='version')

def version_only_diff(rel,old,new):
    need(rel in KINDS,'not a version file: '+rel)
    return lock_diff(rel,old,new) if KINDS[rel]=='cargo-lock' else package_json_diff(rel,old,new)

def verify_versions(b,b2,head):
    """(a)-(c) for exactly the three version files; returns (summary, exact old-byte mapping)."""
    m=nc();entries=b['version_files']
    need(isinstance(entries,dict) and set(entries)==set(VERSION_FILES) and len(entries)==len(VERSION_FILES),'version allowance differs from the authorized path set')
    need(not set(VERSION_FILES)&set(b2['allowed_compiled_changes']),'version file is already allowed by binding-02')
    receipt=b2['compiled_receipt'];raw=m.read(receipt['path']);need(sha(raw)==receipt['sha256'],'compiled receipt differs')
    doc=json.loads(raw);sources=doc['source_files'];names=sorted(VERSION_FILES)
    need(doc['head']==RECEIPT_HEAD,'compiled receipt head differs')
    prior=m.git_blobs(PRIOR_HEAD,names);base=m.git_blobs(b2['head'],names);logical=m.git_blobs(m.LOGICAL_HEAD,names);new=m.git_blobs(head,names)
    built=m.git_blobs(RECEIPT_HEAD,names)
    mapping={};summary={}
    for p in names:
        e=entries[p];need(isinstance(e,dict) and set(e)=={'kind','old_sha256','receipt_sha256','new_sha256'} and e['kind']==KINDS[p],'version entry differs: '+p)
        old=prior[p]
        need(p in sources and e['receipt_sha256']==sources[p]==sha(built[p]),'version receipt pin differs: '+p)
        need(e['old_sha256']==sha(old)==sha(base[p])==sha(logical[p]),'version old pin differs: '+p)
        if p in RECEIPT_IS_OLD:need(e['old_sha256']==e['receipt_sha256'],'version old pin differs from the compiled receipt: '+p)
        else:need(e['old_sha256']!=e['receipt_sha256'],'version receipt exception differs: '+p)
        current=m.read(p)
        need(sha(current)==e['new_sha256']==sha(new[p]),'version file differs from binding/signed head: '+p)
        need(e['new_sha256']!=e['old_sha256'],'version allowance is not a change: '+p)
        summary[p]=dict(kind=e['kind'],old_sha256=e['old_sha256'],receipt_sha256=e['receipt_sha256'],receipt_equals_old=p in RECEIPT_IS_OLD,new_sha256=e['new_sha256'],diff=version_only_diff(p,old,current))
        mapping[str(ROOT/p)]=old
    return summary,mapping

def verify(b,reuse_compat=True):
    """binding-08 checks, then the unchanged U14 entry's verify with the three version files at their old bytes."""
    b7,_,b2=verify_base(b)
    history=verify_history(b)
    head=verify_head(b,b7,b2)
    versions,version_map=verify_versions(b,b2,head['head'])
    with view_class()(version_map) as view:inner,mapping=u14().verify(b7,reuse_compat)
    read={c['path'] for c in view.calls};need(set(version_map)<=read,'U1 checks did not read the version files through the logical view')
    need(not set(mapping)&set(version_map),'U14 and U15 logical views overlap')
    summary=dict(u14=inner,u15=dict(head=head,version_files=versions,history=history,logical_view_paths=sorted(str(Path(k).relative_to(ROOT)) for k in version_map)))
    return summary,{**mapping,**version_map}

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

def run_old_chain(entry,pin,out,version_map,trace):
    """The reused old chain driver, its parent process also shown the three version files at their old bytes only."""
    m=nc();fc=m.load('reused_final_candidate',m.OLD/'final_candidate.py');receipts=[]
    fc.subprocess=types.SimpleNamespace(run=guarded_run(entry,pin,out,receipts,subprocess.run),TimeoutExpired=subprocess.TimeoutExpired)
    before={p.name for p in m.OLD.glob('formal-candidate-*')};saved=sys.argv;calls=[]
    try:
        sys.argv=[str(m.OLD/'final_candidate.py')]
        with view_class()(version_map) as view:
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
    return dict(output=str(created[0].relative_to(ROOT)),result=result,children=len(receipts)),created[0]

CLAIMED=('3ファイル（Cargo.lock・fuzz/Cargo.lock・packages/paludarium-wasm/package.json）の差が、workspace crateとnpmパッケージの版 0.0.0 → 0.1.0 だけであること（構文と行の両方で確認）',
    '3ファイルの新しいbytesが署名済みhead bb197e04のblobと同じであり、古いbytesが57a8c96f・1ceae86c・be45のblobと同じであること。binding-02のreceiptの固定は208fd965のblobであり、2つのlockでは古いbytesと同じ。package.jsonでは違う（208fd965とbe45の間でrepository・publishConfigが足された。U1は今までもbe45・1ceae86cのblobで固定している）',
    'bb197e04が署名済み（Verified）で親が57a8c96f、変更は既知の11ファイルだけであり、保存したCI 7 runがそのheadでattempt 1のまま全job成功であること',
    'ほかの検査（U14・U11・U2・U1・旧chain）は弱めず、そのまま実行したこと')
NOT_CLAIMED=('3ファイル以外の差（Cargo.toml・README.md・docs/release.md・scripts/release・tests/release・CIの定義など）を許すこと。この入口はそれらを許さない',
    'FR10.1とU15の受け入れ（U15_acceptanceはGAPのまま）',
    'unitの完了・正式な確認コマンドとしての採用（人の承認が必要）',
    'bb197e04での性能（FR8.3）の正式な合格。bb197e04の性能の原本は検査して記録するだけで、moduleのreceiptには束ねていない。内側の性能の根拠は今までどおり1ceae86c（binding-02）',
    '新しい測定・CI・build・publish')

def u15_scope(scope,u15):
    """Keeps the U14 claim scope and states what the version allowance does and does not claim."""
    need('u14_records' in scope and 'u11_57a8c96f' in scope and 'performance_1ceae86c' in scope,'U14 claim scope missing')
    note=dict(head=u15['head']['head'],parent=u15['head']['parent'],version_files=sorted(u15['version_files']),logical_view_paths=u15['logical_view_paths'],
        claimed=list(CLAIMED),not_claimed=list(NOT_CLAIMED),performance='inner FR8.3 binding unchanged (1ceae86c); bb197e04 original checked and recorded only',
        scope='版の行（0.0.0 → 0.1.0）だけを3ファイルで許す。署名headはbb197e04、CIの記録はbb197e04のrunである。FR10.1・U15の受け入れはGAPのまま。')
    return {**scope,'u15_version':note}

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
        trace['stage']='verify (binding-08 and the unchanged U14 entry under the version view)'
        before,mapping=verify(b)
        version_map={k:v for k,v in mapping.items() if k in {str(ROOT/p) for p in VERSION_FILES}}
        trace['stage']='old chain (final_candidate.main and its validators)'
        old,old_output=run_old_chain(entry,pin,out,version_map,trace)
        trace['stage']='claim scope'
        _,_,b2=verify_base(b);s14=before['u14']
        u11=u14().u11()
        scope=u15_scope(u14().u14_scope(u11.head_scope(u11.u2().claim_scope(b2,old_output,s14['u11']['u2']['u1']['module_receipt']),s14['u11']['u11']['head']),s14['u14']),before['u15'])
        trace['stage']='re-verify'
        after,_=verify(b);need(after==before,'inputs changed during validation')
        check_pins(entry,pin)
        result=dict(u15_candidate='PASS',command_line=dict(entry_sha256=entry,binding_sha256=pin),binding=BINDING,binding_sha256=pin,entry_sha256=entry,
            base_entry=dict(path=U14_ENTRY,sha256=U14_ENTRY_SHA256),base_binding=dict(name=U14_BINDING,sha256=U14_BINDING_SHA256),
            u1_physical=s14['u11']['u2']['u1'],u2_records=s14['u11']['u2']['u2'],u11=s14['u11']['u11'],u14=s14['u14'],u15=before['u15'],old_chain=old,claim_scope=scope,
            claimed=list(CLAIMED),not_claimed=list(NOT_CLAIMED),allowance='version-only (0.0.0 -> 0.1.0) for exactly 3 sealed files',
            ci_inputs='stored hash-bound JSON only; no live GitHub query at check time',
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False)
        with (out/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
        print(json.dumps(dict(output=str(out.relative_to(ROOT)),u15_candidate='PASS',old_chain_source_compatibility=old['result']['source_compatibility'],FR10_1='GAP',U15_acceptance='GAP',unit_completed=False)))
        return 0
    except BaseException as error:
        with (out/'refusal.json').open('x',encoding='utf-8') as f:
            json.dump(dict(error=str(error),refused_at=trace,traceback=traceback.format_exc(),allowance='version-only (0.0.0 -> 0.1.0) for exactly 3 sealed files; not widened',
                FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False),f,indent=2,ensure_ascii=False)
        print('REFUSED: '+str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main(sys.argv))
