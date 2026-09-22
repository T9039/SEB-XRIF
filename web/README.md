# Web dashboard

React + TypeScript dashboard for the SEB-XRIF API, built with **Vite+** and
styled entirely with the [`ui/`](../ui) design system (shadcn/ui + Tailwind v4).
It is a workspace package inside the pnpm workspace at the repository root.

## Run

```bash
# from the repository root
pnpm install             # once, installs web + ui
make web                 # Vite+ dev server on http://localhost:5173
make dev                 # API + dashboard together
```

The dev server proxies `/api` to the FastAPI service on `:8000`
(`vite.config.ts`). In production, nginx proxies `/api` to the API container.

## What it uses from the UI library

- `Card`, `CardHeader`, `CardTitle`, `CardContent` for panels
- `Badge` for the API/model health indicator
- `Alert`, `Skeleton` for empty and loading states
- `ChartContainer`, `ChartTooltip`, `ChartLegend` (Recharts) for the tier,
  behaviour, and feature-importance charts
- `ThemeProvider` for light/dark theming

All data access lives in `src/api/` (TanStack Query hooks), so swapping the
presentation never touches data logic.

## Scripts

| Command             | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `pnpm run dev`      | `vp dev` — dev server with HMR             |
| `pnpm run build`    | `tsc --noEmit` then `vp build` (Rolldown)  |
| `pnpm run preview`  | `vp preview` — serve the production bundle |
| `pnpm run lint`     | `vp check` — oxfmt + oxlint + type check   |
| `pnpm run lint:fix` | `vp check --fix`                           |
| `pnpm run test`     | `vp test run` — Vitest 4                   |

## Structure

```
src/
  api/client.ts        Axios instance (base URL from VITE_API_URL)
  api/hooks.ts         TanStack Query hooks for every endpoint
  components/          HealthBadge, MetricCards, TierDistribution,
                       TrendChart, ImportancePanel, panel-states
  types.ts             API response types
  App.tsx              Dashboard shell (ui Card grid)
  index.css            Imports the ui theme + scans web sources
  main.tsx             ThemeProvider + QueryClientProvider
```

## Toolchain

The workspace uses **Vite+** (`vp`): Vite 8 + Rolldown (Rust bundler) +
Oxc/Oxlint/Oxfmt (Rust lint/format) + Vitest 4. `vp toolchain` prints the
resolved versions. Tailwind v4 is wired in through `@tailwindcss/vite`, and
`src/index.css` imports the design system's stylesheet:

```css
@import "@humanity-erp/ui/index.css";
@source "./**/*.tsx";
```
