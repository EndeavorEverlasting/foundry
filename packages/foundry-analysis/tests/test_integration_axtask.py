"""Integration tests for EndeavorEverlasting/AxTask.

Validates match_capabilities, compute_readiness, and EvidenceBundle
confidence for a complex React + engine repo.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from foundry_analysis import (
    CapabilityMatch,
    DeterministicSummaryProvider,
    compute_readiness,
    match_capabilities,
)
from foundry_analysis.readiness import check_branch_name_policy, is_safe_merge_candidate
from foundry_analysis.stale import classify_staleness
from foundry_core.enums import ReadinessState
from foundry_core.evidence import EvidenceBundle, confidence_from_bundle

NOW = datetime(2026, 5, 1, tzinfo=timezone.utc)

AXTASK_MANIFEST = {
    "task-creation": ["src/features/tasks/**", "client/src/features/tasks/**"],
    "engine-integration": ["src/engines/**", "client/src/engines/**"],
    "ui-state": ["src/components/**", "client/src/components/**"],
    "docs": ["docs/**", "**/*.md"],
}


def test_axtask_skill_tree_matches_ui_and_engine() -> None:
    """Scenario A: Skill tree PR touches UI and engine surfaces."""
    files = [
        "src/components/SkillTree.tsx",
        "src/engines/offlineGenerator.ts",
        "docs/skill-tree-roadmap.md",
    ]
    matches = match_capabilities(files_changed=files, features=AXTASK_MANIFEST)
    names = {m.feature for m in matches}
    assert "ui-state" in names
    assert "engine-integration" in names
    assert "docs" in names


def test_axtask_capability_confidence() -> None:
    files = ["src/components/SkillTree.tsx", "src/engines/offlineGenerator.ts"]
    matches = match_capabilities(files_changed=files, features=AXTASK_MANIFEST)
    assert matches[0].confidence >= 0.4


def test_axtask_readiness_needs_review() -> None:
    state = compute_readiness(
        ahead=3,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=False,
        risk_tags=["engine_integration"],
    )
    assert state is ReadinessState.MANUAL_REVIEW


def test_axtask_branch_policy_passes() -> None:
    assert check_branch_name_policy(
        "feature/2026-05-01-axtask-interactive-skill-tree"
    ) is None


def test_axtask_summary_populates_evidence() -> None:
    from foundry_analysis.summary import BranchFacts

    facts = BranchFacts(
        repo_name="AxTask",
        branch_name="feature/2026-05-01-axtask-interactive-skill-tree",
        default_branch="main",
        ahead=3,
        behind=0,
        last_commit_at=NOW - timedelta(days=2),
        last_author="Richard",
        commit_shas=["abc123", "def456", "ghi789"],
        files_touched=[
            "src/components/SkillTree.tsx",
            "src/engines/offlineGenerator.ts",
            "docs/skill-tree-roadmap.md",
        ],
        authors=["Richard"],
        capability_matches=[
            CapabilityMatch(
                feature="ui-state",
                matched_files=["src/components/SkillTree.tsx"],
                total_feature_paths=2,
            ),
            CapabilityMatch(
                feature="engine-integration",
                matched_files=["src/engines/offlineGenerator.ts"],
                total_feature_paths=2,
            ),
        ],
    )
    result = DeterministicSummaryProvider().summarize(facts)
    assert result.confidence > 0
    assert isinstance(result.evidence, EvidenceBundle)
    assert confidence_from_bundle(result.evidence) == pytest.approx(result.confidence)
    assert "ui-state" in result.capabilities


def test_axtask_safe_merge_candidate_for_docs_only() -> None:
    files = ["docs/skill-tree-roadmap.md"]
    assert is_safe_merge_candidate(files_changed=files, features=AXTASK_MANIFEST)
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


def test_axtask_staleness_active() -> None:
    assessment = classify_staleness(
        last_commit_at=NOW - timedelta(days=2),
        ahead=3,
        behind=0,
        has_open_pr=True,
        has_recent_owner_activity=True,
        now=NOW,
    )
    assert assessment.state.value == "active"
