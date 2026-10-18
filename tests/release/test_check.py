import copy,io,json,re,sys,tempfile,unittest,os,urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/release'))
import check,policy

CANARY={'U15_OIDC_CRATES_IO_TOKEN':'canary-oidc-0001','U15_FIRST_CRATES_IO_TOKEN':'canary-crates-0002','U15_FIRST_NPM_TOKEN':'canary-npm-0003'}

class Registry:
    """In-memory crates.io/npm presence; never reaches the network."""
    def __init__(self,present=(),status=None,unreachable=False):
        self.present,self.status,self.unreachable,self.requests=set(present),status,unreachable,[]
    def __call__(self,request,timeout):
        self.requests.append(request);url=request.full_url
        if self.unreachable:raise urllib.error.URLError('down')
        if self.status:raise urllib.error.HTTPError(url,self.status,'unavailable',{},None)
        name='@paludarium/wasm' if url.startswith('https://registry.npmjs.org/') else url.rsplit('/',1)[1]
        if name not in self.present:raise urllib.error.HTTPError(url,404,'absent',{},None)
        return io.BytesIO(b'{}')

class CheckTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'target/u15');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def run_child(self,code,timeout=5):
        return check.run_command([sys.executable,'-B','-c',code],self.root,self.root/'receipt',timeout)
    def test_success(self):
        r=self.run_child('print("ok")');check.require_success(r)
        self.assertEqual((self.root/'receipt/stdout.bin').read_bytes(),b'ok\n')
    def test_failure(self):
        r=self.run_child('raise SystemExit(7)')
        with self.assertRaises(ValueError):check.require_success(r)
        self.assertEqual(r['exit'],7)
    def test_timeout(self):
        r=self.run_child('import time;print("partial",flush=True);time.sleep(10)',.05)
        self.assertTrue(r['timeout']);self.assertTrue(r['reaped']);self.assertTrue(r['cleanup'])
        with self.assertRaises(ValueError):check.require_success(r)
    def test_missing_tool(self):
        r=check.run_command([str(self.root/'absent')],self.root,self.root/'receipt')
        self.assertIsNotNone(r['error'])
    def test_shim_refused(self):
        with self.assertRaises(ValueError):check.run_command(['/example/shims/python'],self.root,self.root/'receipt')
    def test_incomplete_receipt(self):
        with self.assertRaises(ValueError):check.require_success(dict(exit=0,timeout=False,error=None,reaped=False))
    def test_source_changed(self):
        (self.root/'source').write_bytes(b'before')
        with self.assertRaises(ValueError):check.checked_command([sys.executable,'-c','open("source","w").write("changed")'],self.root,self.root/'receipt',[Path('source')])
    def test_source_unchanged(self):
        (self.root/'source').write_bytes(b'before')
        self.assertEqual(check.checked_command([sys.executable,'-c','print("ok")'],self.root,self.root/'receipt',[Path('source')])['exit'],0)
    def test_unpublished(self):self.assertEqual(check.registry_state(404,{},'1','x')['state'],'UNPUBLISHED')
    def test_published(self):self.assertFalse(check.registry_state(200,dict(version='1',digest='x'),'1','x')['upload_allowed'])
    def test_query_unknown(self):
        with self.assertRaises(ValueError):check.registry_state(503,{},'1','x')
    def test_digest_mismatch(self):
        with self.assertRaises(ValueError):check.registry_state(200,dict(version='1',digest='other'),'1','x')
    def test_version_mismatch(self):
        with self.assertRaises(ValueError):check.registry_state(200,dict(version='2',digest='x'),'1','x')
    def test_bad_timeout(self):
        with self.assertRaises(ValueError):self.run_child('pass',0)
    def test_secret_environment_not_dumped(self):
        env=dict(os.environ,SECRET_CANARY='never-log-this',RUSTFLAGS='')
        receipt=check.run_command([sys.executable,'-c','pass'],self.root,self.root/'receipt',env=env)
        self.assertEqual(receipt['tool_environment']['RUSTFLAGS'],'')
        self.assertNotIn('never-log-this',(self.root/'receipt/receipt.json').read_text())
    # Step14b (Q2): a decided version is no longer reported as outstanding.
    def test_validate_outstanding_follows_version(self):
        decided=check.validate(ROOT)
        self.assertEqual(decided['version'],'0.1.0');self.assertNotIn('release version',decided['outstanding'])
        self.assertIn('initial registry ownership/publishers',decided['outstanding'])
        undecided=copy.deepcopy(policy.inventory(ROOT));undecided['version']='0.0.0'
        with patch.object(policy,'inventory',return_value=undecided):
            self.assertEqual(check.validate(ROOT)['outstanding'][0],'release version')
    # Step14b (Q4): live absence check for the one-time first publication.
    def absence(self,registry):
        with patch.object(check.urllib.request,'urlopen',side_effect=registry):
            return check.registries_absent(policy.inventory(ROOT)['order'])
    def test_registries_absent(self):
        registry=Registry();result=self.absence(registry)
        self.assertTrue(result['absent']);self.assertEqual(len(result['checked']),12);self.assertEqual(len(registry.requests),12)
        self.assertTrue(all(r.get_method()=='GET' and r.get_header('User-agent')==check.REGISTRY_USER_AGENT for r in registry.requests))
    def test_registry_name_present(self):
        for name in ('paludarium-types','@paludarium/wasm'):
            with self.subTest(name):
                result=self.absence(Registry(present=[name]))
                self.assertFalse(result['absent']);self.assertEqual(result['present'],[name])
    def test_registry_presence_unknown(self):
        with self.assertRaisesRegex(ValueError,'503'):self.absence(Registry(status=503))
        with self.assertRaisesRegex(ValueError,'unreachable'):self.absence(Registry(unreachable=True))
    def test_oidc_environments(self):
        env=dict(PATH='/bin',U15_OIDC_CRATES_IO_TOKEN=CANARY['U15_OIDC_CRATES_IO_TOKEN'],CARGO_REGISTRY_TOKEN='stale')
        dry,cargo,npm=check.publication_environments('oidc',env)
        self.assertEqual(cargo['CARGO_REGISTRY_TOKEN'],CANARY['U15_OIDC_CRATES_IO_TOKEN'])
        for e in (dry,npm):self.assertFalse(set(e)&{'CARGO_REGISTRY_TOKEN','U15_OIDC_CRATES_IO_TOKEN'})
        with self.assertRaisesRegex(ValueError,'still configured'):
            check.publication_environments('oidc',dict(env,U15_FIRST_NPM_TOKEN=CANARY['U15_FIRST_NPM_TOKEN']))
        with self.assertRaisesRegex(ValueError,'OIDC token absent'):check.publication_environments('oidc',dict(PATH='/bin'))
    def test_first_publication_environments(self):
        env=dict(PATH='/bin',U15_FIRST_CRATES_IO_TOKEN=CANARY['U15_FIRST_CRATES_IO_TOKEN'],U15_FIRST_NPM_TOKEN=CANARY['U15_FIRST_NPM_TOKEN'])
        dry,cargo,npm=check.publication_environments('first-publication-token',env)
        self.assertEqual(cargo['CARGO_REGISTRY_TOKEN'],CANARY['U15_FIRST_CRATES_IO_TOKEN']);self.assertEqual(npm['NODE_AUTH_TOKEN'],CANARY['U15_FIRST_NPM_TOKEN'])
        self.assertFalse(set(CANARY.values())&set(dry.values()));self.assertNotIn(CANARY['U15_FIRST_NPM_TOKEN'],cargo.values())
        self.assertNotIn(CANARY['U15_FIRST_CRATES_IO_TOKEN'],npm.values())
        with self.assertRaisesRegex(ValueError,'tokens absent'):check.publication_environments('first-publication-token',dict(env,U15_FIRST_NPM_TOKEN=''))
        with self.assertRaisesRegex(ValueError,'OIDC token present'):check.publication_environments('first-publication-token',dict(env,U15_OIDC_CRATES_IO_TOKEN='x'))
        with self.assertRaisesRegex(ValueError,'unknown'):check.publication_environments('long-lived',env)
    def test_upload_tokens_not_in_receipt(self):
        env=dict(os.environ,CARGO_REGISTRY_TOKEN=CANARY['U15_FIRST_CRATES_IO_TOKEN'],NODE_AUTH_TOKEN=CANARY['U15_FIRST_NPM_TOKEN'])
        check.run_command([sys.executable,'-c','pass'],self.root,self.root/'receipt',env=env)
        text=(self.root/'receipt/receipt.json').read_text()
        self.assertFalse([v for v in CANARY.values() if v in text])
    def test_release_workflow_secret_scope(self):
        text=(ROOT/'.github/workflows/release.yml').read_text();publish=text.split('\n  publish:\n',1)[1]
        self.assertEqual(sorted(re.findall(r'secrets\.(\w+)',text)),['U15_FIRST_CRATES_IO_TOKEN','U15_FIRST_NPM_TOKEN'])
        self.assertEqual(len(re.findall(r'secrets\.',publish)),2);self.assertIn('    environment: release\n',publish)
        self.assertFalse([l for l in text.splitlines() if 'secrets.' in l and not re.fullmatch(r'\s+U15_FIRST_\w+: \$\{\{ secrets\.U15_FIRST_\w+ \}\}',l)])
        oidc=publish.split('id: crates\n',1)[1].split('\n',1)[0]
        self.assertEqual(oidc.strip(),"if: steps.authorize.outputs.authentication == 'oidc'")
        for name in ('release.yml','u15-acceptance.yml','release-check.yml'):
            self.assertNotRegex((ROOT/'.github/workflows'/name).read_text(),r'(?i)echo[^\n]*(token|secret)')

if __name__=='__main__':unittest.main()
