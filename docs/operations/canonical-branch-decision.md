# Foundry canonical-base decision and repository-floor map

**Snapshot date:** 2026-07-12
**Remote verification date:** 2026-07-13
**Machine-readable record:** [foundry-repo-floor-20260712.json](./foundry-repo-floor-20260712.json)
**Lane:** coordinator / cleanup / branch governance
**Status:** canonical target selected; GitHub default-branch mutation not executed

## Decision

Create a permanent `main` branch at exactly:

```text
a1f506f3e6fe5d66ca83c722a6484cb735936fd0
```

That commit is the current head of
`feature/2026-04-25-foundry-release-control-plane` and contains the six-commit
Foundry trunk from bootstrap through integration-test and governance work.

The dated feature ref is the **temporary current GitHub default and source
commit**, not the permanent canonical branch name. Do not move, delete,
rewrite, or force-push that ref.

Changing GitHub's default branch to `main` is still gated on:

1. Re-running the required local floor commands in an actual Foundry worktree.
2. Confirming the default source ref still resolves to the recorded SHA.
3. Recording baseline validation results without attributing existing CI
   failures to unrelated pull-request changes.
4. Creating `main` as a new ref without changing any existing ref.

## Proof boundary

This record contains **remote ref, PR, comparison, comment, workflow, and
decision proof**.

It does not claim a current clean local worktree. A prior snapshot recorded one
clean worktree at
`C:/Users/Cheex/AppData/Local/Temp/opencode/foundry`, on the source branch at
`a1f506f3e6fe5d66ca83c722a6484cb735936fd0`. That local observation was not
independently reproducible during the 2026-07-13 verification because the
execution container could not resolve `github.com` for a clone. The prior
observation is preserved as historical evidence, not promoted to current proof.

Local conflict state, upstream configuration, in-progress merge/rebase/cherry-
pick state, and uncommitted files therefore remain **unverified in this run**.

## Canonical candidates

| Candidate | SHA / state | Evidence | Decision |
| --- | --- | --- | --- |
| `feature/2026-04-25-foundry-release-control-plane` | `a1f506f3e6fe5d66ca83c722a6484cb735936fd0` | Current GitHub default; six-commit trunk | Source commit only; preserve |
| `main` | absent; compare lookup returns 404 | CI push trigger names `main` | Create from `a1f506f3...` |
| `master` | absent; compare lookup returns 404 | No repository metadata or PR targets reference it | Reject |
| PR #1 head | `528ef732ebd82be79defa4d8fbaba7f3b0d4e974` | 4 ahead / 1 behind source trunk | Not canonical; replayable PR payload |
| PR #2 head | `1333435324c9094309f6183a0c62c0017dbdf869` | 3 ahead / 0 behind source trunk | Not canonical; current PR payload |
| PR #3 head | `7805831a00c0ab295b1c6f2882d88907d00ed462` | 1 ahead / 0 behind source trunk | Not canonical; current PR payload |
| PR #4 head | `46204e9d815d79933ffe16acf4032163960e213e` | Repo-floor documentation branch before correction commits | Not canonical; bounded decision PR |

These are the remote refs directly observed through repository metadata and
open pull requests. The connector's branch-search endpoint returned no results
even for the exact default-branch name, so this run does not claim an exhaustive
server-side branch listing beyond the observed refs. The required local
`git branch -a -vv` follow-up remains a gate.

## Pull-request map

### PR #1: replayable, owner review required

**Branch:** `docs/2026-05-01-branch-naming-standard`
**Head:** `528ef732ebd82be79defa4d8fbaba7f3b0d4e974`
**Comparison:** diverged, 4 commits ahead and 1 behind; merge base
`1111a7255d77db8538db5b79e475e1a3b38c8f49`
**GitHub mergeability:** mergeable

Unique payload to preserve:

- `docs/branch-naming-standard.md`
- `packages/foundry-policy/src/foundry_policy/__init__.py`
- `packages/foundry-policy/src/foundry_policy/branch_naming.py`
- `packages/foundry-policy/tests/test_branch_naming.py`
- Four branch commits and the existing PR conversation
- CodeRabbit's recorded docstring-coverage warning

This PR is not documentation-only and is not based on the current source HEAD.
Keep the branch and PR open. Before merge, update or replay it onto the selected
canonical commit, run the policy-package tests, and resolve or explicitly accept
the review warning.

### PR #2: current, merge gate blocked by baseline CI

**Branch:** `docs/2026-05-26-extraction-forensics-gate`
**Head:** `1333435324c9094309f6183a0c62c0017dbdf869`
**Comparison:** 3 commits ahead and 0 behind source trunk
**GitHub mergeability:** mergeable

Unique payload to preserve:

