.PHONY: help sync lint format type test api web figures clean

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

sync:  ## Create or refresh the uv-managed environment
	uv sync

lint:  ## Lint the source tree
	uv run ruff check .

format:  ## Format the source tree
	uv run ruff format .

type:  ## Run static type checks
	uv run mypy analytics api eval

test:  ## Run the test suite
	uv run pytest --cov=analytics --cov=api --cov=eval

api:  ## Run the FastAPI service with reload
	uv run uvicorn api.main:app --reload

figures:  ## Regenerate the paper figures
	cd docs/figures && uv run python src/make_fig1_methods.py && \
		uv run python src/make_fig_lit_methods.py && \
		uv run python src/sebxrif_figs.py

clean:  ## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
