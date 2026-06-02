# Agent Sprint Contract

## Purpose

Foundry needs a strict contract for AI-assisted repo sprints. A handoff prompt is not a sprint. A useful sprint produces scoped repo changes, proof, and a reviewable branch without turning the repo into agent soup.

This contract defines how an agent should move from repo evidence to commits.

## Core Rule

```text
Anchor first. Classify second. Mutate last.
```

No branch advice, PR advice, dependency advice, or implementation advice is valid until the repo state is proven.

## Sprint Modes

| Mode | Goal | Allowed output | Write access |
|---|---|---|---|
| `anchor` | Prove repo, branch, remotes, toolchain, and status | Terminal proof or captured evidence | No |
| `forensics` | Classify branches, PRs, gaps, stale code, and contamination | Ledger docs | Docs only |
| `doctrine` | Convert repeated lessons into reusable Foundry policy | Docs and schemas | Docs only |
| `surgical_fix` | Fix one proven gap | Narrow code or config change | Yes, scoped |
| `implementation` | Build one feature with tests | Code, tests, docs | Yes, scoped |
| `promotion` | Move reviewed work from branch evidence to product branch | Candidate-native commit | Yes, but never raw branch merge |

## Minimum Anchor Proof

An agent must capture these facts before mutation:

```text
repository
current branch
base branch
head commit
working tree status
remotes
recent commits
open PRs relevant to the sprint
branch divergence
language/toolchain files
existing tests
known generated or private artifact paths
```

If any of these are missing, the agent must say `STOP` or limit itself to docs-only notes.

## Mutation Rules

An agent may mutate only after proving:

- target repo
- target base branch
- target head branch
- branch naming policy
- intended file list
- diff scope
- no unrelated generated artifacts
- no secret values
- no Replit runtime files unless explicitly scoped

Never sneak these into a feature PR:

```text
.replit
replit.nix
.cache/replit
.pythonlibs
.venv
node_modules
dist
build
generated workbooks
private screenshots
credential helpers
post-merge hooks
```

## Commit Scope Rules

A valid sprint commit should fit one sentence:

```text
Add the missing pytest dev dependency.
Document the Replit extraction gate.
Implement branch-name validation.
Add read-only anchor command output.
```

If the sentence needs commas, caveats, and three unrelated nouns, split the sprint.

## PR Body Contract

Every PR opened by an agent should include:

```markdown
## Summary
- What changed
- Why it changed

## Scope
- Files intentionally changed

## Out of scope
- Things explicitly not touched

## Validation
- Commands run, or reason validation was docs-only

## Risk
- Known risks and deferred items

## Follow-up
- Next surgical PRs
```

## STOP Conditions

Say `STOP` when:

- branch is not anchored
- base branch is unknown
- worktree is dirty unexpectedly
- diff includes unrelated files
- dependency install fails before tests run
- tests exist but runner is undocumented
- secret-like values appear in tracked files
- branch contains stale implementation against a newer architecture
- feature has UI but no backend/storage proof
- feature has schema but no migration proof
- a raw Replit branch would overwrite candidate-native logic

## Foundry Product Implication

Foundry should eventually model this contract directly:

| Concept | Future product surface |
|---|---|
| Anchor proof | `foundry anchor` |
| Branch divergence | BranchFoundry branch graph |
| Sprint mode | PR wizard / CLI flag |
| STOP condition | Policy engine finding |
| PR body contract | Generated PR body |
| Deferred risk | Review ledger item |
| Contamination path | GuardFoundry finding |

## Operating Standard

```text
A clean sprint leaves the repo easier to reason about than it found it.
```

If an agent cannot prove that, it should not write code.
