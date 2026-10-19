"""Regressions for u15_candidate.py (U15 release version allowance, binding-08).

Runs, in this order:
  1. the unchanged U14 Step46 regressions (test_u14_candidate_v2.py, 93 cases =
     U11 suite 73 + U14 20, pinned by SHA-256) with only the three version files
     (Cargo.lock, fuzz/Cargo.lock, packages/paludarium-wasm/package.json) shown
     at their old bytes through the unchanged historical_child.View, exactly as
     u15_candidate.py shows them to U14, U11, U2, U1 and the old chain;
  2. the U15 cases below (test_300..test_322): positive control, the expected
     stop of the U14 entry alone, the version-only proof (external crates,
     checksums, dependencies, non-workspace packages, other versions, lock
     structure, package.json keys/bytes), the bb197e04 and old pins, the fixed
     path set (a 4th path, including the old chain's Cargo.toml pin), the signed
     head, the stored CI records (failure, wrong head, job lists), the
     performance original, the base/history/spec pins, the command line (exit 2),
     real processes, the old-chain guard, the --logical-child branch and the
     claim scope.
No real file is modified: changed or missing bytes are presented through the
U1 regressions' read-only overlay (builtins.open/io.open) or in-memory binding
copies. The only child processes are refused command lines, which stop before
any check and write nothing.
Exit 0 only when every case ran (93 + 23), none was skipped and all passed.
"""
import contextlib,copy,hashlib,importlib.util,io,json,re,subprocess,sys,tomllib,types,unittest
from pathlib import Path

OWN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('u15_candidate_under_test',OWN/'u15_candidate.py')
u15c=importlib.util.module_from_spec(spec);spec.loader.exec_module(u15c)
ROOT=u15c.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
U14_TESTS=ROOT/(u15c.U14_LOOP+'test_u14_candidate_v2.py')
U14_TESTS_SHA256='aab2a01a68c4afc23ef8a3d7c754e3971468e572347c70a1d59f204e8884bf80'
U14_SUITE_COUNT=93
U15_TEST_COUNT=23
if sha(U14_TESTS.read_bytes())!=U14_TESTS_SHA256:raise SystemExit('U14 regression file differs from the pinned SHA-256')
if sha((ROOT/u15c.U14_ENTRY).read_bytes())!=u15c.U14_ENTRY_SHA256:raise SystemExit('U14 entry differs from the pinned SHA-256')
spec=importlib.util.spec_from_file_location('u14_regressions',U14_TESTS)
u14t=importlib.util.module_from_spec(spec);spec.loader.exec_module(u14t)
Overlay=u14t.Overlay
LOCK,FUZZ,PKG=u15c.CARGO_LOCK,u15c.FUZZ_LOCK,u15c.PACKAGE_JSON
SELF_REL=str(u15c.SELF.relative_to(ROOT));BINDING_REL=u15c.LOOP+u15c.BINDING
U14_BINDING_REL=u15c.U14_LOOP+u15c.U14_BINDING
PRIOR=u15c.PRIOR_HEAD;JIT_HEAD='1ceae86ce303a1019e97ac7d162ce0efa9fadd50';STEP30_HEAD='2b8723ab028ba6b037df08d0cfb51073a660f8cc'
OTHER_SOURCE='packages/paludarium-wasm/index.mjs'
ENTRY_PIN=sha(u15c.SELF.read_bytes());BINDING_PIN=u15c.BINDING_SHA256
CI_RUN='39089163556';PERF_RUN='39089194062'

def run_dirs():return {p.name for p in OWN.glob('run-*')}
def own_listing():return sorted(p.name for p in OWN.iterdir())
def swap(raw,old,new,count=1):
    assert raw.count(old)>=count,old;return raw.replace(old,new,count)

