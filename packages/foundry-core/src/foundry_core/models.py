"""SQLModel entities for the Foundry data model (blueprint §16).

All primary keys are UUIDv7 strings (lexicographically sortable). JSON
columns use JSONB on Postgres so we can index into nested evidence
structures if we ever need to.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from foundry_core.enums import (
    ActionKind,
    BranchState,
    FindingSeverity,
    FindingStatus,
    PullRequestState,
    ReadinessState,
    RepoProvider,
    ScanKind,
    ScanStatus,
    StaleReason,
)
from foundry_core.ids import uuid7


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _json_col() -> Column[Any]:
    """JSONB on Postgres, fall back to JSON for sqlite/tests."""

    return Column(JSONB().with_variant(JSON(), "sqlite"), nullable=False, default=dict)


# --- Users / teams (single-user in v1, but schema is future-ready) ----------


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    email: str = Field(max_length=320, unique=True, index=True)
    display_name: str = Field(max_length=120)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    slug: str = Field(max_length=80, unique=True, index=True)
    name: str = Field(max_length=160)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


# --- Repositories / branches / commits --------------------------------------


class Repository(SQLModel, table=True):
    __tablename__ = "repositories"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    slug: str = Field(max_length=160, unique=True, index=True)
    name: str = Field(max_length=200)
    provider: RepoProvider = Field(default=RepoProvider.LOCAL)
    url: str = Field(max_length=1024)
    default_branch: str = Field(default="main", max_length=200)
    local_path: str | None = Field(default=None, max_length=1024)
    last_synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    branches: list["Branch"] = Relationship(
        back_populates="repository",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    manifests: list["HookManifest"] = Relationship(
        back_populates="repository",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Branch(SQLModel, table=True):
    __tablename__ = "branches"
    __table_args__ = (
        Index("ix_branches_repo_name", "repository_id", "name", unique=True),
        Index("ix_branches_state", "state"),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    name: str = Field(max_length=400)
    head_sha: str = Field(max_length=40, index=True)
    upstream_sha: str | None = Field(default=None, max_length=40)
    merge_base_sha: str | None = Field(default=None, max_length=40)

    ahead_count: int = Field(default=0)
    behind_count: int = Field(default=0)
    diverged_at_sha: str | None = Field(default=None, max_length=40)
    is_default: bool = Field(default=False)

    state: BranchState = Field(default=BranchState.ACTIVE)
    stale_reasons: list[str] = Field(
        default_factory=list,
        sa_column=_json_col(),
    )
    readiness: ReadinessState = Field(default=ReadinessState.NEEDS_REVIEW)
    conflict_risk: str = Field(default="none", max_length=20)

    last_author: str | None = Field(default=None, max_length=320)
    last_commit_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )

    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    repository: Repository = Relationship(back_populates="branches")
    commits: list["Commit"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    summaries: list["Summary"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    findings: list["Finding"] = Relationship(back_populates="branch")
    pull_requests: list["PullRequest"] = Relationship(back_populates="branch")


class Commit(SQLModel, table=True):
    __tablename__ = "commits"
    __table_args__ = (Index("ix_commits_branch_sha", "branch_id", "sha", unique=True),)

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    branch_id: str = Field(foreign_key="branches.id", index=True, max_length=36)
    sha: str = Field(max_length=40, index=True)
    short_sha: str = Field(max_length=12)
    author_name: str = Field(max_length=320)
    author_email: str = Field(max_length=320)
    committed_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )
    message: str = Field(sa_column=Column(Text, nullable=False))
    files_changed: list[str] = Field(default_factory=list, sa_column=_json_col())
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    parents: list[str] = Field(default_factory=list, sa_column=_json_col())

    branch: Branch = Relationship(back_populates="commits")


class PullRequest(SQLModel, table=True):
    __tablename__ = "pull_requests"
    __table_args__ = (
        Index("ix_prs_repo_number", "repository_id", "number", unique=True),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_id: str | None = Field(
        default=None, foreign_key="branches.id", index=True, max_length=36
    )
    number: int = Field(sa_column=Column(Integer, nullable=False))
    title: str = Field(max_length=500)
    state: PullRequestState = Field(default=PullRequestState.OPEN)
    url: str | None = Field(default=None, max_length=1024)
    author: str | None = Field(default=None, max_length=320)
    reviewers: list[str] = Field(default_factory=list, sa_column=_json_col())
    checks_passing: bool | None = Field(default=None)
    opened_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    merged_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    branch: Branch | None = Relationship(back_populates="pull_requests")


# --- Summaries (evidence-backed) --------------------------------------------


class Summary(SQLModel, table=True):
    __tablename__ = "summaries"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    branch_id: str = Field(foreign_key="branches.id", index=True, max_length=36)
    headline: str = Field(max_length=400)
    body: str = Field(sa_column=Column(Text, nullable=False))
    confidence: float = Field(default=0.0)
    evidence: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    capabilities: list[str] = Field(default_factory=list, sa_column=_json_col())
    generator: str = Field(default="deterministic-v1", max_length=80)
    generated_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    branch: Branch = Relationship(back_populates="summaries")


class Snapshot(SQLModel, table=True):
    """Nightly snapshot of a repository's key counts for trend views."""

    __tablename__ = "snapshots"
    __table_args__ = (
        Index("ix_snapshots_repo_taken", "repository_id", "taken_at"),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    taken_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    active_branches: int = Field(default=0)
    stale_branches: int = Field(default=0)
    open_prs: int = Field(default=0)
    critical_findings: int = Field(default=0)
    metrics: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())


