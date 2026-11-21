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

### B6: The plan-mode rule collides with unattended work on approved specs (medium)
- Area: `global/CLAUDE.md:9`, `skills/away/SKILL.md`, `global/AGENTS.md:37`.
- Evidence: by reading the rules together. CLAUDE.md says to agree on a plan in plan mode before editing any work of three or more steps; plan mode waits for the user's approval. The roadmap rule and the away skill say an item whose spec is approved runs without asking. An agent that follows the first rule while the user is away stops at the first item.
- Direction: one clause in CLAUDE.md that an approved spec is the agreed plan, so plan mode is for work that has no approved spec.

### B7: The preflight rule is not being followed (small, about use rather than code)
- Area: `global/AGENTS.md:50`.
- Evidence: the rule says to run `preflight` before pushing any diff larger than a single obvious fix. Between v1.1 and this audit, more than twenty multi-file commits were pushed to this repository and `preflight` ran once, before the first publication. Review happened through `scripts/check`, spec comparison and CI instead.
- Why it matters: a rule that is routinely skipped teaches agents that global rules are optional.
- Direction: either narrow the rule to what is actually wanted (for example, delegated changes and first pushes of a spec) or keep it and add a pre-push reminder; the user decides which.

### B8: Claude's deny rules catch the short bypass flag only in first position (small, not verified live)
- Area: `config/claude-settings.json` (`Bash(git commit -n:*)`).
- Evidence: by reading the patterns. `--no-verify` is matched anywhere by `Bash(git * --no-verify*)`, but `-n` is matched only directly after `git commit`, so `git commit -a -n -m ...` or `git -C <dir> commit -n` matches no rule. A live test was blocked by the session's own permission classifier, so this is unconfirmed. Codex rules have the same prefix limit (v1.2-field-fixes#D7).
- Direction: decide whether a broader pattern is worth its false positives (a message containing ` -n`), or rely on `bin/doctor --project`, which lists commits the hook would have rejected.

### B9: The privacy scan does not recognize Windows home paths (small)
- Area: `lib/patterns.py` (`HOME_PATHS`).
- Evidence: `python3 lib/privacy.py <dir>` on a file with ten sample lines flagged a macOS home path, a Linux home path, an email, a key and a WSL-mounted Windows home path, but not a native Windows path of the form `C:\Users\<name>\code`. Windows is a stated non-goal, so this matters only for pasted paths.
- Direction: add a `[A-Za-z]:\\Users\\<name>` pattern when Windows support is considered.

### B10: Decision logs written before the harness are invisible to the checker (small)
- Area: `lib/decisions.py`, `skills/init`.
- Evidence: running `bin/doctor --project` read-only over the local repositories gave no crash and two kinds of warning. One repository has records without a `why` field (true positives). Another has a new record whose `supersedes` points at an entry in an older log that uses a `## DECIDED` heading and `- D23 (date). ...` lines; doctor reports `supersedes unknown decision`, which is accurate but does not say why.
- Direction: when a `docs/plans` file has decision-like lines outside a `## Decisions` section, have doctor suggest running the `init` skill to migrate them. Until then the fix per repository is to run `init`.

## Fixed during the audit
- `bin/setup --restore` crashed with a traceback when `~/.claude/settings.json` had become invalid JSON; it now skips the settings with a message and undoes the rest (`tests/test_setup.py::test_restore_survives_invalid_settings`).
- `bin/doctor --project <missing dir>` exited 0 with a misleading "AGENTS.md not found" warning; it now fails with "is not a directory" (`tests/test_doctor.py::test_missing_project_directory_fails`).
- Skills named harness tools (`bin/doctor`, `templates/AGENTS.md`) without saying where they are; in another repository an agent could not find them. `init` and `preflight` now say the harness root is two folders above the skill's real path. The `spec` skill sent unattended failures to "Blocked" while `away` uses `docs/plans/blocked.md`; both now name the file (v1-skills#D8).
- `v1-skills#D1` still said the harness has six skills while eight ship, and nothing superseded it; `AGENTS.md` cited it. Added `v1.3-away#D7` superseding it and updated the table. The citation check from v1.4 confirms the fix: with the old table it reports `v1-skills#D1 superseded; cite v1.3-away#D7`.
- A project whose AGENTS.md was copied from the template and left unfilled passed `bin/doctor --project` with only an odd `unknown commit <short commit>` warning. Doctor now warns that template placeholders remain (`tests/test_doctor.py::test_unfilled_template_is_reported`).
- `bin/setup` printed every planned action as if done before applying any, so after a mid-run failure the output did not show how far it got. It now prints each action after it succeeds and reports `stopped after N of M actions` (`tests/test_setup.py::test_failed_action_stops_and_can_be_undone`, which also covers the failure-then-restore path that had no test).
- `lib/decisions.py` read only the first line of a decision record, so records hard-wrapped at 80 columns in a real project were reported as `missing field 'by'` (six false warnings from `bin/doctor --project`). Indented continuation lines are now part of the record (`tests/test_decisions.py::test_accepts_a_record_wrapped_onto_indented_lines`, v1.4-memory-recall#D2).
- The wrapped-record fix above absorbed a nested list under a record and then reported a bad `by` value. Continuation now stops at a nested list item (`tests/test_decisions.py::test_nested_list_under_a_record_is_not_part_of_it`). Found in pass 13 by probing the pass 11 change.

## Covered areas
- Pass 1: README against real behavior (install, check and undo, eval case count). Case count and commands match.
- Pass 2: eval runner (`evals/run.py`) and the `init` name. Four findings, none fixed (each changes grading behavior and needs a decision).
- Pass 3: `bin/setup` and `bin/doctor` edge cases in a temporary home (missing or non-git project, unknown backup id, memory notes in CLAUDE.md, invalid settings). Two bugs fixed; the other cases behaved correctly.
- Pass 4: skill bodies (cross-references, tool paths, script syntax). Two wording bugs fixed; `ui-check.mjs` parses but has still never been run against a page.
- Pass 5: global rules read against each other and against what happened in practice. Two findings recorded, none fixed (both change global rules).
- Pass 6: installed git hooks in a temporary repository (scoped and breaking subjects, Hangul in subject and body, non-conventional subjects, revert, merge, cherry-pick, a chained repo-local hook, a staged secret, a 3 MB binary in 0.17 s). All behaved as specified; no finding. Note for the user: Hangul in the commit body is rejected as well as in the subject unless `.harness.json` allows it.
- Pass 7: plan documents against the code (decisions still in force, roadmap, statements of counts). One outdated decision fixed. Older spec appendices no longer match the current skill files; they are kept as the record of what was approved at the time.
- Pass 8: privacy scan with sample lines and the Claude deny patterns. Two small findings recorded.
- Pass 9: the project template through `bin/doctor`, and what `scripts/check` covers (privacy and decision checks run inside the test suite). One bug fixed.
- Pass 10: untested branches of `bin/setup` (a failing plugin uninstall, then restore). Restore worked; the output problem above was fixed.
- Pass 11: the updated doctor against this machine and against the first real project (read-only). One false-positive bug fixed.
- Pass 12: `bin/doctor --project` read-only across every local repository. No crash and no false positive after the pass 11 fix; one finding recorded.
- Pass 13: regression probes of the fixes made during this audit. One regression found and fixed.
