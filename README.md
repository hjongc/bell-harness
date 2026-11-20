# bell-harness

![check](https://github.com/hjongc/bell-harness/actions/workflows/check.yml/badge.svg)

One working setup for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex), shared across machines: global instructions both tools read, eight skills, git hooks that enforce commit rules and block staged secrets, and scripts that install, check and undo all of it.

Both tools read the same instructions and skills. Project memory lives in git (specs with decision records), so a decision made in one tool is visible to the other.

## Requirements

macOS or Linux with `git` and `python3` (3.9 or newer, standard library only). `claude` and `codex` are optional; whatever is missing is skipped and reported.

## Install

```sh
git clone https://github.com/hjongc/bell-harness.git ~/bell-harness
cd ~/bell-harness
bin/setup --dry-run   # print the plan, change nothing
bin/setup             # apply it, with a backup, then run bin/doctor
```

`bin/setup` changes only these, and records every change in `~/.bell-harness/backups/<id>/manifest.jsonl`:

| Item | Result |
|---|---|
| Skills | `~/.claude/skills/<name>` and `~/.agents/skills/<name>` link to `skills/<name>` |
| Codex instructions | `~/.codex/AGENTS.md` links to `global/AGENTS.md` |
| Claude instructions | `~/.claude/CLAUDE.md` is a local file whose first line imports `global/CLAUDE.md`, so Claude's own memory notes stay on the machine |
| Codex rules | `~/.codex/rules/bell-harness.rules` forbids `--no-verify` |
| Git hooks | `git config --global core.hooksPath` points to `git/hooks` |
| Claude settings | `config/claude-settings.json` is merged key by key into `~/.claude/settings.json`: no attribution trailers, and hook-bypassing git commands are denied. Other keys stay as they are. |
| Retired items | Paths in `config/retire.json` (and `~/.bell-harness/retire.local.json`) move into the backup; listed Claude plugins are uninstalled |

Entries named `paseo*`, `synced` or `.system` are never touched, and setup refuses to run when `~/.claude/skills`, `~/.agents/skills` or `~/.codex/rules` is itself a symlink. Running `bin/setup` again reports `setup: nothing to do`.

## Check and undo

```sh
bin/doctor                      # PASS/WARN/FAIL per check; exit 1 on any FAIL
bin/doctor --project ~/code/app # also check project instructions, table paths, decisions and commit messages
bin/doctor --discovery          # ask claude and codex which skills they actually load
bin/setup --restore <id>        # undo one backup (or: all), skipping anything changed since setup
```

Restore undoes settings key by key, so settings changed after setup survive. Uninstalled plugins are not reinstalled automatically; restore prints the `claude plugin install` command.

Codex rules match command prefixes, and `bin/doctor --project` lists commits made around the hooks that the hooks would reject.

## Skills

| Skill | Use it to |
|---|---|
| `init` | Fill or refresh a project's AGENTS.md and record the decisions behind its constraints |
| `probe` | Pressure-test an idea or feature with one hard question at a time and record the design |
| `spec` | Turn an agreed design into a spec another agent can execute without judgment calls |
| `preflight` | Review a diff against its spec before pushing |
| `eval` | Compare a prompt, skill or model change on fixed cases |
| `ui-design` | Choose style, palette, typography and layout from local design data, including Korean-market conventions |
| `ui-polish` | Inspect the rendered UI (and PDFs) at three widths against a baseline before calling it done |
| `away` | See what can run unattended and keep approved work moving while you are away |

Origins and licenses are in [SOURCES.md](SOURCES.md).

## Project memory

Decisions live in the spec that made them, one line each:

```
- D3: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D1]
```

A project's AGENTS.md has a Sources of truth table (task, where to look, constraints and the decision ids behind them), and the global instructions tell both tools to grep `docs/plans` before changing behavior. `python3 lib/decisions.py` and `bin/doctor --project` report malformed records and decisions that cite deleted paths. There is no automatic recall hook; see `docs/plans/v1-memory.md` for why.

`docs/plans/roadmap.md` lists specs in work order. The next unchecked item can start when its spec says `Status: approved`. Actions listed in the global approval rules still need approval.

## Working while you are away

Ask what is queued before you leave, then set a goal for the range you want the agent to work through. While you are away, the agent records questions and actions that need approval in `docs/plans/blocked.md` and continues with approved items that can proceed independently.

## Start a project

Copy `templates/AGENTS.md` into the project and fill it in, or ask an agent to run the `init` skill. A project can allow a Korean commit summary with a `.harness.json` file (`{"commit": {"allow_hangul": true}}`); the hook reads it from the last commit, so a commit cannot relax its own rules.

## Evals

```sh
python3 evals/run.py [--host claude|codex|all] [--case <id>]... [--jobs N] [--timeout S] [--json <file>]
```

Each of the 18 cases sends a fixed prompt to the real `claude` and `codex` commands in a temporary copy of a fixture repository (`evals/fixtures/`), then grades which harness skill was loaded and regular expressions over the final answer. Ten routing cases use English and Korean prompts. They cover design, spec, eval, project initialization, preflight and small edits that should load no skill. Four memory cases check that a recorded decision is applied, an unrelated task stays quiet about it, a superseded decision loses to the newer one, and a missing reason is reported as missing. Two flow cases check roadmap order and the approval request before publishing. Two away cases check skill routing when you ask what is queued or ask the agent to continue a roadmap with an approval gate. The runner calls paid models, so it is not part of `scripts/check`. Run it after installing the harness and whenever a model or an instruction changes.

## Develop

```sh
scripts/check   # offline tests in a temporary home, privacy scan, real-home guard
```

Changes follow a spec in `docs/plans/`. See [AGENTS.md](AGENTS.md).

## License

MIT. See [LICENSE](LICENSE); third-party parts keep their own MIT notices in `licenses/`.
