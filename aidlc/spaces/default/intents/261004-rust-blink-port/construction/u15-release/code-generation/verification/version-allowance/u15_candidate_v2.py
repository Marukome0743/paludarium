"""U15 formal verification entry v2: release version allowance plus the old-chain pins (not adopted).

Same design and command-line contract as u15_candidate.py (binding-08), which
is kept byte-unchanged as history together with its regressions and its run
folder (pinned by HISTORY_V1). This entry executes u15_candidate.py from its
exact pinned bytes as a library and calls its functions unchanged:
verify_head (signed head bb197e04, stored CI, performance original),
verify_versions (the version-only proof of Cargo.lock, fuzz/Cargo.lock and
packages/paludarium-wasm/package.json, including the accepted receipt-pin
handling of package.json), verify_history (the adopted U14 entry, binding-07,
its regressions and README, and the approved proposal) and u15_scope. Through
it, the adopted U14 Step46 entry (u14_candidate_v2.py with binding-07) runs
unchanged, and through that U11, U2 and U1.

The only authorizations beyond binding-08 are binding-09's, approved by the
person on 2026-10-18 after the binding-08 run refused on the old chain's pin of
Cargo.toml ("Cargo.toml は版の行だけの証明、README.md・docs/release.md・
tests/release の 2 つは bb197e04 のバイト列の固定で許可を足し、もう一度実行して
ください。package.json の照合の扱いもそれでよいです。"):
  (e) Cargo.toml: old bytes = the binding-v4 pin (old chain) = git blobs at
      57a8c96f, 1ceae86c and be45; new bytes = the blob at bb197e04 = the bound
      SHA-256; parsed and line by line, the only difference is
      workspace.package.version and the `version` of the 11 internal
      workspace.dependencies (each `{ path = "crates/<name>", version }`),
      each exactly "0.0.0" -> "0.1.0"; every other key, value, table and line
      is identical;
  (f) README.md, docs/release.md, tests/release/test_policy.py,
      tests/release/test_package.py: an exact-bytes allowance. Old bytes = the
      binding-v4 pin = the blobs at 57a8c96f, 1ceae86c and be45; new bytes =
      the blob at bb197e04 = the bound SHA-256. This proves only that the bytes
      are the signed-head bytes of U15's approved Steps 13-14; their content is
      checked by U15's review and tests, not by this command.
The fixed path set is these 8 files (ALLOWED_PATHS). All 8 are shown at their
old bytes, through the unchanged historical_child.View, to the inner chain
(U14, U11, U2, U1), to the old chain driver and to its validator children.
Anything else that the chain refuses stands: the allowance is never widened.

Command line: `--entry-sha256 <hex> --binding-sha256 <hex>`, in this order.
Argument or pin mismatch: exit 2 before any check, nothing written. A refused
check: exit 1 and refusal.json; a pass: exit 0 and result.json, both in a fresh
run-<ns>-<pid>/ folder. `--logical-child` runs the same hash check first.

No guest, build, CI, measurement or publish is started, and no live GitHub
query is made.
"""
import copy,hashlib,json,os,re,runpy,subprocess,sys,time,tomllib,traceback,types
from pathlib import Path

OWN=Path(__file__).resolve().parent
SELF=Path(__file__).resolve()
ROOT=next(p for p in OWN.parents if (p/'Cargo.toml').is_file())
INTENT='aidlc/spaces/default/intents/261004-rust-blink-port/'
LOOP=INTENT+'construction/u15-release/code-generation/verification/version-allowance/'
V1_ENTRY=LOOP+'u15_candidate.py'
V1_ENTRY_SHA256='6a5077aef1034f6276c2806c66d0cfb62550812ee95217de92f7c7931b638cc0'
V1_BINDING='binding-08.json'
V1_BINDING_SHA256='f20954e14dc761f4dc0172d775af3c2602f8f2887539c900fa2319ba33b30262'
V1_RUN=LOOP+'run-1792293531741241000-82551/'
# The binding-08 entry, its binding, regressions and its refused run stay byte-unchanged (history).
HISTORY_V1={V1_ENTRY:V1_ENTRY_SHA256,LOOP+V1_BINDING:V1_BINDING_SHA256,
    LOOP+'test_u15_candidate.py':'6573bc6c158199bd1466aa076bdee307e9d82da7503a6cb3d48403572f37e10a',
    V1_RUN+'refusal.json':'8e1a65434f12489b9bc497b91b8977d4ea6e279ed895e80148ed242a9564d937',
    V1_RUN+'children.json':'4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945'}
