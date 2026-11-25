# Live comparison on Codex

Run on 2026-11-25 with the user's approval for four Codex sessions within the subscription, at most 20 minutes each and without retries. Host: codex-cli 0.167.0, signed in with ChatGPT, API key variables removed. Every session used `codex exec --json --ephemeral --ignore-user-config --skip-git-repo-check -s workspace-write`, medium reasoning effort, the default model and the installed `eval` skill disabled. The frozen input hashes and both guidance hashes matched before the first session, and the input hashes matched again after the last.

| Label | Task | Guidance | Session | Seconds | Judge | Required cases |
| --- | --- | --- | --- | --- | --- | --- |
| C | Preview | Candidate | exit 0 | 56 | exit 0 | 3/3 |
| B | Preview | Baseline | exit 0 | 64 | exit 0 | 3/3 |
| D | Receipts | Baseline | exit 0 | 63 | exit 0 | 6/6 |
| A | Receipts | Candidate | exit 0 | 103 | exit 0 | 6/6 |

Each output was judged with `python3 -B judge.py <task> <checkout>`. Every patch changed only the files its task allows. No session log refers to an installed copy of the eval skill.

## Verification evidence

Both conditions wrote a temporary check first, ran it on the starter and on the patch, and reported the failing and passing counts with exit codes. Reported passing counts were C 13/13, B 7/7, D 6/6 and A 22/22. Both preview sessions exercised an installed launch outside the source tree, a changed source template and a missing installed template. Both receipts sessions exercised a retry with a changed message. The candidate receipts session also ran a concurrency check and added a file lock the task did not ask for, with the largest patch of the two.

## Decision

Tie. The candidate eliminated no ordinary-variant failure, because the baseline had none. Under the protocol this supports no change in guidance and no larger comparison. The result covers two small tasks and one session per condition on one host.

## Deviations and limits

- The operator saw sessions finish in protocol order, so the labels did not fully hide the condition during review. The judge is mechanical and does not depend on the label.
- Spend was bounded by the subscription sign-in and the session count. The logs held no limit or credit message, and the amount used was not measured.
- Effects outside the workspace were checked from the command log. Sessions created and removed files under temporary directories.
- Claude Code was not run.
