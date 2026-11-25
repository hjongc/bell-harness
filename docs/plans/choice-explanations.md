# choice-explanations: explain what each option leads to

Status: implemented

## Context

Choices that named an item only by its ID left the user asking what it was. The user asked on 2026-11-25 for an explanation with the options, and approved a shared rule for both tools.

Size budget: net +45 lines.

## Decisions

- D1: A question says in plain words what it is about and what each option leads to -- why: the user could not choose from an ID alone -- by: user -- paths: global/AGENTS.md

## Changes by file

1. `global/AGENTS.md`: one sentence in the question rule.
2. `tests/test_instructions.py`: the rule stays.
3. This spec and the `AGENTS.md` row for instruction files.

## Acceptance tests

1. The shared question rule holds the sentence and the file stays within its line limit.
2. `scripts/check` exits 0 with `GUARD: real home unchanged`.

Whether live hosts follow the rule was not measured.

## Done criteria

Acceptance 1-2 hold and only the files above changed.
