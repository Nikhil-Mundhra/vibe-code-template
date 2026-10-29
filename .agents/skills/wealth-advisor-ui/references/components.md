# Components

## Where things live

```
src/app          routing, providers, app shell
src/features     feature folders: screens, feature specific components, queries
src/components   shared presentational primitives (no data fetching, no feature imports)
src/lib          pure helpers: cn, format (money, percent, date), small hooks
```

Tests sit beside the file they test: `button.tsx` and `button.test.tsx`.

## The `cn` helper (lib)

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## CVA pattern for every primitive

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/cn";

const button = cva(
  "inline-flex items-center justify-center gap-2 rounded-control font-medium transition-colors duration-fast " +
    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus " +
    "disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-accent text-on-accent hover:bg-accent-hover",
        secondary: "border border-border-strong bg-surface text-ink hover:bg-surface-sunken",
        ghost: "text-ink hover:bg-surface-sunken",
        danger: "bg-negative text-on-accent hover:opacity-90",
      },
      size: { sm: "h-8 px-3 text-sm", md: "h-10 px-4 text-sm", lg: "h-11 px-5 text-base" },
    },
    defaultVariants: { variant: "secondary", size: "md" },
  },
);

type ButtonProps = React.ComponentProps<"button"> & VariantProps<typeof button> & { pending?: boolean };

export function Button({ variant, size, pending, className, children, disabled, ...rest }: ButtonProps) {
  return (
    <button className={cn(button({ variant, size }), className)} disabled={disabled || pending} aria-busy={pending} {...rest}>
      {children}
    </button>
  );
}
```

React 19 note: refs are regular props, so do not wrap primitives in `forwardRef`. Accept `ref` through `React.ComponentProps<...>`.

## Primitive inventory (create only if missing, check first)

Button, IconButton, Input, Select, Textarea, Checkbox, RadioGroup, Field (label, control, hint, error), Card, Badge, Alert, Table, Skeleton, EmptyState, ErrorState, Dialog, Tooltip, Tabs, PageHeader, Stat (label, value, as of, delta).

Rules: one primary button per view. Badges describe status, never act. Tables get sticky headers when they scroll, row hover, and right aligned numeric columns. Dialogs trap focus, close on Escape, and return focus to the trigger.

## Page anatomy

`PageHeader` (title, short description, primary action on the right) then content in sections separated by `gap-8`. Filters sit above tables, not in side panels, unless there are more than five. Never nest cards inside cards.
