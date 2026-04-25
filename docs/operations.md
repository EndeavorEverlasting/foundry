# Operations runbook

## First-time bootstrap

```powershell
# Windows
./scripts/bootstrap.ps1
```

```bash
# macOS / Linux
./scripts/bootstrap.sh
```

This installs dependencies (pnpm + uv), brings up Postgres + Redis, and runs
the initial Alembic migration.

If `pnpm` or `uv` is missing in your shell:

- `pnpm`: install via Node Corepack (`corepack enable` then `corepack prepare pnpm@latest --activate`) or `npm i -g pnpm`.
- `uv`: install from Astral and ensure its bin path is on `PATH` for your shell session.
- On Windows, restart the terminal after install so PATH shims are loaded.

Bring up the full stack:

```bash
docker compose -f infra/compose/docker-compose.yml up -d
```

Services:

| Name | Port | Purpose |
| --- | --- | --- |
| `postgres` | 5432 | Primary store |
| `redis` | 6379 | Arq queue + cache |
| `api` | 8000 | FastAPI |
| `worker` | — | Arq worker (no HTTP port) |
| `web` | 5173 | Vite dev server for BranchFoundry UI |

## Resetting local state

```powershell
./scripts/reset.ps1
```

Drops containers and volumes (Postgres data, Redis data, cloned repos).

## Logs

All services emit structured logs via `structlog`. Useful filters:

```bash
docker compose logs -f worker | grep branch_sync
docker compose logs -f api    | grep /repos/
```

## Backups

- **Postgres**: dump the `foundry` database. Typical cadence: nightly.
  ```bash
  docker compose exec postgres pg_dump -U foundry foundry > foundry.sql
  ```
- **Repos**: the `repos` volume is a cache — rebuildable from origin, so
  backups are optional.
- **Redis**: queues are ephemeral; no backup required.

## Migrations

```bash
# create a new migration
docker compose exec api alembic revision -m "describe change" --autogenerate

# apply migrations
docker compose exec api alembic upgrade head
```

## Common failure modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| API `/readyz` 503 | DB or Redis unreachable | `docker compose ps`, check networks |
| `branch_sync` stuck in queue | Worker down | `docker compose restart worker` |
| "Repository not found" on sync | Git auth or bad URL | Update repo URL via API; check deploy key |
| Stale data in UI | Sync not yet run | `POST /repos/{id}/sync` |
| Migration conflict | Two branches added migrations | Rebase, renumber, re-run autogenerate |

## Release readiness ownership and fallback

Foundry is the primary control plane for release checks via `/api/v1/release/*`
and the BranchFoundry “Release readiness” UI.

Recommended adoption mode for integrated apps (e.g. AxTask):

1. Keep app-local scripts as fallback in the first rollout window.
2. Run Foundry release checks before PR/deploy decisions.
3. Reduce app-local fallback after a confidence window once Foundry checks are stable.

### Divergence handling workflow

When BranchFoundry shows a repo as diverged or high-risk:

1. Fetch and measure drift:
   - `git fetch origin`
   - `git rev-list --left-right --count origin/main...HEAD`
2. Run a release readiness check first:
   - `POST /api/v1/release/check/{repo_id}` (or from the UI)
   - Review findings by severity before touching deploy settings.
3. Reconcile branch history:
   - Merge `origin/main` into the working branch.
   - Resolve conflicts, then rerun release check.
4. Decide action from evidence:
   - Pass with no high findings: continue PR/deploy flow.
   - High findings on schema/env/routes: hold deploy and fix evidence gaps first.
5. Fallback rule for integrated apps (AxTask model):
   - If Foundry is degraded/unavailable, use app-local `release:check` and manual PR gates.
   - Record fallback usage in release notes for auditability.

## Upgrades

1. Pull latest code.
2. `pnpm install` and `uv sync --all-packages`.
3. `docker compose build`.
4. `docker compose up -d`.
5. `docker compose exec api alembic upgrade head`.
6. Smoke-test: `/healthz`, a repo sync, dashboard load.

## Observability

- Structured logs land in container stdout.
- OpenTelemetry hooks are in place for `api` and `worker` and emit to stdout
  by default. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to forward spans.

## Security posture (v1)

- No auth on API — **do not expose the API to the public internet** in v1.
  Put it behind your VPN or keep it localhost-only.
- Postgres credentials live in `.env`. Don't commit your populated `.env`.
- Cloned repos are written to a named Docker volume; treat that volume as
  sensitive.
