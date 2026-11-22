# Local UI design catalog

Use these commands when the design workflow identifies a decision that would benefit from a lookup. Resolve `<skill-dir>` from the loaded SKILL.md. The tool runs with Python 3.9 or newer and needs no external packages. Use generic terms in queries and exports to avoid carrying private project data into them.

## Query contract

Build each query around **one dominant intent**, using **2–5 meaningful terms** and one useful constraint such as product, platform, or interaction. Verify the returned domain/category, top result identity, and fit for the user's product and platform before applying it. **Retry once** with a narrower rewrite or explicit domain/stack when output is empty or off-topic. If that retry fails, state that no verified match was found and label any general guidance as a fallback. Do not persist unverified output.

For accessibility work, search one observable outcome at a time and use explicit accessibility outcome terms. Query the semantic outcome first (`"error summary validation" --domain ux`), then a component-specific domain if needed (`"decorative icon aria hidden" --domain icons` or `"icon button accessible label" --domain icons`), and only then the implementation stack. Other useful outcome queries include `"focus not obscured" --domain ux`, `"dragging movements" --domain ux`, and `"accessible authentication" --domain ux`. Do not accept a generic accessibility result for a specific interaction or WCAG criterion.

For text-layout and compact-component bugs, search the **semantic UX outcome first, then the detected stack** for implementation details. Useful outcome queries include `"orphan heading line balance" --domain ux`, `"badge chip label wraps" --domain ux`, `"live badge count screen reader" --domain ux`, and `"rapid chip animation interrupted" --domain ux`. After choosing the applicable UX guidance, use a separate stack query such as `"chip badge overflow nowrap" --stack html-tailwind`; do not replace the outcome search with a framework keyword.

For right-to-left interfaces (Arabic, Hebrew, Persian, Urdu, or an explicit `dir="rtl"` / `rtl:` request), add `--rtl` to the `style` and `product` searches and respect the returned `rtl_level`: `full` needs no directional rework, `partial` mirrors but requires per-component checks (icons, carousels, motion paths, charts), and `caveats` means the style or product encodes reading direction — say so before recommending it, and propose a mirrorable alternative when the user needs a strict RTL build. `--rtl=full` restricts the search to the safest rows; `--rtl` alone keeps every level.

## Generate a design system

`--design-system` is an option for when the task needs a full, coherent product-wide visual direction. Skip it for a targeted concern and use `--domain` searches instead:

```bash
python3 <skill-dir>/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This aggregates product/style/color/landing/typography matches, applies reasoning rules from `ui-reasoning.csv`, and returns pattern, style, colors, typography, effects, and anti-patterns to avoid.

**Example:**
```bash
python3 <skill-dir>/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Persist the candidate

Persist only a vetted result that the user wants to save. Keep approved project design decisions authoritative.

To save the design system for retrieval across sessions, add `--persist` and pass `--output-dir` pointed at the project root — without it, files are written relative to whatever directory the tool happens to run from:

```bash
python3 <skill-dir>/scripts/search.py "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>"
```

This creates:
- `design-system/<project-slug>/MASTER.md` — generated system candidate to compare with approved decisions
- `design-system/<project-slug>/pages/` — Folder for page-specific overrides

With a page-specific override, add `--page "dashboard"` to also create `design-system/<project-slug>/pages/dashboard.md`. If Master already exists, a new page file is created without changing Master; an existing page file is skipped unless `--force` is explicitly authorized.

To render the generated system as a static page, add `--preview` (only valid with `--design-system`):

```bash
python3 <skill-dir>/scripts/search.py "<query>" --design-system --persist --preview -p "Project Name" --output-dir "<project-root>"
```

With `--persist`, this writes `design-system/<project-slug>/preview.html` next to Master. Without `--persist`, pass `--output-dir` to write `preview.html` there, or omit it to get a temp file whose path is printed. Existing `preview.html` files are skipped unless `--force` is set.

If `design-system/<project-slug>/MASTER.md` already exists, `--persist` **skips writing and leaves it untouched** unless you also pass `--force` — check whether it exists first (and read it) before regenerating, so you don't silently discard prior decisions the user or a teammate made.

Read an existing `MASTER.md` before deciding whether `--force` is justified. Use `--force` only with explicit user authorization, because it overwrites decisions already made.

### Export design tokens

`--tokens` is valid only with `--design-system`. It prints a machine-readable token document so hex values and font names do not have to be copied by hand:

