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
