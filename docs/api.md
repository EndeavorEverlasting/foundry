# API reference (v1 stub)

Base URL: `/api/v1`. All endpoints return JSON. Auth model is currently
**none** (trusted local/dev deployment); bearer-token auth lands in the next
phase — the `User`/`Team` tables are already in place.

## Health

| Method | Path | Description |
| --- | --- | --- |
| GET | `/healthz` | Liveness |
| GET | `/readyz` | DB + Redis readiness |
| GET | `/version` | Build + git sha |

## Repositories

| Method | Path | Description |
| --- | --- | --- |
| GET | `/repos` | List registered repositories |
| POST | `/repos` | Register a repo (`url`, `provider`, `default_branch`) |
| GET | `/repos/{id}` | Repo detail + summary strip |
| POST | `/repos/{id}/sync` | Enqueue a branch sync |
| POST | `/repos/{id}/manifest` | Upload `foundry.manifest.json` |

## Branches

| Method | Path | Description |
| --- | --- | --- |
| GET | `/repos/{id}/branches` | List branches (filterable: state, stale, ready) |
| GET | `/repos/{id}/branches/{branch}` | Branch detail, summary, evidence, PRs |

## Views

| Method | Path | Description |
| --- | --- | --- |
| GET | `/repos/{id}/graph` | React Flow graph (server-side laning) |
| GET | `/repos/{id}/drift` | "What main is missing / behind" panel |
| GET | `/repos/{id}/stale` | Stale bucket view |
| GET | `/repos/{id}/actions` | Action center rows |

## Release readiness

| Method | Path | Description |
| --- | --- | --- |
| POST | `/release/check/{repo_id}` | Run release policy checks against a repo local path + branch |
| GET | `/release/runs/{run_id}` | Fetch release run details and findings |
| GET | `/release/profiles/{repo_id}` | Fetch repo release profile (auto-created with defaults) |
| PUT | `/release/profiles/{repo_id}` | Update repo release profile spec and enabled state |
| POST | `/release/deploy/preview/{repo_id}` | Generate preview deploy action plan (dry-run by default) |
| POST | `/release/deploy/promote/{repo_id}` | Generate/execute promote action plan |
| POST | `/release/deploy/rollback/{repo_id}` | Generate/execute rollback action plan |

## OpenAPI

FastAPI serves the generated OpenAPI doc at `/openapi.json` and a Swagger UI at
`/docs`. The web app consumes it via an auto-generated TypeScript client.

Regenerate the client from the repo root:

```bash
pnpm gen-client
```

## Error shape

All errors use the following JSON shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable message",
    "details": { "field": "..." }
  }
}
```
