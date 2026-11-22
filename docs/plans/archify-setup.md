# archify-setup: provision Archify through the harness

Status: implemented

## Context

The shared diagram skill defaults to Mermaid and uses Archify for interactive HTML. The user asked to include Archify installation in the harness and commit and push the change.

## Decisions

- D1: Provision Archify through an explicit setup option -- why: the user requested a harness installation path and ordinary setup stays offline under the existing dependency policy -- by: observed -- paths: bin/setup lib/archify.py
- D2: Pin the official release archive and verify its digest before unpacking it into a per-checkout cache -- why: the same opt-in installs the same copy for both hosts without tracking a third-party runtime archive -- by: observed -- paths: .gitignore lib/archify.py lib/harness.py
- D3: Use the existing link and restore actions for the cached Archify skill -- why: the installer already records and reverses host links and replaced entries -- by: observed -- paths: bin/setup lib/harness.py

## Changes by file

1. `lib/archify.py` provisions the official release into an ignored local cache. `.gitignore` excludes the cache.
2. `lib/harness.py` includes a complete cached runtime in skill discovery and link planning. `bin/setup` accepts `--with-archify` and supports a non-mutating preview.
3. `tests/test_setup.py` covers installation, idempotence, restore, dry run, and rejection of an unverified archive or a symlinked cache.
4. `README.md`, `SOURCES.md`, `AGENTS.md`, and `skills/repo-diagrams/references/archify.md` describe installation and provenance. `docs/plans/repo-diagrams.md` links this follow-up, `docs/plans/roadmap.md` tracks it, and `tasks/lessons.md` carries the user's correction from the pilot.
5. This spec records verification.

## Scope and non-goals

- `bin/setup --with-archify` installs the pinned runtime and uses the regular backup for both host links. Later setup and doctor runs discover the cached runtime without downloading it again.
- `bin/setup --with-archify --dry-run` may announce a pending download. It writes neither a cache nor home entries.
- An archive failure stops the opt-in before home changes. Existing install and restore behavior still governs home state. Restore leaves the local release cache available for reuse.
- The base harness remains offline and uses Python's standard library. Archify authoring uses its own Node.js and browser environment. Paid model calls, existing home reconfiguration, and third-party archives or pilot screenshots in the commit are outside scope.

## Acceptance and done condition

Check the real setup entry point in isolated homes. Exercise the default install, opt-in dry run, cache reuse across both host links, an existing unmanaged install restored after replacement, a mismatched archive digest, and a symlinked cache. Run one opt-in with the pinned upstream archive and generate HTML using the installed CLI. `scripts/check`, the privacy and decision checks, and preflight must pass before pushing the scoped commit to the configured upstream branch.

## Verification

- The normal setup command ran in a temporary home with the official v3.2.0
  archive. Its dry run left no cache. The opt-in registered both host links,
  ordinary setup reused the cache, and restore removed both installed links.
- The installed Archify CLI generated standalone HTML. Its receipt reported
  `validate: pass`, `deliver: pass`, `check: pass`, and `browser-check: pass`.
- `scripts/check` reported `Ran 111 tests in 81.351s (4 workers)`, `OK`, and
  `GUARD: real home unchanged`. It included all three Archify setup tests.
- Privacy and decision scans were clean. `bin/doctor --project-only .` passed.
  The full machine check reported existing link mismatches for
  `business-document-design` outside this change.
