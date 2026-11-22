# business-document-design: shared design workflow for professional documents

Status: implemented

## Context

The user asked for a dedicated design skill for business documents such as portfolios. The skill should guide the editorial structure, page layout, evidence, and rendered review of documents intended to be read or shared.

## Decisions

- D1: Ship a shared skill for portfolio and business document design -- why: the user requested a dedicated skill for this work -- by: user -- paths: skills/business-document-design/SKILL.md tests/test_skills.py
- D2: Use the existing installer and format-specific tools for production and export -- why: the new skill guides editorial and layout choices and the existing tools already cover format-specific rendering -- by: observed -- paths: skills/business-document-design/SKILL.md lib/harness.py

## Changes by file

- `skills/business-document-design/SKILL.md` defines routing, document structures, composition, evidence, and exported-file review.
- `tests/test_skills.py` adds the name to the expected shared skill set.
- `README.md` and `SOURCES.md` list the skill and primary references.
- This spec records the acceptance results.

No runtime dependencies or global installation. The linked sources inform the original instructions.

## Acceptance

Review the candidate instructions against these fixed tasks. Check coverage of every listed action. Describe the result as instruction coverage.

| Scenario | Required observable guidance |
|---|---|
| Korean PDF portfolio with a team case study, no measured outcome, and a private screenshot | Use the applicant's role and a decision as the story. Distinguish individual work from team results, use supported evidence in place of a made-up metric, and prepare a disclosure-safe visual. Check Hangul and the exported pages. |
| Client proposal with price assumptions and a long scope table spanning pages | Put the requested decision up front. Distinguish inclusions, exclusions and unconfirmed terms. Repeat the table header and check alignment, units, and page breaks in the export. |
| Leadership report with a chart and a supporting appendix | Lead with the finding and desired decision. Give the chart its period, units, and source. Move supporting detail to the appendix and check that readers can find the same claim in text. |
| Editable business deck with images and a PDF handout | Use the actual format for production. Review the exported handout and check fit, text legibility, figures and links before delivery. |

## Done condition

`scripts/check` exits 0 with `GUARD: real home unchanged`, all four instruction scenarios are covered, and the existing installer recognizes the new skill in a temporary home.

## Offline comparison

The existing UI skills provide generic PDF render checks but lack the document-specific structure and evidence decisions in these cases. None of the four scenarios was fully covered before the new skill.

| Scenario | Candidate evidence |
|---|---|
| Korean PDF portfolio | The portfolio row separates the individual role and supporting evidence from team results. The publication and composition checks cover private artifacts, Hangul, and the exact export. |
| Client proposal | The proposal row distinguishes scope and assumptions. Page composition and export checks cover repeated headers, numeric alignment, units, and broken rows. |
| Leadership report | The report row places the finding and requested decision first and sends supporting material to an appendix. The chart rules require period, units, source, and a takeaway in text. |
| Editable deck and handout | The export workflow uses deck masters and inspects the separate PDF for fit, legibility, figures, and links. |

Instruction coverage was 4/4. A temporary setup fixture also confirmed that the installed skill in both `.agents/skills` and `.claude/skills` points at the copied source. No model run or example document was evaluated.

`scripts/check` exited 0 with `Ran 108 tests in 54.505s (4 workers)`, `OK`, and `GUARD: real home unchanged`.
