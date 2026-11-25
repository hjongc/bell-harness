# away-separate-folder: keep unattended work out of the linked checkout

Status: draft (first review failed; corrected version is over the size budget and waits for the user)

## Context

An away run puts each item on its own branch. In the checkout that supplies the installed skills, switching branches changes the skills while they run. Requirement: R4 in [requirements](../requirements.md), approved by the user on 2026-11-25.

Size budget: net +60 lines.

## Decisions

- D1: Keep unattended work on the linked checkout in a separate folder and compare the original before and after -- why: switching branches there changes the skills in use, approved by the user on 2026-11-25 -- by: user -- paths: skills/away/references/run.md
- D2: Use a Git worktree, and fingerprint file contents as well as status -- why: status alone stays the same when an already changed file changes again -- by: observed -- paths: skills/away/references/run.md
- D3: Copy ignored check inputs into the folder first -- why: a worktree lacks the private term list, and the privacy scan then reports clean without it -- by: observed -- paths: skills/away/references/run.md

## Changes by file

1. `skills/away/references/run.md`: the condition in step 1 and the Separate folder section.
2. `tests/test_skills.py`: runs the documented commands in a temporary repository.
3. `README.md`, `docs/requirements.md`, `docs/plans/roadmap.md`, this spec.

## Acceptance tests

1. The procedure states when to use a separate folder and which values to compare.
2. In a temporary repository with uncommitted work, an item in a separate folder leaves the documented output unchanged, and a content change in a modified or untracked file changes it.
3. `scripts/check` exits 0 with `GUARD: real home unchanged`.

Live host behavior was not exercised.

## Done criteria

Acceptance 1-3 hold and only the files above changed.
