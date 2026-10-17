import json,sys,tempfile,unittest,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/release'))
import check

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

if __name__=='__main__':unittest.main()
