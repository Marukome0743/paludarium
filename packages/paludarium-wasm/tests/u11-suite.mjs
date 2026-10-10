import { createPaludarium } from "../index.mjs";
import { validateOracle } from "./u11-contract.mjs";
import { compare, observeProgram, probeCases } from "./u11-programs.mjs";
import { compareFilesystem } from "./u11-filesystem.mjs";
export async function runSuite({ wasmUrl, oracle, config, probe, aube, fixtures, onRow = () => {} }) {
  validateOracle(oracle);
  const rows = {}, launch = () => createPaludarium({ wasmUrl });
  for (const item of probeCases()) {
    const launcher = await launch();
    try {
      const row = await observeProgram(launcher, { program: "/probe", args: ["/probe", ...item.args], env: config.environment, files: { "/probe": probe, "/home/u10/.keep": new Uint8Array() } });
      try { compare(oracle.rows[item.name], row, oracle.fixture_root); row.pass = true; }
      catch (cause) { row.pass = false; row.comparison_error = String(cause); }
      rows[item.name] = row; await onRow(item.name, row);
    } finally { await launcher.dispose(); }
  }
  const environment = oracle.guest_environment, fixtureRoot = oracle.fixture_root + "/fixture", cwd = fixtureRoot + "/app";
  if (!environment) throw new Error("Fresh native exact environment is required");
  const files = { "/aube": aube, [environment.HOME + "/.keep"]: new Uint8Array(), [environment.TMPDIR + "/.keep"]: new Uint8Array() }, fileModes = {};
  for (const [relative, data] of Object.entries(fixtures)) { const path = fixtureRoot + "/" + relative; files[path] = data; fileModes[path] = 0o644; }
  const launcher = await launch();
  try {
    const filesystem = await launcher.createFileSystem({ files, fileModes });
    for (const item of config.aube) {
      if (item.before) await filesystem.remove(cwd + "/node_modules", { recursive: true });
      const row = await observeProgram(launcher, { program: "/aube", cwd, args: ["/aube", ...item.args], env: environment, filesystem });
      const entries = await filesystem.snapshot();
      row.filesystem = entries.filter(entry => entry.path !== "/aube").map(entry => ({ ...entry, inode: String(entry.inode), links: String(entry.links), mtimeNs: String(entry.mtimeNs), content: btoa(Array.from(entry.content, byte => String.fromCharCode(byte)).join("")) }));
      try { compare(oracle.rows[item.name], row, oracle.fixture_root, oracle.fixture_root); row.filesystem_comparison = await compareFilesystem(oracle.rows[item.name].filesystem_metadata, entries, fixtureRoot); row.pass = true; }
      catch (cause) { row.pass = false; row.comparison_error = String(cause); }
      rows[item.name] = row; await onRow(item.name, row);
    }
  } finally { await launcher.dispose(); }
  return { rows, complete: Object.keys(rows).length === 14 && Object.values(rows).every(row => row.pass), passed: Object.values(rows).every(row => row.pass) };
}
