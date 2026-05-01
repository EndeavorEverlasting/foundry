"""Pydantic response schemas used by the API.

These are intentionally decoupled from SQLModel tables so we can evolve
the public surface without DB churn.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from foundry_core.enums import (
    ActionKind,
    BranchState,
    ConflictRisk,
    FindingSeverity,
    FindingStatus,
    PullRequestState,
    ReadinessState,
    RepoProvider,
    ScanKind,
    ScanStatus,
)
from foundry_core.evidence import EvidenceBundle


class ApiBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HealthResponse(ApiBase):
    status: str = "ok"
    env: str
    version: str


class RepositoryIn(BaseModel):
    slug: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=1, max_length=1024)
    default_branch: str = Field(default="main", max_length=200)
    provider: RepoProvider = RepoProvider.LOCAL
    local_path: str | None = None


class RepositoryOut(ApiBase):
    id: str
    slug: str
    name: str
    url: str
    provider: RepoProvider
    default_branch: str
    local_path: str | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RepoSummary(ApiBase):
    repository: RepositoryOut
    active_branches: int
    stale_branches: int
    open_prs: int
    critical_findings: int
    recent_merges: int
    last_synced_at: datetime | None = None


class BranchOut(ApiBase):
    id: str
    repository_id: str
    name: str
    head_sha: str
    merge_base_sha: str | None = None
    ahead_count: int
    behind_count: int
    is_default: bool
    state: BranchState
    readiness: ReadinessState
    stale_reasons: list[str] = Field(default_factory=list)
    conflict_risk: str = "none"
    last_author: str | None = None
    last_commit_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CommitOut(ApiBase):
    id: str
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    committed_at: datetime
    message: str
    additions: int
    deletions: int
    files_changed: list[str] = Field(default_factory=list)


class SummaryOut(ApiBase):
    id: str
    branch_id: str
    headline: str
    body: str
    confidence: float
    capabilities: list[str] = Field(default_factory=list)
    evidence: EvidenceBundle
    generator: str
    generated_at: datetime


class PullRequestOut(ApiBase):
    id: str
    number: int
    title: str
    state: PullRequestState
    url: str | None = None
    author: str | None = None
    checks_passing: bool | None = None
    opened_at: datetime | None = None
    merged_at: datetime | None = None


class BranchDetail(ApiBase):
    branch: BranchOut
    commits: list[CommitOut] = Field(default_factory=list)
    latest_summary: SummaryOut | None = None
    pull_requests: list[PullRequestOut] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    branch_id: str | None = None
    commit_sha: str
    short_sha: str
    lane: int
    x: int
    y: int
    label: str | None = None
    is_head: bool = False
    is_merge_base: bool = False
    is_default: bool = False


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: str = "parent"


class GraphResponse(BaseModel):
    repository_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    lanes: dict[str, int]


class StaleBranchBucket(BaseModel):
    label: str
    description: str
    branches: list[BranchOut] = Field(default_factory=list)


class StaleView(BaseModel):
    repository_id: str
    buckets: list[StaleBranchBucket]


class ActionCard(BaseModel):
    branch: BranchOut
    kind: ActionKind
    reason: str
    priority: int = 0


class ActionCenter(BaseModel):
    repository_id: str
    by_kind: dict[ActionKind, list[ActionCard]] = Field(default_factory=dict)

    @property
    def total_actions(self) -> int:
        return sum(len(cards) for cards in self.by_kind.values())


class DriftEntry(BaseModel):
    branch: BranchOut
    ahead: int
    behind: int
    conflict_risk: str
    readiness: ReadinessState
    release_score: int = Field(default=0, ge=0, le=100)


class DriftPanel(BaseModel):
    repository_id: str
    main_missing: list[DriftEntry]
    behind_main: list[DriftEntry]
    total_ahead: int = 0
    total_behind: int = 0
    risk_summary: dict[str, int] = Field(default_factory=dict)


class ScanRunOut(ApiBase):
    id: str
    kind: ScanKind
    status: ScanStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    stats: dict[str, str | int | float | bool] = Field(default_factory=dict)


class FindingOut(ApiBase):
    id: str
    rule: str
    severity: FindingSeverity
    status: FindingStatus
    title: str
    detail: str | None = None
    file_path: str | None = None
    line: int | None = None
    on_main: bool = False
    created_at: datetime


class ManifestFeature(BaseModel):
    name: str
    paths: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    description: str | None = None


class ManifestSecurity(BaseModel):
    sensitive_routes: list[str] = Field(default_factory=list, alias="sensitiveRoutes")
    sensitive_stores: list[str] = Field(default_factory=list, alias="sensitiveStores")
    privileged_actions: list[str] = Field(default_factory=list, alias="privilegedActions")


class ManifestRelease(BaseModel):
    route_inventory_file: str | None = Field(default=None, alias="routeInventoryFile")
    env_template_file: str | None = Field(default=None, alias="envTemplateFile")
    schema_globs: list[str] = Field(default_factory=list, alias="schemaGlobs")
    migration_globs: list[str] = Field(default_factory=list, alias="migrationGlobs")
    release_doc_globs: list[str] = Field(default_factory=list, alias="releaseDocGlobs")


class ManifestIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    app: str
    version: str = "0.1"
    features: list[ManifestFeature] = Field(default_factory=list)
    security: ManifestSecurity | None = None
    release: ManifestRelease | None = None


class ManifestOut(ApiBase):
    id: str
    repository_id: str
    app: str
    version: str
    features: list[ManifestFeature]
    security: ManifestSecurity | None = None
    release: ManifestRelease | None = None


class EnqueueResponse(BaseModel):
    job_id: str
    enqueued_at: datetime


class ReleaseProfileOut(ApiBase):
    id: str
    repository_id: str
    enabled: bool = True
    spec: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ReleaseProfileUpdate(BaseModel):
    enabled: bool = True
    spec: dict[str, object] = Field(default_factory=dict)


class ReleaseFindingOut(ApiBase):
    id: str
    code: str
    severity: FindingSeverity
    passed: bool
    message: str
    evidence: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ReleaseRunOut(ApiBase):
    id: str
    repository_id: str
    branch_name: str
    base_ref: str
    range_expr: str | None = None
    passed: bool
    summary: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    findings: list[ReleaseFindingOut] = Field(default_factory=list)


class ReleaseCheckRequest(BaseModel):
    branch_name: str | None = None
    base_ref: str = "origin/main"


class ReleaseDeployRequest(BaseModel):
    execute: bool = False
    base_ref: str = "origin/main"
    target_ref: str | None = None
    rollback_to: str | None = None


class ReleaseDeployResult(BaseModel):
    action: str
    executed: bool
    success: bool
    message: str
    commands: list[str] = Field(default_factory=list)
