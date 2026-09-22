# SEB-XRIF UI component library

A [shadcn/ui](https://ui.shadcn.com) component library (Base UI + Tailwind v4)
with [Storybook](https://storybook.js.org) stories for every component. This is
the design system for the SEB-XRIF dashboard: edit components here, preview
them in Storybook, then consume them from `../web`.

## Requirements

- Node.js 20+ and **pnpm** (the workspace uses pnpm catalogs). If `pnpm` is not
  installed: `corepack enable` or `npm install -g pnpm`.

## Install

```bash
pnpm install
```

Dependency versions are centralised in the `catalog:` block of
`pnpm-workspace.yaml`, and `package.json` references them as `catalog:`.

## Storybook

```bash
pnpm storybook          # dev server on http://localhost:6006
pnpm build-storybook    # static site in ./storybook-static
```

The stories live next to each component as `*.stories.tsx` and load with
autodocs, accessibility (a11y), and light/dark theme switching
(`.storybook/preview.ts`). Tailwind v4 is wired into Storybook's Vite build in
`.storybook/main.ts`.

## Other scripts

| Command                | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| `pnpm storybook`       | Storybook dev server on `:6006`             |
| `pnpm build-storybook` | Build the static Storybook                  |
| `pnpm build`           | Package the library with `vp pack` (tsdown) |
| `pnpm check`           | `vp check` — oxfmt + oxlint + type check    |
| `pnpm test`            | `vp test` (Vitest)                          |

## Structure

```
src/
  components/
    ui/           60+ primitives (button, card, table, chart, sidebar, ...)
    auth/         login, sign-up, social buttons
  hooks/          use-theme, use-mobile
  lib/utils.ts    cn() class merge helper
  index.css       Tailwind v4 theme tokens and dark variant
  index.ts        public entry point
.storybook/
  main.ts         stories glob, addons, Tailwind Vite plugin
  preview.ts      global CSS, a11y, theme decorator
```

## Consuming from the dashboard

`web/` is a sibling workspace package and consumes these components directly
from source, so edits here hot-reload in the dashboard. The wiring is:

- `web/vite.config.ts` aliases `@humanity-erp/ui` to `ui/src/index.ts`.
- `web/tsconfig.json` mirrors the alias in `paths`.
- `web/src/index.css` imports `../../ui/src/index.css` and scans `web/src`.

The dashboard uses `Card`, `Badge`, `Alert`, `Skeleton`, `ChartContainer`
(Recharts), and `ThemeProvider` from this library. Import them by name:

```tsx
import { Button, Card, CardContent, Badge } from "@humanity-erp/ui";
```

If you later prefer the prebuilt package, run `pnpm build` here and import the
`dist` output; the `vp pack` build manages `package.json` exports.
