"""Regressions for entry-c.py with binding-e03.json (approved plan Step 20, version c).

Version c answers independent review 01 (NOT-READY): Major 1 (only head-tree
.gitignore rules count; git runs with an empty core.excludesFile and no GIT_*
variables), Major 2 (the binding cannot drop the 7 required workflows, an
approved job set must contain the base set, the performance workflow is fixed,
the u11-node digest comes from the stored API artifact list), Major 3 (among
tracked head files only .aidlc-version and mise.toml may differ in bytes) and
the Minor findings. test_entry.py and test_entry_b.py are kept unchanged.

Every refusal case changes exactly one input in memory (the entry's
regression-only OVERLAY, deep copies of the binding or of the entry's pinned
constants through unittest.mock, JSON/ZIP documents served from in-memory
paths, or a wrapped git answer) and asserts the message of the check that must
stop it, so each case fails if that check is removed. No real repository file
is modified; git is only read. Temporary folders (in-process run outputs, one
XDG ignore fixture) are created inside this entry folder and removed.

Local dependency (stated, not hidden): the positive control is the real
working copy of this machine. It passes only while every local path that is
not in the head tree is excluded by name or by a head-tree .gitignore rule.
Expectations about specific local paths (.agents/, .venv-u15/, ...) are
checked only when the path exists on disk.
"""
import contextlib,copy,hashlib,importlib.util,io,json,os,re,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry_e3c29d1d_c_under_test',OWN/'entry-c.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
ROOT=E.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
ENTRY='entry-c.py';BINDING='binding-e03.json'
BINDING_PIN=sha((OWN/BINDING).read_bytes());ENTRY_PIN=sha((OWN/ENTRY).read_bytes())
HEAD=E.BASE;PARENT='a54315f9493d6e9fb8d4792ffcefd12203540311'
CHANGED_7=['docs/release.md','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_policy.py','tests/release/test_publish_adapter.py']
U12='39114110570';U13='39114112207';U14='39114108809';CI_RUN='39114018191'
FAKE=E.HERE+'regression-in-memory/'
REAL_GIT=E.git

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def exists(rel):return (ROOT/rel).exists()
@contextlib.contextmanager
def overlay(files=None):
    saved=E.OVERLAY;E.OVERLAY=dict(files or {})
    try:yield
    finally:E.OVERLAY=saved

def git_answering(forced):
    """A git() wrapper: check-ignore answers for the paths in `forced` are replaced by (source, line, pattern); everything else is real git."""
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

