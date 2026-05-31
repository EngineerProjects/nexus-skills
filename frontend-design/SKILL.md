---
name: frontend-design
description: >
  Use when the user wants to build any web UI — components, pages, dashboards,
  landing pages, posters, React/Vue components, HTML/CSS layouts, or when
  styling or redesigning an existing interface. Produces production-grade,
  visually distinctive code that avoids generic AI-generated aesthetics.
user-invocable: true
---

# Frontend Design

## Step 1 — Understand context before touching code

Before writing a single line, answer:

1. **What is this for?** (product type, industry, audience)
2. **What feeling should it evoke?** (serious, playful, premium, raw, minimal…)
3. **What framework / constraints?** (plain HTML, React, Vue, Tailwind, specific CSS approach)
4. **What content does it hold?** (text-heavy, data-dense, visual-first, interactive)

Don't skip this. A button on a medical dashboard and a button on a music app are different objects.

## Step 2 — Commit to an aesthetic direction

Pick one strong direction and execute it fully. Half-measures look worse than extremes.

**Possible directions:**
- **Brutal minimal** — stark typography, almost no decoration, maximum white space
- **Editorial** — magazine-style, strong typographic hierarchy, pull quotes, ruled lines
- **Data-forward** — dense, monospace elements, tabular grids, muted palette with accent highlights
- **Warm organic** — rounded shapes, earthy tones, serif body, generous spacing
- **Dark technical** — dark background, accent neon or blue, code-like UI, strong contrast
- **Geometric** — structured grids, bold shapes, flat color blocks, no gradients
- **Luxury** — refined spacing, thin fonts, gold or deep color accents, restrained motion

State your choice at the start: *"I'm going with editorial — strong typographic hierarchy, newspaper-style columns."*

## Step 3 — Typography first

Typography carries more visual weight than color or layout. Choose a pairing:

```css
/* Editorial example */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap');

:root {
  --font-display: 'Playfair Display', serif;
  --font-body: 'Source Serif 4', serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

Rules:
- Minimum 2 weights of the same family, or an intentional display + body pairing
- Body text: 16–18px, line-height 1.6–1.7
- Display text: bold contrast, large sizes (48px+), tight line-height (1.1–1.2)
- Never use system-ui, Arial, or Inter unless the brief explicitly calls for it

## Step 4 — Color palette (max 4 values)

```css
:root {
  --color-bg: #F5F0E8;       /* warm off-white */
  --color-surface: #FFFFFF;
  --color-text: #1A1A1A;     /* near-black, not pure black */
  --color-accent: #C4442E;   /* single strong accent */
  --color-muted: #8A8A8A;    /* secondary text */
}
```

Rules:
- Define colors as CSS variables at :root — never hardcode hex in components
- One accent color, used sparingly
- Background and text must pass WCAG AA contrast (≥ 4.5:1)
- Avoid purple-on-white gradients — it's the most overused AI default

## Step 5 — Layout and spacing

Use a spacing scale, not arbitrary values:

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 32px;
  --space-xl: 64px;
  --space-2xl: 128px;
}
```

Layout patterns:
```css
/* Centered content column */
.content {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

/* CSS Grid for complex layouts */
.grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-lg);
}
```

Break the grid deliberately — one asymmetric element per layout adds energy without chaos.

## Step 6 — Motion (if applicable)

Prefer CSS transitions over JavaScript for simple interactions:

```css
.button {
  transition: transform 120ms ease, background 120ms ease;
}
.button:hover {
  transform: translateY(-2px);
}
.button:active {
  transform: translateY(0);
}
```

One well-crafted entrance animation beats a dozen scattered ones:
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.hero {
  animation: fadeUp 400ms ease both;
}
.hero-sub {
  animation: fadeUp 400ms 120ms ease both;
}
```

## Code quality standards

**HTML:**
- Semantic elements: `<main>`, `<header>`, `<nav>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- `alt` text on all images
- Labels associated with form inputs

**CSS:**
- Custom properties for all repeated values
- Mobile-first media queries (`min-width`, not `max-width`)
- No `!important` except for utility overrides
- BEM or kebab-case class names, consistent throughout

**React / Vue:**
- Components under 150 lines; extract when bigger
- Props documented with PropTypes or TypeScript types
- No inline styles except truly dynamic values

## Common mistakes to avoid

| Mistake | Fix |
|---|---|
| White background + purple gradient hero | Choose any other direction |
| Card grid of equal-sized boxes | Vary size, weight, and density |
| All text the same weight | Build a clear 3-level hierarchy |
| Animations on everything | One entrance, one hover, that's it |
| 6 shades of blue | 1 accent color + neutrals |
| Tiny font on mobile | 16px minimum body, 44px minimum touch target |
| Overusing `box-shadow` | Borders and background contrast often look cleaner |

## Deliver working code

Always deliver code that runs:
- HTML/CSS: a single self-contained file with `<style>` block, or separate files clearly structured
- React: complete component with all imports, no missing dependencies
- Include realistic placeholder content (not "Lorem ipsum" unless the user asked)
- State the stack used in a comment at the top of the file

```html
<!-- Stack: HTML5 + vanilla CSS | Direction: editorial | Fonts: Playfair + Source Serif -->
```

## Checklist before delivering

- [ ] Code runs without errors in a browser
- [ ] Mobile layout tested (≤ 375px width)
- [ ] Color contrast passes WCAG AA
- [ ] No placeholder text except intentional demo content
- [ ] Font imports included
- [ ] CSS variables defined at :root
- [ ] Semantic HTML used throughout
