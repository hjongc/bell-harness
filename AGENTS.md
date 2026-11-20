# bell-harness

A public harness shared by Claude Code and Codex: global instruction files, skills, git hooks, and the scripts that install and check them. `bin/setup` installs it on a machine, and the MIT license lets anyone reuse it.

## Working in this repository

- Changes follow a spec in `docs/plans/`. The spec named in the request defines the scope and the completion check.
- Run `scripts/check` before you report completion and include its output. It runs the offline tests, the privacy scan, and a guard that fails if the real home directory changed.
- Tests build a temporary home directory with stub `claude` and `codex` commands. Applying the harness to a real machine is a separate step the user asks for, so tests leave the real `~/.claude`, `~/.codex`, `~/.agents` and the global git config as they are.
- Write for Python 3.9 and bash 3.2 with the standard library only. Desktop apps can run git hooks with the system Python, so newer syntax would break commits.
- This repository is public. Tracked files and commit messages hold no personal data: write `~` instead of absolute home paths, and leave out private project or company names, personal email addresses and secrets. `python3 lib/privacy.py` checks this, including the terms in the untracked `.private-terms` file.
- When a change alters behavior that README.md, SOURCES.md or a skill describes, update that file in the same change.

## Sources of truth

Decisions live in `docs/plans/<slug>.md` under `## Decisions`; `python3 lib/decisions.py` checks their format and cited paths.

| Task | Look at | Constraints and why |
|---|---|---|
| Git hooks | `git/hooks/`, `tests/test_hooks.py` | Python 3.9, standard library (v1-repo#D1); commit format (v1-hooks-config#D1) |
| Install and check scripts | `bin/`, `lib/harness.py`, `tests/test_setup.py`, `tests/test_doctor.py` | Tests use a temporary home only (v1-repo#D2) |
| Instruction files and template | `global/`, `templates/AGENTS.md`, `tests/test_instructions.py` | Line limits, no emphasis (v1-hooks-config#D2); no pinned model (v1-hooks-config#D3) |
| Decision records | `lib/decisions.py`, `tests/test_decisions.py` | Format and no recall hook (v1-memory#D1, v1-memory#D2) |
| Anything tracked | `lib/privacy.py`, `.private-terms` | Public repository, no personal data (v1-repo#D3) |

## Commits

`type(scope): imperative summary` in English, at most 72 characters. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Leave out `Co-Authored-By` and other attribution trailers.
