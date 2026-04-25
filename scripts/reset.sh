#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
docker compose -f infra/compose/docker-compose.yml down -v
printf "\033[33mFoundry local state wiped.\033[0m\n"
