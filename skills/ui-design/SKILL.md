---
name: ui-design
description: "Use when designing or refining a web or app screen, component, visual system, or interaction. Derive the layout and visual hierarchy from the user's task, content, and project references. Consult local guidance for unresolved typography, color, layout, chart, UX, or stack decisions, including Korean-market conventions."
---

# UI Design

## Start with the screen's job

1. Read the brief, `docs/design-system.md` or the project's design file, active decisions in `docs/plans/`, and adjacent screens, components and tokens. Note what the user asked to change. For Korean-language or Korean-market UI, read [Korean conventions](references/korean.md) before choosing type, wrapping, dates, currency, or data colors.
2. State the task in one sentence for yourself. Identify what the user needs to find, compare or decide, the next action, and the poor-data or error states that change the layout. Arrange representative content and controls before choosing visual effects. Use authentic terminology and plausible values.
3. Choose which element gets attention first and what should recede. Use type, proximity, spacing, and alignment to group related items. Give a competing action less visual weight. Use cards where grouping, independent interaction, or elevation calls for a surface. For an inventory workspace, put filters near the stock list, align comparable quantities in rows, and place the order action where the selection is made.
4. For a new visual direction, inspect the whole supplied reference, including how hierarchy and spacing change across sections and widths. Extract concrete choices about composition, typography, and imagery and adapt them to this product. For a video reference, inspect frames around the important state changes and capture how pacing, framing, and content change at each beat. For a working screen, prioritize scanability and frequent actions. For a brand page, use specific product copy and a focal point supported by the brief. If the brief calls for an illustrated product demo, frame one actual product interaction with the product's visual system and show its result.
5. If an important layout or interaction is still uncertain, preview the smallest representative slice with real content and the project's design tokens. Compare it with the brief in the target viewport, then refine the specific choice that failed before extending it across the site.

## Give visual choices a reason

- Remove duplicate labels, ornamental status chips, nested boxes, and equal-weight sections that compete with the primary content. Read the headings and calls to action with the product name removed. Replace copy that could describe any product with the action or benefit the page can demonstrate.
- Give color, borders, shadows, and imagery a role in the content, brand, or hierarchy. A gradient, glass surface, or bento grid can serve the brief. For translucent surfaces, start with a mostly solid fill behind reading areas and use a quiet edge or shadow to establish depth where it matters. Verify legibility over the actual backgrounds and in the supported themes. For a feature grid, vary visual weight according to the story each tile tells.
- Use immediate feedback for repeated keyboard actions and core controls. Add motion when it communicates a change, causality, or where a surface came from. For example, an opening filter popover can ease out from its trigger. Keep the transition short, reversible, and usable with reduced motion. Skip decorative stagger and reveal effects in routine workflows.
- Keep controls reachable by keyboard and touch, preserve visible focus, and keep critical labels legible at narrow widths. Use [UX rules](references/quick-reference.md) for the specific issue and [native app checks](references/pro-rules.md) when working on iOS, Android, React Native, or Flutter.

## Consult the local catalog as needed

Use [the search reference](references/search.md) for commands, query examples, RTL filtering, and design-system export. Start with an explicit `--domain` for an unresolved question, `--stack` for implementation guidance on the detected stack, or `--design-system` when comparing new system-wide directions. Use a result only if it fits the task, platform, and project decisions. A generated palette or layout is a candidate to test with the actual content.

After the user approves design choices, record the palette, type scale, spacing, and component rules in `docs/design-system.md` and the reason in the active spec's Decisions section.

```
- D<n>: <decision> -- why: <reason> -- by: user|observed
```

Use `ui-polish` on the rendered implementation to test the hierarchy and interaction decisions.
