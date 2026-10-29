# Tokens

Define all tokens once in the main CSS entry using Tailwind 4's `@theme` block. Names are semantic, not literal. The values below are a starting point to adapt to the brand, but the structure should stay.

```css
@import "tailwindcss";

@theme {
  /* Type */
  --font-sans: "DM Sans", ui-sans-serif, system-ui, sans-serif;
  --font-display: "Fraunces", ui-serif, Georgia, serif;

  /* Surfaces and text (warm neutral) */
  --color-canvas: #faf8f5;
  --color-surface: #ffffff;
  --color-surface-sunken: #f3f0ea;
  --color-border: #e4dfd5;
  --color-border-strong: #c9c2b3;
  --color-ink: #1c1b18;
  --color-ink-muted: #5f5b52;
  --color-ink-subtle: #8a857a;

  /* Accent: one deep, calm hue */
  --color-accent: #1f4d3f;
  --color-accent-hover: #173c31;
  --color-accent-soft: #e3eee9;
  --color-on-accent: #ffffff;

  /* Semantic status (check 4.5:1 contrast on their backgrounds) */
  --color-positive: #1d6b3f;
  --color-positive-soft: #e4f2ea;
  --color-negative: #a3321f;
  --color-negative-soft: #f9e8e4;
  --color-warning: #8a5a00;
  --color-warning-soft: #fbf0d9;
  --color-focus: #2f6fed;

  /* Radius and shadow */
  --radius-control: 0.5rem;
  --radius-card: 0.75rem;
  --shadow-raised: 0 1px 2px rgb(28 27 24 / 0.06), 0 2px 8px rgb(28 27 24 / 0.04);

  /* Motion */
  --ease-out-soft: cubic-bezier(0.2, 0.7, 0.2, 1);
  --duration-fast: 150ms;
  --duration-base: 200ms;
}
```

If a dark theme is required, redefine the same semantic variables under a `[data-theme="dark"]` selector. Components must never need to know which theme is active.

## Type scale (use these roles, not arbitrary sizes)

| Role | Classes | Use |
| --- | --- | --- |
| Page title | `font-display text-3xl tracking-tight text-ink` | One per page |
| Section title | `font-display text-xl text-ink` | Section headers |
| Headline figure | `font-display text-4xl tabular-nums` | At most one or two per screen |
| Body | `text-sm text-ink` (base text on dense screens) or `text-base` on reading screens | Default |
| Label | `text-sm font-medium text-ink` | Form labels, table headers |
| Caption | `text-xs text-ink-muted` | Helper text, as of dates |

Rules: two weights per screen is usually enough. Do not use Fraunces below 20px. Apply `tabular-nums` to every number that appears in a column, a table, or an input. Verify that the loaded Fraunces axes include the numeral features you rely on, and fall back to DM Sans for numbers if they look uneven.

## Spacing and layout

- Use the Tailwind spacing scale in steps of 4 (`1, 2, 3, 4, 6, 8, 12, 16`). Prefer `gap` over margins.
- Page content max width 72rem for data screens, 40rem for forms and reading.
- Vertical rhythm: section gap `gap-8`, group gap `gap-4`, field gap `gap-2`.
- Elevation is rare: borders first, shadow only for overlays and the one raised card that needs it.

## Icons

lucide-react, sizes 16 (inline with text), 20 (buttons, nav), 24 (empty states). `strokeWidth={1.75}`. Decorative icons get `aria-hidden`. Icon only buttons need an `aria-label`.
