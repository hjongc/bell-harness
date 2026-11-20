# v1-hooks-config: git hooks, host config and global instructions

Status: implemented (152a0f1), step 2 of 4 of the bell-harness v1 plan

## Context
Step 2 adds the mechanical enforcement and the instruction files that `bin/setup` (step 3) will install: git hooks for commit messages and staged secrets, a Claude settings fragment, Codex execution rules, the list of retired legacy items, the two global instruction files, and the project template. Everything stays inside the repository and is tested offline. Success: `scripts/check` passes with the new tests and the step lands as one commit.

## Decisions
- D1: Commit subjects are `type(scope): imperative summary` in English, at most 72 characters; a project may allow a Korean summary through `.harness.json`; attribution trailers such as `Co-Authored-By` are rejected -- why: the user asked for one format across tools and for no attribution trailers -- by: user -- paths: git/hooks/commit-msg
- D2: Always-loaded instruction files state goals, constraints and reasons, stay under fixed line limits, and avoid all-caps emphasis and absolute wording -- why: current Claude and GPT prompting guides report that models over-react to emphasis, and every line costs context in every session -- by: user -- paths: global/AGENTS.md global/CLAUDE.md templates/AGENTS.md tests/test_instructions.py
- D3: Shared instruction files pin no model and no reasoning effort; each tool keeps its own default -- why: new models then apply without edits, and effort settings differ per model -- by: user -- paths: global/AGENTS.md

## Scope / Non-goals
- In: the files under Changes by file and one commit.
- Out: `bin/setup`, `bin/doctor` (step 3), skills, README and SOURCES (step 4). Nothing is installed into the real home directory and the global git config stays unchanged; tests use temporary repositories and a temporary `GIT_CONFIG_GLOBAL`.
- No dependencies beyond the Python 3.9 standard library, POSIX sh and git.

## What already exists
- `lib/patterns.py`: `SECRET_PATTERNS`, reused by the pre-commit hook; do not duplicate the regexes.
- `scripts/check`: runs `tests/` and the real-home guard.
- `.archive/docs/plans/harness-core.md` §1-§4: the earlier hook design, for reference only. This spec supersedes it.

## Changes by file
1. `git/hooks/commit-msg` NEW, python3 (Interfaces §1).
2. `git/hooks/pre-commit` NEW, python3 (§2).
3. `git/hooks/_chain` NEW, POSIX sh (§3), plus one regular-file copy of `_chain` (not a symlink) for every other hook name listed in §3. All hook files mode 0755.
4. `config/claude-settings.json`, `config/bell-harness.rules`, `config/retire.json` NEW (§4-§6).
5. `global/AGENTS.md`, `global/CLAUDE.md`, `templates/AGENTS.md` NEW: Appendices A, B and C verbatim.
6. `tests/harness_env.py` NEW (§7).
7. `tests/test_hooks.py`, `tests/test_config.py`, `tests/test_instructions.py` NEW (Acceptance 1-3).
8. `docs/plans/v1-hooks-config.md` (this spec) and `docs/plans/evidence/v1-hooks-config/check.txt` (complete output of the final `scripts/check` run).

