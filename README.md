# SEB-XRIF

**Scalable, Evidence-Based XR Integration Framework** — a reusable, reproducible
way of conducting XR education research. This repository holds the data,
analytics, service, visualization, and evaluation layers of the framework.

Team 3 · PRJT302 · Information Technology, Durban University of Technology.

## What this is

SEB-XRIF is not a single model or dashboard. It is a standard recipe: any
institution exports learning data in the xAPI schema, runs the same analytics
pipeline with the same seed and configuration, and reports the same evaluation
metrics. The Random Forest and the dashboard are the first instantiation of the
framework, not the framework itself.

| Layer | Purpose | Module |
| --- | --- | --- |
| Data | Validated, versioned xAPI-schema data | `analytics/data.py`, `analytics/schema.py` |
| Analytics | Predict Low/Medium/High tier; rank drivers | `analytics/` |
| Service | Prediction and analytics REST API | `api/` |
| Visualization | Dashboard over the API (placeholder UI) | `web/` |
| Evaluation | Accuracy/F1/CV, SUS, Cohen's d, T0/T1/T2 | `eval/` |

The full design, rationale, alternatives, and phased build plan are in the
[technical specification](docs/SEB-XRIF_Technical_Specification.pdf).

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (manages Python 3.12 automatically)
- Node.js 20+ and npm (the web dashboard uses **Vite+**; it installs locally
  via npm, no global CLI needed)
- pnpm (the `web/` + `ui/` JavaScript workspace uses pnpm catalogs; `corepack enable`)
- Docker + Docker Compose (for the containerized stack)
- `make` (optional, for the shortcut targets)

## Quickstart

```bash
# 1. Install Python deps, web deps, git hooks, and .env
./scripts/bootstrap.sh
# or: make bootstrap

# 2. Validate the dataset and snapshot it to parquet
make prepare

# 3. Train the proposed Random Forest (writes models/model.joblib)
make train

# 4. Run the API and the dashboard
make dev            # api on :8000, web on :5173
```

Open the API docs at http://localhost:8000/docs and the dashboard at
http://localhost:5173.

## Command reference

### Environment and quality

| Command | What it does |
| --- | --- |
| `make bootstrap` | Install Python + web dependencies, pre-commit hooks, and `.env` |
| `make sync` | Refresh the uv-managed Python environment |
| `make lint` | ruff check, ruff format --check, mypy, web check (Vite+: oxfmt + oxlint + tsc) |
| `make format` | Reformat the Python tree with ruff |
| `make type` | mypy over `analytics`, `api`, `eval` |
| `make test` | pytest with coverage |
| `make clean` | Remove caches and build artifacts |

### Data and models

| Command | What it does |
| --- | --- |
| `make prepare` | Validate the raw CSV and write `data/processed/learners.parquet` |
| `make train` | Train the Random Forest and export artifact + metadata + SHAP |
| `make train ARGS='--all'` | Train the full comparison matrix |
| `make train ARGS='--models svc knn'` | Train specific models |
| `make train ARGS='--tune'` | Tune before fitting |
| `uv run python -m analytics.train --list` | List every available model |
| `uv run dvc repro` | Reproduce data + model from a clean checkout |

### Services

| Command | What it does |
| --- | --- |
| `make api` | FastAPI with autoreload on http://localhost:8000 |
| `make web` | Vite+ dev server (`vp dev`) on http://localhost:5173 |
| `make dev` | Both at once |
| `make ui-install` | Install the JS workspace dependencies (web + ui) with pnpm |
| `make storybook` | Storybook for the component library on http://localhost:6006 |
| `make storybook-build` | Build the static Storybook |
| `./scripts/run-api.sh` | Same as `make api` (respects `PORT`) |

### Docker

| Command | What it does |
| --- | --- |
| `make docker-up` | Build and start api, web, postgres, and mlflow |
| `make docker-down` | Stop the stack |
| `make docker-logs` | Tail the stack logs |

The containerized stack exposes the API on `:8000`, the dashboard on `:8080`,
PostgreSQL on `:5432`, and MLflow on `:5000`.

## Component library and Storybook

`ui/` is a shadcn/ui design system (Base UI + Tailwind v4) with a Storybook
story for every component. Edit components there and preview them live.

```bash
make ui-install        # pnpm install in ui/
make storybook         # Storybook on http://localhost:6006
make storybook-build   # static site in ui/storybook-static
```

Storybook includes autodocs, an accessibility panel, and light/dark theme
switching. The dashboard in `web/` consumes this library directly, so the two
share one design system. See [`ui/README.md`](ui/README.md) for details.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Service banner and endpoint list |
| `GET` | `/health` | Liveness and model-loaded status |
| `GET` | `/docs` | OpenAPI (Swagger) documentation |
| `POST` | `/predict` | Predict a tier for one learner |
| `POST` | `/predict/batch` | Vectorized tier prediction |
| `GET` | `/metrics` | Active model metrics (503 until trained) |
| `GET` | `/importance` | Native + SHAP importance (503 until trained) |
| `GET` | `/trends` | Class counts and behaviour by tier |

The service starts even without a trained model; prediction and metrics routes
return `503` with a clear message until `make train` has been run.

## Repository layout

```
analytics/  config, schema, data IO, model catalog, train, tune, evaluate, explain
api/        FastAPI app, routes, schemas, model store
eval/       SUS, effect sizes, longitudinal T0/T1/T2 protocol
ui/         shadcn/ui component library + Storybook (design system)
web/        React dashboard built on the ui library (Vite+)
data/       raw and processed datasets (DVC-tracked)
models/     serialized pipelines and metadata sidecars
docs/       technical specification, paper tooling, generated figures
scripts/    bootstrap and run helpers
tests/      Python test suite
notebooks/  exploratory analysis
```

## Stack

- **Data:** pandas, pandera, SQLAlchemy, DVC
- **Analytics:** scikit-learn, XGBoost, LightGBM, CatBoost, Optuna, SHAP
- **Tracking:** MLflow, DVC
- **Service:** FastAPI, Pydantic, uvicorn, gunicorn
- **Frontend:** React, Vite+ (Vite 8 + Rolldown + Oxc), TypeScript, TanStack Query
- **Design system:** shadcn/ui (Base UI + Tailwind v4) with Storybook; charts via the ui chart component (Recharts)
- **Evaluation:** scikit-learn metrics, pingouin, scipy (see the GPL-3 note in the spec)

## Documentation

| Document | Description |
| --- | --- |
| `docs/SEB-XRIF_Technical_Specification.pdf` | Stack, rationale, alternatives, build plan |
| `analytics/README.md` | Model catalog and training pipeline |
| `api/README.md` | Service configuration and endpoints |
| `eval/README.md` | Evaluation protocol |
| `web/README.md` | Dashboard structure, Vite+ toolchain, UI-kit swap |
| `ui/README.md` | Component library and Storybook |

## Data

`data/raw/xAPI-Edu-Data.csv` — the xAPI Educational Mining Dataset (Kalboard
360), 480 records, 127 Low / 211 Medium / 142 High, CC BY-SA 4.0.

## License

Code is released under the MIT License (see [`LICENSE`](LICENSE)). The bundled
dataset retains its CC BY-SA 4.0 license. Note that `pingouin` is GPL-3.0; a
`scipy` fallback is provided in `eval/effect_size.py` for redistribution.
