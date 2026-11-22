---
name: ui-polish
description: "Use when building, polishing, reviewing, or verifying rendered web pages, app screens, PDFs, or print output. Inspect the real surface for hierarchy, generic copy and decoration, realistic data, and interaction behavior. Save evidence and compare against the project's design system or approved reference before visual sign-off."
---

# UI Polish

## Render the target

1. Identify the route, screen or artifact, the primary task, and the affected states. Read the stack, reusable components, tokens, and the local preview command. Use the project's design system, design file, or approved screenshot as the baseline.
2. Capture the current screen before editing when available. Inspect the actual route at 1440, 768, and 390 px wide unless the project specifies other widths. For native apps, use the relevant device sizes. Save matched before and after views and any state needed to demonstrate a finding under `docs/plans/evidence/<slug>/`. Use synthetic values for shareable evidence when the real data is private.
3. Continue defect review if there is no approved baseline. Save the current candidate as a proposed baseline, request approval, and use `withheld: no baseline` for visual sign-off. The proposal is separate from defects that can be fixed now.

## Review what the user sees and does

- Check what draws the eye first and whether the next action is clear. Read the headings and labels by themselves. Flag copy that repeats nearby content or could apply to any product. Compare a simpler version for the most distracting choice, such as a redundant badge, nested card, decorative grid or shadow. Keep an intentional brand or material choice where it supports the task and stays legible in context.
- Check alignment, density, and text wrapping. Run the affected screen with realistic difficult values through its real input boundary (fixtures, props, or API stubs). Try an email or long name that cannot easily wrap, translated labels, missing fields, and zero or large counts where applicable. Render the changed states at the widths most likely to fail and check for clipped text, lost actions, or a jump in layout.
- Use the primary action with keyboard and pointer or touch where relevant. Check focus visibility and return, loading, error and disabled states, and whether controls remain reachable with long labels. Check contrast on the actual background, including overlays. Report emulation as such when a touch behavior requires physical hardware.
- Try frequent actions at normal speed. Remove wait-inducing motion on repeated shortcuts and decorative entrances. For purposeful motion, open, reverse or retrigger it mid-flight, and repeat with reduced motion enabled. A filter popover should open from its trigger and settle correctly through rapid changes. For an animated product demo, view the complete sequence and inspect frames around the action and result. The trigger, change and settled state must be clear.
- Check console errors, failed requests, and layout stability on the path under review. A screenshot shows composition. Drive the interaction to verify behavior.

Fix issues within the requested scope, then repeat the affected viewport, fixture, and action. In the report, name the route or component, the width and state, what the user experienced, and the evidence for the correction. Review-only requests end with findings.

## PDF and print output

1. Render each page to an image with `pdftoppm -png -r 110 file.pdf out/page` when available or inspect every page in print preview.
2. Check page breaks (no orphaned headings, rows split across pages, or empty pages), clipped or overflowing text, margins, and that tables and charts stay legible.
3. Check embedded fonts with `pdffonts file.pdf` when available. Save page images to `docs/plans/evidence/<slug>/` and reference them in the report.

## Browser notes

- Use the available browser or device tools, such as Playwright MCP, Chrome DevTools MCP, Claude in Chrome, or the built-in browser.
- `scripts/ui-check.mjs <url> [outDir] [widths]` captures full-page screenshots and collects console errors and failed requests when Playwright is already available.
- If a local preview fails to connect, check that the dev server is still running. For a canvas, chart or generated image, inspect the rendered pixels to confirm the surface is visible.
- If adding a screenshot regression test is in scope, use the project's existing tooling. Inspect a candidate baseline and obtain approval before accepting it.

## Report

List the meaningful changes, the tested widths, states and interactions, and evidence paths. Use `pass` when the inspected scope meets the baseline, `fixes needed` for remaining findings, or `withheld: no baseline` when the reference is unavailable. State any checks that could not run.
