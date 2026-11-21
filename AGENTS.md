# bell-harness

A public harness shared by Claude Code and Codex: global instruction files, skills, git hooks, and the scripts that install and check them. `bin/setup` installs it on a machine, and the MIT license lets anyone reuse it. Changes follow a spec in `docs/plans/`; the spec named in the request defines the scope and the completion check.

## Non-goals

- No hooks or indexes for memory recall until an eval shows a reproducible failure (v1-memory#D2).
- No dependencies beyond the Python 3.9 standard library, bash 3.2 and git (v1-repo#D1).
- No Windows support in v1.

## Decision priorities

The real home directory stays safe > the repository stays free of personal data > both tools behave the same > less code > convenience.

## Sources of truth

Decisions live in `docs/plans/<slug>.md` under `## Decisions`; `python3 lib/decisions.py` checks their format and cited paths.

| Task | Look at | Constraints and why |
|---|---|---|
| Git hooks | `git/hooks/`, `lib/commit_message.py`, `tests/test_hooks.py` | Python 3.9, standard library: desktop apps run hooks with the system Python (v1-repo#D1); commit format (v1-hooks-config#D1) |
| Install and check scripts | `bin/`, `lib/harness.py`, `tests/test_setup.py`, `tests/test_doctor.py` | Tests use a temporary home only (v1-repo#D2); CLAUDE.md stays a local file (v1-setup-doctor#D1); restore key by key (v1-setup-doctor#D2); validate undo payloads and detect stale links from earlier checkouts (v1.6-regression-loops#D1, v1.6-regression-loops#D2). Keep retirement within real parent directories and guard backup manifest contents (v1.7-path-boundaries#D1, v1.7-path-boundaries#D4) |
| Instruction files and template | `global/`, `templates/AGENTS.md`, `tests/test_instructions.py` | Line limits, no emphasis (v1-hooks-config#D2); no pinned model (v1-hooks-config#D3) |
| Skills | `skills/<name>/SKILL.md`, `tests/test_skills.py`, `SOURCES.md`, `licenses/` | Shared skills, flow in SKILL.md and detail in references (v1.5-audit-fixes#D3, v1-skills#D2); third-party notices kept (v1-skills#D3) |
| Evals | `evals/run.py`, `evals/cases/`, `evals/fixtures/`, `tests/test_evals.py` | Grade observable behavior (v1-evals#D1); live runs stay out of `scripts/check` (v1-evals#D2); Korean answers count (v1-evals#D4); isolate fixture Git context and require graded output (v1.6-regression-loops#D4, v1.6-regression-loops#D5) |
| Decision records | `lib/decisions.py`, `tests/test_decisions.py` | Format and no recall hook (v1-memory#D1, v1-memory#D2) |
| Roadmap and flow | `docs/plans/roadmap.md`, `global/AGENTS.md` | Next item runs without asking only when its spec is approved (v1.1-flow-init#D1, v1.1-flow-init#D2) |
| Anything tracked | `lib/privacy.py`, `.private-terms`, `.privacy-allow`, `.github/workflows/check.yml` | Public repository, no personal data (v1-repo#D3). Scan link text and preserve the Git working tree boundary (v1.7-path-boundaries#D2) |

Checked at 3572356

## Commands

- Check: `scripts/check` (offline tests in a temporary home, the privacy scan, and a guard that fails if the real home directory changed). Run it before reporting completion and include its output.
- `python3 lib/privacy.py`, `python3 lib/decisions.py`, `bin/doctor [--project <path>] [--discovery]`, `bin/doctor --project-only <path>`.
- `bin/setup` and `bin/setup --restore` change the real home directory: run them only when the user asks.

## Skills

Use `away` to brief the user before they leave and continue approved roadmap work in their absence. `map` to fill or refresh the project instructions, `probe` before a new design, `spec` to write the spec, `preflight` before the first push of a spec's work and after delegated changes, `eval` after changing a skill or instruction. When a change alters behavior that README.md, SOURCES.md or a skill describes, update that file in the same change.

## Permission boundaries

- This repository is public. Tracked files and commit messages hold no personal data: write `~` instead of absolute home paths, and leave out private project or company names, personal email addresses and secrets.
- Tests leave the real `~/.claude`, `~/.codex`, `~/.agents` and the global git config as they are; applying the harness to a machine is a separate step the user asks for.

## Commit rules

Default: `type(scope): imperative summary` in English, at most 72 characters. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Leave out `Co-Authored-By` and other attribution trailers.

## Evals

`python3 evals/run.py` (live, calls the real `claude` and `codex`; run after installing and when a model, skill or instruction changes).
