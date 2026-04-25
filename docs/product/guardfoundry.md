# GuardFoundry — product one-pager *(Phase 2)*

**Tagline.** *App-aware security scanning that knows what your code actually
does.*

**Problem.** Generic SAST/DAST tools drown teams in findings that have no
context. "High severity in `user_controller.ts`" means nothing unless you
know that `user_controller.ts` is the privileged account-backup path.

**Solution.** GuardFoundry scans repos, runs findings through app-specific
context from `foundry.manifest.json`, and produces:

- Findings grouped by **feature** and **sensitive surface**, not just file.
- Severity reweighted by app-declared `security.privilegedActions` and
  `sensitiveRoutes`.
- Branch-level overlays: "this branch touches a privileged action — here's
  what else is in it."

**Architecture fit.** GuardFoundry lives in `packages/foundry-security` +
`apps/guardfoundry-web`. It consumes the same `foundry-core` models and
`foundry-hooks-sdk` manifest as BranchFoundry. Cross-product imports are
forbidden (CI-enforced). Shared logic lives in `foundry-*` packages.

**v1 status.** Placeholder only. `apps/guardfoundry-web` is a stub, and
`foundry-security` exposes `ScannerDescriptor` + `BUILTIN_SCANNERS` as the
extension point. Full build-out in Phase 2 per blueprint §20.

**v2 scope (sketch).**

- First-party scanners: dependency audit (OSV), secret scan, basic SAST for
  TS/Python.
- Manifest-aware severity reweighting.
- Branch-level finding overlay in BranchFoundry UI (via shared components,
  not cross-imports).
- SARIF import for third-party scanners.
