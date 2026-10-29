---
name: wealth-advisor-ui
description: Design and build UI for the wealth advisor frontend (React 19, Tailwind 4, CVA, React Hook Form, React Query). Use this skill whenever creating or changing any screen, component, form, table, chart, empty or error state, or styling in the frontend folder, and whenever the user says things like "make it look better", "polish", "redesign", "add a page", or "build a component", even if they never mention design. Enforces the product's visual identity, design tokens, state coverage, accessibility, and a self review loop so output does not look like generic AI generated UI.
---

# Wealth Advisor UI

You are building software that people trust with their money. The interface should feel calm, precise, and quietly confident, closer to a well set financial report than a startup landing page. Every choice below serves that.

## Design direction (commit to this, do not drift)

- **Tone:** editorial and restrained. Warm neutral surfaces, one deep accent, generous whitespace, strong hierarchy through size and weight rather than color.
- **Density:** medium to high on data screens (advisors scan tables all day), airy on onboarding and summary screens.
- **Type:** Fraunces for page titles and a small number of headline figures. DM Sans for everything else. Numbers in tables and forms always use tabular figures.
- **Color:** neutrals do 90 percent of the work. The accent marks the single primary action per view. Positive and negative colors are reserved for financial direction and validation, never decoration.
- **Motion:** short and functional (150 to 200ms). Fades and small translations only. Always respect prefers-reduced-motion.
- **Never:** emoji (strict policy, applies to UI text, toasts, empty states, comments, test names), gradients as decoration, glassmorphism, identical card grids as a default layout, centered hero sections inside the app, urgency or scarcity language, stock illustration blobs.

## Workflow for any UI task

1. **Read before writing.** Open one or two existing screens in the same feature and the tokens file. Match their patterns. If a primitive exists in `components/`, use it. Do not create a near duplicate.
2. **Plan in a few lines:** what is the one primary action, what is the information hierarchy, which states exist (loading, empty, error, partial, success, disabled).
3. **Build with tokens and primitives only.** See `references/tokens.md` and `references/components.md`.
4. **Cover every state** using the checklist in `references/states-and-forms.md`.
5. **Write or update the test** next to the file. Query by role and accessible name.
6. **Run the self review** in `references/review-checklist.md` before saying you are done. If you can capture screenshots at 390, 768 and 1280 pixel widths, do so and critique them honestly. Fix what you find, then report what you checked.

## Hard rules

1. No raw hex, rgb, or arbitrary Tailwind values (`w-[317px]`, `text-[#333]`). Use theme tokens. If a token is missing, add it to the theme with a semantic name and say so in your summary.
2. Variants go through CVA. No ad hoc class strings for button, badge, input, card, or alert styles. Merge classes with the shared `cn` helper in `lib`.
3. Icons come from lucide-react only, sized with the scale in tokens. No emoji, no unicode symbols used as icons.
4. Relative imports only, no path aliases. Respect layering: `app` may import `features`, `features` may import `components` and `lib`, `components` may import `lib`, and nothing imports upward.
5. Forms use React Hook Form with the Zod schemas from `@wealth-advisor/contracts`. Do not rewrite validation or business rules that already live in the shared packages.
6. Money, percentages, and dates are formatted through shared helpers in `lib` (Intl based). Never format inline.
7. Color is never the only signal. Gains and losses show a sign and an icon or label as well.
8. Every interactive element has a visible focus ring, a 40px minimum hit area on touch layouts, and an accessible name.
9. No layout shift between loading and loaded. Skeletons match final dimensions.
10. Copy is plain, specific, and neutral. Say what happened and what to do next. No exclamation marks, no jokes in error states.

## Wealth specific conventions

- Every figure that depends on time shows its as of date or period near the number.
- Show units and currency explicitly. Right align numeric columns, left align labels.
- Projections and hypotheticals are visually distinct from actuals (label plus lighter treatment) and carry required disclosure text from the product, not invented text.
- Destructive or irreversible actions (submit a recommendation, send to client) use a confirmation step that restates the consequence.
- Charts: direct labels over legends where possible, no 3D, no dual axes unless unavoidable, always a text or table alternative, axis units visible.
- Empty states for advisors explain the next step, they do not apologize.

## When unsure

Choose the quieter option. Prefer fewer elements, clearer hierarchy, and more whitespace. If the request conflicts with these rules, follow the request but flag the conflict in one sentence.
