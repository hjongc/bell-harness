---
name: init
description: "Fill or refresh a repository's AGENTS.md from the bell-harness template by reading the code: where to look for each kind of change, the constraints there and the decisions behind them, plus the commands to check work. Use when the user says \"init\", \"init-deep\", \"이 저장소 정리해줘\", \"AGENTS.md 만들어줘\", when a repository has no AGENTS.md or one that does not follow the template, or when bin/doctor reports a stale table."
---

# Init

Write down what an agent needs before changing this repository and cannot see in the code: which constraints apply where, and why. The result is one root `AGENTS.md` in the harness template shape, decision records in `docs/plans/`, and a commit marker that makes the next refresh cheap. Facts the code already shows, such as a directory listing or generic advice, stay out, because every line is read in every session.

## First run

1. **Read what exists.** The current `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, `tasks/lessons.md`, any decision log or ADR, the build and test configuration, and `git log --oneline -50`. Keep every statement that is still true.
2. **Explore.** Find entry points, the single check command, test layout, conventions that differ from the language default, and warnings in comments or docs ("do not", "deprecated", "must stay"). For a large repository, give each top-level directory to a fresh subagent with a fixed brief (entry points, conventions, warnings, commands) and treat their reports as claims to spot-check against the code.
3. **Collect reasons.** For each constraint, find why it exists: a spec, a decision log, a commit message, an issue. Move each one into a `## Decisions` line in the relevant spec under `docs/plans/` (create `docs/plans/decisions.md` when no spec fits): `- D<n>: <decision> -- why: <reason> -- by: user|observed -- paths: <paths>`. Use `user` only when the source shows the user decided it. When no reason can be found, write the constraint without a decision id and list it under open questions in your report rather than inventing one.
4. **Fill the template.** Use the headings of the harness `templates/AGENTS.md`. In `## Sources of truth`, write one row per kind of change: task, the files to look at, the constraint and its decision id. Keep the file under about 100 lines. Edit an existing `AGENTS.md` in place rather than rewriting it.
5. **Mark the check.** Under the table write `Checked at <short sha of HEAD>`.
6. **Leftovers.** When a project `CLAUDE.md` holds only `@AGENTS.md`, or content you merged into `AGENTS.md`, propose deleting it; Claude Code reads `AGENTS.md` directly. Delete only after the user agrees.
7. **Verify.** Run `bin/doctor --project .` from the harness (or the project's own check) and fix every WARN you caused. Then report the rows you wrote, the decisions you moved, and the constraints without a known reason.

## Refresh

When `Checked at <sha>` exists, run `git diff --name-only <sha>..HEAD`. Recheck only the rows whose paths changed and any new top-level area, update those rows and decisions, and move the marker to the new HEAD. When nothing under the table changed, say so and change nothing.

## Scope

One root `AGENTS.md`; no per-directory files. Commit through the normal hooks, or leave the changes for the user to review when the repository restricts commits.
