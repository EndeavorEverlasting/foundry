#!/usr/bin/env bash
# Foundry bootstrap (POSIX)
# Idempotent: safe to run repeatedly.

set -euo pipefail

say() { printf "\033[36m==>\033[0m %s\n" "$*"; }
ok()  { printf "  \033[32m[ok]\033[0m %s\n" "$*"; }
die() { printf "\033[31mERROR:\033[0m %s\n" "$*" >&2; exit 1; }

require() {
  local name=$1 hint=$2
  command -v "$name" >/dev/null 2>&1 || die "Missing tool: $name. $hint"
  ok "$name"
}

say "Foundry bootstrap (POSIX)"
require node   "Install Node 20+ (https://nodejs.org/)"
require pnpm   "Install pnpm: 'corepack enable && corepack prepare pnpm@9 --activate'"
require uv     "Install uv: 'curl -LsSf https://astral.sh/uv/install.sh | sh'"
require docker "Install Docker"
require git    "Install Git"

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if [[ ! -f .env ]]; then
  say "Creating .env from .env.example"
  cp .env.example .env
fi

say "Installing JS dependencies (pnpm install)"
pnpm install

say "Installing Python dependencies (uv sync)"
uv sync

say "Starting Postgres + Redis"
docker compose -f infra/compose/docker-compose.yml up -d postgres redis

say "Waiting for Postgres to be healthy..."
for _ in $(seq 1 30); do
  if docker compose -f infra/compose/docker-compose.yml exec -T postgres pg_isready -U foundry -d foundry >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

say "Running DB migrations"
uv run --package foundry-api alembic -c infra/migrations/alembic.ini upgrade head

printf "\n\033[32mDone.\033[0m Next steps:\n"
printf "  pnpm compose:up     # bring up api + worker + web\n"
printf "  pnpm dev            # run web locally against containerized api\n"
