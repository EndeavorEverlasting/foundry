# Foundry Product Blueprint
**Version:** 2026-04-18  
**Status:** Build-ready planning draft  
**Author:** Richard Perez / ChatGPT synthesis

---

## 1. Executive Summary

**Foundry** is the umbrella platform. It is a modular suite for:
- **Branch intelligence**
- **Engineering observability**
- **App-aware security**
- **Custom integration hooks**
- **Professional dashboards for internal and commercial use**

The suite is designed to work **with Git, not against it**. It is not trying to replace Git itself. It sits above Git and related development systems to create clearer visibility, faster decisions, and stronger controls.

### Product family
- **Foundry** — umbrella platform
- **BranchFoundry** — Git analytics, branch intelligence, engineering visibility
- **GuardFoundry** — security scanning, leak detection, app-aware security enforcement
- **FoundryHooks** — integration SDK / hook layer for host apps
- **FoundryScan** — scanning and background analysis engine
- **FoundryPolicy** — policy engine for enforcement and governance

### Core thesis
Foundry should help answer:
- What is each branch actually building?
- What is `main` missing?
- What work is stale, hidden, duplicated, or merge-ready?
- What app-specific signals matter beyond raw Git metadata?
- Where are the likely security and exposure risks in code, config, runtime surfaces, and data access paths?

### Strategic decision
Foundry should be built as:
- **One shared platform core**
- **Two distinct product surfaces**
  - **BranchFoundry** for branch intelligence
  - **GuardFoundry** for security

This prevents product confusion while allowing shared tooling underneath.

---

## 2. Why this product should exist

Git already gives useful primitives:
- branches
- commits
- merges
- diffs
- authorship
- timestamps
- rebases
- PR workflows

But Git alone does not solve:
- feature-level understanding
- branch drift visibility at a product level
- interactive, executive-grade dashboards
- custom app-aware telemetry
- app-specific security boundary understanding
- reusable, elegant cross-project observability

Foundry exists to convert raw Git and app signals into:
- **clear intelligence**
- **professional dashboards**
- **operational leverage**
- **safer delivery**

---

## 3. Product goals

## 3.1 BranchFoundry goals
BranchFoundry should:
1. Visualize branch topology and commit history clearly
2. Show how far branches are ahead/behind/diverged from `main`
3. Infer what a branch is changing at the capability level
4. Surface forgotten or stalled work
5. Show review, merge, and release readiness
6. Provide evidence-backed summaries, not hand-wavy guesses
7. Support solo builders, team leads, and engineering managers
8. Look polished enough to sell

## 3.2 GuardFoundry goals
GuardFoundry should:
1. Scan code and repo history for secrets and sensitive exposure
2. Support app-aware hooks for custom security context
3. Detect likely leak paths in frontend, backend, config, and database usage
4. Correlate findings with branches, PRs, and releases
5. Generate prioritized remediation views
6. Work as a premium add-on or separate product surface
7. Protect internal logic while letting host apps integrate cleanly

---

## 4. Market-informed design principles

The current field shows a useful split:
- visual Git and branch tools emphasize **graphs, actions, history, and workflow**
- engineering intelligence tools emphasize **team visibility, delivery metrics, and drill-downs**
- AppSec tools emphasize **PR-native findings, secrets, custom rules, and remediation**

### What to emulate
#### From modern Git/branch tools
- interactive commit DAGs
- searchable and filterable history
- direct actions from graph context
- stack/branch dependency awareness
- merge readiness views
- PR inbox / action center

#### From engineering visibility products
- leadership dashboards layered on top of real repo evidence
- drill-downs by repo, team, project, service, time period
- trend views, not just snapshots
- bottleneck and stale-work detection
- portfolio views across many repos

#### From AppSec platforms
- diff-aware analysis
- PR-native feedback
- secret scanning across full history and branches
- custom rule packs
- policy-based enforcement
- remediation guidance, not just raw findings

### What not to emulate
- noisy vanity metrics
- pure surveillance framing
- giant dashboards with weak evidence
- “single pane of glass” bloat before product-market fit
- trying to replace Git itself
- shipping security claims broader than the actual engine supports

---

## 5. Product positioning

## 5.1 Umbrella positioning
**Foundry**  
*A platform for branch intelligence, engineering visibility, and app-aware security.*

## 5.2 BranchFoundry positioning
**BranchFoundry**  
*See what branches are actually building, what `main` is missing, and what needs attention.*

