# Web dashboard (placeholder)

This folder holds the SEB-XRIF dashboard client. It is a **placeholder** until
the production UI kit is dropped in.

Planned stack (specification section 3.4 and section 6):

- React + Vite + TypeScript
- A single `Chart` wrapper component over Chart.js
- TanStack Query for all fetching, caching, and retry logic
- Tailwind CSS + shadcn/ui as the stand-in presentation layer

The data contract is the FastAPI service in `../api`. Because all fetching is
owned by TanStack Query hooks, swapping the placeholder UI kit for the
production kit touches presentation only, never data logic.
