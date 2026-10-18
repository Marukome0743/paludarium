"""Regressions for entry-e.py with binding-e05.json (the person's decision of 2026-10-18: version e).

Version e keeps every check of version d and replaces only lineage and changed
files: (E1) the stored commit records (GitHub commit API copies) must cover
exactly the chain, every commit Verified, its tree hash equal to local git and
its parents equal to local git and the chain; (E2) changed files are counted
from local git only, the list outside aidlc/ equals the binding, the aidlc/
count and list SHA-256 equal the binding; (E3) the GitHub compare is not used.
test_entry.py .. test_entry_d.py are kept unchanged.

Every refusal case changes exactly one input in memory (the entry's
regression-only OVERLAY, deep copies of the binding or of the entry's pinned
constants through unittest.mock, JSON/ZIP documents served from in-memory
paths, or a wrapped git answer) and asserts the message of the check that must
stop it, so each case fails if that check is removed. No real repository file
is modified; git is only read. Temporary folders (in-process run outputs, git
configuration fixtures) are created inside this entry folder and removed.

Local dependency (stated, not hidden): the working copy of this machine
carries the uncommitted product changes of U15 Steps 22-24, so its bytes are
not those of e3c29d1d. The positive control therefore shows the e3c29d1d bytes
through a regression-only overlay built in setUpClass (BASE_OVERLAY): every
tracked path outside aidlc/ whose working bytes differ from, or that is missing
against, the e3c29d1d blob is served as that blob, and every untracked path
that no exclusion covers is shown as absent. The overlay is computed from
local git and listed in the test output; the real run of entry-e is done after
the push, on the new head (binding-e06), not here.
"""
import contextlib,copy,hashlib,importlib.util,io,json,os,re,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry_e3c29d1d_e_under_test',OWN/'entry-e.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
ROOT=E.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
ENTRY='entry-e.py';BINDING='binding-e05.json'
BINDING_PIN=sha((OWN/BINDING).read_bytes());ENTRY_PIN=sha((OWN/ENTRY).read_bytes())
HEAD=E.BASE;PARENT='a54315f9493d6e9fb8d4792ffcefd12203540311'
RECORDS='a7aecb721'  # local commit on top of e3c29d1d that changes only aidlc/ paths (741 files)
CHANGED_7=['docs/release.md','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_policy.py','tests/release/test_publish_adapter.py']
U12='39114110570';U13='39114112207';U14='39114108809';CI_RUN='39114018191'
FAKE=E.HERE+'regression-in-memory/'
REAL_GIT=E.git
BASE_OVERLAY={}

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def exists(rel):return (ROOT/rel).exists()
@contextlib.contextmanager
def overlay(files=None):
    saved=E.OVERLAY;E.OVERLAY=dict(BASE_OVERLAY,**(files or {}))
    try:yield
    finally:E.OVERLAY=saved

def build_base_overlay():
    """Regression-only: the e3c29d1d bytes for every tracked path that differs or is missing, absence for unexpected paths."""
    E.OVERLAY={}
    try:E.verify_working_copy(HEAD,E.EXCLUSIONS);return {}
    except E.Refusal as error:d=error.details
    finally:E.OVERLAY=None
    tree=E.head_tree(HEAD);content=E.blobs(sorted({tree[p][1] for p in d['differing']+d['missing']}))
    out={p:content[tree[p][1]] for p in d['differing']+d['missing']}
    out.update({p:None for p in d['unexpected']})
    return out

def records_doc(rows):
    raw=json.dumps(dict(schema=1,source='regression',repository=E.REPOSITORY,commits=rows)).encode()
    return {'path':FAKE+'commits.json','sha256':sha(raw)},{FAKE+'commits.json':raw}

def record(c,verified=True,reason='valid',tree=None,parents=None):
    return dict(sha=c,parents=[dict(sha=p) for p in (E.git_parents(c) if parents is None else parents)],
        commit=dict(tree=dict(sha=tree or E.git_tree(c)),verification=dict(verified=verified,reason=reason)))

