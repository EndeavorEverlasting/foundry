# Foundry Branch Naming Standard

## Rule

Every branch created by Foundry must include:

1. A branch type.
2. A calendar date in `YYYY-MM-DD` format.
3. A context slug that explains the work.

## Format

```text
<type>/<YYYY-MM-DD>-<context-slug>
```

## Approved branch types

- `feature`
- `fix`
- `docs`
- `chore`
- `release`
- `hotfix`

## Good examples

```text
feature/2026-05-01-foundry-pr-cleanup-policy
fix/2026-05-01-github-stale-pr-merge-handling
docs/2026-05-01-branch-naming-standard
chore/2026-05-01-repo-cleanup-pass
```

## Rejected examples

```text
feature/pr-cleanup-automation
work
cleanup
feature/foundry-update
feature/2026-05-01
```

## Why this exists

Branch names are operational artifacts. They should answer three questions quickly:

- What type of work is this?
- When was it started?
- What is the context?

Foundry must not create vague or undated branches. If Foundry cannot build a compliant branch name, it should refuse to create the branch and return a policy error.

## PR cleanup requirement

Any automated pull request cleanup branch must also create or update documentation that records:

- Generated branch name.
- Repository name.
- Target default branch.
- Cleanup purpose.
- Safety rules used for classification or merge decisions.

Example cleanup branch:

```text
chore/2026-05-01-web-excel-repair-triage-pr-cleanup
```

Example run document:

```text
docs/branch-runs/2026-05-01-web-excel-repair-triage-pr-cleanup.md
```
