## UI and design rules (frontend)

For any UI work in `frontend/`, use the `wealth-advisor-ui` skill (`.claude/skills/wealth-advisor-ui/`). Short version:

- Product feel: calm, editorial, trustworthy. Warm neutrals, one deep accent, strong hierarchy, generous whitespace.
- Fonts: Fraunces for page titles and a few headline figures, DM Sans for everything else, tabular figures for all numbers.
- Tokens only. All colors, radii, shadows, and type roles come from the `@theme` block. No raw hex and no arbitrary Tailwind values.
- Variants via CVA, class merging via `cn` in `lib`. Reuse primitives in `components/` before creating new ones.
- Icons: lucide-react only. Strict no emoji policy everywhere, including copy, toasts, comments, and test names.
- Forms: React Hook Form with Zod schemas from `@wealth-advisor/contracts`. Validate on blur, specific errors, preserve input.
- Every data view implements loading (skeleton), empty, error with retry, and stale states.
- Money, percent, and date formatting goes through helpers in `lib`. Time dependent figures show an as of date.
- Color is never the only signal. Keyboard and focus behavior must work. Respect reduced motion.
- Architecture: `app` then `features` then `components` then `lib`, relative imports only, tests beside their files.
- Before finishing UI work, run the self review in the skill and screenshot at 390, 768, and 1280 widths when possible.
