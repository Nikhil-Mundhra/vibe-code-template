# States and forms

## State coverage (every data driven view)

| State | Requirement |
| --- | --- |
| Loading | Skeleton with final dimensions. No spinners for regions larger than a button. Use pending state on buttons for mutations. |
| Empty | One sentence on what belongs here, one clear next action. Icon from lucide at 24px, muted. |
| Error | What failed in plain words, retry action wired to `refetch`, preserve any stale data on screen when available. |
| Partial or stale | Show data with an as of caption and subtle refetch indicator, not a blocking loader. |
| Success | Inline confirmation or toast that names the object ("Plan saved"), no exclamation marks. |
| Disabled | Explain why when not obvious (tooltip or helper text). |
| Forbidden or not found | Distinct messages, link back to a safe place. |

React Query: use `isPending` for first load, `isFetching` for background refresh, keep previous data for pagination and filter changes, and invalidate precisely by query key. Keep query functions and keys inside the owning feature.

## Forms (React Hook Form + Zod)

- Resolver uses schemas from `@wealth-advisor/contracts`. Extend with `.extend` or `.refine` locally only for UI only rules.
- Validate on blur first, then on change after the first error (`mode: "onTouched"`).
- Use the `Field` primitive: label above control, hint below in caption style, error below in negative color with an icon, wired with `aria-describedby` and `aria-invalid`.
- Single column layout, group related fields with a titled fieldset. Two columns only for short paired values (for example start and end date).
- Submit button shows pending state, form fields stay editable unless submission would conflict. Server errors map to fields when possible, otherwise an Alert at the top of the form with focus moved to it.
- Preserve input on error. Warn on navigation with unsaved changes.
- Currency and percent inputs: numeric keyboard, tabular figures, unit shown as a suffix or prefix inside the control, parse and format through `lib/format`.
- Never validate with color alone. Never disable the submit button just because the form is invalid, show the errors instead.

## Accessibility baseline

Semantic landmarks, one `h1` per page, logical heading order, labels tied to controls, 4.5:1 text contrast (3:1 for large text and UI borders), keyboard reachable everything, visible focus, `aria-live="polite"` for async status messages, no motion that cannot be disabled.
