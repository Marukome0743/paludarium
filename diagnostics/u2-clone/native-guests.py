import hashlib,json,pathlib,subprocess,time
root=pathlib.Path(__file__).parent/'guests'
rows=[]
for p in sorted(root.iterdir()):
 if not p.is_file(): continue
 p.chmod(0o755)
 try:
  if p.name=='infinite':
   proc=subprocess.Popen([str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   time.sleep(0.05);proc.kill();stdout,stderr=proc.communicate(timeout=30)
   code=proc.returncode
  else:
   r=subprocess.run([str(p)],input=b'input\n' if p.name=='stdin' else b'',capture_output=True,timeout=30)
   stdout,stderr,code=r.stdout,r.stderr,r.returncode
  rows.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),returncode=code,stdout=stdout.hex(),stderr=stderr.hex(),timed_out=False))
 except subprocess.TimeoutExpired:
  rows.append(dict(name=p.name,timed_out=True))
print(json.dumps(rows,indent=2))
