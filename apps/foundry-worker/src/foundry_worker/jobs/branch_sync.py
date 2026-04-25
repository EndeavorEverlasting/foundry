"""BranchSync: clone/fetch + branch math + summary regeneration.

This is the heart of BranchFoundry v1. It runs whenever a user hits
`POST /repos/{id}/sync` (or on a schedule once we wire one).

Steps:
1. Load Repository row.
2. Record a ScanRun (kind=branch_sync) in RUNNING state.
3. Ensure the repo exists on disk; fetch.
4. Resolve default branch; enumerate branch refs (local + remote dedup).
5. For each branch:
   - Compute ahead/behind/diverged vs default.
   - Incrementally ingest commits since the last known SHA.
   - Classify staleness.
   - Compute readiness.
   - Match capabilities against the active manifest.
   - Build an EvidenceBundle-backed Summary.
   - Write BranchAction rows for the Action Center.
6. Mark Repository.last_synced_at; mark ScanRun SUCCEEDED.
On failure: ScanRun FAILED with error.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_analysis import (
    BranchFacts,
    DeterministicSummaryProvider,
    classify_staleness,
    compute_readiness,
    match_capabilities,
)
from foundry_core.config import get_settings
from foundry_core.db import session_scope
from foundry_core.enums import (
    ActionKind,
    BranchState,
    PullRequestState,
    ReadinessState,
    ScanKind,
    ScanStatus,
)
from foundry_core.logging import get_logger
from foundry_core.models import (
    Branch,
    BranchAction,
    Commit,
    Feature,
    HookManifest,
    PullRequest,
    Repository,
    ScanRun,
    Summary,
)
from foundry_git import BranchRef, GitPythonBackend, RepoService

log = get_logger("foundry.worker.branch_sync")


async def branch_sync(ctx: dict[str, Any], repo_id: str) -> dict[str, int | str]:
    """Full repo sync. Returns a small stats dict for the scan row."""

    settings = get_settings()
    backend = GitPythonBackend()
    repo_svc = RepoService(backend=backend, repos_dir=settings.repos_dir)

    async with session_scope() as session:
        repo = await _load_repo(session, repo_id)
        if repo is None:
            log.warning("branch_sync.repo_missing", repo_id=repo_id)
            return {"error": "repo_not_found"}

        scan = ScanRun(
            repository_id=repo.id,
            kind=ScanKind.BRANCH_SYNC,
            status=ScanStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        session.add(scan)
        await session.flush()

    stats: dict[str, int | str] = {"branches": 0, "commits_added": 0}
    try:
        async with session_scope() as session:
            repo = await _load_repo(session, repo_id)
            assert repo is not None

            repo_path = _resolve_repo_path(repo_svc, repo)

            if repo.provider == "local" and repo.local_path:
                repo_svc.sync(repo_path)
            else:
                repo_svc.ensure(repo.url, slug=repo.slug)
                repo_svc.sync(repo_path)

            default = repo_svc.default_branch(repo_path, fallback=repo.default_branch)
            if repo.default_branch != default:
                repo.default_branch = default

            refs = repo_svc.list_branches(repo_path)
            feature_map = await _load_feature_map(session, repo.id)

            total_new_commits = 0
            branch_count = 0
            summary_provider = DeterministicSummaryProvider()

            for ref in refs:
                branch_count += 1
                total_new_commits += await _sync_branch(
                    session=session,
                    repo=repo,
                    repo_path=repo_path,
                    repo_svc=repo_svc,
                    ref=ref,
                    default_branch=default,
                    feature_map=feature_map,
                    settings_warn=settings.stale_days_warn,
                    settings_critical=settings.stale_days_critical,
                    summary_provider=summary_provider,
                )

            repo.last_synced_at = datetime.now(timezone.utc)
            repo.updated_at = datetime.now(timezone.utc)

            stats = {"branches": branch_count, "commits_added": total_new_commits}

        async with session_scope() as session:
            scan_row = await session.get(ScanRun, scan.id)
            if scan_row is not None:
                scan_row.status = ScanStatus.SUCCEEDED
                scan_row.finished_at = datetime.now(timezone.utc)
                scan_row.stats = {k: v for k, v in stats.items()}

        log.info("branch_sync.ok", repo_id=repo_id, **stats)
        return stats

    except Exception as exc:  # noqa: BLE001
        log.exception("branch_sync.failed", repo_id=repo_id)
        async with session_scope() as session:
            scan_row = await session.get(ScanRun, scan.id)
            if scan_row is not None:
                scan_row.status = ScanStatus.FAILED
                scan_row.finished_at = datetime.now(timezone.utc)
                scan_row.error = str(exc)[:4000]
        return {"error": str(exc)}


# --- helpers ----------------------------------------------------------------


async def _load_repo(session: AsyncSession, repo_id: str) -> Repository | None:
    result = await session.execute(select(Repository).where(Repository.id == repo_id))
    return result.scalar_one_or_none()


def _resolve_repo_path(repo_svc: RepoService, repo: Repository) -> Path:
    if repo.local_path:
        return Path(repo.local_path)
    return repo_svc.path_for(repo.slug)


async def _load_feature_map(session: AsyncSession, repo_id: str) -> dict[str, list[str]]:
    """Flatten every feature from the repo's manifest into name -> patterns."""

    manifest_rs = await session.execute(
        select(HookManifest).where(HookManifest.repository_id == repo_id)
    )
    manifests = list(manifest_rs.scalars().all())
    if not manifests:
        return {}

    manifest_ids = [m.id for m in manifests]
    feat_rs = await session.execute(
        select(Feature).where(Feature.manifest_id.in_(manifest_ids))
    )
    return {f.name: list(f.paths or []) for f in feat_rs.scalars().all()}


