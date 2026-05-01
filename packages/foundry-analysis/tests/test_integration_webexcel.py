"""Integration tests for EndeavorEverlasting/web-excel-repair-triage.

Tests safe_merge_candidate logic for operational workflows vs. sensitive logic.
"""

from __future__ import annotations

import pytest

from foundry_analysis import compute_readiness, match_capabilities
from foundry_analysis.readiness import check_branch_name_policy, is_safe_merge_candidate
from foundry_core.enums import ReadinessState

WEBEXCEL_MANIFEST = {
    "excel-repair": ["triage/**", "repair/**"],
    "streamlit-ui": ["app.py", "pages/**", "components/**"],
    "docs": ["docs/**", "notes/**", "**/*.md"],
}


def test_webexcel_pdf_intake_risk_tags() -> None:
    files = ["app.py"]
    matches = match_capabilities(files_changed=files, features=WEBEXCEL_MANIFEST)
    names = {m.feature for m in matches}
    assert "streamlit-ui" in names


def test_webexcel_pdf_intake_manual_review() -> None:
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=False,
        risk_tags=["file_ingestion", "payroll_adjacent"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_webexcel_branch_policy_passes() -> None:
    assert (
        check_branch_name_policy("feature/2026-05-01-monthly-pdf-intake") is None
    )


def test_webexcel_docs_safe_merge() -> None:
    files = ["notes/pr_order.md", "notes/pr_cleanup_status_2026-05-01.md"]
    assert is_safe_merge_candidate(files_changed=files, features=WEBEXCEL_MANIFEST)
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


def test_webexcel_repair_engine_risk() -> None:
    files = ["triage/patcher.py", "triage/gate_checks.py"]
    matches = match_capabilities(files_changed=files, features=WEBEXCEL_MANIFEST)
    assert any(m.feature == "excel-repair" for m in matches)
    state = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["data_integrity"],
    )
    assert state is ReadinessState.MANUAL_REVIEW
