// Test-only tracing: source/module bytes are retained; coordinator instrumentation
// is served in memory and never written over product files or used for acceptance.
import { createServer } from "node:http";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { resolve, sep } from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
const [modulePath, probePath, outputDirectory] = process.argv.slice(2);
if (!outputDirectory) throw new Error("usage: diagnostic module probe output");
const root = resolve("."), trace = [], rows = [];
const wasm = await readFile(modulePath), probe = await readFile(probePath);
const hash = bytes => createHash("sha256").update(bytes).digest("hex");
const original = await readFile("packages/paludarium-wasm/coordinator.mjs", "utf8");
let coordinator = `function traceTask(event,data={}) { void fetch('/trace',{method:'POST',body:JSON.stringify({event,time:performance.now(),...data})}).catch(()=>{}); }\n` + original;
function insert(anchor, addition) {
  if (coordinator.split(anchor).length !== 2) throw new Error("Instrumentation anchor is not unique: " + anchor);
  coordinator = coordinator.replace(anchor, anchor + addition);
}
insert("async function launchTask(job, handle) {", "\ntraceTask('requested',{handle,active:childWorkers.size,tasks:job.tasks.size});");
insert("task.worker = worker; childWorkers.add(worker);", "\ntraceTask('created',{handle,active:childWorkers.size});");
insert('else if (report.type === "started") {', "\ntraceTask('started',{handle,diagnostics:report.diagnostics,active:childWorkers.size});");
insert('} else if (report.type === "task-finished") {', "\ntraceTask('finished',{handle,result:report.result,active:childWorkers.size});");
insert("childWorkers.delete(worker);", "\ntraceTask('retired',{handle,active:childWorkers.size});");
const page = `<!doctype html><script type="module">
import {createPaludarium} from '/packages/paludarium-wasm/index.mjs';
import {observeProgram} from '/packages/paludarium-wasm/tests/u11-programs.mjs';
try {
 if (!crossOriginIsolated) throw new Error('shared memory unavailable');
 const probe=new Uint8Array(await (await fetch('/probe')).arrayBuffer());
 for(let trial=0;trial<3;trial++) {
  await fetch('/trace',{method:'POST',body:JSON.stringify({event:'trial',trial})});
  const launcher=await createPaludarium({wasmUrl:'/production.wasm'});
  try {const row=await observeProgram(launcher,{program:'/probe',args:['/probe'],env:{TERM:'dumb',HOME:'/home/u10',TMPDIR:'/tmp'},files:{'/probe':probe,'/home/u10/.keep':new Uint8Array()}}); await fetch('/row',{method:'POST',body:JSON.stringify({trial,row})});}
  finally {await launcher.dispose();}
 }
 window.__diagnosticDone=true;
}catch(error){window.__diagnosticError=String(error);window.__diagnosticDone=true;}
</script>`;
const server = createServer(async (request,response) => {
 const headers={"Cross-Origin-Opener-Policy":"same-origin","Cross-Origin-Embedder-Policy":"require-corp","Cache-Control":"no-store"};
 try {
  if(request.url==='/trace'||request.url==='/row') {
   let body='';for await(const chunk of request){body+=chunk;if(body.length>65536)throw new Error('diagnostic payload bound');}
   const item=JSON.parse(body);(request.url==='/trace'?trace:rows).push(item);
   response.writeHead(200,headers).end();return;
  }
  let content,type='text/javascript';
  if(request.url==='/'){content=page;type='text/html';}
  else if(request.url==='/production.wasm'){content=wasm;type='application/wasm';}
  else if(request.url==='/probe'){content=probe;type='application/octet-stream';}
  else if(request.url==='/packages/paludarium-wasm/coordinator.mjs')content=coordinator;
  else {const path=resolve(root,'.'+new URL(request.url,'http://localhost').pathname);if(!path.startsWith(root+sep))throw new Error('path');content=await readFile(path);}
  response.writeHead(200,{...headers,'Content-Type':type}).end(content);
 }catch(error){if(!response.headersSent)response.writeHead(error.code==='ENOENT'?404:500,headers).end(String(error));else response.destroy(error);}
});
await mkdir(outputDirectory,{recursive:true});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const {firefox}=await import(pathToFileURL(resolve('spikes/wasm-threads/node_modules/playwright/index.mjs')));
let browser,error,version;
try {
 browser=await firefox.launch({timeout:30000});version=browser.version();const tab=await browser.newPage();
 await tab.goto(`http://127.0.0.1:${server.address().port}/`,{timeout:30000});
 await tab.waitForFunction(()=>window.__diagnosticDone,{},{timeout:150000});
 error=await tab.evaluate(()=>window.__diagnosticError??null);
}catch(cause){error=String(cause);}
finally {
 if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
 await writeFile(resolve(outputDirectory,'task-diagnostic.json'),JSON.stringify({diagnostic_only:true,version,error,module_sha256:hash(wasm),probe_sha256:hash(probe),coordinator_source_sha256:hash(original),rows,trace},null,2)+'\n');
}
console.log(JSON.stringify({version,error,trials:rows.length,traceEvents:trace.length}));
if(error||rows.length!==3||rows.some(({row})=>row.exit!==0||row.timed_out))process.exitCode=1;
