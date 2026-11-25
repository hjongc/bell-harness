# doctor-branch: show the branch of the harness checkout

Status: implemented

## Context

Installed skills and instructions are links into the harness checkout, so switching its branch changes their behavior. Doctor reported uncommitted changes there and left the branch out. Requirement: R2 in [requirements](../requirements.md), approved by the user on 2026-11-25.

Size budget: net +60 lines.

## Decisions

- D1: Report a branch other than `main` as WARN with exit 0 -- why: working on a branch is normal, and the user only needs to see which version is live -- by: observed -- paths: bin/doctor

## Changes by file

1. `bin/doctor`: one machine-check line, `harness branch`.
2. `tests/test_doctor.py`: `main`, another branch and a detached HEAD.
3. `docs/requirements.md` NEW, `docs/plans/roadmap.md`, this spec, and the `AGENTS.md` row for the roadmap.

## Acceptance tests

1. `PASS harness branch: main` on `main`.
2. `WARN harness branch:` naming the branch, or `a detached HEAD`, with exit 0.
3. `scripts/check` exits 0 with `GUARD: real home unchanged`.

## Done criteria

Acceptance 1-3 hold and only the files above changed.