OLD_BINDING_V4=INTENT+'construction/u1-skeleton/code-generation/verification/r05-r11-repair-01/binding-v4.json'
CARGO_TOML='Cargo.toml'
EXACT_FILES=('README.md','docs/release.md','tests/release/test_policy.py','tests/release/test_package.py')
INTERNAL_DEPS=('paludarium-types','paludarium-decoder','paludarium-mmu','paludarium-cpu','paludarium-loader','paludarium-vfs','paludarium-kernel',
    'paludarium-host','paludarium-jit','paludarium-runtime','paludarium')
OLD_VERSION='0.0.0';NEW_VERSION='0.1.0'
BINDING='binding-09.json'
BINDING_SHA256='687fee0c4a25147aab064ff101b742a8145d5cb46ea608295146745a524e3649'
SCHEMA=9
REPOSITORY='Marukome0743/paludarium'
USAGE='usage: u15_candidate_v2.py --entry-sha256 <64 hex> --binding-sha256 <64 hex>'
HEX64=re.compile(r'[0-9a-f]{64}')
sha=lambda b:hashlib.sha256(b).hexdigest()
_V1=None

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

def v1():
    """The binding-08 entry module, executed from its exact pinned bytes (it loads the pinned U14 entry and below)."""
    global _V1
    if _V1 is None:
        path=ROOT/V1_ENTRY;need(not path.is_symlink(),'symlinked binding-08 entry')
        raw=path.read_bytes();need(sha(raw)==V1_ENTRY_SHA256,'binding-08 entry bytes differ from the pinned SHA-256')
        module=types.ModuleType('u15_candidate');module.__file__=str(path)
        exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
        need(module.BINDING==V1_BINDING and module.BINDING_SHA256==V1_BINDING_SHA256,'binding-08 entry pins differ')
        _V1=module
    return _V1

def u14():return v1().u14()
def nc():return v1().nc()
def view_class():return v1().view_class()

# The fixed path set the person approved (8 files); a binding cannot authorize any other path.
ALLOWED_PATHS=tuple(sorted(('Cargo.lock','fuzz/Cargo.lock','packages/paludarium-wasm/package.json',CARGO_TOML,*EXACT_FILES)))
def allowed_paths():
    need(tuple(sorted({*v1().VERSION_FILES,CARGO_TOML,*EXACT_FILES}))==ALLOWED_PATHS,'allowed path set differs from the binding-08 version files plus the old-chain files')
    return ALLOWED_PATHS

def load_binding(pin):
    need(HEX64.fullmatch(pin) is not None,'binding SHA-256 required')
    need(pin==BINDING_SHA256,'binding SHA-256 differs from the binding pinned by this entry')
    raw=nc().read(LOOP+BINDING);need(sha(raw)==pin,'binding bytes differ from the pinned SHA-256')
    return json.loads(raw)

