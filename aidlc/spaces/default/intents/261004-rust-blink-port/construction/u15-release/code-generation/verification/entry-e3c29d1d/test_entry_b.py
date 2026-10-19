"""Regressions for entry-b.py with binding-e02.json (approved plan Step 20, version b).

Version b follows the person's decision of 2026-10-18 (option "git の無視＋2 つ"):
paths not in the head tree are excluded when git ignores them (read-only
`git check-ignore --no-index`), and `.aidlc-version` (bytes may differ) and
`.venv-u15/` are excluded by name. Tracked head files are always compared.
test_entry.py (for entry.py, binding-e01) is kept unchanged.

Every refusal case changes exactly one input in memory (the entry's
regression-only OVERLAY, deep copies of the binding, or JSON/ZIP documents
served from in-memory paths) and asserts the message of the check that must
stop it, so each case fails if that check is removed. No real repository file
is modified; git is only read. Output folders of in-process runs go to a
temporary folder inside this entry folder that is removed afterwards; the only
child processes are refused command lines, which write nothing.

The positive control is the real working copy, with nothing hidden.
"""
import contextlib,copy,hashlib,importlib.util,io,json,re,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry_e3c29d1d_b_under_test',OWN/'entry-b.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
ROOT=E.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
ENTRY='entry-b.py';BINDING='binding-e02.json'
BINDING_PIN=sha((OWN/BINDING).read_bytes());ENTRY_PIN=sha((OWN/ENTRY).read_bytes())
HEAD=E.BASE;PARENT='a54315f9493d6e9fb8d4792ffcefd12203540311'
CHANGED_7=['docs/release.md','scripts/release/check.py','scripts/release/policy.py','tests/release/test_api.py','tests/release/test_check.py',
    'tests/release/test_policy.py','tests/release/test_publish_adapter.py']
U12='39114110570';U13='39114112207';U14='39114108809';CI_RUN='39114018191'
FAKE=E.HERE+'regression-in-memory/'

def run_dirs():return {p.name for p in OWN.glob('run-*')}
@contextlib.contextmanager
def overlay(files=None):
    saved=E.OVERLAY;E.OVERLAY=dict(files or {})
    try:yield
    finally:E.OVERLAY=saved