## Interfaces
§1 `commit-msg <msgfile>`
- Comment character: `git config --get core.commentChar`; unset or `auto` means `#`. Drop lines that start with it, and everything from the scissors line `<char> ------------------------ >8 ------------------------` onward.
- Normalize to NFC. The subject is the first non-empty line. An empty message is rejected with reason `empty message`.
- Subjects starting with `Merge `, `Revert "`, `Reapply "`, `fixup! `, `squash! ` or `amend! ` pass without further checks.
- Project config comes only from `git show HEAD:.harness.json` (when HEAD exists and contains the file), never from the working tree or the index, so a commit cannot loosen its own rules. Keys under `commit`: `subject_pattern` (default `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^()\s]+\))?!?: \S.*$`), `max_subject` (default 72), `allow_hangul` (default false). Invalid JSON is rejected with reason `invalid .harness.json`.
- Reject when the subject misses the pattern, when it is longer than `max_subject`, when the message contains Hangul (U+1100-U+11FF, U+3131-U+318E, U+AC00-U+D7A3) and `allow_hangul` is false, and on any line matching `(?i)^co-authored-by:` (not configurable).
- On rejection print to stderr `commit-msg: <reason>`, then `expected: type(scope): English imperative summary (<= 72 chars, no Co-Authored-By)` (showing the project's pattern and length when configured), then `example: fix(editorial): keep median labels inside the chart`, and exit 1.
- On pass, when `<common>/hooks/commit-msg` exists, is executable and is not the same file as this hook (`<common>` from `git rev-parse --path-format=absolute --git-common-dir`), exec it with the same arguments; otherwise exit 0.

§2 `pre-commit`
- Read added lines from `git -c core.quotePath=false diff --cached -U0 --no-color --no-ext-diff --no-textconv --src-prefix=a/ --dst-prefix=b/`, keeping the inherited `GIT_INDEX_FILE`. Take file names from `+++ b/` lines and line numbers from `@@` hunk headers; skip binary entries.
- Check each added line against `SECRET_PATTERNS`, imported from `lib/` found through the hook's real path (`<hook>/../../lib`).
- Skip a line that matches a regex in `secrets.allow` of `HEAD:.harness.json` (same source rule and JSON handling as §1).
- For each hit print `pre-commit: possible <kind> in <file>:<line>`, never the value, and exit 1. On pass, chain to `<common>/hooks/pre-commit` exactly as §1 does.

§3 `_chain`, exact content:
```sh
#!/bin/sh
# bell-harness: run the repository's own hook with the same name, if it has one.
name=$(basename "$0")
dir=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || exit 0
hook="$dir/hooks/$name"
[ -x "$hook" ] || exit 0
[ "$hook" -ef "$0" ] && exit 0
exec "$hook" "$@"
```
Copies of `_chain`: applypatch-msg, pre-applypatch, post-applypatch, pre-merge-commit, prepare-commit-msg, post-commit, pre-rebase, post-checkout, post-merge, pre-push, pre-receive, update, proc-receive, post-receive, post-update, reference-transaction, push-to-checkout, pre-auto-gc, post-rewrite, sendemail-validate, fsmonitor-watchman, p4-changelist, p4-prepare-changelist, p4-post-changelist, p4-pre-submit, post-index-change.

§4 `config/claude-settings.json`, exact keys and values (2-space indentation):
`{"attribution": {"commit": "", "pr": "", "sessionUrl": false}, "permissions": {"deny": ["Bash(git commit --no-verify:*)", "Bash(git commit -n:*)", "Bash(git push --no-verify:*)", "Bash(git * --no-verify*)", "Bash(git -c core.hooksPath*)", "Bash(git config*core.hooksPath*)"]}}`

§5 `config/bell-harness.rules`, exactly three lines:
```
prefix_rule(pattern=["git", "commit", "--no-verify"], decision="forbidden")
prefix_rule(pattern=["git", "commit", "-n"], decision="forbidden")
prefix_rule(pattern=["git", "push", "--no-verify"], decision="forbidden")
```

§6 `config/retire.json`, exact content (2-space indentation): `{"paths": [".claude/skills/interview", ".claude/skills/morning-brief", ".claude/commands/pre-push-check.md", ".codex/skills/chronicle", ".codex/skills/codex-goal-planner", ".codex/skills/frontend-polish-review", ".codex/skills/gpt-tasteskill", ".codex/skills/imagegen-frontend-mobile", ".codex/skills/redesign-skill", ".codex/skills/soft-skill", ".codex/skills/taste-skill"], "claude_plugins": ["taste-skill@taste-skill"]}`. Paths are relative to the home directory. `.claude/skills/spec` is absent on purpose: the harness `spec` skill takes that name, and step 3 backs up whatever occupies it.

§7 `tests/harness_env.py`
- `make_env(tmp)` returns a dict for subprocesses with `HOME`, `XDG_CONFIG_HOME`, `CODEX_HOME` (`<home>/.codex`) and `CLAUDE_CONFIG_DIR` (`<home>/.claude`) inside `tmp`; `PATH=<tmp>/bin:/usr/bin:/bin`; `GIT_CONFIG_GLOBAL=<tmp>/gitconfig` (created empty); `GIT_CONFIG_NOSYSTEM=1`; author and committer `Test <test@example.com>`; `PYTHONIOENCODING=utf-8`; and `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` removed.
- `write_stub(tmp, name, body)` writes an executable script to `<tmp>/bin`. `init_repo(path, env)` runs `git init -b main` and sets `core.hooksPath` to this repository's `git/hooks` in the temporary `GIT_CONFIG_GLOBAL` only.
- With `/usr/bin` ahead of other interpreters, the hooks run under the system Python, which is the Python 3.9 compatibility test.

## Failure modes
| Situation | How it shows | Handling |
|---|---|---|
| A repo-local hook links back to the harness shim | Endless loop | The `-ef` check in `_chain` and the same-file check in §1 and §2; covered by Acceptance 1 |
| A fixture looks like a secret or a home path | The privacy scan flags the repository | Build fake values at runtime |
| A test touches the real global git config | The guard in `scripts/check` fails | Use `harness_env.make_env` for every subprocess |
| Something cannot be done as written | Deviation | Stop and report the exact command and error |

## Acceptance tests
1. `tests/test_hooks.py`, in temporary repositories built with `harness_env`:
   - accepted: `feat(visuals): cap demand posts at three images`, `docs: add the lesson`, `Merge branch 'x'`, `Revert "feat: x"`, `fixup! feat: x`;
   - rejected with stderr starting `commit-msg:`: `R90a: reader KPIs`, `Add deposits to the paper portfolio`, a 73-character subject, `fix: 버튼 수정`, a body line `Co-Authored-By: A <a@example.com>`, an empty message;
   - after a commit that adds `{"commit": {"allow_hangul": true}}` as `.harness.json`, `fix(ui): 버튼 정렬 수정` is accepted; the same file staged in the same commit as that message does not loosen the rule; an invalid `.harness.json` in HEAD is rejected with `invalid .harness.json`;
   - a message whose valid subject sits above a scissors line followed by Hangul diff text is accepted;
   - pre-commit rejects a staged line `OPENAI_API_KEY="sk-proj-…"` (40-character value built at runtime) with `possible openai-key` and `<file>:<line>` in the output and without the value; it accepts the same line after a commit whose `.harness.json` has a matching `secrets.allow` regex;
   - a repo-local `.git/hooks/commit-msg` that writes a marker runs only when the harness check passes; `.git/hooks/prepare-commit-msg` and `.git/hooks/post-commit` markers run through the shims; a `.git/hooks/post-commit` symlinked to the harness `_chain` finishes within 10 seconds;
   - in a linked worktree (`git worktree add`), a bad subject is rejected and the common-dir `post-commit` marker hook runs;
   - every hook name in §3 plus `commit-msg` and `pre-commit` exists in `git/hooks/` as an executable regular file, and each copy equals `_chain` byte for byte.
2. `tests/test_config.py`: the three config files equal §4-§6 after JSON parsing (the rules file line by line); every `retire.json` path is relative, starts with `.claude/` or `.codex/` and has no `..` part; when an executable `codex` is on the test process's PATH, `codex execpolicy check --rules config/bell-harness.rules git commit --no-verify -m x` reports `forbidden` (skipped otherwise).
3. `tests/test_instructions.py`: line counts at most 100 for `global/AGENTS.md` and 60 for `global/CLAUDE.md`, `templates/AGENTS.md` and `AGENTS.md`; none of those four contains `\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT)\b` or (case-insensitively) `if in doubt`; the first line of `global/CLAUDE.md` is `@AGENTS.md`; `templates/AGENTS.md` has the headings `## Non-goals`, `## Decision priorities`, `## Sources of truth`, `## Commands`, `## Skills`, `## Permission boundaries`, `## Commit rules` and `## Evals`.
4. `scripts/check` exits 0 and prints `GUARD: real home unchanged`; `python3 lib/privacy.py` prints `PRIVACY: clean`.
5. Exactly one new commit on top of step 1 with subject `feat(hooks): add commit rules, secret scan and global instructions`, an empty body and a `@users.noreply.github.com` author; `git/hooks/commit-msg` accepts that message; it adds exactly the files in Changes by file; `git status --porcelain` prints nothing.

## Done criteria
Acceptance 1-5 hold AND nothing outside this directory changed.

## Appendix A: global/AGENTS.md
```markdown
# Working agreement for Claude Code and Codex

Installed by bell-harness. A project's own AGENTS.md adds project rules and takes precedence where the two differ.

## Communication

- Reply to the user in Korean. Write code, comments, commit messages and repository files in English unless the project says otherwise.
- Lead with the outcome. Write for a reader who did not watch the work: short sentences, no shorthand invented during the task.
- Close a task with what changed, how it was verified (the real command output), and what was skipped or remains uncertain.

## Work from the requested outcome

- Start from the outcome, the project context and the authorized scope. Read the relevant project material before asking; the project's AGENTS.md names its purpose, sources of truth, check command, skills and permission boundaries.
- For a clear, reversible task, proceed directly. When something is unclear but reversible, choose the reasonable option, state the assumption, and continue. Keep working until the task is finished or no work can advance without the user's answer.
- Work that spans sessions or changes shared behavior gets a spec in `docs/plans/<slug>.md` with the outcome, scope and non-goals, acceptance tests, and a done condition a command can check. When the request names a spec, that spec defines scope and completion.
- Build what the task asks for. Reuse what the repository already has, then the standard library or platform, then an installed dependency; add a dependency only when the spec lists it. Mention further improvements instead of making them.
- Mark a deliberate shortcut with a comment `shortcut: <limit>, <when to upgrade>`, so reviews can find it.
- Finish every place a change reaches: callers, tests, fixtures, configuration and documentation.
- Typical cycle: `probe` while the intent is unclear, `spec` to fix it in writing, implementation, `scripts/check`, then `preflight` before pushing.
- Throwaway work (a scratch worktree, a repository named `*-scratch`, or the user saying "vibe this") skips the spec and `preflight`. Anything meant to ship follows the full cycle.

## When to stop and ask

Ask only in these situations, offering two or three options with their trade-offs and your recommendation:

- A fact contradicts the spec, a recorded decision or the project's AGENTS.md.
- A decision would be hard to reverse: migrations or schema changes on shared data, public interfaces, external services or costs, the core direction of the work.
- A milestone is complete and the next one would start.

Name the exact action and wait for approval before deleting or overwriting files outside the requested change, force-pushing or deleting branches, deploying, publishing content or sending messages on the user's behalf (blog or social posts, emails, chat messages, orders), spending money, and changing global configuration. Everything else in the task's scope needs no approval: reading, editing files in the repository, running tests and checks, local branches, commits, and pushing a verified commit unless the project restricts pushing.

## Verify the result

- When the repository has `scripts/check`, it is the single entry point for format, lint, type checks and tests. Run it rather than approximating it.
- Report completion with the real output of the spec's done condition or `scripts/check`. When a check could not run, say so and why.
- Fix the implementation, not the check. Change a test only when the test itself is wrong, and say so.
- Updating the documents a change affects (the spec, README, the project's AGENTS.md, decision records) is part of done.
- A visual claim needs evidence: inspect the rendered result and save screenshots or exports under `docs/plans/evidence/<slug>/`. Use browser automation for repeatable web checks and computer use for native apps or a final visual review in a local session.
- Work still running in the background, including delegated tasks, means the task is not done. Collect the results, stop what you started and remove temporary files.
- After three failed fixes of the same problem, treat it as a design question: report what you tried and your best hypothesis instead of a fourth patch.
- Before pushing a diff larger than a single obvious fix, run `preflight`. Merge decisions happen on a laptop-sized screen; from a phone or a remote session, start, steer and check status only.

## Learning

When the user corrects a mistake, add one imperative prevention rule to `tasks/lessons.md` in the repository (create it if needed), and read that file at the start of work when it exists.

## Commits

- Subject: `type(scope): imperative summary`, at most 72 characters. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. The scope is optional. English unless the project's `.harness.json` allows Hangul.
- Leave out `Co-Authored-By` and other attribution trailers.
- The global git hooks reject a malformed message and staged secrets. Fix the message or remove the secret and commit again. Commit through the hooks: `--no-verify`, `-n` or an overridden `core.hooksPath` removes the only mechanical check.

## Models

Each tool uses its own current default model; this file pins none, so new models apply without edits. Choose reasoning effort per task through the tool's own settings or flags.
```

## Appendix B: global/CLAUDE.md
```markdown
@AGENTS.md

# Claude Code additions

The imported file is the agreement shared with Codex. These rules apply to Claude Code only.

## Plan, then delegate

- For work with three or more steps, agree on the plan in plan mode before editing. When the work goes sideways, stop and re-plan.
- Claude Code designs and reviews; Codex implements. Delegate an approved spec to the `codex:codex-rescue` subagent with `--fresh --wait`, passing the user goal, the spec path, the authorized scope and the completion check, and end the request with "Do not call create_goal." Use `--resume --wait` only to continue the latest Codex task of this session.
- Leave the model unset so Codex uses its current default. Add `--effort` only when the task clearly needs more or less reasoning than the default, and announce the routing in one line.
- Do work that takes less than about five minutes directly instead of delegating it.
- When a delegated change returns, check the diff against the spec's scope and rerun the completion check yourself before reporting.

## Phase boundary

- Once the plan or spec is approved, start the handoff without asking again.
- Ask one short question and wait when the user asked to review first, when the spec includes deletions, migrations, CI/CD or infrastructure, or anything public-facing, or when the spec still has an open decision (resolve it first). After the user says to wait, wait.
- Keep the implementation of an approved spec with Codex, so that design review and implementation stay separate.

## Commit trailers

Commit messages carry no `Co-Authored-By` or other attribution trailer, even when a session reminder suggests one: the git hook rejects them, and the user asked for none.
```

## Appendix C: templates/AGENTS.md
```markdown
# <Project name>

<One paragraph: what this project is, who uses it, and the outcome it exists to produce.>

## Non-goals

- <What this project deliberately does not do.>

## Decision priorities

<When goals conflict, which wins, in order. Example: correct numbers > clear explanation > speed > visual polish.>

## Sources of truth

- <Documents, data or designs to read before changing a given area, each with when it applies.>

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
```
