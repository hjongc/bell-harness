@AGENTS.md

# Claude Code additions

The imported file is the agreement shared with Codex. These rules apply to Claude Code only.

## Delegate

- When the work goes sideways, stop and re-plan before continuing.
- Claude Code designs and reviews; Codex implements. Delegate an approved spec to the `codex:codex-rescue` subagent with `--fresh --wait`, passing the user goal, the spec path, the authorized scope and the completion check, and end the request with "Do not call create_goal." Use `--resume --wait` only to continue the latest Codex task of this session.
- Leave the model unset so Codex uses its current default. Add `--effort` only when the task clearly needs more or less reasoning than the default, and announce the routing in one line.
- Do work that takes less than about five minutes directly instead of delegating it.
- When a delegated change returns, check the diff against the spec's scope and rerun the completion check yourself before reporting. Codex's sandbox may refuse to write .git; when it reports that, review the working tree and make the commit yourself.

## Phase boundary

- Once the spec is approved, start the handoff without asking again.
- Ask one short question and wait when the user asked to review first, when the spec includes deletions, migrations, CI/CD or infrastructure, or anything public-facing, or when the spec still has an open decision (resolve it first). After the user says to wait, wait.
- Keep the implementation of an approved spec with Codex, so that design review and implementation stay separate.

## Commit trailers

Commit messages carry no `Co-Authored-By` or other attribution trailer, even when a session reminder suggests one: the git hook rejects them, and the user asked for none.
