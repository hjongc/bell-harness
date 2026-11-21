---
name: init
description: "Fill or refresh a repository's AGENTS.md from the bell-harness template by reading the code: where to look for each kind of change, the constraints there and the decisions behind them, plus the commands to check work. Use when the user says \"init\", \"init-deep\", \"이 저장소 정리해줘\", \"AGENTS.md 만들어줘\", when a repository has no AGENTS.md or one that does not follow the template, or when bin/doctor reports a stale table."
---

# Init

Write down what an agent needs before changing this repository and cannot see in the code: which constraints apply where, and why. The result is one root `AGENTS.md` in the harness template shape, decision records in `docs/plans/`, and a commit marker that makes the next refresh cheap. Facts the code already shows, such as a directory listing or generic advice, stay out, because every line is read in every session.

## First run

1. **Baseline.** Record `git status --short` and the output of `bin/doctor --project .` from the harness. Uncommitted work that is already there belongs to someone else: leave it as it is, and when it changes during the run, keep it out of your commit.
2. **Read what exists.** The current `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, `tasks/lessons.md`, any decision log or ADR, the build and test configuration, and `git log --oneline -50`. Keep every statement that is still true. When directories have their own `AGENTS.md`, read them, leave them unedited, and note where they overlap or disagree with the root table.
3. **Explore.** Find entry points, the single check command, test layout, conventions that differ from the language default, and warnings in comments or docs ("do not", "deprecated", "must stay"). For a large repository, give each top-level directory to a fresh subagent with a fixed brief (entry points, conventions, warnings, commands) and treat their reports as claims to spot-check against the code.
4. **Collect reasons.** For each constraint, find why it exists: a spec, a decision log, an issue, the documents a commit changed. A commit subject points to where to look; it is not itself evidence of the reason. Move each reason into a `## Decisions` line in the relevant spec under `docs/plans/` (create `docs/plans/decisions.md` when no spec fits): `- D<n>: <decision> -- why: <reason> -- by: user|observed -- paths: <paths>`. Use `user` only when the source shows the user decided it. When no reason can be found, write the constraint without a decision id and put it in your report as a question for the user rather than inventing one.
5. **Fill the template.** Use the headings of the harness `templates/AGENTS.md`. In `## Sources of truth`, write one row per kind of change: task, the files to look at, the constraint and its decision id. Write the paths in the second column in backticks or as Markdown links; `bin/doctor` checks exactly those. Keep the file under about 100 lines. Edit an existing `AGENTS.md` in place rather than rewriting it.
6. **Mark the check.** Under the table write `Checked at <short sha of HEAD>`.
7. **Leftovers.** When a project `CLAUDE.md` holds only `@AGENTS.md`, or content you merged into `AGENTS.md`, propose deleting it; current Claude Code reads `AGENTS.md` directly. Delete only after the user agrees.
8. **Commit and verify.** Stage only the files this run wrote, commit through the normal hooks (or leave the changes for review when the repository restricts commits), then run `bin/doctor --project .` again and fix every WARN that the baseline did not have.
9. **Report.** The rows you wrote, the decisions you moved and from where, the constraints without a known reason as questions, overlaps with per-directory instruction files, and any step of this skill that was unclear.

## Refresh

Run `bin/doctor --project .`. Its `stale table` and `table check` lines name the rows to recheck: a path that no longer exists, a file removed under a row, or a new top-level folder without a row. Update those rows and their decisions, then move the marker to the new HEAD in the same commit. For a stale decision citation in a Sources of truth row, read its successor and check the cited constraint against the current checkout. Update the wording as well as the id. If the cited decision is missing or has no active successor, report the gap and keep the reason open. When doctor reports nothing and the user names no changed constraint, say so and change nothing.

## Scope

One root `AGENTS.md`; this skill does not create per-directory files.
