# Foundry architecture overview

Foundry is a **branch-intelligence + app-aware security** platform, designed so
each product (BranchFoundry, GuardFoundry, future) plugs into a shared core.

## Layered model

```
 ┌─────────────────────────── UI layer ───────────────────────────┐
 │  branchfoundry-web    guardfoundry-web   (future products)     │
 └────────────────────────────────┬───────────────────────────────┘
                                  │
 ┌──────────────── API layer (FastAPI, /api/v1) ──────────────────┐
 │  repos  branches  graph  drift  stale  actions  manifest       │
 └────────────────────────────────┬───────────────────────────────┘
                                  │
 ┌────────────────── Analysis + jobs layer ──────────────────────┐
 │  foundry-analysis (drift, stale, capabilities, summary,        │
 │                    readiness, EvidenceBundle)                  │
 │  foundry-worker (Arq) — branch_sync, summary_regen             │
 └────────────────────────────────┬───────────────────────────────┘
                                  │
 ┌──────────────────── Collection layer ─────────────────────────┐
 │  foundry-git   foundry-hooks-sdk   (future: runtime collectors)│
 └────────────────────────────────┬───────────────────────────────┘
                                  │
 ┌──────────────────── Storage layer ────────────────────────────┐
 │  Postgres (SQLModel)   Redis (Arq queues + cache)              │
 └────────────────────────────────────────────────────────────────┘
```

## Package boundaries

- **`foundry-core`** — shared config, db session, models, enums, evidence, IDs.
- **`foundry-git`** — git clone/fetch, ref and commit enumeration, divergence.
- **`foundry-analysis`** — pure, deterministic analytics (drift, stale,
  capabilities, readiness, summary). No I/O beyond what callers hand it.
- **`foundry-hooks-sdk`** — canonical `foundry.manifest.json` schema +
  Python + TypeScript loaders.
- **`foundry-policy`** / **`foundry-security`** — stubs for Phase 2+.
- **`foundry-ui`** — shared React primitives + design tokens.

Cross-product imports are **forbidden** (enforced in CI via
`scripts/check_import_boundaries.py`). BranchFoundry and GuardFoundry only
share code via the `foundry-*` packages above.

## Data flow: branch sync

1. API receives `POST /api/v1/repos/{id}/sync` → enqueues `branch_sync` on Arq.
2. Worker clones/fetches the repo via `foundry-git`.
3. For each branch: compute ahead/behind vs default, upsert branches +
   commits, record a `ScanRun`.
4. `foundry-analysis` runs stale classification, readiness scoring,
   capability matching (from `HookManifest`), and composes a
   deterministic summary backed by an `EvidenceBundle`.
5. `Summary` rows land with confidence scores; UI reads from API.

## Evidence model

Every assertion surfaces with an `EvidenceBundle` containing up to four tiers:

| Tier | Source | Examples |
| --- | --- | --- |
| 1 | Git | ahead/behind counts, file globs touched |
| 2 | Structural | manifest-matched feature names |
| 3 | Runtime (future) | traces, feature flags |
| 4 | Model inference (optional) | LLM-assisted prose |

Confidence is a function of tier coverage, not free-form. UI renders it as a
tier-banded `ConfidenceBadge`.

## Environments

- **Local dev**: Docker Compose (`infra/compose/docker-compose.yml`),
  Postgres + Redis + api + worker + web. Repos clone into a named volume.
- **CI**: GitHub Actions runs lint, types, tests, docker-build smoke, and
  import-boundary check.
- **Prod (future)**: same containers, K8s with HPA on worker, managed
  Postgres + Redis.