# --- Hooks / manifests / features -------------------------------------------


class HookManifest(SQLModel, table=True):
    __tablename__ = "hook_manifests"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    app: str = Field(max_length=160)
    version: str = Field(default="0.1", max_length=40)
    raw: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    source_path: str | None = Field(default=None, max_length=1024)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    repository: Repository = Relationship(back_populates="manifests")
    features: list["Feature"] = Relationship(
        back_populates="manifest",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Feature(SQLModel, table=True):
    __tablename__ = "features"
    __table_args__ = (
        Index("ix_features_manifest_name", "manifest_id", "name", unique=True),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    manifest_id: str = Field(foreign_key="hook_manifests.id", index=True, max_length=36)
    name: str = Field(max_length=160)
    paths: list[str] = Field(default_factory=list, sa_column=_json_col())
    signals: list[str] = Field(default_factory=list, sa_column=_json_col())
    description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    manifest: HookManifest = Relationship(back_populates="features")


class HookEvent(SQLModel, table=True):
    """Runtime event emitted by a host app via FoundryHooks (Tier 3 evidence)."""

    __tablename__ = "hook_events"
    __table_args__ = (
        Index("ix_hook_events_repo_received", "repository_id", "received_at"),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_id: str | None = Field(
        default=None, foreign_key="branches.id", index=True, max_length=36
    )
    feature_id: str | None = Field(
        default=None, foreign_key="features.id", index=True, max_length=36
    )
    signal: str = Field(max_length=160)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    received_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


# --- Scans / findings / policies --------------------------------------------


class ScanRun(SQLModel, table=True):
    __tablename__ = "scan_runs"
    __table_args__ = (Index("ix_scan_runs_repo_kind", "repository_id", "kind"),)

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_id: str | None = Field(
        default=None, foreign_key="branches.id", index=True, max_length=36
    )
    kind: ScanKind = Field(default=ScanKind.BRANCH_SYNC)
    status: ScanStatus = Field(default=ScanStatus.PENDING)
    started_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    stats: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class Finding(SQLModel, table=True):
    """Security / hygiene finding. GuardFoundry writes here; BranchFoundry reads counts."""

    __tablename__ = "findings"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_id: str | None = Field(
        default=None, foreign_key="branches.id", index=True, max_length=36
    )
    scan_run_id: str | None = Field(
        default=None, foreign_key="scan_runs.id", index=True, max_length=36
    )
    rule: str = Field(max_length=160)
    severity: FindingSeverity = Field(default=FindingSeverity.LOW)
    status: FindingStatus = Field(default=FindingStatus.OPEN)
    title: str = Field(max_length=400)
    detail: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    file_path: str | None = Field(default=None, max_length=1024)
    line: int | None = Field(default=None)
    commit_sha: str | None = Field(default=None, max_length=40)
    on_main: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    branch: Branch | None = Relationship(back_populates="findings")


class Policy(SQLModel, table=True):
    __tablename__ = "policies"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    slug: str = Field(max_length=120, unique=True, index=True)
    name: str = Field(max_length=200)
    spec: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    enabled: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class PolicyResult(SQLModel, table=True):
    __tablename__ = "policy_results"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    policy_id: str = Field(foreign_key="policies.id", index=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_id: str | None = Field(
        default=None, foreign_key="branches.id", index=True, max_length=36
    )
    passed: bool = Field(default=True)
    detail: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    evaluated_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


# --- Release-contract control plane -----------------------------------------


class ReleaseProfile(SQLModel, table=True):
    """Per-repository release policy profile used by Release Readiness checks."""

    __tablename__ = "release_profiles"

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(
        foreign_key="repositories.id", index=True, max_length=36, unique=True
    )
    spec: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    enabled: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ReleaseRun(SQLModel, table=True):
    """A concrete execution of release policy checks for one repo/branch."""

    __tablename__ = "release_runs"
    __table_args__ = (Index("ix_release_runs_repo_created", "repository_id", "created_at"),)

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    repository_id: str = Field(foreign_key="repositories.id", index=True, max_length=36)
    branch_name: str = Field(max_length=200)
    base_ref: str = Field(max_length=200, default="origin/main")
    range_expr: str | None = Field(default=None, max_length=400)
    passed: bool = Field(default=True)
    summary: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ReleaseFinding(SQLModel, table=True):
    """Individual check result attached to a ReleaseRun."""

    __tablename__ = "release_findings"
    __table_args__ = (Index("ix_release_findings_run", "release_run_id"),)

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    release_run_id: str = Field(foreign_key="release_runs.id", index=True, max_length=36)
    code: str = Field(max_length=120)
    severity: FindingSeverity = Field(default=FindingSeverity.INFO)
    passed: bool = Field(default=True)
    message: str = Field(max_length=600)
    evidence: dict[str, Any] = Field(default_factory=dict, sa_column=_json_col())
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


# --- Branch-level actions (Action Center) -----------------------------------


class BranchAction(SQLModel, table=True):
    """Denormalized actionable items per branch (computed, not edited)."""

    __tablename__ = "branch_actions"
    __table_args__ = (
        Index("ix_branch_actions_branch_kind", "branch_id", "kind", unique=True),
    )

    id: str = Field(default_factory=uuid7, primary_key=True, max_length=36)
    branch_id: str = Field(foreign_key="branches.id", index=True, max_length=36)
    kind: ActionKind = Field(default=ActionKind.NEEDS_REVIEW)
    reason: str = Field(max_length=400)
    priority: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


__all__ = [
    "ActionKind",
    "Branch",
    "BranchAction",
    "BranchState",
    "Commit",
    "Feature",
    "Finding",
    "FindingSeverity",
    "FindingStatus",
    "HookEvent",
    "HookManifest",
    "Policy",
    "PolicyResult",
    "PullRequest",
    "PullRequestState",
    "ReadinessState",
    "ReleaseFinding",
    "ReleaseProfile",
    "ReleaseRun",
    "RepoProvider",
    "Repository",
    "ScanKind",
    "ScanRun",
    "ScanStatus",
    "Snapshot",
    "StaleReason",
    "Summary",
    "Team",
    "User",
    "SQLModel",
]