def verify_base(b):
    """binding-09 names the unchanged binding-08 entry and binding (and through them the U14 entry and binding-07)."""
    need(b['schema']==SCHEMA and b['repository']==REPOSITORY,'binding schema/repository differs')
    V=v1()
    need(b['base']=={'entry':{'path':V.U14_ENTRY,'sha256':V.U14_ENTRY_SHA256},'binding':{'name':V.U14_BINDING,'sha256':V.U14_BINDING_SHA256}},'base entry/binding differs')
    need(b['v1']=={'entry':{'path':V1_ENTRY,'sha256':V1_ENTRY_SHA256},'binding':{'name':V1_BINDING,'sha256':V1_BINDING_SHA256}},'binding-08 entry/binding differs')
    need(set(b)=={'schema','purpose','repository','base','v1','approval','old_chain_files','history_v1'},'binding-09 key set differs')
    # Head, CI, performance, version files, history and spec are binding-08's own (pinned) values, used unchanged.
    b8=V.load_binding(V1_BINDING_SHA256);need(b8['repository']==REPOSITORY,'binding-08 repository differs')
    b7,_,b2=V.verify_base(b8)
    return b8,b7,b2

def verify_history_v1(b):
    """The binding-08 entry, binding, regressions and refused run keep their pinned bytes."""
    need(b.get('history_v1')==HISTORY_V1,'binding-08 history pin set differs')
    m=nc();pins={}
    for rel,pin in sorted(HISTORY_V1.items()):
        need(not (ROOT/rel).is_symlink() and sha(m.read(rel))==pin,'binding-08 history file changed: '+rel);pins[rel]=pin
    refusal=json.loads(m.read(V1_RUN+'refusal.json'))
    need(refusal['error']=='current source changed: Cargo.toml' and refusal['formal_command_adopted'] is False,'binding-08 refused run record differs')
    return pins

def old_chain_pins():
    """The old chain's binding-v4 source pins (bytes checked against U1's REUSED_OLD_CODE pin)."""
    m=nc();pin=m.REUSED_OLD_CODE[OLD_BINDING_V4];raw=m.read(OLD_BINDING_V4);need(sha(raw)==pin,'old chain binding-v4 differs')
    d=json.loads(raw);need(d['head']==m.LOGICAL_HEAD,'old chain binding-v4 head differs');return d['source_files']

def cargo_toml_diff(old,new):
    """Cargo.toml: only workspace.package.version and the 11 internal dependency versions 0.0.0 -> 0.1.0."""
    try:o=tomllib.loads(old.decode('utf-8'));n=tomllib.loads(new.decode('utf-8'))
    except (UnicodeDecodeError,tomllib.TOMLDecodeError) as error:raise ValueError('Cargo.toml does not parse') from error
    pkg=o.get('workspace',{}).get('package',{});deps=o.get('workspace',{}).get('dependencies',{})
    need(pkg.get('version')==OLD_VERSION and n.get('workspace',{}).get('package',{}).get('version')==NEW_VERSION,'Cargo.toml workspace.package.version is not 0.0.0 -> 0.1.0')
    expected=copy.deepcopy(o);expected['workspace']['package']['version']=NEW_VERSION
    ndeps=n.get('workspace',{}).get('dependencies',{})
    for name in INTERNAL_DEPS:
        d=deps.get(name);c=ndeps.get(name)
        need(isinstance(d,dict) and set(d)=={'path','version'} and d['path']=='crates/'+name,'Cargo.toml internal dependency differs: '+name)
        need(d['version']==OLD_VERSION and isinstance(c,dict) and c.get('version')==NEW_VERSION,'Cargo.toml internal dependency version is not 0.0.0 -> 0.1.0: '+name)
        expected['workspace']['dependencies'][name]['version']=NEW_VERSION
    for section in sorted(set(o)|set(n)):
        need(expected.get(section)==n.get(section),'Cargo.toml differs beyond the version values: '+section)
    need(expected==n,'Cargo.toml differs beyond the version values')
    ol=old.split(b'\n');nl=new.split(b'\n');need(len(ol)==len(nl),'Cargo.toml line count differs')
    want={b'version = "0.0.0"'}|{('%s = { path = "crates/%s", version = "0.0.0" }'%(x,x)).encode() for x in INTERNAL_DEPS}
    diff=[i for i in range(len(ol)) if ol[i]!=nl[i]]
    need(len(diff)==len(INTERNAL_DEPS)+1,'Cargo.toml changed line count differs')
    for i in diff:need(ol[i] in want and nl[i]==ol[i].replace(b'"0.0.0"',b'"0.1.0"'),'Cargo.toml line differs beyond a version value: line '+str(i+1))
    need({ol[i] for i in diff}==want,'Cargo.toml changed lines do not cover the versions')
    tables=[i for i,line in enumerate(ol) if line.startswith(b'[')]
    def table(i):return ol[max(t for t in tables if t<i)] if any(t<i for t in tables) else None
    for i in diff:
        want_table=b'[workspace.package]' if ol[i]==b'version = "0.0.0"' else b'[workspace.dependencies]'
        need(table(i)==want_table,'Cargo.toml version line is outside its table: line '+str(i+1))
    return dict(changed_lines=len(diff),internal_dependencies=list(INTERNAL_DEPS),workspace_package_version=[OLD_VERSION,NEW_VERSION])

