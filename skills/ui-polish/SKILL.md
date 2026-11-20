---
name: ui-polish
description: Inspect and polish a rendered UI against a reference before calling it done. Use when building, polishing, reviewing or QA-ing a UI that is rendered - web pages, app screens, and PDF or print output - and before reporting any UI task as complete. Renders the real screen at 1440, 768 and 390 px (or PDF pages as images), compares it with the project's design-system doc, an approved baseline screenshot or a design file, fixes visual, responsive, accessibility and interaction issues, saves screenshots as evidence, and reports a verdict (pass, fixes needed, or withheld: no baseline).
---

# UI Polish

Use this when the user asks to build, improve, redesign, polish, review or QA a UI, especially when the rendered output is the source of truth.

## Outcome

Code that compiles is not done. The work is done when the interface has been rendered, inspected at the relevant widths against a reference, adjusted, and reported with evidence and remaining risks.

## Baseline

Judge the screen against a reference, because taste without one drifts:

1. `docs/design-system.md` (written by the `ui-design` skill), or
2. an approved baseline screenshot, or
3. a design file.

When none exists, the screen cannot pass. Report the verdict as "withheld: no baseline", save the current screenshots as a proposed baseline under `docs/plans/evidence/<slug>/`, and ask the user to approve them.

## Workflow

1. Inspect the stack before changing UI: framework and router, component library, tokens or theme files, reusable components, local start command.
2. Identify the target: page, route, component, modal, form, table or flow; the primary user task; the states it needs (empty, loading, error, disabled, success, destructive).
3. Implement the smallest useful change: reuse existing components and tokens, add dependencies only if the project already points that way, keep dimensions stable with responsive constraints.
4. Run the app and render it in a real browser (see Browser notes).
5. Capture 1440, 768 and 390 px wide unless the project names other widths. Save screenshots to `docs/plans/evidence/<slug>/` (for example `w1440.png`).
6. Check:
   - information hierarchy and clarity of the primary action
   - spacing rhythm and alignment
   - typography scale and text wrapping
   - contrast and focus visibility
   - keyboard navigation of interactive elements
   - hover, active, disabled, loading and error states
   - console errors and failed network requests
   - layout stability when content changes dynamically
   - match with the baseline reference
7. Fix issues and re-check the affected width. Repeat until clean.
8. Write the report (see Report).

## Design rules

- Build the real usable screen first, not a marketing wrapper around it.
- Prefer calm, functional, high-signal UI over decorative dashboards.
- Skip default AI-looking purple/blue gradients, glass effects, floating blobs and ornamental cards unless the product already uses them.
- Keep cards out of cards; nested containers flatten the hierarchy.
- Use icons for common tool actions when an icon library already exists.
- Use semantic tokens when available. Without a token system, keep new colors minimal and note the rationale in code or docs.
- Keep text inside its container at every width.
- Reserve large display type for real hero surfaces, not dense app panels.
- Give repeated controls a stable size so labels, hover states, counters and icons do not shift the layout.

## PDF and print output

1. Render each page to an image: `pdftoppm -png -r 110 file.pdf out/page` when installed, otherwise the browser's print preview.
2. Check page breaks (no orphaned headings, rows split across pages, or empty pages), clipped or overflowing text, margins, and that tables and charts stay legible.
3. Check embedded fonts with `pdffonts file.pdf` when installed; unembedded fonts render differently on other machines.
4. Save the page images to `docs/plans/evidence/<slug>/` and reference them in the report.

## Browser notes

- Use whichever the session has: Playwright MCP, Chrome DevTools MCP, Claude in Chrome, or the built-in browser.
- Computer use is for native apps and for a final human-fidelity visual pass; it needs a local interactive session.
- `scripts/ui-check.mjs <url> [outDir] [widths]` captures full-page screenshots and collects console errors and failed requests. It needs Playwright installed in the project (`npm i -D playwright`).
- If a local preview fails with a connection error, check that the dev server is still running before suspecting the UI code.
- For 3D, canvas, charts or generated media, use screenshots or pixel checks to confirm the surface is not blank.

## Optional visual regression

For important or regression-prone surfaces, add a Playwright screenshot test:

```ts
await expect(page).toHaveScreenshot("surface-name.png", { fullPage: true });
```

Accept a new baseline only after inspecting that the screenshot shows a good state, and with the user's approval.

## Report

- what changed
- what was visually verified, with evidence paths
- checks run (tests, console, network, accessibility)
- verdict: pass / fixes needed / withheld: no baseline
- remaining risks
