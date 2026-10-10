import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [directory, guestPath, mode = "hello"] = process.argv.slice(2);
const deadline = setTimeout(() => { console.error("packed child 30 second deadline"); process.exit(1); }, 30000);
async function collect(stream) {
  const reader = stream.getReader(); const chunks = [];
  try { while (true) { const row = await reader.read(); if (row.done) return Buffer.concat(chunks).toString(); chunks.push(Buffer.from(row.value)); } }
  finally { reader.releaseLock(); }
}
try {
  // All launcher modules are resolved from the extracted distribution.
  const { createPaludarium } = await import(pathToFileURL(resolve(directory, "index.mjs")));
  if (mode === "import") console.log("packed import PASS");
  else if (mode === "corrupt") {
    await assert.rejects(createPaludarium({ wasmUrl: pathToFileURL(resolve(directory, "paludarium.wasm")) }), WebAssembly.CompileError);
    console.log("corrupt wasm rejected PASS");
  } else {
    const launcher = await createPaludarium({ wasmUrl: pathToFileURL(resolve(directory, "paludarium.wasm")) });
    try {
      const bytes = mode === "invalid" ? new Uint8Array([73]) : new Uint8Array(await readFile(guestPath));
      const guest = launcher.run({ program: "/guest", files: { "/guest": bytes } });
      const timer = setTimeout(() => guest.kill(), 30000);
      try {
        const result = await Promise.allSettled([collect(guest.stdout), collect(guest.stderr), guest.exited]);
        if (mode === "invalid") assert.ok(result.every(row => row.status === "rejected" && row.reason.kind === "invalid-program"));
        else {
          assert.ok(result.every(row => row.status === "fulfilled"));
          assert.equal(result[0].value, "hello\n"); assert.equal(result[1].value, "");
          assert.deepEqual(result[2].value, { kind: "exited", code: 0 });
          console.log(JSON.stringify({ stdout: result[0].value, stderr: result[1].value, exit: result[2].value }));
        }
      } finally { clearTimeout(timer); }
    } finally { await Promise.all([launcher.dispose(), launcher.dispose()]); await launcher.dispose(); }
    await assert.rejects(launcher.diagnostics(), /closed/);
    console.log("packed dispose PASS");
  }
} finally { clearTimeout(deadline); }
// The supervising process requires natural process exit: leaked referenced
// coordinator or nested Workers would keep this process alive and fail its bound.