class U15Version(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=u15c.load_binding(BINDING_PIN)
        cls.b7,cls.b5,cls.b2=u15c.verify_base(cls.b)
        cls.summary,cls.mapping=u15c.verify(cls.b,reuse_compat=False)
        cls.View=u15c.view_class();m=u15c.nc()
        cls.old=m.git_blobs(PRIOR,list(u15c.VERSION_FILES));cls.new={p:(ROOT/p).read_bytes() for p in u15c.VERSION_FILES}
        cls.version_map={str(ROOT/p):cls.old[p] for p in u15c.VERSION_FILES}
    def raw(self,rel):return (ROOT/rel).read_bytes()
    def variant(self,edit):
        b=copy.deepcopy(self.b);edit(b);return b
    def rejects(self,pattern,fn,**overlay):
        with Overlay(**overlay):
            with self.assertRaisesRegex(ValueError,pattern):fn()
    def full(self,b=None):return lambda:u15c.verify(b or self.b,reuse_compat=False)
    def versions(self,b=None):return lambda:u15c.verify_versions(b or self.b,self.b2,self.b['head'])
    def head(self,b=None):return lambda:u15c.verify_head(b or self.b,self.b7,self.b2)
    def diff_rejects(self,pattern,rel,new,old=None):
        with self.assertRaisesRegex(ValueError,pattern):u15c.version_only_diff(rel,self.old[rel] if old is None else old,new)
    def ci_variant(self,edit_ci=None,edit_jobs=None,edit_binding=None,rebind=True):
        """Edited CI JSON presented through the overlay; with rebind the binding variant carries the new SHA-256."""
        b=copy.deepcopy(self.b);replace={}
        for key,edit in (('ci',edit_ci),('ci_jobs',edit_jobs)):
            if edit is None:continue
            doc=json.loads(self.raw(b[key]['path']));edit(doc);raw=json.dumps(doc,indent=2).encode();replace[b[key]['path']]=raw
            if rebind:b[key]['sha256']=sha(raw)
        if edit_binding:edit_binding(b)
        return b,replace
    def refused(self,argv,pattern,**overlay):
        """main() refuses the command line with exit 2 before any check and writes nothing."""
        before=run_dirs();err=io.StringIO()
        with Overlay(**overlay),contextlib.redirect_stderr(err):code=u15c.main([str(u15c.SELF),*argv])
        self.assertEqual(code,2);self.assertRegex(err.getvalue(),'^REFUSED: '+pattern);self.assertEqual(run_dirs(),before)
    def child_argv(self,entry=None,pin=None):
        return [str(u15c.SELF),'--logical-child',ENTRY_PIN if entry is None else entry,BINDING_PIN if pin is None else pin,str(OWN/'run-never'),str(u15c.nc().OLD/'old_predicates.py'),'r.json']

    def test_300_positive_control(self):
        u=self.summary['u15'];self.assertEqual(u['head']['head'],self.b['head']);self.assertEqual(u['head']['parent'],PRIOR)
        self.assertEqual(u['logical_view_paths'],sorted(u15c.VERSION_FILES));self.assertEqual(u['head']['changed_paths'],sorted(u15c.HEAD_FILES))
        self.assertEqual(u['head']['jobs'],{'39089163510':1,'39089163556':23,'39089194062':34,'39089195709':29,'39089197410':29,'39089199122':13,'39089200731':7})
        v=u['version_files']
        self.assertEqual(v[LOCK]['diff']['changed_crates'],sorted(u15c.WORKSPACE_CRATES));self.assertEqual(v[LOCK]['diff']['changed_lines'],13)
        self.assertEqual(v[FUZZ]['diff']['changed_crates'],sorted(u15c.FUZZ_CRATES));self.assertEqual(v[FUZZ]['diff']['changed_lines'],9)
        self.assertEqual(v[PKG]['diff']['changed_key'],'version')
        self.assertEqual({p:v[p]['receipt_equals_old'] for p in v},{LOCK:True,FUZZ:True,PKG:False})
        inner=self.summary['u14']['u11']['u2']['u1'];self.assertEqual(inner['compiled_sources'],223)
        for p in u15c.VERSION_FILES:
            shown=self.mapping[str(ROOT/p)];self.assertEqual(shown,self.old[p]);self.assertNotEqual(shown,self.raw(p))
            self.assertEqual(sha(shown),self.b['version_files'][p]['old_sha256']);self.assertEqual(sha(self.raw(p)),self.b['version_files'][p]['new_sha256'])
        with self.View(self.mapping):
            with open(ROOT/LOCK,'rb') as f:shown=f.read()
            with open(ROOT/'Cargo.toml','rb') as f:toml=f.read()
        self.assertEqual(shown,self.old[LOCK]);self.assertEqual(toml,self.raw('Cargo.toml'))
    def test_301_u14_entry_alone_stops_on_the_version_files(self):
        u14=u15c.u14()
        with self.assertRaisesRegex(ValueError,'compiled source changed: '+re.escape(LOCK)+'$'):u14.verify(self.b7,reuse_compat=False)
        with Overlay(replace={LOCK:self.old[LOCK]}):
            with self.assertRaisesRegex(ValueError,'compiled source changed: '+re.escape(FUZZ)):u14.verify(self.b7,reuse_compat=False)
        with Overlay(replace={LOCK:self.old[LOCK],FUZZ:self.old[FUZZ]}):
            with self.assertRaisesRegex(ValueError,'compiled source changed: '+re.escape(PKG)):u14.verify(self.b7,reuse_compat=False)
        with Overlay(replace=dict(self.old)):u14.verify(self.b7,reuse_compat=False)
    def external(self,rel,need_deps=False):
        for p in tomllib.loads(self.new[rel].decode())['package']:
            if 'source' in p and (not need_deps or p.get('dependencies')):return p['name'],p['version']
        self.fail('no external package')
    def test_302_external_crate_version_changed(self):
        for rel in (LOCK,FUZZ):
            name,version=self.external(rel)
            block=('name = "%s"\nversion = "%s"'%(name,version)).encode()
            self.diff_rejects('lock package differs outside the workspace version allowance: '+re.escape(rel)+': '+re.escape(name),rel,swap(self.new[rel],block,block[:-1]+b'9"'))
    def test_303_checksum_changed(self):
        for rel in (LOCK,FUZZ):
            raw=self.new[rel];i=raw.index(b'checksum = "')+len(b'checksum = "');flipped=b'0' if raw[i:i+1]!=b'0' else b'1'
            self.diff_rejects('lock package differs outside the workspace version allowance: '+re.escape(rel),rel,raw[:i]+flipped+raw[i+1:])
    def test_304_dependency_list_changed(self):
        raw=self.new[LOCK];head=b'name = "paludarium-cpu"\nversion = "0.1.0"\ndependencies = [\n'
        self.diff_rejects('workspace crate entry differs beyond its version: Cargo.lock: paludarium-cpu',LOCK,swap(raw,head,head+b' "extra-crate",\n'))
        name,version=self.external(LOCK,need_deps=True);start=raw.index(('name = "%s"\nversion = "%s"\n'%(name,version)).encode())
        at=raw.index(b'dependencies = [\n',start)+len(b'dependencies = [\n')
        self.diff_rejects('lock package differs outside the workspace version allowance: Cargo.lock: '+re.escape(name),LOCK,raw[:at]+b' "extra-crate",\n'+raw[at:])
        removed=re.sub(rb'(name = "paludarium-cpu"\nversion = "0\.1\.0"\ndependencies = \[\n) "[^"\n]+",\n',rb'\1',raw,count=1);self.assertNotEqual(removed,raw)
        self.diff_rejects('workspace crate entry differs beyond its version: Cargo.lock: paludarium-cpu',LOCK,removed)
    def test_305_non_workspace_package_version_changed(self):
        block=b'name = "paludarium-fuzz"\nversion = "0.0.0"'
        self.assertIn(block,self.old[FUZZ]);self.assertNotIn('paludarium-fuzz',u15c.FUZZ_CRATES|u15c.WORKSPACE_CRATES)
        self.diff_rejects('lock package differs outside the workspace version allowance: fuzz/Cargo.lock: paludarium-fuzz',FUZZ,swap(self.new[FUZZ],block,block.replace(b'0.0.0',b'0.1.0')))
        # A workspace crate that only exists in Cargo.lock is not authorized in fuzz/Cargo.lock.
        self.assertNotIn('paludarium-runtime',u15c.FUZZ_CRATES);self.assertNotIn(b'name = "paludarium-runtime"',self.old[FUZZ])
    def test_306_workspace_version_other_than_0_1_0(self):
        block=b'name = "paludarium-jit"\nversion = "0.1.0"'
        for rel in (LOCK,FUZZ):
            for other in (b'0.1.1',b'0.0.0',b'1.0.0',b'0.1.0-rc.1'):
                self.diff_rejects('workspace crate version is not 0.0.0 -> 0.1.0: '+re.escape(rel)+': paludarium-jit',rel,swap(self.new[rel],block,block.replace(b'0.1.0',other)))
        self.diff_rejects('workspace crate version is not 0.0.0 -> 0.1.0: Cargo.lock: paludarium-jit',LOCK,self.new[LOCK],old=swap(self.old[LOCK],b'name = "paludarium-jit"\nversion = "0.0.0"',b'name = "paludarium-jit"\nversion = "0.0.1"'))
        self.diff_rejects('workspace crate version is not 0.0.0 -> 0.1.0: Cargo.lock: paludarium',LOCK,self.old[LOCK])
    def test_307_lock_structure_and_lines(self):
        raw=self.new[LOCK];parts=raw.split(b'\n[[package]]\n')
        self.diff_rejects('lock package count differs: Cargo.lock',LOCK,b'\n[[package]]\n'.join(parts[:-1])+b'\n')
        self.diff_rejects('lock package order differs: Cargo.lock',LOCK,b'\n[[package]]\n'.join([parts[0],parts[2],parts[1],*parts[3:]]))
        self.diff_rejects('lock top-level differs: Cargo.lock',LOCK,swap(raw,b'version = 4\n',b'version = 3\n'))
        self.diff_rejects('lock line differs beyond a workspace version line: Cargo.lock',LOCK,swap(raw,b'name = "paludarium-jit"\nversion = "0.1.0"\n',b'name = "paludarium-jit"\nversion = "0.1.0"  \n'))
        self.diff_rejects('lock changed line count differs: Cargo.lock',LOCK,swap(raw,b'# It is not intended for manual editing.',b'# It is not intended for manual editing!'))
        self.diff_rejects('lock line count differs: Cargo.lock',LOCK,raw+b'\n')
        self.diff_rejects('version file is not UTF-8: Cargo.lock',LOCK,raw+b'\xff')
        self.diff_rejects('lock file does not parse: Cargo.lock',LOCK,raw+b'[[package\n')
        self.diff_rejects('not a version file: Cargo.toml','Cargo.toml',self.raw('Cargo.toml'),old=self.raw('Cargo.toml'))
    def test_308_package_json_other_changes(self):
        new=self.new[PKG];msg='package.json key differs: '+re.escape(PKG)
        self.diff_rejects(msg+': license',PKG,swap(new,b'"license":"Apache-2.0"',b'"license":"MIT"'))
        self.diff_rejects(msg+': publishConfig',PKG,swap(new,b'"provenance":true',b'"provenance":false'))
        self.diff_rejects(msg+': files',PKG,swap(new,b'"LICENSE",',b''))
        order='package.json keys/order differ: '+re.escape(PKG)
        self.diff_rejects(order,PKG,swap(new,b'"license":"Apache-2.0"',b'"license":"Apache-2.0","private":true'))
        self.diff_rejects(order,PKG,swap(new,b',"type":"module"',b''))
        self.diff_rejects(order,PKG,swap(new,b'{"name":"@paludarium/wasm","version":"0.1.0"',b'{"version":"0.1.0","name":"@paludarium/wasm"'))
        for other in (b'0.2.0',b'0.0.0',b'0.1.0-rc.1'):
            self.diff_rejects('package.json version is not 0.0.0 -> 0.1.0',PKG,swap(new,b'"version":"0.1.0"',b'"version":"'+other+b'"'))
        self.diff_rejects('package.json bytes differ beyond the version value',PKG,swap(new,b'"type":"module"',b'"type": "module"'))
        self.diff_rejects('package.json bytes differ beyond the version value',PKG,new.rstrip(b'\n'))
        self.diff_rejects('package.json has a duplicate key',PKG,swap(new,b'"license":"Apache-2.0"',b'"license":"Apache-2.0","license":"Apache-2.0"'))
        self.diff_rejects('package.json does not parse',PKG,b'{')
        self.diff_rejects('package.json is not an object',PKG,b'[]\n',old=b'[]\n')
    def test_309_current_bytes_differ_from_signed_head(self):
        for p in u15c.VERSION_FILES:
            msg='version file differs from binding/signed head: '+re.escape(p)
            self.rejects(msg,self.versions(),replace={p:self.raw(p)+b'\n'})
            self.rejects(msg,self.versions(),replace={p:self.old[p]})
            self.rejects('missing/unreadable input: '+re.escape(p),self.versions(),missing=[p])
            self.rejects(msg,self.versions(self.variant(lambda b,p=p:b['version_files'][p].update(new_sha256='0'*64))))
        self.rejects('version file differs from binding/signed head: '+re.escape(LOCK),self.full(),replace={LOCK:self.raw(LOCK)+b'\n'})
    def test_310_old_and_receipt_pins(self):
        for p in u15c.VERSION_FILES:
            e=self.b['version_files'][p]
            self.rejects('version old pin differs: '+re.escape(p),self.versions(self.variant(lambda b,p=p:b['version_files'][p].update(old_sha256='0'*64))))
            self.rejects('version old pin differs: '+re.escape(p),self.versions(self.variant(lambda b,p=p,e=e:b['version_files'][p].update(old_sha256=e['new_sha256']))))
            self.rejects('version receipt pin differs: '+re.escape(p),self.versions(self.variant(lambda b,p=p:b['version_files'][p].update(receipt_sha256='0'*64))))
            self.rejects('version entry differs: '+re.escape(p),self.versions(self.variant(lambda b,p=p:b['version_files'][p].update(extra=1))))
            self.rejects('version entry differs: '+re.escape(p),self.versions(self.variant(lambda b,p=p:b['version_files'][p].pop('receipt_sha256'))))
        self.rejects('version entry differs: '+re.escape(PKG),self.versions(self.variant(lambda b:b['version_files'][PKG].update(kind='cargo-lock'))))
        # package.json: the receipt pin (208fd965 blob) is not the old bytes; the old bytes cannot stand in for it.
        pkg=self.b['version_files'][PKG];self.assertNotEqual(pkg['receipt_sha256'],pkg['old_sha256'])
        self.rejects('version receipt pin differs: '+re.escape(PKG),self.versions(self.variant(lambda b:b['version_files'][PKG].update(receipt_sha256=pkg['old_sha256']))))
        self.rejects('version old pin differs: '+re.escape(PKG),self.versions(self.variant(lambda b:b['version_files'][PKG].update(old_sha256=pkg['receipt_sha256']))))
        receipt=self.b2['compiled_receipt']['path']
        self.rejects('compiled receipt differs',self.versions(),replace={receipt:self.raw(receipt)+b' '})
        self.assertEqual(u15c.RECEIPT_IS_OLD,frozenset({LOCK,FUZZ}))
    def test_311_fixed_path_set_and_a_fourth_path(self):
        self.assertEqual(u15c.VERSION_FILES,(LOCK,FUZZ,PKG))
        message='version allowance differs from the authorized path set'
        extra={'kind':'cargo-lock','old_sha256':'0'*64,'receipt_sha256':'0'*64,'new_sha256':sha(self.raw('Cargo.toml'))}
        self.rejects(message,self.versions(self.variant(lambda b:b['version_files'].__setitem__('Cargo.toml',extra))))
        self.rejects(message,self.versions(self.variant(lambda b:b['version_files'].pop(PKG))))
        self.rejects(message,self.versions(self.variant(lambda b:b['version_files'].clear())))
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),self.full(),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
        # The old chain's own pin of Cargo.toml (binding-v4, a path changed by bb197e04) is not widened.
        m=u15c.nc();fc=m.load('fc_under_test',m.OLD/'final_candidate.py');pins=json.loads(self.raw(str((m.OLD/'binding-v4.json').relative_to(ROOT))))['source_files']
        with self.View(self.version_map):
            with self.assertRaisesRegex(ValueError,'current source changed: Cargo.toml$'):fc.source_pins(pins)
        with Overlay(replace={p:m.git_blobs(PRIOR,[p])[p] for p in ('Cargo.toml','README.md','docs/release.md','tests/release/test_package.py','tests/release/test_policy.py')}):
            with self.View(self.version_map):fc.source_pins(pins)
    def test_312_signed_head_and_chain(self):
        for head in (PRIOR,JIT_HEAD,'not-a-commit',self.b['head'].upper()):
            self.rejects('signed head differs',self.head(self.variant(lambda b,h=head:b.update(head=h))))
        self.rejects('parent differs from the binding-07 signed head',self.head(self.variant(lambda b:b.update(parent=STEP30_HEAD))))
        self.rejects('signed chain differs',self.head(self.variant(lambda b:b.update(head_chain=[STEP30_HEAD,PRIOR,self.b['head']]))))
        self.rejects('signed head differs',self.full(self.variant(lambda b:b.update(head=PRIOR))))
    def test_313_ci_runs_failure_and_wrong_head(self):
        def run(rid):return lambda ci:next(r for r in ci['runs'] if str(r['id'])==rid)
        cases=((lambda ci:run(CI_RUN)(ci).update(conclusion='failure'),'CI run not successful: '+CI_RUN),
               (lambda ci:run(CI_RUN)(ci).update(status='in_progress'),'CI run not successful: '+CI_RUN),
               (lambda ci:run(PERF_RUN)(ci).update(head_sha=PRIOR),'CI run head differs: '+PERF_RUN),
               (lambda ci:ci['commits'][1].update(verified=False),'signed commit not Verified'),
               (lambda ci:ci['commits'][1].update(parents=[STEP30_HEAD]),'commit parent chain differs'),
               (lambda ci:ci['branch'].update(head=PRIOR),'CI branch head differs'),
               (lambda ci:ci['commits'][1]['files'].pop(),'signed commit file list differs'),
               (lambda ci:ci['compare']['files'].append(dict(filename='Cargo.lock.extra',status='added',sha='0'*40)),'compare file list differs'),
               (lambda ci:ci['compare'].update(commits=[PRIOR,self.b['head']]),'compare differs'),
               (lambda ci:ci['compare'].update(behind_by=1),'compare differs'),
               (lambda ci:next(f for f in ci['compare']['files'] if f['filename']==LOCK).update(sha='0'*40),'compare blob differs from local git: Cargo.lock'),
               (lambda ci:ci['runs_listed_for_head']['ids'].pop(),'CI run listing for the head differs'),
               (lambda ci:ci['runs_listed_for_head'].update(total_count=8),'CI run listing for the head differs'))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_ci=edit);self.rejects(pattern,self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_ci=lambda ci:run(CI_RUN)(ci).update(conclusion='failure'),rebind=False)
        self.rejects('CI evidence bytes differ',self.head(b),replace=replace)
        def rename(doc):next(r for r in doc['runs'] if str(r['id'])==CI_RUN)['name']='Other'
        b,replace=self.ci_variant(edit_ci=rename,edit_jobs=rename,edit_binding=lambda b:b['ci']['runs'][CI_RUN].update(name='Other'))
        self.rejects('CI run set differs from the required runs',self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_binding=lambda b:b['ci']['runs'].pop(CI_RUN))
        self.rejects('CI run missing or unexpected',self.head(b),replace=replace)
    def test_314_ci_jobs(self):
        def jobs(rid):return lambda d:next(r for r in d['runs'] if str(r['id'])==rid)
        cases=((lambda d:jobs(CI_RUN)(d)['jobs'][0].__setitem__(2,'failure'),'CI job not successful: '+CI_RUN),
               (lambda d:jobs(CI_RUN)(d)['jobs'][0].__setitem__(2,'skipped'),'CI job not successful: '+CI_RUN),
               (lambda d:jobs(PERF_RUN)(d)['jobs'].pop(),'CI job set differs: '+PERF_RUN),
               (lambda d:jobs(CI_RUN)(d).update(total_count=24),'CI job count differs from the API total'),
               (lambda d:d.update(head=PRIOR),'CI job evidence repository/head differs'),
               (lambda d:jobs(CI_RUN)(d).update(run_attempt=2),'CI job run identity differs: '+CI_RUN))
        for edit,pattern in cases:
            b,replace=self.ci_variant(edit_jobs=edit);self.rejects(pattern,self.head(b),replace=replace)
        b,replace=self.ci_variant(edit_jobs=lambda d:d.update(head=PRIOR),rebind=False)
        self.rejects('CI job evidence bytes differ',self.head(b),replace=replace)
        self.rejects('CI job set differs: '+CI_RUN,self.head(self.variant(lambda b:b['ci_jobs']['expected'][CI_RUN].pop())))
    def test_315_performance_original(self):
        path=self.b['performance']['path']
        self.rejects('performance original bytes differ',self.head(self.variant(lambda b:b['performance'].update(sha256='0'*64))))
        self.rejects('performance run is not the U14 full-quality run',self.head(self.variant(lambda b:b['performance'].update(run_id=int(CI_RUN)))))
        self.rejects('performance original path differs',self.head(self.variant(lambda b:b['performance'].update(path=self.b2['performance']['path']))))
        doc=json.loads(self.raw(path));doc['head']=PRIOR;raw=json.dumps(doc).encode()
        self.rejects('performance original not passed at the signed head',self.head(self.variant(lambda b:b['performance'].update(sha256=sha(raw)))),replace={path:raw})
        doc=json.loads(self.raw(path));doc['passed']=False;raw=json.dumps(doc).encode()
        self.rejects('performance original not passed at the signed head',self.head(self.variant(lambda b:b['performance'].update(sha256=sha(raw)))),replace={path:raw})
        self.rejects('performance statistic differs',self.head(self.variant(lambda b:b['performance'].update(p=0.5))))
    def test_316_base_u14_entry_and_binding_07(self):
        for edit in (lambda b:b['base']['entry'].update(sha256='0'*64),lambda b:b['base']['entry'].update(path=u15c.U11_ENTRY),
                     lambda b:b['base']['binding'].update(name='binding-06.json'),lambda b:b['base']['binding'].update(sha256=u15c.u14().U11_BINDING_SHA256)):
            with self.assertRaisesRegex(ValueError,'base entry/binding differs'):u15c.verify_base(self.variant(edit))
        self.rejects('binding schema/repository differs',lambda:u15c.verify_base(self.variant(lambda b:b.update(schema=7))))
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u15c.verify_base(self.b),replace={U14_BINDING_REL:self.raw(U14_BINDING_REL)+b'\n'})
        cached=u15c._U14
        try:
            u15c._U14=None
            self.rejects('U14 entry bytes differ from the pinned SHA-256',u15c.u14,replace={u15c.U14_ENTRY:self.raw(u15c.U14_ENTRY)+b'\n'})
            u15c._U14=None
            self.rejects('U11 entry bytes differ from the pinned SHA-256',u15c.nc,replace={u15c.U11_ENTRY:self.raw(u15c.U11_ENTRY)+b'\n'})
        finally:u15c._U14=cached
    def test_317_history_and_spec(self):
        self.assertEqual(sha(self.raw(u15c.SPEC)),u15c.SPEC_SHA256)
        for rel in u15c.HISTORY:
            self.rejects('history file changed: '+re.escape(rel),lambda:u15c.verify_history(self.b),replace={rel:self.raw(rel)+b'\n'})
        for edit in (lambda b:b['history'].pop(u15c.U14_ENTRY),lambda b:b['history'].__setitem__(u15c.U14_ENTRY,'0'*64),lambda b:b.pop('history')):
            with self.assertRaisesRegex(ValueError,'history pin set differs'):u15c.verify_history(self.variant(edit))
        self.rejects('spec differs from the approved proposal bytes',lambda:u15c.verify_history(self.b),replace={u15c.SPEC:self.raw(u15c.SPEC)+b'\n'})
        self.rejects('spec reference differs',lambda:u15c.verify_history(self.variant(lambda b:b['spec'].update(sha256='0'*64))))
        self.rejects('history file changed: '+re.escape(u15c.U14_LOOP+'README.md'),self.full(),replace={u15c.U14_LOOP+'README.md':self.raw(u15c.U14_LOOP+'README.md')+b'\n'})
    def test_318_binding_pin_and_command_line_exit_2(self):
        for pin in ('0'*64,u15c.U14_BINDING_SHA256,ENTRY_PIN):
            with self.assertRaisesRegex(ValueError,'binding SHA-256 differs from the binding pinned by this entry'):u15c.load_binding(pin)
        for pin in ('',BINDING_PIN.upper()):
            with self.assertRaisesRegex(ValueError,'binding SHA-256 required'):u15c.load_binding(pin)
        self.rejects('binding bytes differ from the pinned SHA-256',lambda:u15c.load_binding(BINDING_PIN),replace={BINDING_REL:self.raw(BINDING_REL)+b'\n'})
        usage=re.escape(u15c.USAGE)
        for argv in ([],['--entry-sha256',ENTRY_PIN],['--binding-sha256',BINDING_PIN],['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN],
                     ['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN,'extra'],['--entry-sha256='+ENTRY_PIN,'--binding-sha256='+BINDING_PIN]):
            self.refused(argv,usage)
        self.refused(['--entry-sha256',ENTRY_PIN.upper(),'--binding-sha256',BINDING_PIN],'--entry-sha256 must be 64 lowercase hex digits')
        self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN[:63]],'--binding-sha256 must be 64 lowercase hex digits')
        for pin in ('0'*64,BINDING_PIN,u15c.U14_ENTRY_SHA256):self.refused(['--entry-sha256',pin,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs from the SHA-256 of this entry file')
        for pin in ('0'*64,ENTRY_PIN,u15c.U14_BINDING_SHA256):self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',pin],'--binding-sha256 differs from the SHA-256 of '+re.escape(u15c.BINDING))
        changed=self.raw(BINDING_REL)+b'\n'
        self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',sha(changed)],'--binding-sha256 differs from the binding pinned by this entry',replace={BINDING_REL:changed})
        self.refused(['--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs from the SHA-256 of this entry file',replace={SELF_REL:self.raw(SELF_REL)+b'\n'})
        self.assertEqual(u15c.command_line_pins([str(u15c.SELF),'--entry-sha256',ENTRY_PIN,'--binding-sha256',BINDING_PIN]),(ENTRY_PIN,BINDING_PIN))
    def test_319_real_process_exit_codes(self):
        before=own_listing()
        for argv,pattern in (([],re.escape(u15c.USAGE)),(['--entry-sha256','0'*64,'--binding-sha256',BINDING_PIN],'--entry-sha256 differs'),
                             (['--entry-sha256',ENTRY_PIN,'--binding-sha256','0'*64],'--binding-sha256 differs'),
                             (['--binding-sha256',BINDING_PIN,'--entry-sha256',ENTRY_PIN],re.escape(u15c.USAGE)),
                             (['--entry-sha256',u15c.U14_ENTRY_SHA256,'--binding-sha256',u15c.U14_BINDING_SHA256],'--entry-sha256 differs')):
            r=subprocess.run([sys.executable,'-B',str(u15c.SELF),*argv],cwd=ROOT,capture_output=True,timeout=60)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,b'');self.assertRegex(r.stderr.decode(),'^REFUSED: '+pattern)
        r=subprocess.run([sys.executable,'-B',*self.child_argv(entry='0'*64)],cwd=ROOT,capture_output=True,timeout=60)
        self.assertEqual(r.returncode,1);self.assertEqual(r.stdout,b'');self.assertIn('--entry-sha256 differs from the SHA-256 of this entry file',r.stderr.decode())
        self.assertEqual(own_listing(),before)
    def test_320_old_chain_guard_and_child_boundaries(self):
        calls=[];nc=u15c.nc()
        def fake_real(argv,**kw):calls.append((argv,kw));return types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
        run=u15c.guarded_run(ENTRY_PIN,BINDING_PIN,OWN,[],fake_real)
        kw=dict(cwd=ROOT,capture_output=True,timeout=900);good=[sys.executable,'-B',str(nc.OLD/'old_predicates.py'),str(OWN/'never-written.json')]
        run(good,**kw);self.assertEqual(calls[0][0][2:6],[str(u15c.SELF),'--logical-child',ENTRY_PIN,BINDING_PIN]);self.assertEqual(calls[0][0][-2:],good[2:])
        for argv in ([sys.executable,'-B',str(nc.OLD/'final_candidate.py'),'r.json'],[sys.executable,'-I',str(nc.OLD/'old_predicates.py'),'r.json'],
                     [sys.executable,'-B',str(OWN/'old_predicates.py'),'r.json'],good+['extra']):
            with self.assertRaisesRegex(ValueError,'unexpected old child argv'):run(argv,**kw)
        for options in ({**kw,'cwd':OWN},{**kw,'timeout':901}):
            with self.assertRaisesRegex(ValueError,'unexpected child options'):run(good,**options)
        self.assertEqual(len(calls),1)
        argv=self.child_argv();saved=(list(sys.argv),list(sys.path))
        with self.assertRaisesRegex(ValueError,'internal child argv differs'):u15c.logical_child(argv[:-1])
        for entry,message in (('0'*64,'--entry-sha256 differs from the SHA-256 of this entry file'),(ENTRY_PIN.upper(),'--entry-sha256 must be 64 lowercase hex digits'),
                              (u15c.U14_ENTRY_SHA256,'--entry-sha256 differs from the SHA-256 of this entry file')):
            self.rejects(message,lambda e=entry:u15c.logical_child(self.child_argv(entry=e)),replace={LOCK:self.raw(LOCK)+b'\n'})
        self.rejects('--binding-sha256 differs from the SHA-256 of '+re.escape(u15c.BINDING),lambda:u15c.logical_child(self.child_argv(pin=u15c.U14_BINDING_SHA256)),replace={LOCK:self.raw(LOCK)+b'\n'})
        with self.assertRaisesRegex(ValueError,'validator outside the reused old set'):u15c.logical_child(argv[:5]+[str(OWN/'old_predicates.py'),'r.json'])
        with self.assertRaisesRegex(ValueError,'child receipt folder differs'):u15c.logical_child(argv[:4]+[str(ROOT/u15c.U14_LOOP/'run-never')]+argv[5:])
        with self.assertRaisesRegex(ValueError,'child receipt folder differs'):u15c.logical_child(argv)
        self.assertEqual((sys.argv,sys.path),saved)
    def test_321_logical_child_rejects_changed_inputs(self):
        argv=self.child_argv()
        self.rejects('version file differs from binding/signed head: '+re.escape(LOCK),lambda:u15c.logical_child(argv),replace={LOCK:self.raw(LOCK)+b'\n'})
        self.rejects('compiled source changed: '+re.escape(OTHER_SOURCE),lambda:u15c.logical_child(argv),replace={OTHER_SOURCE:self.raw(OTHER_SOURCE)+b'\n'})
        self.rejects('history file changed: '+re.escape(u15c.U14_LOOP+'README.md'),lambda:u15c.logical_child(argv),replace={u15c.U14_LOOP+'README.md':self.raw(u15c.U14_LOOP+'README.md')+b'\n'})
        self.rejects('--entry-sha256 differs from the SHA-256 of this entry file',lambda:u15c.logical_child(argv),replace={SELF_REL:self.raw(SELF_REL)+b'\n'})
    def test_322_claim_scope(self):
        scope={'old_current_semantics':{'scope':'old'},'performance_1ceae86c':{'module_sha256':'d892ea28'},'u11_57a8c96f':{'head':PRIOR},'u14_records':{'head':PRIOR}};kept=copy.deepcopy(scope)
        out=u15c.u15_scope(scope,self.summary['u15']);self.assertEqual(scope,kept);self.assertEqual({k:out[k] for k in kept},kept)
        note=out['u15_version'];self.assertEqual((note['head'],note['parent']),(self.b['head'],PRIOR))
        self.assertEqual(note['version_files'],sorted(u15c.VERSION_FILES));self.assertEqual(note['claimed'],list(u15c.CLAIMED));self.assertEqual(note['not_claimed'],list(u15c.NOT_CLAIMED))
        self.assertTrue(any('FR10.1' in s for s in note['not_claimed']));self.assertTrue(any('Cargo.toml' in s for s in note['not_claimed']));self.assertIn('GAP',note['scope'])
        for missing in ('performance_1ceae86c','u11_57a8c96f','u14_records'):
            with self.assertRaisesRegex(ValueError,'U14 claim scope missing'):u15c.u15_scope({k:v for k,v in scope.items() if k!=missing},self.summary['u15'])

def run_u14_suite_under_u15_view():
    """The unchanged U14 (and U11, U2, U1) regressions with the three version files at their old bytes only."""
    b=u15c.load_binding(BINDING_PIN);b7,_,b2=u15c.verify_base(b);head=u15c.verify_head(b,b7,b2)
    _,mapping=u15c.verify_versions(b,b2,head['head'])
    with u15c.view_class()(mapping) as view:
        first,second=u14t.run_u11_suite_under_u14_view()
        third=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(u14t.U14Step46))
    read={c['path'] for c in view.calls};assert set(mapping)<=read,'version files were not read through the view'
    return first,second,third

def main():
    first,second,third=run_u14_suite_under_u15_view()
    fourth=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(U15Version))
    inner=first.testsRun+second.testsRun+third.testsRun;run=inner+fourth.testsRun;expected=U14_SUITE_COUNT+U15_TEST_COUNT
    skipped=sum(len(r.skipped) for r in (first,second,third,fourth))
    print(f'regressions: run {run} / expected {expected} (U14 suite {inner}/{U14_SUITE_COUNT} under the U15 version view + U15 {fourth.testsRun}/{U15_TEST_COUNT}), skipped {skipped}')
    ok=all(r.wasSuccessful() for r in (first,second,third,fourth)) and inner==U14_SUITE_COUNT and fourth.testsRun==U15_TEST_COUNT and not skipped
    return 0 if ok else 1

if __name__=='__main__':sys.exit(main())
