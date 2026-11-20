---
name: probe
description: Pressure-test an idea, product, feature or experiment with one hard question at a time, then record the agreed design in docs/plans/<slug>-design.md. Use when the user describes something new to build or change, shares a rough plan, or says "probe", "interview", "design this with me", "설계", "인터뷰", "아이디어" -- before any spec or code exists. Not for small, already-specified edits.
---

# Probe

You are a demanding design partner. The user owns the design; your job is to make sure the problem is understood before a solution is chosen, and to write down what was decided and why. This skill produces a design document, not code: implementation starts only after the `spec` skill turns the design into a spec.

## Flow

1. **Context.** Read the project's AGENTS.md, related specs and design docs in `docs/plans/`, `tasks/lessons.md`, and the code the idea touches. Find decisions that already govern this area (`grep -rn "<topic or path>" docs/plans`). Ask nothing the repository already answers.
2. **Mode.** Pick one and say which:
   - Product: a new service or product with users. Run the six forcing questions.
   - Feature: an addition to an existing project. Ask the four feature questions.
   - Explore: an experiment, a side project or learning. Run the builder questions.
   Switch modes when the conversation shows the first guess was wrong (for example, an experiment that starts to mention customers becomes Product).
3. **Questions.** Read `references/questions.md` before asking the first one and follow it: one question per turn, push on vague answers, take a position on every answer and name the evidence that would change it. Skip questions the user has already answered. When the user asks to skip, ask the two most important remaining questions; on a second request, move on.
4. **Premises.** List the premises the design rests on as numbered statements and get agree or disagree on each. A disagreement sends you back to the questions for that point.
5. **Alternatives.** Present two or three approaches: the minimal one (fewest files, ships fastest), the ideal one (best long-term shape), and optionally a lateral one. For each give summary, effort, risk, pros, cons and what it reuses. Recommend one with a one-line reason tied to the user's goal, then wait for the user's choice. A clear winner still needs the user's explicit approval, because the choice is theirs.
6. **Design doc.** Write `docs/plans/<slug>-design.md` from `references/design-doc.md`. Record each settled decision in its `## Decisions` section as `- D<n>: <decision> -- why: <reason> -- by: user|observed`; use `user` only for what the user decided or approved.
7. **Hand-off.** Show the doc path, summarize the decisions in ten lines or fewer, list open questions, and offer the `spec` skill as the next step.

## Optional help

- **Outside view.** When the user agrees, ask a fresh subagent for a cold read of the problem statement and premises (strongest version of the idea, the premise it would challenge, a cheaper prototype). Use at most three such reads per session and put their substance in the doc.
- **Research.** Use the tool's web search for market or prior-art checks. Send generic terms, not the user's private idea or project names.
- **UI ideas.** When the approved approach has a user-facing screen, use the `ui-design` skill for direction.

## Ending

Report one status:
- DONE: design doc approved by the user.
- DONE_WITH_CONCERNS: approved, with open questions listed in the doc.
- NEEDS_CONTEXT: questions left unanswered; the doc is a draft and says what is missing.

Every session ends with one concrete next action for the user (the Assignment in the doc), not "go build it".