def verify_old_chain_files(b,b2,head):
    """(e) Cargo.toml version-only and (f) the four exact-bytes files; returns (summary, exact old-byte mapping)."""
    m=nc();pins=old_chain_pins();names=[CARGO_TOML,*EXACT_FILES]
    entries=b['old_chain_files']
    need(isinstance(entries,dict) and set(entries)==set(names) and len(entries)==len(names),'old-chain allowance differs from the authorized path set')
    prior=m.git_blobs(v1().PRIOR_HEAD,names);base=m.git_blobs(b2['head'],names);logical=m.git_blobs(m.LOGICAL_HEAD,names);new=m.git_blobs(head,names)
    mapping={};summary={}
    for p in names:
        e=entries[p];kind='version-only' if p==CARGO_TOML else 'exact-bytes'
        need(isinstance(e,dict) and set(e)=={'kind','old_sha256','new_sha256'} and e['kind']==kind,'old-chain entry differs: '+p)
        old=prior[p]
        need(e['old_sha256']==pins.get(p)==sha(old)==sha(base[p])==sha(logical[p]),'old-chain old pin differs: '+p)
        current=m.read(p)
        need(sha(current)==e['new_sha256']==sha(new[p]),'old-chain file differs from binding/signed head: '+p)
        need(e['new_sha256']!=e['old_sha256'],'old-chain allowance is not a change: '+p)
        row=dict(kind=kind,old_sha256=e['old_sha256'],new_sha256=e['new_sha256'])
        if p==CARGO_TOML:row['diff']=cargo_toml_diff(old,current)
        else:row['scope']=EXACT_SCOPE
        summary[p]=row;mapping[str(ROOT/p)]=old
    return summary,mapping

EXACT_SCOPE='この許可は、bytesがU15の承認済みSteps 13〜14の署名済みhead bb197e04のbytesであることだけを証明する。内容はU15のレビューと試験で確かめるものであり、このコマンドでは確かめていない。'

def verify(b,reuse_compat=True):
    """binding-09 checks, then the unchanged U14 entry's verify with all 8 allowed files at their old bytes."""
    V=v1();b8,b7,b2=verify_base(b)
    history=V.verify_history(b8);history_v1=verify_history_v1(b)
    head=V.verify_head(b8,b7,b2)
    versions,version_map=V.verify_versions(b8,b2,head['head'])
    files,file_map=verify_old_chain_files(b,b2,head['head'])
    mapping8={**version_map,**file_map};need(sorted(str(Path(k).relative_to(ROOT)) for k in mapping8)==list(allowed_paths()),'logical view outside the 8 allowed paths')
    with view_class()(mapping8) as view:inner,mapping=u14().verify(b7,reuse_compat)
    read={c['path'] for c in view.calls};need(set(version_map)<=read,'U1 checks did not read the version files through the logical view')
    need(not set(mapping)&set(mapping8),'U14 and U15 logical views overlap')
    summary=dict(u14=inner,u15=dict(head=head,version_files=versions,old_chain_files=files,history=history,history_v1=history_v1,
        logical_view_paths=sorted(str(Path(k).relative_to(ROOT)) for k in mapping8)))
    return summary,{**mapping,**mapping8}

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
    """The reused old chain driver; its parent process is also shown the 8 allowed files at their old bytes only."""
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
    pinned=set(old_chain_pins())&set(allowed_paths());need(pinned<=set(trace['old_chain_parent_logical_reads']),'old chain did not read its pinned allowed files through the logical view')
    return dict(output=str(created[0].relative_to(ROOT)),result=result,children=len(receipts),parent_logical_reads=trace['old_chain_parent_logical_reads']),created[0]

