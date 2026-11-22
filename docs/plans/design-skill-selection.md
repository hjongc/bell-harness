# design-skill-selection: carry interview choices into the spec

Status: implemented

## Outcome

Implement the [approved design](design-skill-selection-design.md) in the shared prompt workflow. An agent asks about a consequential unresolved choice, proposes specialist skills alongside the design, and carries their reasons and usage phases into the implementation spec. A well-specified edit goes directly to execution.

## Decisions

- D1: Add one optional Skill plan section to the design and spec templates -- why: the selected workflow already has two handoff artifacts and a compact table can carry the requirement through both -- by: observed -- paths: skills/probe/references/design-doc.md skills/spec/SKILL.md
- D2: Review fixed routing examples separately from any live model behavior -- why: skill text inspection can catch omissions but cannot establish that a host asks the right question or produces a better artifact -- by: observed -- paths: skills/probe/SKILL.md skills/spec/SKILL.md
- D3: Track this implementation as its own roadmap item -- why: the user approved proceeding from the separate spec and asked to approve the roadmap -- by: user -- paths: docs/plans/roadmap.md

## Changes by file

1. `skills/probe/SKILL.md` clarifies the trigger for an implicit interview and retains the one-question loop. While a choice is open, use project instructions, past decisions, supplied references, and installed skill descriptions to inform the next question. At the proposal, list only skills that help meet an agreed requirement. Research external references only for a named gap. Label them as reference candidates.
2. `skills/probe/references/design-doc.md` adds the optional Skill plan section below the recommended approach. When a specialist is relevant, record its name, the requirement it serves, and the phase. Record external references separately in this section when applicable.
3. `skills/spec/SKILL.md` copies that table into the spec when present. Tie observable outcomes to acceptance checks. If a named skill is unavailable on the implementation host, preserve the requirement and record the alternative verification or the unresolved gap.
4. `README.md` updates the shared design workflow and the probe and spec descriptions. `SOURCES.md` records the original handoff extension.
5. `docs/plans/roadmap.md` tracks approval and completion for this implementation.
6. This spec records the fixed-case review and command results after implementation.

## Interface

Use the same row in the design and implementation spec.

```markdown
## Skill plan

| Skill | Requirement and reason | Phase |
|---|---|---|
| `ui-polish` | Verify long and missing inventory values on the real route at narrow widths | Verification |
```

Use local workflow vocabulary for the phase, such as design, implementation, or verification. Omit the section when no specialist or capability gap is relevant. A reference candidate is identified by name and source URL and remains outside the list of skills to invoke.

## Scope boundaries

- Keep explicit requests to use a skill and project-specific instructions in force.
- Reuse the active host's existing view of installed skills. Add no catalog, hook, index, package, installation command, or dependency.
- Keep the global prompts and installer outside this first change. Live model calls and changes to the eval runner require separate scope.

## Acceptance

Apply the same fixed prompts and follow-up answers to the existing and revised instructions in a manual comparison. Record whether each instruction is explicit, then report live host behavior separately if evaluated.

| Input and follow-up | Required behavior |
|---|---|
| “Improve the dashboard.” → “Operators need to find stock exceptions quickly.” | Ask about the user's most important outcome. The proposal ties rendered QA to scanability and difficult data states. No external lookup when installed skills cover the need. |
| Same dashboard request → “The page should show how customers can complete one workflow.” | The proposal focuses on the demonstrated workflow. Add motion or demo guidance only if that choice serves the agreed outcome. |
| “Use the existing spacing token for the table row gap and change nothing else.” | Begin the specified change directly. No implicit interview or proposed shortlist. |
| “Design the data API upgrade. We have clients pinned to the old version.” | Probe the unresolved compatibility or rollout choice. Propose a way to verify existing callers and carry that rationale into the spec. UI skills stay outside the plan. |
| “We need an accessible, interruptible custom drag gesture.” with no suitable installed specialist | Identify the capability gap and label any externally researched candidate as a reference. The workflow does not install or add it to the selected-skill list. |
| An approved design says `offline-verification` is used to exercise the installed CLI in a temporary directory | The spec keeps the skill, reason, and verification phase together and defines a check at the actual CLI entry point. |

## Done condition

`scripts/check` exits 0 with `GUARD: real home unchanged`. The revised instructions cover all six fixed cases, the result reports the baseline and candidate, and the change is limited to the files above.

## Baseline instruction review

The six acceptance cases were fixed before editing. The baseline review reads `skills/probe/SKILL.md`, `skills/probe/references/design-doc.md`, and `skills/spec/SKILL.md` in HEAD, including the relevant question guidance. A case passes only when the instructions explicitly cover its required behavior. This review uses no model calls, external discovery, or installations.

| Case | Baseline result |
|---|---|
| Operational dashboard | Gap. Generic feature questions and optional UI guidance give no skill shortlist tied to actual data or selection order. |
| Product demonstration | Gap. The same optional UI guidance does not tie demo or motion expertise to the user's intended outcome. |
| Specified spacing change | Covered. The probe description excludes small, already-specified edits. |
| API compatibility | Gap. Feature interview questions cover compatibility, but the proposed verification rationale has no handoff. |
| Specialist gap | Gap. Optional market or prior-art research does not define how to handle an unavailable capability. |
| CLI verification handoff | Gap. Neither template carries the skill and its reason and phase. |

Baseline instruction coverage: 1/6.

## Candidate instruction review

| Case | Candidate result |
|---|---|
| Operational dashboard | Covered. Probe asks what someone needs to find or decide. Its inventory example ties a rendered review to scanability and difficult data. Selection stays within installed skills when they cover the need. |
| Product demonstration | Covered. Probe asks what someone needs to learn. Its demo example selects motion guidance only when it helps explain the workflow. |
| Specified spacing change | Covered. The interview gate directs settled edits to execution, before skill-plan presentation. |
| API compatibility | Covered. Probe targets the compatibility or rollout choice and selects verification of existing clients. The spec handoff preserves the reason and turns it into a check. |
| Specialist gap | Covered. Probe records the capability gap and separates external references from selected skills. Installation is a separate decision. |
| CLI verification handoff | Covered. Spec copies the skill name, reason and phase and turns the requested installed-CLI behavior into an acceptance check. |

Manual instruction coverage: 1/6 at baseline and 6/6 after the change. The comparison checks the written instructions. Live skill selection and artifact quality remain unmeasured.

`scripts/check` exited 0 with `Ran 108 tests in 61.571s (4 workers)`, `OK`, and `GUARD: real home unchanged`. The design and spec table headers and row shape matched.
