"""Regressions for u15_candidate_v4.py (binding-11).

Runs, in this order:
  1. the unchanged v3 regressions (test_u15_candidate_v3.py, pinned by
     SHA-256; its main() runs the v2 suite of 132 (which runs v1's 116) and the
     15 binding-10 cases, 147 in all). The v3 suite was written for the working
     tree at a54315f9, so it runs inside a regression-only view that shows the
     7 Step 17 files at their a54315f9 blobs. This view belongs to the test
     harness only; u15_candidate_v4.py itself shows v3 exactly these 7 files at
     their a54315f9 bytes;
  2. the binding-11 cases below (test_600..test_615).
No real file is modified (read-only overlay or in-memory binding copies). The
only child processes are refused command lines, which write nothing.
Exit 0 only when every case ran (147 + 16), none was skipped and all passed.
"""
import contextlib,copy,hashlib,importlib.util,io,json,re,subprocess,sys,types,unittest,zipfile
from pathlib import Path

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('u15_candidate_v4_under_test',OWN/'u15_candidate_v4.py')
u4c=importlib.util.module_from_spec(spec);spec.loader.exec_module(u4c)
ROOT=u4c.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
V3_TESTS=OWN/'test_u15_candidate_v3.py'
V3_TESTS_SHA256='148960fa85fcc8074bc833e4c9d9aa086431b993b6990781cdb5b60fe970b068'
V3_SUITE_COUNT=147
V4_TEST_COUNT=16
if sha(V3_TESTS.read_bytes())!=V3_TESTS_SHA256:raise SystemExit('v3 regression file differs from the pinned SHA-256')
if sha((ROOT/u4c.V3_ENTRY).read_bytes())!=u4c.V3_ENTRY_SHA256:raise SystemExit('v3 entry differs from the pinned SHA-256')
spec=importlib.util.spec_from_file_location('u15_v3_regressions',V3_TESTS)
v3t=importlib.util.module_from_spec(spec);spec.loader.exec_module(v3t)
Overlay=v3t.Overlay
HEAD='e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9';PARENT=u4c.PARENT;GRANDPARENT=u4c.GRANDPARENT
OTHER_SOURCE='packages/paludarium-wasm/index.mjs'
ENTRY_PIN=sha(u4c.SELF.read_bytes());BINDING_PIN=u4c.BINDING_SHA256
CI_RUN='39114018191';U13_RUN='39114112207';PERF_RUN='39114108809';RERUN=u4c.RERUN_RUN
SAFARI=u4c.RERUN_FAILED_JOB
README=OWN/'README.md';PENDING=OWN/'pending-minor-fixes.md'

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def own_listing():return sorted(p.name for p in OWN.iterdir())
strings=v3t.strings
# Statements that contradict the 15-file allowance at the signed head e3c29d1d (v3's list plus the a54315f9-current ones).
FORBIDDEN=re.compile(v3t.FORBIDDEN.pattern+r'|署名headはa54315f9|CIの記録はa54315f9の8 run|Steps 13〜14bの署名済みhead a54315f9のbytesであることだけ|Steps 13-14b'
    r'|Signed head a54315f9|8 runs at a54315f9|今のbytesがa54315f9|今のbytes・a54315f9|a54315f9のbytesへの固定|bb197e04 original checked and recorded only')
def contradictions(x):return [s for s in strings(x) if FORBIDDEN.search(s)]
def run(doc,rid):return next(r for r in doc['runs'] if str(r['id'])==rid)

