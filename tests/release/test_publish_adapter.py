"""Real archive fixtures with mocked network/upload adapters, never a publication."""
import base64,hashlib,io,json,os,shutil,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from test_package import tar
from test_policy import ROOT
from test_check import CANARY
import check,package,policy

class PublishAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'target/u15');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.head='a'*40
        sourcefiles={}
        sourcefiles['Cargo.toml']=(ROOT/'Cargo.toml').read_bytes().replace(b'0.0.0',b'0.1.0')
        sourcefiles['rust-toolchain.toml']=(ROOT/'rust-toolchain.toml').read_bytes()
        for member in __import__('tomllib').loads(sourcefiles['Cargo.toml'].decode())['workspace']['members']:
            sourcefiles[member+'/Cargo.toml']=(ROOT/member/'Cargo.toml').read_bytes()
        sourcefiles['packages/paludarium-wasm/package.json']=(ROOT/'packages/paludarium-wasm/package.json').read_bytes().replace(b'0.0.0',b'0.1.0')
        for n,b in sourcefiles.items():
            p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        self.inv=policy.inventory(self.root);self.out=self.root/'target/u15';self.art=self.out/'package-test';self.art.mkdir(parents=True)
        self.crates=[]
        for name in self.inv['order']:
            dep='\n'.join('[dependencies.'+d+']\nversion="'+v+'"' for d,v in self.inv['packages'][name]['dependencies'].items())
            m='[package]\nname="'+name+'"\nversion="0.1.0"\nlicense="Apache-2.0"\n'+dep
            p=self.art/'source/target/package'/(name+'-0.1.0.crate');p.parent.mkdir(parents=True,exist_ok=True)
            tar(p,{'Cargo.toml':m.encode(),'LICENSE':b'Apache','README.md':b'usage'},name+'-0.1.0');self.crates.append(p)
        files={n:b'export {};' for n in package.REQUIRED_JS}
        files.update({'package.json':b'{"name":"@paludarium/wasm","version":"0.1.0"}',
          'paludarium.wasm':b'\0asm\x01\0\0\0','index.d.ts':b'export {};','LICENSE':b'Apache','README.md':b'usage'})
        self.npm=self.art/'wasm.tgz';tar(self.npm,files)
        with zipfile.ZipFile(self.art/'source-snapshot.zip','x') as z:
            for n,b in sourcefiles.items():z.writestr(n,b)
        sourcehash=package.sha(json.dumps({n:package.sha(b) for n,b in sourcefiles.items()},sort_keys=True).encode())
        expected=dict(version='0.1.0',head=self.head,source_sha256=sourcehash,tar_sha256=package.sha(self.npm.read_bytes()),wasm_sha256=package.sha(files['paludarium.wasm']),source_files={})
        self.result=dict(passed=True,head=self.head,local_snapshot=False,source_sha256=sourcehash,
            crates=package.inspect_crates(self.crates,self.inv),npm=package.inspect_npm(self.npm,expected))
        (self.out/'package-result.json').write_text(json.dumps(self.result));self.uploaded=set()
        self.env=dict(PALUDARIUM_TEST_NODE=sys.executable,PALUDARIUM_RELEASE_NPM=__file__,U15_OIDC_CRATES_IO_TOKEN=CANARY['U15_OIDC_CRATES_IO_TOKEN'])
        self.mode='oidc';self.envs=[]
    def request(self,url,timeout):
        if 'crates.io/' in url:
            name=url.split('/')[-2]
            if name not in self.uploaded:raise check.urllib.error.HTTPError(url,404,'absent',{},None)
            return io.BytesIO(json.dumps(dict(version=dict(num='0.1.0',checksum=self.result['crates'][name]['sha256']))).encode())
        if 'npm' not in self.uploaded:raise check.urllib.error.HTTPError(url,404,'absent',{},None)
        digest='sha512-'+base64.b64encode(hashlib.sha512(self.npm.read_bytes()).digest()).decode()
        return io.BytesIO(json.dumps(dict(version='0.1.0',dist=dict(integrity=digest))).encode())
    def command(self,argv,cwd,output,*args,**kwargs):
        self.envs.append((Path(output).name,args[-1]))  # both adapters receive env last
        if '-p' in argv:
            name=argv[argv.index('-p')+1]
            if '--dry-run' in argv:
                target=Path(cwd)/'target/package'/(name+'-0.1.0.crate');target.parent.mkdir(parents=True,exist_ok=True)
                original=next(p for p in self.crates if p.name==target.name);shutil.copyfile(original,target)
            else:self.uploaded.add(name)
        else:self.uploaded.add('npm')
        return dict(exit=0,timeout=False,error=None,reaped=True)
    def execute(self):
        approved=dict(head=self.head,version='0.1.0',order=self.inv['order'],authentication=self.mode)
        with patch.dict(os.environ,self.env),patch.object(check,'authorize',return_value=approved),patch.object(check,'checked_command',side_effect=self.command),patch.object(check,'run_command',side_effect=self.command),patch.object(check.urllib.request,'urlopen',side_effect=self.request):
            return check.publish_artifacts(self.root,None)
    def test_mocked_upload_transport(self):
        self.assertEqual(len(self.execute()['published']),12)
    def test_existing_versions_are_not_uploaded(self):
        self.uploaded=set(self.inv['order'])|{'npm'}
        self.assertEqual(len(self.execute()['published']),12)
    def test_artifact_head_changed_before_upload(self):
        self.result['head']='b'*40;(self.out/'package-result.json').write_text(json.dumps(self.result))
        with self.assertRaises(ValueError):self.execute()
        self.assertEqual(self.uploaded,set())
    def test_npm_digest_changed_before_upload(self):
        self.npm.write_bytes(self.npm.read_bytes()+b'changed')
        with self.assertRaises(ValueError):self.execute()
        self.assertEqual(self.uploaded,set())
    # Step14b (Q4): the first publication uses the scoped tokens, only for uploads, never recorded.
    def test_first_publication_tokens_reach_uploads_only(self):
        self.mode='first-publication-token';del self.env['U15_OIDC_CRATES_IO_TOKEN']
        self.env.update(U15_FIRST_CRATES_IO_TOKEN=CANARY['U15_FIRST_CRATES_IO_TOKEN'],U15_FIRST_NPM_TOKEN=CANARY['U15_FIRST_NPM_TOKEN'])
        result=self.execute();self.assertEqual(result['authentication'],'first-publication-token')
        crates,npm=CANARY['U15_FIRST_CRATES_IO_TOKEN'],CANARY['U15_FIRST_NPM_TOKEN']
        dry=[e for n,e in self.envs if n.startswith('dry-')];uploads=[e for n,e in self.envs if n.startswith('publish-') and n!='publish-npm']
        npm_env=[e for n,e in self.envs if n=='publish-npm']
        self.assertEqual((len(dry),len(uploads),len(npm_env)),(11,11,1))
        self.assertTrue(all(not set(CANARY.values())&set(e.values()) for e in dry))
        self.assertTrue(all(e['CARGO_REGISTRY_TOKEN']==crates and npm not in e.values() for e in uploads))
        self.assertEqual(npm_env[0]['NODE_AUTH_TOKEN'],npm);self.assertNotIn(crates,npm_env[0].values())
        recorded=json.dumps(result)+(self.out/'publication-progress.json').read_text()
        self.assertFalse([v for v in CANARY.values() if v in recorded])
    def test_oidc_mode_refuses_leftover_first_token(self):
        self.env['U15_FIRST_CRATES_IO_TOKEN']=CANARY['U15_FIRST_CRATES_IO_TOKEN']
        with self.assertRaisesRegex(ValueError,'still configured'):self.execute()
        self.assertEqual(self.uploaded,set());self.assertEqual(self.envs,[])
    def test_oidc_mode_uses_oidc_token(self):
        self.execute()
        self.assertTrue(all(e['CARGO_REGISTRY_TOKEN']==CANARY['U15_OIDC_CRATES_IO_TOKEN'] for n,e in self.envs if n.startswith('publish-') and n!='publish-npm'))
        self.assertTrue(all('CARGO_REGISTRY_TOKEN' not in e for n,e in self.envs if n.startswith('dry-') or n=='publish-npm'))

if __name__=='__main__':unittest.main()
