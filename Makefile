# SEB-XRIF developer commands.
#
# Requires GNU make (on Windows: `choco install make`, `scoop install make`, or
# MSYS2's `make`). Every recipe is a Python or pnpm/docker command, so the same
# targets run on Windows, Linux, and macOS with no Git Bash required.
.RECIPEPREFIX = >

.PHONY: help bootstrap sync lint format type test api web dev up stop teardown \
        train prepare matrix tune paper eval-report mlflow db-upgrade db-init \
        repro-check check-xapi flatten-xapi fetch-arete docker-up docker-down \
        docker-logs figures clean ui-install storybook storybook-build

help:
> @echo "SEB-XRIF targets:"
> @echo "  up           ONE COMMAND: install if needed, train if needed, run api + dashboard"
> @echo "  bootstrap    install Python + web dependencies, hooks, and .env"
> @echo "  sync         refresh the uv-managed Python environment"
> @echo "  lint         ruff + mypy (+ web typecheck)"
> @echo "  format       ruff format the Python tree"
> @echo "  type         mypy static checks"
> @echo "  test         pytest with coverage"
> @echo "  prepare      validate and snapshot the dataset"
> @echo "  train        train models (ARGS='--all')"
> @echo "  matrix       run the full 16-model comparison matrix (single-threaded)"
> @echo "  tune         tune the top models with Optuna (ARGS='--trials 20')"
> @echo "  repro-check  reproduce from a clean checkout and verify the DVC graph"
> @echo "  check-xapi   check a statements file against the xAPI profile (ARGS='file.jsonl')"
> @echo "  flatten-xapi flatten any statements file to a CSV table (ARGS='file.jsonl')"
> @echo "  fetch-arete  download the ARETE XR pilots (ARGS='pbis')"
> @echo "  mlflow       open the MLflow UI on :5000"
> @echo "  db-upgrade   apply database migrations (alembic upgrade head)"
> @echo "  db-init      create tables directly (development convenience)"
> @echo "  paper        build the paper PDF (Markdown -> Typst)"
> @echo "  eval-report  build the SUS/Cohen's d/T0-T2 report (ARGS='--input pilot.json')"
> @echo "  api          run FastAPI on :8000"
> @echo "  web          run Vite dev server on :5173"
> @echo "  dev          run api and web together"
> @echo "  ui-install   install the JS workspace deps (web + ui) with pnpm"
> @echo "  storybook    run Storybook for the ui library on :6006"
> @echo "  storybook-build  build the static Storybook"
> @echo "  stop         stop dev servers, Docker stacks and the Funnel (keeps data)"
> @echo "  teardown     remove all services, volumes, generated files AND the repo"
> @echo "  docker-up    build and start the full stack"
> @echo "  docker-down  stop the stack"
> @echo "  figures      regenerate the paper figures"
> @echo "  clean        remove caches and build artifacts"

bootstrap:
> @uv run python scripts/bootstrap.py

sync:
> uv sync

lint:
> @uv run python scripts/lint.py

format:
> uv run ruff format .

type:
> uv run mypy analytics api eval

test:
> @uv run python scripts/test.py $(ARGS)

prepare:
> uv run python -m analytics.data

repro-check:
> @uv run python scripts/repro_check.py

check-xapi:
> uv run python -m analytics.xapi check --path $(ARGS)

flatten-xapi:
> uv run python -m analytics.xapi flatten --path $(ARGS) --out $(basename $(ARGS)).csv

fetch-arete:
> uv run python scripts/fetch_arete.py $(ARGS)

train:
> @uv run python scripts/train.py $(if $(SOURCE),--source $(SOURCE),) $(ARGS)

matrix:
> @uv run python scripts/matrix.py $(ARGS)

tune:
> @uv run python scripts/tune.py $(ARGS)

mlflow:
> uv run mlflow ui --host 0.0.0.0 --port 5000

db-upgrade:
> uv run alembic upgrade head

db-init:
> uv run python -m analytics.db init

paper:
> @uv run python paper/build.py

eval-report:
> uv run python -m eval.report $(ARGS)

api:
> @uv run python scripts/run_api.py

web:
> @uv run python scripts/run_web.py

dev:
> @uv run python scripts/run.py --no-train

up:
> @uv run python scripts/run.py $(ARGS)

stop:
> @uv run python scripts/stop.py $(ARGS)

teardown:
> @uv run python scripts/teardown.py $(ARGS)

ui-install:
> pnpm install

storybook:
> @uv run python scripts/storybook.py $(ARGS)

storybook-build:
> pnpm --dir ui run build-storybook

docker-up:
> docker compose up --build $(ARGS)

docker-down:
> docker compose down

docker-logs:
> docker compose logs -f

figures:
> @uv run python scripts/figures.py

clean:
> @uv run python scripts/clean.py
