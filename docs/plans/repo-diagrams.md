# repo-diagrams: add repository diagrams to the shared harness

Status: implemented

## Context

The Mermaid, Archify, and Excalidraw pilot compared one source-backed CLI workflow at three viewport widths. The user chose Mermaid for repository documentation and Archify for interactive explanations and asked to add the combination to the harness.

## Decisions

- D1: Default repository diagrams to Mermaid and use Archify for interactive HTML -- why: the user chose the text format for durable docs and the interactive viewer for presentations -- by: user -- paths: skills/repo-diagrams/SKILL.md
- D2: Ship one shared skill with an optional Archify integration -- why: one trigger keeps the format choice consistent across hosts and the optional renderer preserves the existing harness dependency baseline (v1-repo#D1) -- by: observed -- paths: skills/repo-diagrams/SKILL.md skills/repo-diagrams/references/archify.md

## Scope and non-goals

- Add the diagram workflow and the Archify reference to the existing shared skill discovery path.
- The base harness keeps its current dependencies. Archify uses its separately provisioned upstream runtime.
- Outside scope are global setup, plugin installation, publishing, Excalidraw support, and paid live model evaluation.

## Changes by file

1. `skills/repo-diagrams/SKILL.md` adds format selection, source tracing, and artifact verification.
2. `skills/repo-diagrams/references/archify.md` integrates an available Archify runtime and describes the missing-runtime case.
3. `README.md` lists the skill and usage. `SOURCES.md` records the original workflow and external references.
4. `tests/test_skills.py` registers the new folder. `tests/test_setup.py` checks both links for all skills discovered by the existing fixture.
5. `docs/plans/roadmap.md` tracks the change. This spec records verification.

## Acceptance tests

Use these fixed cases to compare HEAD and the candidate instructions. A case is covered when the required action and format are explicit in the skill. The review measures written guidance independently of live model routing.

| Prompt and condition | Expected behavior |
|---|---|
| Add the API request flow to the README. | Use a Mermaid sequence diagram or flowchart with code locations for important calls or branches. |
| Explain which processes and stores this project runs. | Use a Mermaid overview of runtime responsibilities and boundaries with source evidence. |
| Make an interactive demo where I can click a failure node to inspect its source. Archify is available. | Use the installed Archify workflow, run its validation, and verify that a click opens the intended evidence. |
| The same interactive demo request. Archify is unavailable. | Surface the missing runtime, keep Mermaid available as an alternate artifact, and leave installation under the user's control. |
| Summarize the repository in two paragraphs. | Keep the requested prose format. |

Run the existing install-then-noop test with the temporary home and both host stubs. Run `scripts/check`, `python3 lib/privacy.py`, and `python3 lib/decisions.py`.

## Done condition

All five written cases are covered. The temporary-home setup links the skill for both hosts. The full check reports `GUARD: real home unchanged`, the privacy and decision checks are clean, and changes are limited to the files above.

## Fixed-case instruction review

HEAD had no repository-diagram workflow. Its general instruction to work from the requested outcome covered the text-only case.

| Case | HEAD | Candidate |
|---|---|---|
| README request flow | No diagram format or tracing guidance | Mermaid default, ordered-call view, and source locations |
| Runtime overview | No diagram format or boundary guidance | Mermaid flowchart for processes and boundaries, with source locations |
| Interactive demo with Archify | No tool invocation or click check | Archify validation and inspection of the selected node's evidence |
| Interactive demo without Archify | No fallback or installation boundary | Report the missing runtime and offer Mermaid source |
| Two-paragraph summary | Requested prose format | Explicit text-only rule keeps the prose format |

Written guidance covers 1 of 5 cases at HEAD and 5 of 5 in the candidate. Live routing and renderer behavior were outside this review. The earlier pilot tested the Mermaid and Archify artifacts.

## Verification result

`scripts/check` exited 0 and reported `Ran 108 tests in 65.741s (4 workers)`, `OK`, and `GUARD: real home unchanged`. The install-then-noop test checked both installed links for every discovered skill in the temporary home. The privacy and decision checks reported `PRIVACY: clean` and `DECISIONS: clean`.

## Installed runtime smoke test

[Archify setup](archify-setup.md) adds the repeatable provisioning path for other machines.

After explicit approval for machine-wide skill links, Archify v3.2.0 and
`repo-diagrams` were verified at both hosts' skill locations on the authoring
machine. The installed Archify CLI generated standalone HTML from the pilot
workflow and passed `validate`, `deliver`, `check`, and `browser-check` with
Chrome's default sandbox. The smoke test used a temporary home and disabled
the optional Archify update check.
