"""Enumerations shared across Foundry services."""

from __future__ import annotations

from enum import Enum


class BranchState(str, Enum):
    """High-level lifecycle status for a branch."""

    ACTIVE = "active"
    MERGED = "merged"
    STALE = "stale"
    ORPHANED = "orphaned"
    ARCHIVED = "archived"


class StaleReason(str, Enum):
    """Why a branch was classified as stale."""

    NO_RECENT_COMMITS = "no_recent_commits"
    NO_PR_ACTIVITY = "no_pr_activity"
    ORPHANED_FROM_MAIN = "orphaned_from_main"
    NO_OWNER_ACTIVITY = "no_owner_activity"


class ReadinessState(str, Enum):
    """Aggregate merge-readiness of a branch."""

    READY = "ready"
    NEEDS_REBASE = "needs_rebase"
    NEEDS_REVIEW = "needs_review"
    AT_RISK = "at_risk"
    FAILING_CHECKS = "failing_checks"
    DRAFT = "draft"
    SAFE_MERGE_CANDIDATE = "safe_merge_candidate"
    MANUAL_REVIEW = "manual_review"


class ActionKind(str, Enum):
    """Action-center card categories."""

    NEEDS_REVIEW = "needs_review"
    READY_TO_MERGE = "ready_to_merge"
    AT_RISK = "at_risk"
    NEEDS_REBASE = "needs_rebase"
    FAILING_CHECKS = "failing_checks"
    BRANCH_POLICY_VIOLATION = "branch_policy_violation"
    MANUAL_REVIEW = "manual_review"


class ScanKind(str, Enum):
    """Type of background scan."""

    BRANCH_SYNC = "branch_sync"
    SUMMARY_REGEN = "summary_regen"
    SECRETS_SCAN = "secrets_scan"
    CONFIG_SCAN = "config_scan"
    FRONTEND_EXPOSURE = "frontend_exposure"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class PullRequestState(str, Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    DRAFT = "draft"


class RepoProvider(str, Enum):
    LOCAL = "local"
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    AZURE = "azure"
    GENERIC = "generic"


class ConflictRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HookEventKind(str, Enum):
    DOMAIN = "domain"
    SECURITY = "security"
    POLICY = "policy"
