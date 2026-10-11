import { readFile, readdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
export const population = ['index.mjs', 'coordinator.mjs', 'execution.mjs', 'worker-support.mjs', 'filesystem-snapshot.mjs'];
// Conservatively count every nonempty non-comment-only line, including braces.
// V8 offsets are UTF-16 offsets, as are JavaScript string indices.
export function lines(source, scripts) {
  let offset = 0;
  let comment = false;
  return source.split('\n').flatMap((line, index) => {
    const start = offset; offset += line.length + 1;
    const trimmed = line.trim();
    const wasComment = comment;
    if (trimmed.startsWith('/*') && !trimmed.includes('*/')) comment = true;
    if (comment && trimmed.includes('*/')) comment = false;
    if (!trimmed || trimmed.startsWith('//') || wasComment || trimmed.startsWith('/*')) return [];
    const positions = [];
    for (let i = 0; i < line.length; i++) if (!/\s/.test(line[i])) positions.push(start + i);
    const hit = scripts.some(script => positions.some(position => {
      // Each function is independent; nested uncalled functions must not inherit
      // the containing module's execution count.
      const candidates = script.functions.flatMap(fn => fn.ranges)
        .filter(range => range.startOffset <= position && position < range.endOffset);
      if (!candidates.length) return false;
      const narrowest = candidates.reduce((a, b) =>
        a.endOffset - a.startOffset <= b.endOffset - b.startOffset ? a : b);
      return narrowest.count > 0;
    }));
    return [{ line: index + 1, hit }];
  });
}
export async function aggregate(rawDirectory, root) {
  const scripts = [];
  for (const name of await readdir(rawDirectory)) {
    if (!name.endsWith('.json')) continue;
    scripts.push(...JSON.parse(await readFile(resolve(rawDirectory, name), 'utf8')).result);
  }
  const files = [];
  for (const name of population) {
    const path = resolve(root, 'packages/paludarium-wasm', name);
    const matched = scripts.filter(script => script.url.startsWith('file:') && fileURLToPath(script.url) === path);
    const measured = lines(await readFile(path, 'utf8'), matched);
    files.push({ path: `packages/paludarium-wasm/${name}`, raw_scripts: matched.length,
      lines: measured.length, hit: measured.filter(line => line.hit).length, measured });
  }
  const total = files.reduce((sum, file) => ({ lines: sum.lines + file.lines, hit: sum.hit + file.hit }), { lines: 0, hit: 0 });
  return { population, definition: 'all nonempty non-comment-only lines, including structural lines; narrowest V8 range, merged across processes and Workers', files, total,
    passed: files.every(file => file.raw_scripts > 0 && file.lines > 0) && total.hit / total.lines >= 0.8 };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [raw, output] = process.argv.slice(2);
  const report = await aggregate(raw, process.cwd());
  await writeFile(output, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ total: report.total, passed: report.passed }));
  if (!report.passed) process.exitCode = 1;
}
