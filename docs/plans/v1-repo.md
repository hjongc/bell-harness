# v1-repo: public repository skeleton

Status: implemented (1cce749), step 1 of 4 of the bell-harness v1 plan

## Context
bell-harness becomes a public, MIT-licensed repository that installs one harness for Claude Code and Codex on every machine of its owner. This step clears non-public material out of the working tree, adds the license and the repository instructions, adds offline checks that protect privacy and the real home directory, and records the first commit. Success: `scripts/check` passes and the first commit contains exactly the files listed in Acceptance 4.

## Decisions
- D1: Hooks, tests and scripts run on Python 3.9 and bash 3.2 with the standard library only -- why: desktop apps run git hooks with the macOS system Python and a short PATH, so newer syntax or a dependency breaks commits -- by: user -- paths: git/hooks lib scripts/check tests/test_python39.py
- D2: Tests run against a temporary home with stub `claude` and `codex` commands, and `scripts/check` fails when the real home changed -- why: applying the harness to a real machine is a separate step the user asks for, so a test must never do it by accident -- by: user -- paths: scripts/check tests/harness_env.py
- D3: Tracked files and commit messages hold no personal data; `lib/privacy.py` checks them, including the terms in the untracked `.private-terms` file -- why: the repository is public -- by: user -- paths: lib/privacy.py lib/patterns.py
- D4: The repository is MIT-licensed and publishes only the harness; earlier plans, pilots and vendored code move to an untracked archive instead of being deleted -- why: the user chose to publish the harness and to lose nothing from the old setup -- by: user -- paths: LICENSE .gitignore

## Scope / Non-goals
- In: moving the paths listed below into `.archive/`, the new files below, `git init -b main`, one commit.
- Out: git hooks, global instruction files, skills, `bin/setup`, `bin/doctor`, README and SOURCES (later steps). Nothing outside this directory changes: the real `~/.claude`, `~/.codex`, `~/.agents` and the global git config stay as they are.
- No dependencies beyond the Python 3.9 standard library, bash 3.2 and git.

## What already exists
- `tasks/lessons.md`: keep it unchanged.
- The earlier secret-scan design in `docs/plans/harness-core.md` §2 (moved to `.archive/docs/plans/` by change 1). Interfaces §1 replaces its patterns.

## Changes by file
Paths are relative to the repository root.
1. Move into `.archive/`, keeping each relative path: `.gstack-pilot/`, `vendor/`, `.claude/`, `.agents/`, `.playwright-mcp/`, `docs/research/`, `docs/plans/evidence/`, and every `docs/plans/*.md` except `docs/plans/v1-*.md`. Before replacing them, copy the current `AGENTS.md`, `CLAUDE.md` and `.gitignore` into `.archive/root/`. Delete nothing.
2. `.gitignore` REPLACE with these lines: `.archive/`, `.private-terms`, `.DS_Store`, `__pycache__/`, `*.pyc`.
3. `LICENSE` NEW: the standard MIT License text with the line `Copyright (c) 2026 hjongc`.
4. `AGENTS.md` REPLACE with Appendix A verbatim. `CLAUDE.md` REPLACE with the single line `@AGENTS.md`.
5. `lib/patterns.py` NEW (Interfaces §1).
6. `lib/privacy.py` NEW (Interfaces §2).
7. `scripts/check` NEW, executable, `#!/usr/bin/env python3` (Interfaces §3).
8. `tests/test_privacy.py`, `tests/test_python39.py` NEW (Acceptance 1-2).
9. `docs/plans/evidence/v1-repo/check.txt` NEW: the complete output of the final `scripts/check` run.

## Interfaces
§1 `lib/patterns.py`
- `SECRET_PATTERNS`: list of `(kind, compiled regex)`, checked in this order:
  - `anthropic-key`: `sk-ant-[A-Za-z0-9_-]{20,}`
  - `openai-key`: `(?<![A-Za-z0-9])sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{32,}`
  - `github-token`: `\bgh[pousr]_[A-Za-z0-9]{36,}` and `\bgithub_pat_[A-Za-z0-9_]{20,}`
  - `aws-key`: `\bA(?:KI|SI)A[0-9A-Z]{16}\b`
  - `private-key`: `-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----`
  - `assigned-secret`, case-insensitive: an identifier containing `api_key`, `api-key`, `apikey`, `secret`, `password` or `token`, then optional spaces, `:` or `=`, optional spaces, and a quoted value of at least 12 non-space characters that contains a letter and a digit and does not start with `${`, `{{` or `<`.
- `HOME_PATHS`: `/Us[e]rs/[^/\s]+` and `/home/[a-z][^/\s]*`.
- `EMAIL`: a conventional address regex. `EMAIL_ALLOW`: addresses ending in `@users.noreply.github.com`, `@example.com`, `@example.org` or `@example.net`.
- Write every pattern literal so that it does not match its own source text. The `[e]` in `HOME_PATHS` is the model.