## 5.3 GuardFoundry positioning
**GuardFoundry**  
*App-aware security scanning and policy enforcement built to work with your product’s real boundaries.*

## 5.4 FoundryHooks positioning
**FoundryHooks**  
*A lightweight integration layer that lets host apps expose product-specific signals without exposing internal security mechanics.*

---

## 6. Product surfaces

## 6.1 BranchFoundry
Primary users:
- you as first user
- technical founders
- engineering leads
- product-minded engineering managers
- teams with many branches and uneven merge discipline

Primary jobs:
- understand branch status
- understand change intent
- see main-vs-branch drift
- spot forgotten work
- review release readiness
- produce portfolio and team visibility

## 6.2 GuardFoundry
Primary users:
- you as builder/operator
- security-conscious dev teams
- enterprise clients with custom app boundaries
- teams needing more than generic repo scanning

Primary jobs:
- detect secrets and leak paths
- highlight boundary failures
- model custom app risk through hooks
- provide actionable next steps
- tie security findings back to branch and release context

---

## 7. Architectural model

Foundry should be built as a **platform with separated layers**.

## 7.1 Core layers
1. **Collectors**
   - Git CLI / libgit2 / provider APIs
   - CI/CD metadata
   - PR metadata
   - issue metadata later
   - app-emitted events from FoundryHooks
   - dependency manifests
   - optional browser/runtime telemetry
   - config and environment metadata

2. **Normalizer**
   - convert raw inputs into stable internal schemas
   - unify branch, commit, PR, hook, finding, and artifact models

3. **Analysis engine**
   - branch drift
   - commit clustering
   - feature inference
   - stale branch detection
   - merge readiness scoring
   - risk scoring
   - ownership inference
   - hook coverage analysis
   - policy evaluation

4. **Storage**
   - PostgreSQL for state and relational data
   - object storage for snapshots and artifacts
   - Redis for queueing/caching
   - optional search index later

5. **Jobs engine**
   - scheduled scans
   - repo syncs
   - findings refresh
   - summary generation
   - digest generation
   - policy evaluation
   - snapshotting

6. **API layer**
   - REST to start
   - GraphQL later if the UI benefits from complex nested queries

7. **UI layer**
   - shared design system
   - BranchFoundry web app
   - GuardFoundry web app
   - embeddable dashboard modules later

8. **SDK / integration layer**
   - FoundryHooks for app-specific signals
   - event emission
   - manifest support
   - optional route/module annotations
   - optional security policy hooks

## 7.2 Deployment philosophy
Build so it can run as:
- local development mode
- self-hosted single-node deployment
- Docker Compose
- later Kubernetes if justified
- optional cloud-hosted SaaS later

---

## 8. Recommended initial tech stack

You prefer Python. That is a strong fit.

## 8.1 Backend
- **Python**
- **FastAPI** for API and service surface
- **Pydantic** for schemas
- **SQLAlchemy** or **SQLModel** for ORM/data layer
- **PostgreSQL** for storage
- **Redis** for caching/jobs
- **Celery**, **RQ**, or **Arq** for jobs
- **GitPython** to start, with option to add direct Git CLI calls or pygit2/libgit2 later
- **Semgrep CLI**, **trufflehog**, **gitleaks**, or similar wrappers later for GuardFoundry integrations where useful

## 8.2 Frontend
- **React**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** or equivalent design primitives
- **Recharts**, **visx**, or **D3** for graphing
- **React Flow** or custom graph rendering if branch DAG interaction grows sophisticated

## 8.3 Infrastructure
- Docker
- Docker Compose
- GitHub Actions for CI
- optional Traefik / Nginx reverse proxy
- optional S3-compatible artifact storage
- optional OpenTelemetry later

## 8.4 Why this stack
- fast to start
- commercial-looking front end possible
- Python-friendly analysis layer
- clean API boundaries
- easy containerization
- easy local development

---

## 9. Monorepo structure

Use **one monorepo** for the platform.

```text
foundry/
├─ apps/
│  ├─ branchfoundry-web/
│  ├─ guardfoundry-web/
│  ├─ foundry-api/
│  └─ foundry-worker/
├─ packages/
│  ├─ foundry-core/
│  ├─ foundry-git/
│  ├─ foundry-analysis/
│  ├─ foundry-hooks-sdk/
│  ├─ foundry-policy/
│  ├─ foundry-ui/
│  └─ foundry-security/
├─ infra/
│  ├─ docker/
│  ├─ compose/
│  ├─ migrations/
│  └─ ci/
├─ docs/
│  ├─ architecture/
│  ├─ product/
│  ├─ api/
│  ├─ hooks/
│  └─ operations/
├─ examples/
│  ├─ axtask-integration/
│  └─ demo-repo/
└─ scripts/
```

