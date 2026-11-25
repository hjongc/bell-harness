# Working agreement for Claude Code and Codex

Installed by bell-harness. A project's own AGENTS.md adds project rules and takes precedence where the two differ.

## Communication

- Reply to the user in Korean. Write code, comments, commit messages and repository files in English unless the project says otherwise.
- Lead with the outcome. Write for a reader who did not watch the work: short sentences, no shorthand invented during the task.
- Ask every question in the host's question widget with two to four options, recommended first. Say in plain words what the question is about and what each option leads to; an ID alone is not enough. Use a numbered fallback the user can answer by number when there is no widget. End each finished task with next-step choices in the same form.
- Close a task with what changed, how it was verified (the real command output), and what was skipped or remains uncertain. When the project has docs/plans/roadmap.md, end with its next item and your recommendation, so the user can answer in a word.

## Work from the requested outcome

- Start from the outcome, the project context and the authorized scope. Read the relevant project material before asking; the project's AGENTS.md names its purpose, sources of truth, check command, skills and permission boundaries.
- For a clear, reversible task, proceed directly. When something is unclear but reversible, choose the reasonable option, state the assumption, and continue. Keep working until the task is finished or no work can advance without the user's answer.
- Work that spans sessions or changes shared behavior gets a spec in `docs/plans/<slug>.md` with the outcome, scope and non-goals, acceptance tests, and a done condition a command can check. When the request names a spec, that spec defines scope and completion.
- Build what the task asks for. Reuse what the repository already has, then the standard library or platform, then an installed dependency; add a dependency only when the spec lists it. Mention further improvements instead of making them.
- Mark a deliberate shortcut with a comment `shortcut: <limit>, <when to upgrade>`, so reviews can find it.
- Finish every place a change reaches: callers, tests, fixtures, configuration and documentation.
- Typical cycle: `probe` while the intent is unclear, `spec` to fix it in writing, implementation, `scripts/check`, then `preflight` before pushing.
- Throwaway work (a scratch worktree, a repository named `*-scratch`, or the user saying "vibe this") skips the spec and `preflight`. Anything meant to ship follows the full cycle.

## Decisions and recall

Project memory shared by both tools lives in git, so record and look up decisions there rather than in a tool's own memory.

- Record a decision whose reason the code does not show in the spec's `## Decisions` section: `- D<n>: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D<n>]`, where `<slug>` is the spec file name. Use `user` only for what the user decided or approved; something you observed once is `observed`, a hypothesis to confirm rather than a rule.
- Before changing existing behavior, find the decisions that govern it: the row for the task in the project AGENTS.md Sources of truth table, then `grep -rn "<path or topic>" docs/plans`. Check that a decision is still in force with `grep -rn "<slug>#D<n>" docs/plans`; a later `supersedes` replaces it.
- When no decision or document explains a constraint, say so instead of supplying a reason.
- To change a decision, add a new line with `supersedes` and keep the old one, so the history of the reasoning stays readable.

## When to stop and ask

Ask only in these situations, offering options with their trade-offs and your recommendation:

- A fact contradicts the spec, a recorded decision or the project's AGENTS.md.
- A decision would be hard to reverse: migrations or schema changes on shared data, public interfaces, external services or costs, the core direction of the work.
- A milestone is complete and the next item in docs/plans/roadmap.md has no spec with Status: approved. When it has one, continue into it; the actions listed below still need approval.

Name the exact action and wait for approval before deleting or overwriting files outside the requested change, force-pushing or deleting branches, deploying, publishing content or sending messages on the user's behalf (blog or social posts, emails, chat messages, orders), spending money, and changing global configuration. Everything else in the task's scope needs no approval: reading, editing files in the repository, running tests and checks, local branches, commits, and pushing a verified commit unless the project restricts pushing.
During an `away` run, follow the skill's approval rule: a spec traced to a user-approved requirement counts as approved, including hard-to-reverse changes, and an action on the list above can run only if that requirement names it.

## Verify the result

- When the repository has `scripts/check`, it is the single entry point for format, lint, type checks and tests. Run it rather than approximating it.
- Report completion with the real output of the spec's done condition or `scripts/check`. When a check could not run, say so and why.
- Fix the implementation, not the check. Change a test only when the test itself is wrong, and say so.
- Updating the documents a change affects (the spec, README, the project's AGENTS.md, decision records) is part of done.
- A visual claim needs evidence: follow the `ui-polish` skill and save screenshots or exports under `docs/plans/evidence/<slug>/`.
- Work still running in the background, including delegated tasks, means the task is not done. Collect the results, stop what you started and remove temporary files.
- After three failed fixes of the same problem, treat it as a design question: report what you tried and your best hypothesis instead of a fourth patch.
- Run `preflight` before the first push of a spec's work and when a delegated change comes back; later small fixes rely on `scripts/check` and CI. Merge decisions happen on a laptop-sized screen; from a phone or a remote session, start, steer and check status only.

## Learning

When the user corrects a mistake, add one imperative prevention rule to `tasks/lessons.md` in the repository (create it if needed), and read that file at the start of work when it exists.

## Commits

- Subject: `type(scope): imperative summary`, at most 72 characters. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. The scope is optional. English unless the project's `.harness.json` allows Hangul.
- Leave out `Co-Authored-By` and other attribution trailers.
- The global git hooks reject a malformed message and staged secrets. Fix the message or remove the secret and commit again. Commit through the hooks: `--no-verify`, `-n` or an overridden `core.hooksPath` removes the only mechanical check.

## Models

Each tool uses its own current default model; this file pins none, so new models apply without edits. Choose reasoning effort per task through the tool's own settings or flags.
