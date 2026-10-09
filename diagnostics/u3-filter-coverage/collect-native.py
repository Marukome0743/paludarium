from pathlib import Path
import subprocess,os,signal,json,hashlib
out=Path("target/u3-filter-coverage-evidence/native");out.mkdir(parents=True,exist_ok=True)
subprocess.run(["bash","tests/guests/u3/build.sh","target/u3-guests"],check=True)
rows=[]
for name in ["observe","fault-observe","cpuid-observe"]:
 binary=Path("target/u3-guests")/name
 with (out/(name+".native")).open("wb") as stdout,(out/(name+".stderr")).open("wb") as stderr:
  p=subprocess.Popen([str(binary.resolve())],stdout=stdout,stderr=stderr,start_new_session=True)
  try: code=p.wait(timeout=30)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGKILL);p.wait();raise
 data=(out/(name+".native")).read_bytes();count=len(data.splitlines())
 rows.append({"name":name,"exit":code,"rows":count,"binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"output_sha256":hashlib.sha256(data).hexdigest()})
 (out/"receipt.json").write_text(json.dumps(rows,indent=2)+"\n")
 assert code==0 and count>0 and not (out/(name+".stderr")).read_bytes()