### Why a monorepo is correct here
- shared schemas
- shared UI components
- shared policy and analysis engines
- easier coordinated releases
- simpler internal development while the product family is young

---

## 10. FoundryHooks design

FoundryHooks should be:
- lightweight
- optional
- app-aware
- difficult to misuse
- easy to document
- not a giant invasive dependency

## 10.1 Hook types
1. **Feature manifest hooks**
   - declare product capabilities, modules, or domains
   - map code paths to features
   - improve summary accuracy

2. **Event hooks**
   - emit meaningful domain events
   - examples:
     - task created
     - reward recalculated
     - classification corrected
     - auth flow changed
     - payment route invoked
     - admin action executed

3. **Route/module annotations**
   - declare that certain files or modules belong to named capabilities
   - useful for branch capability inference

4. **Security hooks**
   - expose custom boundary definitions
   - identify protected routes, privileged functions, sensitive stores, token handling paths, etc.

5. **Policy hooks**
   - allow branch or release checks against declared policies

## 10.2 Do not attempt in v1
- full automatic hook placement for arbitrary apps
- deep magical auto-understanding of every framework
- hidden invasive runtime instrumentation by default

## 10.3 Do attempt in v1
- scan repo
- suggest candidate hook points
- generate a draft hook manifest
- let developer accept/edit it
- keep the contract explicit

This is realistic and sellable.

---

## 11. BranchFoundry feature blueprint

## 11.1 Core v1 features
1. **Repo dashboard**
   - repo summary
   - active branches
   - stale branches
   - recent merges
   - scan status

2. **Interactive branch graph**
   - branch/commit DAG
   - filters by author, date, label, repo, branch state
   - hover details
   - click-through evidence panels

3. **Branch detail page**
   - ahead/behind/diverged counts
   - related commits
   - file/module impact
   - inferred capabilities
   - linked PRs
   - suggested next actions

4. **Main drift panel**
   - what `main` is missing
   - what branch is behind on
   - conflict risk indicators
   - merge readiness

5. **Summary engine**
   - plain-language branch summaries
   - evidence-backed
   - confidence scoring
   - “why we think this” panel

6. **Stale work view**
   - forgotten branches
   - dormant branches with meaningful changes
   - orphaned experiments
   - branches with no recent ownership activity

7. **Action center**
   - branches needing review
   - branches ready to merge
   - branches at risk
   - branches needing rebase
   - branches with failing checks

## 11.2 Later BranchFoundry features
- stacked branch awareness
- merge queue integration
- release train view
- executive portfolio dashboard
- change-risk heatmaps
- branch grouping by feature/domain
- AI-assisted changelog generation
- issue tracker correlation
- code ownership visualizations

---

## 12. GuardFoundry feature blueprint

## 12.1 Core v1 features
1. **Secrets scanning**
   - repo
   - branch
   - full history if configured
   - prioritize active/likely-valid secrets when feasible

2. **Config exposure scanning**
   - env files
   - unsafe defaults
   - exposed credentials
   - debug settings
   - overly broad CORS / origins / headers where detectable

3. **Frontend exposure review**
   - unsafe console logging
   - sensitive data emitted to browser runtime
   - token leakage patterns
   - suspicious network payload exposure patterns where detectable

4. **Branch-aware findings**
   - findings tied to branch and PR context
   - show whether exposure is already on `main` or only in a branch

5. **Custom security hooks**
   - identify sensitive app boundaries
   - privileged routes
   - admin actions
   - token exchange flows
   - secret-bearing operations
   - data export paths

6. **Remediation view**
   - severity
   - evidence
   - likely fix areas
   - related commits/files
   - policy impact

## 12.2 Later GuardFoundry features
- custom rule authoring UI
- database posture checks for supported providers
- browser instrumentation helpers
- auth/session flow analysis
- policy packs by framework
- tenant-aware enterprise controls
- risk trend dashboards

---

## 13. AxTask as the proving ground

AxTask should be the first integrated app.

## 13.1 Why AxTask is a strong first target
- already familiar
- multiple evolving features
- clear product capability areas
- real branch drift risk
- custom UX and logic that generic Git tooling cannot fully understand

