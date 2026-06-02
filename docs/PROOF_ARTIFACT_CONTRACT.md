# Proof Artifact Contract

## Purpose

Foundry should not merely tell a user that a repo is safe, mergeable, broken, or partially extracted. It should produce durable proof artifacts that another human or agent can inspect later.

This contract defines the minimum proof bundle for repo operations work.

## Principle

```text
No proof, no promotion.
```

A sprint is incomplete if the result cannot be audited after the terminal scrollback is gone.

## Required Proof Artifacts

| Artifact | Purpose | Required when |
|---|---|---|
| Anchor proof | Shows repo location, branch, remotes, status, base, and recent commits | Every sprint |
| Toolchain proof | Shows Python, Node, package manager, Docker, or language tooling state | Any code or test sprint |
| Dependency proof | Shows runtime and dev/test dependencies install or fail clearly | Any local run or test claim |
| Test proof | Shows tests pass, fail with real failures, or runner is undocumented | Any implementation or dependency sprint |
| Branch proof | Shows base/head, divergence, changed files, and PR state | Any branch, PR, or promotion sprint |
| Secret-safe scan | Shows secret-like paths or confirms none without printing values | Any repo extraction or contaminated-source sprint |
| Contamination scan | Shows Replit, generated artifact, workflow, hook, or cache risk | Any Replit-origin sprint |
| Completion gate | States current extraction or readiness classification | Any forensic sprint |

## Standard Classifications

Use explicit labels instead of vague confidence language.

```text
ANCHOR_PROVEN
ANCHOR_INCOMPLETE
DEPENDENCY_PROVEN
DEPENDENCY_UNDOCUMENTED
DEPENDENCY_INSTALL_FAILED
TEST_STACK_PROVEN
TEST_STACK_UNDOCUMENTED
TESTS_PASS
TESTS_FAIL_REAL_FAILURES
SECRET_PATH_REVIEW_REQUIRED
SECRET_VALUE_RISK
REPLIT_CONTAMINATION_RISK
BRANCH_GRAPH_PROVEN
BRANCH_GRAPH_INCOMPLETE
PARTIALLY_EXTRACTED
EXTRACTED_WITH_DEFERRED_RISKS
FULLY_EXTRACTED
```

## Anchor Proof Minimum

```text
repo full name
repo URL
local path if available
default branch
current branch
head SHA
base SHA
worktree state
open PRs relevant to scope
branch divergence
fetch result
```

If the work is performed through GitHub APIs instead of a local terminal, the proof should state that clearly and include API-derived equivalents.

## Dependency Proof Minimum

A dependency proof must show:

```text
language version
venv or package environment
runtime dependency install result
dev/test dependency install result
test runner availability
selected package locations when contamination is suspected
```

Do not call Python proven just because `.venv` exists. A venv polluted by `.pythonlibs`, user site packages, or global packages is limited proof at best.

## Test Proof Minimum

A test proof must classify one of:

| Result | Meaning |
|---|---|
| `TESTS_PASS` | Test runner exists and tests passed in the proven environment |
| `TESTS_FAIL_REAL_FAILURES` | Runner works, dependencies installed, failures are real test failures |
| `TEST_STACK_UNDOCUMENTED` | Tests exist but runner or dev dependency is missing |
| `TESTS_NOT_APPLICABLE_DOCS_ONLY` | Docs-only change with no runtime behavior changed |
| `TESTS_BLOCKED_BY_ENVIRONMENT` | Required external service or platform is unavailable |

## Branch Proof Minimum

Branch proof must include:

```text
base ref
base SHA
head ref
head SHA
ahead/behind or compare result
changed files
PR state if applicable
mergeability if applicable
risk classification
```

If the branch is old, divergent, or contaminated, Foundry should recommend candidate-native promotion instead of raw branch merge.

## Secret-Safe Review Rule

Never print raw secret values. Print only:

```text
path
line number when safe
pattern category
redacted snippet if needed
```

Secret-like findings are not automatically a breach. They are a review requirement.

## Completion Gate

Every forensic sprint should end with one status:

| Status | Meaning |
|---|---|
| `NOT_EXTRACTED` | Repo state or evidence is not anchored |
| `PARTIALLY_EXTRACTED` | Some useful intent or implementation is known, but proof gaps remain |
| `EXTRACTED_WITH_DEFERRED_RISKS` | Main product intent is preserved, with named deferred risks |
| `FULLY_EXTRACTED` | All branches, evidence, dependencies, tests, risks, and preserved features are classified |

The default for Replit-origin work is `PARTIALLY_EXTRACTED` until proven otherwise.

## Storage Format

A proof artifact can be stored as:

```text
docs/reviews/*.md
reports/*.json
artifacts/*.jsonl
PR body sections
CI summaries
```

For early Foundry work, Markdown review docs are enough. Later, Foundry should promote these fields into structured JSON so BranchFoundry and GuardFoundry can read them directly.

## Product Implication

Foundry should eventually generate a proof bundle after every operation:

```text
foundry anchor --json
foundry risk-scan --json
foundry branch-proof --base <base> --head <head>
foundry test-proof --command "pnpm py:test"
foundry completion-gate --status PARTIALLY_EXTRACTED
```

## Operating Standard

```text
A proof artifact is the receipt. Without it, the sprint did not happen.
```
