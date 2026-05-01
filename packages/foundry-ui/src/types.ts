/**
 * Lightweight shared types mirroring the Foundry REST surface.
 * These are kept hand-written in v1 and replaced by generated types from
 * OpenAPI later (see `turbo gen-client`).
 */

export type BranchState =
  | "active"
  | "merged"
  | "stale"
  | "orphaned"
  | "archived";

export type ReadinessState =
  | "ready"
  | "needs_rebase"
  | "needs_review"
  | "at_risk"
  | "failing_checks"
  | "draft"
  | "safe_merge_candidate"
  | "manual_review";

export type ActionKind =
  | "needs_review"
  | "ready_to_merge"
  | "at_risk"
  | "needs_rebase"
  | "failing_checks"
  | "branch_policy_violation"
  | "manual_review";

export type PullRequestState = "open" | "merged" | "closed" | "draft";

export type RepoProvider = "local" | "github" | "gitlab" | "bitbucket" | "azure" | "generic";

export interface Repository {
  id: string;
  slug: string;
  name: string;
  url: string;
  provider: RepoProvider;
  default_branch: string;
  local_path: string | null;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RepoSummary {
  repository: Repository;
  active_branches: number;
  stale_branches: number;
  open_prs: number;
  critical_findings: number;
  recent_merges: number;
  last_synced_at: string | null;
}

export interface Branch {
  id: string;
  repository_id: string;
  name: string;
  head_sha: string;
  merge_base_sha: string | null;
  ahead_count: number;
  behind_count: number;
  is_default: boolean;
  state: BranchState;
  readiness: ReadinessState;
  stale_reasons: string[];
  conflict_risk: "none" | "low" | "medium" | "high";
  last_author: string | null;
  last_commit_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Commit {
  id: string;
  sha: string;
  short_sha: string;
  author_name: string;
  author_email: string;
  committed_at: string;
  message: string;
  additions: number;
  deletions: number;
  files_changed: string[];
}

export interface Tier1Evidence {
  commit_shas: string[];
  files_touched: string[];
  authors: string[];
  branches: string[];
  pr_numbers: number[];
}

export interface Tier2Evidence {
  module_matches: string[];
  manifest_features: string[];
  tests_touched: string[];
  ownership_hints: string[];
}

export interface Tier3Evidence {
  hook_events: string[];
  domain_events: string[];
  scan_finding_ids: string[];
  runtime_metadata: Record<string, string>;
}

export interface Tier4Evidence {
  model: string | null;
  natural_language: string | null;
  inferred_capabilities: string[];
}

export interface EvidenceBundle {
  tier1: Tier1Evidence;
  tier2: Tier2Evidence;
  tier3: Tier3Evidence;
  tier4: Tier4Evidence;
}

export interface Summary {
  id: string;
  branch_id: string;
  headline: string;
  body: string;
  confidence: number;
  capabilities: string[];
  evidence: EvidenceBundle;
  generator: string;
  generated_at: string;
}

export interface PullRequest {
  id: string;
  number: number;
  title: string;
  state: PullRequestState;
  url: string | null;
  author: string | null;
  checks_passing: boolean | null;
  opened_at: string | null;
  merged_at: string | null;
}

export interface BranchDetail {
  branch: Branch;
  commits: Commit[];
  latest_summary: Summary | null;
  pull_requests: PullRequest[];
  suggested_actions: string[];
}

export interface GraphNode {
  id: string;
  branch_id: string | null;
  commit_sha: string;
  short_sha: string;
  lane: number;
  x: number;
  y: number;
  label: string | null;
  is_head: boolean;
  is_merge_base: boolean;
  is_default: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: string;
}

export interface GraphResponse {
  repository_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  lanes: Record<string, number>;
}

export interface StaleBranchBucket {
  label: string;
  description: string;
  branches: Branch[];
}

export interface StaleView {
  repository_id: string;
  buckets: StaleBranchBucket[];
}

export interface ActionCard {
  branch: Branch;
  kind: ActionKind;
  reason: string;
  priority: number;
}

export interface ActionCenter {
  repository_id: string;
  by_kind: Partial<Record<ActionKind, ActionCard[]>>;
}

export interface DriftEntry {
  branch: Branch;
  ahead: number;
  behind: number;
  conflict_risk: "none" | "low" | "medium" | "high";
  readiness: ReadinessState;
}

export interface DriftPanel {
  repository_id: string;
  main_missing: DriftEntry[];
  behind_main: DriftEntry[];
}

export interface ManifestFeature {
  name: string;
  paths: string[];
  signals: string[];
  description: string | null;
}

export interface ManifestRelease {
  routeInventoryFile?: string | null;
  envTemplateFile?: string | null;
  schemaGlobs?: string[];
  migrationGlobs?: string[];
  releaseDocGlobs?: string[];
}

export interface Manifest {
  id: string;
  repository_id: string;
  app: string;
  version: string;
  features: ManifestFeature[];
  release?: ManifestRelease | null;
}

export type ReleaseSeverity = "info" | "low" | "medium" | "high" | "critical";

export interface ReleaseProfile {
  id: string;
  repository_id: string;
  enabled: boolean;
  spec: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ReleaseFinding {
  id: string;
  code: string;
  severity: ReleaseSeverity;
  passed: boolean;
  message: string;
  evidence: Record<string, unknown>;
  created_at: string;
}

export interface ReleaseRun {
  id: string;
  repository_id: string;
  branch_name: string;
  base_ref: string;
  range_expr: string | null;
  passed: boolean;
  summary: Record<string, unknown>;
  created_at: string;
  findings: ReleaseFinding[];
}

export interface ReleaseDeployResult {
  action: string;
  executed: boolean;
  success: boolean;
  message: string;
  commands: string[];
}
