/** Decode version 1 (u64 ns) or version 2 (signed i128 ns) filesystem data. */
export function decodeSnapshot(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const decoder = new TextDecoder(); let offset = 0;
  const requireBytes = length => { if (length > bytes.length - offset) throw new Error("invalid filesystem snapshot"); };
  const u32 = () => { requireBytes(4); const value = view.getUint32(offset, true); offset += 4; return value; };
  const u64 = () => { requireBytes(8); const value = view.getBigUint64(offset, true); offset += 8; return value; };
  const i128 = () => { const low = u64(); requireBytes(8); const high = view.getBigInt64(offset, true); offset += 8; return (high << 64n) + low; };
  const chunk = () => { const length = u32(); requireBytes(length); const value = bytes.slice(offset, offset + length); offset += length; return value; };
  let count = u32(), version = 1;
  if (count === 0xffffffff) { version = u32(); if (version !== 2) throw new Error("unsupported filesystem snapshot version"); count = u32(); }
  if (count > Math.floor((bytes.length - offset) / (version === 2 ? 44 : 36))) throw new Error("invalid filesystem snapshot count");
  const entries = [];
  for (let index = 0; index < count; index++) {
    const path = decoder.decode(chunk()), mode = u32(), inode = u64(), links = u64();
    const mtimeNs = version === 2 ? i128() : u64(), content = chunk();
    entries.push({ path, mode, inode, links, mtimeNs, content });
  }
  if (offset !== bytes.length) throw new Error("invalid filesystem snapshot length");
  return entries;
}
