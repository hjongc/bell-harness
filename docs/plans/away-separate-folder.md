# away-separate-folder: keep unattended work out of the linked checkout

Status: implemented

## Context

An away run puts each item on its own branch. In the checkout that supplies the installed skills, switching branches changes the skills while they run. Requirement: R4 in [requirements](../requirements.md), approved by the user on 2026-11-25.

Size budget: net +60 lines.

## Decisions

- D1: Keep unattended work on the linked checkout in a separate folder -- why: switching branches there changes the skills in use, approved by the user on 2026-11-25 -- by: user -- paths: skills/away/references/run.md
- D2: Compare only the branch and the commit -- why: the user chose this on 2026-11-25 after two versions that compared file contents failed review, accepting that an accidental file edit goes unnoticed -- by: user -- paths: skills/away/references/run.md
- D3: Copy ignored check inputs into the folder first -- why: a worktree lacks the private term list, and the privacy scan then reports clean without it -- by: observed -- paths: skills/away/references/run.md

## Changes by file

1. `skills/away/references/run.md`: the condition in step 1 and the Separate folder section.
2. `tests/test_skills.py`: the procedure keeps its commands and the comparison.
3. `README.md`, `docs/requirements.md`, `docs/plans/roadmap.md`, this spec.

## Acceptance tests

1. The procedure states when to use a separate folder, which two values to compare and when.
2. One run in a temporary repository with uncommitted work: branch and commit of the original stay the same while the item is committed in the folder, and removal refuses while uncommitted work exists.
3. `scripts/check` exits 0 with `GUARD: real home unchanged`.

Live host behavior was not exercised.

## Done criteria

Acceptance 1-3 hold and only the files above changed.

## Verification

One run of acceptance 2 printed:

```text
branch and commit unchanged; own edits kept:  M a ?? untracked
refused while uncommitted work exists
removed when clean, branch kept: feat/x
existing branch form works
branch switch detected
```
