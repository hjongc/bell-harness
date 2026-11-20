---
name: preflight
description: Review the current diff against its spec before pushing: size, scope, unnecessary code, decisions it touches, and a rerun of the done condition. Use before pushing a diff larger than a single obvious fix, when the user says "preflight", "pre-push", "푸시 전 점검", or when a delegated change comes back for review.
---

# Preflight

A gate before pushing, run only when the diff is worth the tokens. The output is a short verdict, not an essay.

## 1. Size

Run `git diff --stat <target>...HEAD` plus `git status --short` (target: the upstream or `main`). When the diff is a one-liner or a single obvious fix, say so and stop.

## 2. Spec match

Find the spec the work follows (named in the request, the commit messages, or `docs/plans/`). Then check:
- Every changed file appears in its Changes by file, or the deviation is explained.
- Nothing in Non-goals or "Do not" was done.
- Each acceptance test has a matching test or recorded evidence.
- Documents the change affects (README, the project's AGENTS.md, skills, the spec's Status) are updated.

When there is no spec and the diff is more than a small fix, report that as a finding.

## 3. Less code

For each added block, ask whether it could have stopped at an earlier rung: not exist at all, a standard library feature, a platform feature, an already-installed dependency, a one-liner. Flag dead paths, speculative abstraction, configuration for cases that do not exist, and anything that solves a problem the spec did not ask about.

## 4. Decisions

For the paths the diff touches, look up decisions in force (`grep -rn "<path>" docs/plans`). Flag a change that contradicts one without a new decision line that supersedes it. When the project has `lib/decisions.py` or `bin/doctor --project`, run it.

## 5. Evidence

Treat a delegated or earlier result as a claim: run the spec's done condition (or `scripts/check`) now and paste the real output. A UI change needs its screenshots under `docs/plans/evidence/<slug>/`.

## 6. Verdict

One of:
- clean to push
- small fixes needed (list them, then fix them when they are in scope)
- send back (state the specific ask)

Record findings that should change future work: a correction from the user goes to `tasks/lessons.md`; a new or changed decision goes to the spec's `## Decisions`. When the diff came from one tool, a review by the other tool before merge adds a second vendor's view.
