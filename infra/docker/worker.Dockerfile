FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv

WORKDIR /workspace

COPY pyproject.toml uv.lock* ./
COPY apps/foundry-api/pyproject.toml ./apps/foundry-api/
COPY apps/foundry-worker/pyproject.toml ./apps/foundry-worker/
COPY packages/foundry-core/pyproject.toml ./packages/foundry-core/
COPY packages/foundry-git/pyproject.toml ./packages/foundry-git/
COPY packages/foundry-analysis/pyproject.toml ./packages/foundry-analysis/
COPY packages/foundry-hooks-sdk/python/pyproject.toml ./packages/foundry-hooks-sdk/python/
COPY packages/foundry-policy/pyproject.toml ./packages/foundry-policy/
COPY packages/foundry-security/pyproject.toml ./packages/foundry-security/

COPY apps/foundry-api ./apps/foundry-api
COPY apps/foundry-worker ./apps/foundry-worker
COPY packages ./packages

RUN uv sync --frozen --no-dev || uv sync --no-dev

ENV PYTHONPATH="/workspace/apps/foundry-api/src:/workspace/apps/foundry-worker/src:/workspace/packages/foundry-core/src:/workspace/packages/foundry-git/src:/workspace/packages/foundry-analysis/src:/workspace/packages/foundry-hooks-sdk/python/src:/workspace/packages/foundry-policy/src:/workspace/packages/foundry-security/src"

RUN mkdir -p /var/lib/foundry/repos

CMD ["arq", "foundry_worker.main.WorkerSettings"]
