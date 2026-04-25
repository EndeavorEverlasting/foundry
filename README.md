# Foundry

> A platform for branch intelligence, engineering visibility, and app-aware security.

Foundry is the umbrella for a family of modular products:

| Product | Purpose |
| --- | --- |
| **BranchFoundry** | Branch intelligence, Git analytics, engineering visibility |
| **GuardFoundry** | App-aware security scanning and policy enforcement |
| **FoundryHooks** | Integration SDK for host apps (manifests, events, annotations) |
| **FoundryScan** | Background scanning / analysis engine |
| **FoundryPolicy** | Policy engine for enforcement and governance |

This repository is a **polyglot monorepo** (Python + TypeScript) managed with **pnpm workspaces + Turborepo** for JS/TS and **uv workspaces** for Python.

---

## Quick start

Prereqs: Node 20+, pnpm 9+, Python 3.11+, [uv](https://docs.astral.sh/uv/), Docker Desktop.

```bash
# 1. Install JS deps
pnpm install

# 2. Install Python deps
uv sync

# 3. Copy env template
cp .env.example .env

# 4. Bring up Postgres + Redis + API + worker + web
pnpm compose:up

# 5. Run DB migrations
docker compose -f infra/compose/docker-compose.yml exec api alembic upgrade head

# 6. Seed AxTask as the first integrated repo (optional)
docker compose -f infra/compose/docker-compose.yml exec api python -m scripts.seed_axtask
```

Then visit:

- Web: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

On Windows PowerShell, substitute `cp` with `Copy-Item`. The `scripts/bootstrap.ps1` helper wraps the above.

---

## Layout

```
apps/                     # Deployable services
  foundry-api/            # FastAPI REST service
  foundry-worker/         # Arq async worker
  branchfoundry-web/      # React + Vite UI (BranchFoundry)
  guardfoundry-web/       # Shell placeholder (v1 non-goal)
packages/                 # Shared libraries
  foundry-core/           # Python: shared schemas, evidence model, enums
  foundry-git/            # Python: Git ingestion + branch math
  foundry-analysis/       # Python: drift, stale, summary, capabilities
  foundry-hooks-sdk/      # Python + TS: manifest spec + loaders
  foundry-policy/         # Python: stub
  foundry-security/       # Python: stub
  foundry-ui/             # TS: shared React primitives + generated API client
infra/                    # Deployment assets
  docker/                 # Dockerfiles
  compose/                # docker-compose.yml
  migrations/             # Alembic env + versions
  ci/                     # GitHub Actions
docs/                     # Architecture, API, hooks, operations docs
examples/                 # AxTask integration, demo repo
scripts/                  # Bootstrap, seed, reset helpers
```

See [docs/architecture/overview.md](docs/architecture/overview.md) for a deeper dive, and [foundry_product_blueprint.md](foundry_product_blueprint.md) for the full product vision.

---

## Common tasks

| Command | What it does |
| --- | --- |
| `pnpm dev` | Run all JS/TS dev servers |
| `pnpm build` | Build all JS/TS packages |
| `pnpm lint` | Lint JS/TS |
| `pnpm typecheck` | TS type-check |
| `pnpm test` | JS/TS tests |
| `pnpm py:lint` | Ruff lint (Python) |
| `pnpm py:format` | Ruff format (Python) |
| `pnpm py:typecheck` | mypy (Python) |
| `pnpm py:test` | pytest (Python) |
| `pnpm compose:up` | Start Docker stack |
| `pnpm compose:down` | Stop Docker stack |
| `pnpm compose:logs` | Tail Docker logs |

---

## Status

BranchFoundry v1 is under active development. GuardFoundry v1 lands in a later phase. See [foundry_product_blueprint.md](foundry_product_blueprint.md) §20 for the build order.
