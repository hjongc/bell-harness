# v1-skills: six shared skills, sources and README

Status: implemented by Claude directly (step 4a of the bell-harness v1 plan); ui-design and ui-polish were ported by subagents and reviewed

## Context
The harness ships six skills that both Claude Code and Codex load from the same folders (`bin/setup` links `skills/<name>` into `~/.claude/skills` and `~/.agents/skills`). This step writes them, records where each comes from, and adds the README. Success: `scripts/check` passes with the skill format tests and the privacy scan stays clean.

## Decisions
- D1: The six skills are probe, spec, preflight, eval, ui-polish and ui-design, one copy shared by both tools -- why: the user approved this list in the v1 plan, and one copy keeps the tools consistent -- by: user -- paths: skills tests/test_skills.py
- D2: SKILL.md holds the flow and when to use it; question lists, templates and data sit in `references/`, `scripts/` and `data/` and load on demand -- why: a skill body loads when triggered, so keeping it short saves context in every session that uses it -- by: user -- paths: skills/probe/references skills/ui-design/references
- D3: Third-party material keeps its MIT notice in `licenses/` and is listed in SOURCES.md with what changed -- why: the repository is public and MIT requires the notice -- by: user -- paths: SOURCES.md licenses
- D4: probe writes `docs/plans/<slug>-design.md` and spec writes `docs/plans/<slug>.md`, both with decision lines in the v1-memory format -- why: git documents are the memory both tools share (v1-memory#D1) -- by: user -- paths: skills/probe/SKILL.md skills/spec/SKILL.md
- D5: ui-design saves approved design choices to the project's `docs/design-system.md`, and ui-polish withholds a verdict when no baseline exists -- why: without a recorded reference, visual review drifts with taste -- by: user -- paths: skills/ui-design/SKILL.md skills/ui-polish/SKILL.md
- D6: The vendored JavaFX guide's placeholder home path is allowed in `.privacy-allow` instead of editing the data -- why: vendored data stays unchanged so updates can be diffed against upstream -- by: observed -- paths: .privacy-allow

## Scope / Non-goals
- In: the files under Changes by file and one commit.
- Out: the evals runner and memory evals (step 4b), installing on the real machine (step 5).

## Changes by file
1. `skills/probe/SKILL.md`, `skills/probe/references/questions.md`, `skills/probe/references/design-doc.md` NEW.
2. `skills/spec/SKILL.md`, `skills/preflight/SKILL.md`, `skills/eval/SKILL.md` NEW.
3. `skills/ui-polish/` NEW (SKILL.md, `scripts/ui-check.mjs`).
4. `skills/ui-design/` NEW (SKILL.md, `references/`, `scripts/`, `data/`), `licenses/ui-ux-pro-max.txt`, `licenses/gstack.txt` NEW.
5. `tests/test_skills.py`, `tests/test_ui_design.py` NEW.
6. `SOURCES.md`, `README.md`, `.privacy-allow` NEW; `AGENTS.md` Sources of truth row for skills.
7. This spec and `docs/plans/evidence/v1-skills/check.txt`.

## Acceptance tests
1. `tests/test_skills.py`: exactly the six skills; each SKILL.md has frontmatter `name` equal to its folder and a `description` of 1-1024 characters containing "Use "; at most 250 lines; no all-caps emphasis; every `references/` or `scripts/` file it names exists; both license files exist and SOURCES.md names every skill.
2. `tests/test_ui_design.py`: `search.py "fintech dashboard"` under the system Python exits 0 with output.
3. `scripts/check` exits 0 with `GUARD: real home unchanged`; `python3 lib/privacy.py` prints `PRIVACY: clean`; `python3 lib/decisions.py` prints `DECISIONS: clean`.

## Done criteria
Acceptance 1-3 hold and one commit `feat(skills): add six shared skills, sources and readme` records the step.
