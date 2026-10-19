# U11 filesystem comparison

## Fixture inputs and ownership

U10's fixed binaries and three original package.json inputs are unchanged.
U11 sets the three initial regular-file modification times to epoch zero on
native Linux and in the private VFS. Native observations retain the preparation
receipt, exact HOME/TMPDIR and full case configuration. The guest receives those
same environment strings, fixture absolute paths and cwd. This makes aube's
settings_hash identical: even an absent .npmrc contributes its absolute pathname
to the fixed upstream hash (aube v2.6.1 state.rs lines 1684–1705).

Each aube sequence uses one exclusively leased private filesystem. Only after
the previous guest has exited and its Worker stack has been reclaimed does the
runner remove node_modules. Install, frozen install and list therefore observe
the same retained state. The launcher rejects concurrent borrowed filesystem
mutations and cross-launcher/stale handles.

## Full fixture comparison

The comparator requires the complete native and guest fixture path inventories
to match. It compares object kind, permission mode, symlink target, regular file
SHA-256, hardlink count and normalized identity. Equal file contents do not imply
equal hardlink identity. Native inode numbers and guest inode numbers are
normalized to each shared inode's first lexical fixture path. Guest HOME/cache
and temporary files outside the fixture remain in raw observations separately;
the guest binary is bound by its existing binary hash rather than repeatedly
embedding its bytes in every filesystem snapshot.

All three initial inputs retain byte-identical hashes and epoch mtimes. aube's
local_directory_hashes and settings_hash are compared without filtering. The
fixed directory metadata fingerprint hashes path/NUL, size (u64 LE), seconds
(i64 LE), nanoseconds (u32 LE) and executable flag (aube-store tarball.rs
lines 74–86). Equal initial metadata makes this fingerprint equal directly.

Only generated aube-lock.yaml time varies across independent executions. For
state.json and fresh.json, the comparator first verifies lockfile_meta size,
seconds and nanoseconds against the same run's observed actual lockfile. It
also verifies every package_json_meta size/time against the corresponding
actual file. Only then does it map the generated lockfile's seconds/nanoseconds
to the same explicit placeholder and compare the remaining complete JSON.
Both raw state bytes, original SHA-256 and actual timestamps remain available.
This prevents a missing/zero/stale runtime timestamp from becoming a false pass.
Native nanosecond metadata is parsed as a decimal string to retain u64 precision.

## Progress output

The original native and wasm command observations remain diagnostic evidence.
Fixed aube's nonTTY progress uses a two-second heartbeat; a fast native install
has no progress bars while a slower browser can emit bars and a different
completion presentation (progress/ci.rs lines 20–23 and 96–99). Human approval
authorizes U11 install/frozen to use the same official --reporter=append-only
option on both sides. U10 cases are unchanged. stdout/stderr and #1645 remain
required; progress output is not blanket-filtered by the comparator.

## Evidence status

検証済み: initial no-reporter Node14 completed with full fixture metadata
comparisons (node-complete/observations.json). Chromium completed the same
original sequence; Firefox's original sequence exited successfully but its
dynamic progress stderr differed. 検証済み: Firefox153.0 official reporter
sequence completed all fourteen cases (firefox-reporter/observations.json).
Verified final same-head CI38021278452 at signed source7eb1819f52acede33e83775374dd4ee93edf643b: all fourteen cases pass in Node, Chromium, Firefox and real Safari. Raw primary/native observations are under verification/final-7eb-ci; successful Safari raw observations are separately under verification/final-7eb-safari-attempt3. Both use identical module/oracle/guest hashes. Earlier Safari initialization failures remain preserved and are not used as acceptance results. U10's differential runner also uses the same approved official reporter for primary comparisons, with separate original-argv raw observations and stable-outcome checks; cases.json remains unchanged.
