# <Project name>

<One paragraph: what this project is, who uses it, and the outcome it exists to produce.>

## Non-goals

- <What this project deliberately does not do.>

## Decision priorities

<When goals conflict, which wins, in order. Example: correct numbers > clear explanation > speed > visual polish.>

## Sources of truth

Where to look before a kind of change. Planned work is listed in order in docs/plans/roadmap.md. Write paths in the second column in backticks or as Markdown links so bin/doctor can check them. Decisions live in `docs/plans/<slug>.md` under `## Decisions`; cite them as `<slug>#D<n>`.

| Task | Look at | Constraints and why |
|---|---|---|
| <Kind of change> | <Entry points, tests, data or designs> | <Rule, with the decision id or document that explains it> |

Checked at <short commit>

## Commands

- Check: `scripts/check` <or the project's single verification command>
- <Run, build and deploy commands, and which of them need approval.>

## Skills

- <Harness or project skills that apply here, and when to use them.>

## Permission boundaries

- <Actions that need the user's approval in this project beyond the shared list, such as publishing, orders or production data.>

## Commit rules

<"Default", or the variation recorded in `.harness.json`, such as a Korean summary.>

## Evals

<The evaluation command for prompt, model or agent changes, or "none".>
