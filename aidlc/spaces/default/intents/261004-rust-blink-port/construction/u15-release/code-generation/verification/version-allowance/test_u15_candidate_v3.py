"""Regressions for u15_candidate_v3.py (binding-10).

Runs, in this order:
  1. the unchanged v2 regressions (test_u15_candidate_v2.py, pinned by
     SHA-256; its main() runs the binding-08 suite of 116 and the 16 binding-09
     cases, 132 in all). The v2 suite was written for the working tree at
     bb197e04, so it runs inside a regression-only view that shows the 12 Step
     14b files at their bb197e04 blobs. This view belongs to the test harness
     only; u15_candidate_v3.py itself shows v2 only the two MOVED files at
     their bb197e04 bytes;
  2. the binding-10 cases below (test_500..test_514), including the 15-file
     extension (test_507 a 16th path, test_508 the old chain's pins with the 8-
     and 15-file views, test_512 the contradiction check, test_514 the 7
     old-chain files).
No real file is modified (read-only overlay or in-memory binding copies). The
only child processes are refused command lines, which write nothing.
Exit 0 only when every case ran (132 + 15), none was skipped and all passed.
"""
import contextlib,copy,hashlib,importlib.util,io,json,re,subprocess,sys,types,unittest
from pathlib import Path

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('u15_candidate_v3_under_test',OWN/'u15_candidate_v3.py')
u3c=importlib.util.module_from_spec(spec);spec.loader.exec_module(u3c)
ROOT=u3c.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
V2_TESTS=OWN/'test_u15_candidate_v2.py'
V2_TESTS_SHA256='57c0727fbfe71716fbd386227292f8d69171d7b5e7ac499f5e277c188fd53b7f'
V2_SUITE_COUNT=132
V3_TEST_COUNT=15
if sha(V2_TESTS.read_bytes())!=V2_TESTS_SHA256:raise SystemExit('v2 regression file differs from the pinned SHA-256')
if sha((ROOT/u3c.V2_ENTRY).read_bytes())!=u3c.V2_ENTRY_SHA256:raise SystemExit('v2 entry differs from the pinned SHA-256')
spec=importlib.util.spec_from_file_location('u15_v2_regressions',V2_TESTS)
v2t=importlib.util.module_from_spec(spec);spec.loader.exec_module(v2t)
Overlay=v2t.Overlay
SELF_REL=str(u3c.SELF.relative_to(ROOT));BINDING_REL=u3c.LOOP+u3c.BINDING
HEAD='a54315f9493d6e9fb8d4792ffcefd12203540311';PARENT=u3c.PARENT;PRIOR='57a8c96f610d6e02234354e5e4fb5cac068d5036'
OTHER_SOURCE='packages/paludarium-wasm/index.mjs'
ENTRY_PIN=sha(u3c.SELF.read_bytes());BINDING_PIN=u3c.BINDING_SHA256
CI_RUN='39108225399';PERF_RUN='39096893624'
# The Step 14b files the old chain's binding-v4 pins outside the 8 allowed files.
OLD_CHAIN_PINNED=('.github/workflows/release-check.yml','.github/workflows/release.yml','scripts/release/check.py','scripts/release/policy.py',
    'tests/release/test_api.py','tests/release/test_check.py','tests/release/test_publish_adapter.py')

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def own_listing():return sorted(p.name for p in OWN.iterdir())
def strings(x):
    if isinstance(x,str):yield x
    elif isinstance(x,dict):
        for k,v in x.items():yield from strings(k);yield from strings(v)
    elif isinstance(x,(list,tuple)):
        for v in x:yield from strings(v)
# Statements that contradict the 8-file allowance at a54315f9.
FORBIDDEN=re.compile(r'3ファイル以外の差|3ファイルで許す|それらを許さない|(だけ|のみ)を?3ファイル|bb197e04のbytesへの固定4つ|署名headはbb197e04|Steps 13〜14の署名済みhead bb197e04のbytesであることだけ'
    r'|8ファイルだけ|8ファイル以外の差|そのまま拒否される|ほかの10ファイル|Exactly 8 files')
def contradictions(x):return [s for s in strings(x) if FORBIDDEN.search(s)]

