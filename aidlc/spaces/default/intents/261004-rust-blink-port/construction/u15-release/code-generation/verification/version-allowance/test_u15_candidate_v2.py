"""Regressions for u15_candidate_v2.py (binding-09).

Runs, in this order:
  1. the unchanged binding-08 regressions (test_u15_candidate.py, pinned by
     SHA-256): its main() runs the U14 suite (93) under the 3-file version view
     and the 23 U15 cases, 116 in all, exactly as before;
  2. the binding-09 cases below (test_400..test_415):positive control, the
     binding-08 entry's old-chain stop on Cargo.toml, the Cargo.toml
     version-only proof (non-version keys, tables and lines, other version
     values, dependency paths/keys), the four exact-bytes files (differing from
     the bb197e04 blob or the old pins), the fixed 8-path set (a 9th path in the
     binding, another compiled source, another old-chain pin), the binding-09
     base and binding-08 pins, the binding-08 history, the command line (exit
     2, also as real processes), the old-chain guard, the --logical-child
     branch and the claim scope; test_415 (review-01) fails when any v2
     statement contradicts the 8-file allowance (an inherited 3-file sentence).
No real file is modified (read-only overlay or in-memory binding copies). The
only child processes are refused command lines, which write nothing.
Exit 0 only when every case ran (116 + 16), none was skipped and all passed.
"""
import contextlib,copy,hashlib,importlib.util,io,json,re,subprocess,sys,types,unittest
from pathlib import Path

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('u15_candidate_v2_under_test',OWN/'u15_candidate_v2.py')
u2c=importlib.util.module_from_spec(spec);spec.loader.exec_module(u2c)
ROOT=u2c.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
V1_TESTS=OWN/'test_u15_candidate.py'
V1_TESTS_SHA256='6573bc6c158199bd1466aa076bdee307e9d82da7503a6cb3d48403572f37e10a'
V1_SUITE_COUNT=116
V2_TEST_COUNT=16
if sha(V1_TESTS.read_bytes())!=V1_TESTS_SHA256:raise SystemExit('binding-08 regression file differs from the pinned SHA-256')
if sha((ROOT/u2c.V1_ENTRY).read_bytes())!=u2c.V1_ENTRY_SHA256:raise SystemExit('binding-08 entry differs from the pinned SHA-256')
spec=importlib.util.spec_from_file_location('u15_v1_regressions',V1_TESTS)
v1t=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1t)
Overlay=v1t.Overlay
TOML='Cargo.toml';EXACT=u2c.EXACT_FILES
SELF_REL=str(u2c.SELF.relative_to(ROOT));BINDING_REL=u2c.LOOP+u2c.BINDING;V1_BINDING_REL=u2c.LOOP+u2c.V1_BINDING
PRIOR='57a8c96f610d6e02234354e5e4fb5cac068d5036'
OTHER_SOURCE='packages/paludarium-wasm/index.mjs';OTHER_PIN='scripts/release/check.py'
ENTRY_PIN=sha(u2c.SELF.read_bytes());BINDING_PIN=u2c.BINDING_SHA256

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def own_listing():return sorted(p.name for p in OWN.iterdir())
def swap(raw,old,new,count=1):
    assert raw.count(old)>=count,old;return raw.replace(old,new,count)