class EntryBE02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=E.strict_json((OWN/BINDING).read_bytes(),BINDING)
        cls.tree=E.head_tree(HEAD)
        cls.ci_doc=json.loads(E.read(cls.b['ci']['path']));cls.jobs_doc=json.loads(E.read(cls.b['ci_jobs']['path']))
    def hidden(self,**files):return overlay(files)
    def rejects(self,pattern,fn,**files):
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):fn()
    def variant(self,edit):b=copy.deepcopy(self.b);edit(b);return b
    def full(self,b=None):return lambda:E.verify(b or self.b)
    def blob(self,p):return E.blobs([self.tree[p][1]])[self.tree[p][1]]
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
    def wc(self,**files):
        with overlay(files):return E.verify(self.b)['working_copy']

    # ---- positive control: the real working copy ------------------------------
    def test_01_positive_control_real_working_copy(self):
        s=E.verify(self.b)
        self.assertEqual(s['head'],HEAD);self.assertEqual(s['changed_paths'],[]);self.assertEqual(s['lineage']['chain'],[HEAD])
        wc=s['working_copy'];self.assertEqual(wc['head_tree_files_outside_aidlc'],675);self.assertEqual(wc['compared_equal'],673)
        name={r['path']:r for r in wc['excluded_by_name']};git={r['path']:r for r in wc['excluded_by_git_ignore']}
        self.assertFalse(set(name)&set(git))
        for p in ('mise.toml','.aidlc-version'):self.assertEqual(name[p]['rule'],'path_bytes_may_differ:'+p);self.assertTrue(name[p]['in_head_tree'])
        self.assertEqual(name['.venv-u15/']['rule'],'top_level:.venv-u15')
        for p in ('tools/aidlc-recovery/local-runtime.patch','tools/aidlc-recovery/recovery.test.ts'):self.assertEqual(name[p]['rule'],'prefix:tools/aidlc-recovery/')
        for p,rule in (('target/','directory_component:target'),('.jj/','top_level:.jj'),('.git/','top_level:.git'),('aidlc/','top_level:aidlc')):self.assertEqual(name[p]['rule'],rule)
        for p,pat in (('.agents/','/.agents/'),('.claude/','/.claude/'),('.codex/','/.codex/'),('aidlc.settings.local.json','aidlc.settings.local.json'),
                ('packages/paludarium-wasm/paludarium.wasm','/packages/paludarium-wasm/paludarium.wasm'),('spikes/wasm-threads/pkg/','/spikes/wasm-threads/pkg/')):
            self.assertTrue(git[p]['pattern'].endswith(':'+pat),p)
        self.assertTrue(all(r['path'] in self.tree or r['path'].endswith('/') or r['path'] not in self.tree for r in wc['excluded_by_git_ignore']))
        self.assertFalse(any(r['path'] in self.tree for r in wc['excluded_by_git_ignore']))
        self.assertEqual(sorted(s['ci']['runs']),sorted(self.b['ci']['runs']));self.assertEqual(s['ci']['reruns'][0]['attempt_1_failed_job']['id'],117638480843)
        self.assertTrue(s['performance'][U14]['passed']);self.assertFalse(s['upstream']['used'])

    # ---- (3) working copy: git ignore ------------------------------------------
    def test_02_git_ignored_untracked_files_pass(self):
        wc=self.wc(**{'docs/notes.log':b'x','crates/x.profraw':b'','scratch.local':b'1','.vscode/settings.json':b'{}'})
        git={r['path']:r['pattern'] for r in wc['excluded_by_git_ignore']}
        self.assertTrue(git['docs/notes.log'].endswith(':*.log'));self.assertTrue(git['crates/x.profraw'].endswith(':*.profraw'))
        self.assertTrue(git['scratch.local'].endswith(':*.local'));self.assertTrue(git['.vscode/settings.json'].endswith(':.vscode/*'))
    def test_03_unignored_unknown_files_are_refused(self):
        for p in ('crates/paludarium-types/src/extra.rs','new-top-level.txt','tools/aidlc-recoveryX/a.txt','mytarget/x','docs/target','x/.DS_Store.bak','.venv-u15x/a'):
            self.rejects('unexpected: '+re.escape(p),self.full(),**{p:b'x'})
    def test_04_negated_ignore_pattern_is_not_ignored(self):
        self.rejects(r'unexpected: \.vscode/extensions\.json',self.full(),**{'.vscode/extensions.json':b'{}'})
        raw=b'.gitignore\x0019\x00.vscode/*\x00a\x00.gitignore\x0020\x00!.vscode/extensions.json\x00b\x00\x00\x00\x00c\x00'
        self.assertEqual(E.parse_check_ignore(raw,['a','b','c']),{'a':'.gitignore:19:.vscode/*','b':None,'c':None})
        with self.assertRaisesRegex(E.Refusal,'every path'):E.parse_check_ignore(raw,['a','b'])
        with self.assertRaisesRegex(E.Refusal,'malformed'):E.parse_check_ignore(b'x\x00y\x00',['x'])
    def test_05_tracked_files_are_compared_even_if_ignore_rules_match(self):
        everything=lambda paths:{p:'regression:1:*' for p in paths}
        with mock.patch.object(E,'git_ignore_status',everything):
            raw=self.blob('Cargo.toml')
            self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
            self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})
            wc=self.wc();self.assertEqual(wc['compared_equal'],673)
        asked=[]
        def record(paths):asked.extend(paths);return {p:None for p in paths}
        with mock.patch.object(E,'git_ignore_status',record):
            with overlay():
                with self.assertRaises(E.Refusal):E.verify(self.b)
        self.assertTrue(asked);self.assertFalse(set(asked)&set(self.tree))
    def test_06_aidlc_version_may_differ_but_other_tracked_files_may_not(self):
        wc=self.wc(**{'.aidlc-version':b'anything\n'})
        row=next(r for r in wc['excluded_by_name'] if r['path']=='.aidlc-version');self.assertFalse(row['bytes_equal_head'])
        for p in ('.gitignore','Cargo.toml','tests/guests/u10/.gitignore','rust-toolchain.toml'):
            raw=self.blob(p);self.rejects('differing: '+re.escape(p),self.full(),**{p:raw+b'\n'})
    def test_07_venv_excluded_by_name(self):
        wc=self.wc(**{'.venv-u15/extra.py':b'x'})
        self.assertIn('.venv-u15/extra.py',{r['path'] for r in wc['excluded_by_name']})
        self.assertFalse(any(r['path'].startswith('.venv-u15') for r in wc['excluded_by_git_ignore']))
    def test_08_git_ignore_disabled_or_list_changed_is_refused(self):
        for edit in (lambda b:b['exclusions']['git_ignored_untracked'].update(enabled=False),lambda b:b['exclusions']['top_level'].append('spikes'),
                lambda b:b['exclusions']['paths_bytes_may_differ'].append('Cargo.toml'),lambda b:b['exclusions']['prefixes'].clear(),
                lambda b:b['exclusions'].update(decision='x'),lambda b:b['exclusions'].update(extra=[])):
            self.rejects('exclusion list differs',self.full(self.variant(edit)))
    def test_09_without_git_ignore_the_ignored_paths_would_be_refused(self):
        with mock.patch.object(E,'git_ignore_status',lambda paths:{p:None for p in paths}):
            with overlay():
                with self.assertRaisesRegex(E.Refusal,r'unexpected: \.agents/'):E.verify(self.b)

    # ---- (3) working copy: by name and tracked ------------------------------------
    def test_10_one_byte_difference_in_a_product_file(self):
        raw=self.blob('Cargo.toml');self.rejects(r'differing: Cargo\.toml',self.full(),**{'Cargo.toml':raw[:-1]+bytes([raw[-1]^1])})
    def test_11_missing_product_file(self):self.rejects(r'missing: README\.md',self.full(),**{'README.md':None})
    def test_12_excluded_by_name_pass_and_are_listed(self):
        files={'mise.toml':b'changed\n','tools/aidlc-recovery/extra.txt':b'1','crates/a/target/x.o':b'1','docs/.DS_Store':b'','scripts/__pycache__/m.pyc':b'','packages/x/node_modules/y.js':b''}
        wc=self.wc(**files);name={r['path']:r for r in wc['excluded_by_name']}
        for p in files:self.assertIn(p,name)
        self.assertFalse(name['mise.toml']['bytes_equal_head'])
    def test_13_missing_excluded_tree_file_is_still_refused(self):
        self.rejects(r'missing: mise\.toml',self.full(),**{'mise.toml':None})
        self.rejects(r'missing: \.aidlc-version',self.full(),**{'.aidlc-version':None})

    # ---- (2) changed files ----------------------------------------------------
    def test_20_changed_list_more_at_e02(self):
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
    def test_30_lineage_signature_and_order(self):
        doc=self.ci_doc;self.assertEqual(E.verify_lineage(doc,[PARENT,HEAD],PARENT,HEAD)['chain'],[PARENT,HEAD])
        d=copy.deepcopy(doc);d['commits'][1]['verified']=False
        with self.assertRaisesRegex(E.Refusal,'not Verified'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][0]['reason']='unsigned'
        with self.assertRaisesRegex(E.Refusal,'not Verified'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        with self.assertRaisesRegex(E.Refusal,'from the base to the head'):E.verify_lineage(doc,[HEAD,PARENT],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][1]['parents']=['1'*40]
        with self.assertRaisesRegex(E.Refusal,'stored parent differs'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'].append(dict(sha='2'*40,parents=[PARENT],tree='x',verified=True,reason='valid'));d['commits'][1]['parents']=['2'*40]
        with self.assertRaisesRegex(E.Refusal,'local parent differs|git rev-list'):E.verify_lineage(d,[PARENT,'2'*40,HEAD],PARENT,HEAD)
        d=copy.deepcopy(doc);d['commits'][1]['tree']='3'*40
        with self.assertRaisesRegex(E.Refusal,'stored head tree'):E.verify_lineage(d,[PARENT,HEAD],PARENT,HEAD)
    def test_31_e02_head_unsigned_or_chain_differs(self):
        s,j,files=self.ci_spec(edit_ci=lambda d:d['commits'][1].update(verified=False))
        self.rejects('not Verified',self.full(self.variant(lambda b:b.update(ci=s))),**files)
        self.rejects('from the base to the head',self.full(self.variant(lambda b:b.update(commit_chain=[PARENT,HEAD]))))
        self.rejects('binding base differs',self.full(self.variant(lambda b:b['base'].update(commit=PARENT))))
        self.rejects('binding head is not a commit id',self.full(self.variant(lambda b:b.update(head='e3c29d1d'))))

    # ---- (4) CI -----------------------------------------------------------------
    def test_40_ci_positive_on_in_memory_copy(self):
        out,_=self.ci_passes();self.assertEqual(len(out['runs']),7)
    def test_41_ci_run_missing(self):
        def drop(d):d['runs']=[r for r in d['runs'] if str(r['id'])!=U13]
        self.ci_rejects('stored CI runs differ',edit_ci=drop)
        self.ci_rejects('cover exactly the workflow set',edit_spec=lambda s:s['runs'].pop(U13))
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
    def test_44_rerun_must_be_exactly_the_named_job(self):
        self.ci_rejects('failed job differs',edit_spec=lambda s:s['reruns'][U12].update(job_id=1))
        self.ci_rejects('failed job differs',edit_jobs=lambda d:self.run_of(d,U12)['attempt_1']['jobs'][0].__setitem__(2,'failure'))
        def two(d):
            r=self.run_of(d,U12);r['jobs'][0][3]=r['run_started_at']
        self.ci_rejects('re-ran other jobs',edit_jobs=two)
        self.ci_rejects('no approval',edit_spec=lambda s:s['reruns'][U12].update(approval=' '))
        self.ci_rejects('key set differs',edit_spec=lambda s:s['reruns'][U12].update(extra=1))
    def test_45_job_set_differs(self):
        def drop(d):
            r=self.run_of(d,U13);r['jobs']=r['jobs'][1:];r['total_count']=len(r['jobs'])
        self.ci_rejects('job set differs from the expected set',edit_jobs=drop)
        self.ci_rejects('job failed or job count',edit_jobs=lambda d:self.run_of(d,U13)['jobs'][0].__setitem__(2,'failure'))
        self.ci_rejects('job failed or job count',edit_jobs=lambda d:self.run_of(d,U13).update(total_count=1))
        def rename(d):self.run_of(d,U13)['jobs'][0][0]='renamed job'
        self.ci_rejects('job set differs from the expected set',edit_jobs=rename)
        names=sorted(['renamed job',*[j[0] for j in self.run_of(self.jobs_doc,U13)['jobs'][1:]]])
        self.ci_passes(edit_jobs=rename,edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':names,'approval':'人の承認（回帰用）'}}))
        self.ci_rejects('lacks an approval',edit_jobs=rename,edit_spec=lambda s:s['job_sets'].update({'U13 current full quality':{'jobs':names,'approval':''}}))
    def test_46_ci_record_bytes_pinned(self):
        self.ci_rejects('CI record bytes differ',edit_spec=lambda s:s.update(sha256='0'*64))

    # ---- (5) performance -------------------------------------------------------
    def perf_variant(self,edit_obs=None,edit_entry=None,zip_member=None):
        p=copy.deepcopy(self.b['performance']);e=p['runs'][U14];orig=json.loads(E.read(e['path']))
        if edit_obs:edit_obs(orig)
        raw=json.dumps(orig).encode();buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('performance/observations.json',raw if zip_member is None else zip_member)
        z=buf.getvalue();e.update(path=FAKE+'obs.json',sha256=sha(raw));e['artifact'].update(zip_path=FAKE+'u11.zip',digest='sha256:'+sha(z),size_in_bytes=len(z))
        if edit_entry:edit_entry(e)
        return p,{FAKE+'obs.json':raw,FAKE+'u11.zip':z}
    def perf_rejects(self,pattern,**kw):
        p,files=self.perf_variant(**kw);runs=self.b['ci']['runs']
        with overlay(files):
            with self.assertRaisesRegex(E.Refusal,pattern):E.verify_performance(p,runs,HEAD)
    def test_50_performance_passed_false(self):
        p,files=self.perf_variant()
        with overlay(files):self.assertTrue(E.verify_performance(p,self.b['ci']['runs'],HEAD)[U14]['passed'])
        self.perf_rejects('passed is not true',edit_obs=lambda o:o.update(passed=False))
        self.perf_rejects('passed is not true',edit_obs=lambda o:o['result'].update(**{'pass':False}))
        self.perf_rejects('passed is not true',edit_obs=lambda o:o.update(complete=False))
        self.perf_rejects('original head differs',edit_obs=lambda o:o.update(head=PARENT))
    def test_51_zip_digest_and_member(self):
        self.perf_rejects('ZIP differs from the API digest',edit_entry=lambda e:e['artifact'].update(digest='sha256:'+'0'*64))
        self.perf_rejects('ZIP differs from the API digest',edit_entry=lambda e:e['artifact'].update(size_in_bytes=1))
        self.perf_rejects('differs from the ZIP member',zip_member=b'{}')
        self.perf_rejects('not u11-node',edit_entry=lambda e:e['artifact'].update(name='u12-node'))
        p=copy.deepcopy(self.b['performance']);p['runs']={}
        with self.assertRaisesRegex(E.Refusal,'performance runs differ'):E.verify_performance(p,self.b['ci']['runs'],HEAD)

    # ---- (0) base records and history ---------------------------------------
    def test_60_base_records_changed(self):
        c=E.BASE_RECORDS['checkpoint']
        for rel,pattern in ((c['copy'],'base checkpoint record bytes'),(c['result'],'base result.json bytes'),*[(p,'base record bytes') for p in E.BASE_RECORDS['files']]):
            raw=E.read(rel);self.rejects(pattern,self.full(),**{rel:raw+b' '})
        self.rejects('binding base records differ',self.full(self.variant(lambda b:b['base_records']['checkpoint'].update(id='x'))))
    def test_61_live_checkpoint_record(self):
        c=E.BASE_RECORDS['checkpoint'];live=json.loads(E.read(c['live']))
        self.rejects('base id but different bytes',E.verify_base_records,**{c['live']:E.read(c['live'])+b'\n'})
        live['id']='later-id'
        with overlay({c['live']:json.dumps(live).encode()}):self.assertIn('superseded',E.verify_base_records()['live_checkpoint_record'])
    def test_62_history_files_changed(self):
        for rel in E.HISTORY:self.rejects('history file bytes differ',self.full(),**{rel:E.read(rel)+b'#'})
        self.rejects('history pins differ',self.full(self.variant(lambda b:b['history'].popitem())))
    def test_63_v1_entry_and_binding_e01_stay_and_are_not_selected(self):
        self.assertTrue((OWN/'entry.py').is_file() and (OWN/'binding-e01.json').is_file() and (OWN/'run-1792325657506892000-42086'/'refusal.json').is_file())
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',sha((OWN/'binding-e01.json').read_bytes())])
        self.assertEqual(code,1);self.assertRegex(docs['refusal.json']['error'],'binding schema/repository differs')

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
                (['--entry-sha256',sha((OWN/'entry.py').read_bytes()),'--binding-sha256',BINDING_PIN],'differs from the SHA-256 of this entry'),
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
        self.assertEqual(r['entry_e3c29d1d_b'],'PASS');self.assertEqual(r['changed_paths'],[]);self.assertEqual((r['FR10_1'],r['U15_acceptance'],r['formal_command_adopted']),('GAP','GAP',False))
        for k in ('claimed','claimed_en','not_claimed','not_claimed_en'):self.assertTrue(r[k])
        self.assertTrue(any('変わったファイルの中身' in s for s in r['not_claimed']) and any('content of changed files' in s for s in r['not_claimed_en']))
        self.assertTrue(any('実公開' in s for s in r['not_claimed']) and any('Real publication' in s for s in r['not_claimed_en']))
        self.assertIn('.aidlc-version',{x['path'] for x in r['excluded_by_name']});self.assertIn('.agents/',{x['path'] for x in r['excluded_by_git_ignore']})
        self.assertEqual(r['exclusion_decision'],E.DECISION_B)
    def test_72_refusal_writes_refusal_json(self):
        code,docs,err=self.in_process(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],**{'README.md':None})
        self.assertEqual(code,1);self.assertEqual(sorted(docs),['refusal.json']);r=docs['refusal.json']
        self.assertEqual(r['refused_at']['stage'],'(3) working copy');self.assertEqual(r['details']['missing'],['README.md']);self.assertFalse(r['exclusions_widened'])
    def test_73_binding_shape(self):
        self.rejects('binding key set differs',self.full(self.variant(lambda b:b.update(extra=1))))
        self.rejects('purpose/approval missing',self.full(self.variant(lambda b:b.update(approval=''))))
        self.rejects('duplicate key',lambda:E.strict_json(b'{"a":1,"a":2}','x'))

    # ---- (6) upstream tree_equal ----------------------------------------------
    def upstream(self,edit_ci=None,tree=None):
        U='4'*40
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

    # ---- git stays read-only -------------------------------------------------
    def test_90_git_is_read_only(self):
        for cmd in ('status','checkout','update-ref','gc','fetch'):
            with self.assertRaisesRegex(E.Refusal,'read-only set'):E.git(cmd)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(EntryBE02)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() and not result.skipped and result.testsRun==suite.countTestCases() else 1)