CLAIMED_V2=('Cargo.tomlの差が、workspace.package.versionと内部の依存11件のversionの 0.0.0 → 0.1.0 だけであること（構文と行の両方で確認）。古いbytesは旧chainのbinding-v4の固定・57a8c96f・1ceae86c・be45のblob、新しいbytesはbb197e04のblob',
    'README.md・docs/release.md・tests/release/test_policy.py・tests/release/test_package.pyの今のbytesがbb197e04のblob（binding-09の固定）であり、古いbytesが旧chainのbinding-v4の固定・57a8c96f・1ceae86c・be45のblobであること')
# v2's statement of what is allowed. It replaces binding-08's 3-file statements (v1 NOT_CLAIMED[0] and the
# u15_version scope / not_claimed[0]), which are false for this entry; v1's bytes are not changed.
ALLOWANCE_V2=('許すのは8ファイルだけである。版の行（0.0.0 → 0.1.0）だけの証明が4つ（Cargo.lock・fuzz/Cargo.lock・packages/paludarium-wasm/package.json・Cargo.toml）、'
    'bb197e04のbytesへの固定が4つ（README.md・docs/release.md・tests/release/test_policy.py・tests/release/test_package.py）。署名headはbb197e04、CIの記録はbb197e04のrunである。FR10.1・U15の受け入れはGAPのまま。')
UNPINNED_ADDED=('scripts/release/acceptance.py','tests/release/test_acceptance.py','.github/workflows/u15-acceptance.yml')
NOT_CLAIMED_V2=('8ファイル以外の差を許すこと。この入口が許すのは、版の行だけの証明4つ（Cargo.lock・fuzz/Cargo.lock・packages/paludarium-wasm/package.json・Cargo.toml）と、bb197e04のbytesへの固定4つ（README.md・docs/release.md・tests/release/test_policy.py・tests/release/test_package.py）だけである',
    'README.md・docs/release.md・tests/release/test_policy.py・tests/release/test_package.pyの内容が正しいこと。'+EXACT_SCOPE,
    'bb197e04で足された3ファイル（'+'・'.join(UNPINNED_ADDED)+'）の作業ツリーのbytes。この3つは採用済みのchainの固定の範囲の外であり、このコマンドはbytesを固定していない（commitとcompareのファイル一覧に入っていることだけを確かめる）。bytesはU15のレビュー・試験とCIで確かめる')

def statements():
    """(claimed, not_claimed) of v2: v1's lists with v1's 3-file not_claimed[0] replaced by v2's statements."""
    V=v1();need(V.NOT_CLAIMED[0].startswith('3ファイル以外の差'),'binding-08 not_claimed[0] differs')
    return [*V.CLAIMED,*CLAIMED_V2],[*NOT_CLAIMED_V2,*V.NOT_CLAIMED[1:]]

