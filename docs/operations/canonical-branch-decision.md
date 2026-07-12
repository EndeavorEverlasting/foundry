# Foundry canonical-branch decision

**Date:** 2026-07-12
**Repo-floor snapshot:** [foundry-repo-floor-20260712.json](./foundry-repo-floor-20260712.json)
**Author:** repo-floor coordinator
**Status:** decision recorded; mutation pending owner approval

## Current state

Foundry has **no `main` branch**. The GitHub default branch is
`feature/2026-04-25-foundry-release-control-plane`, which contains every
commit in the repository (6 total, from bootstrap through integration tests).

No other branch carries independent product work. Three documentation PRs
branch off the canonical trunk and target it as their base.

## Evidence

| Fact | Value |
| --- | --- |
| GitHub default branch | `feature/2026-04-25-foundry-release-control-plane` |
| Default branch SHA | `a1f506f3e6fe5d66ca83c722a6484cb735936fd0` |
| `refs/heads/main` | **does not exist** |
| `refs/remotes/origin/main` | **does not exist** |
| Total commits (default) | 6 |
| Local worktrees | 1 (clean) |
| Conflicts | 0 |
| Open PRs | 3 (all docs, all mergeable) |
| CI runs on push to default | **never fires** (CI triggers `push` to `main`) |
| CI runs on PRs | 5 total, all failed (Node toolchain setup, not code) |

## PR classification

| PR | Title | Branch | Base | Commits | Mergeable | CI | Classification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #1 | docs: enforce dated branch naming standard | `docs/2026-05-01-branch-naming-standard` | feature branch | 4 | MERGEABLE | failed (pnpm) | **current** |
| #2 | Docs: Add extraction forensics gate doctrine | `docs/2026-05-26-extraction-forensics-gate` | feature branch | 3 | MERGEABLE | failed (pnpm) | **current** |
| #3 | Add SysAdminSuite mainline promotion insights | `docs/sysadminsuite-mainline-promotion-insights-2026-05-26` | feature branch | 1 | MERGEABLE | failed (pnpm) | **current** |

All three PRs are:
- Documentation-only
- Based on the current canonical HEAD
- Cleanly mergeable
- Blocked only by a CI toolchain issue (pnpm setup), not code problems

No PR is stale, superseded, divergent, or conflicting. All should be
retained and merged after CI is repaired.

## Decision

**Create `main` from the current canonical branch.**

Rationale:
1. The feature branch has always been the only code branch. There is no
   "feature work" to separate from a stable base.
2. The 6-commit history is linear and coherent (bootstrap, API, web, docs,
   hooks, integration tests).
3. CI is configured for `main` and currently never runs on push. Creating
   `main` enables push-triggered CI.
4. The dated branch name is a development convention, not a canonical name.
   A permanent `main` branch is the standard GitHub default.
5. Three open PRs already target the feature branch. After creating `main`,
   these PRs should be retargeted.

## Recommended mutation sequence

Execute these steps **in order** after owner approval. Each step is
independent and should be verified before proceeding.

### Step 1: Create `main` from current HEAD

```bash
git checkout -b main feature/2026-04-25-foundry-release-control-plane
git push -u origin main
```

### Step 2: Change GitHub default branch

Use the GitHub UI or API:
```
gh repo edit EndeavorEverlasting/foundry --default-branch main
```

### Step 3: Retarget open PRs

```bash
gh pr edit 1 --base main
gh pr edit 2 --base main
gh pr edit 3 --base main
```

### Step 4: Retire the dated branch

After all PRs are merged or retargeted:
- Do **not** delete `feature/2026-04-25-foundry-release-control-plane`
  immediately. Convert it to a protected tag or archive branch.
- The branch contains the full development history and should be preserved
  for provenance.

### Step 5: Repair CI

The CI workflow (`.github/workflows/ci.yml`) already targets `main` for
push triggers. After creating `main`, push-triggered CI will activate.
The Node.js job failure (pnpm setup) is a separate toolchain issue that
should be fixed independently.

## Risks

| Risk | Mitigation |
| --- | --- |
| CI Node jobs fail after `main` creation | Fix pnpm setup in a follow-up; Python and import-boundary jobs may pass independently |
| PRs show merge conflicts after retarget | All PRs are docs-only and based on current HEAD; conflict risk is negligible |
| Loss of development history | Preserve the dated branch as a tag or archive; do not delete |
| Downstream references to dated branch name | Update Continuum cross-repo map and any integration configs |

## What this decision does NOT do

- Does not merge, rebase, squash, or delete any branch
- Does not change the GitHub default branch (requires owner mutation)
- Does not fix CI toolchain issues
- Does not modify product code, dashboards, APIs, or runtime behavior
- Does not close any open PR
