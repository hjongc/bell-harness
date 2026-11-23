---
name: away
description: "Show what can run unattended and keep working until the user's return time: list the queued roadmap items and approval gates, then advance through the chosen range and other grounded work. Use when the user says they are leaving or will be back later (\"자리 비울게\", \"자러 간다\", \"밥 먹고 올게\", \"나갔다 올게\", \"I'm stepping away\"), asks what can be done meanwhile (\"그동안 뭐 할 수 있어?\"), or asks to keep going while they are gone."
---

# Away

The user is about to leave, or has left, and wants work to continue without them. They cannot answer questions, so the job is to do everything that is already approved, park everything that needs them, and make the return quick.

## 1. Briefing (before they leave)

Read `docs/plans/roadmap.md`, the spec of each unchecked item, and `docs/requirements.md` when present. When there is no roadmap, use the specs in `docs/plans/` by their `Status` line. Show exactly these three groups under these headings, one line per item with what it changes; write "none" for an empty group so the user can see nothing was skipped. List only roadmap items; mention other pending work in one closing line at most:

- **Ready:** the spec says `Status: approved`. These run in order without asking.
- **Stops:** approved, but an action needs approval under the rule below. Say which action and how far work can proceed.
- **Waiting:** no approved spec. Name the decisions each one still needs, so the user can approve now and add it to the queue.

Ask for the return time and the roadmap range in one question widget prompt. Offer two to four choices per question, recommended first, or numbered choices answerable by number when there is no widget. Reuse any answer the user already gave and ask only for missing details. Resolve an ambiguous time with explicit date, time and timezone choices. When nothing is Ready, say so and use "none" for the roadmap range.

End the briefing with the goal sentence the user can paste, filling in the agreed time, timezone and range. If an answer is pending, label the sentence as proposed and use the recommended choices. The user sets the goal.

```text
/goal Until <HH:MM> <timezone>, keep working per the away skill: roadmap items through <item>, then todo requirements, then audit passes; open one pull request per item.
```

## 2. While they are away

Use these sources in order. When one is exhausted, move to the next. Read `references/run.md` for the deadline check and the per-item procedure.

1. Work the approved items in the chosen roadmap range in order.
2. Write and implement specs for user-approved requirements marked `todo` in `docs/requirements.md`. Skip this source if the file is missing and make the requirements interview the first question on return.
3. Audit the existing implementation for bugs, waste and code that can shrink while preserving behavior. Ground each finding in project evidence.
4. Look for gaps in the planning documents and park questions about them. If a full audit and gap pass leave no grounded work, report the exhaustion and why the run ended early.

- A spec traced to a user-approved requirement counts as approved, including hard-to-reverse changes. An action on the global approval list can run only if the approved requirement itself names it. Park actions named only by a spec and honor stricter project or session restrictions.
- A question that would normally go to the user goes to `docs/plans/blocked.md` instead: the item, the question, two or three options with trade-offs, your recommendation, and what you did meanwhile. Then continue with the next item that does not depend on the answer. When a choice is reversible and inside the spec, take the reasonable option, record it as an `observed` decision, and keep going rather than parking it.
- Three failed attempts on one item: stop that item, record the last error in `docs/plans/blocked.md`, move on.

## 3. When they return

Lead with opened pull requests and their real check results, then list branches awaiting pull requests and remaining work. Offer to open pending pull requests if GitHub CLI access blocked them. If the requirements file is missing, offer the `probe` requirements interview first. Offer a short requirements update interview when the run exposed changes to review.

Ask every entry in `docs/plans/blocked.md` using the question widget, with up to four independent questions per prompt and dependent questions one at a time. Use two to four options per question, recommended first, with numbered choices answerable by number when there is no widget. After the user answers, record their decisions in the relevant specs and remove the resolved entries. End with next-step choices in the same form if there are no decisions left to ask.
