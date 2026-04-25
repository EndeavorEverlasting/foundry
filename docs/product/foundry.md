# Foundry — product one-pager

**What it is.** Foundry is a platform for turning raw engineering signals
(Git, app manifests, security scans, runtime data) into actionable
intelligence and operational leverage for modern product teams.

**What it solves.** Teams ship faster than their ability to understand what
they've shipped. Branches drift, stale work piles up, features cross
security-sensitive surfaces without anyone noticing, and dashboards remain
descriptive when they need to be directive.

**Who it's for.** Engineering leaders, platform/infra teams, and security
engineers at orgs with 10+ repos or 50+ active branches.

**Products.**

- **BranchFoundry** — Git-first branch intelligence. Graph, drift, stale,
  actions, evidence-backed summaries. *(v1 now.)*
- **GuardFoundry** — application-aware security scanning that uses
  `foundry.manifest.json` to focus on what actually matters per app.
  *(Phase 2.)*
- **FoundryHooks** — lightweight SDK + manifest spec apps use to tell Foundry
  about their own structure. Shared across products.

**Why it's different.**

1. **Evidence-first.** Every assertion carries a tiered `EvidenceBundle`.
   Confidence is a function of tier coverage, not vibes.
2. **App-aware.** The manifest contract means Foundry understands features
   and security surfaces without invasive instrumentation.
3. **Modular.** Collectors, analysis, jobs, storage, API, UI are all
   replaceable. Products plug in; they don't monolith.
4. **Local-first dev.** Works offline via Docker Compose. No SaaS lock-in.

**v1 scope.** BranchFoundry end-to-end, seeded against the AxTask app, with
manifest-driven capability inference and evidence-backed summaries.
