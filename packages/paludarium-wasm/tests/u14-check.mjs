import { createServer } from "node:http";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { resolve, sep } from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { runBrowser } from "./u11-browser-driver.mjs";
import { runJitSuite } from "./u14-suite.mjs";

const [environment, modulePath, oraclePath, guestDirectory, outputDirectory] = process.argv.slice(2);
if (!outputDirectory || !["node", "chromium", "firefox", "safari"].includes(environment)) throw new Error("usage: u14-check.mjs node|chromium|firefox|safari module oracle guests output");
const root = resolve("."), hash = bytes => createHash("sha256").update(bytes).digest("hex");
const rawOracle = await readFile(oraclePath, "utf8"), oracle = JSON.parse(rawOracle.replace(/("mtime_ns"\s*:\s*)(\d+)/g, '$1"$2"'));
const probe = await readFile(resolve(guestDirectory, "probe")), aube = await readFile(resolve(guestDirectory, "aube"));
if (hash(probe) !== oracle.binary_hashes.probe || hash(aube) !== oracle.binary_hashes.aube) throw new Error("Guest differs from fresh native binary");
const fixtures = {};
for (const name of ["app/package.json", "app/filedep/package.json", "outside/linked/package.json"]) fixtures[name] = new Uint8Array(await readFile("tests/guests/u10/fixtures/" + name));
const input = { oracle, config: oracle.case_config, probe: new Uint8Array(probe), aube: new Uint8Array(aube), fixtures };
if (!input.config) throw new Error("Exact fresh native case config missing");
const report = { schema: 1, environment, module_sha256: hash(await readFile(modulePath)), oracle_sha256: hash(rawOracle),
                 guest_hashes: oracle.binary_hashes, rows: { interpreter: {}, jit: {} }, complete: false };
await mkdir(outputDirectory, { recursive: true });
const persist = () => writeFile(resolve(outputDirectory, "observations.json"), JSON.stringify(report, null, 2) + "\n");
await persist();
const onRow = async (mode, name, row) => {
  report.rows[mode][name] = row; await persist();
  console.log(JSON.stringify({ environment, mode, name, pass: row.pass, seconds: row.seconds, jit: row.jit, error: row.comparison_error ?? row.jit_error }));
};
let server;
try {
  let result;
  if (environment === "node") {
    report.version = process.version;
    result = await runJitSuite({ ...input, wasmUrl: pathToFileURL(resolve(modulePath)), onRow });
  } else {
    const encoded = { ...input, probe: probe.toString("base64"), aube: aube.toString("base64"),
      fixtures: Object.fromEntries(Object.entries(fixtures).map(([name, bytes]) => [name, Buffer.from(bytes).toString("base64")])) };
    const page = `<!doctype html><script type="module">
import{runJitSuite}from'/packages/paludarium-wasm/tests/u14-suite.mjs';
try{if(!crossOriginIsolated)throw Error('Shared memory unavailable');const input=await(await fetch('/input.json')).json();const decode=text=>Uint8Array.from(atob(text),c=>c.charCodeAt(0));input.probe=decode(input.probe);input.aube=decode(input.aube);for(const name of Object.keys(input.fixtures))input.fixtures[name]=decode(input.fixtures[name]);window.__u11Report=await runJitSuite({...input,wasmUrl:'/production.wasm',onRow:async(mode,name,row)=>{await fetch('/row',{method:'POST',body:JSON.stringify({mode,name,row})});}});}catch(error){window.__u11Report={complete:false,passed:false,error:String(error)};}</script>`;
    server = createServer(async (request, response) => {
      const headers = { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp", "Cache-Control": "no-store" };
      try {
        if (request.url === "/") response.writeHead(200, { ...headers, "Content-Type": "text/html" }).end(page);
        else if (request.url === "/input.json") response.writeHead(200, { ...headers, "Content-Type": "application/json" }).end(JSON.stringify(encoded));
        else if (request.url === "/row" && request.method === "POST") {
          const chunks = []; let size = 0;
          for await (const chunk of request) { size += chunk.length; if (size > 16 * 1024 * 1024) throw Error("Evidence row too large"); chunks.push(chunk); }
          const { mode, name, row } = JSON.parse(Buffer.concat(chunks));
          if (!["interpreter", "jit"].includes(mode) || !Object.hasOwn(oracle.rows, name)) throw Error("Unknown evidence row");
          await onRow(mode, name, row); response.writeHead(200, headers).end();
        } else {
          const path = request.url === "/production.wasm" ? resolve(modulePath) : resolve(root, "." + new URL(request.url, "http://localhost").pathname);
          if (request.url !== "/production.wasm" && !path.startsWith(root + sep)) throw Error("Invalid path");
          response.writeHead(200, { ...headers, "Content-Type": path.endsWith(".wasm") ? "application/wasm" : "text/javascript" }).end(await readFile(path));
        }
      } catch (error) { response.writeHead(500, headers).end(String(error)); }
    });
    await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
    result = await runBrowser(environment, `http://127.0.0.1:${server.address().port}/`, 1200000);
  }
  Object.assign(report, result); await persist();
  if (!report.complete || !report.passed || report.caseCount !== 28) throw Error("U14 JIT/interpreter acceptance failed");
} catch (error) { report.error = String(error); await persist(); process.exitCode = 1; }
finally { if (server) await new Promise(resolve => server.close(resolve)); }
