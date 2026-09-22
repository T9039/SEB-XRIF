# Web dashboard (placeholder)

React + TypeScript client for the SEB-XRIF API, built and managed with
**Vite+** (`vp`) — VoidZero's unified toolchain: Vite 8 + Rolldown (Rust
bundler) + Oxc/Oxlint/Oxfmt (Rust lint/format) + Vitest. This is a
**placeholder UI**: the production design system replaces the markup and CSS,
but never the data layer.

## Run

```bash
# from the repository root
make web                 # Vite+ dev server on http://localhost:5173
make dev                 # API + dashboard together
```

The dev server proxies `/api` to the FastAPI service on `:8000`
(`vite.config.ts`). In production, nginx proxies `/api` to the API container.

## Scripts

| Command            | Purpose                                     |
| ------------------ | ------------------------------------------- |
| `npm run dev`      | `vp dev` — dev server with HMR              |
| `npm run build`    | `tsc --noEmit` then `vp build` (Rolldown)   |
| `npm run preview`  | `vp preview` — serve the production bundle  |
| `npm run lint`     | `vp check` — oxfmt + oxlint + type check    |
| `npm run lint:fix` | `vp check --fix` — auto-format and auto-fix |
| `npm run test`     | `vp test run` — Vitest 4                    |

The `vp` binary resolves from the local `vite-plus` dependency
(`node_modules/.bin/vp`), so no global install is required. Installing
`vite-plus` globally adds the standalone `vp` command.

## Toolchain

`vp toolchain` prints the resolved versions. Currently:

- Vite 8.3.0 (bundled in `@voidzero-dev/vite-plus-core`)
- Rolldown 1.2.9 (Rust bundler) with Oxc 0.150.0
- Vitest 4.1.11
- Oxlint 1.83.0, oxlint-tsgolint 7.0, Oxfmt 0.68.0
- tsdown 0.23.0 and Vite Task

The `vite` package in `package.json` is aliased to
`@voidzero-dev/vite-plus-core` via `overrides`, and `vitest` is pinned to the
version the toolchain ships, so the whole stack uses one tested set of tools.

## Structure

```
src/
  api/client.ts        Axios instance (base URL from VITE_API_URL)
  api/hooks.ts         TanStack Query hooks for every endpoint
  charts/Chart.tsx     Single Chart.js wrapper (swap point for the library)
  components/          HealthBadge, MetricCards, TierDistribution,
                       TrendChart, ImportancePanel
  types.ts             API response types
  App.tsx              Dashboard shell
  index.css            Placeholder styles
```

## Swapping in the production UI kit

1. Keep `src/api/hooks.ts` unchanged — all data access lives there.
2. Keep `src/charts/Chart.tsx`; re-style or repoint it if the chart library
   changes.
3. Replace the `components/` and `App.tsx` markup with the production kit.
4. Add `VITE_API_URL` in `.env` if the API is not served under `/api`.
