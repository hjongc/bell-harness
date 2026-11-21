# Backlog

Findings from audit passes over the harness. Each entry has evidence and a size. Nothing here is approved work; an item becomes work when it gets a spec.

## Open

### B1: Moving the harness repository blocks both setup and doctor (medium)
- Area: README "Install", `bin/setup` preflight.
- Evidence: in a temporary home, run `bin/setup`, rename the harness directory, run `bin/setup --dry-run` from the new location. Output: `setup: global core.hooksPath is <old>/git/hooks, not <new>/git/hooks`, exit 2. `bin/doctor` then reports every link as FAIL and says to run `bin/setup`, which refuses. Links into the old location also stop counting as managed, so they would be backed up as foreign entries.
- Why it matters: the only way out is to unset `core.hooksPath` by hand, which no document mentions. A user who reorganizes folders or clones to a different path on a second machine after copying their home hits this.
- Direction: treat a `core.hooksPath` or link whose recorded value appears in an earlier backup manifest as the harness's own and replace it; or document `git config --global --unset core.hooksPath` in the README until then.

## Covered areas
- Pass 1: README against real behavior (install, check and undo, eval case count). Case count and commands match.
