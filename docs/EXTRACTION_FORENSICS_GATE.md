# Extraction Forensics Gate

## Purpose

Foundry must support evidence-first extraction of product intent and usable implementation from contaminated development environments, especially Replit-origin repositories with messy local branches, sub-REPL branches, agent artifacts, generated workflows, stale code, and unclear dependency state.

This doctrine was derived from active extraction work across:

- AxTask
- WebExcel Repair Triage
- SysAdminSuite

The core lesson is simple:

```text
Find the pole before giving advice.
```

No branch surgery, PR creation, merge advice, rebase advice, dependency advice, or implementation work should begin until the repository state is anchored.

## Extraction Status Labels

Foundry should classify each repository extraction as one of:

| Status | Meaning |
|---|---|
| `NOT_EXTRACTED` | Repository state is not anchored, evidence is unclassified, or usable source material is unknown. |
| `PARTIALLY_EXTRACTED` | Some product intent or implementation is preserved, but branches, evidence directories, dependencies, tests, or migration paths remain unclassified. |
| `EXTRACTED_WITH_DEFERRED_RISKS` | Product intent and key implementation paths are preserved, but documented risks remain intentionally deferred. |
| `FULLY_EXTRACTED` | All known branches/evidence sources are classified, local setup is proven, tests/dependencies are documented, and preserved features have proof across the required layers. |

Default stance for Replit-origin repos should be `PARTIALLY_EXTRACTED` until proven otherwise.

## Mandatory Anchor Phase

Foundry must anchor before advice.

Minimum anchor commands should prove:

```bash
pwd
git remote -v
git branch --show-current
git status -sb
git log --oneline --decorate -12
git fetch origin --prune
git branch --all --verbose --no-abbrev
```

Foundry must not run this blindly in Replit-contaminated repos:

```bash
git fetch --all --prune
```

Reason: Replit repos may contain many `subrepl-*` remotes pointing at `ssh.spock.replit.dev`. Fetching all can trigger password prompts or fail mid-anchor. Use `git fetch origin --prune` first, then inspect local refs and target sub-REPL remotes surgically.

## Replit Source Material Rule

Treat Replit as contaminated source material, not authority.

The correct extraction model is:

```text
GitHub stability
+ Replit feature intent
+ portable implementation outside Replit
- Replit-specific junk
- destructive regressions
- workflow contamination
= real product branch
```

Raw Replit branches are evidence, not merge candidates.

## Local Sub-REPL Evidence Rule

Replit sub-REPL remote fetch can fail while local branch refs still contain useful evidence.

Foundry should check:

```bash
git branch --verbose --no-abbrev
git for-each-ref --format='%(refname:short) %(objectname:short) %(committerdate:iso8601) %(subject)'
```

before declaring a sub-REPL unavailable.

Classification:

```text
LOCAL_SUBREPL_EVIDENCE_AVAILABLE
```

Use when local `subrepl-*` branches exist even though remote SSH access fails.

## Secret Safety Rule

Foundry must never print secret values by default.

Avoid broad credential config diagnostics such as:

```bash
git config --show-origin --get-regexp 'credential|insteadOf|url\.|remote\..*\.url'
```

because this can expose inline token helpers.

Safer default:

```bash
git config --show-origin --get-regexp 'remote\..*\.url'
```

For repository scans, print secret-like file paths only, not contents:

```bash
grep -RIl \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude-dir=dist \
  --exclude-dir=build \
  --exclude-dir=.venv \
  -E 'ghp_|gho_|github_pat_|x-access-token|DATABASE_URL|SESSION_SECRET|OPENAI_API_KEY|REPLIT|replit|TOKEN|SECRET|PASSWORD|PRIVATE_KEY|CLIENT_SECRET|API_KEY|CONNECTION_STRING' .
```

## Branch / Feature Classification Labels

Foundry should classify branch evidence and feature preservation with explicit labels:

| Label | Meaning |
|---|---|
| `preserved` | Feature is implemented and proven in the current candidate path. |
| `partially_preserved` | Some layers are present, but proof or implementation is incomplete. |
| `missing` | Product intent exists but no candidate implementation was found. |
| `ui_only` | UI exists without backend/storage proof. |
| `backend_only` | Backend exists without UI/client proof. |
| `cli_only` | CLI/script exists without app integration proof. |
| `test_only` | Tests or fixtures exist without implementation proof. |
| `stale_branch_code` | Branch contains obsolete implementation against older architecture. |
| `unsafe_to_port` | Raw code should not be applied directly. |
| `candidate_native_rewrite_needed` | Intent is valid but implementation must be rewritten against current candidate architecture. |
| `schema_migration_drift` | Schema defines tables/fields not created by migrations. |
| `test_stack_undocumented` | Tests exist but runner/dependencies are not documented. |
| `dependency_undocumented` | Runtime or build dependency is required but not declared. |
| `gh_cli_unavailable` | Branch push works but GitHub CLI is missing/unavailable. Use connector/API/browser PR path. |
| `replit_only_behavior` | Feature depends on Replit-specific runtime behavior. |
| `deferred_with_reason` | Explicitly deferred with risk and follow-up recorded. |

## Preservation Proof Matrix

Do not call a feature preserved until the relevant layers are checked.

| Layer | Proof examples |
|---|---|
| UI | Route/page/component exists and calls expected API. |
| API | Route exists and validates auth/input. |
| Storage | Read/write path exists against current candidate schema. |
| Schema | Tables/types exist in current schema. |
| Migration | Clean database migration creates required schema. |
| Tests | Unit/contract/integration/smoke proof exists. |
| Local run | Feature can be run outside Replit or limitation is documented. |
| Contamination | No `.replit`, `replit.nix`, Replit workflows, post-merge scripts, or stale symbols accidentally included. |

