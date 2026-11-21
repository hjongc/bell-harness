---
name: spec
description: Turn an agreed design into an implementation spec at docs/plans/<slug>.md that another agent or model can execute without judgment calls, with acceptance tests and a done condition a command can check. Use when the user says "spec", "스펙", "compile the plan", when a probe session ends, before delegating implementation to another agent or an unattended run, or when work will span sessions or change shared behavior.
---

# Spec

The spec is the prompt for whoever implements it, possibly a different tool or a smaller model in a later session. Anything not written in it does not exist for the implementer, so it carries the scope, the decisions with their reasons, and a completion check that a command can verify.

## Inputs

- The conversation, and `docs/plans/<slug>-design.md` when a probe session produced one.
- The project's AGENTS.md (Sources of truth table, commands, permission boundaries) and `tasks/lessons.md`.
- Decisions already in force for the touched paths: `grep -rn "<path or topic>" docs/plans`, then check none of them is superseded (`grep -rn "<slug>#D<n>" docs/plans`).
- The code itself: find what can be reused before specifying anything new.

## Before writing

Every decision is settled. When one is still open, ask the user now (options, trade-offs, your recommendation) or move the item to Non-goals; a spec with an open question pushes the judgment onto the implementer.

## Template

```markdown
# <slug>: <title>

Status: draft | approved | implemented (<commit>)

## Context
Two or three sentences: why this change, and the one-line definition of success.

## Decisions
- D1: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D<n>]

## Scope / Non-goals
- In: <what is in>
- Out: <what is explicitly out, and where it goes instead>
- Dependencies: <none beyond what the project already uses, or the exact new one>

## What already exists
- <file or helper to reuse, and how>

## Changes by file
1. `path/to/file` NEW | DELETE | <what changes, imperative>

## Interfaces
Exact signatures, schemas, command lines and output formats, in code blocks.

## Failure modes
| Situation | How it shows | Handling |
|---|---|---|

## Do not
- <tempting actions that are out of bounds: files not to touch, approaches not to take, commands not to run>

## Visual verification (only when the change is visible)
What to look at, at which widths, with which tool, and the evidence path `docs/plans/evidence/<slug>/`.

## Acceptance tests
1. <command and expected output, or an observable fact>

## Done criteria
One checkable condition, for example: `scripts/check` exits 0 AND acceptance 1-4 hold AND only the files in Changes by file changed.
```

## Writing rules

- Each acceptance test is executable or observable; "works correctly" is not a test.
- Put scope inside the done condition ("only the listed files changed", "no new dependency") so a grader that rechecks it every turn also enforces scope.
- Record each decision with its reason in `## Decisions`, so a later session or the other tool can find it with grep. Use `user` for what the user decided or approved and `observed` for something seen once.
- Keep the spec under about 150 lines. A longer one usually means two specs.
- Name no model and no reasoning effort in the spec; the person or tool that runs it chooses.

## Cross-session work

When pausing unfinished implementation, update the active spec with the working revision, the last verification command and result, and the next unchecked acceptance item. Include decision ids for any constraint the next session needs. On resume, compare the revision and local diff with the checkpoint before using an earlier result. Replace the checkpoint as work progresses.

## Unattended runs

When the spec will run without a person watching (overnight, a goal loop), add:

```markdown
## Unattended rules
1. Ambiguity: take the conservative option, add one `observed` line to Decisions, continue.
2. Three failures on one item: stop that item, record the last error under Blocked, move on.
3. Do not touch: <CI config, migrations, secrets, unrelated modules>.
4. No force-push, branch deletion, destructive migration or unlisted dependency.
```

## After writing

Show the path and a short summary. What happens next follows the tool's own instructions for approval and delegation (for Claude Code, the Phase boundary rules in its CLAUDE.md). When the user asked to review first, or the spec touches deletions, migrations, CI/CD, infrastructure or anything public, wait for approval.
