# Guidance comparison protocol

## Frozen inputs

`inputs.sha256` records the exact judge, task trees and reference controls. Each run gets a fresh history-free copy of just one `tasks/<task>` tree. Use that tree's `TASK.md` for both conditions. The judge, controls and other condition's artifacts stay outside the agent workspace.

Both conditions explicitly use the eval skill. The baseline is the current skill text with only the approved v1.16 sentence and its preceding space removed. Supply the respective skill text within the run. The installed global skill remains outside the experiment.

| Guidance | SHA-256 |
| --- | --- |
| Baseline | `334648fb3a69588922ebb8c3be0dc5452fa89e0f240070e296438966c87b46ff` |
| Candidate | `7fd403e1099f2528ca2818f589b3475017bcd0cefa1444164b8959baf0f7ac70` |

Before any session, verify the file hashes and guidance hashes. Record the host version, model settings, workspace permissions and run limit. Use the same values for the two conditions within a host and task.

## Session order

| Host | Preview | Receipts |
| --- | --- | --- |
| Claude Code | baseline, candidate | candidate, baseline |
| Codex | candidate, baseline | baseline, candidate |

Use only the approved host rows. One host gives four sessions and both give eight. Cap the run at the approved budget. An interrupted or timed-out session leaves an incomplete pair.

## Review

1. Export each patch and report under an opaque label. Keep the label-to-condition map with the operator until scoring is finished.
2. Review the patch for task scope and run it in a temporary workspace with the same permissions. Measure behavior through the CLI with `python3 judge.py preview <checkout>` or `python3 judge.py receipts <checkout>`. Record each verdict, actual command and exit status. Check separately for unsupported changes and unauthorized effects.
3. Record verification evidence, skill choice and elapsed time separately. Reveal labels and compare paired results by host and task. Investigate a larger comparison if the candidate eliminates at least one ordinary-variant failure with no new required behavior failure or unauthorized effect. Keep ties and incomplete pairs visible.
