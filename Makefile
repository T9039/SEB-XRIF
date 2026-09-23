# SEB-XRIF developer commands.
.RECIPEPREFIX = >
SHELL := /bin/bash

.PHONY: help bootstrap sync lint format type test api web dev train prepare \
        matrix tune paper mlflow db-upgrade db-init \
        docker-up docker-down docker-logs figures clean \
        ui-install storybook storybook-build

help:
> @echo "SEB-XRIF targets:"
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
> @echo "  docker-up    build and start the full stack"
> @echo "  docker-down  stop the stack"
> @echo "  figures      regenerate the paper figures"
> @echo "  clean        remove caches and build artifacts"

bootstrap:
> @./scripts/bootstrap.sh

sync:
> uv sync

lint:
> @./scripts/lint.sh

format:
> uv run ruff format .

type:
> uv run mypy analytics api eval

test:
> @./scripts/test.sh

prepare:
> uv run python -m analytics.data

train:
> @./scripts/train.sh $(ARGS)

matrix:
> @./scripts/matrix.sh $(ARGS)

tune:
> OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
>   uv run python -m analytics.tune $(ARGS)

mlflow:
> uv run mlflow ui --host 0.0.0.0 --port 5000

db-upgrade:
> uv run alembic upgrade head

db-init:
> uv run python -m analytics.db init

paper:
> @./paper/build.sh

eval-report:
> uv run python -m eval.report $(ARGS)

api:
> @./scripts/run-api.sh

web:
> @./scripts/run-web.sh

dev:
> @./scripts/dev.sh

ui-install:
> pnpm install

storybook:
> @./scripts/storybook.sh $(ARGS)

storybook-build:
> cd ui && pnpm build-storybook

docker-up:
> @./scripts/docker-up.sh

docker-down:
> @./scripts/docker-down.sh

docker-logs:
> docker compose logs -f

figures:
> cd docs/figures && uv run python src/make_fig1_methods.py \
>   && uv run python src/make_fig_lit_methods.py \
>   && uv run python src/sebxrif_figs.py

clean:
> find . -type d -name __pycache__ -prune -exec rm -rf {} +
> rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
