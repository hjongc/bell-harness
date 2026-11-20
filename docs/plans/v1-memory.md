# v1-memory: decision records and recall rules

Status: approved, inserted before step 3 of the bell-harness v1 plan

## Context
Claude Code and Codex should recall a project's decisions and their reasons when a task touches them, stay quiet when it does not, and follow the newer decision when one is replaced. Their built-in memories are not shared with each other, so the shared medium is documents in git. This step adds no hook and no index: the always-loaded project `AGENTS.md` points to where to look, decisions sit in specs in a fixed format that grep finds, and the global instructions tell both tools to look before changing behavior. Success: `scripts/check` passes with the new decision checks.

## Decisions
- D1: Decisions live in the `## Decisions` section of the spec that made them, one line each in the format below, and both tools find them with grep through the project `AGENTS.md` Sources of truth table -- why: git documents are the only memory both tools read, and a fixed format makes grep precise enough without an index -- by: user -- paths: lib/decisions.py global/AGENTS.md templates/AGENTS.md
- D2: No automatic recall hook and no search index; add one only when a memory eval fails reproducibly, starting with a once-per-session SessionStart hook rather than a per-prompt hook -- why: a lifecycle hook runs on every session or prompt and adds noise and maintenance, and the harness adds hooks only for failures that reproduce -- by: user
- D3: Claude's auto memory and Codex memories are separate stores that the other tool does not read -- why: observed while comparing the two tools' memory features -- by: observed

## Record format
```
- D<n>: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D<n> ...]
```
- `<slug>` is the spec file name without `.md`; other documents cite a decision as `<slug>#D<n>`.
- `by: user` marks what the user decided or approved; `observed` marks something an agent saw once, a hypothesis rather than a rule.
- A changed decision gets a new line with `supersedes`; the old line stays.
- `paths` lists repository paths the decision governs; `lib/decisions.py` reports a path that no longer exists on a decision that is still in force.

## Scope / Non-goals
- In: the files under Changes by file and one commit.
- Out: the stale-decision check in `bin/doctor --project` (step 3, reusing `lib/decisions.py`), the `## Decisions` section in the `spec` skill template (step 4a), the four memory evals (step 4b), hooks, indexes, new skills.

## Changes by file
1. `lib/decisions.py` NEW: `parse(text, slug)`, `check(root)` and a command line that prints `DECISIONS: clean` or one line per problem.
2. `tests/test_decisions.py` NEW.
3. `global/AGENTS.md`: section `## Decisions and recall`.
4. `templates/AGENTS.md` and `AGENTS.md`: Sources of truth as a `Task | Look at | Constraints and why` table.
5. `docs/plans/v1-repo.md`, `docs/plans/v1-hooks-config.md`: `## Decisions` recorded after the fact.
6. `docs/plans/v1-memory.md` (this spec) and `docs/plans/evidence/v1-memory/check.txt`.

## Acceptance tests
1. `tests/test_decisions.py`: fixture text with a malformed line, a duplicate id, an unknown `supersedes` target and a missing path each produce one problem; a missing path on a superseded decision produces none; `check` on this repository returns no problems.
2. `scripts/check` exits 0 and prints `GUARD: real home unchanged`; `python3 lib/privacy.py` prints `PRIVACY: clean`.
3. One commit `feat(memory): add decision records and recall rules`, accepted by `git/hooks/commit-msg`.

## Done criteria
Acceptance 1-3 hold.
