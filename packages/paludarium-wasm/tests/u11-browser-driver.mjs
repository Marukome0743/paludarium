// Actual Safari uses Apple's WebDriver; Chromium/Firefox reuse pinned Playwright.
import { spawn } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";

export async function webdriverRequest(base, method, path, body) {
  const response = await fetch(base + path, { method, headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(10000) });
  const payload = await response.json();
  if (!response.ok || !Object.hasOwn(payload, 'value') || payload.value?.error) throw new Error(`WebDriver ${method} ${path}: ${JSON.stringify(payload.value)}`);
  return payload.value;
}

async function stopDriver(driver) {
  if (driver.exitCode !== null || driver.signalCode !== null) return;
  const stopped = new Promise(resolve => driver.once("exit", resolve));
  driver.kill("SIGTERM");
  const force = setTimeout(() => driver.kill("SIGKILL"), 1000);
  try { await stopped; } finally { clearTimeout(force); }
}

async function safari(url, timeout) {
  const port = 4455, base = `http://127.0.0.1:${port}`;
  const driver = spawn("/usr/bin/safaridriver", ["--port", String(port)], { stdio: ["ignore", "pipe", "pipe"] });
  let driverError, sessionId, log = "", phase = "driver-startup", failure;
  driver.on("error", error => { driverError = error; });
  for (const stream of [driver.stdout, driver.stderr]) stream.on("data", bytes => { log = (log + bytes.toString()).slice(-8192); });
  try {
    const startup = Date.now() + 10000;
    for (;;) {
      if (driverError) throw driverError;
      if (driver.exitCode !== null || driver.signalCode !== null) throw new Error(`Safari driver exited: ${driver.exitCode ?? driver.signalCode}; ${log}`);
      try { await webdriverRequest(base, "GET", "/status"); break; }
      catch (error) { if (Date.now() >= startup) throw error; await sleep(100); }
    }
    phase = "session-creation";
    const session = await webdriverRequest(base, "POST", "/session", { capabilities: { alwaysMatch: { browserName: "safari" } } });
    sessionId = session.sessionId;
    if (!sessionId) throw new Error("Safari did not return a session ID");
    phase = "navigation";
    await webdriverRequest(base, "POST", `/session/${sessionId}/url`, { url });
    phase = "script-report";
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      const report = await webdriverRequest(base, "POST", `/session/${sessionId}/execute/sync`, { script: "return window.__u11Report || null;", args: [] });
      if (report) return { environment: "safari", version: session.capabilities?.browserVersion ?? "unknown", ...report };
      await sleep(100);
    }
    throw new Error("Safari page report exceeded external suite deadline");
  } catch (cause) {
    failure = new Error(`Safari ${phase}: ${cause}; driver exit=${driver.exitCode}, signal=${driver.signalCode}, log=${log}`, { cause });
    failure.phase = phase;
    throw failure;
  } finally {
    let cleanupError;
    try { if (sessionId) await webdriverRequest(base, "DELETE", `/session/${sessionId}`); }
    catch (error) { cleanupError = error; }
    await stopDriver(driver);
    if (cleanupError) {
      if (failure) failure.message += `; cleanup: ${cleanupError}`;
      else throw new Error(`Safari cleanup: ${cleanupError}`);
    }
  }
}

export async function runBrowser(name, url, timeout = 600000) {
  if (!Number.isFinite(timeout) || timeout <= 0 || timeout > 1200000) throw new Error("Invalid external browser deadline");
  if (name === "safari") return safari(url, timeout);
  if (!["chromium", "firefox"].includes(name)) throw new Error("Unsupported actual browser");
  const playwright = await import("../../../spikes/wasm-threads/node_modules/playwright/index.mjs");
  const browser = await playwright[name].launch({ timeout: 30000 });
  try {
    const page = await browser.newPage();
    await page.goto(url, { timeout: 30000 });
    await page.waitForFunction(() => window.__u11Report !== undefined, null, { timeout });
    const report = await page.evaluate(() => window.__u11Report);
    return { environment: name, version: browser.version(), ...report };
  } finally { await browser.close(); }
}
