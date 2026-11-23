# autopilot: work through the whole absence, ask with buttons

Status: implemented (9ca80ec)

## Context

Agents stop at phase ends with plain-text questions, so the user keeps typing "계속" (continue). And `away` runs end in under an hour because they run only approved roadmap items and then draft specs. Success: questions and next steps arrive as one-click choices, and an away run keeps doing grounded, reviewed work until the time the user returns, each result on its own branch and pull request. Design: [autopilot-design.md](autopilot-design.md).

## Decisions

- D1: Every question to the user goes through the host's question widget with two to four options, the recommended option first; a host without a widget gets numbered options answerable by number. A finished task ends with its next-step choices in the same form -- why: the user wants to answer with one click instead of typing "계속" -- by: user -- paths: global/AGENTS.md skills/probe/references/questions.md
- D2: An away run ends at a time the user gives in the briefing; the goal sentence names that time, and running out of one work source moves to the next instead of ending the run -- why: runs ended in under an hour while the user was gone much longer -- by: user -- paths: skills/away/SKILL.md
- D3: Work sources, in order: approved roadmap items; requirements with status `todo` in `docs/requirements.md`, for which the agent writes and implements a spec; audit passes for bugs, waste and code that can shrink without changing behavior; last, questions about gaps in the requirements, parked for the user -- why: the user asked the agent to write and carry out specs from the planning documents, to catch bugs and audit findings, and to guard against bloated code -- by: user -- paths: skills/away/SKILL.md skills/away/references/run.md -- supersedes: v1.3-away#D5
- D4: A project's requirements live in `docs/requirements.md` from `templates/requirements.md` (id, requirement, acceptance criteria, status, spec); `probe` builds it in a button interview and updates it in short interviews on return and at milestones; the project AGENTS.md points to it -- why: without ids and status the agent guesses what is built; the user wants it built and kept current through interviews -- by: user -- paths: templates/requirements.md templates/AGENTS.md skills/probe/SKILL.md
- D5: During an away run, a spec traced to an approved requirement counts as approved, including hard-to-reverse changes; an action on the global approval list runs only when the requirement itself names it, and the agent cannot add one in a spec it wrote -- why: the user chose "everything in the planning documents, including those actions when the spec names them"; anchoring to the requirement keeps the user as the source of the approval -- by: user -- paths: skills/away/SKILL.md global/AGENTS.md -- supersedes: v1.3-away#D2
- D6: Each self-written spec states a net line budget; after implementation a fresh reviewer that sees only the requirement, the spec and the diff judges whether the acceptance criteria hold and whether a smaller change would do; an item over budget or failing review gets no pull request and goes to `docs/plans/blocked.md` with its branch kept -- why: the user wants bloat prevented and intent verified, and self-review shares the implementer's blind spots -- by: user -- paths: skills/away/references/run.md skills/spec/SKILL.md
- D7: Each away item gets its own branch named for its meaning (`feat/<topic>`, `fix/<topic>`, `refactor/<topic>`), commits split by meaning, and a regular pull request whose body names the requirement, the check output and the size; an item that depends on an unmerged one stacks on that branch and says so; the agent never merges -- why: the user asked for meaningful branches, commits and regular pull requests -- by: user -- paths: skills/away/references/run.md
- D8: On return, the report leads with the opened pull requests and their check results, then asks every `docs/plans/blocked.md` entry as button questions, up to four per prompt -- why: the user wants to answer with buttons -- by: user -- paths: skills/away/SKILL.md
- D9: Independent questions may share one widget prompt (up to four); dependent ones go one at a time -- why: batching four independent choices in the design interview for this spec took two prompts instead of eight, and the user answered without friction -- by: observed -- paths: skills/probe/references/questions.md

## Scope / Non-goals

