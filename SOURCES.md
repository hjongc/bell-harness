# Sources

Where each skill comes from and what changed. Third-party license texts are in `licenses/`.

| Skill | Origin | License | Changes |
|---|---|---|---|
| `skills/map` | Own work, with ideas from [OmO init-deep](https://github.com/code-yeongyu/oh-my-openagent) | Own work. OmO uses the Sustainable Use License. | Original refresh logic checks active decision citations. No text copied. |
| `skills/probe` | The author's earlier `interview` skill, plus the conversation rules, questions and design doc template of the office-hours skill in [gstack](https://github.com/garrytan/gstack) | MIT (`licenses/gstack.txt`) for the gstack parts | Runs without Bun or gstack state: design docs go to `docs/plans/<slug>-design.md` with decision lines in the bell-harness format; three modes (Product, Feature with four questions, Explore); second opinions use a fresh subagent; web research uses the tool's own search with generic terms; all-caps emphasis rewritten as plain instructions with reasons. |
| `skills/spec` | The author's earlier `spec` skill | Own work | Model routing table removed; template gains Status, Decisions, What already exists, Failure modes and Do not; works in Codex on its own; delegation left to each tool's instructions. |
| `skills/preflight` | The author's earlier Claude command `pre-push-check` | Own work | Shared skill for both tools; adds the spec match and decision checks and where to record findings. |
| `skills/eval` | The author's earlier `agent-evaluation` skill, which links to [ECC](https://github.com/affaan-m/ECC) workflows as references | Own work | Renamed; points to `evals/run.py` and adds skill-routing checks. |
| `skills/ui-polish` | The author's earlier Codex skill `frontend-polish-review` | Own work | Tool-neutral browser options; a verdict needs a baseline (`withheld: no baseline` otherwise); PDF and print checks; evidence paths; configurable widths in `scripts/ui-check.mjs`. |
| `skills/ui-design` | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT (`licenses/ui-ux-pro-max.txt`) | Renamed; scripts run as `python3 <skill-dir>/scripts/...`; `--design-system` optional; reads and records project design decisions in `docs/design-system.md`; adds `references/korean.md`. Data and scripts are unchanged and `scripts/tests/` is left out. |
| `skills/away` | Own work | Own work | Adds an unattended roadmap briefing, approval handling and a return report. |

The writing principles for the always-loaded instruction files follow the prompting guides published by Anthropic and OpenAI for their current models.
