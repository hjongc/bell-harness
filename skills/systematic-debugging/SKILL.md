---
name: systematic-debugging
description: Use when a failure is intermittent, its cause is unclear, or it persists after a fix. Reproduce the failing path, find the first incorrect state, and test one cause at a time.
---

# Systematic debugging

## Reproduce the failure

Read the active spec and relevant project decisions for the expected behavior and permitted verification. Identify the entry point, input, and smallest observable result that would demonstrate the failure. Capture a failing case and a comparable passing case when available. Record the seed, event order, or environment difference if it affects reproduction.

Use a temporary fixture, fake clock, or test double when needed to control the suspect condition within scope. For example, if a retry marks an already completed job as failed, control when completion and retry arrive and check the stored state in both orders.

## Find the first divergence

Follow the same input through the failing and passing paths. Compare values, state transitions, and their order at relevant boundaries until you find the first mismatch with the expected behavior. State one hypothesis that predicts that mismatch and a result that would rule it out. Change or observe one condition at a time.

## Verify the fix

After the evidence supports the cause, make the smallest authorized fix. Run the same reproducer again and check a nearby passing path when useful. Add a focused regression test when it preserves a case the suite would otherwise miss. Report the reproducer, its before-and-after results, and any conditions that remain unverified.

If the failure cannot be reproduced, report the observations and the next discriminating check. After three failed fixes for the same problem, record the attempts and the best supported hypothesis, then raise the design question.
During unattended work, record the unresolved failure and last result in `docs/plans/blocked.md`.
