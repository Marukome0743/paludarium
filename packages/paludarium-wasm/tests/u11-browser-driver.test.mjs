import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
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
test("unsupported browser does not launch a substitute", async () => assert.rejects(runBrowser("webkit", "http://127.0.0.1/"), /Unsupported actual browser/));
test("unbounded browser deadline rejected before launch", async () => assert.rejects(runBrowser("safari", "http://127.0.0.1/", 0), /Invalid external browser deadline/));
