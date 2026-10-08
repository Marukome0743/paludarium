import hashlib,json,pathlib,subprocess
root=pathlib.Path(__file__).parent/'guests'
rows=[]
for p in sorted(root.iterdir()):
 if not p.is_file(): continue
 p.chmod(0o755)
 try:
  r=subprocess.run([str(p)],capture_output=True,timeout=30)
  rows.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),returncode=r.returncode,stdout=r.stdout.hex(),stderr=r.stderr.hex(),timed_out=False))
 except subprocess.TimeoutExpired:
  rows.append(dict(name=p.name,timed_out=True))
print(json.dumps(rows,indent=2))
