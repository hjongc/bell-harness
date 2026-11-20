# v1-evals: live evals for skill routing and project memory

Status: implemented (step 4b of the bell-harness v1 plan; runner built by a subagent and reviewed)

## Context
Offline tests prove the files are well-formed; they cannot show that a model loads `probe` when asked to design something, or applies a recorded decision. `evals/run.py` runs fixed prompts through the real `claude` and `codex` commands in throwaway fixture repositories and grades what they did. It is run by hand after the harness is installed and whenever a model or an instruction changes. Success: the offline tests of the runner pass in `scripts/check`; the live run happens in step 5.

## Decisions
- D1: Evals grade observable behavior: which skill was loaded (Claude: a `Skill` tool call; Codex: a command that reads `.../<skill>/SKILL.md`) and regular expressions over the final answer, not the model's account of itself -- why: self-reports are unreliable and a regex grader is reproducible without another model -- by: user -- paths: evals/run.py
- D2: Live evals stay out of `scripts/check` and run only on request -- why: they call paid models, take minutes and depend on the network -- by: user -- paths: evals/run.py scripts/check
- D3: Memory evals cover four behaviors: a recorded decision is applied, an irrelevant task stays quiet about it, a superseded decision loses to the newer one, and a missing reason is reported as missing -- why: these are the recall behaviors the no-hook design must show (v1-memory#D2) -- by: user -- paths: evals/cases

## Scope / Non-goals
- In: `evals/run.py`, `evals/cases/*.json`, `evals/fixtures/<name>/`, `tests/test_evals.py`, README "Evals" section, this spec, evidence.
- Out: an LLM grader, scoring dashboards, running live evals inside `scripts/check`.
- Python 3.9 standard library only.

## Interfaces
§1 Case file `evals/cases/<id>.json`:
```json
{"id": "route-probe", "fixture": "basic", "hosts": ["claude", "codex"],
 "prompt": "...", "expect_skill": "probe",
 "expect_answer": "(?i)regex", "reject_answer": "(?i)regex"}
```
`expect_skill` is a skill name, or `null` meaning no harness skill may load. `expect_answer`/`reject_answer` are optional; a case passes when every given check holds.

§2 Cases (8, each run on both hosts, 16 runs):
- Routing, `basic` fixture, both hosts: `route-small-edit` (fix a typo in README.md; expect_skill null), `route-probe` (think through a new reading-habit tracker; probe), `route-spec` (the design in `docs/plans/notes-design.md` is agreed, write the implementation spec; spec), `route-eval` (compare skill routing before and after a description change; eval).
- Memory, `memory` fixture, both hosts, prompts tell the model not to edit files: `memory-apply` (which Python syntax may a new helper in `git/hooks/check.py` use; expect `3\.9`, reject suggesting `match` statements or `X | Y` unions as allowed), `memory-quiet` (rewrite the README intro sentence, reply with the sentence only; reject `3\.9|system Python|D1`), `memory-superseded` (which format the export report uses; expect `JSON`, reject recommending `CSV`), `memory-unknown` (why `src/log.py` caps log lines at 200 characters; expect wording that no reason is recorded or known).

§3 Fixtures `evals/fixtures/basic/` and `evals/fixtures/memory/`: small repositories (README.md, AGENTS.md from the template shape with a Sources of truth table, CLAUDE.md `@AGENTS.md`, and for `memory`: `docs/plans/hooks.md` with `- D1: Hook scripts run on Python 3.9 ... -- why: desktop apps run hooks with the system Python ... -- by: user -- paths: git/hooks`, `docs/plans/export.md` with D1 CSV superseded by D2 JSON, `git/hooks/check.py`, `src/log.py` with an unexplained 200-character cap). The runner copies a fixture into a temporary directory and commits it with `git init`.

§4 `python3 evals/run.py [--host claude|codex|all] [--case <id>]... [--jobs N] [--timeout S] [--json <file>]`
- Claude: `claude -p <prompt> --output-format stream-json --verbose --max-turns 8 --disallowedTools Edit Write NotebookEdit` with cwd in the fixture copy. Skill loaded = an assistant `tool_use` named `Skill` whose `input.skill` (strip a `plugin:` prefix) is the name. Answer = the `result` event's `result`.
- Codex: `codex exec --json --skip-git-repo-check --ephemeral -s read-only -C <copy> <prompt>`. Skill loaded = any command item whose text contains `/<name>/SKILL.md`. Answer = the last agent message text.
- Only harness skill names (folders in `skills/`) count for routing.
- Prints one `PASS|FAIL <host> <case>: <detail>` line per run (detail names the skills seen and the failed check), then `EVALS: <passed>/<total> passed`; exit 1 when any run fails, 2 on usage errors or a missing host. A timeout is a FAIL.

## Acceptance tests
1. `tests/test_evals.py` with stub `claude` and `codex` (via `harness_env`) emitting fixture event streams: a matching skill call passes; a wrong or extra harness skill fails; `expect_skill: null` fails when any harness skill loads; `expect_answer`/`reject_answer` are applied to the final answer; a non-harness skill (`paseo`) is ignored; `--case` filters; exit codes 0/1; every case file parses and names an existing fixture and harness skill.
2. `scripts/check` exits 0 with `GUARD: real home unchanged`; `PRIVACY: clean`; `DECISIONS: clean`.

## Done criteria
Acceptance 1-2 hold and one commit `feat(evals): add live routing and memory evals` records the step.