## 13.2 First five AxTask signals to track
1. **Task creation flow changes**
2. **Reward / coin accrual logic changes**
3. **Classification engine changes**
4. **Feedback prompt logic changes**
5. **PWA / install / device-specific experience changes**

## 13.3 Suggested AxTask feature manifest
```json
{
  "app": "AxTask",
  "features": [
    "task-creation",
    "reward-engine",
    "classification-engine",
    "feedback-system",
    "pwa-install-flow"
  ],
  "modules": {
    "task-creation": ["src/features/tasks/**"],
    "reward-engine": ["src/features/rewards/**"],
    "classification-engine": ["src/features/classification/**"],
    "feedback-system": ["src/features/feedback/**"],
    "pwa-install-flow": ["src/features/pwa/**", "src/features/install/**"]
  }
}
```

## 13.4 First integration objective
BranchFoundry should be able to say:
- this branch changes the reward engine
- this branch affects feedback prompts
- this branch alters task creation behavior
- main is missing these changes
- these areas have low/high confidence based on touched files, tests, and hooks

That is a real product moment.

---

## 14. Evidence model

Foundry must not pretend to know things it cannot support.

Every summary should be tied to evidence.

## 14.1 Evidence tiers
### Tier 1 — direct Git evidence
- commits
- diffs
- file paths
- authors
- branches
- PR metadata

### Tier 2 — structural inference
- module matches
- feature manifest matches
- tests touched
- route/module annotations
- ownership rules

### Tier 3 — runtime/app evidence
- hook events
- domain events
- scan findings
- runtime metadata

### Tier 4 — model inference
- semantic summaries
- likely capability changes
- risk phrasing
- natural-language branch descriptions

## 14.2 UI requirement
Every summary card should expose:
- confidence
- evidence count
- commits involved
- files/modules involved
- tests touched
- related hooks/events if present
- last scan time

This is essential for trust.

---

## 15. UX and visual design direction

The product needs to look professional on day one.

## 15.1 Recommended visual tone
**Restrained premium engineering observability**

Not:
- toy-like
- gamer-ish
- fake-cyberpunk
- generic bootstrap admin panel
- bloated enterprise sludge

## 15.2 Design traits
- dark-first, but elegant
- high contrast without eye strain
- strong typography hierarchy
- glass used sparingly, not everywhere
- subtle motion
- dense but readable information panels
- evidence side drawers
- polished empty states
- strong icon discipline
- consistent use of risk/status colors

## 15.3 Dashboard principles
- top summary strip
- primary graph area
- side evidence panel
- scan/action center
- saved views/filters
- clickable cross-navigation

## 15.4 Home screen goals
When users load it, it should signal:
- serious
- fast
- credible
- modern
- expensive enough to sell
- not trying too hard

---

## 16. Data model sketch

## 16.1 Core entities
- Repository
- Branch
- Commit
- PullRequest
- ScanRun
- Finding
- Feature
- HookManifest
- HookEvent
- Policy
- PolicyResult
- Summary
- Snapshot
- User
- Team
- Environment

## 16.2 Example relationships
- Repository has many Branches
- Branch has many Commits
- Branch has many Summaries
- Branch has many Findings
- Repository has one or more HookManifests
- HookManifest maps Features to code or runtime signals
- ScanRun produces Findings and Summaries
- PolicyResult belongs to Branch or Repository

---

## 17. Security architecture notes

Because GuardFoundry exists, Foundry itself must be secure.

## 17.1 Baseline principles
- least privilege
- no unnecessary code retention
- separate metadata from code content where practical
- audit sensitive operations
- encrypt secrets
- tenant isolation if multi-tenant later
- signed job and hook payloads where appropriate
- transparent data retention policies

## 17.2 Early choices
- support local/self-hosted mode
- avoid requiring source upload to a third-party by default
- make scanning location explicit
- be careful with browser/runtime collection
- keep customer trust high

---

## 18. Commercialization guidance

## 18.1 Initial wedge
Sell or position **BranchFoundry first**.

Why:
- easier to demo
- lower trust barrier
- immediate visual payoff
- more universal problem
- safer early claim surface

## 18.2 Premium motion
Add **GuardFoundry** as:
- premium add-on
- enterprise tier
- security suite module
- consulting-enabled deployment

## 18.3 Likely customer segments
1. solo technical builders with many branches
2. small product teams
3. agencies with many client repos
4. engineering managers needing visibility
5. enterprise teams with custom app boundaries and security needs