§2 `lib/privacy.py`
- `scan(root)` returns a list of `(location, kind)`; `location` is `path:line` or `commit <short-hash>`.
- Files: `git ls-files -co --exclude-standard` when `root` is inside a git work tree; otherwise every file under `root` except `.git/`, `.archive/`, `__pycache__/` and `.private-terms`. Skip a file whose first 8 KiB contain a NUL byte.
- Kinds: every `SECRET_PATTERNS` kind; `home-path`; `email` for an address outside `EMAIL_ALLOW`; `private-term` for a case-insensitive substring listed in `.private-terms` (one term per line; blank lines and lines starting with `#` ignored; a missing file means no terms).
- When the repository has commits, also scan the output of `git log --all --format=%an%n%ae%n%cn%n%ce%n%B` with the same rules.
- `.privacy-allow` (optional, tracked): lines of `<fnmatch path glob> <kind>`; a matching hit is skipped.
- CLI `python3 lib/privacy.py [root]` (default: the repository root): print `PRIVACY: <location>: <kind>` for each hit and never the matched text. With no hits, print `PRIVACY: clean` and exit 0; otherwise exit 1.

§3 `scripts/check`
1. Snapshot the real home directory, taken from `os.path.expanduser("~")` before anything else runs:
   - for `.claude/skills`, `.agents/skills`, `.codex/skills`, `.codex/rules` and `.claude/commands`: the sorted entry names with their type and symlink target;
   - the SHA-256, or `missing`, of `.claude/settings.json`, `.claude/CLAUDE.md` and `.codex/AGENTS.md`;
   - the output of `git config --global --get core.hooksPath`.
2. Run `unittest` discovery with `tests/` as both the start directory and the top-level directory, verbosity 2. There is no `tests/__init__.py`; test modules add the repository's `lib/` to `sys.path` themselves.
3. Snapshot again. Print `GUARD: changed <item>` for each difference, or `GUARD: real home unchanged` when there is none.
4. Exit 0 only when every test passed and the guard found no change.
Tests pass modified environment variables only to subprocesses and never modify `os.environ` of the test process.

## Failure modes
| Situation | How it shows | Handling |
|---|---|---|
| The sandbox refuses a move | Partial archive | Request the permission. If it is still refused, stop and report the exact command and error; leave the rest for the reviewer |
| The sandbox refuses `git init` or `git commit` | No commit | Request the permission. If it is still refused, stop after Acceptance 1-3 pass and report the exact command and error |
| A new file contains a privacy hit | `scripts/check` fails | Fix the file. Add no `.privacy-allow` entries in this step |
| A test fixture looks like a secret or a home path | The repository scan flags itself | Build fake values at runtime by string concatenation; never write them as literals |

## Acceptance tests
1. `tests/test_privacy.py`: synthetic files written to a temporary directory at runtime produce exactly the expected kinds, covering an `sk-proj-` key, an Anthropic key, a GitHub token, an `OPENAI_API_KEY="..."` assignment, a home path, a personal email and a private term. These produce no hit: `token = "${TOKEN}"`, `api_key = "<your-key>"`, an `@users.noreply.github.com` address. A `.privacy-allow` line suppresses its hit. The printed output never contains a matched value. The test also scans the repository itself and expects no hits.
2. `tests/test_python39.py`: every `.py` file and every file whose first line is a python3 shebang, among `git ls-files -co --exclude-standard` (or the file walk of §2 before `git init`), parses with `ast.parse(source, feature_version=(3, 9))`.
3. `scripts/check` prints `GUARD: real home unchanged` and exits 0.
4. `git ls-files` prints exactly: `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `LICENSE`, `docs/plans/evidence/v1-repo/check.txt`, `docs/plans/v1-repo.md`, `lib/patterns.py`, `lib/privacy.py`, `scripts/check`, `tasks/lessons.md`, `tests/test_privacy.py`, `tests/test_python39.py`.
5. `git log --format='%ae%n%s%n%b'` shows exactly one commit: the author email ends in `@users.noreply.github.com`, the subject is `chore: initialize the public harness repository`, and the body is empty.
6. Each moved path exists under `.archive/` with its original relative path, for example `.archive/.gstack-pilot/runtime/VERSION`, `.archive/docs/plans/harness-core.md` and `.archive/root/AGENTS.md`.

## Done criteria
`scripts/check` exits 0 AND `python3 lib/privacy.py` prints `PRIVACY: clean` AND Acceptance 4-6 hold AND `git status --porcelain` prints nothing AND nothing outside this directory changed.

## Appendix A: AGENTS.md
```markdown
# bell-harness

A public harness shared by Claude Code and Codex: global instruction files, skills, git hooks, and the scripts that install and check them. `bin/setup` installs it on a machine, and the MIT license lets anyone reuse it.

## Working in this repository

- Changes follow a spec in `docs/plans/`. The spec named in the request defines the scope and the completion check.
- Run `scripts/check` before you report completion and include its output. It runs the offline tests, the privacy scan, and a guard that fails if the real home directory changed.
- Tests build a temporary home directory with stub `claude` and `codex` commands. Applying the harness to a real machine is a separate step the user asks for, so tests leave the real `~/.claude`, `~/.codex`, `~/.agents` and the global git config as they are.
- Write for Python 3.9 and bash 3.2 with the standard library only. Desktop apps can run git hooks with the system Python, so newer syntax would break commits.
- This repository is public. Tracked files and commit messages hold no personal data: write `~` instead of absolute home paths, and leave out private project or company names, personal email addresses and secrets. `python3 lib/privacy.py` checks this, including the terms in the untracked `.private-terms` file.
- When a change alters behavior that README.md, SOURCES.md or a skill describes, update that file in the same change.

## Commits

`type(scope): imperative summary` in English, at most 72 characters. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Leave out `Co-Authored-By` and other attribution trailers.
```
