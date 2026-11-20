# Design doc template

Write to `docs/plans/<slug>-design.md`. The doc is a decision record, not a transcript: one line per decision with its reason; an approach ruled out during the session gets one line with the reason; leave out sections that would be empty. When an earlier design doc for the same topic exists, add `Supersedes: <file>` under the status line and keep the old file.

```markdown
# Design: <title>

Status: DRAFT | APPROVED
Mode: Product | Feature | Explore
Date: <YYYY-MM-DD>

## Problem
<What is wrong or missing, for whom, in the user's words where possible.>

## Evidence
<Product: demand evidence and the status quo (Q1, Q2), with quotes and numbers.
Feature: the success condition (F1). Explore: what makes this cool.>

## Target user and smallest useful version
<Product: the named person and the narrowest wedge (Q3, Q4). Feature: who uses the change. Explore: the first thing to build and show.>

## Constraints
<Non-negotiables with their reasons (F2), and what this deliberately does not do (F3).>

## Premises
1. <agreed statement>

## Approaches considered
### A: <name> (minimal)
<summary, effort, risk, pros, cons, reuses>
### B: <name> (ideal)
<...>
### C: <name> (lateral, optional)
<...>

## Recommended approach
<The approach the user chose and why.>

## Decisions
- D1: <decision> -- why: <reason> -- by: user|observed

## Edge cases and failure modes
<Which must work in this version and how each is handled.>

## Success criteria
<Observable, checkable conditions; these become the spec's acceptance tests.>

## Open questions
<Each with the default you would take if forced.>

## The Assignment
<One concrete action for the user to take next, outside the code.>

## What I noticed
<Two to four observations about how the user reasons, quoting their own words back rather than characterizing them.>
```
