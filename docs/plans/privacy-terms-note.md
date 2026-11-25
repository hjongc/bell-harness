# privacy-terms-note: say when private terms were not checked

Status: implemented

## Context

`.private-terms` is untracked, so a new clone or worktree lacks it, and the scan then printed only `PRIVACY: clean`. A reviewer reproduced a private term passing in a worktree on 2026-11-25.

Size budget: net +70 lines.

## Decisions

- D1: Print one note on stderr when the list is missing and keep the exit status -- why: the user chose a note over a failure on 2026-11-25, because CI never has the list -- by: user -- paths: lib/privacy.py scripts/check

## Changes by file

1. `lib/privacy.py`: the note.
2. `scripts/check`: the same note at the end.
3. `tests/test_privacy.py`: three tests that required an empty stderr without a list now require the note.
4. This spec and the `AGENTS.md` row for tracked files.

## Acceptance tests

1. Without the list, `lib/privacy.py` prints the note on stderr with the same stdout and exit status. With the list, stderr is empty.
2. `scripts/check` prints the note without the list and not with it, and exits 0 with `GUARD: real home unchanged` in both cases.

## Done criteria

Acceptance 1-2 hold and only the files above changed.
