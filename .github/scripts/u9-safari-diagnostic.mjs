import {createServer} from 'node:http';
import {readFile,writeFile,realpath} from 'node:fs/promises';
import {resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {setTimeout as sleep} from 'node:timers/promises';
import {once} from 'node:events';
const started=Date.now(),deadline=started+28000;
const controller=new AbortController();
const timer=setTimeout(()=>controller.abort(Error('28 second operation deadline (2 seconds reserved for cleanup)')),Math.max(1,deadline-Date.now()));
const staticRoot=await realpath(process.env.SAFARI_STATIC_ROOT??fileURLToPath(new URL('.',import.meta.url)));
const server=createServer(async(req,res)=>{try{const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const path=await realpath(resolve(staticRoot,name==='/'?'index.html':'.'+name));if(!path.startsWith(staticRoot+sep)){res.writeHead(404).end();return}res.writeHead(200,{'Content-Type':path.endsWith('wasm')?'application/wasm':path.endsWith('mjs')?'text/javascript':path.endsWith('json')?'application/json':'text/html','Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp'});res.end(await readFile(path))}catch(error){res.writeHead(404).end(String(error))}});
let driver,id,base,report,cleanup={driver_reaped:false,server_closed:false};
async function api(method,path,body,signal=controller.signal){console.error(JSON.stringify({phase:'request',method,path,elapsed:Date.now()-started}));signal.throwIfAborted();const response=await fetch(base+path,{method,headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal});const json=await response.json();console.error(JSON.stringify({phase:"response",method,path,status:response.status,elapsed:Date.now()-started}));if(!response.ok)throw Error(JSON.stringify(json));return json.value}
try{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve)});
 // Reserve an available driver port without changing Safari's settings.
 const probe=createServer();await new Promise(resolve=>probe.listen(0,'127.0.0.1',resolve));const port=probe.address().port;await new Promise(resolve=>probe.close(resolve));base=`http://127.0.0.1:${port}`;
 const executable=process.env.SAFARI_DRIVER_EXECUTABLE??'/usr/bin/safaridriver';
 const args=process.env.SAFARI_DRIVER_ARGS?JSON.parse(process.env.SAFARI_DRIVER_ARGS).map(arg=>arg.replaceAll('{port}',String(port))):['--port',String(port)];
 driver=spawn(executable,args,{stdio:['ignore','ignore','pipe']});
 driver.stderr.on('data',data=>console.error(String(data)));driver.on('exit',(code,signal)=>console.error(JSON.stringify({driver_exit:code,signal})));driver.on('error',error=>controller.abort(error));
 if(process.env.SAFARI_DRIVER_PID_FILE)await writeFile(process.env.SAFARI_DRIVER_PID_FILE,String(driver.pid));
 while(true){controller.signal.throwIfAborted();try{await api('GET','/status');break}catch(error){console.error(String(error));controller.signal.throwIfAborted();await sleep(100,undefined,{signal:controller.signal})}}
 const session=await api('POST','/session',{capabilities:{alwaysMatch:{browserName:'safari'}}});id=session.sessionId;
 await api('POST',`/session/${id}/url`,{url:`http://127.0.0.1:${server.address().port}${process.env.SAFARI_ENTRY_PATH??'/'}`});
 while(!report){report=await api('POST',`/session/${id}/execute/sync`,{script:'return window[arguments[0]]||null',args:[process.env.SAFARI_REPORT_KEY??'report']});if(!report)await sleep(100,undefined,{signal:controller.signal})}
 report={browserVersion:session.capabilities.browserVersion,platform:session.capabilities.platformName,...report};
 process.exitCode=report&&!report.error?0:1;
}catch(error){report={error:String(error)};process.exitCode=1}
finally{
 clearTimeout(timer);controller.abort();
 // Cleanup requests have their own short abort bound, never an unbounded await.
 if(id)await api('DELETE',`/session/${id}`,undefined,AbortSignal.timeout(500)).catch(()=>{});
 if(driver){const reaped=once(driver,'exit').catch(()=>{});if(driver.exitCode===null&&driver.signalCode===null){driver.kill('SIGTERM');const kill=setTimeout(()=>driver.kill('SIGKILL'),500);await reaped;clearTimeout(kill)}cleanup.driver_reaped=driver.exitCode!==null||driver.signalCode!==null}
 server.closeAllConnections();await new Promise(resolve=>server.close(resolve));cleanup.server_closed=!server.listening;
 console.log(JSON.stringify({...report,elapsed_ms:Date.now()-started,cleanup}));
}