## AxTask Lessons

### Leaderboard Harvest

AxTask PR #54 restored the leaderboard backend natively.

Raw Replit code referenced stale symbols:

```text
forumPosts
forumComments
skillUnlocks
```

The correct fix used candidate-native symbols instead:

```text
wallets
coinTransactions
classificationContributions
communityReplies
userRewards
rewardsCatalog
userOfflineSkills
userAvatarSkills
users
```

Lesson:

```text
Valid product intent + stale branch code = candidate-native rewrite, not raw port.
```

### Skill Tree Persistence

AxTask `subrepl-dbmojt3g` preserved the intent: Skill Tree unlocks should persist server-side across refresh/login/device boundaries.

Its raw implementation was stale:

```text
skillUnlocks
/api/skill-unlocks
old single-page Skill Tree rewrite
shared/skill-nodes.ts
```

Candidate architecture was newer:

```text
avatarSkillNodes
userAvatarSkills
offlineSkillNodes
userOfflineSkills
/api/gamification/avatar-skills
/api/gamification/offline-skills
```

Result:

- Docs-only PR captured the forensic decision.
- Raw implementation was rejected.
- Candidate-native migration gap was then fixed surgically.

### Schema / Migration Drift

AxTask schema defined:

```text
offlineSkillNodes
userOfflineSkills
```

but migrations did not create:

```text
offline_skill_nodes
user_offline_skills
```

Classification:

```text
SCHEMA_MIGRATION_DRIFT
```

Priority:

```text
P1 when the feature is part of deployable candidate behavior.
```

### Python Test Stack Gap

AxTask Billing Bridge runtime dependencies installed, but `pytest` was missing.

Classification:

```text
TEST_STACK_UNDOCUMENTED
```

Do not call Python setup proven until:

- `.venv` exists
- `.venv` is isolated
- runtime deps install
- dev/test deps install
- test runner exists
- tests pass or fail with real test failures

## WebExcel Repair Triage Lessons

WebExcel extraction should inventory concepts first, then branch deltas.

Special care:

- Excel / OOXML repair logic is high-risk.
- Do not casually rewrite `.xlsx` files with high-level tools.
- Preserve Web Excel compatibility assumptions.
- Inspect workbook repair philosophy, tests, and constraints before suggesting mutations.

Concept buckets should include:

- workbook repair
- worksheet repair
- tableParts relationships
- sharedStrings
- styles
- defined names
- formulas
- conditional formatting
- data validation
- calcChain
- pivot/cache artifacts
- Web Excel compatibility
- candidate workbook naming
- artifact/README/error log generation

Foundry should support concept-first extraction, then code-usefulness extraction branch by branch.

## SysAdminSuite Lessons

SysAdminSuite extraction requires platform discipline.

Do not assume Replit/Linux execution proves Windows production behavior.

Concept buckets should include:

- printer reconnaissance / mapping
- network survey commands
- file share / UNC discovery
- software installer orchestration
- Windows baseline checks
- Bash vs PowerShell vs CMD decisioning
- Rust/C/portable executable direction
- GUI/WPF/HTA/local app ideas
- logging/audit/dry-run
- rollback/safety behavior

Sysadmin-specific risk labels should include:

- `windows_only`
- `linux_only`
- `powershell_only`
- `bash_only`
- `admin_rights_required`
- `network_policy_constrained`
- `privileged_operation_risk`

Commands should remain defensive, administrative, and scoped to owned or authorized systems.

Foundry should flag risky patterns in diffs:

```text
credential
password
token
secret
bypass
disable defender
exfil
stealth
keylog
dump
hash
mimikatz
encodedcommand
executionpolicy bypass
net user
localgroup administrators
schtasks
startup
Run key
```

A hit does not automatically mean malicious behavior. It means manual review required.

## Extraction Completion Gate

Foundry should not call a repo fully extracted until:

- local branches are classified
- origin branches are classified
- sub-REPL branches are classified or explicitly unavailable
- evidence directories are inventoried
- secret-like paths are scanned by path only
- Replit-specific files are quarantined
- local setup is proven
- Python/Node/PowerShell/Rust/C tooling is inventoried as applicable
- runtime dependencies are installed or gaps are classified
- dev/test dependencies are installed or gaps are classified
- tests pass or fail with real test failures
- schema/migration alignment is proven where applicable
- feature preservation matrix exists
- branch/use-case ledger exists
- next PRs are surgical and scoped

## Recommended Foundry Workflow

### Phase 1: Anchor

- repo root
- remotes
- current branch
- working tree cleanliness
- recent commits
- origin fetch
- branch graph
- toolchain availability

### Phase 2: Evidence Discovery

- local branches
- origin branches
- sub-REPL branches
- capture branches
- attached assets
- `.local/tasks`
- agent docs and guardrails
- Replit state/cache paths by path only

### Phase 3: Concept Inventory

Scan the whole codebase for concepts before coding.

Capture:

- concept name
- source evidence
- product intent
- candidate evidence
- exact files touched
- risk labels
- proof gaps
- next action

### Phase 4: Branch Diff Triage

For each source branch:

- verify base/source refs
- inspect commit summary
- inspect diff stat
- inspect name-status
- run stale-symbol scan
- run contamination scan
- inspect patch preview
- classify branch

### Phase 5: Action Selection

Choose one:

- docs-only audit PR
- candidate-native implementation branch
- migration-proof branch
- test/smoke branch
- dependency documentation branch
- reject raw branch
- defer with reason

## Mantra

```text
Find the pole. Read the snow. Then move.
```
