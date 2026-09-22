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

The dashboard in `../web` currently ships a placeholder UI. To use these
components instead, build the library and add it as a dependency:

```bash
pnpm build                       # produces dist/index.mjs + dist/index.d.ts
cd ../web && npm install ../ui   # or add "@humanity-erp/ui": "file:../ui"
```

Then import the stylesheet once and use the components:

```tsx
import "@humanity-erp/ui/index.css";
import { Button, Card } from "@humanity-erp/ui";
```
