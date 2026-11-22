# Design: Interview-driven skill selection

Status: APPROVED
Mode: Feature
Date: 2026-11-22

## Problem

A request such as “improve this UI” can mean making an operational task easier or explaining a product to prospective users. Those outcomes require different design and verification work. The same ambiguity appears in document, API, and workflow design. The harness already has an interview and approval flow. It needs to carry the reasons for selecting specialist skills from the conversation into implementation.

## Evidence

The existing `probe` workflow asks one question at a time and records agreed decisions. It only points to `ui-design` in optional guidance for an approved approach with a user-facing screen. The existing `spec` template carries scope, failure modes, and acceptance checks. It has no place to carry skill choices and their reasons. Both flows already run through the same shared skill files in Claude Code and Codex.

## Target user and smallest useful version

For someone asking an agent to design or improve an artifact, use the existing `probe → spec` flow. Ask only about choices that can materially change the deliverable, approach, or verification. At the design proposal, show a concise shortlist with each skill's purpose, phase, and the requirement it serves. Carry that shortlist into the implementation spec.

## Constraints

- Read project instructions, prior decisions, and supplied references before asking. Use the existing one-question interview. Proceed directly for a well-specified revision.
- Prefer capable skills available to the active host, including project and harness skills. Look outside the installed set only for a specific unmet need. Present external matches as references. Existing permissions govern installation and other changes.
- Show the shortlist once with the design proposal. Mention a candidate during the interview only when its availability or capabilities change the options the user is considering.
- Keep the current design and spec documents as the shared record. The first version uses neither a separate catalog nor a new discovery service.

## Approaches considered

### A. Extend the existing probe and spec handoff

Use available skill descriptions while interviewing, then record the winners in the design document and implementation spec. This reuses the existing conversation, documents, and approvals. The main risk is vague skill reasons, so each entry ties to a user requirement and a named phase.

### B. Add a curated specialty catalog

Use the same handoff and maintain a shared capability map for installed and upstream skills. That would help compare candidates across sources, but it would add maintenance and could drift from what each host actually has installed.

## Recommended approach

The user chose A. The design proposal should name the skill, the need it addresses, and where it is used. Example: `ui-polish — verify the inventory table with missing and long values at narrow widths — verification`. The spec carries over the name and rationale and uses the associated observable outcome as an acceptance check when relevant.

## Decisions

- D1: Start an interview automatically only when an unresolved choice can materially change the result -- why: the user chose direct execution for requests whose direction is already settled -- by: user -- paths: skills/probe/SKILL.md
- D2: Prefer installed skills and research external references only for a specific capability gap -- why: the user chose the available set as the default and external candidates as references -- by: user -- paths: skills/probe/SKILL.md
- D3: Show the shortlist with the design proposal and mention a candidate earlier only when it changes the design options -- why: the user chose one consolidated presentation with an exception for material design decisions -- by: user -- paths: skills/probe/SKILL.md skills/probe/references/design-doc.md
- D4: Record each selected skill, its rationale, and its usage phase in the design document and carry the list into the implementation spec -- why: the user chose to extend the existing workflow and keep the rationale available at handoff -- by: user -- paths: skills/probe/references/design-doc.md skills/spec/SKILL.md

## Edge cases and failure modes

- The user supplies a style reference but leaves an important choice open. Ask about the undecided outcome or behavior. Use the reference as evidence of choices it already settles.
- A suitable skill does not exist on the active host. Record the gap and a feasible local verification approach when one exists. Carry an external reference as optional. Ask only if the gap materially changes what can be delivered.
- Multiple skills cover the same task. Use the narrower skill that covers the requirement with less overlap. If no specialist is needed, the design proposal can say so.
- A selected skill is available to one host and missing on the host implementing the spec. Retain the required verification outcome and record which part of the skill workflow could be applied.

## Success criteria

1. For an ambiguous dashboard request, the first question concerns a material user outcome. An operational answer yields a shortlist tied to scanability, data states, or interaction. A product demonstration answer yields a shortlist tied to communicating the workflow and, if needed, motion.
2. For a specified spacing fix, the agent begins the change without starting an interview or showing a shortlist.
3. For a breaking-API concern, the question concerns client compatibility or rollout. The shortlist names the available verification skill that helps exercise callers, or records a gap. UI skills are absent.
4. For a known capability gap, the proposal identifies the gap and labels any external candidate as a reference. No installation happens as part of selection.
5. The design document and the corresponding spec show the same selected skills, rationale, and usage phase. The spec names the applicable verification outcomes.

## The Assignment

Use `spec` to turn the approved approach into a scoped implementation plan with fixed UI and non-UI cases.

## What I noticed

The user identified “결과를 바꿀 선택” as the threshold for interview time and chose to show the shortlist “설계안과 함께 한 번만.” The handoff should preserve the reason for selecting a skill without interrupting the conversation to present intermediate picks.
