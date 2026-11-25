# away-separate-folder: keep unattended work out of the linked checkout

Status: implemented

## Context

An away run puts each item on its own branch. In the checkout that supplies the installed skills, switching branches changes the skills while they run. Requirement: R4 in [requirements](../requirements.md), approved by the user on 2026-11-25.

Size budget: net +60 lines.

## Decisions

- D1: Use a Git worktree for such items and compare the original folder's branch, commit and status afterwards -- why: the user approved a separate folder with a before and after check, and worktrees need no new dependency -- by: user -- paths: skills/away/references/run.md

## Changes by file

1. `skills/away/references/run.md`: step 1 names the condition, the commands, the comparison and the cleanup.
2. `tests/test_skills.py`: the procedure keeps those commands.
3. `docs/requirements.md`, `docs/plans/roadmap.md`, this spec.

## Acceptance tests

1. The procedure states when to use a separate folder and which values to compare.
2. In a temporary repository, work committed through the procedure's commands leaves the original folder's branch, commit and status as they were.
3. `scripts/check` exits 0 with `GUARD: real home unchanged`.

Live host behavior was not exercised.

## Done criteria

Acceptance 1-3 hold and only the files above changed.
