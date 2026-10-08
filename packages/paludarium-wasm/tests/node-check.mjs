import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { runChecks } from "./checks.mjs";
const [wasmPath, nativePath] = process.argv.slice(2);
if (!wasmPath || !nativePath) throw new Error("usage: node-check.mjs <production.wasm> <fresh-native-results.json>");
const watchdog = setTimeout(() => { console.error("Production wasm test process watchdog"); process.exit(1); }, 30000);
try {
  const report = await runChecks({ wasmUrl: pathToFileURL(wasmPath), native: JSON.parse(await readFile(nativePath, "utf8")), readGuest: name => readFile(new URL(`guests/${name}`, import.meta.url)) });
  console.log(JSON.stringify({ environment: "Node Worker", version: process.version, ...report }));
} catch (error) { console.error(error); process.exitCode = 1; }
finally { clearTimeout(watchdog); }
