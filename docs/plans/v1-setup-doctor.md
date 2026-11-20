# v1-setup-doctor: install, restore and check

Status: approved, step 3 of 4 of the bell-harness v1 plan (implemented by Claude directly at the user's request)

## Context
Step 3 adds the two commands that make the harness portable: `bin/setup` installs it into a home directory with a recorded backup and can undo itself, and `bin/doctor` reports whether a machine matches the harness. Both are tested against temporary home directories with stub `claude` and `codex` commands. Success: `scripts/check` passes with the new tests and the real home directory is untouched.

## Decisions
- D1: `~/.claude/CLAUDE.md` is a regular file whose first line imports the harness file, not a symlink, and setup treats it as satisfied while that first line is in place -- why: Claude writes its own memory edits into this file, and they must stay on the machine instead of landing in the public repository -- by: user -- paths: bin/setup lib/harness.py
- D2: Restore undoes settings key by key and deny entry by deny entry, and skips anything changed since setup -- why: Claude and the user edit settings after setup, and copying the old file back would erase those edits -- by: user -- paths: bin/setup
- D3: Entries named `paseo*`, `synced` or `.system` are never moved, linked or reported -- why: other tools manage them -- by: user -- paths: lib/harness.py
- D4: The test copy of the harness is the working tree committed into a fresh repository rather than a `git clone --local` -- why: a clone holds only committed files, so the new scripts would be missing before their own commit -- by: observed -- paths: tests/test_setup.py

## Scope / Non-goals
- In: the files under Changes by file and one commit.
- Out: running either command on the real home directory (a later, explicit step), editing `~/.codex/config.toml` (doctor only reports on it), skills and README (step 4).
- Python 3.9 standard library, POSIX sh and git only.

## What already exists
- `tests/harness_env.py`: `make_env`, `write_stub`, `init_repo`. Use it for every subprocess.
- `config/claude-settings.json`, `config/bell-harness.rules`, `config/retire.json`, `global/AGENTS.md`, `global/CLAUDE.md`, `git/hooks/`.
- `lib/patterns.py` (`HOME_PATHS`), `lib/privacy.py` and `lib/decisions.py` (`check`).

## Changes by file
1. `bin/setup` NEW, python3, executable (Interfaces §1-§3).
2. `bin/doctor` NEW, python3, executable (§4).
3. `lib/harness.py` NEW: code shared by setup and doctor (paths, the managed-entry rules, manifest reading).
4. `tests/test_setup.py`, `tests/test_doctor.py` NEW (Acceptance 1-2).
5. `docs/plans/v1-setup-doctor.md` (this spec) and `docs/plans/evidence/v1-setup-doctor/check.txt`.

## Interfaces
§1 What `bin/setup` manages, with `H` = the repository root (resolved real path) and `~` = `$HOME`:
- Skill links: for every directory `H/skills/<name>/` that contains `SKILL.md`, a symlink `~/.claude/skills/<name>` and `~/.agents/skills/<name>` pointing to it. A harness link whose skill no longer exists in `H/skills/` is removed. An entry is "managed" when it is a symlink whose target lies inside `H`.
- Instruction files: `~/.codex/AGENTS.md` is a symlink to `H/global/AGENTS.md`. `~/.claude/CLAUDE.md` is a regular file whose only content is `@<H>/global/CLAUDE.md` followed by a newline; it is regular so that Claude's own memory edits land in it rather than in the public repository.
- `~/.codex/rules/bell-harness.rules` is a symlink to `H/config/bell-harness.rules`.
- `git config --global core.hooksPath` is `H/git/hooks`.
- `~/.claude/settings.json` contains every key of `H/config/claude-settings.json`: objects merge recursively, `permissions.deny` gains missing entries (existing entries and order kept), scalars take the fragment's value. All other keys, including `hooks` and `enabledPlugins`, stay byte-for-byte equivalent after JSON parsing.
- Retirement: each path in `H/config/retire.json` `paths`, plus `~/.bell-harness/retire.local.json` `paths` when that file exists, is moved into the backup when it exists and is not managed. Each id in `claude_plugins` that is enabled in `~/.claude/settings.json` is uninstalled with `claude plugin uninstall <id>` before the settings merge.
- Never touched, in code and in tests: entries named `paseo*`, `synced` or `.system`, and any path outside `~/.claude`, `~/.agents`, `~/.codex`, `~/.bell-harness` and the global git config.

§2 `bin/setup [--dry-run]`
1. Preflight, with no changes: `git`, `python3` and `claude` and `codex` (both may be absent; report it) on PATH; global `user.name` and `user.email` set; `~/.claude/settings.json` absent or valid JSON; global `core.hooksPath` unset or already `H/git/hooks`. Any failure prints `setup: <reason>` and exits 2.
2. Plan: list every action needed to reach §1, each printed as one line with `~` in place of the home path. An already-satisfied item produces no action. With `--dry-run`, print the plan and exit 0.
3. Apply: create `~/.bell-harness/backups/<UTC timestamp>/` only when at least one action runs. Before each action that replaces or moves something, move the old item into `<backup>/home/<home-relative path>`. After each finished action append one JSON line to `<backup>/manifest.jsonl` (`{"action": ..., "path": ..., "previous": ...}`, flushed and fsynced), recording settings changes per key path with the previous value or `absent`. Settings are written atomically (temporary file, then rename) with mode 0600, through to the target if the file is a symlink, and only when the content changes; re-read the file's hash just before the rename and abort that action if it changed meanwhile.
4. Print `setup: done (<n> actions, backup <id>)` or `setup: nothing to do`, then run `bin/doctor`.
A second run right after a successful run reports `setup: nothing to do` and creates no backup.

§3 `bin/setup --restore <id>|all [--dry-run]`
- Undo the actions of backup `<id>` (or of every backup, newest first) in reverse order. An action is undone only when the current state still equals what setup left; otherwise print `restore: skipped <path> (changed since setup)` and continue.
- Settings are restored key by key and deny entry by deny entry, never by copying the old file back, so later changes by Claude survive.
- Print the reinstall command for each uninstalled plugin (`claude plugin install <id>`) instead of running it.
- Rename a fully processed backup to `<id>.restored`.

§4 `bin/doctor [--project <path>] [--discovery]`
- Prints one line per check, `PASS|WARN|FAIL <check>: <detail>`, with `~` in place of the home path, and exits 1 when any line is FAIL.
- Machine checks: prerequisites from §2 (FAIL for git, python3 and git identity; WARN for a missing `claude` or `codex`); every §1 item in place (FAIL); no retired path present (WARN naming it, with the setup command); no enabled plugin from `claude_plugins` (WARN); unmanaged entries in `~/.claude/skills` and `~/.agents/skills` other than the never-touched names (WARN, listing them); a `model =` line at the top level, in a `[profiles.*]` table of `~/.codex/config.toml`, or in `~/.codex/*.config.toml` (WARN: pinned model); uncommitted changes in `H` (WARN); `codex mcp list` lacking `playwright` or `chrome-devtools` (WARN, printing `codex mcp add playwright -- npx @playwright/mcp@latest` or `codex mcp add chrome-devtools -- npx chrome-devtools-mcp@latest`).
- `--project <path>`: `AGENTS.md` has the headings of `templates/AGENTS.md` (WARN per missing heading); `CLAUDE.md` absent or with first non-empty line `@AGENTS.md` (WARN); `.harness.json` parses (FAIL otherwise); a repo-local `core.hooksPath` (WARN: harness hooks bypassed); commits in `@{u}..HEAD`, or the last 20 without an upstream, whose message the harness `commit-msg` hook rejects (WARN listing short hashes). Every problem `lib/decisions.check(<path>)` returns (malformed record, duplicate id, unknown `supersedes` target, a decision in force citing a missing path) is a WARN `stale decision: <problem>`.
- `--discovery` (live): in a temporary directory, start `claude -p "Reply OK" --output-format stream-json --verbose --max-turns 1`, read events until the first `system`/`init` event, then stop the process; its `skills` list must contain every harness skill name, no name from `retire.json` (the last path component, without `.md`), and no name starting with a retired plugin's prefix (for example `taste-skill:`). `codex debug prompt-input "probe"` (no model call) must list every harness skill as `.../<name>/SKILL.md` and none of the retired names. A missing host is a WARN. The instruction files are checked statically by the machine checks, because the init event does not list imported memory files.

## Failure modes
| Situation | How it shows | Handling |
|---|---|---|
| Crash in the middle of setup | Partial install | The manifest holds every finished action; `--restore <id>` undoes them |
| Claude rewrites settings during setup | Lost write | Hash re-check before rename; abort that action with a message |
| A non-harness link or file sits where a link goes | Conflict | Back it up, then link; recorded in the manifest |
| A test writes into the real home | Guard failure | Every subprocess uses `harness_env.make_env` |
| Something cannot be done as written | Deviation | Stop and report the exact command and error |

## Acceptance tests
1. `tests/test_setup.py`, each in a temporary home built by `harness_env` with stub `claude` (records its arguments; prints fixture JSON for `plugin`, `-p` and `--version`) and stub `codex`, and a copy of this repository's working tree (tracked and untracked, not ignored files, committed into a fresh repository so uncommitted work is tested too) with fixture skills `probe` and `spec` as `H`:
   - fixtures: every retired path, an old `~/.claude/skills/spec` directory, a foreign symlink in `~/.agents/skills`, `paseo-x` and `synced` entries, a settings file with `hooks`, `enabledPlugins` holding `codex@openai-codex` and `taste-skill@taste-skill`, an unrelated key and one existing deny rule;
   - after `bin/setup`: every §1 item holds; retired items, the old `spec` and the foreign link are in the backup under their home-relative paths; the stub recorded `plugin uninstall taste-skill@taste-skill`; `hooks`, `enabledPlugins` (minus the uninstalled plugin as the stub reports it), the unrelated key and the existing deny rule are unchanged; `paseo-x` and `synced` are untouched; no output line contains the temporary home path;
   - a second run prints `setup: nothing to do` and adds no backup directory; `--dry-run` on a fresh fixture changes nothing;
   - after removing one skill directory from `H` and rerunning, its two links are gone;
   - `--restore <id>` returns the fixture tree (paths, types, link targets, file hashes) and the settings keys to the pre-setup state, except a settings key changed after setup, which keeps its new value and prints `restore: skipped`;
   - a preflight failure (invalid settings JSON, or a foreign global `core.hooksPath`) exits 2 and changes nothing.
2. `tests/test_doctor.py`: on the installed fixture `bin/doctor` exits 0; breaking one skill link gives exit 1 and a FAIL line naming it; a leftover retired path and a pinned `model =` in `[profiles.day]` each give a WARN; `--project` on a temporary repository with a template-based `AGENTS.md` has no FAIL, and a commit made with `--no-verify` and subject `bad message` gives a WARN with its hash; a decision in the temporary repository citing a deleted path gives a `stale decision` WARN; `--discovery` with stubs printing fixture output passes, and fails when a skill name is missing from the fixture.
3. `scripts/check` exits 0 and prints `GUARD: real home unchanged`; `python3 lib/privacy.py` prints `PRIVACY: clean`.
4. One new commit `feat(setup): add install, restore and doctor commands` with an empty body; `git/hooks/commit-msg` accepts it; it adds exactly the files in Changes by file; `git status --porcelain` prints nothing.

## Done criteria
Acceptance 1-4 hold AND nothing outside this directory changed.
