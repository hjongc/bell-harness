# Backlog

Findings from audit passes over the harness. Each entry has evidence and a size. Nothing here is approved work; an item becomes work when it gets a spec.

## Open

### B1: Moving the harness repository blocks both setup and doctor (medium)
- Area: README "Install", `bin/setup` preflight.
- Evidence: in a temporary home, run `bin/setup`, rename the harness directory, run `bin/setup --dry-run` from the new location. Output: `setup: global core.hooksPath is <old>/git/hooks, not <new>/git/hooks`, exit 2. `bin/doctor` then reports every link as FAIL and says to run `bin/setup`, which refuses. Links into the old location also stop counting as managed, so they would be backed up as foreign entries.
- Why it matters: the only way out is to unset `core.hooksPath` by hand, which no document mentions. A user who reorganizes folders or clones to a different path on a second machine after copying their home hits this.
- Direction: treat a `core.hooksPath` or link whose recorded value appears in an earlier backup manifest as the harness's own and replace it; or document `git config --global --unset core.hooksPath` in the README until then.

### B2: The harness skill `init` shares its name with Claude Code's built-in `/init` (medium)
- Area: `skills/init`, `evals/cases/route-init.json`.
- Evidence: Claude Code ships a built-in `/init` command that writes a CLAUDE.md. In a temporary repository, `claude -p "Load the skill named init with the Skill tool..."` returned the harness heading `# Init`, so the Skill tool resolves to the harness skill. What a user gets by typing `/init` could not be determined (`claude -p "/init"` printed nothing identifiable within two turns). Earlier, before the harness skill existed, `/init` ran the built-in.
- Why it matters: the user may type `/init` expecting the harness behavior and get a generated CLAUDE.md, which the harness now treats as redundant (v1.1-flow-init#D6). The routing eval only checks that a skill named `init` was called, not which body loaded.
- Direction: check interactively what `/init` runs; if the built-in wins, rename the skill (for example `map`) or state the difference in its description.

### B3: Eval runs are not isolated from the real harness repository (medium)
- Area: `evals/run.py:81` (`parse_codex`), `evals/run.py:100` (`command_for`).
- Evidence: in the full live run of 2026-11-21, `codex route-eval` failed with `skills=[eval, spec, spec]`: Codex read the harness's own `skills/spec/SKILL.md` while investigating, and the grader counts any command containing `/<name>/SKILL.md` as a load. The fixture copy lives in a temporary directory, but the agent can read the whole disk.
- Why it matters: results depend on what happens to be in the working harness repository, and a correct run can fail.
- Direction: for Codex, count only reads under the skills directories it loads from (`.agents/skills/`), and treat reads of other paths as file reads.

### B4: Every eval case gets the same eight-turn limit and one attempt (small)
- Area: `evals/run.py:102` (`--max-turns 8`).
- Evidence: `claude away-gate-ko` returned an empty answer once and passed on rerun; the case asks for multi-step work while writes are disabled. A single run cannot tell a flaky case from a broken one (three flakes seen in 62 live runs across two days).
- Direction: an optional `max_turns` per case, and a `--repeat N` flag that reports pass counts.

### B5: A plugin skill whose name ends in a harness skill name counts as that skill (small)
- Area: `evals/run.py:68` (`name.split(":")[-1]`).
- Evidence: by reading the code: `Skill(skill="other-plugin:spec")` is recorded as `spec`. No such plugin is installed on this machine, so it has not happened.
- Direction: accept only the bare name, or the bare name with a known harness prefix.

## Fixed during the audit
- `bin/setup --restore` crashed with a traceback when `~/.claude/settings.json` had become invalid JSON; it now skips the settings with a message and undoes the rest (`tests/test_setup.py::test_restore_survives_invalid_settings`).
- `bin/doctor --project <missing dir>` exited 0 with a misleading "AGENTS.md not found" warning; it now fails with "is not a directory" (`tests/test_doctor.py::test_missing_project_directory_fails`).
- Skills named harness tools (`bin/doctor`, `templates/AGENTS.md`) without saying where they are; in another repository an agent could not find them. `init` and `preflight` now say the harness root is two folders above the skill's real path. The `spec` skill sent unattended failures to "Blocked" while `away` uses `docs/plans/blocked.md`; both now name the file (v1-skills#D8).

## Covered areas
- Pass 1: README against real behavior (install, check and undo, eval case count). Case count and commands match.
- Pass 2: eval runner (`evals/run.py`) and the `init` name. Four findings, none fixed (each changes grading behavior and needs a decision).
- Pass 3: `bin/setup` and `bin/doctor` edge cases in a temporary home (missing or non-git project, unknown backup id, memory notes in CLAUDE.md, invalid settings). Two bugs fixed; the other cases behaved correctly.
- Pass 4: skill bodies (cross-references, tool paths, script syntax). Two wording bugs fixed; `ui-check.mjs` parses but has still never been run against a page.