def u15_scope_v2(scope,u15):
    out=v1().u15_scope(scope,u15);claimed,not_claimed=statements()
    version=dict(out['u15_version']);version.update(scope=ALLOWANCE_V2,claimed=claimed,not_claimed=not_claimed)
    out={**out,'u15_version':version}
    note=dict(old_chain_files=sorted(u15['old_chain_files']),allowed_paths=list(allowed_paths()),claimed=list(CLAIMED_V2),not_claimed=list(NOT_CLAIMED_V2),exact_bytes_scope=EXACT_SCOPE,
        approval='人の承認（2026-10-18）：Cargo.tomlは版の行だけの証明、README.md・docs/release.md・tests/releaseの2つはbb197e04のバイト列の固定で許可を足す。package.jsonの照合の扱いもそれでよい。')
    return {**out,'u15_old_chain':note}

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
        trace['stage']='verify (binding-09, binding-08 checks and the unchanged U14 entry under the 8-file view)'
        before,mapping=verify(b)
        mapping8={k:v for k,v in mapping.items() if k in {str(ROOT/p) for p in allowed_paths()}}
        trace['stage']='old chain (final_candidate.main and its validators)'
        old,old_output=run_old_chain(entry,pin,out,mapping8,trace)
        trace['stage']='claim scope'
        _,_,b2=verify_base(b);s14=before['u14'];u11=u14().u11()
        scope=u15_scope_v2(u14().u14_scope(u11.head_scope(u11.u2().claim_scope(b2,old_output,s14['u11']['u2']['u1']['module_receipt']),s14['u11']['u11']['head']),s14['u14']),before['u15'])
        trace['stage']='re-verify'
        after,_=verify(b);need(after==before,'inputs changed during validation')
        check_pins(entry,pin)
        V=v1()
        result=dict(u15_candidate_v2='PASS',command_line=dict(entry_sha256=entry,binding_sha256=pin),binding=BINDING,binding_sha256=pin,entry_sha256=entry,
            base_entry=dict(path=V.U14_ENTRY,sha256=V.U14_ENTRY_SHA256),base_binding=dict(name=V.U14_BINDING,sha256=V.U14_BINDING_SHA256),
            v1_entry=dict(path=V1_ENTRY,sha256=V1_ENTRY_SHA256,binding=V1_BINDING,binding_sha256=V1_BINDING_SHA256),
            u1_physical=s14['u11']['u2']['u1'],u2_records=s14['u11']['u2']['u2'],u11=s14['u11']['u11'],u14=s14['u14'],u15=before['u15'],old_chain=old,claim_scope=scope,
            allowed_paths=list(allowed_paths()),
            allowance=dict(version_only=sorted([*V.VERSION_FILES,CARGO_TOML]),exact_bytes=list(EXACT_FILES),
                exact_bytes_scope=EXACT_SCOPE,
                exact_bytes_scope_en='This allowance proves only that the bytes are the signed-head (bb197e04) bytes of U15\'s approved Steps 13-14; their content is checked by U15\'s review and tests, not by this command.'),
            claimed=statements()[0],not_claimed=statements()[1],allowance_statement=ALLOWANCE_V2,
            ci_inputs='stored hash-bound JSON only; no live GitHub query at check time',
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False)
        with (out/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
        print(json.dumps(dict(output=str(out.relative_to(ROOT)),u15_candidate_v2='PASS',old_chain_source_compatibility=old['result']['source_compatibility'],FR10_1='GAP',U15_acceptance='GAP',unit_completed=False)))
        return 0
    except BaseException as error:
        with (out/'refusal.json').open('x',encoding='utf-8') as f:
            json.dump(dict(error=str(error),refused_at=trace,traceback=traceback.format_exc(),allowed_paths=list(ALLOWED_PATHS),
                allowance='version-only for Cargo.lock, fuzz/Cargo.lock, package.json, Cargo.toml; exact signed-head bytes for README.md, docs/release.md, tests/release/test_policy.py, tests/release/test_package.py; not widened',
                FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False),f,indent=2,ensure_ascii=False)
        print('REFUSED: '+str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main(sys.argv))
