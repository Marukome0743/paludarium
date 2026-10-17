import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { EventEmitter } from "node:events";
import { createRequire, syncBuiltinESMExports } from "node:module";
import { runBrowser, webdriverRequest } from "./u11-browser-driver.mjs";
async function endpoint(handler, run) {
  const server = createServer(handler);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  try { await run(`http://127.0.0.1:${server.address().port}`); }
  finally { await new Promise(resolve => server.close(resolve)); }
}
test("WebDriver returns actual response value", async () => endpoint((_, response) => response.end('{"value":{"ready":true}}'), async base => assert.deepEqual(await webdriverRequest(base, "GET", "/status"), { ready: true })));
test("WebDriver POST sends exact capability payload", async () => endpoint((request, response) => { let body = ""; request.on("data", bytes => { body += bytes; }); request.on("end", () => response.end(JSON.stringify({ value: JSON.parse(body) }))); }, async base => assert.deepEqual(await webdriverRequest(base, "POST", "/session", { safari: true }), { safari: true })));
test("WebDriver HTTP failure is retained", async () => endpoint((_, response) => response.writeHead(500).end('{"value":{"message":"driver unavailable"}}'), async base => assert.rejects(webdriverRequest(base, "GET", "/status"), /driver unavailable/)));
test("WebDriver protocol failure rejects even successful HTTP status", async () => endpoint((_, response) => response.end('{"value":{"error":"invalid session id"}}'), async base => assert.rejects(webdriverRequest(base, "DELETE", "/session/stale"), /invalid session id/)));
test("WebDriver malformed response rejects", async () => endpoint((_, response) => response.end('not json'), async base => assert.rejects(webdriverRequest(base, "GET", "/status"))));
test("WebDriver missing protocol envelope rejects", async () => endpoint((_, response) => response.end('{}'), async base => assert.rejects(webdriverRequest(base, "GET", "/status"))));
test("WebDriver request honours a supplied timeout against a slow endpoint", async () => { let timer; await endpoint((_, response) => { timer = setTimeout(() => response.end('{"value":{"late":true}}'), 2000); }, async base => { try { await assert.rejects(webdriverRequest(base, "GET", "/status", undefined, 100), { name: "TimeoutError" }); } finally { clearTimeout(timer); } }); });
test("unsupported browser does not launch a substitute", async () => assert.rejects(runBrowser("webkit", "http://127.0.0.1/"), /Unsupported actual browser/));
test("unbounded browser deadline rejected before launch", async () => assert.rejects(runBrowser("safari", "http://127.0.0.1/", 0), /Invalid external browser deadline/));
test("Safari session creation alone waits 60000 ms while other WebDriver requests keep 10000 ms", async () => {
  // Stub safaridriver, fetch and AbortSignal.timeout only for this test; everything is restored in finally.
  const childProcess = createRequire(import.meta.url)("node:child_process");
  const original = { spawn: childProcess.spawn, fetch: globalThis.fetch, timeout: AbortSignal.timeout };
  const timeouts = new WeakMap(), requests = [], spawned = [];
  childProcess.spawn = (command, args) => {
    const driver = Object.assign(new EventEmitter(), { exitCode: null, signalCode: null, stdout: new EventEmitter(), stderr: new EventEmitter() });
    driver.kill = signal => { if (driver.signalCode === null) { driver.signalCode = signal; setImmediate(() => driver.emit("exit", null, signal)); } return true; };
    spawned.push({ command, args, driver });
    return driver;
  };
  syncBuiltinESMExports();
  AbortSignal.timeout = ms => { const signal = original.timeout.call(AbortSignal, ms); timeouts.set(signal, ms); return signal; };
  const replies = { "GET /status": { ready: true }, "POST /session": { sessionId: "s1", capabilities: { browserVersion: "stub" } }, "POST /session/s1/url": null, "POST /session/s1/execute/sync": { stub: true }, "DELETE /session/s1": null };
  globalThis.fetch = async (url, init) => {
    const key = `${init.method} ${new URL(url).pathname}`;
    requests.push({ key, timeoutMs: timeouts.get(init.signal) });
    if (!Object.hasOwn(replies, key)) return new Response('{"value":{"error":"unexpected request"}}', { status: 404 });
    return new Response(JSON.stringify({ value: replies[key] }));
  };
  try {
    assert.deepEqual(await runBrowser("safari", "http://127.0.0.1/page", 5000), { environment: "safari", version: "stub", stub: true });
  } finally {
    childProcess.spawn = original.spawn;
    syncBuiltinESMExports();
    globalThis.fetch = original.fetch;
    AbortSignal.timeout = original.timeout;
  }
  assert.deepEqual(spawned.map(({ command, args }) => [command, args]), [["/usr/bin/safaridriver", ["--port", "4455"]]]);
  assert.equal(spawned[0].driver.signalCode, "SIGTERM");
  assert.deepEqual(requests, [
    { key: "GET /status", timeoutMs: 10000 },
    { key: "POST /session", timeoutMs: 60000 },
    { key: "POST /session/s1/url", timeoutMs: 10000 },
    { key: "POST /session/s1/execute/sync", timeoutMs: 10000 },
    { key: "DELETE /session/s1", timeoutMs: 10000 },
  ]);
});
