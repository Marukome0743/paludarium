# Release verification and publication

## Current status

The workspace and npm package are still `0.0.0`; this is an undecided release
version, and publication preflight rejects it. Nothing has been published by
U15. The eleven public crates are types, host, mmu, vfs, loader, decoder, cpu,
jit, kernel, runtime and paludarium, in the dependency order calculated from
the manifests. Harness and the Rust Wasm adapter have `publish = false`.

The tested toolchain remains `nightly-2026-10-11`. A real external consumer
using the eleven generated crates through a private loopback sparse registry
built successfully. The initial stable 1.99.0 probe failed because every
crate declares MSRV 1.101. The separately installed latest stable 1.99.1 also
failed with exit 101 for the same declared MSRV; both raw failures are retained,
never labeled stable support. The Wasm
adapter additionally needs nightly build-std and atomic-wait support.

## Non-publishing checks

Use the real Python 3.15 executable and project-local coverage 7.16.2:

```sh
python3 -B -m unittest discover -s tests/release -p 'test_*.py' -v
python3 -B scripts/release/check.py --mode validate
python3 -B scripts/release/check.py --mode package-check
```

`package-check` creates an exclusive `target/u15/package-*` directory. It
retains argv, tool SHA, stdout, stderr, real exit/timeout/reaping, source and
lock before/after hashes. The original source is never rewritten. It builds
eleven real `.crate` files, checks all members and normalized dependencies,
builds a crate-external consumer from a temporary sparse registry, probes
stable separately, and builds the production Wasm without diagnostic features.
One npm tarball is inspected and used for all seven distribution boundary
checks, including real Wasm hello, invalid guest cleanup, missing JS and a
corrupt Wasm. A mock upload test is not a registry or OIDC test.

`release-check.yml` is PR/manual/reusable and has no publication credentials.
It measures the fixed policy/package/check file population, each at least
80%, including the actual package path. Existing Rust/JS/workspace/U9 floors
remain unchanged. A branch-only workflow may need a PR and owner Actions
approval before GitHub allows it to run; dispatch registration is not assumed.

## Owner prerequisites before any release

1. Decide the actual semantic version and update Cargo workspace/internal
   dependency versions and npm together. Do not silently select `0.0.0`.
2. Confirm ownership of all eleven crate names and `@paludarium/wasm`.
   crates.io's current Trusted Publishing documentation requires each crate
   to have been published already: initial publication needs an owner API
   token and a separate explicit approval. This workflow does not create a
   long-lived token or silently perform that first publication.
3. Register the exact upstream repository, `release.yml` and `release`
   environment as Trusted Publisher for each crate and the npm package.
   npm requires its package settings, supported runner/CLI and matching
   `repository.url`; npm 12.2.0 with Node 26.12.0 is used here.
4. An upstream administrator must create environment `release`, require
   reviewers, prevent self-review and disable administrator bypass. The
   inspected upstream and fork currently have no environments. The current
   account has no upstream admin/push permission; no protection settings
   were changed or inferred from the YAML environment name.
5. Obtain same-head/source-bound acceptance evidence for FR6.3, FR7.2,
   FR7.3, FR8.2 and FR8.3. The reviewed verification job must emit one
   official `u15-acceptance` artifact with `release-evidence.json`; the
   fetcher rejects absent/ambiguous artifacts, incomplete listings, changed
   ZIP digests and different heads. This acceptance artifact producer is a
   deliberate external gate until the final source's canonical verification
   is reviewed and adopted; it is not fabricated by package unit tests.

The evidence document follows `policy.release_gate`: exact head/tag/repository,
official completed successful quality run identities for every required
purpose, each acceptance ID with its verified artifact digest, and confirmed
Trusted Publisher registration. The authorization step re-fetches GitHub
commit, reachability, environment, run and actual environment-review history.
Evidence from old U14 measurements is historical unless the declared source
and build closure are independently proven equivalent. No same-binary
performance rerun is used to wait for a passing result.

## Publication and recovery

Only after the user explicitly approves the precise version, tag/head,
registries, artifact digests, authentication and protection configuration may
the owner create/push a version tag. This plan did not authorize tag creation
or publication. `release.yml` accepts only an exact `vMAJOR.MINOR.PATCH` after
Python validation, verifies signed main reachability and actual environment
protection before builds, then requires the protected human approval.

Only the publish job receives `id-token: write`. crates-io-auth-action obtains
a short-lived token and revokes it in its post step; npm uses Trusted
Publishing and automatic provenance. All third-party actions are pinned to
officially resolved commit SHAs. The fork is never substituted for upstream.

The publish job checks the previously tested eleven crate artifacts and npm
tarball. Cargo dry-run reassembly must have the approved byte digest before
upload; original source/locks must remain unchanged. Existing versions are
queried first: an equal digest is verified without re-upload, a different
digest or unknown network result stops the sequence. The same npm tarball is
uploaded. Registry checksums/integrity are checked after each upload.

On partial failure, preserve `publication-progress.json`, attempted uploads,
unverified uploads and all logs. Do not delete, replace, move a tag or retry
publication automatically. An owner must inspect registry state and propose
the remaining recovery. A successful workflow alone does not establish
FR10.1: registry retrieval/source/provenance verification is required.

## Official references

- [Cargo publishing](https://doc.rust-lang.org/cargo/reference/publishing.html)
- [Current crates.io Trusted Publishing implementation documentation](https://github.com/rust-lang/crates.io/blob/8b4b7af90bf73b0bbb73b47a29b9de86ed702093/svelte/src/routes/docs/trusted-publishing/%2Bpage.svelte)
- [crates.io authentication action](https://github.com/rust-lang/crates-io-auth-action)
- [npm Trusted Publishing](https://docs.npmjs.com/trusted-publishers/)
- [GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
