---
name: eval
description: Evaluate a prompt, skill, model, tool-selection or automation change against fixed cases before claiming it is better, and report baseline versus candidate with the real commands and results. Use when the user asks to evaluate or compare, says "eval", "평가", "벤치마크", after changing instructions or skills, when a new model arrives, or for an agent behavior regression including approval boundaries.
---

# Eval

1. **Fix the setup first.** Start with the project's evaluation command (the Evals line in its AGENTS.md; in bell-harness, `python3 evals/run.py`) or the smallest offline fixture. Write down the inputs, expected outcomes, grader and active permissions before running anything, so the result cannot be fitted afterwards.
2. **Compare like with like.** Run the baseline and the candidate on the same cases when both exist. Run each check as provided, keeping its own output and exit status. Change one thing at a time. When the change affects a boundary, include one allowed action and one failing or forbidden action.
3. **Check effects directly.** Prefer observable outputs and side effects (files, tool calls, exit codes) over the model's own account. For a prediction agent, score accuracy separately from tool choice, arguments, units and how it states its limits. For skill routing, check which skill was loaded, and that none was loaded where none should be. For executable changes with meaningful input variation, choose an ordinary variant before comparison, run it through the normal entry point, and report its outcome separately from skill routing.
4. **Report honestly.** Give the commands, the observed results, the failing cases and coverage limits, and name any comparison you could not run. Keep the agreed cases and thresholds fixed while implementing; changing them is a separate, stated decision.

Deeper references: [ECC benchmark workflow](https://github.com/affaan-m/ECC/blob/main/skills/benchmark-optimization-loop/SKILL.md) and [ECC ML workflow](https://github.com/affaan-m/ECC/blob/main/skills/mle-workflow/SKILL.md).
