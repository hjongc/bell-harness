# Backlog

Findings from audit passes over the harness. Each entry has evidence and a size. Nothing here is approved work; an item becomes work when it gets a spec.

## Priorities

Suggested order, by what a user would hit first:
1. B6 (plan mode against unattended work) and B2 (`init` name clash): both can make an everyday request do the wrong thing.
2. B1 (moving the repository blocks setup and doctor): rare, but there is no documented way out.
3. B3, B4, B5 (eval runner): they make results less trustworthy, not wrong in use.
4. B7 (preflight rule not followed) and B8 (short bypass flag): decisions for the user about how strict to be.
5. B10, B11, B9: small.

## Open

None. B1-B11 were decided in v1.5-audit-fixes.

## Fixed during the audit
- `bin/setup --restore` crashed with a traceback when `~/.claude/settings.json` had become invalid JSON; it now skips the settings with a message and undoes the rest (`tests/test_setup.py::test_restore_survives_invalid_settings`).
- `bin/doctor --project <missing dir>` exited 0 with a misleading "AGENTS.md not found" warning; it now fails with "is not a directory" (`tests/test_doctor.py::test_missing_project_directory_fails`).
- Skills named harness tools (`bin/doctor`, `templates/AGENTS.md`) without saying where they are; in another repository an agent could not find them. `init` and `preflight` now say the harness root is two folders above the skill's real path. The `spec` skill sent unattended failures to "Blocked" while `away` uses `docs/plans/blocked.md`; both now name the file (v1-skills#D8).
- `v1-skills#D1` still said the harness has six skills while eight ship, and nothing superseded it; `AGENTS.md` cited it. Added `v1.3-away#D7` superseding it and updated the table. The citation check from v1.4 confirms the fix: with the old table it reports `v1-skills#D1 superseded; cite v1.3-away#D7`.
- A project whose AGENTS.md was copied from the template and left unfilled passed `bin/doctor --project` with only an odd `unknown commit <short commit>` warning. Doctor now warns that template placeholders remain (`tests/test_doctor.py::test_unfilled_template_is_reported`).
- `bin/setup` printed every planned action as if done before applying any, so after a mid-run failure the output did not show how far it got. It now prints each action after it succeeds and reports `stopped after N of M actions` (`tests/test_setup.py::test_failed_action_stops_and_can_be_undone`, which also covers the failure-then-restore path that had no test).
- `lib/decisions.py` read only the first line of a decision record, so records hard-wrapped at 80 columns in a real project were reported as `missing field 'by'` (six false warnings from `bin/doctor --project`). Indented continuation lines are now part of the record (`tests/test_decisions.py::test_accepts_a_record_wrapped_onto_indented_lines`, v1.4-memory-recall#D2).
- The wrapped-record fix above absorbed a nested list under a record and then reported a bad `by` value. Continuation now stops at a nested list item (`tests/test_decisions.py::test_nested_list_under_a_record_is_not_part_of_it`). Found in pass 13 by probing the pass 11 change.

## Covered areas
- Pass 1: README against real behavior (install, check and undo, eval case count). Case count and commands match.
- Pass 2: eval runner (`evals/run.py`) and the `init` name. Four findings, none fixed (each changes grading behavior and needs a decision).
- Pass 3: `bin/setup` and `bin/doctor` edge cases in a temporary home (missing or non-git project, unknown backup id, memory notes in CLAUDE.md, invalid settings). Two bugs fixed; the other cases behaved correctly.
- Pass 4: skill bodies (cross-references, tool paths, script syntax). Two wording bugs fixed; `ui-check.mjs` parses but has still never been run against a page.
- Pass 5: global rules read against each other and against what happened in practice. Two findings recorded, none fixed (both change global rules).
- Pass 6: installed git hooks in a temporary repository (scoped and breaking subjects, Hangul in subject and body, non-conventional subjects, revert, merge, cherry-pick, a chained repo-local hook, a staged secret, a 3 MB binary in 0.17 s). All behaved as specified; no finding. Note for the user: Hangul in the commit body is rejected as well as in the subject unless `.harness.json` allows it.
- Pass 7: plan documents against the code (decisions still in force, roadmap, statements of counts). One outdated decision fixed. Older spec appendices no longer match the current skill files; they are kept as the record of what was approved at the time.
- Pass 8: privacy scan with sample lines and the Claude deny patterns. Two small findings recorded.
- Pass 9: the project template through `bin/doctor`, and what `scripts/check` covers (privacy and decision checks run inside the test suite). One bug fixed.
- Pass 10: untested branches of `bin/setup` (a failing plugin uninstall, then restore). Restore worked; the output problem above was fixed.
- Pass 11: the updated doctor against this machine and against the first real project (read-only). One false-positive bug fixed.
- Pass 12: `bin/doctor --project` read-only across every local repository. No crash and no false positive after the pass 11 fix; one finding recorded.
- Pass 13: regression probes of the fixes made during this audit. One regression found and fixed.
- Pass 14: regression probes of the other audit fixes (setup output order and the "replaces" note, the placeholder warning on filled files, pattern paths, a file passed as a project). No finding.
- Pass 15: the real-home guard in `scripts/check`. One small finding recorded. Every listed area has now been covered; the audit ends here.