async def _sync_branch(
    *,
    session: AsyncSession,
    repo: Repository,
    repo_path: Path,
    repo_svc: RepoService,
    ref: BranchRef,
    default_branch: str,
    feature_map: dict[str, list[str]],
    settings_warn: int,
    settings_critical: int,
    summary_provider: DeterministicSummaryProvider,
) -> int:
    """Upsert one branch. Returns number of commits added."""

    existing_rs = await session.execute(
        select(Branch).where(
            Branch.repository_id == repo.id, Branch.name == ref.name
        )
    )
    branch = existing_rs.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    try:
        divergence = repo_svc.divergence(repo_path, ref.name, default_branch)
    except Exception:  # noqa: BLE001
        divergence = None

    ahead = divergence.ahead if divergence else 0
    behind = divergence.behind if divergence else 0
    merge_base = divergence.merge_base if divergence else None

    if branch is None:
        branch = Branch(
            repository_id=repo.id,
            name=ref.name,
            head_sha=ref.head_sha,
            is_default=ref.is_default,
            ahead_count=ahead,
            behind_count=behind,
            merge_base_sha=merge_base,
            state=BranchState.ACTIVE,
            readiness=ReadinessState.NEEDS_REVIEW,
            created_at=now,
            updated_at=now,
        )
        session.add(branch)
        await session.flush()
        since_sha: str | None = None
    else:
        branch.head_sha = ref.head_sha
        branch.is_default = ref.is_default
        branch.ahead_count = ahead
        branch.behind_count = behind
        branch.merge_base_sha = merge_base
        branch.updated_at = now
        # Look up latest ingested commit for incremental sync.
        last_rs = await session.execute(
            select(Commit.sha)
            .where(Commit.branch_id == branch.id)
            .order_by(Commit.committed_at.desc())
            .limit(1)
        )
        since_sha = last_rs.scalar_one_or_none()

    commits = repo_svc.iter_commits(
        repo_path, ref.name, since_sha=since_sha, limit=200
    )
    commits_added = 0
    last_commit_at: datetime | None = branch.last_commit_at
    last_author: str | None = branch.last_author
    authors: set[str] = set()
    files_touched: set[str] = set()
    tests_touched: set[str] = set()
    commit_shas_for_summary: list[str] = []

    for ci in commits:
        # Skip if we already have this sha on this branch (belt-and-braces).
        dup_rs = await session.execute(
            select(Commit.id).where(Commit.branch_id == branch.id, Commit.sha == ci.sha)
        )
        if dup_rs.scalar_one_or_none() is not None:
            continue
        session.add(
            Commit(
                branch_id=branch.id,
                sha=ci.sha,
                short_sha=ci.short_sha,
                author_name=ci.author_name,
                author_email=ci.author_email,
                committed_at=ci.committed_at,
                message=ci.message,
                files_changed=ci.files_changed,
                additions=ci.additions,
                deletions=ci.deletions,
                parents=ci.parents,
            )
        )
        commits_added += 1
        if last_commit_at is None or ci.committed_at > last_commit_at:
            last_commit_at = ci.committed_at
            last_author = ci.author_name or last_author
        authors.add(ci.author_name)
        for f in ci.files_changed:
            files_touched.add(f)
            if _looks_like_test(f):
                tests_touched.add(f)
        commit_shas_for_summary.append(ci.sha)

    branch.last_commit_at = last_commit_at
    branch.last_author = last_author

    # Pull in historical authors/files if we had no new commits this round.
    if not commits_added and branch.head_sha:
        # Pull a window for staleness/capability facts even if no new commits.
        recent = repo_svc.iter_commits(repo_path, ref.name, limit=80, include_diffs=True)
        for ci in recent:
            authors.add(ci.author_name)
            for f in ci.files_changed:
                files_touched.add(f)
                if _looks_like_test(f):
                    tests_touched.add(f)
            commit_shas_for_summary.append(ci.sha)
            if last_commit_at is None or ci.committed_at > last_commit_at:
                last_commit_at = ci.committed_at
                last_author = ci.author_name or last_author

    # PR context -----------------------------------------------------------
    prs_rs = await session.execute(
        select(PullRequest).where(PullRequest.branch_id == branch.id)
    )
    prs = list(prs_rs.scalars().all())
    has_open_pr = any(p.state == PullRequestState.OPEN for p in prs)
    is_draft_pr = any(p.state == PullRequestState.DRAFT for p in prs)
    checks_passing = None
    for p in prs:
        if p.checks_passing is not None:
            checks_passing = p.checks_passing
            break
    has_reviewers = any(p.reviewers for p in prs)

    # Staleness + readiness ------------------------------------------------
    assessment = classify_staleness(
        last_commit_at=last_commit_at,
        ahead=ahead,
        behind=behind,
        has_open_pr=has_open_pr,
        has_recent_owner_activity=bool(last_author),
        warn_days=settings_warn,
        critical_days=settings_critical,
    )
    branch.state = assessment.state
    branch.stale_reasons = [r.value for r in assessment.reasons]
    branch.readiness = compute_readiness(
        ahead=ahead,
        behind=behind,
        has_open_pr=has_open_pr,
        is_draft_pr=is_draft_pr,
        checks_passing=checks_passing,
        has_reviewers=has_reviewers,
    )

    # Capabilities ---------------------------------------------------------
    capability_matches = (
        match_capabilities(files_changed=sorted(files_touched), features=feature_map)
        if feature_map
        else []
    )

    # Summary --------------------------------------------------------------
    facts = BranchFacts(
        repo_name=repo.name,
        branch_name=branch.name,
        default_branch=default_branch,
        ahead=ahead,
        behind=behind,
        last_commit_at=last_commit_at,
        last_author=last_author,
        commit_shas=list(dict.fromkeys(commit_shas_for_summary))[:50],
        files_touched=sorted(files_touched)[:200],
        authors=sorted(authors),
        tests_touched=sorted(tests_touched),
        capability_matches=capability_matches,
    )
    summary_result = summary_provider.summarize(facts)

    # Replace any prior summary for this branch (v1: one latest summary).
    await session.execute(delete(Summary).where(Summary.branch_id == branch.id))
    session.add(
        Summary(
            branch_id=branch.id,
            headline=summary_result.headline,
            body=summary_result.body,
            confidence=summary_result.confidence,
            evidence=summary_result.evidence.model_dump(),
            capabilities=summary_result.capabilities,
            generator=summary_result.generator,
            generated_at=datetime.now(timezone.utc),
        )
    )

    # Action Center rows ---------------------------------------------------
    await _rewrite_actions(session, branch, has_open_pr)

    return commits_added


