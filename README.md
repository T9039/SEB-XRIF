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

## Quickstart

One command: it installs what is missing, trains the default model if none
exists, and starts the dashboard and API together.

```bash
git clone https://github.com/T9039/SEB-XRIF.git    # HTTPS
# or, with SSH: git clone git@github.com:T9039/SEB-XRIF.git
cd SEB-XRIF
make up            # or: python3 scripts/run.py
```

Then open:

- **Dashboard:** http://localhost:5173
- **API docs:** http://localhost:8000/docs

It runs in the foreground and keeps serving until you press `Ctrl+C` (it waits
for the API to be ready before opening the dashboard, so the first page load
does not fail). Add `--detach` to start it in the background and return to your
shell, then stop it with `make stop`:

```bash
make up ARGS='--detach'   # or: python3 scripts/run.py --detach
```

It is idempotent — re-running it is safe.

> Windows: run `python scripts\run.py` instead (details in
> [Windows setup](#windows-setup)).

### Doing it by hand

```bash
./scripts/bootstrap.sh   # install Python + web deps, hooks, and .env
make train               # train the default Random Forest (writes models/model.joblib)
make dev                 # api on :8000, web on :5173 (no training step)
```

`make prepare` (validate the CSV to parquet) is optional and not needed to run
the dashboard.

## Prerequisites

Everything below is required unless marked optional.

- [`uv`](https://docs.astral.sh/uv/) — installs and manages Python 3.12 for you.
- **Node.js 20+** — includes `npm` and `corepack`.
- **pnpm** — enable with `corepack enable`, or `npm install -g pnpm`.
- **Git** — to clone the repository.
- `make` — recommended (the shortcut targets). Optional on Windows.
- Docker + Docker Compose — only for the containerized stack (`make docker-up`).

### Windows setup

The single-command startup is Python, so it runs natively on Windows. The other
`make` targets are POSIX shell; use **Git Bash** (bundled with Git for Windows)
for those.

1. **Install Git for Windows** — https://git-scm.com/download/win (includes Git Bash).
2. **Install `uv`** — in PowerShell:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Install Node.js 20+** — https://nodejs.org (LTS installer).
4. **Enable pnpm** — in PowerShell or Git Bash:
   ```bash
   corepack enable
   ```
5. **Clone and run** — in `cmd.exe` or PowerShell:
   ```bat
   git clone https://github.com/T9039/SEB-XRIF.git
   REM or, with SSH: git clone git@github.com:T9039/SEB-XRIF.git
   cd SEB-XRIF
   python scripts\run.py
   ```

`scripts\run.py` installs what is missing, trains the default model if needed,
and starts the API and dashboard. For the other `make` targets, open Git Bash
and run them there.

> Docker on Windows uses Docker Desktop with the WSL 2 backend; it is only needed
> for `make docker-up`, not for the single-command path above.

### Linux / macOS

Install `uv`, Node, and pnpm by any means, then run `make up` (or
`python3 scripts/run.py`). `make` is available by default on macOS and most
Linux distributions.


## For beta testers

Thanks for trying SEB-XRIF. The goal is to find faults and annoyances, so please
be blunt. New to the system? Open the **Guide** tab in the dashboard — it is a
plain-language walkthrough (what each tab is for, the data it accepts, the
measures it enforces, and the limits). For the developer reference see
[`docs/instructions.md`](docs/instructions.md). Then set it up with `make up` (or
`python scripts\run.py` on Windows) and work through the dashboard tabs.

**What to try**

1. **Overview / Data / Diagnostics** — the seeded Kalboard (LMS) data and model.
   Check the numbers look sane and the tables sort/search.
2. **Predict** — fill the form and predict a support band. Try leaving fields at
   their defaults and changing a few.
3. **Explore** — switch the header **Data source** to an ARETE XR pilot and see
   the engagement trends, the early-warning risk panel, and the LMS→XR mapping.
4. **Datasets** — register your own data:
   - a **profile-conformant xAPI statements** file (`.jsonl`) — accepted and trainable;
   - a **table** (`.csv`) — pick the target column and adapt it;
   - a **foreign xAPI** file — use **Flatten to CSV**, then upload the result.
   Use **Check** on any file first; it tells you what the system sees.
5. **Theme** — toggle light/dark in the header (light is the default).

**Things that should fail gracefully (please check they do)**

- Uploading something that is not a dataset (empty file, random bytes, a `.csv`
  with no target column).
- A table whose target has one value per class (too small to train).
- Picking an XR pilot that has not been downloaded (`make fetch-arete`).
- Selecting a source with no trained model in **Predict**.

**Reporting an issue**

Please include: what you did, what you expected, what happened, and any browser
console errors (F12 → Console), plus your OS. If a panel shows an error message,
copy it verbatim.

## Hosted beta (deployment)

A hosted instance can be stood up on any machine with Docker, `tailscale`, and
`openssl`. One idempotent command builds the serving stack and exposes it to the
internet through **Tailscale Funnel**:

```bash
./deploy/deploy.sh          # override the public port with FUNNEL_PORT=...
```

On first run it generates `deploy/.env` (Postgres and beta basic-auth password)
and `deploy/Caddyfile` (the bcrypt hash of that password) — both **gitignored**;
delete them to rotate the credentials. It then builds and starts
`deploy/docker-compose.yml` (`api` + `web` + `postgres`, fronted by `caddy` with
HTTP basic auth), waits until the API reports a loaded model, and prints the
live URL, username, and password. MLflow and `lrsql` are deliberately omitted
from this stack (they are training / test-only).

Nothing is published to the host except Caddy, bound to `127.0.0.1`; Funnel is
the only path from the public internet and it reaches exactly one port.

```bash
# stop the public listener, then the stack (FUNNEL_PORT defaults to 8443)
tailscale funnel --https=8443 off
docker compose -f deploy/docker-compose.yml --env-file deploy/.env down
```

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
| `make check-xapi ARGS=file.jsonl` | Check a statements file against the xAPI profile |
| `make flatten-xapi ARGS=file.jsonl` | Flatten any statements file to a CSV table |
| `make fetch-arete` | Download the ARETE XR xAPI pilots (checksum-verified) |
| `make train` | Train the Random Forest and export artifact + metadata + SHAP |
| `make train SOURCE=<name>` | Train a specific source (uploaded or built-in) |
| `make train SOURCE=<name> ARGS='--matrix'` | Train the full matrix and promote the best model |
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
| `make up` | **One command:** install if needed, train if needed, run api + dashboard (`ARGS='--no-train'` to skip training) |
| `make api` | FastAPI with autoreload on http://localhost:8000 |
| `make web` | Vite+ dev server (`vp dev`) on http://localhost:5173 |
| `make dev` | Both at once (no training step) |
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

### Stop and teardown

Two Python scripts shut the project down. They are standard-library only, so
they run with a plain `python`/`python3` on Windows, Linux, and macOS (no Git
Bash required).

| Command | What it does |
| --- | --- |
| `python3 scripts/stop.py` | **Stop** the dev servers (API, dashboard, Storybook, MLflow), both Docker stacks, and the Tailscale Funnel. Keeps containers, volumes, and data. |
| `python3 scripts/teardown.py` | **Total teardown:** stop everything, remove the Docker stacks (containers, volumes, images), the Funnel, and every generated artifact (models, processed/uploaded/ARETE data, MLflow runs, caches, the local database, generated `.env` files and deploy secrets, `.venv`/`node_modules`), then delete the repository directory itself. |

`make stop` and `make teardown` are shortcuts. Both accept `--dry-run` to show
what would happen first. `teardown` asks for confirmation unless you pass `-y`;
`--keep-repo` deletes only the generated files and keeps the repository, and
`--keep-deps` leaves `.venv`/`node_modules` in place.

To reset a machine to a clean clone:

```bash
python3 scripts/teardown.py -y      # removes everything, including this repo
git clone https://github.com/T9039/SEB-XRIF.git    # HTTPS
# or, with SSH: git clone git@github.com:T9039/SEB-XRIF.git
cd SEB-XRIF
make up
```

On Windows:

```bat
python scripts\teardown.py -y
git clone https://github.com/T9039/SEB-XRIF.git
REM or, with SSH: git clone git@github.com:T9039/SEB-XRIF.git
cd SEB-XRIF
python scripts\run.py
```

HTTPS is fine for cloning (the repository is public), but pushing over HTTPS
needs a personal access token. If you push, use the SSH URL, or switch an
existing clone with:

```bash
git remote set-url origin git@github.com:T9039/SEB-XRIF.git
```

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
| `GET` | `/datasets` | Built-in and uploaded sources with trained status |
| `POST` | `/datasets` | Upload a statements file, or adapt a table with a mapping |
| `POST` | `/datasets/check` | Check conformance / adaptability before uploading |
| `POST` | `/datasets/flatten` | Flatten any xAPI statements file to a CSV table |
| `DELETE` | `/datasets/{name}` | Delete an uploaded source |
| `POST` | `/datasets/{name}/train` | Train a model for a source (one model or best-of-matrix) |
| `GET` | `/model/features` | Features and option sets a source's model expects |

`/predict`, `/predict/batch`, `/metrics`, `/importance` and `/model/diagnostics`
accept a `?source=` parameter (default `kalboard`) and serve that source's model.

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
deploy/     Tailscale Funnel + Caddy serving stack for the hosted beta
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
| [`docs/instructions.md`](docs/instructions.md) | **How to use it:** tabs, data schema, evaluation protocol, and limits |
| `docs/SEB-XRIF_Technical_Specification.pdf` | Stack, rationale, alternatives, build plan |
| `docs/reproducibility.md` | What is pinned and how to reproduce from a clean checkout |
| `docs/datasets.md` | Bundled seed, ARETE XR pilots, and the LMS-to-XR feature mapping |
| `docs/xapi_profile.md` | The xAPI profile, and how to check a dataset for conformance |
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

### Sources and adapters

A **dataset adapter** maps one source onto the canonical frame plus its feature
and target metadata (`analytics/datasets/`). Built-in adapters are code
(`kalboard`, `arete-*`); the generic `xapi-profile` adapter ingests any source
that exports the framework's xAPI profile as a statements file — a producer who
conforms needs no new code. A bespoke source (like ARETE) needs a small adapter
and a human-defined target. Uploaded sources live as `data/raw/uploads/<name>.jsonl`
plus a `<name>.json` sidecar (target, class labels, description) and are managed
from the **Datasets** tab or the `/datasets` API. See
[`docs/datasets.md`](docs/datasets.md).

## License

Code is released under the MIT License (see [`LICENSE`](LICENSE)). The bundled
dataset retains its CC BY-SA 4.0 license. Note that `pingouin` is GPL-3.0; a
`scipy` fallback is provided in `eval/effect_size.py` for redistribution.
