# bell-harness

![check](https://github.com/hjongc/bell-harness/actions/workflows/check.yml/badge.svg)

One working setup for [Claude Code](https://claude.com/claude-code) and [Codex](https://developers.openai.com/codex), shared across machines: global instructions both tools read, eleven skills, git hooks that enforce commit rules and block staged secrets, and scripts that install, check and undo all of it.

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

Entries named `paseo*`, `synced` or `.system` are never touched, and setup refuses to run when `~/.claude/skills`, `~/.agents/skills` or `~/.codex/rules` is itself a symlink. Setup and restore require a real backup directory path. A retirement path with a symlinked parent is reported and skipped. A retirement entry that is itself a symlink can still be moved. Running `bin/setup` again reports `setup: nothing to do`.

## Check and undo

```sh
bin/doctor                      # PASS/WARN/FAIL per check; exit 1 on any FAIL
bin/doctor --project ~/code/app # also check project instructions, table paths, decisions and commit messages
bin/doctor --project-only ~/code/app # check only project files and Git history
bin/doctor --project-only ~/code/app --instruction-status # also show uncommitted instructions
bin/doctor --discovery          # ask claude and codex which skills they actually load
bin/setup --list-backups         # list IDs, active/restored state and manifest health
bin/setup --restore <id>        # undo one backup (or: all), skipping anything changed since setup
```

If you move the harness repository, run `bin/setup` from its new location to repair the links and hooks path.

The backup list is read-only and sorted newest first. A valid record describes the manifest's structure. Restore also checks the current state before undoing actions. Listing, restore, and earlier-root discovery reject links at the backup directory, backup ID, or manifest.

Restore checks each backup manifest before undoing its actions. If a retired item's saved or destination path has a symlinked parent, restore keeps that backup available for retry after the path is fixed. It undoes settings key by key, so settings changed after setup survive. Uninstalled plugins are not reinstalled automatically; restore prints the `claude plugin install` command.

Codex rules match command prefixes. Both project diagnostic modes validate recorded commit messages with the harness policy and never run Git hooks. Use `--project-only` in a checkout without a harness installation. It cannot be combined with `--discovery`.

Add `--instruction-status` to a project-only check at the checkout root to see changes to root and nested `AGENTS.md` and `CLAUDE.md` files. Untracked files have their own warning. For tracked files, `index` compares staging with the current commit, and `worktree` compares files on disk with staging. A dot marks an unchanged column. Git-ignored untracked files are omitted, and the query leaves the index and files intact.

## Skills

| Skill | Use it to |
|---|---|
| `map` | Fill or refresh a project's AGENTS.md and record the decisions behind its constraints |
| `probe` | Pressure-test an idea or feature with one hard question at a time and record the design |
| `spec` | Turn an agreed design into a spec another agent can execute without judgment calls |
| `preflight` | Review a diff before the first push of a spec's work and when a delegated change comes back |
| `eval` | Compare a prompt, skill or model change on fixed cases |
| `offline-verification` | Exercise a built, installed or normal entry point with offline inputs and record the evidence |
| `systematic-debugging` | Reproduce and isolate an intermittent, unclear or recurring failure |
| `ui-design` | Design around the user’s task, real content, and project references, with optional local catalog search |
| `ui-polish` | Test rendered screens with realistic data and repeated interactions, and review PDFs against a baseline |
| `away` | See what can run unattended and keep approved work moving while you are away |

Origins and licenses are in [SOURCES.md](SOURCES.md).

## Project memory

Decisions live in the spec that made them, one line each:

```
- D3: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D1]
```

A project's AGENTS.md has a Sources of truth table (task, where to look, constraints and the decision ids behind them), and the global instructions tell both tools to grep `docs/plans` before changing behavior. `python3 lib/decisions.py` and `bin/doctor --project` report malformed records, decisions that cite deleted paths, and table rows that cite missing or superseded decisions. A row may keep a historical citation alongside its active replacement. There is no automatic recall hook; see `docs/plans/v1-memory.md` for why.

For a cross-session handoff, keep the last verified command and its result, outstanding work and the relevant decision ids in the active spec. On resume, check the current checkout before relying on the earlier result. Keep personal preferences in private local instructions.

`docs/plans/roadmap.md` lists specs in work order. The next unchecked item can start when its spec says `Status: approved`. Actions listed in the global approval rules still need approval.

## Working while you are away

Ask what is queued before you leave, then set a goal for the range you want the agent to work through. While you are away, the agent records questions and actions that need approval in `docs/plans/blocked.md` and continues with approved items that can proceed independently.

## Start a project

Copy `templates/AGENTS.md` into the project and fill it in, or ask an agent to run the `map` skill. A project can allow a Korean commit summary with a `.harness.json` file (`{"commit": {"allow_hangul": true}}`); the hook reads it from the last commit, so a commit cannot relax its own rules.

## Evals

```sh
python3 evals/run.py [--host claude|codex|all] [--case <id>]... [--jobs N] [--timeout S] [--repeat N] [--json <file>]
```

Each of the 25 cases sends a fixed prompt to the real `claude` and `codex` commands in a temporary copy of a fixture repository (`evals/fixtures/`), then grades skill use, final answers or observed mock actions. Fourteen routing cases use English and Korean prompts. They cover design, spec, eval, project initialization, preflight, offline verification, systematic debugging and small edits that should load no skill. Six memory cases check that a recorded decision is applied, an unrelated task stays quiet about it, a superseded decision loses to the newer one, a missing reason is reported as missing, a Korean question retrieves the English decision and its rationale, and a single observation stays optional. Three flow cases check roadmap order and count actual mock publish attempts with and without explicit approval. Two away cases check skill routing when you ask what is queued or ask the agent to continue a roadmap with an approval gate. The runner calls paid models, so it is not part of `scripts/check`. Run it after installing the harness and whenever a model or an instruction changes.

Each attempt needs a nonempty final answer. Routing cases require observable skill content from a successful Codex command or a successful result matched to Claude's Skill call. Incomplete evidence fails a routing case with an explicit unverified reason. Answer-only cases still grade the final answer. Fixture Git commands and host processes run without inherited repository-local Git variables.

Use `--repeat N` to run each host and case N times. A host-case pair passes when every attempt passes, and `--json` records every attempt. A case can set `max_turns` to override Claude's default of eight turns.

## Develop

```sh
scripts/check   # offline tests in a temporary home, privacy scan, real-home guard
```

The check runs discovered test suites in up to four independent processes. Use `scripts/check --jobs 1` for serial output. A suite that cannot be sent to a worker makes the check run serially. The home guard covers the entire run in either mode.

The privacy scan checks the link text of Git working tree symlinks and skips paths below them. In `.privacy-allow`, use a path glob and a detection kind on each rule line. Blank lines and lines starting with `#` are comments or separators. The home guard compares the contents of regular backup manifests, including restored backups.

Changes follow a spec in `docs/plans/`. See [AGENTS.md](AGENTS.md).

## License

MIT. See [LICENSE](LICENSE); third-party parts keep their own MIT notices in `licenses/`.
