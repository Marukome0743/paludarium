"""Regressions for entry-f.py with binding-e05f.json (version f, after independent review 03).

Version f keeps every check of version e and adds F1: git never follows replace
refs (--no-replace-objects on every call, GIT_NO_REPLACE_OBJECTS=1), and a
shallow repository or a graft file is refused. Review 03's Minor 3 is answered
here: no test depends on a pre-push local commit id (version e's tests 28 and
31 used a7aecb72). Those cases now run in a temporary git repository built by
this test (FIXTURE): a root commit A, a commit B that changes 351 files (350
inside aidlc/ and one outside), and a commit C used only as a replacement for
B. test_entry.py .. test_entry_e.py are kept unchanged.

Every refusal case changes exactly one input in memory (the entry's
regression-only OVERLAY, deep copies of the binding or of the entry's pinned
constants through unittest.mock, JSON/ZIP documents served from in-memory
paths, a wrapped git answer, or the entry's ROOT pointed at the temporary
repository) and asserts the message of the check that must stop it, so each
case fails if that check is removed. No real repository file is modified and
the real repository is only read; the temporary repositories (fixture, its
shallow clone, git configuration fixtures and in-process run outputs) are
created inside this entry folder and removed.

Local dependency (stated, not hidden): the working copy of this machine
carries the uncommitted product changes of U15 Steps 22-24, so its bytes are
not those of e3c29d1d. The positive control therefore shows the e3c29d1d bytes
through a regression-only overlay built in setUpClass (BASE_OVERLAY, computed
from local git and listed in the test output). The real run of entry-f is done
after the push, on the new head, not here.
"""
import contextlib,copy,hashlib,importlib.util,io,json,os,re,shutil,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry_e3c29d1d_f_under_test',OWN/'entry-f.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
ROOT=E.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
ENTRY='entry-f.py';BINDING='binding-e05f.json'
BINDING_PIN=sha((OWN/BINDING).read_bytes());ENTRY_PIN=sha((OWN/ENTRY).read_bytes())
HEAD=E.BASE;PARENT='a54315f9493d6e9fb8d4792ffcefd12203540311'
CHANGED_7=['docs/release.md','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_policy.py','tests/release/test_publish_adapter.py']
U12='39114110570';U13='39114112207';U14='39114108809';CI_RUN='39114018191'
FAKE=E.HERE+'regression-in-memory/'
REAL_GIT=E.git
BASE_OVERLAY={}
MANY=350  # aidlc/ files changed by fixture commit B (more than GitHub's 300-file compare cap)

def run_dirs():return {p.name for p in OWN.glob('run-*')}
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

# ---- the temporary git repository (review 03, Minor 3) ---------------------------
FIXTURE_ENV={'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_NOSYSTEM':'1','GIT_AUTHOR_NAME':'regression','GIT_AUTHOR_EMAIL':'regression@example.invalid',
    'GIT_COMMITTER_NAME':'regression','GIT_COMMITTER_EMAIL':'regression@example.invalid','GIT_AUTHOR_DATE':'2026-10-19T00:00:00Z','GIT_COMMITTER_DATE':'2026-10-19T00:00:00Z'}
def fixture_git(repo,*args,replace=True):
    """git in a temporary repository, for building fixtures and as the "plain git" control (it follows replace refs)."""
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')};env.update(FIXTURE_ENV)
    r=subprocess.run(['git','-c','commit.gpgsign=false','-c','core.hooksPath='+os.devnull,*args],cwd=repo,capture_output=True,timeout=120,env=env)
    if r.returncode:raise AssertionError('fixture git '+' '.join(args)+': '+r.stderr.decode())
    return r.stdout.decode().strip()

def build_fixture(root):
    repo=root/'repo';repo.mkdir()
    fixture_git(repo,'init','-q','-b','main')
    (repo/'README.md').write_text('fixture\n');(repo/'aidlc').mkdir();(repo/'aidlc/base.md').write_text('base\n')
    fixture_git(repo,'add','-A');fixture_git(repo,'commit','-q','-m','A');a=fixture_git(repo,'rev-parse','HEAD')
    many=repo/'aidlc/many';many.mkdir()
    for i in range(MANY):(many/('f%03d.txt'%i)).write_text(str(i)+'\n')
    (repo/'docs').mkdir();(repo/'docs/x.md').write_text('x\n')
    fixture_git(repo,'add','-A');fixture_git(repo,'commit','-q','-m','B');b=fixture_git(repo,'rev-parse','HEAD')
    fixture_git(repo,'checkout','-q','-b','side',a);(repo/'README.md').write_text('other\n')
    fixture_git(repo,'commit','-q','-am','C');c=fixture_git(repo,'rev-parse','HEAD')
    fixture_git(repo,'checkout','-q','main')
    return repo,a,b,c

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