async def _rewrite_actions(session: AsyncSession, branch: Branch, has_open_pr: bool) -> None:
    await session.execute(delete(BranchAction).where(BranchAction.branch_id == branch.id))

    now = datetime.now(timezone.utc)

    def add(kind: ActionKind, reason: str, priority: int = 0) -> None:
        session.add(
            BranchAction(
                branch_id=branch.id,
                kind=kind,
                reason=reason,
                priority=priority,
                created_at=now,
            )
        )

    if branch.readiness == ReadinessState.READY:
        add(ActionKind.READY_TO_MERGE, "Up to date with base and ahead of default.", priority=10)
    if branch.readiness == ReadinessState.NEEDS_REBASE:
        add(
            ActionKind.NEEDS_REBASE,
            f"Behind default by {branch.behind_count} commits while ahead by {branch.ahead_count}.",
            priority=7,
        )
    if branch.readiness == ReadinessState.FAILING_CHECKS:
        add(ActionKind.FAILING_CHECKS, "CI checks are failing on the open PR.", priority=9)
    if branch.readiness == ReadinessState.NEEDS_REVIEW:
        reason = "Open PR has no reviewers." if has_open_pr else "Branch is ahead of default and has no PR."
        add(ActionKind.NEEDS_REVIEW, reason, priority=5)
    if branch.state in (BranchState.STALE, BranchState.ORPHANED):
        add(ActionKind.AT_RISK, "Branch is stale or orphaned.", priority=3)


def _looks_like_test(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    if "/test" in p or "/tests/" in p:
        return True
    if p.endswith("_test.py") or p.endswith(".spec.ts") or p.endswith(".spec.tsx"):
        return True
    if p.endswith(".test.ts") or p.endswith(".test.tsx") or p.endswith(".test.js"):
        return True
    return False