def git_answering(forced):
    def wrapped(*args,stdin=None,ok=(0,)):
        raw=REAL_GIT(*args,stdin=stdin,ok=ok)
        if args[0]!='check-ignore':return raw
        f=raw.split(b'\0');f=f[:-1] if f and f[-1]==b'' else f;out=[]
        for i in range(0,len(f),4):
            path=f[i+3].decode()
            if path in forced:out+=[x.encode() for x in forced[path]]+[f[i+3]]
            else:out+=f[i:i+4]
        return b''.join(x+b'\0' for x in out)
    return wrapped

class EntryEE05(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global BASE_OVERLAY
        BASE_OVERLAY=build_base_overlay()
        print('\n[test_entry_e] e3c29d1d-bytes overlay: '+str(len(BASE_OVERLAY))+' paths: '+', '.join(sorted(BASE_OVERLAY))[:2000],file=sys.stderr)
        cls.b=E.strict_json((OWN/BINDING).read_bytes(),BINDING)
        cls.tree=E.head_tree(HEAD)
        cls.ci_doc=json.loads(E.read(cls.b['ci']['path']));cls.jobs_doc=json.loads(E.read(cls.b['ci_jobs']['path']))
        cls.arts_doc=json.loads(E.read(cls.b['ci_artifacts']['path']))
    def rejects(self,pattern,fn,**files):
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):fn()
    def passes(self,fn,**files):
        with overlay(files):return fn()
    def variant(self,edit):b=copy.deepcopy(self.b);edit(b);return b
    def full(self,b=None):return lambda:E.verify(b or self.b)
    def blob(self,p):return E.blobs([self.tree[p][1]])[self.tree[p][1]]
    def wc(self,**files):
        with overlay(files):return E.verify(self.b)['working_copy']
    def ci_spec(self,edit_ci=None,edit_jobs=None,edit_spec=None,repo_doc=None):
        ci=copy.deepcopy(self.ci_doc);jobs=copy.deepcopy(self.jobs_doc)
        if repo_doc:repo_doc(ci,jobs)
        if edit_ci:edit_ci(ci)
        if edit_jobs:edit_jobs(jobs)
        rc=json.dumps(ci).encode();rj=json.dumps(jobs).encode()
        s=copy.deepcopy(self.b['ci']);s.update(path=FAKE+'ci.json',sha256=sha(rc));j={'path':FAKE+'jobs.json','sha256':sha(rj)}
        if edit_spec:edit_spec(s)
        return s,j,{FAKE+'ci.json':rc,FAKE+'jobs.json':rj}
    def ci_rejects(self,pattern,**kw):
        s,j,files=self.ci_spec(**kw)
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):E.verify_ci(s,j,HEAD,E.REPOSITORY)
    def ci_passes(self,**kw):
        s,j,files=self.ci_spec(**kw)
        with overlay(files):return E.verify_ci(s,j,HEAD,E.REPOSITORY)
    def run_of(self,doc,rid):return next(r for r in doc['runs'] if str(r['id'])==rid)
    def with_tree_entry(self,path,blob_of='README.md'):
        tree=dict(self.tree);tree[path]=self.tree[blob_of]
        return mock.patch.object(E,'head_tree',lambda head:dict(tree))
    def lineage(self,rows,chain,base,head):
        s,files=records_doc(rows)
        with overlay(files):return E.verify_lineage(s,chain,base,head)
    def lineage_rejects(self,pattern,rows,chain,base,head):
        s,files=records_doc(rows)
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):E.verify_lineage(s,chain,base,head)
    def records_head(self):return REAL_GIT('rev-parse','--verify',RECORDS+'^{commit}').decode().strip()

    # ---- positive control (e3c29d1d bytes through the overlay) -----------------
    def test_00_overlay_is_needed_and_stated(self):
        # Without the overlay the working copy (Steps 22-24 product edits) is refused; with it, it equals e3c29d1d.
        if BASE_OVERLAY:
            saved=E.OVERLAY;E.OVERLAY=None
            try:
                with self.assertRaisesRegex(E.Refusal,'working copy differs from head'):E.verify(self.b)
            finally:E.OVERLAY=saved
        self.assertFalse([p for p in BASE_OVERLAY if E.in_aidlc(p)])
    def test_01_positive_control_e3c29d1d_bytes(self):
        s=self.passes(self.full())
        self.assertEqual((s['head'],s['changed_paths'],s['lineage']['chain']),(HEAD,[],[HEAD]))
        self.assertEqual(s['aidlc_changed_paths']['count'],0);self.assertEqual(s['aidlc_changed_paths']['sha256'],sha(b''))
        self.assertFalse(s['compare']['used']);self.assertFalse(s['lineage']['compare_used'])
        self.assertEqual(s['lineage']['trees'],{HEAD:E.BASE_TREE})
        wc=s['working_copy'];self.assertEqual(wc['head_tree_files_outside_aidlc'],len(self.tree))
        self.assertEqual(wc['compared_equal'],len(self.tree)-2)
        self.assertEqual(wc['ignored_by_a_source_not_accepted'],{})
        name={r['path']:r for r in wc['excluded_by_name']}
        for p in ('mise.toml','.aidlc-version'):self.assertEqual(name[p]['rule'],'path_bytes_may_differ:'+p)
        self.assertIn('aidlc/ の中は比べない',name['aidlc/']['note'])
        self.assertEqual(sorted(s['ci']['runs']),sorted(self.b['ci']['runs']));self.assertEqual(s['ci']['differences_from_base']['rerun_limit'],2)
        self.assertTrue(s['performance'][U14]['passed']);self.assertEqual(s['performance'][U14]['repository_id'],E.REPOSITORY_ID)
        self.assertFalse(s['upstream']['used'])

    # ---- (1) lineage by commit records (E1) -------------------------------------
    def test_20_lineage_positive_two_commits(self):
        out=self.lineage([record(PARENT),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        self.assertEqual(out['trees'],{PARENT:E.git_tree(PARENT),HEAD:E.BASE_TREE});self.assertFalse(out['compare_used'])
    def test_21_tree_mismatch(self):
        self.lineage_rejects('stored tree differs from local git: '+HEAD,[record(PARENT),record(HEAD,tree='3'*40)],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('stored tree differs from local git: '+PARENT,[record(PARENT,tree='3'*40),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        bad=record(HEAD);del bad['commit']['tree']
        self.lineage_rejects('stored tree differs from local git',[bad],[HEAD],HEAD,HEAD)
    def test_22_parents_differ(self):
        self.lineage_rejects('stored parents differ from local git: '+HEAD,[record(PARENT),record(HEAD,parents=['1'*40])],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('stored parents differ from local git: '+PARENT,[record(PARENT,parents=[]),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        bad=record(HEAD);bad['parents']='x'
        self.lineage_rejects('stored parents differ',[bad],[HEAD],HEAD,HEAD)
        def other_parent(*args,**kw):
            if args[:2]==('rev-list','--parents'):return (args[-1]+' '+'7'*40+'\n').encode()
            return REAL_GIT(*args,**kw)
        with mock.patch.object(E,'git',other_parent):
            self.lineage_rejects('stored parents differ from local git',[record(HEAD,parents=[PARENT])],[HEAD],HEAD,HEAD)
    def test_23_chain_parent_and_order(self):
        # parents equal local git, but the chain skips a commit: the chain check stops it
        grand=E.git_parents(PARENT)[0]
        self.lineage_rejects('stored parent differs from the chain: '+HEAD,[record(grand),record(HEAD)],[grand,HEAD],grand,HEAD)
        self.lineage_rejects('from the base to the head',[record(PARENT),record(HEAD)],[HEAD,PARENT],PARENT,HEAD)
        def other_order(*args,**kw):
            if args[:2]==('rev-list','--reverse'):return b'1111111111111111111111111111111111111111\n'
            return REAL_GIT(*args,**kw)
        with mock.patch.object(E,'git',other_order):
            self.lineage_rejects('local commit order differs',[record(PARENT),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
    def test_24_unsigned_commit(self):
        for kw in (dict(verified=False),dict(reason='unsigned'),dict(verified='true')):
            with self.subTest(**kw):self.lineage_rejects('not Verified in the stored record: '+HEAD,[record(PARENT),record(HEAD,**kw)],[PARENT,HEAD],PARENT,HEAD)
        bad=record(HEAD);del bad['commit']['verification']
        self.lineage_rejects('not Verified',[bad],[HEAD],HEAD,HEAD)
    def test_25_commit_missing_extra_or_twice_in_records(self):
        self.lineage_rejects('do not cover exactly the chain: missing '+PARENT,[record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('do not cover exactly the chain: missing ; extra '+PARENT,[record(PARENT),record(HEAD)],[HEAD],HEAD,HEAD)
        self.lineage_rejects('list a commit twice',[record(HEAD),record(HEAD)],[HEAD],HEAD,HEAD)
    def test_26_records_file_pinned_and_shaped(self):
        s,files=records_doc([record(HEAD)])
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'commit records bytes differ'):E.verify_lineage(dict(s,sha256='0'*64),[HEAD],HEAD,HEAD)
            with self.assertRaisesRegex(E.Refusal,'commit records binding key set'):E.verify_lineage(dict(s,extra=1),[HEAD],HEAD,HEAD)
        raw=json.dumps(dict(repository='someone/else',commits=[record(HEAD)])).encode()
        with overlay({FAKE+'c.json':raw}):
            with self.assertRaisesRegex(E.Refusal,'commit records repository differs'):E.verify_lineage({'path':FAKE+'c.json','sha256':sha(raw)},[HEAD],HEAD,HEAD)
        self.rejects('commit records bytes differ',self.full(),**{self.b['commit_records']['path']:E.read(self.b['commit_records']['path'])+b' '})
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.pop('commit_records'))))
    def test_27_stored_record_of_e3c29d1d_is_the_real_one(self):
        doc=json.loads(E.read(self.b['commit_records']['path']))
        self.assertEqual(doc['commits'],[record(HEAD)])
    def test_28_more_than_300_changed_files_pass(self):
        head=self.records_head();local=sorted(p.decode() for p in REAL_GIT('diff-tree','-r','-z','--no-renames','--name-only',HEAD,head).split(b'\0') if p)
        self.assertGreater(len(local),300);self.assertTrue(all(p.startswith('aidlc/') for p in local))
        out=self.lineage([record(HEAD),record(head,parents=[HEAD])],[HEAD,head],HEAD,head)
        self.assertEqual(out['head_tree'],E.git_tree(head))
        changed=E.verify_changed([],dict(count=len(local),sha256=sha('\n'.join(local).encode())),HEAD,head)
        self.assertEqual((changed['product'],changed['aidlc']['count']),([],len(local)));self.assertFalse(changed['compare']['used'])

    # ---- (2) changed files by local git (E2) -------------------------------------
    def aidlc_of(self,base,head):
        local=sorted(p.decode() for p in REAL_GIT('diff-tree','-r','-z','--no-renames','--name-only',base,head).split(b'\0') if p and p.startswith(b'aidlc/'))
        return dict(count=len(local),sha256=sha('\n'.join(local).encode()))
    def test_30_product_list_exact_more_fewer(self):
        a=self.aidlc_of(PARENT,HEAD);self.assertEqual(a['count'],0)
        self.assertEqual(E.verify_changed(CHANGED_7,a,PARENT,HEAD)['product'],CHANGED_7)
        with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed(CHANGED_7[1:],a,PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed(sorted(CHANGED_7+['README.md']),a,PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'sorted unique'):E.verify_changed(list(reversed(CHANGED_7)),a,PARENT,HEAD)
        self.rejects('changed product files differ',self.full(self.variant(lambda b:b['changed_files'].append('README.md'))))
    def test_31_aidlc_count_and_digest(self):
        head=self.records_head();a=self.aidlc_of(HEAD,head)
        self.assertEqual(E.verify_changed([],a,HEAD,head)['aidlc'],dict(E.verify_changed([],a,HEAD,head)['aidlc'],**a))
        with self.assertRaisesRegex(E.Refusal,'aidlc/ file count differs'):E.verify_changed([],dict(a,count=a['count']-1),HEAD,head)
        with self.assertRaisesRegex(E.Refusal,'aidlc/ file count differs'):E.verify_changed([],dict(a,count=a['count']+1),HEAD,head)
        with self.assertRaisesRegex(E.Refusal,'aidlc/ file list SHA-256 differs'):E.verify_changed([],dict(a,sha256='0'*64),HEAD,head)
        self.rejects('aidlc/ file count differs',self.full(self.variant(lambda b:b['aidlc_changed'].update(count=1))))
        self.rejects('aidlc/ file list SHA-256 differs',self.full(self.variant(lambda b:b['aidlc_changed'].update(sha256='0'*64))))
    def test_32_aidlc_shape_and_paths_in_binding(self):
        a=self.aidlc_of(PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'names a path inside aidlc/'):E.verify_changed(['aidlc/x.md'],a,PARENT,HEAD)
        for bad in (None,{},dict(a,extra=1),dict(a,count='0'),dict(a,count=True),dict(a,sha256='abc'),dict(a,sha256='0'*64+'0')):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(E.Refusal,'aidlc_changed differs'):E.verify_changed(CHANGED_7,bad,PARENT,HEAD)
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.pop('aidlc_changed'))))
    def test_33_list_digest_rule(self):
        self.assertEqual(E.list_digest([]),sha(b''));self.assertEqual(E.list_digest(['aidlc/a','aidlc/b']),sha(b'aidlc/a\naidlc/b'))
    def test_34_compare_is_not_used(self):
        # A stored compare that is truncated, wrong or absent changes nothing: version e never reads it.
        for edit in (lambda d:d['compare'].update(files=[]),lambda d:d['compare'].update(status='diverged',ahead_by=99),lambda d:d.pop('compare')):
            s,j,files=self.ci_spec(edit_ci=edit)
            out=self.passes(self.full(self.variant(lambda b:b.update(ci=s))),**files)
            self.assertFalse(out['compare']['used'])
        self.assertNotIn('compare',E.verify_changed.__code__.co_varnames)

    # ---- (3) working copy (kept from version d) -----------------------------------
    def test_40_head_gitignore_rules_exclude_untracked_files(self):
        wc=self.wc(**{'docs/notes.log':b'x','crates/x.profraw':b'','scratch.local':b'1'})
        git={r['path']:r['pattern'] for r in wc['excluded_by_git_ignore']}
        for p,pat in (('docs/notes.log','*.log'),('crates/x.profraw','*.profraw'),('scratch.local','*.local')):
            self.assertTrue(git[p].startswith('.gitignore:') and git[p].endswith(':'+pat),git[p])
    def test_41_other_ignore_sources_refused(self):
        forced={'crates/x/new.rs':('.git/info/exclude','1','*.rs')}
        with mock.patch.object(E,'git',git_answering(forced)):
            self.rejects('unexpected: crates/x/new.rs',self.full(),**{'crates/x/new.rs':b'x'})
        status,foreign=E.parse_check_ignore(b''.join(x+b'\0' for x in (b'.git/info/exclude',b'1',b'*.rs',b'a.rs')),['a.rs'],{'.gitignore'})
        self.assertEqual((status,sorted(foreign)),({'a.rs':None},['a.rs']))
    def test_42_unknown_files_and_tracked_bytes_refused(self):
        for p in ('crates/paludarium-types/src/extra.rs','new-top-level.txt','tools/aidlc-recoveryX/a.txt'):
            self.rejects('unexpected: '+re.escape(p),self.full(),**{p:b'x'})
        raw=self.blob('Cargo.toml');self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
        self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})
        with self.with_tree_entry('tools/aidlc-recovery/local-runtime.patch'):
            self.rejects('differing: tools/aidlc-recovery/local-runtime.patch',self.full(),**{'tools/aidlc-recovery/local-runtime.patch':b'other'})
    def test_43_only_two_tracked_files_may_differ(self):
        wc=self.wc(**{'.aidlc-version':b'anything\n','mise.toml':b'x\n'})
        rows={r['path']:r for r in wc['excluded_by_name']};self.assertFalse(rows['mise.toml']['bytes_equal_head'])
        raw=self.blob('.gitignore');self.rejects(r'differing: \.gitignore',self.full(),**{'.gitignore':raw+b'\n'})
    def test_44_exclusion_list_must_equal_the_approved_list(self):
        for edit in (lambda b:b['exclusions']['top_level'].append('spikes'),lambda b:b['exclusions']['paths_bytes_may_differ'].append('Cargo.toml')):
            self.rejects('exclusion list differs',self.full(self.variant(edit)))
    def test_45_git_reads_no_user_or_system_configuration(self):
        env=E.git_env();self.assertEqual((env['GIT_CONFIG_GLOBAL'],env['GIT_CONFIG_NOSYSTEM']),(os.devnull,'1'))
        with tempfile.TemporaryDirectory(dir=OWN,prefix='regression-home-') as tmp:
            (Path(tmp)/'.gitconfig').write_text('[[[ this is not git configuration\n')
            with mock.patch.dict(os.environ,{'HOME':tmp,'XDG_CONFIG_HOME':tmp,'GIT_DIR':'/nonexistent'}):
                plain=subprocess.run(['git','rev-parse','--verify',HEAD+'^{tree}'],cwd=ROOT,capture_output=True,timeout=60,
                    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')})
                self.assertNotEqual(plain.returncode,0)
                self.assertEqual(E.git_tree(HEAD),E.BASE_TREE);self.assertEqual(E.git_parents(HEAD),[PARENT])
    def test_46_git_is_read_only(self):
        for cmd in ('status','checkout','update-ref','fetch'):
            with self.assertRaisesRegex(E.Refusal,'read-only set'):E.git(cmd)

    # ---- (4) CI, (5) performance (kept from version d) -----------------------------
    def test_50_ci_required_workflows_reruns_and_limit(self):
        out,_=self.ci_passes();self.assertEqual(len(out['runs']),7)
        def drop_spec(s):s['workflows'].remove('U13 current full quality');s['runs'].pop(U13)
        self.ci_rejects('drops a required workflow',edit_spec=drop_spec)
        self.ci_rejects('not completed/success',edit_ci=lambda d:self.run_of(d,CI_RUN).update(conclusion='failure'))
        self.ci_rejects('failed job differs',edit_spec=lambda s:s['reruns'][U12].update(job_id=1))
        allow={'job_name':'x','job_id':1,'approval':'人の承認（回帰用）'}
        self.ci_rejects('exceed the limit of 2 per binding',edit_spec=lambda s:s['reruns'].update({U13:allow,U14:allow}))
        self.ci_rejects('CI record bytes differ',edit_spec=lambda s:s.update(sha256='0'*64))
    def perf_variant(self,edit_arts=None,edit_obs=None):
        p=copy.deepcopy(self.b['performance']);e=p['runs'][U14];orig=json.loads(E.read(e['path']))
        if edit_obs:edit_obs(orig)
        raw=json.dumps(orig).encode();buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('performance/observations.json',raw)
        z=buf.getvalue();e.update(path=FAKE+'obs.json',sha256=sha(raw));e['artifact'].update(zip_path=FAKE+'u11.zip')
        arts=copy.deepcopy(self.arts_doc);node=next(a for a in arts['runs'][0]['artifacts'] if a['name']=='u11-node')
        node.update(digest='sha256:'+sha(z),size_in_bytes=len(z))
        if edit_arts:edit_arts(node)
        ra=json.dumps(arts).encode()
        return p,{'path':FAKE+'arts.json','sha256':sha(ra)},{FAKE+'obs.json':raw,FAKE+'u11.zip':z,FAKE+'arts.json':ra}
    def test_51_performance_expired_repository_and_passed(self):
        p,a,files=self.perf_variant()
        with overlay(files):self.assertTrue(E.verify_performance(p,a,self.b['ci']['runs'],HEAD)[U14]['passed'])
        for kw,pattern in ((dict(edit_arts=lambda n:n.update(expired=True)),'expired'),(dict(edit_arts=lambda n:n['workflow_run'].update(repository_id=1)),'repository_id'),
                           (dict(edit_obs=lambda o:o.update(passed=False)),'passed is not true'),(dict(edit_arts=lambda n:n.update(size_in_bytes=1)),'stored API digest')):
            p,a,files=self.perf_variant(**kw)
            with overlay(files):
                with self.assertRaisesRegex(E.Refusal,pattern):E.verify_performance(p,a,self.b['ci']['runs'],HEAD)

    # ---- (0) base records and history -------------------------------------------
    def test_60_base_records_and_history(self):
        c=E.BASE_RECORDS['checkpoint']
        self.rejects('base checkpoint record bytes',self.full(),**{c['copy']:E.read(c['copy'])+b' '})
        self.assertEqual(len(E.HISTORY),24)  # v1-v4 12 files + entry/b/c/d, binding-e01..e04, test_entry..test_entry_d 12 files
        for v in ('entry-d.py','binding-e04.json','test_entry_d.py','entry-c.py','binding-e03.json'):
            self.assertEqual(E.HISTORY[E.HERE+v],sha((OWN/v).read_bytes()),v)
        for rel in E.HISTORY:self.rejects('history file bytes differ',self.full(),**{rel:E.read(rel)+b'#'})
        self.rejects('history pins differ',self.full(self.variant(lambda b:b['history'].popitem())))
    def test_61_earlier_bindings_are_refused(self):
        for old in ('binding-e01.json','binding-e02.json','binding-e03.json','binding-e04.json'):
            code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',sha((OWN/old).read_bytes())])
            self.assertEqual(code,1);self.assertRegex(docs['refusal.json']['error'],'binding key set differs|binding schema/repository differs')

    # ---- command line ----------------------------------------------------------------
    def in_process(self,argv,**files):
        err=io.StringIO();out=io.StringIO()
        with tempfile.TemporaryDirectory(dir=OWN,prefix='regression-out-') as tmp:
            saved=E.OUT_DIR;E.OUT_DIR=Path(tmp)
            try:
                with overlay(files),contextlib.redirect_stderr(err),contextlib.redirect_stdout(out):code=E.main([str(E.SELF),*argv])
                made=sorted(Path(tmp).glob('run-*/*'));docs={p.name:json.loads(p.read_bytes()) for p in made}
            finally:E.OUT_DIR=saved
        return code,docs,err.getvalue()
    def test_70_pins_and_arguments_exit_2_without_output(self):
        before=run_dirs()
        for argv,pattern in (([],'usage'),(['--entry-sha256','0'*64,'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
                (['--entry-sha256',sha((OWN/'entry-d.py').read_bytes()),'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
                (['--entry-sha256',ENTRY_PIN,'--binding-sha256','0'*64],'matches no binding')):
            code,docs,err=self.in_process(argv);self.assertEqual(code,2);self.assertEqual(docs,{});self.assertRegex(err,'^REFUSED: .*'+pattern)
        self.assertEqual(run_dirs(),before)
    def test_71_pass_writes_result_json_in_both_languages(self):
        code,docs,_=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN])
        self.assertEqual(code,0);r=docs['result.json'];self.assertEqual(r['entry_e3c29d1d_e'],'PASS')
        self.assertEqual((r['FR10_1'],r['U15_acceptance'],r['formal_command_adopted']),('GAP','GAP',False))
        self.assertFalse(r['compare']['used']);self.assertEqual(r['decision'],E.DECISION_E)
        self.assertTrue(any('tree' in s and 'compare' in s for s in r['claimed_en']));self.assertTrue(any('SHA-1' in s for s in r['not_claimed_en']))
    def test_72_refusal_writes_refusal_json(self):
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{'README.md':None})
        self.assertEqual(code,1);r=docs['refusal.json'];self.assertEqual(r['entry_e3c29d1d_e'],'REFUSED')
        self.assertEqual(r['refused_at']['stage'],'(3) working copy');self.assertEqual(r['details']['missing'],['README.md'])
    def test_73_binding_shape(self):
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.update(extra=1))))
        self.rejects('binding schema/repository differs',self.full(self.variant(lambda b:b.update(schema='u15-entry-e3c29d1d-binding/d1'))))
        self.rejects('binding head is not a commit id',self.full(self.variant(lambda b:b.update(head='e3c29d1d'))))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(EntryEE05)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() and not result.skipped and result.testsRun==suite.countTestCases() else 1)
