# Self review checklist

Run this before reporting completion. Be critical. If an item fails, fix it, do not just mention it.

## Visual
- [ ] One clear focal point and one primary action per view
- [ ] Hierarchy works when squinting: title, section titles, body, captions are distinguishable
- [ ] Only tokens used, no raw colors or arbitrary values
- [ ] Spacing follows the scale, rhythm is consistent, nothing cramped or floating
- [ ] Numbers are tabular, right aligned in columns, with units and as of dates
- [ ] No emoji anywhere, no decorative gradients, no cards inside cards
- [ ] Looks calm. If it looks like a template, remove elements until it does not

## Behavior
- [ ] Loading, empty, error, partial, and disabled states all implemented and reachable
- [ ] No layout shift when data arrives
- [ ] Forms validate on blur, errors are specific, input preserved on failure
- [ ] Destructive actions confirm and restate consequences

## Accessibility
- [ ] Keyboard only pass completed, focus order and focus ring correct
- [ ] Names and labels on all controls, icon buttons labeled
- [ ] Gains and losses not conveyed by color alone
- [ ] Reduced motion respected

## Responsive
- [ ] Checked at 390, 768, and 1280 pixel widths, no horizontal page scroll
- [ ] Wide tables scroll inside their own container with sticky first column if needed
- [ ] Touch targets at least 40px on small screens

## Code
- [ ] Layering respected, relative imports only
- [ ] Variants via CVA, classes merged with `cn`
- [ ] Test beside the file, queries by role and name, states covered
- [ ] Type check, lint, and Vitest pass

## Screenshot loop (when tooling allows)
Capture the screen at the three widths in each key state (loaded, empty, error). Write down the three weakest things you see, fix them, recapture once. Report what changed.