class EntryFE05f(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global BASE_OVERLAY
        BASE_OVERLAY=build_base_overlay()
        print('\n[test_entry_f] e3c29d1d-bytes overlay: '+str(len(BASE_OVERLAY))+' paths: '+', '.join(sorted(BASE_OVERLAY))[:2000],file=sys.stderr)
        cls.b=E.strict_json((OWN/BINDING).read_bytes(),BINDING)
        cls.tree=E.head_tree(HEAD)
        cls.ci_doc=json.loads(E.read(cls.b['ci']['path']));cls.jobs_doc=json.loads(E.read(cls.b['ci_jobs']['path']))
        cls.arts_doc=json.loads(E.read(cls.b['ci_artifacts']['path']))
        cls.tmp=Path(tempfile.mkdtemp(dir=OWN,prefix='regression-repo-'))
        cls.repo,cls.A,cls.B,cls.C=build_fixture(cls.tmp)
    @classmethod
    def tearDownClass(cls):shutil.rmtree(cls.tmp,ignore_errors=True)
    def in_fixture(self,repo=None):return mock.patch.object(E,'ROOT',repo or self.repo)
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
    def ci_spec(self,edit_ci=None,edit_jobs=None,edit_spec=None):
        ci=copy.deepcopy(self.ci_doc);jobs=copy.deepcopy(self.jobs_doc)
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
    def fixture_aidlc(self):
        names=sorted(['aidlc/many/f%03d.txt'%i for i in range(MANY)])
        return dict(count=MANY,sha256=sha('\n'.join(names).encode()))

    # ---- positive control (e3c29d1d bytes through the overlay) -----------------
    def test_00_overlay_is_needed_and_stated(self):
        if BASE_OVERLAY:
            saved=E.OVERLAY;E.OVERLAY=None
            try:
                with self.assertRaisesRegex(E.Refusal,'working copy differs from head'):E.verify(self.b)
            finally:E.OVERLAY=saved
        self.assertFalse([p for p in BASE_OVERLAY if E.in_aidlc(p)])
    def test_01_positive_control_e3c29d1d_bytes(self):
        s=self.passes(self.full())
        self.assertEqual((s['head'],s['changed_paths'],s['lineage']['chain']),(HEAD,[],[HEAD]))
        self.assertEqual(s['aidlc_changed_paths']['count'],0);self.assertFalse(s['compare']['used'])
        self.assertEqual(s['repository_state']['shallow'],False);self.assertEqual(s['repository_state']['graft_file'],False)
        self.assertEqual(s['lineage']['trees'],{HEAD:E.BASE_TREE})
        wc=s['working_copy'];self.assertEqual(wc['compared_equal'],len(self.tree)-2)
        self.assertEqual(sorted(s['ci']['runs']),sorted(self.b['ci']['runs']))
        self.assertTrue(s['performance'][U14]['passed']);self.assertFalse(s['upstream']['used'])

    # ---- F1: replace refs, grafts, shallow (review 03, Minor 1) ----------------------
    def test_10_git_never_follows_replace_refs(self):
        self.assertIn('--no-replace-objects',E.GIT_ARGS);self.assertEqual(E.git_env()['GIT_NO_REPLACE_OBJECTS'],'1')
        real_tree=fixture_git(self.repo,'--no-replace-objects','rev-parse',self.B+'^{tree}')
        fixture_git(self.repo,'replace',self.B,self.C)
        try:
            # control: plain git in the fixture follows the replace ref and reports C's tree and parents for B
            self.assertEqual(fixture_git(self.repo,'rev-parse',self.B+'^{tree}'),fixture_git(self.repo,'rev-parse',self.C+'^{tree}'))
            self.assertNotEqual(fixture_git(self.repo,'rev-parse',self.B+'^{tree}'),real_tree)
            with self.in_fixture():
                self.assertEqual(E.git_tree(self.B),real_tree);self.assertEqual(E.git_parents(self.B),[self.A])
                out=self.lineage([record(self.A,parents=[]),record(self.B,tree=real_tree,parents=[self.A])],[self.A,self.B],self.A,self.B)
                self.assertEqual(out['head_tree'],real_tree)
                # a record that says what a replace-following git reports for B is refused
                self.lineage_rejects('stored tree differs from local git: '+self.B,[record(self.A,parents=[]),record(self.B,tree=fixture_git(self.repo,'rev-parse',self.C+'^{tree}'),parents=[self.A])],[self.A,self.B],self.A,self.B)
                self.assertEqual(E.verify_changed(['docs/x.md'],self.fixture_aidlc(),self.A,self.B)['product'],['docs/x.md'])
        finally:fixture_git(self.repo,'replace','-d',self.B)
    def test_11_graft_file_is_refused(self):
        with self.in_fixture():self.assertFalse(E.verify_repository_state()['graft_file'])
        grafts=self.repo/'.git/info/grafts';grafts.parent.mkdir(exist_ok=True);grafts.write_text(self.B+' '+self.C+'\n')
        try:
            with self.in_fixture():
                with self.assertRaisesRegex(E.Refusal,'git graft file present'):E.verify_repository_state()
        finally:grafts.unlink()
    def test_12_shallow_repository_is_refused(self):
        shallow=self.tmp/'shallow'
        fixture_git(self.tmp,'clone','-q','--depth','1','--branch','main','file://'+str(self.repo),str(shallow))
        try:
            self.assertEqual(fixture_git(shallow,'rev-parse','--is-shallow-repository'),'true')
            with self.in_fixture(shallow):
                with self.assertRaisesRegex(E.Refusal,'shallow repository'):E.verify_repository_state()
                # the shallow boundary hides B's parent: exactly why it is refused before any lineage check
                self.assertEqual(E.git_parents(self.B),[])
        finally:shutil.rmtree(shallow,ignore_errors=True)
    def test_13_repository_state_runs_before_lineage_in_verify(self):
        trace={}
        with mock.patch.object(E,'verify_repository_state',side_effect=E.Refusal('shallow repository: regression')):
            with overlay():
                with self.assertRaisesRegex(E.Refusal,'shallow repository'):E.verify(self.b,trace)
        self.assertEqual(trace['stage'],'(1a) repository state (shallow, grafts)')
        self.assertFalse(E.verify_repository_state()['shallow'])

    # ---- (1) lineage by commit records ---------------------------------------------
    def test_20_lineage_positive_two_commits(self):
        out=self.lineage([record(PARENT),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        self.assertEqual(out['trees'],{PARENT:E.git_tree(PARENT),HEAD:E.BASE_TREE});self.assertFalse(out['compare_used'])
    def test_21_tree_mismatch(self):
        self.lineage_rejects('stored tree differs from local git: '+HEAD,[record(PARENT),record(HEAD,tree='3'*40)],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('stored tree differs from local git: '+PARENT,[record(PARENT,tree='3'*40),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
    def test_22_parents_differ(self):
        self.lineage_rejects('stored parents differ from local git: '+HEAD,[record(PARENT),record(HEAD,parents=['1'*40])],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('stored parents differ from local git: '+PARENT,[record(PARENT,parents=[]),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
    def test_23_chain_parent_and_order(self):
        grand=E.git_parents(PARENT)[0]
        self.lineage_rejects('stored parent differs from the chain: '+HEAD,[record(grand),record(HEAD)],[grand,HEAD],grand,HEAD)
        def other_order(*args,**kw):
            if args[:2]==('rev-list','--reverse'):return b'1111111111111111111111111111111111111111\n'
            return REAL_GIT(*args,**kw)
        with mock.patch.object(E,'git',other_order):
            self.lineage_rejects('local commit order differs',[record(PARENT),record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
    def test_24_unsigned_commit(self):
        for kw in (dict(verified=False),dict(reason='unsigned'),dict(verified='true')):
            with self.subTest(**kw):self.lineage_rejects('not Verified in the stored record: '+HEAD,[record(PARENT),record(HEAD,**kw)],[PARENT,HEAD],PARENT,HEAD)
    def test_25_commit_missing_extra_or_twice_in_records(self):
        self.lineage_rejects('do not cover exactly the chain: missing '+PARENT,[record(HEAD)],[PARENT,HEAD],PARENT,HEAD)
        self.lineage_rejects('do not cover exactly the chain: missing ; extra '+PARENT,[record(PARENT),record(HEAD)],[HEAD],HEAD,HEAD)
        self.lineage_rejects('list a commit twice',[record(HEAD),record(HEAD)],[HEAD],HEAD,HEAD)
    def test_26_records_file_pinned(self):
        s,files=records_doc([record(HEAD)])
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'commit records bytes differ'):E.verify_lineage(dict(s,sha256='0'*64),[HEAD],HEAD,HEAD)
        # commits-e3c29d1d.json is pinned twice in version f: as history (checked first) and as the commit records
        self.rejects('history file bytes differ from the pinned SHA-256: .*commits-e3c29d1d.json',self.full(),**{self.b['commit_records']['path']:E.read(self.b['commit_records']['path'])+b' '})
        with mock.patch.dict(E.HISTORY,{k:v for k,v in E.HISTORY.items() if not k.endswith('commits-e3c29d1d.json')},clear=True):
            b=self.variant(lambda b:b.update(history=dict(E.HISTORY)))
            self.rejects('commit records bytes differ',self.full(b),**{self.b['commit_records']['path']:E.read(self.b['commit_records']['path'])+b' '})
    def test_27_stored_record_of_e3c29d1d_is_the_real_one(self):
        self.assertEqual(json.loads(E.read(self.b['commit_records']['path']))['commits'],[record(HEAD)])
    def test_28_more_than_300_changed_files_pass_in_a_temporary_repository(self):
        # review 03, Minor 3: no pre-push local commit id; the fixture's commit B changes 351 files.
        local=fixture_git(self.repo,'diff-tree','-r','--no-renames','--name-only',self.A,self.B).split('\n')
        self.assertEqual(len(local),MANY+1)
        with self.in_fixture():
            out=self.lineage([record(self.A,parents=[]),record(self.B,parents=[self.A])],[self.A,self.B],self.A,self.B)
            self.assertEqual(out['head_tree'],fixture_git(self.repo,'rev-parse',self.B+'^{tree}'))
            changed=E.verify_changed(['docs/x.md'],self.fixture_aidlc(),self.A,self.B)
            self.assertEqual((changed['product'],changed['aidlc']['count']),(['docs/x.md'],MANY));self.assertFalse(changed['compare']['used'])
            self.lineage_rejects('stored parents differ from local git: '+self.A,[record(self.A,parents=[self.C]),record(self.B,parents=[self.A])],[self.A,self.B],self.A,self.B)

    # ---- (2) changed files by local git -----------------------------------------------
    def test_30_product_list_exact_more_fewer(self):
        a=dict(count=0,sha256=sha(b''))
        self.assertEqual(E.verify_changed(CHANGED_7,a,PARENT,HEAD)['product'],CHANGED_7)
        with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed(CHANGED_7[1:],a,PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed(sorted(CHANGED_7+['README.md']),a,PARENT,HEAD)
        with self.in_fixture():
            with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed([],self.fixture_aidlc(),self.A,self.B)
            with self.assertRaisesRegex(E.Refusal,'changed product files differ'):E.verify_changed(['README.md','docs/x.md'],self.fixture_aidlc(),self.A,self.B)
        self.rejects('changed product files differ',self.full(self.variant(lambda b:b['changed_files'].append('README.md'))))
    def test_31_aidlc_count_and_digest_in_a_temporary_repository(self):
        a=self.fixture_aidlc()
        with self.in_fixture():
            self.assertEqual(E.verify_changed(['docs/x.md'],a,self.A,self.B)['aidlc']['sha256'],a['sha256'])
            with self.assertRaisesRegex(E.Refusal,'aidlc/ file count differs'):E.verify_changed(['docs/x.md'],dict(a,count=MANY-1),self.A,self.B)
            with self.assertRaisesRegex(E.Refusal,'aidlc/ file count differs'):E.verify_changed(['docs/x.md'],dict(a,count=MANY+1),self.A,self.B)
            with self.assertRaisesRegex(E.Refusal,'aidlc/ file list SHA-256 differs'):E.verify_changed(['docs/x.md'],dict(a,sha256='0'*64),self.A,self.B)
        self.rejects('aidlc/ file count differs',self.full(self.variant(lambda b:b['aidlc_changed'].update(count=1))))
        self.rejects('aidlc/ file list SHA-256 differs',self.full(self.variant(lambda b:b['aidlc_changed'].update(sha256='0'*64))))
    def test_32_aidlc_shape_and_paths_in_binding(self):
        a=dict(count=0,sha256=sha(b''))
        with self.assertRaisesRegex(E.Refusal,'names a path inside aidlc/'):E.verify_changed(['aidlc/x.md'],a,PARENT,HEAD)
        for bad in (None,{},dict(a,extra=1),dict(a,count='0'),dict(a,count=True),dict(a,sha256='abc')):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(E.Refusal,'aidlc_changed differs'):E.verify_changed(CHANGED_7,bad,PARENT,HEAD)
    def test_34_compare_is_not_used(self):
        for edit in (lambda d:d['compare'].update(files=[]),lambda d:d.pop('compare')):
            s,j,files=self.ci_spec(edit_ci=edit)
            self.assertFalse(self.passes(self.full(self.variant(lambda b:b.update(ci=s))),**files)['compare']['used'])

    # ---- (3) working copy -----------------------------------------------------------
    def test_40_head_gitignore_rules_exclude_untracked_files(self):
        git={r['path']:r['pattern'] for r in self.wc(**{'docs/notes.log':b'x','crates/x.profraw':b''})['excluded_by_git_ignore']}
        self.assertTrue(git['docs/notes.log'].endswith(':*.log'));self.assertTrue(git['crates/x.profraw'].endswith(':*.profraw'))
    def test_41_other_ignore_sources_refused(self):
        with mock.patch.object(E,'git',git_answering({'crates/x/new.rs':('.git/info/exclude','1','*.rs')})):
            self.rejects('unexpected: crates/x/new.rs',self.full(),**{'crates/x/new.rs':b'x'})
    def test_42_unknown_files_and_tracked_bytes_refused(self):
        self.rejects('unexpected: new-top-level.txt',self.full(),**{'new-top-level.txt':b'x'})
        raw=self.blob('Cargo.toml');self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
        self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})
        with self.with_tree_entry('tools/aidlc-recovery/local-runtime.patch'):
            self.rejects('differing: tools/aidlc-recovery/local-runtime.patch',self.full(),**{'tools/aidlc-recovery/local-runtime.patch':b'other'})
    def test_43_only_two_tracked_files_may_differ(self):
        rows={r['path']:r for r in self.wc(**{'mise.toml':b'x\n'})['excluded_by_name']};self.assertFalse(rows['mise.toml']['bytes_equal_head'])
        self.rejects(r'differing: \.gitignore',self.full(),**{'.gitignore':self.blob('.gitignore')+b'\n'})
    def test_44_exclusion_list_must_equal_the_approved_list(self):
        self.rejects('exclusion list differs',self.full(self.variant(lambda b:b['exclusions']['top_level'].append('spikes'))))
    def test_45_git_reads_no_user_or_system_configuration(self):
        env=E.git_env();self.assertEqual((env['GIT_CONFIG_GLOBAL'],env['GIT_CONFIG_NOSYSTEM']),(os.devnull,'1'))
        with tempfile.TemporaryDirectory(dir=OWN,prefix='regression-home-') as tmp:
            (Path(tmp)/'.gitconfig').write_text('[[[ this is not git configuration\n')
            with mock.patch.dict(os.environ,{'HOME':tmp,'XDG_CONFIG_HOME':tmp,'GIT_DIR':'/nonexistent'}):
                plain=subprocess.run(['git','rev-parse','--verify',HEAD+'^{tree}'],cwd=ROOT,capture_output=True,timeout=60,
                    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')})
                self.assertNotEqual(plain.returncode,0);self.assertEqual(E.git_tree(HEAD),E.BASE_TREE)
    def test_46_git_is_read_only(self):
        for cmd in ('status','checkout','replace','update-ref'):
            with self.assertRaisesRegex(E.Refusal,'read-only set'):E.git(cmd)

    # ---- (4) CI, (5) performance ------------------------------------------------------
    def test_50_ci_required_workflows_reruns_and_limit(self):
        out,_=self.ci_passes();self.assertEqual(len(out['runs']),7)
        def drop_spec(s):s['workflows'].remove('U13 current full quality');s['runs'].pop(U13)
        self.ci_rejects('drops a required workflow',edit_spec=drop_spec)
        self.ci_rejects('not completed/success',edit_ci=lambda d:self.run_of(d,CI_RUN).update(conclusion='failure'))
        allow={'job_name':'x','job_id':1,'approval':'人の承認（回帰用）'}
        self.ci_rejects('exceed the limit of 2 per binding',edit_spec=lambda s:s['reruns'].update({U13:allow,U14:allow}))
    def test_51_performance_expired_repository_and_passed(self):
        p=copy.deepcopy(self.b['performance']);e=p['runs'][U14];raw=E.read(e['path']);buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('performance/observations.json',raw)
        zb=buf.getvalue();e['artifact'].update(zip_path=FAKE+'u11.zip')
        for edit,pattern in ((lambda n:None,None),(lambda n:n.update(expired=True),'expired'),(lambda n:n['workflow_run'].update(repository_id=1),'repository_id')):
            arts=copy.deepcopy(self.arts_doc);node=next(a for a in arts['runs'][0]['artifacts'] if a['name']=='u11-node')
            node.update(digest='sha256:'+sha(zb),size_in_bytes=len(zb));edit(node);ra=json.dumps(arts).encode()
            with overlay({FAKE+'u11.zip':zb,FAKE+'arts.json':ra}):
                spec_={'path':FAKE+'arts.json','sha256':sha(ra)}
                if pattern is None:self.assertTrue(E.verify_performance(p,spec_,self.b['ci']['runs'],HEAD)[U14]['passed'])
                else:
                    with self.assertRaisesRegex(E.Refusal,pattern):E.verify_performance(p,spec_,self.b['ci']['runs'],HEAD)

    # ---- (0) base records and history -------------------------------------------
    def test_60_base_records_and_history(self):
        self.assertEqual(len(E.HISTORY),28)  # v1-v4 12 + entry..entry-e, binding-e01..e05, test_entry..test_entry_e, commits-e3c29d1d.json 16
        for v in ('entry-e.py','binding-e05.json','test_entry_e.py','commits-e3c29d1d.json','entry-d.py'):
            self.assertEqual(E.HISTORY[E.HERE+v],sha((OWN/v).read_bytes()),v)
        for rel in E.HISTORY:self.rejects('history file bytes differ',self.full(),**{rel:E.read(rel)+b'#'})
        self.rejects('history pins differ',self.full(self.variant(lambda b:b['history'].popitem())))
    def test_61_earlier_bindings_are_refused(self):
        for old in ('binding-e03.json','binding-e04.json','binding-e05.json'):
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
        for argv,pattern in (([],'usage'),(['--entry-sha256',sha((OWN/'entry-e.py').read_bytes()),'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
                (['--entry-sha256',ENTRY_PIN,'--binding-sha256','0'*64],'matches no binding')):
            code,docs,err=self.in_process(argv);self.assertEqual(code,2);self.assertEqual(docs,{});self.assertRegex(err,'^REFUSED: .*'+pattern)
        self.assertEqual(run_dirs(),before)
    def test_71_pass_writes_result_json(self):
        code,docs,_=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN])
        self.assertEqual(code,0);r=docs['result.json'];self.assertEqual(r['entry_e3c29d1d_f'],'PASS')
        self.assertEqual((r['FR10_1'],r['U15_acceptance'],r['formal_command_adopted']),('GAP','GAP',False))
        self.assertEqual(r['decision_f'],E.DECISION_F);self.assertFalse(r['repository_state']['shallow'])
        self.assertTrue(any('replace' in s for s in r['claimed_en']))
    def test_72_refusal_writes_refusal_json(self):
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{'README.md':None})
        self.assertEqual(code,1);r=docs['refusal.json'];self.assertEqual(r['entry_e3c29d1d_f'],'REFUSED')
        self.assertEqual(r['refused_at']['stage'],'(3) working copy')
    def test_73_binding_shape(self):
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.update(extra=1))))
        self.rejects('binding schema/repository differs',self.full(self.variant(lambda b:b.update(schema='u15-entry-e3c29d1d-binding/e1'))))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(EntryFE05f)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() and not result.skipped and result.testsRun==suite.countTestCases() else 1)