class U15E3c29d1d(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=u4c.load_binding(BINDING_PIN)
        cls.b10,cls.b9,cls.b8,cls.b7,cls.b2=u4c.verify_base(cls.b)
        cls.summary,cls.mapping=u4c.verify(cls.b,reuse_compat=False)
        cls.View=u4c.view_class();m=u4c.nc()
        cls.a5=m.git_blobs(PARENT,list(u4c.HEAD_FILES))
        cls.a5_map={str(ROOT/p):v for p,v in cls.a5.items()}
        cls.map15={k:v for k,v in cls.mapping.items() if k in {str(ROOT/p) for p in u4c.ALLOWED_PATHS_15}}
        cls.jobs=json.loads((ROOT/cls.b['ci_jobs']['path']).read_bytes())
    def raw(self,rel):return (ROOT/rel).read_bytes()
    def variant(self,edit):
        b=copy.deepcopy(self.b);edit(b);return b
    def rejects(self,pattern,fn,**overlay):
        with Overlay(**overlay):
            with self.assertRaisesRegex(ValueError,pattern):fn()
    def full(self,b=None):return lambda:u4c.verify(b or self.b,reuse_compat=False)
    def head(self,b=None):return lambda:u4c.verify_head(b or self.b,self.b10)
    def files(self,b=None):return lambda:u4c.verify_files(b or self.b,self.b10,HEAD)
    def ci_variant(self,edit_ci=None,edit_jobs=None,edit_binding=None,rebind=True):
        b=copy.deepcopy(self.b);replace={}
        for key,edit in (('ci',edit_ci),('ci_jobs',edit_jobs)):
            if edit is None:continue
            doc=json.loads(self.raw(b[key]['path']));edit(doc);raw=json.dumps(doc,indent=2).encode();replace[b[key]['path']]=raw
            if rebind:b[key]['sha256']=sha(raw)
        if edit_binding:edit_binding(b)
        return b,replace
    def parent_sets(self):return u4c.parent_job_sets(self.b10)
    def rerun_doc(self,edit):
        d=copy.deepcopy({str(r['id']):r for r in self.jobs['runs']});edit(d[RERUN]);return d
    def refused(self,argv,pattern,**overlay):
        before=run_dirs();err=io.StringIO()
        with Overlay(**overlay),contextlib.redirect_stderr(err):code=u4c.main([str(u4c.SELF),*argv])
        self.assertEqual(code,2);self.assertRegex(err.getvalue(),'^REFUSED: '+pattern);self.assertEqual(run_dirs(),before)
    def child_argv(self,entry=None,pin=None):
        return [str(u4c.SELF),'--logical-child',ENTRY_PIN if entry is None else entry,BINDING_PIN if pin is None else pin,str(OWN/'run-never'),str(u4c.nc().OLD/'old_predicates.py'),'r.json']
    def scope_v4(self):
        V=u4c.v3();scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{},'u14_records':{}}
        with self.View(self.a5_map):out=V.u15_scope_v3(scope,self.summary['v3']['v2']['u15'],self.summary['v3']['u15_a54315f9'])
        return out,u4c.u15_scope_v4(out,self.summary['u15_e3c29d1d'])

    def test_600_positive_control(self):
        u=self.summary['u15_e3c29d1d'];h=u['head'];self.assertEqual((h['head'],h['parent'],h['head_chain']),(HEAD,PARENT,[PARENT,HEAD]))
        self.assertEqual(h['changed_paths'],sorted(u4c.HEAD_FILES));self.assertEqual(len(h['runs']),7)
        self.assertEqual({rid:r['run_attempt'] for rid,r in h['runs'].items() if r['run_attempt']!=1},{RERUN:2})
        self.assertEqual(h['rerun']['attempt_1_failed_job'],dict(name=SAFARI[0],id=SAFARI[1]));self.assertEqual(h['rerun']['attempt_2_rerun_job']['name'],SAFARI[0])
        self.assertEqual(sorted(u['files']),list(u4c.ALLOWED_PATHS_15));pins=u4c.v3_pins(self.b10)
        for p in u4c.HEAD_FILES:
            row=u['files'][p];self.assertEqual(row['e3c29d1d_sha256'],sha(self.raw(p)));self.assertEqual(row['a54315f9_sha256'],pins[p]);self.assertEqual(row['scope'],u4c.EXACT_SCOPE_V4)
        for p in u4c.UNCHANGED_FILES:self.assertEqual(u['files'][p]['e3c29d1d_sha256'],sha(self.raw(p)))
        self.assertEqual(sorted(str(Path(k).relative_to(ROOT)) for k in self.map15),list(u4c.ALLOWED_PATHS_15))
        self.assertEqual(self.summary['v3']['u15_a54315f9']['head']['head'],PARENT)
        perf=h['performance_e3c29d1d'];self.assertEqual((perf['rows'],perf['p']),(20,0.0009765625));self.assertLess(perf['meanJit'],perf['meanInterpreter'])
        self.assertEqual(perf['artifact']['digest'],'sha256:'+sha(self.raw(u4c.PERFORMANCE_ZIP)))
    def test_601_v3_entry_alone_stops_on_the_changed_files(self):
        V=u4c.v3()
        with self.assertRaisesRegex(ValueError,'moved file differs from binding/signed head: docs/release.md'):V.verify(self.b10,reuse_compat=False)
        with Overlay(replace={'docs/release.md':self.a5['docs/release.md']}):
            with self.assertRaisesRegex(ValueError,'moved file differs from binding/signed head: tests/release/test_policy.py'):V.verify(self.b10,reuse_compat=False)
        with Overlay(replace={p:self.a5[p] for p in u4c.V3_MOVED}):
            with self.assertRaisesRegex(ValueError,'old-chain extra file differs from binding/signed head: scripts/release/check.py'):V.verify(self.b10,reuse_compat=False)
        with Overlay(replace=dict(self.a5)):V.verify(self.b10,reuse_compat=False)
    def test_602_changed_files(self):
        for p in u4c.HEAD_FILES:
            msg='changed file differs from binding/signed head: '+re.escape(p)
            self.rejects(msg,self.files(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.files(),replace={p:self.a5[p]})
            self.rejects('missing/unreadable input: '+re.escape(p),self.files(),missing=[p])
            self.rejects(msg,self.files(self.variant(lambda b,p=p:b['changed_files'][p].update(e3c29d1d_sha256='0'*64))))
            self.rejects('changed file a54315f9 pin differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['changed_files'][p].update(a54315f9_sha256='0'*64))))
            self.rejects('changed file a54315f9 pin differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['changed_files'][p].update(a54315f9_sha256=sha(self.raw(p))))))
            self.rejects('changed entry differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['changed_files'][p].update(extra=1))))
        self.rejects('changed file differs from binding/signed head: scripts/release/check.py',self.full(),replace={'scripts/release/check.py':self.raw('scripts/release/check.py')+b' '})
    def test_603_unchanged_files(self):
        for p in u4c.UNCHANGED_FILES:
            msg='allowed file differs from the signed head: '+re.escape(p)
            self.rejects(msg,self.files(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.files(self.variant(lambda b,p=p:b['unchanged_files'].__setitem__(p,'0'*64))))
        self.rejects('allowed file differs from the signed head: .github/workflows/release.yml',self.full(),replace={'.github/workflows/release.yml':self.raw('.github/workflows/release.yml')+b'\n'})
    def test_604_head_parent_chain_compare(self):
        for h in (PARENT,GRANDPARENT,'x',HEAD.upper()):self.rejects('signed head differs',self.head(self.variant(lambda b,h=h:b.update(head=h))))
        self.rejects('parent differs from the binding-10 signed head',self.head(self.variant(lambda b:b.update(parent=GRANDPARENT))))
        self.rejects('signed chain differs',self.head(self.variant(lambda b:b.update(head_chain=[GRANDPARENT,PARENT,HEAD]))))
        cases=((lambda ci:ci['commits'][1]['files'].pop(),'signed commit file list differs'),
               (lambda ci:ci['commits'][1]['files'].append('scripts/release/acceptance.py'),'signed commit file list differs'),
               (lambda ci:ci['commits'][1].update(parents=[GRANDPARENT]),'commit parent chain differs'),
               (lambda ci:ci['commits'][1].update(verified=False),'signed commit not Verified'),
               (lambda ci:ci['branch'].update(head=PARENT),'CI branch head differs'),
               (lambda ci:ci['compare']['files'].pop(),'compare file list differs'),
               (lambda ci:ci['compare']['files'].append(dict(filename='README.md',status='modified',sha='0'*40)),'compare file list differs'),
               (lambda ci:ci['compare'].update(base=GRANDPARENT),'compare differs'),
               (lambda ci:ci['compare'].update(ahead_by=2),'compare differs'),
               (lambda ci:next(f for f in ci['compare']['files'] if f['filename']=='tests/release/test_api.py').update(sha='0'*40),'compare blob differs from local git: tests/release/test_api.py'))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_ci=edit);self.rejects(pattern,self.head(b),replace=replace)
    def test_605_ci_runs_and_jobs(self):
        cases=((lambda ci:run(ci,CI_RUN).update(conclusion='failure'),'CI run not successful: '+CI_RUN),
               (lambda ci:run(ci,PERF_RUN).update(head_sha=PARENT),'CI run head differs: '+PERF_RUN),
               (lambda ci:run(ci,RERUN).update(status='in_progress'),'CI run not successful: '+RERUN),
               (lambda ci:ci['runs_listed_for_head']['ids'].pop(),'CI run listing for the head differs'))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_ci=edit);self.rejects(pattern,self.head(b),replace=replace)
        # Only the one recorded run may be attempt 2, and it must be attempt 2.
        b,replace=self.ci_variant(edit_ci=lambda ci:run(ci,CI_RUN).update(run_attempt=2),edit_binding=lambda b:b['ci']['runs'][CI_RUN].update(run_attempt=2))
        self.rejects('CI run attempt differs from the allowance: '+CI_RUN,self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_ci=lambda ci:run(ci,CI_RUN).update(run_attempt=2))
        self.rejects('CI run identity/attempt differs: '+CI_RUN,self.head(b),replace=replace)
        self.rejects('CI run attempt differs from the allowance: '+RERUN,self.head(self.variant(lambda b:b['ci']['runs'][RERUN].update(run_attempt=1))))
        for allowance in ({},{RERUN:[1]},{RERUN:[SAFARI[1],1]},{RERUN:[SAFARI[1]],CI_RUN:[1]}):
            self.rejects('attempt-1 failure allowance differs from the one recorded rerun',self.head(self.variant(lambda b,a=allowance:b.update(attempt_1_failures=a))))
        b,replace=self.ci_variant(edit_ci=lambda ci:run(ci,CI_RUN).update(conclusion='failure'),rebind=False)
        self.rejects('CI evidence bytes differ',self.head(b),replace=replace)
        for edit,pattern in ((lambda d:run(d,CI_RUN)['jobs'][0].__setitem__(2,'failure'),'CI job not successful: '+CI_RUN),
                             (lambda d:run(d,PERF_RUN)['jobs'].pop(),'CI job set differs: '+PERF_RUN),
                             (lambda d:run(d,CI_RUN).update(total_count=24),'CI job count differs from the API total'),
                             (lambda d:d.update(head=PARENT),'CI job evidence repository/head differs'),
                             (lambda d:run(d,CI_RUN).update(attempt_1=copy.deepcopy(run(d,RERUN)['attempt_1'])),'unexpected earlier attempt record: '+CI_RUN)):
            b,replace=self.ci_variant(edit_jobs=edit);self.rejects(pattern,self.head(b),replace=replace)
        self.rejects('CI run missing or unexpected',self.head(self.variant(lambda b:b['ci']['runs'].pop(CI_RUN))))
        # The expected job sets are a54315f9's: renaming a job in the new records is refused even when rebound.
        def rename(doc):
            for j in run(doc,U13_RUN)['jobs']:
                if j[0]=='lint':j[0]='lint (renamed)'
        b,replace=self.ci_variant(edit_jobs=rename);self.rejects('CI job set differs: '+U13_RUN,self.head(b),replace=replace)
        def workflow(doc):run(doc,CI_RUN)['name']='U14 current full quality'
        b,replace=self.ci_variant(edit_ci=workflow,edit_jobs=workflow,edit_binding=lambda b:b['ci']['runs'][CI_RUN].update(name='U14 current full quality'))
        self.rejects('CI job set differs: '+CI_RUN,self.head(b),replace=replace)
        self.rejects('CI run has no workflow at the parent head',self.head(self.variant(lambda b:b['ci']['runs'][CI_RUN].update(name='Other'))))
        self.rejects('parent CI job evidence bytes differ',self.head(),replace={self.b10['ci_jobs']['path']:self.raw(self.b10['ci_jobs']['path'])+b' '})
    def test_606_rerun_allowance(self):
        def a1(r):return r['attempt_1']
        def safari_rows(rows):return [j for j in rows if j[0]==SAFARI[0]]
        # Through the stored records (U1's verify_ci_jobs and v4's own checks).
        cases=((lambda d:a1(run(d,RERUN))['jobs'][0].__setitem__(2,'failure'),'CI attempt 1 failures differ: '+RERUN),
               (lambda d:run(d,RERUN)['jobs'][0].__setitem__(2,'failure'),'CI job not successful: '+RERUN),
               (lambda d:run(d,RERUN)['jobs'][0].__setitem__(3,'2026-10-18T09:58:00Z'),'CI later attempt re-ran other jobs: '+RERUN),
               (lambda d:run(d,RERUN).pop('attempt_1'),'CI attempt 1 record missing: '+RERUN),
               (lambda d:a1(run(d,RERUN)).update(total_count=28),'CI attempt 1 job count differs from the API total'),
               (lambda d:a1(run(d,RERUN)).update(conclusion='success'),'CI attempt 1 identity differs: '+RERUN),
               (lambda d:a1(run(d,RERUN))['jobs'].pop(0),'CI attempt 1 job set differs: '+RERUN),
               (lambda d:a1(run(d,RERUN))['failures'][0].update(cause=''),'CI attempt 1 failure record incomplete: '+RERUN))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_jobs=edit);self.rejects(pattern,self.head(b),replace=replace)
        # v4's own allowance, directly.
        sets=self.parent_sets();u4c.verify_rerun({RERUN:self.rerun_doc(lambda r:None)[RERUN]},sets)
        def other_failed(r):
            for j in a1(r)['jobs']:
                if j[0]=='lint':j[2]='failure'
        def renamed_failed(r):
            for j in safari_rows(a1(r)['jobs']):j[0]='u11-programs / differential (ubuntu-latest, node)'
        def other_id(r):
            for j in safari_rows(a1(r)['jobs']):j[1]=1
        cases=((other_failed,'attempt-1 failed job differs from the allowance'),(renamed_failed,'attempt-1 failed job differs from the allowance'),
               (other_id,'attempt-1 failed job differs from the allowance'),
               (lambda r:a1(r)['failures'][0].update(job_id=1),'attempt-1 failure record differs from the allowance'),
               (lambda r:a1(r)['failures'].append(dict(a1(r)['failures'][0])),'attempt-1 failure record differs from the allowance'),
               (lambda r:a1(r).update(total_count=30),'CI attempt 1 job count differs from the API total'),
               (lambda r:r['jobs'][2].__setitem__(2,'failure'),'attempt-2 job not successful'),
               (lambda r:r['jobs'].pop(),'attempt-2 job set differs from the parent'),
               (lambda r:r['jobs'][0].__setitem__(3,'2026-10-18T09:58:00Z'),'attempt 2 re-ran other jobs'),
               (lambda r:r.update(run_attempt=3),'rerun run differs from the allowance'),
               (lambda r:r.pop('attempt_1'),'rerun run differs from the allowance'))
        for edit,pattern in cases:
            with self.assertRaisesRegex(ValueError,pattern):u4c.verify_rerun({RERUN:self.rerun_doc(edit)[RERUN]},sets)
        bad=copy.deepcopy(sets);bad[u4c.RERUN_NAME]=bad[u4c.RERUN_NAME][1:]
        with self.assertRaisesRegex(ValueError,'attempt-2 job set differs from the parent'):u4c.verify_rerun({RERUN:self.rerun_doc(lambda r:None)[RERUN]},bad)
    def test_607_performance(self):
        path=self.b['performance']['path'];zp=u4c.PERFORMANCE_ZIP
        self.rejects('performance original bytes differ',self.head(self.variant(lambda b:b['performance'].update(sha256='0'*64))))
        self.rejects('performance run is not the U14 full-quality run',self.head(self.variant(lambda b:b['performance'].update(run_id=int(CI_RUN)))))
        self.rejects('performance original path differs',self.head(self.variant(lambda b:b['performance'].update(path=self.b10['performance']['path']))))
        self.rejects('performance artifact ZIP differs from the API digest',self.head(self.variant(lambda b:b['performance']['artifact'].update(digest='sha256:'+'0'*64))))
        self.rejects('performance artifact ZIP differs from the API digest',self.head(self.variant(lambda b:b['performance']['artifact'].update(size_in_bytes=1))))
        self.rejects('performance artifact ZIP differs from the API digest',self.head(),replace={zp:self.raw(zp)+b'\0'})
        self.rejects('missing/unreadable input: '+re.escape(zp),self.head(),missing=[zp])
        for key,value in (('member','performance/other.json'),('zip_path',path),('id',1),('name','u11-node-other')):
            self.rejects('performance artifact entry differs',self.head(self.variant(lambda b,k=key,v=value:b['performance']['artifact'].update({k:v}))))
        self.rejects('performance artifact entry differs',self.head(self.variant(lambda b:b['performance']['artifact'].update(extra=1))))
        alt=json.dumps(json.loads(self.raw(path))).encode();self.assertNotEqual(alt,self.raw(path))
        self.rejects('performance original differs from the artifact ZIP member',self.head(self.variant(lambda b:b['performance'].update(sha256=sha(alt)))),replace={path:alt})
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('observations.json',b'{}')
        other=buf.getvalue()
        self.rejects('performance artifact ZIP member missing',self.head(self.variant(lambda b:b['performance']['artifact'].update(digest='sha256:'+sha(other),size_in_bytes=len(other)))),replace={zp:other})
    def test_608_sixteenth_path(self):
        V=u4c.v3();self.assertEqual(u4c.ALLOWED_PATHS_15,V.ALLOWED_PATHS_15);self.assertEqual(len(u4c.ALLOWED_PATHS_15),15)
        self.assertTrue(set(u4c.HEAD_FILES)<=set(u4c.ALLOWED_PATHS_15));self.assertEqual(sorted({*u4c.HEAD_FILES,*u4c.UNCHANGED_FILES}),list(u4c.ALLOWED_PATHS_15))
        self.assertEqual(set(u4c.HEAD_FILES),set(V.MOVED)|set(u4c.V3_EXTRA_CHANGED));self.assertTrue(set(u4c.V3_EXTRA_CHANGED)<=set(V.EXTRA_FILES))
        sixteenth='scripts/release/package.py';self.assertIn(sixteenth,V.v2().old_chain_pins());self.assertNotIn(sixteenth,u4c.ALLOWED_PATHS_15)
        row={'a54315f9_sha256':sha(self.raw(sixteenth)),'e3c29d1d_sha256':sha(self.raw(sixteenth))}
        for extra in (sixteenth,'scripts/release/acceptance.py'):
            self.rejects('changed allowance differs from the authorized path set',self.files(self.variant(lambda b,e=extra:b['changed_files'].__setitem__(e,row))))
            self.rejects('unchanged allowance differs from the authorized path set',self.files(self.variant(lambda b,e=extra:b['unchanged_files'].__setitem__(e,sha(self.raw(e))))))
        self.rejects('changed allowance differs from the authorized path set',self.files(self.variant(lambda b:b['changed_files'].pop('tests/release/test_api.py'))))
        self.rejects('unchanged allowance differs from the authorized path set',self.files(self.variant(lambda b:b['unchanged_files'].pop('README.md'))))
        moved=self.variant(lambda b:b['unchanged_files'].__setitem__('docs/release.md',sha(self.raw('docs/release.md'))));moved['changed_files'].pop('docs/release.md')
        self.rejects('changed allowance differs from the authorized path set',self.files(moved))
        self.rejects('binding-11 key set differs',lambda:u4c.verify_base(self.variant(lambda b:b.pop('unchanged_files'))))
        saved=u4c.HEAD_FILES
        try:
            u4c.HEAD_FILES=(*saved,'scripts/release/acceptance.py')
            with self.assertRaisesRegex(ValueError,'changed files are not inside the 15 allowed paths'):u4c.verify_constants()
            u4c.HEAD_FILES=(*saved[1:],'README.md')
            with self.assertRaisesRegex(ValueError,'changed files differ from v3 MOVED and EXTRA_FILES'):u4c.verify_constants()
        finally:u4c.HEAD_FILES=saved
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),self.full(),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
    def test_609_old_chain_pins_with_the_v4_mapping(self):
        m=u4c.nc();fc=m.load('fc_v4_under_test',m.OLD/'final_candidate.py');pins=u4c.v3().v2().old_chain_pins()
        changed=[p for p in u4c.HEAD_FILES if p in pins];self.assertEqual(sorted(changed),sorted(u4c.HEAD_FILES))
        # The working tree (e3c29d1d) alone and the a54315f9 view alone are refused by the old chain; the 15 old bytes pass.
        with self.assertRaisesRegex(ValueError,'current source changed: '):fc.source_pins(pins)
        with self.View(self.a5_map):
            with self.assertRaisesRegex(ValueError,'current source changed: '):fc.source_pins(pins)
        with self.View(self.map15):fc.source_pins(pins)
        for p in u4c.HEAD_FILES:
            self.assertEqual(sha(self.map15[str(ROOT/p)]),pins[p])
            partial={k:v for k,v in self.map15.items() if k!=str(ROOT/p)}
            with self.View(partial):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(p)+'$'):fc.source_pins(pins)
        sixteenth='scripts/release/package.py'
        with Overlay(replace={sixteenth:self.raw(sixteenth)+b'\n'}):
            with self.View(self.map15):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(sixteenth)+'$'):fc.source_pins(pins)
    def test_610_v3_pins_and_binding_11(self):
        for r in u4c.HISTORY_V3:
            self.rejects('v3 history file changed: '+re.escape(r),lambda:u4c.verify_history_v3(self.b),replace={r:self.raw(r)+b'\n'})
        with self.assertRaisesRegex(ValueError,'v3 history pin set differs'):u4c.verify_history_v3(self.variant(lambda b:b['history_v3'].popitem()))
        for edit,msg in ((lambda b:b['v3']['entry'].update(sha256='0'*64),'v3 entry/binding differs'),(lambda b:b['v3']['binding'].update(name='binding-09.json'),'v3 entry/binding differs'),
                         (lambda b:b.update(schema=10),'binding schema/repository differs'),(lambda b:b.update(extra=1),'binding-11 key set differs')):
            with self.assertRaisesRegex(ValueError,msg):u4c.verify_base(self.variant(edit))
        cached=u4c._V3
        try:
            u4c._V3=None
            self.rejects('v3 entry bytes differ from the pinned SHA-256',u4c.v3,replace={u4c.V3_ENTRY:self.raw(u4c.V3_ENTRY)+b'\n'})
        finally:u4c._V3=cached
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u4c.verify_base(self.b),replace={u4c.LOOP+u4c.V3_BINDING:self.raw(u4c.LOOP+u4c.V3_BINDING)+b'\n'})
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u4c.load_binding(BINDING_PIN),replace={u4c.LOOP+u4c.BINDING:self.raw(u4c.LOOP+u4c.BINDING)+b'\n'})
    def test_611_argument_pins_exit_2(self):
        for pin in ('0'*64,u4c.V3_BINDING_SHA256,ENTRY_PIN):
            with self.assertRaisesRegex(ValueError,'binding SHA-256 differs from the binding pinned by this entry'):u4c.load_binding(pin)
        usage=re.escape(u4c.USAGE)
        for argv in ([],['--entry-sha256',ENTRY_PIN],['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN]):self.refused(argv,usage)
        for pin in ('0'*64,u4c.V3_ENTRY_SHA256):self.refused(['--entry-sha256',pin,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs from the SHA-256 of this entry file')
        for pin in ('0'*64,u4c.V3_BINDING_SHA256):self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',pin],'--binding-sha256 differs from the SHA-256 of '+re.escape(u4c.BINDING))
        self.refused(['--entry-sha256',ENTRY_PIN.upper(),'--binding-sha256',BINDING_PIN],'--entry-sha256 must be 64 lowercase hex digits')
        before=own_listing()
        for argv,pattern in (([],usage),(['--entry-sha256',u4c.V3_ENTRY_SHA256,'--binding-sha256',u4c.V3_BINDING_SHA256],'--entry-sha256 differs')):
            r=subprocess.run([sys.executable,'-B',str(u4c.SELF),*argv],cwd=ROOT,capture_output=True,timeout=60)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,b'');self.assertRegex(r.stderr.decode(),'^REFUSED: '+pattern)
        self.assertEqual(own_listing(),before)
    def test_612_old_chain_guard_and_child(self):
        calls=[];nc=u4c.nc()
        self.assertNotEqual(u4c.SELF,(ROOT/u4c.V3_ENTRY).resolve());self.assertEqual(u4c.SELF.name,'u15_candidate_v4.py')
        def fake_real(argv,**kw):calls.append(argv);return types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
        run_=u4c.guarded_run(ENTRY_PIN,BINDING_PIN,OWN,[],fake_real);kw=dict(cwd=ROOT,capture_output=True,timeout=900)
        good=[sys.executable,'-B',str(nc.OLD/'old_predicates.py'),str(OWN/'never.json')];run_(good,**kw)
        # The old chain's children re-run v4 (not v3).
        self.assertEqual(calls[0][2:6],[str(u4c.SELF),'--logical-child',ENTRY_PIN,BINDING_PIN])
        with self.assertRaisesRegex(ValueError,'unexpected old child argv'):run_([sys.executable,'-B',str(nc.OLD/'final_candidate.py'),'r.json'],**kw)
        with self.assertRaisesRegex(ValueError,'unexpected child options'):run_(good,**{**kw,'timeout':901})
        argv=self.child_argv()
        self.rejects('--entry-sha256 differs from the SHA-256 of this entry file',lambda:u4c.logical_child(self.child_argv(entry=u4c.V3_ENTRY_SHA256)))
        self.rejects('changed file differs from binding/signed head: docs/release.md',lambda:u4c.logical_child(argv),replace={'docs/release.md':self.raw('docs/release.md')+b'\n'})
        with self.assertRaisesRegex(ValueError,'child receipt folder differs'):u4c.logical_child(argv)
        r=subprocess.run([sys.executable,'-B',*self.child_argv(entry='0'*64)],cwd=ROOT,capture_output=True,timeout=60)
        self.assertEqual(r.returncode,1);self.assertIn('--entry-sha256 differs from the SHA-256 of this entry file',r.stderr.decode())
    def test_613_no_statement_contradicts_the_e3c29d1d_allowance(self):
        V=u4c.v3()
        # The detector finds v3's a54315f9-current statements (so it can fail).
        self.assertTrue(contradictions(V.statements()) and contradictions(V.ALLOWANCE_V3) and contradictions(V.EXACT_SCOPE_V3) and contradictions(V.ALLOWANCE_V3_EN))
        self.assertTrue(contradictions(['inner FR8.3 binding unchanged (1ceae86c); bb197e04 original checked and recorded only']))
        _,out=self.scope_v4();claimed,not_claimed=u4c.statements()
        own=[claimed,not_claimed,u4c.ALLOWANCE_V4,u4c.ALLOWANCE_V4_EN,u4c.EXACT_SCOPE_V4,u4c.EXACT_SCOPE_V4_EN,u4c.LAYERING_V4,u4c.RERUN_STATEMENT,u4c.RERUN_STATEMENT_EN,
            u4c.PERFORMANCE_SCOPE_V4,u4c.PERFORMANCE_SCOPE_V4_JA,out['u15_version'],out['u15_old_chain'],out['u15_e3c29d1d'],self.summary['u15_e3c29d1d']]
        self.assertEqual(contradictions(own),[])
        layer=u4c.v3_summary_for_result(self.summary['v3'])
        rows=[layer['v2']['u15']['old_chain_files'],layer['u15_a54315f9']['files'],layer['u15_a54315f9']['old_chain_extra']]
        self.assertEqual(contradictions(rows),[])
        self.assertEqual(out['u15_version']['head'],HEAD);self.assertEqual(out['u15_version']['scope'],u4c.ALLOWANCE_V4)
        self.assertEqual(out['u15_old_chain']['allowed_paths'],list(u4c.ALLOWED_PATHS_15));self.assertEqual(out['u15_old_chain']['exact_bytes_scope'],u4c.EXACT_SCOPE_V4)
        for p in u4c.ALLOWED_PATHS_15:
            self.assertIn(p,u4c.ALLOWANCE_V4);self.assertIn(p,u4c.ALLOWANCE_V4_EN);self.assertIn(p,not_claimed[0])
        for p in u4c.HEAD_FILES:self.assertIn(p,u4c.ALLOWANCE_V4);self.assertIn(p,u4c.LAYERING_V4)
        self.assertIn('15ファイル',u4c.ALLOWANCE_V4);self.assertIn('15ファイル',not_claimed[0])
        for p in u4c.EXACT_FILES_ALL:self.assertIn(p,u4c.EXACT_SCOPE_V4)
        for s in ('e3c29d1d','Steps 13〜17','U15のレビューと試験','確かめていない'):self.assertIn(s,u4c.EXACT_SCOPE_V4)
        for s in ('e3c29d1d','Steps 13-17',"U15's review and tests",'not by this command'):self.assertIn(s,u4c.EXACT_SCOPE_V4_EN)
        for p,row in self.summary['u15_e3c29d1d']['files'].items():
            if p in u4c.EXACT_FILES_ALL:self.assertEqual(row['scope'],u4c.EXACT_SCOPE_V4)
            else:self.assertNotIn('scope',row)
        self.assertNotIn(V.CLAIMED_V3[1],claimed);self.assertNotIn(V.CLAIMED_V3[2],claimed);self.assertIn(V.CLAIMED_V3[0],claimed);self.assertIn(V.CLAIMED_V3[3],claimed)
        for s in (claimed[-3],u4c.RERUN_STATEMENT):
            self.assertIn('39114110570',s);self.assertIn(SAFARI[0],s);self.assertIn(str(SAFARI[1]),s);self.assertIn('attempt 2',s)
        self.assertTrue(any('FR10.1' in s and 'GAP' in s for s in not_claimed));self.assertTrue(any('中身が正しいこと' in s for s in not_claimed))
        self.assertTrue(any('原因' in s and 'Safari' in s for s in not_claimed))
    def test_614_minor_fixes(self):
        V=u4c.v3();scope3,out=self.scope_v4()
        # (1) The performance claim scope names every checked original.
        self.assertEqual(scope3['u15_version']['performance'],'inner FR8.3 binding unchanged (1ceae86c); bb197e04 original checked and recorded only')
        for s in ('bb197e04','a54315f9','e3c29d1d','39089194062','39096893624','39114108809','1ceae86c'):
            self.assertIn(s,out['u15_version']['performance']);self.assertIn(s,out['u15_version']['performance_ja'])
        self.assertNotIn(scope3['u15_version']['performance'],list(strings(out)))
        # (2) Every row value carries its time point; v2's MOVED rows keep bb197e04 values with a bb197e04 time point.
        layer=u4c.v3_summary_for_result(self.summary['v3']);self.assertEqual(layer['time_point'],u4c.V3_LAYER_TIME_POINT)
        v2rows=layer['v2']['u15']['old_chain_files'];self.assertEqual(sorted(v2rows),sorted(['Cargo.toml',*V.v2().EXACT_FILES]))
        for p,row in v2rows.items():
            self.assertEqual(set(row['time_points']),{'old_sha256','new_sha256'});self.assertIn('bb197e04',row['time_points']['new_sha256'])
            self.assertEqual(row['new_sha256'],self.b9['old_chain_files'][p]['new_sha256'])
            if p!='Cargo.toml':self.assertEqual(row['scope'],u4c.V2_ROW_SCOPE)
        for p in V.MOVED:self.assertEqual(v2rows[p]['new_sha256'],self.b10['moved_files'][p]['bb197e04_sha256'])
        for p,row in layer['u15_a54315f9']['files'].items():self.assertIn('a54315f9_sha256',row['time_points'])
        for p,row in layer['u15_a54315f9']['old_chain_extra'].items():
            self.assertEqual(row['scope'],u4c.V3_ROW_SCOPE);self.assertEqual(set(row['time_points']),{'old_sha256','a54315f9_sha256'})
        self.assertNotIn(V.EXACT_SCOPE_V3,list(strings(layer)))
        self.assertEqual(self.summary['v3']['u15_a54315f9']['old_chain_extra']['scripts/release/check.py']['scope'],V.EXACT_SCOPE_V3)
        # (3) and (4) The README headings and the versioning rule; the pending list notes v4.
        text=README.read_text(encoding='utf-8');pending=PENDING.read_text(encoding='utf-8')
        self.assertNotIn('v2（現行、未採用）',text);self.assertIn('## v2（履歴',text);self.assertIn('## v3（採用済み、履歴）',text);self.assertIn('## v4（未採用）',text)
        self.assertIn('上書きしない',text);self.assertIn('v4b',text);self.assertIn('binding-12',text)
        self.assertIn('v4 での対応',pending)
    def test_615_claim_scope_layering(self):
        _,out=self.scope_v4();note=out['u15_e3c29d1d']
        self.assertEqual((note['head'],note['parent'],note['changed_paths'],note['unchanged_paths']),(HEAD,PARENT,list(u4c.HEAD_FILES),list(u4c.UNCHANGED_FILES)))
        self.assertEqual(note['layering'],u4c.LAYERING_V4);self.assertEqual(note['ci_rerun'],u4c.RERUN_STATEMENT)
        self.assertEqual(out['u15_a54315f9']['time_point'],u4c.V3_LAYER_TIME_POINT);self.assertEqual(out['u15_a54315f9']['head'],PARENT)
        scope3,_=self.scope_v4()
        for key in ('u15_version','u15_old_chain','u15_a54315f9'):
            with self.assertRaisesRegex(ValueError,'v3 claim scope differs'):u4c.u15_scope_v4({k:v for k,v in scope3.items() if k!=key},self.summary['u15_e3c29d1d'])
        V=u4c.v3();scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{}}
        with self.assertRaisesRegex(ValueError,'U14 claim scope missing'):V.u15_scope_v3(scope,self.summary['v3']['v2']['u15'],self.summary['v3']['u15_a54315f9'])

def main():
    # The v3 suite replays the a54315f9 working tree: the 7 Step 17 files at their a54315f9 blobs (harness only).
    world=u4c.nc().git_blobs(PARENT,list(u4c.HEAD_FILES))
    with Overlay(replace=world):code=v3t.main()
    fifth=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(U15E3c29d1d))
    print(f'regressions: v3 suite (147) exit {code} under the a54315f9 working-tree view; binding-11 {fifth.testsRun}/{V4_TEST_COUNT}, skipped {len(fifth.skipped)}; total {V3_SUITE_COUNT+fifth.testsRun} / expected {V3_SUITE_COUNT+V4_TEST_COUNT}')
    ok=code==0 and fifth.wasSuccessful() and fifth.testsRun==V4_TEST_COUNT and not fifth.skipped
    return 0 if ok else 1

if __name__=='__main__':sys.exit(main())