- In: the files under Changes by file.
- Out: a Stop hook or any standing loop (v1.3-away#D1 stands); new skills; changes to `bin/`, `lib/`, hooks or `config/`; running `bin/setup` or live evals; creating `docs/requirements.md` for this repository (that is the user's first interview, after merge).
- Out: an offline fixture that runs a whole away loop. The first real overnight run is the field test; its result goes into this spec's Decisions.
- Dependencies: none.

## What already exists

- `skills/away/SKILL.md` briefing groups, blocked.md format and three-failure rule: keep them.
- `skills/spec/SKILL.md` `## Unattended rules` block: extend it with the size budget.
- `skills/probe/references/questions.md` already says to use the question widget: generalize it.
- `evals/cases/away-gate-ko.json`: its publish action is not named in a requirement, so it must still be parked; keep the case unchanged.

## Changes by file

1. `global/AGENTS.md`: in Communication, add one line for D1 (widget, two to four options, recommended first, numbered fallback; end a task with next-step choices). After the approval paragraph, add one line for D5 pointing to the `away` skill. Stay within 70 lines.
2. `skills/away/SKILL.md`: briefing asks the return time and the range in one widget prompt and ends with a goal sentence that names the time (D2). Replace "While they are away" with the source order (D3), the approval rule (D5) and a pointer to `references/run.md`. Replace the drafting paragraph (old D5). Return step per D8. Update the description to mention the return time.
3. `skills/away/references/run.md` NEW: per-item procedure: branch naming and stacking (D7), self-written spec from a requirement with a line budget, implementation, `scripts/check` or the project check, the fresh reviewer brief and verdict format (D6), pull request body, updating the requirement status and the roadmap; audit pass procedure (what to look for, one pull request per finding); the deadline check (`date`) before starting each item and what to do when it passes mid-item.
4. `templates/requirements.md` NEW: header, how to use it, and a table `| ID | Requirement | Acceptance criteria | Status | Spec |` with status values `todo`, `in-progress`, `done`, `dropped`, plus one example row.
5. `templates/AGENTS.md`: in Sources of truth, one sentence: requirements live in `docs/requirements.md`. Stay within 60 lines.
6. `skills/probe/SKILL.md`: add a Requirements mode: build `docs/requirements.md` from the template in a button interview starting from existing planning documents, or update it in a short interview (on return, at a milestone). Each new row is user-approved.
7. `skills/probe/references/questions.md`: replace the widget rule with D1 and D9.
8. `skills/spec/SKILL.md`: add rule 5 to Unattended rules: `Size budget: net +<n> lines; over budget means no pull request.`
9. `skills/map/SKILL.md`: in step 2 read `docs/requirements.md` when present; in the report, suggest the probe requirements interview when it is missing.
10. `evals/cases/away-deadline-ko.json` NEW: fixture `flow-gate`, hosts claude and codex, prompt `7시까지 자리 비울게. 그동안 할 수 있는 거 진행해줘.`, expect_skill `away`, expect_answer `(?i)/goal[^\n]*(7시|07:00|7:00|19:00)`.
11. `tests/test_instructions.py`: assert `global/AGENTS.md` mentions the question widget and the numbered fallback.
12a. `tests/test_evals.py`: update the fixed case count from 27 to 28 for the new away case.
12. `tests/test_skills.py`: assert `templates/requirements.md` has the five column headers and the four status values; assert `skills/away/SKILL.md` references `references/run.md`.
13. `README.md`: rewrite "Working while you are away" for the deadline, sources, branches and pull requests, and the requirements document; update the eval case count.
14. `AGENTS.md`: add `templates/requirements.md` to the Instruction files row and cite autopilot#D1 and autopilot#D5; move `Checked at` to the new HEAD.
15. `docs/plans/roadmap.md`: add `- [ ] autopilot: work through the whole absence, ask with buttons`; tick it when done.
16. `docs/plans/autopilot.md`: set `Status: implemented (<commit>)` at the end.

## Interfaces

Goal sentence produced by the briefing:

```text
/goal Until <HH:MM> <timezone>, keep working per the away skill: roadmap items through <item>, then todo requirements, then audit passes; open one pull request per item.
```

Reviewer verdict, appended to the pull request body and to blocked.md on failure:

```text
Review: PASS|FAIL -- acceptance: <met|unmet: which> -- smaller change: <none|description> -- size: +<added> -<removed> (budget +<n>)
```

## Failure modes

| Situation | How it shows | Handling |
|---|---|---|
| No `docs/requirements.md` | file missing | skip that source; first return question offers the requirements interview |
| Deadline passes mid-item | `date` past the time | finish the commit, push the branch, open the pull request only if review passed, report |
| Over budget or review FAIL | verdict line | no pull request; blocked.md entry with branch name and verdict |
| `gh` unavailable or not signed in | `gh auth status` fails | push branches, list them in the report, ask to open pull requests on return |
| Approval-list action not named in a requirement | spec mentions it | park the action in blocked.md (unchanged behavior, keeps away-gate-ko valid) |

## Do not

- Do not add a hook, a new skill, or code under `bin/`, `lib/`, `git/` or `config/`.
- Do not change `evals/cases/away-gate-ko.json` or the flow cases.
- Do not run `bin/setup`, `python3 evals/run.py` or `git push`.
- Do not use emphasis words that `tests/test_skills.py` rejects.

## Acceptance tests

1. `wc -l global/AGENTS.md` is at most 70 and `wc -l templates/AGENTS.md` at most 60.
2. `grep -n "references/run.md" skills/away/SKILL.md` matches; `skills/away/references/run.md` exists.
3. `grep -c "todo\|in-progress\|done\|dropped" templates/requirements.md` is at least 4.
4. `python3 lib/decisions.py` exits 0 and reports v1.3-away#D2 and #D5 as superseded by autopilot.
5. `python3 -c "import json;json.load(open('evals/cases/away-deadline-ko.json'))"` exits 0.
6. `scripts/check` exits 0.

## Done criteria

`scripts/check` exits 0 AND acceptance 1-5 hold AND `git diff --name-only main` lists only the files in Changes by file.
