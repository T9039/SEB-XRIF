FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies first for layer caching.
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev || uv sync --no-dev

# Application code.
COPY . .

EXPOSE 8000

CMD ["gunicorn", "api.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000"]