class U15OldChainFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=u2c.load_binding(BINDING_PIN)
        cls.b8,cls.b7,cls.b2=u2c.verify_base(cls.b)
        cls.summary,cls.mapping=u2c.verify(cls.b,reuse_compat=False)
        cls.View=u2c.view_class();m=u2c.nc()
        names=[TOML,*EXACT];cls.old=m.git_blobs(PRIOR,names);cls.new={p:(ROOT/p).read_bytes() for p in names}
        cls.map8={k:v for k,v in cls.mapping.items() if k in {str(ROOT/p) for p in u2c.ALLOWED_PATHS}}
        cls.fc=m.load('fc_v2_under_test',m.OLD/'final_candidate.py');cls.pins=u2c.old_chain_pins()
    def raw(self,rel):return (ROOT/rel).read_bytes()
    def variant(self,edit):
        b=copy.deepcopy(self.b);edit(b);return b
    def rejects(self,pattern,fn,**overlay):
        with Overlay(**overlay):
            with self.assertRaisesRegex(ValueError,pattern):fn()
    def full(self,b=None):return lambda:u2c.verify(b or self.b,reuse_compat=False)
    def files(self,b=None):return lambda:u2c.verify_old_chain_files(b or self.b,self.b2,self.b8['head'])
    def toml_rejects(self,pattern,new,old=None):
        with self.assertRaisesRegex(ValueError,pattern):u2c.cargo_toml_diff(self.old[TOML] if old is None else old,new)
    def refused(self,argv,pattern,**overlay):
        before=run_dirs();err=io.StringIO()
        with Overlay(**overlay),contextlib.redirect_stderr(err):code=u2c.main([str(u2c.SELF),*argv])
        self.assertEqual(code,2);self.assertRegex(err.getvalue(),'^REFUSED: '+pattern);self.assertEqual(run_dirs(),before)
    def child_argv(self,entry=None,pin=None):
        return [str(u2c.SELF),'--logical-child',ENTRY_PIN if entry is None else entry,BINDING_PIN if pin is None else pin,str(OWN/'run-never'),str(u2c.nc().OLD/'old_predicates.py'),'r.json']

    def test_400_positive_control(self):
        u=self.summary['u15'];self.assertEqual(u['logical_view_paths'],list(u2c.ALLOWED_PATHS));self.assertEqual(len(u2c.ALLOWED_PATHS),8)
        f=u['old_chain_files'];self.assertEqual(f[TOML]['diff']['changed_lines'],12);self.assertEqual(f[TOML]['kind'],'version-only')
        for p in EXACT:self.assertEqual((f[p]['kind'],f[p]['scope']),('exact-bytes',u2c.EXACT_SCOPE))
        for p in (TOML,*EXACT):
            shown=self.mapping[str(ROOT/p)];self.assertEqual(shown,self.old[p]);self.assertNotEqual(shown,self.raw(p));self.assertEqual(sha(shown),self.pins[p])
        self.assertEqual(sorted(u['version_files']),sorted(u2c.v1().VERSION_FILES));self.assertEqual(sorted(u['history_v1']),sorted(u2c.HISTORY_V1))
        with self.View(self.mapping):
            with open(ROOT/'docs/release.md','rb') as f2:shown=f2.read()
        self.assertEqual(shown,self.old['docs/release.md'])
    def test_401_binding_08_entry_stops_on_cargo_toml_this_entry_does_not(self):
        three={k:v for k,v in self.map8.items() if k in {str(ROOT/p) for p in u2c.v1().VERSION_FILES}}
        with self.View(three):
            with self.assertRaisesRegex(ValueError,'current source changed: Cargo.toml$'):self.fc.source_pins(self.pins)
        with self.View(self.map8):self.fc.source_pins(self.pins)
        for p in (TOML,*EXACT):
            partial={k:v for k,v in self.map8.items() if k!=str(ROOT/p)}
            with self.View(partial):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(p)+'$'):self.fc.source_pins(self.pins)
    def test_402_cargo_toml_non_version_key_changed(self):
        new=self.new[TOML];beyond='Cargo.toml differs beyond the version values'
        self.toml_rejects(beyond+': workspace',swap(new,b'edition = "2024"',b'edition = "2021"'))
        self.toml_rejects(beyond+': workspace',swap(new,b'license = "Apache-2.0"',b'license = "MIT"'))
        self.toml_rejects(beyond+': workspace',swap(new,b'unsafe_op_in_unsafe_fn = "deny"',b'unsafe_op_in_unsafe_fn = "warn"'))
        self.toml_rejects(beyond+': workspace',swap(new,b'[workspace.lints.rust]',b'extra-crate = "1"\n\n[workspace.lints.rust]'))
        self.toml_rejects(beyond+': profile',swap(new,b'debug = "line-tables-only"',b'debug = true'))
        self.toml_rejects(beyond+': package',new+b'\n[package]\nname = "x"\n')
    def test_403_cargo_toml_other_version_values(self):
        new=self.new[TOML]
        for other in (b'0.1.1',b'0.0.0',b'1.0.0'):
            self.toml_rejects('workspace.package.version is not 0.0.0 -> 0.1.0',swap(new,b'[workspace.package]\nversion = "0.1.0"',b'[workspace.package]\nversion = "'+other+b'"'))
            self.toml_rejects('internal dependency version is not 0.0.0 -> 0.1.0: paludarium-jit',swap(new,b'path = "crates/paludarium-jit", version = "0.1.0"',b'path = "crates/paludarium-jit", version = "'+other+b'"'))
        self.toml_rejects('workspace.package.version is not 0.0.0 -> 0.1.0',new,old=new)
        self.toml_rejects('internal dependency version is not 0.0.0 -> 0.1.0: paludarium-types',new,old=swap(self.old[TOML],b'path = "crates/paludarium-types", version = "0.0.0"',b'path = "crates/paludarium-types", version = "0.0.1"'))
    def test_404_cargo_toml_dependency_path_changed(self):
        new=self.new[TOML]
        self.toml_rejects('Cargo.toml differs beyond the version values: workspace',swap(new,b'path = "crates/paludarium-jit"',b'path = "crates/paludarium-jit2"'))
        self.toml_rejects('Cargo.toml differs beyond the version values: workspace',swap(new,b'path = "crates/paludarium-jit", version = "0.1.0"',b'path = "crates/paludarium-jit", version = "0.1.0", features = ["x"]'))
        self.toml_rejects('internal dependency differs: paludarium-jit',new,old=swap(self.old[TOML],b'path = "crates/paludarium-jit"',b'path = "crates/other"'))
        self.toml_rejects('internal dependency differs: paludarium-jit',new,old=swap(self.old[TOML],b'paludarium-jit = { path = "crates/paludarium-jit", version = "0.0.0" }\n',b''))
    def test_405_cargo_toml_lines(self):
        new=self.new[TOML]
        self.toml_rejects('Cargo.toml line differs beyond a version value',swap(new,b'paludarium-jit = { path = "crates/paludarium-jit", version = "0.1.0" }',b'paludarium-jit = {path = "crates/paludarium-jit", version = "0.1.0"}'))
        self.toml_rejects('Cargo.toml changed line count differs',swap(new,b'edition = "2024"',b'edition  =  "2024"'))
        self.toml_rejects('Cargo.toml line count differs',new+b'\n')
        self.toml_rejects('Cargo.toml does not parse',new+b'[[x\n')
        self.toml_rejects('Cargo.toml does not parse',new+b'\xff')
    def test_406_exact_files_differ_from_signed_head(self):
        for p in (TOML,*EXACT):
            msg='old-chain file differs from binding/signed head: '+re.escape(p)
            self.rejects(msg,self.files(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.files(),replace={p:self.old[p]})
            self.rejects('missing/unreadable input: '+re.escape(p),self.files(),missing=[p])
            self.rejects(msg,self.files(self.variant(lambda b,p=p:b['old_chain_files'][p].update(new_sha256='0'*64))))
        self.rejects('old-chain file differs from binding/signed head: README.md',self.full(),replace={'README.md':self.raw('README.md')+b' '})
    def test_407_old_pins(self):
        for p in (TOML,*EXACT):
            e=self.b['old_chain_files'][p]
            self.rejects('old-chain old pin differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['old_chain_files'][p].update(old_sha256='0'*64))))
            self.rejects('old-chain old pin differs: '+re.escape(p),self.files(self.variant(lambda b,p=p,e=e:b['old_chain_files'][p].update(old_sha256=e['new_sha256']))))
            self.rejects('old-chain entry differs: '+re.escape(p),self.files(self.variant(lambda b,p=p:b['old_chain_files'][p].update(extra=1))))
        self.rejects('old-chain entry differs: README.md',self.files(self.variant(lambda b:b['old_chain_files']['README.md'].update(kind='version-only'))))
        self.rejects('old-chain entry differs: Cargo.toml',self.files(self.variant(lambda b:b['old_chain_files'][TOML].update(kind='exact-bytes'))))
        self.rejects('old chain binding-v4 differs',self.files(),replace={u2c.OLD_BINDING_V4:self.raw(u2c.OLD_BINDING_V4)+b' '})
    def test_408_fixed_path_set_and_a_ninth_path(self):
        self.assertEqual(u2c.ALLOWED_PATHS,tuple(sorted(('Cargo.lock','fuzz/Cargo.lock','packages/paludarium-wasm/package.json','Cargo.toml','README.md','docs/release.md','tests/release/test_policy.py','tests/release/test_package.py'))))
        message='old-chain allowance differs from the authorized path set'
        extra={'kind':'exact-bytes','old_sha256':self.pins[OTHER_PIN],'new_sha256':sha(self.raw(OTHER_PIN))}
        self.rejects(message,self.files(self.variant(lambda b:b['old_chain_files'].__setitem__(OTHER_PIN,extra))))
        self.rejects(message,self.files(self.variant(lambda b:b['old_chain_files'].__setitem__('scripts/release/acceptance.py',extra))))
        self.rejects(message,self.files(self.variant(lambda b:b['old_chain_files'].pop('docs/release.md'))))
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),self.full(),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
        with Overlay(replace={OTHER_PIN:self.raw(OTHER_PIN)+b'\n'}):
            with self.View(self.map8):
                with self.assertRaisesRegex(ValueError,'current source changed: '+re.escape(OTHER_PIN)+'$'):self.fc.source_pins(self.pins)
    def test_409_base_v1_and_binding_keys(self):
        V=u2c.v1()
        for edit,msg in ((lambda b:b['base']['entry'].update(sha256='0'*64),'base entry/binding differs'),(lambda b:b['base']['binding'].update(name='binding-06.json'),'base entry/binding differs'),
                         (lambda b:b['v1']['entry'].update(sha256='0'*64),'binding-08 entry/binding differs'),(lambda b:b['v1']['binding'].update(sha256=V.U14_BINDING_SHA256),'binding-08 entry/binding differs'),
                         (lambda b:b.update(schema=8),'binding schema/repository differs'),(lambda b:b.update(head=PRIOR),'binding-09 key set differs'),(lambda b:b.pop('approval'),'binding-09 key set differs')):
            with self.assertRaisesRegex(ValueError,msg):u2c.verify_base(self.variant(edit))
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u2c.verify_base(self.b),replace={V1_BINDING_REL:self.raw(V1_BINDING_REL)+b'\n'})
        cached=u2c._V1
        try:
            u2c._V1=None
            self.rejects('binding-08 entry bytes differ from the pinned SHA-256',u2c.v1,replace={u2c.V1_ENTRY:self.raw(u2c.V1_ENTRY)+b'\n'})
            u2c._V1=None
            self.rejects('U14 entry bytes differ from the pinned SHA-256',u2c.nc,replace={V.U14_ENTRY:self.raw(V.U14_ENTRY)+b'\n'})
        finally:u2c._V1=cached
    def test_410_binding_08_history(self):
        for rel in u2c.HISTORY_V1:
            self.rejects('binding-08 history file changed: '+re.escape(rel),lambda:u2c.verify_history_v1(self.b),replace={rel:self.raw(rel)+b'\n'})
        for edit in (lambda b:b['history_v1'].popitem(),lambda b:b['history_v1'].__setitem__(u2c.V1_ENTRY,'0'*64)):
            with self.assertRaisesRegex(ValueError,'binding-08 history pin set differs'):u2c.verify_history_v1(self.variant(edit))
        rel=u2c.LOOP+'test_u15_candidate.py'
        self.rejects('binding-08 history file changed: '+re.escape(rel),self.full(),replace={rel:self.raw(rel)+b'\n'})
    def test_411_binding_pin_and_command_line_exit_2(self):
        for pin in ('0'*64,u2c.V1_BINDING_SHA256,ENTRY_PIN):
            with self.assertRaisesRegex(ValueError,'binding SHA-256 differs from the binding pinned by this entry'):u2c.load_binding(pin)
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u2c.load_binding(BINDING_PIN),replace={BINDING_REL:self.raw(BINDING_REL)+b'\n'})
        usage=re.escape(u2c.USAGE)
        for argv in ([],['--entry-sha256',ENTRY_PIN],['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN],['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN,'extra']):
            self.refused(argv,usage)
        self.refused(['--entry-sha256',ENTRY_PIN.upper(),'--binding-sha256',BINDING_PIN],'--entry-sha256 must be 64 lowercase hex digits')
        for pin in ('0'*64,u2c.V1_ENTRY_SHA256):self.refused(['--entry-sha256',pin,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs from the SHA-256 of this entry file')
        for pin in ('0'*64,u2c.V1_BINDING_SHA256):self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',pin],'--binding-sha256 differs from the SHA-256 of '+re.escape(u2c.BINDING))
        changed=self.raw(BINDING_REL)+b'\n'
        self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',sha(changed)],'--binding-sha256 differs from the binding pinned by this entry',replace={BINDING_REL:changed})
        before=own_listing()
        for argv,pattern in (([],usage),(['--entry-sha256',u2c.V1_ENTRY_SHA256,'--binding-sha256',u2c.V1_BINDING_SHA256],'--entry-sha256 differs'),
                             (['--entry-sha256',ENTRY_PIN,'--binding-sha256','0'*64],'--binding-sha256 differs')):
            r=subprocess.run([sys.executable,'-B',str(u2c.SELF),*argv],cwd=ROOT,capture_output=True,timeout=60)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,b'');self.assertRegex(r.stderr.decode(),'^REFUSED: '+pattern)
        r=subprocess.run([sys.executable,'-B',*self.child_argv(entry='0'*64)],cwd=ROOT,capture_output=True,timeout=60)
        self.assertEqual(r.returncode,1);self.assertIn('--entry-sha256 differs from the SHA-256 of this entry file',r.stderr.decode())
        self.assertEqual(own_listing(),before)
    def test_412_old_chain_guard_and_child_boundaries(self):
        calls=[];nc=u2c.nc()
        def fake_real(argv,**kw):calls.append((argv,kw));return types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
        run=u2c.guarded_run(ENTRY_PIN,BINDING_PIN,OWN,[],fake_real)
        kw=dict(cwd=ROOT,capture_output=True,timeout=900);good=[sys.executable,'-B',str(nc.OLD/'old_predicates.py'),str(OWN/'never-written.json')]
        run(good,**kw);self.assertEqual(calls[0][0][2:6],[str(u2c.SELF),'--logical-child',ENTRY_PIN,BINDING_PIN])
        for argv in ([sys.executable,'-B',str(nc.OLD/'final_candidate.py'),'r.json'],[sys.executable,'-B',str(OWN/'old_predicates.py'),'r.json'],good+['x']):
            with self.assertRaisesRegex(ValueError,'unexpected old child argv'):run(argv,**kw)
        with self.assertRaisesRegex(ValueError,'unexpected child options'):run(good,**{**kw,'timeout':901})
        self.assertEqual(len(calls),1)
        argv=self.child_argv();saved=(list(sys.argv),list(sys.path))
        with self.assertRaisesRegex(ValueError,'internal child argv differs'):u2c.logical_child(argv[:-1])
        for entry in ('0'*64,u2c.V1_ENTRY_SHA256):
            self.rejects('--entry-sha256 differs from the SHA-256 of this entry file',lambda e=entry:u2c.logical_child(self.child_argv(entry=e)),replace={'README.md':self.raw('README.md')+b'\n'})
        self.rejects('--binding-sha256 differs from the SHA-256 of '+re.escape(u2c.BINDING),lambda:u2c.logical_child(self.child_argv(pin=u2c.V1_BINDING_SHA256)),replace={'README.md':self.raw('README.md')+b'\n'})
        with self.assertRaisesRegex(ValueError,'validator outside the reused old set'):u2c.logical_child(argv[:5]+[str(OWN/'old_predicates.py'),'r.json'])
        with self.assertRaisesRegex(ValueError,'child receipt folder differs'):u2c.logical_child(argv)
        self.assertEqual((sys.argv,sys.path),saved)
    def test_413_logical_child_rejects_changed_inputs(self):
        argv=self.child_argv()
        self.rejects('old-chain file differs from binding/signed head: docs/release.md',lambda:u2c.logical_child(argv),replace={'docs/release.md':self.raw('docs/release.md')+b'\n'})
        self.rejects('version file differs from binding/signed head: Cargo.lock',lambda:u2c.logical_child(argv),replace={'Cargo.lock':self.raw('Cargo.lock')+b'\n'})
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),lambda:u2c.logical_child(argv),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
    def test_414_claim_scope(self):
        scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{},'u14_records':{}}
        out=u2c.u15_scope_v2(scope,self.summary['u15'])
        self.assertIn('u15_version',out);note=out['u15_old_chain']
        self.assertEqual(note['allowed_paths'],list(u2c.ALLOWED_PATHS));self.assertEqual(note['exact_bytes_scope'],u2c.EXACT_SCOPE)
        self.assertIn('U15のレビューと試験',u2c.EXACT_SCOPE);self.assertIn('bb197e04',u2c.EXACT_SCOPE)
        self.assertTrue(any('内容が正しいこと' in s for s in note['not_claimed']))
        with self.assertRaisesRegex(ValueError,'U14 claim scope missing'):u2c.u15_scope_v2({k:v for k,v in scope.items() if k!='u14_records'},self.summary['u15'])
    def test_415_no_statement_contradicts_the_8_file_allowance(self):
        """review-01 M1/m2/m3: no inherited 3-file statement survives in v2's result statements or claim scope."""
        def strings(x):
            if isinstance(x,str):yield x
            elif isinstance(x,dict):
                for k,v in x.items():yield from strings(k);yield from strings(v)
            elif isinstance(x,(list,tuple)):
                for v in x:yield from strings(v)
        forbidden=re.compile(r'3ファイル以外の差|3ファイルで許す|それらを許さない|(だけ|のみ)を?3ファイル')
        def contradictions(x):return [s for s in strings(x) if forbidden.search(s)]
        scope={'old_current_semantics':{},'performance_1ceae86c':{},'u11_57a8c96f':{},'u14_records':{}}
        # The detector finds binding-08's own 3-file statements (so it can fail).
        self.assertTrue(contradictions(u2c.v1().u15_scope(scope,self.summary['u15'])['u15_version']))
        self.assertTrue(contradictions(list(u2c.v1().NOT_CLAIMED)))
        out=u2c.u15_scope_v2(scope,self.summary['u15']);claimed,not_claimed=u2c.statements()
        self.assertEqual(contradictions(out),[]);self.assertEqual(contradictions([claimed,not_claimed,u2c.ALLOWANCE_V2]),[])
        self.assertEqual(out['u15_version']['scope'],u2c.ALLOWANCE_V2);self.assertEqual(out['u15_version']['not_claimed'],not_claimed)
        for p in u2c.ALLOWED_PATHS:
            self.assertIn(p,u2c.ALLOWANCE_V2);self.assertIn(p,not_claimed[0])
        self.assertIn('8ファイル',not_claimed[0]);self.assertIn('8ファイル',u2c.ALLOWANCE_V2)
        unpinned=[s for s in not_claimed if 'scripts/release/acceptance.py' in s]
        self.assertEqual(len(unpinned),1)
        for p in ('scripts/release/acceptance.py','tests/release/test_acceptance.py','.github/workflows/u15-acceptance.yml'):self.assertIn(p,unpinned[0])
        self.assertTrue(set(u2c.UNPINNED_ADDED)<=set(u2c.v1().HEAD_FILES) and not set(u2c.UNPINNED_ADDED)&set(u2c.ALLOWED_PATHS))
        for h in ('binding-v4','57a8c96f','1ceae86c','be45'):self.assertIn(h,u2c.CLAIMED_V2[1])
        self.assertEqual(not_claimed[len(u2c.NOT_CLAIMED_V2):],list(u2c.v1().NOT_CLAIMED[1:]))

def main():
    code=v1t.main()
    fourth=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(U15OldChainFiles))
    print(f'regressions: binding-08 suite (116 = U14 93 + U15 23) exit {code}; binding-09 {fourth.testsRun}/{V2_TEST_COUNT}, skipped {len(fourth.skipped)}; total {V1_SUITE_COUNT+fourth.testsRun} / expected {V1_SUITE_COUNT+V2_TEST_COUNT}')
    ok=code==0 and fourth.wasSuccessful() and fourth.testsRun==V2_TEST_COUNT and not fourth.skipped
    return 0 if ok else 1

if __name__=='__main__':sys.exit(main())
