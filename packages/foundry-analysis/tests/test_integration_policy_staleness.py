"""Policy enforcement and staleness state transition tests.

These tests exercise the four state transitions required by the spec:
1. Branch policy violation -> hold:branch_policy_violation
2. Draft PR -> ReadinessState.DRAFT
3. Behind main -> ReadinessState.NEEDS_REBASE
4. Documentation only -> safe_merge_candidate
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from foundry_analysis import classify_staleness, compute_readiness
from foundry_analysis.readiness import check_branch_name_policy, is_safe_merge_candidate
from foundry_core.enums import BranchState, ReadinessState, StaleReason

NOW = datetime(2026, 5, 1, tzinfo=timezone.utc)


def test_branch_policy_violation_bad_name() -> None:
    result = check_branch_name_policy("skill-tree-fix")
    assert result == "hold:branch_policy_violation"


def test_branch_policy_violation_good_name() -> None:
    assert check_branch_name_policy("feature/2026-05-01-skill-tree") is None


def test_draft_pr_returns_draft() -> None:
    state = compute_readiness(
        ahead=3,
        behind=0,
        has_open_pr=True,
        is_draft_pr=True,
        checks_passing=None,
        has_reviewers=True,
    )
    assert state is ReadinessState.DRAFT


def test_behind_main_returns_needs_rebase() -> None:
    state = compute_readiness(
        ahead=3,
        behind=5,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
    )
    assert state is ReadinessState.NEEDS_REBASE


def test_docs_only_returns_safe_merge() -> None:
    features = {"docs": ["docs/**", "**/*.md"]}
    files = ["docs/guide.md", "README.md"]
    assert is_safe_merge_candidate(files_changed=files, features=features)
    state = compute_readiness(
        ahead=1,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        docs_only=True,
    )
    assert state is ReadinessState.SAFE_MERGE_CANDIDATE


def test_docs_only_false_when_code_present() -> None:
    features = {"docs": ["docs/**", "**/*.md"]}
    files = ["docs/guide.md", "src/main.py"]
    assert not is_safe_merge_candidate(files_changed=files, features=features)


def test_staleness_orphaned() -> None:
    assessment = classify_staleness(
        last_commit_at=NOW - timedelta(days=60),
        ahead=0,
        behind=0,
        has_open_pr=False,
        has_recent_owner_activity=False,
        warn_days=14,
        critical_days=45,
        now=NOW,
    )
    assert assessment.state is BranchState.ORPHANED
    assert StaleReason.ORPHANED_FROM_MAIN in assessment.reasons


def test_staleness_no_pr_activity() -> None:
    assessment = classify_staleness(
        last_commit_at=NOW - timedelta(days=20),
        ahead=2,
        behind=0,
        has_open_pr=False,
        has_recent_owner_activity=False,
        warn_days=14,
        critical_days=45,
        now=NOW,
    )
    assert assessment.state is BranchState.STALE
    assert StaleReason.NO_PR_ACTIVITY in assessment.reasons