---

## 19. Suggested roadmap

## Phase 0 — foundation
- choose monorepo tooling
- set up FastAPI service
- set up React app shell
- set up PostgreSQL + Redis + worker
- create core schemas
- create Docker dev environment

## Phase 1 — BranchFoundry v1
- repo ingestion
- branch sync
- interactive graph
- branch detail views
- ahead/behind/diverged logic
- plain-language summaries
- evidence drawer
- stale branch detection
- polished dashboard shell

## Phase 2 — FoundryHooks v1
- feature manifest spec
- route/module annotations
- event hook schema
- candidate hook suggestion generator
- AxTask example integration

## Phase 3 — GuardFoundry v1
- secrets scan support
- config exposure checks
- frontend exposure checks
- branch-aware findings UI
- remediation views
- policy stub engine

## Phase 4 — polish and sellability
- saved views
- team/project dashboards
- shareable reports
- branding pass
- trial/demo environment
- pricing experiments
- docs and onboarding

---

## 20. Build order for today

If building today, do this in order:

1. Create the monorepo
2. Stand up the API, DB, worker, and web shell
3. Implement repo ingestion and branch sync
4. Build the branch graph UI
5. Implement branch status math
6. Add summary generation with evidence placeholders
7. Add AxTask manifest support
8. Add first five AxTask feature mappings
9. Add stale branch detection
10. Add polished dashboard styling
11. Only then start GuardFoundry fundamentals

---

## 21. Practical anti-bloat rules

To keep this real:

1. Do not build everything at once
2. Do not merge BranchFoundry and GuardFoundry into one muddy screen
3. Do not ship fake-smart summaries without evidence
4. Do not overpromise full automatic hook placement
5. Do not start with enterprise-only complexity
6. Do not build manager-surveillance theater
7. Do not let visual polish outrun actual usefulness
8. Do not build security claims wider than the scanner supports

---

## 22. MVP definition

A valid MVP for Foundry is:

### BranchFoundry MVP
- scans one or more repos
- displays branch graph
- shows ahead/behind/diverged
- shows stale branches
- generates evidence-backed summaries
- supports one real app manifest, starting with AxTask
- looks professional

### GuardFoundry pre-MVP / early beta
- scans for secrets/config exposures
- ties findings to branch context
- supports custom security hook declarations
- produces a usable findings panel

That is enough to start with dignity.

---

## 23. Immediate repository tasks

- [ ] Create `foundry` monorepo
- [ ] Create product README and vision docs
- [ ] Create backend service skeleton
- [ ] Create frontend shell and design tokens
- [ ] Create DB schema and migrations
- [ ] Build repo sync service
- [ ] Build branch graph prototype
- [ ] Define summary evidence schema
- [ ] Define `foundry.manifest.json`
- [ ] Integrate AxTask as example app
- [ ] Draft GuardFoundry scan interface
- [ ] Add CI/CD and Docker Compose

---

## 24. Example manifest spec draft

```json
{
  "app": "AxTask",
  "version": "0.1",
  "features": [
    {
      "name": "task-creation",
      "paths": ["src/features/tasks/**"],
      "signals": ["task.created", "task.updated"]
    },
    {
      "name": "reward-engine",
      "paths": ["src/features/rewards/**"],
      "signals": ["reward.recalculated", "reward.awarded"]
    },
    {
      "name": "classification-engine",
      "paths": ["src/features/classification/**"],
      "signals": ["classification.confirmed", "classification.corrected"]
    },
    {
      "name": "feedback-system",
      "paths": ["src/features/feedback/**"],
      "signals": ["feedback.prompted", "feedback.submitted"]
    },
    {
      "name": "pwa-install-flow",
      "paths": ["src/features/pwa/**", "src/features/install/**"],
      "signals": ["install.prompted", "install.completed"]
    }
  ],
  "security": {
    "sensitiveRoutes": ["/admin", "/api/rewards", "/api/classification"],
    "sensitiveStores": ["userTokens", "paymentState"],
    "privilegedActions": ["admin.override", "reward.adjust"]
  }
}
```

---

## 25. Final recommendation

Build **Foundry** as the umbrella.

Ship **BranchFoundry** first.

Use **AxTask** as the first integrated proving ground.

Keep **GuardFoundry** as a sibling product built on the same core, not jammed awkwardly into the first screen.

Make the platform elegant, evidence-backed, modular, and commercially credible.

That is the right balance between ambition and reality.
