"""Integration tests for EndeavorEverlasting/foundry self-governance.

Validates internal branch naming conventions, policy regressions,
and classification of governance vs. code changes.
"""

from __future__ import annotations

import pytest

from foundry_analysis import compute_readiness, match_capabilities
from foundry_analysis.readiness import check_branch_name_policy, is_safe_merge_candidate
from foundry_core.enums import ReadinessState

FOUNDRY_MANIFEST = {
    "branch-policy": ["foundry_policy/**", "docs/branch-naming*"],
    "analysis": ["packages/foundry-analysis/**/*.py"],
    "worker": ["apps/foundry-worker/**/*.py"],
    "docs": ["docs/**", "**/*.md"],
}


def test_foundry_docs_only_safe_merge() -> None:
    files = ["docs/branch-naming-standard.md"]
    assert is_safe_merge_candidate(files_changed=files, features=FOUNDRY_MANIFEST)
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


def test_foundry_policy_code_needs_review() -> None:
    files = [
        "foundry_policy/branch_naming.py",
        "packages/foundry-analysis/src/foundry_analysis/readiness.py",
    ]
    assert not is_safe_merge_candidate(files_changed=files, features=FOUNDRY_MANIFEST)
    matches = match_capabilities(files_changed=files, features=FOUNDRY_MANIFEST)
    names = {m.feature for m in matches}
    assert "branch-policy" in names
    assert "analysis" in names


def test_foundry_worker_manual_review() -> None:
    files = ["apps/foundry-worker/src/foundry_worker/jobs/pr_cleanup.py"]
    matches = match_capabilities(files_changed=files, features=FOUNDRY_MANIFEST)
    assert any(m.feature == "worker" for m in matches)
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["external_api"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_foundry_branch_name_policy_enforced() -> None:
    assert check_branch_name_policy("docs/2026-05-01-naming-standard") is None
    assert check_branch_name_policy("feature/2026-05-01-pr-cleanup") is None
    assert check_branch_name_policy("quick-fix") == "hold:branch_policy_violation"


def test_foundry_dry_run_report_safe() -> None:
    files = ["docs/dry-run-report-schema.md", "docs/examples/pr_cleanup_dry_run.md"]
    assert is_safe_merge_candidate(files_changed=files, features=FOUNDRY_MANIFEST)
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


def test_foundry_policy_engine_change_manual_review() -> None:
    files = ["packages/foundry-policy/src/foundry_policy/engine.py"]
    matches = match_capabilities(files_changed=files, features=FOUNDRY_MANIFEST)
    assert any(m.feature == "worker" for m in matches) or not matches
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["policy_change"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_foundry_auto_merge_logic_manual_review() -> None:
    state = compute_readiness(
        ahead=3,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["merge_automation", "destructive_automation"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_foundry_branch_cleanup_risk() -> None:
    state = compute_readiness(
        ahead=1,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["branch_cleanup", "destructive_automation"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_foundry_github_api_integration_risk() -> None:
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["external_api"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_foundry_repo_scanning_risk() -> None:
    files = ["apps/foundry-worker/src/foundry_worker/jobs/repo_scan.py"]
    matches = match_capabilities(files_changed=files, features=FOUNDRY_MANIFEST)
    state = compute_readiness(
        ahead=1,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["external_api"],
    )
    assert state is ReadinessState.MANUAL_REVIEW