class EntryCE03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=E.strict_json((OWN/BINDING).read_bytes(),BINDING)
        cls.tree=E.head_tree(HEAD)
        cls.ci_doc=json.loads(E.read(cls.b['ci']['path']));cls.jobs_doc=json.loads(E.read(cls.b['ci_jobs']['path']))
        cls.arts_doc=json.loads(E.read(cls.b['ci_artifacts']['path']))
    def rejects(self,pattern,fn,**files):
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):fn()
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

    # ---- positive control ---------------------------------------------------------
    def test_01_positive_control_real_working_copy(self):
        s=E.verify(self.b)
        self.assertEqual((s['head'],s['changed_paths'],s['lineage']['chain']),(HEAD,[],[HEAD]))
        wc=s['working_copy'];self.assertEqual(wc['head_tree_files_outside_aidlc'],len(self.tree))
        self.assertEqual(wc['compared_equal'],len(self.tree)-2)
        self.assertEqual(wc['accepted_gitignore_sources'],sorted(p for p in self.tree if p.endswith('.gitignore') and p.split('/')[-1]=='.gitignore'))
        self.assertEqual(wc['ignored_by_a_source_not_accepted'],{})
        name={r['path']:r for r in wc['excluded_by_name']};git={r['path']:r for r in wc['excluded_by_git_ignore']}
        self.assertFalse(set(name)&set(git));self.assertFalse(any(p in self.tree for p in git))
        self.assertFalse(any(r['in_head_tree'] for r in wc['excluded_by_name'] if r['kind']=='file' and r['path'] not in E.EXCLUSIONS['paths_bytes_may_differ']))
        for p in ('mise.toml','.aidlc-version'):self.assertEqual(name[p]['rule'],'path_bytes_may_differ:'+p);self.assertTrue(name[p]['in_head_tree'])
        for r in wc['excluded_by_git_ignore']:
            self.assertIn(r['pattern'].split(':',1)[0],wc['accepted_gitignore_sources'])
        for p,rule in (('.venv-u15/','top_level:.venv-u15'),('target/','directory_component:target'),('.jj/','top_level:.jj'),('.git/','top_level:.git'),('aidlc/','top_level:aidlc')):
            if exists(p):self.assertEqual(name[p]['rule'],rule)
        for p in ('.agents/','.claude/','.codex/','spikes/wasm-threads/pkg/'):
            if exists(p):self.assertIn(p,git)
        self.assertEqual(sorted(s['ci']['runs']),sorted(self.b['ci']['runs']));self.assertEqual(s['ci']['reruns'][0]['attempt_1_failed_job']['id'],117638480843)
        self.assertEqual(s['ci']['differences_from_base']['added_workflows'],[]);self.assertEqual(s['ci']['differences_from_base']['job_set_overrides'],{})
        self.assertTrue(s['performance'][U14]['passed']);self.assertEqual(s['performance'][U14]['digest_source'],self.b['ci_artifacts']['path'])
        self.assertFalse(s['upstream']['used'])

    # ---- (3) Major 1: the source of an ignore rule ------------------------------------
    def test_02_head_gitignore_rules_exclude_untracked_files(self):
        wc=self.wc(**{'docs/notes.log':b'x','crates/x.profraw':b'','scratch.local':b'1','.vscode/settings.json':b'{}'})
        git={r['path']:r['pattern'] for r in wc['excluded_by_git_ignore']}
        for p,pat in (('docs/notes.log','*.log'),('crates/x.profraw','*.profraw'),('scratch.local','*.local'),('.vscode/settings.json','.vscode/*')):
            self.assertTrue(git[p].startswith('.gitignore:') and git[p].endswith(':'+pat),git[p])
    def test_03_rules_from_other_sources_do_not_count(self):
        sources={'.gitignore'}
        raw=b''.join(x+b'\0' for x in (b'.git/info/exclude',b'1',b'*.rs',b'a.rs',b'/Users/x/.config/git/ignore',b'2',b'*.tmp',b'b.tmp',
            b'crates/new/.gitignore',b'1',b'*',b'crates/new/c',b'.gitignore',b'6',b'*.log',b'd.log'))
        status,foreign=E.parse_check_ignore(raw,['a.rs','b.tmp','crates/new/c','d.log'],sources)
        self.assertEqual(status,{'a.rs':None,'b.tmp':None,'crates/new/c':None,'d.log':'.gitignore:6:*.log'})
        self.assertEqual(sorted(foreign),['a.rs','b.tmp','crates/new/c'])
    def test_04_info_exclude_and_untracked_gitignore_are_refused_end_to_end(self):
        forced={'crates/x/new.rs':('.git/info/exclude','1','*.rs'),'crates/new/.gitignore':('crates/new/.gitignore','1','*'),'crates/new/a.rs':('crates/new/.gitignore','1','*')}
        with mock.patch.object(E,'git',git_answering(forced)):
            for p in forced:self.rejects('unexpected: '+re.escape(p),self.full(),**{p:b'x'})
            with overlay({'crates/x/new.rs':b'x'}):
                with self.assertRaises(E.Refusal) as caught:E.verify(self.b)
        self.assertIn('crates/x/new.rs',caught.exception.details['ignored_by_a_source_not_accepted'])
    def test_05_git_runs_without_git_variables_and_with_empty_excludes_file(self):
        self.assertIn('core.excludesFile=',E.GIT_ARGS)
        with tempfile.TemporaryDirectory(dir=OWN,prefix='regression-xdg-') as tmp:
            (Path(tmp)/'git').mkdir();(Path(tmp)/'git'/'ignore').write_text('*.rs\n')
            env={'XDG_CONFIG_HOME':tmp,'GIT_DIR':'/nonexistent','GIT_WORK_TREE':'/nonexistent','GIT_INDEX_FILE':'/nonexistent',
                'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'core.excludesFile','GIT_CONFIG_VALUE_0':str(Path(tmp)/'git'/'ignore')}
            with mock.patch.dict(os.environ,env):
                self.assertFalse(any(k.startswith('GIT_') and k not in ('GIT_OPTIONAL_LOCKS','GIT_TERMINAL_PROMPT') for k in E.git_env()))
                self.assertEqual(E.git_tree(HEAD),E.BASE_TREE)
                raw=E.git('check-ignore','-z','-v','-n','--no-index','--stdin',stdin=b'crates/x/new.rs\0',ok=(0,1))
        self.assertEqual(raw.split(b'\0')[:3],[b'',b'',b''])
    def test_06_negated_pattern_and_malformed_answers(self):
        self.rejects(r'unexpected: \.vscode/extensions\.json',self.full(),**{'.vscode/extensions.json':b'{}'})
        raw=b'.gitignore\x0019\x00.vscode/*\x00a\x00.gitignore\x0020\x00!.vscode/extensions.json\x00b\x00\x00\x00\x00c\x00'
        self.assertEqual(E.parse_check_ignore(raw,['a','b','c'],{'.gitignore'})[0],{'a':'.gitignore:19:.vscode/*','b':None,'c':None})
        with self.assertRaisesRegex(E.Refusal,'every path'):E.parse_check_ignore(raw,['a','b'],{'.gitignore'})
        with self.assertRaisesRegex(E.Refusal,'malformed'):E.parse_check_ignore(b'x\x00y\x00',['x'],{'.gitignore'})
    def test_07_unignored_unknown_files_are_refused(self):
        for p in ('crates/paludarium-types/src/extra.rs','new-top-level.txt','tools/aidlc-recoveryX/a.txt','mytarget/x','docs/target','x/.DS_Store.bak','.venv-u15x/a'):
            self.rejects('unexpected: '+re.escape(p),self.full(),**{p:b'x'})
    def test_08_without_the_git_ignore_check_ignored_files_are_refused(self):
        with mock.patch.object(E,'git_ignore_status',lambda paths,sources:({p:None for p in paths},{})):
            self.rejects(r'unexpected: .*crates/x\.profraw',self.full(),**{'crates/x.profraw':b''})

    # ---- (3) Major 3: tracked files are compared --------------------------------------
    def test_10_tracked_files_under_by_name_paths_are_compared(self):
        for p in ('tools/aidlc-recovery/local-runtime.patch','crates/a/target/x.o','spikes/node_modules/y.js','scripts/__pycache__/m.pyc','docs/.DS_Store','.venv-u15/pyvenv.cfg'):
            with self.with_tree_entry(p):
                self.rejects('differing: '+re.escape(p),self.full(),**{p:b'not the blob'})
                self.rejects('missing: '+re.escape(p),self.full(),**{p:None})
                wc=self.wc(**{p:self.blob('README.md')});self.assertEqual(wc['compared_equal'],len(self.tree)-1)
    def test_11_tracked_files_are_compared_whatever_git_ignore_says(self):
        everything=lambda paths,sources:({p:'.gitignore:1:*' for p in paths},{})
        with mock.patch.object(E,'git_ignore_status',everything):
            raw=self.blob('Cargo.toml');self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
            self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})
        asked=[]
        def record(paths,sources):asked.extend(paths);return ({p:None for p in paths},{})
        with mock.patch.object(E,'git_ignore_status',record):
            with overlay({'zz-untracked.txt':b'x'}):
                with self.assertRaises(E.Refusal):E.verify(self.b)
        self.assertIn('zz-untracked.txt',asked);self.assertFalse(set(asked)&set(self.tree))
    def test_12_only_two_tracked_files_may_differ(self):
        wc=self.wc(**{'.aidlc-version':b'anything\n','mise.toml':b'x\n'})
        rows={r['path']:r for r in wc['excluded_by_name']};self.assertFalse(rows['.aidlc-version']['bytes_equal_head']);self.assertFalse(rows['mise.toml']['bytes_equal_head'])
        for p in ('.gitignore','Cargo.toml','tests/guests/u10/.gitignore','rust-toolchain.toml'):
            raw=self.blob(p);self.rejects('differing: '+re.escape(p),self.full(),**{p:raw+b'\n'})
        self.rejects(r'missing: mise\.toml',self.full(),**{'mise.toml':None})
        self.rejects(r'missing: \.aidlc-version',self.full(),**{'.aidlc-version':None})
    def test_13_untracked_by_name_paths_pass_and_are_listed(self):
        files={'tools/aidlc-recovery/extra.txt':b'1','crates/a/target/x.o':b'1','docs/.DS_Store':b'','scripts/__pycache__/m.pyc':b'','packages/x/node_modules/y.js':b'','.venv-u15/extra.py':b''}
        wc=self.wc(**files);name={r['path']:r for r in wc['excluded_by_name']}
        for p in files:self.assertIn(p,name);self.assertFalse(name[p]['in_head_tree'])
    def test_14_exclusion_list_must_equal_the_approved_list(self):
        for edit in (lambda b:b['exclusions']['git_ignored_untracked'].update(enabled=False),lambda b:b['exclusions']['top_level'].append('spikes'),
                lambda b:b['exclusions']['paths_bytes_may_differ'].append('Cargo.toml'),lambda b:b['exclusions']['prefixes'].clear(),
                lambda b:b['exclusions'].update(decision='x'),lambda b:b['exclusions'].update(extra=[])):
            self.rejects('exclusion list differs',self.full(self.variant(edit)))
    def test_15_one_byte_and_missing_product_file(self):
        raw=self.blob('Cargo.toml');self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
        self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})

    # ---- (2) changed files ----------------------------------------------------
    def test_20_changed_list_more_at_e03(self):
        self.rejects('changed files differ between the binding and local git',self.full(self.variant(lambda b:b['changed_files'].append('README.md'))))
    def test_21_changed_list_exact_more_fewer_and_compare(self):
        chain=[PARENT,HEAD];doc=self.ci_doc
        self.assertEqual(E.verify_changed(doc,CHANGED_7,chain,PARENT,HEAD),CHANGED_7)
        with self.assertRaisesRegex(E.Refusal,'binding and local git'):E.verify_changed(doc,CHANGED_7[1:],chain,PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'binding and local git'):E.verify_changed(doc,sorted(CHANGED_7+['README.md']),chain,PARENT,HEAD)
        d=copy.deepcopy(doc);d['compare']['files']=d['compare']['files'][1:]
        with self.assertRaisesRegex(E.Refusal,'stored compare file list'):E.verify_changed(d,CHANGED_7,chain,PARENT,HEAD)
        d=copy.deepcopy(doc);d['compare']['files'][0]['sha']='0'*40
        with self.assertRaisesRegex(E.Refusal,'stored compare blob'):E.verify_changed(d,CHANGED_7,chain,PARENT,HEAD)
        d=copy.deepcopy(doc);d['compare']['ahead_by']=2
        with self.assertRaisesRegex(E.Refusal,'stored compare differs'):E.verify_changed(d,CHANGED_7,chain,PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'sorted unique'):E.verify_changed(doc,list(reversed(CHANGED_7)),chain,PARENT,HEAD)

    # ---- (1) signature and lineage -------------------------------------------
    def test_30_lineage_signature_order_and_trees(self):
        doc=self.ci_doc;self.assertEqual(E.verify_lineage(doc,[PARENT,HEAD],PARENT,HEAD)['chain'],[PARENT,HEAD])
        d=copy.deepcopy(doc);d['commits'][1]['verified']=False
        with self.assertRaisesRegex(E.Refusal,'not Verified'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][0]['reason']='unsigned'
        with self.assertRaisesRegex(E.Refusal,'not Verified'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'from the base to the head'):E.verify_lineage(doc,[HEAD,PARENT],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][1]['parents']=['1'*40]
        with self.assertRaisesRegex(E.Refusal,'stored parent differs'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][0]['tree']='3'*40
        with self.assertRaisesRegex(E.Refusal,'stored tree differs from local git: '+PARENT):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][1]['tree']='3'*40
        with self.assertRaisesRegex(E.Refusal,'stored tree differs from local git: '+HEAD):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        real_rev_list=E.git
        def other_parent(*args,**kw):
            if args[:2]==('rev-list','--parents'):return (args[-1]+' '+'7'*40+'\n').encode()
            return real_rev_list(*args,**kw)
        with mock.patch.object(E,'git',other_parent):
            with self.assertRaisesRegex(E.Refusal,'local parent differs'):E.verify_lineage(doc,[PARENT,HEAD],PARENT,HEAD)
    def test_31_e03_head_unsigned_or_chain_differs(self):
        s,j,files=self.ci_spec(edit_ci=lambda d:d['commits'][1].update(verified=False))
        self.rejects('not Verified',self.full(self.variant(lambda b:b.update(ci=s))),**files)
        self.rejects('from the base to the head',self.full(self.variant(lambda b:b.update(commit_chain=[PARENT,HEAD]))))
        self.rejects('binding base differs',self.full(self.variant(lambda b:b['base'].update(commit=PARENT))))
        self.rejects('binding head is not a commit id',self.full(self.variant(lambda b:b.update(head='e3c29d1d'))))

    # ---- (4) CI (Major 2) -------------------------------------------------------------
    def test_40_ci_positive_on_in_memory_copy(self):
        out,_=self.ci_passes();self.assertEqual(len(out['runs']),7)
    def test_41_required_workflows_cannot_be_dropped(self):
        def drop_doc(d):d['runs']=[r for r in d['runs'] if str(r['id'])!=U13];d['runs_listed_for_head']['ids'].remove(int(U13));d['runs_listed_for_head']['total_count']-=1
        def drop_jobs(d):d['runs']=[r for r in d['runs'] if str(r['id'])!=U13]
        def drop_spec(s):s['workflows'].remove('U13 current full quality');s['runs'].pop(U13)
        self.ci_rejects('drops a required workflow: U13 current full quality',edit_ci=drop_doc,edit_jobs=drop_jobs,edit_spec=drop_spec)
        self.ci_rejects('stored CI runs differ',edit_ci=lambda d:d.update(runs=[r for r in d['runs'] if str(r['id'])!=U13]))
        self.ci_rejects('cover exactly the workflow set',edit_spec=lambda s:s['workflows'].append('U99 extra'))
        self.ci_rejects('run listing',edit_ci=lambda d:d['runs_listed_for_head']['ids'].append(1))
    def test_42_ci_run_failed_or_not_completed(self):
        self.ci_rejects('not completed/success',edit_ci=lambda d:self.run_of(d,CI_RUN).update(conclusion='failure'))
        self.ci_rejects('not completed/success',edit_ci=lambda d:self.run_of(d,CI_RUN).update(status='in_progress'))
        self.ci_rejects('head/repository differs',edit_ci=lambda d:self.run_of(d,CI_RUN).update(head_sha=PARENT))
        self.ci_rejects('branch head differs',edit_ci=lambda d:d['branch'].update(head=PARENT))
    def test_43_unallowed_attempt_2(self):
        self.ci_rejects('stored CI run differs',edit_ci=lambda d:self.run_of(d,U13).update(run_attempt=2))
        self.ci_rejects('attempt differs from the allowance',edit_spec=lambda s:s['runs'][U13].update(run_attempt=2))
        self.ci_rejects('attempt differs from the allowance',edit_spec=lambda s:s['reruns'].clear())
        self.ci_rejects('not an allowed rerun',edit_jobs=lambda d:self.run_of(d,U13).update(attempt_1={'jobs':[]}))
    def test_44_rerun_checked_against_the_stored_attempt_1_jobs(self):
        out,_=self.ci_passes();self.assertEqual(out['reruns'][0]['attempt_1_other_jobs_success'],28)
        self.ci_rejects('failed job differs',edit_spec=lambda s:s['reruns'][U12].update(job_id=1))
        self.ci_rejects('failed job differs',edit_jobs=lambda d:self.run_of(d,U12)['attempt_1']['jobs'][0].__setitem__(2,'failure'))
        def two(d):
            r=self.run_of(d,U12);r['jobs'][0][3]=r['run_started_at']
        self.ci_rejects('re-ran other jobs',edit_jobs=two)
        self.ci_rejects('no approval',edit_spec=lambda s:s['reruns'][U12].update(approval=' '))
        self.ci_rejects('key set differs',edit_spec=lambda s:s['reruns'][U12].update(extra=1))
    def test_45_job_set_overrides_cannot_shrink(self):
        def drop(d):
            r=self.run_of(d,U13);r['jobs']=r['jobs'][1:];r['total_count']=len(r['jobs'])
        self.ci_rejects('job set differs from the expected set',edit_jobs=drop)
        base=sorted(j[0] for j in self.run_of(self.jobs_doc,U13)['jobs'])
        self.ci_rejects('drops base jobs',edit_jobs=drop,edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':base[1:],'approval':'人の承認（回帰用）'}}))
        self.ci_rejects('override is empty',edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':[],'approval':'人の承認（回帰用）'}}))
        def add(d):
            r=self.run_of(d,U13);r['jobs'].append(['new job',1,'success','2026-10-18T09:20:00Z']);r['total_count']=len(r['jobs'])
        self.ci_rejects('job set differs from the expected set',edit_jobs=add)
        out,_=self.ci_passes(edit_jobs=add,edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':base+['new job'],'approval':'人の承認（回帰用）'}}))
        self.assertEqual(out['differences_from_base']['job_set_overrides']['U13 current full quality']['added_jobs'],['new job'])
        self.ci_rejects('lacks an approval',edit_jobs=add,edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':base+['new job'],'approval':''}}))
        self.ci_rejects('job failed or job count',edit_jobs=lambda d:self.run_of(d,U13).update(jobs=[],total_count=0))
        self.ci_rejects('job failed or job count',edit_jobs=lambda d:self.run_of(d,U13)['jobs'][0].__setitem__(2,'failure'))
    def test_46_ci_record_bytes_pinned(self):
        self.ci_rejects('CI record bytes differ',edit_spec=lambda s:s.update(sha256='0'*64))

    # ---- (5) performance (Major 2) ---------------------------------------------
    def perf_variant(self,edit_obs=None,edit_entry=None,edit_arts=None,zip_member=None,zip_digest_matches=True):
        p=copy.deepcopy(self.b['performance']);e=p['runs'][U14];orig=json.loads(E.read(e['path']))
        if edit_obs:edit_obs(orig)
        raw=json.dumps(orig).encode();buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('performance/observations.json',raw if zip_member is None else zip_member)
        z=buf.getvalue();e.update(path=FAKE+'obs.json',sha256=sha(raw));e['artifact'].update(zip_path=FAKE+'u11.zip')
        arts=copy.deepcopy(self.arts_doc);node=next(a for a in arts['runs'][0]['artifacts'] if a['name']=='u11-node')
        if zip_digest_matches:node.update(digest='sha256:'+sha(z),size_in_bytes=len(z))
        if edit_arts:edit_arts(arts)
        if edit_entry:edit_entry(e)
        ra=json.dumps(arts).encode()
        return p,{'path':FAKE+'arts.json','sha256':sha(ra)},{FAKE+'obs.json':raw,FAKE+'u11.zip':z,FAKE+'arts.json':ra}
    def perf_rejects(self,pattern,**kw):
        p,a,files=self.perf_variant(**kw)
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):E.verify_performance(p,a,self.b['ci']['runs'],HEAD)
    def test_50_performance_passed_false(self):
        p,a,files=self.perf_variant()
        with overlay(files):self.assertTrue(E.verify_performance(p,a,self.b['ci']['runs'],HEAD)[U14]['passed'])
        self.perf_rejects('passed is not true',edit_obs=lambda o:o.update(passed=False))
        self.perf_rejects('passed is not true',edit_obs=lambda o:o['result'].update(**{'pass':False}))
        self.perf_rejects('passed is not true',edit_obs=lambda o:o.update(complete=False))
        self.perf_rejects('original head differs',edit_obs=lambda o:o.update(head=PARENT))
    def test_51_digest_comes_from_the_stored_artifact_list(self):
        self.perf_rejects('stored API digest',zip_digest_matches=False)
        node=lambda d:next(x for x in d['runs'][0]['artifacts'] if x['name']=='u11-node')
        self.perf_rejects('stored API digest',edit_arts=lambda d:node(d).update(size_in_bytes=1))
        self.perf_rejects('artifact id differs',edit_entry=lambda e:e['artifact'].update(id=1))
        self.perf_rejects('does not belong to the run',edit_arts=lambda d:node(d)['workflow_run'].update(id=1))
        self.perf_rejects('does not belong to the run',edit_arts=lambda d:node(d)['workflow_run'].update(head_sha=PARENT))
        self.perf_rejects('not exactly one u11-node',edit_arts=lambda d:(d['runs'][0]['artifacts'].append(dict(node(d))),d['runs'][0].update(total_count=33)))
        self.perf_rejects('artifact list missing',edit_arts=lambda d:d['runs'][0].update(id=1))
        self.perf_rejects('artifacts record repository/head',edit_arts=lambda d:d.update(head=PARENT))
        self.perf_rejects('differs from the ZIP member',zip_member=b'{}')
        self.perf_rejects('performance entry differs',edit_entry=lambda e:e['artifact'].update(digest='sha256:'+'0'*64))
        p,a,files=self.perf_variant();a['sha256']='0'*64
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'CI artifacts record bytes'):E.verify_performance(p,a,self.b['ci']['runs'],HEAD)
    def test_52_performance_workflow_is_fixed(self):
        p,a,files=self.perf_variant();p['workflows']=['U12 current full quality']
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'performance workflow is not'):E.verify_performance(p,a,self.b['ci']['runs'],HEAD)
        p,a,files=self.perf_variant();p['runs']={}
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'performance runs differ'):E.verify_performance(p,a,self.b['ci']['runs'],HEAD)

    # ---- (0) base records and history ---------------------------------------
    def test_60_base_record_bytes_changed(self):
        c=E.BASE_RECORDS['checkpoint']
        for rel,pattern in ((c['copy'],'base checkpoint record bytes'),(c['result'],'base result.json bytes'),*[(p,'base record bytes') for p in E.BASE_RECORDS['files']]):
            raw=E.read(rel);self.rejects(pattern,self.full(),**{rel:raw+b' '})
        self.rejects('binding base records differ',self.full(self.variant(lambda b:b['base_records']['checkpoint'].update(id='x'))))
    def base_record_rejects(self,pattern,edit=None,edit_result=None):
        c=E.BASE_RECORDS['checkpoint'];rec=json.loads(E.read(c['copy']));res=json.loads(E.read(c['result']))
        if edit:edit(rec)
        if edit_result:edit_result(res)
        raw=json.dumps(rec).encode();rr=json.dumps(res).encode()
        with mock.patch.dict(c,copy_sha256=sha(raw),result_sha256=sha(rr),command_sha256=rec['command_sha256']):
            self.rejects(pattern,E.verify_base_records,**{c['copy']:raw,c['result']:rr,c['live']:None})
    def test_61_base_record_contents_are_checked(self):
        self.base_record_rejects('did not pass',lambda r:r.update(exit_code=1))
        self.base_record_rejects('did not pass',lambda r:r.update(verified=False))
        self.base_record_rejects('did not pass',lambda r:r.update(evidence_unchanged=False))
        self.base_record_rejects('record id differs',lambda r:r.update(unit='u14-jit-wasm'))
        self.base_record_rejects('command SHA-256 differs',lambda r:r.update(command_label=r['command_label']+' '))
        def other_entry(r):
            r['command_label']=r['command_label'].replace(E.BASE_RECORDS['checkpoint']['binding_sha256'],'0'*64);r['command_sha256']=sha(r['command_label'].encode())
        self.base_record_rejects('not entry v4 with binding-11',other_entry)
        self.base_record_rejects('whole recorded stdout',lambda r:r.update(stdout_tail=r['stdout_tail']+'x'))
        def other_output(r):
            r['stdout_tail']=r['stdout_tail'].replace('run-1792320136065939000-60394','run-0-0');b=r['stdout_tail'].encode();r.update(stdout_sha256=sha(b),stdout_bytes=len(b))
        self.base_record_rejects('output folder differs',other_output)
        self.base_record_rejects('not the v4 pass',edit_result=lambda r:r.update(u15_candidate_v4='REFUSED'))
        self.base_record_rejects('not the v4 pass',edit_result=lambda r:r.update(binding_sha256='0'*64))
    def test_62_live_checkpoint_record(self):
        c=E.BASE_RECORDS['checkpoint'];live=json.loads(E.read(c['live']))
        self.rejects('base id but different bytes',E.verify_base_records,**{c['live']:E.read(c['live'])+b'\n'})
        for bad in ('absent',None,'',' ',5):
            l=dict(live)
            if bad=='absent':l.pop('id')
            else:l['id']=bad
            self.rejects('has no id',E.verify_base_records,**{c['live']:json.dumps(l).encode()})
        live['id']='later-id'
        with overlay({c['live']:json.dumps(live).encode()}):self.assertIn('superseded',E.verify_base_records()['live_checkpoint_record'])
        with overlay({c['live']:None}):self.assertIn('missing',E.verify_base_records()['live_checkpoint_record'])
    def test_63_history_files_changed(self):
        for rel in E.HISTORY:self.rejects('history file bytes differ',self.full(),**{rel:E.read(rel)+b'#'})
        self.rejects('history pins differ',self.full(self.variant(lambda b:b['history'].popitem())))
    def test_64_earlier_versions_stay_and_are_not_selected(self):
        for p in ('entry.py','binding-e01.json','test_entry.py','entry-b.py','binding-e02.json','test_entry_b.py','independent-review-01.md',
                'run-1792325657506892000-42086/refusal.json','run-1792326450015585000-34598/result.json'):self.assertTrue((OWN/p).is_file(),p)
        for old in ('binding-e01.json','binding-e02.json'):
            code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',sha((OWN/old).read_bytes())])
            self.assertEqual(code,1);self.assertRegex(docs['refusal.json']['error'],'binding key set differs|binding schema/repository differs')

    # ---- binding / entry SHA-256 and the command line --------------------------
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
        for argv,pattern in (([],'usage'),(['--entry-sha256',ENTRY_PIN],'usage'),(['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN],'usage'),
                (['--entry-sha256','0'*64,'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
                (['--entry-sha256',sha((OWN/'entry-b.py').read_bytes()),'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
                (['--entry-sha256',ENTRY_PIN,'--binding-sha256','0'*64],'matches no binding'),
                (['--entry-sha256',ENTRY_PIN.upper(),'--binding-sha256',BINDING_PIN],'64 lowercase hex')):
            code,docs,err=self.in_process(argv);self.assertEqual(code,2);self.assertEqual(docs,{});self.assertRegex(err,'^REFUSED: .*'+pattern)
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{E.HERE+ENTRY:(OWN/ENTRY).read_bytes()+b'\n'})
        self.assertEqual(code,2);self.assertEqual(docs,{})
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{E.HERE+BINDING:(OWN/BINDING).read_bytes()+b'\n'})
        self.assertEqual(code,2);self.assertRegex(err,'matches no binding')
        r=subprocess.run([sys.executable,'-B',str(E.SELF),'--entry-sha256','0'*64,'--binding-sha256',BINDING_PIN],capture_output=True,timeout=120)
        self.assertEqual(r.returncode,2);self.assertRegex(r.stderr.decode(),'^REFUSED: ');self.assertEqual(run_dirs(),before)
    def test_71_pass_writes_result_json_in_both_languages(self):
        code,docs,_=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN])
        self.assertEqual(code,0);self.assertEqual(sorted(docs),['result.json']);r=docs['result.json']
        self.assertEqual(r['entry_e3c29d1d_c'],'PASS');self.assertEqual(list(r)[:2],['entry_e3c29d1d_c','differences_from_base'])
        self.assertEqual(r['changed_paths'],[]);self.assertEqual((r['FR10_1'],r['U15_acceptance'],r['formal_command_adopted']),('GAP','GAP',False))
        for k in ('claimed','claimed_en','not_claimed','not_claimed_en'):self.assertTrue(r[k])
        self.assertTrue(any('変わったファイルの中身' in s for s in r['not_claimed']) and any('content of changed files' in s for s in r['not_claimed_en']))
        self.assertTrue(any('実公開' in s for s in r['not_claimed']) and any('Real publication' in s for s in r['not_claimed_en']))
        self.assertTrue(any('API' in s and 'artifact' in s for s in r['claimed_en']));self.assertFalse(any('binding' in s and 'digest' in s for s in r['claimed_en']))
        self.assertIn('.aidlc-version',{x['path'] for x in r['excluded_by_name']})
        self.assertEqual((r['exclusion_decision'],r['review_response']),(E.DECISION_B,E.REVIEW_C))
    def test_72_refusal_writes_refusal_json(self):
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{'README.md':None})
        self.assertEqual(code,1);self.assertEqual(sorted(docs),['refusal.json']);r=docs['refusal.json']
        self.assertEqual(r['refused_at']['stage'],'(3) working copy');self.assertEqual(r['details']['missing'],['README.md']);self.assertFalse(r['exclusions_widened'])
    def test_73_binding_shape(self):
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.update(extra=1))))
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.pop('ci_artifacts'))))
        self.rejects('purpose/approval missing',self.full(self.variant(lambda b:b.update(approval=''))))
        self.rejects('duplicate key',lambda:E.strict_json(b'{"a":1,"a":2}','x'))

    # ---- (6) upstream tree_equal ----------------------------------------------
    def upstream(self,edit_ci=None,tree=None,U='4'*40):
        def repo(ci,jobs):
            ci['repository']=jobs['repository']=E.UPSTREAM_REPOSITORY;ci['branch']={'name':'main','head':U};jobs['head']=U
            ci['commits'].append(dict(sha=U,parents=['5'*40],tree=tree or E.BASE_TREE,verified=True,reason='valid'))
            for r in ci['runs']:r.update(head_sha=U,repository=E.UPSTREAM_REPOSITORY,head_repository=E.UPSTREAM_REPOSITORY)
        s,j,files=self.ci_spec(repo_doc=repo,edit_ci=edit_ci,edit_spec=lambda s:s.update(branch='main'))
        return {'repository':E.UPSTREAM_REPOSITORY,'head':U,'tree_equal':True,'ci':s,'ci_jobs':j},files
    def test_80_tree_equal_match_and_mismatch(self):
        u,files=self.upstream()
        with overlay(files):out=E.verify_upstream(u,HEAD)
        self.assertTrue(out['used']);self.assertFalse(out['tree_checked_in_local_git'])
        u,files=self.upstream(tree='6'*40)
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'upstream head tree differs'):E.verify_upstream(u,HEAD)
        u,files=self.upstream(edit_ci=lambda d:d['commits'][-1].update(verified=False))
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'upstream head not Verified'):E.verify_upstream(u,HEAD)
        u,files=self.upstream(edit_ci=lambda d:self.run_of(d,CI_RUN).update(conclusion='failure'))
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'not completed/success'):E.verify_upstream(u,HEAD)
        u,files=self.upstream();u['tree_equal']=False
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'upstream binding differs'):E.verify_upstream(u,HEAD)
        u,files=self.upstream();b=self.variant(lambda b:b.update(upstream=u))
        with overlay(files):self.assertTrue(E.verify(b)['upstream']['used'])
    def test_81_upstream_in_local_git_and_repository(self):
        u,files=self.upstream(U=PARENT)
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'local upstream head tree differs'):E.verify_upstream(u,HEAD)
        u,files=self.upstream(U=HEAD)
        with overlay(files):self.assertTrue(E.verify_upstream(u,HEAD)['tree_checked_in_local_git'])
        u,files=self.upstream();u['repository']='someone/else'
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'upstream binding differs'):E.verify_upstream(u,HEAD)
        u,files=self.upstream(edit_ci=lambda d:self.run_of(d,CI_RUN).update(repository=E.REPOSITORY))
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,'head/repository differs'):E.verify_upstream(u,HEAD)

    # ---- git stays read-only -------------------------------------------------
    def test_90_git_is_read_only(self):
        for cmd in ('status','checkout','update-ref','gc','fetch'):
            with self.assertRaisesRegex(E.Refusal,'read-only set'):E.git(cmd)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(EntryCE03)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() and not result.skipped and result.testsRun==suite.countTestCases() else 1)