```bash
python3 <skill-dir>/scripts/search.py "<query>" --design-system --tokens dtcg
python3 <skill-dir>/scripts/search.py "<query>" --design-system --tokens css
```

- `dtcg` prints W3C Design Tokens Community Group JSON (`$value` / `$type`, `color`, `font`, and a `semantic` layer such as `color.primary`, `color.on-primary`, `color.background`, `font.heading`).
- `css` prints `:root` custom properties using the same names as the bundled design-system token compiler (`--color-primary`, `--font-heading`, …).
- Dark-mode results emit the resolved dark values and record the mode in `$description`.
- With `--persist`, also write `tokens.json` next to `MASTER.md` (and `tokens.css` when `--tokens css`). Existing files follow the same `--force` / skip-if-exists rules. Token files are master-level only; `--page` overrides do not emit page-specific tokens.

```bash
python3 <skill-dir>/scripts/search.py "<query>" --design-system --persist --tokens dtcg -p "Project Name" --output-dir "<project-root>"
```

**Retrieval when building a specific page:**
Read the approved project decisions first. Within a generated set, a matching page file supplies page-specific guidance over Master.

### Tune the generated output

Three optional 1-10 sliders that tune `--design-system` output without changing your query. Add any combination of them to the same command:

```bash
python3 <skill-dir>/scripts/search.py "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```

| Dial | Low (1-3) | Mid (4-7) | High (8-10) |
|------|-----------|-----------|-------------|
| `--variance` | Centered / minimal (biases toward Minimalism-style categories) | Balanced / modern | Bold / asymmetric (biases toward Brutalism, Bento Grids) |
| `--motion` | Subtle micro-interactions | Standard scroll/stagger motion | Complex choreography (pin, Flip, SplitText) |
| `--density` | Spacious (24-96px spacing scale) | Standard (16-64px, current default) | Dense/dashboard (8-32px spacing scale) |

- Use `--motion` after identifying a transition that serves the screen. It attaches a GSAP snippet (with framework notes, Do/Don't, and performance notes) pulled from `--domain gsap`, matched to the resolved tier (Subtle/Standard/Complex).
- `--density` overrides the `--space-*` CSS variable table in the ASCII/markdown/MASTER.md output — use it for dashboards (high) vs. marketing pages (low) without hand-editing tokens.
- Leaving a dial unset keeps that part of the output exactly as it was before (no behavior change).

**Example:**
```bash
python3 <skill-dir>/scripts/search.py "internal analytics dashboard" --design-system --density 8 -p "Ops Console"
```

## Search by domain

```bash
python3 <skill-dir>/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

| Need | Domain | Example |
|------|--------|---------|
| Product type patterns | `product` | `"entertainment social" --domain product` |
| More style options | `style` | `"publication editorial typography" --domain style` |
| Color palettes | `color` | `"entertainment vibrant" --domain color` |
| Font pairings | `typography` | `"playful modern" --domain typography` |
| Individual Google Fonts | `google-fonts` | `"sans serif popular variable" --domain google-fonts` |
| Chart recommendations | `chart` | `"real-time dashboard" --domain chart` |
| UX best practices | `ux` | `"error summary validation" --domain ux` |
| Landing page structure | `landing` | `"hero social-proof" --domain landing` |
| Icon recommendations | `icons` | `"decorative icon aria hidden" --domain icons` |
| GSAP animation presets | `gsap` | `"state change shared element" --domain gsap` |
| React/Next.js performance | `react` | `"rerender memo list" --domain react` |
| App/native interface guidelines | `web` | `"accessibilityLabel touch safe-areas" --domain web` |
| RTL compatibility | `style`, `product` | `"dashboard" --domain style --rtl=full` |

Domain is auto-detected from the query if `--domain` is omitted — but auto-detection can misroute overlapping terms (e.g. "font" matches both `typography` and `google-fonts`). If results look off-topic, pass `--domain` explicitly.

## Search by stack

```bash
python3 <skill-dir>/scripts/search.py "<keyword>" --stack <stack>
```

**Available stacks:** `react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `nuxt-ui`, `angular`, `laravel`, `swiftui`, `react-native`, `flutter`, `jetpack-compose`, `html-tailwind`, `shadcn`, `threejs`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`. Detect the project stack from its manifests and source files before querying.

## Output Formats

`--design-system` supports `-f ascii` (default, terminal display), `-f markdown` (documentation), `--json` (machine-readable, includes the raw design system dict plus persistence status), and `--tokens dtcg|css` (W3C Design Tokens JSON or CSS variables; requires `--design-system`).
