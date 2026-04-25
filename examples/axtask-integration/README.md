# AxTask integration example

This folder contains the [foundry.manifest.json](foundry.manifest.json) that AxTask ships with.
BranchFoundry reads it to:

- Map touched files to high-level product capabilities (Tier-2 evidence).
- Flag commits that cross security-sensitive surfaces (sensitive routes, privileged actions).
- Enrich branch summaries with "this branch likely affects X and Y".

Feature inventory (blueprint §13.3):

| Feature              | Purpose                                                |
| -------------------- | ------------------------------------------------------ |
| `task-creation`      | Creating, editing, classifying tasks                   |
| `feedback-system`    | Capturing and resolving user feedback                  |
| `adherence-tracking` | Measuring task adherence                               |
| `reward-engine`      | Reward/streak logic tied to adherence                  |
| `account-management` | Auth, profile, TOTP, account backup/import            |

## Seeding the local repo

Run the seeder once the API is up. This registers the local AxTask folder
as a repo, uploads the manifest, and enqueues a sync:

```bash
docker compose -f infra/compose/docker-compose.yml exec api python -m scripts.seed_axtask
```

Override the repo location via `FOUNDRY_AXTASK_PATH` (must point to a path that
exists inside the container — mount your dev folder into `docker-compose.yml`
if you want to read the real repo).
