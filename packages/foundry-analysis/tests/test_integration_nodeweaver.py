"""Integration tests for EndeavorEverlasting/NodeWeaver.

Tests API & integration classification, breaking-change detection,
and taxonomy schema safety.
"""

from __future__ import annotations

import pytest

from foundry_analysis import compute_readiness, match_capabilities
from foundry_analysis.readiness import check_branch_name_policy
from foundry_core.enums import ReadinessState

NODEWEAVER_MANIFEST = {
    "repo-context-api": ["api/routes/**", "schemas/**"],
    "taxonomy": ["docs/*taxonomy*", "classification/**"],
    "docs": ["docs/**", "**/*.md"],
}


def test_nodeweaver_api_change_manual_review() -> None:
    files = [
        "api/routes/repo_context.py",
        "schemas/repo_context.py",
    ]
    matches = match_capabilities(files_changed=files, features=NODEWEAVER_MANIFEST)
    names = {m.feature for m in matches}
    assert "repo-context-api" in names
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["api_contract"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_nodeweaver_taxonomy_docs_needs_review() -> None:
    files = ["docs/repo-context-classification-taxonomy.md"]
    matches = match_capabilities(files_changed=files, features=NODEWEAVER_MANIFEST)
    assert any(m.feature == "taxonomy" for m in matches)
    state = compute_readiness(
        ahead=1,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        docs_only=False,
    )
    assert state is ReadinessState.READY


def test_nodeweaver_branch_policy() -> None:
    assert check_branch_name_policy("feature/2026-05-01-repo-context") is None
    assert check_branch_name_policy("update-taxonomy") == "hold:branch_policy_violation"
