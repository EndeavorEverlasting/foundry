# BranchFoundry — product one-pager

**Tagline.** *Know what every branch is doing, how far it has drifted, and
what to do about it.*

**Problem.** At any given time, a product repo has dozens of branches in
flight. Some are ready to merge, some are forgotten, some conflict with main,
some cross security-sensitive code paths. Everyone has a different mental
model and `git log` does not help.

**Solution.** BranchFoundry ingests Git, fuses it with an optional
`foundry.manifest.json`, and surfaces:

- **Dashboard** — active vs stale, ready-to-merge, conflict risk, recent
  merges, scan status.
- **Branch graph** — React Flow visualization with server-side lane
  assignment, filters, hover evidence.
- **Branch detail** — ahead/behind/diverged, touched modules, inferred
  capabilities with confidence, linked PRs, suggested actions.
- **Drift panel** — what main is missing, what branches are behind, conflict
  risk, merge readiness.
- **Stale view** — forgotten, dormant-with-changes, orphaned experiments,
  no-recent-ownership.
- **Action center** — needs review, ready to merge, at risk, needs rebase,
  failing checks.
- **Release readiness** — centralized release-contract checks (schema/migration,
  env template, route inventory, release docs) with evidence-backed pass/fail.
- **Divergence playbook** — prescriptive, low-friction next steps when branches
  drift from `main` (measure drift, reconcile, re-check, then decide).

**Signals used.**

1. Git (ahead/behind, touched files, authorship, recency) — always on.
2. Manifest (feature mapping, security surfaces) — when present.
3. PR metadata (open/closed/merged/draft) — when source supports it.
4. Scan runs (future: GuardFoundry findings overlaid on branches).
5. Release profile rules (manifest + repo policy) for deploy discipline.
6. Divergence score (ahead/behind + conflict pressure) to prioritize reconciliation.

**Divergence guidance contract.**

When drift is non-trivial, BranchFoundry should recommend this sequence:

1. Measure (`ahead/behind`, changed files vs `main`).
2. Check (`release/check` run and findings).
3. Reconcile (merge `main` into feature).
4. Re-check (confirm findings clear).
5. Decide (PR forward, split work, or hold deploy).

**Summary contract.** Every branch carries a deterministic, templated
summary backed by an `EvidenceBundle`. The UI renders a tier-banded
`ConfidenceBadge`. No hallucinations; LLM prose is strictly optional and
always marked Tier-4.

**v1 success criteria.**

- Can register a local repo, run sync, and see every branch classified
  within 60 s for repos up to ~2k branches.
- Drift and stale panels are accurate enough to drive real merge/delete
  decisions against AxTask.
- Manifest-driven feature mapping produces at least 70% branch coverage on
  AxTask's five features.

**Non-goals in v1.**

- Multi-user auth and roles (seam exists, feature waits).
- Cloud SaaS hosting.
- AI-generated PRs. Summaries describe; they do not act.
