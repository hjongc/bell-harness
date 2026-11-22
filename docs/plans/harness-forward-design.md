# Design: grow the shared harness from observed results

Status: DRAFT
Mode: Feature
Date: 2026-11-22

## Problem

The shared harness should make day-to-day work easier and catch real regressions. Recent experience also shows that agents can satisfy a specific evaluation while delivering worse results. Further changes need evidence at the task entry point and a clear reason for adding another rule, feature or skill.

## Evidence

- v1.15 measures mock publication attempts. v1.16 proposes checking a historical fix against the original case, an ordinary variation and an invalid control. That replay measures the effectiveness of a check.
- The project-only doctor reported a valid import in an untracked `CLAUDE.md`, and the output omitted the untracked nested `AGENTS.md`. A filtered Git query identified both and preserved the temporary index.
- The previous check optimizations reduced full runtime with unchanged coverage. A current local microprobe sped up repository preparation alone, and the likely saving is small relative to the full check.
- v1.13 found the existing workflow already met all five verification criteria in its one-task trial. A new shared skill or instruction should improve a specific outcome before becoming a default.

## Recommended order

| Item | Outcome | Evidence needed to proceed |
| --- | --- | --- |
| [v1.16 outcome-check pilot](v1.16-eval-quality-pilot.md) | Calibrate an outcome check on a real parser defect. | Reproduce the historical matrix before adding one sentence to `eval`. |
| [v1.17 instruction status](v1.17-instruction-status.md) | Find root and nested agent instructions requiring a commit before branch review. | Verify staged, unstaged and untracked paths through project-only doctor in temporary checkouts. This is independent of the quality result. |
| [v1.18 check performance](v1.18-check-fixture-performance.md) | Locate the bottleneck on the actual worker schedule. | Ship a fixture change only with equivalent coverage and at least ten percent median full-wall improvement. This item can end with a profile. |
| [v1.19 guidance comparison](v1.19-eval-guidance-comparison.md) | Test whether the guidance helps agents produce fresh deliverables in the measured workflow. | v1.16 evidence and a separate approval for the bounded live sessions. Offline preparation can precede the live approval. |

The first three items can use the existing offline workflow. The live comparison is scheduled after them so that its approval does not delay the independent work.

## Further decisions after evidence

- If a blind review finds correct mixed-workflow outputs repeatedly marked down on routing, draft a small mixed case with a required skill and explicitly allowed relevant skills. Keep isolated routing probes for their original purpose. Review case results separately before changing any shared score.
- If reviewers find a recurring outcome gap across two distinct tasks, first try a narrower description or example in the relevant existing skill. A proposed new skill needs its own task examples, evidence that it helps, and separate approval before shared installation.
- If the full-check profile identifies a different bottleneck, choose one follow-up based on the measured critical path. Reuse the existing offline check and its real-home guard as the acceptance entry point.

## Decisions

- D1: Order the replay, instruction diagnostic, performance measurement and live comparison in that sequence -- why: the first three have concrete offline checks and the longer comparison depends on the replay and separate approval -- by: observed -- paths: docs/plans/roadmap.md
- D2: Draft further routing or skill work after repeated outcome evidence -- why: a routing result or one successful example alone does not establish a shared workflow improvement -- by: observed -- paths: evals/run.py skills/eval/SKILL.md

## The Assignment

Approve v1.16 through v1.18 for the offline sequence, or approve v1.16 alone for the smallest next step. Review the live session budget separately once the offline evidence is available.
