"""Integration tests for foundry-worker branch_sync job.

Validates the end-to-end flow of branch syncing, action rewriting,
and EvidenceBundle-backed summary generation against the four
real-world target repositories.  Uses mocked sessions to avoid the
SQLModel/SQLAlchemy ORM setup overhead.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import delete, select

from foundry_analysis import (
    CapabilityMatch,
    DeterministicSummaryProvider,
    classify_staleness,
    compute_readiness,
    match_capabilities,
)
from foundry_analysis.readiness import check_branch_name_policy, is_safe_merge_candidate
from foundry_core.enums import (
    ActionKind,
    BranchState,
    PullRequestState,
    ReadinessState,
)
from foundry_core.evidence import EvidenceBundle, confidence_from_bundle
from foundry_core.models import (
    Branch,
    BranchAction,
    Commit,
    Feature,
    HookManifest,
    PullRequest,
    Repository,
    Summary,
)
from foundry_worker.jobs.branch_sync import (
    _load_feature_map,
    _rewrite_actions,
)


def _mock_result(rows: list[Any]) -> MagicMock:
    mock = MagicMock()
    mock.scalars.return_value.all.return_value = rows
    mock.scalars.return_value.first.return_value = rows[0] if rows else None
    return mock


def _make_repo():
    r = MagicMock()
    r.id = "repo-1"
    r.slug = "axtask"
    r.name = "AxTask"
    r.url = "https://github.com/EndeavorEverlasting/AxTask.git"
    r.default_branch = "main"
    return r


def _make_manifest(repo):
    m = MagicMock()
    m.id = "manifest-1"
    m.repository_id = repo.id
    m.app = "AxTask"
    m.version = "0.1"
    return m


class _FakeFeature:
    def __init__(self, id, manifest_id, name, paths):
        self.id = id
        self.manifest_id = manifest_id
        self.name = name
        self.paths = paths


def _make_features(manifest):
    return [
        _FakeFeature(
            id="feat-1",
            manifest_id=manifest.id,
            name="ui-state",
            paths=["src/components/**", "client/src/components/**"],
        ),
        _FakeFeature(
            id="feat-2",
            manifest_id=manifest.id,
            name="engine-integration",
            paths=["src/engines/**", "client/src/engines/**"],
        ),
        _FakeFeature(
            id="feat-3",
            manifest_id=manifest.id,
            name="docs",
            paths=["docs/**", "**/*.md"],
        ),
    ]


class _FakeAsyncSession:
    def __init__(self, repo: Repository, manifest: HookManifest, features: list[Feature]):
        self._repo = repo
        self._manifest = manifest
        self._features = features
        self._actions: list[BranchAction] = []
        self._added: list[Any] = []

    async def execute(self, stmt):
        sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "hook_manifests" in sql:
            return _mock_result([self._manifest])
        if "features" in sql:
            return _mock_result(self._features)
        if "branch_actions" in sql and "DELETE" in sql.upper():
            self._actions.clear()
            return _mock_result([])
        if "branch_actions" in sql and "SELECT" in sql.upper():
            return _mock_result(self._actions)
        return _mock_result([])

    def add(self, obj):
        self._added.append(obj)
        if isinstance(obj, BranchAction):
            self._actions.append(obj)

    async def flush(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.mark.asyncio
async def test_load_feature_map_returns_flattened_features():
    repo = _make_repo()
    manifest = _make_manifest(repo)
    features = _make_features(manifest)
    session = _FakeAsyncSession(repo, manifest, features)
    feature_map = await _load_feature_map(session, repo.id)
    assert "ui-state" in feature_map
    assert "engine-integration" in feature_map
    assert "docs" in feature_map
    assert "src/components/**" in feature_map["ui-state"]


@pytest.mark.asyncio
async def test_rewrite_actions_for_manual_review():
    branch = MagicMock(
        id="branch-1",
        repository_id="repo-1",
        name="feature/2026-05-01-risky",
        head_sha="abc123",
        ahead_count=2,
        behind_count=0,
        state=BranchState.ACTIVE,
        readiness=ReadinessState.MANUAL_REVIEW,
    )
    repo = _make_repo()
    manifest = _make_manifest(repo)
    features = _make_features(manifest)
    session = _FakeAsyncSession(repo, manifest, features)

    await _rewrite_actions(session, branch, has_open_pr=True)

    kinds = {a.kind for a in session._actions}
    assert ActionKind.MANUAL_REVIEW in kinds


@pytest.mark.asyncio
async def test_rewrite_actions_for_safe_merge():
    branch = MagicMock(
        id="branch-2",
        repository_id="repo-1",
        name="feature/2026-05-01-docs",
        head_sha="def456",
        ahead_count=1,
        behind_count=0,
        state=BranchState.ACTIVE,
        readiness=ReadinessState.SAFE_MERGE_CANDIDATE,
    )
    repo = _make_repo()
    manifest = _make_manifest(repo)
    features = _make_features(manifest)
    session = _FakeAsyncSession(repo, manifest, features)

    await _rewrite_actions(session, branch, has_open_pr=True)

    kinds = {a.kind for a in session._actions}
    assert ActionKind.READY_TO_MERGE in kinds


@pytest.mark.asyncio
async def test_branch_sync_pipeline_axtask():
    files = [
        "src/components/SkillTree.tsx",
        "src/engines/offlineGenerator.ts",
        "docs/skill-tree-roadmap.md",
    ]
    feature_map = {
        "ui-state": ["src/components/**", "client/src/components/**"],
        "engine-integration": ["src/engines/**", "client/src/engines/**"],
        "docs": ["docs/**", "**/*.md"],
    }
    matches = match_capabilities(files_changed=files, features=feature_map)
    assert any(m.feature == "ui-state" for m in matches)
    assert any(m.feature == "engine-integration" for m in matches)

    readiness = compute_readiness(
        ahead=3,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=False,
        risk_tags=["engine_integration"],
    )
    assert readiness is ReadinessState.MANUAL_REVIEW

    assessment = classify_staleness(
        last_commit_at=datetime(2026, 4, 29, tzinfo=timezone.utc),
        ahead=3,
        behind=0,
        has_open_pr=True,
        has_recent_owner_activity=True,
    )
    assert assessment.state is BranchState.ACTIVE

    provider = DeterministicSummaryProvider()
    from foundry_analysis.summary import BranchFacts

    facts = BranchFacts(
        repo_name="AxTask",
        branch_name="feature/2026-05-01-axtask-interactive-skill-tree",
        default_branch="main",
        ahead=3,
        behind=0,
        last_commit_at=datetime(2026, 4, 29, tzinfo=timezone.utc),
        last_author="Richard",
        commit_shas=["abc123", "def456", "ghi789"],
        files_touched=files,
        authors=["Richard"],
        capability_matches=matches,
    )
    result = provider.summarize(facts)
    assert isinstance(result.evidence, EvidenceBundle)
    assert result.confidence == confidence_from_bundle(result.evidence)
    assert "ui-state" in result.capabilities or "engine-integration" in result.capabilities


@pytest.mark.asyncio
async def test_branch_sync_pipeline_webexcel():
    feature_map = {
        "streamlit-ui": ["app.py", "pages/**", "components/**"],
        "docs": ["docs/**", "notes/**", "**/*.md"],
    }

    files = ["app.py"]
    matches = match_capabilities(files_changed=files, features=feature_map)
    assert any(m.feature == "streamlit-ui" for m in matches)

    readiness = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=False,
        risk_tags=["file_ingestion", "payroll_adjacent"],
    )
    assert readiness is ReadinessState.MANUAL_REVIEW

    docs_files = ["notes/pr_order.md", "notes/pr_cleanup_status_2026-05-01.md"]
    assert is_safe_merge_candidate(files_changed=docs_files, features=feature_map)


@pytest.mark.asyncio
async def test_branch_sync_pipeline_foundry_self_governance():
    assert check_branch_name_policy("feature/2026-05-01-policy") is None
    assert check_branch_name_policy("quick-fix") == "hold:branch_policy_violation"

    docs_files = ["docs/branch-naming-standard.md"]
    assert is_safe_merge_candidate(
        files_changed=docs_files,
        features={"docs": ["docs/**", "**/*.md"]},
    )

    readiness = compute_readiness(
        ahead=1,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        docs_only=True,
    )
    assert readiness is ReadinessState.SAFE_MERGE_CANDIDATE


@pytest.mark.asyncio
async def test_branch_sync_pipeline_nodeweaver():
    feature_map = {
        "repo-context-api": ["api/routes/**", "schemas/**"],
        "docs": ["docs/**", "**/*.md"],
    }
    files = ["api/routes/repo_context.py", "schemas/repo_context.py"]
    matches = match_capabilities(files_changed=files, features=feature_map)
    assert any(m.feature == "repo-context-api" for m in matches)

    readiness = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
        risk_tags=["api_contract"],
    )
    assert readiness is ReadinessState.MANUAL_REVIEW


@pytest.mark.asyncio
async def test_branch_sync_pipeline_draft_status():
    readiness = compute_readiness(
        ahead=2,
        behind=0,
        has_open_pr=True,
        is_draft_pr=True,
        checks_passing=None,
        has_reviewers=True,
    )
    assert readiness is ReadinessState.DRAFT


@pytest.mark.asyncio
async def test_branch_sync_pipeline_behind_needs_rebase():
    readiness = compute_readiness(
        ahead=2,
        behind=5,
        has_open_pr=True,
        is_draft_pr=False,
        checks_passing=None,
        has_reviewers=True,
    )
    assert readiness is ReadinessState.NEEDS_REBASE