class U15A54315f9(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=u3c.load_binding(BINDING_PIN)
        cls.b9,cls.b8,cls.b7,cls.b2=u3c.verify_base(cls.b)
        cls.summary,cls.mapping=u3c.verify(cls.b,reuse_compat=False)
        cls.View=u3c.view_class();m=u3c.nc()
        cls.par=m.git_blobs(PARENT,list(u3c.MOVED))
        cls.map8={k:v for k,v in cls.mapping.items() if k in {str(ROOT/p) for p in u3c.ALLOWED_PATHS}}
        cls.map15={k:v for k,v in cls.mapping.items() if k in {str(ROOT/p) for p in u3c.ALLOWED_PATHS_15}}
        cls.old7=m.git_blobs(PARENT,list(u3c.EXTRA_FILES))
    def raw(self,rel):return (ROOT/rel).read_bytes()
    def variant(self,edit):
        b=copy.deepcopy(self.b);edit(b);return b
    def rejects(self,pattern,fn,**overlay):
        with Overlay(**overlay):
            with self.assertRaisesRegex(ValueError,pattern):fn()
    def full(self,b=None):return lambda:u3c.verify(b or self.b,reuse_compat=False)
    def head(self,b=None):return lambda:u3c.verify_head(b or self.b,self.b8)
    def files(self,b=None):return lambda:u3c.verify_files(b or self.b,self.b9,HEAD)
    def extra(self,b=None):return lambda:u3c.verify_extra(b or self.b,HEAD)
    def ci_variant(self,edit_ci=None,edit_jobs=None,edit_binding=None,rebind=True):
        b=copy.deepcopy(self.b);replace={}
        for key,edit in (('ci',edit_ci),('ci_jobs',edit_jobs)):
            if edit is None:continue
            doc=json.loads(self.raw(b[key]['path']));edit(doc);raw=json.dumps(doc,indent=2).encode();replace[b[key]['path']]=raw
            if rebind:b[key]['sha256']=sha(raw)
        if edit_binding:edit_binding(b)
        return b,replace
    def refused(self,argv,pattern,**overlay):
        before=run_dirs();err=io.StringIO()
        with Overlay(**overlay),contextlib.redirect_stderr(err):code=u3c.main([str(u3c.SELF),*argv])
        self.assertEqual(code,2);self.assertRegex(err.getvalue(),'^REFUSED: '+pattern);self.assertEqual(run_dirs(),before)
    def child_argv(self,entry=None,pin=None):
        return [str(u3c.SELF),'--logical-child',ENTRY_PIN if entry is None else entry,BINDING_PIN if pin is None else pin,str(OWN/'run-never'),str(u3c.nc().OLD/'old_predicates.py'),'r.json']

    def test_500_positive_control(self):
        u=self.summary['u15_a54315f9'];self.assertEqual((u['head']['head'],u['head']['parent']),(HEAD,PARENT))
        self.assertEqual(u['head']['changed_paths'],sorted(u3c.HEAD_FILES));self.assertEqual(len(u['head']['runs']),8)
        self.assertEqual(sorted(u['files']),sorted(u3c.ALLOWED_PATHS))
        for p in u3c.MOVED:
            self.assertEqual(u['files'][p]['a54315f9_sha256'],sha(self.raw(p)));self.assertEqual(u['files'][p]['bb197e04_sha256'],self.b9['old_chain_files'][p]['new_sha256'])
        self.assertEqual(sorted(str(Path(k).relative_to(ROOT)) for k in self.map8),list(u3c.ALLOWED_PATHS))
        for k,v in self.map8.items():self.assertEqual(sha(v),self.summary['v2']['u15']['old_chain_files'].get(str(Path(k).relative_to(ROOT)),{}).get('old_sha256',sha(v)))
        self.assertEqual(u['head']['performance_a54315f9']['rows'],20)
    def test_501_v2_entry_alone_stops_on_the_moved_files(self):
        V=u3c.v2()
        with self.assertRaisesRegex(ValueError,'old-chain file differs from binding/signed head: docs/release.md'):V.verify(self.b9,reuse_compat=False)
        with Overlay(replace={'docs/release.md':self.par['docs/release.md']}):
            with self.assertRaisesRegex(ValueError,'old-chain file differs from binding/signed head: tests/release/test_policy.py'):V.verify(self.b9,reuse_compat=False)
        with Overlay(replace=dict(self.par)):V.verify(self.b9,reuse_compat=False)
    def test_502_moved_files_differ_from_a54315f9(self):
        for p in u3c.MOVED:
            msg='moved file differs from binding/signed head: '+re.escape(p)
            self.rejects(msg,self.files(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.files(),replace={p:self.par[p]})
            self.rejects('missing/unreadable input: '+re.escape(p),self.files(),missing=[p])
            self.rejects(msg,self.files(self.variant(lambda b,p=p:b['moved_files'][p].update(new_sha256='0'*64))))
            self.rejects('moved file bb197e04 pin differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['moved_files'][p].update(bb197e04_sha256='0'*64))))
            self.rejects('moved entry differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['moved_files'][p].update(extra=1))))
        self.rejects('moved file differs from binding/signed head: docs/release.md',self.full(),replace={'docs/release.md':self.raw('docs/release.md')+b' '})
    def test_503_stay_files_differ(self):
        for p in u3c.STAY:
            msg='allowed file differs from the signed head: '+re.escape(p)
            self.rejects(msg,self.files(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.files(self.variant(lambda b,p=p:b['stay_files'].__setitem__(p,'0'*64))))
        self.rejects('allowed file differs from the signed head: README.md',self.full(),replace={'README.md':self.raw('README.md')+b'\n'})
    def test_504_head_parent_chain_compare(self):
        for h in (PARENT,PRIOR,'x',HEAD.upper()):self.rejects('signed head differs',self.head(self.variant(lambda b,h=h:b.update(head=h))))
        self.rejects('parent differs from the binding-08 signed head',self.head(self.variant(lambda b:b.update(parent=PRIOR))))
        self.rejects('signed chain differs',self.head(self.variant(lambda b:b.update(head_chain=[PRIOR,PARENT,HEAD]))))
        cases=((lambda ci:ci['commits'][1]['files'].pop(),'signed commit file list differs'),
               (lambda ci:ci['commits'][1].update(parents=[PRIOR]),'commit parent chain differs'),
               (lambda ci:ci['commits'][1].update(verified=False),'signed commit not Verified'),
               (lambda ci:ci['branch'].update(head=PARENT),'CI branch head differs'),
               (lambda ci:ci['compare']['files'].pop(),'compare file list differs'),
               (lambda ci:ci['compare']['files'].append(dict(filename='README.md',status='modified',sha='0'*40)),'compare file list differs'),
               (lambda ci:ci['compare'].update(base=PRIOR),'compare differs'),
               (lambda ci:ci['compare'].update(ahead_by=2),'compare differs'),
               (lambda ci:next(f for f in ci['compare']['files'] if f['filename']=='docs/release.md').update(sha='0'*40),'compare blob differs from local git: docs/release.md'))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_ci=edit);self.rejects(pattern,self.head(b),replace=replace)
    def test_505_ci_runs_and_jobs(self):
        def run(doc,rid):return next(r for r in doc['runs'] if str(r['id'])==rid)
        cases=((lambda ci:run(ci,CI_RUN).update(conclusion='failure'),'CI run not successful: '+CI_RUN),
               (lambda ci:run(ci,PERF_RUN).update(head_sha=PARENT),'CI run head differs: '+PERF_RUN),
               (lambda ci:run(ci,CI_RUN).update(status='in_progress'),'CI run not successful: '+CI_RUN),
               (lambda ci:ci['runs_listed_for_head']['ids'].pop(),'CI run listing for the head differs'))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_ci=edit);self.rejects(pattern,self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_ci=lambda ci:run(ci,CI_RUN).update(run_attempt=2),edit_binding=lambda b:b['ci']['runs'][CI_RUN].update(run_attempt=2))
        self.rejects('CI job run identity differs|CI run is not a first attempt|CI attempt 1 record missing',self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_ci=lambda ci:run(ci,CI_RUN).update(conclusion='failure'),rebind=False)
        self.rejects('CI evidence bytes differ',self.head(b),replace=replace)
        for edit,pattern in ((lambda d:run(d,CI_RUN)['jobs'][0].__setitem__(2,'failure'),'CI job not successful: '+CI_RUN),
                             (lambda d:run(d,PERF_RUN)['jobs'].pop(),'CI job set differs: '+PERF_RUN),
                             (lambda d:run(d,CI_RUN).update(total_count=24),'CI job count differs from the API total'),
                             (lambda d:d.update(head=PARENT),'CI job evidence repository/head differs')):
            b,replace=self.ci_variant(edit_jobs=edit);self.rejects(pattern,self.head(b),replace=replace)
        self.rejects('CI run missing or unexpected',self.head(self.variant(lambda b:b['ci']['runs'].pop(CI_RUN))))
        def rename(doc):run(doc,CI_RUN)['name']='U14 current full quality'
        b,replace=self.ci_variant(edit_ci=rename,edit_jobs=rename,edit_binding=lambda b:b['ci']['runs'][CI_RUN].update(name='U14 current full quality'))
        self.rejects('CI job set differs: '+CI_RUN,self.head(b),replace=replace)
        self.rejects('CI run has no workflow at the parent head',self.head(self.variant(lambda b:b['ci']['runs'][CI_RUN].update(name='Other'))))
    def test_506_performance(self):
        self.rejects('performance original bytes differ',self.head(self.variant(lambda b:b['performance'].update(sha256='0'*64))))
        self.rejects('performance run is not the U14 full-quality run',self.head(self.variant(lambda b:b['performance'].update(run_id=int(CI_RUN)))))
        self.rejects('performance original path differs',self.head(self.variant(lambda b:b['performance'].update(path=self.b8['performance']['path']))))
    def test_507_sixteenth_path(self):
        self.assertEqual(u3c.ALLOWED_PATHS,u3c.v2().ALLOWED_PATHS);self.assertEqual(len(u3c.ALLOWED_PATHS),8)
        self.assertEqual(u3c.ALLOWED_PATHS_15,tuple(sorted((*u3c.ALLOWED_PATHS,*OLD_CHAIN_PINNED))));self.assertEqual(len(u3c.ALLOWED_PATHS_15),15)
        self.assertEqual(u3c.OTHER_STEP14B,u3c.OUTSIDE_PINS)
        sixteenth='scripts/release/package.py';self.assertIn(sixteenth,u3c.v2().old_chain_pins());self.assertNotIn(sixteenth,u3c.ALLOWED_PATHS_15)
        row={'old_sha256':u3c.v2().old_chain_pins()[sixteenth],'new_sha256':sha(self.raw(sixteenth))}
        self.rejects('old-chain extra allowance differs from the authorized path set',self.extra(self.variant(lambda b:b['old_chain_extra'].__setitem__(sixteenth,row))))
        self.rejects('old-chain extra allowance differs from the authorized path set',self.extra(self.variant(lambda b:b['old_chain_extra'].__setitem__('scripts/release/acceptance.py',row))))
        self.rejects('old-chain extra allowance differs from the authorized path set',self.extra(self.variant(lambda b:b['old_chain_extra'].pop('scripts/release/check.py'))))
        self.rejects('binding-10 key set differs',lambda:u3c.verify_base(self.variant(lambda b:b.pop('old_chain_extra'))))
        m=u3c.nc();fc=m.load('fc_v3_16',m.OLD/'final_candidate.py');pins=u3c.v2().old_chain_pins()
        with Overlay(replace={sixteenth:self.raw(sixteenth)+b'\n'}):
            with self.View(self.map15):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(sixteenth)+'$'):fc.source_pins(pins)
        extra={'bb197e04_sha256':'0'*64,'new_sha256':sha(self.raw('scripts/release/check.py'))}
        self.rejects('moved allowance differs from the authorized path set',self.files(self.variant(lambda b:b['moved_files'].__setitem__('scripts/release/check.py',extra))))
        self.rejects('moved allowance differs from the authorized path set',self.files(self.variant(lambda b:b['moved_files'].pop('docs/release.md'))))
        self.rejects('unchanged allowance differs from the authorized path set',self.files(self.variant(lambda b:b['stay_files'].__setitem__('scripts/release/policy.py',sha(self.raw('scripts/release/policy.py'))))))
        self.rejects('unchanged allowance differs from the authorized path set',self.files(self.variant(lambda b:b['stay_files'].pop('README.md'))))
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),self.full(),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
    def test_508_old_chain_pins_with_the_8_and_the_15_file_views(self):
        m=u3c.nc();fc=m.load('fc_v3_under_test',m.OLD/'final_candidate.py');pins=u3c.v2().old_chain_pins()
        changed=[p for p in u3c.HEAD_FILES if p in pins and p not in u3c.ALLOWED_PATHS];self.assertEqual(sorted(changed),sorted(OLD_CHAIN_PINNED))
        self.assertEqual(sorted(u3c.EXTRA_FILES),sorted(OLD_CHAIN_PINNED));self.assertFalse(set(u3c.OUTSIDE_PINS)&set(pins))
        # The first v3 run stopped here with the 8-file view; the 15-file view passes.
        with self.View(self.map8):
            with self.assertRaisesRegex(ValueError,'current source changed: \\.github/workflows/release-check\\.yml$'):fc.source_pins(pins)
        with self.View(self.map15):fc.source_pins(pins)
        for p in OLD_CHAIN_PINNED:
            self.assertEqual(self.map15[str(ROOT/p)],m.git_blobs(PARENT,[p])[p])
            partial={k:v for k,v in self.map15.items() if k!=str(ROOT/p)}
            with self.View(partial):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(p)+'$'):fc.source_pins(pins)
    def test_509_v2_pins_and_binding_10(self):
        for rel in u3c.HISTORY_V2:
            self.rejects('v2 history file changed: '+re.escape(rel),lambda:u3c.verify_history_v2(self.b),replace={rel:self.raw(rel)+b'\n'})
        with self.assertRaisesRegex(ValueError,'v2 history pin set differs'):u3c.verify_history_v2(self.variant(lambda b:b['history_v2'].popitem()))
        for edit,msg in ((lambda b:b['v2']['entry'].update(sha256='0'*64),'v2 entry/binding differs'),(lambda b:b['v2']['binding'].update(name='binding-08.json'),'v2 entry/binding differs'),
                         (lambda b:b.update(schema=9),'binding schema/repository differs'),(lambda b:b.update(extra=1),'binding-10 key set differs')):
            with self.assertRaisesRegex(ValueError,msg):u3c.verify_base(self.variant(edit))
        cached=u3c._V2
        try:
            u3c._V2=None
            self.rejects('v2 entry bytes differ from the pinned SHA-256',u3c.v2,replace={u3c.V2_ENTRY:self.raw(u3c.V2_ENTRY)+b'\n'})
        finally:u3c._V2=cached
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u3c.verify_base(self.b),replace={u3c.LOOP+u3c.V2_BINDING:self.raw(u3c.LOOP+u3c.V2_BINDING)+b'\n'})
    def test_510_argument_pins_exit_2(self):
        for pin in ('0'*64,u3c.V2_BINDING_SHA256,ENTRY_PIN):
            with self.assertRaisesRegex(ValueError,'binding SHA-256 differs from the binding pinned by this entry'):u3c.load_binding(pin)
        usage=re.escape(u3c.USAGE)
        for argv in ([],['--entry-sha256',ENTRY_PIN],['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN]):self.refused(argv,usage)
        for pin in ('0'*64,u3c.V2_ENTRY_SHA256):self.refused(['--entry-sha256',pin,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs from the SHA-256 of this entry file')
        for pin in ('0'*64,u3c.V2_BINDING_SHA256):self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',pin],'--binding-sha256 differs from the SHA-256 of '+re.escape(u3c.BINDING))
        self.refused(['--entry-sha256',ENTRY_PIN.upper(),'--binding-sha256',BINDING_PIN],'--entry-sha256 must be 64 lowercase hex digits')
        before=own_listing()
        for argv,pattern in (([],usage),(['--entry-sha256',u3c.V2_ENTRY_SHA256,'--binding-sha256',u3c.V2_BINDING_SHA256],'--entry-sha256 differs')):
            r=subprocess.run([sys.executable,'-B',str(u3c.SELF),*argv],cwd=ROOT,capture_output=True,timeout=60)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,b'');self.assertRegex(r.stderr.decode(),'^REFUSED: '+pattern)
        self.assertEqual(own_listing(),before)
    def test_511_old_chain_guard_and_child(self):
        calls=[];nc=u3c.nc()
        def fake_real(argv,**kw):calls.append(argv);return types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
        run=u3c.guarded_run(ENTRY_PIN,BINDING_PIN,OWN,[],fake_real);kw=dict(cwd=ROOT,capture_output=True,timeout=900)
        good=[sys.executable,'-B',str(nc.OLD/'old_predicates.py'),str(OWN/'never.json')];run(good,**kw)
        self.assertEqual(calls[0][2:6],[str(u3c.SELF),'--logical-child',ENTRY_PIN,BINDING_PIN])
        with self.assertRaisesRegex(ValueError,'unexpected old child argv'):run([sys.executable,'-B',str(nc.OLD/'final_candidate.py'),'r.json'],**kw)
        with self.assertRaisesRegex(ValueError,'unexpected child options'):run(good,**{**kw,'timeout':901})
        argv=self.child_argv()
        self.rejects('--entry-sha256 differs from the SHA-256 of this entry file',lambda:u3c.logical_child(self.child_argv(entry=u3c.V2_ENTRY_SHA256)),replace={'docs/release.md':self.raw('docs/release.md')+b'\n'})
        self.rejects('moved file differs from binding/signed head: docs/release.md',lambda:u3c.logical_child(argv),replace={'docs/release.md':self.raw('docs/release.md')+b'\n'})
        with self.assertRaisesRegex(ValueError,'child receipt folder differs'):u3c.logical_child(argv)
        r=subprocess.run([sys.executable,'-B',*self.child_argv(entry='0'*64)],cwd=ROOT,capture_output=True,timeout=60)
        self.assertEqual(r.returncode,1);self.assertIn('--entry-sha256 differs from the SHA-256 of this entry file',r.stderr.decode())
    def test_512_no_statement_contradicts_the_15_file_allowance(self):
        # The detector finds v2's 8-file statements and the first v3 statements (so it can fail).
        self.assertTrue(contradictions(u3c.v2().statements()) and contradictions(u3c.v2().ALLOWANCE_V2))
        self.assertTrue(contradictions(['許すのは8ファイルだけである','採用済みの旧chain（binding-v4）が固定しているものは、そのまま拒否される','Step 14bのほかの10ファイル（x）']))
        scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{},'u14_records':{}}
        out=u3c.u15_scope_v3(scope,self.summary['v2']['u15'],self.summary['u15_a54315f9']);claimed,not_claimed=u3c.statements()
        self.assertEqual(contradictions(out),[])
        self.assertEqual(contradictions([claimed,not_claimed,u3c.ALLOWANCE_V3,u3c.ALLOWANCE_V3_EN,u3c.EXACT_SCOPE_V3,u3c.EXACT_SCOPE_V3_EN,u3c.LAYERING]),[])
        self.assertEqual(contradictions(u3c.v2_summary_for_result(self.summary['v2'])['u15']['old_chain_files']),[])
        self.assertEqual(contradictions(self.summary['u15_a54315f9']),[])
        self.assertEqual(out['u15_version']['head'],HEAD);self.assertEqual(out['u15_version']['scope'],u3c.ALLOWANCE_V3)
        self.assertEqual(out['u15_old_chain']['allowed_paths'],list(u3c.ALLOWED_PATHS_15))
        for p in u3c.ALLOWED_PATHS_15:
            self.assertIn(p,u3c.ALLOWANCE_V3);self.assertIn(p,u3c.ALLOWANCE_V3_EN);self.assertIn(p,not_claimed[0])
        self.assertIn('15ファイル',u3c.ALLOWANCE_V3);self.assertIn('15ファイル',not_claimed[0])
        for p in u3c.EXACT_FILES_ALL:self.assertIn(p,u3c.EXACT_SCOPE_V3)
        for s in (u3c.EXACT_SCOPE_V3,):self.assertIn('a54315f9',s);self.assertIn('U15のレビューと試験',s);self.assertIn('確かめていない',s)
        self.assertIn('a54315f9',u3c.EXACT_SCOPE_V3_EN);self.assertIn("U15's review and tests",u3c.EXACT_SCOPE_V3_EN);self.assertIn('not by this command',u3c.EXACT_SCOPE_V3_EN)
        outside=[s for s in not_claimed if 'scripts/release/acceptance.py' in s and 'tests/release/test_acceptance.py' in s];self.assertEqual(len(outside),1)
        for p in u3c.OUTSIDE_PINS:self.assertIn(p,outside[0])
        for p in u3c.EXTRA_FILES:self.assertNotIn(p,outside[0])
        self.assertIn('a54315f9のCI',outside[0]);self.assertIn('U15のレビュー',outside[0])
        self.assertTrue(any('FR10.1' in s and 'GAP' in s for s in not_claimed));self.assertTrue(any('中身が正しいこと' in s for s in not_claimed))
        self.assertNotIn(u3c.v2().CLAIMED_V2[1],claimed)
    def test_514_seven_old_chain_files(self):
        self.assertEqual(sorted(self.summary['u15_a54315f9']['old_chain_extra']),sorted(OLD_CHAIN_PINNED))
        pins=u3c.v2().old_chain_pins()
        for p in OLD_CHAIN_PINNED:
            row=self.summary['u15_a54315f9']['old_chain_extra'][p]
            self.assertEqual(row['old_sha256'],pins[p]);self.assertEqual(row['a54315f9_sha256'],sha(self.raw(p)));self.assertEqual(row['scope'],u3c.EXACT_SCOPE_V3)
            msg='old-chain extra file differs from binding/signed head: '+re.escape(p)
            self.rejects(msg,self.extra(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.extra(),replace={p:self.old7[p]})
            self.rejects('missing/unreadable input: '+re.escape(p),self.extra(),missing=[p])
            self.rejects(msg,self.extra(self.variant(lambda b,p=p:b['old_chain_extra'][p].update(new_sha256='0'*64))))
            self.rejects('old-chain extra old pin differs: '+re.escape(p),self.extra(self.variant(lambda b,p=p:b['old_chain_extra'][p].update(old_sha256='0'*64))))
            self.rejects('old-chain extra old pin differs: '+re.escape(p),self.extra(self.variant(lambda b,p=p:b['old_chain_extra'][p].update(old_sha256=sha(self.raw(p))))))
            self.rejects('old-chain extra entry differs: '+re.escape(p),self.extra(self.variant(lambda b,p=p:b['old_chain_extra'][p].update(extra=1))))
        self.rejects('old-chain extra file differs from binding/signed head: scripts/release/check.py',self.full(),replace={'scripts/release/check.py':self.raw('scripts/release/check.py')+b' '})
        self.rejects('old chain binding-v4 differs',self.extra(),replace={u3c.v2().OLD_BINDING_V4:self.raw(u3c.v2().OLD_BINDING_V4)+b' '})
    def test_513_claim_scope_layering(self):
        scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{},'u14_records':{}}
        out=u3c.u15_scope_v3(scope,self.summary['v2']['u15'],self.summary['u15_a54315f9']);note=out['u15_a54315f9']
        self.assertEqual((note['head'],note['parent'],note['moved'],note['stay']),(HEAD,PARENT,list(u3c.MOVED),list(u3c.STAY)));self.assertEqual(note['layering'],u3c.LAYERING)
        self.assertEqual(out['u15_old_chain']['exact_bytes_scope'],u3c.EXACT_SCOPE_V3)
        with self.assertRaisesRegex(ValueError,'U14 claim scope missing'):u3c.u15_scope_v3({k:v for k,v in scope.items() if k!='u14_records'},self.summary['v2']['u15'],self.summary['u15_a54315f9'])

def main():
    # The v2 suite replays the bb197e04 working tree: the 12 Step 14b files at their bb197e04 blobs (harness only).
    world=u3c.nc().git_blobs(PARENT,list(u3c.HEAD_FILES))
    with Overlay(replace=world):code=v2t.main()
    fourth=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(U15A54315f9))
    print(f'regressions: v2 suite (132) exit {code} under the bb197e04 working-tree view; binding-10 {fourth.testsRun}/{V3_TEST_COUNT}, skipped {len(fourth.skipped)}; total {V2_SUITE_COUNT+fourth.testsRun} / expected {V2_SUITE_COUNT+V3_TEST_COUNT}')
    ok=code==0 and fourth.wasSuccessful() and fourth.testsRun==V3_TEST_COUNT and not fourth.skipped
    return 0 if ok else 1

if __name__=='__main__':sys.exit(main())
