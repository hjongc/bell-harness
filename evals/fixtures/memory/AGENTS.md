# Toolkit

A small toolkit of git hooks and an export report for one maintainer.

## Non-goals

- Supporting other version control systems.

## Decision priorities

Working hooks > clear reports > speed.

## Sources of truth

Where to look before a kind of change. Decisions live in `docs/plans/<slug>.md` under `## Decisions`; cite them as `<slug>#D<n>`.

| Task | Look at | Constraints and why |
|---|---|---|
| Change a git hook | `git/hooks`, `docs/plans/hooks.md` | Hook language level (hooks#D1) |
| Change the export report | `docs/plans/export.md` | Report format (export#D2 replaces export#D1) |

## Commands

- Check: none yet

## Skills

- None.

## Permission boundaries

- None beyond the shared list.

## Commit rules

Default

## Evals

none
