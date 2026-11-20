---
name: away
description: "Show what can run unattended and keep working while the user is away: list the queued roadmap items, where work would stop, and what still needs approval; then work through the chosen range, parking questions in docs/plans/blocked.md instead of waiting. Use when the user says they are leaving or will be back later (\"자리 비울게\", \"자러 간다\", \"밥 먹고 올게\", \"나갔다 올게\", \"I'm stepping away\"), asks what can be done meanwhile (\"그동안 뭐 할 수 있어?\"), or asks to keep going while they are gone."
---

# Away

The user is about to leave, or has left, and wants work to continue without them. They cannot answer questions, so the job is to do everything that is already approved, park everything that needs them, and make the return quick.

## 1. Briefing (before they leave)

Read `docs/plans/roadmap.md` and the spec of each unchecked item. When there is no roadmap, use the specs in `docs/plans/` by their `Status` line. Show three groups, one line per item with what it changes:

- **Ready:** the spec says `Status: approved`. These run in order without asking.
- **Stops:** approved, but the item includes an action on the approval list (publishing, deploying, deleting outside the change, force-pushing, spending money, sending messages, global configuration). Say which action.
- **Waiting:** no approved spec. Name the decisions each one still needs, so the user can approve now and add it to the queue.

Then ask which range to run. The user sets the goal themselves; offer a sentence they can paste, for example `/goal Work through the roadmap up to <item>, following the away skill.` When nothing is Ready, say so plainly instead of inventing work.

## 2. While they are away

- Work the chosen items in roadmap order. For each: follow its spec, run its done condition, commit, tick it in the roadmap, then start the next.
- A question that would normally go to the user goes to `docs/plans/blocked.md` instead: the item, the question, two or three options with trade-offs, your recommendation, and what you did meanwhile. Then continue with the next item that does not depend on the answer. When a choice is reversible and inside the spec, take the reasonable option, record it as an `observed` decision, and keep going rather than parking it.
- Actions on the approval list are not run unattended, even when the spec is approved. Prepare everything up to that action and park the action itself.
- Three failed attempts on one item: stop that item, record the last error in `docs/plans/blocked.md`, move on.
- Stay inside the chosen range. Finishing early is fine; starting unapproved work is not.

## 3. When they return

Lead with a short report: items finished (with the real check output), items remaining, and every entry in `docs/plans/blocked.md` as one numbered list the user can answer in a single reply. After they answer, record the answers as decisions in the relevant specs and remove the resolved entries.
