# ui-design-quality: task-first design and evidence-based polish

Status: implemented

## Context

The user reported generic AI-looking output from ui-design and ui-polish and asked to use Emil Kowalski's skills as a reference. The design workflow should derive the screen from content and actions. The review workflow should expose weak hierarchy, gratuitous motion, and failures that demo content hides.

## Decisions

- D1: Start with the user's work and the project's visual vocabulary, then consult the catalog for a specific open decision -- why: a product label can suggest tokens but cannot determine what the user needs to see or do -- by: observed -- paths: skills/ui-design/SKILL.md
- D2: Require an observable reason for decoration and motion, and exercise the rendered surface with realistic difficult data and repeated input -- why: screenshots of the default state miss both needless feedback delays and content failures -- by: observed -- paths: skills/ui-design/SKILL.md skills/ui-polish/SKILL.md
- D3: Continue defect review without a baseline and withhold visual sign-off pending approval -- why: the known reference is needed for approval under v1-skills#D5, while accessible interactions and overflow can still be checked -- by: observed -- paths: skills/ui-polish/SKILL.md

- D4: Distinguish working product UI, brand pages, and illustrative product demos when choosing visual emphasis -- why: people scan and act in working UI, while brand and demo surfaces can use composition and motion to tell a focused story -- by: observed -- paths: skills/ui-design/SKILL.md skills/ui-polish/SKILL.md

## Changes by file

- `skills/ui-design/SKILL.md` leads with task, content, project constraints, and concrete composition and motion choices. Approved decisions still go to the project design record.
- `skills/ui-design/references/search.md` holds query and generation details for the existing catalog tool. Its CLI, data, and other references stay in place.
- `skills/ui-polish/SKILL.md` checks subtractive edits, realistic data, and interactions on the actual route and records concrete evidence. Keep the print workflow and baseline approval rule.
- `README.md` and `SOURCES.md` describe the revised skills and upstream influence. Adapt the ideas in original wording.
- `tasks/lessons.md` records the prevention rule for generic UI output.
- This spec holds the comparison. Dependencies, installations, and paid model calls are out of scope.

## Acceptance

Compare the baseline and candidate skill texts against the same scenarios below. Count a scenario only when the instructions explicitly call for every listed action. This is a manual instruction coverage check. It does not grade generated UI or prove runtime routing.

| Scenario | Required observable guidance |
|---|---|
| New inventory workspace with filters, stock rows, and an order action | Arrange real content and the primary action before style search. Treat catalog output as optional input and avoid ornamental containers that compete with the work. |
| Existing finance page with approved colors and a custom table | Read and reuse the project's design decisions. Search only for the unresolved issue. Preserve approved choices when persisting guidance. |
| Command palette used repeatedly and a pointer-opened filter popover | Keep the repeated keyboard path immediate. Give any retained transition a purpose and verify reversal and reduced motion. |
| Responsive member list with long email, missing avatar, zero members, and translated labels | Inject representative values through fixtures, props, or API stubs. Render the changed states on the real route and verify the affected viewport. |
| UI polish requested on a working screen with no approved reference | Perform defect review and collect evidence. Withhold visual sign-off and propose a baseline for approval. |
| Brand landing page supplied with a visual reference | Use the full page to derive concrete composition and typography choices, keep the product message specific, and preserve intentional styling when it supports the brief. |
| Requested animated product demo for an existing landing page | Frame one actual product interaction using its visual system. Inspect the motion sequence for trigger, state change, and stable end frame. |
| Multi-page PDF | Inspect every page for pagination and clipping, and save page images as evidence. |

## Done condition

`scripts/check` exits 0 with `GUARD: real home unchanged`. The same eight scenarios are scored for both versions, the candidate covers all eight, and the diff is limited to the listed files.

## Offline comparison

Reviewed the versions from `git show HEAD:skills/ui-design/SKILL.md` and `git show HEAD:skills/ui-polish/SKILL.md` against the working-tree versions.

| Scenario | Baseline | Candidate evidence |
|---|---|---|
| Inventory workspace | Partial. The workflow leads into a product-category search and gives no content-first composition step. | ui-design starts by arranging stock rows, filters and the order action, with cards and catalog results tied to a concrete need. |
| Existing finance page | Covered. The existing design record and targeted search take priority. | ui-design starts with project design decisions. The search reference keeps the approved system authoritative and protects existing exports. |
| Command palette and filter popover | Partial. Generic motion timing and motion accessibility guidance omit immediate shortcut activation and reversal. | ui-design specifies immediate repeated input. ui-polish exercises reversal and reduced motion. |
| Responsive member list | Partial. The checklist calls for layout stability but gives no realistic fixture or required input path. | ui-polish injects difficult values through input fixtures and renders the changed states at the affected widths. |
| Missing baseline | Covered. The old workflow collects screenshots and withholds approval. | ui-polish explicitly continues defect review and keeps the proposed baseline separate from sign-off. |
| Brand landing page | Partial. The old workflow names style keywords but does not derive composition from the full reference. | ui-design studies the whole reference, carries over concrete visual choices, and ties copy and emphasis to the product. |
| Animated product demo | Partial. A static screenshot can establish that the surface is visible but does not validate the sequence. | ui-design frames one actual interaction. ui-polish checks the sequence and frames around the trigger, change and settled state. |
| Multi-page PDF | Covered. The old workflow renders pages, checks pagination, and saves images. | ui-polish keeps all three actions. |

Instruction coverage was 3/8 before and 8/8 after. No model run or rendered UI was evaluated.

`scripts/check` exited 0 with `Ran 108 tests in 54.505s (4 workers)`, `OK`, and `GUARD: real home unchanged`.

## Upstream references and applied guidance

| Reference | Guidance applied |
|---|---|
| [Impeccable critique catalog](https://impeccable.style/slop/) | ui-polish identifies redundant copy and visual clutter on the rendered screen and compares a simpler treatment. |
| [Emil Kowalski's skills](https://aiforui.dev/skills) | ui-design keeps repeated keyboard actions immediate. ui-polish exercises reversals, reduced motion, and realistic hard data. |
| [Meng To's video reference workflow](https://github.com/MengTo/Skills/blob/main/agent-skills/codex/video-to-superprompt/SKILL.md) | ui-design studies the whole page and extracts meaningful frames from video references to explain changes in composition, pacing, and content. |
| [Benji Taylor's Stageshow](https://benji.org/stageshow) | ui-design frames one product interaction around its result. ui-polish inspects its ordered trigger, change, and settled state. |
| [OpenDesign's prototype workflow](https://github.com/nexu-io/open-design#what-is-opendesign) | ui-design previews a small prototype with the project's design tokens when a consequential choice is open and refines it against the brief before broadening the implementation. |
| [Solid Glass material rationale](https://github.com/deeplethe/solid-glass#the-style) | ui-design keeps reading surfaces mostly solid, uses restrained edge and shadow treatments for depth, and checks the actual backgrounds in supported themes. |

These instructions adapt selected ideas. The upstream packages, applications, and design assets are not part of the implementation.
