# Web dashboard (placeholder)

React + Vite + TypeScript client for the SEB-XRIF API. This is a **placeholder
UI**: the production design system replaces the markup and CSS, but never the
data layer.

## Run

```bash
# from the repository root
make web                 # Vite dev server on http://localhost:5173
make dev                 # API + dashboard together
```

The dev server proxies `/api` to the FastAPI service on `:8000`
(`vite.config.ts`). In production, nginx proxies `/api` to the API container.

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Vite dev server |
| `npm run build` | Type-check and build the static bundle |
| `npm run preview` | Serve the built bundle |
| `npm run typecheck` | TypeScript only |
| `npm run test` | Vitest |

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
