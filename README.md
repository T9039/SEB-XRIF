# SEB-XRIF

**Scalable, Evidence-Based XR Integration Framework** — a reusable, reproducible
way of conducting XR education research. This repository holds the data,
analytics, service, visualization, and evaluation layers of the framework.

Team 3 · PRJT302 · Information Technology, Durban University of Technology.

## What this is

SEB-XRIF is not a single model or dashboard. It is a standard recipe: any
institution exports learning data in the xAPI schema, runs the same pipeline with
the same seed and configuration, and reports the same evaluation instruments
(accuracy/F1 with cross-validation, SUS, and Cohen's d over T0/T1/T2). The data
contract and the evaluation protocol transfer; the **target does not transfer by
itself** — each source defines its own features and outcome. Here the Kalboard
LMS seed trains the supervised academic support-band model, while the ARETE XR
pilots have a derived engagement/drop-off risk model, on the same ingest and
reporting machinery. The Random Forest and the dashboard are the first
instantiation of the framework, not the framework itself.

| Layer | Purpose | Module |
| --- | --- | --- |
| Data | Validated, versioned xAPI-schema data; ARETE XR pilots | `analytics/data.py`, `analytics/schema.py`, `analytics/xr.py` |
| Analytics | Compare 16 models; predict a support band (LMS) and an XR risk band; rank drivers | `analytics/` |
| Service | Prediction and analytics REST API | `api/` |
| Visualization | Tabbed dashboard with a persistent data-source selector (LMS / XR pilots) | `web/` |
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
| `make repro-check` | Reproduce from a clean checkout and verify the DVC graph |
| `make fetch-arete` | Download the ARETE XR xAPI pilots (checksum-verified) |
| `make train` | Train the Random Forest and export artifact + metadata + SHAP |
| `make train ARGS='--all'` | Train the full comparison matrix |
| `make train ARGS='--models svc knn'` | Train specific models |
| `make train ARGS='--tune'` | Tune before fitting |
| `make matrix` | Run the full 16-model comparison matrix (single-threaded) |
| `make tune ARGS='--trials 20'` | Tune the top models with Optuna |
| `make mlflow` | Open the MLflow UI on http://localhost:5000 |
| `make figures` | Regenerate the documentation figures |
| `make eval-report ARGS='--input pilot.json --store --source pilot'` | Build and store an evaluation report |
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
| `make docker-up` | Build and start api, web, postgres, lrsql, and mlflow |
| `make docker-down` | Stop the stack |
| `make docker-logs` | Tail the stack logs |

The containerized stack exposes the API on `:8000`, the dashboard on `:8080`,
PostgreSQL on `:5432`, the Learning Record Store on `:8081`, and MLflow on
`:5000`.

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
| `GET` | `/version` | App, model, and runtime versions |
| `GET` | `/docs` | OpenAPI (Swagger) documentation |
| `POST` | `/predict` | Predict a support band for one learner |
| `POST` | `/predict/batch` | Vectorized support-band prediction |
| `GET` | `/metrics` | Active model metrics (503 until trained) |
| `GET` | `/importance` | Native + SHAP importance (503 until trained) |
| `GET` | `/trends` | Class counts and behaviour by band |
| `GET` | `/learners` | Paged learner table |
| `GET` | `/options` | Categorical option sets |
| `GET` | `/results` | Model comparison matrix + tuning/explain/evaluation |
| `GET` | `/model/diagnostics` | ROC, PR, calibration, ECE, learning curves |
| `GET` | `/analytics/columns` | Queryable columns for Chart Studio |
| `POST` | `/analytics/query` | Server-side aggregation query |
| `GET` | `/analytics/correlation` | Correlation matrix |
| `GET` | `/analytics/distribution` | Feature distribution |
| `GET` | `/analytics/embedding` | PCA embedding and clusters |
| `GET` | `/model/pdp` | Partial dependence for a feature |
| `GET` | `/charts` | Saved Chart Studio views |
| `POST` | `/charts` | Save a Chart Studio view |
| `DELETE` | `/charts/{name}` | Delete a Chart Studio view |
| `GET` | `/xr/pilots` | Known ARETE XR pilots and whether downloaded |
| `GET` | `/xr/trends` | Engagement over time for an XR pilot |
| `GET` | `/xr/risk` | Early-warning engagement/risk bands for a pilot |
| `GET` | `/xr/learners` | Paged per-learner XR engagement features |
| `GET` | `/evaluation` | Longitudinal SUS + T0/T1/T2 summary from the store |

The service starts even without a trained model; prediction and metrics routes
return `503` with a clear message until `make train` has been run.

## Repository layout

```
analytics/  config, schema, data IO, adapters, model catalog, train, tune,
            evaluate, explain, decision, xr, diagnostics
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

## Remote access (Tailscale)

The dev servers bind to all interfaces, so they are reachable over the tailnet
using this machine's Tailscale address (find it with `tailscale ip -4`):

| Service | Local | Over Tailscale |
| --- | --- | --- |
| Dashboard | http://localhost:5173 | http://\<tailscale-ip\>:5173 |
| API docs | http://localhost:8000/docs | http://\<tailscale-ip\>:8000/docs |
| Storybook | http://localhost:6006 | http://\<tailscale-ip\>:6006 |

If a host firewall blocks inbound, allow the Tailscale interface once:

```bash
sudo ufw allow in on tailscale0
```

Or keep the firewall closed and use Tailscale Serve (set the operator once to
avoid sudo for every command):

```bash
sudo tailscale set --operator=$USER
tailscale serve --bg --yes --http=5173 http://localhost:5173
tailscale serve --bg --yes --http=8000 http://localhost:8000
tailscale serve --bg --yes --http=6006 http://localhost:6006
```

## Continuous integration

GitHub Actions runs on every push and pull request (`.github/workflows/ci.yml`):

- **python** — `uv sync`, ruff, mypy, Alembic against a Postgres service, pytest, clean-checkout reproduction check
- **web** — pnpm install, `vp check`, vitest, `vp build`
- **ui** — static Storybook build
- **docker** — builds the API and web images (with layer caching)
- **paper** — compiles the Typst paper and uploads the PDF as an artifact

Recommended repository setting: protect `main` and require these jobs to pass.
Developer tools run behind a Compose profile: `docker compose --profile tools up storybook` (or `mlflow`).

## Documentation

| Document | Description |
| --- | --- |
| `docs/SEB-XRIF_Technical_Specification.pdf` | Stack, rationale, alternatives, build plan |
| `docs/reproducibility.md` | What is pinned and how to reproduce from a clean checkout |
| `docs/datasets.md` | Bundled seed, ARETE XR pilots, and the LMS-to-XR feature mapping |
| `analytics/README.md` | Model catalog and training pipeline |
| `api/README.md` | Service configuration and endpoints |
| `eval/README.md` | Evaluation protocol |
| `web/README.md` | Dashboard structure, Vite+ toolchain, UI-kit swap |
| `ui/README.md` | Component library and Storybook |

## Data

`data/raw/xAPI-Edu-Data.csv` — the xAPI Educational Mining Dataset (Kalboard
360), 480 records, 127 Low / 211 Medium / 142 High, CC BY-SA 4.0. It is K-12 LMS
data and is **not XR**; it prototypes the analytics layer. The model's
Low/Medium/High classes are reported as support bands (priority-support, monitor,
on-track).

The XR side uses the **ARETE** augmented-reality xAPI pilots (five files across
four pilots, CC BY 4.0), downloaded with `make fetch-arete` and served through the
same pipeline: per-learner engagement features (`/xr/learners`), engagement
trends (`/xr/trends`), and an early-warning drop-off risk model (`/xr/risk`).
Every source defines its own target — the academic band for Kalboard, drop-off
risk for ARETE — which is why the data-source selector changes the model and
panels, not just the data. See [`docs/datasets.md`](docs/datasets.md).

## License

Code is released under the MIT License (see [`LICENSE`](LICENSE)). The bundled
dataset retains its CC BY-SA 4.0 license. Note that `pingouin` is GPL-3.0; a
`scipy` fallback is provided in `eval/effect_size.py` for redistribution.
