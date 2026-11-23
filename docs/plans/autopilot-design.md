# Design: work through the whole absence, ask with buttons

Status: APPROVED
Mode: Feature
Date: 2026-11-23

## Problem

The user still types "계속" (continue) often: agents end a phase or a task with a plain-text question and stop. And an `away` run usually ends in under an hour, while the user wanted work to continue for the whole time they are gone; a `/goal` run ends the same way.

## Evidence

- `skills/away/SKILL.md` runs only roadmap items with `Status: approved`, then drafts specs for the waiting items and stops (v1.3-away#D5). Today one roadmap item is open, and it waits for a cost approval, so the queue is empty at the start.
- The goal sentence the briefing offers is "work through the roadmap up to <item>", which is met as soon as the queue is empty. Nothing ties the run to the time the user returns.
- Button questions appear only in `skills/probe/references/questions.md` ("When the tool has a question widget, use it"). The global rules and the end-of-task report ask nothing in a form that can be answered with one click.

## Target user and smallest useful version

The harness owner, leaving for hours (sleep, work) with one project open. The smallest useful version: a run that keeps finding grounded work until a given time, puts every result on its own branch and pull request, and greets the user on return with button questions instead of a wall of text.

## Constraints

- Work comes only from documents the user approved: the requirements document, the roadmap and specs. The agent does not invent product direction.
- Code must not grow inefficiently, and each result must be shown to do what the requirement meant.
- The user merges. The agent never merges into main.
- Both tools behave the same: Codex has no question widget in a normal session, so it offers numbered options answered by number.
- Global instruction line caps stay (v1.3-away#D3): `global/AGENTS.md` 70 lines, now 64.

## Premises

1. A run lasts until a time the user gives, not until a list is empty.
2. A requirements document with numbered requirements, acceptance criteria and a status per requirement lets an agent pick unbuilt work without guessing.
3. That document is built through a button interview at the start and refined through short interviews later (on return, at milestones), so every requirement is user-approved.
4. A requirement the user approved is enough approval for the agent to write its spec and implement it unattended, including hard-to-reverse changes and the actions on the global approval list when the requirement names them.
5. Pull requests are reviewed before merge, so per-item branches make unattended changes safe to discard.
6. An implementer grading its own work misses scope growth; a reviewer that sees only the requirement and the diff does not share that bias.

## Approaches considered

### A: Extend the existing skills (minimal)
`away` gets a deadline and a work-source loop; `probe` gets a requirements mode; `spec` gets a size budget; one new template `templates/requirements.md`; one global rule for button questions. Effort: one spec, about six files. Risk: `away` grows past a short body; move the loop detail into `skills/away/references/` if it does. Reuses the roadmap, blocked.md, preflight and the decision format.

### B: New `requirements` and `autopilot` skills (ideal separation)
Separate skills for the requirements interview and the unattended loop; `away` stays a briefing. Cleaner boundaries, but two more skills to route between `away`, `probe` and `map`, more eval cases, and more text for both tools to load. Rejected for now: the harness prefers less code (decision priorities).

### C: A standing Stop hook that re-prompts until the deadline (lateral)
Keeps a session alive mechanically. Rejected: v1.3-away#D1 chose a per-session goal over a standing hook, and a hook would fire in sessions where the user did not leave.

## Recommended approach

A: extend the existing skills. The user approved it on 2026-11-23.

## Skill plan

| Skill | Requirement and reason | Phase |
|---|---|---|
| `spec` | Turn this design into an executable spec with a done condition | After approval |
| `preflight` | Review the diff against scope and size | Before the first push |
| `eval` | Behavior change in `away`, `probe` and the global rules needs before and after cases | After implementation |

## Decisions

- D1: Every question to the user goes through the host's question widget with two to four options, the recommended option first; a host without a widget gets numbered options answerable by number. A finished task ends with its next-step choices in the same form -- why: the user wants to answer with one click instead of typing "계속" -- by: user -- paths: global/AGENTS.md skills/probe/references/questions.md
- D2: An away run ends at a time the user gives in the briefing; the goal sentence names that time, and running out of one work source moves to the next instead of ending the run -- why: runs ended in under an hour while the user was gone for much longer -- by: user -- paths: skills/away/SKILL.md
- D3: Work sources, in order: approved roadmap items; requirements with status `todo` in `docs/requirements.md`, for which the agent writes and implements a spec; audit passes that find bugs, waste and code that can shrink without changing behavior; and last, new questions about gaps in the requirements, parked for the user -- supersedes: v1.3-away#D5 -- why: the user asked the agent to write and carry out specs from the planning documents and to catch bugs and audit findings, while guarding against bloated code -- by: user -- paths: skills/away/SKILL.md
- D4: A project's requirements live in `docs/requirements.md` from `templates/requirements.md` (id, requirement, acceptance criteria, status, implementing spec); `probe` builds it in a button interview and updates it in short interviews on return and at milestones; the project AGENTS.md lists it with the other planning documents -- why: without ids and status the agent guesses what is built; the user wants the document built and kept current through interviews -- by: user -- paths: templates/requirements.md templates/AGENTS.md skills/probe/SKILL.md
- D5: During an away run, a spec traced to an approved requirement counts as approved, including hard-to-reverse changes; an action on the global approval list (deploy, spending, sending, global configuration, force-push) runs only when the requirement itself names it, and the agent cannot add one in a spec it wrote -- supersedes: v1.3-away#D2 -- why: the user chose "everything in the planning documents, including those actions when the spec names them"; tying the action to the requirement keeps the user, not the agent, as the source of the approval -- by: user -- paths: skills/away/SKILL.md global/AGENTS.md
- D6: Each self-written spec states a net line budget; after implementation a fresh reviewer that sees only the requirement, the spec and the diff judges whether it meets the acceptance criteria and whether a smaller change would do; an item over budget or failing review gets no pull request and goes to `docs/plans/blocked.md` with its branch kept -- why: the user wants bloat prevented and intent verified, and self-review shares the implementer's blind spots -- by: user -- paths: skills/away/SKILL.md skills/spec/SKILL.md
- D7: Each item gets its own branch named for its meaning (`feat/<topic>`, `fix/<topic>`, `refactor/<topic>`), commits split by meaning, and a regular (not draft) pull request whose body names the requirement, the check output and the size; an item that depends on an unmerged one stacks on that branch and says so; the user merges -- why: the user asked for meaningful branches, commits and pull requests, and chose regular pull requests -- by: user
- D8: On return, the report leads with merged-ready pull requests and the check results, then asks every `docs/plans/blocked.md` entry as button questions, four per prompt -- why: the user wants to answer with buttons rather than a numbered text reply -- by: user -- paths: skills/away/SKILL.md

## Edge cases and failure modes

- No `docs/requirements.md`: the run uses the roadmap and audit sources only and parks "build the requirements document" as the first return question.
- The deadline passes mid-item: finish the current commit, push the branch, open the pull request only if the review passed, then report.
- Three failures on one item: stop it, record the last error in blocked.md, continue with the next source (unchanged from v1.3).
- Audit passes find nothing for a full pass: move to requirement-gap questions; when those are exhausted too, end early and say why.
- This repository: `bin/setup` and live evals still run only when the user asks (project AGENTS.md takes precedence over the global rules).

## Success criteria

- `away` briefing asks for the return time and the range with the question widget and outputs a goal sentence containing the time.
- In an offline fixture with an empty roadmap and one `todo` requirement, the run writes a spec, implements it on `feat/<topic>`, records a review verdict, and opens a pull request (mocked `gh`).
- An item over its line budget produces no pull request and one blocked.md entry.
- `global/AGENTS.md` stays within 70 lines with the button rule; `scripts/check` passes.
- Eval: with the rule, an agent ending a task offers next-step choices; graded on observable output.

## Open questions

- How long one review may run before the item is parked. Default: one review per item, no retries.
- Whether audit refactors that shrink code should batch several small ones into one pull request. Default: one pull request per finding.

## The Assignment

Pick one project you will leave running tonight, and list the planning documents it already has (requirements, PRD, design notes) so the first requirements interview starts from them.
