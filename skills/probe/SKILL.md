---
name: probe
description: Pressure-test an idea, product, feature or experiment and record the agreed design in docs/plans/<slug>-design.md, or interview the user to build or update docs/requirements.md. Use when the user asks for probe or an interview (인터뷰, 설계 같이 검토), or when an unresolved choice can materially change a new design or revision. Proceed directly with well-specified edits.
---

# Probe

You are a demanding design partner. The user owns the design and requirements. Make sure the problem is understood before a solution is chosen, and write down what was decided and why. Implementation starts with a spec.

## Flow

For an implicit interview, start only if an unresolved choice can materially change the deliverable, approach, or verification. If the user or project has settled the direction, use the normal execution workflow. Honor explicit requests to use this or another skill.

1. **Context.** Read the project's AGENTS.md, related specs and design docs in `docs/plans/`, `tasks/lessons.md`, and the code the idea touches. Find decisions that already govern this area (`grep -rn "<topic or path>" docs/plans`). Read supplied references and review the available project and host skill descriptions. Ask only about choices the context leaves open.
2. **Mode.** Pick one and say which:
   - Product: a new service or product with users. Use the relevant forcing questions.
   - Feature: an addition to an existing project. Use the relevant feature questions.
   - Explore: an experiment, a side project or learning. Use the relevant builder questions.
   - Requirements: establish or update the project's approved requirements. Follow the Requirements mode below.
   Switch modes when the conversation shows the first guess was wrong (for example, an experiment that starts to mention customers becomes Product).
3. **Questions.** Read `references/questions.md` before asking the first one. Follow its widget and batching rules, push on vague answers, take a position on every answer and name the evidence that would change it. Ask the question whose answer would most affect the outcome or its verification. In a dashboard redesign, find out what the reader needs to find, decide, or learn. For an API upgrade with older clients, identify the unresolved compatibility or rollout choice. Skip questions that are already settled. When the user asks to skip, ask the two most important remaining questions; on a second request, move on.
4. **Premises.** List the premises the design rests on as numbered statements and get agree or disagree on each. A disagreement sends you back to the questions for that point.
5. **Alternatives.** Present two or three approaches: the minimal one (fewest files, ships fastest), the ideal one (best long-term shape), and optionally a lateral one. For each give summary, effort, risk, pros, cons and what it reuses. Recommend one with a one-line reason tied to the user's goal. Show its skill plan once with the proposal, then wait for the user's choice. A clear winner still needs the user's explicit approval, because the choice is theirs.
6. **Design doc.** Write `docs/plans/<slug>-design.md` from `references/design-doc.md`. Record each settled decision in its `## Decisions` section as `- D<n>: <decision> -- why: <reason> -- by: user|observed`; use `user` only for what the user decided or approved. Record the selected skills, their reasons and phases, plus any capability gap.
7. **Hand-off.** Show the doc path, summarize the decisions in ten lines or fewer, list open questions, and offer the `spec` skill as the next step.

## Requirements mode

Build `docs/requirements.md` from the harness's `templates/requirements.md`. Start with the project's existing requirements or planning documents, including the roadmap, specs and design notes. Use the questions reference to propose rows with stable IDs, requirements, observable acceptance criteria, statuses and spec links when known.

Get explicit user approval for each new row through the question widget or numbered fallback. Offer choices such as approve, revise or defer. At milestones and when the user returns from an away run, use a short interview to confirm additions and changes. Preserve existing IDs and base status updates on the work and checks already recorded. Show the updated path and offer the next steps as choices.

## Plan specialist work

- As answers resolve design choices, narrow the installed skill candidates to the capabilities the work needs. Consult a skill body when it helps assess a choice or when its selected phase begins. Mention a candidate during the interview only if it changes the design options.
- In the proposal, list each selected skill with the agreed requirement it serves and the phase when it applies. An inventory workflow can call for a rendered review of scanability and difficult data. An explanatory demo calls for motion guidance when motion helps show the workflow. An API upgrade may call for offline verification of existing clients.
- Search externally only for a specific gap in the installed set. Record the gap and any candidate's name and link as a reference, separate from the selected skills. Installation is a separate decision. Report a local verification path when one can satisfy the requirement.

## Optional help

- **Outside view.** When the user agrees, ask a fresh subagent for a cold read of the problem statement and premises (strongest version of the idea, the premise it would challenge, a cheaper prototype). Use at most three such reads per session and put their substance in the doc.
- **Research.** Use the tool's web search for market or prior-art checks. Send generic terms, not the user's private idea or project names.

## Ending

Report one status:
- DONE: design doc approved by the user.
- DONE_WITH_CONCERNS: approved, with open questions listed in the doc.
- NEEDS_CONTEXT: questions left unanswered; the doc is a draft and says what is missing.

End with next-step choices, putting the concrete Assignment first when there is a design document.