- `docs/AGENT_SPRINT_CONTRACT.md`
- `docs/EXTRACTION_FORENSICS_GATE.md`
- `docs/PROOF_ARTIFACT_CONTRACT.md`
- Three branch commits and the existing PR conversation
- The extraction, sprint, and proof-artifact doctrine recorded in those files

The branch is a clean descendant of the selected source commit. Retargeting it
to `main` after `main` is created should not change ancestry, but merge remains
blocked until validation is rerun and recorded.

### PR #3: current, merge gate blocked by baseline CI

**Branch:** `docs/sysadminsuite-mainline-promotion-insights-2026-05-26`
**Head:** `7805831a00c0ab295b1c6f2882d88907d00ed462`
**Comparison:** 1 commit ahead and 0 behind source trunk
**GitHub mergeability:** mergeable

Unique payload to preserve:

- `docs/insights/sysadminsuite-mainline-promotion-2026-05-26.md`
- The single branch commit and existing PR conversation
- The "archive branches are museums; product branches are roads" doctrine
- CodeRabbit's no-actionable-comments review result

The branch is a clean descendant of the selected source commit. Retarget only
after `main` exists and the base SHA is rechecked.

## CI evidence

`.github/workflows/ci.yml` triggers pushes only for `main`, while pull requests
trigger regardless of base name. Because `main` is absent, push-triggered CI is
currently ineffective for the GitHub default branch.

The latest observed pull-request runs do not provide green build proof:

| PR | Docker smoke | Import boundary | Python | Node |
| --- | --- | --- | --- | --- |
| #1 | passed | passed | failed at Ruff; Mypy/Pytest skipped | failed at pnpm setup; remaining steps skipped |
| #2 | passed | passed | failed at Ruff; Mypy/Pytest skipped | failed at pnpm setup; remaining steps skipped |
| #3 | failed during job setup | passed | failed at Ruff; Mypy/Pytest skipped | failed at pnpm setup; remaining steps skipped |
| #4 | passed | passed | failed at Ruff; Mypy/Pytest skipped | failed at pnpm setup; remaining steps skipped |

These failures may be baseline or infrastructure failures, but this decision
does not claim causality without the job-log and local reproduction evidence.

## Safe mutation sequence

Do not execute these commands until the local floor gate below passes.

### 1. Re-prove the floor and source SHA

```bash
git fetch origin --prune
git status --short
git branch --show-current
git log --oneline --decorate -8
git worktree list --porcelain
git branch -a -vv
git diff --name-only --diff-filter=U
git rev-parse origin/feature/2026-04-25-foundry-release-control-plane
```

Expected source SHA:

```text
a1f506f3e6fe5d66ca83c722a6484cb735936fd0
```

### 2. Create `main` without moving any existing branch

```bash
git push origin a1f506f3e6fe5d66ca83c722a6484cb735936fd0:refs/heads/main
```

### 3. Verify the new ref

```bash
git fetch origin --prune
git rev-parse origin/main
git rev-parse origin/feature/2026-04-25-foundry-release-control-plane
```

Both commands must print the same full SHA before changing the GitHub default.

### 4. Change the GitHub default branch

```bash
gh repo edit EndeavorEverlasting/foundry --default-branch main
```

### 5. Retarget, without closing or rewriting, the open PRs

```bash
gh pr edit 1 --base main
gh pr edit 2 --base main
gh pr edit 3 --base main
gh pr edit 4 --base main
```

Re-run comparisons and checks after each retarget. PR #1 still requires replay
or update work because its head is one source-trunk commit behind.

## Forbidden follow-on mutations

- No branch deletion
- No force-push
- No blind merge, rebase, squash, or cherry-pick
- No closing PR #1, #2, or #3 before their unique files, commits, tests,
  comments, and doctrine are retained
- No claim that the local floor is clean until the local commands run
- No claim of feature, integration, build, or runtime proof from this sprint

## Checks required after checkout

The changed paths are documentation and JSON, but repository-level checks still
scan the complete tree. Run and record:

```bash
git diff --check
git status --short
git diff --stat
git diff
python -m json.tool docs/operations/foundry-repo-floor-20260712.json
uv run ruff check .
uv run mypy packages/foundry-core/src \
  packages/foundry-analysis/src \
  packages/foundry-git/src \
  packages/foundry-hooks-sdk/python/src \
  apps/foundry-api/src \
  apps/foundry-worker/src
uv run pytest -q
pnpm install --frozen-lockfile
pnpm -r lint
pnpm -r typecheck
pnpm -r test --if-present
pnpm -r build
python scripts/check_import_boundaries.py
docker build -f infra/docker/api.Dockerfile .
docker build -f infra/docker/worker.Dockerfile .
docker build -f infra/docker/web.Dockerfile .
```
